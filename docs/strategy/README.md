# Strategy

## Contest-day workflow (v2, rehearsed 2026-10-19)
**Full timeline and fallbacks:** [contest-day-runbook.md](contest-day-runbook.md).
1. **T-15:** `python arena/golive.py --browser` (background). It runs the preflight and detectors D1–D6, auto-registers, and prints level 1. Rehearsed on a Challenge training: live to level 1 statement in 19 s.
2. **Per level:** the `ccc-solve` + `ccc-patterns` loop. Read `sizes:`, write `solve.py` (with `check()`), run `go N`. On a pass it prints level N+1.
3. **After each level:** commit in the background.

## Training status
| Run | Game | Mode | Levels passed | Notes |
|---|---|---|---|---|
| lawnmower | ccc-2024.04-classic-lawn-mower | exploration | **1–7 (all)** | L4 ~4 min, L5 40 s, L6 1.5 min, L7 24 min. L7 (Hamiltonian cycle with several trees) needed an exact solver with restarts, now `lib.paths.ham_cycle` |
| speedtest | ccc-2024.10-classic-desks | exploration | **1–7 (all)** | L4–L7 in 6.5 min (lib `pack`) |
| rps | ccc-2023.03-classic-rock-paper-scissors | exploration | **1–7 (all)** | 11 min total (lib `tourney`); rules partly in PDF images |
| **spaceship** | ccc-2025.11-classic-spaceship | **challenge (timed)** | **1–8 (all) in 36.6 min** | L7 29 min (A\* + maze heuristic + multiprocessing), L8 1.8 min. The 2025 winners: 7/8 in 3h42m |

| honeycomb | ccc-2023.03-school-honeycomb | challenge (platform) | **1–5 (all) in 3.4 min** | 2 WRONG (blank-line output format) → `go` now blocks on shape mismatch |
| pacman | Pacman (offline, `arena/offline.py`) | timed | **1–7 (all) in 3.0 min** | 1 WRONG (skipped the rules image) |
| islands | Islands 2023 (offline) | timed | **1–7 (all) in 22.3 min** | L7 13.5 min: parity BFS heavy tail → **min vertex cut** (`lib.flow`) |
| i21-*, sg-* | interp2021, Smart Grid (offline) | model A/B | 4/4 in ~50 s; 7/7 in ~4.2 min | Sonnet = Opus on speed, 0 WRONG both; Opus more disciplined → **Opus drives** |

Speed details, the time-sink analysis, Claude Code speed settings and the A/B are in [workflow-speed.md](workflow-speed.md).

## Ideas to build next
- ~~Timed rehearsal~~: done (Spaceship 8/8, 36.6 min). ~~Penalty check~~: no penalty in passedAt.
- **Parallelism:** for a team of 2–3, each person runs their own Claude session on a different level or approach. Any member can submit.
