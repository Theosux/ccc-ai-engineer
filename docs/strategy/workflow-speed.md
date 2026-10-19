# Workflow speed: measurements, optimizations, contest-day runbook

Measured on 2026-10-09 in practice run `speedtest` (Room Planner / desks, exploration mode). Levels 1–3 were solved with the new flow. Windows, Python 3.14. Network latency to `files.codingcontest.org` varied a lot during the session.

## Where the time goes (per step)
| Step | Time | Notes |
|---|---|---|
| Python + requests start-up | 0.25 s | per CLI call |
| `POST /api/game-token` | 0.44 s | only on register / 401 |
| `GET contestant-info` | 0.40–0.50 s | |
| `GET level/N/files` (returns pre-signed URL) | 0.44–0.72 s | |
| Blob download of `level-N.zip` (~1 MB, mostly PDF) | **0.7–3.7 s, once 33 s** | latency-bound: a HEAD alone takes ~1 s; parallel Range requests did not help |
| PDF → text | 0.09 s (pypdfium2) / 0.16 s (pypdf) | |
| PDF → PNG | 1.5 s for 4 pages at 1.5× | on demand only (`--png`, 0.75×) |
| `GET level/N/sandbox` probe | 0.64 s | now skipped when game-info says `sandbox:false` |
| Submit small or medium file (≤150 KB) | 0.8–1.6 s | |
| Submit 1.2 MB file | **20.5 s** | server-side grading (~16 s/MB). Uplink measured at 2 MB in 3.6 s, so not our bandwidth |
| Solver run | 0.1–0.2 s per input | parallel across inputs now |

**The real bottleneck is not the CLI but Claude's turns.** Each tool call costs several seconds of model latency and some tokens. The old loop needed about 5 calls per level (fetch, Read statement, Read example in/out, go, fetch next). The new loop needs **2** (Write solve.py, `go N`).

## Before → after
| Action | Old CLI | New CLI |
|---|---|---|
| `fetch N` (back-to-back, same network) | median 7.9 s (7.0 / 7.9 / 11.1) | median 4.9 s (4.2 / 4.9 / 12.2), and the output **includes** the statement + example |
| Read statement + example | 1–3 extra tool calls | 0 (printed by fetch / go) |
| `go 1` (5 small files) | 4.3 s plus a separate `fetch 2` call | ~4 s, with the next level printed in the same call |
| `go` on a level with a wrong solver | submits all files; the large one alone takes ~20 s | **stops at the first WRONG** (smallest first): 2.9 s total |
| `go` after a partial pass | resubmits everything | skips passed files (0.8 s to "PASSED" when all were already passed) |
| Contest start → level 1 statement on screen | manual: `contest`, `fetch 1`, Read | `wait` (background): **8.8 s** from LIVE to printed statement (tested on a running training contest) |

## What was changed in `arena/ccc.py`
- **`go N` chains:** run (parallel) → verify → submit (sequential, verified) → if passed, `fetch N+1` and print it.
- **`fetch` prints** the cleaned `statement.txt` (boilerplate removed, `[pK]` page markers) plus the example input and expected output. `solve.py` starts as a copy of level N-1.
- **`check(data, out)` support:** constructive levels no longer need `--force`. `go` validates every output with the solver's own check.
- **Public `/game/game-info`** (cached per run) supplies the level count, input file ids, unscored ids, and the sandbox/optimization flags. That removes the contestant-info call and the sandbox probe from `fetch`.
- **Sequential, smallest-first submit** that stops on WRONG, with a verify + re-submit of any CORRECT-but-unrecorded file (see the race below).
- **Robustness:** keep-alive sessions; retry on network errors and 502/503/504; a stall timeout on the blob; the client's `?raw=true` fallback; a clear `SESSION EXPIRED` message; automatic HTTP re-login when `.auth/credentials.env` exists; `login --http`; UTF-8 stdout; Git Bash path-mangling fix in `api`; crash tracebacks shown once and without ANSI colours.
- **`wait`:** polls the public contest endpoint (every 240 s while far away, every 2 s in the last 90 s). Every 4 min it touches `/api/auth/current-user` to keep the server session warm. On RUNNING + `gameBaseUrl` it registers the run, gets the token and fetches level 1, retrying for up to 60 s while the game API warms up.
- Not built: `watch` mode (Claude drives the loop itself), a separate `new N` (fetch already copies), and PyPy (not installed; `--solver "pypy3 solve.py"` works if it is installed later).

