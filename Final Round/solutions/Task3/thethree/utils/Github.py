import json
import base64
import http.client


class Github:
    def __init__(self, config: dict) -> None:
        self.owner = config["REPOSITORY"]["OWNER"]
        self.repo = config["REPOSITORY"]["NAME"]
        self.token = config["AUTHENTICATION"]["TOKEN"]
        self.branch = config["REPOSITORY"]["BRANCH"]
        self.message = config["MESSAGE"]
        self.host = "api.github.com"
        self.base_url = f"/repos/{self.owner}/{self.repo}/contents/"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/vnd.github+json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

    def get_sha(self, file_path):
        try:
            body = json.dumps({'branch': self.branch}).encode('utf-8')

            conn = http.client.HTTPSConnection(self.host, timeout=10)
            conn.request('GET', self.base_url + file_path,
                         headers=self.headers, body=body)
            response = conn.getresponse()
            status = response.status
            body = response.read().decode('utf-8')
            conn.close()
            if status == 200:
                print("Retrieve SHA successfully!")
                body = json.loads(body)
                return body["sha"]
            else:
                print("File does not exist, no need SHA!")
        except Exception as e:
            print(e)
            print("Retrieve SHA fail!")

    def upload(self, file_path: str, file_content: str):
        file_content = base64.b64encode(
            file_content.encode('utf-8')).decode('utf-8')
        data = {
            "branch": self.branch,
            "message": self.message,
            "content": file_content,
        }
        # if file exist, assign file's SHA as an attribute, else ignore
        sha = self.get_sha(file_path)
        if sha is not None:
            data["sha"] = sha

        try:
            conn = http.client.HTTPSConnection(self.host, timeout=10)
            body = json.dumps(data).encode('utf-8')
            conn.request('PUT', self.base_url + file_path,
                         headers=self.headers, body=body)
            response = conn.getresponse()
            status = response.status
            conn.close()
            if status == 200:
                print("200 - Overwrite successfully!")
            elif status == 201:
                print("201 - Push a new file successfully!")
            else:
                raise Exception("Status code: {}".format(status))

        except Exception as e:
            print(e)
            print("Overwrite fail!")

    def pull(self, file_path: str):
        conn = http.client.HTTPSConnection(self.host, timeout=10)
        body = json.dumps({"branch": self.branch}).encode("utf-8")
        conn.request("GET", self.base_url +
                     file_path, headers=self.headers, body=body)
        response = conn.getresponse()
        body = response.read().decode('utf-8')
        conn.close()
        body = json.loads(body)
        return base64.b64decode(body['content']).decode('utf-8')
