import time

from game import Game, MAX, state_from_moves
from search import Minimax, AlphaBeta


game = Game(d=27)

minimax = Minimax(game)

algorithms = {
    "A": AlphaBeta(game, order="A"),
    "B": AlphaBeta(game, order="B"),
    "C": AlphaBeta(game, order="C")
}

DEPTH = 6

print("CONNECT-K ARENA - KONTROL NOKTASI 2")
print("R:", game.R)
print("C:", game.C)
print("K:", game.K)
print("V:", game.V)
print("Derinlik:", DEPTH)


while True:

    print("\nHamleleri bosluk birakarak giriniz.")
    print("Bos tahta icin Enter tusuna basiniz.")
    print("Cikis icin q yaziniz.")

    user_input = input("\nHamleler: ").strip()

    if user_input.lower() == "q":

        print("Program kapatildi.")
        break

    try:

        moves = [
            int(x) for x in user_input.split()
        ]

        state = state_from_moves(game, moves)

        print("\nOLUSTURULAN TAHTA:")
        game.print_board(state)

        print(
            "Siradaki oyuncu:",
            "MAX" if state.player == MAX else "MIN"
        )

        print(
            "Yasal hamleler:",
            game.actions(state)
        )

        if game.is_terminal(state):

            print("Oyun zaten bitmis.")
            print("Utility:", game.utility(state))

            continue

        # Minimax referans olcumu
        start = time.perf_counter()

        mm_move, mm_value, mm_nodes = (
            minimax.choose_move(state, DEPTH)
        )

        mm_time = (
            time.perf_counter() - start
        ) * 1000

        print("\nMINIMAX SONUCU")
        print("Hamle:", mm_move)
        print("Deger:", mm_value)
        print("Dugum:", mm_nodes)
        print(f"Sure: {mm_time:.3f} ms")

        # Alfa-beta yontemlerini karsilastir
        for method, algorithm in algorithms.items():

            print(f"\nALPHA BETA - YONTEM {method}")

            print(
                "Hamle sirasi:",
                algorithm.ordered_actions(state)
            )

            start = time.perf_counter()

            move, value, nodes = (
                algorithm.choose_move(state, DEPTH)
            )

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            reduction = (
                1 - nodes / mm_nodes
            ) * 100

            print("Secilen hamle:", move)
            print("Deger:", value)
            print("Dugum:", nodes)
            print(f"Sure: {elapsed:.3f} ms")
            print(f"Dugum azalmasi: %{reduction:.2f}")

            # Dogruluk kontrolleri
            assert value == mm_value
            assert nodes <= mm_nodes
            assert move in game.actions(state)

            # Secilen hamleyi Minimax ile dogrula
            child = game.result(state, move)

            minimax.nodes = 0

            if state.player == MAX:

                exact_value = minimax.min_value(
                    child, DEPTH - 1
                )

            else:

                exact_value = minimax.max_value(
                    child, DEPTH - 1
                )

            assert exact_value == mm_value

            print("Dogruluk: BASARILI")

        print("\nTum yontemler dogru sonuc verdi!")

    except ValueError as error:

        print("Hata:", error)

    except AssertionError:

        print("HATA: Dogruluk kontrolu basarisiz!")