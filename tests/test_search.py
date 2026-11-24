import unittest

from game import Game, MAX, MIN, state_from_moves
from search import Minimax


class TestMinimax(unittest.TestCase):

    def setUp(self):
        self.game = Game(d=27)
        self.minimax = Minimax(self.game)
        self.state = self.game.initial_state()

    # Test 1: Bos tahta ve dugum sayisi
    def test_empty_board(self):

        move, value, nodes = self.minimax.choose_move(
            self.state, 2
        )

        self.assertEqual(move, 2)
        self.assertEqual(value, 0)
        self.assertEqual(nodes, 43)

    # Test 2: MAX bir hamlede kazanabilir
    def test_max_win(self):

        moves = [0, 1, 0, 1, 0, 1, 0, 2]

        state = state_from_moves(self.game, moves)

        move, value, nodes = self.minimax.choose_move(
            state, 1
        )

        self.assertEqual(move, 0)
        self.assertEqual(value, 1)

    # Test 3: MIN bir hamlede kazanabilir
    def test_min_win(self):

        moves = [1, 0, 1, 0, 2, 0, 2, 0, 3]

        state = state_from_moves(self.game, moves)

        move, value, nodes = self.minimax.choose_move(
            state, 1
        )

        self.assertEqual(move, 0)
        self.assertEqual(value, -1)

    # Test 4: MAX, MIN'in kazanmasini engeller
    def test_block_min(self):

        moves = [1, 0, 1, 0, 2, 0, 2, 0]

        state = state_from_moves(self.game, moves)

        move, value, nodes = self.minimax.choose_move(
            state, 2
        )

        self.assertEqual(move, 0)
        self.assertEqual(value, 0)

    # Test 5: MIN, MAX'in kazanmasini engeller
    def test_block_max(self):

        moves = [0, 1, 0, 1, 0, 2, 0]

        state = state_from_moves(self.game, moves)

        self.assertEqual(state.player, MIN)

        move, value, nodes = self.minimax.choose_move(
            state, 2
        )

        self.assertEqual(move, 0)
        self.assertEqual(value, 0)

    # Test 6: Tekrarlanabilirlik ve sayac sifirlama
    def test_deterministic(self):

        result1 = self.minimax.choose_move(
            self.state, 2
        )

        self.minimax.choose_move(self.state, 4)

        result2 = self.minimax.choose_move(
            self.state, 2
        )

        self.assertEqual(result1, result2)

    # Test 7: Terminal durumda arama
    def test_terminal_state(self):

        moves = [0, 1, 0, 1, 0, 1, 0, 1, 0]

        state = state_from_moves(self.game, moves)

        move, value, nodes = self.minimax.choose_move(
            state, 2
        )

        self.assertIsNone(move)
        self.assertEqual(value, 1)
        self.assertEqual(nodes, 1)

    # Test 8: Gecersiz derinlik
    def test_invalid_depth(self):

        with self.assertRaises(ValueError):
            self.minimax.choose_move(self.state, 0)

        with self.assertRaises(ValueError):
            self.minimax.choose_move(self.state, -1)

    # Test 9: Arama sirasinda tahta degismemeli
    def test_state_immutable(self):

        moves = [0, 1, 2, 3]

        state = state_from_moves(self.game, moves)

        original_board = state.board
        original_player = state.player
        original_last_move = state.last_move

        self.minimax.choose_move(state, 4)

        self.assertEqual(state.board, original_board)
        self.assertEqual(state.player, original_player)

        self.assertEqual(
            state.last_move,
            original_last_move
        )

    # Test 10: Derinlik siniri kontrolu
    def test_depth_limit(self):

        move, value, nodes = self.minimax.choose_move(
            self.state, 1
        )

        self.assertEqual(move, 2)
        self.assertEqual(value, 0)
        self.assertEqual(nodes, 7)


if __name__ == "__main__":
    unittest.main()