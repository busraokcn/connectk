import math

from dataclasses import replace

from game import MAX
from tt_search import TTAlphaBeta, EXACT


class ThreatAlphaBeta(TTAlphaBeta):

    def __init__(self, game, **kwargs):

        # Tehdit kontrolunun ek maliyeti nedeniyle
        # zaman kontrolunu daha sik yap.
        kwargs.setdefault("check_interval", 100)

        super().__init__(game, **kwargs)

        self.extensions = 0
        self.extension_nodes = 0

    # ==========================================
    # ISTATISTIKLERI SIFIRLA
    # ==========================================

    def reset_extensions(self):

        self.extensions = 0
        self.extension_nodes = 0

    # ==========================================
    # KAZANMA KONTROLU
    # ==========================================

    def is_winning_child(self, child, player):

        if not self.game.is_terminal(child):
            return False

        return self.game.utility(child) == player

    def winning_moves(self, state):

        if self.game.is_terminal(state):
            return []

        wins = []

        for move in self.game.actions(state):

            child = self.game.result(state, move)

            if self.is_winning_child(
                child, state.player
            ):

                wins.append(move)

        return wins

    # ==========================================
    # RAKIBIN ACIL TEHDIDI
    # ==========================================

    def opponent_has_threat(self, state):

        opponent_state = replace(
            state,
            player=-state.player
        )

        return bool(
            self.winning_moves(opponent_state)
        )

    # ==========================================
    # TEHDIT UZATMALI ARAMA
    # ==========================================

    def _search(
        self,
        state,
        depth,
        alpha,
        beta,
        key,
        is_root=False
    ):

        # Normal derinliklerde TT aramasini kullan.
        if depth > 0:

            return super()._search(
                state,
                depth,
                alpha,
                beta,
                key,
                is_root
            )

        self.nodes += 1

        self.check_time(force=is_root)

        # Terminal kontrolu once yapilir.
        if self.game.is_terminal(state):

            return self.game.utility(state), None

        # Daha once hesaplanan kesin yaprak degeri
        entry = self.lookup(key, state)

        if (
            entry is not None
            and entry.depth == 0
            and entry.flag == EXACT
        ):

            self.tt_cutoffs += 1

            return entry.value, None

        # Yasal alt konumlari olustur.
        children = [
            self.game.result(state, move)
            for move in self.game.actions(state)
        ]

        # Siradaki oyuncu hemen kazanabilir mi?
        own_threat = any(
            self.is_winning_child(
                child, state.player
            )
            for child in children
        )

        # Rakibin acil tehdidi var mi?
        opponent_threat = (
            False if own_threat
            else self.opponent_has_threat(state)
        )

        # ======================================
        # TEHDIT YOKSA NORMAL EVAL
        # ======================================

        if not own_threat and not opponent_threat:

            value = self.evaluate(state)

        # ======================================
        # TEHDIT VARSA BIR HAMLE UZAT
        # ======================================

        else:

            self.extensions += 1

            values = []

            for child in children:

                self.nodes += 1

                self.extension_nodes += 1

                self.check_time()

                if self.game.is_terminal(child):

                    value = self.game.utility(child)

                else:

                    value = self.evaluate(child)

                values.append(value)

            if state.player == MAX:

                value = max(values)

            else:

                value = min(values)

        # Butun ek hamleler incelendigi icin
        # sonuc bu uzatma kuralina gore kesindir.
        self.store(
            key,
            state,
            0,
            value,
            EXACT,
            None
        )

        return value, None

    # ==========================================
    # SABIT DERINLIKTE ARAMA
    # ==========================================

    def choose_move(self, state, depth):

        if self._deadline is None:

            self.reset_extensions()

        return super().choose_move(
            state, depth
        )

    # ==========================================
    # ZAMAN SINIRLI ARAMA
    # ==========================================

    def choose_move_timed(
        self,
        state,
        time_limit=1.0,
        max_depth=None
    ):

        self.reset_extensions()

        return super().choose_move_timed(
            state,
            time_limit=time_limit,
            max_depth=max_depth
        )