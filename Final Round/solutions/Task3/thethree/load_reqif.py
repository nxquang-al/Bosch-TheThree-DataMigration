import xmltodict
import re


def preprocess(content: str) -> str:
    """
    A preprocess function help add flag for html content will not parser by xmltodict
    """
    content = re.sub(r'<THE-VALUE><div',
                     '<THE-VALUE><![CDATA[<div', content)
    content = re.sub(r'</div></THE-VALUE>',
                     '</div>]]></THE-VALUE>', content)
    content = re.sub(r'/></THE-VALUE>', '></div>]]></THE-VALUE>', content)
    return content


def load_reqif(filename: str) -> dict:
    """
    Loads the reqif file and returns the reqif content
    """
    return xmltodict.parse(preprocess(open(filename).read()))
