"""
A little project in base python.
A tic-tak-toe game. Written using functions and cycles.
Tic-tac-toe, also known as noughts and crosses or Xs and Os,
is a game for two players (X and O) who take turns
marking the spaces in a 3×3 grid.
The player who succeeds in placing three of their marks
in a horizontal, vertical, or diagonal row is the winner.

"""
# Import libraries
import random
import os
import datetime as dt
import art


# Defining functions


def game_board(board_list):
    """Draws a game board based on a list of lists"""
    print()
    print(board_list)


def board_update(board_list):
    """
    Updates game board to print, using game list values

    Args:
        board_list (list): A list, containing board info

    Returns:
        str: Updated board representation to print
    """
    result = (
        f"  {board_list[7]} | {board_list[8]} | {board_list[9]} \n "
        "---|---|---\n"
        f"  {board_list[4]} | {board_list[5]} | {board_list[6]} \n "
        "---|---|---\n"
        f"  {board_list[1]} | {board_list[2]} | {board_list[3]} \n"
    )
    return result


def user_pic():
    """This function prompts the user to select either an 'X' or an 'O'
    and returns the choice as a tuple with the player 1's choice first and
    player 2's choice second.
    """

    # Pick a side X or O
    p_1 = "_"
    p_2 = "_"

    while p_1 not in "XO":
        p_1 = input("Player 1! Pick a side! X or O? ").upper()
        if p_1 not in "XO":
            print("\n" * 100)
            print("Sorry, you need to enter X or O!")

    if p_1 == "X":
        p_2 = "O"
    else:
        p_2 = "X"

    return p_1, p_2


def user_choice():
    """Define the users choice for a position

    This function takes in a user's input and checks whether it is a digit
    from 1 to 9 and if the position is empty. If not, it will prompt the user
    to enter a valid position.

    Args:
        None

    Return:
        int: the position index selected by the user
    """

    choice = "_"

    while (
        not choice.isdigit()
        or int(choice) not in range(1, 10)
        or pos[int(choice)] != " "
    ):

        choice = input("Select a position index (1-9): ")

        if not choice.isdigit():
            print("Sorry that is not a digit! Please enter 1-9!")

        elif int(choice) not in range(1, 10):
            print("Sorry that is not a correct position value! " "Please enter 1-9!")
        elif pos[int(choice)] != " ":
            print("Sorry this spot was already taken!")

    return int(choice)


def continue_game():
    """
    Function to ask the user if they would like to continue playing the game

    Returns
    -------
    bool
        True if the user answered yes, False if the user answered no
    """
    go_game = "_"

    try:

        while go_game.capitalize()[0] not in ["Y", "N"]:
            go_game = input("Continue? Enter Yes or No: ")

            if go_game.capitalize()[0] not in ["Y", "N"]:
                print("\n" * 100)
                print(
                    "Sorry, I didn't understand.\n"
                    "Please make sure to enter Yes or No."
                )
    except IndexError:

        go_game = "N"

    return bool(go_game.capitalize()[0] == "Y")


def board_replace(dictionary, place):
    """Makes changes in the board according to a choice

    Args:
        dictionary (dict): A dictionary representing a board state
        place (int): An index in the dictionary to change

    Returns:
        dict: The updated board state
    """
    if turn % 2 != 0:
        dictionary[place] = player1

    else:
        dictionary[place] = player2

    return dictionary


def check_win():
    """
    This function checks for a winner in the game by checking all
    the possible winning combinations of the tic-tac-toe board.
    It returns either 'Player 1', 'Player 2' or 'nobody'
    depending on the outcome of the board.
    """

    if (
        pos[7] == pos[8] == pos[9] == player1
        or pos[4] == pos[5] == pos[6] == player1
        or pos[1] == pos[2] == pos[3] == player1
        or pos[1] == pos[4] == pos[7] == player1
        or pos[2] == pos[5] == pos[8] == player1
        or pos[3] == pos[6] == pos[9] == player1
        or pos[7] == pos[5] == pos[3] == player1
        or pos[1] == pos[5] == pos[9] == player1
    ):

        return "Player 1"

    elif (
        pos[7] == pos[8] == pos[9] == player2
        or pos[4] == pos[5] == pos[6] == player2
        or pos[1] == pos[2] == pos[3] == player2
        or pos[1] == pos[4] == pos[7] == player2
        or pos[2] == pos[5] == pos[8] == player2
        or pos[3] == pos[6] == pos[9] == player2
        or pos[7] == pos[5] == pos[3] == player2
        or pos[1] == pos[5] == pos[9] == player2
    ):

        return "Player 2"

    else:

        return "nobody"


def choose_first():
    """Returns a random integer between 1 and 2 to decide which player
    goes first.

    Parameters:
        None

    Returns:
        int: A random integer between 1 and 2
    """
    return random.randint(1, 2)


def reset_board():
    """Resets the game board and all related values to the default.

    Parameters:
        None

    Returns:
        def_winner: String 'nobody'
        def_board_list: A list of 9 strings representing the board positions
        def_board: String representing a 3x3 board
        def_turn: An integer between 1 and 2
    """
    def_winner = "nobody"

    def_board_list = ["not_used", " ", " ", " ", " ", " ", " ", " ", " ", " "]

    def_board = (
        f"  {def_board_list[7]} | {def_board_list[8]} | {def_board_list[9]} \n "
        "---|---|---\n"
        f"  {def_board_list[4]} | {def_board_list[5]} | {def_board_list[6]} \n "
        "---|---|---\n"
        f"  {def_board_list[1]} | {def_board_list[2]} | {def_board_list[3]} \n"
    )

    def_turn = choose_first()

    return def_winner, def_board_list, def_board, def_turn


