import unittest

from dataclasses import replace

from game import Game, MAX, MIN, state_from_moves
from evaluate import Evaluator
from agirliklar import WEIGHT_SETS, create_evaluator


class TestEvalQuality(unittest.TestCase):

    # Test 1: Tum agirliklarda ayna simetrisi
    def test_all_weight_mirror_symmetry(self):

        moves = [4, 3, 5, 3, 0]

        for variant in (0, 1, 2):

            game = Game(d=27, V=variant)

            mirror_moves = [
                game.C - 1 - col
                for col in moves
            ]

            state = state_from_moves(game, moves)

            mirrored = state_from_moves(
                game, mirror_moves
            )

            for name in WEIGHT_SETS:

                evaluator = create_evaluator(
                    game, name
                )

                with self.subTest(
                    variant=variant,
                    weight=name
                ):

                    self.assertAlmostEqual(
                        evaluator.evaluate(state),
                        evaluator.evaluate(mirrored)
                    )

    # Test 2: Silindirde temel oznitelikler korunmali
    def test_rotation_base_features(self):

        game = Game(d=27)

        evaluator = Evaluator(game)

        moves = [4, 3, 5, 3, 0]

        rotated_moves = [
            (col + 2) % game.C
            for col in moves
        ]

        state = state_from_moves(game, moves)

        rotated = state_from_moves(
            game, rotated_moves
        )

        first = evaluator.features(state)

        second = evaluator.features(rotated)

        for key in (
            "max_k1",
            "max_k2",
            "min_k1",
            "min_k2"
        ):

            self.assertEqual(first[key], second[key])

    # Test 3: Sarma agirliginin donmeye etkisi
    def test_rotation_wrap_effect(self):

        game = Game(d=27)

        evaluator = Evaluator(game)

        state = state_from_moves(
            game, [4, 3, 5, 3, 0]
        )

        rotated = state_from_moves(
            game, [0, 5, 1, 5, 2]
        )

        self.assertEqual(
            evaluator.raw_score(state), 5
        )

        self.assertEqual(
            evaluator.raw_score(rotated), 3
        )

        self.assertNotEqual(
            evaluator.evaluate(state),
            evaluator.evaluate(rotated)
        )

    # Test 4: Oyuncular degisirse isaret degismeli
    def test_player_swap_symmetry(self):

        game = Game(d=27)

        state = state_from_moves(
            game,
            [0, 1, 0, 1, 0, 1, 0, 2]
        )

        swapped_board = tuple(
            tuple(
                -cell if cell in (MAX, MIN) else cell
                for cell in row
            )
            for row in state.board
        )

        swapped = replace(
            state,
            board=swapped_board,
            player=-state.player
        )

        for name in WEIGHT_SETS:

            evaluator = create_evaluator(game, name)

            self.assertAlmostEqual(
                evaluator.evaluate(state),
                -evaluator.evaluate(swapped)
            )

    # Test 5: Engelli hucreler pencereye dahil edilmemeli
    def test_blocked_window_quality(self):

        game = Game(d=27, V=3)

        evaluator = Evaluator(game)

        unavailable = evaluator.unavailable_cells()

        for window in evaluator.windows:

            self.assertTrue(
                set(window.cells).isdisjoint(unavailable)
            )

        state = game.initial_state()

        self.assertEqual(
            evaluator.evaluate(state), 0
        )


if __name__ == "__main__":

    unittest.main()