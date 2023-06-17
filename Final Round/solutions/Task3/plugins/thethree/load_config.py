import yaml
import http.client


def load_config(file_name: str) -> dict:
    """
    Loads the config file and returns the module config
    """
    if 'opt/airflow' in file_name:
        return yaml.safe_load(open(file_name, 'r'))
    else:
        conn = http.client.HTTPConnection('127.0.0.1:2023')
        conn.request('GET', file_name)
        response = conn.getresponse()
        body = response.read().decode('utf-8')
        print(body)
        return yaml.safe_load(body)
