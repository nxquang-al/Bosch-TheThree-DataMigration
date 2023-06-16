import yaml

def load_config(filename: str) -> dict:
    """
    Loads the config file and returns the module config
    """
    return yaml.safe_load(open(filename, 'r'))