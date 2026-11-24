import random
import csv
import json
import time

from itertools import combinations

from game import Game, MAX, MIN, state_from_moves
from search import AlphaBeta

from agirliklar import (
    WEIGHT_SETS,
    SEED,
    DEPTH,
    create_evaluator
)


GAMES_PER_DIRECTION = 10
ORDER = "A"


# ==========================================
# RASTGELE BASLANGICLAR
# ==========================================

def generate_openings(game):

    rng = random.Random(SEED)

    openings = []
    seen = set()

    while len(openings) < GAMES_PER_DIRECTION:

        state = game.initial_state()

        moves = []

        # Ilk 2-4 hamle rastgele oynanir
        move_count = rng.randint(2, 4)

        for _ in range(move_count):

            if game.is_terminal(state):
                break

            action = rng.choice(game.actions(state))

            state = game.result(state, action)

            moves.append(action)

        if game.is_terminal(state):
            continue

        key = (state.board, state.player)

        if key in seen:
            continue

        seen.add(key)

        openings.append(moves)

    return openings


# ==========================================
# TEK OYUN OYNATMA
# ==========================================

def play_game(game, max_weight, min_weight, opening):

    state = state_from_moves(game, opening)

    moves = list(opening)

    agents = {
        MAX: AlphaBeta(
            game,
            order=ORDER,
            evaluator=create_evaluator(game, max_weight)
        ),

        MIN: AlphaBeta(
            game,
            order=ORDER,
            evaluator=create_evaluator(game, min_weight)
        )
    }

    total_nodes = 0
    ai_moves = 0

    start = time.perf_counter()

    # Oyun bitene kadar ajanlari oynat
    while not game.is_terminal(state):

        agent = agents[state.player]

        move, value, nodes = agent.choose_move(
            state, DEPTH
        )

        # Ajan yasal hamle secmeli
        assert move in game.actions(state)

        assert -1 <= value <= 1

        state = game.result(state, move)

        moves.append(move)

        total_nodes += nodes

        ai_moves += 1

        assert len(moves) <= game.R * game.C

    elapsed = time.perf_counter() - start

    utility = game.utility(state)

    # Kazanani belirle
    if utility == MAX:

        winner = max_weight

    elif utility == MIN:

        winner = min_weight

    else:

        winner = "BERABERE"

    # Hamle dizisinin tekrar oynatilabildigini kontrol et
    replay = state_from_moves(game, moves)

    assert replay == state
    assert game.is_terminal(replay)
    assert game.utility(replay) == utility

    return {
        "MAX": max_weight,
        "MIN": min_weight,
        "Baslangic": " ".join(map(str, opening)),
        "Hamle Dizisi": " ".join(map(str, moves)),
        "Kazanan": winner,
        "Utility": utility,
        "Toplam Hamle": len(moves),
        "AI Hamle": ai_moves,
        "Toplam Dugum": total_nodes,
        "Sure (s)": round(elapsed, 3)
    }


# ==========================================
# TURNUVA
# ==========================================

