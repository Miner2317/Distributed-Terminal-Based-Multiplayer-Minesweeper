import datetime
import sockets
from game.space import Space
import random


class Game_Manager:
    def __init__(self):
        self.board = []            # server side game board
        self.playerdata = {}       # Dictionary {username:points} to store a player's points
        self.movedata = {}         # Dictionary {username:[[firsttime,lastesttime]]} to store move times
        self.flaggedmines = {}     # Dictionary {username:nminasflagged} to store a player's number of flagged mines
        self.deadPlayers = []      # List of usernames that lost to bombs

    def new_board(self, comprimento, altura):
        """
        Receives ints for board size and generates it
        """
        dados = []
        for n in range(altura):
            linha = []
            for i in range(comprimento):
                linha.append(Space(n + 1, i + 1, 0, "", 0, 0, 0))
            dados.append(linha)
        self.board = dados

    def add_bombs(self, percentage):
        """
        Receives percentages of bombs to add to board, randomizes locations and adds them
        """
        # Get number of bombs to put
        n_bombs = int((len(self.board) * len(self.board[0])) * (percentage / 100))
        count = 0
        while count < n_bombs:
            # Randomize position
            randomx = random.randint(0, len(self.board))
            randomy = random.randint(0, len(self.board[0]))

            # Set as bomb
            if self.board[randomx - 1][randomy - 1].bomb == 0:
                self.board[randomx - 1][randomy - 1].bomb = 1
                count += 1
            else:
                # Spot was already a bomb, cycle continues
                pass

        # After adding bombs, update surrounding bombs for every space
        for linha in self.board:
            for space in linha:
                self.check_bombs(space)

    def add_player_flag(self, username, flagposition):
        """
        Receives user and list of [x,y] in which to place a flag
        Check if its possible and does so.
        """
        x = flagposition[1]
        y = flagposition[0]
        pos = self.board[x][y]
        if (pos.visible == 1) or (pos.flagged == 1):
            # Spot was visible or was already a flag
            pass
        else:
            # Spot is available
            pos.flagged = 1
            pos.flaggedby = username
            if pos.bomb == 1:
                # Flagged spot was a bomb, update points and number of flagged mines
                if username not in self.playerdata.keys():
                    self.playerdata[username] = 1
                else:
                    self.playerdata[username] += 1
                if username not in self.flaggedmines.keys():
                    self.flaggedmines[username] = 1
                else:
                    self.flaggedmines[username] += 1
            else:
                # Flagged spot was not a bomb, update points
                if username not in self.playerdata.keys():
                    self.playerdata[username] = -3
                else:
                    self.playerdata[username] += (-3)
            # Update player times and print in server terminal

            self.update_player_time(username)
            self.system_print("add_flag", username)
        return self.board

    def remove_player_flag(self, username, flagposition):
        """
        Receives user and list of [x,y] in which to remove a flag
        Check if its possible and does so.
        """
        x = flagposition[1]
        y = flagposition[0]
        pos = self.board[x][y]
        if pos.flagged == 1 and pos.flaggedby == username:
            # Spot is flagged by the user
            pos.flagged = 0
            pos.flaggedby = ""
            pos.visible = 0
            self.update_player_time(username)
            self.system_print("rem_flag", username)
        else:
            # Spot is not a flag or flagged by someone else
            pass
        return self.board

    def update_player_time(self, username):
        """
        Receives a username and updates the latest move savved
        """
        currenttime = datetime.datetime.now()
        if username in self.movedata.keys():
            playercurrenttime = self.movedata[username]
            playercurrenttime[1] = currenttime
            self.movedata[username] = playercurrenttime
        else:
            # It's a player's first move
            self.movedata[username] = [currenttime, currenttime]

    def check_finish(self):
        """
        Check if all the spots are visible or flagged
        """
        check = 0
        for linha in self.board:
            for space in linha:
                if space.visible == 0 and space.flagged == 0:
                    # Hidden space without a flag
                    check += 1
        if check == 0:
            # If the check equals 0, then that means the game is over
            self.generate_standings()
            return sockets.SUCCESS
        else:
            # Continue the game
            return sockets.ERROR

    def system_print(self, update_type, username):
        """
        Prints information in the server terminal about the received move
        """
        if update_type == "move":
            print("O utilizador " + username + " abriu uma célula.")
            if username in self.deadPlayers:
                print("O utilizador perdeu o jogo aqui.")
        elif update_type == "add_flag":
            print("O utilizador " + username + " adicionou uma flag.")
        elif update_type == "rem_flag":
            print("O utilizador " + username + " removeu uma flag.")
        usertime = float((self.movedata[username][1] - self.movedata[username][0]).total_seconds())
        if usertime == float(0):
            print("Tempo atual deste user é de 0s é o seu primeiro move.")
        else:
            print("Tempo atual deste user é de "+str(usertime)+"s.")
        nminas = 0
        if username in self.flaggedmines.keys():
            nminas = self.flaggedmines[username]
        print("Número de minas assinaladas por este user : " + str(nminas) + ".")
        print("Board atual :")
        self.showboard("s", self.board)

    def generate_standings(self):
        """
        Generates leaderboards at the end of a game
        Sorts players by points, and in a case of a tie, sorts the tie by least time
        """
        playeralldata = []
        for user in self.playerdata.keys():
            if user in self.movedata.keys():
                playeralldata.append([user, self.playerdata[user],
                                      float((self.movedata[user][1] - self.movedata[user][0]).total_seconds())])
        # Sort by moves
        playeralldata.sort(key=lambda x: x[1], reverse=True)
        # Run tied by time several times
        for x in range(len(playeralldata) - 1):
            for linha in range(len(playeralldata) - 1):
                lista = []
                if playeralldata[linha][1] == playeralldata[linha + 1][1]:
                    # Then these 2 players are a tie
                    lista.append(playeralldata[linha])
                    lista.append(playeralldata[linha + 1])
                    # Sort by least time
                    lista.sort(key=lambda x: x[2])
                    playeralldata[linha] = lista[0]
                    playeralldata[linha + 1] = lista[1]
        leaderstring = ""
        for linha in playeralldata:
            leaderstring += str(linha) + "$"
        leaderstring = leaderstring[:-1]
        return leaderstring

    def check_bombs(self, space):
        """
        Checks for bombs surrounding a given space
        """
        if space.bomb == 1:
            return None
        else:
            n_bombs = 0
            x = space.xposition
            y = space.yposition
            # Generate 8 surrounding positions
            positions = [[x - 1, y - 1], [x, y - 1], [x + 1, y - 1], [x - 1, y], [x + 1, y], [x - 1, y + 1], [x, y + 1],
                         [x + 1, y + 1]]
            valid_positions = []
            # Check which positions are out of bounds
            for position in positions:
                if position[0] <= 0 or position[0] > len(self.board):
                    # Out of bonds by X
                    pass
                elif position[1] <= 0 or position[1] > len(self.board[0]):
                    # Out of bonds by Y
                    pass
                else:
                    # Valid position
                    valid_positions.append(position)
            # Check valid positions for bombs
            if len(valid_positions) == 0:
                pass
            else:
                for validposition in valid_positions:
                    if self.board[validposition[0] - 1][validposition[1] - 1].bomb == 1:
                        n_bombs += 1
            # Set new surrounding bombs value
            space.surrounding = n_bombs

    def showboard(self, board, username):
        """
        Displays the board of a certain received user
        """
        if board == "s":
            board = self.board
        for linha in board:
            view = " "
            for space in linha:
                # If flagged, first show flag
                if space.flagged == 1:
                    if space.flaggedby == username:
                        view += ("\x1b[6;30;" + str(42) + "m" + " 🚩 " + "\x1b[0m" + " ")
                    else:
                        view += ("\x1b[6;30;" + str(44) + "m" + " 🚩 " + "\x1b[0m" + " ")
                # Not visible, don't show any other details
                elif space.visible == 0:
                    view += ("\x1b[6;31;" + str(100) + "m" + "    " + "\x1b[0m" + " ")
                elif space.bomb == 1:
                    view += ("\x1b[6;30;" + str(41) + "m" + " 💣 " + "\x1b[0m" + " ")
                elif space.surrounding != 0:
                    view += ("\x1b[6;30;" + str(47) + "m" + " " + str(space.surrounding) + "  " + "\x1b[0m" + " ")
                else:
                    view += ("\x1b[6;30;" + str(47) + "m" + "    " + "\x1b[0m" + " ")
            view += "\n"
            print(view)

    def check_player_life(self, username):
        """
        Checks if a given user is in the list of players that have lost
        """
        if username in self.deadPlayers:
            return True
        else:
            return False

    def copyboard(self):
        """
        Makes and returns a copy of the server board
        """
        copy = []
        for linha in self.board:
            linha2 = []
            for space in linha:
                linha2.append(
                    Space(space.xposition, space.yposition, space.flagged, space.flaggedby, space.bomb, space.visible,
                          space.surrounding))
            copy.append(linha2)
        return copy

    def player_move(self, username, y, x):
        """
        Receives a username and 2 coordinates to open a cell when possible
        """
        if self.board[x][y].visible == 1 or self.board[x][y].flagged == 1:
            # Position was already visible or was a flag, impossible move
            return self.board
        else:
            if self.board[x][y].bomb == 1:
                # If spot was a bomb, show that the user lost and his version of the board, but keep the server's as is
                copy = self.copyboard()
                copy[x][y].visible = 1
                self.board[x][y].visible = 0
                self.deadPlayers.append(username)
                if username in self.playerdata.keys():
                    pass
                else:
                    # If his first move was hitting a bomb
                    self.playerdata[username] = 0
                # Update user's latest move time and print info to the server terminal
                self.update_player_time(username)
                self.system_print("move", username)
                return copy
            elif self.board[x][y].surrounding != 0:
                # Spot was a number, stop there
                self.board[x][y].visible = 1
                self.update_player_time(username)
                return self.board
            else:
                # Spot was an empty spot
                self.board[x][y].visible = 1
                self.update_player_time(username)
                # Generate 8 surrounding positions
                positions = [[x - 1, y - 1], [x, y - 1], [x + 1, y - 1], [x - 1, y], [x + 1, y], [x - 1, y + 1],
                             [x, y + 1],
                             [x + 1, y + 1]]
                valid_positions = []
                # Check which positions are out of bounds
                for position in positions:
                    if position[0] < 0 or position[0] >= len(self.board):
                        # Out of bonds by X
                        pass
                    elif position[1] < 0 or position[1] >= len(self.board[0]):
                        # Out of bonds by Y
                        pass
                    else:
                        # Valid position
                        valid_positions.append(position)

                positions_to_check = []
                # All spaces around an empty space are either a number, or another empty space, so we can set as visible
                for position in valid_positions:
                    self.board[position[0]][position[1]].visible = 1
                    # Save only empty spaces for next check
                    if self.board[position[0]][position[1]].surrounding != 0:
                        pass
                    else:
                        positions_to_check.append(position)

                while len(positions_to_check) > 0:
                    active_pos = positions_to_check.pop(0)
                    x = active_pos[0]
                    y = active_pos[1]
                    # Generate valid surrounding positions of given empty space
                    # Generate 8 surrounding positions
                    positions = [[x - 1, y - 1], [x, y - 1], [x + 1, y - 1], [x - 1, y], [x + 1, y], [x - 1, y + 1],
                                 [x, y + 1], [x + 1, y + 1]]
                    valid_positions = []
                    # Check which positions are out of bounds
                    for position in positions:
                        if position[0] < 0 or position[0] >= len(self.board):
                            # Out of bonds by X
                            pass
                        elif position[1] < 0 or position[1] >= len(self.board[0]):
                            # Out of bonds by Y
                            pass
                        else:
                            # Valid position
                            valid_positions.append(position)
                    hidden_positions = []
                    # Remove positions that are already visible
                    for position in valid_positions:
                        if self.board[position[0]][position[1]].visible == 1:
                            pass
                        else:
                            hidden_positions.append(position)

                    for position in hidden_positions:
                        # If the new spot is a number, simply open it
                        if self.board[position[0]][position[1]].surrounding != 0:
                            # If the new spot is a number, simply open it
                            self.board[position[0]][position[1]].visible = 1
                        else:
                            # Set new empty space to visible and add it to future positions to check
                            self.board[position[0]][position[1]].visible = 1
                            positions_to_check.append(position)
                self.update_player_time(username)
                self.system_print("move", username)
                return self.board

    def getstring(self, board, username):
        """
        Generates and returns the string version of a given board's view for a certain user
        """
        if board == "s":
            board = self.board
        finalstr = ""
        for linha in board:
            strlinha = ""
            for space in linha:
                if space.flagged == 1 and space.flaggedby == username:
                    # FM = Flagged by given user
                    strlinha += "FM,"
                elif space.flagged == 1:
                    # F = Flagged by other users
                    strlinha += "F,"
                elif space.bomb == 1 and space.visible == 1:
                    # B = Visible bomb for this user
                    strlinha += "B,"
                elif space.visible == 1:
                    strlinha += str(space.surrounding) + ","
                elif space.visible == 0:
                    # H = Hidden space
                    strlinha += "H,"
            strlinha = strlinha[:-1]
            finalstr += strlinha + "$"
        finalstr = finalstr[:-1]
        return finalstr
