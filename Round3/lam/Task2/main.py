import yaml
import json
from RstBuilder import RstBuilder

NAME_TAG = '@LONG-NAME'


def load_config(filename: str) -> dict:
    return yaml.safe_load(open(filename, 'r'))['module']


def load_json(filename: str) -> dict:
    return json.load(open(filename))

def get_directives_data(artifact, directives):
    for directive in directives:
        if 'attributes' in directive:
            for key, value in directive['attributes'].items():
                directive['attributes'][key] = artifact.get(value, value)
        if 'directives' in directive:
            directive['directives'] = get_directives_data(artifact, directive['directives'])
    return directives

def build_rst_artifacts(rst, data, config):
    rst_config = config['__rst__']
    for artifact in data:
        artifact_type = artifact[config['__type__']['key']]

        if artifact_type not in rst_config:
            rst_type = 'requirement'
            artifact_type = '__other__'
        else:
            rst_type = rst_config[artifact_type]['rst_type']

        if rst_type == 'subheading':
            rst.subheading(artifact[rst_config[artifact_type]['key']])
            rst.newline()
        else:
            if 'directives' in rst_config[artifact_type]:
                directives = get_directives_data(artifact, rst_config[artifact_type]['directives'])
                rst.directives(directives)
                rst.newline()


if __name__ == '__main__':
    config = load_config('../config.yml')
    data = load_json('../Requirements.json')

    with open('../Requirements.rst', 'w') as f:
        rst = RstBuilder(f)
        rst.heading(data[config['name']['key']])
        rst.newline()
        build_rst_artifacts(
            rst, data[config['artifacts']['key']], config['artifacts']['artifact'])
