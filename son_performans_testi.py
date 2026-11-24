import json
import csv
import time
import random

from statistics import mean

from game import Game, state_from_moves
from tt_search import TTAlphaBeta
from threat_search import ThreatAlphaBeta
from agirliklar import create_evaluator


SEED = 27
TIME_LIMIT = 1.0

game = Game(d=27)

positions = []


# ==========================================
# ONCEKI 10 RASTGELE KONUM
# ==========================================

with open(
    "rastgele_konumlar.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


for index, moves in enumerate(
    data["positions"][:10], start=1
):

    positions.append((
        f"Rastgele {index}",
        game,
        moves
    ))


# ==========================================
# UFUK ETKISI KONUMU
# ==========================================

with open(
    "ufuk_etkisi_ornek.json",
    "r",
    encoding="utf-8"
) as file:

    example = json.load(file)


positions.append((
    "Ufuk etkisi",
    game,
    example["moves"]
))


# ==========================================
# DORT FARKLI VARYANT
# ==========================================

for variant in range(4):

    variant_game = Game(
        d=27,
        R=7,
        C=8,
        K=5,
        V=variant
    )

    rng = random.Random(SEED)

    state = variant_game.initial_state()

    moves = []

    for _ in range(8):

        if variant_game.is_terminal(state):
            break

        move = rng.choice(
            variant_game.actions(state)
        )

        state = variant_game.result(
            state, move
        )

        moves.append(move)

    assert not variant_game.is_terminal(state)

    positions.append((
        f"7x8 Varyant {variant}",
        variant_game,
        moves
    ))


assert len(positions) == 15


# ==========================================
# PERFORMANS DENEYI
# ==========================================

print("CONNECT-K ARENA - SON PERFORMANS TESTI")

print("Konum sayisi:", len(positions))
print("Sure siniri:", TIME_LIMIT)
print("Agirlik: W3")
print("Kontrol araligi: 100 dugum")

results = []


for index, (name, current_game, moves) in enumerate(
    positions, start=1
):

    state = state_from_moves(
        current_game, moves
    )

    assert not current_game.is_terminal(state)

    evaluator = create_evaluator(
        current_game, "W3"
    )

    print("\n" + "=" * 60)

    print("KONUM:", index, "-", name)

    print(
        "Parametreler:",
        current_game.R,
        current_game.C,
        current_game.K,
        current_game.V
    )

    print("Hamleler:", moves)

    current_game.print_board(state)

    methods = [
        ("Normal TT", TTAlphaBeta),
        ("Tehdit Uzatma", ThreatAlphaBeta)
    ]

    # Calistirma sirasi etkisini azalt
    if index % 2 == 0:

        methods.reverse()

    for method_name, agent_class in methods:

        agent = agent_class(
            current_game,
            order="A",
            evaluator=evaluator,
            use_tt=True,
            seed=SEED,
            check_interval=100
        )

        start = time.perf_counter()

        result = agent.choose_move_timed(
            state,
            time_limit=TIME_LIMIT
        )

        elapsed = time.perf_counter() - start

        # Yasal hamle kontrolu
        legal = (
            result.move
            in current_game.actions(state)
        )

        # Son tamamlanan iterasyon kontrolu
        history_ok = True

        if result.history:

            last = result.history[-1]

            history_ok = (
                result.move == last.move
                and result.value == last.value
                and result.depth == last.depth
            )

        else:

            history_ok = (
                result.depth == 0
                and result.value is None
            )

        # Onceki en iyi hamle ilk sirada olmali
        ordering_ok = all(
            current.first_move == previous.move

            for previous, current in zip(
                result.history,
                result.history[1:]
            )
        )

        completed_nodes = sum(
            item.nodes
            for item in result.history
        )

        node_ok = (
            result.nodes >= completed_nodes
        )

        time_ok = elapsed <= TIME_LIMIT

        extensions = getattr(
            agent, "extensions", 0
        )

        extension_nodes = getattr(
            agent, "extension_nodes", 0
        )

        success = (
            legal
            and history_ok
            and ordering_ok
            and node_ok
            and time_ok
        )

        print("\nYONTEM:", method_name)

        print("Secilen hamle:", result.move)
        print("Derinlik:", result.depth)
        print("Arama degeri:", result.value)
        print("Dugum:", result.nodes)
        print("TT hit:", agent.tt_hits)
        print("TT cutoff:", agent.tt_cutoffs)
        print("Uzatma:", extensions)
        print("Ek dugum:", extension_nodes)

        print(f"Gercek sure: {elapsed:.6f} s")

        print("Sure doldu:", result.timed_out)

        print("Yasal hamle:", legal)
        print("Son iterasyon:", history_ok)
        print("Hamle siralamasi:", ordering_ok)

        print(
            "Sonuc:",
            "BASARILI" if success else "BASARISIZ"
        )

        results.append({
            "Konum": index,
            "Konum Adi": name,
            "R": current_game.R,
            "C": current_game.C,
            "K": current_game.K,
            "V": current_game.V,
            "Hamle Dizisi": " ".join(map(str, moves)),
            "Yontem": method_name,
            "Hamle": result.move,
            "Derinlik": result.depth,
            "Deger": result.value,
            "Dugum": result.nodes,
            "TT Hit": agent.tt_hits,
            "TT Cutoff": agent.tt_cutoffs,
            "Uzatma": extensions,
            "Ek Dugum": extension_nodes,
            "Sure (s)": elapsed,
            "Sure Doldu": result.timed_out,
            "Yasal Hamle": legal,
            "Son Iterasyon": history_ok,
            "Hamle Siralamasi": ordering_ok,
            "Dugum Kontrolu": node_ok,
            "Zaman Kontrolu": time_ok,
            "Sonuc": (
                "BASARILI" if success
                else "BASARISIZ"
            )
        })


# ==========================================
# DETAYLI SONUCLARI KAYDET
# ==========================================

with open(
    "son_performans_sonuclar.csv",
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
# GENEL SONUCLAR
# ==========================================

summary = []

print("\n" + "=" * 60)

print("GENEL SONUCLAR")


for method in (
    "Normal TT",
    "Tehdit Uzatma"
):

    rows = [
        row for row in results
        if row["Yontem"] == method
    ]

    successful = sum(
        row["Sonuc"] == "BASARILI"
        for row in rows
    )

    time_success = sum(
        row["Zaman Kontrolu"]
        for row in rows
    )

    avg_depth = mean(
        row["Derinlik"] for row in rows
    )

    avg_nodes = mean(
        row["Dugum"] for row in rows
    )

    avg_time = mean(
        row["Sure (s)"] for row in rows
    )

    max_time = max(
        row["Sure (s)"] for row in rows
    )

    avg_extensions = mean(
        row["Uzatma"] for row in rows
    )

    print("\nYONTEM:", method)

    print(
        "Basarili konum:",
        f"{successful}/{len(rows)}"
    )

    print(
        "Zaman basarisi:",
        f"{time_success}/{len(rows)}"
    )

    print(f"Ortalama derinlik: {avg_depth:.3f}")

    print(f"Ortalama dugum: {avg_nodes:.2f}")

    print(f"Ortalama sure: {avg_time:.6f} s")

    print(f"En uzun sure: {max_time:.6f} s")

    print(
        f"Ortalama uzatma: {avg_extensions:.2f}"
    )

    summary.append({
        "Yontem": method,
        "Konum Sayisi": len(rows),
        "Basarili Konum": successful,
        "Zaman Basarisi": time_success,
        "Ortalama Derinlik": round(avg_depth, 3),
        "Ortalama Dugum": round(avg_nodes, 2),
        "Ortalama Sure (s)": round(avg_time, 6),
        "En Uzun Sure (s)": round(max_time, 6),
        "Ortalama Uzatma": round(avg_extensions, 2)
    })


with open(
    "son_performans_ozet.csv",
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
    row["Sonuc"] == "BASARISIZ"
    for row in results
)

time_failures = sum(
    not row["Zaman Kontrolu"]
    for row in results
)

print("\n" + "=" * 60)

print("TOPLAM SONUCLAR")

print("Toplam arama:", len(results))
print("Basarisiz arama:", failures)
print("Zaman sinirini asan:", time_failures)

print(
    f"En uzun genel sure: "
    f"{max(row['Sure (s)'] for row in results):.6f} s"
)

print("\nOlusturulan dosyalar:")

print("son_performans_sonuclar.csv")
print("son_performans_ozet.csv")

assert len(results) == 30

assert failures == 0, (
    "En az bir son kontrol basarisiz oldu"
)

print("\nTum son performans kontrolleri basarili!")