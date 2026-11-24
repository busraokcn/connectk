import unittest
import math

from game import Game, state_from_moves
from tt_search import TTAlphaBeta
from threat_search import ThreatAlphaBeta
from agirliklar import create_evaluator


class TestThreatExtension(unittest.TestCase):

    def setUp(self):

        self.game = Game(d=27)

        self.evaluator = create_evaluator(
            self.game, "W3"
        )

        self.agent = ThreatAlphaBeta(
            self.game,
            order="A",
            evaluator=self.evaluator
        )

    # Test 1: MAX kazanma tehdidi
    def test_max_threat(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 2]
        )

        self.assertIn(
            0,
            self.agent.winning_moves(state)
        )

        key = self.agent.zobrist.hash_state(state)

        value, _ = self.agent._search(
            state, 0, -math.inf, math.inf, key
        )

        self.assertEqual(value, 1)

        self.assertGreater(
            self.agent.extensions, 0
        )

    # Test 2: MIN kazanma tehdidi
    def test_min_threat(self):

        state = state_from_moves(
            self.game,
            [1, 0, 1, 0, 2, 0, 2, 0, 3]
        )

        self.assertIn(
            0,
            self.agent.winning_moves(state)
        )

        key = self.agent.zobrist.hash_state(state)

        value, _ = self.agent._search(
            state, 0, -math.inf, math.inf, key
        )

        self.assertEqual(value, -1)

    # Test 3: Sakin konumda uzatma yapilmamali
    def test_quiet_position(self):

        state = self.game.initial_state()

        key = self.agent.zobrist.hash_state(state)

        value, _ = self.agent._search(
            state, 0, -math.inf, math.inf, key
        )

        self.assertEqual(value, 0)

        self.assertEqual(
            self.agent.extensions, 0
        )

        self.assertEqual(
            self.agent.extension_nodes, 0
        )

    # Test 4: Terminal kontrolu once yapilmali
    def test_terminal_first(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 1, 0]
        )

        key = self.agent.zobrist.hash_state(state)

        value, _ = self.agent._search(
            state, 0, -math.inf, math.inf, key
        )

        self.assertEqual(value, 1)

        self.assertEqual(
            self.agent.extensions, 0
        )

    # Test 5: Bulunan ufuk etkisini onleme
    def test_horizon_example(self):

        moves = [
            3, 5, 2, 2, 0, 1, 0, 0, 0,
            0, 1, 1, 2, 1, 1, 4, 4
        ]

        state = state_from_moves(
            self.game, moves
        )

        normal = TTAlphaBeta(
            self.game,
            order="A",
            evaluator=self.evaluator
        )

        old_move, _, _ = normal.choose_move(
            state, 1
        )

        new_move, value, _ = (
            self.agent.choose_move(state, 1)
        )

        self.assertEqual(old_move, 5)

        self.assertNotEqual(new_move, 5)

        child = self.game.result(
            state, new_move
        )

        self.assertEqual(
            self.agent.winning_moves(child),
            []
        )

        self.assertGreater(
            self.agent.extensions, 0
        )

    # Test 6: TT acik ve kapali esitligi
    def test_tt_equivalence(self):

        off = ThreatAlphaBeta(
            self.game,
            order="A",
            evaluator=self.evaluator,
            use_tt=False
        )

        positions = [
            [],
            [0, 1, 0, 1],
            [4, 3, 5, 3, 0],
            [0, 1, 0, 1, 0, 1, 0, 2]
        ]

        for moves in positions:

            state = state_from_moves(
                self.game, moves
            )

            _, first, _ = (
                self.agent.choose_move(state, 3)
            )

            _, second, _ = (
                off.choose_move(state, 3)
            )

            self.assertEqual(first, second)


if __name__ == "__main__":

    unittest.main()