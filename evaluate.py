import math

from dataclasses import dataclass

from game import Game, BLOCKED, EMPTY, MAX, MIN


# Varsayilan agirliklar
DEFAULT_WEIGHTS = {
    "max_k1": 12,
    "max_k2": 3,
    "min_k1": 12,
    "min_k2": 3,
    "max_wrap": 2,
    "min_wrap": 2
}


# Pencere veri modeli
@dataclass(frozen=True)
class Window:

    cells: tuple
    direction: str
    wraps: bool


# Degerlendirme sinifi
class Evaluator:

    def __init__(self, game, weights=None, scale=30.0):

        self.game = game

        self.weights = dict(
            DEFAULT_WEIGHTS if weights is None
            else weights
        )

        self.scale = scale

        # Agirliklari kontrol et
        if set(self.weights) != set(DEFAULT_WEIGHTS):
            raise ValueError("Eksik veya gecersiz agirlik")

        for weight in self.weights.values():

            if not math.isfinite(weight) or weight < 0:
                raise ValueError("Gecersiz agirlik")

        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("Olcek pozitif olmali")

        # Pencereleri bir kez olustur
        self.windows = self.build_windows()

    # Kullanilamayan hucreleri belirle
    def unavailable_cells(self):

        unavailable = set()

        state = self.game.initial_state()

        for col in range(self.game.C):

            blocked_found = False

            for row in range(self.game.R):

                if state.board[row][col] == BLOCKED:
                    blocked_found = True

                if blocked_found:
                    unavailable.add((row, col))

        return unavailable

    # Butun K uzunlugundaki pencereleri olustur
    def build_windows(self):

        R = self.game.R
        C = self.game.C
        K = self.game.K

        windows = []
        seen = set()

        unavailable = self.unavailable_cells()

        directions = [
            (0, 1, "Yatay"),
            (1, 0, "Dikey"),
            (1, 1, "Sag capraz"),
            (1, -1, "Sol capraz")
        ]

        for row in range(R):

            for col in range(C):

                for dr, dc, name in directions:

                    cells = []
                    wraps = False
                    valid = True

                    for step in range(K):

                        new_row = row + step * dr
                        new_col = col + step * dc

                        # Satirlar sarilamaz
                        if not 0 <= new_row < R:

                            valid = False
                            break

                        # Silindir varyanti
                        if self.game.V == 1:

                            if not 0 <= new_col < C:
                                wraps = True

                            new_col = new_col % C

                        else:

                            if not 0 <= new_col < C:

                                valid = False
                                break

                        cell = (new_row, new_col)

                        # Engelli hucreleri ele
                        if cell in unavailable:

                            valid = False
                            break

                        cells.append(cell)

                    if not valid:
                        continue

                    if len(cells) != K:
                        continue

                    if len(set(cells)) != K:
                        continue

                    key = tuple(sorted(cells))

                    if key in seen:
                        continue

                    seen.add(key)

                    windows.append(
                        Window(
                            cells=tuple(cells),
                            direction=name,
                            wraps=wraps
                        )
                    )

        return tuple(windows)

    # Oznitelikleri hesapla
    def features(self, state):

        features = {
            "max_k1": 0,
            "max_k2": 0,
            "min_k1": 0,
            "min_k2": 0,
            "max_wrap": 0,
            "min_wrap": 0
        }

        K = self.game.K

        board = state.board

        for window in self.windows:

            values = [
                board[row][col]
                for row, col in window.cells
            ]

            max_count = values.count(MAX)
            min_count = values.count(MIN)
            empty_count = values.count(EMPTY)

            # Engelli pencereyi atla
            if BLOCKED in values:
                continue

            # Karisik pencereyi atla
            if max_count > 0 and min_count > 0:
                continue

            # MAX K-1
            if max_count == K - 1 and empty_count == 1:

                features["max_k1"] += 1

                if window.wraps:
                    features["max_wrap"] += 1

            # MAX K-2
            elif max_count == K - 2 and empty_count == 2:

                features["max_k2"] += 1

                if window.wraps:
                    features["max_wrap"] += 1

            # MIN K-1
            elif min_count == K - 1 and empty_count == 1:

                features["min_k1"] += 1

                if window.wraps:
                    features["min_wrap"] += 1

            # MIN K-2
            elif min_count == K - 2 and empty_count == 2:

                features["min_k2"] += 1

                if window.wraps:
                    features["min_wrap"] += 1

        return features

    # Ham puani hesapla
    def raw_score(self, state):

        f = self.features(state)

        w = self.weights

        score = (
            w["max_k1"] * f["max_k1"]
            + w["max_k2"] * f["max_k2"]
            - w["min_k1"] * f["min_k1"]
            - w["min_k2"] * f["min_k2"]
            + w["max_wrap"] * f["max_wrap"]
            - w["min_wrap"] * f["min_wrap"]
        )

        # Misere varyantinda isareti ters cevir
        if self.game.V == 2:

            score = -score

        return score

    # Sezgisel degerlendirme
    def evaluate(self, state):

        score = self.raw_score(state)

        value = math.tanh(score / self.scale)

        # Terminal degerlerini koru
        return max(
            -0.999999,
            min(0.999999, value)
        )

    # Pencere istatistikleri
    def window_statistics(self):

        statistics = {
            "Yatay": 0,
            "Dikey": 0,
            "Sag capraz": 0,
            "Sol capraz": 0,
            "Sarmali": 0,
            "Toplam": len(self.windows)
        }

        for window in self.windows:

            statistics[window.direction] += 1

            if window.wraps:
                statistics["Sarmali"] += 1

        return statistics


