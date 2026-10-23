# opt agent notes (level 6, large/enormous)

## Key idea
Planner over TARGET configurations (pos + active for all 6 emitters), not single ticks.
- opt_macro.py: from the current state, coordinate ascent per emitter (any ring pos active / stay inactive / park on
  an outward position) maximizing (new pattern cells - destroyed - 3*skirting violations) / travel ticks.
  Seeds: pair-on-a-line through a missing cell, 2-ray crossing at a missing cell, current config. Travel to the
  target is simulated exactly (3 alignments: end-aligned, start-early, safe = all off, move, all on).
  Never lets a skirting cell become M.
- opt_beam.py (better): time-bucketed beam (W states per tick count). Each state expands to the top one-tick moves
  (all 4096 combos) plus top macro moves; best 3 expansions by gain/ticks go to bucket t+len.
- opt_pal.py / opt_palrun.py: palindrome/repeat compression of the core after an acceptance (tiny gain, ~20 lines).
- opt_macro2.py / opt_beam2.py: UNTESTED variant allowing temporary skirting dirt with penalty LAM (rules only need
  skirting clean at acceptance time). `pypy3 opt_beam2.py 4-enormous 64,122 4 1.5` to test.

## Commands (from level6/, PyPy, 5 procs each)
- `pypy3 opt_run.py 3-large b4 25 1 opt_beam`  -> cand/opt_b4_3-large.txt   (~5 min large; was stopped at 120/190
  patterns, sorted by best/ length descending, so the remaining 70 smallest patterns were never run with the beam)
- `pypy3 opt_run.py 4-enormous b4 25 1 opt_beam` -> cand/opt_b4_4-enormous.txt (never run; ~20 min estimated.
  Sample results: #64 286->196, #122 218->153 vs the macro planner)
- `pypy3 opt_run.py <fid> m1 40 1` (opt_macro greedy, fast: ~2 min per file)
- `pypy3 opt_final.py <fid>` -> cand/opt_final_<fid>.txt = per-pattern min of best/ + every cand/opt_*, verified.
- opt_run.py also folds in earlier cand/opt_* files, so later runs only add improvements.
