# CCC patterns: "level says X → do Y → use Z"

Lib import (first line of solve.py): `import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))` then `from lib import *`.
API details: `arena/lib/__init__.py` docstrings. Self-test: `python arena/lib/tests/test_lib.py`.

## Catalog
| Statement says… | Technique | arena/lib |
|---|---|---|
| "N, then N lines/records" | token reader | `Reader(data)`: `.int() .ints(k) .word() .grid(h)`; `out_lines(list)` |
| Lines contain spaces / free text | line reader | `Lines(data)`, `paragraphs(data)` for blank-line blocks |
| Coordinates like `4,2` or messy lines | regex ints | `ints_of(s)`, `pairs_of(s)` |
| Linear positions 1..R*C | index ↔ (row,col) | `idx_to_rc(p, cols)`, `rc_to_idx` |
| Lawn/map/room "as a paragraph of characters" | `grid = r.grid(h)` (h row tokens); `grid[y][x]` | `dims`, `find`, `cells(g,'X')` |
| Moves WASD / NESW / UDLR / "L R F" turns | vector maps, y DOWN (N = y-1) | `WASD NESW UDLR TURN_R TURN_L OPP walk(moves)` |
| "smallest rectangle it fits in" | bbox of visited cells (+1 each side) | `bbox(walk(m))` |
| "check if valid" / VALID-INVALID | write the validator, keep it for later levels | `covers_once`, `find_cover_start`, `valid_cover(g,m,cycle=)` |
| "find a path/arrangement, multiple solutions" | construct → validate with previous level's checker; `def check(data,out)` in solve.py | `try_symmetries(g, construct, check)` |
| Visit every cell once (Hamiltonian path) | boustrophedon/snake + local fix around obstacles; fallback search | `snake_rows/cols`, `ham_path`, `ham_path_exact(start,end)` |
| …and return to start (cycle) | parity: needs EVEN free-cell count; construction or exact | `ham_cycle(g)` (edge propagation + restarts) |
| Shortest path on grid, unit steps | BFS (multi-source: list of sources) | `grid_bfs(g, [src], passable)`, `path_to(par, end)` |
| State = (pos, dir/speed/time/keys) | BFS/Dijkstra over tuple states | `bfs(start, nbrs, goal)`, `dijkstra(start, nbrs, goal)` |
| Weighted / "minimum cost/time" | Dijkstra; A* with admissible h (Manhattan) | `dijkstra`, `astar(start, nbrs, h, is_goal)` |
| Regions / islands / connected parts | flood fill / DSU | `grid_components`, `DSU` |
| Dependencies / ordering | Kahn toposort (None = cycle) | `toposort(nodes, edges)` |
| "after 10^9 / 10^18 steps" | cycle detection, fast-forward | `state_at(s0, step, n, key)` |
| Collisions, segments, rectangles, "must not touch" | cross product, inclusive rect overlap (touch=True adds the 1-cell gap) | `geom.segments_intersect`, `geom.rects_overlap` |
| Fill a room with rectangles/desks, "given number is the max" | guillotine DP over (w,h) + exact pinwheel blocks + top-level pinwheel split | `pack_rects(W,H,[(a,b)],target=k)`, `render_rects`, `check_rects_grid` |
| …"must not touch (incl. diagonal)" | **inflate pieces and room by the gap**, then plain packing | `pack_rects(..., gap=1)` |
| …mixed sizes, "cover max cells" | weighted DP (value per piece) | `pack_rects(..., value=lambda w,h: w*h)` |
| "score ≥ threshold" / maximise | greedy baseline → hill climb / annealing until threshold | `anneal(sol, neighbor, cost, seconds)`, `hill_climb` |
| Assign X to Y at min cost / matching | Hungarian / bipartite matching | `scipy.optimize.linear_sum_assignment`, `networkx.max_weight_matching` |
| Distribute amounts over slots with capacities | min-cost flow | `networkx.min_cost_flow` / `max_flow_min_cost` |
| "maximum number of X that fit" (small) | ILP (binary vars per placement) | `scipy.optimize.milp` |
| Knockout bracket: simulate | pairs (0,1),(2,3)… per round | `make_fight(beats)`, `play_rounds(s,f,k)`, `champion` |
| "given counts, arrange so X wins" | **round-based survivor chain**: s_t ⊂ s_{t-1}, losers matched to survivors (Hall/flow), s_t ≈ counts/2^t | `build_bracket(counts, 'S', beats)` |
| Fixed tree + "choose the X spots" | tree DP: set of achievable values per node, reconstruct top-down | `fill_bracket(s, 'S', beats)` |
| …+ adversary spots ("no matter what Z is") | ∃∀ tree DP over *families of outcome sets* (bitmasks) | `rig_bracket(s, 'S', beats)` |
| Physics-ish steps (pace, accel, max speed) | precompute 1D move sequences; combine axes; BFS on (pos, vel) | `bfs` with tuple state |
| Fast solver unsure | brute force on small random inputs + compare | `crosscheck(fast, brute, gen)` |