def board_full_check():
    """Checks if the board is full or not.

    Parameters:
        None

    Returns:
        boolean: True if no empty space is found, False if empty space
        is found.
    """
    return " " not in pos


def proceed():
    """Asks the players to start the game.

    Parameters:
        None

    Returns:
        boolean: True if the players decide to start the game, False if not.
    """
    go_game = "_"

    try:

        while go_game.capitalize()[0] not in ["Y", "N"]:

            go_game = input("Start the game? Enter Yes or No: ")

            if go_game.capitalize()[0] not in ["Y", "N"]:
                print(
                    "Sorry, I didn't understand.\n"
                    "Please make sure to enter Yes or No."
                )
    except IndexError:
        go_game = "Y"

    return bool(go_game.capitalize()[0] == "Y")


def game_over():
    """Prints the game over screen with the final scores.

    Parameters:
        None

    Returns:
        None
    """
    print("\n" * 100)
    print("| {0:=^19} |".format(" GAME OVER "))
    print("| {0:^19} |".format(" "))
    print("| {0:-^19} |".format(" Score: "))
    print("| {0:^8} | {1:^8} |".format(names_data["Player 1"], names_data["Player 2"]))
    print("| {0:^8} | {1:^8} |".format(wins_data["Player 1"], wins_data["Player 2"]))
    print("\n")


def log_score(name, score):
    """
    Writes a game score to the scores.txt file.

    Parameters
    ----------
    name : str
        The name of the player
    score : int
        The score of the player

    Returns
    -------
    None
    """
    filename = "scores.txt"

    if os.path.exists(filename):
        append_write = "a"  # append if already exists
        start_line = ""
    else:
        append_write = "w"  # make a new file if not
        start_line = "date,name,score\n"

    with open(filename, append_write, encoding="utf8") as score_file:
        score_file.write(start_line)
        score_file.write(str(dt.date.today()) + "," + name + "," + str(score) + "\n")


def set_names():
    """Ask players for their names and returns them as a tuple

    Args:
        None

    Returns:
        Tuple containing player names
    """

    name1 = input("Player 1 enter your name: ")
    name2 = input("Player 2 enter your name: ")
    if name1 == '':
        name1 = 'Player 1'
    if name2 == '':
        name2 = 'Player 2'

    return name1, name2


# Defining rows of a board for start screen
pos = ["not_used", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# Defining board itself
board = board_update(pos)

# Storing total wins data
wins_data = {"Player 1": 0, "Player 2": 0}

# Storing player names
names_data = {"Player 1": "Unknown", "Player 2": "Unknown"}

# Printing Welcome message
print("\n" * 100)
art.tprint("Tic Tak Toe", "tarty4")
print(
    "\n"
    "Welcome to the Tic Tak Toe game!\n"
    "You pick the spot by index.\n"
    "Here is the board indexes:\n"
)
print(board)

# Ask for player names
names_data["Player 1"], names_data["Player 2"] = set_names()

# Choose a marker for players
player1, player2 = user_pic()

# Main game cycle
while True:
    # Defaulting board values
    win, pos, board, turn = reset_board()

    # Clear output
    print("\n" * 100)

    # Display the board
    game_board(board)

    # Print info
    print(f"Player 1 = {names_data['Player 1']} = {player1}")
    print(f"Player 2 = {names_data['Player 2']} = {player2}")
    print(f"Player {turn} goes first!\n")

    # Promt to start the game
    game_start = proceed()
    if not game_start:
        break

    # Turn cycle
    # while win == "nobody" and not board_full:
    while True:

        # Clear any historical output and show the game list
        print("\n" * 100)

        # Draw a board
        game_board(board)

        # Greet a marker
        if turn % 2 != 0:
            print(f"Turn: {names_data['Player 1']}")
        else:
            print(f"Turn: {names_data['Player 2']}")

        # Have player choose position
        position = user_choice()

        # Rewrite that position and update board
        pos = board_replace(pos, position)

        # Update the board
        board = board_update(pos)

        # Checking winner
        win = check_win()

        # Actions if win accurse
        if win != "nobody":
            print("\n" * 100)
            art.aprint("basking in glory")
            print("\n")
            print(f"{names_data[win]} won!\n")
            wins_data[win] += 1
            print(board)
            break

        # Checking full board
        board_full = board_full_check()

        # Checking for a full board and no win
        if board_full and win == "nobody":
            print("\n" * 100)
            art.aprint("shrug")
            print("\n")
            print("No free spots left on a board! It seems to be a tie!\n")
            print(board)
            break

        # Adding to a turn counter
        turn += 1

    # Ask if you want to keep playing
    game_on = continue_game()

    # Displaying final game scores
    if not game_on:
        game_over()
        log_score(names_data["Player 1"], wins_data["Player 1"])
        log_score(names_data["Player 2"], wins_data["Player 2"])
        break
