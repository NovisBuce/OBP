from flask import Flask, render_template, request, jsonify
import random
import os

app = Flask(__name__)

# Cesty k souborům
CARDS_PATH = os.path.join(os.getcwd(), "static/cards")

# Herní proměnné
player_cards = []
dealer_cards = []
player_money = 100
player_bet = 0
game_over = False
player_turn = True

# Načítání karty - vrací URL na obrázek karty
def load_card(card_name):
    return f"/static/cards/{card_name}"  # Vrací cestu k obrázku

# Funkce pro rozdání karet
def deal_card(to_whom):
    card_file = random.choice(os.listdir(CARDS_PATH))  # Vybere náhodně kartu
    to_whom.append(card_file)

# Funkce pro spočítání hodnoty ruky
def calculate_hand(hand):
    value = 0
    aces = 0  # Počet es
    for card in hand:
        rank = card.split("_")[0]
        if rank in ["jack", "queen", "king"]:
            value += 10
        elif rank == "ace":
            aces += 1
            value += 11
        else:
            try:
                value += int(rank)
            except ValueError:
                continue

    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value

# Start nové hry
@app.route('/start_game', methods=['POST'])
def start_game():
    global player_cards, dealer_cards, player_bet, player_money, game_over, player_turn
    player_cards = []
    dealer_cards = []
    player_bet = int(request.form.get('bet', 0))
    player_money -= player_bet
    game_over = False
    player_turn = True

    # Rozdání počátečních karet
    deal_card(player_cards)
    deal_card(player_cards)
    deal_card(dealer_cards)
    deal_card(dealer_cards)

    # Vracení karet jako URL
    return jsonify({
        'player_cards': [load_card(card) for card in player_cards],
        'dealer_cards': [load_card(dealer_cards[0])]  # První karta dealera je vidět
    })

# Hit - vzít kartu
@app.route('/hit', methods=['POST'])
def hit():
    global player_cards, game_over, player_turn
    if player_turn and calculate_hand(player_cards) <= 21:
        deal_card(player_cards)
        if calculate_hand(player_cards) > 21:  # Pokud hráč překročí 21
            game_over = True
            player_turn = False
    return jsonify({
        'player_cards': [load_card(card) for card in player_cards],
        'game_over': game_over
    })

# Stand - stát
@app.route('/stand', methods=['POST'])
def stand():
    global dealer_cards, player_cards, game_over, player_turn, player_money, player_bet

    # Dealer táhne karty, dokud nemá alespoň 17
    while calculate_hand(dealer_cards) < 17:
        deal_card(dealer_cards)

    player_score = calculate_hand(player_cards)
    dealer_score = calculate_hand(dealer_cards)

    # Vyhodnocení výsledku hry
    if player_score > 21:
        result = "Prohráli jste, překročili jste 21!"
    elif dealer_score > 21:
        result = "Vyhráli jste, dealer překročil 21!"
        player_money += player_bet * 2
    elif dealer_score > player_score:
        result = "Prohráli jste!"
    elif player_score > dealer_score:
        result = "Vyhráli jste!"
        player_money += player_bet * 2
    else:
        result = "Remíza!"
        player_money += player_bet  # Vrácení sázky

    game_over = True
    player_turn = False  # Hráč už nemůže hrát

    # Vracení aktuálního stavu hry
    return jsonify({
        'player_cards': [os.path.join(CARDS_PATH, card) for card in player_cards],
        'dealer_cards': [os.path.join(CARDS_PATH, card) for card in dealer_cards],
        'game_result': result,
        'player_money': player_money,
        'game_over': game_over
    })
    
@app.route('/reset_game', methods=['POST'])
def reset_game():
    global player_cards, dealer_cards, player_bet, player_money, game_over, player_turn
    
    # Obnovíme herní proměnné na výchozí hodnoty
    player_cards = []
    dealer_cards = []
    player_bet = 0
    player_money = 100  # Předpokládáme, že počáteční množství peněz je 100
    game_over = False
    player_turn = True
    
    return jsonify({
        'player_cards': [],
        'dealer_cards': [],
        'player_money': player_money,
        'player_bet': player_bet,
        'game_result': "",
        'game_over': game_over
    })

@app.route('/')
def home():
    return render_template('index.html', player_money=player_money, player_bet=player_bet)

if __name__ == '__main__':
    app.run(debug=True)
