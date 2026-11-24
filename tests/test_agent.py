import unittest
import subprocess
import sys
import time
import threading
import queue

from pathlib import Path

from game import Game, state_from_moves


ROOT = Path(__file__).resolve().parents[1]


class TestAgentProtocol(unittest.TestCase):

    def setUp(self):

        self.game = Game(d=27)

        self.command = [
            sys.executable,
            str(ROOT / "agent.py"),
            "--R", "5",
            "--C", "6",
            "--K", "5",
            "--V", "1",
            "--seed", "27"
        ]

    # ======================================
    # YARDIMCI: AJANI CALISTIR
    # ======================================

    def run_agent(self, commands, args=None):

        command = (
            self.command
            if args is None
            else args
        )

        result = subprocess.run(
            command,
            input=commands,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=ROOT,
            timeout=10
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=result.stderr
        )

        outputs = result.stdout.splitlines()

        # Her cikti yalnizca tam sayi olmali.
        for line in outputs:

            self.assertRegex(
                line,
                r"^-?\d+$"
            )

        return outputs, result.stderr

    # ======================================
    # YARDIMCI: YASAL HAMLE KONTROLU
    # ======================================

    def assert_legal_move(
        self, game, moves, output
    ):

        state = state_from_moves(
            game,
            moves
        )

        move = int(output)

        self.assertIn(
            move,
            game.actions(state)
        )

    # ======================================
    # TEST 1: BIRDEN FAZLA MOVES KOMUTU
    # ======================================

    def test_multiple_moves_commands(self):

        commands = (
            "MOVES\n"
            "MOVES 3 3 4\n"
            "MOVES 0 1 0 1 0 1 0 2\n"
            "MOVES 1 0 1 0 2 0 2 0\n"
            "QUIT\n"
        )

        outputs, errors = self.run_agent(
            commands
        )

        self.assertEqual(len(outputs), 4)

        self.assertEqual(errors.strip(), "")

        positions = [
            [],
            [3, 3, 4],
            [0, 1, 0, 1, 0, 1, 0, 2],
            [1, 0, 1, 0, 2, 0, 2, 0]
        ]

        for moves, output in zip(
            positions, outputs
        ):

            self.assert_legal_move(
                self.game,
                moves,
                output
            )

        # Kazanma ve engelleme hamleleri
        self.assertEqual(outputs[2], "0")
        self.assertEqual(outputs[3], "0")

    # ======================================
    # TEST 2: STDOUT VE STDERR AYRIMI
    # ======================================

    def test_debug_output(self):

        outputs, errors = self.run_agent(
            "MOVES 0 1 0 1 0 1 0 2\nQUIT\n",
            args=self.command + ["--debug"]
        )

        # stdout yalnizca hamle numarasi
        self.assertEqual(outputs, ["0"])

        # Debug bilgileri stderr icinde
        self.assertIn("Ajan hazir", errors)
        self.assertIn("Derinlik=", errors)
        self.assertIn("Dugum=", errors)
        self.assertIn("Sure=", errors)
        self.assertIn("TT hit=", errors)

    # ======================================
    # TEST 3: HOCANIN ORNEK PARAMETRELERI
    # ======================================

    def test_teacher_example(self):

        command = [
            sys.executable,
            str(ROOT / "agent.py"),
            "--R", "6",
            "--C", "7",
            "--K", "4",
            "--V", "2",
            "--seed", "7"
        ]

        game = Game(
            d=7,
            R=6,
            C=7,
            K=4,
            V=2
        )

        outputs, errors = self.run_agent(
            "MOVES\nMOVES 3 3 4\nQUIT\n",
            args=command
        )

        self.assertEqual(len(outputs), 2)

        self.assertEqual(errors.strip(), "")

        self.assert_legal_move(
            game, [], outputs[0]
        )

        self.assert_legal_move(
            game, [3, 3, 4], outputs[1]
        )

    # ======================================
    # TEST 4: DOLU SUTUNA TAS ATMAMA
    # ======================================

    def test_full_column(self):

        moves = [0, 0, 0, 0, 0]

        outputs, errors = self.run_agent(
            "MOVES 0 0 0 0 0\nQUIT\n"
        )

        self.assertEqual(len(outputs), 1)

        self.assertNotEqual(outputs[0], "0")

        self.assert_legal_move(
            self.game,
            moves,
            outputs[0]
        )

    # ======================================
    # TEST 5: TERMINAL DURUM
    # ======================================

    def test_terminal_position(self):

        outputs, errors = self.run_agent(
            "MOVES 0 1 0 1 0 1 0 1 0\n"
            "QUIT\n"
        )

        # Yerel terminal durum isareti
        self.assertEqual(outputs, ["-1"])

    # ======================================
    # TEST 6: GECERSIZ KOMUTLAR
    # ======================================

    def test_invalid_commands(self):

        commands = (
            "MOVES abc\n"
            "MOVES 99\n"
            "UNKNOWN\n"
            "MOVES 0 1 0 1 0 1 0 2\n"
            "QUIT\n"
        )

        outputs, errors = self.run_agent(
            commands
        )

        # Hatali komutlar stdout'a yazilmamali.
        # Gecerli komut yine calismali.
        self.assertEqual(outputs, ["0"])

        self.assertIn(
            "Gecersiz MOVES komutu",
            errors
        )

        self.assertIn(
            "Bilinmeyen komut",
            errors
        )

    # ======================================
    # TEST 7: EOF DURUMUNDA KAPANMA
    # ======================================

    def test_eof_exit(self):

        # QUIT gelmese bile girdi kapaninca
        # program normal sekilde kapanmali.
        outputs, errors = self.run_agent("")

        self.assertEqual(outputs, [])
        self.assertEqual(errors.strip(), "")

    # ======================================
    # TEST 8: TEHDIT UZATMALI AJAN
    # ======================================

    def test_threat_agent(self):

        moves = [
            3, 5, 2, 2, 0, 1, 0, 0, 0,
            0, 1, 1, 2, 1, 1, 4, 4
        ]

        command_text = (
            "MOVES "
            + " ".join(map(str, moves))
            + "\nQUIT\n"
        )

        outputs, errors = self.run_agent(
            command_text,
            args=self.command + ["--threat"]
        )

        self.assertEqual(len(outputs), 1)

        self.assert_legal_move(
            self.game,
            moves,
            outputs[0]
        )

    # ======================================
    # TEST 9: CANLI FLUSH VE ZAMAN KONTROLU
    # ======================================

    def test_live_response_and_flush(self):

        stdout_queue = queue.Queue()
        stderr_queue = queue.Queue()

        def read_lines(stream, target):

            for line in stream:

                target.put(line.rstrip("\r\n"))

            target.put(None)

        command = self.command + ["--debug"]

        with subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=ROOT
        ) as process:

            out_thread = threading.Thread(
                target=read_lines,
                args=(
                    process.stdout,
                    stdout_queue
                ),
                daemon=True
            )

            err_thread = threading.Thread(
                target=read_lines,
                args=(
                    process.stderr,
                    stderr_queue
                ),
                daemon=True
            )

            out_thread.start()
            err_thread.start()

            try:

                # Program tamamen baslatilsin.
                ready = stderr_queue.get(
                    timeout=5
                )

                self.assertIsNotNone(ready)

                self.assertIn(
                    "Ajan hazir",
                    ready
                )

                positions = [
                    [],
                    [3, 3, 4],
                    [0, 1, 0, 1, 0, 1, 0, 2]
                ]

                for moves in positions:

                    message = (
                        "MOVES "
                        + " ".join(map(str, moves))
                        + "\n"
                    )

                    start = time.perf_counter()

                    process.stdin.write(message)
                    process.stdin.flush()

                    try:

                        output = stdout_queue.get(
                            timeout=1.0
                        )

                    except queue.Empty:

                        self.fail(
                            "Ajan 1 saniye icinde "
                            "cevap vermedi"
                        )

                    elapsed = (
                        time.perf_counter() - start
                    )

                    self.assertIsNotNone(output)

                    self.assertRegex(
                        output,
                        r"^\d+$"
                    )

                    self.assert_legal_move(
                        self.game,
                        moves,
                        output
                    )

                    self.assertLessEqual(
                        elapsed,
                        1.0
                    )

                    print(
                        f"\nCanli protokol | "
                        f"Hamle: {output} | "
                        f"Sure: {elapsed:.6f} s"
                    )

                # Program hala acik olmali
                self.assertIsNone(
                    process.poll()
                )

                # QUIT komutu ile kapat
                process.stdin.write("QUIT\n")
                process.stdin.flush()

                process.wait(timeout=5)

                self.assertEqual(
                    process.returncode,
                    0
                )

                # Fazladan stdout cikisi olmamali
                self.assertIsNone(
                    stdout_queue.get(timeout=2)
                )

            finally:

                if process.poll() is None:

                    process.kill()
                    process.wait(timeout=5)

                out_thread.join(timeout=2)
                err_thread.join(timeout=2)


if __name__ == "__main__":

    unittest.main()