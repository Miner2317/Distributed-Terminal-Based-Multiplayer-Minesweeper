import server
import logging
import skeletons
import sockets


class GameServer:
    def __init__(self, port: int, game_server: server.GameServer) -> None:
        """
        Creates a dm_client given the dm_server dm_server to use
        :param port: The math dm_server port of the host the dm_client will use
        """
        super().__init__()
        self._state = skeletons.SharedServerState(game_server, port)
        logging.basicConfig(filename=server.LOG_FILENAME,
                            level=server.LOG_LEVEL,
                            format='%(asctime)s (%(levelname)s): %(message)s')

    def run(self) -> None:
        """
        Runs the dm_server
        """
        print("Boot do server.")
        skeletons.ServerControlSession(self._state).start()

        with sockets.Socket.create_server_socket(self._state.port, server.ACCEPT_TIMEOUT) as server_socket:
            logging.info("Waiting for clients to connect on port " + str(self._state.port))

            while self._state.keep_running:
                self._state.concurrent_clients.acquire()
                client_socket = server_socket.accept()
                if client_socket is not None:
                    self._state.add_client(client_socket)
                    skeletons.ClientSession(self._state, client_socket).start()
                else:
                    self._state.concurrent_clients.release()

            logging.info("Waiting for clients to terminate...")

        logging.info("Server stopped")
