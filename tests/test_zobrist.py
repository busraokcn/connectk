import unittest

from dataclasses import replace

from game import (
    Game,
    MAX,
    MIN,
    BLOCKED,
    state_from_moves
)

from zobrist import ZobristHash


class TestZobrist(unittest.TestCase):

    def setUp(self):

        self.game = Game(d=27)

        self.zobrist = ZobristHash(
            self.game,
            seed=27
        )

    # Test 1: Anahtar sayisi ve 64 bit kontrolu
    def test_key_table(self):

        expected = self.game.R * self.game.C * 3

        self.assertEqual(
            len(self.zobrist.table),
            expected
        )

        keys = list(self.zobrist.table.values())

        keys.append(self.zobrist.side_key)

        for key in keys:

            self.assertGreaterEqual(key, 0)
            self.assertLess(key, 2 ** 64)

    # Test 2: Bos tahta
    def test_empty_hash(self):

        state = self.game.initial_state()

        self.assertEqual(
            self.zobrist.hash_state(state),
            0
        )

    # Test 3: Ayni seed ayni anahtarlari uretmeli
    def test_seed_reproducibility(self):

        second = ZobristHash(
            self.game,
            seed=27
        )

        self.assertEqual(
            self.zobrist.table,
            second.table
        )

        self.assertEqual(
            self.zobrist.side_key,
            second.side_key
        )

    # Test 4: Farkli hamle sirasi, ayni konum
    def test_transposition(self):

        first = state_from_moves(
            self.game,
            [0, 1, 2]
        )

        second = state_from_moves(
            self.game,
            [2, 1, 0]
        )

        self.assertEqual(
            first.board,
            second.board
        )

        self.assertEqual(
            first.player,
            second.player
        )

        self.assertEqual(
            self.zobrist.hash_state(first),
            self.zobrist.hash_state(second)
        )

    # Test 5: Farkli konumlar
    def test_different_positions(self):

        first = state_from_moves(
            self.game,
            [0, 1, 2]
        )

        second = state_from_moves(
            self.game,
            [0, 1, 3]
        )

        self.assertNotEqual(
            self.zobrist.hash_state(first),
            self.zobrist.hash_state(second)
        )

    # Test 6: Siradaki oyuncu hash'i etkilemeli
    def test_side_to_move(self):

        state = self.game.initial_state()

        other = replace(
            state,
            player=MIN
        )

        first = self.zobrist.hash_state(state)

        second = self.zobrist.hash_state(other)

        self.assertNotEqual(first, second)

        self.assertEqual(
            first ^ second,
            self.zobrist.side_key
        )

    # Test 7: Engelli varyant
    def test_blocked_cells_hash(self):

        game = Game(d=27, V=3)

        zobrist = ZobristHash(
            game,
            seed=27
        )

        state = game.initial_state()

        expected = 0

        for row in range(game.R):

            for col in range(game.C):

                if state.board[row][col] == BLOCKED:

                    expected ^= zobrist.table[
                        (row, col, BLOCKED)
                    ]

        self.assertEqual(
            zobrist.hash_state(state),
            expected
        )

        self.assertNotEqual(expected, 0)


if __name__ == "__main__":

    unittest.main()