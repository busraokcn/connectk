import unittest
import random

from unittest.mock import patch

from game import Game, state_from_moves
from timed_search import SearchTimeout
from tt_search import TTAlphaBeta
from threat_search import ThreatAlphaBeta
from agirliklar import create_evaluator


class TestFinalSearch(unittest.TestCase):

    def setUp(self):

        self.game = Game(d=27)

        self.evaluator = create_evaluator(
            self.game, "W3"
        )

        self.agent = ThreatAlphaBeta(
            self.game,
            order="A",
            evaluator=self.evaluator,
            use_tt=True
        )

    # ======================================
    # TEST 1: Son tamamlanan derinligi koru
    # ======================================

    def test_timeout_keeps_completed_depth(self):

        state = self.game.initial_state()

        original_check = self.agent.check_time

        def simulated_timeout(force=False):

            # Ilk iterasyon tamamlansin.
            # Ikinci iterasyon yarida kesilsin.
            if (
                self.agent._preferred_move is not None
                and self.agent.nodes >= 3
            ):

                raise SearchTimeout(
                    "Yapay zaman asimi"
                )

            original_check(force=force)

        with patch.object(
            self.agent,
            "check_time",
            side_effect=simulated_timeout
        ):

            result = self.agent.choose_move_timed(
                state,
                time_limit=1.0,
                max_depth=5
            )

        self.assertTrue(result.timed_out)

        self.assertEqual(result.depth, 1)

        self.assertEqual(len(result.history), 1)

        last = result.history[-1]

        self.assertEqual(result.move, last.move)

        self.assertEqual(result.value, last.value)

        self.assertGreater(result.nodes, last.nodes)

        self.assertIsNone(self.agent._deadline)

    # ======================================
    # TEST 2: Ilk derinlik bile tamamlanamazsa
    # ======================================

    def test_timeout_before_first_depth(self):

        state = self.game.initial_state()

        with patch.object(
            self.agent,
            "check_time",
            side_effect=SearchTimeout(
                "Yapay zaman asimi"
            )
        ):

            result = self.agent.choose_move_timed(
                state,
                time_limit=1.0
            )

        self.assertTrue(result.timed_out)

        self.assertEqual(result.depth, 0)

        self.assertIsNone(result.value)

        self.assertEqual(result.history, ())

        self.assertIn(
            result.move,
            self.game.actions(state)
        )

        self.assertIsNone(self.agent._deadline)

    # ======================================
    # TEST 3: Terminal durumda zamanli arama
    # ======================================

    def test_timed_terminal_state(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 1, 0]
        )

        result = self.agent.choose_move_timed(
            state,
            time_limit=1.0
        )

        self.assertIsNone(result.move)

        self.assertEqual(result.value, 1)

        self.assertEqual(result.depth, 0)

        self.assertFalse(result.timed_out)

    # ======================================
    # TEST 4: Dort varyantta TT dogrulugu
    # ======================================

    def test_all_variants_fixed_depth(self):

        for variant in range(4):

            game = Game(
                d=27,
                R=7,
                C=8,
                K=5,
                V=variant
            )

            evaluator = create_evaluator(
                game, "W3"
            )

            rng = random.Random(27)

            state = game.initial_state()

            for _ in range(8):

                if game.is_terminal(state):
                    break

                move = rng.choice(
                    game.actions(state)
                )

                state = game.result(
                    state, move
                )

            self.assertFalse(
                game.is_terminal(state)
            )

            for agent_class in (
                TTAlphaBeta,
                ThreatAlphaBeta
            ):

                with self.subTest(
                    variant=variant,
                    method=agent_class.__name__
                ):

                    on = agent_class(
                        game,
                        evaluator=evaluator,
                        use_tt=True
                    )

                    off = agent_class(
                        game,
                        evaluator=evaluator,
                        use_tt=False
                    )

                    on_move, on_value, _ = (
                        on.choose_move(state, 3)
                    )

                    off_move, off_value, _ = (
                        off.choose_move(state, 3)
                    )

                    self.assertEqual(
                        on_value, off_value
                    )

                    self.assertIn(
                        on_move,
                        game.actions(state)
                    )

                    self.assertIn(
                        off_move,
                        game.actions(state)
                    )

                    # Secilen hamlenin degerini
                    # TT kapali olarak dogrula.
                    child = game.result(
                        state, on_move
                    )

                    _, exact_value, _ = (
                        off.choose_move(child, 2)
                    )

                    self.assertEqual(
                        exact_value, on_value
                    )

    # ======================================
    # TEST 5: Zaman asimindan sonra yeni arama
    # ======================================

    def test_reuse_after_timeout(self):

        state = self.game.initial_state()

        with patch.object(
            self.agent,
            "check_time",
            side_effect=SearchTimeout(
                "Yapay zaman asimi"
            )
        ):

            first = self.agent.choose_move_timed(
                state,
                time_limit=1.0
            )

        self.assertTrue(first.timed_out)

        second = self.agent.choose_move_timed(
            state,
            time_limit=1.0,
            max_depth=3
        )

        self.assertEqual(second.depth, 3)

        self.assertFalse(second.timed_out)

        self.assertIsNone(self.agent._deadline)

        self.assertIn(
            second.move,
            self.game.actions(state)
        )

    # ======================================
    # TEST 6: Gecersiz sure parametresi
    # ======================================

    def test_invalid_time_limit(self):

        state = self.game.initial_state()

        for invalid in (
            0, -1, float("inf"), float("nan")
        ):

            with self.subTest(limit=invalid):

                with self.assertRaises(ValueError):

                    self.agent.choose_move_timed(
                        state,
                        time_limit=invalid
                    )


if __name__ == "__main__":

    unittest.main()