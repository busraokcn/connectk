from dataclasses import dataclass
import random


# Hücre ve oyuncu değerleri
EMPTY = 0
MAX = 1
MIN = -1
BLOCKED = 2


@dataclass(frozen=True)
class State:
    board: tuple
    player: int
    last_move: tuple | None = None


class Game:

    def __init__(self, d=27, R=None, C=None, K=None, V=None):
        self.d = d

        self.R = 5 + (d % 3) if R is None else R
        self.C = 6 + ((d // 3) % 3) if C is None else C
        self.K = 4 + ((d // 9) % 2) if K is None else K
        self.V = (d // 18) % 4 if V is None else V

    # Başlangıç tahtası
    def initial_state(self):
        board = [
            [EMPTY for c in range(self.C)]
            for r in range(self.R)
        ]

        if self.V == 3:
            rng = random.Random(self.d)
            obstacles = set()

            while len(obstacles) < 2:
                r = rng.randrange(self.R)
                c = rng.randrange(self.C)
                obstacles.add((r, c))

            for r, c in obstacles:
                board[r][c] = BLOCKED

        immutable_board = tuple(
            tuple(row) for row in board
        )

        return State(
            board=immutable_board,
            player=MAX
        )

    # Taşın düşeceği satırı bulma
    def _landing_row(self, state, col):
        for row in range(self.R):
            if state.board[row][col] != EMPTY:
                if row == 0:
                    return None

                return row - 1

        return self.R - 1

    # Yasal hamleleri belirleme
    def actions(self, state):
        if self.is_terminal(state):
            return []

        legal_moves = []

        for col in range(self.C):
            if self._landing_row(state, col) is not None:
                legal_moves.append(col)

        return legal_moves

    # Taş yerleştirme
    def result(self, state, action):
        if self.is_terminal(state):
            raise ValueError("Oyun zaten bitti")

        if not 0 <= action < self.C:
            raise ValueError("Gecersiz sutun numarasi")

        row = self._landing_row(state, action)

        if row is None:
            raise ValueError("Bu sutuna tas yerlestirilemez")

        new_board = [list(r) for r in state.board]

        new_board[row][action] = state.player

        immutable_board = tuple(
            tuple(r) for r in new_board
        )

        return State(
            board=immutable_board,
            player=-state.player,
            last_move=(row, action)
        )

    # K taşı dizen oyuncuyu bulma
    def line_player(self, state):

        if state.last_move is None:
            return None

        row, col = state.last_move
        player = state.board[row][col]

        if player not in (MAX, MIN):
            return None

        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1)
        ]

        for dr, dc in directions:

            if dr == 0 and self.K > self.C:
                continue

            count = 1

            for sign in (1, -1):

                for step in range(1, self.K):

                    new_row = row + sign * step * dr
                    new_col = col + sign * step * dc

                    if not 0 <= new_row < self.R:
                        break

                    if self.V == 1:
                        new_col = new_col % self.C

                    elif not 0 <= new_col < self.C:
                        break

                    if state.board[new_row][new_col] != player:
                        break

                    count += 1

                    if count >= self.K:
                        return player

        return None

    # Oyunun bitip bitmediğini kontrol etme
    def is_terminal(self, state):

        # K taşı dizen oyuncu varsa oyun biter
        if self.line_player(state) is not None:
            return True

        # Hamle yapılabilecek sütun kaldı mı?
        for col in range(self.C):
            if self._landing_row(state, col) is not None:
                return False

        # Hiç hamle kalmadıysa oyun biter
        return True

    # Oyunun fayda değerini hesaplama
    def utility(self, state):

        player = self.line_player(state)

        if player is not None:

            # Misere varyantında dizen oyuncu kaybeder
            if self.V == 2:
                return -player

            return player

        # Kimse kazanmadı ve hamle kalmadı
        if self.is_terminal(state):
            return 0

        raise ValueError("Oyun henuz bitmedi")

    # Tahtayı terminalde gösterme
    def print_board(self, state):
        symbols = {
            EMPTY: ".",
            MAX: "X",
            MIN: "O",
            BLOCKED: "#"
        }

        for row in state.board:
            print(" ".join(symbols[cell] for cell in row))

        print("-" * (self.C * 2 - 1))
        print(" ".join(str(c) for c in range(self.C)))


# Hamle dizisinden oyun durumu oluşturma
def state_from_moves(game, moves):
    state = game.initial_state()

    for move in moves:
        state = game.result(state, move)

    return state


# Programı test etme
if __name__ == "__main__":

    game = Game(d=27)

    print("CONNECT-K ARENA")
    print("R:", game.R)
    print("C:", game.C)
    print("K:", game.K)
    print("V:", game.V)
    print("d:", game.d)

    # Test 1: Başlangıç durumu
    state = game.initial_state()

    assert game.is_terminal(state) is False
    print("\nTest 1: Baslangic durumu - BASARILI")

    # Test 2: MAX yatay kazanıyor
    moves = [0, 0, 1, 1, 2, 2, 3, 3, 4]
    state = state_from_moves(game, moves)

    assert game.is_terminal(state) is True
    assert game.utility(state) == 1

    print("Test 2: MAX yatay kazanma - BASARILI")

    # Test 3: MAX dikey kazanıyor
    moves = [0, 1, 0, 1, 0, 1, 0, 1, 0]
    state = state_from_moves(game, moves)

    assert game.is_terminal(state) is True
    assert game.utility(state) == 1

    print("Test 3: MAX dikey kazanma - BASARILI")

    # Test 4: Silindir kazanması
    moves = [4, 4, 5, 5, 0, 0, 1, 1, 2]
    state = state_from_moves(game, moves)

    assert game.is_terminal(state) is True
    assert game.utility(state) == 1

    print("Test 4: Silindir kazanmasi - BASARILI")

    # Test 5: Standart varyant
    standard_game = Game(d=27, V=0)
    state = state_from_moves(standard_game, moves)

    assert standard_game.is_terminal(state) is False

    print("Test 5: Standart varyant - BASARILI")

    # Test 6: MIN kazanıyor
    moves = [1, 0, 1, 0, 2, 0, 2, 0, 3, 0]
    state = state_from_moves(game, moves)

    assert game.is_terminal(state) is True
    assert game.utility(state) == -1

    print("Test 6: MIN kazanmasi - BASARILI")

    # Test 7: Oyun bittikten sonra yasal hamle yok
    assert game.actions(state) == []

    print("Test 7: Terminal durumda actions - BASARILI")

    # Test 8: Biten oyuna taş eklenememesi
    try:
        game.result(state, 5)
    except ValueError:
        print("Test 8: Terminal durumda result - BASARILI")
    else:
        raise AssertionError("Biten oyunda hamle yapildi")

    # Test 9: Misere varyantı
    misere_game = Game(d=27, V=2)

    moves = [0, 0, 1, 1, 2, 2, 3, 3, 4]
    state = state_from_moves(misere_game, moves)

    assert misere_game.is_terminal(state) is True
    assert misere_game.utility(state) == -1

    print("Test 9: Misere varyanti - BASARILI")

    # Test 10: Beraberlik
    moves = [
        4, 0, 3, 2, 0, 0, 1, 5, 4, 3,
        5, 2, 2, 0, 2, 3, 1, 5, 3, 4,
        4, 5, 0, 2, 4, 5, 1, 3, 1, 1
    ]

    state = state_from_moves(game, moves)

    assert game.is_terminal(state) is True
    assert game.utility(state) == 0

    print("Test 10: Beraberlik - BASARILI")

    # Test 11: Bitmemiş oyunda utility
    try:
        game.utility(game.initial_state())
    except ValueError:
        print("Test 11: Bitmemis oyun - BASARILI")
    else:
        raise AssertionError("Bitmemis oyunda utility hesaplandi")

    print("\nTum terminal ve utility kontrolleri basarili!")