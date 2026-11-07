"""Smoke tests for the tutorial snapshot, debugger, and reference solution."""
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TutorialTests(unittest.TestCase):
    def run_python(self, *args, input="", cwd=ROOT, **env):
        result = subprocess.run(
            [sys.executable, *args], input=input, text=True,
            capture_output=True, cwd=cwd,
            env={**os.environ, "PYTHON_COLORS": "0", **env}, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_exercise_keeps_intentional_answer_bug(self):
        from dicegame.runner import GameRunner
        runner = GameRunner()
        for die, value in zip(runner.dice, [1, 2, 3, 4, 5]):
            die.value = value
        self.assertEqual(runner.answer(), 5)
        self.assertNotEqual(runner.answer(), sum(die.value for die in runner.dice))

    def test_breakpoint_can_be_disabled(self):
        # Keep the deliberately broken uppercase-Y path as a debugging exercise.
        code = textwrap.dedent('''
            from unittest.mock import patch
            import main
            from dicegame.utils import UnnecessaryError
            with patch('builtins.input', side_effect=['0', 'Y']):
                try:
                    main.main()
                except UnnecessaryError:
                    print('expected exercise exception')
        ''')
        output = self.run_python("-c", code, PYTHONBREAKPOINT="0")
        self.assertIn("expected exercise exception", output)

    def test_debugger_commands(self):
        output = self.run_python(
            "-m", "pdb", "main.py", input="c\nn\ns\nuntil 26\np c\nq\ny\n",
            PYTHONBREAKPOINT="pdb.set_trace",
        )
        self.assertIn("-> breakpoint()", output)
        self.assertIn("-> while True:", output)
        self.assertIn("(Pdb) 0", output)
        self.assertNotIn("***", output)

    def test_post_mortem(self):
        code = textwrap.dedent('''
            import pdb
            from dicegame.utils import UnnecessaryError, i_just_throw_an_exception
            try:
                i_just_throw_an_exception()
            except UnnecessaryError:
                pdb.post_mortem()
        ''')
        output = self.run_python("-c", code, input="p some_value\nq\n")
        self.assertIn("I don't know what you were expecting", output)
        self.assertNotIn("***", output)

    def test_reference_solution_can_win(self):
        code = textwrap.dedent('''
            from unittest.mock import patch
            from dicegame.runner import GameRunner
            answers = iter(['5', 'y'] * 5 + ['5'])
            with patch('random.random', return_value=0), patch(
                'builtins.input', side_effect=lambda _: next(answers)
            ):
                GameRunner.run()
        ''')
        output = self.run_python("-c", code, cwd=ROOT / "solutions")
        self.assertIn("You won", output)
        self.assertIn("Wins: 6 Loses 0", output)


if __name__ == "__main__":
    unittest.main()
