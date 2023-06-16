from thethree.upload_to_github import upload_to_github

def map_caption(filename: str):
    """
    Modify this function to map the filename or its module type to the corresponding toctree caption.
    E.g. "MO_RS" -> "Software Requirements"
         "SC_RS" -> "System Requirements"
    """
    return "System Requirements"



def update_index_rst(github_config, index_file_path: str, new_file_path: str):
    # Define the file name and caption to update
    caption = map_caption(new_file_path)

    # Read in the contents of the index.rst file
    with open(index_file_path, "r") as f:
        content = f.read()

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
    print(current_files)
    current_files = [e.strip() for e in current_files if e.startswith(" ")]
    # current_files now is a list of file paths in the toctree directive,
    # e.g. ["./sw_req.rst", "./sw_req_2.rst"]

    # Generate a new toctree directive with the updated file path
    new_files = current_files + [new_file_path]
    new_options = current_options + "\n" if current_options else ""
    new_directive = f".. toctree::\n{new_options}\n"
    new_directive += "\n".join(f"   {file}" for file in new_files)

    # Replace the old toctree directive with the new one
    content = content[:start] + new_directive + content[end:]

    # Write the updated content back to the index.rst file
    with open(index_file_path, "w") as f:
        f.write(content)

    # Automatically upload index.rst to GitHub if file is updated
    upload_to_github(github_config, index_file_path)