import xmltodict
import yaml
import json

NAME_TAG = '@LONG-NAME'


def load_config(filename: str) -> dict:
    return yaml.safe_load(open(filename, 'r'))['module']


def load_reqif(filename: str) -> dict:
    return xmltodict.parse(open(filename).read())['REQ-IF']['CORE-CONTENT']['REQ-IF-CONTENT']


def find_ref_object(reqif: list | dict, ref: str) -> dict:
    if isinstance(reqif, dict):
        reqif = [reqif]
    return [obj for obj in reqif if obj['@IDENTIFIER'] == ref][0]


def set_value(data: dict, config: dict, value) -> None:
    if 'value_mapping' in config:
        default_value = config.get('default_value', value)
        value = config['value_mapping'].get(value, default_value)

    value_type = config.get('value_type')
    if value_type == 'number':
        value = int(value)
    elif value_type == 'html_string':
        value = xmltodict.unparse(value, pretty=True)[39:]

    data[config['key']] = value


def get_specification(reqif: dict) -> dict:
    return reqif['SPECIFICATIONS']['SPECIFICATION']


def get_name(reqif: dict) -> str:
    return get_specification(reqif)[NAME_TAG]


def get_type(reqif: dict) -> str:
    ref = get_specification(reqif)['TYPE']['SPECIFICATION-TYPE-REF']
    return find_ref_object(reqif['SPEC-TYPES']['SPECIFICATION-TYPE'], ref)[NAME_TAG]


def get_artifact(data: dict, config: dict) -> dict:
    artifact = dict()

    type_ref = data['TYPE']['SPEC-OBJECT-TYPE-REF']
    definition = find_ref_object(
        reqif['SPEC-TYPES']['SPEC-OBJECT-TYPE'], type_ref)
    set_value(artifact, config['__type__'], definition[NAME_TAG])

    for attr_value_type in data['VALUES']:
        type_name = attr_value_type.split('-')[-1]

        if not isinstance(data['VALUES'][attr_value_type], list):
            data['VALUES'][attr_value_type] = [data['VALUES'][attr_value_type]]

        for attr in data['VALUES'][attr_value_type]:
            ref = attr['DEFINITION']['ATTRIBUTE-DEFINITION-' +
                                     type_name + '-REF']

            attr_name = find_ref_object(
                definition['SPEC-ATTRIBUTES']['ATTRIBUTE-DEFINITION-' +
                                              type_name], ref)[NAME_TAG]
            attr_value = attr.get('@THE-VALUE', attr.get('THE-VALUE'))

            if attr_name in config:
                set_value(artifact, config[attr_name], attr_value)

    return artifact


def get_artifacts(reqif: dict, config: dict) -> list:
    return [get_artifact(data, config) for data in reqif['SPEC-OBJECTS']['SPEC-OBJECT']]


def build_json(reqif: dict, config: dict) -> dict:
    json_dict = dict()

    set_value(json_dict, config['name'], get_name(reqif))

    set_value(json_dict, config['type'], get_type(reqif))

    set_value(json_dict, config['artifacts'], get_artifacts(
        reqif, config['artifacts']['artifact']))

    return json_dict


if __name__ == '__main__':
    config = load_config('../config.yml')
    reqif = load_reqif('../Requirements.reqif')
    json.dump(build_json(reqif, config), open(
        '../Requirements.json', 'w'), indent=4)
