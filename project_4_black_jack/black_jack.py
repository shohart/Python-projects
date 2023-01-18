import random
import time
import os
import datetime as dt
import art


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
    """
    Function to ask the user if they would like to continue playing the game

    Returns
    -------
    bool
        True if the user answered yes, False if the user answered no
    """
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


def print_hands(dl, pl):
    """Prints the current hands of the dealer and player.

    Parameters:
    dl (Dealer): The dealer object
    pl (Player): The player object
    """
    print("\n" * 100)
    print(f"Dealer: {dl.hand.value}")
    for i in range(5):
        row = " ".join(dl.hand.cards[n].pic[i] for n in range(len(dl.hand.cards)))
        print(row)

    print("\n")
    if pl.box != 0:
        print(f"Current box: {pl.box}")
    else:
        print("\n")
    print("\n")

    print(f"Player: {pl.hand.value}")
    for i in range(5):
        row = " ".join(pl.hand.cards[n].pic[i] for n in range(len(pl.hand.cards)))
        print(row)


def game_over(pl):
    """Prints the game over screen with the final scores.

    Parameters:
        None

    Returns:
        None
    """
    print("\n" * 100)
    print("| {0:=^19} |".format(" GAME OVER "))
    print("| See you, {0:^10} |".format(pl.name))
    print("| {0:-^19} |".format(" Score: "))
    print("| {0:<11} | {1:>5} |".format("Rounds won:", pl.rounds_won))
    print("| {0:<11} | {1:>5} |".format("Money in:", pl.chips.deposit))
    print("| {0:<11} | {1:>5} |".format("Money out:", pl.chips.bank))
    print("| {0:<11} | {1:>5} |".format("BALANCE:", pl.chips.bank - pl.chips.deposit))
    print("\n")


def statement(pl_name):
    """
    Writes players's statement to the {pl_name}_statement.txt file.

    Parameters
    ----------
    name : str
        The name of the player

    Returns
    -------
    None
    """
    filename = f"{pl_name.name}_statement.txt"
    now = dt.datetime.now().strftime("%d-%m-%Y,%H:%M")

    if os.path.exists(filename):
        append_write = "a"  # append if already exists
    else:
        append_write = "w"  # make a new file if not

    with open(filename, append_write, encoding="utf8") as score_file:
        for op in pl_name.chips.history:
            score_file.write(now + "," + op + "\n")


def log_score(pl_name):
    """
    Writes a game score to the scores.txt file.

    Parameters
    ----------
    name : str
        The name of the player

    Returns
    -------
    None
    """
    filename = "scores.txt"

    if os.path.exists(filename):
        append_write = "a"  # append if already exists
    else:
        append_write = "w"  # make a new file if not

    now = dt.datetime.now().strftime("%d-%m-%Y,%H:%M")

    with open(filename, append_write, encoding="utf8") as score_file:
        score_file.write(
            now
            + ","
            + pl_name.name
            + ","
            + str(pl_name.rounds_won)
            + ","
            + str(pl_name.chips.bank)
            + ","
            + str(pl_name.chips.deposit)
            + "\n"
        )


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
        """
        Shuffle a deck.
        """
        random.shuffle(self.all_cards)
        print("Deck has been shuffled!")

    def deal_one(self):
        return self.all_cards.pop()


class Hand:
    """
    Represents a hand of cards in a card game.

    Attributes:
        cards (list): A list of individual cards held in the hand.
        value (int): The numerical value of the hand.
    """

    def __init__(self):
        self.cards = []
        self.value = 0

    def add(self, card):
        """
        Add cards to hand.

        Args:
            card (card): card to be added
        """
        self.cards.append(card)

    def check(self):
        """
        Count total value of cards in hand, according to black jack rules.
        """
        aces = []
        rest = []

        for card in self.cards:
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

        self.value = total

    def reset(self):
        self.cards = []
        self.value = 0

    def __str__(self):
        return f"Hand is {len(self.hand)} cards. Score: {self.value}"


