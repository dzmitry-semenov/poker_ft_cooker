from pydantic import BaseModel
from typing import List
import httpx
import requests
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

class PokerClient:

    #Инициации игрока
    def __init__(self, server_url):
        self.server_url = server_url

    def create_player(self, username, balance):
        response = httpx.post(f"{self.server_url}/players/", json={"username": username, "balance": balance})
        return response.json()

    def get_players(self):
        response = httpx.get(f"{self.server_url}/players/")
        return response.json()

    def get_deck(self):
        response = httpx.get(f"{self.server_url}/Deck/")
        return response.json()

    #Что-то для возможностей игрока 
    def action(self, player_id):
        action_payload = {
            "action": "raise",
            "amount": 50
        }
        response = httpx.post(f"{self.server_url}/players/{player_id}/action/", json=action_payload)
        return response.json()

    def check_turn(self, player_id):
        try:
            players = self.get_players()
            if players[player_id].turn:
                return True
            return False
        except Exception as e:
            print(f"Error: {e}")

    #Чтобы было
    def delete_player(self, player_id):
        response = httpx.delete(f"{self.server_url}/players/{player_id}")
        return response.json()


# Пример использования клиента
server_url = "http://127.0.0.1:8000"
client = PokerClient(server_url)
my_balance = 1000
# Создаем игрока
player_id = client.create_player("dtepanchez", my_balance)
deck = client.get_deck()