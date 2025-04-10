from flask import Flask, request, jsonify, render_template
import random

app = Flask(__name__)

# Barvy a hodnoty UNO karet
BARVY = ['červená', 'modrá', 'zelená', 'žlutá']
HODNOTY = [str(i) for i in range(0, 10)]

# Herní stav
karty_hrace = []
karty_pocitace = []
balicek = []
odhazovaci_hromadka = []

hra_skoncila = False
zprava = ""


def vytvor_balicek():
    return [f"{barva}_{hodnota}" for barva in BARVY for hodnota in HODNOTY] * 1


def rozdej_karty():
    global balicek, karty_hrace, karty_pocitace, odhazovaci_hromadka, hra_skoncila, zprava
    balicek = vytvor_balicek()
    random.shuffle(balicek)
    karty_hrace = [balicek.pop() for _ in range(7)]
    karty_pocitace = [balicek.pop() for _ in range(7)]
    odhazovaci_hromadka = [balicek.pop()]
    hra_skoncila = False
    zprava = ""


def karta_sedi(karta, vrchni_karta):
    barva1, hodnota1 = karta.split("_")
    barva2, hodnota2 = vrchni_karta.split("_")
    return barva1 == barva2 or hodnota1 == hodnota2


@app.route('/')
def domovska_stranka():
    return render_template('uno.html')


@app.route('/nova_hra', methods=['POST'])
def nova_hra():
    rozdej_karty()
    return jsonify({
        'karty_hrace': karty_hrace,
        'vrchni_karta': odhazovaci_hromadka[-1],
        'zprava': "Hra začala!"
    })


@app.route('/tah_hrace', methods=['POST'])
def tah_hrace():
    global hra_skoncila, zprava

    zvolena_karta = request.json.get('karta')

    if zvolena_karta not in karty_hrace:
        return jsonify({'chyba': 'Karta není v ruce hráče'})

    if not karta_sedi(zvolena_karta, odhazovaci_hromadka[-1]):
        return jsonify({'chyba': 'Karta nesedí barvou ani hodnotou'})

    karty_hrace.remove(zvolena_karta)
    odhazovaci_hromadka.append(zvolena_karta)

    if len(karty_hrace) == 0:
        hra_skoncila = True
        zprava = "Vyhrál jsi!"
        return jsonify({'stav': 'vyhra', 'zprava': zprava})

    # Tah počítače
    tah_pocitace()

    return jsonify({
        'karty_hrace': karty_hrace,
        'vrchni_karta': odhazovaci_hromadka[-1],
        'zprava': zprava,
        'hra_skoncila': hra_skoncila
    })


def tah_pocitace():
    global hra_skoncila, zprava

    for karta in karty_pocitace:
        if karta_sedi(karta, odhazovaci_hromadka[-1]):
            karty_pocitace.remove(karta)
            odhazovaci_hromadka.append(karta)
            zprava = f"Počítač odhodil {karta}"
            if len(karty_pocitace) == 0:
                hra_skoncila = True
                zprava = "Počítač vyhrál!"
            return

    # Počítač si lízne kartu
    if balicek:
        nova_karta = balicek.pop()
        karty_pocitace.append(nova_karta)
        zprava = "Počítač si lízl kartu"


@app.route('/tahni', methods=['POST'])
def tahni():
    if balicek:
        nova_karta = balicek.pop()
        karty_hrace.append(nova_karta)
        return jsonify({'nova_karta': nova_karta, 'zprava': f"Líznul jsi {nova_karta}"})
    return jsonify({'zprava': "Balíček je prázdný!"})


if __name__ == '__main__':
    app.run(debug=True)