## Meta-patterns (from Room Planner / RPS)
- **Count-only constructions** (only how many of each type matters): search over count vectors (≤5 types),
  check feasibility with a tiny flow/Hall test, then expand to an explicit layout. Far stronger than greedy fill orders.
- **Greedy misses by exactly 1 on some cases** = a structural gap (non-guillotine pinwheel, parity), not a bug.
  Find the smallest failing case, solve it exactly (`pack_exact`/brute force), and add it as a DP primitive.
- **Exact DP on small domains**: per-node *sets* of reachable values (≤32 subsets for 5 styles) are cheap.
  Monotone combine (bigger in → bigger out) lets you keep only minimal sets.

## Pitfalls (each cost real contests time)
- **Rules only in images.** Some games (RPS) put every rule in PDF images. Extracted text = bullets "▪▪▪".
  Render ALL pages (diagram pages carry no text, so `fetch --png` may skip them):
  `python -c "import pypdfium2 as p; d=p.PdfDocument('files/level-N.pdf'); [d[i].render(scale=0.75).to_pil().save(f'pages/p{i+1}.png') for i in range(len(d))]"`
- **Width vs height order.** CCC usually gives `W H` (width first) but grids are listed as H rows of W chars. Check the example dims vs the rows.
- **Coordinates.** y grows DOWN in grids ("North = W = up = y-1"). Some levels use x,y with origin bottom-left or `row col`. Verify with the example.
- **Grid sizes off by one.** "Size of lawn" = max-min+1. Coordinates may be 0- or 1-based.
- **Output format.** One line per case, space-separated, trailing `\n`. Case order = input order. `out_lines` handles this.
- **Multiple valid answers.** The example output will NOT match. Define `check(data, out)` (the previous level's validator) so `ccc.py go` accepts the output. Never submit without it.
- **Garbled statement text.** pypdf can extract text with shifted font encoding, e.g. `' L D J R Q D O V` = "Diagonals" (each char +29). If a line looks like noise, read the PDF page or decode the shift.
- **"Every input is solvable" / "tree never on the edge".** These guarantees enable a construction. The NEXT level usually removes them, so write the construction generally (symmetries plus a search fallback) and the next level is often free (lawnmower L4→L5 took 40 s).
- **Parity.** Grid graphs are bipartite. A Hamiltonian cycle needs an even number of free cells. A path on an odd count must start and end on the majority colour.
- **Heavy-tailed search.** DFS/backtracking either finishes instantly or never. Use a portfolio: one deterministic run with growing slices, alternated with short (0.2 s) random-seed runs (`ham_cycle` does this). One stuck case blocks a whole file. Measured on lawnmower L7: long slices 77 s, short random 2 s, but some cases are solved only by the deterministic run.
- **Recursion.** Python recursion is limited to about 1000 frames. Lib functions are iterative. If you recurse, call `sys.setrecursionlimit(10**6)` and run the code in a `threading.Thread` with `threading.stack_size(512*2**20)`.
- **Large file is not always the hardest.** In lawnmower L7, small files had 50 cases and the hard ones were sparse open grids.
- **Weighted A\* with parent pointers.** With f = g + w·h (w > 1), a state can be improved after it was expanded. Its children then hang on a parent chain with different timing, and reconstructed paths break (Spaceship L8: collisions in our own output). Keep a `closed` set and never reopen. In time-dependent searches, key on `(state, t)` as the fallback.
- **Windows encoding.** Python's `open()` defaults to cp1252 here. Always pass `encoding="utf-8"` when writing files that contain non-ASCII characters.
