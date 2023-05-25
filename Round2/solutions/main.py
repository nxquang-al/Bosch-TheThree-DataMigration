import json
import xmltodict


def find_keys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in find_keys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in find_keys(j, kv):
                yield x


def mapping(spec_attrs, spec_obj_values, attr_key):
    result = []

    HEAD_NAME = 'ATTRIBUTE'
    DEFINITION_TAG = 'DEFINITION'
    IDENTIFIER_TAG = '@IDENTIFIER'

    attr_name = attr_key.split('-')[-1]
    attrs = spec_obj_values.get(attr_key)

    if isinstance(attrs, dict):
        attrs = [attrs]

    for attr in attrs:
        for def_attr in spec_attrs[f'{HEAD_NAME}-{DEFINITION_TAG}-{attr_name}']:
            attr_ref = attr[DEFINITION_TAG][f'{HEAD_NAME}-{DEFINITION_TAG}-{attr_name}-REF']
            if attr_ref == def_attr.get(IDENTIFIER_TAG):
                key = ''
                value = attr.get('THE-VALUE')
                if value is None:
                    value = attr.get('@THE-VALUE')

                match def_attr.get('@LONG-NAME'):
                    # XHTML
                    case 'ReqIF.Text':
                        key = 'ReqIF.Text'
                        value = xmltodict.unparse(value, pretty=True)[39:]
                    case 'ReqIF.Name':
                        key = 'Title'
                        value = value['div']['#text']
                    case 'ReqIF.ChapterName':
                        key = 'ReqIF.Text'
                        value = xmltodict.unparse(value, pretty=True)[39:]

                    # DATE
                    case 'ReqIF.ForeignCreatedOn':
                        key = 'Created On'
                    case 'ReqIF.ForeignModifiedOn':
                        key = 'Modified On'

                    # STRING
                    case 'ReqIF.ForeignID':
                        key = 'Identifier'
                        value = int(value)
                    case 'ReqIF.ForeignCreatedBy':
                        key = 'Creator'
                    case 'ReqIF.ForeignModifiedBy':
                        key = 'Contributor'

                    # ENUMERATION
                    case 'Artifact Format':
                        key = ''

                    # OTHERWISE
                    case _:
                        key = ''
                        if attr_name == 'STRING':
                            key = def_attr.get('@LONG-NAME')

                        if attr_name == 'ENUMERATION':
                            key = def_attr.get('@LONG-NAME')
                            value = find_enum_value(
                                attr['VALUES']['ENUM-VALUE-REF'])

                if key != '':
                    result.append({key: value})
    return result


def find_enum_value(ref_value):
    dt_def_enum = list(
        find_keys(data_dict, 'DATATYPE-DEFINITION-ENUMERATION'))[0]

    values = []
    for dt in dt_def_enum:
        for dump in dt['SPECIFIED-VALUES']['ENUM-VALUE']:
            values.append(dump)

    for value in values:
        if value['@IDENTIFIER'] == ref_value:
            return value['@LONG-NAME']


def zip_artifact(spec_object, spec_type):

    artifact_info = {}

    type_ref = spec_object['TYPE']['SPEC-OBJECT-TYPE-REF']
    type_object = find_type_spec(spec_type, type_ref)

    artifact_info.update(
        {"Attribute Type": type_object['@LONG-NAME'], 'Description': ''})

    for key in spec_object['VALUES'].keys():
        for info in mapping(type_object['SPEC-ATTRIBUTES'], spec_object['VALUES'], attr_key=key):
            artifact_info.update(info)

    return dict(sorted(artifact_info.items()))


def find_type_spec(spec_type, ref):
    for type in spec_type:
        if type['@IDENTIFIER'] == ref:
            return type


def get_spec_object_ref_hierarchy(data, hierarchy=None):
    if hierarchy is None:
        hierarchy = []

    if isinstance(data, list):
        for item in data:
            get_spec_object_ref_hierarchy(item, hierarchy)

    elif isinstance(data, dict):
        object_ref = data.get("OBJECT", {}).get("SPEC-OBJECT-REF")
        if object_ref:
            hierarchy.append(object_ref)

        children = data.get("CHILDREN")

        if children:
            get_spec_object_ref_hierarchy(
                children.get('SPEC-HIERARCHY'), hierarchy)

    return hierarchy


if __name__ == '__main__':
    data_dict = xmltodict.parse(open("example.xml").read())

    spec = list(find_keys(data_dict, 'SPECIFICATIONS'))[0]['SPECIFICATION']

    module_name = spec['@LONG-NAME']
    module_type = list(
        find_keys(dict(data_dict), 'SPECIFICATION-TYPE'))[0]['@LONG-NAME']

    spec_objects = list(
        find_keys(dict(data_dict), 'SPEC-OBJECTS'))[0]['SPEC-OBJECT']
    spec_type = list(find_keys(dict(data_dict), 'SPEC-OBJECT-TYPE'))[0]

    list_artifact_info = []

    data = get_spec_object_ref_hierarchy(spec['CHILDREN']['SPEC-HIERARCHY'])

    for id in data:
        for obj in spec_objects:
            if id == obj['@IDENTIFIER']:
                list_artifact_info.append(zip_artifact(obj, spec_type))

    json_data = json.dumps({
        "Module Name": module_name,
        "Module Type": module_type,
        "List Artifact Info": list_artifact_info
    })

    with open("test.json", "w") as json_file:
        json_file.write(json_data)
