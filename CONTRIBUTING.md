# Contributing

## Development environment

Use Python 3.14.8 to reproduce the captured output. On Linux (x86-64 or ARM64)
or Apple Silicon macOS with Nix flakes enabled, `nix develop` provides the
standard `python314` package.
`flake.lock` pins the package collection for reproducibility.

The main exercise deliberately contains bugs. Keep those bugs in place when
maintaining the baseline. Reference fixes belong in `solutions/` or in the
lesson's suggested edits, not in the learner's starting code.

## Run checks

From the repository root, using Python 3.14.8:

```sh
python -m unittest discover -s tests -v
python tools/render_walkthrough.py --check
python -m compileall -q main.py dicegame solutions tools
```

The tests cover debugger stepping, post-mortem inspection, the intentional
summation bug, and the reference solution's six-win path. GitHub Actions runs
the tests, transcript check, and compilation check.

A reader who edits the exercise while learning is expected to change its
behavior. These checks verify the committed starting point, not completed
solutions in the main exercise files.

## Update captured output

The README is one continuous debugger session, broken into short teaching steps.
`LESSON` in `tools/render_walkthrough.py` defines every command in order. The
optional example in `docs/advanced.md` runs in a separate session defined by
`ADVANCED`.

After changing source or lesson commands, run:

```sh
python tools/render_walkthrough.py
python tools/render_walkthrough.py --check
```

This updates:

- Each captured block in `README.md`.
- The optional command-list example in `docs/advanced.md`.
- `docs/session.txt`, the complete uninterrupted main lesson.

All captured commands run on the real Python 3.14.8 debugger. A small input
wrapper echoes supplied commands as a terminal would. Internal capture markers
split the output into steps; they are removed before rendering and introduce no
extra debugger commands. All supplied input must be consumed, and expected
outcomes are checked so a silently abandoned session cannot pass.

Only checkout and standard-library paths are replaced with `<repo>` and
`<stdlib>`. Trailing whitespace is removed for Markdown. Source lines, stop
positions, dice output, and exception output are not reconstructed. Long dice
and traceback blocks are collapsed in the README rather than deleted.

After regeneration, read the README from start to finish. Check that each step
explains only the commands used there, that the prose matches the stop positions,
and that the instructions require no unmentioned restart or source edit. Do not
hand-edit generated blocks to make mismatched output look correct.

## Documentation style

Write for a reader encountering the repository for the first time. Do not refer
to a maintainer's local directories, previous checkout, chat session, or setup
history. Keep one goal per step, introduce commands when needed, and place the
output and explanation next to the action. Put maintenance details here instead
of interrupting the beginner lesson.
