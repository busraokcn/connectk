import math

from dataclasses import dataclass

from game import MAX
from timed_search import TimedAlphaBeta
from zobrist import ZobristHash


# TT bayraklari
EXACT = "EXACT"
LOWER = "LOWER"
UPPER = "UPPER"


# ==========================================
# TRANSPOSITION TABLE KAYDI
# ==========================================

@dataclass(frozen=True)
class TTEntry:

    depth: int
    value: float
    flag: str
    best_move: int | None
    board: tuple
    player: int


# ==========================================
# TT DESTEKLI ALPHA BETA
# ==========================================

class TTAlphaBeta(TimedAlphaBeta):

    def __init__(
        self,
        game,
        order="A",
        evaluator=None,
        check_interval=1000,
        seed=27,
        use_tt=True,
        max_entries=100000
    ):

        super().__init__(
            game,
            order=order,
            evaluator=evaluator,
            check_interval=check_interval
        )

        if max_entries < 1:
            raise ValueError("Tablo kapasitesi pozitif olmali")

        self.use_tt = use_tt

        self.max_entries = max_entries

        self.zobrist = ZobristHash(
            game, seed=seed
        )

        self.tt = {}

        self.tt_hits = 0
        self.tt_cutoffs = 0
        self.tt_stores = 0

    # ======================================
    # TABLOYU TEMIZLE
    # ======================================

    def clear_table(self):

        self.tt.clear()

        self.tt_hits = 0
        self.tt_cutoffs = 0
        self.tt_stores = 0

    # ======================================
    # TABLODAN KAYIT OKU
    # ======================================

    def lookup(self, key, state):

        if not self.use_tt:
            return None

        entry = self.tt.get(key)

        if entry is None:
            return None

        # Hash cakismasina karsi kontrol
        if entry.board != state.board:
            return None

        if entry.player != state.player:
            return None

        self.tt_hits += 1

        return entry

    # ======================================
    # TABLOYA KAYIT EKLE
    # ======================================

    def store(
        self,
        key,
        state,
        depth,
        value,
        flag,
        best_move
    ):

        if not self.use_tt:
            return

        old = self.tt.get(key)

        if old is not None:

            same_state = (
                old.board == state.board
                and old.player == state.player
            )

            if same_state:

                # Daha derin kaydi koru
                if old.depth > depth:
                    return

                # Kesin kaydi sinirla degistirme
                if (
                    old.depth == depth
                    and old.flag == EXACT
                    and flag != EXACT
                ):
                    return

        elif len(self.tt) >= self.max_entries:

            # Tablo doluysa yeni kayit ekleme
            return

        self.tt[key] = TTEntry(
            depth=depth,
            value=value,
            flag=flag,
            best_move=best_move,
            board=state.board,
            player=state.player
        )

        self.tt_stores += 1

    # ======================================
    # TT DESTEKLI ARAMA
    # ======================================

    def _search(
        self,
        state,
        depth,
        alpha,
        beta,
        key,
        is_root=False
    ):

        self.nodes += 1

        self.check_time(force=is_root)

        # Terminal kontrolu her seyden once
        if self.game.is_terminal(state):

            return self.game.utility(state), None

        # Orijinal arama sinirlarini sakla
        alpha_start = alpha
        beta_start = beta

        entry = self.lookup(key, state)

        # Sabit derinlik dogrulugunu korumak icin
        # ayni derinlikteki degeri kullan.
        if (
            entry is not None
            and entry.depth == depth
            and not is_root
        ):

            if entry.flag == EXACT:

                self.tt_cutoffs += 1

                return entry.value, entry.best_move

            if (
                entry.flag == LOWER
                and entry.value >= beta
            ):

                self.tt_cutoffs += 1

                return entry.value, entry.best_move

            if (
                entry.flag == UPPER
                and entry.value <= alpha
            ):

                self.tt_cutoffs += 1

                return entry.value, entry.best_move

        # Derinlik sinirina ulasildi
        if depth == 0:

            value = self.evaluate(state)

            self.store(
                key,
                state,
                depth,
                value,
                EXACT,
                None
            )

            return value, None

        actions = self.ordered_actions(state)

        # TT'deki onceki en iyi hamleyi
        # kok disindaki dugumlerde ilk siraya al.
        if (
            not is_root
            and entry is not None
            and entry.best_move in actions
        ):

            actions.remove(entry.best_move)

            actions.insert(0, entry.best_move)

        best_move = None

        # ==================================
        # MAX DUGUMU
        # ==================================

        if state.player == MAX:

            best_value = -math.inf

            for action in actions:

                child = self.game.result(
                    state, action
                )

                if self.use_tt:

                    child_key = self.zobrist.update_hash(
                        key, child
                    )

                else:

                    child_key = None

                value, _ = self._search(
                    child,
                    depth - 1,
                    alpha,
                    beta,
                    child_key
                )

                if value > best_value:

                    best_value = value

                    best_move = action

                alpha = max(alpha, best_value)

                if best_value >= beta:

                    break

        # ==================================
        # MIN DUGUMU
        # ==================================

        else:

            best_value = math.inf

            for action in actions:

                child = self.game.result(
                    state, action
                )

                if self.use_tt:

                    child_key = self.zobrist.update_hash(
                        key, child
                    )

                else:

                    child_key = None

                value, _ = self._search(
                    child,
                    depth - 1,
                    alpha,
                    beta,
                    child_key
                )

                if value < best_value:

                    best_value = value

                    best_move = action

                beta = min(beta, best_value)

                if best_value <= alpha:

                    break

        # ==================================
        # TT BAYRAGINI BELIRLE
        # ==================================

        if best_value <= alpha_start:

            flag = UPPER

        elif best_value >= beta_start:

            flag = LOWER

        else:

            flag = EXACT

        # Yalnizca tamamlanan aramanin
        # sonucunu tabloya kaydet.
        self.store(
            key,
            state,
            depth,
            best_value,
            flag,
            best_move
        )

        return best_value, best_move

    # ======================================
    # SABIT DERINLIKTE ARAMA
    # ======================================

    def choose_move(self, state, depth):

        if depth < 1:
            raise ValueError("Derinlik en az 1 olmali")

        # Normal aramalarda tabloyu temizle.
        # Iterative deepening sirasinda koru.
        if self._deadline is None:

            self.clear_table()

        self.nodes = 0

        if self.use_tt:

            # Kokte tam hash hesaplanir.
            key = self.zobrist.hash_state(state)

        else:

            key = None

        value, move = self._search(
            state,
            depth,
            -math.inf,
            math.inf,
            key,
            is_root=True
        )

        return move, value, self.nodes

    # ======================================
    # ZAMAN SINIRLI ARAMA
    # ======================================

    def choose_move_timed(
        self,
        state,
        time_limit=1.0,
        max_depth=None
    ):

        # Yeni kok aramasinda eski kayitlari temizle.
        self.clear_table()

        return super().choose_move_timed(
            state,
            time_limit=time_limit,
            max_depth=max_depth
        )