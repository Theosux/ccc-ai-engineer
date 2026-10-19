# Solving playbook: one level under time pressure

Ranking = levels done, then time. **Correct-first, fast-to-write.** Runtime matters only when a file times out.

## 0. Fetch (≤1 min)
`python arena/ccc.py fetch N`. Read `statement.txt`, then the **example in/out** (it's the real spec).
If a statement line looks like gibberish (`' L D J R Q D O V`), that's font-shifted text: read the PDF.

## 1. Diff vs previous level (≤2 min)
- "Input identical to previous level": copy the previous `solve.py` and change only the logic.
- Which guarantee was removed? ("tree can now be anywhere", "x no longer divisible by 3", "multiple trees").
  That removal IS the level. If last level's code was general, it may pass unchanged. **Run it first.**
- New output type? `VALID/INVALID` → validator. "find a/any …, multiple solutions" → construction + `check()`.

## 2. Write the solver
- Start from `from lib import *` (header in `ccc-patterns.md`). Parse with `Reader`. Put per-case logic in a function.
- Confirm conventions against the example: W vs H order, x/y vs row/col, 0/1-based, y-down, output separators.
- **Constructive level:** first copy the previous level's validator into `check(data, out)` in solve.py.
  `go` then accepts output that differs from the example. Write one construction for one orientation and get
  the rest via `try_symmetries`. Add a generic search fallback (`ham_path`, `ham_cycle`, BFS) for leftover cases.
- **Optimization level ("shortest", "max", "≤ threshold"):** get *any* valid answer first (greedy), check the
  threshold, then improve: exact BFS/Dijkstra if the state space is small; otherwise `anneal`/`hill_climb`,
  min-cost flow (`networkx.min_cost_flow`), assignment (`scipy.optimize.linear_sum_assignment`), ILP (`scipy.optimize.milp`).

## 3. Verify locally, then submit
- `python arena/lib/check.py arena/runs/<run>/levelN` runs solve+check on every input with timings.
- `python arena/ccc.py go N`: example must match OR `check()` must pass on all files. Read per-case verdicts on failure.
- WRONG on one file → look at failing case lines → reproduce on that case only (`Reader` + slice) → fix.

## 4. When it's slow
1. Profile: `python arena/lib/check.py arena/runs/<run>/levelN 3-medium --profile` (top 15 functions by cumtime).
2. Usually one hot function: an O(n) check inside a loop. Make it incremental or trigger it only when needed (example: the 8-ring split test cut `ham_path` 100×).
3. **Search that sometimes never finishes = heavy tail.** Use time-sliced restarts with random tie-breaks and keep one deterministic run in the portfolio (`ham_cycle` does this).
4. Pure-Python CPU loops (simulation, brute force): PyPy is about 10–60× faster. It doesn't help when the time is spent waiting on wall-clock restart slices.
5. Still slow? Sanity-check the input size. Brute force with pruning is usually enough for CCC (≤ ~1000 cells, ≤ 150 KB files).

## 5. Time budget heuristics (from lawnmower practice)
- L1–3: 1–3 min each. Reused/generalized level: under 1 min. Construction level: 5–10 min.
- Measured (Room Planner L4–7, RPS L1–7): 0.3–2 min per level once lib had the right tool; 6 min when it didn't.
- Hard search (Hamiltonian, packing): 20–30 min. If a pure search fails >10% of cases after 10 min,
  change the method (exact constraint propagation, a different construction), not the parameters.
- Never wait silently on a 10-min run: run small files first (`check.py <dir> 1-small`).

## 6. When stuck > 10 min (protocol)
1. **Stop tuning.** Write the smallest failing case to a file. Is it really solvable? (brute force it, or the
   statement guarantees it). Hand-solve it once: the hand solution shows the structure the heuristic lacks.
2. **Name the failure type:** off-by-one vs bound (structural: pinwheel/parity) · wrong split amounts (greedy
   commits too early) · timeout (heavy tail) · misread rule (re-read PDF images + example).
3. **Change the formulation, not the parameters:** halves → rounds/layers; greedy → DP over counts/sets;
   DFS → exact propagation; time-sliced restarts. RPS L5: 4 min lost tuning fill orders; the round-chain
   reformulation solved all cases first try.
4. Only a few cases fail? Chain methods: fast heuristic → exact/slow fallback only for the misses
   (`pack_rects`, `build_bracket` both do this). Level passes only when every file is CORRECT.
5. Time-box: 20 more min, then ask the teammate to attack it from scratch with a different method.

## 7. Endgame: the last levels
Real contestants rarely finish the last 1–2 levels (see `past-games.md`), so they decide the ranking.
- **Threshold/optimization:** any answer under the threshold passes. Valid baseline in 5 min → measure the gap per
  file → improve only failing files. Order: exact small-case DP → greedy + local repair → anneal/restarts.
- **Huge inputs:** compute input stats first (max N, sizes). O(N²) Python dies at ~10^4; use PyPy (`# ccc: pypy`),
  numpy, or precompute tables shared across cases (memo across cases: Room Planner DP built once).
- **Brute force fails:** find invariants (parity, bounds like ⌊area/piece⌋, counts), reduce to counts/types,
  solve the reduced problem exactly, then expand. Lower bounds also tell you when greedy is already optimal.
- **Search:** best-first/A* with an admissible bound (Spaceship L7: h = max(minTimeX, minTimeY)), beam search for
  "good enough", exact propagation + random restarts for feasibility (heavy tail).
- **Adversarial / "no matter what":** ∃∀ DP over sets of outcomes; never sample the adversary for correctness
  (sample only as an extra check).
- **Validate everything locally** with the previous level's checker; a WRONG on the last level costs penalty time.

## Checklist before every submit
- [ ] example OK or `check()` OK on ALL files  - [ ] one line per case, trailing newline
- [ ] no debug prints on stdout (use stderr)       - [ ] no "FAIL" placeholders in output
