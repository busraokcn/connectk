import random
import json

from game import Game, MAX, MIN, state_from_moves


# Sabit ayarlar
SEED = 27
POSITION_COUNT = 50


# Rastgele oyun konumlari olusturma
def generate_positions(game, count=50, seed=27):

    rng = random.Random(seed)

    positions = []
    seen = set()

    attempts = 0

    while len(positions) < count:

        attempts += 1

        if attempts > 10000:
            raise RuntimeError(
                "Yeterli sayida konum olusturulamadi"
            )

        state = game.initial_state()
        moves = []

        # MAX ve MIN sirasi dengeli olsun
        if len(positions) % 2 == 0:

            move_count = rng.choice(
                list(range(4, 21, 2))
            )

        else:

            move_count = rng.choice(
                list(range(5, 21, 2))
            )

        # Rastgele yasal hamleler yap
        for i in range(move_count):

            if game.is_terminal(state):
                break

            legal_moves = game.actions(state)

            action = rng.choice(legal_moves)

            state = game.result(state, action)

            moves.append(action)

        # Bitmis oyunlari kabul etme
        if game.is_terminal(state):
            continue

        # Ayni oyun konumunu tekrar kabul etme
        key = (state.board, state.player)

        if key in seen:
            continue

        seen.add(key)

        positions.append(moves)

    return positions


if __name__ == "__main__":

    game = Game(d=27)

    positions = generate_positions(
        game,
        POSITION_COUNT,
        SEED
    )

    print("CONNECT-K ARENA - RASTGELE KONUMLAR")

    print("Seed:", SEED)
    print("R:", game.R)
    print("C:", game.C)
    print("K:", game.K)
    print("V:", game.V)

    max_count = 0
    min_count = 0

    unique_states = set()

    # Olusturulan konumlari kontrol et
    for i, moves in enumerate(positions, start=1):

        state = state_from_moves(game, moves)

        assert not game.is_terminal(state)

        key = (state.board, state.player)

        assert key not in unique_states

        unique_states.add(key)

        if state.player == MAX:
            max_count += 1
        else:
            min_count += 1

        player_name = (
            "MAX" if state.player == MAX else "MIN"
        )

        print(
            f"Konum {i:02d} | "
            f"Hamle sayisi: {len(moves):2d} | "
            f"Sira: {player_name} | "
            f"Hamleler: {moves}"
        )

    # JSON dosyasina kaydedilecek bilgiler
    data = {
        "seed": SEED,
        "R": game.R,
        "C": game.C,
        "K": game.K,
        "V": game.V,
        "positions": positions
    }

    # Konumlari JSON dosyasina kaydet
    with open(
        "rastgele_konumlar.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(data, file, indent=4)

    # Tekrarlanabilirlik kontrolu
    repeated = generate_positions(
        game,
        POSITION_COUNT,
        SEED
    )

    assert positions == repeated
    assert len(positions) == 50
    assert len(unique_states) == 50
    assert max_count == 25
    assert min_count == 25

    print("\nSONUCLAR")
    print("Toplam konum:", len(positions))
    print("Benzersiz konum:", len(unique_states))
    print("Terminal konum: 0")
    print("MAX sirasindaki konum:", max_count)
    print("MIN sirasindaki konum:", min_count)

    print("Tekrarlanabilirlik: BASARILI")

    print(
        "\nKonumlar rastgele_konumlar.json "
        "dosyasina kaydedildi."
    )

    print("Tum konum kontrolleri basarili!")