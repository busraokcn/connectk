import time

from game import Game, state_from_moves
from search import AlphaBeta
from timed_search import TimedAlphaBeta
from agirliklar import create_evaluator


game = Game(d=27)

# Asama 3 turnuvasinin birincisi
evaluator = create_evaluator(game, "W3")

algorithm = TimedAlphaBeta(
    game,
    order="A",
    evaluator=evaluator,
    check_interval=1000
)

reference = AlphaBeta(
    game,
    order="A",
    evaluator=evaluator
)


print("CONNECT-K ARENA - ITERATIVE DEEPENING")
print("Agirlik: W3")
print("Sure siniri: 1 saniye")
print("Kontrol araligi: 1000 dugum")


# ==========================================
# SABIT DERINLIK DOGRULUK KONTROLU
# ==========================================

state = state_from_moves(
    game,
    [0, 1, 0, 1]
)

ref_move, ref_value, ref_nodes = (
    reference.choose_move(state, 3)
)

result = algorithm.choose_move_timed(
    state,
    time_limit=1.0,
    max_depth=3
)

assert result.depth == 3
assert result.value == ref_value
assert not result.timed_out

print("\nSabit derinlik dogruluk kontrolu: BASARILI")


# ==========================================
# 1 SANIYELIK ARAMA DENEYLERI
# ==========================================

positions = {

    "Bos tahta": [],

    "MAX gelisme konumu": [
        0, 1, 0, 1
    ],

    "Rakibi engelleme": [
        1, 0, 1, 0, 2, 0, 2, 0
    ],

    "Sarmali gelisim": [
        4, 3, 5, 3, 0
    ]
}

times = []
depths = []

for name, moves in positions.items():

    state = state_from_moves(game, moves)

    print("\n" + "=" * 65)
    print("KONUM:", name)

    game.print_board(state)

    start = time.perf_counter()

    result = algorithm.choose_move_timed(
        state,
        time_limit=1.0
    )

    actual_elapsed = time.perf_counter() - start

    print("\nTAMAMLANAN ITERASYONLAR")

    for item in result.history:

        print(
            f"Derinlik: {item.depth:2} | "
            f"Hamle: {item.move} | "
            f"Deger: {item.value:.6f} | "
            f"Dugum: {item.nodes:6} | "
            f"Ilk denenen: {item.first_move} | "
            f"Sure: {item.elapsed:.6f} s"
        )

    # Onceki en iyi hamlenin
    # yeni iterasyonda ilk sirada oldugunu kontrol et.
    for previous, current in zip(
        result.history,
        result.history[1:]
    ):

        assert current.first_move == previous.move

    # Son tamamlanan iterasyonun sonucu korunmali.
    if result.history:

        last = result.history[-1]

        assert result.move == last.move
        assert result.value == last.value
        assert result.depth == last.depth

    assert result.move in game.actions(state)

    assert result.nodes >= sum(
        item.nodes for item in result.history
    )

    print("\nARAMA SONUCU")

    print("Secilen hamle:", result.move)

    print("Son tamamlanan derinlik:", result.depth)

    print("Arama degeri:", result.value)

    print("Toplam dugum:", result.nodes)

    print(f"Gercek sure: {actual_elapsed:.6f} s")

    print("Sure doldu:", result.timed_out)

    assert actual_elapsed <= 1.0, (
        "1 saniye siniri asildi"
    )

    times.append(actual_elapsed)
    depths.append(result.depth)

    print("Zaman kontrolu: BASARILI")
    print("Hamle siralamasi kontrolu: BASARILI")
    print("Son iterasyon kontrolu: BASARILI")


# ==========================================
# GENEL SONUCLAR
# ==========================================

print("\n" + "=" * 65)
print("GENEL SONUCLAR")

print("Konum sayisi:", len(positions))

print(
    f"Ortalama derinlik: "
    f"{sum(depths) / len(depths):.2f}"
)

print(
    f"Ortalama sure: "
    f"{sum(times) / len(times):.6f} s"
)

print(f"En uzun sure: {max(times):.6f} s")

print("\nTum zamanli arama kontrolleri basarili!")