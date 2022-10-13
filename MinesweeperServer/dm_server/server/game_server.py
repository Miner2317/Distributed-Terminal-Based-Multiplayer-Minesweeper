import sockets
from game.game_manager import Game_Manager


class GameServer:
    def __init__(self):
        self.users = []             # List of usernames currently connected to server
        self.ongoing = "0"          # Tag if a game is running or not , "1" for True , "0" for False
        self.game = Game_Manager()  # Ongoing game, or temporary empty game

    def set_username(self, name):
        """
        Checks if username is currently connected to the server
        :param name: username of player
        :return: Sucess or Error tag
        """
        if name in self.users:
            return sockets.ERROR
        else:
            # Username is free
            self.users.append(name)
            return sockets.SUCCESS

    def get_server_state(self):
        """
        :return: str:"0" when no game is running or str:"1" when the game is running
        """
        return self.ongoing

    def create_game(self, comprimento, altura, percentagem):
        """
        Receives int's for game size and percentage of bombs
        If valid, generates the game and sets it as the ongoing one in the server, returns a sucess tag
        Otherwise, returns an error tag
        """
        if (comprimento <= 9 or altura <= 9) or (comprimento >= 24 or altura >= 24) or (
                percentagem < 5 or percentagem > 20):
            return sockets.ERROR
        else:
            self.game = Game_Manager()
            self.game.new_board(comprimento, altura)
            self.game.add_bombs(percentagem)
            self.ongoing = "1"
            return sockets.SUCCESS

    def player_move(self, x, y, username):
        """
        Receives position data and username
        Calls to open that cell and returns the player's resulting board
        """
        update = self.game.player_move(username, x, y)
        return self.game.getstring(update, username)

    def player_flag(self, x, y, username):
        """
        Receives position data and username
        Calls to flag that cell and returns the player's resulting board
        """
        update = self.game.add_player_flag(username, [x, y])
        return self.game.getstring(update, username)

    def rem_player_flag(self, x, y, username):
        """
        Receives position data and username
        Calls to remove a flag from that cell and returns the player's resulting board
        """
        update = self.game.remove_player_flag(username, [x, y])
        return self.game.getstring(update, username)

    def check_life(self, username):
        """
        Receives a username
        Returns True or False based on if the user is still alive in the game
        """
        return self.game.check_player_life(username)

    def check_endgame(self):
        """
        Calls to check if the game is over, if so
        Update server to prepare for a next game
        """
        if self.game.check_finish() == sockets.SUCCESS:
            self.ongoing = "0"
        return self.game.check_finish()

    def get_leader(self):
        """
        Returns string of leaderboard standings
        """
        return self.game.generate_standings()

    def get_board(self):
        """
        Returns string of the system's board
        """
        return self.game.getstring("s", "System")

    def get_player_board(self, username):
        """
        Receives username
        Returns string of the user's board
        """
        return self.game.getstring("s", username)

    def disconnect_user(self, username):
        """
        Removes user from active user's list
        """
        self.users.remove(username)
