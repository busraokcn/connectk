from game import Game, state_from_moves
from evaluate import Evaluator, DEFAULT_WEIGHTS


# ==========================================
# AGIRLIK VEKTORLERI
# ==========================================

WEIGHT_SETS = {

    # W1: Dengeli strateji
    "W1": dict(DEFAULT_WEIGHTS),

    # W2: Tehdit odakli strateji
    "W2": {
        "max_k1": 24,
        "max_k2": 2,
        "min_k1": 24,
        "min_k2": 2,
        "max_wrap": 1,
        "min_wrap": 1
    },

    # W3: Gelisim ve silindir odakli strateji
    "W3": {
        "max_k1": 10,
        "max_k2": 6,
        "min_k1": 10,
        "min_k2": 6,
        "max_wrap": 4,
        "min_wrap": 4
    }
}


WEIGHT_NAMES = {
    "W1": "Dengeli",
    "W2": "Tehdit odakli",
    "W3": "Gelisim ve silindir odakli"
}


SCALE = 30.0
SEED = 27
DEPTH = 5


# Belirli agirlik vektoruyle Evaluator olustur
def create_evaluator(game, weight_name):

    if weight_name not in WEIGHT_SETS:

        raise ValueError("Gecersiz agirlik vektoru")

    return Evaluator(
        game,
        weights=WEIGHT_SETS[weight_name],
        scale=SCALE
    )


# ==========================================
# AGIRLIK VEKTORU KONTROLLERI
# ==========================================

if __name__ == "__main__":

    game = Game(d=27)

    evaluators = {
        name: create_evaluator(game, name)
        for name in WEIGHT_SETS
    }

    print("CONNECT-K ARENA - AGIRLIK VEKTORLERI")

    print("Seed:", SEED)
    print("Arama derinligi:", DEPTH)
    print("Olcek:", SCALE)

    # Agirliklari ekrana yazdir
    print("\nAGIRLIK TABLOSU")

    print(
        f"{'Oznitelik':<15}"
        f"{'W1':<10}"
        f"{'W2':<10}"
        f"{'W3':<10}"
    )

    print("-" * 45)

    for feature in DEFAULT_WEIGHTS:

        print(
            f"{feature:<15}"
            f"{WEIGHT_SETS['W1'][feature]:<10}"
            f"{WEIGHT_SETS['W2'][feature]:<10}"
            f"{WEIGHT_SETS['W3'][feature]:<10}"
        )

    # Test edilecek oyun konumlari
    positions = {

        "Bos tahta": [],

        "MAX kazanma tehdidi": [
            0, 1, 0, 1, 0, 1, 0, 2
        ],

        "MIN kazanma tehdidi": [
            1, 0, 1, 0, 2, 0, 2, 0
        ],

        "MAX uc tas": [
            0, 1, 0, 1, 0
        ],

        "MAX sarmali gelisim": [
            4, 3, 5, 3, 0
        ],

        "Dengeli sarmali konum": [
            4, 4, 5, 5, 0, 0, 1, 1
        ]
    }

    # Her konumu uc agirlikla degerlendir
    for position_name, moves in positions.items():

        state = state_from_moves(game, moves)

        print("\n" + "=" * 50)
        print("KONUM:", position_name)

        game.print_board(state)

        assert not game.is_terminal(state)

        print()

        for weight_name, evaluator in evaluators.items():

            raw = evaluator.raw_score(state)

            value = evaluator.evaluate(state)

            print(
                f"{weight_name} | "
                f"Ham puan: {raw:>4} | "
                f"Eval: {value:.6f}"
            )

            assert -1 < value < 1

    # Varsayilan agirlik kontrolu
    assert WEIGHT_SETS["W1"] == DEFAULT_WEIGHTS

    # Bos tahta kontrolu
    empty = game.initial_state()

    for evaluator in evaluators.values():

        assert evaluator.evaluate(empty) == 0

    # MAX tehdidi kontrolu
    threat = state_from_moves(
        game,
        [0, 1, 0, 1, 0, 1, 0, 2]
    )

    assert evaluators["W1"].raw_score(threat) == 9

    assert evaluators["W2"].raw_score(threat) == 22

    assert evaluators["W3"].raw_score(threat) == 4

    # W2 tehdide daha fazla onem vermeli
    assert (
        evaluators["W2"].evaluate(threat)
        > evaluators["W1"].evaluate(threat)
        > evaluators["W3"].evaluate(threat)
    )

    # Sarmali gelisim kontrolu
    wrapped = state_from_moves(
        game,
        [4, 3, 5, 3, 0]
    )

    assert (
        evaluators["W3"].evaluate(wrapped)
        > evaluators["W1"].evaluate(wrapped)
        > evaluators["W2"].evaluate(wrapped)
    )

    # Gecersiz agirlik adi kontrolu
    try:

        create_evaluator(game, "W4")

    except ValueError:

        print("\nGecersiz agirlik kontrolu: BASARILI")

    else:

        raise AssertionError(
            "Gecersiz agirlik kabul edildi"
        )

    print("\nTum agirlik vektoru kontrolleri basarili!")