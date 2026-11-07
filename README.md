# Debugging Python 3.15.2 with `pdb`

Learn to inspect a running program, step into functions, set breakpoints, and
investigate exceptions using Python's built-in debugger. No third-party Python
packages are needed.

This walkthrough runs against **the files on this branch**, not an older version
of the exercise. It preserves the progress copied into this fork: `answer()`
already correctly adds `die.value`, and `main.py` already has `breakpoint()`.
There are still bugs to investigate, including the uppercase `Y` response and
round counters being reset. You do not need to reset files or insert a breakpoint
to follow along.

## 1. Use the correct checkout and interpreter

Clone the modern branch into its own directory:

```sh
git clone --branch update-python https://github.com/trbutler4/pdb-tutorial.git pdb-tutorial-modern
cd pdb-tutorial-modern
nix develop
python --version
```

The version must be `Python 3.15.2`. If you already have the separate fork clone
created during setup, enter that separate `pdb-tutorial-fork` directory instead
of cloning again. Do not run these lessons from your original Python 3.4 checkout.

The Nix shell is configured for x86_64 Linux. `flake.lock` pins nixpkgs, and
`flake.nix` pins the Python 3.15.2 source and checksum. Its first invocation may
compile Python. Outside Nix, install Python 3.15.2 and confirm that `python`
selects that interpreter before proceeding.

## 2. How to read and reproduce the sessions

Each of the three sessions below starts afresh with this command, from the
repository root:

```sh
PYTHON_COLORS=0 PYTHONBREAKPOINT=pdb.set_trace python -m pdb main.py
```

The environment settings disable colored output and explicitly select `pdb` for
`breakpoint()`. The first `(Pdb)` prompt is at `main.py` line 1, **before** the
import runs. At that prompt, enter the commands shown after `(Pdb)`. At a game
prompt, enter the shown game answer instead. Do not type the prompts themselves.

Every session begins with `!import random` and `!random.seed(0)`. This gives the
same dice values, so you can compare the complete output, including the answer
20. If you skip those commands, the dice values and totals will differ.

All transcript blocks below are captured from actual Python 3.15.2 execution.
Only installation-dependent paths are replaced: `<repo>` means the checkout's
absolute path and `<stdlib>` means Python's standard-library directory. Those
are path labels, not commands. Trailing whitespace is removed for Markdown.
No debugger output lines or dice have been omitted.
Line numbers, stop positions, commands, source listings, and values are the
captured results, not reconstructed examples.

### Command reference

| Command | What it does |
| --- | --- |
| `l` or `l 1, 13` | List source around the stop or a specified range. |
| `ll` | List the current function's source. |
| `s` | Step into a called function. A call event can stop at its definition or decorator. |
| `n` | Execute the current line without stepping through called functions. |
| `b 34` | Break at line 34 in the current file. |
| `b dicegame/runner.py:18` | Break at a line in a specified file. |
| `b` | List breakpoints. |
| `cl 1` | Clear breakpoint number 1. |
| `c` | Continue until a breakpoint or an exception. |
| `r` | Run until the current function returns. |
| `p expression` | Print a Python expression without mistaking it for a debugger command. |
| `!statement` | Execute a Python statement in the selected frame. |
| `help command` | Show debugger help, for example `help n`. |
| `q` | Quit the current debugging session. |

The arrow marks the line about to execute, not a line that has already completed.
For example, `c` is not defined while stopped **before** `c = 0`. Execute that
assignment with `n` first. Use `p c` to inspect the variable: entering `c` by itself
means **continue**, not "show the variable named c".

## 3. Inspect the dice and the answer

Start a fresh debugger session using the command above and follow this transcript
from top to bottom. The important transitions are:

1. `c` reaches the existing inline breakpoint at `main.py:8`. `n` advances to the
   call at line 9. `s` enters `GameRunner.run()` at its call event on line 21.
2. The next `n` stops before `c = 0` on line 25. Another `n` executes it and
   reaches line 26. Now `p c` prints zero.
