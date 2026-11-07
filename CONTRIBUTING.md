# Contributing

## Development environment

Use Python 3.14. On Linux (x86-64 or ARM64) or Apple Silicon macOS,
`nix develop` provides a pinned Python interpreter. If you use direnv,
`direnv allow` enables the same environment through `.envrc`.

## Program changes

The main exercise deliberately contains bugs. Keep those bugs in the learner's
starting code. Reference fixes belong in `solutions/`.

Run the exercise from the repository root:

```sh
python main.py
```

Run the reference solution with:

```sh
python solutions/main.py
```

## README changes

Follow the README from start to finish with Python 3.14 when changing the
walkthrough. Check that the commands, source lines, and output match the actual
debugger session. The recorded output uses Python 3.14.8.

Write for any reader, without references to a maintainer's local checkout or
setup history. Introduce commands when needed and keep each explanation next
to its action and output.
