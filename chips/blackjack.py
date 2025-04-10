import pygame
import os
import random

# Inicializace Pygame
pygame.init()

# Nastavení okna
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack")

# Cesty k souborům
CARDS_PATH = "/workspaces/OBP/karty"  # Tento adresář by měl obsahovat obrázky karet

# Načítání karet
def load_card(card_name):
    card = pygame.image.load(os.path.join(CARDS_PATH, card_name))
    return pygame.transform.scale(card, (100, 150))  # Přizpůsobíme velikost karet

# Herní proměnné
player_cards = []
dealer_cards = []
player_money = 100
player_bet = 0
game_over = False
player_turn = True

# Fonty
font = pygame.font.Font(None, 36)

# Funkce pro rozdaní karty
def deal_card(to_whom):
    card_file = random.choice(os.listdir(CARDS_PATH))  # Vybere náhodně kartu
    to_whom.append(card_file)

# Funkce pro spočítání hodnoty ruky
def calculate_hand(hand):
    value = 0
    aces = 0  # Počet es
    for card in hand:
        # Rozdělíme název karty a získáme první část (hodnota karty) - např. '2', 'ace', 'jack'
        rank = card.split("_")[0]  # '2' v '2_of_spades', 'ace' v 'ace_of_spades', atd.
        
        # Pokud je karta obrázková (J, Q, K), přičteme 10
        if rank in ["jack", "queen", "king"]:
            value += 10
        elif rank == "ace":
            aces += 1  # Počítáme esy zvlášť
            value += 11  # Eso začíná s hodnotou 11
        else:
            try:
                value += int(rank)  # Číslo karty (2-10)
            except ValueError:
                continue  # Pokud se nepodaří převést, přeskočíme kartu (např. chybné soubory)

    # Pokud máme eso a hodnota ruky přesahuje 21, převedeme esy na 1
    while value > 21 and aces:
        value -= 10  # Pokud přesáhneme 21, vezmeme esu hodnotu 1 místo 11
        aces -= 1
    
    return value

# Funkce pro vykreslení textu
def draw_text(text, x, y, color=(255, 255, 255)):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

# Funkce pro zobrazení tlačítka
def draw_button(text, x, y, width, height, action=None):
    # Vykreslení tlačítka
    pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height))  # Rámování tlačítka
    pygame.draw.rect(screen, (255, 255, 255), (x + 5, y + 5, width - 10, height - 10))  # Tlačítko se světlým pozadím
    draw_text(text, x + 10, y + 10)
    return pygame.Rect(x, y, width, height)

# Rozdání počátečních karet
deal_card(player_cards)
deal_card(player_cards)
deal_card(dealer_cards)
deal_card(dealer_cards)

# Hlavní smyčka hry
running = True
while running:
    screen.fill((0, 128, 0))  # Zelené pozadí

    # Události
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and player_turn and not game_over:
            x, y = event.pos

            # Možnost vsadit 10
            bet_button = draw_button("Vsadit 10", 50, 450, 150, 50)
            if bet_button.collidepoint(x, y):
                if player_money >= 10:
                    player_money -= 10
                    player_bet += 10
            
            # Možnost "Hit" - vzít kartu
            hit_button = draw_button("Hit", 220, 450, 100, 50)
            if hit_button.collidepoint(x, y):
                if calculate_hand(player_cards) <= 21:
                    deal_card(player_cards)
                    if calculate_hand(player_cards) > 21:  # Pokud hráč přesáhne 21
                        game_over = True
                        player_turn = False
            
            # Možnost "Stand" - stát
            stand_button = draw_button("Stand", 340, 450, 100, 50)
            if stand_button.collidepoint(x, y):
                player_turn = False

    # Zobrazení sázky a peněz
    draw_text(f"Peníze: ${player_money}", 40, 50)
    draw_text(f"Sázka: ${player_bet}", 40, 100)

    # Vykreslení karet hráče
    for i, card in enumerate(player_cards):
        screen.blit(load_card(card), (150 + i * 120, 300))  # Posun karet pro lepší rozložení

    # Vykreslení karet dealera
    for i, card in enumerate(dealer_cards):
        if player_turn and i != 0:  # První kartu ukáže, ostatní skryje
            pygame.draw.rect(screen, (0, 0, 0), (150 + i * 120, 100, 100, 150))  # Zakrytá karta
        else:
            screen.blit(load_card(card), (150 + i * 120, 100))

    # Konec hry: dealer tahá karty
    if not player_turn and not game_over:
        while calculate_hand(dealer_cards) < 17:  # Dealer musí brát karty, dokud nemá alespoň 17
            deal_card(dealer_cards)

        player_score = calculate_hand(player_cards)
        dealer_score = calculate_hand(dealer_cards)

        # Zobrazení výsledků
        if player_score > 21:  # Pokud hráč překročí 21
            draw_text("Prohrál jsi, překročil jsi 21!", 800, 250, (255, 0, 0))
        elif dealer_score > 21:  # Pokud dealer překročí 21
            draw_text("Vyhrál jsi, dealer překročil 21!", 800, 250, (255, 255, 0))
            player_money += player_bet * 2
        elif dealer_score > player_score:
            draw_text("Prohrál jsi!", 800, 250, (255, 0, 0))
        elif player_score > dealer_score:
            draw_text("Vyhrál jsi!", 800, 250, (255, 255, 0))
            player_money += player_bet * 2
        else:
            draw_text("Remíza!", 800, 250, (255, 255, 255))
            player_money += player_bet  # Vrácení sázky

        game_over = True

    # Vykreslení tlačítek
    bet_button = draw_button("Vsadit 10", 50, 450, 150, 50)
    hit_button = draw_button("Hit", 220, 450, 100, 50)
    stand_button = draw_button("Stand", 340, 450, 100, 50)
    reset_button = draw_button("Reset", 460, 450,100, 50)

    pygame.display.flip()

pygame.quit()
