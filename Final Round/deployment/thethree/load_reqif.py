import xmltodict

def load_reqif(filename: str) -> dict:
    """
    Loads the reqif file and returns the reqif content
    """
    return xmltodict.parse(open(filename).read())