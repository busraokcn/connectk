import json
import time
import sys

from game import Game, MAX, state_from_moves
from tt_search import TTAlphaBeta
from agirliklar import create_evaluator


game = Game(d=27)

evaluator = create_evaluator(game, "W3")

agent = TTAlphaBeta(
    game,
    order="A",
    evaluator=evaluator,
    use_tt=True,
    seed=27,
    check_interval=100
)


def inspect_position(moves):

    state = state_from_moves(game, moves)

    print("\nOYUN TAHTASI")

    game.print_board(state)

    print(
        "Siradaki oyuncu:",
        "MAX" if state.player == MAX else "MIN"
    )

    if game.is_terminal(state):

        print("Oyun terminal durumda.")
        print("Utility:", game.utility(state))

        return None

    print(
        "Zobrist hash:",
        agent.zobrist.hash_state(state)
    )

    start = time.perf_counter()

    result = agent.choose_move_timed(
        state,
        time_limit=1.0
    )

    elapsed = time.perf_counter() - start

    print("\nTAMAMLANAN DERINLIKLER")

    for item in result.history:

        print(
            f"D={item.depth:2} | "
            f"Hamle={item.move} | "
            f"Deger={item.value:.6f} | "
            f"Dugum={item.nodes}"
        )

    print("\nARAMA SONUCU")

    print("Secilen hamle:", result.move)
    print("Derinlik:", result.depth)
    print("Arama degeri:", result.value)
    print("Toplam dugum:", result.nodes)

    print("TT hit:", agent.tt_hits)
    print("TT cutoff:", agent.tt_cutoffs)
    print("TT boyutu:", len(agent.tt))

    print(f"Gercek sure: {elapsed:.6f} s")

    assert result.move in game.actions(state)

    assert elapsed <= 1.0, (
        "Zaman siniri asildi"
    )

    print("Kontrol: BASARILI")

    return elapsed


print("CONNECT-K ARENA - KONTROL NOKTASI 4")
print("R:", game.R)
print("C:", game.C)
print("K:", game.K)
print("V:", game.V)
print("Agirlik: W3")
print("TT: ACIK")
print("Sure siniri: 1 saniye")


# Otomatik 10 konum deneyi
if "--demo" in sys.argv:

    with open(
        "rastgele_konumlar.json",
        "r",
        encoding="utf-8"
    ) as file:

        positions = json.load(file)["positions"][:10]

    times = []

    for index, moves in enumerate(
        positions, start=1
    ):

        print("\n" + "=" * 50)
        print("KONUM:", index)

        print("Hamleler:", moves)

        elapsed = inspect_position(moves)

        assert elapsed is not None

        times.append(elapsed)

    print("\nGENEL SONUC")

    print("Basarili konum:", len(times), "/ 10")

    print(f"En uzun sure: {max(times):.6f} s")

    print("Tum kontrol noktasi testleri basarili!")


# Elle hamle girme
else:

    while True:

        print("\nHamleleri boslukla giriniz.")
        print("Bos tahta icin Enter.")
        print("Cikis icin q.")

        text = input("Hamleler: ").strip()

        if text.lower() == "q":

            print("Program kapatildi.")
            break

        try:

            moves = [
                int(x) for x in text.split()
            ]

            inspect_position(moves)

        except ValueError as error:

            print("Hata:", error)

        except AssertionError as error:

            print("Kontrol hatasi:", error)