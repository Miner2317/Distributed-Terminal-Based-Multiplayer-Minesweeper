import sockets
from sockets.sockets_mod import Socket


class GameServer:
    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.current_connection = Socket.create_client_socket(host, port)

    def set_username(self, name):
        """
        Stubs function  to comunicate with server to set a sent username
        """
        self.current_connection.send_str(sockets.SET_USERNAME_OP)
        self.current_connection.send_str(name)
        return self.current_connection.receive_str()

    def get_server_state(self):
        """
        Stubs function to comunicate with server and chekc if a game is running
        """
        self.current_connection.send_str(sockets.GET_STATE)
        return self.current_connection.receive_str()

    def get_board(self):
        """
        Stubs function to comunicate with server and get the server's version of the board
        """
        self.current_connection.send_str(sockets.GET_BOARD)
        return self.current_connection.receive_str()

    def player_move(self, x, y, username):
        """
        Stubs function to comunicate with server and send data for a player's open cell move
        """
        self.current_connection.send_str(sockets.PLAYER_MOVE)
        self.current_connection.send_int(x, sockets.INT_SIZE)
        self.current_connection.send_int(y, sockets.INT_SIZE)
        self.current_connection.send_str(username)
        return self.current_connection.receive_str()

    def player_flag(self, x, y, username):
        """
        Stubs function to comunicate with server and send data for a player's place flag move
        """
        self.current_connection.send_str(sockets.PLAYER_FLAG)
        self.current_connection.send_int(x, sockets.INT_SIZE)
        self.current_connection.send_int(y, sockets.INT_SIZE)
        self.current_connection.send_str(username)
        return self.current_connection.receive_str()

    def remove_player_flag(self, x, y, username):
        """
        Stubs function to comunicate with server and send data for a player's remove flag move
        """
        self.current_connection.send_str(sockets.REM_PLAYER_FLAG)
        self.current_connection.send_int(x, sockets.INT_SIZE)
        self.current_connection.send_int(y, sockets.INT_SIZE)
        self.current_connection.send_str(username)
        return self.current_connection.receive_str()

    def check_player_life(self, username):
        """
        Stubs function to comunicate with server and check if a player is still alive
        """
        self.current_connection.send_str(sockets.CHECK_LIFE)
        self.current_connection.send_str(username)
        return self.current_connection.receive_str()

    def create_game(self, comprimento, altura, percentagem, username):
        """
        Stubs function to comunicate with server and create a game with sent dimensions
        """
        self.current_connection.send_str(sockets.CREATE_GAME)
        self.current_connection.send_int(comprimento, sockets.INT_SIZE)
        self.current_connection.send_int(altura, sockets.INT_SIZE)
        self.current_connection.send_int(percentagem, sockets.INT_SIZE)
        self.current_connection.send_str(username)
        return self.current_connection.receive_str()

    def get_player_board(self, username):
        """
        Stubs function to comunicate with server and get the player's version of the board
        """
        self.current_connection.send_str(sockets.GET_PLAYER_BOARD)
        self.current_connection.send_str(username)
        return self.current_connection.receive_str()

    def get_leaderboard(self):
        """
        Stubs function to comunicate with server and get the final leaderboards
        """
        self.current_connection.send_str(sockets.GET_LEADER)
        return self.current_connection.receive_str()

    def check_endgame(self):
        """
        Stubs function to comunicate with server and check if the game has ended
        """
        self.current_connection.send_str(sockets.CHECK_ENDGAME)
        return self.current_connection.receive_str()

    def disconnect_user(self, username):
        """
        Stubs function to comunicate with server a player's disconnection
        """
        self.current_connection.send_str(sockets.DISCONNECT_USER)
        self.current_connection.send_str(username)

    def bye(self):
        """
        Stubs function to comunicate with server and disconnect the server
        """
        self.current_connection.send_str(sockets.BYE_OP)
        self.current_connection.close()
