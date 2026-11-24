from game import Game, state_from_moves
from evaluate import Evaluator


game = Game(d=27)

evaluator = Evaluator(game)


positions = {
    "Bos tahta": [],

    "MAX kazanma tehdidi": [
        0, 1, 0, 1, 0, 1, 0, 2
    ],

    "MIN kazanma tehdidi": [
        1, 0, 1, 0, 2, 0, 2, 0
    ],

    "MAX uc tas": [
        0, 1, 0, 1, 0
    ],

    "Karisik pencere": [
        0, 0, 0, 1, 0, 1, 0
    ],

    "Sarmali pencere": [
        4, 4, 5, 5, 0, 0, 1, 1
    ]
}


print("CONNECT-K ARENA - OZ NITELIK TESTI")

print("Toplam pencere:", len(evaluator.windows))


for name, moves in positions.items():

    state = state_from_moves(game, moves)

    print("\nKONUM:", name)

    game.print_board(state)

    features = evaluator.features(state)

    print("\nOZ NITELIKLER")

    for feature, value in features.items():

        print(f"{feature:<12}: {value}")

    print("\nHam puan:", evaluator.raw_score(state))

    print(
        f"Eval degeri: {evaluator.evaluate(state):.6f}"
    )


print("\nTum oz nitelikler hesaplandi!")