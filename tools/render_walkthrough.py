"""Capture the guided lesson on Python 3.14.8 and check its Markdown output."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]

# Input is echoed as in a terminal. Invisible capture markers let us divide one
# uninterrupted session into teaching steps without inserting debugger commands.
LAUNCHER = textwrap.dedent('''
    import builtins
    import runpy
    import sys

    def terminal_input(prompt='', counter=iter(range(1000))):
        import sys
        line = sys.stdin.readline()
        if not line:
            raise EOFError
        print(f'\\x1e{next(counter)}\\x1f', end='')
        print(prompt + line, end='', flush=True)
        return line.rstrip('\\n')

    builtins.input = terminal_input
    sys.argv = ['pdb', 'main.py']
    runpy.run_module('pdb', run_name='__main__')
''')

LESSON = [
    ('start', ['!import random', '!random.seed(0)', 'c']),
    ('source', ['l 4, 9']),
    ('enter', ['n', 's']),
    ('next', ['n', 'n', 'p c']),
    ('create', ['n', 'n', 'p [die.value for die in runner.dice]']),
    ('input-break', ['b 34', 'c', 'cl 1']),
    ('guess', ['n', '20']),
    ('answer-call', ['n', 's']),
    ('answer-body', ['n', 'n', 'n', 'p die.value']),
    ('return', ['p sum(die.value for die in self.dice)', 'r', 'p total']),
    ('crash', ['c', 'Y']),
    ('inspect-crash', ['p some_value', 'u', 'p prompt', 'l 55, 60']),
    ('quit', ['q']),
]

ADVANCED = [
    ('commands', [
        '!import random', '!random.seed(0)', 'c',
        'b dicegame/runner.py:18', 'commands 1', 'p total', 'end',
        'c', '20', 'c', 'cl 1', 'q', 'y', 'q',
    ]),
]


def capture(steps):
    commands = [command for _, inputs in steps for command in inputs]
    result = subprocess.run(
        [sys.executable, '-c', LAUNCHER], cwd=ROOT,
        input='\n'.join(commands) + '\n', text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env={**os.environ, 'PYTHON_COLORS': '0', 'NO_COLOR': '1',
             'PYTHONBREAKPOINT': 'pdb.set_trace'}, timeout=20,
    )
    output = result.stdout.replace(str(ROOT), '<repo>')
    output = output.replace(str(Path(os.__file__).parent), '<stdlib>')
    chunks = re.split(r'\x1e(\d+)\x1f', output)
    consumed = [int(chunks[i]) for i in range(1, len(chunks), 2)]
    plain = chunks[0] + ''.join(chunks[i] for i in range(2, len(chunks), 2))
    if result.returncode != 0 or '***' in plain or consumed != list(range(len(commands))):
        raise RuntimeError(f'Session failed or did not consume all input:\n{plain}')
    records = [chunks[i] for i in range(2, len(chunks), 2)]
    records[0] = chunks[0] + records[0]
    sections = {}
    offset = 0
    for name, inputs in steps:
        text = ''.join(records[offset:offset + len(inputs)])
        sections[name] = normalize(text)
        offset += len(inputs)
    return sections, normalize(plain)


def normalize(text):
    return '\n'.join(line.rstrip() for line in text.rstrip().splitlines()) + '\n'


def replace_blocks(text, sections):
    for name, output in sections.items():
        start = f'<!-- transcript:{name}:start -->\n'
        end = f'<!-- transcript:{name}:end -->'
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before + start + '```text\n' + output + '```\n' + end + after
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if sys.version_info[:3] != (3, 14, 8):
        parser.error('Use Python 3.14.8, for example: nix develop -c python tools/render_walkthrough.py')
    lesson, full_lesson = capture(LESSON)
    advanced, _ = capture(ADVANCED)
    for expected in [
        'Sigh. What is your guess?: 20', 'answer()->5',
        '(Pdb) p sum(die.value for die in self.dice)\n20',
        'Uncaught exception. Entering post mortem debugging',
        "(Pdb) p prompt\n'Y'",
    ]:
        if expected not in full_lesson:
            raise RuntimeError(f'Missing lesson result: {expected!r}')
    if '(Pdb) c\n1\n' not in advanced['commands']:
        raise RuntimeError('Breakpoint command list did not run on the second iteration')
    outputs = {
        ROOT / 'README.md': replace_blocks((ROOT / 'README.md').read_text(), lesson),
        ROOT / 'docs/advanced.md': replace_blocks((ROOT / 'docs/advanced.md').read_text(), advanced),
        ROOT / 'docs/session.txt': full_lesson,
    }
    stale = [str(path.relative_to(ROOT)) for path, output in outputs.items()
             if not path.exists() or path.read_text() != output]
    if args.check:
        if stale:
            raise SystemExit('Captured output differs: ' + ', '.join(stale))
        print('Guided lesson, advanced example, and full session match Python 3.14.8.')
    else:
        for path, output in outputs.items():
            path.write_text(output)
        print('Regenerated guided lesson, advanced example, and full session.')


if __name__ == '__main__':
    main()
