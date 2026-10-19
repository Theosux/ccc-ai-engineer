# Past CCC Classic games: level progressions + techniques

Sources: PDFs + Python solutions in https://github.com/gergely-elias/ccc ; Spaceship: statements from
https://github.com/blu3r4y/ccc-linz-nov2025 + C# solver https://github.com/angua/CCC41 ; Lawn Mower, Room Planner,
RPS from our own runs (`arena/runs/lawnmower|speedtest|rps`, all 7/7).
Practice games available on the platform (`ccc.py games`): Spaceship, Room Planner (desks), Lawn Mower, RPS (+ school games).

Technique cells = what the published solutions did, or *(s)* = our suggested approach where no solution was available.

**Universal shape:** L1 parse+count → L2 simulate/aggregate → L3 *validate* (VALID/INVALID or a checker) →
L4 *construct* (many valid answers, "use previous level to validate") → L5–6 remove a simplifying guarantee →
L7–8 hard search / optimization ("shortest", "maximum", "below threshold").

## Robotic Lawn Mower (2024.04): we solved 7/7
| L | Change | Technique (our time) |
|---|---|---|
| 1 | count W/D/S/A per path | `str.count` (min) |
| 2 | smallest lawn fitting path | bbox of walk, `max-min+1` |
| 3 | lawn grid + tree, path valid? (visit all free cells once, start unknown) | try start offset from bbox; `valid_cover` |
| 4 | construct cover path, tree never on edge | row snake + 2-row column-zigzag band around tree; 8 symmetries; validate; `ham_path` fallback (4 min) |
| 5 | tree anywhere | same code, unchanged (40 s) |
| 6 | path must end next to start (cycle); PDF text garbled | strip-construction cycle; parity = both dims odd (1.5 min) |
| 7 | multiple trees, cycle | **exact edge-propagation Hamiltonian cycle + random restarts** (`ham_cycle`). DFS+Warnsdorff failed on ~10% (24 min) |

## Room Planner / Desks (2024.10, 40th CCC): we solved 7/7 (L4–L7 in 6.5 min total, run `speedtest`)
Input `x y k` per room (x = columns). Output: grid. "Given number is the maximum possible" = hit it exactly.
| L | Change | Technique (our time) |
|---|---|---|
| 1 | count 3×1 desks (x divisible by 3) | `(x//3)*y` |
| 2 | grid of desk IDs | horizontal rows, IDs 1..n |
| 3 | x not divisible by 3 | rows of horizontal + vertical desks in remainder columns, try both orientations |
| 4 | desks must not touch (incl. diagonal), char grid `X`/`.` | **inflate desk + room by 1** → plain packing of 4×2 into (x+1)×(y+1); guillotine DP hits all 323 (1.5 min) |
| 5 | desk 1×2 | guillotine misses by 1 on 23 rooms (pinwheels, e.g. 6×6→8) → DP + exact small blocks (1 min) |
| 6 | desk length 1..7 per room (4th int) | + top-level 5-region pinwheel split; all hit in 2 s (2.8 min) |
| 7 | mix lengths freely, maximize covered cells | weighted DP `value=w*h` (1 min) |
All via `lib.pack.pack_rects(x, y, [(L,1)], gap=1, target=k[, value])` + `check_rects_grid`.

## Rock Paper Scissors (2023.03): we solved 7/7 (11 min total, run `rps`)
**Rules are only in PDF images** (extracted text = bullets): render pages. Brackets: M = 2^k, pairs (0,1),(2,3)…
| L | Change | Technique (our time) |
|---|---|---|
| 1 | winner of 2-char fight | lookup (0.4 min) |
| 2 | M fighters, styles left after 2 rounds | simulate 2 rounds (0.3) |
| 3 | counts R/P/S → order with no R and ≥1 S after 2 rounds | blocks `PRRR` + shuffle rest, verify (1.2, image read) |
| 4 | S must win whole tournament | `build_bracket(counts,'S',beats)` (1.8) |
| 5 | + Spock `Y`, Lizard `L` (diagram on PDF p4, standard RPSLS) | halving heuristic failed 18 cases → **round-based survivor chain + matching** (6.3) |
| 6 | fixed order, fill `X` spots so S wins | tree DP over achievable-winner sets `fill_bracket` (0.5) |
| 7 | + `Z` spots filled by adversary afterwards; S must win for every Z | DP over families of outcome-set bitmasks `rig_bracket` (0.7) |

## Islands (2023)
| L | Change | Technique |
|---|---|---|
| 1 | land or water at x,y (coords "x,y") | index `grid[y][x]` |
| 2 | two coords on same island? (4-connected) | flood fill / DSU component ids |
| 3 | route (8-dir) self-intersects? (repeat tile or crossing diagonals) | set of tiles + set of diagonal edges; crossing = (a→b diag) and the other diagonal of the same 2×2 |
| 4 | find sea route A→B (8-dir, no land, no crossing) | BFS on water with 8-neighbours (shortest has no self-cross) |
| 5 | route encircling an island (end adjacent to start) | *(s)* walk ring of water around island (boundary following) |
| 6 | shortest encircling route | *(s)* BFS on (cell, winding/crossing a ray) state = "cut" trick: forbid crossing a ray from island to edge, BFS from one side to the other |
| 7 | must not encircle other islands | *(s)* same + extra rays/constraints for other islands |

