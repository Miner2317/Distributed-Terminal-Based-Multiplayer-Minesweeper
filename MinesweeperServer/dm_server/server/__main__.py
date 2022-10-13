import skeletons
from server import GameServer
from sockets import PORT


def main():
    skeletons.GameServer(PORT, GameServer()).run()

main()
