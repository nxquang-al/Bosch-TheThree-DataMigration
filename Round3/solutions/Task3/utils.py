import yaml
from yaml.loader import SafeLoader


def load_config(file_path):
    data = None
    with open(file_path, "r") as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data
