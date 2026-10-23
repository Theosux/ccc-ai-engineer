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

## main agent (17:10-17:55)
- main_run.py = opt_run.py + folds ALL cand/*_<fid>.txt, procs arg (argv6), skip arg (argv7), MAIN_KW env json passed to plan()
  (e.g. MAIN_KW='{"W":24}'), writes cand/main_<var>_<fid>.txt after every pattern, resume via main_done_<var>_<fid>.txt.
- main_final.py = per-pattern min of best/ + all cand/* (verified) -> cand/main_final_<fid>.txt.
- Results: opt_beam W4 enormous 9187->7160 (3 min); W12 enormous ->6417 (10 min), large W12 7432->6664 (6 min),
  medium opt_beam W8 6708->6616 (1 min). Beam width is the lever: W24 started (enormous 20/140 gave -137) but was stopped.
- med_tb2 W=32 over the 26 largest medium patterns: 0 improvements -> not worth it.
- Next: MAIN_KW='{"W":24}' (or 48) pypy3 main_run.py <fid> b24 25 3 opt_beam 5  (resumes from main_done_b24_<fid>.txt).
