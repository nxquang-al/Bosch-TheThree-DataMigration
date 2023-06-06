import xmltodict
import yaml
import json

NAME_TAG = '@LONG-NAME'


def load_config(filename: str) -> dict:
    '''
    Loads the config file and returns the module config
    '''
    return yaml.safe_load(open(filename, 'r'))['module']


def load_reqif(filename: str) -> dict:
    '''
    Loads the reqif file and returns the reqif content
    '''
    return xmltodict.parse(open(filename).read())['REQ-IF']['CORE-CONTENT']['REQ-IF-CONTENT']


def listify(obj):
    '''
    Returns a list of the object if it is not a list
    '''
    return obj if isinstance(obj, list) else [obj]


def find_ref_object(source: list | dict, ref: str) -> dict:
    '''
    Returns the object with the given ref
    '''
    return [obj for obj in listify(source) if obj['@IDENTIFIER'] == ref][0]


def map_value(config: dict, value):
    '''
    Maps the value to the config value mapping
    '''
    if 'value_mapping' in config:
        default_value = config.get('default_value', value)
        value = config['value_mapping'].get(value, default_value)
    return value


def format_value(config: dict, value):
    '''
    Formats the value according to the config
    '''
    value_type = config.get('value_type', '')
    if value_type == 'number':
        value = int(value)
    elif value_type == 'html_string':
        value = xmltodict.unparse(value, pretty=True)[39:]
    return value


def set_value(data: dict, value, config: dict) -> None:
    '''
    Sets the value in the data dict according to the config
    '''
    value = map_value(config, value)
    value = format_value(config, value)
    data[config['key']] = value


def get_name(reqif: dict) -> str:
    '''
    Returns the name of the reqif
    '''
    return reqif['SPECIFICATIONS']['SPECIFICATION'][NAME_TAG]


def get_type(reqif: dict) -> str:
    '''
    Returns the type of the reqif
    '''
    ref = reqif['SPECIFICATIONS']['SPECIFICATION']['TYPE']['SPECIFICATION-TYPE-REF']
    return find_ref_object(reqif['SPEC-TYPES']['SPECIFICATION-TYPE'], ref)[NAME_TAG]


def get_artifact_definition(spec_object: dict) -> str:
    '''
    Returns the artifact definition of the spec object
    '''
    ref = spec_object['TYPE']['SPEC-OBJECT-TYPE-REF']
    definition = find_ref_object(
        reqif['SPEC-TYPES']['SPEC-OBJECT-TYPE'], ref)
    return definition


def get_artifact_attributes(spec_object: dict, definition: dict, config: dict) -> dict:
    '''
    Returns the artifact attributes of the spec object
    '''
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
            attr_value = attr.get('@THE-VALUE', attr.get('THE-VALUE'))

            if attr_name in config: 
                set_value(attributes, attr_value, config[attr_name])
            else:
                attributes[attr_name] = attr_value

    return attributes


def get_artifact(spec_object: dict, config: dict) -> dict:
    '''
    Returns the artifact of the spec object
    '''
    artifact = dict()

    definition = get_artifact_definition(spec_object)
    artifact_type = definition[NAME_TAG]
    set_value(artifact, artifact_type, config['type'])

    attributes = get_artifact_attributes(spec_object, definition, config)
    artifact.update(attributes)

    return artifact


def get_artifacts(reqif: dict, config: dict) -> list:
    '''
    Returns the artifacts of the reqif
    '''
    artifacts = []
    for spec_object in reqif['SPEC-OBJECTS']['SPEC-OBJECT']:
        artifacts.append(get_artifact(spec_object, config))
    return artifacts


def build_json(reqif: dict, config: dict) -> dict:
    '''
    Builds the json from the reqif and config
    '''
    json_dict = dict()
    set_value(json_dict, get_name(reqif), config['name'])
    set_value(json_dict, get_type(reqif), config['type'])

    artifacts = get_artifacts(reqif, config['artifacts']['artifact'])
    set_value(json_dict, artifacts, config['artifacts'])

    return json_dict


if __name__ == '__main__':
    config = load_config('../config.yml')
    reqif = load_reqif('../Requirements.reqif')
    json.dump(build_json(reqif, config), open(
        '../Requirements.json', 'w'), indent=4)
