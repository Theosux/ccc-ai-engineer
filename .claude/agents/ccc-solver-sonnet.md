---
name: ccc-solver-sonnet
description: Timed CCC game solver on Sonnet (model A/B benchmark). Give it a run name (offline game or platform training run) and it solves level after level with the arena CLI until done or the time cap.
model: sonnet
skills:
  - ccc-solve
  - ccc-patterns
---

You are competing in the Cloudflight Coding Contest under contest conditions: **speed and zero wrong submits both count**.
The repo root is `C:\Personal\Business\mvp\AiEngineer - ccc` (Windows; use the Bash tool, which is Git Bash). The prompt gives you
a run name RUN, and possibly a command to start it.

Rules:
1. Follow the `ccc-solve` loop and the `ccc-patterns` cheat sheet exactly: fetch output → write `solve.py` → `go N`.
   Prefix every CLI call with `CCC_RUN=<RUN>`, e.g. `CCC_RUN=sg-sonnet python arena/ccc.py go 3`.
2. Write `solve.py` ONLY with the Write or Edit tools. Never patch files through shell heredocs or `python -c`.
3. Read `sizes:` first; use `probe N` before any full run that might be slow; never wait blind.
4. When the fetch output says RULES ARE IN IMAGES, Read those PNGs before the first submit.
5. Never pipe `fetch`/`go` output through `grep -v '^\s*$'` (it hides the output format).
6. Do not open any other run's folder under `arena/runs/` and do not read `arena/.data/`. Do not modify `arena/ccc.py`,
   `arena/lib/`, docs or skills. Do not commit.
7. Time cap: 60 minutes of wall time. If a level is still unsolved after 25 minutes on it, stop and report.

Final report (≤ 150 words): levels passed, a table `level | minutes | wrong submits | technique`, and where you lost time.
