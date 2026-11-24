import json
import math

from game import Game, MAX, MIN, state_from_moves
from search import AlphaBeta, Minimax
from agirliklar import create_evaluator


game = Game(d=27)

evaluator = create_evaluator(game, "W3")

shallow = AlphaBeta(
    game,
    order="A",
    evaluator=evaluator
)

deep = AlphaBeta(
    game,
    order="A",
    evaluator=evaluator
)

reference = Minimax(
    game,
    evaluator=evaluator
)


SHALLOW_DEPTH = 1
DEEP_DEPTH = 2


# ==========================================
# BIR HAMLEDE KAZANMA KONTROLU
# ==========================================

def winning_moves(state):

    if game.is_terminal(state):
        return []

    player = state.player

    wins = []

    for move in game.actions(state):

        child = game.result(state, move)

        if game.is_terminal(child):

            if game.utility(child) == player:

                wins.append(move)

    return wins


# ==========================================
# BIR HAMLEYE AIT KESIN ARAMA DEGERI
# ==========================================

def exact_move_value(state, move, depth):

    child = game.result(state, move)

    if state.player == MAX:

        return reference.min_value(
            child, depth - 1
        )

    return reference.max_value(
        child, depth - 1
    )


# ==========================================
# AJANLARI KARSILIKLI OYNAT
# ==========================================

def find_example(opening, shallow_player):

    state = state_from_moves(game, opening)

    moves = list(opening)

    while not game.is_terminal(state):

        player = state.player

        if player == shallow_player:

            move, value, nodes = shallow.choose_move(
                state,
                SHALLOW_DEPTH
            )

            child = game.result(state, move)

            # Sig aramanin sectigi hamleden sonra
            # rakip hemen kazanabiliyor mu?
            threats = winning_moves(child)

            if threats:

                better_move, better_value, _ = (
                    deep.choose_move(
                        state,
                        DEEP_DEPTH
                    )
                )

                bad_value = exact_move_value(
                    state,
                    move,
                    DEEP_DEPTH
                )

                good_value = exact_move_value(
                    state,
                    better_move,
                    DEEP_DEPTH
                )

                # Daha derin aramada eski hamle
                # kesin kayba neden olmali.
                if (
                    bad_value == -player
                    and player * good_value > -1
                    and better_move != move
                ):

                    assert good_value == better_value

                    # Rakibin gercek cevabini oynat
                    reply, _, _ = deep.choose_move(
                        child,
                        DEEP_DEPTH
                    )

                    final_state = game.result(
                        child, reply
                    )

                    assert reply in threats
                    assert game.is_terminal(final_state)
                    assert game.utility(final_state) == -player

                    return {
                        "opening": list(opening),
                        "moves": list(moves),
                        "player": player,
                        "shallow_depth": SHALLOW_DEPTH,
                        "deep_depth": DEEP_DEPTH,
                        "bad_move": move,
                        "shallow_value": value,
                        "bad_deep_value": bad_value,
                        "better_move": better_move,
                        "better_value": good_value,
                        "opponent_winning_moves": threats,
                        "opponent_reply": reply,
                        "final_moves": moves + [move, reply],
                        "utility": game.utility(final_state)
                    }

        else:

            move, value, nodes = deep.choose_move(
                state,
                DEEP_DEPTH
            )

        assert move in game.actions(state)

        state = game.result(state, move)

        moves.append(move)

    return None


# ==========================================
# BASLANGIC KONUMLARINI OKU
# ==========================================

with open(
    "turnuva_baslangiclari.json",
    "r",
    encoding="utf-8"
) as file:

    openings = json.load(file)["openings"]


with open(
    "rastgele_konumlar.json",
    "r",
    encoding="utf-8"
) as file:

    extra_openings = json.load(file)["positions"]


# Once turnuva baslangiclari, sonra ek konumlar
all_openings = openings + extra_openings


print("CONNECT-K ARENA - UFUK ETKISI")

