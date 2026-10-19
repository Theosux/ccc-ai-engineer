# Contest-day runbook: 42nd CLASSIC CCC, Fri 23 Oct 2026

**Start:** 13:00 UTC = **16:00 Cluj** (EEST). Duration 240 min, so it **ends 20:00 Cluj**.

**Team Krateo (3)** is on-site at CREIC Cluj-Napoca, venue 153.

**Only Teo's laptop runs the tooling.** Claude drives everything and Teo's laptop does all submits. The teammates read statements, hunt edge cases, and sanity-check outputs and visualizers.

Ignore the separate DATA/AI registration (team "The Posers"). golive only watches CLASSIC.

## Timeline (Cluj time)
| When | Who | Action |
|---|---|---|
| Thu evening | Teo | Charge the laptop. `git pull`. Run `python arena/golive.py --preflight`: everything must be OK. Phone hotspot ready. |
| **10:45** | Claude | `python arena/golive.py --observe school --from 07:45Z --minutes 15`, run in the **background**. It records the real #school go-live at 08:00 UTC (11:00 Cluj) as a read-only dress rehearsal. |
| **11:15** | Claude | Read `arena/runs/observe/42nd-school-ccc-5871.jsonl` and the timeline it printed. Compare the real sequence (status values, when `gameBaseUrl`/`gameSlug` appear, SSE events) against our assumptions. If they differ, adjust the detectors in `arena/golive.py` and rerun the fixture tests. |
| 15:00 (T-60) | Teo | Arrive at the venue, connect to Wi-Fi, `git pull`. `python arena/golive.py --preflight`. |
| 15:30 (T-30) | Teo | Open Claude Code in the repo, then: *"We are working on ccc check claude.md for context"*, then *"contest is about to start"*. |
| **15:45 (T-15)** | Claude | Start **`python arena/golive.py --browser`** with `run_in_background`. It runs the preflight, then watches with D1–D6 and keeps the session warm. The Edge window is the D6 witness, so leave it open. Teo can also watch the contest page in Opera GX. |
| 16:00 (T0) | auto | The first detector fires, then golive registers run `contest`, beeps, shows a toast, writes `LIVE.txt`, prints the **level 1 statement and example**, and exits. Claude starts solving immediately. |
| During | Claude | The `ccc-solve` loop: write `solve.py`, then `go N`. PASSED prints level N+1. Commit in the background after each level. |
| Stuck > 10 min | Claude + team | Follow `docs/knowledge/solving-playbook.md` §6. Reformulate instead of tuning. Teammates re-read the statement or PDF images for missed rules. |
| 19:30 (T-30) | all | Endgame (playbook §7): submit anything that passes `check()`. The ranking is level reached, then time. |
| 20:00 | | End. `git add -A && git commit && git push`, then write a progress-log entry. |

## Go-live detectors (`arena/golive.py`)
| # | Signal | Notes |
|---|---|---|
| D1 | `GET /api/contests/42nd-classic-ccc-5872`: `status` ∈ {RUNNING, STATS_FROZEN}, or start time passed with a game assigned | Adaptive polling: 240 s, then 15 s from T-15 min, then **1 s from T-90 s** |
| D2 | SSE `/api/contests/status/stream` | Any event triggers an immediate D1 check |
| D3 | `GET /api/contests/my-registrations`: the CLASSIC entry's status | 30 s, then 5 s near start |
| D4 | Once a game URL is known: `GET <game>/api/contestant/level/1/files` = 200 | **The game token is issued days before the start, so a token alone means nothing.** |
| D6 | `--browser`: an Edge window on `/contests/<slug>/game` logs every `/api` call and the game iframe URL | Gives the real `gameBaseUrl` even if the API shape differs |

Everything is logged raw, with tokens redacted, to `arena/runs/contest/golive-log.jsonl`.

## Fallback ladder
| Problem | Do this |
|---|---|
| golive reports login failures | `python arena/ccc.py login --http` (credentials.env), else `python arena/ccc.py login` (Edge window). Then rerun golive. |
| LIVE but "not ready yet" for over 2 min | Rerun with `--browser` if it wasn't used. Open the contest in Opera GX: is there a check-in, terms or start button? Click it, then rerun golive. |
| Game token refused (403) | Same as above: the UI probably needs an acceptance step. Make sure the team registration shows CLASSIC in `--preflight`. |
| Level zip download fails | In Opera GX, download the level zip from the game page. Then `python arena/ccc.py fetch N --zip "C:\Users\Teo\Downloads\<file>.zip"`, which builds the same `levelN/` folder. |
| Submit API fails | `python arena/ccc.py run N`, then drag and drop `arena/runs/contest/levelN/out/*` onto the platform's Solutions panel. File names already match the platform's rule ("last number picks the case"). |
| Venue Wi-Fi dies | Phone hotspot. Nothing needs reconfiguring. |
| Laptop dies | A teammate's laptop: clone the repo, `pip install requests playwright pypdf pypdfium2`, `python arena/ccc.py login`, `contest`, `fetch N`. Solvers are in git if they were committed after each level. |

## Rules of the road
- **Submit sequentially from one place.** The server lost concurrent updates in testing (5 parallel CORRECT, only 2 recorded). Teo says simultaneous submits by different teammates are fine, but we keep one submitter anyway.
- **Wrong submits:** a wrong submit did **not** add penalty time to `passedAt` in Challenge mode (tested 2026-10-19). Still, use `check()` and never submit unverified output.
- **Visualizers:** `levelN/sandbox.html` or `files/sandbox-level-N.html` is the official visualizer. Its JavaScript contains the **exact simulation and collision rules** (Spaceship L5), so read it when the semantics are unclear.
- **Images:** when the statement text is only bullets, the rules are images. `fetch` now auto-renders them and prints which PNGs to Read.

## Optional: teammate second-opinion session (not the primary strategy)
Use it only when a level has been stuck for more than about 10 minutes, typically the last 1–2 levels. Teo's laptop stays the **only submitter**.
1. **Setup (once, before the contest):** on the teammate's laptop, `git clone` the repo, then `pip install requests playwright pypdf pypdfium2 ortools networkx scipy`. Install Claude Code and log in with the teammate's own account.
2. **When a level is stuck:** Teo's session runs `git add arena/runs/contest/levelN && git commit -m wip && git push`. The teammate runs `git pull`. The level folder then has the statement, the inputs and our current `solve.py`.
3. The teammate opens Claude Code in the repo and asks: *"We are working on ccc check claude.md for context. Level N of run contest is stuck. Our approach was X. Solve it with a DIFFERENT method. Use only `CCC_RUN=contest python arena/ccc.py run N` and `probe N`, never `go` or `submit`."* `run` and `probe` work offline from the local files; only `go` and `submit` touch the server.
4. **Handover:** the teammate copies the solver to `arena/runs/contest/levelN/solve_alt.py` and pushes a branch: `git checkout -b alt-N && git add ... && git commit && git push -u origin alt-N`. Teo's session runs `git fetch && git checkout origin/alt-N -- arena/runs/contest/levelN/solve_alt.py`, then `python arena/ccc.py go N --solver solve_alt.py`.
5. **Cost:** this uses the teammate's own Claude usage. Its value is a genuinely different approach (for example CP-SAT or min-cut instead of a search) while the main session keeps trying its own.
