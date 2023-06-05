import argparse
import requests
import base64
from utils import load_config


def init_arguments():
    """
    This function is used to get arguments from the command line.
    -i, --input_file flags are used the path to config file
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input_file",
        default="config.yaml",
        help="Path to config file. Accepts file *.yaml only",
    )

    args = parser.parse_args()
    return args.input_file


if __name__ == "__main__":
    config_file_path = init_arguments()

    config = load_config(config_file_path)
    assert config is not None  # To ensure config_file_path is valid

    apiURL = f"https://api.github.com/repos/{config['REPOSITORY']['OWNER']}/{config['REPOSITORY']['NAME']}/contents/{config['FILENAME']}"
    headers = {
        "Authorization": f"""Bearer {config['AUTHENTICATION']['TOKEN']}""",
        "Content-Type": "application/vnd.github+json",
    }

    # Firstly, request to get file's SHA, if file does exist, the status_code will be 200.
    data = {"branch": config["REPOSITORY"]["BRANCH"]}
    response = requests.get(apiURL, headers=headers, json=data)
    if response.status_code == 200:
        sha = response.json()["content"]["sha"]
    else:
        sha = None

    with open(config["FILENAME"], "rb") as f:
        encoded_data = base64.b64encode(f.read())

        data = {
            "branch": config["REPOSITORY"]["BRANCH"],  # define the branch
            "message": config["MESSAGE"],  # commit message
            "content": encoded_data.decode("utf-8"),  # content of the commited file
        }
        if sha is not None:
            data["sha"] = sha
        # else if sha is none, the file does not exist in the repo

        response = requests.put(apiURL, headers=headers, json=data)
        if response == 200:
            print("Overwrite successfully!")
        else:
            print("Overwrite fail!")
            print(f"Message: {response.json()['message']}")
