import random

from game import (
    Game,
    MAX,
    MIN,
    EMPTY,
    BLOCKED,
    state_from_moves
)


class ZobristHash:

    def __init__(self, game, seed=27):

        self.game = game
        self.seed = seed

        rng = random.Random(seed)

        self.table = {}

        for row in range(game.R):

            for col in range(game.C):

                for piece in (MAX, MIN, BLOCKED):

                    self.table[(row, col, piece)] = (
                        rng.getrandbits(64)
                    )

        self.side_key = rng.getrandbits(64)

    # Butun tahtanin hash degerini hesapla
    def hash_state(self, state):

        key = 0

        for row in range(self.game.R):

            for col in range(self.game.C):

                piece = state.board[row][col]

                if piece != EMPTY:

                    key ^= self.table[
                        (row, col, piece)
                    ]

        if state.player == MIN:

            key ^= self.side_key

        return key

    # ======================================
    # ARTIMLI HASH HESAPLAMA
    # ======================================

    def update_hash(self, parent_key, child_state):

        # Son hamlenin konumu
        if child_state.last_move is None:

            raise ValueError("Son hamle bulunamadi")

        row, col = child_state.last_move

        # Yeni eklenen tas
        piece = child_state.board[row][col]

        if piece not in (MAX, MIN):

            raise ValueError("Gecersiz tas")

        if child_state.player != -piece:

            raise ValueError("Gecersiz oyuncu sirasi")

        # Yeni tasin anahtari
        piece_key = self.table[
            (row, col, piece)
        ]

        # Yeni tas ve oyuncu sirasi
        new_key = (
            parent_key
            ^ piece_key
            ^ self.side_key
        )

        return new_key


# ==========================================
# ZOBRIST HASH KONTROLLERI
# ==========================================

if __name__ == "__main__":

    game = Game(d=27)

    zobrist = ZobristHash(game, seed=27)

    print("CONNECT-K ARENA - ZOBRIST HASHING")

    print("Seed:", zobrist.seed)
    print("R:", game.R)
    print("C:", game.C)
    print("K:", game.K)
    print("V:", game.V)

    print(
        "\nHucre anahtari sayisi:",
        len(zobrist.table)
    )

    print(
        "Oyuncu anahtari:",
        zobrist.side_key
    )

    positions = {
        "Bos tahta": [],
        "Tek hamle": [0],
        "Iki hamle": [0, 1],
        "Uc hamle": [0, 1, 2],
        "Alternatif hamle sirasi": [2, 1, 0],
        "Farkli konum": [0, 1, 3]
    }

    hashes = {}

    for name, moves in positions.items():

        state = state_from_moves(game, moves)

        key = zobrist.hash_state(state)

        hashes[name] = key

        print("\nKONUM:", name)

        game.print_board(state)

        print("Hash:", key)

        print(f"Hexadecimal: {key:016X}")

        assert 0 <= key < 2 ** 64

    assert hashes["Bos tahta"] == 0

    assert (
        hashes["Uc hamle"]
        == hashes["Alternatif hamle sirasi"]
    )

    print("\nAyni konum kontrolu: BASARILI")

    assert (
        hashes["Uc hamle"]
        != hashes["Farkli konum"]
    )

    print("Farkli konum kontrolu: BASARILI")

    second = ZobristHash(game, seed=27)

    assert zobrist.table == second.table
    assert zobrist.side_key == second.side_key

    print("Seed kontrolu: BASARILI")

    blocked_game = Game(d=27, V=3)

    blocked_hash = ZobristHash(
        blocked_game,
        seed=27
    )

    blocked_state = blocked_game.initial_state()

    print("\nENGELLI VARYANT")

    blocked_game.print_board(blocked_state)

    print(
        "Engelli tahta hash:",
        blocked_hash.hash_state(blocked_state)
    )

    # ======================================
    # YENI ARTIMLI HASH KONTROLU
    # ======================================

    print("\nARTIMLI HASH KONTROLU")

    state = game.initial_state()

    key = zobrist.hash_state(state)

    moves = [0, 1, 2, 3, 4, 5, 0, 1]

    for index, move in enumerate(moves, start=1):

        child = game.result(state, move)

        incremental_key = zobrist.update_hash(
            key, child
        )

        full_key = zobrist.hash_state(child)

        assert incremental_key == full_key

        print(
            f"Hamle {index}: Sutun {move}"
        )

        print("Tam hash:", full_key)

        print("Artimli hash:", incremental_key)

        print("Esitlik: BASARILI\n")

        state = child

        key = incremental_key

    print("Tum Zobrist kontrolleri basarili!")