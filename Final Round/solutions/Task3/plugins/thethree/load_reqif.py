import xmltodict
import re
import http.client


def preprocess(content):
    start = re.sub(r'<THE-VALUE><div',
                   '<THE-VALUE><![CDATA[<div', content)
    end = re.sub(r'</div></THE-VALUE>',
                 '</div>]]></THE-VALUE>', start)
    end = re.sub(r'/></THE-VALUE>', '></div>]]></THE-VALUE>', end)
    return end


def load_reqif(file_name: str) -> dict:
    """
    Loads the reqif file and returns the reqif content
    """
    if 'opt/airflow' in file_name:
        return xmltodict.parse(preprocess(open(file_name).read()))
    else:
        conn = http.client.HTTPConnection('127.0.0.1:2023')
        conn.request('GET', file_name)
        response = conn.getresponse()
        body = response.read().decode('utf-8')
        print(body)
        return xmltodict.parse(preprocess(body))
