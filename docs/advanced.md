# Breakpoint command lists

This optional example builds on the commands introduced in the main tutorial.
Start a **new** session from an unedited copy of the exercise. Do not continue
from the post-mortem prompt at the end of the main lesson.

```sh
python -m pdb main.py
```

1. Set the random seed and enter `c` to reach the inline breakpoint, as before.
2. Enter `b dicegame/runner.py:18` to stop before the loop increments `total`.
3. Enter `commands 1`. At the `(com)` prompt, enter `p total`, followed by `end`.
4. Enter `c`, then answer the game's guess prompt with `20`.

The command list automatically prints `0` at the first breakpoint hit. Enter `c`
again and it prints `1` on the second hit. You no longer need to type `p total`
on each iteration. This also exposes the same summation bug as the main lesson:
`total` increases by one rather than by the die's value.

Enter `cl 1` to remove the breakpoint. Then quit with `q`, confirm with `y`, and
enter `q` at the command-line debugger's restart prompt to return to the shell.

<details>
<summary>Complete captured session on Python 3.14.8</summary>

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
Sigh. What is your guess?: 20
0
> <repo>/dicegame/runner.py(18)answer()
-> total += 1
(Pdb) c
1
> <repo>/dicegame/runner.py(18)answer()
-> total += 1
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

</details>

Breakpoint numbers belong to a session. This example uses a fresh session so
its first breakpoint is number 1.

[Back to the tutorial](../README.md)
