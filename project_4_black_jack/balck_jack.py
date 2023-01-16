import random

# Defining cards
suits = ("♠", "♥", "♦", "♣")
ranks = (" 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9", "10", " J", " Q", " K", " A")
values = {
    " 2": 2,
    " 3": 3,
    " 4": 4,
    " 5": 5,
    " 6": 6,
    " 7": 7,
    " 8": 8,
    " 9": 9,
    "10": 10,
    " J": 10,
    " Q": 10,
    " K": 10,
    " A": [11, 1],
}


def continue_game():
    # Define game continue or not

    go_game = "empty value"

    while go_game.capitalize() not in ["Yes", "No", "Y", "N"]:

        go_game = input("Continue? Enter Yes or No: ")

        if go_game.capitalize() not in ["Yes", "No", "Y", "N"]:
            print("\n" * 100)
            print(
                "Sorry, I didn't understand.\n" "Please make sure to enter Yes or No."
            )

    return bool(go_game.capitalize() in ["Yes", "Y"])


def proceed():
    """Asks the players to start the game.

    Parameters:
        None

    Returns:
        boolean: True if the players decide to start the game, False if not.
    """
    go_game = "empty value"

    while go_game.capitalize() not in ["Yes", "No", "Y", "N"]:

        go_game = input("Start the game? Enter Yes or No: ")

        if go_game.capitalize() not in ["Yes", "No", "Y", "N"]:
            print(
                "Sorry, I didn't understand.\n" "Please make sure to enter Yes or No."
            )

    return bool(go_game.capitalize() in ["Yes", "Y"])


class Card:
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
            "┌───────┐",
            f"│{self.rank}     │",
            f"│   {self.suit}   │",
            f"│    {self.rank} │",
            "└───────┘",
        ]

    def __str__(self):
        return "\n".join(x for x in self.pic)


class Deck:
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
        print("Deck has been shuffled!")

    def deal_one(self):
        return self.all_cards.pop()


class Player:
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

    def __init__(self):
        self.name = input("Enter your name: ")
        self.bank = 0
        self.hand = []
        self.history = []
        self.hand_value = 0

    def hit(self):

        move = "_"

        while move not in ["stand", "hit", "h", "s"]:
            move = input("Stand or Hit?").lower()

            if move not in ["stand", "hit", "h", "s"]:
                print("\n" * 100)
                print('Sorry, you need to enter "Hit" or "Pass"!')
                continue

        return bool(move in ["hit", "h"])

    def add_funds(self):

        amount = "_"

        while not amount.isdigit():
            amount = input("How much do you want to add?")

            if not amount.isdigit():
                print("Sorry that is not a digit! Please enter a valid digit!")
                continue

        self.bank += int(amount)
        self.history.append(f"{self.name},ADD,{amount},deposit")
        print(f"{amount} just added to your bank.\nYour bank: {self.bank}")

    def bet(self):

        amount = "_"

        while True:
            amount = input("Place a bet! Enter the ammount: ")

            if not amount.isdigit() or amount == "0":
                print("Sorry that is not a valid bet!")
                continue

            elif int(amount) > self.bank:
                print("Oops! You do not have so much money! Please reduce a bet!")
                continue

            else:
                self.bank -= int(amount)
                self.history.append(f"{self.name},REMOVE,{amount},bet")
                print(
                    f"A bet of {amount} was successfully placed.",
                    f"Your bank: {self.bank}",
                )
                break

        return int(amount)

    def add_cards(self, new_cards):
        self.hand.append(new_cards)

    def check_hand(self):
        aces = []
        rest = []

        for card in self.hand:
            if card.rank == " A":
                aces.append(card.value)
            else:
                rest.append(card.value)

        total = sum(rest)
        for ace in aces:
            if total <= 10:
                total += ace[0]
            else:
                total += ace[1]

        self.hand_value = total

    def __str__(self):
        return (
            f"Player {self.name} has {len(self.hand)} cards."
            + f"Player's balance: {self.bank}"
        )


class Dealer:
    def __init__(self, shoe):
        self.hand = []
        self.shoe = shoe
        self.box = 0
        self.hand_value = 0

    def deal_one(self):
        return self.shoe.all_cards.pop(0)

    def add_cards(self, new_cards):
        self.hand.append(new_cards)

    def shuffle(self):
        random.shuffle(self.shoe.all_cards)
        print("Deck has been shuffled by Dealer!")

    def check_hand(self):
        aces = []
        rest = []

        for card in self.hand:
            if card.rank == " A":
                aces.append(card.value)
            else:
                rest.append(card.value)

        total = sum(rest)
        for ace in aces:
            if total <= 10:
                total += ace[0]
            else:
                total += ace[1]

        self.hand_value = total

    def reset(self):
        self.hand = []
        self.box = 0
        self.hand_value = 0

    def __str__(self):
        return f"There are {len(self.shoe)} cards in the shoe."


# Static intro:

# Display intro screen
# print('\n'*100)
print(
    "Welcome to the BlackJack game! "
    "You need to get to 21 points in your hand.\n"
    "But not more! Ace could be either 11 or 1 in your favor!\n"
)

# Initiate class instances
game_deck = Deck()

dealer = Dealer(game_deck)
player = Player()
print(f"Hello {player.name}!")

# Initial shuffle the deck
game_deck.shuffle()

if player.bank <= 0:
    print("Your initial bank is empty!")
    player.add_funds()

while True:
    # Start a game
    game_start = True

    while game_start:
        # Start the cycle

        game_start = proceed()

        # shuffle the shoe
        dealer.shuffle()

        # deal cards
        for i in range(2):
            player.add_cards(dealer.deal_one())
            dealer.add_cards(dealer.deal_one())

        # print hands
        print("Dealer:")
        for i in range(5):
            row = " ".join(dealer.hand[n].pic[i] for n in range(len(dealer.hand)))
            print(row)

        print("\n" * 5)

        print("Player:")
        for i in range(5):
            row = " ".join(player.hand[n].pic[i] for n in range(len(player.hand)))
            print(row)

        # ask for a bet
        dealer.box += player.bet()

        # second loop with a hit
        while True:
            # check and compare hands
            player.check_hand()
            dealer.check_hand()

            if player.hand_value > 21:
                print("BUST! Your bet is lost.")
                break
            elif dealer.hand_value > 21:
                player.bank += dealer.box * 1.5
                print(f"Your bet has won! Congratulations! You won {dealer.box * 1.5}")
                break

            # shuffle the deck
            dealer.shuffle()

            # deal cards
            if player.hit():
                player.add_cards(dealer.deal_one())

            dealer.add_cards(dealer.deal_one())

            # print hands
            print("Dealer:")
            for i in range(5):
                row = " ".join(dealer.hand[n].pic[i] for n in range(len(dealer.hand)))
                print(row)

            print("\n" * 2)
            print(f"Current box: {dealer.box}")
            print("\n" * 2)

            print("Player:")
            for i in range(5):
                row = " ".join(player.hand[n].pic[i] for n in range(len(player.hand)))
                print(row)

        # compare hands

        #  ask for a hit

    if not proceed():
        break
