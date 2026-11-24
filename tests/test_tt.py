import unittest
import math

from dataclasses import replace

from game import Game, MAX, state_from_moves
from search import AlphaBeta

from tt_search import (
    TTAlphaBeta,
    EXACT,
    LOWER,
    UPPER
)

from agirliklar import create_evaluator


class TestTT(unittest.TestCase):

    def setUp(self):

        self.game = Game(d=27)

        self.evaluator = create_evaluator(
            self.game, "W3"
        )

        self.agent = TTAlphaBeta(
            self.game,
            evaluator=self.evaluator,
            use_tt=True
        )

        self.reference = AlphaBeta(
            self.game,
            evaluator=self.evaluator
        )

    # Test 1: Normal AlphaBeta ile esitlik
    def test_fixed_depth_equivalence(self):

        positions = [
            [],
            [0, 1, 0, 1],
            [4, 3, 5, 3, 0],
            [0, 1, 0, 1, 0, 1, 0, 2],
            [1, 0, 1, 0, 2, 0, 2, 0],
            [1, 0, 1, 0, 2, 0, 2, 0, 3]
        ]

        for moves in positions:

            state = state_from_moves(
                self.game, moves
            )

            ref_move, ref_value, _ = (
                self.reference.choose_move(state, 4)
            )

            move, value, _ = (
                self.agent.choose_move(state, 4)
            )

            self.assertEqual(value, ref_value)

            self.assertIn(
                move,
                self.game.actions(state)
            )

            child = self.game.result(state, move)

            if state.player == MAX:

                exact = self.reference.min_value(
                    child, 3, -math.inf, math.inf
                )

            else:

                exact = self.reference.max_value(
                    child, 3, -math.inf, math.inf
                )

            self.assertEqual(exact, ref_value)

    # Test 2: EXACT kaydinin kullanilmasi
    def test_exact_entry(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1]
        )

        key = self.agent.zobrist.hash_state(state)

        first, _ = self.agent._search(
            state, 2, -math.inf, math.inf, key
        )

        self.assertEqual(
            self.agent.tt[key].flag,
            EXACT
        )

        previous_nodes = self.agent.nodes

        second, _ = self.agent._search(
            state, 2, -math.inf, math.inf, key
        )

        self.assertEqual(first, second)

        self.assertEqual(
            self.agent.nodes - previous_nodes,
            1
        )

        self.assertGreater(
            self.agent.tt_cutoffs, 0
        )

    # Test 3: LOWER bayragi ve beta kesmesi
    def test_lower_bound(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 2]
        )

        key = self.agent.zobrist.hash_state(state)

        value, _ = self.agent._search(
            state, 1, -math.inf, 0.5, key
        )

        self.assertEqual(value, 1)

        self.assertEqual(
            self.agent.tt[key].flag,
            LOWER
        )

        previous_nodes = self.agent.nodes

        self.agent._search(
            state, 1, -math.inf, 0.5, key
        )

        self.assertEqual(
            self.agent.nodes - previous_nodes,
            1
        )

    # Test 4: UPPER bayragi ve alfa kesmesi
    def test_upper_bound(self):

        state = state_from_moves(
            self.game,
            [1, 0, 1, 0, 2, 0, 2, 0, 3]
        )

        key = self.agent.zobrist.hash_state(state)

        value, _ = self.agent._search(
            state, 1, -0.5, math.inf, key
        )

        self.assertEqual(value, -1)

        self.assertEqual(
            self.agent.tt[key].flag,
            UPPER
        )

        previous_nodes = self.agent.nodes

        self.agent._search(
            state, 1, -0.5, math.inf, key
        )

        self.assertEqual(
            self.agent.nodes - previous_nodes,
            1
        )

    # Test 5: Farkli derinlikte kayit kontrolu
    def test_depth_validation(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1]
        )

        key = self.agent.zobrist.hash_state(state)

        self.agent._search(
            state, 2, -math.inf, math.inf, key
        )

        previous_nodes = self.agent.nodes

        value, _ = self.agent._search(
            state, 1, -math.inf, math.inf, key
        )

        _, expected, _ = (
            self.reference.choose_move(state, 1)
        )

        self.assertEqual(value, expected)

        self.assertGreater(
            self.agent.nodes - previous_nodes,
            1
        )

    # Test 6: Hash cakismasi kontrolu
    def test_collision_guard(self):

        first = state_from_moves(
            self.game,
            [0, 1, 2]
        )

        second = state_from_moves(
            self.game,
            [0, 1, 3]
        )

        key = self.agent.zobrist.hash_state(first)

        self.agent._search(
            first, 1, -math.inf, math.inf, key
        )

        # Yapay hash cakismasi olustur
        self.agent.tt[key] = replace(
            self.agent.tt[key],
            board=second.board
        )

        self.assertIsNone(
            self.agent.lookup(key, first)
        )

    # Test 7: TT kapali kontrolu
    def test_disabled_table(self):

        agent = TTAlphaBeta(
            self.game,
            evaluator=self.evaluator,
            use_tt=False
        )

        state = self.game.initial_state()

        _, value, _ = agent.choose_move(
            state, 4
        )

        _, expected, _ = (
            self.reference.choose_move(state, 4)
        )

        self.assertEqual(value, expected)

        self.assertEqual(len(agent.tt), 0)
        self.assertEqual(agent.tt_hits, 0)
        self.assertEqual(agent.tt_stores, 0)

    # Test 8: Iterative deepening ve TT
    def test_timed_search(self):

        state = self.game.initial_state()

        result = self.agent.choose_move_timed(
            state,
            time_limit=1.0,
            max_depth=4
        )

        self.assertEqual(result.depth, 4)

        self.assertIn(
            result.move,
            self.game.actions(state)
        )

        self.assertGreater(
            self.agent.tt_hits, 0
        )

        self.assertGreater(
            len(self.agent.tt), 0
        )

        for previous, current in zip(
            result.history,
            result.history[1:]
        ):

            self.assertEqual(
                current.first_move,
                previous.move
            )

    # Test 9: Terminal kontrolu
    def test_terminal_state(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 1, 0]
        )

        move, value, nodes = (
            self.agent.choose_move(state, 4)
        )

        self.assertIsNone(move)
        self.assertEqual(value, 1)
        self.assertEqual(nodes, 1)


if __name__ == "__main__":

    unittest.main()