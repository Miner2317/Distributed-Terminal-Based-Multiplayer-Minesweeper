from threading import Thread
import logging
from typing import Union
import server
import skeletons
import sockets


class ServerControlSession(Thread):
    """Session to control the dm_server"""

    def __init__(self, shared_state: skeletons.SharedServerState):
        """
        Constructs a thread to hold a session with the dm_client that controls the dm_server

        param shared_state: The dm_server's shared state
        """
        Thread.__init__(self)
        self._shared_state = shared_state
        self._control_client_socket: Union[sockets.Socket, None] = None

    def _list_clients(self) -> None:
        clients = self._shared_state.clients()
        self._control_client_socket.send_int(len(clients), sockets.INT_SIZE)
        for client in self._shared_state.clients():
            self._control_client_socket.send_str(str(client))

    def run(self):
        """Maintains a session with the dm_client, following the established protocol"""
        with sockets.Socket.create_server_socket(self._shared_state.port + 1, server.ACCEPT_TIMEOUT) as control_socket:
            logging.info("Waiting for CONTROL clients to connect on port " + str(self._shared_state.port + 1))
            while self._shared_state.keep_running:
                # wait for a control dm_client at a time
                self._handle_control_client(control_socket)

    def _handle_control_client(self, control_socket: sockets.Socket):
        self._control_client_socket = control_socket.accept()
        if self._control_client_socket is not None:
            logging.debug("CONTROL dm_client " + str(self._control_client_socket.peer_addr) + " just connected")
            last_request = False
            while not last_request:
                last_request = self.dispatch_request()
            logging.debug("CONTROL dm_client " + str(self._control_client_socket.peer_addr) + " disconnected")
            self._control_client_socket.close()

    def dispatch_request(self) -> bool:
        request_type = self._control_client_socket.receive_str()
        last_request = False
        if request_type == sockets.BYE_OP:
            last_request = True
        return last_request
