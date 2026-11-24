import json
import csv
import math
import time

from statistics import mean

from game import Game, MAX, state_from_moves
from search import Minimax
from tt_search import TTAlphaBeta
from agirliklar import create_evaluator


DEPTH = 6

game = Game(d=27)


# Asama 2'deki rastgele konumlari oku
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

for state in states:

    assert not game.is_terminal(state)


# Eski ve yeni degerlendirme secenekleri
evaluators = {
    "Eski Eval": None,
    "W3 Eval": create_evaluator(game, "W3")
}

results = []


print("CONNECT-K ARENA - TT DOGRULUK TESTI")

print("Konum sayisi:", len(states))
print("Derinlik:", DEPTH)


for eval_name, evaluator in evaluators.items():

    reference = Minimax(
        game,
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

    print("\n" + "=" * 60)
    print("DEGERLENDIRME:", eval_name)

    for index, state in enumerate(states, start=1):

        # Minimax referans sonucu
        ref_move, ref_value, ref_nodes = (
            reference.choose_move(state, DEPTH)
        )

        # TT kapali
        start = time.perf_counter()

        off_move, off_value, off_nodes = (
            tt_off.choose_move(state, DEPTH)
        )

        off_ms = (
            time.perf_counter() - start
        ) * 1000

        # TT acik
        start = time.perf_counter()

        on_move, on_value, on_nodes = (
            tt_on.choose_move(state, DEPTH)
        )

        on_ms = (
            time.perf_counter() - start
        ) * 1000

        # Kok degerleri ayni olmali
        assert ref_value == off_value == on_value, (
            f"Kok degeri hatasi: {eval_name}, "
            f"konum {index}"
        )

        # Secilen hamleler yasal olmali
        assert off_move in game.actions(state)
        assert on_move in game.actions(state)

        # TT kapaliyken tablo kullanilmamali
        assert len(tt_off.tt) == 0
        assert tt_off.tt_hits == 0

        # Her iki ajanin hamlesini
        # Minimax ile bagimsiz dogrula
        for move in {off_move, on_move}:

            child = game.result(state, move)

            if state.player == MAX:

                exact = reference.min_value(
                    child,
                    DEPTH - 1
                )

            else:

                exact = reference.max_value(
                    child,
                    DEPTH - 1
                )

            assert exact == ref_value, (
                f"Hamle degeri hatasi: "
                f"{eval_name}, konum {index}"
            )

        assert off_nodes <= ref_nodes
        assert on_nodes <= ref_nodes

        reduction = (
            1 - on_nodes / off_nodes
        ) * 100

        results.append({
            "Degerlendirme": eval_name,
            "Konum": index,
            "Hamle Dizisi": " ".join(
                map(str, positions[index - 1])
            ),
            "Derinlik": DEPTH,
            "Minimax Hamle": ref_move,
            "Minimax Deger": ref_value,
            "Minimax Dugum": ref_nodes,
            "TT Kapali Hamle": off_move,
            "TT Kapali Deger": off_value,
            "TT Kapali Dugum": off_nodes,
            "TT Kapali Sure (ms)": round(off_ms, 6),
            "TT Acik Hamle": on_move,
            "TT Acik Deger": on_value,
            "TT Acik Dugum": on_nodes,
            "TT Acik Sure (ms)": round(on_ms, 6),
            "TT Hit": tt_on.tt_hits,
            "TT Cutoff": tt_on.tt_cutoffs,
            "TT Boyutu": len(tt_on.tt),
            "Dugum Azalmasi (%)": round(reduction, 4),
            "Sonuc": "BASARILI"
        })

        print(
            f"Konum {index:02d}/50 | "
            f"Minimax: {ref_value:.6f} | "
            f"TT kapali: {off_value:.6f} | "
            f"TT acik: {on_value:.6f} | "
            f"Azalma: %{reduction:.2f} | "
            f"BASARILI",
            flush=True
        )


# ==========================================
# CSV DOSYASINA KAYDET
# ==========================================

with open(
    "tt_dogruluk_sonuclar.csv",
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

print("\n" + "=" * 60)

print("GENEL DOGRULUK SONUCLARI")


for eval_name in evaluators:

    rows = [
        row for row in results
        if row["Degerlendirme"] == eval_name
    ]

    print("\nDEGERLENDIRME:", eval_name)

    print("Basarili konum:", len(rows), "/ 50")

    print(
        "Ortalama Minimax dugum:",
        round(
            mean(row["Minimax Dugum"] for row in rows),
            2
        )
    )

    print(
        "Ortalama TT kapali dugum:",
        round(
            mean(row["TT Kapali Dugum"] for row in rows),
            2
        )
    )

    print(
        "Ortalama TT acik dugum:",
        round(
            mean(row["TT Acik Dugum"] for row in rows),
            2
        )
    )

    print(
        "Ortalama TT kapali sure (ms):",
        round(
            mean(
                row["TT Kapali Sure (ms)"]
                for row in rows
            ),
            3
        )
    )

    print(
        "Ortalama TT acik sure (ms):",
        round(
            mean(
                row["TT Acik Sure (ms)"]
                for row in rows
            ),
            3
        )
    )

    print(
        "Ortalama dugum azalmasi (%):",
        round(
            mean(
                row["Dugum Azalmasi (%)"]
                for row in rows
            ),
            2
        )
    )

    print(
        "Toplam TT hit:",
        sum(row["TT Hit"] for row in rows)
    )

    print(
        "Toplam TT cutoff:",
        sum(row["TT Cutoff"] for row in rows)
    )


assert len(results) == 100

print("\nToplam dogrulama: 100/100")
print("Hatali sonuc: 0")

print("\nSonuclar tt_dogruluk_sonuclar.csv dosyasina kaydedildi.")

print("Tum TT dogruluk kontrolleri basarili!")