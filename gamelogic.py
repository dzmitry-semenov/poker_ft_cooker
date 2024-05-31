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
    def __init__(self, deck_data=None):
        if deck_data:
            self.cards = [Card(card['suit'], card['value']) for card in deck_data]
        else:
            self.cards = [Card(suit, value) for suit in Card.suits for value in Card.values]
            random.shuffle(self.cards)
        self.draw_center_card = self.cards[:5]
        self.cards = self.cards[5:]

    def draw(self):
        return self.cards.pop()


class Player:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.hand = []
        self.in_game = True

    def reset_hand(self):
        self.hand = []

    def add_card(self, card):
        self.hand.append(card)


class Table:
    def __init__(self, deck_data):
        self.center_cards = []
        self.deck = Deck(deck_data)

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
    if len(set(suits)) == 1:
        if sorted(values) == list(range(10, 15)):
            return 1000, "Royal Flush"
        elif len(set(values)) == 5 and sorted(values)[4] - sorted(values)[0] == 4:
            return 900, "Straight Flush"
        else:
            return 600, "Flush"
    elif len(set(values)) == 2:
        if values.count(values[0]) == 4 or values.count(values[1]) == 4:
            return 800, "Four of a Kind"
        else:
            return 700, "Full House"
    elif sorted(values) == list(range(min(values), max(values) + 1)):
        return 500, "Straight"
    elif len(set(values)) == 3:
        return 400, "Three of a Kind"
    elif len(set(values)) == 4:
        return 300, "Two Pair"
    elif len(set(values)) == 5:
        return 200, "One Pair"
    else:
        return 100, "High Card"


def play_round(players, table):
    table.reset()
    for player in players:
        player.reset_hand()
        player.in_game = True
        for _ in range(2):
            player.add_card(table.deck.draw())

    for _ in range(3):
        table.draw_center_card()

    scores = {player.name: calculate_score(player.hand + table.center_cards) for player in players if player.in_game}
    combination_ranks = {}
    combinations = {}

    for player in players:
        if player.in_game:
            rank, combination = check_combination(player.hand + table.center_cards)
            combination_ranks[player.name] = rank
            combinations[player.name] = combination

    max_combination_rank = max(combination_ranks.values())
    winners = [player for player, rank in combination_ranks.items() if rank == max_combination_rank]


    if len(winners) == 1:
        winner = winners[0]
    else:
        winner = winners[0]

    winning_combination = combinations[winner]

    return winner, scores, winning_combination


def play_game(players, table):
    while True:
        winner, scores, winning_combination = play_round(players, table)
        print(f"Winner: {winner} with {winning_combination}")
        print("Scores:", scores)

        response = input("Do you want to play another round? (yes/no): ").strip().lower()
        if response != 'yes':
            break