class Chips:
    """
    A class for managing chips
    """

    def __init__(self, player):
        """
        Initialize a Chips object

        Parameters:
            player (str): The name of the player
        """
        self.bank = 0
        self.history = []
        self.deposit = 0
        self.won = 0
        self.player_name = player

    def add_funds(self):
        """
        Add funds to the player's bank
        """
        amount = "_"

        while not amount.isdigit() and amount != "0":
            amount = input("\nHow much do you want to add? ")

            if not amount.isdigit():
                print("\nSorry that is not a digit! Please enter a valid digit!")
                continue

        self.bank += int(amount)
        self.deposit += int(amount)

        self.history.append(f"{self.player_name},ADD,{amount},deposit")
        print(f"\n{amount} just added to your bank.\nYour bank: {self.bank}")

    def bet(self):
        """
        Place a bet with the player's funds
        """
        amount = "_"

        while True:
            amount = input("\nPlace a bet! Enter the ammount: ")

            if not amount.isdigit() or amount == "0":
                print("\nSorry that is not a valid bet!")
                continue

            elif int(amount) > self.bank:
                print("\nOops! You do not have so much money! Please reduce a bet!")
                continue

            else:
                self.bank -= int(amount)
                self.history.append(f"{self.player_name},REMOVE,{amount},bet")
                print(
                    f"\nA bet of {amount} was successfully placed.",
                    f"Your bank: {self.bank}",
                )
                break

        return int(amount)

    def __str__(self):
        """
        Represent the Chips object as a string with the player's balance
        """
        return f"Player's balance: {self.bank}"


class Player:
    """
    This class represents a player in the game.

    It holds information about the player's name,
    hand, chips, rounds won and box score.
    """

    def __init__(self):
        self.name = input("Enter your name to proceed: ")
        self.hand = Hand()
        self.chips = Chips(self.name)
        self.rounds_won = 0
        self.box = 0

    def hit(self):
        """
        This method gets the player's decision to either stand or hit.
        """

        move = "_"

        while move not in ["stand", "hit", "h", "s"]:
            move = input("\nStand or Hit? ").lower()

            if move not in ["stand", "hit", "h", "s"]:
                print("\n" * 100)
                print('Sorry, you need to enter "Hit" or "Stand"!')
                continue

        return bool(move in ["hit", "h"])

    def reset(self):
        """
        This method resets the player's box score and hand.
        """
        self.box = 0
        self.hand.reset()

    def __str__(self):
        return (
            f"Player {self.name} has {len(self.hand.cards)} cards."
            + f"Player's balance: {self.chips.bank}"
        )


class Dealer:
    """
    A class representing a blackjack dealer.

    Attributes:
        hand (Hand): The dealer's current hand.
        shoe (Deck): The shoe from which the dealer draws cards.
        shoe_left (int): The number of cards left in the shoe.
    """

    def __init__(self):
        self.hand = Hand()
        self.shoe = Deck()
        self.shoe_left = len(self.shoe.all_cards)

    def deal_one(self):
        """
        Draw one card from the shoe.
        """
        if self.shoe_left != 0:
            self.shoe_left -= 1
            return self.shoe.all_cards.pop(0)

        else:
            pass

    def reset(self):
        """
        Reset the dealer's hand.
        """
        self.hand.reset()

    def __str__(self):
        """
        Return a string representation of the dealer.
        """
        return f"There are {len(self.shoe)} cards in the shoe."


# Clean output
print("\n" * 100)

# initial variables
game_start = True
game_on = True
player = Player()

