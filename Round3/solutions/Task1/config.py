import xmltodict
import yaml

from utils import *

IDENTIFIER_TAG = '@IDENTIFIER'
NAME_TAG = '@LONG-NAME'


def refactor_key_value(key, value, attr_name):

    _, _, CONFIG_SRC = init_argument()

    mapping = load_artifact_config(CONFIG_SRC).get(
        'mapping', {}).get(attr_name.lower())

    if key in mapping.keys():

        config_attribute = mapping.get(key)

        if config_attribute.get('ignore') == True:
            return None, None

        type_value = config_attribute.get('datatype')

        if isinstance(value, dict) and (type_value is None or type_value == 'string'):
            value = value.get('div', {}).get('#text', '')
        key = config_attribute.get('key', key)

        if type_value is not None:
            match type_value:
                case 'number':
                    value = int(value)
                case 'html_string':
                    value = xmltodict.unparse(value, pretty=True)[39:]

    return key, value


def load_config(filename):

    with open(filename, 'r') as file:
        config = yaml.safe_load(file).get('module', {})

    return config


def load_artifact_config(filename):
    return load_config(filename).get('artifacts', {}).get('value').get('element')


def load_data(filename):
    return xmltodict.parse(open(filename).read())


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
        find_keys(load_data(INP_SRC), 'DATATYPE-DEFINITION-ENUMERATION'))[0]

    values = []
    for dt in dt_def_enum:
        for dump in dt['SPECIFIED-VALUES']['ENUM-VALUE']:
            values.append(dump)

    for value in values:
        if value.get(IDENTIFIER_TAG) == ref_value:
            return value.get(NAME_TAG)


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

                if attr_name == 'ENUMERATION':
                    value = find_enum_value(attr['VALUES']['ENUM-VALUE-REF'])

                key, value = refactor_key_value(key, value, attr_name)

                if key is not None:
                    result.append({key: value})

    return result
