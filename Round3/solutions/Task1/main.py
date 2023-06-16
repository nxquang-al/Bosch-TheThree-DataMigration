import json
import xmltodict

from config import *
from tqdm import tqdm
from utils import *

NAME_TAG = '@LONG-NAME'


def init_argument():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input_file", help="Directory to input file. Accepts file *.reqif or *.xml only")
    parser.add_argument("-o", "--output_file",
                        help="Directory to output *.json file.")
    parser.add_argument("-s", "--settings",
                        help="Directory to configure settings *.yml file")

    args = parser.parse_args()

    return args.input_file, args.output_file, args.settings


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


def get_artifact_definition(spec_object: dict) -> str:
    """
    Returns the artifact definition of the spec object
    """
    ref = list(find_keys(spec_object, 'SPEC-OBJECT-TYPE-REF'))[0]
    definition = find_ref_object(
        reqif['SPEC-TYPES']['SPEC-OBJECT-TYPE'], ref)
    return definition


def find_enum_value(ref_value):
    """
    The function finds the long name of an enum value given its identifier.

    :param ref_value: The input parameter "ref_value" is a string representing the identifier of an
    enumerated value that we want to find the corresponding long name for
    :return: the `@LONG-NAME` attribute of the `ENUM-VALUE` element in the `SPECIFIED-VALUES` element of
    the `DATATYPE-DEFINITION-ENUMERATION` element that has an `@IDENTIFIER` attribute equal to the
    `ref_value` parameter passed to the function.
    """

    INP_SRC, _, _ = init_argument()

    dt_def_enum = list(
        find_keys(load_reqif(INP_SRC), 'DATATYPE-DEFINITION-ENUMERATION'))[0]

    values = []
    for dt in dt_def_enum:
        for dump in dt['SPECIFIED-VALUES']['ENUM-VALUE']:
            values.append(dump)

    for value in values:
        if value.get('@IDENTIFIER') == ref_value:
            return value.get(NAME_TAG)


def find_name_value_attribute(attr, definition, type_name):
    # get the source and ref of the attribute
    source_tag = 'ATTRIBUTE-DEFINITION-' + type_name
    ref_tag = source_tag + '-REF'

    source = definition['SPEC-ATTRIBUTES'][source_tag]
    ref = attr['DEFINITION'][ref_tag]

    # get the name and value of the attribute
    attr_name = find_ref_object(source, ref)[NAME_TAG]

    if type_name == 'enumeration'.upper():
        attr_value = find_enum_value(attr['VALUES']['ENUM-VALUE-REF'])
    else:
        attr_value = attr.get(
            '@THE-VALUE', attr.get('THE-VALUE'))

    return attr_name, attr_value


def get_artifact_attributes(spec_object: dict, definition: dict, config: dict) -> dict:
    """
    Returns the artifact attributes of the spec object
    """
    attributes = dict()
    for attr_type_tag in spec_object['VALUES']:
        type_name = attr_type_tag.split('-')[-1]

        for attr in listify(spec_object['VALUES'][attr_type_tag]):

            attr_name, attr_value = find_name_value_attribute(
                attr, definition, type_name)

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


def get_artifact(spec_object: dict, config: dict) -> dict:
    """
    Returns the artifact of the spec object
    """
    artifact = dict()

    definition = get_artifact_definition(spec_object)
    artifact_type = definition[NAME_TAG]
    set_value(artifact, artifact_type, config['type'])

    attributes = get_artifact_attributes(spec_object, definition, config)

    artifact.update(attributes)

    return dict(sorted(artifact.items()))


def get_artifacts(reqif: dict, config: dict) -> list:
    """
    Returns the artifacts of the reqif
    """
    artifacts = []

    ref_hierarchy = get_spec_object_ref_hierarchy(
        list(find_keys(reqif, 'SPEC-HIERARCHY'))[0])

    for idx in tqdm(range(len(ref_hierarchy))):
        ref = ref_hierarchy[idx]

        for spec_object in reqif['SPEC-OBJECTS']['SPEC-OBJECT']:
            if ref == spec_object.get('@IDENTIFIER'):
                artifacts.append(get_artifact(spec_object, config))

    return artifacts


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


def build_json(reqif: dict, config: dict) -> dict:
    """
    Builds the json from the reqif and config
    """
    json_dict = dict()
    set_value(json_dict, get_module_name(reqif), config['name'])
    set_value(json_dict, get_module_type(reqif), config['type'])

    artifacts = get_artifacts(reqif, config['artifacts']['artifact'])
    set_value(json_dict, artifacts, config['artifacts'])

    return json_dict


def load_reqif(filename: str) -> dict:
    """
    Loads the reqif file and returns the reqif content
    """
    if is_locked(filename) is not True:
        return xmltodict.parse(preprocess(open(filename).read()))['REQ-IF']['CORE-CONTENT']['REQ-IF-CONTENT']
    else:
        raise KeyError(
            'File %s is locked, please end to write the file and close the file' % filename)


if __name__ == '__main__':

    INP_SRC, OUT_SRC, CONFIG_SRC = init_argument()

    print(INP_SRC, OUT_SRC, CONFIG_SRC)

    reqif = load_reqif(INP_SRC)
    config = load_config(CONFIG_SRC)

    if is_locked(OUT_SRC) is not True:
        json.dump(build_json(reqif, config), open(
            OUT_SRC, 'w'), indent=2)
    else:
        raise KeyError(
            'File %s is locked, please end to write the file and close the file' % OUT_SRC)
