import xmltodict
import yaml
import json

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



def listify(obj):
    """
    Returns a list of the object if it is not a list
    """
    return obj if isinstance(obj, list) else [obj]


def find_ref_object(source: list | dict, ref: str) -> dict:
    """
    Returns the object with the given ref
    """
    return [obj for obj in listify(source) if obj['@IDENTIFIER'] == ref][0]


def map_value(config: dict, value):
    """
    Maps the value to the config value mapping
    """
    if 'value_mapping' in config:
        default_value = config.get('default_value', value)
        value = config['value_mapping'].get(value, default_value)
    return value


def format_value(config: dict, value):
    """
    Formats the value according to the config
    """
    value_type = config.get('value_type')

    if isinstance(value, dict) and (value_type is None or value_type == 'string'):
        value = value.get('div', {}).get('#text', '')

    if value_type == 'number':
        value = int(value)
    elif value_type == 'html_string':
        value = xmltodict.unparse(value, pretty=True)[39:]

    return value


def set_value(data: dict, value, config: dict, attr_name='') -> None:
    """
    Sets the value in the data dict according to the config
    """
    value = map_value(config, value)
    value = format_value(config, value)
    data[config.get('key', attr_name)] = value


def get_module_name(reqif: dict) -> str:
    """
    Returns the name of the reqif
    """
    return list(find_keys(reqif, 'SPECIFICATION'))[0][NAME_TAG]


def get_module_type(reqif: dict) -> str:
    """
    Returns the type of the reqif
    """
    ref = list(find_keys(reqif, 'SPECIFICATION-TYPE-REF'))[0]
    return find_ref_object(reqif['SPEC-TYPES']['SPECIFICATION-TYPE'], ref)[NAME_TAG]


def get_artifact_definition(reqif, spec_object: dict) -> str:
    """
    Returns the artifact definition of the spec object
    """
    ref = list(find_keys(spec_object, 'SPEC-OBJECT-TYPE-REF'))[0]
    definition = find_ref_object(
        reqif['SPEC-TYPES']['SPEC-OBJECT-TYPE'], ref)
    return definition


def find_enum_value(reqif, ref_value):
    """
    The function finds the long name of an enum value given its identifier.

    :param ref_value: The input parameter "ref_value" is a string representing the identifier of an
    enumerated value that we want to find the corresponding long name for
    :return: the `@LONG-NAME` attribute of the `ENUM-VALUE` element in the `SPECIFIED-VALUES` element of
    the `DATATYPE-DEFINITION-ENUMERATION` element that has an `@IDENTIFIER` attribute equal to the
    `ref_value` parameter passed to the function.
    """

    dt_def_enum = list(
        find_keys(reqif, 'DATATYPE-DEFINITION-ENUMERATION'))[0]

    values = []
    for dt in dt_def_enum:
        for dump in dt['SPECIFIED-VALUES']['ENUM-VALUE']:
            values.append(dump)

    for value in values:
        if value.get('@IDENTIFIER') == ref_value:
            return value.get(NAME_TAG)


def get_artifact_attributes(reqif, spec_object: dict, definition: dict, config: dict) -> dict:
    """
    Returns the artifact attributes of the spec object
    """
    attributes = dict()
    for attr_type_tag in spec_object['VALUES']:
        type_name = attr_type_tag.split('-')[-1]

        for attr in listify(spec_object['VALUES'][attr_type_tag]):
            # get the source and ref of the attribute
            source_tag = 'ATTRIBUTE-DEFINITION-' + type_name
            ref_tag = source_tag + '-REF'

            source = definition['SPEC-ATTRIBUTES'][source_tag]
            ref = attr['DEFINITION'][ref_tag]

            # get the name and value of the attribute
            attr_name = find_ref_object(source, ref)[NAME_TAG]

            if type_name == 'enumeration'.upper():
                attr_value = find_enum_value(reqif, attr['VALUES']['ENUM-VALUE-REF'])
            else:
                attr_value = attr.get(
                    '@THE-VALUE', attr.get('THE-VALUE'))

            if attr_value is None:
                continue

            if attr_name in config:
                if config.get(attr_name).get('ignore') == True:
                    continue

                set_value(attributes, attr_value,
                          config[attr_name], attr_name=attr_name)
            else:
                attributes[attr_name] = attr_value

    return attributes


def get_artifact(reqif, spec_object: dict, config: dict) -> dict:
    """
    Returns the artifact of the spec object
    """
    artifact = dict()

    definition = get_artifact_definition(reqif, spec_object)
    artifact_type = definition[NAME_TAG]
    set_value(artifact, artifact_type, config['type'])

    attributes = get_artifact_attributes(reqif, spec_object, definition, config)

    artifact.update(dict(sorted(attributes.items())))

    return artifact


def get_artifacts(reqif: dict, config: dict) -> list:
    """
    Returns the artifacts of the reqif
    """
    artifacts = []

    ref_hierarchy = get_spec_object_ref_hierarchy(
        list(find_keys(reqif, 'SPEC-HIERARCHY'))[0])

    for idx in range(len(ref_hierarchy)):
        ref = ref_hierarchy[idx]

        for spec_object in reqif['SPEC-OBJECTS']['SPEC-OBJECT']:
            if ref == spec_object.get('@IDENTIFIER'):
                artifacts.append(get_artifact(reqif, spec_object, config))

    return artifacts


def build_json(reqif: dict, config: dict) -> dict:
    """
    Builds the json from the reqif and config
    """
    reqif = reqif['REQ-IF']['CORE-CONTENT']['REQ-IF-CONTENT']
    config = config['module']

    json_data = dict()
    set_value(json_data, get_module_name(reqif), config['name'])
    set_value(json_data, get_module_type(reqif), config['type'])

    artifacts = get_artifacts(reqif, config['artifacts']['artifact'])
    set_value(json_data, artifacts, config['artifacts'])

    return json_data
