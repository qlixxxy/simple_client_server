import socket
import select


class Server:

    """
    This class takes two arguments: a host address and a port to initialize the socket
    """

    _package_size = 1024

    def __init__(self, server_ip: str, server_port: int):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((server_ip, server_port))
        self.server.listen(2000)
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
            if not to_read:
                print("Server is in offline mode")
                break
            for connection in to_read:
                if connection == self.server:
                    new_connection, addr = connection.accept()
                    self.console_formating(addr)
                    new_connection.setblocking(False)
                    self.input.append(new_connection)
                else:
                    collected_data = []
                    while True:
                        try:
                            data_received = connection.recv(self._package_size).decode(
                                "utf-8"
                            )
                        except BlockingIOError:
                            break
                        collected_data.append(data_received)
                    if collected_data:
                        file = "".join(collected_data).split(" ")
                        collected_data.clear()
                        server_response = self.file_handler(file)
                        descriptor = connection.fileno()
                        try:
                            self.buffer[descriptor].append(server_response)
                        except KeyError:
                            self.buffer[descriptor] = [server_response]
                        self.input.remove(connection)
                        if connection not in self.output:
                            self.output.append(connection)
                    else:
                        if connection in self.output:
                            self.output.remove(connection)
                        self.input.remove(connection)
                        connection.close()
            for connection in to_send:
                descriptor = connection.fileno()
                client_message = "".join(self.buffer[descriptor])
                del self.buffer[descriptor]
                connection.send(client_message.encode(encoding="utf-8"))
                if connection in self.output:
                    self.output.remove(connection)
                connection.close()
            for connection in errors:
                self.input.remove(connection)
                if connection in self.output:
                    self.output.remove(connection)
                connection.close()

    def file_handler(self, file):
        if len(file) == 1:
            with open(file[0], "r") as f:
                request_data = f.read().splitlines()
            data_to_send = " ".join(request_data)
            return data_to_send
        elif len(file) > 1:
            with open(file[0], "a") as f:
                text_to_write = " ".join(file[1:])
                f.write(text_to_write)
            data_to_send = "Changes accepted"
            return data_to_send

    def console_formating(self, address: str):
        separator = "_" * 50
        formatted_text = "User connected:\n{} \nIP: {} \nPORT: {}\n{}".format(
            separator, address[0], address[1], separator
        )
        print(formatted_text)