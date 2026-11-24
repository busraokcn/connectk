import json
import csv
import time
import statistics

from game import Game, MAX, state_from_moves
from search import Minimax, AlphaBeta


DEPTH = 6

# Daha once olusturulan 50 konumu oku
with open(
    "rastgele_konumlar.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


# JSON dosyasindaki parametreleri kullan
game = Game(
    d=data["seed"],
    R=data["R"],
    C=data["C"],
    K=data["K"],
    V=data["V"]
)

positions = data["positions"]

assert len(positions) == 50

minimax = Minimax(game)
alphabeta = AlphaBeta(game)

results = []
errors = []

correct_count = 0
node_count_correct = 0
move_correct_count = 0


print("CONNECT-K ARENA - ALPHA BETA DOGRULUK TESTI")
print("Seed:", data["seed"])
print("Konum sayisi:", len(positions))
print("Arama derinligi:", DEPTH)

print()

print(
    f"{'Konum':<8}"
    f"{'MM Deger':<10}"
    f"{'AB Deger':<10}"
    f"{'MM Dugum':<12}"
    f"{'AB Dugum':<12}"
    f"{'Azalma %':<12}"
    f"{'Sonuc':<10}"
)

print("-" * 74)


# Her oyun konumu icin karsilastirma yap
for index, moves in enumerate(positions, start=1):

    state = state_from_moves(game, moves)

    assert not game.is_terminal(state)

    # MINIMAX OLCUMU
    start = time.perf_counter()

    mm_move, mm_value, mm_nodes = minimax.choose_move(
        state, DEPTH
    )

    mm_time = (time.perf_counter() - start) * 1000

    # ALPHA BETA OLCUMU
    start = time.perf_counter()

    ab_move, ab_value, ab_nodes = alphabeta.choose_move(
        state, DEPTH
    )

    ab_time = (time.perf_counter() - start) * 1000

    # Kok degerlerinin esitligi
    value_correct = mm_value == ab_value

    # Dugum sayisi kontrolu
    nodes_correct = ab_nodes <= mm_nodes

    # Secilen hamlenin yasalligi
    legal_move = ab_move in game.actions(state)

    exact_value = None

    # Alpha-beta hamlesini Minimax ile dogrula
    if legal_move:

        child = game.result(state, ab_move)

        minimax.nodes = 0

        if state.player == MAX:

            exact_value = minimax.min_value(
                child, DEPTH - 1
            )

        else:

            exact_value = minimax.max_value(
                child, DEPTH - 1
            )

    move_correct = (
        legal_move and exact_value == mm_value
    )

    # Basarili kontrolleri say
    if value_correct:
        correct_count += 1

    if nodes_correct:
        node_count_correct += 1

    if move_correct:
        move_correct_count += 1

    # Dugum azalmasini hesapla
    reduction = (
        1 - ab_nodes / mm_nodes
    ) * 100

    success = (
        value_correct
        and nodes_correct
        and move_correct
    )

    status = "OK" if success else "HATA"

    if not success:

        errors.append(index)

        print("\nHATALI KONUM:", index)
        print("Hamle dizisi:", moves)
        print("Gercek hamle degeri:", exact_value)
        game.print_board(state)

    print(
        f"{index:<8}"
        f"{mm_value:<10}"
        f"{ab_value:<10}"
        f"{mm_nodes:<12}"
        f"{ab_nodes:<12}"
        f"{reduction:<12.2f}"
        f"{status:<10}"
    )

    # Sonuclari kaydet
    results.append({
        "Konum": index,
        "Hamle Dizisi": " ".join(map(str, moves)),
        "Derinlik": DEPTH,
        "Minimax Hamle": mm_move,
        "AlphaBeta Hamle": ab_move,
        "Minimax Deger": mm_value,
        "AlphaBeta Deger": ab_value,
        "Minimax Dugum": mm_nodes,
        "AlphaBeta Dugum": ab_nodes,
        "Minimax Sure (ms)": round(mm_time, 3),
        "AlphaBeta Sure (ms)": round(ab_time, 3),
        "Dugum Azalmasi (%)": round(reduction, 2),
        "Gercek Hamle Degeri": exact_value,
        "Sonuc": status
    })


# CSV dosyasina kaydet
with open(
    "alphabeta_dogruluk.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=list(results[0].keys())
    )

    writer.writeheader()
    writer.writerows(results)


# Ortalama degerleri hesapla
avg_mm_nodes = statistics.mean(
    row["Minimax Dugum"] for row in results
)

avg_ab_nodes = statistics.mean(
    row["AlphaBeta Dugum"] for row in results
)

avg_mm_time = statistics.mean(
    row["Minimax Sure (ms)"] for row in results
)

avg_ab_time = statistics.mean(
    row["AlphaBeta Sure (ms)"] for row in results
)

avg_reduction = statistics.mean(
    row["Dugum Azalmasi (%)"] for row in results
)


# Genel sonuclari yazdir
print("\n" + "=" * 55)
print("GENEL SONUCLAR")
print("=" * 55)

print("Toplam konum:", len(positions))

print(
    "Kok degeri dogru:",
    f"{correct_count}/50"
)

print(
    "Dugum sayisi kontrolu:",
    f"{node_count_correct}/50"
)

print(
    "Secilen hamle dogru:",
    f"{move_correct_count}/50"
)

print("Hatali konum sayisi:", len(errors))

print(
    f"\nOrtalama Minimax dugum: {avg_mm_nodes:.2f}"
)

print(
    f"Ortalama AlphaBeta dugum: {avg_ab_nodes:.2f}"
)

print(
    f"Ortalama Minimax sure: {avg_mm_time:.3f} ms"
)

print(
    f"Ortalama AlphaBeta sure: {avg_ab_time:.3f} ms"
)

print(
    f"Ortalama dugum azalmasi: %{avg_reduction:.2f}"
)

print("\nSonuclar alphabeta_dogruluk.csv dosyasina kaydedildi.")


if errors:

    print("Hatali konumlar:", errors)

    raise AssertionError(
        "Dogruluk testlerinde hata bulundu"
    )

else:

    print("Tum 50 konumda dogruluk testi basarili!")