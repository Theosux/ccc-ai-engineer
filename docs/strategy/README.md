# Strategy

## Contest-day workflow (v1, tested 2026-10-09)
1. **Before the start:**
   - `python arena/ccc.py info` confirms the login is still valid. If not, run `login`.
   - Have the repo open in Claude Code with the `ccc-solve` skill loaded.
2. **At the start:** `python arena/ccc.py contest 42nd-classic-ccc-5872 --name contest`, then `fetch 1`.
3. **Per level:** follow the `ccc-solve` loop.
   - Claude reads `statement.txt` and writes `solve.py`.
   - `go N` verifies, submits sequentially, and on a pass prints level N+1's statement (no separate fetch).
4. **After each level:** commit the solutions.

## Training status
| Run | Game | Mode | Levels passed | Notes |
|---|---|---|---|---|
| lawnmower | ccc-2024.04-classic-lawn-mower | exploration | **1–7 (all)** | L4 ~4 min, L5 40 s, L6 1.5 min, L7 24 min. L7 (Hamiltonian cycle with several trees) needed an exact solver with restarts, now `lib.paths.ham_cycle` |
| speedtest | ccc-2024.10-classic-desks | exploration | 1–3 | Used to benchmark the new `go` loop |

Speed details and the contest-day runbook are in [workflow-speed.md](workflow-speed.md).

## Ideas to build next
- **Timed rehearsal:** a full Challenge-mode run (4 h) on Room Planner or Spaceship.
- **Penalty check:** in Challenge mode, see whether a wrong submit adds to `gameScore.timeMs`.
- **Parallelism:** for a team of 2–3, each person runs their own Claude session on a different level or approach. Any member can submit.
