import math

from dataclasses import replace
from game import Game, MAX, MIN, state_from_moves


# ==========================================
# MINIMAX
# ==========================================

class Minimax:

    def __init__(self, game, evaluator=None):
        self.game = game
        self.nodes = 0
        self.evaluator = evaluator

    def evaluate(self, state):

        # Onceki asamalardaki degerlendirme
        if self.evaluator is None:
            return 0

        # Yeni sezgisel degerlendirme
        return self.evaluator.evaluate(state)

    def ordered_actions(self, state):

        center = (self.game.C - 1) / 2

        return sorted(
            self.game.actions(state),
            key=lambda col: (
                abs(col - center),
                col
            )
        )

    def max_value(self, state, depth):

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
                self.min_value(new_state, depth - 1)
            )

        return value

    def min_value(self, state, depth):

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
                self.max_value(new_state, depth - 1)
            )

        return value

    def choose_move(self, state, depth):

        if depth < 1:
            raise ValueError("Derinlik en az 1 olmali")

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


# ==========================================
# ALPHA BETA
# ==========================================

class AlphaBeta(Minimax):

    def __init__(
        self,
        game,
        order="A",
        evaluator=None
    ):

        super().__init__(game, evaluator)

        if order not in ("A", "B", "C"):
            raise ValueError("Gecersiz siralama yontemi")

        self.order = order

    def center_distance(self, col):

        center = (self.game.C - 1) / 2

        return abs(col - center)

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

        for action in actions:

            child = self.game.result(state, action)

            if self.game.is_terminal(child):

                value = self.game.utility(child)

                if value == player:
                    winning_moves.add(action)

                elif value == -player:
                    losing_moves.add(action)

        opponent_state = replace(
            state,
            player=-player
        )

        for action in actions:

            child = self.game.result(
                opponent_state,
                action
            )

            if self.game.is_terminal(child):

                value = self.game.utility(child)

                if value == -player:
                    opponent_threats.add(action)

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

            if value >= beta:
                return value

            alpha = max(alpha, value)

        return value

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

            if value <= alpha:
                return value

            beta = min(beta, value)

        return value

    def choose_move(self, state, depth):

        if depth < 1:
            raise ValueError("Derinlik en az 1 olmali")

        self.nodes = 1

        if self.game.is_terminal(state):

            return (
                None,
                self.game.utility(state),
                self.nodes
            )

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


# ==========================================
# TEMEL MINIMAX KONTROLLERI
# ==========================================

if __name__ == "__main__":

    game = Game(d=27)

    minimax = Minimax(game)

    print("CONNECT-K ARENA - SEARCH TESTI")

    positions = [
        ("Bos tahta", [], 2, 0),

        (
            "MAX kazanma",
            [0, 1, 0, 1, 0, 1, 0, 2],
            0,
            1
        ),

        (
            "Rakibi engelleme",
            [1, 0, 1, 0, 2, 0, 2, 0],
            0,
            0
        ),

        (
            "MIN kazanma",
            [1, 0, 1, 0, 2, 0, 2, 0, 3],
            0,
            -1
        )
    ]

    for name, moves, expected_move, expected_value in positions:

        state = state_from_moves(game, moves)

        move, value, nodes = minimax.choose_move(
            state, 2
        )

        assert move == expected_move
        assert value == expected_value

        if not moves:
            assert nodes == 43

        print(
            f"{name} | Hamle: {move} | "
            f"Deger: {value} | Dugum: {nodes}"
        )

    state = game.initial_state()

    first = minimax.choose_move(state, 2)
    second = minimax.choose_move(state, 2)

    assert first == second

    print("Deterministik kontrol: BASARILI")
    print("Tum search kontrolleri basarili!")