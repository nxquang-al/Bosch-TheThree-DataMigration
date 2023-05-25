import json
import xmltodict


INP_SRC = 'example.xml'
OUT_SRC = 'test.json'

IDENTIFIER_TAG = '@IDENTIFIER'
NAME_TAG = '@LONG-NAME'


def find_keys(node, kv):
    """
    The function recursively searches for a specific key in a nested dictionary and returns its value.

    :param node: The node parameter is the current node being searched in the recursive function. It can
    be either a dictionary or a list
    :param kv: kv stands for "key value" and is a parameter that represents the key that we want to
    search for in a nested dictionary or list. The function "find_keys" recursively searches through the
    nested structure and yields the values associated with the specified key
    """
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


def refactor_key_value(key, value, attr_name, attr):
    match key:
        # XHTML
        # - ReqIF.ChapterName is ReqIF.Text in the "Heading"
        case 'ReqIF.Text':
            key = 'ReqIF.Text'
            value = xmltodict.unparse(value, pretty=True)[39:]
        case 'ReqIF.Name':
            key = 'Title'
            value = value['div']['#text']
        case 'ReqIF.ChapterName':
            key = 'ReqIF.Text'
            value = xmltodict.unparse(value, pretty=True)[39:]
            print(value)

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
        # - Artifact Format not needed to collect
        case 'Artifact Format':
            key = None

        # OTHERWISE
        case _:
            if attr_name == 'STRING':
                key = key

            elif attr_name == 'ENUMERATION':
                value = find_enum_value(
                    attr['VALUES']['ENUM-VALUE-REF'])

            else:
                key = None

    return key, value


def mapping_attr_definition(spec_attrs, spec_obj_values, attr_key):
    result = []

    attrs = spec_obj_values.get(attr_key)
    attr_name = attr_key.split('-')[-1]

    DEFINITION_TAG = f'ATTRIBUTE-DEFINITION-{attr_name}'

    if isinstance(attrs, dict):
        attrs = [attrs]

    for attr in attrs:
        for def_attr in spec_attrs.get(DEFINITION_TAG):
            attr_ref = attr['DEFINITION'][f'{DEFINITION_TAG}-REF']

            if attr_ref == def_attr.get(IDENTIFIER_TAG):
                key = def_attr.get(NAME_TAG)
                value = attr.get('THE-VALUE')

                if value is None:
                    value = attr.get('@THE-VALUE')

                key, value = refactor_key_value(key, value, attr_name, attr)

                if key is not None:
                    result.append({key: value})

    return result


def find_enum_value(ref_value):
    """
    The function finds the long name of an enum value given its identifier.

    :param ref_value: The input parameter "ref_value" is a string representing the identifier of an
    enumerated value that we want to find the corresponding long name for
    :return: the `@LONG-NAME` attribute of the `ENUM-VALUE` element in the `SPECIFIED-VALUES` element of
    the `DATATYPE-DEFINITION-ENUMERATION` element that has an `@IDENTIFIER` attribute equal to the
    `ref_value` parameter passed to the function.
    """
    dt_def_enum = list(
        find_keys(data_dict, 'DATATYPE-DEFINITION-ENUMERATION'))[0]

    values = []
    for dt in dt_def_enum:
        for dump in dt['SPECIFIED-VALUES']['ENUM-VALUE']:
            values.append(dump)

    for value in values:
        if value.get(IDENTIFIER_TAG) == ref_value:
            return value.get(NAME_TAG)


def zip_artifact(spec_object, spec_type):
    """
    The function takes a specification object and type, and returns a dictionary of artifact
    information.

    :param spec_object: The spec_object parameter is a dictionary that represents a specification
    object. It contains information about the object's type, values, and other attributes
    :param spec_type: The type of specification being used (e.g. "DOORS", "SysML", etc.)
    :return: a dictionary containing information about an artifact specified by the input `spec_object`
    and `spec_type`. The dictionary includes the attribute type and description, as well as information
    about the artifact's values based on the mapping function. The dictionary is sorted by key.
    """

    artifact_info = {}

    type_ref = spec_object['TYPE']['SPEC-OBJECT-TYPE-REF']
    type_object = find_type_spec(spec_type, type_ref)

    artifact_info.update(
        {"Attribute Type": type_object.get(NAME_TAG), 'Description': ''})

    for key in spec_object['VALUES'].keys():
        spec_attrs = type_object['SPEC-ATTRIBUTES']
        spec_obj_values = spec_object['VALUES']

        for info in mapping_attr_definition(spec_attrs, spec_obj_values,  attr_key=key):
            artifact_info.update(info)

    return dict(sorted(artifact_info.items()))


def find_type_spec(spec_type, ref):
    """
    The function searches for a specific type in a list of types based on its identifier and returns it.

    :param spec_type: It is a list of dictionaries that contains information about different types. Each
    dictionary represents a type and has a key '@IDENTIFIER' that uniquely identifies the type
    :param ref: The parameter "ref" is a string that represents the identifier of a type that we want to
    find in a list of type specifications
    :return: the dictionary object of the type that has an '@IDENTIFIER' key matching the 'ref'
    parameter.
    """
    for type in spec_type:
        if ref == type.get(IDENTIFIER_TAG):
            return type


def get_spec_object_ref_hierarchy(data, hierarchy=None):
    """
    This function recursively extracts the "SPEC-OBJECT-REF" values from a nested dictionary structure
    and returns them in a list.

    :param data: The data parameter is a JSON object or a dictionary containing information about a
    software system's specification hierarchy
    :param hierarchy: A list that stores the hierarchy of SPEC-OBJECT-REF values found in the input data
    :return: a list of SPEC-OBJECT-REF values from a nested dictionary structure. The list contains the
    SPEC-OBJECT-REF values in the order they appear in the hierarchy.
    """
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


def find_name_module(data):
    spec = list(find_keys(data, 'SPECIFICATIONS'))[0]['SPECIFICATION']

    return spec.get(NAME_TAG)


def find_type_module(data):

    return list(
        find_keys(dict(data), 'SPECIFICATION-TYPE'))[0].get(NAME_TAG)


def find_list_artifact_info(data):
    result = []

    spec = list(find_keys(data, 'SPECIFICATIONS'))[0]['SPECIFICATION']
    spec_type = list(find_keys(dict(data_dict), 'SPEC-OBJECT-TYPE'))[0]
    spec_objects = list(
        find_keys(dict(data_dict), 'SPEC-OBJECTS'))[0]['SPEC-OBJECT']

    ref_hierarchy = get_spec_object_ref_hierarchy(
        spec['CHILDREN']['SPEC-HIERARCHY'])

    for ref in ref_hierarchy:
        for obj in spec_objects:
            if ref == obj.get(IDENTIFIER_TAG):
                result.append(zip_artifact(obj, spec_type))

    return result


if __name__ == '__main__':

    # Reading an XML file specified by URL, parsing it into a Python dictionary using the `xmltodict` library
    data_dict = xmltodict.parse(open(INP_SRC).read())

    json_data = json.dumps({
        "Module Name": find_name_module(data_dict),
        "Module Type": find_type_module(data_dict),
        "List Artifact Info": find_list_artifact_info(data_dict)
    })

    with open(OUT_SRC, "w") as json_file:
        json_file.write(json_data)