3. Three more `n` commands create the runner, print the round, and reach the dice
   display loop. `b 34` and `c` skip stepping through each dice-print operation.
4. `b` shows the breakpoint hit count. `cl 1` removes it. The next `n` executes
   the game input prompt. Enter `10`, deliberately less than the sum 20.
5. Advance to line 37 and use `s` to enter `answer()`. Three `n` commands reach
   the first addition at line 18. Inspect `die.value`, print it with an f-string,
   and inspect its ASCII representation.
6. `r` finishes `answer()` and displays the returned value 20. `p total` confirms
   it. This snapshot's summation is already correct.

<!-- transcript:inspect:start -->
```text
> <repo>/main.py(1)<module>()
-> from dicegame.runner import GameRunner
(Pdb) !import random
(Pdb) !random.seed(0)
(Pdb) c
Add the values of the dice
It's really that easy
What are you doing with your life.
> <repo>/main.py(8)main()
-> breakpoint()
(Pdb) l 1, 13
  1  	from dicegame.runner import GameRunner
  2
  3
  4  	def main():
  5  	    print("Add the values of the dice")
  6  	    print("It's really that easy")
  7  	    print("What are you doing with your life.")
  8  ->	    breakpoint()
  9  	    GameRunner.run()
 10
 11
 12  	if __name__ == "__main__":
 13  	    main()
(Pdb) n
> <repo>/main.py(9)main()
-> GameRunner.run()
(Pdb) s
--Call--
> <repo>/dicegame/runner.py(21)run()
-> @classmethod
(Pdb) n
> <repo>/dicegame/runner.py(25)run()
-> c = 0
(Pdb) n
> <repo>/dicegame/runner.py(26)run()
-> while True:
(Pdb) p c
0
(Pdb) n
> <repo>/dicegame/runner.py(27)run()
-> runner = cls()
(Pdb) n
> <repo>/dicegame/runner.py(29)run()
-> print("Round {}\n".format(runner.round))
(Pdb) n
Round 1

> <repo>/dicegame/runner.py(31)run()
-> for die in runner.dice:
(Pdb) p len(runner.dice)
5
(Pdb) b 34
Breakpoint 1 at <repo>/dicegame/runner.py:34
(Pdb) c
---------
|*     *|
|*     *|
|*     *|
---------
---------
|*     *|
|   *   |
|*     *|
---------
---------
|*      |
|   *   |
|      *|
---------
---------
|*      |
|       |
|      *|
---------
---------
|*     *|
|       |
|*     *|
---------
> <repo>/dicegame/runner.py(34)run()
-> guess = input("Sigh. What is your guess?: ")
(Pdb) b
Num Type         Disp Enb   Where
1   breakpoint   keep yes   at <repo>/dicegame/runner.py:34
	breakpoint already hit 1 time
(Pdb) cl 1
Deleted breakpoint 1 at <repo>/dicegame/runner.py:34
(Pdb) n
Sigh. What is your guess?: 10
> <repo>/dicegame/runner.py(35)run()
-> guess = int(guess)
(Pdb) n
> <repo>/dicegame/runner.py(37)run()
-> if guess == runner.answer():
(Pdb) s
--Call--
> <repo>/dicegame/runner.py(15)answer()
-> def answer(self):
(Pdb) n
> <repo>/dicegame/runner.py(16)answer()
-> total = 0
(Pdb) n
> <repo>/dicegame/runner.py(17)answer()
-> for die in self.dice:
(Pdb) n
> <repo>/dicegame/runner.py(18)answer()
-> total += die.value
(Pdb) p die.value
6
(Pdb) !print(f"die value: {die.value}")
die value: 6
(Pdb) p die.show()
'---------\n|*     *|\n|*     *|\n|*     *|\n---------'
(Pdb) r
--Return--
> <repo>/dicegame/runner.py(19)answer()->20
-> return total
(Pdb) p total
20
(Pdb) q
Quitting pdb will kill the process. Quit anyway? [y/n] y
The program exited via sys.exit(). Exit status: 1
The program finished and will be restarted
> <repo>/main.py(1)<module>()
-> from dicegame.runner import GameRunner
(Pdb) q
```
<!-- transcript:inspect:end -->

