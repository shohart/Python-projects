# Black Jack Game

Welcome to this Black Jack game! This game is a student project written in Python for an online course on Udemy.com. This game utilizes classes and functions to create a full-fledged Black Jack game.

![Cards](https://samsfun.ru/assets/images/content/Blackjack/en/black-jack-strategien.jpg)

- [Black Jack Game](#black-jack-game)
  - [1. Features](#1-features)
  - [2. Classes](#2-classes)
    - [2.1. Card](#21-card)
      - [2.1.1.Parameters](#211parameters)
      - [2.1.2. Attributes](#212-attributes)
      - [2.1.3. Methods](#213-methods)
    - [2.2. Deck](#22-deck)
    - [2.3. Hand](#23-hand)
      - [2.3.1. Attributes](#231-attributes)
      - [2.3.2. Methods](#232-methods)
    - [2.4. Chips](#24-chips)
      - [2.4.1. Initialization](#241-initialization)
      - [2.4.2. Methods](#242-methods)
    - [2.5. Player](#25-player)
      - [2.5.1. Initialization](#251-initialization)
    - [2.6. Methods](#26-methods)
    - [2.7. Dealer](#27-dealer)
      - [2.7.1. Attributes](#271-attributes)
      - [2.7.2. Initialization](#272-initialization)
      - [2.7.3. Methods](#273-methods)
  - [3. Functions](#3-functions)
    - [3.1.continue\_game()](#31continue_game)
    - [3.2. proceed()](#32-proceed)
    - [3.3. print\_hands(dl, pl)](#33-print_handsdl-pl)
    - [3.4. game\_over(pl)](#34-game_overpl)
    - [3.5. statement(pl\_name)](#35-statementpl_name)
    - [3.6. log\_score()](#36-log_score)
  - [4. Main Game Logic](#4-main-game-logic)
  - [5. Installation](#5-installation)
  - [6. Project Structure](#6-project-structure)
  - [7. Libraries](#7-libraries)

## 1. Features

- Draws graphical representation of cards in the console
- Logs bet, win and deposit chips history to a file 'scores.txt'
- Logs overall scores to a filename '{playername}\_statement.txt'

## 2. Classes

### 2.1. Card

This class represents a playing card.

#### 2.1.1.Parameters

_suit (str):_ The suit of the card (e.g. "Hearts" or "Spades")

_rank (str):_ The rank of the card (e.g. "Ace" or "King")

#### 2.1.2. Attributes

_suit (str):_ The suit of the card (e.g. "Hearts" or "Spades")

_rank (str):_ The rank of the card (e.g. "Ace" or "King")

_value (int):_ The numerical value of the card

#### 2.1.3. Methods

_init():_ Initializes the playing card object

_str():_ Returns the string representation of the card

### 2.2. Deck

This class creates a Deck object from Card objects, which has two methods: _shuffle()_,
which shuffles the deck and _deal_one()_, which deals one card from the deck. The Deck object is initialized with a list of all the cards.

**init**
Initializes the Deck object with a list of all the cards.

**shuffle()**
Shuffles a deck.

**deal_one()**
Deals one card from the Deck.

### 2.3. Hand

The Hand class is used to represent a hand of cards in a card game. Each instance of the class contains a list of individual cards held in the hand and a numerical value of the hand.

#### 2.3.1. Attributes

- _cards(list):_ A list of individual cards held in the hand.

- _value(int):_ The numerical value of the hand.

#### 2.3.2. Methods

- _add()_ The add method is used to add a card to the hand.

  **Arguments:** _card:_ Card to be added.

- _check()_ The check method is used to count the total value of cards in the hand, according to black jack rules.

- _reset()_ The reset method is used to reset the hand back to an empty list and a value of 0.

- _str()_ This method is used to return a string representation of the hand, including the number of cards and the score.

### 2.4. Chips

The Chips class is used for managing chips for a player. It contains methods for adding funds to a player's bank, placing a bet, and representing the object as a string with the player's balance.

#### 2.4.1. Initialization

The init method is used to initialize a Chips object. It takes one parameter, _player_, which is the name of the player. It also sets up the initial values of the player's bank, history, deposit, won, and player's name.

#### 2.4.2. Methods

- _add_funds_ The _add_funds_
  method is used to add funds to the player's bank. It takes no parameters and returns nothing. It prompts the user to enter the amount they want to add, then adds it to the bank. It also updates the history and prints a confirmation message.
- _bet_ The _bet_ method is used to
  place a bet with the player's funds. It takes no parameters and returns the amount of the bet. It prompts the user to enter the amount they want to bet, then checks if the amount is valid. If it is valid, it deducts it from the bank and updates the history. It then prints a confirmation message and returns the amount of the bet.

- _str_ The _str_ method is used to
  represent the **Chips** object as a string with the player's balance. It takes no parameters and returns a string.

### 2.5. Player

This class represents a player in the game. It holds information about the player's name, hand, chips, rounds won and box score.

#### 2.5.1. Initialization

At this piont class initializes the player's name, hand, chips, rounds won and box score. It also sets
_self.name_ to an inputted name.

### 2.6. Methods

- _hit_ This method gets the player's decision to either stand or hit. It takes no arguments and returns
  _True_
  if the player chooses to hit, or
  _False_
  if the player chooses to stand.

- _reset_ This method resets the player's box score and hand. It takes no arguments and returns nothing.

- _str_ This method returns a string representation of the player's name, number of cards in the hand and bank balance. It takes no arguments.

### 2.7. Dealer

The Dealer class is responsible for representing a blackjack dealer. It has three attributes and three methods.

#### 2.7.1. Attributes

- _hand_:
  The dealer's current hand.
- _shoe_:
  The shoe from which the dealer draws
  cards.
- _shoe_left_:
  The number of cards left in the shoe.

#### 2.7.2. Initialization

At this point class initializes
_hand_
and
_shoe_
attributes, as well as setting the
_shoe_left_
attribute to the number of cards in the _shoe_.

#### 2.7.3. Methods

- _deal_one()_
  The
  deal_one()
  method is responsible for drawing one card from the shoe. It decrements the
  shoe_left
  attribute and returns the card from the shoe.

- _reset()_
  The
  reset()
  method is responsible for resetting the dealer's hand. It calls the
  reset()
  method of the
  Hand
  class.

- _str()_
  The
  str()
  method is responsible for returning a string representation of the dealer. It returns a string containing the number of cards in the shoe.

## 3. Functions

### 3.1.continue_game()

This function takes no parameters asks the user if they would like to continue playing the game.

- **Returns** a boolean. It will return
  _True_
  if the user answered
  _Yes_
  , and
  _False_
  if the user answered
  _No_
  .

### 3.2. proceed()

This function asks the players to start the game.

- **Returns**
  a boolean
  : _True_ if the players decide to start the game, _False_ if not.

- **Usage**
  The function takes no parameters and returns a boolean value. It displays a message asking the players to start the game. The players have to enter either "Yes" or "No" (or their abbreviations "Y" or "N") as an input. If the entered value is not valid, the function will display an error message stating that the value is not valid.

### 3.3. print_hands(dl, pl)

This function prints the current hands of the dealer and player.

- **Parameters**
  _dl_
  _(Dealer)_: The dealer object
  _pl_
  _(Player):_ The player object
  Example Usage
  python
  print_hands(dl, pl)

- **Output**
  of the function is a visual representation of the hands of the dealer and the player. The dealer's hand is printed first, followed by the player's hand. If the player but a bet in a box, the bet value is printed first before the hand.

### 3.4. game_over(pl)

This function prints the game over screen with the final scores. Parameter _pl_ points to a player.

### 3.5. statement(pl_name)

This function is used to write the players' statements to a
_{pl_name}\_statement.txt_
file.

- **Parameters**
  _pl_name_
  : str - name of the player

- **Returns**
  None

**Code Explanation:**
The function starts by setting the **filename** to
_{pl_name.name}\_statement.txt_
and setting the current date and time to
_now_
.

The
**if**
statement checks if the file exists and sets the mode of writing to
**append**
or
**write**
accordingly.

The
**with**
statement opens the file in the mode set by the
**if**
statement and iterates through the
_pl_name.chips.history_
list. For each item in the list, it adds the current date and time and the history item to the file as a line.

Finally, the file is closed.

### 3.6. log_score()

This function writes a game score to the _scores.txt_ file.

- **Parameters**
  _name_
  (str): The name of the player
- **Returns**
  None

## 4. Main Game Logic

The goal of the game is to beat the dealer's hand without going over 21. In the game, face cards (Kings, Queens, and Jacks) are all worth 10 and Aces can be worth 1 or 11:

![BlackJack rules](https://rb.gy/7out8p)

The game initiates by displaying the intro screen, which includes the game rules. After that, the program will reset any previous game settings, create class instances and ask the user to make an initial bet.

Then, the program will deal two cards to the player and one card to the dealer. It will also check the hand values and display them.

After that, the program will enter the main game loop. In this loop, the program will ask the player if they want to hit and deal another card to the player. If the player's hand value is less than 21, they can continue to hit until they either go over 21 or decide to stay.

When the player's turn is over, the program will enter the dealer's turn. In this turn, the dealer will hit until their hand value is greater than or equal to 17.

Once the hand values are finalized, the program will check who won the game and add or subtract the bet amount from the player's bank.

Finally, the program will ask the player if they want to play again. If their bank is empty, they will be asked to add funds.

## 5. Installation

```Git
git clone --no-checkout https://github.com/shohart/ shohart
cd shohart
git sparse-checkout init --cone
git sparse-checkout set UDEMY-python-projects/project_4_black_jack
python setup.py py2exe
```

## 6. Project Structure

Project contains 4 files:

- [black_jack.ipynb](./black_jack.ipynb) - Jupiter notebook with development stages and steps.
- [black_jack.py](./black_jack.py) - a python script, containing main code of the project.
- [requirements.txt](./requirements.txt) - a list of python modules and versions.
- [README.md](./README.md) - this file.

## 7. Libraries

- random
- time
- os
- datetime
- art
- py2exe
