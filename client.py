import socket
from time import sleep


class Client:
    def __init__(self, clients_quantity):
        self.clients = [
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            for client in range(clients_quantity)
        ]
        self.server_responses = {}

    def get_request(
        self, server_ip: str, server_port: int, filename: str, text: bool = False
    ):
        for client in self.clients:
            client.connect((server_ip, server_port))
        for index, client in enumerate(self.clients):
            if text:
                request = filename + f" I am the {index} Client\n"
            else:
                request = filename
            client.send(request.encode(encoding="utf-8"))
        for index, client in enumerate(self.clients):
            while True:
                server_response = client.recv(1024).decode("utf-8")
                if not server_response:
                    break
                if self.server_responses.get(index, None):
                    self.server_responses[index].append(server_response)
                else:
                    self.server_responses[index] = [server_response]
        for index, info in self.server_responses.items():
            info = "".join(info)
            print(f'Client {index} got "{info}" message from server')
