from socket import socket, timeout
from typing import Union

import sockets


class Socket:
    def __init__(self, connection: socket):
        self._current_connection: socket = connection

    def accept(self) -> Union['Socket', None]:
        try:
            client_connection, _ = self._current_connection.accept()
            return Socket(client_connection)
        except timeout:
            return None

    @property
    def peer_addr(self):
        return self._current_connection.getpeername()

    def receive_int(self, n_bytes: int) -> int:
        """
        :param n_bytes: The number of bytes to read from the current connection
        :return: The next integer read from the current connection
        """
        data = self._current_connection.recv(n_bytes)
        return int.from_bytes(data, byteorder='big', signed=True)

    def send_int(self, value: int, n_bytes: int) -> None:
        """
        :param value: The integer value to be sent to the current connection
        :param n_bytes: The number of bytes to send
        """
        self._current_connection.send(value.to_bytes(n_bytes, byteorder="big", signed=True))

    def receive_str(self) -> str:
        """
        :return: The next string read from the current connection
        """
        n_bytes: int = self.receive_int(sockets.INT_SIZE)
        received: bytes = self._current_connection.recv(n_bytes)
        return received.decode()

    def send_str(self, value: str) -> None:
        """
        :param value: The string value to send to the current connection
        """
        to_send: bytes = value.encode()
        self.send_int(len(to_send), sockets.INT_SIZE)
        self._current_connection.send(to_send)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._current_connection is not None:
            self._current_connection.close()

    @staticmethod
    def create_server_socket(port: int, timeout2: int = None) -> 'Socket':
        new_socket: socket = socket()
        new_socket.bind(('', port))
        new_socket.listen(1)
        new_socket.settimeout(timeout2)
        return Socket(new_socket)

    @staticmethod
    def create_client_socket(host: str, port: int) -> 'Socket':
        new_socket: socket = socket()
        new_socket.connect((host, port))
        return Socket(new_socket)
