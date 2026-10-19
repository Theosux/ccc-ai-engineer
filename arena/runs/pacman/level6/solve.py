# ccc: pypy
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *
from collections import deque

MV = {"L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)}
INV = {"L": "R", "R": "L", "U": "D", "D": "U"}


def cases(data):
    return [data]


def parse(d):
    r = Reader(d)
    n = r.int()
    g = [list(row) for row in r.grid(n)]
    p = (r.int() - 1, r.int() - 1)
    ghosts = []
    for _ in range(r.int()):
        gp = (r.int() - 1, r.int() - 1)
        r.int()
        s = r.word()
        ghosts.append((gp, s + "".join(INV[m] for m in reversed(s))))  # walk the pattern, then back
    lim = r.int()
    return g, p, ghosts, lim


def ghost_cells(ghosts):
    """occ[t % P] = set of ghost cells after t steps (t = 0 is the start)."""
    P = max((len(s) for _, s in ghosts), default=1)
    occ = []
    pos = [gp for gp, _ in ghosts]
    for t in range(P):
        occ.append(set(pos))
        pos = [(r + MV[s[t % len(s)]][0], c + MV[s[t % len(s)]][1]) for (r, c), (_, s) in zip(pos, ghosts)]
    return occ, P


def solve_case(d):
    """Exact shortest route collecting all coins: layered BFS over (cell, coin mask), time = layer (ghost phase)."""
    g, (pr, pc), ghosts, lim = parse(d)
    occ, P = ghost_cells(ghosts)
    n, m = len(g), len(g[0])
    coins = [(r, c) for r in range(n) for c in range(m) if g[r][c] == "C"]
    bit = {rc: 1 << k for k, rc in enumerate(coins)}
    full = (1 << len(coins)) - 1
    occi = [{r * m + c for r, c in o} for o in occ]
    wall = [g[i // m][i % m] == "W" for i in range(n * m)]
    cbit = [bit.get((i // m, i % m), 0) for i in range(n * m)]
    moves = [("L", -1), ("R", 1), ("U", -m), ("D", m)]
    K = 1 << len(coins)
    seen = bytearray(n * m * K * P)
    start = (pr * m + pc) * K + cbit[pr * m + pc]
    layer, t, parents = [start], 0, []
    seen[start * P] = 1
    while layer:
        par = {}
        nt = t + 1
        ph = nt % P
        bad = occi[ph]
        nxt = []
        for st in layer:
            i, mask = divmod(st, K)
            for ch, dv in moves:
                j = i + dv
                if wall[j] or j in bad:
                    continue
                nm = mask | cbit[j]
                ns = j * K + nm
                key = ns * P + ph
                if seen[key]:
                    continue
                seen[key] = 1
                par[ns] = (st, ch)
                if nm == full:
                    parents.append(par)
                    path, cur = [], ns
                    for pl in reversed(parents):
                        cur, mv = pl[cur]
                        path.append(mv)
                    return "".join(reversed(path))
                nxt.append(ns)
        parents.append(par)
        layer, t = nxt, nt
    return ""


def check(data, out):
    g, p, ghosts, lim = parse(data)
    occ, P = ghost_cells(ghosts)
    coins = {(r, c) for r, row in enumerate(g) for c, ch in enumerate(row) if ch == "C"}
    s = out.strip()
    if len(s) > lim:
        return False, f"len {len(s)}"
    for i, m in enumerate(s, 1):
        p = (p[0] + MV[m][0], p[1] + MV[m][1])
        if g[p[0]][p[1]] == "W" or p in occ[i % P]:
            return False, f"step {i} dies"
        coins.discard(p)
    return not coins, f"{len(coins)} coins left"


if __name__ == "__main__":
    run_cases(cases, solve_case)
