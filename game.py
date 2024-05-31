import pygame
from pygame.locals import KEYDOWN, K_RETURN, K_BACKSPACE
import sys
import httpx
import requests
import tkinter as tk
import time
from gamelogic import Deck, Player, Table, play_round, play_game

pygame.init()

root = tk.Tk()
l = root.winfo_screenwidth()
h = root.winfo_screenheight()
screen = pygame.display.set_mode((l, h))
pygame.display.set_caption("Poker Game")
input_box = pygame.Rect(l / 2 - l / 8, h / 1.5, l / 4, h / 16)


class PokerClient:

    # Инициации игрока
    def __init__(self, server_url):
        self.server_url = server_url

    def create_player(self, username, balance):
        response = httpx.post(f"{self.server_url}/players/", json={"username": username, "balance": balance})
        return response.json()

    def get_players(self):
        response = httpx.get(f"{self.server_url}/players/")
        return response.json()

    # Что-то для возможностей игрока
    def action(self, player_id, action, amount):
        action_payload = {
            "action": action,
            "amount": amount
        }
        response = httpx.post(f"{self.server_url}/players/{player_id}/action/", json=action_payload)
        return response.json()

    def bet(self, player_id, amount):
        return self.action(player_id, 'bet', amount)

    def call(self, player_id, amount):
        return self.action(player_id, 'call', amount)

    def check(self, player_id, amount):
        return self.action(player_id, 'check', 0)

    def fold(self, player_id):
        return self.action(player_id, 'fold', 0)

    def raisee(self, player_id, amount):
        return self.action(player_id, 'raisee', amount)

    # Чтобы было
    def delete_player(self, player_id):
        response = httpx.delete(f"{self.server_url}/players/{player_id}")
        return response.json()

    def check_turn(self, player_id):
        try:
            players = self.get_players()
            if players[player_id].turn:
                return True
            return False
        except Exception as e:
            print(f"Error: {e}")

def resize_image(original_image, new_width, new_height):
    resized_image = pygame.transform.scale(original_image, (new_width, new_height))
    return resized_image


def draw_card_animation(card_image, start_pos, end_pos, duration=0.5):
    start_time = time.time()
    while time.time() - start_time < duration:
        t = (time.time() - start_time) / duration
        current_pos = (start_pos[0] + t * (end_pos[0] - start_pos[0]), start_pos[1] + t * (end_pos[1] - start_pos[1]))
        screen.fill((0, 128, 0))
        render_all()
        screen.blit(card_image, current_pos)
        pygame.display.flip()
        pygame.time.delay(10)


