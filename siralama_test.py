from game import Game, MAX, state_from_moves
from search import Minimax, AlphaBeta


game = Game(d=27)

minimax = Minimax(game)

algorithms = {
    "A": AlphaBeta(game, order="A"),
    "B": AlphaBeta(game, order="B"),
    "C": AlphaBeta(game, order="C")
}


positions = {
    "Bos tahta": [],

    "MAX kazanma": [
        0, 1, 0, 1, 0, 1, 0, 2
    ],

    "Rakibi engelleme": [
        1, 0, 1, 0, 2, 0, 2, 0
    ],

    "MIN kazanma": [
        1, 0, 1, 0, 2, 0, 2, 0, 3
    ],

    "Dolu sutun": [
        0, 0, 0, 0, 0
    ]
}


DEPTH = 4

print("CONNECT-K ARENA - HAMLE SIRALAMA TESTI")


for name, moves in positions.items():

    state = state_from_moves(game, moves)

    print("\nKONUM:", name)

    game.print_board(state)

    mm_move, mm_value, mm_nodes = (
        minimax.choose_move(state, DEPTH)
    )

    print("\nMinimax degeri:", mm_value)
    print("Minimax dugum sayisi:", mm_nodes)

    for method, algorithm in algorithms.items():

        ordered = algorithm.ordered_actions(state)

        move, value, nodes = algorithm.choose_move(
            state, DEPTH
        )

        print(f"\nYONTEM {method}")
        print("Hamle sirasi:", ordered)
        print("Secilen hamle:", move)
        print("Deger:", value)
        print("Dugum sayisi:", nodes)

        # Siralama yasal hamleleri degistirmemeli
        assert sorted(ordered) == game.actions(state)

        # Kok degeri ayni olmali
        assert value == mm_value

        # Dugum sayisi Minimax'i asmamali
        assert nodes <= mm_nodes

        # Secilen hamle yasal olmali
        assert move in game.actions(state)

        # Secilen hamlenin gercek degerini dogrula
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

        # Bos tahtada beklenen siralamalar
        if name == "Bos tahta":

            if method == "A":
                assert ordered == [0, 1, 2, 3, 4, 5]

            else:
                assert ordered == [2, 3, 1, 4, 0, 5]

        # C yonteminde taktik hamle ilk sirada olmali
        if method == "C" and name in (
            "MAX kazanma",
            "MIN kazanma",
            "Rakibi engelleme"
        ):

            assert ordered[0] == 0

        print("Dogruluk: BASARILI")


# Misere varyanti icin ek kontrol
misere_game = Game(d=27, V=2)

misere_state = state_from_moves(
    misere_game,
    [0, 1, 0, 1, 0, 1, 0, 2]
)

misere_algorithm = AlphaBeta(
    misere_game,
    order="C"
)

ordered = misere_algorithm.ordered_actions(
    misere_state
)

# 0 numarali sutun Misere'de kaybettirir
assert ordered[-1] == 0

print("\nMisere siralama kontrolu: BASARILI")

print("\nTum hamle siralama testleri basarili!")