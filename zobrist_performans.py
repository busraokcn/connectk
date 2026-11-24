import random
import time
import csv

from game import Game
from zobrist import ZobristHash


SEED = 27
GAME_COUNT = 10
REPEAT = 100


print("CONNECT-K ARENA - ZOBRIST PERFORMANSI")

results = []


# Dort varyantta da test yap
for variant in range(4):

    game = Game(d=27, V=variant)

    zobrist = ZobristHash(game, seed=SEED)

    rng = random.Random(SEED)

    transitions = []

    correct = 0

    # Rastgele oyunlar olustur
    for _ in range(GAME_COUNT):

        state = game.initial_state()

        key = zobrist.hash_state(state)

        while not game.is_terminal(state):

            move = rng.choice(
                game.actions(state)
            )

            child = game.result(state, move)

            incremental_key = zobrist.update_hash(
                key, child
            )

            full_key = zobrist.hash_state(child)

            assert incremental_key == full_key

            transitions.append(
                (key, child)
            )

            correct += 1

            state = child

            key = incremental_key

    # Olcumden once isinma
    for parent_key, child in transitions:

        zobrist.hash_state(child)

        zobrist.update_hash(
            parent_key, child
        )

    # ======================================
    # TAM HASH SURESI
    # ======================================

    start = time.perf_counter_ns()

    for _ in range(REPEAT):

        for parent_key, child in transitions:

            zobrist.hash_state(child)

    full_elapsed = (
        time.perf_counter_ns() - start
    )

    # ======================================
    # ARTIMLI HASH SURESI
    # ======================================

    start = time.perf_counter_ns()

    for _ in range(REPEAT):

        for parent_key, child in transitions:

            zobrist.update_hash(
                parent_key, child
            )

    incremental_elapsed = (
        time.perf_counter_ns() - start
    )

    calls = len(transitions) * REPEAT

    full_us = full_elapsed / calls / 1000

    incremental_us = (
        incremental_elapsed / calls / 1000
    )

    speedup = full_us / incremental_us

    print("\n" + "=" * 50)

    print("Varyant:", variant)

    print("Rastgele oyun:", GAME_COUNT)

    print("Kontrol edilen hamle:", correct)

    print(
        "Dogruluk:",
        f"{correct}/{len(transitions)}"
    )

    print("Her yontem icin cagri:", calls)

    print(
        f"Tam hash suresi: {full_us:.6f} us"
    )

    print(
        f"Artimli hash suresi: "
        f"{incremental_us:.6f} us"
    )

    print(
        f"Hizlanma katsayisi: {speedup:.3f} kat"
    )

    results.append({
        "Varyant": variant,
        "Oyun Sayisi": GAME_COUNT,
        "Kontrol Edilen Hamle": correct,
        "Cagri Sayisi": calls,
        "Tam Hash (us)": round(full_us, 6),
        "Artimli Hash (us)": round(
            incremental_us, 6
        ),
        "Hizlanma": round(speedup, 3)
    })


# Sonuclari dosyaya kaydet
with open(
    "zobrist_performans.csv",
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

print("Toplam rastgele oyun:", GAME_COUNT * 4)

print(
    "Toplam dogrulanan hamle:",
    sum(
        row["Kontrol Edilen Hamle"]
        for row in results
    )
)

print(
    "Her yontem icin toplam olcum:",
    sum(
        row["Cagri Sayisi"]
        for row in results
    )
)

print("\nSonuclar zobrist_performans.csv dosyasina kaydedildi.")

print("Tum artimli hash kontrolleri basarili!")