def flip_card_animation(card_back, card_front, pos, duration=0.5):
    start_time = time.time()
    while time.time() - start_time < duration:
        t = (time.time() - start_time) / duration
        if t < 0.5:
            scale = 1 - 2 * abs(t - 0.25)
            card_image = pygame.transform.scale(card_back, (int(card_back.get_width() * scale), card_back.get_height()))
        else:
            scale = 1 - 2 * abs(t - 0.75)
            card_image = pygame.transform.scale(card_front,
                                                (int(card_front.get_width() * scale), card_front.get_height()))
        screen.fill((0, 128, 0))
        render_all()
        screen.blit(card_image, (pos[0] + (card_back.get_width() - card_image.get_width()) // 2, pos[1]))
        pygame.display.flip()
        pygame.time.delay(10)


def render_text(text, position, font_size=32, color=(255, 255, 255)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


def render_all():
    screen.fill((0, 128, 0))
    screen.blit(resized_back, (l / 20, h / 20))
    for i, (opponent_position, player) in enumerate(zip(opponent_positions, players[1:])):
        x, y = opponent_position
        for j in range(2):
            if i == 0 or i == 2:
                if j < len(opponent_cards_drawn[i]):
                    rotated_back = pygame.transform.rotate(resized_back, 90)
                    screen.blit(rotated_back, (x, y))
                y += 0.1 * l
            else:
                if j < len(opponent_cards_drawn[i]):
                    screen.blit(resized_back, (x, y))
                x += 0.1 * l
        render_text(f"{player['name']}: ${player['score']}", (opponent_position[0], opponent_position[1] - 30))

    for i, center_position in enumerate(center_positions):
        x, y = center_position
        if i < len(played_cards_drawn):
            screen.blit(resized_card_images[played_cards_drawn[i].get_image_index()], (x, y))
        elif i < len(played_cards_drawn) + len(played_cards_face_down):
            screen.blit(resized_back, (x, y))

    x = 0.4 * l
    y = 0.6 * h
    for card in hand_drawn:
        screen.blit(resized_card_images[card.get_image_index()], (x, y))
        x += 0.1 * l

    render_text(f"{players[0]['name']}: ${players[0]['score']}", (0.4 * l, 0.6 * h - 30))

    x = l / 15
    y = 0.85 * h
    button_rects.clear()
    for i in range(5):
        rect = screen.blit(resized_buttons[i], (x, y))
        button_rects.append(rect)
        x += resized_buttons[i].get_width() + 0.08 * l

    render_text(f"Bank: ${full_bank}", (0.8 * l, 0.05 * h), font_size=52, color=(255, 255, 255))
    render_text(f"Last bet: ${current_bet}", (0.8 * l, 0.1 * h), font_size=52, color=(255, 255, 255))

    if input_active:
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        text_surface = font.render(input_text, True, (255, 255, 255))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        pygame.display.flip()


def flip_center_cards():
    for i in range(3):
        animate_flip(center_positions[i], resized_back,
                     resized_card_images[played_cards_face_down[i].get_image_index()])
        played_cards_drawn.append(played_cards_face_down[i])


def animate_flip(position, back_image, front_image):
    x, y = position
    card_width, card_height = back_image.get_size()

    for frame in range(10):
        screen.fill((0, 128, 0))

        scale_factor = abs(1 - frame / 5.0)
        if frame < 5:
            scaled_image = pygame.transform.scale(back_image, (int(card_width * scale_factor), card_height))
        else:
            scaled_image = pygame.transform.scale(front_image, (int(card_width * scale_factor), card_height))

        new_x = x + (card_width - scaled_image.get_width()) // 2
        new_y = y

        screen.blit(scaled_image, (new_x, new_y))

        render_all()
        pygame.display.flip()
        time.sleep(0.05)


def display_menu():
    start_button = pygame.image.load("textures/buttons/start.png")
    exit_button = pygame.image.load("textures/buttons/exit.png")
    new_h = h / 8
    new_ls = start_button.get_width() / start_button.get_height() * new_height
    new_le = exit_button.get_width() / exit_button.get_height() * new_height
    start_button = resize_image(start_button, new_ls, new_h)
    exit_button = resize_image(exit_button, new_le, new_h)
    global input_box
    input_box = pygame.Rect(l / 2 - l / 8, h / 1.5, l / 4, h / 16)


    nickname = ""
    input_active = False

    while True:
        screen.fill((0, 128, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if start_button_rect.collidepoint(mouse_x, mouse_y):
                    return nickname
                elif exit_button_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()
                elif input_box.collidepoint(mouse_x, mouse_y):
                    input_active = True
                else:
                    input_active = False
            elif event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        nickname = nickname[:-1]
                    else:
                        nickname += event.unicode

        start_button_rect = screen.blit(start_button, (l / 2 - start_button.get_width() / 2, h / 3))
        exit_button_rect = screen.blit(exit_button, (l / 2 - exit_button.get_width() / 2, h / 2))

        pygame.draw.rect(screen, (255, 255, 255), input_box, 3)
        render_text(nickname, (input_box.x + 10, input_box.y + 4), font_size=64, color=(255, 255, 255))

        pygame.display.flip()


resized_card_images = []
new_width = l / 12
new_height = 1.42 * new_width

for i in range(2, 15):
    for suit in ['H', 'D', 'C', 'S']:
        original_image = pygame.image.load(f"textures/cards/{i}{suit}.png")
        resized_image = resize_image(original_image, new_width, new_height)
        resized_card_images.append(resized_image)

back = pygame.image.load("textures/cards/back_red.png")
resized_back = resize_image(back, new_width, new_height)

bet = pygame.image.load("textures/buttons/bet.png")
call = pygame.image.load("textures/buttons/call.png")
check = pygame.image.load("textures/buttons/check.png")
fold = pygame.image.load("textures/buttons/fold.png")
rais = pygame.image.load("textures/buttons/raise.png")

buttons = [bet, call, check, fold, rais]
resized_buttons = []

for i in range(5):
    new_height = h / 9
    new_width = buttons[i].get_width() / buttons[i].get_height() * new_height
    resized_image = resize_image(buttons[i], new_width, new_height)
    resized_buttons.append(resized_image)

hand = []
hand_drawn = []

center_positions = [(0.25 * l, 0.325 * h), (0.35 * l, 0.325 * h), (0.45 * l, 0.325 * h), (0.55 * l, 0.325 * h), (0.65 * l, 0.325 * h)]
played_cards = []
played_cards_drawn = []
played_cards_face_down = []

opponent_positions = [(0.02 * l, 0.325 * h), (0.4 * l, 0.05 * h), (0.79 * l, 0.325 * h)]
opponent_cards = [[], [], []]
opponent_cards_drawn = [[], [], []]

nickname = display_menu()

server_url = "http://127.0.0.1:8000"
client = PokerClient(server_url)
my_balance = 1000
# Создаем игрока
player_id = client.create_player(nickname, my_balance)
deck = client.get_deck()

players_data = client.get_players()
players = [Player(player['name'], player['score']) for player in players_data]
deck_data = client.get_deck()
table = Table(deck_data)

betting_round = 0
current_bet = 0
full_bank = 0
player_action = None
raise_amount = 0
input_active = False
input_text = ""
button_rects = []

while True:
    if client.check_turn(player_id):
        break
    time.sleep(5)

def handle_bet(amount):
    global currentPlayerBet, player_action, input_active
    currentPlayerBet = client.bet(player_id, amount)
    player_action = "bet"
    input_active = True

def handle_call(amount):
    global player_action, full_bank
    full_bank += client.call(player_id, amount)
    player_action = "call"

def handle_check():
    global player_action
    check(player_id, players[0].name, players[0].balance)
    player_action = "check"

def handle_fold():
    global player_action
    fold(player_id, players[0].name, players[0].balance)
    player_action = "fold"

def handle_raise():
    global currentPlayerBet, player_action, input_active, raise_amount
    currentPlayerBet = client.raisee(player_id, players[0].name, players[0].balance, raise_amount)
    player_action = "raise"
    input_active = True

font = pygame.font.Font(None, 25)

def process_player_action():
    global current_bet, raise_amount, input_active, player_action, full_bank, players
    if player_action == "bet":
        if players[0].balance >= currentPlayerBet > current_bet:
            players[0].balance -= currentPlayerBet
            current_bet = currentPlayerBet
            full_bank += currentPlayerBet
        elif currentPlayerBet <= current_bet:
            text_surface = font.render("Entered bet should be greater than current bet. Action isn't possible.", True,
                                       (255, 255, 255))
            screen.blit(text_surface, (50, 50))
        else:
            text_surface = font.render("Not enough money to bet. Action isn't possible.", True, (255, 255, 255))
            screen.blit(text_surface, (50, 50))
    elif player_action == "call":
        if players[0].balance >= current_bet:
            players[0].balance -= current_bet
            full_bank += current_bet
        else:
            text_surface = font.render("Not enough money to call. Action isn't possible.", True, (255, 255, 255))
            screen.blit(text_surface, (50, 50))
    elif player_action == "check":
        pass
    elif player_action == "fold":
        players[0].in_game = False
    elif player_action == "raise":
        if players[0].balance >= raise_amount:
            players[0].balance -= raise_amount
            current_bet += raise_amount
            full_bank += raise_amount
        else:
            text_surface = font.render("Not enough money to raise. Action isn't possible.", True, (255, 255, 255))
            screen.blit(text_surface, (50, 50))
    else:
        text_surface = font.render("Action not recognized. Please choose a valid action.", True, (255, 255, 255))
        screen.blit(text_surface, (50, 50))

    pygame.display.update()

    player_action = None
    input_active = False

runningrunning = True
draw_sequence = 0
num_cards_per_player = 2

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for i, button_rect in enumerate(button_rects):
                if button_rect.collidepoint(mouse_x, mouse_y):
                    if i == 0:
                        handle_bet(current_bet)
                    elif i == 1:
                        handle_call(current_bet)
                    elif i == 2:
                        handle_check()
                    elif i == 3:
                        handle_fold()
                    elif i == 4:
                        handle_raise()
        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == K_RETURN:
                    raise_amount = int(input_text)
                    current_bet += raise_amount
                    client.raisee(player_id, raise_amount)
                    process_player_action()
                    input_text = ""
                    input_active = False
                elif event.key == K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

    if not running:
        break

    # Fetch the latest game state from the server
    players = client.get_players()
    deck = client.get_deck()

    screen.fill((0, 128, 0))
    render_all()
    pygame.display.flip()

    if draw_sequence < num_cards_per_player:
        for i, opponent_position in enumerate(opponent_positions):
            x, y = opponent_position
            card = deck.draw()
            players[i + 1]['hand'].append(card)
            if i == 0 or i == 2:
                draw_card_animation(resized_back, (l / 20, h / 20), (x, y))
                y += 0.1 * l
            else:
                draw_card_animation(resized_back, (l / 20, h / 20), (x, y))
                x += 0.1 * l
            opponent_cards_drawn[i].append(card)

        card = deck.draw()
        players[0]['hand'].append(card)
        draw_card_animation(resized_card_images[card.get_image_index()], (l / 20, h / 20),
                            (0.4 * l + (len(players[0]['hand']) - 1) * 0.1 * l, 0.6 * h))
        hand_drawn.append(card)
        draw_sequence += 1

    elif draw_sequence == num_cards_per_player:
        for i in range(5):
            card = table.draw_center_card()
            draw_card_animation(resized_back, (l / 20, h / 20), center_positions[i])
            played_cards_face_down.append(card)

        flip_center_cards()
        draw_sequence += 1

    if player_action:
        process_player_action()
        if player_action == "fold":
            for i, opponent_position in enumerate(opponent_positions):
                for card in players[i + 1]['hand']:
                    draw_card_animation(resized_card_images[card.get_image_index()], (l / 20, h / 20), opponent_position)
            winner, scores, winning_combination = play_round(players, table)
            print(f"Winner: {winner} with {winning_combination}")
            print("Scores:", scores)
            table.reset()
            for player in players:
                player['hand'] = []
            draw_sequence = 0
            player_action = None

    # Sleep for a second before fetching the latest game state again
    time.sleep(1)

pygame.quit()