---
name: ccc-solve
description: Fast loop for solving a CCC level on codingcontest.org with the arena CLI (fetch → read statement → write solve.py → go). Use when training on a practice game or during the contest, whenever the user says "solve level N", "next level", "start training on <game>", or "contest started".
---

# CCC Solve Loop

CLI: `python arena/ccc.py` from the repo root (details in `arena/README.md`). **Target: 2 tool calls per level, which are writing solve.py and running `go`.**

## 0. Setup (once)
- **Contest:** follow `docs/strategy/contest-day-runbook.md`. From T-15 min, run `python arena/golive.py --browser` in the **background** (run_in_background). It does preflight, multi-detector watch and auto-register, and when it exits its output already contains the level 1 statement and example. On failure it prints the fallback ladder (`fetch N --zip <file>` for manual zips).
- **Training (platform):** `python arena/ccc.py train <gameSlug> --mode exploration|challenge --name <short>`, then `fetch 1`.
- **Training (offline past games, local judge):** `python arena/offline.py list`, then `python arena/offline.py start <game> --name <run>`. It prints level 1. Use `go N` as usual: the judge is local, levels unlock as you pass, and `runs/<run>/timing.jsonl` logs fetch/pass/wrong events.
- Check: `python arena/ccc.py info`.

## The speed rules (Spaceship rehearsal: about 20 of L7's 29 min were spent waiting on runs that were too slow)
1. **Read `sizes:` first.** It decides the algorithm.
2. **Never start a full run blind.** For anything non-trivial, run `python arena/ccc.py probe N` first (≤ 25 s). It times a sample of the largest and random cases in parallel and prints `VERDICT: OK / SLOW (go N --timeout X) / TOO SLOW`. On TOO SLOW, or "heavy tail" (cases unfinished at the budget), change the algorithm or heuristic. Don't wait.
3. **Use `run_cases(cases, solve_case)`** (the stub template). It gives free parallelism across cases on 16 cores, progress and ETA lines, and probe support.
4. **No side work while a level is unsolved.** No infra fixes and no doc edits. Every minute goes to the current level.
5. `go`/`run` default to a 180 s timeout. Raise it only with a probe ETA in hand.

## 1. Read
`fetch N` (or the tail of `go N-1`) prints the cleaned statement, the example input and the expected output. **Do not re-read files that were already printed.**
- `!!!!! RULES ARE IN IMAGES`: **Read the listed page PNGs before the first submit, every time**, even when the example looks self-explanatory. The objective ("shortest", "highest score", "exactly L steps") and special rules ("coins respawn", "ghost tie-break by alphabet") live there. Pacman L6 cost a WRONG when it was skipped.
- `!!!!! expected output has N BLANK separator line(s)`: keep them (`run_cases(..., sep="\n\n", header=True)`). **Never pipe fetch/go output through `grep -v '^\s*$'`**: it hides the output format (Honeycomb L5: 2 WRONGs).
- **Movement/collision/simulation semantics unclear?** The visualizer HTML (`files/sandbox-level-N.html`) contains the exact rules in its JS. Grep it (e.g. `hasShipCollided`, `move`, `calculateHistory`).
- Write solvers with the Write tool. Don't patch them through shell heredocs: escaping errors cost minutes in rehearsal.
- Lines starting `[repaired]` were garbled in the PDF and were auto-decoded. If a diagram, colours or a picture matter, run `fetch N --png` and Read `levelN/pages/pK.png`. The page numbers appear as `[pK]` in the statement.
- `levelN/sandbox.html`, when present, is the official visualizer.

## 2. Write `arena/runs/<run>/levelN/solve.py`
- It is already a **copy of level N-1's solver**. Edit it: keep the parsing, change what is new.
- It reads stdin and writes stdout. For arena/lib, use the header `import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))` and then `from lib import ...`.
- Shape: `cases(data) -> list` and `solve_case(c) -> str`, with `if __name__ == "__main__": run_cases(cases, solve_case)`. For a whole-file problem, return `[data]` from cases. Shared precomputed tables: `run_cases(cases, solve_case, init=fn, initargs=(...))`. `CCC_SEQ=1` gives sequential runs for debugging. `CCC_ONLY=3,7` runs only those cases.
- **Many valid answers** ("order does not matter", constructions): define `check(data, out) -> bool | (bool, msg)` in solve.py. `go` then accepts outputs that pass `check()` even if the example differs. A copied `check()` from the previous level must be updated, or deleted.

- **Patterns and helpers:** see the `ccc-patterns` skill (lib cheat sheet, pattern → technique). For profiling: `python arena/lib/check.py arena/runs/<run>/levelN --profile`.
- **Heavy brute force or simulation:** make the first line of solve.py `# ccc: pypy` to run it on PyPy (~60× faster on plain loops). Or set `CCC_PY=pypy` per command.

## 3. `python arena/ccc.py go N` (use a tool timeout of 600000 ms)
It runs all inputs in parallel and verifies (example or check). It submits sequentially, smallest first, and stops at the first WRONG. Passed files are skipped. Slow levels: `probe N` first (see the speed rules).
- **PASSED:** it prints the next level's statement in the same output. Go straight to step 2 for N+1.
- **WRONG:** read the case line ranges and messages, fix, and run `go N` again.
- **EXAMPLE MISMATCH** with no check: look at the shown first diff and fix. If the answer is non-unique, add `check()`. `--force` is the last resort.
- **CRASH / TIMEOUT:** the traceback is shown once. Optimise, or use `--timeout`.

## Rules
- Never submit files in parallel or from two sessions at once: the server loses updates. Teammates coordinate per level.
- Never submit unverified output. A wrong submit may cost penalty time.
- Later levels often say "validate with your previous code", so keep `check()` functions around.
- After each passed level (contest): `git add arena/runs && git commit -m "<run> level N" && git push`. Run it in the background; don't wait on it.
