import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *
from collections import deque

MV = {"L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)}


def cases(data):
    return [data]


def parse(d):
    r = Reader(d)
    n = r.int()
    g = [list(row) for row in r.grid(n)]
    p = (r.int() - 1, r.int() - 1)
    lim = r.int()
    return g, p, lim


def bfs_to_coin(g, s, coins):
    par = {s: None}
    q = deque([s])
    while q:
        u = q.popleft()
        if u in coins:
            path = []
            while par[u]:
                u, m = par[u]
                path.append(m)
            return path[::-1]
        for m, (dr, dc) in MV.items():
            v = (u[0] + dr, u[1] + dc)
            if v not in par and g[v[0]][v[1]] not in "WG":
                par[v] = (u, m)
                q.append(v)
    return None


def solve_case(d):
    g, p, lim = parse(d)
    coins = {(r, c) for r, row in enumerate(g) for c, ch in enumerate(row) if ch == "C"}
    out = []
    while coins:
        path = bfs_to_coin(g, p, coins)
        for m in path:
            p = (p[0] + MV[m][0], p[1] + MV[m][1])
            coins.discard(p)
        out += path
    return "".join(out)


def check(data, out):
    g, p, lim = parse(data)
    s = out.strip()
    if len(s) > lim:
        return False, f"len {len(s)} > {lim}"
    coins = {(r, c) for r, row in enumerate(g) for c, ch in enumerate(row) if ch == "C"}
    for i, m in enumerate(s):
        p = (p[0] + MV[m][0], p[1] + MV[m][1])
        if g[p[0]][p[1]] in "WG":
            return False, f"step {i} hits {g[p[0]][p[1]]}"
        coins.discard(p)
    return not coins, f"{len(coins)} coins left"


if __name__ == "__main__":
    run_cases(cases, solve_case)
