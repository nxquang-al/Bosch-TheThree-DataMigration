import json

from config import *
from tqdm import tqdm
from utils import *


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

    artifacts = {}

    type_ref = spec_object['TYPE']['SPEC-OBJECT-TYPE-REF']
    type_object = find_type_spec(spec_type, type_ref)

    artifact_config = load_artifact_config(CONFIG_SRC)

    artifacts.update(
        {artifact_config.get('type').get('key', 'type'): type_object.get(NAME_TAG)})

    for key in spec_object['VALUES'].keys():
        spec_attrs = type_object['SPEC-ATTRIBUTES']
        spec_obj_values = spec_object['VALUES']

        for info in mapping_attr_definition(spec_attrs, spec_obj_values,  attr_key=key):
            artifacts.update(info)

    return dict(sorted(artifacts.items()))


def find_name_module(data):
    spec = list(find_keys(data, 'SPECIFICATIONS'))[0]['SPECIFICATION']

    return spec.get(NAME_TAG)


def find_type_module(data):

    return list(
        find_keys(dict(data), 'SPECIFICATION-TYPE'))[0].get(NAME_TAG)


def find_list_artifacts(data):
    result = []

    spec = list(find_keys(data, 'SPECIFICATIONS'))[0]['SPECIFICATION']
    spec_type = list(find_keys(dict(data_dict), 'SPEC-OBJECT-TYPE'))[0]
    spec_objects = list(
        find_keys(dict(data_dict), 'SPEC-OBJECTS'))[0]['SPEC-OBJECT']

    ref_hierarchy = get_spec_object_ref_hierarchy(
        spec['CHILDREN']['SPEC-HIERARCHY'])

    for idx in tqdm(range(len(ref_hierarchy))):
        ref = ref_hierarchy[idx]

        for obj in spec_objects:
            if ref == obj.get(IDENTIFIER_TAG):
                result.append(zip_artifact(obj, spec_type))

    return result


if __name__ == '__main__':
    INP_SRC, OUT_SRC, CONFIG_SRC = init_argument()

    # Reading an XML file specified by URL, parsing it into a Python dictionary using the `xmltodict` library
    data_dict = load_data(INP_SRC)

    config_module = {key: value.get(
        'key', key) for key, value in load_config(CONFIG_SRC).items()}

    json_data = json.dumps({
        config_module.get('name'): find_name_module(data_dict),
        config_module.get('type'): find_type_module(data_dict),
        config_module.get('artifacts'): find_list_artifacts(data_dict)
    }, indent=4)

    with open(OUT_SRC, "w") as json_file:
        json_file.write(json_data)
