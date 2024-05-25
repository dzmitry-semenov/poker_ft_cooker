import random


class Card:
    suit_to_index = {'H': 0, 'D': 1, 'C': 2, 'S': 3}
    suits = ['H', 'D', 'C', 'S']
    values = list(range(2, 15))

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __lt__(self, other):
        return self.value < other.value

    def get_image_index(self):
        return (self.value - 2) + Card.suit_to_index[self.suit] * 13


class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in Card.suits for value in Card.values]
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()


class Player:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.hand = []

    def reset_hand(self):
        self.hand = []

    def add_card(self, card):
        self.hand.append(card)


class Table:
    def __init__(self):
        self.center_cards = []
        self.deck = Deck()

    def reset(self):
        self.center_cards = []
        self.deck = Deck()

    def draw_center_card(self):
        card = self.deck.draw()
        self.center_cards.append(card)
        return card


def calculate_score(hand):
    score = sum(card.value for card in hand)
    return score


def check_combination(hand):
    values = [card.value for card in hand]
    suits = [card.suit for card in hand]
    if len(set(values)) == 2:
        if values.count(values[0]) == 4 or values.count(values[1]) == 4:
            return "Four of a Kind"
        else:
            return "Full House"
    if len(set(suits)) == 1:
        return "Flush"
    if sorted(values) == list(range(min(values), max(values) + 1)):
        return "Straight"
    if len(set(values)) == 3:
        return "Three of a Kind"
    if len(set(values)) == 4:
        return "Two Pair"
    if len(set(values)) == 5:
        return "One Pair"
    return "High Card"


def play_round(players, table):
    table.reset()
    for player in players:
        player.reset_hand()
        for _ in range(2):
            player.add_card(table.deck.draw())

    for _ in range(3):
        table.draw_center_card()

    scores = {player.name: calculate_score(player.hand + table.center_cards) for player in players}
    combinations = {player.name: check_combination(player.hand + table.center_cards) for player in players}

    winner = max(scores, key=scores.get)
    winning_combination = combinations[winner]

    return winner, scores, winning_combination