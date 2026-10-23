# Contest handoff: 42nd CLASSIC, Nanofabricator (written ~17:20 Cluj, 23 Oct 2026)

## State
- Levels 1-6 all PASSED (L1-L5 by ~16:09, L6 baseline ~16:24). Run name `contest`, CLI `python arena/ccc.py`.
- Level 6 is an optimization level: rank = level, then the total line count of level 6 (lower is better) = the sum over
  2-medium + 3-large + 4-enormous. **The server keeps the LATEST submission, not the best**, so only ever submit merged best files.
- **Last submitted (final before reset): medium 6708, large 7473, enormous 9187 = 23368.**
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

## Resume next (biggest expected gains, from the agents' final reports)
1. Opus beam on enormous, which was never run (expected -20..30%): `cd arena/runs/contest/level6 && ../../../.tools/pypy/pypy3.exe opt_run.py 4-enormous b4 25 1 opt_beam`
2. Finish the large beam (stopped at 120/190): `../../../.tools/pypy/pypy3.exe opt_run.py 3-large b4 25 1 opt_beam`
3. Re-merge with `pypy3 opt_final.py <fid>` or `python merge.py <fid> best/... cand/*_<fid>.txt`, then submit.
4. Medium: the W=32 pass of med_tb2.py (masked-board tbeam) over all 210 patterns (it stopped at 31). See med_NOTES.md.
5. Untested: allow temporary skirting M with a penalty (opt_macro2.py / opt_beam2.py).
All agents are stopped and no background jobs are running.
