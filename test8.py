import socket
import select
import sys
import os
import pickle
import time


def clear_scr():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_welcome(welcome_text):
    height = len(welcome_text)
    for x in range(height):
        clear_scr()
        lines = height - x
        while lines:
            print()
            lines -= 1
        for y in range(x+1):
            print(welcome_text[y])
        time.sleep(0.3)


def print_game(game):
    clear_scr()
    letters = ["A: ", "B: ", "C: ", "D: ", "E: ", "F: ", "G: ", "H: ", "I: "]

    for x in range(len(game)):
        print(letters[x], end="")
        col = game[x]
        while col:
            print("╔╗ ", end="")
            col -= 1
        print("\n   ", end="")
        col = game[x]
        while col:
            print("╚╝ ", end="")
            col -= 1
        print()


def update_game(socket_server):
    game = b''
    new_game_chunk = True
    while True:
        game_chunk = socket_server.recv(16)
        if not game_chunk:
            print("You were disconnected from the server.)")
            socket_server.close()
            sys.exit()
        if new_game_chunk:
            game_length = int(game_chunk[:HEADER_LENGTH])
            new_game_chunk = False
        
        game += game_chunk

        if len(game)-HEADER_LENGTH == game_length:
            return pickle.loads(game[HEADER_LENGTH:])


def send_to_server(socket_server, my_command):
    my_command = f"{len(my_command):<{HEADER_LENGTH}}".encode("utf-8") + my_command.encode("utf-8")
    try:
        socket_server.send(my_command)
    except:
        print("You were disconnected from the server.")
        socket_server.close()
        sys.exit(1)


def get_server_move(socket_server):
    header = socket_server.recv(HEADER_LENGTH)
    if not header:
        print("You were disconnected from the server.")
        socket_server.close()
        sys.exit(1)
    opponent_move_length = int(header.decode("utf-8"))
    return socket_server.recv(opponent_move_length).decode("utf-8")


def valid_move(command, game):

    if len(command) != 2:
        return False

    if not command[0].isdigit():
        return False

    if not command[1].isalpha():
        return False

    row = ord(command[1].lower()) - ord('a')
    if row >= len(game):
        return False

    if int(command[0]) > game[row]:
        return False

    return True



HEADER_LENGTH = 10
IP = "192.168.56.110"
PORT = 8888

welcome_text = [
    "***********************************************************************************************",
    "*    ██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗    ████████╗ ██████╗      *",
    "*    ██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝    ╚══██╔══╝██╔═══██╗     *",
    "*    ██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗         ██║   ██║   ██║     *",
    "*    ██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝         ██║   ██║   ██║     *",
    "*    ╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗       ██║   ╚██████╔╝     *",
    "*     ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝       ╚═╝    ╚═════╝      *",
    "*                                                                                             *",
    "*         ███╗   ██╗██╗███╗   ███╗███████╗     ██████╗  █████╗ ███╗   ███╗███████╗            *",
    "*         ████╗  ██║██║████╗ ████║██╔════╝    ██╔════╝ ██╔══██╗████╗ ████║██╔════╝            *",
    "*         ██╔██╗ ██║██║██╔████╔██║███████╗    ██║  ███╗███████║██╔████╔██║█████╗              *",
    "*         ██║╚██╗██║██║██║╚██╔╝██║╚════██║    ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝              *",
    "*         ██║ ╚████║██║██║ ╚═╝ ██║███████║    ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗            *",
    "*         ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝            *",
    "***********************************************************************************************",
    "*   Instructions:                                                                             *",
    "*   1. Cards are laid out in rows                                                             *",
    "*   2. Each player take turns taking cards                                                    *",
    "*   3. Players can take any number of cards in any row but only from one row at a time        *",
    "*   4. The player who takes the last card loses the game                                      *",
    "*   5. To take cards, type NR where N is the number of cards and R is the row letter.         *",
    "*   6. For example the command '3B' will take 3 cards from row B                              *",
    "***********************************************************************************************"
]

socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    socket_server.connect((IP, PORT))
except:
    print("Cannot connect to the server. Please try again.")
    sys.exit()

print_welcome(welcome_text)

while True:
    command = input("Enter 's' to start or 'q' to quit: ")
    if (command == 's' or command == 'q'):
        break

if command == 'q':
    sys.exit()

game = []
your_turn = True
opponent_move = False
game_ended = False
game_won = False

while True:
    game = update_game(socket_server)
    print_game(game)
    if opponent_move:
        print(f"Opponent's last move: {opponent_move}")
        opponent_move = False
    game_ended = all(x == 0 for x in game)
    if game_ended:
        break

    if your_turn:
        while True:
            command = input("Take cards <NoOfCards><RowLetter> or 'q' to quit: ")
            if valid_move(command, game) or command == 'q':
                break

        if (command == 'q'):
            print("You disconnected from the server.")
            sys.exit()
        send_to_server(socket_server, command)
        game_won = False
    else:
        print("Waiting for your opponent to take cards...")
        opponent_move = get_server_move(socket_server)
        game_won = True
    
    your_turn = not your_turn


if game_won:
    print("Congratulations! You won the game!")
else:
    print("Sorry you lose. :(")

socket_server.close()