# Main game cycle
while True:

    # Display intro screen
    print("\n" * 100)
    art.tprint("BlackJack", font="speed")
    print(f"\nHello {player.name}!\n")
    print(
        "Rules:\n"
        " * The goal of blackjack is to beat the dealer's hand\n"
        "   without going over 21.\n"
        " * The player can continue to hit until they either go\n"
        "   over 21 or decide to stay.\n"
        " * Face cards (Kings, Queens, and Jacks) are all worth 10.\n"
        "   Aces can be worth 1 or 11.\n"
        " * If the player goes over 21, they have 'busted' and lost\n"
        "   the game.\n"
        " * Whoever has the higher total wins the game.\n"
        " * If both totals are equal, the game is a tie.\n"
    )

    game_start = game_on = proceed()
    if not game_on:
        break

    # Initiate class instances
    dealer = Dealer()

    print(f"\nThere are {dealer.shoe_left} cards in the shoe!")
    time.sleep(3)

    # Initial bet
    if player.chips.bank <= 0:
        print("\nYour initial bank is empty!")
        player.chips.add_funds()
        time.sleep(2)

    # Check if shoe is empty
    while game_start and game_on and dealer.shoe_left >= 4:
        if dealer.shoe_left < 4:
            print("No cards left in the shoe!")
            time.sleep(2)
            break

        player.reset()
        dealer.reset()
        [dealer.shoe.shuffle() for _ in range(3)]

        # Deal cards
        [player.hand.add(dealer.deal_one()) for _ in range(2)]
        dealer.hand.add(dealer.deal_one())

        # Clear output
        print("\n" * 100)

        player.hand.check()
        dealer.hand.check()
        print_hands(dealer, player)

        # Ask for a bet
        player.box += player.chips.bet()
        time.sleep(2)

        # Second loop with a hit
        while True:
            player.hand.check()
            dealer.hand.check()
            dealer.shoe.shuffle()
            print_hands(dealer, player)

            # Deal cards

            # Player's turn
            while True:
                player.hand.check()
                if player.hand.value >= 21:
                    time.sleep(2)
                    break
                elif dealer.shoe_left == 0:
                    print("No cards left in the shoe!")
                    time.sleep(2)
                    break

                hit = player.hit()

                if not hit:
                    break
                else:
                    # player.hand.check()
                    # print_hands(dealer, player)
                    player.hand.add(dealer.deal_one())
                    player.hand.check()
                    print_hands(dealer, player)

            # Dealer's turn
            while True:
                dealer.hand.check()
                if dealer.hand.value >= 21:
                    time.sleep(2)
                    break
                elif dealer.shoe_left == 0:
                    print("No cards left in the shoe!")
                    time.sleep(2)
                    break

                elif dealer.hand.value <= 16:
                    dealer.hand.add(dealer.deal_one())
                    dealer.hand.check()
                    print_hands(dealer, player)
                    time.sleep(2)

                elif dealer.hand.value >= 17:
                    break

            player.hand.check()
            dealer.hand.check()
            print_hands(dealer, player)

            # Check hands
            if player.hand.value > 21 >= dealer.hand.value:
                print(f"\nBUST! Your bet {player.box} lost.")
                time.sleep(4)
                break

            elif dealer.hand.value == 21 == player.hand.value:
                player.chips.bank += player.box
                player.chips.won += player.box
                player.rounds_won += 1
                print(f"\nTIE! Double BlackJack! You won {player.box}.")
                player.chips.history.append(f"{player.name},ADD,{player.box},win")
                time.sleep(4)
                break

            elif 21 > player.hand.value > dealer.hand.value:
                player.chips.bank += player.box
                player.chips.won += player.box
                player.rounds_won += 1
                print(f"\nWIN! Your bet {player.box} won!")
                player.chips.history.append(f"{player.name},ADD,{player.box},win")
                time.sleep(4)
                break

            elif dealer.hand.value != 21 == player.hand.value:
                player.chips.bank += player.box * 1.5
                player.chips.won += player.box * 1.5
                player.rounds_won += 1
                print(f"\nBALCKJACK! Congratulations! You won {player.box * 1.5}")
                player.chips.history.append(
                    f"{player.name},ADD,{player.box  * 1.5},win"
                )
                time.sleep(5)
                break

            elif player.hand.value < dealer.hand.value <= 21:
                print(f"\nBUST! Your bet {player.box} lost.")
                time.sleep(4)
                break

            elif (player.hand.value == dealer.hand.value) or (
                player.hand.value > 21 and dealer.hand.value > 21
            ):
                player.chips.bank += player.box
                player.chips.won += player.box
                print(f"\nTIE! You won {player.box}.")
                player.chips.history.append(f"{player.name},ADD,{player.box},win")
                time.sleep(4)
                break

            elif dealer.hand.value > 21 > player.hand.value:
                player.chips.bank += player.box
                player.chips.won += player.box
                player.rounds_won += 1
                print(f"\nWIN! Your bet {player.box} won!")
                player.chips.history.append(f"{player.name},ADD,{player.box},win")
                time.sleep(4)
                break

            else:
                raise NameError("Unknown situation!")

        # Ask to play again
        if player.chips.bank == 0:
            print("\nYour bank is empty!")
            player.chips.add_funds()

    # Displaying final game scores
    game_over(player)
    statement(player)
    log_score(player)

    # Ask for continue
    game_on = continue_game()
    if not game_on:
        break
