# Learn `pdb` by debugging a dice game

The game asks you to add five dice, but it rejects the right answer. You'll use
Python's built-in debugger to find out why, then investigate a second bug in the
replay prompt.

Follow the steps in order. They form **one debugging session**: keep the program
open between steps, and leave source-code changes until the end.

## Set up

You need Git and Python **3.14**. The output below was recorded on Python 3.14.8.

```sh
git clone https://github.com/trbutler4/pdb-tutorial.git
cd pdb-tutorial
python --version
```

Check that the last command reports Python 3.14.

<details>
<summary>Using Nix instead of an installed Python</summary>

On Linux (x86-64 or ARM64) or Apple Silicon macOS with flakes enabled,
the repository provides a pinned interpreter:

```sh
nix develop
python --version
```

Stay in this shell for the rest of the lesson.

</details>

## 1. Pause the program

Run this from the repository directory:

```sh
python -m pdb main.py
```

The `(Pdb)` prompt means the debugger is waiting for a command. Type only the
text after the prompt, not `(Pdb)` itself.

Enter `!import random`, then `!random.seed(0)`, then `c`. The `!` prefix runs a
Python statement inside the debugger. The first two commands make the dice match
this walkthrough. `c` means **continue**: let the program run
until it reaches the `breakpoint()` already included in `main.py`.

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
```

You're now paused inside `main()`. `<repo>` in the output stands for the path to
your copy of the repository.

## 2. See where you stopped

Enter `l 4, 9`. The `l` command **lists source code**; here it shows lines 4 to 9.

```text
(Pdb) l 4, 9
  4  	def main():
  5  	    print("Add the values of the dice")
  6  	    print("It's really that easy")
  7  	    print("What are you doing with your life.")
  8  ->	    breakpoint()
  9  	    GameRunner.run()
