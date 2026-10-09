---
name: ccc-patterns
description: Problem-solving cheat sheet + helper library (arena/lib) for Cloudflight Coding Contest levels. Use whenever writing or strategizing a CCC solve.py — reading a new level statement, choosing a technique (grid/BFS/Hamiltonian path/construction/validator/optimization), when a level says "multiple correct solutions", when a solver is slow or fails some cases, or when the user says "solve level N" / "next level" / "contest started" (use together with ccc-solve).
---

# CCC patterns + arena/lib

ccc-solve handles the fetch → go loop. This skill tells you HOW to solve a level fast.
Deeper references are in `docs/knowledge/`. Open them only when needed:
`ccc-patterns.md` (X → technique → lib function, pitfalls), `solving-playbook.md` (procedure, slow-solver steps),
`past-games.md` (how every past game's levels escalated), `resources.md` (links, local libs).

## solve.py skeleton
```python
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *

def solve(data):
    r = Reader(data)
    out = []
    for _ in range(r.int()):
        w, h = r.ints(2); g = r.grid(h)        # grid[y][x], y grows down
        out.append(answer(g))
    return out_lines(out)

def check(data, out):                          # ONLY if many answers are valid; go uses it instead of example match
    ...return ok, msg

if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
```
Local run with timings: `python arena/lib/check.py arena/runs/<run>/levelN [1-small] [--profile]`.

## lib cheat sheet (`from lib import *`)
- **parse:** `Reader(data)` `.int() .ints(k) .word() .words(k) .grid(h) .rest()` · `Lines(data)` · `paragraphs` · `ints_of("4,2 8,5")` · `pairs_of` · `out_lines(list)`
- **grid:** `WASD NESW UDLR` → (dx,dy) · `VEC2WASD OPP TURN_R TURN_L DIRS4 DIRS8` · `nb4/nb8(x,y,w,h)` · `find(g,'X')` · `cells(g,'.')` · `walk(moves,start)` · `bbox` · `cells_to_moves` · `idx_to_rc(p,cols)` · `rot_cw transpose flip_h flip_v` · `SYMS sym_grid sym_moves_back` · `show(g, marks)` (stderr)
- **paths:** `valid_cover(g, moves, cycle=False)` (start unknown) · `covers_once(g,start,moves)` · `snake_rows/snake_cols` · `try_symmetries(g, construct, check)` · `ham_path(g, start, end, cycle, time_limit)` (fast DFS) · `ham_cycle(g)` / `ham_path_exact(g,start,end)` (exact, constraint propagation + restarts) · `ham_cycle_graph(n, edges)` (any graph)
- **search:** `grid_bfs(g, sources, passable)` → (dist, par) · `bfs(start, nbrs, goal)` · `dijkstra(start, nbrs→(v,c), goal)` · `astar(start, nbrs, h, is_goal)` · `path_to(par, end)` · `grid_components` · `toposort` · `DSU`
- **sim/opt/geom:** `state_at(s0, step, n)` (cycle skip for 10^18 steps) · `anneal(sol, neighbor, cost, seconds)` · `hill_climb` · `geom.segments_intersect / rects_overlap(touch=) / convex_hull / manhattan` · `crosscheck(fast, brute, gen)`
- Also installed: `networkx` (flows, matching), `scipy.optimize` (`linear_sum_assignment`, `milp`), `numpy`.

## Decision rules
1. **Read the example in/out first.** Confirm W/H order, x/y vs row/col, 0/1-based, y-down.
2. **Diff against the previous level.** Find the guarantee that was dropped. Rerun the previous solver first; general code often passes as is.
3. **VALID/INVALID level:** write a clean validator. The next level will ask you to construct, using it as `check()`.
4. **"Multiple correct solutions":** define `check()`, write one construction for one orientation, use `try_symmetries`, and add a search fallback.
5. **Visit-all-cells / cycle:** snake construction. If obstacles vary, `ham_cycle` / `ham_path_exact`. Cycles need an even free count.
6. **Shortest / min cost:** BFS (unit), Dijkstra (weights), with a state tuple if it has speed/dir/time.
7. **Threshold/optimize:** valid greedy first, then flow / assignment / ILP / anneal until the threshold.
8. **Search sometimes hangs:** heavy tail. Restart portfolio (deterministic plus short random runs), not longer timeouts.
9. **Garbled statement line** (`' L D J R Q D O V`): font shift +29 ("Diagonals…"). Read the PDF.
10. **No debug output on stdout**, never write "FAIL" placeholders into outputs, and use utf-8 when writing files.
