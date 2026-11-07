"""Regenerate README transcripts by running the real debugger on Python 3.15.2.

Paths and trailing line whitespace are normalized. No output lines are omitted.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]

# Echo input exactly as a terminal does, without terminal escape sequences.
LAUNCHER = textwrap.dedent('''
    import builtins
    import runpy
    import sys

    def terminal_input(prompt=''):
        import sys
        print(prompt, end='', flush=True)
        line = sys.stdin.readline()
        if not line:
            raise EOFError
        print(line, end='', flush=True)
        return line.rstrip('\\n')

    builtins.input = terminal_input
    sys.argv = ['pdb', 'main.py']
    runpy.run_module('pdb', run_name='__main__')
''')

SESSIONS = {
    'inspect': [
        'c', 'l 1, 13', 'n', 's', 'n', 'n', 'p c',
        'n', 'n', 'n', 'p len(runner.dice)',
        'b 34', 'c', 'b', 'cl 1', 'n', '10', 'n', 's',
        'n', 'n', 'n', 'p die.value', '!print(f"die value: {die.value}")',
        'p die.show()', 'r', 'p total',
        'q', 'y', 'q',
    ],
    'commands': [
        'c', 'b dicegame/runner.py:18', 'commands 1',
        'p total', 'end', 'c', '10', 'c', 'cl 1', 'q', 'y', 'q',
    ],
    'postmortem': [
        'c', 'c', '10', 'Y', 'p some_value', 'p value', 'q',
    ],
}

EXPECTED = {
    'inspect': [
        '-> breakpoint()', '(Pdb) p c\n0',
        'die value: 6', 'answer()->20', '(Pdb) p total\n20',
    ],
    'commands': [
        '(com) p total', 'guess?: 10\n0\n', '(Pdb) c\n6\n',
    ],
    'postmortem': [
        'dicegame.utils.UnnecessaryError: You actually called this function...',
        'Uncaught exception. Entering post mortem debugging',
        '(Pdb) p value\n1',
    ],
}


def capture(name):
    result = subprocess.run(
        [sys.executable, '-c', LAUNCHER], cwd=ROOT,
        input='\n'.join(['!import random', '!random.seed(0)', *SESSIONS[name]]) + '\n', text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env={**os.environ, 'PYTHON_COLORS': '0', 'NO_COLOR': '1',
             'PYTHONBREAKPOINT': 'pdb.set_trace'}, timeout=20,
    )
    output = result.stdout.replace(str(ROOT), '<repo>')
    output = output.replace(str(Path(os.__file__).parent), '<stdlib>')
    if result.returncode != 0 or '***' in output:
        raise RuntimeError(f'{name} failed:\n{output}')
    for expected in EXPECTED[name]:
        if expected not in output:
            raise RuntimeError(f'{name} did not produce {expected!r}:\n{output}')
    return '\n'.join(line.rstrip() for line in output.rstrip().splitlines()) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--session', choices=SESSIONS)
    args = parser.parse_args()
    if sys.version_info[:3] != (3, 15, 2):
        parser.error('Use Python 3.15.2, for example: nix develop -c python tools/render_walkthrough.py')
    if args.session:
        print(capture(args.session), end='')
        return
    path = ROOT / 'README.md'
    original = path.read_text()
    updated = original
    for name in SESSIONS:
        start = f'<!-- transcript:{name}:start -->\n'
        end = f'<!-- transcript:{name}:end -->'
        before, rest = updated.split(start, 1)
        _, after = rest.split(end, 1)
        updated = before + start + '```text\n' + capture(name) + '```\n' + end + after
    if args.check:
        if updated != original:
            raise SystemExit('README transcripts differ. Run tools/render_walkthrough.py to refresh.')
        print('All README transcripts match Python 3.15.2 execution.')
    else:
        path.write_text(updated)
        print('Regenerated all README transcripts.')


if __name__ == '__main__':
    main()
