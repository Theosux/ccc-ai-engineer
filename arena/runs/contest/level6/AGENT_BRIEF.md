# Level 6 optimization brief (CCC 2026-10 Classic "Nanofabricator", LIVE contest, ends 20:00 Cluj)

We have solved all 6 levels. Ranking now = total score of level 6 (lower is better) = SUM of program line
counts over 3 scored files: 2-medium, 3-large, 4-enormous. Noop lines ("- - - - - -") DO count.

## Leaderboard (16:45)
Top: 15531, 15724, 15874 ... many teams at exactly 16614. **Us: ~37k** (medium 7394, large 14685, enormous 16072).
Sum over all patterns of (rows spanned by pattern x count) = 18182 > 16614, so the top teams create MORE than
one row per tick on average. Our current methods are below; something fundamentally better exists.

## Exact rules (from the official visualizer JS, files/sandbox-level-6.html, fully verified by our simulator)
- Hex board radius r (interior radius r-1); char grid with 2r+1 rows, 4r+1 cols. Border ring of 6r cells.
- 6 emitters; emitter e fires in a fixed direction: 1=E(0,+2) 2=SE(+1,+1) 3=SW(+1,-1) 4=W(0,-2) 5=NW(-1,-1) 6=NE(-1,+1)
  (row,col deltas in the char grid). They ride on the border ring; start at corners: ring index (e-1)*r
  (ring index 0 = left corner (r,0), going clockwise). F = +1 clockwise, B = -1, T = toggle active, - = noop.
- Each tick: one instruction line (one action per emitter, simultaneously), then for each interior cell the
  number of ACTIVE rays covering it: ==2 -> matter M, >=3 -> empty O, <=1 -> unchanged. A ray covers every
  interior cell from the emitter in its direction to the edge (full chord, or nothing if pointing outward).
- Then pattern check (fixed position): all pattern M cells are M and no "skirting" cell (non-pattern cell adjacent
  to a pattern cell) is M -> accepted: pattern cells removed, count+1. At most once per tick.
- Cells not pattern and not skirting are "don't care" (junk there is fine forever).
- Program for a pattern must reach exactly `count` acceptances.

## Code (arena/runs/contest/level6/)
- solve.py: parse(), Geo(r) (ring, rays, interior), pattern_cells(), simulate(geo,pcells,prog)->acceptances,
  check(), baseline planner. Read it first.
- sweep.py: row-write planner (emitters 1&4 on the same row = full row of count 2; extras 2,3,5,6 cross it at
  skirting cells -> count 3 holes; erase/create ops; beam over rows; tries 6 rotations).
- tbeam.py: tick-level beam search over all 4096 action combos with bitmask simulation (best for medium).
- static.py: one-tick static configurations. cyc.py: cycle compression. merge.py: per-pattern best-of merge.
- best/out_level-6_<fid>.txt = current best submitted outputs (READ ONLY for you).
- Python: `python` (CPython) or PyPy at arena/.tools/pypy/pypy3.exe (much faster; use it for searches).

## Rules for helper agents
- NEVER submit, never run `ccc.py go/submit`, never edit best/, out/, solve.py, sweep.py, tbeam.py.
- Write your own new files named `<agentname>_*.py` in level6/, and candidate outputs to
  `cand/<agentname>_<anything>_<fid>.txt` in the full output format (programs separated by one blank line,
  one program per pattern in input order). Each program must be verified with solve.simulate == count.
  Partial improvement is fine: copy the best/ program for patterns you did not improve.
- Max 5 worker processes at a time (shared 16-core laptop).
- Report: per file total of your candidate vs best/, and the idea used.
