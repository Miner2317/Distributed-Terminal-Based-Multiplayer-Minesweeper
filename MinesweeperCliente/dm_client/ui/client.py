import sockets
from stubs import GameServer


class Client:
    def __init__(self, game_server: GameServer) -> None:
        """
        Creates a dm_client given the control_client_stubs to use
        :param game_server: The control_client_stubs the dm_client will use
        """
        self._server = game_server
        self.username = ""

    def stop_bye(self):
        """
        Disconnects client from server
        :return:
        """
        self._server.bye()

    def get_server_state(self):
        """
        Checks for existence of a running game in the server
        :return: "1" if a game is running, "0" if it's not
        """
        return self._server.get_server_state()

    def set_username(self):
        """
        Asks the client for input of a username until a valid one is found
        :return: None
        """
        username = input("Introduza o username desejado : ")
        result = self._server.set_username(username)
        if result == sockets.SUCCESS:
            self.username = username
            print("O seu username foi escolhido com sucesso.")
        elif result == sockets.ERROR:
            print("Username já está em uso, por favor volte a tentar:")
            self.set_username()

    def main_menu(self, server_state):
        """
        Presents the initial menu for the client based on the possible choices
        :param server_state: "1" for when a game is running, "0" for when its not.
        :return: None
        """
        if server_state == "0":
            print("\n         Opções:                             \n")
            print("           1 - Criar um jogo                     ")
            print("           2 - Sair                          \n\n")
            opc = input("Introduza a sua opção : ")
            while opc not in ["1", "2"]:
                print("Por favor volte a tentar. ")
                opc = input("Introduza a sua opção : ")
            if opc == "1":
                server_update = self.get_server_state()
                if server_update == "1":
                    print("Alguém já iniciou um jogo.")
                    self.main_menu(server_update)
                else:
                    self.present_join(server_state)
            elif opc == "2":
                self._server.disconnect_user(self.username)
                self.stop_bye()
        if server_state == "1":
            print("\n         Opções:                             \n")
            print("           1 - Entrar no jogo a decorrer         ")
            print("           2 - Sair                          \n\n")
            opc = input("Introduza a sua opção : ")
            while opc not in ["1", "2"]:
                print("Por favor volte a tentar. ")
                opc = input("Introduza a sua opção : ")
            if opc == "1":
                self.present_join(server_state)
            elif opc == "2":
                self._server.disconnect_user(self.username)
                self.stop_bye()

    def present_join(self, menu):
        """
        Presents the menu when a game is being created or when joining one
        """
        # Nenhum jogo a decorrer
        if menu == "0":
            print("Os seguintes valores devem estar entre 10 a 23 inclusivamente.")
            dimensaox = int(input("Introduza o comprimento da sua board:   "))
            dimensaoy = int(input("Introduza a altura da sua board:  "))
            print("O seguinte valor deve estar entre 5 a 20 (por cento) inclusivamente :   ")
            percentagem = int(input("Introduza a percentagem de minas :"))

            server_update = self.get_server_state()
            if server_update == "1":
                print("Alguém já iniciou um jogo.")
                self.main_menu(server_update)
            else:
                result = self._server.create_game(dimensaox, dimensaoy, percentagem, self.username)
                if result == sockets.ERROR:
                    print("Introduziu dimensões erradas. Por favor volte a tentar.")
                    self.present_join(menu)
                elif result == sockets.SUCCESS:
                    print("Jogo criado com sucesso")
                    self.play_game()
        # Game is running
        elif menu == "1":
            print("Juntou-se ao jogo a decorrer .")
            self.play_game()

    def showboard(self, boardstring):
        """
        Prints the game board from a received string version of it
        """
        lista = boardstring.split("$")
        top = " "
        listasize= lista[0].split(",")
        for x in range(len(listasize)):
            if x >= 10:
                top += "  " + str(x) + " "
            else:
                top += "  " + str(x) + "  "
        print(top)
        listafinal = []
        for linha in lista:
            linha2 = []
            listaspaces = linha.split(",")
            for space in listaspaces:
                linha2.append(space)
            listafinal.append(linha2)
        contador = 0
        for linha in listafinal:
            view = str(contador) + " "
            contador += 1
            for space in linha:
                # If flagged, first show flag
                if space == "FM":
                    view += ("\x1b[6;30;" + str(42) + "m" + " 🚩 " + "\x1b[0m" + " ")
                elif space == "F":
                    view += ("\x1b[6;30;" + str(44) + "m" + " 🚩 " + "\x1b[0m" + " ")
                # Not visible, don't show any other details
                elif space == "B":
                    view += ("\x1b[6;30;" + str(41) + "m" + " 💣 " + "\x1b[0m" + " ")
                elif space == "H":
                    view += ("\x1b[6;30;" + str(100) + "m" + "    " + "\x1b[0m" + " ")
                elif space == "0":
                    view += ("\x1b[6;30;" + str(47) + "m" + "    " + "\x1b[0m" + " ")
                else:
                    view += ("\x1b[6;30;" + str(47) + "m" + " " + space + "  " + "\x1b[0m" + " ")
            view += "\n"
            print(view)

    def dead_menu(self):
        """
        Menu to show to the player that lost the game, whilst game is still running
        :return:
        """
        while True:
            print("Infelizmente, perdeu o jogo.")
            print("Pode pedir uma atualização ao servidor para ver como está a decorrer o jogo. ")
            print("       1 - Atualizar.          ")
            print("       2 - Sair.               ")
            opc = input("Introduza a sua opção :  ")
            while opc not in ["1", "2"]:
                print("Por favor volte a tentar. ")
                opc = input("Introduza a sua opção : ")
            if opc == "1":
                result = self._server.check_endgame()
                if result == sockets.SUCCESS:
                    self.game_over_menu()
                    break
                else:
                    boardstring = self._server.get_player_board(self.username)
                    self.showboard(boardstring)
            elif opc == "2":
                self._server.disconnect_user(self.username)
                self._server.bye()
                break

    def game_over_menu(self):
        """
        Menu to show to the player when the game is over, such as leaderboards
        :return:
        """
        print("Board Final : ")
        boardstring = self._server.get_player_board(self.username)
        self.showboard(boardstring)
        print("Leaderboards : ")
        self.print_leaderboards(self._server.get_leaderboard())
        input("Pressione enter para sair do jogo.")
        self._server.disconnect_user(self.username)
        self.stop_bye()

    def print_leaderboards(self, leaderboardstring):
        """
        Prints player's username, score and time from a received string
        """
        leaders = leaderboardstring.split("$")
        for linha in leaders:
            linha = linha.replace("]", "")
            linha = linha.replace("[", "")
            linha = linha.replace("'", "")
            elements = linha.split(",")
            print("NOME : ", elements[0], "   PONTOS : ", elements[1], "  TEMPO DE JOGO : ", elements[2])

    def play_game(self):
        """
        Menu whilst a game is running
        """
        boardstring = self._server.get_board()
        self.showboard(boardstring)
        while True:
            # Check if game is still running
            result = self._server.check_endgame()
            if result == sockets.SUCCESS:
                # If the game is over, break from cycle and present game_over screen
                self.game_over_menu()
                break
            else:
                print("     Opções :                            ")
                print("     1 - Abrir uma célula                ")
                print("     2 - Colocar uma bandeira            ")
                print("     3 - Tirar uma bandeira              ")
                print("     4 - Atualizar board                 ")
                print("     5 - Desistir do jogo                ")
                opc = input("Introduza a sua opção :  ")
                while opc not in ["1", "2", "3", "4", "5"]:
                    print("Por favor volte a tentar. ")
                    opc = input("Introduza a sua opção : ")
                if opc == "1":
                    x = int(input(" Introduza o X desejado para abrir : "))
                    y = int(input(" Introduza o Y desejado para abrir ? : "))
                    # Show's player board
                    boardstring = self._server.player_move(x, y, self.username)
                    self.showboard(boardstring)
                    # Checks if the player is still alive
                    playeris_alive = self._server.check_player_life(self.username)
                    if playeris_alive == sockets.ERROR:
                        # Means he opened a bomb, redirect to dead_menu
                        self.dead_menu()
                        break
                elif opc == "2":
                    x = int(input(" Introduza o X desejado para colocar uma bandeira : "))
                    y = int(input(" Introduza o Y desejado para colocar uma bandeira : "))
                    boardstring = self._server.player_flag(x, y, self.username)
                    self.showboard(boardstring)
                elif opc == "3":
                    x = int(input(" Introduza o X desejado para remover uma bandeira : "))
                    y = int(input(" Introduza o Y desejado para remover uma bandeira : "))
                    boardstring = self._server.remove_player_flag(x, y, self.username)
                    self.showboard(boardstring)
                elif opc == "4":
                    print("Board Atualizada: ")
                    boardstring = self._server.get_player_board(self.username)
                    self.showboard(boardstring)
                elif opc == "5":
                    print("Desistiu do jogo. ")
                    self._server.disconnect_user(self.username)
                    self._server.bye()
                    break

    def run(self) -> None:
        """
        Main client run function
        """
        print("Bem vindo ao sistema multi-jogador Minesweeper.")
        self.set_username()
        server_state = self.get_server_state()
        self.main_menu(server_state)
