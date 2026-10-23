# Contest handoff: 42nd CLASSIC, Nanofabricator (written ~17:20 Cluj, 23 Oct 2026)

## State
- Levels 1-6 all PASSED (L1-L5 by ~16:09, L6 baseline ~16:24). Run name `contest`, CLI `python arena/ccc.py`.
- Level 6 is an optimization level: rank = level, then the total line count of level 6 (lower is better) = the sum over
  2-medium + 3-large + 4-enormous. **The server keeps the LATEST submission, not the best**, so only ever submit merged best files.
- Last submitted: medium 6763, large 8063, enormous 9187 (total about 24.0k). Leaderboard top at 16:45 was 15531 (many at 16614).
  Leaderboard: `game_req('GET','/api/game-engine/leaderboard?scope=WORLD',ctx)` (see the snippet in this session: `import ccc; ctx=ccc.active_run()`).
- Noop lines DO count (tested).

## Files (arena/runs/contest/level6/)
- `best/out_level-6_<fid>.txt`: current best = what was last submitted. **Source of truth.**
- `cand/*.txt`: all candidate outputs (tbeam_*, med_*, opt_*). `python merge.py <fid> best/out_level-6_<fid>.txt cand/*_<fid>.txt`
  rebuilds best/ per pattern (verifies each program with the exact simulator).
- Submit: `cp best/out_level-6_<fid>.txt out/` then `python arena/ccc.py submit 6 --only <fid>` (from the repo root).
- `AGENT_BRIEF.md`: exact rules plus the helper-agent rules. `opt_NOTES.md` / `med_NOTES.md`: the helper agents' methods (if written).
- `solve.py`: parser, Geo, exact simulator `simulate()`, `check()`, baseline, and run_cases over sweep planners (slow: ~20 min).
- `sweep.py`: row-write sweep (1&4 on the same row = full row; extras = holes; erase/create ops; beam; 6 rotations; variant search).
- `tbeam.py` + `run_tbeam.py <fid> <W> <procs>`: tick-level beam over 4096 actions, bitmask sim. Best on medium (W=16); large W=4 helped.
- `static.py` (one-tick static config) and `cyc.py` (cycle compression): tiny gains only.
- `opt_*.py` (Opus agent) and `med_*.py` (Sonnet agent): see their NOTES.

## Ideas not finished
- Larger tbeam W on large/enormous (W=10 large and W=3 enormous were stopped before finishing).
- Enormous/large are mazes: row writes allow only 4 holes per tick; creation by crossings plus beam looks better.
