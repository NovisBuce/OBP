import pygame
import os

os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Moje PyGame hra")

# Hlavní smyčka hry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Ukončení hry
pygame.quit()
