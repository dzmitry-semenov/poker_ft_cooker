import pygame
import random
import sys
import tkinter as tk
import time

pygame.init()

root = tk.Tk()

l = root.winfo_screenwidth()
h = root.winfo_screenheight()
screen = pygame.display.set_mode((l, h))
pygame.display.set_caption("Poker Game")


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


def render_all():
    screen.fill((0, 128, 0))

    # Render deck texture in the top-left corner
    screen.blit(resized_back, (0, 0))

    # Render opponent cards
    for i, opponent_position in enumerate(opponent_positions):
        x, y = opponent_position
        for j in range(2):
            if i == 0 or i == 2:  # Left and right opponents
                if j < len(opponent_cards_drawn[i]):
                    rotated_back = pygame.transform.rotate(resized_back, 90)
                    screen.blit(rotated_back, (x, y))
                y += 0.1 * l
            else:  # Top opponent
                if j < len(opponent_cards_drawn[i]):
                    screen.blit(resized_back, (x, y))
                x += 0.1 * l

    # Render center cards
    for i, center_position in enumerate(center_positions):
        x, y = center_position
        if i < len(played_cards_drawn):
            screen.blit(resized_card_images[played_cards_drawn[i]], (x, y))
        elif i < len(played_cards_drawn) + len(played_cards_face_down):
            screen.blit(resized_back, (x, y))

    # Render player hand
    x = 0.4 * l
    y = 0.6 * h
    for card in hand_drawn:
        screen.blit(resized_card_images[card], (x, y))
        x += 0.1 * l

    # Render buttons
    x = l / 15
    y = 0.85 * h
    for i in range(5):
        screen.blit(resized_buttons[i], (x, y))
        x += resized_buttons[i].get_width() + 0.08 * l


def flip_center_cards():
    for i in range(3, 5):
        flip_card_animation(resized_back, resized_card_images[played_cards_face_down[i - 3]], center_positions[i])
        played_cards_drawn.append(played_cards_face_down[i - 3])


resized_card_images = []

new_width = l / 12
new_height = 1.42 * new_width

for i in range(1, 14):
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
deck = list(range(52))
random.shuffle(deck)

center_positions = [(0.25 * l, 0.325 * h), (0.35 * l, 0.325 * h), (0.45 * l, 0.325 * h), (0.55 * l, 0.325 * h),
                    (0.65 * l, 0.325 * h)]
played_cards = []
played_cards_drawn = []
played_cards_face_down = []

opponent_positions = [(0.02 * l, 0.325 * h), (0.4 * l, 0.05 * h), (0.79 * l, 0.325 * h)]
opponent_cards = [[], [], []]
opponent_cards_drawn = [[], [], []]

running = True
drawn_player_hand = False
drawn_center_cards = False
drawn_opponent_cards = [False, False, False]
draw_sequence = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not running:
        break

    screen.fill((0, 128, 0))
    render_all()
    pygame.display.flip()

    if draw_sequence == 0:
        # Draw one card for each player
        for i, opponent_position in enumerate(opponent_positions):
            x, y = opponent_position
            card = deck.pop()
            opponent_cards[i].append(card)
            if i == 0 or i == 2:  # Left and right opponents
                draw_card_animation(resized_back, (0, 0), (x, y))
                y += 0.1 * l
            else:  # Top opponent
                draw_card_animation(resized_back, (0, 0), (x, y))
                x += 0.1 * l
            opponent_cards_drawn[i].append(card)
        card = deck.pop()
        hand.append(card)
        draw_card_animation(resized_card_images[card], (0, 0), (0.4 * l + (len(hand) - 1) * 0.1 * l, 0.6 * h))
        hand_drawn.append(card)
        draw_sequence += 1

    elif draw_sequence == 1:
        # Draw one closed card in the center
        card = deck.pop()
        played_cards.append(card)
        draw_card_animation(resized_back, (0, 0), center_positions[0])
        played_cards_face_down.append(card)
        draw_sequence += 1

    elif draw_sequence == 2:
        # Draw the second card for each player
        for i, opponent_position in enumerate(opponent_positions):
            x, y = opponent_position
            if i == 0 or i == 2:  # Left and right opponents
                y += 0.1 * l
            else:  # Top opponent
                x += 0.1 * l
            card = deck.pop()
            opponent_cards[i].append(card)
            if i == 0 or i == 2:  # Left and right opponents
                draw_card_animation(resized_back, (0, 0), (x, y))
                y += 0.1 * l
            else:  # Top opponent
                draw_card_animation(resized_back, (0, 0), (x, y))
                x += 0.1 * l
            opponent_cards_drawn[i].append(card)
        card = deck.pop()
        hand.append(card)
        draw_card_animation(resized_card_images[card], (0, 0), (0.4 * l + (len(hand) - 1) * 0.1 * l, 0.6 * h))
        hand_drawn.append(card)
        draw_sequence += 1

    elif draw_sequence == 3:
        # Draw the second closed card in the center
        card = deck.pop()
        played_cards.append(card)
        draw_card_animation(resized_back, (0, 0), center_positions[1])
        played_cards_face_down.append(card)
        draw_sequence += 1

    elif draw_sequence == 4:
        # Draw the last three open cards in the center
        for i in range(2, 5):
            card = deck.pop()
            played_cards.append(card)
            draw_card_animation(resized_card_images[card], (0, 0), center_positions[i])
            played_cards_drawn.append(card)
        draw_sequence += 1

pygame.quit()