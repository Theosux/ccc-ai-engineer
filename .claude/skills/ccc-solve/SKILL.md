---
name: ccc-solve
description: Fast loop for solving a CCC level on codingcontest.org with the arena CLI (fetch → read statement → write solve.py → go). Use when training on a practice game or during the contest, whenever the user says "solve level N", "next level", "start training on <game>", or "contest started".
---

# CCC Solve Loop

The CLI is `python arena/ccc.py` (see `arena/README.md`). Commands run from the repo root.

## 0. Session setup (once)
- Check the active run: `python arena/ccc.py info`.
  - If it says "not logged in", run `python arena/ccc.py login`. Teo logs in through the Edge window.
- **Training:** `python arena/ccc.py train <gameSlug> --mode exploration|challenge --name <short>`. List the slugs with `games`.
- **Contest:** `python arena/ccc.py contest 42nd-classic-ccc-5872 --name contest`, run once the contest has started.

## 1. Fetch
`python arena/ccc.py fetch N` creates `arena/runs/<run>/levelN/`:
- `files/`: the unzipped level. Inputs are `in_level-N_<fileId>.txt` with fileIds `0-example`, `1-small`, `2-small`, `3-medium`, `4-medium`, `5-large`. The expected example output is `out_level-N_0-example.txt`. The statement is `level-N.pdf`.
- `statement.txt`: text extracted from the PDF. **Read this first.** Only Read the PDF itself if the text is ambiguous or a diagram matters.
- `solve.py`: a stub.

## 2. Solve
- Write `levelN/solve.py`. It reads **stdin** and writes **stdout**, with no file I/O.
- Check whether the statement says "Input — identical to previous level". If it does, copy the previous level's `solve.py` and change only the output logic.
- Parse with `data.split()` (tokens) unless lines matter, for example grids containing spaces.
- Keep it simple and correct. Inputs are small (≈150 KB), so brute force usually works on early levels.

## 3. Run and submit
`python arena/ccc.py go N`:
- It runs every input, compares the example with the expected output, and **submits only if the example matches**.
- It prints a verdict per file: `CORRECT (k/k cases)` or `WRONG` with the line ranges of the failing cases and a message such as "Wrong answer, got 'X'".
- If one file is wrong: fix the solver, then `python arena/ccc.py run N` followed by `submit N --only <fileId>`.
- The per-file cooldown after a submit is about 5 s. `submit` waits it out automatically.
- If the solver times out on large inputs, optimise, or raise the limit with `--timeout`.

## 4. Next
Once all scored files pass, the next level unlocks: `fetch N+1`. The level status shows in `info`.

## Speed rules (contest)
- Never submit unverified output. A wrong submit may cost penalty time (unconfirmed for 2026).
- Build a small validator when a level asks for one. Later levels often reuse it ("use your code from the previous level to validate").
- Commit solutions after each passed level: `git add arena/runs && git commit -m "<run> level N" && git push`.