## Platform findings that matter for speed
- **Concurrent submits lose updates (confirmed).** 5 parallel submits all returned CORRECT, but only 2 were recorded. Sequential submits accumulate correctly, and each response carries the cumulative `score`. This applies to **teammates too** (team Krateo has 2 members).
- The submit response contains the full `score` (`gameScore.level` = highest unlocked level, `state.levelN.passedAt`), so no extra `info` call is needed after submitting.
- Unlock rule in the client: `maxAccessibleLevel = score.gameScore.level`, and a level is accessible if untimed or `N <= maxAccessibleLevel`. The next level's zip can therefore be fetched right after the passing response. Verified in exploration mode only; challenge mode is not tested.
- The zip is a static, per-game blob (`files.codingcontest.org/game-files/<game>/level-N.zip`) behind a short-lived SAS URL.
- Case feedback fields: `caseState`, `caseMessage`, `startLineNumber`/`endLineNumberExcl`, `errorLineNumber`, `optimizationScore`. Optimization levels expose `passScore` and `scoreDirection` in game-info.

## Contest-day runbook (superseded: see [contest-day-runbook.md](contest-day-runbook.md), which uses `golive.py`)
| When | Action |
|---|---|
| T-60 min | Pull the repo. Run `python arena/ccc.py info` on a practice run to prove the login works. If SESSION EXPIRED, run `login` (browser), or `login --http` if `credentials.env` exists. |
| T-30 min | Open Claude Code in the repo with the `ccc-solve` skill. Agree with the teammate who submits which level (never both at once). |
| T-15 min | `python arena/ccc.py wait` **in the background**. It prints a countdown, keeps the session warm, and exits with the level 1 statement. |
| T+0 | When `wait` exits, read the printed statement and write `arena/runs/contest/level1/solve.py`, then `go 1`. If `wait` failed, run `contest`, then `fetch 1`. |
| Per level | Write `solve.py`, then `go N` (tool timeout 600000). PASSED prints N+1. Commit in the background. |
| Stuck > 20 min | Use `fetch N --png` for diagrams. Use `check()` to validate locally. Consider a teammate working on the same level from another angle (but only one submits). |
| Last 10 min | Keep submitting files that pass `check()`. Ranking is by level reached, then time (see `docs/contest/`). |

## Known risks
- **Network latency to the blob host** (seen 1–33 s). There is a stall timeout plus retry. Use a wired connection at the venue if possible.
- **Session expiry.** The server-side idle timeout is unknown, and the cookies are session cookies. The game token is an opaque UUID with an unknown TTL. Mitigations: `wait` keeps the session warm, the token refreshes automatically on 401/403, and HTTP re-login uses credentials (Teo must create `arena/.auth/credentials.env`).
- **Large-file grading time** (~20 s/MB). Tool timeouts must be long. Stop-on-WRONG avoids paying it for bad solvers.
- **New game format.** If the 2026 zip naming differs, fetch falls back to the "last number picks the case" rule, and game-info still lists the file ids. Check the `inputs:` line in the fetch output.
- **Challenge-mode unlock timing** is untested. If `fetch N+1` returns 403 right after passing, `go` retries for 20 s, then prints an error. Re-run `fetch N+1`.
- `wait` was only tested against an already-running training contest and the pre-start branch of the real contest. The real status flip (OPEN_REGISTRATION → RUNNING, `gameBaseUrl` set) happens live for the first time on contest day.

