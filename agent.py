import argparse
import sys
import time

from game import Game, state_from_moves
from agirliklar import create_evaluator
from tt_search import TTAlphaBeta
from threat_search import ThreatAlphaBeta


# ==========================================
# AJAN AYARLARI
# ==========================================

TIME_LIMIT = 1.0

# Komut okuma ve cikti icin guvenlik payi
COMMAND_BUDGET = 0.95


# ==========================================
# KOMUT SATIRI PARAMETRELERI
# ==========================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Connect-K Arena Turnuva Ajani"
    )

    parser.add_argument(
        "--R",
        type=int,
        default=5
    )

    parser.add_argument(
        "--C",
        type=int,
        default=6
    )

    parser.add_argument(
        "--K",
        type=int,
        default=5
    )

    parser.add_argument(
        "--V",
        type=int,
        choices=[0, 1, 2, 3],
        default=1
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=27
    )

    # Alternatif ajani denemek icin
    parser.add_argument(
        "--threat",
        action="store_true"
    )

    # Hata ayiklama bilgileri
    parser.add_argument(
        "--debug",
        action="store_true"
    )

    args = parser.parse_args()

    if args.R < 1 or args.C < 1 or args.K < 2:

        parser.error(
            "Gecersiz oyun parametreleri"
        )

    if args.V == 3 and args.R * args.C < 2:

        parser.error(
            "Engelli varyant icin en az iki hucre gerekli"
        )

    return args


# ==========================================
# TURNUVA AJANI
# ==========================================

class ArenaAgent:

    def __init__(self, args):

        self.args = args

        self.game = Game(
            d=args.seed,
            R=args.R,
            C=args.C,
            K=args.K,
            V=args.V
        )

        self.evaluator = create_evaluator(
            self.game,
            "W3"
        )

        # Varsayilan: Normal TT ajani
        # Alternatif: Tehdit uzatmali ajan
        agent_class = (
            ThreatAlphaBeta
            if args.threat
            else TTAlphaBeta
        )

        self.algorithm = agent_class(
            self.game,
            order="A",
            evaluator=self.evaluator,
            use_tt=True,
            seed=args.seed,
            check_interval=100
        )

    # ======================================
    # HATA AYIKLAMA
    # ======================================

    def debug(self, message):

        if self.args.debug:

            print(
                message,
                file=sys.stderr,
                flush=True
            )

    # ======================================
    # HAMLE SEC
    # ======================================

    def choose_move(self, moves, start):

        state = state_from_moves(
            self.game,
            moves
        )

        actions = self.game.actions(state)

        # Oyun bitmisse yasal hamle bulunmaz.
        if not actions:

            self.debug(
                "Oyun terminal durumda. Yasal hamle yok."
            )

            return -1

        # Arama basarisiz olursa kullanilacak
        # yasal yedek hamle
        fallback = actions[0]

        # Komut isleme suresini de hesaba kat.
        remaining = (
            COMMAND_BUDGET
            - (time.perf_counter() - start)
        )

        if remaining <= 0:

            return fallback

        result = self.algorithm.choose_move_timed(
            state,
            time_limit=min(
                TIME_LIMIT,
                remaining
            )
        )

        move = result.move

        # Son guvenlik kontrolu
        if move not in actions:

            self.debug(
                "Gecersiz arama hamlesi. Yedek hamle kullanildi."
            )

            move = fallback

        elapsed = time.perf_counter() - start

        self.debug(
            f"Hamle={move} | "
            f"Derinlik={result.depth} | "
            f"Deger={result.value} | "
            f"Dugum={result.nodes} | "
            f"Sure={elapsed:.6f} s | "
            f"TT hit={self.algorithm.tt_hits}"
        )

        return move

    # ======================================
    # TURNUVA PROTOKOLU
    # ======================================

    def run(self):

        self.debug(
            f"Ajan hazir: "
            f"R={self.game.R}, "
            f"C={self.game.C}, "
            f"K={self.game.K}, "
            f"V={self.game.V}"
        )

        for line in sys.stdin:

            start = time.perf_counter()

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            command = parts[0].upper()

            if command == "QUIT":

                self.debug("Ajan kapatiliyor.")

                break

            if command == "MOVES":

                try:

                    moves = [
                        int(value)
                        for value in parts[1:]
                    ]

                    move = self.choose_move(
                        moves,
                        start
                    )

                    # Standart ciktida yalnizca
                    # sutun numarasi bulunur.
                    print(
                        move,
                        flush=True
                    )

                except ValueError as error:

                    print(
                        f"Gecersiz MOVES komutu: {error}",
                        file=sys.stderr,
                        flush=True
                    )

            else:

                print(
                    f"Bilinmeyen komut: {command}",
                    file=sys.stderr,
                    flush=True
                )


# ==========================================
# PROGRAM BASLANGICI
# ==========================================

def main():

    args = parse_arguments()

    agent = ArenaAgent(args)

    agent.run()


if __name__ == "__main__":

    main()