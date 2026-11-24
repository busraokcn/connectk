import time

from collections import Counter

from game import Game, MAX, state_from_moves
from search import AlphaBeta
from tt_search import TTAlphaBeta
from agirliklar import create_evaluator


game = Game(d=27)

evaluator = create_evaluator(game, "W3")


reference = AlphaBeta(
    game,
    order="A",
    evaluator=evaluator
)

tt_off = TTAlphaBeta(
    game,
    order="A",
    evaluator=evaluator,
    use_tt=False
)

tt_on = TTAlphaBeta(
    game,
    order="A",
    evaluator=evaluator,
    use_tt=True
)


positions = {

    "Bos tahta": [],

    "MAX gelisme": [
        0, 1, 0, 1
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

    "Sarmali gelisim": [
        4, 3, 5, 3, 0
    ]
}


DEPTH = 6

print("CONNECT-K ARENA - TT ILK TESTI")

print("Derinlik:", DEPTH)
print("Agirlik: W3")

total_hits = 0
total_cutoffs = 0


for name, moves in positions.items():

    state = state_from_moves(game, moves)

    print("\n" + "=" * 55)
    print("KONUM:", name)

    game.print_board(state)

    ref_move, ref_value, ref_nodes = (
        reference.choose_move(state, DEPTH)
    )

    start = time.perf_counter()

    off_move, off_value, off_nodes = (
        tt_off.choose_move(state, DEPTH)
    )

    off_time = (
        time.perf_counter() - start
    ) * 1000

    start = time.perf_counter()

    on_move, on_value, on_nodes = (
        tt_on.choose_move(state, DEPTH)
    )

    on_time = (
        time.perf_counter() - start
    ) * 1000

    print(
        f"\nNormal AlphaBeta | "
        f"Hamle: {ref_move} | "
        f"Deger: {ref_value:.6f} | "
        f"Dugum: {ref_nodes}"
    )

    print(
        f"TT KAPALI | "
        f"Hamle: {off_move} | "
        f"Deger: {off_value:.6f} | "
        f"Dugum: {off_nodes} | "
        f"Sure: {off_time:.3f} ms"
    )

    print(
        f"TT ACIK   | "
        f"Hamle: {on_move} | "
        f"Deger: {on_value:.6f} | "
        f"Dugum: {on_nodes} | "
        f"Sure: {on_time:.3f} ms"
    )

    # Uc arama sonucu ayni olmali
    assert ref_value == off_value == on_value

    assert on_move in game.actions(state)
    assert off_move in game.actions(state)

    # TT kapaliyken tablo bos kalmali
    assert len(tt_off.tt) == 0
    assert tt_off.tt_hits == 0

    # TT'nin sectigi hamleyi bagimsiz dogrula
    child = game.result(state, on_move)

    if state.player == MAX:

        exact_value = reference.min_value(
            child,
            DEPTH - 1,
            float("-inf"),
            float("inf")
        )

    else:

        exact_value = reference.max_value(
            child,
            DEPTH - 1,
            float("-inf"),
            float("inf")
        )

    assert exact_value == ref_value

    flags = Counter(
        entry.flag
        for entry in tt_on.tt.values()
    )

    reduction = (
        1 - on_nodes / off_nodes
    ) * 100

    print("\nTT ISTATISTIKLERI")

    print("Tablo boyutu:", len(tt_on.tt))
    print("TT hit:", tt_on.tt_hits)
    print("TT cutoff:", tt_on.tt_cutoffs)
    print("TT kayit:", tt_on.tt_stores)

    print("EXACT:", flags["EXACT"])
    print("LOWER:", flags["LOWER"])
    print("UPPER:", flags["UPPER"])

    print(
        f"Dugum azalmasi: %{reduction:.2f}"
    )

    total_hits += tt_on.tt_hits
    total_cutoffs += tt_on.tt_cutoffs

    print("Dogruluk: BASARILI")


assert total_hits > 0
assert total_cutoffs > 0


print("\n" + "=" * 55)
print("GENEL SONUCLAR")

print("Dogrulanan konum:", len(positions))
print("Toplam TT hit:", total_hits)
print("Toplam TT cutoff:", total_cutoffs)

print("\nTum TT ilk kontrolleri basarili!")