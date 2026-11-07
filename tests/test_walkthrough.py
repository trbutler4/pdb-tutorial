"""Checks for the continuous lesson and its generated documentation blocks."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import render_walkthrough as walkthrough


class WalkthroughTests(unittest.TestCase):
    def test_main_lesson_runs_without_a_restart(self):
        sections, full = walkthrough.capture(walkthrough.LESSON)
        self.assertEqual(list(sections), [name for name, _ in walkthrough.LESSON])
        self.assertEqual(full.count('> <repo>/main.py(1)<module>()'), 1)
        self.assertEqual(full.count('Round 1'), 1)
        self.assertIn('Sigh. What is your guess?: 20', full)
        self.assertIn('answer()->5', full)
        self.assertIn("(Pdb) p prompt\n'Y'", full)
        self.assertNotIn('The program finished and will be restarted', full)
        self.assertTrue(full.endswith('(Pdb) q\n'))

    def test_capture_rejects_unconsumed_commands(self):
        result = SimpleNamespace(returncode=0, stdout='Debugger stopped early\n')
        with patch.object(walkthrough.subprocess, 'run', return_value=result):
            with self.assertRaisesRegex(RuntimeError, 'did not consume all input'):
                walkthrough.capture([('example', ['p total'])])

    def test_replace_blocks_preserves_explanations(self):
        original = (
            'Before\n<!-- transcript:example:start -->\nold output\n'
            '<!-- transcript:example:end -->\nAfter\n'
        )
        updated = walkthrough.replace_blocks(original, {'example': '(Pdb) p total\n5\n'})
        self.assertTrue(updated.startswith('Before\n'))
        self.assertTrue(updated.endswith('After\n'))
        self.assertIn('```text\n(Pdb) p total\n5\n```', updated)
        self.assertNotIn('old output', updated)

    def test_normalization_does_not_drop_internal_blank_lines(self):
        self.assertEqual(walkthrough.normalize('one  \n\ntwo\t\n'), 'one\n\ntwo\n')


if __name__ == '__main__':
    unittest.main()
