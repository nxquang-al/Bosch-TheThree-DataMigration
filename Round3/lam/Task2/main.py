import yaml
import json
from RstBuilder import RstBuilder
from HTMLParser import MyHTMLParser

NAME_TAG = "@LONG-NAME"


def load_config(filename: str) -> dict:
    """
    Loads the config file and returns the module config
    """
    return yaml.safe_load(open(filename, "r"))["module"]


def load_json(filename: str) -> dict:
    """
    Loads the json file and returns the json content
    """
    return json.load(open(filename))


def find_property_have_key(obj: dict, target: str):
    """
    Returns the property that have the given key
    """
    for key, value in obj.items():
        if value.get("key") == target:
            return key, value


def listify(obj):
    """
    Returns a list of the object if it is not a list
    """
    return obj if isinstance(obj, list) else [obj]


def get_directives_data(artifact: dict, directives: list):
    """
    Returns the directives data for the given artifact
    """
    for directive in listify(directives):
        for key, value in directive.get("attributes", {}).items():
            attr = find_property_have_key(config["artifacts"]["artifact"], value)
            if attr is not None:
                attr_type = attr[1].get("value_type", "")
                if attr_type == "html_string":
                    print("html_string  ")

                    # value = xmltodict.unparse(artifact.get(value, value), pretty=True)[39:]
            directive["attributes"][key] = artifact.get(value, value)

        content = directive.get("html_content", "")
        attr = find_property_have_key(config["artifacts"]["artifact"], content)
        if attr is not None:
            print(attr)
            parser = MyHTMLParser()
            parser.feed(artifact.get(content, content))
            directive["html_content"] = parser.get_rst()

        if "directives" in directive:
            # recursively, directive in directive
            directive["directives"] = get_directives_data(
                artifact, directive["directives"]
            )
    return directives


def get_rst_type(artifact_type, rst_config):
    """
    Returns the rst type for the given artifact type
    """
    if artifact_type == rst_config["heading"]["atifact_type"]:
        return "heading"
    if artifact_type == rst_config["information"]["atifact_type"]:
        return "information"
    return "other"


def build_rst_artifacts(rst, artifacts: list, config: dict):
    rst_config = config["__rst__"]
    for artifact in artifacts:
        artifact_type = artifact[config["type"]["key"]]
        rst_type = get_rst_type(artifact_type, rst_config)

        if rst_type == "heading":
            attr_name = rst_config[rst_type]["value"]
            rst.subheading(artifact[attr_name])
            rst.newline()
        else:
            directives_config = rst_config[rst_type].get("directives", [])
            directives = get_directives_data(artifact, directives_config)
            rst.directives(directives)
            rst.newline()


if __name__ == "__main__":
    config = load_config("../config.yml")
    data = load_json("../Requirements.json")

    rst = RstBuilder(open("../Requirements.rst", "w"))
    rst.newline()
    rst.heading(data[config["name"]["key"]])
    rst.newline()
    artifacts = data[config["artifacts"]["key"]]
    build_rst_artifacts(rst, artifacts, config["artifacts"]["artifact"])
