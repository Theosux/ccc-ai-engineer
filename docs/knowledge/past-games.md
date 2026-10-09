# Past CCC Classic games: level progressions + techniques

Sources: PDFs + Python solutions in https://github.com/gergely-elias/ccc ; Spaceship from the C# solver in
https://github.com/angua/CCC41 ; Lawn Mower from our own run (`arena/runs/lawnmower`, 7/7 solved).
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

## Room Planner / Desks (2024.10, 40th CCC)
| L | Change | Technique |
|---|---|---|
| 1 | count max 3×1 desks in rooms (x divisible by 3) | arithmetic `(x//3)*y` |
| 2 | output grid of desk IDs (count given = max) | fill rows with horizontal desks, IDs 1..n |
| 3 | x no longer divisible by 3 | *(s)* mix orientations: horizontal strip + vertical desks in remainder columns |
| 4 | desks may not touch (incl. diagonal); IDs dropped | *(s)* pattern: desks in every other row/col; output a char matrix; validator checks gaps |
| 5 | desk is now 1×2 (no touching) | *(s)* new tiling pattern; try both orientations, keep the one reaching the given count |
| 6 | desk length 1..7 (width 1) | *(s)* generalize the pattern by length k; perimeter/greedy packing; validate count+no-touch |
Pitfall: "given number is the max possible" means you must hit it exactly. Write a checker (bounds, overlap, touching via 8-neighbours) first.

## Rock Paper Scissors (2023.03)
| L | Change | Technique |
|---|---|---|
| 1 | winner of a 2-char fight | lookup (R>S, S>P, P>R; same = same) |
| 2 | bracket of 2^k fighters, styles left after 2 rounds | simulate pairs round by round |
| 3 | given counts of R/P/S, build first-round order so no R remains after 2 rounds and S survives | greedy blocks `PRRR` (one P kills ≤3 R in a 4-block), then P's, then S |
| 4 | Scissors must win the whole tournament | recursive bracket filling by halves (power-of-2 sub-brackets), simulate to verify |
| 5 | adds Lizard, Spock (RPSLS) | *(s)* generalize beats-table; same constructive idea |
| 6–7 | wildcards X / Z in input to be replaced | *(s)* choose replacements so the rigging works; search over bracket halves |
Key: always keep `simulate(bracket)` as the validator.

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

## Spaceship (2025.11, 41st CCC, 8 levels; best teams 7)
Paces 5→1 (time per step; 0 = stand still), accelerate/decelerate one pace step at a time.
| L | Change | Technique |
|---|---|---|
| 1–2 | sum/simulate pace sequences: time and position | simulate |
| 3–4 | 1D: produce pace sequence to reach x (within time limit) | accel 5,4,3,2,1 … decel 2,3,4,5; precompute |
| 5 | 2D: independent x and y sequences, pad the faster axis with waits | combine 1D solutions |
| 6 | asteroid to avoid + time limit | try x-first / y-first L-shaped paths, detour around blocked line |
| 7 | many asteroids | state-space search on (pos, paceX, paceY) with lower-bound pruning (time-to-reach) |
| 8 | (nobody solved) | — |

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

## Cross-game conventions
- Input: first line N (cases), then records; grids are "paragraphs" of H rows; sizes often `W H` (width first) or a single N for square maps.
- Coordinates vary per game: `x,y` with comma (Islands), 1-based `row col` (Pacman, Addictive), WASD with y down (Lawn Mower). Always confirm on the example.
- Validator levels output `VALID`/`INVALID` (or SAME/DIFFERENT). The next level becomes "construct one", checked by the same rules.
- "There are multiple correct solutions" means our example output will differ. Use a `check()` in solve.py.
- Optimization levels: "below a threshold" / "≥ X on every file". Any solution under the threshold passes, so it doesn't need to be optimal.
- Visualizer `sandbox-level-N.html` ships with constructive levels.