The f-string in the session executes on the same Python 3.15.2 interpreter as
the rest of the lesson. There is no separate legacy-interpreter requirement.

When quitting from the inline debugger, Python asks for confirmation. After `y`,
the command-line debugger reports the script's exit status and restarts at line
1. Enter `q` again at that outer prompt to return to the shell. That restart
message is debugger behavior, not another game bug.

## 4. Run a command each time a breakpoint is hit

Start a **new** session with the same shell command. First reach the inline
breakpoint with `c`, then create the line-18 breakpoint and its command list in
that active debugger. `commands 1` changes the prompt to `(com)` until `end`.

At line 18, `total` has already been initialized, and the loop has selected a
die, but that die's value has not yet been added. The command list prints `0`
on the first hit and `6` on the second. `c` resumes from each hit. We clear the
breakpoint before quitting.

<!-- transcript:commands:start -->
```text
> <repo>/main.py(1)<module>()
-> from dicegame.runner import GameRunner
(Pdb) !import random
(Pdb) !random.seed(0)
(Pdb) c
Add the values of the dice
It's really that easy
What are you doing with your life.
> <repo>/main.py(8)main()
-> breakpoint()
(Pdb) b dicegame/runner.py:18
Breakpoint 1 at <repo>/dicegame/runner.py:18
(Pdb) commands 1
(com) p total
(com) end
(Pdb) c
Round 1

---------
|*     *|
|*     *|
|*     *|
---------
---------
|*     *|
|   *   |
|*     *|
---------
---------
|*      |
|   *   |
|      *|
---------
---------
|*      |
|       |
|      *|
---------
---------
|*     *|
|       |
|*     *|
---------
Sigh. What is your guess?: 10
0
> <repo>/dicegame/runner.py(18)answer()
-> total += die.value
(Pdb) c
6
> <repo>/dicegame/runner.py(18)answer()
-> total += die.value
(Pdb) cl 1
Deleted breakpoint 1 at <repo>/dicegame/runner.py:18
(Pdb) q
Quitting pdb will kill the process. Quit anyway? [y/n] y
The program exited via sys.exit(). Exit status: 1
The program finished and will be restarted
> <repo>/main.py(1)<module>()
-> from dicegame.runner import GameRunner
(Pdb) q
```
<!-- transcript:commands:end -->

This lets you inspect a loop without repeatedly typing the same expression.
Keep breakpoint numbers session-specific: each fresh session here starts with
breakpoint 1 rather than borrowing a number from an earlier run.

## 5. Diagnose the uppercase-Y exception

Start another **new** session. Seed the random generator, use `c` to reach the
inline breakpoint, then `c` again to run the game. Enter `10` and then uppercase
`Y` at the game's replay prompt.

The game reports the wrong guess normally, then raises `UnnecessaryError`
instead of accepting `Y`. Because the game is running under `python -m pdb`,
the debugger enters post-mortem inspection automatically. Inspect `some_value`
and `value` in the raising function, then use `q` to exit.

