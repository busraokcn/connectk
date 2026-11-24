import time
import csv

from game import Game, state_from_moves
from search import Minimax


# Oyun ve Minimax nesnesi
game = Game(d=27)
minimax = Minimax(game)


# Ölçüm yapılacak oyun konumları
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


# Arama derinlikleri
depths = [2, 4, 6]

# Ölçüm sonuçlarını saklayacağımız liste
results = []


print("CONNECT-K ARENA - MINIMAX OLCUMLERI")
print("R:", game.R)
print("C:", game.C)
print("K:", game.K)
print("V:", game.V)


# Her konum için ölçüm yap
for name, moves in positions.items():

    state = state_from_moves(game, moves)

    print("\nKONUM:", name)
    game.print_board(state)

    print(
        f"{'Derinlik':<10}"
        f"{'Hamle':<8}"
        f"{'Deger':<8}"
        f"{'Dugum':<12}"
        f"{'Sure(ms)':<12}"
        f"{'b_etkin':<10}"
    )

    print("-" * 60)

    for depth in depths:

        start = time.perf_counter()

        move, value, nodes = minimax.choose_move(
            state, depth
        )

        end = time.perf_counter()

        elapsed = (end - start) * 1000

        # Etkin dallanma çarpanı
        b_effective = nodes ** (1 / depth)

        # Seçilen hamle yasal mı?
        assert move in game.actions(state)

        print(
            f"{depth:<10}"
            f"{move:<8}"
            f"{value:<8}"
            f"{nodes:<12}"
            f"{elapsed:<12.3f}"
            f"{b_effective:<10.3f}"
        )

        # Sonuçları listeye ekle
        results.append([
            name,
            depth,
            move,
            value,
            nodes,
            round(elapsed, 3),
            round(b_effective, 3)
        ])


# Ölçümleri CSV dosyasına kaydet
with open(
    "minimax_sonuclar.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Konum",
        "Derinlik",
        "Hamle",
        "Minimax Degeri",
        "Dugum Sayisi",
        "Sure (ms)",
        "Etkin Dallanma Carpani"
    ])

    writer.writerows(results)


print("\nToplam olcum sayisi:", len(results))

assert len(results) == 15

print("Sonuclar minimax_sonuclar.csv dosyasina kaydedildi.")
print("Tum Minimax olcumleri tamamlandi!")