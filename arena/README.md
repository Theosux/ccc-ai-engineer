# Arena: training + contest working folder

Run everything from the repo root: `python arena/ccc.py <cmd>`. Run selection: the active run, or `CCC_RUN=<name>` per command.

## The loop (2 tool calls per level)
1. `fetch N`: downloads the level and **prints the cleaned statement + example input/expected output**. `levelN/solve.py` starts as a copy of level N-1's solver (or a stub).
2. Edit `levelN/solve.py`: stdin → stdout. Optionally add `check(data, out) -> bool | (bool, msg)` for levels with many valid answers.
3. `go N`:
   - runs all inputs in parallel and verifies the example (or `check()` on every file);
   - submits smallest file first, **sequentially**, skips files already passed, and stops at the first WRONG;
   - if the level passed, **fetches N+1 and prints its statement**. So `go N` → write solver → `go N+1` → ...

Diagrams: `fetch N --png` renders the statement pages to `levelN/pages/p*.png` (local zip, ~1 s). Read them.

## Commands
| Command | What it does |
|---|---|
| `wait [contest] [--name contest]` | Contest day. Polls until the game is live (keeps the session warm), registers the run, prints level 1. Run it in the background from T-15 min. |
| `contest [contest] [--name contest]` | Registers the contest run now (fails clearly if not started). Default contest is `42nd-classic-ccc-5872`. |
| `train <gameSlug> [--mode exploration\|challenge] [--name X]` | Starts a practice run. Becomes active unless `CCC_RUN` is set. |
| `fetch N [--png] [--scale 0.75]` | Downloads, unzips, writes `map.json` and `statement.txt`, and prints the statement + example. |
| `go N [--force] [--no-next] [--solver CMD] [--timeout S]` | Run + verify + submit + auto-fetch next. `--force` submits despite an example/check mismatch. |
| `run N [--only ID] [--solver CMD]` | Outputs only (into `levelN/out/`). |
| `submit N [--only ID ...] [--include-example]` | Submits (sequentially). With `--only` it does not stop on WRONG. |
| `info [--raw]` | Unlocked level, per-level todo files, cooldowns. |
| `login` / `login --http` | Browser login (Edge), or HTTP login using `.auth/credentials.env` (`CCC_USER=`, `CCC_PASS=`). |
| `games`, `use NAME`, `api GET\|POST <path> [--game]` | Utilities. `api` survives Git Bash path mangling. |

`--solver "pypy3 solve.py"` or `--solver "node solve.js"` runs any command (cwd = levelN). PyPy is not installed (as of 2026-10-09).

## Layout
```
arena/.auth/        GITIGNORED: cookies.json, state.json (runs + game tokens), edge-profile/, credentials.env (optional)
arena/runs/<run>/   contest.json, game-info.json (level metadata), contestant-info.json
  level<N>/         files/ (unzipped: level-N.pdf, in_level-N_<id>.txt, out_level-N_0-example.txt)
                    statement.txt, map.json, solve.py, out/, submissions.jsonl, sandbox.html?, pages/?
```

## Rules learned the hard way
- **Never submit in parallel.** The game engine loses concurrent updates: 5 parallel CORRECT verdicts, only 2 recorded. `submit`/`go` are sequential and re-submit any file that was CORRECT but not recorded. Teammates: do not submit the same level at the same moment.
- Large outputs are slow to grade (~16 s/MB server side). The 1.2 MB file took 20 s. Give `go` a long tool timeout.
- An expired session (HTTP 401) prints `SESSION EXPIRED`. With `credentials.env` present, the CLI re-logs in automatically.