print("Sig arama derinligi:", SHALLOW_DEPTH)
print("Derin arama derinligi:", DEEP_DEPTH)
print("Agirlik: W3")
print("Siralama: A")


example = None

game_count = 0

seen = set()


for opening in all_openings:

    key = tuple(opening)

    if key in seen:
        continue

    seen.add(key)

    for shallow_player in (MAX, MIN):

        game_count += 1

        example = find_example(
            opening,
            shallow_player
        )

        print(
            f"Oyun {game_count:02d} | "
            f"Ornek bulundu: {example is not None}",
            flush=True
        )

        if example is not None:
            break

    if example is not None:
        break


if example is None:

    raise SystemExit(
        "Uygun ufuk etkisi ornegi bulunamadi."
    )


# ==========================================
# BULUNAN KONUMU GOSTER
# ==========================================

state = state_from_moves(
    game,
    example["moves"]
)

print("\n" + "=" * 60)
print("UFUK ETKISI ORNEGI BULUNDU")
print("=" * 60)

print("Denenen oyun sayisi:", game_count)

print("Baslangic:", example["opening"])

print("Hamle dizisi:", example["moves"])

print(
    "Siradaki oyuncu:",
    "MAX" if state.player == MAX else "MIN"
)

print("\nORIJINAL TAHTA")

game.print_board(state)

print("\nSIG ARAMA")

print("Derinlik:", SHALLOW_DEPTH)

print("Secilen kotu hamle:", example["bad_move"])

print(
    "Arama degeri:",
    example["shallow_value"]
)


# ==========================================
# KOTU HAMLEDEN SONRAKI TAHTA
# ==========================================

bad_state = game.result(
    state,
    example["bad_move"]
)

print("\nKOTU HAMLEDEN SONRA")

game.print_board(bad_state)

print(
    "Rakibin kazanabilecegi sutunlar:",
    example["opponent_winning_moves"]
)


# ==========================================
# DERINLIGE GORE KARSILASTIRMA
# ==========================================

print("\nDERINLIK KARSILASTIRMASI")

depth_results = []

for depth in range(1, 6):

    move, value, nodes = deep.choose_move(
        state, depth
    )

    bad_value = exact_move_value(
        state,
        example["bad_move"],
        depth
    )

    exact = exact_move_value(
        state,
        move,
        depth
    )

    assert exact == value

    depth_results.append({
        "depth": depth,
        "move": move,
        "value": value,
        "bad_move_value": bad_value,
        "nodes": nodes
    })

    print(
        f"Derinlik: {depth} | "
        f"En iyi hamle: {move} | "
        f"Deger: {value:.6f} | "
        f"Eski hamlenin degeri: {bad_value:.6f} | "
        f"Dugum: {nodes}"
    )


print("\nDERIN ARAMANIN SECIMI")

print("Daha iyi hamle:", example["better_move"])

print("Daha iyi deger:", example["better_value"])

good_state = game.result(
    state,
    example["better_move"]
)

game.print_board(good_state)


# ==========================================
# GERCEK OYUN SONUCU
# ==========================================

final_state = state_from_moves(
    game,
    example["final_moves"]
)

print("\nKOTU HAMLEYLE BITEN GERCEK OYUN")

game.print_board(final_state)

print(
    "Rakibin kazanma hamlesi:",
    example["opponent_reply"]
)

print("Utility:", game.utility(final_state))

assert game.is_terminal(final_state)

assert game.utility(final_state) == -state.player


# ==========================================
# ORNEGI DOSYAYA KAYDET
# ==========================================

example["games_checked"] = game_count

example["depth_results"] = depth_results

example["R"] = game.R
example["C"] = game.C
example["K"] = game.K
example["V"] = game.V

example["weight"] = "W3"
example["order"] = "A"


with open(
    "ufuk_etkisi_ornek.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        example,
        file,
        indent=4
    )


print("\nOrnek ufuk_etkisi_ornek.json dosyasina kaydedildi.")

print("Ufuk etkisi dogrulandi!")