# Pencere olusturma testleri
if __name__ == "__main__":

    game = Game(d=27)

    evaluator = Evaluator(game)

    print("CONNECT-K ARENA - PENCERE HESAPLAMA")

    print("R:", game.R)
    print("C:", game.C)
    print("K:", game.K)
    print("V:", game.V)

    print("\nSILINDIR VARYANTI")

    statistics = evaluator.window_statistics()

    for name, count in statistics.items():
        print(name + ":", count)

    # Test 1: Toplam pencere sayisi
    assert len(evaluator.windows) == 48

    # Test 2: Yonlere gore pencere sayilari
    assert statistics["Yatay"] == 30
    assert statistics["Dikey"] == 6
    assert statistics["Sag capraz"] == 6
    assert statistics["Sol capraz"] == 6

    # Test 3: Sarmali pencere sayisi
    assert statistics["Sarmali"] == 28

    # Test 4: Her pencere K farkli hucre icermeli
    for window in evaluator.windows:

        assert len(window.cells) == game.K

        assert len(set(window.cells)) == game.K

        for row, col in window.cells:

            assert 0 <= row < game.R
            assert 0 <= col < game.C

    # Test 5: Tekrarlanan pencere olmamali
    keys = [
        tuple(sorted(window.cells))
        for window in evaluator.windows
    ]

    assert len(keys) == len(set(keys))

    # Test 6: Sarmali yatay pencere
    expected = (
        (4, 4),
        (4, 5),
        (4, 0),
        (4, 1),
        (4, 2)
    )

    assert any(
        window.cells == expected and window.wraps
        for window in evaluator.windows
    )

    print("\nSarmali pencere ornegi:")
    print(expected)

    # Test 7: Standart varyant
    standard_game = Game(d=27, V=0)

    standard = Evaluator(standard_game)

    print("\nSTANDART VARYANT")

    for name, count in standard.window_statistics().items():
        print(name + ":", count)

    assert len(standard.windows) == 20

    assert standard.window_statistics()["Sarmali"] == 0

    # Test 8: Misere varyanti
    misere_game = Game(d=27, V=2)

    misere = Evaluator(misere_game)

    assert len(misere.windows) == 20

    print("\nMisere pencere kontrolu: BASARILI")

    # Test 9: Engelli varyant
    blocked_game = Game(d=27, V=3)

    blocked = Evaluator(blocked_game)

    unavailable = blocked.unavailable_cells()

    for window in blocked.windows:

        assert not (
            set(window.cells) & unavailable
        )

    print("\nENGELLI VARYANT")

    blocked_game.print_board(
        blocked_game.initial_state()
    )

    print(
        "Kullanilamayan hucreler:",
        sorted(unavailable)
    )

    print("Toplam pencere:", len(blocked.windows))

    print("Engelli pencere kontrolu: BASARILI")

    print("\nTum pencere kontrolleri basarili!")