import unittest

from game import (
    Game,
    State,
    EMPTY,
    MAX,
    MIN,
    BLOCKED,
    state_from_moves
)

from perft import perft


class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game(d=27)
        self.state = self.game.initial_state()

    # Kazanma hamlesinden önce oyun devam etmeli
    def check_win(self, moves, expected=MAX):

        before = state_from_moves(self.game, moves[:-1])

        self.assertFalse(self.game.is_terminal(before))

        after = self.game.result(before, moves[-1])

        self.assertTrue(self.game.is_terminal(after))
        self.assertEqual(self.game.utility(after), expected)

    # Test 1: Başlangıç durumu
    def test_initial_state(self):

        self.assertEqual(len(self.state.board), 5)
        self.assertEqual(len(self.state.board[0]), 6)
        self.assertEqual(self.state.player, MAX)

        for row in self.state.board:
            for cell in row:
                self.assertEqual(cell, EMPTY)

        self.assertEqual(
            self.game.actions(self.state),
            [0, 1, 2, 3, 4, 5]
        )

        self.assertFalse(self.game.is_terminal(self.state))

    # Test 2: Yerçekimi ve değiştirilemez tahta
    def test_gravity_and_immutable(self):

        state1 = self.game.result(self.state, 2)
        state2 = self.game.result(state1, 2)

        self.assertEqual(state1.board[4][2], MAX)
        self.assertEqual(state2.board[3][2], MIN)

        self.assertEqual(self.state.board[4][2], EMPTY)
        self.assertEqual(state1.board[3][2], EMPTY)

        self.assertEqual(state1.player, MIN)
        self.assertEqual(state2.player, MAX)

        self.assertIsInstance(state1.board, tuple)
        self.assertIsInstance(state1.board[0], tuple)

    # Test 3: Dolu sütun ve geçersiz hamle
    def test_full_column(self):

        state = state_from_moves(
            self.game, [0, 0, 0, 0, 0]
        )

        self.assertNotIn(0, self.game.actions(state))

        with self.assertRaises(ValueError):
            self.game.result(state, 0)

        with self.assertRaises(ValueError):
            self.game.result(state, -1)

        with self.assertRaises(ValueError):
            self.game.result(state, 6)

    # Test 4: Yatay kazanma
    def test_horizontal_win(self):

        moves = [0, 0, 1, 1, 2, 2, 3, 3, 4]

        self.check_win(moves)

    # Test 5: Dikey kazanma
    def test_vertical_win(self):

        moves = [0, 1, 0, 1, 0, 1, 0, 1, 0]

        self.check_win(moves)

    # Test 6: Birinci çapraz kazanma
    def test_diagonal_right(self):

        moves = [
            0, 3, 1, 2, 3, 2, 2, 5, 1, 0,
            4, 0, 1, 0, 2, 4, 0, 3, 1
        ]

        self.check_win(moves)

    # Test 7: İkinci çapraz kazanma
    def test_diagonal_left(self):

        moves = [
            5, 2, 4, 3, 2, 3, 3, 0, 4, 5,
            1, 5, 4, 5, 3, 1, 5, 2, 4
        ]

        self.check_win(moves)

    # Test 8: Silindir yatay kazanma
    def test_cylinder_horizontal(self):

        moves = [4, 4, 5, 5, 0, 0, 1, 1, 2]

        self.check_win(moves)

        standard_game = Game(d=27, V=0)

        state = state_from_moves(standard_game, moves)

        self.assertFalse(
            standard_game.is_terminal(state)
        )

    # Test 9: Silindir çapraz kazanma
    def test_cylinder_diagonal(self):

        moves = [
            0, 0, 0, 5, 5, 5, 1, 4, 2, 4,
            4, 4, 0, 3, 3, 1, 5, 3, 0
        ]

        self.check_win(moves)

        standard_game = Game(d=27, V=0)

        state = state_from_moves(standard_game, moves)

        self.assertFalse(
            standard_game.is_terminal(state)
        )

    # Test 10: MIN oyuncusunun kazanması
    def test_min_win(self):

        moves = [1, 0, 1, 0, 2, 0, 2, 0, 3, 0]

        self.check_win(moves, expected=MIN)

    # Test 11: Misere varyantı
    def test_misere(self):

        game = Game(d=27, V=2)

        moves = [0, 0, 1, 1, 2, 2, 3, 3, 4]

        state = state_from_moves(game, moves)

        self.assertTrue(game.is_terminal(state))
        self.assertEqual(game.utility(state), -1)

    # Test 12: Beraberlik
    def test_draw(self):

        moves = [
            4, 0, 3, 2, 0, 0, 1, 5, 4, 3,
            5, 2, 2, 0, 2, 3, 1, 5, 3, 4,
            4, 5, 0, 2, 4, 5, 1, 3, 1, 1
        ]

        state = state_from_moves(self.game, moves)

        self.assertTrue(self.game.is_terminal(state))
        self.assertEqual(self.game.utility(state), 0)

    # Test 13: Terminal durumda hamle engelleme
    def test_terminal(self):

        moves = [0, 1, 0, 1, 0, 1, 0, 1, 0]

        state = state_from_moves(self.game, moves)

        self.assertEqual(self.game.actions(state), [])

        with self.assertRaises(ValueError):
            self.game.result(state, 5)

        with self.assertRaises(ValueError):
            self.game.utility(self.state)

    # Test 14: Engelli oyun varyantı
    def test_blocked_cells(self):

        game = Game(d=27, V=3)
        state = game.initial_state()

        obstacles = []

        for r in range(game.R):
            for c in range(game.C):
                if state.board[r][c] == BLOCKED:
                    obstacles.append((r, c))

        self.assertEqual(len(obstacles), 2)

        # Aynı seed aynı engelleri üretmeli
        self.assertEqual(state, game.initial_state())

        row, col = min(obstacles)

        # Engel üst satırda değilse taş üstüne düşmeli
        if row > 0:

            new_state = game.result(state, col)

            self.assertEqual(
                new_state.board[row - 1][col],
                MAX
            )

            self.assertEqual(
                new_state.board[row][col],
                BLOCKED
            )

            # Engelin altında kalan hücreler değişmemeli
            for r in range(row + 1, game.R):
                self.assertEqual(
                    new_state.board[r][col],
                    state.board[r][col]
                )

            # Engelin üstündeki boşlukları doldur
            for i in range(row - 1):
                new_state = game.result(new_state, col)

            self.assertNotIn(col, game.actions(new_state))

        else:
            self.assertNotIn(col, game.actions(state))

    # Test 15: Boş tahtada Perft
    def test_perft_empty(self):

        expected = [
            1, 6, 36, 216, 1296, 7776, 46650
        ]

        for depth, value in enumerate(expected):

            with self.subTest(depth=depth):

                self.assertEqual(
                    perft(self.game, self.state, depth),
                    value
                )

    # Test 16: Yarı dolu ve terminal Perft
    def test_perft_positions(self):

        state = state_from_moves(
            self.game, [0, 0, 0, 0, 0]
        )

        self.assertEqual(perft(self.game, state, 1), 5)
        self.assertEqual(perft(self.game, state, 2), 25)
        self.assertEqual(perft(self.game, state, 3), 125)
        self.assertEqual(perft(self.game, state, 4), 625)

        state = state_from_moves(
            self.game, [0, 1, 0, 1, 0, 1, 0, 2]
        )

        self.assertEqual(perft(self.game, state, 1), 6)
        self.assertEqual(perft(self.game, state, 2), 31)
        self.assertEqual(perft(self.game, state, 3), 175)
        self.assertEqual(perft(self.game, state, 4), 882)

        state = state_from_moves(
            self.game, [0, 1, 0, 1, 0, 1, 0, 1, 0]
        )

        self.assertEqual(perft(self.game, state, 4), 1)


if __name__ == "__main__":
    unittest.main()