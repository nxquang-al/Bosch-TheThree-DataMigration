import yaml

def load_config(file_name: str) -> dict:
    """
    Loads the config file and returns the module config
    """
    return yaml.safe_load(open(file_name, 'r'))