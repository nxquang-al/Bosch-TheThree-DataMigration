import xmltodict

def load_reqif(file_name: str) -> dict:
    """
    Loads the reqif file and returns the reqif content
    """
    return xmltodict.parse(open(file_name).read())