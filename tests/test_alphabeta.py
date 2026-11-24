import unittest
import math

from game import Game, MAX, MIN, state_from_moves
from search import Minimax, AlphaBeta


class TestAlphaBeta(unittest.TestCase):

    def setUp(self):
        self.game = Game(d=27)
        self.state = self.game.initial_state()
        self.minimax = Minimax(self.game)

    # Test 1: Hamle siralamalari
    def test_move_ordering(self):

        expected = {
            "A": [0, 1, 2, 3, 4, 5],
            "B": [2, 3, 1, 4, 0, 5],
            "C": [2, 3, 1, 4, 0, 5]
        }

        for method, order in expected.items():

            with self.subTest(method=method):

                algorithm = AlphaBeta(
                    self.game, order=method
                )

                self.assertEqual(
                    algorithm.ordered_actions(self.state),
                    order
                )

    # Test 2: Kazanma ve engelleme onceligi
    def test_tactical_ordering(self):

        algorithm = AlphaBeta(
            self.game, order="C"
        )

        positions = [
            [0, 1, 0, 1, 0, 1, 0, 2],
            [1, 0, 1, 0, 2, 0, 2, 0],
            [1, 0, 1, 0, 2, 0, 2, 0, 3]
        ]

        for moves in positions:

            state = state_from_moves(
                self.game, moves
            )

            ordered = algorithm.ordered_actions(state)

            self.assertEqual(ordered[0], 0)

            self.assertEqual(
                sorted(ordered),
                self.game.actions(state)
            )

    # Test 3: Minimax ile ayni sonucu bulmali
    def test_minimax_equivalence(self):

        positions = [
            [],
            [0, 1, 0, 1, 0, 1, 0, 2],
            [1, 0, 1, 0, 2, 0, 2, 0],
            [1, 0, 1, 0, 2, 0, 2, 0, 3],
            [0, 0, 0, 0, 0]
        ]

        depth = 4

        for moves in positions:

            state = state_from_moves(
                self.game, moves
            )

            mm_move, mm_value, mm_nodes = (
                self.minimax.choose_move(state, depth)
            )

            for method in ("A", "B", "C"):

                with self.subTest(
                    moves=moves, method=method
                ):

                    algorithm = AlphaBeta(
                        self.game, order=method
                    )

                    move, value, nodes = (
                        algorithm.choose_move(
                            state, depth
                        )
                    )

                    self.assertEqual(value, mm_value)

                    self.assertLessEqual(
                        nodes, mm_nodes
                    )

                    self.assertIn(
                        move,
                        self.game.actions(state)
                    )

                    child = self.game.result(
                        state, move
                    )

                    self.minimax.nodes = 0

                    if state.player == MAX:

                        exact = self.minimax.min_value(
                            child, depth - 1
                        )

                    else:

                        exact = self.minimax.max_value(
                            child, depth - 1
                        )

                    self.assertEqual(
                        exact, mm_value
                    )

    # Test 4: Terminal durumda arama
    def test_terminal_state(self):

        moves = [0, 1, 0, 1, 0, 1, 0, 1, 0]

        state = state_from_moves(
            self.game, moves
        )

        algorithm = AlphaBeta(self.game)

        move, value, nodes = (
            algorithm.choose_move(state, 6)
        )

        self.assertIsNone(move)
        self.assertEqual(value, 1)
        self.assertEqual(nodes, 1)

    # Test 5: Beta esitlik durumunda kesme
    def test_beta_equality_cutoff(self):

        algorithm = AlphaBeta(
            self.game, order="A"
        )

        algorithm.nodes = 0

        value = algorithm.max_value(
            self.state,
            depth=1,
            alpha=-math.inf,
            beta=0
        )

        self.assertEqual(value, 0)

        # Kok dugum + bir cocuk
        self.assertEqual(algorithm.nodes, 2)

    # Test 6: Erken ve yanlis beta kesmesi
    def test_beta_no_premature_cutoff(self):

        moves = [0, 1, 0, 1, 0, 1, 0, 2]

        state = state_from_moves(
            self.game, moves
        )

        algorithm = AlphaBeta(
            self.game, order="B"
        )

        algorithm.nodes = 0

        value = algorithm.max_value(
            state,
            depth=1,
            alpha=-math.inf,
            beta=1
        )

        # Kazanma hamlesi bulunmali
        self.assertEqual(value, 1)

    # Test 7: Alpha esitlik durumunda kesme
    def test_alpha_equality_cutoff(self):

        state = self.game.result(
            self.state, 0
        )

        self.assertEqual(state.player, MIN)

        algorithm = AlphaBeta(
            self.game, order="A"
        )

        algorithm.nodes = 0

        value = algorithm.min_value(
            state,
            depth=1,
            alpha=0,
            beta=math.inf
        )

        self.assertEqual(value, 0)
        self.assertEqual(algorithm.nodes, 2)

    # Test 8: Misere varyanti
    def test_misere(self):

        game = Game(d=27, V=2)

        state = state_from_moves(
            game,
            [0, 1, 0, 1, 0, 1, 0, 2]
        )

        algorithm = AlphaBeta(
            game, order="C"
        )

        ordered = algorithm.ordered_actions(state)

        self.assertEqual(ordered[-1], 0)

        move, value, nodes = (
            algorithm.choose_move(state, 1)
        )

        self.assertNotEqual(move, 0)
        self.assertEqual(value, 0)

    # Test 9: Gecersiz parametreler
    def test_invalid_parameters(self):

        with self.assertRaises(ValueError):

            AlphaBeta(self.game, order="D")

        algorithm = AlphaBeta(self.game)

        with self.assertRaises(ValueError):

            algorithm.choose_move(self.state, 0)

        with self.assertRaises(ValueError):

            algorithm.choose_move(self.state, -1)


if __name__ == "__main__":
    unittest.main()