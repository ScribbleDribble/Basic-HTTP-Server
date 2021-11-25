# HTTP is a communication protocol for servers to receive requests and to respond to clients.
# it is an application layer protocol that sits above TCP. HTTP headers describes the communication

# $ telnet google.com 80    # address and port number
# $ GET / HTTP/1.0 # specify the http method, path and protocol and we can get googles home page.
# that was all we needed to get google's home page

# the first line of the header defines the resource we want to retrieve

import socket
import os


class HTTPServer:


    def __init__(self, host, port=8000):
        self.host = host
        self.port = port

        self.max_req_size = 1024
        self.page_contents = {}

        self.status_codes = {"200": "HTTP/1.1 200 OK\n", "400": "HTTP/1.1 400 BAD REQUEST\n",
                             "404": "HTTP/1.1 404 NOT FOUND\n"}

        self.read_html_files()

    def read_html_files(self):

        for html_page in os.listdir(os.getcwd()+"/pages"):
            with open(os.getcwd()+ "/pages/" + html_page, "r") as f:
                text = f.read()
                resource_name = f"/{html_page.split('.')[0]}"
                self.page_contents[resource_name] = text



    def handle_request(self, message: str, addr):
        message = message.split(" ")

        # parse header data
        method = message[0]
        requested_resource = message[1]
        response = ""

        # if we have received a GET request, we must find out the resource they want.
        # dont forget to prepend the HTML status code and version of the protocol.
        if method == "GET":

            if requested_resource not in self.page_contents:
                return self.status_codes["404"]

            response += self.status_codes["200"]
            response += self.page_contents[requested_resource]
            print(f"200 OK for GET {requested_resource} from {addr}")
            return response

        elif method == "POST":
            pass


        else:
            return self.status_codes["400"]


    def startup(self):
            # define socket and type
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                while True:
                    s.listen()
                    conn, addr = s.accept()

                    # the with keyword is syntax sugar for a try finally block - exceptions and resource clean up e.g.
                    # socket.close() will be handled automatically.
                    with conn:
                        print(f"{addr} has connected.")
                        request = conn.recv(self.max_req_size).decode()
                        response = self.handle_request(request, addr)
                        conn.sendall(response.encode())



httpserver = HTTPServer("127.0.0.1")
httpserver.startup()
