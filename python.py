from flask import Flask, render_template, request, jsonify
import os
import random

app = Flask(__name__)

# Cesta k adresáři s kartami
CARDS_PATH = "/workspaces/OBP/static/cards"

# Třída pro hráče
class Hrac:
    def __init__(self):
        self.karty = []  # Seznam karet hráče
        self.penize = 1000  # Počáteční peníze
        self.sazka = 0  # Počáteční sázka

    def pridej_kartu(self, karta):
        self.karty.append(karta)  # Přidá kartu do ruky hráče

    def vypocitej_hodnotu(self):
        hodnota = 0
        esa = 0
        # Pro každý karty vypočítáme hodnotu
        for karta in self.karty:
            rank = karta.split("_")[0]  # Vezmeme první část názvu karty (hodnota)
            if rank in ["jack", "queen", "king"]:
                hodnota += 10  # J, Q, K mají hodnotu 10
            elif rank == "ace":
                hodnota += 11  # Eso má hodnotu 11
                esa += 1  # Počítáme esa, protože mohou mít hodnotu 1 nebo 11
            else:
                hodnota += int(rank)  # Čísla karet přičteme jako hodnotu
        # Pokud je hodnota větší než 21 a máme eso, snížíme hodnotu o 10
        while hodnota > 21 and esa:
            hodnota -= 10
            esa -= 1
        return hodnota  # Vrátí celkovou hodnotu karet

    def reset(self):
        self.karty = []  # Vyprázdní ruku hráče
        self.sazka = 0  # Resetuje sázku

# Třída pro hru
class Hra:
    def __init__(self):
        self.hrac = Hrac()  # Vytvoříme nového hráče
        self.dealer = Hrac()  # Vytvoříme dealera
        self.konec = False  # Určuje, jestli hra skončila
        self.tah_hrace = True  # Určuje, jestli je tah hráče

    def rozdej_kartu(self, komu):
        karta = random.choice(os.listdir(CARDS_PATH))  # Náhodně vybere kartu
        komu.pridej_kartu(karta)  # Přidá kartu hráči nebo dealerovi

    def nova_hra(self, sazka):
        self.hrac.reset()  # Resetuje hráče
        self.dealer.reset()  # Resetuje dealera
        self.hrac.sazka = sazka  # Nastaví sázku
        self.hrac.penize -= sazka  # Odečte sázku od peněz hráče
        self.konec = False  # Hra ještě neskončila
        self.tah_hrace = True  # Hráč začíná
        # Rozdání karet
        self.rozdej_kartu(self.hrac)
        self.rozdej_kartu(self.hrac)
        self.rozdej_kartu(self.dealer)
        self.rozdej_kartu(self.dealer)

    def hit(self):
        if self.tah_hrace and self.hrac.vypocitej_hodnotu() <= 21:
            self.rozdej_kartu(self.hrac)  # Hráč si vezme kartu
            if self.hrac.vypocitej_hodnotu() > 21:
                self.konec = True  # Pokud hráč překročí 21, hra končí
                self.tah_hrace = False

    def stand(self):
        self.tah_hrace = False  # Hráč končí svůj tah
        while self.dealer.vypocitej_hodnotu() < 17:
            self.rozdej_kartu(self.dealer)  # Dealer bere karty dokud nemá alespoň 17
        self.konec = True  # Hra končí
        self.vyhodnot()  # Vyhodnotí výsledek

    def vyhodnot(self):
        # Vyhodnotí výsledek hry
        skore_hrace = self.hrac.vypocitej_hodnotu()
        skore_dealera = self.dealer.vypocitej_hodnotu()
        if skore_hrace > 21:
            return "Prohráli jste!"  # Hráč překročil 21, prohrál
        elif skore_dealera > 21:
            self.hrac.penize += self.hrac.sazka * 2  # Hráč vyhrál, dealer překročil 21
            return "Vyhrál jste!"  # Hráč vyhrál
        elif skore_hrace > skore_dealera:
            self.hrac.penize += self.hrac.sazka * 2  # Hráč vyhrál, jeho skóre je vyšší
            return "Vyhrál jste!"  # Hráč vyhrál
        elif skore_hrace < skore_dealera:
            return "Prohráli jste!"  # Dealer má vyšší skóre, hráč prohrál
        else:
            self.hrac.penize += self.hrac.sazka  # Remíza, hráč dostane zpět svou sázku
            return "Remíza!"  # Remíza

# Vytvoříme novou hru
hra = Hra()

# === ROUTY ===
@app.route('/')
def index():
    return render_template("index.html", player_money=hra.hrac.penize, player_bet=hra.hrac.sazka)

# Spustí novou hru
@app.route('/start_game', methods=['POST'])
def start_game():
    sazka = int(request.form.get("bet", 10))  # Získáme sázku z formuláře
    hra.nova_hra(sazka)  # Spustíme novou hru
    # Pošleme karty hráče a dealera zpět do HTML
    player_cards = [f"cards/{card}" for card in hra.hrac.karty]
    dealer_cards = [f"cards/{card}" for card in hra.dealer.karty[:1]]  # Dealer má jen jednu kartu
    return jsonify({
        "player_money": hra.hrac.penize,
        "player_bet": hra.hrac.sazka,
        "player_cards": player_cards,
        "dealer_cards": dealer_cards
    })

# Hráč chce vzít další kartu
@app.route('/hit', methods=['POST'])
def hit():
    hra.hit()  # Hráč si vezme kartu
    player_cards = [f"cards/{card}" for card in hra.hrac.karty]  # Karty hráče
    return jsonify({
        "player_cards": player_cards,
        "game_over": hra.konec  # Informace, jestli hra skončila
    })

# Hráč chce skončit tah
@app.route('/stand', methods=['POST'])
def stand():
    hra.stand()  # Hráč končí svůj tah
    player_cards = [f"cards/{card}" for card in hra.hrac.karty]  # Karty hráče
    dealer_cards = [f"cards/{card}" for card in hra.dealer.karty]  # Karty dealera
    return jsonify({
        "player_cards": player_cards,
        "dealer_cards": dealer_cards,
        "game_result": hra.vyhodnot(),  # Výsledek hry
        "player_money": hra.hrac.penize  # Aktuální stav peněz hráče
    })

# Resetování hry
@app.route('/reset_game', methods=['POST'])
def reset_game():
    hra.hrac.reset()  # Resetuje hráče
    hra.dealer.reset()  # Resetuje dealera
    return jsonify({
        "player_money": hra.hrac.penize,  # Počáteční stav peněz
        "player_bet": hra.hrac.sazka  # Počáteční stav sázky
    })

# Spustí Flask aplikaci
if __name__ == '__main__':
    app.run(debug=True)
