from game import Game, state_from_moves
from perft import measure_perft


game = Game(d=27)

print("CONNECT-K ARENA - KONTROL NOKTASI 0")
print("R:", game.R)
print("C:", game.C)
print("K:", game.K)
print("V:", game.V)

while True:

    print("\nHamleleri bosluk birakarak giriniz.")
    print("Bos tahta icin Enter tusuna basiniz.")
    print("Cikis icin q yaziniz.")

    user_input = input("\nHamleler: ").strip()

    if user_input.lower() == "q":
        print("Program kapatildi.")
        break

    try:

        moves = [
            int(x) for x in user_input.split()
        ]

        state = state_from_moves(game, moves)

        print("\nOLUSTURULAN TAHTA:")
        game.print_board(state)

        print("\nSiradaki oyuncu:", state.player)
        print("Yasal hamleler:", game.actions(state))
        print("Terminal durum:", game.is_terminal(state))

        if game.is_terminal(state):
            print("Utility:", game.utility(state))

        print("\nPERFT SONUCLARI:")
        measure_perft(game, state, 4)

    except ValueError as error:
        print("Hata:", error)