from game import Game, MAX, state_from_moves
from search import Minimax, AlphaBeta


game = Game(d=27)

minimax = Minimax(game)
alphabeta = AlphaBeta(game)


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


print("CONNECT-K ARENA - ALPHA BETA")
print("R:", game.R)
print("C:", game.C)
print("K:", game.K)
print("V:", game.V)


for name, moves in positions.items():

    state = state_from_moves(game, moves)

    print("\nKONUM:", name)

    game.print_board(state)

    depth = 4

    mm_move, mm_value, mm_nodes = minimax.choose_move(
        state, depth
    )

    ab_move, ab_value, ab_nodes = alphabeta.choose_move(
        state, depth
    )

    print("\nMINIMAX")
    print("Hamle:", mm_move)
    print("Deger:", mm_value)
    print("Dugum:", mm_nodes)

    print("\nALPHA BETA")
    print("Hamle:", ab_move)
    print("Deger:", ab_value)
    print("Dugum:", ab_nodes)

    reduction = (1 - ab_nodes / mm_nodes) * 100

    print(
        f"\nDugum azalmasi: %{reduction:.2f}"
    )

    # İki algoritmanın değeri aynı olmalı
    assert mm_value == ab_value

    # Alpha-beta daha fazla düğüm gezmemeli
    assert ab_nodes <= mm_nodes

    # Seçilen hamle yasal olmalı
    assert ab_move in game.actions(state)

    # Alpha-beta'nın seçtiği hamleyi
    # düz Minimax ile bağımsız olarak doğrula
    child = game.result(state, ab_move)

    if state.player == MAX:
        exact_value = minimax.min_value(
            child, depth - 1
        )
    else:
        exact_value = minimax.max_value(
            child, depth - 1
        )

    assert exact_value == mm_value

    print("Dogruluk kontrolu: BASARILI")


print("\nTum Alpha-Beta kontrolleri basarili!")