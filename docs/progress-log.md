# Progress Log

## 2026-10-09 — Session 1: Workspace + contest research
**Done**
- Created the project scaffold, the `ccc-context` ritual skill, and the private repo Theosux/ccc-ai-engineer.
- Ran 2 research agents (rules/format/scoring; platform mechanics) and 1 verification agent. Wrote the verified facts into `docs/contest/`.

**Key findings**
- **When:** 23 Oct 2026, 13:00 UTC (16:00 Romania), 4 hours. Solo or teams of up to 3.
- **Format:** about 7–8 levels that unlock one after another. You submit output files only and get an instant verdict per file.
- **Platform:** Catcoder is retired. 2026 is the first contest on the new platform, so the old CLI tools are probably broken.
- **AI:** no explicit AI rule exists, but it is clearly tolerated or expected.

**Open, for Teo to resolve**
- Confirm the AI policy with the organizers.
- Find out whether wrong submissions still cost +1 minute.
- In Exploration mode: check the cooldown length and the zip file names.
- Pick a venue.

**Next:** log in to /challenges and run Exploration mode on a past Classic game (Lawn Mower or Room Planner) to capture the real 2026 zip format and upload flow. Then design the contest-day pipeline (`docs/strategy/`) and the first custom solving skills.

## 2026-10-09 — Session 2: Arena workflow, tested live
**Done**
- Teo registered a team and cleared the rules with the organizers.
- Reverse-engineered the new platform's API from its JS bundles. Built `arena/ccc.py`:
  - `login` uses Edge via Playwright with a dedicated profile; cookies are kept in the gitignored `arena/.auth/`.
  - The other commands: `train`, `contest`, `fetch`, `run`, `submit`, `go`, `info`, `api`.
- Added the `ccc-solve` skill (the per-level loop) and `arena/README.md` (folder map).
- **Live test:** Lawn Mower in Exploration mode. Levels 1–3 all passed, about 30 s per level.
- **Confirmed facts:**
  - Zip naming: `in_level-N_<fileId>.txt`.
  - The statement is a PDF, auto-extracted to `statement.txt`.
  - Verdicts come per case with line ranges.
  - The per-file cooldown is about 5 s.

**Next:** Lawn Mower L4+ (the first real algorithmic levels). Then a timed Challenge-mode rehearsal, which will also show whether wrong submits add penalty time. Then build a small solver helper library.

## 2026-10-09 — Session 3: Optimization pass (2 agents)
**Done**
- **Speed agent:** rewrote `arena/ccc.py`. The target is 2 tool calls per level: write solve.py, then run `go N`.
  - `fetch` prints the cleaned statement and the example. A new level's solve.py starts as a copy of the previous level's.
  - `go` runs all inputs in parallel and verifies against the example or `check()`. It submits sequentially, smallest file first, stops on the first WRONG, then auto-fetches N+1.
  - New commands: `wait` (contest start), `login --http` (uses `arena/.auth/credentials.env`).
  - Runbook: `docs/strategy/workflow-speed.md`.
- **Knowledge agent:** built `arena/lib/` (parsers, grid, Hamiltonian paths/cycles, search, simulation, optimization, geometry, checks; tests pass). Wrote `docs/knowledge/` (patterns, playbook, past games, resources) and the `ccc-patterns` skill.
  - **Lawn Mower 7/7 solved.**
- **Main session:**
  - PyPy is now in `arena/.tools/pypy`, selected with `# ccc: pypy` or `CCC_PY=pypy`.
  - Garbled PDF lines are auto-repaired (glyph shift −29).
  - `.gitattributes` keeps inputs byte-exact.
  - PDFs and PNGs are gitignored.

**Key lessons**
- Never submit in parallel: the server loses concurrent updates. This also applies to teammates.
- Constructive levels need `check()`. Write each construction generally, because the next level usually drops a guarantee.
- Hamiltonian-type searches have heavy tails: use a portfolio of restarts, not longer timeouts.

**Open:** Teo will create `arena/.auth/credentials.env` (CCC_USER/CCC_PASS) for automatic re-login.

**Next:** a timed Challenge-mode rehearsal on Spaceship (8 levels, the 2025 game). It will measure the real per-level pace, the unlocking in timed mode, and whether wrong submits add penalty time.

## 2026-10-19 — Session 4: Go-live automation + timed rehearsal (4 days left)
**Done**
- Teo created `arena/.auth/credentials.env`. It is gitignored (verified), and the automatic HTTP re-login with it works (the session had expired after 10 days).
- **`arena/golive.py`:**
  - Preflight checks: login, CLASSIC registration (team Krateo, CREIC Cluj; AI ignored), contest, clock offset, latency, game token, PyPy, lib tests, git, disk, browser.
  - Multi-detector watch: D1 adaptive contest poll, D2 SSE status stream, D3 my-registrations, D4 level-1 download probe, D6 Edge witness (network-based), plus keep-alive.
  - Trigger: register, beep and toast, `LIVE.txt`, print level 1.
  - Read-only `--observe school` to record the real #school go-live at 08:00 UTC on contest day.
  - 11 offline fixture tests (`arena/tests/test_golive.py`).
- **`ccc.py`:**
  - `fetch --zip` (emergency manual zip);
  - `fetch` now prints input `sizes:`;
  - pages that are image-only are auto-rendered and flagged;
  - garble variant 2 is repaired;
  - check-OK mismatch wording is clearer.
- `docs/strategy/contest-day-runbook.md` (timeline, detectors, fallback ladder).
- **Training agent:** Room Planner 7/7 and RPS 7/7 with zero wrong submits. New lib modules `pack` and `tourney`; knowledge §6/§7.
- **Timed Challenge rehearsal on Spaceship (the 2025 game): 8/8 in 36.6 min.** golive went from live to level 1 in 19 s. L1–L6 took 5.4 min, L7 29.4 min (A* + geodesic heuristic + multiprocessing), L8 1.8 min (time-dependent A*). The 2025 winners did 7/8 in 3h42m, and nobody solved L8.

**Key findings**
- `/api/game-token` is issued days BEFORE the start, so it is not a live signal. D4 probes whether level 1 can be downloaded instead.
- A wrong submit added NO penalty to `passedAt` (Challenge mode).
- The visualizer JS contains the exact simulation and collision rules.
- Check input sizes before choosing an algorithm.

**Next (contest day, 23 Oct):** follow `docs/strategy/contest-day-runbook.md`.
- 10:45 Cluj: start `golive --observe school`.
- 11:15: compare the observed go-live against our detectors.
- 15:45: start `golive --browser`.
- Optional before then: one more timed rehearsal (Lawn Mower or Room Planner in Challenge mode) to keep the routine sharp.
