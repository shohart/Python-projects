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


# Defining functions


def game_board(board):
    # Drawing a game board
    print()
    print(board)


def user_pic():
    # Pick a side X or O

    player1 = '_'
    player2 = '_'

    while player1 not in 'XO':
        player1 = input('Player 1! Pick a side! X or O? ').upper()
        if player1 not in 'XO':
            print('\n'*100)
            print('Sorry, you need to enter X or O!')

    if player1 == 'X':
        player2 = 'O'
    else:
        player2 = 'X'

    return player1, player2


def user_choice():
    # Defining user position choice

    choice = 'WRONG'

    while not choice.isdigit() or \
        int(choice) not in range(1, 10) or \
            pos[int(choice)] != ' ':

        choice = input('Select a position index (1-9): ')

        if not choice.isdigit():
            print("Sorry that is not a digit! Please enter 1-9!")

        elif int(choice) not in range(1, 10):
            print('Sorry that is not a correct position value! '
                  'Please enter 1-9!')
        elif pos[int(choice)] != ' ':
            print('Sorry this spot was already taken!')

    return int(choice)


def continue_game():
    # Define game continue or not

    go_game = 'empty value'

    while go_game.capitalize() not in ['Yes', 'No']:

        go_game = input('Continue? Enter Yes or No: ')

        if go_game.capitalize() not in ['Yes', 'No']:
            print('\n'*100)
            print("Sorry, I didn't understand.\n"
                  "Please make sure to enter Yes or No.")

    if go_game.capitalize() == "Yes":
        # Game is still on
        return True

    else:
        # Game is over
        return False


def board_replace(dictionary, position):
    # Making changes in the board according to a choice

    if turn % 2 != 0:
        dictionary[position] = player1

    else:
        dictionary[position] = player2

    return dictionary


def check_win():
    # Checking rows for winner

    if pos[7] == pos[8] == pos[9] == player1 or \
       pos[4] == pos[5] == pos[6] == player1 or \
       pos[1] == pos[2] == pos[3] == player1 or \
                                     \
       pos[1] == pos[4] == pos[7] == player1 or \
       pos[2] == pos[5] == pos[8] == player1 or \
       pos[3] == pos[6] == pos[9] == player1 or \
                                     \
       pos[7] == pos[5] == pos[3] == player1 or \
       pos[1] == pos[5] == pos[9] == player1:

        return 'Player 1'

    elif pos[7] == pos[8] == pos[9] == player2 or \
            pos[4] == pos[5] == pos[6] == player2 or \
            pos[1] == pos[2] == pos[3] == player2 or \
                                         \
            pos[1] == pos[4] == pos[7] == player2 or \
            pos[2] == pos[5] == pos[8] == player2 or \
            pos[3] == pos[6] == pos[9] == player2 or \
                                         \
            pos[7] == pos[5] == pos[3] == player2 or \
            pos[1] == pos[5] == pos[9] == player2:

        return 'Player 2'

    else:

        return 'nobody'


def choose_first():
    # Choose who goes first on a game
    return random.randint(1, 2)


def reset_board():
    # Set all the values to default

    win = 'nobody'

    pos = [
        'not_used',
        ' ', ' ', ' ',
        ' ', ' ', ' ',
        ' ', ' ', ' '
    ]

    board = (

        f'  {pos[7]} | {pos[8]} | {pos[9]} \n '
        '---|---|---\n'
        f'  {pos[4]} | {pos[5]} | {pos[6]} \n '
        '---|---|---\n'
        f'  {pos[1]} | {pos[2]} | {pos[3]} \n'

    )

    turn = choose_first()

    return win, pos, board, turn


def board_full_check():
    # Check if the board is full or not
    return ' ' not in pos


def proceed():
    # Define actual start of the game

    go_game = 'empty value'

    while go_game.capitalize() not in ['Yes', 'No']:

        go_game = input('Start the game? Enter Yes or No: ')

        if go_game.capitalize() not in ['Yes', 'No']:
            print("Sorry, I didn't understand.\n"
                  "Please make sure to enter Yes or No.")

    if go_game.capitalize() == "Yes":
        # Game is still on
        return True

    else:
        # Game is over
        return False


def game_over():
    print('\n'*100)
    print("| {0:=^19} |".format(' GAME OVER '))
    print("| {0:^19} |".format(' '))
    print("| {0:-^19} |".format(' Score: '))
    print("| {0:^8} | {1:^8} |".format('Player 1', 'Player 2'))
    print("| {0:^8} | {1:^8} |".format(wins_data['Player 1'],
                                       wins_data['Player 2']))
    print('\n')


# Clear any historical output and show the game list
print('\n'*100)

# Defining rows of a board
pos = ['not_used',
       '1', '2', '3',
       '4', '5', '6',
       '7', '8', '9'
       ]

# Defining board itself
board = (

    f'  {pos[7]} | {pos[8]} | {pos[9]} \n '
    '---|---|---\n'
    f'  {pos[4]} | {pos[5]} | {pos[6]} \n '
    '---|---|---\n'
    f'  {pos[1]} | {pos[2]} | {pos[3]} \n'

)


# Setting initial service variables
game_on = True
player1 = 'Empty'
player2 = 'Empty'
win = 'nobody'
board_full = False

# Storing total wins data
wins_data = {'Player 1': 0, 'Player 2': 0}

# Printing Welcome message
print('\n'*100)
print('Welcome to the Tic Tak Toe game! '
      'You pick the spot by index.\n'
      'Here is the board indexes:\n')
print(board)

# Choose a marker for players
player1, player2 = user_pic()

# Clear output
print('\n'*100)

game_start = True

# Main game cycle
while game_on and game_start:

    # Defaulting board values
    win, pos, board, turn = reset_board()
    board_full = board_full_check()
    game_start = True

    # Clear any historical output and show the game list
    print('\n'*100)

    # Printing info
    print(f'Player 1: {player1}')
    print(f'Player 2: {player2}')
    print(f'Player {turn} goes first!\n')

    # Promt to start the game
    game_start = proceed()

    # Turn cycle
    while win == 'nobody' and not board_full:

        # Clear any historical output and show the game list
        print('\n'*100)

        # Draw a board
        game_board(board)

        # Greet a marker
        if turn % 2 != 0:
            print('Turn: Player 1')
        else:
            print('Turn: Player 2')

        # Have player choose position
        position = user_choice()

        # Rewrite that position and update board
        pos = board_replace(pos, position)

        # Update the board
        board = (

            f'  {pos[7]} | {pos[8]} | {pos[9]} \n '
            '---|---|---\n'
            f'  {pos[4]} | {pos[5]} | {pos[6]} \n '
            '---|---|---\n'
            f'  {pos[1]} | {pos[2]} | {pos[3]} \n'

        )

        # Show the updated game board
        game_board(board)

        # Checking winner
        win = check_win()

        # Actions if win accurse
        if win != 'nobody':
            print('\n'*100)
            print(f'{win} won!\n')
            wins_data[win] += 1
            print(board)

        # Checking full board
        board_full = board_full_check()

        # Checking for a full board and no win
        if board_full and win == 'nobody':
            print('\n'*100)
            print('No free spots left on a board! It seems to be a tie!\n')
            print(board)

        # Adding to a turn counter
        turn += 1

    # Ask if you want to keep playing
    game_on = continue_game()

    # Displaying final game scores
    if not game_on:
        game_over()