def run_tournament():

    game = Game(d=27)

    names = list(WEIGHT_SETS.keys())

    openings = generate_openings(game)

    assert len(openings) == 10

    # Baslangiclari JSON dosyasina kaydet
    with open(
        "turnuva_baslangiclari.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump({
            "seed": SEED,
            "depth": DEPTH,
            "order": ORDER,
            "R": game.R,
            "C": game.C,
            "K": game.K,
            "V": game.V,
            "openings": openings
        }, file, indent=4)

    # Galibiyet matrisi
    wins = {
        a: {b: 0 for b in names}
        for a in names
    }

    draws = {
        a: {b: 0 for b in names}
        for a in names
    }

    results = []

    game_number = 0

    print("CONNECT-K ARENA - AGIRLIK TURNUVASI")

    print("Seed:", SEED)
    print("Derinlik:", DEPTH)
    print("Siralama:", ORDER)

    print("\nRASTGELE BASLANGICLAR")

    for index, opening in enumerate(openings, start=1):

        print(f"Baslangic {index:02d}: {opening}")

    print("\nTURNUVA BASLADI\n")

    total_start = time.perf_counter()

    fields = [
        "Oyun",
        "Baslangic No",
        "MAX",
        "MIN",
        "Baslangic",
        "Hamle Dizisi",
        "Kazanan",
        "Utility",
        "Toplam Hamle",
        "AI Hamle",
        "Toplam Dugum",
        "Sure (s)"
    ]

    # Her tamamlanan oyunu hemen kaydet
    with open(
        "agirlik_turnuvasi_sonuclar.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        # W1-W2, W1-W3, W2-W3
        for first, second in combinations(names, 2):

            # Oyuncularin yerlerini degistir
            directions = [
                (first, second),
                (second, first)
            ]

            for max_weight, min_weight in directions:

                print(
                    f"\nESLESME: "
                    f"MAX={max_weight} "
                    f"MIN={min_weight}"
                )

                for opening_index, opening in enumerate(
                    openings, start=1
                ):

                    game_number += 1

                    result = play_game(
                        game,
                        max_weight,
                        min_weight,
                        opening
                    )

                    result["Oyun"] = game_number

                    result["Baslangic No"] = opening_index

                    results.append(result)

                    winner = result["Kazanan"]

                    if winner == "BERABERE":

                        draws[max_weight][min_weight] += 1
                        draws[min_weight][max_weight] += 1

                    elif winner == max_weight:

                        wins[max_weight][min_weight] += 1

                    else:

                        wins[min_weight][max_weight] += 1

                    writer.writerow(result)

                    file.flush()

                    print(
                        f"Oyun {game_number:02d}/60 | "
                        f"Baslangic: {opening_index} | "
                        f"Kazanan: {winner} | "
                        f"Hamle: {result['Toplam Hamle']} | "
                        f"Dugum: {result['Toplam Dugum']} | "
                        f"Sure: {result['Sure (s)']} s",
                        flush=True
                    )

    total_elapsed = time.perf_counter() - total_start

    # ==========================================
    # GALIBIYET MATRISI
    # ==========================================

    print("\n" + "=" * 50)
    print("GALIBIYET MATRISI")
    print("=" * 50)

    print(f"{'Ajan':<10}", end="")

    for name in names:

        print(f"{name:<10}", end="")

    print()

    matrix_rows = []

    for a in names:

        row = {"Ajan": a}

        print(f"{a:<10}", end="")

        for b in names:

            value = "-" if a == b else wins[a][b]

            row[b] = value

            print(f"{str(value):<10}", end="")

        print()

        matrix_rows.append(row)

    with open(
        "galibiyet_matrisi.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=["Ajan"] + names
        )

        writer.writeheader()
        writer.writerows(matrix_rows)

    # ==========================================
    # GENEL PUAN TABLOSU
    # ==========================================

    summary = []

    for name in names:

        win_count = sum(wins[name].values())

        loss_count = sum(
            wins[opponent][name]
            for opponent in names
        )

        draw_count = sum(draws[name].values())

        total = win_count + loss_count + draw_count

        assert total == 40

        # Galibiyet 1, beraberlik 0.5 puan
        points = win_count + 0.5 * draw_count

        summary.append({
            "Ajan": name,
            "Oyun": total,
            "Galibiyet": win_count,
            "Maglubiyet": loss_count,
            "Beraberlik": draw_count,
            "Puan": points,
            "Galibiyet Orani (%)": round(
                win_count / total * 100, 2
            )
        })

    # Puana gore sirala
    summary.sort(
        key=lambda row: row["Puan"],
        reverse=True
    )

    print("\nGENEL PUAN TABLOSU")

    for row in summary:

        print(
            f"{row['Ajan']} | "
            f"Oyun: {row['Oyun']} | "
            f"Galibiyet: {row['Galibiyet']} | "
            f"Maglubiyet: {row['Maglubiyet']} | "
            f"Beraberlik: {row['Beraberlik']} | "
            f"Puan: {row['Puan']} | "
            f"Galibiyet orani: "
            f"%{row['Galibiyet Orani (%)']}"
        )

    with open(
        "agirlik_turnuvasi_ozet.csv",
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

    # ==========================================
    # SON KONTROLLER
    # ==========================================

    assert len(results) == 60

    for a, b in combinations(names, 2):

        assert (
            wins[a][b]
            + wins[b][a]
            + draws[a][b]
            == 20
        )

    total_draws = sum(
        row["Kazanan"] == "BERABERE"
        for row in results
    )

    total_wins = sum(
        row["Galibiyet"]
        for row in summary
    )

    total_losses = sum(
        row["Maglubiyet"]
        for row in summary
    )

    assert total_wins + total_draws == 60
    assert total_wins == total_losses

    assert sum(
        row["Puan"] for row in summary
    ) == 60

    best_points = summary[0]["Puan"]

    winners = [
        row["Ajan"]
        for row in summary
        if row["Puan"] == best_points
    ]

    print("\n" + "=" * 50)
    print("TURNUVA SONUCU")
    print("=" * 50)

    print("Toplam oyun:", len(results))
    print("Sonuclanan oyun:", total_wins)
    print("Berabere biten oyun:", total_draws)

    print(
        "En basarili agirlik:",
        ", ".join(winners)
    )

    print(f"Toplam sure: {total_elapsed:.3f} saniye")

    print("\nOlusturulan dosyalar:")

    print("turnuva_baslangiclari.json")
    print("agirlik_turnuvasi_sonuclar.csv")
    print("galibiyet_matrisi.csv")
    print("agirlik_turnuvasi_ozet.csv")

    print("\nTum 60 oyun basariyla tamamlandi!")


if __name__ == "__main__":

    run_tournament()