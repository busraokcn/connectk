import unittest
import math

from unittest.mock import Mock

from game import Game, MAX, state_from_moves
from search import Minimax, AlphaBeta
from evaluate import Evaluator


class TestEvalSearch(unittest.TestCase):

    def setUp(self):

        self.game = Game(d=27)

        self.evaluator = Evaluator(self.game)

    # Test 1: Eski davranisin korunmasi
    def test_legacy_evaluation(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 2]
        )

        self.assertEqual(
            Minimax(self.game).evaluate(state), 0
        )

        self.assertEqual(
            AlphaBeta(self.game).evaluate(state), 0
        )

    # Test 2: Yeni Eval fonksiyonunun kullanilmasi
    def test_evaluator_connection(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 2]
        )

        expected = self.evaluator.evaluate(state)

        algorithms = [
            Minimax(
                self.game,
                evaluator=self.evaluator
            ),

            AlphaBeta(
                self.game,
                evaluator=self.evaluator
            )
        ]

        for algorithm in algorithms:

            self.assertAlmostEqual(
                algorithm.evaluate(state),
                expected
            )

    # Test 3: MAX icin sezgisel arama
    def test_max_heuristic_search(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1]
        )

        algorithm = AlphaBeta(
            self.game,
            evaluator=self.evaluator
        )

        move, value, nodes = algorithm.choose_move(
            state, 1
        )

        self.assertGreater(value, 0)

        self.assertIn(
            move,
            self.game.actions(state)
        )

        expected = max(
            self.evaluator.evaluate(
                self.game.result(state, action)
            )
            for action in self.game.actions(state)
        )

        self.assertAlmostEqual(value, expected)

    # Test 4: MIN icin sezgisel arama
    def test_min_heuristic_search(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 2]
        )

        algorithm = AlphaBeta(
            self.game,
            evaluator=self.evaluator
        )

        move, value, nodes = algorithm.choose_move(
            state, 1
        )

        self.assertLess(value, 0)

        expected = min(
            self.evaluator.evaluate(
                self.game.result(state, action)
            )
            for action in self.game.actions(state)
        )

        self.assertAlmostEqual(value, expected)

    # Test 5: Terminal kontrolu Eval'den once
    def test_terminal_before_evaluation(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 1, 0]
        )

        fake_evaluator = Mock()

        fake_evaluator.evaluate.side_effect = (
            AssertionError("Terminal durumda Eval cagrildi")
        )

        minimax = Minimax(
            self.game,
            evaluator=fake_evaluator
        )

        alphabeta = AlphaBeta(
            self.game,
            evaluator=fake_evaluator
        )

        self.assertEqual(
            minimax.min_value(state, 0), 1
        )

        self.assertEqual(
            alphabeta.min_value(
                state, 0, -math.inf, math.inf
            ),
            1
        )

        fake_evaluator.evaluate.assert_not_called()

    # Test 6: Yeni Minimax ve AlphaBeta esitligi
    def test_heuristic_equivalence(self):

        positions = [
            [],
            [0, 1, 0, 1],
            [0, 1, 0, 1, 2],
            [0, 1, 0, 1, 0, 1, 0, 2],
            [1, 0, 1, 0, 2, 0, 2, 0],
            [4, 4, 5, 5, 0, 0, 1, 1]
        ]

        depth = 3

        minimax = Minimax(
            self.game,
            evaluator=self.evaluator
        )

        for moves in positions:

            state = state_from_moves(
                self.game, moves
            )

            mm_move, mm_value, mm_nodes = (
                minimax.choose_move(state, depth)
            )

            for method in ("A", "B", "C"):

                with self.subTest(
                    moves=moves,
                    method=method
                ):

                    algorithm = AlphaBeta(
                        self.game,
                        order=method,
                        evaluator=self.evaluator
                    )

                    move, value, nodes = (
                        algorithm.choose_move(
                            state, depth
                        )
                    )

                    self.assertAlmostEqual(
                        value, mm_value
                    )

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

                    if state.player == MAX:

                        exact = minimax.min_value(
                            child, depth - 1
                        )

                    else:

                        exact = minimax.max_value(
                            child, depth - 1
                        )

                    self.assertAlmostEqual(
                        exact, mm_value
                    )


if __name__ == "__main__":
    unittest.main()