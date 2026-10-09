---
name: ccc-solve
description: Fast loop for solving a CCC level on codingcontest.org with the arena CLI (fetch → read statement → write solve.py → go). Use when training on a practice game or during the contest, whenever the user says "solve level N", "next level", "start training on <game>", or "contest started".
---

# CCC Solve Loop

CLI: `python arena/ccc.py` from the repo root (details in `arena/README.md`). **Target: 2 tool calls per level, which are writing solve.py and running `go`.**

## 0. Setup (once)
- **Contest:** from T-15 min, run `python arena/ccc.py wait` in the **background** (run_in_background). When it exits, its output already contains the level 1 statement and example. If it says SESSION EXPIRED, run `login` and restart it.
- **Training:** `python arena/ccc.py train <gameSlug> --mode exploration|challenge --name <short>`, then `fetch 1`.
- Check: `python arena/ccc.py info`.

## 1. Read
`fetch N` (or the tail of `go N-1`) prints the cleaned statement, the example input and the expected output. **Do not re-read files that were already printed.**
- If a diagram, colours or a picture matter, run `fetch N --png` and Read `levelN/pages/pK.png`. The page numbers appear as `[pK]` in the statement.
- `levelN/sandbox.html`, when present, is the official visualizer.

## 2. Write `arena/runs/<run>/levelN/solve.py`
- It is already a **copy of level N-1's solver**. Edit it: keep the parsing, change what is new.
- It reads stdin and writes stdout. For arena/lib, use the header `import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))` and then `from lib import ...`.
- **Many valid answers** ("order does not matter", constructions): define `check(data, out) -> bool | (bool, msg)` in solve.py. `go` then accepts outputs that pass `check()` even if the example differs. A copied `check()` from the previous level must be updated, or deleted.

## 3. `python arena/ccc.py go N` (use a tool timeout of 600000 ms)
It runs all inputs in parallel and verifies (example or check). It submits sequentially, smallest first, and stops at the first WRONG. Passed files are skipped.
- **PASSED:** it prints the next level's statement in the same output. Go straight to step 2 for N+1.
- **WRONG:** read the case line ranges and messages, fix, and run `go N` again.
- **EXAMPLE MISMATCH** with no check: look at the shown first diff and fix. If the answer is non-unique, add `check()`. `--force` is the last resort.
- **CRASH / TIMEOUT:** the traceback is shown once. Optimise, or use `--timeout`.

## Rules
- Never submit files in parallel or from two sessions at once: the server loses updates. Teammates coordinate per level.
- Never submit unverified output. A wrong submit may cost penalty time.
- Later levels often say "validate with your previous code", so keep `check()` functions around.
- After each passed level (contest): `git add arena/runs && git commit -m "<run> level N" && git push`. Run it in the background; don't wait on it.
