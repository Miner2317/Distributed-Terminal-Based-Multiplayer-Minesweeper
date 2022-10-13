import threading
from threading import Thread
import logging
import skeletons
import sockets


class ClientSession(Thread):
    def __init__(self, shared_state: skeletons.SharedServerState, client_socket: sockets.Socket):
        """
        Constructs a thread to hold a session with the dm_client

        param shared_state: The dm_server's state shared by threads
        param client_socket: The dm_client's socket
        """
        Thread.__init__(self)
        self._shared_state = shared_state
        self._client_connection = client_socket

    def run(self):
        """
        Maintains a session with the dm_client, following the established protocol
        """
        with self._client_connection as client:
            logging.debug("Client " + str(client.peer_addr) + " just connected")
            last_request = False
            while not last_request:
                last_request = self.dispatch_request()
            logging.debug("Client " + str(client.peer_addr) + " disconnected")
            self._shared_state.remove_client(self._client_connection)
            self._shared_state.concurrent_clients.release()

    def get_server_state(self):
        """
        Asks server if a game is running or not
        :return: int:0 when no game is running or int:1 when the game is running
        """
        with threading.Lock():
            result = self._shared_state.game_server.get_server_state()
            self._client_connection.send_str(result)

    def _set_username(self):
        """
        Attempts to add username to server's list
        Displays entry or attempt in server terminal
        Sends a sucess or error tag
        """
        with threading.Lock():
            username = self._client_connection.receive_str()
            result = self._shared_state.game_server.set_username(username)
            if result == sockets.SUCCESS:
                print("O utilizador " + username + " entrou no sistema.")
            elif result == sockets.ERROR:
                print("Alguém tentou entrar com o username " + username + " mas este já estava no sistema.")
            self._client_connection.send_str(result)

    def create_game(self):
        """
        Receives username and several integers for game data
        Tells server to attempt to create a game with the data received
        Sends sucess or error tag
        """
        with threading.Lock():
            comprimento = self._client_connection.receive_int(sockets.INT_SIZE)
            altura = self._client_connection.receive_int(sockets.INT_SIZE)
            percentagem = self._client_connection.receive_int(sockets.INT_SIZE)
            username = self._client_connection.receive_str()
            result = self._shared_state.game_server.create_game(comprimento, altura, percentagem)
            if result == sockets.SUCCESS:
                print("O utilizador " + username + " criou um novo jogo de dimensões e percentagem : " + str(
                    [comprimento, altura, percentagem]) + ".")
            elif result == sockets.ERROR:
                print("O utilizador " + username + " tentou criar um novo jogo de dimensões e percentagem inválidas.")
            self._client_connection.send_str(result)

    def get_board(self):
        """
        Function to get the server version of the board
        """
        with threading.Lock():
            result = self._shared_state.game_server.get_board()
            self._client_connection.send_str(result)

    def player_move(self):
        """
        Receives data on the position the player wants to open, and respective player
        Sends the resulting board back to the client
        """
        with threading.Lock():
            x = self._client_connection.receive_int(sockets.INT_SIZE)
            y = self._client_connection.receive_int(sockets.INT_SIZE)
            username = self._client_connection.receive_str()

            result = self._shared_state.game_server.player_move(x, y, username)
            self._client_connection.send_str(result)

    def player_flag(self):
        """
        Receives data on the position the player wants to flag, and respective player
        Sends the resulting board back to the client
        """
        with threading.Lock():
            x = self._client_connection.receive_int(sockets.INT_SIZE)
            y = self._client_connection.receive_int(sockets.INT_SIZE)
            username = self._client_connection.receive_str()
            result = self._shared_state.game_server.player_flag(x, y, username)
            self._client_connection.send_str(result)

    def rem_player_flag(self):
        """
        Receives data on the position the player wants to remove a flag from, and respective player
        Sends the resulting board back to the client
        """
        with threading.Lock():
            x = self._client_connection.receive_int(sockets.INT_SIZE)
            y = self._client_connection.receive_int(sockets.INT_SIZE)
            username = self._client_connection.receive_str()
            result = self._shared_state.game_server.rem_player_flag(x, y, username)
            self._client_connection.send_str(result)

    def check_life(self):
        """
        Receives a username
        Checks if username is still alive in the game
        """
        with threading.Lock():
            username = self._client_connection.receive_str()
            result = self._shared_state.game_server.check_life(username)
            if result:
                self._client_connection.send_str(sockets.ERROR)
            elif not result:
                self._client_connection.send_str(sockets.SUCCESS)

    def get_player_board(self):
        """
        Receives a username
        Sends the user's board back to the client
        """
        with threading.Lock():
            username = self._client_connection.receive_str()
            result = self._shared_state.game_server.get_player_board(username)
            self._client_connection.send_str(result)

    def check_endgame(self):
        """
        Checks if a game has ended
        """
        with threading.Lock():
            result = self._shared_state.game_server.check_endgame()
            self._client_connection.send_str(result)

    def get_leader(self):
        """
        Asks server to print end of game leaderboards
        """
        result = self._shared_state.game_server.get_leader()
        self._client_connection.send_str(result)

    def disconnect_user(self):
        """
        Receives a username
        Removes user from active user's in server
        """
        username = self._client_connection.receive_str()
        self._shared_state.game_server.disconnect_user(username)

    def dispatch_request(self) -> bool:
        """
        Dispatches requests based on type
        :return: last_request: True/False
        """
        request_type = self._client_connection.receive_str()
        last_request = False
        if request_type == sockets.SET_USERNAME_OP:
            self._set_username()
        elif request_type == sockets.GET_STATE:
            self.get_server_state()
        elif request_type == sockets.CREATE_GAME:
            self.create_game()
        elif request_type == sockets.GET_BOARD:
            self.get_board()
        elif request_type == sockets.GET_PLAYER_BOARD:
            self.get_player_board()
        elif request_type == sockets.PLAYER_MOVE:
            self.player_move()
        elif request_type == sockets.PLAYER_FLAG:
            self.player_flag()
        elif request_type == sockets.REM_PLAYER_FLAG:
            self.rem_player_flag()
        elif request_type == sockets.CHECK_LIFE:
            self.check_life()
        elif request_type == sockets.CHECK_ENDGAME:
            self.check_endgame()
        elif request_type == sockets.GET_LEADER:
            self.get_leader()
        elif request_type == sockets.DISCONNECT_USER:
            self.disconnect_user()
        elif request_type == sockets.BYE_OP:
            last_request = True
        return last_request
