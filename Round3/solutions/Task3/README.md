# Data Migration - Round 3

## Team TheThree - Task 3

### Technical Overview
- We use the GitHub REST API to upload files.
    - First, use a GET method to retreive the current SHA of a file. If file does not exist on that branch, the value of SHA is None.
    - Second, use a PUT method to upload the file. The file is encoded, together with its SHA (if overwrite) and commit message are pushed to the branch
- Of course, you must provide your personal access token and this token must be authorized to access the resources.
- For more detail, please refer to [GitHub REST API documentation](https://docs.github.com/en/rest?apiVersion=2022-11-28)

### Usage
- **Step 1:** Modify the `/Task3/config.yaml`
```yaml
AUTHENTICATION:
  TOKEN: <GitHub-Access-Token>
  USERNAME: <username>
FILENAME: <filename>
MESSAGE: <commit message>
REPOSITORY:
  BRANCH: <name-of-branch>
  NAME: <name-of-repo>
  OWNER: <repo-owner>
```
- **Step 2:** run the `main.py` to start uploading
```bash
$ python main.py -i config.yaml
```