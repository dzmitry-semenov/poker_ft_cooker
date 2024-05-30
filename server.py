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


# Инициализация FastAPI
app = FastAPI()

# Эндпоинты для управления игроками
@app.post("/players/")
async def create_player(player_in: PlayerIn):
    players.append(Player(id = len(players), name=player_in.name, score=player_in.score))
    return len(players)-1


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

class GameState:
    def __init__(self):
        self.current_bet = 0
        self.pot = 0
        self.stage = 0  # 0 for preflop, 1 for flop, etc.

    def reset_for_next_round(self):
        self.current_bet = 0
        self.pot = 0
        self.stage = 0

game_state = GameState()

async def betting_round(start_player: int):
    global players, game_state
    
    num_players = len(players)
    player_turn = start_player
    betting_continues = True
    
    while betting_continues:
        player = players[player_turn]
        if player.score > 0:
            print(f"Player {player.name}'s turn to bet.")
            # Here, you would prompt player to make their move: fold, call, raise.
            # This is simplified; in a real scenario, you would handle player input asynchronously.
            
            # Example bet (this part should be replaced with actual player interaction):
            bet = min(100, player.score)  # Just an example bet to keep things moving
            player_score -= bet
            game_state.pot += bet
            
            # If player raises, you should reset the counter for how many players need to match the bet
            
        player_turn = (player_turn + 1) % num_players
        betting_continues = False  # For our simplified example, we'll stop after one loop. In practice, you continue until all bets are matched.




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
        betting_round(start_player=0)

    uvicorn.run(app, host="127.0.0.5", port=8000)