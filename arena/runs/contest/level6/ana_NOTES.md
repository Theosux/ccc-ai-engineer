# ana agent notes (level 6 analysis)

## Formula hunt
- Sum of cnt*(min over the 3 axes of the lines spanned) = 15596 (medium 8122, large 4825, enormous 2649), and adding
  centre-line travel gives 15655. Nothing matches 15642 exactly (ana_f.py / ana_f2.py).
- One line per tick is IMPOSSIBLE on noisy patterns. A pair writes count 2 on the whole line, and each of the other
  4 emitters crosses it at exactly one cell, so at most 4 skirt holes can be punched per line-tick (proof sketch).
  Holes per line on the best axis: enormous 126/140 patterns have 5+ holes. On patterns with 4 holes or fewer,
  best/ already matches or beats cnt*lines, and medium best/ beats the formula overall (ana_pot.py). So the 15596
  match is almost certainly a coincidence, and the real gap is the noisy large/enormous patterns.

## Tools (all verify with solve.simulate; run from level6/ with PyPy)
- ana_line.py / ana_line2.py: line sweep. A pair writes a line per tick, back and forth one copy per sweep,
  the 4 other emitters punch holes; beam over the 256 extras combos with an exact local validity check.
  ana_line2 adds a 5-line lookahead heuristic.
- ana_line3.py: the same sweep with exact per-axis reachability sets, then a joint beam to check junk.
- ana_two.py: a two-pair sweep (2 lines per tick + 2 singles). It fails in practice because the crossing of the two
  pair lines lands on pattern cells (blobs fill the board).
- ana_six.py: 6-singles lattice beam (experiment; got stuck on #64).
- Runner: `pypy3 ana_run.py <fid> <k> <K> <W> <maxwait> <tag> [module]` -> cand/ana_parts/<tag>_<fid>_<k>.jsonl
  (only programs shorter than best/ at the time are stored)
- Merge: `python ana_merge.py <fid> line` -> cand/ana_line_<fid>.txt = best/ + all ana_parts improvements, verified.

## Results (gains vs best/ at merge time)
- medium: 6648 -> 6582, large: 6664 -> 6604, enormous: about -28 (already absorbed into best/).
