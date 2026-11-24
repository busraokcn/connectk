import math

from game import Game, MAX, MIN, EMPTY, state_from_moves
from agirliklar import WEIGHT_SETS, create_evaluator
from search import AlphaBeta


game = Game(d=27)

evaluators = {
    name: create_evaluator(game, name)
    for name in WEIGHT_SETS
}


def show_windows(state, evaluator):

    print("\nPUANLAMAYA DAHIL PENCERELER")

    count = 0

    for window in evaluator.windows:

        values = [
            state.board[row][col]
            for row, col in window.cells
        ]

        max_count = values.count(MAX)
        min_count = values.count(MIN)
        empty_count = values.count(EMPTY)

        if max_count > 0 and min_count > 0:
            continue

        feature = None

        if max_count == game.K - 1 and empty_count == 1:

            feature = "max_k1"

        elif max_count == game.K - 2 and empty_count == 2:

            feature = "max_k2"

        elif min_count == game.K - 1 and empty_count == 1:

            feature = "min_k1"

        elif min_count == game.K - 2 and empty_count == 2:

            feature = "min_k2"

        if feature is None:
            continue

        count += 1

        print(f"\nPencere {count}")
        print("Hucreler:", window.cells)
        print("Yon:", window.direction)
        print("Sarmali:", window.wraps)
        print("MAX tas:", max_count)
        print("MIN tas:", min_count)
        print("Bos hucre:", empty_count)
        print("Oznitelik:", feature)

        if window.wraps:

            if feature.startswith("max"):
                print("Ek oznitelik: max_wrap")
            else:
                print("Ek oznitelik: min_wrap")

    print("\nPuanlanan farkli pencere sayisi:", count)


print("CONNECT-K ARENA - KONTROL NOKTASI 3")

print("R:", game.R)
print("C:", game.C)
print("K:", game.K)
print("V:", game.V)

print("Toplam pencere:", len(evaluators["W1"].windows))


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

        print("\nOYUN TAHTASI")
        game.print_board(state)

        print(
            "Siradaki oyuncu:",
            "MAX" if state.player == MAX else "MIN"
        )

        if game.is_terminal(state):

            print("Oyun terminal durumda.")
            print("Utility:", game.utility(state))
            print("Eval hesaplanmasina gerek yok.")

            continue

        features = evaluators["W1"].features(state)

        print("\nOZ NITELIKLER")

        for name, value in features.items():

            print(f"{name:<12}: {value}")

        # Pencereleri tek tek goster
        show_windows(
            state,
            evaluators["W1"]
        )

        print("\nAGIRLIK KARSILASTIRMASI")

        for name, evaluator in evaluators.items():

            print("\nAGIRLIK:", name)

            weights = evaluator.weights

            manual_score = 0

            for feature, count in features.items():

                sign = (
                    1 if feature.startswith("max")
                    else -1
                )

                contribution = (
                    sign * weights[feature] * count
                )

                manual_score += contribution

                print(
                    f"{feature}: "
                    f"{sign * weights[feature]} "
                    f"x {count} = {contribution}"
                )

            if game.V == 2:
                manual_score = -manual_score

            manual_eval = math.tanh(
                manual_score / evaluator.scale
            )

            manual_eval = max(
                -0.999999,
                min(0.999999, manual_eval)
            )

            actual_score = evaluator.raw_score(state)

            actual_eval = evaluator.evaluate(state)

            assert manual_score == actual_score

            assert abs(
                manual_eval - actual_eval
            ) < 1e-12

            print("Ham puan:", actual_score)

            print(
                f"Eval: {actual_eval:.6f}"
            )

            print("Formul kontrolu: BASARILI")

        # Turnuva birincisi W3 ile hamle sec
        algorithm = AlphaBeta(
            game,
            order="A",
            evaluator=evaluators["W3"]
        )

        move, value, nodes = algorithm.choose_move(
            state, 5
        )

        print("\nW3 - ALPHA BETA ARAMA SONUCU")

        print("Derinlik: 5")
        print("Secilen hamle:", move)
        print(f"Arama degeri: {value:.6f}")
        print("Dugum sayisi:", nodes)

        print("\nTum kontroller basarili!")

    except ValueError as error:

        print("Hata:", error)

    except AssertionError:

        print("HATA: Dogruluk kontrolu basarisiz!")