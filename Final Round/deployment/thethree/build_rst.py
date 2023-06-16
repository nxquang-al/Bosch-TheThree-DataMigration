import copy
from thethree.RstBuilder import RstBuilder
from thethree.HTMLParser import MyHTMLParser

NAME_TAG = "@LONG-NAME"


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


def get_directives_data(config, artifact: dict, directives: list):
    """
    Returns the directives data for the given artifact
    """
    for directive in listify(directives):
        # Attribute Value text
        for key, value in directive.get("attributes", {}).items():
            attr = find_property_have_key(
                config["artifacts"]["artifact"], value)

            directive["attributes"][key] = artifact.get(value, value)

        # HTML Content
        content = directive.get("html_content", "")
        attr = find_property_have_key(config["artifacts"]["artifact"], content)
        if attr is not None:
            parser = MyHTMLParser()
            parser.feed(artifact.get(content, content))
            directive["html_content"] = parser.get_rst()

        # Sub_directive, at the end of the rst
        if "sub_directives" in directive.keys():
            for key, value in directive.get("sub_directives", {}).items():
                attr = find_property_have_key(
                    config["artifacts"]["artifact"], value)

                # If "value: ..." does not set in config list artifacts,
                # then the value works as the key in Json, query directly from Json
                directive["sub_directives"][key] = artifact.get(value, value)

        # In case there are directives in directive
        if "directives" in directive:
            # recursively, directive in directive
            directive["directives"] = get_directives_data(
                config, artifact, directive["directives"]
            )
    return directives


def get_rst_type(artifact_type, rst_config):
    """
    Returns the rst type for the given artifact type
    """
    if artifact_type == rst_config["heading"]["artifact_type"]:
        return "heading"
    if artifact_type == rst_config["information"]["artifact_type"]:
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
            directives_config = copy.deepcopy(
                rst_config[rst_type].get("directives", [])
            )
            directives = listify(get_directives_data(
                config, artifact, directives_config))
            rst.directives(directives)
            rst.newline()


def build_rst(data: dict, config: dict, filepath: str):
    config = config['module']

    rst = RstBuilder(open(filepath, "w"))
    rst.newline()
    rst.heading(data[config["name"]["key"]])
    rst.newline()
    artifacts = data[config["artifacts"]["key"]]
    build_rst_artifacts(rst, artifacts, config["artifacts"]["artifact"])
