import json
import csv
import time

from statistics import mean

from game import Game, state_from_moves
from tt_search import TTAlphaBeta
from agirliklar import create_evaluator


TIME_LIMIT = 1.0
POSITION_COUNT = 10

game = Game(d=27)

evaluator = create_evaluator(game, "W3")


# Daha once uretilen konumlari oku
with open(
    "rastgele_konumlar.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


positions = data["positions"][:POSITION_COUNT]

assert len(positions) == POSITION_COUNT

results = []


print("CONNECT-K ARENA - TT PERFORMANS TESTI")

print("Konum sayisi:", POSITION_COUNT)
print("Sure siniri:", TIME_LIMIT)
print("Agirlik: W3")
print("Siralama: A")


for index, moves in enumerate(positions, start=1):

    state = state_from_moves(game, moves)

    assert not game.is_terminal(state)

    print("\n" + "=" * 60)

    print("KONUM:", index)
    print("Hamleler:", moves)

    game.print_board(state)

    # Calistirma sirasi etkisini azaltmak icin
    # her ikinci konumda TT acik once calisir.
    modes = (
        [False, True]
        if index % 2 == 1
        else [True, False]
    )

    for enabled in modes:

        mode_name = (
            "ACIK" if enabled else "KAPALI"
        )

        agent = TTAlphaBeta(
            game,
            order="A",
            evaluator=evaluator,
            check_interval=1000,
            seed=27,
            use_tt=enabled
        )

        # Gercek toplam arama suresini olc
        start = time.perf_counter()

        result = agent.choose_move_timed(
            state,
            time_limit=TIME_LIMIT
        )

        elapsed = time.perf_counter() - start

        # Yasal hamle kontrolu
        assert result.move in game.actions(state)

        # Son tamamlanan iterasyonu kontrol et
        if result.history:

            last = result.history[-1]

            assert result.depth == last.depth
            assert result.move == last.move
            assert result.value == last.value

        else:

            assert result.depth == 0

        # Tamamlanan iterasyonlarin dugumleri
        completed_nodes = sum(
            item.nodes
            for item in result.history
        )

        assert result.nodes >= completed_nodes

        # Onceki iyi hamle ilk sirada olmali
        for previous, current in zip(
            result.history,
            result.history[1:]
        ):

            assert current.first_move == previous.move

        time_ok = elapsed <= TIME_LIMIT

        if not enabled:

            assert len(agent.tt) == 0
            assert agent.tt_hits == 0

        results.append({
            "Konum": index,
            "Hamle Dizisi": " ".join(map(str, moves)),
            "TT": mode_name,
            "Derinlik": result.depth,
            "Secilen Hamle": result.move,
            "Arama Degeri": result.value,
            "Toplam Dugum": result.nodes,
            "Tamamlanan Dugum": completed_nodes,
            "Yarim Kalan Dugum": (
                result.nodes - completed_nodes
            ),
            "Sure (s)": round(elapsed, 9),
            "TT Hit": agent.tt_hits,
            "TT Cutoff": agent.tt_cutoffs,
            "TT Kayit": agent.tt_stores,
            "TT Boyutu": len(agent.tt),
            "Sure Doldu": result.timed_out,
            "Zaman Kontrolu": (
                "BASARILI" if time_ok else "BASARISIZ"
            )
        })

        print(
            f"\nTT {mode_name} | "
            f"Derinlik: {result.depth} | "
            f"Hamle: {result.move} | "
            f"Dugum: {result.nodes} | "
            f"Sure: {elapsed:.6f} s | "
            f"Hit: {agent.tt_hits} | "
            f"Cutoff: {agent.tt_cutoffs}",
            flush=True
        )

        print(
            "Zaman kontrolu:",
            "BASARILI" if time_ok else "BASARISIZ"
        )


# ==========================================
# DETAYLI SONUCLARI KAYDET
# ==========================================

with open(
    "tt_performans_sonuclar.csv",
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


# ==========================================
# OZET TABLO
# ==========================================

summary = []

print("\n" + "=" * 60)
print("GENEL PERFORMANS SONUCLARI")


for mode in ("KAPALI", "ACIK"):

    rows = [
        row for row in results
        if row["TT"] == mode
    ]

    assert len(rows) == POSITION_COUNT

    avg_depth = mean(
        row["Derinlik"]
        for row in rows
    )

    avg_nodes = mean(
        row["Toplam Dugum"]
        for row in rows
    )

    avg_time = mean(
        row["Sure (s)"]
        for row in rows
    )

    max_time = max(
        row["Sure (s)"]
        for row in rows
    )

    success = sum(
        row["Zaman Kontrolu"] == "BASARILI"
        for row in rows
    )

    summary.append({
        "TT": mode,
        "Konum Sayisi": len(rows),
        "Ortalama Derinlik": round(avg_depth, 2),
        "Ortalama Dugum": round(avg_nodes, 2),
        "Ortalama Sure (s)": round(avg_time, 6),
        "En Uzun Sure (s)": round(max_time, 6),
        "Zaman Basarisi": success,
        "Toplam TT Hit": sum(
            row["TT Hit"] for row in rows
        ),
        "Toplam TT Cutoff": sum(
            row["TT Cutoff"] for row in rows
        )
    })

    print("\nTT", mode)

    print("Ortalama derinlik:", avg_depth)

    print(f"Ortalama dugum: {avg_nodes:.2f}")

    print(f"Ortalama sure: {avg_time:.6f} s")

    print(f"En uzun sure: {max_time:.6f} s")

    print(
        "Zaman basarisi:",
        f"{success}/{POSITION_COUNT}"
    )


# ==========================================
# KONUM BAZINDA DERINLIK KARSILASTIRMASI
# ==========================================

deeper = 0
equal = 0
shallower = 0

for index in range(1, POSITION_COUNT + 1):

    off = next(
        row for row in results
        if row["Konum"] == index
        and row["TT"] == "KAPALI"
    )

    on = next(
        row for row in results
        if row["Konum"] == index
        and row["TT"] == "ACIK"
    )

    if on["Derinlik"] > off["Derinlik"]:

        deeper += 1

    elif on["Derinlik"] == off["Derinlik"]:

        equal += 1

    else:

        shallower += 1


print("\nDERINLIK KARSILASTIRMASI")

print("TT acikken daha derin:", deeper)
print("Ayni derinlik:", equal)
print("TT acikken daha sig:", shallower)

depth_difference = (
    summary[1]["Ortalama Derinlik"]
    - summary[0]["Ortalama Derinlik"]
)

print(
    "Ortalama derinlik farki:",
    round(depth_difference, 2)
)


# Ozet CSV dosyasi
with open(
    "tt_performans_ozet.csv",
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


failures = sum(
    row["Zaman Kontrolu"] == "BASARISIZ"
    for row in results
)

print("\nTOPLAM SONUCLAR")

print("Toplam arama:", len(results))
print("Zaman sinirini asan:", failures)

print("\nOlusturulan dosyalar:")

print("tt_performans_sonuclar.csv")
print("tt_performans_ozet.csv")


assert len(results) == 20

assert failures == 0, (
    "En az bir arama 1 saniye sinirini asti"
)

print("\nTum TT performans kontrolleri basarili!")