<!-- transcript:postmortem:start -->
```text
> <repo>/main.py(1)<module>()
-> from dicegame.runner import GameRunner
(Pdb) !import random
(Pdb) !random.seed(0)
(Pdb) c
Add the values of the dice
It's really that easy
What are you doing with your life.
> <repo>/main.py(8)main()
-> breakpoint()
(Pdb) c
Round 1

---------
|*     *|
|*     *|
|*     *|
---------
---------
|*     *|
|   *   |
|*     *|
---------
---------
|*      |
|   *   |
|      *|
---------
---------
|*      |
|       |
|      *|
---------
---------
|*     *|
|       |
|*     *|
---------
Sigh. What is your guess?: 10
Sorry that's wrong
The answer is: 20
Like seriously, how could you mess that up
Wins: 0 Loses 1
Would you like to play again?[Y/n]: Y
Traceback (most recent call last):
  File "<stdlib>/pdb.py", line 3873, in main
    pdb._run(target)
    ~~~~~~~~^^^^^^^^
  File "<stdlib>/pdb.py", line 2770, in _run
    self.run(target.code)
    ~~~~~~~~^^^^^^^^^^^^^
  File "<stdlib>/bdb.py", line 912, in run
    exec(cmd, globals, locals)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1, in <module>
  File "<repo>/main.py", line 13, in <module>
    main()
    ~~~~^^
  File "<repo>/main.py", line 9, in main
    GameRunner.run()
    ~~~~~~~~~~~~~~^^
  File "<repo>/dicegame/runner.py", line 60, in run
    i_just_throw_an_exception()
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "<repo>/dicegame/utils.py", line 11, in i_just_throw_an_exception
    raise UnnecessaryError("You actually called this function...")
dicegame.utils.UnnecessaryError: You actually called this function...
Uncaught exception. Entering post mortem debugging
Running 'cont' or 'step' will restart the program
> <repo>/dicegame/utils.py(11)i_just_throw_an_exception()
-> raise UnnecessaryError("You actually called this function...")
(Pdb) p some_value
"I don't know what you were expecting"
(Pdb) p value
1
(Pdb) q
```
<!-- transcript:postmortem:end -->

Post-mortem inspection exposes the state retained by the traceback. It does
**not** resume the failed game. In this mode, the debugger explicitly says that
`cont` or `step` will restart the program.

### Find the cause and make a fix

Read `dicegame/runner.py`, especially the replay condition on line 57. It accepts
lowercase `'y'` and the empty string, but uppercase `'Y'` goes to the exception
branch. A useful replacement for the replay condition and its branches is:

```python
if prompt.lower() in {"y", ""}:
    continue
else:
    break
```

This accepts either case and exits normally for other responses. These lines
are a suggested edit, not an edit already applied to the exercise files. Once
you change source, its behavior can differ from the pre-fix transcripts. Start
a new process to test your change.

For the round-counter bug, find `runner = cls()` inside the `while True` loop.
That constructs a new runner, whose constructor calls `reset()`, on every round.
Move the construction before the loop to preserve the score and round number.
Think separately about when the dice should be rerolled. The `solutions/`
directory provides a reference implementation, and the tests exercise its
six-consecutive-win path.

For post-mortem debugging in your own code, `pdb.post_mortem()` can be called
inside an exception handler. At an interactive Python prompt, `pdb.pm()` instead
uses the last unhandled exception. These are alternative entry points, not
additional steps required for the captured session above.

## 6. Keep the tutorial verifiable

From a clean, unedited exercise snapshot, run:

```sh
nix develop -c python -m unittest discover -s tests -v
nix develop -c python tools/render_walkthrough.py --check
```

The second command executes all three sessions and compares their entire output
with the README blocks. It fails if commands, line numbers, or output drift.
It requires exactly Python 3.15.2. The capture wrapper echoes supplied input as
a terminal would, but leaves the debugger, program, and source files unchanged.

Maintainers can deliberately refresh the blocks after changing the exercise:

```sh
nix develop -c python tools/render_walkthrough.py
```

After regeneration, also review the prose against the new stop positions and
results. GitHub Actions runs the tests and transcript comparison on Python
3.15.2. A learner who edits the exercise is expected to change its output, so
the transcript check is a baseline maintenance check, not a restriction on
solving the bugs.

## Credits and translations

This fork builds on the original `spiside/pdb-tutorial` dice-game debugging
exercise. Community translations of the original tutorial are available in
Korean (`mingrammer/pdb-tutorial`), Chinese (`MartinLwx/pdb-tutorial`), and
Russian (`0xfadeef/pdb-tutorial`). They are independent versions and are not the
source for this branch's Python 3.15.2 transcripts.