## Spaceship (2025.11, 41st CCC, 8 levels): **we solved 8/8 in 36.6 min** (timed Challenge rehearsal, 2026-10-19, run `spaceship`)
The 2025 winners did 7/8 in 3h42m, and nobody solved L8. Pace = time per 1 unit of space (5 slow … 1 fast, negative = backwards, 0 = stand still for 1 tick). Paces change one step at a time: `-1⇆…⇆-5⇆0⇄5⇄…⇄1`. Sequences start and end with 0.

**Exact semantics** come from the visualizer JS:
- A pace p lasts |p| ticks (a 0 lasts 1) and moves at the end of the pace.
- Collision means |dx| ≤ 2 and |dy| ≤ 2 at **any tick**.
- An asteroid's position at tick t is p0 + trunc(t / v) on each axis.

| L | Change | What worked | Time |
|---|---|---|---|
| 1 | total time of paces | sum | 1.0 min |
| 2 | 0 and negative paces | sign/abs | 0.5 |
| 3 | 1D reach x, generous limit | ramp 5→k, cruise k, ramp back. **This is the optimal 1D profile** (min over k). `check()` validator | 0.5 |
| 4 | 2D, limit requires optimal | the same 1D optimum per axis | 1.1 |
| 5 | 1 asteroid, generous | axis-aligned waypoint legs + exact tick simulator (from visualizer) | 1.4 |
| 6 | tighter limit | one axis detours to a lane while the other travels (search lane, delay, return wait) | 0.9 |
| 7 | **5000 asteroids, dist ≤ 589 (inputs 19 MB)** | event-driven **A\*** on (x, y, paceX, remX, paceY, remY). Heuristic = max(exact 1-D cost-to-go table from reverse Dijkstra, **8-connected BFS maze distance**). Weighted w=3 → 2 → 1.5 → 1, PyPy, `multiprocessing.Pool` per case: 140 s for 500 cases | **29.4** |
| 8 | moving asteroids (500) | the same A\* made time-dependent: key (state, t), check every intermediate tick, cache asteroid cells per tick (25 lookups per query) | 1.8 |

**L7 lesson:** I wasted about 10 min on a free-space heuristic and a waypoint search before looking at the input size. **Read the `sizes:` line from fetch first.** In a maze, an obstacle-aware heuristic (geodesic BFS) is what makes A\* fast.

## Smart Grid (2020.10)
L1 cheapest minute → L2 cheapest contiguous interval per task (prefix sums / sliding window) →
L3 power amount drawn in cheapest minute in [start,end] (range min) → L4 max power per minute, bill ≤ threshold
(greedy by price; or **min-cost flow**) → L5 + max concurrent tasks → L6 nonlinear price (rises with load: spread load,
convex cost → greedy marginal cost / annealing) → L7 many households sharing price. Solutions used annealing + graph flow.

## Pacman (≈2022), Matchmaking (≈2021), Addictive Game (old)
- **Pacman:** count coins → simulate moves (1-based row/col, L/R/U/D) → ghosts move in parallel, collision = dead →
  generate route collecting all coins (BFS to nearest coin repeatedly, ≤ max length) → avoid moving ghosts
  (time-expanded BFS on (pos, t mod period)) → maximize coin value within step limit (greedy + search).
- **Matchmaking:** max score player (tie: lower id) → win/loss ratings, sort by (-score, id) → Elo updates
  (`floor(k*(s-exp))`, team ratings) → build balanced teams.
- **Addictive Game (Flow):** linear position ↔ (row,col) (1-based, `(p-1)//cols+1`) → validate paths connecting
  same-colour points → find connecting paths (BFS / backtracking).

## How far real contestants get
blu3r4y (Python, solo) finished: 2021 L1–3 (rank #16), 2022 L1–4, 2023 L1–5, 2025 L1–4 (of 8)
(github.com/blu3r4y/ccc-linz-*). Last 1–2 levels are rarely
solved in-contest, so **a fast clean L1–5 already ranks well**; the winners are the ones who crack the hard search level.

## Cross-game conventions
- Input: first line N (cases), then records; grids are "paragraphs" of H rows; sizes often `W H` (width first) or a single N for square maps.
- Coordinates vary per game: `x,y` with comma (Islands), 1-based `row col` (Pacman, Addictive), WASD with y down (Lawn Mower). Always confirm on the example.
- Validator levels output `VALID`/`INVALID` (or SAME/DIFFERENT). The next level becomes "construct one", checked by the same rules.
- "There are multiple correct solutions" means our example output will differ. Use a `check()` in solve.py.
- Optimization levels: "below a threshold" / "≥ X on every file". Any solution under the threshold passes, so it doesn't need to be optimal.
- Visualizer `sandbox-level-N.html` ships with constructive levels.
