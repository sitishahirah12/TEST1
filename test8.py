import socket
import select
import sys
import os
import pickle
import time


def clear_scr():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome():
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


def new_game():
    return [6, 4, 7, 4, 1, 5]


def print_game(game):
    clear_scr()
    letters = ["A: ", "B: ", "C: ", "D: ", "E: ", "F: ", "G: ", "H: ", "I: ", "J: "]

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


def send_game_status(socket_client, game):
    game_status = pickle.dumps(game)
    game_status = bytes(f"{len(game_status):<{HEADER_LENGTH}}", "utf-8") + game_status
    socket_client.send(game_status)


def send_to_client(socket_client, my_command):
    my_command = f"{len(my_command):<{HEADER_LENGTH}}".encode("utf-8") + my_command.encode("utf-8")
    try:
        socket_client.send(my_command)
    except:
        print("Client disconnected")
        socket_client.close()
        sys.exit(1)

        
def get_client_move(socket_client):
    header = socket_client.recv(HEADER_LENGTH)
    if not header:
        print("Client disconnected")
        socket_client.close()
        sys.exit(1)
    opponent_move_length = int(header.decode("utf-8"))
    return socket_client.recv(opponent_move_length).decode("utf-8")


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

 
def change_status(game, command):
    row = int(ord(command[1].lower()) - ord('a'))
    game[row] -= int(command[0])
    return game

HEADER_LENGTH = 10
IP = "192.168.56.110"
PORT = 8888

socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_server.bind((IP, PORT))
socket_server.listen(1)
clear_scr()

welcome_text = [
    "**********************************************************************************************",
    "*    ██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗    ████████╗ ██████╗     *",
    "*    ██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝    ╚══██╔══╝██╔═══██╗    *",
    "*    ██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗         ██║   ██║   ██║    *",
    "*    ██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝         ██║   ██║   ██║    *",
    "*    ╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗       ██║   ╚██████╔╝    *",
    "*     ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝       ╚═╝    ╚═════╝     *",
    "*                                                                                            *",
    "*         ███╗   ██╗██╗███╗   ███╗███████╗     ██████╗  █████╗ ███╗   ███╗███████╗           *",
    "*         ████╗  ██║██║████╗ ████║██╔════╝    ██╔════╝ ██╔══██╗████╗ ████║██╔════╝           *",
    "*         ██╔██╗ ██║██║██╔████╔██║███████╗    ██║  ███╗███████║██╔████╔██║█████╗             *",
    "*         ██║╚██╗██║██║██║╚██╔╝██║╚════██║    ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝             *",
    "*         ██║ ╚████║██║██║ ╚═╝ ██║███████║    ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗           *",
    "*         ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝           *",
    "**********************************************************************************************",
    "*   Instructions:                                                                            *",
    "*   1. Cards are laid out in rows                                                            *",
    "*   2. Each player take turns taking cards                                                   *",
    "*   3. Players can take any number of cards in any row but only from one row at a time       *",
    "*   4. The player who takes the last card loses the game                                     *",
    "*   5. To take cards, type NR where N is the number of cards and R is the row letter.        *",
    "*   6. For example the command '3B' will take 3 cards from row B                             *",
    "**********************************************************************************************"
]

print("Waiting for opponent...")
socket_client, client_address = socket_server.accept()

print_welcome()

while True:
    command = input("Enter 's' to start or 'q' to quit: ")
    if (command == 's' or command == 'q'):
        break

if command == 'q':
    sys.exit()


game = new_game()
your_turn = False
opponent_move = False
game_won = False
game_ended = False

while not game_ended:

    print_game(game)
    if opponent_move:
        print(f"Opponent's last move: {opponent_move}")
        opponent_move = False

    try:
        send_game_status(socket_client, game)
    except:
        print("Client disconnected")
        socket_client.close()

        sys.exit(1)
 
    if your_turn:

        while True:
            command = input("Take cards <NoOfCards><RowLetter> or 'q' to quit: ")
            if valid_move(command, game) or command == 'q':
                break

        if (command == 'q'):
            print("You disconnected.")
            sys.exit()
        
        game = change_status(game, command)
        send_to_client(socket_client, command)
        game_ended = all(x == 0 for x in game)
        game_won = False
    else:
        print("Waiting for your opponent to take cards...")
        opponent_move = get_client_move(socket_client)
        game = change_status(game, opponent_move)
        game_ended = all(x == 0 for x in game)
        game_won = True

    
    your_turn = not your_turn

try:
    send_game_status(socket_client, game)
except:
    print("Client disconnected")
    socket_client.close()
    sys.exit(1)

if game_won:
    print_game(game)
    print(f"Opponent's last move: {opponent_move}")
    print("Congratulations! You won the game!")
else:
    print("Sorry you lose. :(")

socket_client.close()
