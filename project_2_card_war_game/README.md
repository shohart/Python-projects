# War Card Game

This is a Python implementation of the classic card game War.

## Contents

1. [Overview](#overview)
2. [Classes](#classes)
3. [How to play](#how-to-play)

## Overview

The game is played between two players and requires a standard 52-card deck. The cards are shuffled and each player is dealt 26 cards. The players then take turns playing the top card from their hand. The player whose card has the higher value wins the battle and collects both cards. If both cards have the same value, it is a war. In a war, both players place additional cards face-down and then reveal the top card from each of those cards. The player who reveals a card with the higher value wins all the cards from the war. If both cards have the same value, the war continues until one player runs out of cards or both players agree to end the game. The player with all the cards at the end of the game wins.

## Classes

The game is implemented in the following classes:

### Card

This class represents a playing card. It has two attributes: suit and rank, and one method: str().

### Deck

This class creates a Deck object which has two methods: shuffle() which shuffles the deck and deal_one() which deals one card from the deck. The Deck object is initialized with a list of all the cards.

### Player

This class represents a Player in a game. It has two attributes: name and all_cards, and four methods: remove_one(), add_cards(), shuffle(), and str().

## How to Play

- Create two Player objects.
- Create a Deck object and shuffle it.
- Deal 26 cards to each player.
- Players take turns playing the top card from their hand.
- The player whose card has the higher value wins the battle and collects both cards.
- If both cards have the same value, it is a war.
- In a war, both players place additional cards face-down and then reveal the top card from each of those cards.
- The player who reveals a card with the higher value wins all the cards from the war.
- If both cards have the same value, the war continues until one player runs out of cards or both players agree to end the game.
- The player with all the cards at the end of the game wins.
