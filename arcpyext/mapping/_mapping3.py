# coding=utf-8
"""This module contains extended functionality for related to the arcpy.mp module."""

# Python 2/3 compatibility
# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins.disabled import *
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()
# pylint: enable=wildcard-import,unused-wildcard-import,wrong-import-order,wrong-import-position

# Standard lib imports
import logging
import json
import os.path
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from decimal import Decimal
from pathlib2 import Path
try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

# Third-party imports
import arcpy

# Local imports

from ._cim import ProProject
from ._cim.layers import ProVectorTileLayer
from ._mapping_helpers import tokenise_table_name
from .. import _native as _prosdk
from .._utils import get_arcgis_version
from .._patches._mp._cim_helpers import is_query_layer
from .._str import eformat, format_def_query
from ..exceptions import DataSourceUpdateError

# Put the map document class here so we can access the per-version type in a consistent location across Python versions
Document = arcpy.mp.ArcGISProject
LayerFile = arcpy.mp.LayerFile


def fix_datum_transforms(arc_file):
    """For various ArcGIS-type files (currently APRX and MAPX), 'fix' datum transform information so that it is 
    compatible for the document version by re-writing datum transformation information.

    In ArcGIS Pro 3.0, various datum transforms had there WKIDs changed in line with official EPSG designation.
    In doing so, Esri broke compatibility with APRXs/MAPXs generated out of ArcGIS Pro 3.0 even when exported (via 
    sharing) to the ArcGIS Pro 2.x level. This function attempts to safely revert WKID/WKT information for older
    APRX/MAPX versions.

    Args:
        arc_file (str|Path): The ArcGIS file to operate on.
    """

    # treat file as Path
    arc_file = Path(str(arc_file))

    # store datum transform changes by version level that they changed at
    # in other words, if the file is older than that, proceed:
    transforms_to_fix = [
        {
            "version": Decimal(3),
            "transformFixes": [
                {
                    "currentWkt": 'GEOGTRAN["GDA_1994_To_GDA2020_1",GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],GEOGCS["GDA2020",DATUM["GDA2020",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],METHOD["Coordinate_Frame"],PARAMETER["X_Axis_Translation",0.06155],PARAMETER["Y_Axis_Translation",-0.01087],PARAMETER["Z_Axis_Translation",-0.04019],PARAMETER["X_Axis_Rotation",-0.0394924],PARAMETER["Y_Axis_Rotation",-0.0327221],PARAMETER["Z_Axis_Rotation",-0.0328979],PARAMETER["Scale_Difference",-0.009994],OPERATIONACCURACY[0.01],AUTHORITY["EPSG",8048]]',
                    "currentWkid": "8048",
                    "name": "GDA_1994_To_GDA2020_1",
                    "oldWkt": 'GEOGTRAN["GDA_1994_To_GDA2020_1",GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],GEOGCS["GDA2020",DATUM["GDA2020",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],METHOD["Coordinate_Frame"],PARAMETER["X_Axis_Translation",0.06155],PARAMETER["Y_Axis_Translation",-0.01087],PARAMETER["Z_Axis_Translation",-0.04019],PARAMETER["X_Axis_Rotation",-0.0394924],PARAMETER["Y_Axis_Rotation",-0.0327221],PARAMETER["Z_Axis_Rotation",-0.0328979],PARAMETER["Scale_Difference",-0.009994],OPERATIONACCURACY[0.01],AUTHORITY["EPSG",108060]]',
                    "oldWkid": "108060"
                }, {
                    "currentWkt": 'GEOGTRAN["GDA_1994_To_GDA2020_NTv2_3_Conformal",GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],GEOGCS["GDA2020",DATUM["GDA2020",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],METHOD["NTv2"],PARAMETER["Dataset_australia/GDA94_GDA2020_conformal",0.0],OPERATIONACCURACY[0.05],AUTHORITY["EPSG",8446]]',
                    "currentWkid": "8446",
                    "name": "GDA_1994_To_GDA2020_NTv2_3_Conformal",
                    "oldWkt": 'GEOGTRAN["GDA_1994_To_GDA2020_NTv2_3_Conformal",GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],GEOGCS["GDA2020",DATUM["GDA2020",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],METHOD["NTv2"],PARAMETER["Dataset_australia/GDA94_GDA2020_conformal",0.0],OPERATIONACCURACY[0.05],AUTHORITY["EPSG",108446]]',
                    "oldWkid": "108446"
                }, {
                    "currentWkt": 'GEOGTRAN["GDA_1994_To_GDA2020_NTv2_2_Conformal_and_Distortion",GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],GEOGCS["GDA2020",DATUM["GDA2020",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],METHOD["NTv2"],PARAMETER["Dataset_australia/GDA94_GDA2020_conformal_and_distortion",0.0],OPERATIONACCURACY[0.05],AUTHORITY["EPSG",8447]]',
                    "currentWkid": "8447",
                    "name": "GDA_1994_To_GDA2020_NTv2_2_Conformal_and_Distortion",
                    "oldWkt": 'GEOGTRAN["GDA_1994_To_GDA2020_NTv2_2_Conformal_and_Distortion",GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],GEOGCS["GDA2020",DATUM["GDA2020",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],METHOD["NTv2"],PARAMETER["Dataset_australia/GDA94_GDA2020_conformal_and_distortion",0.0],OPERATIONACCURACY[0.05],AUTHORITY["EPSG",108447]]',
                    "oldWkid": "108447"
                }
            ]
        }
    ]

    def register_xml_namespaces(filename):
        namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
        for ns in namespaces:
            ET.register_namespace(ns, namespaces[ns])
        return namespaces

    if arc_file.suffix.lower() == ".aprx":
        # process as ArcGIS Project
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # extract contents to temporary directory
            shutil.unpack_archive(str(arc_file), str(temp_dir), format="zip")

            # check version of the archive to see whether we need to process
            doc_info_xml_tree = ET.parse(str(temp_dir_path / "DocumentInfo.xml"))
            doc_version = Decimal(".".join(doc_info_xml_tree.find("./Version").text.split(".")[:2]))

            # track if the project has changed
            project_made_changes = False

            for tf in transforms_to_fix:
                if not doc_version < tf["version"]:
                    # set of changes doesn't apply to this version
                    continue

                # process this APRX against this set of transform changes

                # get paths to all maps in the project
                gis_project_xml_tree = ET.parse(str(temp_dir_path / "GISProject.xml"))
                project_items_xpath = "./ProjectItems/CIMProjectItem"
                project_items = gis_project_xml_tree.findall(project_items_xpath)
                map_project_items = [pi for pi in project_items if pi.find("./ItemType").text == "Map"]
                map_paths = [pi.find("./CatalogPath").text.replace("CIMPATH=", "") for pi in map_project_items]

                # for each map, check if the datum transforms need winding back
                for map_path in map_paths:
                    # track whether changes were made to the map
                    map_made_changes = False

                    # parse the map file, get the datum transforms
                    map_xml_path = str(temp_dir_path / map_path)
                    map_xml_namespaces = register_xml_namespaces(map_xml_path)
                    map_xml_tree = ET.parse(map_xml_path)
                    datum_transforms = map_xml_tree.findall("./DatumTransforms/CIMDatumTransform")

                    # for each datum transform, compare current WKT to check if we need to wind back
                    for dt in datum_transforms:
                        transformation_items = dt.findall("./GeoTransformation/XForms/TransformationItem")
                        for ti in transformation_items:
                            transform = ti.find("./XForm")
                            if transform == None:
                                continue

                            wkt_element = transform.find("./WKT")
                            if wkt_element == None:
                                continue

                            wkt = wkt_element.text.strip()

                            for fix_info in tf["transformFixes"]:
                                if not wkt == fix_info["currentWkt"]:
                                    continue

                                # fix the transform
                                wkt_element.text = fix_info["oldWkt"]
                                wkid_element = transform.find("./WKID")
                                wkid_element.text = fix_info["oldWkid"]
                                map_made_changes = True

                    if map_made_changes:
                        # save the map back out
                        # ensure all the original attributes are written out on the root
                        map_xml_root = map_xml_tree.getroot()
                        existing_uris = [k.split('}')[0].strip('{') for k in map_xml_root.keys()]
                        for prefix, uri in map_xml_namespaces.items():
                            if not uri in existing_uris:
                                tag = f"xmlns:{prefix}" if prefix else "xmlns"
                                map_xml_root.set(tag, uri)

                        map_xml_tree.write(str(temp_dir_path / map_path), encoding="UTF-8")
                        # with (temp_dir_path / map_path).open("w") as output_file_handle:
                        #     output_file_handle.write(ET.tostring(map_xml_tree.getroot(), encoding="unicode"))
                        # note that we made changes to the project
                        project_made_changes = True

            if project_made_changes:
                # need to zip the APRX back up
                with zipfile.ZipFile(
                    str(arc_file), "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True
                ) as output_file_handle:
                    # glob the input extracted directory
                    files_to_archive = temp_dir_path.glob("**/*")
                    for f in files_to_archive:
                        if not f.is_dir():
                            # write file in zip to relative path
                            output_file_handle.write(f, f.relative_to(temp_dir_path))

    elif arc_file.suffix.lower() == ".mapx":
        mapx_modified = False

        # get the version of the map
        map_json = json.loads(arc_file.read_text(encoding="utf-8"))
        doc_version = Decimal(".".join(map_json["version"].split(".")[:2]))

        for tf in transforms_to_fix:
            if not doc_version < tf["version"]:
                # set of changes doesn't apply to this version
                continue

            # process this MAPX against this set of transform fixes

            datum_transforms = map_json.get("mapDefinition", {}).get("datumTransforms", [])
            for dt in datum_transforms:
                geo_transforms = dt.get("geoTransformation", {}).get("geoTransforms", [])
                for gt in geo_transforms:
                    for fix_info in tf["transformFixes"]:
                        if str(gt.get("name")) == fix_info["name"]:
                            gt["latestWkid"] = int(fix_info["oldWkid"])
                            gt["wkid"] = int(fix_info["oldWkid"])
                            mapx_modified = True

        if mapx_modified:
            with arc_file.open("w", encoding="utf-8") as output_file_handle:
                output_file_handle.write(
                    json.dumps(map_json, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
                )


def open_document(project):
    """Open an ArcGIS Pro Project or ArcGIS Pro Layer File from a given path.

    If the path is already a Project, this is a no-op.
    """

    if isinstance(project, arcpy.mp.ArcGISProject):
        return project

    if isinstance(project, arcpy.mp.LayerFile):
        return project

    _, file_ext = os.path.splitext(project)

    if file_ext.lower() == ".aprx":
        return arcpy.mp.ArcGISProject(project)
    elif file_ext.lower() == ".lyrx":
        return arcpy.mp.LayerFile(project)
    else:
        raise ValueError("Unknown file type for given path: {}".format(project))


def _change_data_source(layer, new_props):
    try:
        # updating of connection properties should always be assumed to be partial updates
        # must build dictionaries of partial attributes in order to update
        # the dictionary has to also deal with multiple levels of source/destination, to deal with relationships
        def get_paired_conn_props(original, new):
            matched_conn_props = {}
            new_conn_props = {}
            skip_this_level = False

            if "source" in original:
                # Connection properties has the 'source' part of a relationship, going down to next level
                source_matched, source_updated_conn_props = get_paired_conn_props(original["source"], new)
                matched_conn_props["source"] = source_matched
                new_conn_props["source"] = source_updated_conn_props
                skip_this_level = True

            if "destination" in original:
                # Connection properties has the 'destination' part of a relationship, going down to next level
                destination_matched, destination_updated_conn_props = get_paired_conn_props(
                    original["destination"], new
                )
                matched_conn_props["destination"] = destination_matched
                new_conn_props["destination"] = destination_updated_conn_props
                skip_this_level = True

            if skip_this_level:
                return (matched_conn_props, new_conn_props)

            for k in new:
                if k in original:
                    if isinstance(original[k], Mapping) and isinstance(new[k], Mapping):
                        matched_conn_props[k], new_conn_props[k] = get_paired_conn_props(original[k], new[k])
                    elif k in ["dataset", "featureDataset"]:
                        # process magic field updating
                        new_value = new[k]

                        # determine if dataset value needs formatting
                        needs_format = eformat.needs_formatting(new[k])

                        if needs_format:
                            if original[k] is not None:
                                # pass original value for parts
                                dataset_parts = tokenise_table_name(original[k])

                                # format new value, if necessary
                                new_value = eformat.format(new[k], **dataset_parts)
                                matched_conn_props[k] = original[k]
                                new_conn_props[k] = new_value
                        else:
                            matched_conn_props[k] = original[k]
                            new_conn_props[k] = new_value
                    else:
                        matched_conn_props[k] = original[k]
                        new_conn_props[k] = new[k]
                else:
                    new_conn_props[k] = new[k]

            return (matched_conn_props, new_conn_props)

        # pull out any options from new_props
        transform_options = {}
        if "transformOptions" in new_props:
            transform_options = new_props.pop("transformOptions")

        matched_conn_props, new_conn_props = get_paired_conn_props(layer.connectionProperties, new_props)

        logger = _get_logger()
        logger.debug("Matched conn props: %s", matched_conn_props)
        logger.debug("New conn props    : %s", new_conn_props)

        layer.updateConnectionProperties(matched_conn_props, new_conn_props, validate=False)

        if hasattr(layer, "isBroken") and layer.isBroken:
            raise DataSourceUpdateError("Layer is now broken.", layer)

        # process any transform options
        # if statement tries to handle layers that do support definition queries, and tables that do (but tables don't
        # support the "supports" function)
        if "definitionQuery" in transform_options and (
            (hasattr(layer, "supports") and layer.supports("DEFINITIONQUERY")) or
            (not hasattr(layer, "supports") and hasattr(layer, "definitionQuery"))
        ):
            # must format/replace definition query
            def_query_opts = transform_options["definitionQuery"]
            layer.definitionQuery = format_def_query(
                layer.definitionQuery,
                identifier_case=def_query_opts.get("identifierCase"),
                identifier_quotes=def_query_opts.get("identifierQuotes")
            )

        # get the layer's CIM to process changes
        layer_cim = layer.getDefinition("V2")

        # get the table part of the CIM, unless the layer is a table already
        table_cim = layer_cim.featureTable if hasattr(layer_cim, "featureTable") else layer_cim

        # check if layer is a query layer, if so, don't continue, the definition can't be set safely
        if not is_query_layer(table_cim):
            if "fields" in transform_options:
                field_options = transform_options["fields"]

                # function for processing field name
                def get_field_name(field_name):
                    if "fieldNameMap" in field_options:
                        if field_name in field_options["fieldNameMap"]:
                            return field_options["fieldNameMap"][field_name]

                    if "fieldNameCase" in field_options:
                        field_name_template = "{}"
                        if field_options["fieldNameCase"].lower() == "lower":
                            field_name_template = "{:l}"
                        if field_options["fieldNameCase"].lower() == "upper":
                            field_name_template = "{:u}"

                        return eformat.format(field_name_template, field_name)

                    return field_name

                # handle field descriptions
                if hasattr(table_cim, "fieldDescriptions"):
                    for f in table_cim.fieldDescriptions:
                        f.fieldName = get_field_name(f.fieldName)

                # handle display fields (doesn't handle display field expressions)
                if hasattr(table_cim, "displayField"):
                    table_cim.displayField = get_field_name(table_cim.displayField)

            layer.setDefinition(layer_cim)

    except Exception as e:
        raise DataSourceUpdateError("Exception raised internally by ArcPy", layer, e)

    if hasattr(layer, "isBroken") and layer.isBroken:
        raise DataSourceUpdateError("Layer is now broken.", layer)


def _describe_layer_file(file_path):
    layer_file = arcpy.mp.LayerFile(file_path)

    # prevent repeated calls
    arcgis_version = get_arcgis_version()

    return {
        "filePath": file_path,
        "layers": [
            _native_describe_layer(
                {
                    "arcpy": l,
                    "index": index,
                    "prosdk": l.getDefinition("V3" if arcgis_version >= 3 else "V2")
                }
            ) for (index, l) in enumerate(layer_file.listLayers())
        ],
        "tables": [
            _native_describe_table(
                {
                    "arcpy": t,
                    "index": index,
                    "prosdk": t.getDefinition("V3" if arcgis_version >= 3 else "V2")
                }
            ) for (index, t) in enumerate(layer_file.listTables())
        ]
    }


def _describe_map(file_path):
    ao_map_document = _native_document_open(file_path)

    try:
        # build return object
        return {
            "filePath": file_path,
            "maps": [
                _native_describe_map(ao_map_document, map_frame) for map_frame in _native_list_maps(ao_map_document)
            ]
        }
    finally:
        _native_document_close(ao_map_document)


def _get_data_source_desc(layer_or_table):
    return layer_or_table.connectionProperties


def _get_logger():
    return logging.getLogger("arcpyext.mapping")


def _list_maps(proj):
    return proj.listMaps()


def _list_layers(proj, mp):
    return mp.listLayers()


def _list_tables(proj, mp):
    return mp.listTables()


def _native_add_data_connection_details(layer_table_parts, layer_table_details):
    l = layer_table_parts["arcpy"]
    if hasattr(l, "supports"):
        conn_props = l.connectionProperties if l.supports("CONNECTIONPROPERTIES") else None
    else:
        # this is a table, with no support for the "supports" function, but it should have connection properties
        conn_props = l.connectionProperties

    if not conn_props:
        return

    if "source" in conn_props:
        #this is a complex layer, e.g. has a join
        conn_props = conn_props.get("source")

    layer_table_details["datasetName"] = conn_props.get("dataset")
    layer_table_details["datasetType"] = conn_props.get("workspace_factory")

    conn_info = conn_props.get("connection_info", {})
    layer_table_details["database"] = conn_info.get("database")
    layer_table_details["server"] = conn_info.get("server")
    layer_table_details["service"] = conn_info.get("instance")
    layer_table_details["userName"] = conn_info.get("user")


def _native_document_close(proj_parts):
    proj_parts["prosdk"].close()
    proj_parts["prosdk"] = None
    proj_parts["arcpy"] = None


def _native_document_open(proj_path):
    proj = ProProject(proj_path)
    proj.open()

    return {"arcpy": arcpy.mp.ArcGISProject(proj_path), "prosdk": proj}


def _native_describe_fields(layer_or_table_fields):
    if not layer_or_table_fields:
        return None

    return [
        {
            "alias": f.alias,
            "index": i,
            "name": f.name if hasattr(f, "name") else f.fieldName,
            "type": None,  # Can't get this information yet
            "visible": f.visible
        } for i, f in enumerate(layer_or_table_fields)
    ]


def _native_describe_layer(layer_parts):

    # the "prosdk" variant in a layer from a layer file is actually the CIM object from getDefinition() in arcpy
    # as such, we have to so some work to get access to the right properties, due to naming differences
    # at some point, ideally, we'd port as much of this to pure-Python/arcpy as possible

    service_id = (
        layer_parts["prosdk"].service_id
        if hasattr(layer_parts["prosdk"], "service_id") else layer_parts["prosdk"].serviceLayerID
    )

    # Vector Tile layers are inherently service-based, but "isWebLayer" doesn't return true for them as of Pro 3.0.6 - probable bug
    is_service_layer = (
        layer_parts["arcpy"].isWebLayer or isinstance(layer_parts["prosdk"], ProVectorTileLayer)
        or (hasattr(layer_parts["prosdk"], "layerType") and layer_parts["prosdk"].layerType == "CIMVectorTileLayer")
    )

    feature_table = (
        layer_parts["prosdk"].feature_table if hasattr(layer_parts["prosdk"], "feature_table") else
        layer_parts["prosdk"].featureTable if hasattr(layer_parts["prosdk"], "featureTable") else None
    )

    feature_table_fields = None
    if hasattr(feature_table, "fields"):
        feature_table_fields = feature_table.fields
    elif hasattr(feature_table, "fieldDescriptions"):
        feature_table_fields = feature_table.fieldDescriptions

    # yapf: disable
    layer_details = {
        "dataSource": layer_parts["arcpy"].dataSource if layer_parts["arcpy"].supports("DATASOURCE") else None,
        "definitionQuery": layer_parts["arcpy"].definitionQuery if layer_parts["arcpy"].supports("DEFINITIONQUERY") else None,
        "fields": _native_describe_fields(feature_table_fields) if feature_table_fields else [],
        "index": layer_parts["index"],
        "isBroken": layer_parts["arcpy"].isBroken,
        "isFeatureLayer": layer_parts["arcpy"].isFeatureLayer,
        "isGroupLayer": layer_parts["arcpy"].isGroupLayer,
        "isNetworkAnalystLayer": layer_parts["arcpy"].isNetworkAnalystLayer,
        "isRasterLayer": layer_parts["arcpy"].isRasterLayer,
        "isRasterizingLayer": None,  # not implemented yet
        "isServiceLayer": is_service_layer,
        "longName": layer_parts["arcpy"].longName,
        "name": layer_parts["arcpy"].name,
        "serviceId": service_id,
        "visible": layer_parts["arcpy"].visible,

        # these get added with the call to _native_add_data_connection_details
        "database": None,
        "datasetName": None,
        "datasetType": None,
        "server": None,
        "service": None,
        "userName": None
    }
    # yapf: enable

    _native_add_data_connection_details(layer_parts, layer_details)

    return layer_details


def _native_describe_map(pro_proj, map_frame):

    return {
        "name": map_frame["arcpy"].name,
        "spatialReference": map_frame["prosdk"].spatial_reference.exportToString(),
        "layers": [_native_describe_layer(l) for l in _native_list_layers(pro_proj, map_frame)],
        "tables": [_native_describe_table(t) for t in _native_list_tables(pro_proj, map_frame)]
    }


def _native_describe_table(table_parts):
    table_details = {
        "dataSource": table_parts["arcpy"].dataSource,
        "definitionQuery": table_parts["arcpy"].definitionQuery,
        "fields": _native_describe_fields(table_parts["prosdk"].fields),
        "name": table_parts["arcpy"].name,
        "index": table_parts["index"],
        "isBroken": table_parts["arcpy"].isBroken,
        "serviceId": table_parts["prosdk"].service_id,

        # these get added with the call to _native_add_data_connection_details
        "database": None,
        "datasetName": None,
        "datasetType": None,
        "server": None,
        "service": None,
        "userName": None
    }

    _native_add_data_connection_details(table_parts, table_details)

    return table_details


def _native_list_layers(pro_proj, map_frame):
    arcpy_layers = map_frame["arcpy"].listLayers()
    prosdk_layers = map_frame["prosdk"].layers

    if not len(arcpy_layers) == len(prosdk_layers):
        raise ValueError("The number of layers from arcpy and from the ArcGIS Pro SDK are not the same.")

    layers = []

    for index, (arcpy_layer, prosdk_layer) in enumerate(zip(arcpy_layers, prosdk_layers)):
        if arcpy_layer == None:
            raise ValueError(
                "Could not get arpcy layer at index '{}' for map '{}'".format(index, map_frame["arcpy"].name)
            )

        if prosdk_layer == None:
            raise ValueError(
                "Could not get ArcGIS Pro SDK layer at index '{}' for map '{}'".format(index, map_frame["prosdk"].name)
            )

        if not arcpy_layer.name == prosdk_layer.name:
            raise ValueError(
                "Layer from arcpy and layer from ArcGIS Pro SDK do not have the same name, order likely not correct."
            )

        layers.append({"index": index, "arcpy": arcpy_layer, "prosdk": prosdk_layer})

    return layers


def _native_list_maps(pro_proj):
    arcpy_maps = pro_proj["arcpy"].listMaps()
    prosdk_maps = pro_proj["prosdk"].maps

    if not len(arcpy_maps) == len(prosdk_maps):
        raise ValueError("Length of native maps and length of ArcGIS Pro SDK maps is not the same.")

    maps = []

    # get prosdk maps by name, so we can match up (not guaranteed to return same order as arcpy)
    prosdk_maps_by_name = {m.name: m for m in prosdk_maps}
    for arcpy_map in arcpy_maps:
        prosdk_map = prosdk_maps_by_name.get(arcpy_map.name)
        if not prosdk_map:
            raise ValueError(
                "Map from arcpy ({}) could not be found by name in the ArcGIS Pro SDK, somthing unexpected happened.".
                format(arcpy_map.name)
            )
        maps.append({"arcpy": arcpy_map, "prosdk": prosdk_map})

    return maps


def _native_list_tables(pro_proj, map_frame):
    arcpy_tables = map_frame["arcpy"].listTables()
    prosdk_tables = map_frame["prosdk"].tables

    if not len(arcpy_tables) == len(prosdk_tables):
        raise ValueError("The number of layers from arcpy and from the ArcGIS Pro SDK are not the same.")

    tables = []

    for index, (arcpy_table, prosdk_table) in enumerate(zip(arcpy_tables, prosdk_tables)):
        if not arcpy_table.name == prosdk_table.name:
            raise ValueError(
                "Table from arcpy and table from ArcGIS Pro SDK do not have the same name, order likely not correct."
            )

        tables.append({"index": index, "arcpy": arcpy_table, "prosdk": prosdk_table})

    return tables
