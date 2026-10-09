"""Self-test for arena/lib. Run: python arena/lib/tests/test_lib.py   (plain asserts, no pytest needed)."""
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib import *  # noqa
from lib import geom


def t_parse():
    r = Reader("2\n3 2\n..X\n...\nWDS\n1 1\n.\nX\n")
    assert r.int() == 2
    assert r.ints(2) == [3, 2] and r.grid(2) == ["..X", "..."] and r.word() == "WDS"
    L = Lines("a b\n\nc d e\n")
    assert L.line() == "a b" and L.line().split() == ["c", "d", "e"]
    assert paragraphs("a\nb\n\nc\n") == [["a", "b"], ["c"]]
    assert out_lines([1, (2, 3), "x"]) == "1\n2 3\nx\n"


def t_grid():
    g = ["..X", "..."]
    assert dims(g) == (3, 2) and find(g, "X") == (2, 0)
    assert walk("DS") == [(0, 0), (1, 0), (1, 1)]
    assert cells_to_moves([(0, 0), (1, 0), (1, 1), (0, 1)]) == "DSA"
    assert sorted(nb4(0, 0, 3, 2)) == [(0, 1), (1, 0)]
    assert len(list(nb8(1, 1, 3, 3))) == 8
    assert rot_cw(["ab", "cd"]) == ["ca", "db"] and transpose(["ab", "cd"]) == ["ac", "bd"]
    # symmetry round trip: a valid path on transformed grid maps back to a valid path on original
    rng = random.Random(3)
    for _ in range(50):
        w, h = rng.randint(2, 6), rng.randint(2, 6)
        grid = ["." * w for _ in range(h)]
        for s in SYMS:
            gg = sym_grid(grid, s)
            m = cells_to_moves(snake_rows(0, 0, len(gg[0]) - 1, len(gg) - 1))
            assert find_cover_start(grid, sym_moves_back(m, s)) is not None


def t_paths():
    lvl3 = ["..X..", ".....", "....."]  # lawnmower level-3 example: INVALID x3, then VALID
    assert [valid_cover(lvl3, p) for p in ("SSDWDSDWWDSS", "DSSAWDDSDWWDSS", "SSDWWDSSDWWDSS", "ASSDWDSDWWDSS")] \
        == [False, False, False, True]
    assert valid_cover(["....", "....", "....", "...."], cells_to_moves(snake_rows(0, 0, 3, 3)))
    assert not valid_cover(["...."], "DDDD") and not valid_cover(["...."], "DQ")
    # ham_path / exact on random small grids with one obstacle
    rng = random.Random(7)
    for _ in range(30):
        w, h = rng.randint(3, 7), rng.randint(3, 7)
        rows = [["."] * w for _ in range(h)]
        rows[rng.randrange(h)][rng.randrange(w)] = "X"
        g = ["".join(r) for r in rows]
        p = ham_path(g, time_limit=2)
        q = ham_path_exact(g, time_limit=5)
        assert (p is None) == (q is None) or p is None, g  # exact must find anything DFS finds
        if q:
            assert valid_cover(g, cells_to_moves(q))
    # cycles
    for g in (["...."] * 4, [".....", ".....", "X....", ".....", ".....", ".....", "....."],
              ["....", ".X..", "....", "...."]):
        c = ham_cycle(g, time_limit=5)
        if sum(r.count(".") for r in g) % 2 == 0 and g[1] != ".X..":
            assert c and valid_cover(g, cells_to_moves(c), cycle=True), g
    assert ham_cycle(["...", "...", "..."]) is None  # odd count
    hp = ham_path(["....", "....", "...."], cycle=True)
    assert hp and valid_cover(["....", "....", "...."], cells_to_moves(hp), cycle=True)
    # fixed endpoints
    g = ["....", "....", "...."]
    p = ham_path_exact(g, start=(0, 0), end=(3, 2))
    assert p[0] == (0, 0) and p[-1] == (3, 2) and valid_cover(g, cells_to_moves(p))


def t_search():
    g = ["..#", "...", "#.."]
    dist, par = grid_bfs(g, [(0, 0)])
    assert dist[(2, 2)] == 4 and path_to(par, (2, 2))[0] == (0, 0)
    d2, _ = grid_bfs(g, [(0, 0), (2, 2)])
    assert d2[(1, 1)] == 2
    adj = {0: [(1, 4), (2, 1)], 1: [(3, 1)], 2: [(1, 2), (3, 5)], 3: []}
    dist, par, _ = dijkstra(0, lambda u: adj[u])
    assert dist[3] == 4 and path_to(par, 3) == [0, 2, 1, 3]
    c, p = astar((0, 0), lambda u: [((u[0] + 1, u[1]), 1), ((u[0], u[1] + 1), 1)],
                 lambda u: abs(3 - u[0]) + abs(3 - u[1]), lambda u: u == (3, 3))
    assert c == 6 and p[-1] == (3, 3)
    d, par, found = bfs(0, lambda u: [u + 1, u * 2], goal=lambda u: u == 10)
    assert found == 10 and d[10] == 5  # 0-1-2-4-5-10
    assert len(grid_components([".#.", "##.", "..."])) == 2
    assert toposort([1, 2, 3], [(1, 2), (2, 3)]) == [1, 2, 3] and toposort([1, 2], [(1, 2), (2, 1)]) is None
    u = DSU()
    u.union(1, 2); u.union(3, 4)
    assert u.same(1, 2) and not u.same(1, 3)


def t_sim_opt_geom():
    assert state_at(0, lambda s: (s + 3) % 7, 10**18) == (3 * 10**18) % 7
    assert state_at(5, lambda s: max(s - 1, 0), 3) == 2
    best, c = anneal([5, -3, 8], lambda s, r: [x + r.choice((-1, 1)) for x in s], lambda s: sum(x * x for x in s), seconds=0.3)
    assert c <= 3
    assert geom.segments_intersect((0, 0), (2, 2), (0, 2), (2, 0))
    assert not geom.segments_intersect((0, 0), (1, 0), (0, 1), (1, 1))
    assert geom.rects_overlap((0, 0, 1, 1), (1, 1, 2, 2)) and not geom.rects_overlap((0, 0, 1, 1), (2, 0, 3, 1))
    assert geom.rects_overlap((0, 0, 1, 1), (2, 0, 3, 1), touch=True)
    assert geom.convex_hull([(0, 0), (1, 1), (2, 0), (2, 2), (0, 2)]) == [(0, 0), (2, 0), (2, 2), (0, 2)]
    assert crosscheck(lambda s: str(sum(map(int, s.split()))), lambda s: str(sum(int(x) for x in s.split())),
                      lambda r: " ".join(str(r.randint(0, 9)) for _ in range(5)), trials=20) is None


if __name__ == "__main__":
    t0 = time.time()
    for name, fn in list(globals().items()):
        if name.startswith("t_"):
            fn()
            print(f"ok {name}")
    print(f"ALL OK ({time.time() - t0:.1f}s)")
