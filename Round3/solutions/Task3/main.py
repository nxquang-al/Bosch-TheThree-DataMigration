import argparse
import requests
import base64
from utils import load_config


def init_arguments():
    """
    This function is used to get arguments from the command line.
    .. Flags:
        :-i, --input_file: path to config file
    .. Returns:
        :args.input_file: path to config yaml
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


def retrieve_SHA(url, headers, branch, filename):
    """
    Query GitHub to retreive SHA for file.
    If file exists on the branch, then return its current SHA
    If file does note exist, the SHA will be None

    .. Args:
        :url: GitHub API URL to access to a repo
        :headers: request headers, include the access token
        :branch: the name of the branch to access, defined in the config yaml.
        :filename: the name of the file we want to push/overwrite, defined in the config.
    .. Returns:
        :SHA: sha value corresponding to the file.

    """
    url += filename
    response = requests.get(url, headers, data={"branch": branch})
    if response.status_code == 200:
        # Response message is OK, file exists and can extract SHA
        sha = response.json()["sha"]
    else:
        # file does not exist in the repo, ignore the SHA value.
        sha = None
    return sha


def upload(url, headers, branch, message, filename, sha=None):
    """
    Push the file to GitHub and overwrite if the file exists

    .. Args:
        :url: GitHub API URL to access to the repo
        :headers: request headers, include the access token
        :branch: the name of the branch to upload, defined in the config file
        :message: commit message, defined in the config file
        :filename: the name of the file to upload, defined in the config file
        :sha: the current SHA value of the file.
    .. Outputs:
        :200: if file exists and overwrite it successfully
        :201: if file doesnot exist and push it successfully
        :401: action fail
    """
    url += filename
    with open(filename, "rb") as f:
        encoded_data = base64.b64encode(
            f.read()
        )  # file's content must be written under the base64 format

        data = {
            "branch": branch,
            "message": message,
            "content": encoded_data.decode("utf-8"),  # content of the commited file
        }
        # if file exist, assign file's SHA as an attribute, else ignore
        if sha is not None:
            data["sha"] = sha

        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 200:
            print("200 - Overwrite successfully!")
        elif response.status_code == 201:
            print("201 - Push a new file successfully!")
        else:
            print("Overwrite fail!")
            print("Message: {}".format(response.json()["message"]))


if __name__ == "__main__":
    INP_CONFIG = init_arguments()

    config = load_config(INP_CONFIG)
    assert config is not None  # To ensure INP_CONFIG is valid

    api_url = f"https://api.github.com/repos/{config['REPOSITORY']['OWNER']}/{config['REPOSITORY']['NAME']}/contents/"
    headers = {
        "Authorization": f"""Bearer {config['AUTHENTICATION']['TOKEN']}""",
        "Content-Type": "application/vnd.github+json",
    }

    sha = retrieve_SHA(
        api_url,
        headers,
        branch=config["REPOSITORY"]["BRANCH"],
        filename=config["FILENAME"],
    )

    upload(
        api_url,
        headers,
        branch=config["REPOSITORY"]["BRANCH"],
        message=config["MESSAGE"],
        filename=config["FILENAME"],
        sha=sha,
    )
