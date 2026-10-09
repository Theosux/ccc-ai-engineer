# External resources (only the useful ones)

## Past CCC material
- https://github.com/gergely-elias/ccc: PDFs + Python solutions (Islands, Lawn Mower, Pacman, RPS, Room Planner, Smart Grid, Matchmaking, Addictive Game). Uses `networkx`.
- https://github.com/angua/CCC41: Spaceship (41st CCC) C# solver; `CCC41Lib/Solver.cs` has level logic.
- https://github.com/aarroyoc/catcoder: Autonomous Drone (school game).
- https://github.com/Lingepumpe/ccc_solver_template: solver template for catcoder.
- Practice platform: `python arena/ccc.py games` (Spaceship, Room Planner, Lawn Mower, RPS classic + school games).

## Algorithms reference
- https://cp-algorithms.com: graphs (BFS/0-1 BFS/Dijkstra, flows, matching), geometry, DP. Best "how does X work" source.
- https://github.com/kth-competitive-programming/kactl: dense C++ snippets (geometry, flows). Good for porting.
- https://github.com/cheran-senthil/PyRival: Python CP library (fast IO, segment trees, flows, FFT), PyPy-friendly.
- https://usaco.guide: technique explanations with problems (flood fill, BFS states, DP).
- Hamiltonian cycles in grids: edge-degree constraint propagation (what `lib.ham_cycle` does) and cycle merging over 2×2 blocks.
- Local search: https://en.wikipedia.org/wiki/Simulated_annealing and AtCoder Heuristic Contest writeups (anneal temperature schedule, delta evaluation).

## Libraries available locally (Python 3.14)
- `networkx` 3.6: `shortest_path`, `max_weight_matching`, `maximum_flow`, `min_cost_flow`, `connected_components`, `simple_cycles`.
- `scipy` 1.17: `optimize.linear_sum_assignment` (assignment), `optimize.milp` (ILP via HiGHS: exact packing/scheduling for small instances), `sparse.csgraph` (fast BFS/Dijkstra on big graphs).
- `numpy` 2.4: vectorised simulation and grids.
- PyPy 3.11 (v8.0.0) was tested from a temp unzip (not installed). See the final report and `solving-playbook.md` §4.
