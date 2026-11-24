import unittest
import random

from game import Game, state_from_moves
from zobrist import ZobristHash


class TestIncrementalHash(unittest.TestCase):

    def setUp(self):

        self.game = Game(d=27)

        self.zobrist = ZobristHash(
            self.game,
            seed=27
        )

    # Test 1: MAX hamlesi
    def test_max_move(self):

        state = self.game.initial_state()

        parent_key = self.zobrist.hash_state(
            state
        )

        child = self.game.result(state, 0)

        incremental = self.zobrist.update_hash(
            parent_key, child
        )

        full = self.zobrist.hash_state(child)

        self.assertEqual(incremental, full)

    # Test 2: MIN hamlesi
    def test_min_move(self):

        state = state_from_moves(
            self.game, [0]
        )

        parent_key = self.zobrist.hash_state(
            state
        )

        child = self.game.result(state, 1)

        incremental = self.zobrist.update_hash(
            parent_key, child
        )

        full = self.zobrist.hash_state(child)

        self.assertEqual(incremental, full)

    # Test 3: Farkli hamle siralari
    def test_incremental_transposition(self):

        hashes = []

        for moves in (
            [0, 1, 2],
            [2, 1, 0]
        ):

            state = self.game.initial_state()

            key = self.zobrist.hash_state(state)

            for move in moves:

                child = self.game.result(
                    state, move
                )

                key = self.zobrist.update_hash(
                    key, child
                )

                state = child

            self.assertEqual(
                key,
                self.zobrist.hash_state(state)
            )

            hashes.append(key)

        self.assertEqual(
            hashes[0],
            hashes[1]
        )

    # Test 4: Dort varyantta rastgele oyunlar
    def test_all_variants(self):

        for variant in range(4):

            game = Game(d=27, V=variant)

            zobrist = ZobristHash(
                game, seed=27
            )

            rng = random.Random(27)

            for _ in range(5):

                state = game.initial_state()

                key = zobrist.hash_state(state)

                while not game.is_terminal(state):

                    move = rng.choice(
                        game.actions(state)
                    )

                    child = game.result(
                        state, move
                    )

                    key = zobrist.update_hash(
                        key, child
                    )

                    self.assertEqual(
                        key,
                        zobrist.hash_state(child)
                    )

                    self.assertGreaterEqual(
                        key, 0
                    )

                    self.assertLess(
                        key, 2 ** 64
                    )

                    state = child

    # Test 5: Terminal hamle
    def test_terminal_move(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 1]
        )

        parent_key = self.zobrist.hash_state(
            state
        )

        child = self.game.result(state, 0)

        self.assertTrue(
            self.game.is_terminal(child)
        )

        self.assertEqual(
            self.zobrist.update_hash(
                parent_key, child
            ),
            self.zobrist.hash_state(child)
        )

    # Test 6: Son hamlesi olmayan durum
    def test_missing_last_move(self):

        state = self.game.initial_state()

        key = self.zobrist.hash_state(state)

        with self.assertRaises(ValueError):

            self.zobrist.update_hash(
                key, state
            )


if __name__ == "__main__":

    unittest.main()