```

The arrow marks the current line. The next line calls `GameRunner.run()`, which
is where the game logic lives.

## 3. Step into the game

Enter `n`, then `s`:

- `n` means **next**. It advances from the inline breakpoint to the next line.
- `s` means **step**. It follows the call into `GameRunner.run()`.

```text
(Pdb) n
> <repo>/main.py(9)main()
-> GameRunner.run()
(Pdb) s
--Call--
> <repo>/dicegame/runner.py(21)run()
-> @classmethod
```

`--Call--` means you've entered a function. In this Python version, that event
points at the `@classmethod` decorator. The function body hasn't run yet.

Enter `n` twice, then `p c`:

```text
(Pdb) n
> <repo>/dicegame/runner.py(25)run()
-> c = 0
(Pdb) n
> <repo>/dicegame/runner.py(26)run()
-> while True:
(Pdb) p c
0
```

The first `n` reaches `c = 0`; the second executes it. `p c` **prints the value**
of the variable. Don't enter `c` alone to inspect it: that would continue running
the program.

## 4. Inspect the dice

Enter `n` twice to create the game runner. Then enter
`p [die.value for die in runner.dice]` to see its dice values.

```text
(Pdb) n
> <repo>/dicegame/runner.py(27)run()
-> runner = cls()
(Pdb) n
> <repo>/dicegame/runner.py(29)run()
-> print("Round {}\n".format(runner.round))
(Pdb) p [die.value for die in runner.dice]
[6, 5, 3, 2, 4]
```

The dice are **6, 5, 3, 2, 4**. Their sum is **20**. Remember that number for the
guess prompt.

## 5. Skip ahead to the guess prompt

Rather than step through every dice-printing operation, set a **breakpoint** at
the input line:

1. Enter `b 34` to break at line 34 of the current file, `dicegame/runner.py`.
2. Enter `c` to continue to that line.
3. Enter `cl 1` to clear breakpoint number 1 once you've reached it.

The game prints the dice and stops **before** asking for a guess. The current
line should be `guess = input("Sigh. What is your guess?: ")` on line 34.

<details>
<summary>Check the output, including the dice display</summary>

```text
(Pdb) b 34
Breakpoint 1 at <repo>/dicegame/runner.py:34
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
> <repo>/dicegame/runner.py(34)run()
-> guess = input("Sigh. What is your guess?: ")
(Pdb) cl 1
Deleted breakpoint 1 at <repo>/dicegame/runner.py:34
```

</details>

## 6. Enter the correct total

Enter `n` to execute the input line. When the **game** asks for your guess, enter
`20`. This is game input, not a debugger command.

```text
(Pdb) n
Sigh. What is your guess?: 20
> <repo>/dicegame/runner.py(35)run()
-> guess = int(guess)
```

You're back at `(Pdb)`, just before the guess is converted from text to an
integer.

## 7. Find how the answer is calculated

Enter `n` to convert the guess. Then enter `s` to step into the `answer()` call
on the comparison line.

```text
(Pdb) n
> <repo>/dicegame/runner.py(37)run()
-> if guess == runner.answer():
(Pdb) s
--Call--
> <repo>/dicegame/runner.py(15)answer()
-> def answer(self):
```

Enter `n` three times to reach the first addition in the loop. Then use
`p die.value` to inspect the die being processed.

```text
(Pdb) n
> <repo>/dicegame/runner.py(16)answer()
-> total = 0
(Pdb) n
> <repo>/dicegame/runner.py(17)answer()
-> for die in self.dice:
(Pdb) n
> <repo>/dicegame/runner.py(18)answer()
-> total += 1
(Pdb) p die.value
6
```

The die's value is **6**, but line 18 says **`total += 1`**. That looks suspicious:
it counts each die instead of adding the number shown on it.

## 8. Check the function's result

Enter `p sum(die.value for die in self.dice)` to calculate the actual total.
Then enter `r`, followed by `p total`.

`r` means **return**: finish this function without stepping through the rest of
its loop.

```text
(Pdb) p sum(die.value for die in self.dice)
20
(Pdb) r
--Return--
> <repo>/dicegame/runner.py(19)answer()->5
-> return total
(Pdb) p total
5
```

There's the first bug: the dice add up to **20**, but `answer()` returns **5**.
It adds one for each of the five dice, regardless of their values.

Keep the source unchanged for now so you can continue this same session.

## 9. Trigger the replay bug

Enter `c` to let the game finish checking your guess. It incorrectly says the
answer is 5. At `Would you like to play again?[Y/n]:`, enter uppercase **`Y`**.

The game crashes with `UnnecessaryError`. Since you launched it under `pdb`,
you're returned to a debugger prompt at the line that raised the exception.

<details>
<summary>Check the exception output</summary>

```text
(Pdb) c
Sorry that's wrong
The answer is: 5
Like seriously, how could you mess that up
Wins: 0 Loses 1
Would you like to play again?[Y/n]: Y
Traceback (most recent call last):
  File "<stdlib>/pdb.py", line 3656, in main
    pdb._run(target)
    ~~~~~~~~^^^^^^^^
  File "<stdlib>/pdb.py", line 2566, in _run
    self.run(target.code)
    ~~~~~~~~^^^^^^^^^^^^^
  File "<stdlib>/bdb.py", line 913, in run
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
```

`<stdlib>` stands for Python's standard-library directory.

</details>

You can now inspect the state left behind by the crash. This is called
**post-mortem debugging**. It does not resume the failed game.

## 10. Look at the caller

First enter `p some_value` to inspect a variable in the function that raised the
exception. Then enter `u`, short for **up**, to move to the function that called
it: `GameRunner.run()`.

Enter `p prompt` to inspect the replay response, followed by `l 55, 60` to read
the condition that handles it.

```text
(Pdb) p some_value
"I don't know what you were expecting"
(Pdb) u
> <repo>/dicegame/runner.py(60)run()
-> i_just_throw_an_exception()
(Pdb) p prompt
'Y'
(Pdb) l 55, 60
 55  	            prompt = input("Would you like to play again?[Y/n]: ")
 56
 57  	            if prompt == 'y' or prompt == '':
 58  	                continue
 59  	            else:
 60  ->	                i_just_throw_an_exception()
```

`prompt` is `'Y'`, but the condition accepts only lowercase `'y'` or an empty
string. Uppercase `'Y'` falls into the exception branch. That's the second bug.

Enter `q` to **quit** the debugger and return to your shell.

```text
(Pdb) q
```

## Try the fixes

Now that the session is over, edit `dicegame/runner.py`:

1. In `answer()`, change `total += 1` to `total += die.value`.
2. In the replay condition, compare `prompt.lower()` with `'y'` so either case is
   accepted. For other responses, exit the loop instead of raising an exception.

Run `python main.py` to try the changes. It pauses at the existing inline
breakpoint; enter `c` to play. Enter the total displayed by the dice, then `Y`
to check that both fixes work. The dice are random in this new run, so don't
assume the answer is still 20.

**One more bug to investigate:** play several rounds and watch the round number
and win count. Why do they reset? Use what you've learned to inspect where a new
`GameRunner` is created. The `solutions/` directory contains a reference version
if you get stuck.

## Commands you've used

| Command | Purpose |
| --- | --- |
| `l first, last` | Read a range of source lines. |
| `n` | Execute the next line without stepping into its calls. |
| `s` | Step into a function call. |
| `p expression` | Print the value of an expression. |
| `b line` | Set a breakpoint. |
| `cl number` | Clear a breakpoint. |
| `c` | Continue running. |
| `r` | Run until the current function returns. |
| `u` | Inspect the calling function's frame. |
| `q` | Quit. |

## Credits

Based on the original `spiside/pdb-tutorial` dice-game exercise. Community
translations of the original are available in Korean (`mingrammer/pdb-tutorial`),
Chinese (`MartinLwx/pdb-tutorial`), and Russian (`0xfadeef/pdb-tutorial`).
