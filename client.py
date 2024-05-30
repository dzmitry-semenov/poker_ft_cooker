import httpx
import requests
import time

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


    #Что-то для возможностей игрока 
    def bet(self, player_id, username, balance):
        response = httpx.put(f"{self.server_url}/players/{player_id}", json={"username": username, "balance": balance})
        return response.json()
    
    def call(self, player_id, username, balance):
        response = httpx.put(f"{self.server_url}/players/{player_id}", json={"username": username, "balance": balance})
        return response.json()
    
    def check(self, player_id, username, balance):
        response = httpx.put(f"{self.server_url}/players/{player_id}", json={"username": username, "balance": balance})
        return response.json()
    
    def fold(self, player_id, username, balance):
        response = httpx.put(f"{self.server_url}/players/{player_id}", json={"username": username, "balance": balance})
        return response.json()
    
    def raisee(self, player_id, username, balance):
        response = httpx.put(f"{self.server_url}/players/{player_id}", json={"username": username, "balance": balance})
        return response.json()


    #Чтобы было
    def delete_player(self, player_id):
        response = httpx.delete(f"{self.server_url}/players/{player_id}")
        return response.json()

def check_turn(player_id):
    try:
        response = requests.get(f'http://127.0.0.1:8000/turn/{player_id}')
        data = response.json()
        if data['message'] == "Your turn":
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")

# Пример использования клиента
server_url = "http://127.0.0.1:8000"
client = PokerClient(server_url)
my_balance = 1000
# Создаем игрока
player_id = client.create_player("dtepanchez", my_balance)

while True:
    if check_turn(player_id):
        break
    time.sleep(5)  # Добавляем задержку перед следующим запросом, чтобы снизить нагрузку на сервер