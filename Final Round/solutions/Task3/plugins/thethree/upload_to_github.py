from thethree.utils.Github import Github


def upload_to_github(config, file_path, rst_data):
    github = Github(config)
    github.upload(file_path, rst_data)
