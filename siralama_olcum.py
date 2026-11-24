import json
import csv
import time
import statistics

from game import Game, MAX, state_from_moves
from search import Minimax, AlphaBeta


DEPTH = 6


# Hamle siralamasi icin harcanan sureyi olcen sinif
class MeasuredAlphaBeta(AlphaBeta):

    def __init__(self, game, order):
        super().__init__(game, order)
        self.order_time = 0
        self.order_calls = 0

    def ordered_actions(self, state):

        start = time.perf_counter_ns()

        actions = super().ordered_actions(state)

        self.order_time += (
            time.perf_counter_ns() - start
        )

        self.order_calls += 1

        return actions

    def choose_move(self, state, depth):

        self.order_time = 0
        self.order_calls = 0

        return super().choose_move(state, depth)


# Rastgele konumlari JSON dosyasindan oku
with open(
    "rastgele_konumlar.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


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

algorithms = {
    "A": MeasuredAlphaBeta(game, "A"),
    "B": MeasuredAlphaBeta(game, "B"),
    "C": MeasuredAlphaBeta(game, "C")
}

results = []
errors = []


print("CONNECT-K ARENA - SIRALAMA OLCUMLERI")
print("Seed:", data["seed"])
print("Konum sayisi:", len(positions))
print("Derinlik:", DEPTH)


# 50 konumun tamamini incele
for index, moves in enumerate(positions, start=1):

    state = state_from_moves(game, moves)

    assert not game.is_terminal(state)

    # Minimax referans olcumu
    start = time.perf_counter()

    mm_move, mm_value, mm_nodes = (
        minimax.choose_move(state, DEPTH)
    )

    mm_time = (time.perf_counter() - start) * 1000

    print(f"\nKONUM {index:02d}")
    print("Minimax degeri:", mm_value)
    print("Minimax dugum:", mm_nodes)

    # Ayni hamlenin gercek degerini tekrar hesaplamamak icin
    exact_values = {}

    # Uc farkli siralama yontemini calistir
    for method, algorithm in algorithms.items():

        start = time.perf_counter()

        move, value, nodes = algorithm.choose_move(
            state, DEPTH
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        # Nanosaniyeyi milisaniyeye cevir
        order_ms = algorithm.order_time / 1_000_000

        # Dugum azalmasi
        reduction = (
            1 - nodes / mm_nodes
        ) * 100

        legal = move in game.actions(state)

        exact_value = None

        # Secilen hamleyi duz Minimax ile dogrula
        if legal:

            if move not in exact_values:

                child = game.result(state, move)

                minimax.nodes = 0

                if state.player == MAX:

                    exact_values[move] = (
                        minimax.min_value(
                            child, DEPTH - 1
                        )
                    )

                else:

                    exact_values[move] = (
                        minimax.max_value(
                            child, DEPTH - 1
                        )
                    )

            exact_value = exact_values[move]

        success = (
            value == mm_value
            and nodes <= mm_nodes
            and legal
            and exact_value == mm_value
        )

        status = "OK" if success else "HATA"

        if not success:
            errors.append((index, method))

        print(
            f"Yontem {method} | "
            f"Hamle: {move} | "
            f"Deger: {value} | "
            f"Dugum: {nodes} | "
            f"Sure: {elapsed:.3f} ms | "
            f"Siralama: {order_ms:.3f} ms | "
            f"{status}"
        )

        # Sonuclari kaydet
        results.append({
            "Konum": index,
            "Hamle Dizisi": " ".join(map(str, moves)),
            "Yontem": method,
            "Derinlik": DEPTH,
            "Secilen Hamle": move,
            "Minimax Deger": mm_value,
            "AlphaBeta Deger": value,
            "Gercek Hamle Degeri": exact_value,
            "Minimax Dugum": mm_nodes,
            "AlphaBeta Dugum": nodes,
            "Minimax Sure (ms)": round(mm_time, 3),
            "AlphaBeta Sure (ms)": round(elapsed, 3),
            "Siralama Sure (ms)": round(order_ms, 3),
            "Siralama Cagrisi": algorithm.order_calls,
            "Dugum Azalmasi (%)": round(reduction, 2),
            "Sonuc": status
        })


# Tum sonuclari CSV dosyasina kaydet
with open(
    "siralama_sonuclar.csv",
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


# Genel sonuclari hesapla
summary = []

print("\n" + "=" * 65)
print("GENEL KARSILASTIRMA")
print("=" * 65)

for method in ("A", "B", "C"):

    rows = [
        row for row in results
        if row["Yontem"] == method
    ]

    avg_nodes = statistics.mean(
        row["AlphaBeta Dugum"] for row in rows
    )

    avg_time = statistics.mean(
        row["AlphaBeta Sure (ms)"] for row in rows
    )

    avg_order = statistics.mean(
        row["Siralama Sure (ms)"] for row in rows
    )

    avg_reduction = statistics.mean(
        row["Dugum Azalmasi (%)"] for row in rows
    )

    correct = sum(
        row["Sonuc"] == "OK" for row in rows
    )

    # En az budama yapilan konumu bul
    worst = min(
        rows,
        key=lambda row: row["Dugum Azalmasi (%)"]
    )

    print(f"\nYONTEM {method}")
    print("Dogruluk:", f"{correct}/50")
    print(f"Ortalama dugum: {avg_nodes:.2f}")
    print(f"Ortalama sure: {avg_time:.3f} ms")
    print(f"Ortalama siralama suresi: {avg_order:.3f} ms")
    print(f"Ortalama dugum azalmasi: %{avg_reduction:.2f}")

    print(
        "En az budama yapilan konum:",
        worst["Konum"]
    )

    print(
        "Bu konumdaki dugum azalmasi:",
        f"%{worst['Dugum Azalmasi (%)']:.2f}"
    )

    summary.append({
        "Yontem": method,
        "Dogruluk": correct,
        "Ortalama Dugum": round(avg_nodes, 2),
        "Ortalama Sure (ms)": round(avg_time, 3),
        "Ortalama Siralama Sure (ms)": round(avg_order, 3),
        "Ortalama Dugum Azalmasi (%)": round(
            avg_reduction, 2
        ),
        "En Az Budama Konumu": worst["Konum"],
        "En Az Budama (%)": worst["Dugum Azalmasi (%)"]
    })


# Ozet sonuclari ayri CSV dosyasina kaydet
with open(
    "siralama_ozet.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=list(summary[0].keys())
    )

    writer.writeheader()
    writer.writerows(summary)


# En iyi yontemleri belirle
best_nodes = min(
    summary,
    key=lambda row: row["Ortalama Dugum"]
)

best_time = min(
    summary,
    key=lambda row: row["Ortalama Sure (ms)"]
)


print("\n" + "=" * 65)
print("SONUC")
print("=" * 65)

print("Toplam AlphaBeta olcumu:", len(results))
print("Hatali olcum sayisi:", len(errors))

print(
    "En az dugum ziyaret eden yontem:",
    best_nodes["Yontem"]
)

print(
    "En hizli yontem:",
    best_time["Yontem"]
)

print("\nOlusturulan dosyalar:")
print("siralama_sonuclar.csv")
print("siralama_ozet.csv")

assert len(results) == 150

if errors:

    print("Hatali konum ve yontemler:", errors)

    raise AssertionError(
        "Siralama dogruluk testinde hata bulundu"
    )

print("\nTum 150 siralama olcumu basarili!")