import socket
import select
from time import sleep


class Server:

    """
    This class takes two arguments: a host address and a port to initialize the socket
    """

    _package_size = 2048

    def __init__(self, server_ip: str, server_port: int):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((server_ip, server_port))
        self.server.listen(100)
        self.server.setblocking(False)
        self.input = [self.server]
        self.output = []
        self.errors = []
        self.buffer = {}

    def receiving_mode(self):
        while True:
            to_read, to_send, errors = select.select(
                self.input, self.output, self.errors
            )
            for connection in to_read:
                if connection == self.server:
                    new_connection, addr = connection.accept()
                    self.console_formating(addr)
                    new_connection.setblocking(False)
                    self.input.append(new_connection)
                else:
                    data_received = connection.recv(self._package_size).decode("utf-8")
                    if data_received:
                        if self.buffer.get(connection, None):
                            self.buffer[connection].append(data_received)
                        else:
                            self.buffer[connection] = [data_received]
                        if connection not in self.output:
                            self.output.append(connection)
                    else:
                        if connection in self.output:
                            self.output.remove(connection)
                        self.input.remove(connection)
                        connection.close()
                        del self.buffer[connection]
            for connection in to_send:
                client_message = self.buffer.get(connection)
                if client_message:
                    client_message = " ".join(client_message).split(" ")
                    client_message = self.file_handler(client_message)
                    connection.send(client_message)
                else:
                    self.output.remove(connection)
            for connection in errors:
                self.input.remove(connection)
                connection.close()
                del self.buffer[connection]

    def file_handler(self, file):
        if len(file) == 1:
            with open(file[0], "r") as f:
                request_data = f.read().splitlines()
            data_to_send = " ".join(request_data).encode(encoding="utf-8")
            return data_to_send
        elif len(file) > 1:
            with open(file[0], "w") as f:
                text_to_write = " ".join(file[1:])
                f.write(text_to_write) 
            data_to_send = 'Changes accepted'.encode(encoding="utf-8")
            return data_to_send

    def console_formating(self, address: str):
        separator = "_" * 50
        formatted_text = "User connected:\n{} \nIP: {} \nPORT: {}\n{}".format(
            separator, address[0], address[1], separator
        )
        print(formatted_text)


server_1 = Server("127.0.0.1", 6060)
server_1.receiving_mode()
