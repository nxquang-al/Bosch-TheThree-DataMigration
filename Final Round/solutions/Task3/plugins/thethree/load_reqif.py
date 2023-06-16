import xmltodict
import re


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
    return xmltodict.parse(preprocess(open(file_name).read()))
