import unittest
import math

from game import Game, state_from_moves
from evaluate import Evaluator


class TestEvaluator(unittest.TestCase):

    def setUp(self):

        self.game = Game(d=27)

        self.evaluator = Evaluator(self.game)

    # Test 1: Bos tahtada tum oznitelikler sifir
    def test_empty_features(self):

        state = self.game.initial_state()

        features = self.evaluator.features(state)

        self.assertTrue(
            all(value == 0 for value in features.values())
        )

    # Test 2: MAX K-1 penceresi
    def test_max_k1(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 2]
        )

        features = self.evaluator.features(state)

        self.assertEqual(features["max_k1"], 1)
        self.assertEqual(features["min_k2"], 1)
        self.assertEqual(features["min_k1"], 0)

    # Test 3: MAX K-2 penceresi
    def test_max_k2(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0]
        )

        features = self.evaluator.features(state)

        self.assertEqual(features["max_k2"], 1)
        self.assertEqual(features["max_k1"], 0)

    # Test 4: MIN K-1 penceresi
    def test_min_k1(self):

        state = state_from_moves(
            self.game,
            [1, 0, 1, 0, 2, 0, 2, 0]
        )

        features = self.evaluator.features(state)

        self.assertEqual(features["min_k1"], 1)
        self.assertEqual(features["max_k1"], 0)

    # Test 5: MIN K-2 penceresi
    def test_min_k2(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1]
        )

        features = self.evaluator.features(state)

        self.assertEqual(features["min_k2"], 1)

    # Test 6: Karisik pencereler
    def test_mixed_window(self):

        state = state_from_moves(
            self.game,
            [0, 0, 0, 1, 0, 1, 0]
        )

        features = self.evaluator.features(state)

        self.assertTrue(
            all(value == 0 for value in features.values())
        )

    # Test 7: Sarmali pencereler
    def test_wrapped_features(self):

        state = state_from_moves(
            self.game,
            [4, 4, 5, 5, 0, 0, 1, 1]
        )

        features = self.evaluator.features(state)

        expected = {
            "max_k1": 2,
            "max_k2": 4,
            "min_k1": 2,
            "min_k2": 4,
            "max_wrap": 4,
            "min_wrap": 4
        }

        self.assertEqual(features, expected)

    # Test 8: Standart varyantta sarma yok
    def test_standard_no_wrap(self):

        game = Game(d=27, V=0)

        evaluator = Evaluator(game)

        state = state_from_moves(
            game,
            [4, 4, 5, 5, 0, 0, 1, 1]
        )

        features = evaluator.features(state)

        self.assertEqual(features["max_wrap"], 0)
        self.assertEqual(features["min_wrap"], 0)

    # Test 9: Sol-sag ayna simetrisi
    def test_mirror_features(self):

        moves = [4, 4, 5, 5, 0, 0, 1, 1]

        mirrored_moves = [
            self.game.C - 1 - col
            for col in moves
        ]

        state = state_from_moves(
            self.game, moves
        )

        mirrored_state = state_from_moves(
            self.game, mirrored_moves
        )

        self.assertEqual(
            self.evaluator.features(state),
            self.evaluator.features(mirrored_state)
        )
            # Test 10: Bos tahta degerlendirmesi
    def test_empty_evaluation(self):

        state = self.game.initial_state()

        self.assertEqual(
            self.evaluator.evaluate(state), 0
        )

    # Test 11: MAX avantajli konum
    def test_positive_evaluation(self):

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 2]
        )

        self.assertEqual(
            self.evaluator.raw_score(state), 9
        )

        self.assertAlmostEqual(
            self.evaluator.evaluate(state),
            math.tanh(9 / 30)
        )

    # Test 12: MIN avantajli konum
    def test_negative_evaluation(self):

        state = state_from_moves(
            self.game,
            [1, 0, 1, 0, 2, 0, 2, 0]
        )

        self.assertEqual(
            self.evaluator.raw_score(state), -12
        )

        self.assertAlmostEqual(
            self.evaluator.evaluate(state),
            math.tanh(-12 / 30)
        )

    # Test 13: Dengeli konum
    def test_balanced_evaluation(self):

        state = state_from_moves(
            self.game,
            [4, 4, 5, 5, 0, 0, 1, 1]
        )

        self.assertEqual(
            self.evaluator.evaluate(state), 0
        )

    # Test 14: Ayna simetrisi
    def test_evaluation_symmetry(self):

        moves = [4, 3, 5, 3, 0]

        mirrored_moves = [
            self.game.C - 1 - col
            for col in moves
        ]

        state = state_from_moves(
            self.game, moves
        )

        mirrored_state = state_from_moves(
            self.game, mirrored_moves
        )

        self.assertAlmostEqual(
            self.evaluator.evaluate(state),
            self.evaluator.evaluate(mirrored_state)
        )

    # Test 15: Misere isaret kontrolu
    def test_misere_evaluation(self):

        normal_game = Game(d=27, V=0)

        misere_game = Game(d=27, V=2)

        moves = [0, 1, 0, 1, 0, 1, 0, 2]

        normal_state = state_from_moves(
            normal_game, moves
        )

        misere_state = state_from_moves(
            misere_game, moves
        )

        normal = Evaluator(normal_game)

        misere = Evaluator(misere_game)

        self.assertGreater(
            normal.evaluate(normal_state), 0
        )

        self.assertLess(
            misere.evaluate(misere_state), 0
        )

        self.assertAlmostEqual(
            normal.evaluate(normal_state),
            -misere.evaluate(misere_state)
        )

    # Test 16: Farkli agirlik kullanimi
    def test_custom_weights(self):

        weights = dict(self.evaluator.weights)

        weights["max_k1"] = 24

        evaluator = Evaluator(
            self.game,
            weights=weights
        )

        state = state_from_moves(
            self.game,
            [0, 1, 0, 1, 0, 1, 0, 2]
        )

        self.assertEqual(
            evaluator.raw_score(state), 21
        )

        self.assertGreater(
            evaluator.evaluate(state),
            self.evaluator.evaluate(state)
        )

    # Test 17: Eval sinir kontrolu
    def test_evaluation_bounds(self):

        weights = dict(self.evaluator.weights)

        weights["max_k1"] = 1000000
        weights["min_k1"] = 1000000

        evaluator = Evaluator(
            self.game,
            weights=weights
        )

        positions = [
            [0, 1, 0, 1, 0, 1, 0, 2],
            [1, 0, 1, 0, 2, 0, 2, 0]
        ]

        for moves in positions:

            state = state_from_moves(
                self.game, moves
            )

            value = evaluator.evaluate(state)

            self.assertGreater(value, -1)
            self.assertLess(value, 1)


if __name__ == "__main__":
    unittest.main()