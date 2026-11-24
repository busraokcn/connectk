import time

from game import Game, MAX, state_from_moves
from search import Minimax, AlphaBeta
from evaluate import Evaluator


game = Game(d=27)

evaluator = Evaluator(game)

algorithms = {
    "Eski Minimax": Minimax(game),

    "Yeni Minimax": Minimax(
        game,
        evaluator=evaluator
    ),

    "Eski AlphaBeta": AlphaBeta(
        game,
        order="A"
    ),

    "Yeni AlphaBeta": AlphaBeta(
        game,
        order="A",
        evaluator=evaluator
    )
}


positions = {
    "Bos tahta": [],

    "MAX gelisme konumu": [
        0, 1, 0, 1
    ],

    "MIN gelisme konumu": [
        0, 1, 0, 1, 2
    ],

    "MAX kazanma": [
        0, 1, 0, 1, 0, 1, 0, 2
    ],

    "Rakibi engelleme": [
        1, 0, 1, 0, 2, 0, 2, 0
    ],

    "MIN kazanma": [
        1, 0, 1, 0, 2, 0, 2, 0, 3
    ],

    "Sarmali pencere": [
        4, 4, 5, 5, 0, 0, 1, 1
    ]
}


DEPTH = 3

print("CONNECT-K ARENA - EVAL ARAMA TESTI")
print("Derinlik:", DEPTH)


for name, moves in positions.items():

    state = state_from_moves(game, moves)

    print("\n" + "=" * 60)
    print("KONUM:", name)

    game.print_board(state)

    print(
        f"Tahta Eval: {evaluator.evaluate(state):.6f}"
    )

    results = {}

    for name_alg, algorithm in algorithms.items():

        start = time.perf_counter()

        move, value, nodes = algorithm.choose_move(
            state, DEPTH
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        results[name_alg] = (
            move, value, nodes
        )

        print(
            f"\n{name_alg}"
            f" | Hamle: {move}"
            f" | Deger: {value:.6f}"
            f" | Dugum: {nodes}"
            f" | Sure: {elapsed:.3f} ms"
        )

        assert move in game.actions(state)

    # Eski algoritmalar kendi aralarinda esit olmali
    assert (
        results["Eski Minimax"][1]
        == results["Eski AlphaBeta"][1]
    )

    # Yeni algoritmalar kendi aralarinda esit olmali
    assert (
        results["Yeni Minimax"][1]
        == results["Yeni AlphaBeta"][1]
    )

    # AlphaBeta dugum kontrolu
    assert (
        results["Yeni AlphaBeta"][2]
        <= results["Yeni Minimax"][2]
    )

    # Yeni AlphaBeta hamlesini Minimax ile dogrula
    move = results["Yeni AlphaBeta"][0]

    child = game.result(state, move)

    minimax = algorithms["Yeni Minimax"]

    if state.player == MAX:

        exact_value = minimax.min_value(
            child, DEPTH - 1
        )

    else:

        exact_value = minimax.max_value(
            child, DEPTH - 1
        )

    assert exact_value == results["Yeni Minimax"][1]

    print("\nDogruluk: BASARILI")


print("\nTum Eval arama kontrolleri basarili!")