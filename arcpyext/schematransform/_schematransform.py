import io
import json
import logging
import os
import shutil
import time

import arcpy


TABLE = "Table"
FEATURE_CLASS = "FeatureClass"
RELATIONSHIP = "RelationshipClass"
DOMAIN = "Domain"
CODED_VALUE = "CodedValue"
RANGE = "CodedValue"

OUTPUT_GDB = 1
OUTPUT_XML = 2

# Configure module logging
logger = logging.getLogger("arcpyext.schematransform")

def trace(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        name = ''

        for arg in args:
            if type(arg) is dict and "name" in arg:
                name = arg["name"]

        logger.debug("%r %r %2.2f sec" % (method.__name__, name, te-ts))
        return result

    return timed

def to_json(in_gdb, out_file):
    """
    Convert GDB into a JSON gdb schema representation.

    The JSON file can can be used as an intermediate file from which schema changes can be performed and from which
    new File GDB or XML Workspaces versions can be generated.
    """

    logger.info("Transform GDB schema to JSON, from '{0}' to '{1}'...".format(in_gdb, out_file))

    arcpy.env.workspace = in_gdb

    if not arcpy.Exists(in_gdb):
        raise IOError('Input GDB not found')

    logger.info("Profiling source gdb...")
    domains = arcpy.da.ListDomains(in_gdb)
    datasets = [c for c in arcpy.Describe(in_gdb).children]
    tables = [c for c in datasets if c.dataType == TABLE]
    fcs = [c for c in datasets if c.dataType == FEATURE_CLASS]
    rs =  [c for c in datasets if c.dataType == RELATIONSHIP]

    logger.info("Exporting...")
    with io.open(out_file, "w", encoding = "utf-8") as f:

        domains = list(map(lambda x: _domain_to_json(x), domains))
        fcs = list(map(lambda x: _fc_to_json(x), fcs))
        tables = list(map(lambda x: _t_to_json(x), tables))
        rs = list(map(lambda x: _r_to_json(x), rs))

        _json_to_file(f,  {
            'schema': domains + fcs + tables + rs
        })

    logger.info("Transform done.")

def to_gdb(in_file, out_gdb):
    """
    Convert a JSON gdb schema representation into a file/sde geodatabase
    """

    logger.info("Transform JSOB to GDB, from '{0}' to '{1}'...".format(in_file, out_gdb))

    if not arcpy.Exists(in_file):
        logger.debug("Input file: {0}".format(in_file))
        raise IOError("Input file not found")

    if arcpy.Exists(out_gdb):
        shutil.rmtree(out_gdb, ignore_errors = False)

    logger.info("Creating output File GDB...")
    out_gdb_mem = "in_memory"
    arcpy.env.workspace = out_gdb
    out_path = os.path.dirname(out_gdb)
    out_name = os.path.basename(out_gdb)
    arcpy.CreateFileGDB_management(out_path, out_name)

    with open(in_file) as f:

        logger.info("Parsing json")
        schema = json.load(f, encoding = "utf-8")

        # Domains
        logger.info("Domains")
        for x in schema['schema']:
            if x['type'] == DOMAIN:
                _json_to_domain(OUTPUT_GDB, out_gdb, x)

        # Enable in-memory mode
        arcpy.env.workspace = out_gdb_mem

        # Tables
        logger.info("Tables")
        for x in schema['schema']:
            if x['type'] == TABLE:
                _json_to_t(OUTPUT_GDB, out_gdb_mem, x)
            elif x['type'] == FEATURE_CLASS:
                _json_to_fc(OUTPUT_GDB, out_gdb_mem, x)

        # Move tables from memory to disk
        for x in schema['schema']:
            if x['type'] == TABLE:
                _t_from_memory_to_disk(out_gdb_mem, out_gdb, x)
            elif x['type'] == FEATURE_CLASS:
                _fc_from_memory_to_disk(out_gdb_mem, out_gdb, x)

        # Disable in-memory mode
        arcpy.env.workspace = out_gdb

        # Add global ID columns (not supported by in-memory workspaces)
        logger.info("Global Ids'")
        for x in schema['schema']:
            if x['type'] == TABLE or x['type'] == FEATURE_CLASS:
                _add_global_id(out_gdb, x)

        # Add global ID columns (not supported by in-memory workspaces)
        logger.info("Bind domains")
        for x in schema['schema']:
            if x['type'] == TABLE or x['type'] == FEATURE_CLASS:
                _bind_domain(out_gdb, x)

        # Indexes
        logger.info("Indexes")
        for x in schema['schema']:
            if x['type'] == TABLE or x['type'] == FEATURE_CLASS:
                _add_indices(OUTPUT_GDB, out_gdb, x)

        # Relationships
        logger.info("Relationships")
        for x in schema['schema']:
            if x['type'] == RELATIONSHIP:
                _add_r(out_gdb, x)

    logger.info("Transform done.")

def to_xml(in_file, out_file):
    """
    Convert JSON gdb schema into an XML Workspace

    Status: Incomplete. I've only been able to successfully output domains and tables (without indexes, which have 
    broken run-time). I choose to use string templates for now given how verbose the xml libraries are to use.
    """

    logger.info("Transform JSON to XML Workspace, from '{0}'' to '{1}'...")

    if not arcpy.Exists(in_file):
        logger.error("Input file not found: {0}".format(in_file))
        raise IOError('Input file not found')

    if arcpy.Exists(out_file):
        os.remove(out_file)

    logger.info("Creating output xml workspace")
    with open(in_file) as f:

        logger.info("Parsing json")
        schema = json.load(f, encoding = "utf-8")

        with io.open(out_file, 'w', encoding = "utf-8") as fo:

            _xml_to_file(
                fo,
                """<?xml version="1.0" encoding="UTF-8"?>
                    <esri:Workspace xmlns:esri='http://www.esri.com/schemas/ArcGIS/10.3' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:xs='http://www.w3.org/2001/XMLSchema'>
                        <WorkspaceDefinition xsi:type='esri:WorkspaceDefinition'>
                        <WorkspaceType>esriLocalDatabaseWorkspace</WorkspaceType>
                        <Version></Version>"""
            )

            # Domains
            logger.info("Domains")
            _xml_to_file(fo, """<Domains xsi:type='esri:ArrayOfDomain'>""")
            for x in schema['schema']:
                if x['type'] == DOMAIN:
                    res = _json_to_domain(OUTPUT_XML, None, x)
                    _xml_to_file(fo, res)

            _xml_to_file(fo, """</Domains>""")

            # Tables
            _xml_to_file(fo, """<DatasetDefinitions xsi:type='esri:ArrayOfDataElement'>""")
            logger.info("Tables")
            for x in schema['schema']:
                if x['type'] == TABLE:
                    res = _json_to_t(OUTPUT_XML, None, x)
                    _xml_to_file(fo, res)
                # elif x['type'] == FEATURE_CLASS:
                #     _json_to_fc(OUTPUT_XML, None, x)
            _xml_to_file(fo, """</DatasetDefinitions>""")

            _xml_to_file(
                fo,
                """</WorkspaceDefinition>
                   <WorkspaceData xsi:type='esri:WorkspaceData'></WorkspaceData>
                </esri:Workspace>"""
            )


    logger.info("Transform done.")

###############################################################################
# PRIVATE FUNCTIONS
###############################################################################

#----------------
# To XML methods
#----------------
def _xml_to_file(f, o):
    f.write(unicode(o))

#----------------
# To JSON methods
#----------------

def _json_to_file(f, o):
    f.write(json.dumps(o, sort_keys=False, indent=4, ensure_ascii=False))

def _fields_to_json(fields):
    return [
        {
            'name': v.name,
            'aliasName': v.aliasName,
            'type': v.type,
            'defaultValue': v.defaultValue,
            'domain': v.domain,
            'editable': v.editable,
            'nullable': v.isNullable,
            'length': v.length,
            'precision': v.precision,
            'required': v.required,
            'scale': v.scale
        } for v in fields
    ]

def _indexes_to_json(indexes):
    return [
        {
            'name': v.name,
            'fields': _fields_to_json(v.fields),
            'ascending': v.isAscending,
            'unique': v.isUnique
        } for v in indexes
    ]


def _t_to_json(x):

    return {
        'name': x.name,
        'type': TABLE,
        'fields': _fields_to_json(x.fields),
        'indexes': _indexes_to_json(x.indexes)
    }

def _fc_to_json(x):
    res = {
        'name': x.name,
        'type': FEATURE_CLASS,
        'fields': _fields_to_json(x.fields),
        'indexes': _indexes_to_json(x.indexes),
        'geometryField': x.shapeFieldName,
        'geometryType': x.shapeType,
        'sr': x.spatialReference.exportToString(),
    }

    return res

def _r_to_json(x):
    res = {
        'name': x.name,
        'type': RELATIONSHIP,
        'originClassNames': x.originClassNames,
        'destinationClassNames': x.destinationClassNames,
        'originClassKeys': x.originClassKeys,
        'destinationClassKeys': x.destinationClassKeys,
        'cardinality': x.cardinality,
        'isComposite': x.isComposite
    }

    return res

# @see http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-data-access/domain.htm
def _domain_to_json(x):
    res = {
        'name': x.name,
        'type': DOMAIN,
        'subType': x.domainType,
        'fieldType': x.type,
        'description': x.description
    }

    try:
        if x.domainType == CODED_VALUE:
            res['values'] = [{'k': v[0],  'v': v[1]} for v in x.codedValues.items()]
        elif x.domainType == RANGE:
            res['min'] = x.range[0]
            res['max'] = x.range[1]
    except:
        logger.error("Unexpected error: {0}".format(sys.exc_info()[0]))
        res['error'] = 'Error'

    return res

#---------------
# To GDB methods
#---------------

@trace
def _add_fields(output_target, out_gdb, x):

    if output_target == OUTPUT_GDB:

        for f in x['fields']:
            type = _json_type_to_gdb_type(f['type'])
            if type in ['TEXT', 'FLOAT', 'DOUBLE', 'SHORT', 'LONG', 'DATE', 'BLOB', 'RASTER', 'GUID']:
                arcpy.AddField_management(
                    in_table=out_gdb + '/' + x['name'],
                    field_name=f['name'],
                    field_type=type,
                    field_alias=f['aliasName'],
                    field_length=f['length'],
                    field_precision=f['precision'],
                    field_scale=f['scale'],
                    field_is_nullable='NULLABLE' if f['nullable'] else 'NON_NULLABLE',
                    field_is_required='REQUIRED' if f['required'] else 'NON_REQUIRED',
                    field_domain=f['domain'] if f['domain'] else 'None'
                )

    elif output_target == OUTPUT_XML:

        return list(map(lambda f:
            """<Field xsi:type="esri:Field">
                <Name>%(name)s</Name>
                <AliasName>%(alias)s</AliasName>
                <Type>%(type)s</Type>
                <IsNullable>%(nullable)s</IsNullable>
                <Length>%(length)s</Length>
                <Precision>%(precision)s</Precision>
                <Scale>%(scale)s</Scale>
                <Required>%(required)s</Required>
                <Editable>%(editable)s</Editable>
                <ModelName>%(name)s</ModelName>
            </Field>""" % {
                'name': f['name'],
                'alias': f['aliasName'],
                'type': _json_type_to_xml_type(f['type']),
                'length': f['length'],
                'nullable': 'true' if f['nullable'] else 'false',
                'editable': 'true' if f['editable'] else 'false',
                'required': 'true' if f['required'] else 'false',
                'scale': f['scale'] or 0,
                'precision': f['precision'] or 0
            }
        , x['fields']))


@trace
def _add_global_id(out_gdb, x):
    for f in x['fields']:
        type = _json_type_to_gdb_type(f['type'])
        if type == 'GLOBALID':
            arcpy.AddGlobalIDs_management(in_datasets=[out_gdb + '/' + x['name']])

@trace
def _bind_domain(out_gdb, x):
    for f in x['fields']:
        if f['domain']:
            logger.info(f['domain'])
            arcpy.AssignDomainToField_management(
                in_table=out_gdb + '/' + x['name'],
                field_name=f['name'],
                domain_name=f['domain'])

@trace
def _add_indices(output_target, out_gdb, x):

    if output_target == OUTPUT_GDB:
        for i in x['indexes']:
            if i['fields'][0]['type'] not in ['OID', 'Geometry', 'GlobalID']:
                arcpy.AddIndex_management(
                    in_table=out_gdb + '/' + x['name'],
                    index_name=i['name'],
                    fields=[f['name'] for f in i['fields']],
                    unique='UNIQUE' if i['unique'] else 'NON_UNIQUE',
                    ascending='ASCENDING' if i['ascending'] else 'NON_ASCENDING')

    elif output_target == OUTPUT_XML:

        return list(map(lambda i:
            """<Index xsi:type="esri:Index">
                    <Name>%(name)s</Name>
                    <IsUnique>%(isUnique)s</IsUnique>
                    <IsAscending>%(isAscending)s</IsAscending>
                    <Fields xsi:type="esri:Fields">
                        <FieldArray xsi:type="esri:ArrayOfField">
                            %(fields)s
                        </FieldArray>
                    </Fields>
                </Index>""" % {
                'name': i['name'],
                'isUnique':'true' if i['unique'] else 'false',
                'isAscending':'true' if i['ascending'] else 'false',
                'fields':  "\n".join(_add_fields(output_target, None, i))
            }
        , x['indexes']))

@trace
def _add_r(out_gdb, x):

    origin=x['originClassNames'][0]
    destination=x['destinationClassNames'][0]
    originField=x['originClassKeys'][0][0]
    destinationField=x['originClassKeys'][1][0]
    logger.debug("{0} {1} {2} {3}".format(origin, originField, destination, destinationField))

    arcpy.CreateRelationshipClass_management(
        out_relationship_class=x['name'],
        origin_table=origin,
        destination_table=destination,
        relationship_type='COMPOSITE' if x['isComposite'] else 'SIMPLE',
        forward_label='To child',
        backward_label='To parent',
        message_direction='NONE',
        cardinality=_normalise_cardinality(x['cardinality']),
        attributed='NONE',
        origin_primary_key=originField,
        origin_foreign_key=destinationField
    )

@trace
def _json_to_t(output_target, out_gdb, x):

    if output_target == OUTPUT_GDB:

        arcpy.CreateTable_management(out_gdb, x['name'])
        _add_fields(output_target, out_gdb, x)

    elif output_target == OUTPUT_XML:

        template = """<DataElement xsi:type="esri:DETable">
                <CatalogPath>/OC= %(name)s</CatalogPath>
                <Name>%(name)s</Name>
                <MetadataRetrieved>false</MetadataRetrieved>
                <DatasetType>esriDTTable</DatasetType>
                <DSID>%(dsId)s</DSID>
                <Versioned>false</Versioned>
                <CanVersion>false</CanVersion>
                <ConfigurationKeyword />
                <HasOID>true</HasOID>
                <OIDFieldName>OBJECTID</OIDFieldName>
                <Fields xsi:type="esri:Fields">
                    <FieldArray xsi:type="esri:ArrayOfField">
                        %(fields)s
                    </FieldArray>
                </Fields>
                <Indexes xsi:type="esri:Indexes">
                    <IndexArray xsi:type="esri:ArrayOfIndex">
                        %(indexes)s
                    </IndexArray>
                </Indexes>
                <!--
                <CLSID>{7A566981-C114-11D2-8A28-006097AFF44E}</CLSID>
                -->
                <EXTCLSID />
                <!--
                <RelationshipClassNames xsi:type="esri:Names">
                <Name>LR_SRM_WA_R_WF_ASSET</Name>
                </RelationshipClassNames>
                -->
                <AliasName>LR_SRM_WA_WF_ASSET</AliasName>
                <ModelName />
                <HasGlobalID>false</HasGlobalID>
                <GlobalIDFieldName />
                <RasterFieldName />
                <ExtensionProperties xsi:type="esri:PropertySet">
                <PropertyArray xsi:type="esri:ArrayOfPropertySetProperty" />
                </ExtensionProperties>
                <ControllerMemberships xsi:type="esri:ArrayOfControllerMembership" />
                <EditorTrackingEnabled>false</EditorTrackingEnabled>
                <CreatorFieldName />
                <CreatedAtFieldName />
                <EditorFieldName />
                <EditedAtFieldName />
                <IsTimeInUTC>true</IsTimeInUTC>
                <ChangeTracked>false</ChangeTracked>
                <FieldFilteringEnabled>false</FieldFilteringEnabled>
                <FilteredFieldNames xsi:type="esri:Names" />
            </DataElement>"""

        return template % {
            'dsId': 0,
            'name': x['name'],
            'type': _json_type_to_xml_type(x['type']),
            'fields': "\n".join(_add_fields(output_target, out_gdb, x)),
            'indexes': "\n".join(_add_indices(output_target, out_gdb, x))
        }

@trace
def _json_to_fc(output_target, out_gdb, x):
    if output_target == OUTPUT_GDB:
        arcpy.CreateFeatureclass_management(
            out_gdb,
            x['name'],
            geometry_type=x['geometryType'],
            spatial_reference=arcpy.SpatialReference().loadFromString(x['sr']))

        _add_fields(output_target, out_gdb, x)

@trace
def _json_to_domain(output_target, out_gdb, x):

    if output_target == OUTPUT_GDB:

        # Process: Create the coded value domain
        arcpy.CreateDomain_management(
            out_gdb,
            x['name'],
            field_type=_json_type_to_gdb_type(x['fieldType']),
            domain_type='CODED' if x['subType'] == 'CodedValue' else 'RANGE',
            domain_description=x['description'])

        for kv in x['values']:
            arcpy.AddCodedValueToDomain_management(out_gdb, x['name'], kv['k'], kv['v'])

    elif output_target == OUTPUT_XML:

        template = """<Domain xsi:type='esri:CodedValueDomain'>
                <DomainName>%(name)s</DomainName>
                <FieldType>%(type)s</FieldType>
                <MergePolicy>esriMPTDefaultValue</MergePolicy>
                <SplitPolicy>esriSPTDefaultValue</SplitPolicy>
                <Description></Description>
                <Owner></Owner>
                <CodedValues xsi:type='esri:ArrayOfCodedValue'>
                    %(domains)s
                </CodedValues>
            </Domain>"""

        domains = list(map(lambda kv:
            """<CodedValue xsi:type='esri:CodedValue'>
                <Name>%(v)s</Name>
                <Code xsi:type='xs:%(type)s'>%(k)s</Code>
            </CodedValue>""" % {'type': _json_type_to_xml_attr_type(x['fieldType']), 'k': kv['k'], 'v': kv['v']}
        , x['values']))

        return template % {'name': x['name'], 'type': _json_type_to_xml_type(x['fieldType']), 'domains': "\n".join(domains) }

@trace
def _t_from_memory_to_disk(in_gdb, out_gdb, x):
    arcpy.CreateTable_management(
        out_path=out_gdb,
        out_name=x['name'],
        template=in_gdb + '/' + x['name'])

@trace
def _fc_from_memory_to_disk(in_gdb, out_gdb, x):
    arcpy.CreateFeatureclass_management(
        out_path=out_gdb,
        out_name=x['name'],
        template=in_gdb + '/' + x['name'])

def _json_type_to_gdb_type(type):
    # type = type.lower()
    if type == 'String':
        return 'TEXT'
    elif type == 'Integer':
        return 'LONG'
    elif type == 'SmallInteger':
        return 'SHORT'
    elif type == 'Float':
        return 'FLOAT'
    elif type == 'Double':
        return 'DOUBLE'
    elif type == 'Date':
        return 'DATE'
    elif type == 'GlobalID':
        return 'GLOBALID'
    return type

def _json_type_to_xml_type(type):
    # type = type.lower()
    if type == 'String':
        return 'esriFieldTypeString'
    elif type == 'Text':
        return 'esriFieldTypeString'
    elif type == 'Integer':
        return 'esriFieldTypeInteger'
    elif type == 'Long':
        return 'esriFieldTypeInteger'
    elif type == 'SmallInteger':
        return 'esriFieldTypeSmallInteger'
    elif type == 'Short':
        return 'esriFieldTypeSmallInteger'
    elif type == 'Float':
        return 'esriFieldTypeFloat'
    elif type == 'Double':
        return 'esriFieldTypeDouble'
    elif type == 'Date':
        return 'esriFieldTypeDate'
    elif type == 'GlobalID':
        return 'esriFieldTypeGlobalID'
    elif type == 'OID':
        return 'esriFieldTypeOID'
    return type

def _json_type_to_xml_attr_type(type):
    # type = type.lower()
    if type == 'String':
        return 'string'
    elif type == 'Text':
        return 'string'
    elif type == 'Integer':
        return 'int'
    elif type == 'Long':
        return 'int'
    elif type == 'Short':
        return 'short'
    elif type == 'SmallInteger':
        return 'short'
    return type

def _normalise_cardinality(type):
    # type = type.lower()
    if type == 'OneToMany':
        return 'ONE_TO_MANY'
    elif type == 'OneToOne':
        return 'ONE_TO_ONE'
    elif type == 'ManyToMany':
        return 'MANY_TO_MANY'
    return type