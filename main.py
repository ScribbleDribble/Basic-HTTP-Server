# HTTP is a communication protocol for servers to receive requests and to respond to clients.
# it is an application layer protocol that sits above TCP. HTTP headers describes the communication

# $ telnet google.com 80    # address and port number
# $ GET / HTTP/1.0 # specify the http method, path and protocol and we can get googles home page.

# the first line of the header defines the resource we want to retrieve

import socket
import os
import threading
import logging


class HTTPServer:

    def __init__(self, host, port=8000):
        self.host = host
        self.port = port

        self.max_req_size = 1024
        self.page_contents = {}


        self.status_codes = {"200": "HTTP/1.1 200 OK\n", "400": "HTTP/1.1 400 BAD REQUEST\n",
                             "404": "HTTP/1.1 404 NOT FOUND\n", "505": "HTTP/1.1 505 HTTP VERSION NOT SUPPORTED\n"}

        self.accepted_versions = {"HTTP/1.1", "HTTP/1.0"}

        logging.basicConfig(level=logging.INFO, filename="logs.txt", filemode="w", format='%(asctime)s - %(message)s - %(levelname)s',
                            datefmt='%d-%b-%y %H:%M:%S')

        self.read_html_files()
        self.run()

    def read_html_files(self):

        for html_page in os.listdir(os.getcwd()+"/pages"):
            with open(os.getcwd()+ "/pages/" + html_page, "r") as f:
                text = f.read()
                resource_name = f"/{html_page.split('.')[0]}"
                self.page_contents[resource_name] = text + "\n"

    def is_valid_version(self, client_version: str) -> bool:

        version = ""
        for c in client_version:
            if c.isalnum() or c == "/" or c == ".":
                version += c

        if version not in self.accepted_versions:
            return False
        return True

    def handle_request(self, message: str, addr: str) -> str:

        message = message.split(" ")
        if len(message) < 3:
            logging.info(f"505 from {addr}")
            return self.status_codes["400"]

        # parse header data
        method = message[0]
        requested_resource = message[1]
        client_version = message[2]

        if not self.is_valid_version(client_version):
            logging.info(f"505 OK for {requested_resource} from {addr}")
            return self.get_status_code("505")

        # if we have received a GET request, we must find out the resource they want.
        # dont forget to prepend the HTML status code and version of the protocol.
        response = ""
        if method == "GET":
            if requested_resource not in self.page_contents:
                return self.get_status_code("404")

            response += self.get_status_code("200")
            response += self.page_contents[requested_resource]
            logging.info(f"200 OK for GET {requested_resource} from {addr}")
            return response

        elif method == "POST":
            return "not implemented yet"

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

