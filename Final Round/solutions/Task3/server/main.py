from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
import os
import json


def save_files(file_data):
    config = {}

    base_dir = '/opt/airflow/config/'
    # base_dir = './'
    base_dir += datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '/'
    os.makedirs(base_dir)
    for name, filename, content in file_data:
        if len(filename) == 0 or len(content) == 0:
            continue

        filepath = base_dir + filename
        config[name] = filepath

        open(filepath, 'wb').write(content)
    return config


class HTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        file_data = []
        lines = body.split(b'\r\n')
        for i in range(len(lines)):
            line = lines[i].rstrip()
            if line.startswith(b'Content-Disposition:'):
                params = line.split(b';')

                name = params[1].split(b'=')[1]
                name = name.decode().replace('"', '')

                filename = params[2].split(b'=')[1]
                filename = filename.decode().replace('"', '')

                content = lines[i + 3].rstrip()

                file_data.append((name, filename, content))

        config = save_files(file_data)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(json.dumps(config).encode())


def start_server(HOST_NAME='localhost', PORT=8000):
    httpd = HTTPServer((HOST_NAME, PORT), HTTPRequestHandler)
    print("Server Starts - %s:%s" % (HOST_NAME, PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
