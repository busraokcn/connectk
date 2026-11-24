import math
import time

from dataclasses import dataclass

from game import EMPTY
from search import AlphaBeta


# Sure doldugunda kullanilacak istisna
class SearchTimeout(Exception):
    pass


# Tamamlanan bir derinligin sonucu
@dataclass(frozen=True)
class DepthResult:

    depth: int
    move: int
    value: float
    nodes: int
    elapsed: float
    first_move: int


# Zaman sinirli aramanin genel sonucu
@dataclass(frozen=True)
class TimedResult:

    move: int | None
    value: float | None
    depth: int
    nodes: int
    elapsed: float
    timed_out: bool
    history: tuple


# ==========================================
# ZAMAN SINIRLI ALPHA BETA
# ==========================================

class TimedAlphaBeta(AlphaBeta):

    def __init__(
        self,
        game,
        order="A",
        evaluator=None,
        check_interval=1000
    ):

        super().__init__(
            game,
            order=order,
            evaluator=evaluator
        )

        if check_interval < 1:
            raise ValueError("Kontrol araligi pozitif olmali")

        self.check_interval = check_interval

        self._deadline = None
        self._root_state = None
        self._preferred_move = None
        self._root_first = None

    # ======================================
    # SURE KONTROLU
    # ======================================

    def check_time(self, force=False):

        if self._deadline is None:
            return

        if force or self.nodes % self.check_interval == 0:

            if time.perf_counter() >= self._deadline:

                raise SearchTimeout("Arama suresi doldu")

    # ======================================
    # HAMLE SIRALAMASI
    # ======================================

    def ordered_actions(self, state):

        if state is self._root_state:
            self.check_time(force=True)

        actions = super().ordered_actions(state)

        # Onceki iterasyonun en iyi hamlesi
        # yeni iterasyonda ilk siraya alinir.
        if state is self._root_state:

            if self._preferred_move in actions:

                actions.remove(self._preferred_move)

                actions.insert(0, self._preferred_move)

            self._root_first = (
                actions[0] if actions else None
            )

        return actions

    # ======================================
    # MAX VE MIN DUGUMLERI
    # ======================================

    def max_value(self, state, depth, alpha, beta):

        self.check_time()

        return super().max_value(
            state, depth, alpha, beta
        )

    def min_value(self, state, depth, alpha, beta):

        self.check_time()

        return super().min_value(
            state, depth, alpha, beta
        )

    # ======================================
    # ITERATIVE DEEPENING
    # ======================================

    def choose_move_timed(
        self,
        state,
        time_limit=1.0,
        max_depth=None
    ):

        if not math.isfinite(time_limit) or time_limit <= 0:
            raise ValueError("Sure siniri pozitif olmali")

        if max_depth is not None and max_depth < 1:
            raise ValueError("Derinlik pozitif olmali")

        start = time.perf_counter()

        if self.game.is_terminal(state):

            return TimedResult(
                move=None,
                value=self.game.utility(state),
                depth=0,
                nodes=1,
                elapsed=time.perf_counter() - start,
                timed_out=False,
                history=()
            )

        actions = self.game.actions(state)

        # Hicbir derinlik tamamlanamazsa
        # kullanilacak yasal yedek hamle.
        best_move = actions[0]

        best_value = None
        completed_depth = 0
        total_nodes = 0
        timed_out = False

        history = []

        remaining = sum(
            cell == EMPTY
            for row in state.board
            for cell in row
        )

        if max_depth is None:

            max_depth = remaining

        else:

            max_depth = min(max_depth, remaining)

        # Zaman sinirini asmamak icin guvenlik payi.
        reserve = min(0.100, time_limit * 0.20)

        self._deadline = (
            start + time_limit - reserve
        )

        self._root_state = state
        self._preferred_move = None

        try:

            for depth in range(1, max_depth + 1):

                self.nodes = 0
                self._root_first = None

                try:

                    self.check_time(force=True)

                    move, value, nodes = self.choose_move(
                        state, depth
                    )

                    # Iterasyon tamamlandiktan sonra
                    # sureyi yeniden kontrol et.
                    self.check_time(force=True)

                except SearchTimeout:

                    # Yarim kalan aramanin dugumleri
                    # toplam maliyete dahil edilir.
                    total_nodes += self.nodes

                    timed_out = True

                    # Yarim kalan sonucu kullanma.
                    break

                # Sadece tamamlanan sonucu kaydet.
                best_move = move
                best_value = value
                completed_depth = depth

                total_nodes += nodes

                history.append(
                    DepthResult(
                        depth=depth,
                        move=move,
                        value=value,
                        nodes=nodes,
                        elapsed=time.perf_counter() - start,
                        first_move=self._root_first
                    )
                )

                # Sonraki iterasyonda ilk denenecek hamle.
                self._preferred_move = best_move

        finally:

            # Sonraki aramalara eski zaman siniri kalmasin.
            self._deadline = None
            self._root_state = None
            self._preferred_move = None
            self._root_first = None

        self.nodes = total_nodes

        return TimedResult(
            move=best_move,
            value=best_value,
            depth=completed_depth,
            nodes=total_nodes,
            elapsed=time.perf_counter() - start,
            timed_out=timed_out,
            history=tuple(history)
        )