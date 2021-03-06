# HTTP is a communication protocol for servers to receive requests and to respond to clients in the form of documented media (HTML).
# it is an application layer protocol that sits above TCP.

# $ telnet google.com 80    # address and port number -
# $ GET / HTTP/1.0 # specify the http method, path and protocol and we can get googles home page.

# the first line of the header defines the resource we want to retrieve

import socket
import os
import threading
import logging
import datetime

class HTTPServer:

    def __init__(self, host, port=8001):
        self.host = host
        self.port = port

        self.max_req_size = 1024
        self.page_contents = {}

        self.status_codes = {"200": "HTTP/1.1 200 OK\n", "201": "HTTP/1.1 201 CREATED\n",
                             "400": "HTTP/1.1 400 BAD REQUEST\n", "404": "HTTP/1.1 404 NOT FOUND\n",
                             "505": "HTTP/1.1 505 HTTP VERSION NOT SUPPORTED\n"}

        self.accepted_versions = {"HTTP/1.1", "HTTP/1.0"}

        logging.basicConfig(level=logging.INFO, filename="logs.txt", filemode="a",
                            format='%(asctime)s - %(message)s - %(levelname)s', datefmt='%d-%b-%y %H:%M:%S')

        self.cache_pages()
        self.run()

    def cache_pages(self):

        for html_page in os.listdir(os.getcwd()+"/pages"):
            with open(os.getcwd()+ "/pages/" + html_page, "r") as f:
                text = f.read()
                resource_name = f"/{html_page.split('.')[0]}"
                if resource_name == "/index":
                    self.page_contents['/'] = text + "\n"

                self.page_contents[resource_name] = text + "\n"

    def is_valid_version(self, client_version: str) -> bool:
        client_version = client_version.split("\n")[0]
        version = ""
        for c in client_version:
            if c.isalnum() or c == "/" or c == ".":
                version += c

        if version not in self.accepted_versions:
            return False
        return True

    def parse_GET(self, requested_resource: str, addr: str) -> str:

        response = ""
        # we may or may not have parameters in the url. consider both cases
        page = requested_resource.split("?")[0] if len(requested_resource.split("?")[0]) > 0 else requested_resource

        if page not in self.page_contents:
            return self.get_status_code("404")

        response += self.get_status_code("200")
        response += "\n" + self.page_contents[page]
        logging.info(f"200 OK for GET {page} from {addr}")
        return response

    def parse_POST(self, message: str, requested_resource: str, addr: str) -> str:

        response = ""

        message_body = message.split("\n")[-1]
        fields = message_body.split("&")

        # easy access based on form-id set from HTML code
        # k: form-id v: submitted data
        form_table = {}
        for field in fields:
            form_id = field.split("=")[0]
            client_data = field.split("=")[1]
            form_table[form_id] = client_data

        for k in form_table:
            print(form_table[k])

        form_data = message_body.split("=")[-1]

        response += self.get_status_code("201")
        # redirect the user back to the page they were on
        response += "\n" + self.page_contents[requested_resource]
        logging.info(f"{self.get_status_code('201')} in {requested_resource} for {addr}")

        return response

    def handle_request(self, message: str, addr: str) -> str:

        starting_line = message.split(" ")
        if len(starting_line) < 3:
            logging.info(f"400 from {addr} - starting line {starting_line}")
            return self.status_codes["400"]

        # message data
        method = starting_line[0]
        requested_resource = starting_line[1]
        client_version = starting_line[2]

        if not self.is_valid_version(client_version):
            logging.info(f"505 OK for {requested_resource} from {addr}. Client HTTP version: {client_version}")
            return self.get_status_code("505")

        if method == "GET":
            return self.parse_GET(requested_resource, addr)

        elif method == "POST":
            return self.parse_POST(message, requested_resource, addr)

        else:
            logging.info(f"404 for {requested_resource} from {addr}")
            return self.get_status_code("404")

    def get_status_code(self, status_code: str):
        if status_code not in self.status_codes:
            raise ValueError(f"Status code {status_code} not a valid HTTP code or not yet implemented.")

        return self.status_codes[status_code]

    def accept_connection(self, conn, addr):
        with conn:
            request = conn.recv(self.max_req_size).decode()
            response = self.handle_request(request, addr)
            conn.sendall(response.encode())

    def run(self):
        # the with keyword is syntax sugar for a try finally block - exceptions and resource clean up e.g.
        # socket.close() will be handled automatically.
        # define socket and type
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            while True:
                s.listen()
                conn, addr = s.accept()
                print(f"{addr} has connected.")
                threading.Thread(target=self.accept_connection, args=(conn, addr)).start()


httpserver = HTTPServer("127.0.0.1")

