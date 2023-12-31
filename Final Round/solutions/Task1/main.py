import argparse
from github import Github
from utils import load_config


def init_arguments():
    """
    This function is used to get arguments from the command line.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--file_path",
        help="Path to the new rst file",
    )

    args = parser.parse_args()
    return args.file_path


def map_caption(module_type: str):
    """
    Modify this function to map the filename or its module type to the corresponding toctree caption.
    E.g. "MO_RS" -> "Software Requirements"
         "SC_RS" -> "System Requirements"
    """
    return "System Requirements"


def update_index_rst(
    github_config: dict, new_rst_file_path: str, module_type: str = "SC_RS"
):
    """
    Get the content of index.rst from GitHub, modify it, and finally upload it again.

    .. Args::
        :github_config: config for GitHub api setup
        :new_rst_file_path: path to the new rst file
        :module_type: Module Type of this new rst file, used to map caption

    """
    # index.rst path is fixed in Github
    index_rst_file_path = "docs/index.rst"
    new_rst_file_path = new_rst_file_path.replace("docs", "")
    github = Github(github_config)
    # Define the file name and caption to update
    caption = map_caption(module_type)

    # Read in the contents of the index.rst file
    content = github.pull(index_rst_file_path)

    # Find the toctree directive with the caption we want to update
    start = content.find(f":caption: {caption}")
    if start == -1:
        print(f"Could not find toctree with caption: {caption}")
        exit()

    # Parse the start and end of the toctree directive
    start = content.rfind(
        ".. toctree::", 0, start
    )  # find the beginning of the current toctree
    mid = content.find("\n\n", start)  # end of options section
    next_toc = content.find(
        ".. toctree::", start + 1
    )  # find the beginning of the next toctree
    end = content.find(
        "\n\n", mid + 2, next_toc
    )  # end of file_paths, under options section and above the next toctree

    # Get the current options in the toctree directive
    current_options = content[start:mid].split("\n")
    current_options = "\n".join(current_options[1:])
    # current_options now looks like: "   :maxdepth: 1\n  :caption: Software Requirement"

    current_files = content[mid + 2 : end].split("\n")
    current_files = [e.strip() for e in current_files if e.startswith(" ")]
    # current_files now is a list of file paths in the toctree directive,
    # e.g. ["./sw_req.rst", "./sw_req_2.rst"]

    # Generate a new toctree directive with the updated file path
    new_files = current_files
    if new_rst_file_path not in current_files:
        new_files.append(new_rst_file_path)
    new_options = current_options + "\n" if current_options else ""
    new_directive = f".. toctree::\n{new_options}\n"
    new_directive += "\n".join(f"   {file}" for file in new_files)

    # Replace the old toctree directive with the new one
    content = content[:start] + new_directive + content[end:]

    # Automatically upload index.rst to GitHub if file is updated
    github.upload(index_rst_file_path, content)


if __name__ == "__main__":
    github_config = load_config("./github_config.yml")
    NEW_RST_PATH = init_arguments()

    # Actually this module type is retreived from the json via the key: config["module"]["type"][key]
    # We hardcode here but we handle it carefully in Airflow
    module_type = "MO_RS"

    update_index_rst(github_config, NEW_RST_PATH, module_type)
