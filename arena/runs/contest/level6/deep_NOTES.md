# deep agent notes (level 6), started 17:20

## Trap verdicts (Rares, origin/rares-traps: 813b460, 64cee85, f5268fa, 1449d94)
Checked against solve.simulate and files/sandbox-level-6.html (applyEmitterStep / testPattern / acceptAndDeletePattern).
- Exact count: our check() needs acc == cnt. The JS only flags acc < cnt. Not a trap for us: stopping at the cnt-th acceptance is always shortest.
- Score = lines, noop lines count: known (tested earlier).
- Persistence (count<=1 keeps the cell, ==2 -> M, >=3 -> O), skirt rule, removal of pattern cells on acceptance, at most one acceptance per tick, move/toggle before firing, check at end of tick: all REAL and all already in simulate (it matches the JS line by line).
- Ring of 6r cells, start corners (e-1)*r: real, handled.
- "O markers != skirt": TRUE but harmless. O cells not adjacent to an M cell are don't-care. The JS computes skirt from M neighbours (testPattern), and so do we.
- "Full-height patterns have no junk rows": true as a statement, but it only matters for row-sweep planners. Don't-care cells still exist outside P|S.
- ">4 skirt cells per row (up to 16 in enormous)": REAL. It is the key limit of one-line-per-tick sweeps (4 singles = at most 4 holes per line).
- "Mirror variants waste 50% of best_sweep2": FALSE for our sweep.py. It has NO mirror variants (6 rotations x 4 thresholds only), and relabel() is correct for rotations.
- Rares' rewrite 1449d94 (copied to deep_rsweep.py): BROKEN. (a) SyntaxError: `global CREATE_MAX` after an assignment, in dead code after `return`, so the module does not even import. (b) The mirror relabel maps 1<->4, 2<->6, 3<->5 without swapping F/B. The x-mirror (y, 4r-x) needs 1<->4, 2<->3, 5<->6 with F<->B. (c) The refinement calls plan_pattern_beam on the UNrotated pcells, then relabels it with k. Verdict: do not use. The sweep family is not competitive with best/ anyway.
- No algorithm ideas in Rares' doc beyond "write >1 row per tick".

## Idea audit (measured)
- Board on P|S is ALWAYS clean right after an acceptance, so copies decouple. The cost of copy j+1 depends only on the emitter state.
- Steady-state per-copy (best/ at 17:25): medium r3 2.16, r4 2.97, r5 4.12. Large r6 7.6, r7 8.6, r8 14.2. Enormous: mostly cnt 1-2, first copy dominates.
- Period-1 (static config, 1 line/copy) feasibility, exhaustive in line space (<=2 lines per axis): only 9/210 medium patterns qualify, and best/ already has 1/copy on all 9 (deep_static.py).
- Temporary skirt dirt with a penalty in the tick beam (deep_tb.py, deep_cmp.py): WORSE on 8/8 test patterns (e.g. #0: 44 vs 92/65/77). Greedy fill then can't clean. Dead end in the beam form.
- Exact CP-SAT model of the machine (deep_sat.py, OR-tools 9.15 in CPython):
  * prefix+cycle model (prefix T0 lines to the 1st acceptance, then a k-line cycle back to the same emitter state, repeated): medium #0 44->43 (kmin=3), #2 4->3 (cnt 1, proven optimal). #40: kmin=3, no gain (43 is optimal for that horizon).
  * full exact model with true variable acceptance + hint from best/: correct, but it does not improve long programs within 60 s.
- CP-SAT window LNS (deep_lns.py): replace a w-line window by fewer lines that reach the same emitter state, the same number of
  acceptances, and the same board on every P|S cell that is not overwritten before the next acceptance. It post-processes ANY
  program, including other agents' best/. See results below.

## Commands
- `python deep_lns.py <fid> <tag> <nproc> <W> <tl> [order=gap] [stop=<epoch>]` -> cand/deep_<tag>_<fid>.txt (merged on the latest best/)
- `python deep_sat.py 2-medium i,j,..` (prefix+cycle exact)

## Results at wrap-up (17:55)
- deep_lns.py on medium #132 (W=8, tl=4 s, 2 workers): 76 -> 65 lines in 35 s, verified (6/6 acceptances). Every 8-line
  window it tried could be shortened by 1. **This is the measured best idea**: a CP-SAT post-processor that works on any agent's best/.
- Large #143 (W=10, tl=8 s): no result within 280 s. Infeasible windows cost the full time limit. For large/enormous, use a
  smaller W (6-8), tl 2-4 s, and a per-pattern deadline.
- No cand/deep_* files written (stopped before a full run). To resume:
  `python deep_lns.py 2-medium lns 4 8 4 order=gap` (then 3-large / 4-enormous with W=6, tl=3, stop=<epoch>).
