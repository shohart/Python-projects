"""_summary_

Returns:
    _type_: _description_
"""
import random

# Defining cards
suits = ("♠", "♥", "♦", "♣")
ranks = (
    '2', '3', '4', '5', '6',
    '7', '8', '9', '10', 'J',
    'Q', 'K', 'A'
)
values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10,
    'Q': 10, 'K': 10, 'A': [10, 1]
}


class Card():
    """
    This class represents a playing card.

    Args:
    suit (str): The suit of the card (e.g. "Hearts" or "Spades")
    rank (str): The rank of the card (e.g. "Ace" or "King")

    Attributes:
    suit (str): The suit of the card (e.g. "Hearts" or "Spades")
    rank (str): The rank of the card (e.g. "Ace" or "King")
    value (int): The numerical value of the card

    Methods:
    init(): Initializes the playing card object
    str(): Returns the string representation of the card
    """

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]
        self.pic = [
            '┌───────┐',
            f'│ {self.rank}     │',
            f'│   {self.suit}   │',
            f'│     {self.rank} │',
            '└───────┘'
        ]

    def __str__(self):
        return "\n".join(x for x in self.pic)


class Deck():
    """
    This class creates a Deck object which has two methods:
    shuffle() which shuffles the deck and deal_one() which deals one card
    from the deck.
    The Deck object is initialized with a list of all the cards.
    """

    def __init__(self):
        self.all_cards = []

        for suit in suits:

            for rank in ranks:
                created_card = Card(suit, rank)
                self.all_cards.append(created_card)

    def shuffle(self):
        random.shuffle(self.all_cards)
        print('Deck has been shuffled!')

    def deal_one(self):
        return self.all_cards.pop()


class Player():
    """
    This class represents a Player in a game.

    It has the following attributes:

    name: The name of the player
    all_cards: A list of all the cards in the player's hand
    It has the following methods:

    remove_one(): Removes and returns the first card in the player's hand
    add_cards(): Takes a new card or list of cards and adds them to the
    player's hand
    shuffle(): Shuffles the player's cards
    str(): Returns a string representation of the player and the number
    of cards in their hand
    """

    def __init__(self, name, bank=100):
        self.name = name
        self.bank = bank
        self.hand = []

    def hit(self):

        move = '_'

        while move not in ['pass', 'hit', 'h', 'p']:
            move = input('Hit or Pass?').lower()

            if move not in ['pass', 'hit', 'h', 'p']:
                print('\n'*100)
                print('Sorry, you need to enter "Hit" or "Pass"!')
                continue

        return bool(move in ['hit', 'h'])

    def add_funds(self, amount):

        amount = '_'

        while not amount.isdigit():
            amount = input('How much do you want to add?')

            if not amount.isdigit():
                print("Sorry that is not a digit! Please enter a valid digit!")
                continue

        self.bank += int(amount)
        print(f'{amount} just added to your bank.\nYour bank: {self.bank}')

    def bet(self, amount):

        amount = '_'

        while not amount.isdigit() and amount > self.bank:
            amount = input('Place a bet! Enter the ammount: ')

            if not amount.isdigit():
                print("Sorry that is not a digit! Please enter a valid digit!")
                continue

            if amount > self.bank:
                print('Oops! You do not have so much money! Please reduce a bet!')
                continue

        self.bank -= int(amount)

        return int(amount)

    def add_cards(self, new_cards):
        self.hand.append(new_cards)

    def __str__(self):
        return f'Player {self.name} has {len(self.hand)} cards. \
                 Players balance: {self.bank}'


class Dealer():

    def __init__(self, shoe):
        self.hand = []
        self.shoe = shoe

    def deal_one(self):
        return self.shoe.pop(0)

    def add_cards(self, new_cards):
        self.hand.append(new_cards)

    def shuffle(self):
        random.shuffle(self.shoe)

    def __str__(self):
        return f'There are {len(self.shoe)} cards in the shoe.'
