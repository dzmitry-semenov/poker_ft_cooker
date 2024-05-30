from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
from typing import List
from requests import Request
import uvicorn
import time
import random

class Card:
    suit_to_index = {'H': 0, 'D': 1, 'C': 2, 'S': 3}
    suits = ['H', 'D', 'C', 'S']
    values = list(range(2, 15))

    def __init__(self, suit: str, value: int):
        self.suit = suit
        self.value = value

    def __lt__(self, other):
        return self.value < other.value

    def get_image_index(self):
        return (self.value - 2) + Card.suit_to_index[self.suit] * 13
    

class PlayerIn(BaseModel):
    name: str
    score: int = 1000

class Player(BaseModel):
    id: int
    name: str
    score: int = 1000
    turn: bool = False
    action: str = 'none'
    bet: int = 0
    hand: List[Card] = []

class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in Card.suits for value in Card.values]
        random.shuffle(self.cards)
        self.draw_center_card = self.cards[:5]
        self.cards = self.cards[5:]

    def draw(self):
        return self.cards.pop()

players: List[Player] = []
deck = Deck()
bank = 0


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


def find_winner():
    global players, deck
    scores = {player.name: calculate_score(player.hand + deck.center_cards) for player in players if player.in_game}
    combination_ranks = {}
    combinations = {}

    for player in players:
        if player.in_game:
            rank, combination = check_combination(player.hand + deck.center_cards)
            combination_ranks[player.name] = rank
            combinations[player.name] = combination

    max_combination_rank = max(combination_ranks.values())
    winners = [player for player, rank in combination_ranks.items() if rank == max_combination_rank]


    if len(winners) != 1:
        max_score = max(scores[player] for player in winners)
        winners = [player for player in winners if scores[player] == max_score]

    return winners



# Инициализация FastAPI
app = FastAPI()

# Эндпоинты для управления игроками
@app.post("/players/")
async def create_player(player_in: PlayerIn):
    players.append(Player(id = len(players), name=player_in.name, score=player_in.score))
    return len(players)-1

class Action(BaseModel):
    action: str
    amount: int

@app.post("/players/{player_id}/action")
async def action(player_id: int, action: Action):
    global players
    players[player_id].action = action.action

@app.get("/players/", response_model=List[Player])
async def read_players():
    global players
    return players

@app.get("/Deck/", response_model=List[Player])
async def read_deck():
    global deck
    return deck


async def deal_cards_to_players():
    global players
    for player in players:
        # Раздаем каждому игроку по две карты
        player(hand = [deck.draw(), deck.draw()])


async def betting_round(start_player: int, a=[1, 1, 1, 1], marker_raise = 0):
    global players
    
    num_players = len(players)
    player_turn = start_player
    betting_continues = True
    while betting_continues and sum(a) > 1:
        player = players[player_turn]
        if player.score > 0 and a[player_turn]:
            player.turn = True
            while player.action == 'none':
                time.sleep(0.5)
                continue
            player.turn = False
            curent_action = players[player_turn]
            if curent_action.action == 'fold':
                a[player_turn] = 0
                players[player_turn].hand = []
            elif curent_action.action != 'check':
                players[player_turn].score -= curent_action.amount
                players[player_turn].bet += curent_action.amount
                bank += curent_action.amount
                if curent_action.action == 'raisee':
                    betting_round(player_turn+1, a, 1)
        if (player_turn - start_player)%4 == (sum(a)-marker_raise)%4:
            b = set([a[i]*players[i].bet for i in range(4)])
            b.remove(0)
            betting_continues = (len(b) != 1)
        player_turn = (player_turn + 1) % num_players

    

@app.delete("/players/{player_id}/", response_model=Player)
async def delete_player(player_id: int):
    global players
    for player in players:
        if player.id == player_id:
            del_player = player
    return del_player
    


if __name__ == "__main__":
    while len(players) < 4:
        time.sleep(1)
        continue
    
    for _ in range(4):
        deck = Deck() 
        deal_cards_to_players()
        for _ in range(3):
            betting_round(start_player=0)
        for winner in find_winner():
            players[winner].score += bank/len(find_winner())
        for player in players:
            player.bet = 0
            player.hand = []
            player.action = ''
            player.turn = False

    uvicorn.run(app, host="127.0.0.5", port=8000)