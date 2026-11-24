from game import Game, state_from_moves
import time


# Belirli bir derinlikteki yaprak sayısını hesaplama
def perft(game, state, depth):

    if depth == 0 or game.is_terminal(state):
        return 1

    total = 0

    for action in game.actions(state):
        new_state = game.result(state, action)

        total += perft(game, new_state, depth - 1)

    return total


# Perft performans ölçümü
def measure_perft(game, state, max_depth):

    print(f"{'Derinlik':<12}{'Yaprak sayisi':<20}{'Sure (ms)':<15}")
    print("-" * 47)

    for depth in range(1, max_depth + 1):

        start = time.perf_counter()

        nodes = perft(game, state, depth)

        end = time.perf_counter()

        elapsed = (end - start) * 1000

        print(f"{depth:<12}{nodes:<20}{elapsed:<15.3f}")


if __name__ == "__main__":

    game = Game(d=27)

    print("CONNECT-K ARENA - PERFT")
    print("R:", game.R)
    print("C:", game.C)
    print("K:", game.K)
    print("V:", game.V)

    # Test 1: Boş tahta
    state = game.initial_state()

    print("\nTEST 1: BOS TAHTA")
    game.print_board(state)

    measure_perft(game, state, 6)

    # Boş tahta doğruluk kontrolü
    expected = [6, 36, 216, 1296, 7776, 46650]

    for depth, value in enumerate(expected, start=1):
        assert perft(game, state, depth) == value

    print("\nBos tahta kontrolu basarili!")

    # Test 2: Bir sütunu tamamen doldurma
    moves = [0, 0, 0, 0, 0]
    state = state_from_moves(game, moves)

    print("\nTEST 2: DOLU SUTUN")
    game.print_board(state)

    measure_perft(game, state, 4)

    assert perft(game, state, 1) == 5
    assert perft(game, state, 2) == 25

    print("\nDolu sutun kontrolu basarili!")

    # Test 3: Bir hamlede kazanma konumu
    moves = [0, 1, 0, 1, 0, 1, 0, 2]
    state = state_from_moves(game, moves)

    print("\nTEST 3: BIR HAMLEDE KAZANMA")
    game.print_board(state)

    measure_perft(game, state, 4)

    assert perft(game, state, 1) == 6
    assert perft(game, state, 2) == 31

    print("\nKazanma konumu kontrolu basarili!")

    # Test 4: Bitmiş oyun
    moves = [0, 1, 0, 1, 0, 1, 0, 1, 0]
    state = state_from_moves(game, moves)

    assert perft(game, state, 0) == 1
    assert perft(game, state, 4) == 1

    print("\nTerminal durum kontrolu basarili!")

    print("\nTum perft kontrolleri basarili!")