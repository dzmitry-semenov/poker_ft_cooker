import pygame
import random
import sys
import tkinter as tk

pygame.init()

root = tk.Tk()

l = root.winfo_screenwidth()
h = root.winfo_screenheight()
screen = pygame.display.set_mode((l, h))
pygame.display.set_caption("Poker Game")

def resize_image(original_image, new_width, new_height):
    resized_image = pygame.transform.scale(original_image, (new_width, new_height))
    return resized_image

resized_card_images = []

new_width = l/12
new_height = 1.42*new_width

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
    new_height = h/9
    new_width = buttons[i].get_width() / buttons[i].get_height() * new_height
    resized_image = resize_image(buttons[i], new_width, new_height)
    resized_buttons.append(resized_image)

hand = []
deck = list(range(52))
random.shuffle(deck)

for _ in range(2):
    card = deck.pop()
    hand.append(card)

center_positions = [(0.25*l, 0.325*h), (0.35*l, 0.325*h), (0.45*l, 0.325*h), (0.55*l, 0.325*h), (0.65*l, 0.325*h)]
played_cards = [deck.pop() for _ in range(5)]

running = True
while running:
    screen.fill((0, 128, 0))

    opponent_positions = [(0.02*l, 0.325*h), (0.4*l, 0.05*h), (0.79*l, 0.325*h)]  # Positions to display opponent hands
    for i, opponent_position in enumerate(opponent_positions):
        x, y = opponent_position
        for _ in range(2):
            screen.blit(resized_back, (x, y))
            x += 0.1*l

    for i, center_position in enumerate(center_positions):
        x, y = center_position
        screen.blit(resized_card_images[played_cards[i]], (x, y))

    x = 0.4*l
    y = 0.6*h
    for card in hand:
        screen.blit(resized_card_images[card], (x, y))
        x += 0.1*l

    x = l/15
    y = 0.85*h
    for i in range(5):
        new_width = buttons[i].get_width() / buttons[i].get_height() * new_height
        screen.blit(resized_buttons[i], (x, y))
        x += new_width + 0.08*l

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()