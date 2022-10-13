from sockets.sockets_mod import Socket

INT_SIZE = 8
PORT = 35000
SERVER_ADDRESS = "localhost"

BYE_OP = "bye"
SUCCESS = "success"
ERROR = "error"
SET_USERNAME_OP = "set_username_op"
GET_STATE = "get_state"
CREATE_GAME = "create_game"
JOIN_GAME = "join_game"
GET_BOARD = "get_board"
PLAYER_MOVE = "player_move"
PLAYER_FLAG = "player_flag"
REM_PLAYER_FLAG = "rem_player_flag"
CHECK_LIFE = "check_life"
GET_PLAYER_BOARD = "get_player_board"
CHECK_ENDGAME = "check_endgame"
GET_LEADER = "get_leader"
DISCONNECT_USER = "disconnect_user"