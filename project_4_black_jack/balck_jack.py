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


def print_hands(dl, pl):
    print("\n" * 100)
    print(f"Dealer: {dl.hand_value}")
    for i in range(5):
        row = " ".join(dl.hand[n].pic[i] for n in range(len(dl.hand)))
        print(row)

    print("\n")
    if pl.box != 0:
        print(f"Current box: {pl.box}")
    else:
        print("\n")
    print("\n")

    print(f"Player: {pl.hand_value}")
    for i in range(5):
        row = " ".join(pl.hand[n].pic[i] for n in range(len(pl.hand)))
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
    print("| {0:<11} | {1:>5} |".format("Money in:", pl.money_deposit))
    print("| {0:<11} | {1:>5} |".format("Money out:", pl.bank))
    print("| {0:<11} | {1:>5} |".format("BALANCE:", pl.bank - pl.money_deposit))
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
        for op in pl_name.history:
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
            + str(pl_name.bank)
            + ","
            + str(pl_name.money_deposit)
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
        self.rounds_won = 0
        self.money_deposit = 0
        self.money_won = 0
        self.box = 0

    def hit(self):

        move = "_"

        while move not in ["stand", "hit", "h", "s"]:
            move = input("\nStand or Hit? ").lower()

            if move not in ["stand", "hit", "h", "s"]:
                print("\n" * 100)
                print('Sorry, you need to enter "Hit" or "Stand"!')
                continue

        return bool(move in ["hit", "h"])

    def add_funds(self):

        amount = "_"

        while not amount.isdigit() and amount != "0":
            amount = input("\nHow much do you want to add? ")

            if not amount.isdigit():
                print("\nSorry that is not a digit! Please enter a valid digit!")
                continue

        self.bank += int(amount)
        self.money_deposit += int(amount)

        self.history.append(f"{self.name},ADD,{amount},deposit")
        print(f"\n{amount} just added to your bank.\nYour bank: {self.bank}")

    def bet(self):

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
                self.history.append(f"{self.name},REMOVE,{amount},bet")
                print(
                    f"\nA bet of {amount} was successfully placed.",
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

    def reset(self):
        self.hand = []
        self.hand_value = 0
        self.box = 0

    def __str__(self):
        return (
            f"Player {self.name} has {len(self.hand)} cards."
            + f"Player's balance: {self.bank}"
        )


class Dealer:
    def __init__(self, shoe):
        self.hand = []
        self.shoe = shoe
        self.hand_value = 0
        self.shoe_left = len(self.shoe.all_cards)

    def deal_one(self):
        if self.shoe_left != 0:
            self.shoe_left -= 1
            return self.shoe.all_cards.pop(0)

        else:
            pass

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

    def reset(self, deck):
        self.hand = []
        self.hand_value = 0
        # self.shoe = deck

    def __str__(self):
        return f"There are {len(self.shoe)} cards in the shoe."


# initial variables
game_start = True
game_on = True


while game_on:

    # Display intro screen
    print("\n" * 100)
    art.tprint("BlackJack", font="speed")
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

    # Initiate class instances
    game_deck = Deck()

    dealer = Dealer(game_deck)
    player = Player()
    print(f"\nHello {player.name}!")
    print(f"\nThere are {dealer.shoe_left} cards in the shoe!")

    # Initial shuffle the deck
    game_deck.shuffle()
    time.sleep(3)

    # Initial bet
    if player.bank <= 0:
        print("\nYour initial bank is empty!")
        player.add_funds()
        time.sleep(2)

    while game_start and game_on and dealer.shoe_left >= 4:
        if dealer.shoe_left < 4:
            print("No cards left in the shoe!")
            time.sleep(2)
            break

        player.reset()
        dealer.reset(game_deck)
        dealer.shuffle()

        # Deal cards
        [player.add_cards(dealer.deal_one()) for _ in range(2)]
        [dealer.add_cards(dealer.deal_one()) for _ in range(2)]

        # Clear output
        print("\n" * 100)

        player.check_hand()
        dealer.check_hand()
        print_hands(dealer, player)

        # Ask for a bet
        player.box += player.bet()
        time.sleep(2)

        # Second loop with a hit
        while True:
            player.check_hand()
            dealer.check_hand()
            dealer.shuffle()
            print_hands(dealer, player)

            # Deal cards

            # Player's turn
            while True:
                player.check_hand()
                if player.hand_value >= 21:
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
                    player.check_hand()
                    print_hands(dealer, player)
                    player.add_cards(dealer.deal_one())
                    player.check_hand()
                    print_hands(dealer, player)

            # Dealer's turn
            while True:
                dealer.check_hand()
                if dealer.hand_value >= 21:
                    time.sleep(2)
                    break
                elif dealer.shoe_left == 0:
                    print("No cards left in the shoe!")
                    time.sleep(2)
                    break

                elif dealer.hand_value <= 16:
                    dealer.add_cards(dealer.deal_one())
                    dealer.check_hand()
                    print_hands(dealer, player)
                    time.sleep(2)

                elif dealer.hand_value >= 17:
                    break

            player.check_hand()
            dealer.check_hand()
            print_hands(dealer, player)

            # Check hands
            if player.hand_value > 21 >= dealer.hand_value:
                print(f"\nBUST! Your bet {player.box} lost.")
                time.sleep(4)
                break

            elif dealer.hand_value == 21 == player.hand_value:
                player.bank += player.box
                player.money_won += player.box
                player.rounds_won += 1
                print(f"\nTIE! Double BlackJack! You won {player.box}.")
                player.history.append(f"{player.name},ADD,{player.box},win")
                time.sleep(4)
                break

            elif 21 > player.hand_value > dealer.hand_value:
                player.bank += player.box
                player.money_won += player.box
                player.rounds_won += 1
                print(f"\nWIN! Your bet {player.box} won!")
                player.history.append(f"{player.name},ADD,{player.box},win")
                time.sleep(4)
                break

            elif dealer.hand_value != 21 == player.hand_value:
                player.bank += player.box * 1.5
                player.money_won += player.box * 1.5
                player.rounds_won += 1
                print(f"\nBALCKJACK! Congratulations! You won {player.box * 1.5}")
                player.history.append(f"{player.name},ADD,{player.box  * 1.5},win")
                time.sleep(5)
                break

            elif player.hand_value < dealer.hand_value <= 21:
                print(f"\nBUST! Your bet {player.box} lost.")
                time.sleep(4)
                break

            elif (player.hand_value == dealer.hand_value) or (
                player.hand_value > 21 and dealer.hand_value > 21
            ):
                player.bank += player.box
                player.money_won += player.box
                print(f"\nTIE! You won {player.box}.")
                player.history.append(f"{player.name},ADD,{player.box},win")
                time.sleep(4)
                break

            elif dealer.hand_value > 21 > player.hand_value:
                player.bank += player.box
                player.money_won += player.box
                player.rounds_won += 1
                print(f"\nWIN! Your bet {player.box} won!")
                player.history.append(f"{player.name},ADD,{player.box},win")
                time.sleep(4)
                break

            else:
                raise NameError("Unknown situation!")

        # Ask to play again
        if player.bank == 0:
            print("\nYour bank is empty!")
            player.add_funds()

    # Displaying final game scores
    game_over(player)
    statement(player)
    log_score(player)

    # Ask for continue
    game_on = continue_game()
