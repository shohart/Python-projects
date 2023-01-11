# Tic Tak Toe

This is a simple game of tic tac toe written in Python. The game is played between two players, who take turns marking the spaces in a 3x3 grid. The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row is the winner.

## Game Layout

The game board is made up of nine squares, each identified by a number ranging from 1 to 9. The board is set up as follows:

| 7   | 8   | 9   |
| --- | --- | --- |
| 4   | 5   | 6   |
| 1   | 2   | 3   |

## Gameplay

The game begins with Player 1 selecting which side they will play (X or O). Player 1 will then pick a position on the board they wish to place their mark by entering the corresponding number. This will be followed by Player 2 doing the same. The game will continue until either one of the players has successfully placed three of their marks in a row, or until all of the spots on the board are taken, in which case the game is a tie.

## Functions

The game uses several functions to run.

### game_board

This function is used to draw the game board.

### user_pic

This function is used to have the players select which side they wish to play. The function will prompt the player to enter either an X or O.

### user_choice

This function is used to have the players pick a position on the board. The function will prompt the player to enter a number from 1 to 9.

### continue_game

This function is used to ask the players if they wish to continue playing. The function will prompt the player to enter either Yes or No.

### board_replace

This function is used to replace the board with the player's mark.

### check_win

This function is used to check if either player has won the game.
