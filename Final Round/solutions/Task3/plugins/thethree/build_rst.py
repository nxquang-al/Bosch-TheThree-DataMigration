import copy
import re
from thethree.utils.RstBuilder import RstBuilder
from thethree.utils.HTMLParser import MyHTMLParser

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


def postprocess(content):
    lines = re.split("\n", content)
    print(lines)
    for i, line in enumerate(lines):
        if line == "":
            continue
        elif line.startswith("|"):
            lines[i] = "   " + line
        else:
            lines[i] = "     " + line
    return "\n".join(lines)


def get_directives_data(config, artifact: dict, directives: list):
    """
    Returns the directives data for the given artifact
    """
    for directive in listify(directives):
        directive["title"] = artifact.get("Title", "Title")
        # Attribute Value text
        for key, value in directive.get("attributes", {}).items():
            attr = find_property_have_key(config, value)
            if attr is not None:
                directive["attributes"][key] = artifact.get(value, value)

        # HTML Content
        content = directive.get("html_content", "")
        attr = find_property_have_key(config, content)
        if attr is not None:
            parser = MyHTMLParser()
            parser.feed(artifact.get(content, content).replace("\u00a0", ""))
            directive["html_content"] = postprocess(parser.get_rst())

        # Sub_directive, at the end of the rst
        if "sub_directives" in directive.keys():
            for key, value in directive["sub_directives"].items():
                attr = find_property_have_key(config, value)
                directive["sub_directives"][key] = {}
                directive["sub_directives"][key]["content"] = postprocess(
                    artifact.get(value, "")
                )
                # get ID to generate unique title for subdirective, e.g. 'verify' + 68019 -> 'verify68019'
                directive["sub_directives"][key]["title"] = key + str(
                    artifact.get("Identifier", "")
                )
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
            directives_config = copy.deepcopy(
                rst_config[rst_type].get("directives", [])
            )
            directives = listify(
                get_directives_data(config, artifact, directives_config)
            )
            rst.directives(directives)
            rst.newline()


def build_rst(data: dict, config: dict):
    config = config["module"]

    rst = RstBuilder()
    rst.newline()
    rst.heading(data[config["name"]["key"]])
    rst.newline()
    artifacts = data[config["artifacts"]["key"]]
    build_rst_artifacts(rst, artifacts, config["artifacts"]["artifact"])

    return rst.get_rst()
