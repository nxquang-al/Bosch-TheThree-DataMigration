import yaml
import xmltodict

from utils import is_locked


def load_config(filename: str) -> dict:
    """
    Loads the config file and returns the module config
    """
    if is_locked(filename) is not True:
        return yaml.safe_load(open(filename, 'r'))['module']
    else:
        raise KeyError(
            'File %s is locked, please end to write the file and close the file' % filename)


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
