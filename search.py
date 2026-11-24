from game import Game, MAX, MIN, state_from_moves
import math


class Minimax:

    def __init__(self, game):
        self.game = game
        self.nodes = 0

    # Geçici değerlendirme fonksiyonu
    def evaluate(self, state):
        return 0

    # Merkeze yakın hamlelere öncelik ver
    def ordered_actions(self, state):

        center = (self.game.C - 1) / 2

        return sorted(
            self.game.actions(state),
            key=lambda col: (abs(col - center), col)
        )

    # MAX oyuncusunun değerini hesapla
    def max_value(self, state, depth):

        self.nodes += 1

        # Oyun bittiyse gerçek faydayı döndür
        if self.game.is_terminal(state):
            return self.game.utility(state)

        # Derinlik sınırına ulaşıldıysa
        if depth == 0:
            return self.evaluate(state)

        value = -math.inf

        for action in self.ordered_actions(state):

            new_state = self.game.result(state, action)

            value = max(
                value,
                self.min_value(new_state, depth - 1)
            )

        return value

    # MIN oyuncusunun değerini hesapla
    def min_value(self, state, depth):

        self.nodes += 1

        # Oyun bittiyse gerçek faydayı döndür
        if self.game.is_terminal(state):
            return self.game.utility(state)

        # Derinlik sınırına ulaşıldıysa
        if depth == 0:
            return self.evaluate(state)

        value = math.inf

        for action in self.ordered_actions(state):

            new_state = self.game.result(state, action)

            value = min(
                value,
                self.max_value(new_state, depth - 1)
            )

        return value

    # En iyi hamleyi seç
    def choose_move(self, state, depth):

        if depth < 1:
            raise ValueError("Derinlik en az 1 olmali")

        # Kök düğüm de sayılır
        self.nodes = 1

        if self.game.is_terminal(state):
            return None, self.game.utility(state), self.nodes

        best_move = None

        if state.player == MAX:

            best_value = -math.inf

            for action in self.ordered_actions(state):

                new_state = self.game.result(state, action)

                value = self.min_value(
                    new_state, depth - 1
                )

                if value > best_value:

                    best_value = value
                    best_move = action

        else:

            best_value = math.inf

            for action in self.ordered_actions(state):

                new_state = self.game.result(state, action)

                value = self.max_value(
                    new_state, depth - 1
                )

                if value < best_value:

                    best_value = value
                    best_move = action

        return best_move, best_value, self.nodes


# Minimax algoritmasını test et
if __name__ == "__main__":

    game = Game(d=27)
    minimax = Minimax(game)

    print("CONNECT-K ARENA - MINIMAX")
    print("R:", game.R)
    print("C:", game.C)
    print("K:", game.K)
    print("V:", game.V)

    # Test 1: Boş tahta
    state = game.initial_state()

    move, value, nodes = minimax.choose_move(state, 2)

    print("\nTEST 1: BOS TAHTA")
    game.print_board(state)

    print("Secilen hamle:", move)
    print("Minimax degeri:", value)
    print("Dugum sayisi:", nodes)

    assert move == 2
    assert value == 0
    assert nodes == 43

    print("BASARILI")

    # Test 2: MAX bir hamlede kazanabilir
    moves = [0, 1, 0, 1, 0, 1, 0, 2]

    state = state_from_moves(game, moves)

    move, value, nodes = minimax.choose_move(state, 2)

    print("\nTEST 2: MAX KAZANMA HAMLESI")
    game.print_board(state)

    print("Secilen hamle:", move)
    print("Minimax degeri:", value)
    print("Dugum sayisi:", nodes)

    assert move == 0
    assert value == 1

    print("BASARILI")

    # Test 3: Rakibin kazanmasını engelle
    moves = [1, 0, 1, 0, 2, 0, 2, 0]

    state = state_from_moves(game, moves)

    move, value, nodes = minimax.choose_move(state, 2)

    print("\nTEST 3: RAKIBI ENGELLEME")
    game.print_board(state)

    print("Secilen hamle:", move)
    print("Minimax degeri:", value)
    print("Dugum sayisi:", nodes)

    assert move == 0
    assert value == 0

    print("BASARILI")

    # Test 4: MIN bir hamlede kazanabilir
    moves = [1, 0, 1, 0, 2, 0, 2, 0, 3]

    state = state_from_moves(game, moves)

    move, value, nodes = minimax.choose_move(state, 2)

    print("\nTEST 4: MIN KAZANMA HAMLESI")
    game.print_board(state)

    print("Secilen hamle:", move)
    print("Minimax degeri:", value)
    print("Dugum sayisi:", nodes)

    assert move == 0
    assert value == -1

    print("BASARILI")

    # Test 5: Aynı durumda aynı sonuç
    state = game.initial_state()

    result1 = minimax.choose_move(state, 2)
    result2 = minimax.choose_move(state, 2)

    assert result1 == result2

    print("\nTEST 5: TEKRARLANABILIRLIK - BASARILI")

    print("\nTum Minimax kontrolleri basarili!")