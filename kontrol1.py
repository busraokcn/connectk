import time

from game import Game, MAX, state_from_moves
from search import Minimax


game = Game(d=27)
minimax = Minimax(game)

print("CONNECT-K ARENA - KONTROL NOKTASI 1")
print("R:", game.R)
print("C:", game.C)
print("K:", game.K)
print("V:", game.V)

while True:

    print("\nHamleleri bosluk birakarak giriniz.")
    print("Bos tahta icin Enter tusuna basiniz.")
    print("Cikis icin q yaziniz.")

    user_input = input("\nHamleler: ").strip()

    if user_input.lower() == "q":
        print("Program kapatildi.")
        break

    try:

        moves = [int(x) for x in user_input.split()]

        state = state_from_moves(game, moves)

        print("\nOLUSTURULAN TAHTA:")
        game.print_board(state)

        print(
            "\nSiradaki oyuncu:",
            "MAX" if state.player == MAX else "MIN"
        )

        print("Yasal hamleler:", game.actions(state))

        if game.is_terminal(state):
            print("Oyun zaten bitmis.")
            print("Utility:", game.utility(state))
            continue

        print("\nMINIMAX SONUCLARI:")

        print(
            f"{'Derinlik':<10}"
            f"{'Hamle':<8}"
            f"{'Deger':<8}"
            f"{'Dugum':<12}"
            f"{'Sure(ms)':<12}"
            f"{'b_etkin':<10}"
        )

        print("-" * 60)

        for depth in [2, 4, 6]:

            start = time.perf_counter()

            move, value, nodes = minimax.choose_move(
                state, depth
            )

            elapsed = (time.perf_counter() - start) * 1000

            b_effective = nodes ** (1 / depth)

            print(
                f"{depth:<10}"
                f"{move:<8}"
                f"{value:<8}"
                f"{nodes:<12}"
                f"{elapsed:<12.3f}"
                f"{b_effective:<10.3f}"
            )

        print("\nSECILEN HAMLEDEN SONRAKI TAHTA:")

        new_state = game.result(state, move)
        game.print_board(new_state)

        print("\nEn iyi hamle:", move)
        print("Minimax degeri:", value)

    except ValueError as error:
        print("Hata:", error)