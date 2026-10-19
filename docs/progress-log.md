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

## 2026-10-19: Session 5: Speed pass, dataset, training, model A/B (4 days left)
**Why:** Teo was not satisfied with the Spaceship rehearsal time (36.6 min). The transcript showed that about 20 of L7's 29 min were spent waiting on runs that were too slow, not thinking.

**Built**
- `lib.runner.run_cases`: a pool across cases on 16 cores, progress and ETA lines, names the cases still running at the end, `sep`/`header` output options.
- `ccc.py probe N`: about 20 s for a sample of the largest and random cases, an ETA, and a verdict of OK / SLOW / TOO SLOW / HEAVY TAIL. It predicted 135 s for Spaceship L7, and the actual run took 154 s.
- `ccc.py` changes:
  - progress is streamed;
  - default timeout 180 s;
  - `go` blocks output whose blank-line structure differs from the example;
  - `fetch` flags blank-line separators and text-less image pages;
  - a teammate clone can run `run`/`probe` without state;
  - `pass` events are logged.
- `lib.cp`: CP-SAT with circuit and exact cover. Lawn Mower L7 first try, 128 cases in 32 s.
- `lib.flow`: an OR-Tools vertex cut.
- Installed ortools, python-sat, z3 and sortedcontainers.
- `arena/offline.py`: past games from GitHub archives, played through the same `go` loop. It has a local judge (reference outputs, plus judges written by a separate agent so the trainee stays unspoiled), unlocks levels and writes `timing.jsonl`. 4 fresh games, 25 levels.
- Agents `ccc-solver-{opus,sonnet}`. Runbook: model choice, probe-first rules, and an optional teammate second-opinion protocol.

**Training (timed)**
- Honeycomb (School): 5/5 in 3.4 min.
- Pacman: 7/7 in 3.0 min.
- Islands: 7/7 in 22.3 min. On L7 a heavy-tailed parity BFS was replaced by a min vertex cut, about 0.1 s per case.
- School games are too easy to teach anything; use them only as drills.

**Model A/B (cold subagents, same unseen games)**
- interp2021: Sonnet 50 s, Opus 49 s.
- Smart Grid: Sonnet 263 s, Opus 249 s.
- Both had 0 WRONG. Sonnet broke 2 process rules.
- **Opus drives on contest day.** `/fast` is optional: it uses extra usage credits and must be enabled at the start of the session.

**Lessons**
- Probe before running.
- Read the rule images before the first submit.
- Never strip blank lines from the output.
- Never patch solvers through heredocs (this broke 5 times today).
- "Shortest loop around X keeping Y outside" is a min vertex cut.

**Next:** Thursday is a final short dress rehearsal (a School game: drones or asteroid-mining) in the contest configuration, then `golive --preflight`. On Friday, follow `contest-day-runbook.md`.

## 2026-10-19: Session 6: Spaceship re-run after the speed pass (4 days left)
**Done:** timed re-run of Spaceship, the 2025 Classic, in the `ship2` run. **8/8 in 13.9 min, down from 36.6 min.** L1–L6 took 4.6 min, L7 7.0 min (284 s of it was the solver run), L8 2.2 min. Every file is CORRECT on the real judge (verified via `submit --only`, because the platform reused the existing, already-passed training contest). Details are in `strategy/workflow-speed.md`.

**Lessons**
- The training start reuses a RUNNING contest, so re-runs need `submit --only`.
- Never pipe `go` and then chain a submit: the exit code is lost and unverified output gets submitted.
- Probe ETAs miss internal-retry tails (55 s predicted, 284 s actual).
- Weighted A* needs a closed set (no reopening) when paths are rebuilt from parent pointers.
- A heredoc patch slipped in again on L4: use Write/Edit only.

**Next:** unchanged. A Thursday dress rehearsal on an unseen School game, then `golive --preflight`, then Friday's runbook.
