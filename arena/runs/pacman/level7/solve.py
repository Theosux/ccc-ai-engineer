import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *
from collections import deque

MV = {"D": (1, 0), "L": (0, -1), "R": (0, 1), "U": (-1, 0)}  # alphabetical: ghost tie-break


def cases(data):
    return [data]


def parse(d):
    r = Reader(d)
    n = r.int()
    g = r.grid(n)
    p = (r.int() - 1, r.int() - 1)
    gh = [(r.int() - 1, r.int() - 1) for _ in range(r.int())]
    coins = {}
    for _ in range(r.int()):
        cr, cc, v = r.int() - 1, r.int() - 1, r.int()
        coins[(cr, cc)] = v
    L = r.int()
    return g, p, gh, coins, L


def ghost_track(g, start, target):
    """Lexicographically smallest shortest path start->target, as the list of cells (start..target)."""
    n = len(g)
    dist = {target: 0}
    q = deque([target])
    while q:
        u = q.popleft()
        for dr, dc in MV.values():
            v = (u[0] + dr, u[1] + dc)
            if 0 <= v[0] < n and 0 <= v[1] < n and v not in dist and g[v[0]][v[1]] != "W":
                dist[v] = dist[u] + 1
                q.append(v)
    cells = [start]
    u = start
    while u != target:
        for dr, dc in MV.values():
            v = (u[0] + dr, u[1] + dc)
            if dist.get(v) == dist[u] - 1:
                u = v
                break
        cells.append(u)
    return cells


def ghost_at(track, t):
    d = len(track) - 1
    if d == 0:
        return track[0]
    k = t % (2 * d)
    return track[k] if k <= d else track[2 * d - k]


def solve_case(d):
    g, p, gh, coins, L = parse(d)
    n = len(g)
    tracks = [ghost_track(g, s, p) for s in gh]
    NEG = -1
    best = {p: 0}
    for t in range(1, L + 1):
        bad = {ghost_at(tr, t) for tr in tracks}
        nb = {}
        for (r, c), sc in best.items():
            for dr, dc in MV.values():
                v = (r + dr, c + dc)
                if g[v[0]][v[1]] == "W" or v in bad:
                    continue
                s2 = sc + coins.get(v, 0)
                if nb.get(v, NEG) < s2:
                    nb[v] = s2
        best = nb
    return str(max(best.values()) if best else 0)


if __name__ == "__main__":
    run_cases(cases, solve_case)
