import threading
from typing import Set, List
import server
import sockets


class SharedServerState:
    def __init__(self, game_server: server.GameServer, port: int):
        self._clients: Set[sockets.Socket] = set()
        self._keep_running: bool = True
        self._port = port
        self._game_server: server.GameServer = game_server
        self._clients_lock = threading.Lock()
        self._running_lock = threading.Lock()
        self._concurrent_clients = threading.Semaphore(server.MAX_NUMBER_OF_CONCURRENT_CLIENTS)

    def add_client(self, client_socket: sockets.Socket) -> None:
        with self._clients_lock:
            self._clients.add(client_socket)

    def remove_client(self, client_socket: sockets.Socket) -> None:
        with self._clients_lock:
            self._clients.remove(client_socket)

    def stop_server(self) -> None:
        with self._running_lock:
            self._keep_running = False

    @property
    def port(self) -> int:
        return self._port

    @property
    def keep_running(self) -> bool:
        with self._running_lock:
            return self._keep_running

    @property
    def game_server(self) -> server.GameServer:
        return self._game_server

    @property
    def concurrent_clients(self) -> threading.Semaphore:
        return self._concurrent_clients

    def clients(self) -> List[str]:
        result = []
        with self._clients_lock:
            for client_socket in self._clients:
                result.append(client_socket.peer_addr)
        return result
