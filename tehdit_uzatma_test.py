import json
import csv
import time

from game import Game, MAX, state_from_moves
from tt_search import TTAlphaBeta
from threat_search import ThreatAlphaBeta
from agirliklar import create_evaluator


game = Game(d=27)

evaluator = create_evaluator(game, "W3")


# Ufuk etkisi deneyindeki konumu oku
with open(
    "ufuk_etkisi_ornek.json",
    "r",
    encoding="utf-8"
) as file:

    example = json.load(file)


state = state_from_moves(
    game,
    example["moves"]
)

bad_move = example["bad_move"]


normal = TTAlphaBeta(
    game,
    order="A",
    evaluator=evaluator,
    use_tt=True,
    check_interval=100
)

extended = ThreatAlphaBeta(
    game,
    order="A",
    evaluator=evaluator,
    use_tt=True
)


print("CONNECT-K ARENA - TEHDIT UZATMA")

print("Agirlik: W3")
print("Hamleler:", example["moves"])

print(
    "Siradaki oyuncu:",
    "MAX" if state.player == MAX else "MIN"
)

print("\nORIJINAL TAHTA")

game.print_board(state)


results = []


# ==========================================
# DERINLIK 1-5 KARSILASTIRMASI
# ==========================================

for depth in range(1, 6):

    print("\n" + "=" * 55)

    print("DERINLIK:", depth)

    for name, agent in (
        ("Normal", normal),
        ("Tehdit Uzatma", extended)
    ):

        start = time.perf_counter()

        move, value, nodes = agent.choose_move(
            state, depth
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        child = game.result(state, move)

        threats = extended.winning_moves(child)

        extensions = getattr(
            agent, "extensions", 0
        )

        extension_nodes = getattr(
            agent, "extension_nodes", 0
        )

        print("\nYontem:", name)

        print("Secilen hamle:", move)

        print(f"Arama degeri: {value:.6f}")

        print("Dugum:", nodes)

        print("Uzatma sayisi:", extensions)

        print("Ek dugum:", extension_nodes)

        print(f"Sure: {elapsed:.6f} ms")

        print(
            "Rakibin kazanma hamleleri:",
            threats
        )

        results.append({
            "Derinlik": depth,
            "Yontem": name,
            "Hamle": move,
            "Deger": value,
            "Dugum": nodes,
            "Uzatma Sayisi": extensions,
            "Ek Dugum": extension_nodes,
            "Sure (ms)": round(elapsed, 6),
            "Rakip Tehdit": len(threats)
        })


# ==========================================
# DERINLIK 1 DOGRULUK KONTROLU
# ==========================================

before = results[0]
after = results[1]

assert before["Hamle"] == bad_move

assert before["Rakip Tehdit"] > 0

assert after["Hamle"] != bad_move

assert after["Rakip Tehdit"] == 0

assert after["Uzatma Sayisi"] > 0

assert state.player * after["Deger"] > -1


print("\n" + "=" * 55)
print("ONCE VE SONRA")

print(
    "Normal aramanin hamlesi:",
    before["Hamle"]
)

print(
    "Tehdit uzatmanin hamlesi:",
    after["Hamle"]
)

print(
    "Normal aramadan sonraki rakip tehdidi:",
    before["Rakip Tehdit"]
)

print(
    "Uzatmali aramadan sonraki rakip tehdidi:",
    after["Rakip Tehdit"]
)

print("\nKOTU HAMLE ONLENDI!")

good_state = game.result(
    state,
    after["Hamle"]
)

game.print_board(good_state)


# ==========================================
# SONUCLARI KAYDET
# ==========================================

with open(
    "tehdit_uzatma_sonuclar.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=list(results[0].keys())
    )

    writer.writeheader()

    writer.writerows(results)


print(
    "\nSonuclar tehdit_uzatma_sonuclar.csv "
    "dosyasina kaydedildi."
)

print("Tehdit uzatma kontrolleri basarili!")