## Session 5 (2026-10-19): where the Spaceship rehearsal time went, and the fixes
Timestamps come from the session transcript. L1–L6 took 5.3 min, about 50 s per level, of which 15–25 s per turn was model think and write time. **L7 took 29.4 min, and about 20 min of that was waiting:**
| Window | What happened | Fix |
|---|---|---|
| 12:25–12:35 | 10 min blocked on a brute-force run with the 600 s default timeout, before looking at `sizes:` | `go`/`run` default to 180 s; skill rule "sizes → probe → full run" |
| 12:37–12:48 | the first A\* ran in the background while I did infra work; then a 5-case timing test burned its 300 s | `ccc.py probe N`: parallel sample (largest + random cases) under a 20 s budget, ETA plus a verdict, and flags heavy tails; rule "no side work during a level" |
| 12:51–12:54 | the final run took 3.3 min with a hand-written `multiprocessing.Pool` | `lib.runner.run_cases`: an automatic pool across cases, with progress and ETA streamed through `go` |
Measured on Spaceship L7 (500 cases, 20 MB): `probe` returned in **22 s** with an ETA of 135 s (lower bound, heavy tail flagged), and the full run via `run_cases` took **154 s**. So the forecast is accurate, and the rehearsal's 20 min of blind waiting shrinks to about 30 s of probing.

## Claude Code speed settings (researched 2026-10-19)
Sources: code.claude.com/docs/en/fast-mode.md, model-config.md, sub-agents.md, cli-reference.md, headless.md.
- **`/fast`** uses the same Opus model with faster output, **up to 2.5× faster**. It works on Opus 5.5, Opus 5 and Opus 4.8, **not Sonnet or Haiku**. It is billed at $8/$40 per MTok on Opus 5.5 and draws **only from usage credits** (extra usage), not from the subscription limits. Turn it on **at the start** of a session: enabling it mid-conversation charges the whole context uncached once. Settings key: `"fastMode": true`.
- **Effort:** `/effort low|medium|high|xhigh|max`, `--effort`, `CLAUDE_CODE_EFFORT_LEVEL`, or the settings key `effortLevel`. Lower effort is faster. Thinking cannot be fully disabled on the 5.5 models.
- **`/model <name>`** switches immediately mid-session. A subagent with its own `model:` keeps it. Switching away from Opus turns `/fast` off.
- **Custom agents** (`.claude/agents/*.md`) support `model`, `effort`, `tools`, `skills`, `permissionMode`, `maxTurns`, and more. Fast mode for subagents is not documented, so treat it as unverified.
- **Headless:** `claude -p --model <m> --effort <e> --output-format json --permission-mode acceptEdits --max-turns N`. The JSON has the cost but no wall time, so measure that with the shell.

## Model A/B: Sonnet 5.5 vs Opus 5.5 (2026-10-19)
Protocol: each model ran as a **cold** subagent (no session context; it loaded `ccc-solve` and `ccc-patterns` itself) with an identical prompt. Both played the same unseen offline game, one after the other, never in parallel. The judge was local: references plus the judge agent's validators. Times are fetch → pass from `timing.jsonl`. Runs: `arena/runs/{i21,sg}-{sonnet,opus}`. (The `sg-opus` folder was not kept: only `i21-sonnet`, `i21-opus` and `sg-sonnet` were restored to the repo, so the Opus Smart Grid row comes from its run log and report.)

| Game | Model | Per level (s) | Total | Wrong | Notes |
|---|---|---|---|---|---|
| interp2021 (4 levels, interpreter) | Sonnet | 10 / 8 / 13 / 19 | **50 s** | 0 | |
| interp2021 | Opus | 11 / 11 / 16 / 11 | **49 s** | 0 | |
| smartgrid (7 levels, scheduling + convex cost) | Sonnet | 7 / 9 / 6 / 16 / 18 / 72 / 134 | **263 s** | 0 | broke 2 rules: a heredoc patch, and ran `go` despite probe TOO SLOW (73 s run) |
| smartgrid | Opus | 6 / 7 / 7 / 31 / 58 / 83 / 57 | **249 s** | 0 | min-cost flow on L4; followed every rule |

**Result: a tie on speed and correctness on these games.** Wall time is dominated by tool round trips and solver runs, not by token generation, so Sonnet's faster output does not turn into faster levels. Opus was more disciplined (it followed the process rules) and chose stronger techniques. Hard levels decide the ranking (Spaceship L7, Islands L7), and there Opus's stronger reasoning matters more.

**Decision for 23 Oct: Opus 5.5 drives** (default effort). Optionally use `/fast` from the **start** of the session if Teo enables usage credits. That gives up to 2.5× faster output, which helps most on the long solver writes of hard levels. Sonnet stays a fallback if the Opus usage limit is hit.
