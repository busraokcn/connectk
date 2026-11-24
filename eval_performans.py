import json
import csv
import time
import statistics

from game import Game, state_from_moves
from agirliklar import WEIGHT_SETS, create_evaluator


REPEAT = 100

game = Game(d=27)


# Daha once olusturulan 50 konumu oku
with open(
    "rastgele_konumlar.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


positions = data["positions"]

assert len(positions) == 50

states = [
    state_from_moves(game, moves)
    for moves in positions
]

results = []


print("CONNECT-K ARENA - EVAL PERFORMANS TESTI")
print("Konum sayisi:", len(states))
print("Tekrar sayisi:", REPEAT)


for name in WEIGHT_SETS:

    evaluator = create_evaluator(game, name)

    mirror_correct = 0
    rotation_equal = 0
    rotation_changed = 0

    print("\n" + "=" * 50)
    print("AGIRLIK:", name)

    # ======================================
    # AYNA SIMETRISI VE DONME KONTROLU
    # ======================================

    for moves, state in zip(positions, states):

        original = evaluator.evaluate(state)

        # Sol-sag ayna simetrisi
        mirror_moves = [
            game.C - 1 - col
            for col in moves
        ]

        mirrored = state_from_moves(
            game, mirror_moves
        )

        mirror_value = evaluator.evaluate(mirrored)

        assert abs(original - mirror_value) < 1e-12

        mirror_correct += 1

        # Silindir tahtayi bir sutun dondur
        rotated_moves = [
            (col + 1) % game.C
            for col in moves
        ]

        rotated = state_from_moves(
            game, rotated_moves
        )

        rotation_value = evaluator.evaluate(rotated)

        # Temel oznitelikler degismemeli
        original_features = evaluator.features(state)

        rotated_features = evaluator.features(rotated)

        for key in (
            "max_k1",
            "max_k2",
            "min_k1",
            "min_k2"
        ):

            assert (
                original_features[key]
                == rotated_features[key]
            )

        # Sarmali ek agirlik sonucu degistirebilir
        if abs(original - rotation_value) < 1e-12:

            rotation_equal += 1

        else:

            rotation_changed += 1

    # ======================================
    # EVAL CALISMA SURESI
    # ======================================

    # Olcumden once isinma turu
    for state in states:

        evaluator.evaluate(state)

    timings = []

    for _ in range(REPEAT):

        start = time.perf_counter_ns()

        for state in states:

            evaluator.evaluate(state)

        elapsed = time.perf_counter_ns() - start

        # Bir Eval cagrisinin mikrosaniye cinsinden suresi
        average_us = elapsed / len(states) / 1000

        timings.append(average_us)

    avg_us = statistics.mean(timings)

    median_us = statistics.median(timings)

    total_calls = len(states) * REPEAT

    print("Toplam Eval cagrisi:", total_calls)

    print(
        "Ayna simetrisi:",
        f"{mirror_correct}/50"
    )

    print(
        "Donmede ayni kalan:",
        rotation_equal
    )

    print(
        "Donmede degisen:",
        rotation_changed
    )

    print(
        f"Ortalama Eval suresi: {avg_us:.3f} us"
    )

    print(
        f"Medyan Eval suresi: {median_us:.3f} us"
    )

    print(
        f"En dusuk tur ortalamasi: {min(timings):.3f} us"
    )

    print(
        f"En yuksek tur ortalamasi: {max(timings):.3f} us"
    )

    results.append({
        "Agirlik": name,
        "Konum Sayisi": len(states),
        "Tekrar": REPEAT,
        "Eval Cagrisi": total_calls,
        "Ortalama Sure (us)": round(avg_us, 3),
        "Medyan Sure (us)": round(median_us, 3),
        "Minimum Tur Ortalamasi (us)": round(
            min(timings), 3
        ),
        "Maksimum Tur Ortalamasi (us)": round(
            max(timings), 3
        ),
        "Ayna Simetrisi": mirror_correct,
        "Donmede Ayni": rotation_equal,
        "Donmede Degisen": rotation_changed
    })


# Sonuclari CSV dosyasina kaydet
with open(
    "eval_performans.csv",
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


print("\n" + "=" * 50)
print("GENEL SONUCLAR")

print(
    "Toplam olculen Eval cagrisi:",
    sum(row["Eval Cagrisi"] for row in results)
)

print(
    "Toplam ayna simetrisi kontrolu:",
    sum(row["Ayna Simetrisi"] for row in results)
)

print("\nSonuclar eval_performans.csv dosyasina kaydedildi.")

print("Tum Eval performans kontrolleri basarili!")