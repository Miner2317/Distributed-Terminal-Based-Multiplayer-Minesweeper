from stubs import GameServer
from sockets import PORT, SERVER_ADDRESS
from ui.client import Client


def main():
    game_server = GameServer(SERVER_ADDRESS, PORT)
    client = Client(game_server)
    client.run()


main()
