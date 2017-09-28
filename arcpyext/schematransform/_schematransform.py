import arcpy
import json
import io 
import os
import shutil
import time 

TABLE = "Table"
FEATURE_CLASS = "FeatureClass"
RELATIONSHIP = "RelationshipClass"
DOMAIN = "Domain"
CODED_VALUE = 'CodedValue'
RANGE = 'CodedValue'

def trace(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        name = '' 

        for arg in args:
            if 'name' in arg:
                name = arg['name']

        # print '%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts)
        print '%r %r %2.2f sec' % (method.__name__, name, te-ts)
        return result

    return timed

def to_json(in_gdb, out_file):
    print 'Transform gdb schema to json'
    print 'From: %s' % in_gdb
    print 'To: %s' % out_file

    arcpy.env.workspace = in_gdb

    if not arcpy.Exists(in_gdb):
        raise Exception('Input gdb not found')

    print 'Profiling source gdb'
    domains = arcpy.da.ListDomains(in_gdb)
    datasets = [c for c in arcpy.Describe(in_gdb).children]  
    tables = [c for c in datasets if c.dataType == TABLE]  
    fcs = [c for c in datasets if c.dataType == FEATURE_CLASS]  
    rs =  [c for c in datasets if c.dataType == RELATIONSHIP]  

    print 'Exporting'
    with io.open(out_file, 'w', encoding='utf-8') as f:

        domains = list(map(lambda x: _domain_to_json(x), domains))
        fcs = list(map(lambda x: _fc_to_json(x), fcs))
        tables = list(map(lambda x: _t_to_json(x), tables))
        rs = list(map(lambda x: _r_to_json(x), rs))

        _json_to_file(f,  {
            'schema': domains + fcs + tables + rs
        })
    
    print 'Done'

def to_gdb(in_file, out_gdb):
    print 'Transform json to gdb'
    print 'From: %s' % in_file
    print 'To: %s' % out_gdb

    if not arcpy.Exists(in_file):
        print in_file
        raise Exception('Input file not found')

    if arcpy.Exists(out_gdb):
        shutil.rmtree(out_gdb, ignore_errors=False) 

    print 'Creating output gdb'  
    out_gdb_mem = "in_memory"
    arcpy.env.workspace = out_gdb
    out_path = os.path.dirname(out_gdb)
    out_name = os.path.basename(out_gdb)
    arcpy.CreateFileGDB_management(out_path, out_name)

    with open(in_file) as f:

        print 'Parsing json'
        schema = json.load(f, encoding='utf-8')

        # Domains
        print 'Domains'
        for x in schema['schema']:
            if x['type'] == DOMAIN:
                _json_to_domain(out_gdb, x)    

        # Enable in-memory mode
        arcpy.env.workspace = out_gdb_mem

        # Tables
        print 'Tables'
        for x in schema['schema']:
            if x['type'] == TABLE:
                _json_to_t(out_gdb_mem, x)
            elif x['type'] == FEATURE_CLASS:
                _json_to_fc(out_gdb_mem, x)

        # Move tables from memory to disk
        for x in schema['schema']:
            if x['type'] == TABLE:
                _t_from_memory_to_disk(out_gdb_mem, out_gdb, x)
            elif x['type'] == FEATURE_CLASS:
                _fc_from_memory_to_disk(out_gdb_mem, out_gdb, x)                       

        # Disable in-memory mode
        arcpy.env.workspace = out_gdb             

        # Add global ID columns (not supported by in-memory workspaces)
        print 'Global Ids'
        for x in schema['schema']:
            if x['type'] == TABLE or x['type'] == FEATURE_CLASS:
                _add_global_id(out_gdb, x)

        # Add global ID columns (not supported by in-memory workspaces)
        print 'Bind domains'
        for x in schema['schema']:
            if x['type'] == TABLE or x['type'] == FEATURE_CLASS:
                _bind_domain(out_gdb, x)

        # Indexes
        print 'Indexes'
        for x in schema['schema']:
            if x['type'] == TABLE or x['type'] == FEATURE_CLASS:
                _add_indices(out_gdb, x)

        # Relationships
        print 'Relationships'
        for x in schema['schema']:
            if x['type'] == RELATIONSHIP:
                _add_r(out_gdb, x)
    
    print 'Done'    

###############################################################################
# PRIVATE FUNCTIONS
###############################################################################

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
        print 'Unexpected error:', sys.exc_info()[0]
        res['error'] = 'Error'
    
    return res 

#---------------
# To GDB methods
#---------------

@trace
def _add_fields(out_gdb, x):
    for f in x['fields']:
        type = _normalise_data_type(f['type'])
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

@trace
def _add_global_id(out_gdb, x):
    for f in x['fields']:
        type = _normalise_data_type(f['type'])
        if type == 'GLOBALID':
            arcpy.AddGlobalIDs_management(in_datasets=[out_gdb + '/' + x['name']])        

@trace
def _bind_domain(out_gdb, x):
    for f in x['fields']:
        if f['domain']:
            print f['domain']
            arcpy.AssignDomainToField_management(
                in_table=out_gdb + '/' + x['name'], 
                field_name=f['name'],
                domain_name=f['domain'])

@trace
def _add_indices(out_gdb, x):
    for i in x['indexes']:
        if i['fields'][0]['type'] not in ['OID', 'Geometry', 'GlobalID']:
            arcpy.AddIndex_management(
                in_table=out_gdb + '/' + x['name'], 
                index_name=i['name'], 
                fields=[f['name'] for f in i['fields']], 
                unique='UNIQUE' if i['unique'] else 'NON_UNIQUE', 
                ascending='ASCENDING' if i['ascending'] else 'NON_ASCENDING')            

@trace
def _add_r(out_gdb, x):

    origin=x['originClassNames'][0]
    destination=x['destinationClassNames'][0]
    originField=x['originClassKeys'][0][0]
    destinationField=x['originClassKeys'][1][0]
    print '%s %s %s %s' % (origin, originField, destination, destinationField)

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
def _json_to_t(out_gdb, x):
    arcpy.CreateTable_management(out_gdb, x['name'])
    _add_fields(out_gdb, x)

@trace
def _json_to_fc(out_gdb, x):
    arcpy.CreateFeatureclass_management(
        out_gdb, 
        x['name'],
        geometry_type=x['geometryType'],
        spatial_reference=arcpy.SpatialReference().loadFromString(x['sr']))

    _add_fields(out_gdb, x)

@trace
def _json_to_domain(out_gdb, x):
    
    # Process: Create the coded value domain
    arcpy.CreateDomain_management(
        out_gdb, 
        x['name'], 
        field_type=_normalise_data_type(x['fieldType']), 
        domain_type='CODED' if x['subType'] == 'CodedValue' else 'RANGE',
        domain_description=x['description'])

    for kv in x['values']:        
        arcpy.AddCodedValueToDomain_management(out_gdb, x['name'], kv['k'], kv['v'])    

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

def _normalise_data_type(type):
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


def _normalise_cardinality(type):
    # type = type.lower()
    if type == 'OneToMany':
        return 'ONE_TO_MANY'
    elif type == 'OneToOne':
        return 'ONE_TO_ONE'
    elif type == 'ManyToMany':
        return 'MANY_TO_MANY'
    return type              