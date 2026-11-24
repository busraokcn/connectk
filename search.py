from game import Game, MAX, MIN, state_from_moves
import math
from dataclasses import replace


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

class AlphaBeta(Minimax):

    def __init__(self, game, order="A"):

        super().__init__(game)

        if order not in ("A", "B", "C"):
            raise ValueError("Gecersiz siralama yontemi")

        self.order = order

    # Merkeze olan uzaklik
    def center_distance(self, col):

        center = (self.game.C - 1) / 2

        return abs(col - center)

    # Hamle siralama yontemleri
    def ordered_actions(self, state):

        actions = self.game.actions(state)

        # Yontem A: Siralamasiz
        if self.order == "A":
            return actions

        # Yontem B: Merkezden disari
        if self.order == "B":

            return sorted(
                actions,
                key=lambda col: (
                    self.center_distance(col),
                    col
                )
            )

        # Yontem C: Kazanma ve engelleme
        if not actions:
            return []

        player = state.player

        winning_moves = set()
        losing_moves = set()
        opponent_threats = set()

        # Kendi kazanma ve kaybetme hamlelerimiz
        for action in actions:

            child = self.game.result(state, action)

            if self.game.is_terminal(child):

                value = self.game.utility(child)

                if value == player:
                    winning_moves.add(action)

                elif value == -player:
                    losing_moves.add(action)

        # Rakibin sirasi olsaydi ne yapabilirdi?
        opponent_state = replace(
            state,
            player=-player
        )

        # Rakibin bir hamlede kazanabilecegi sutunlar
        for action in actions:

            child = self.game.result(
                opponent_state,
                action
            )

            if self.game.is_terminal(child):

                value = self.game.utility(child)

                if value == -player:
                    opponent_threats.add(action)

        # Hamlelerin onceligini belirle
        def priority(col):

            if col in winning_moves:
                rank = 0

            elif col in losing_moves:
                rank = 3

            elif col in opponent_threats:
                rank = 1

            else:
                rank = 2

            return (
                rank,
                self.center_distance(col),
                col
            )

        return sorted(actions, key=priority)

    # MAX oyuncusunun değerini hesapla
    def max_value(self, state, depth, alpha, beta):

        self.nodes += 1

        if self.game.is_terminal(state):
            return self.game.utility(state)

        if depth == 0:
            return self.evaluate(state)

        value = -math.inf

        for action in self.ordered_actions(state):

            new_state = self.game.result(state, action)

            value = max(
                value,
                self.min_value(
                    new_state,
                    depth - 1,
                    alpha,
                    beta
                )
            )

            # Beta kesmesi
            if value >= beta:
                return value

            alpha = max(alpha, value)

        return value

    # MIN oyuncusunun değerini hesapla
    def min_value(self, state, depth, alpha, beta):

        self.nodes += 1

        if self.game.is_terminal(state):
            return self.game.utility(state)

        if depth == 0:
            return self.evaluate(state)

        value = math.inf

        for action in self.ordered_actions(state):

            new_state = self.game.result(state, action)

            value = min(
                value,
                self.max_value(
                    new_state,
                    depth - 1,
                    alpha,
                    beta
                )
            )

            # Alpha kesmesi
            if value <= alpha:
                return value

            beta = min(beta, value)

        return value

    # En iyi hamleyi seç
    def choose_move(self, state, depth):

        if depth < 1:
            raise ValueError("Derinlik en az 1 olmali")

        self.nodes = 1

        if self.game.is_terminal(state):
            return None, self.game.utility(state), self.nodes

        alpha = -math.inf
        beta = math.inf

        best_move = None

        if state.player == MAX:

            best_value = -math.inf

            for action in self.ordered_actions(state):

                new_state = self.game.result(state, action)

                value = self.min_value(
                    new_state,
                    depth - 1,
                    alpha,
                    beta
                )

                if value > best_value:
                    best_value = value
                    best_move = action

                alpha = max(alpha, best_value)

        else:

            best_value = math.inf

            for action in self.ordered_actions(state):

                new_state = self.game.result(state, action)

                value = self.max_value(
                    new_state,
                    depth - 1,
                    alpha,
                    beta
                )

                if value < best_value:
                    best_value = value
                    best_move = action

                beta = min(beta, best_value)

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