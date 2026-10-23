# opt2 agent notes (level 6, 18:50-19:45)

## Idea
Ran deep's CP-SAT window LNS (deep_lns.py, measured but never run at scale) over ALL files as a post-processor of best/.
opt2_lns.py = deep_lns.py + output cand/opt2_<tag>_<fid>.txt + per-pattern time cap (env OPT2_CAP seconds)
+ reverse window order (env OPT2_REV=1, so a second pass starts at the program end).
opt2_merge.py <fid> <globs...> -> cand/opt2_final_<fid>.txt = per-pattern min of best/ + globs, verified with simulate.

## Commands
- `OPT2_CAP=70 python opt2_lns.py 2-medium lns 3 8 4 order=gap stop=<epoch>`
- `OPT2_CAP=100 python opt2_lns.py 3-large lns 2 6 3 order=gap stop=<epoch>`
- `python opt2_merge.py <fid> "cand/opt2_*_<fid>.txt"`
