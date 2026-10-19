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
    g, p, ghosts, lim = parse(d)
    occ, P = ghost_cells(ghosts)
    s = (p, 0)
    par = {s: None}
    q = deque([s])
    while q:
        u = q.popleft()
        (r, c), t = u
        if g[r][c] == "C":
            path = []
            while par[u]:
                u, m = par[u]
                path.append(m)
            return "".join(reversed(path))
        nt = (t + 1) % P
        for m, (dr, dc) in MV.items():
            v = ((r + dr, c + dc), nt)
            if v not in par and g[r + dr][c + dc] != "W" and (r + dr, c + dc) not in occ[nt]:
                par[v] = (u, m)
                q.append(v)
    return ""


def check(data, out):
    g, p, ghosts, lim = parse(data)
    occ, P = ghost_cells(ghosts)
    s = out.strip()
    if not s or len(s) > lim:
        return False, f"len {len(s)}"
    for i, m in enumerate(s, 1):
        p = (p[0] + MV[m][0], p[1] + MV[m][1])
        if g[p[0]][p[1]] == "W" or p in occ[i % P]:
            return False, f"step {i} dies"
        if g[p[0]][p[1]] == "C":
            return i == len(s), "moves after the coin"
    return False, "coin not reached"


if __name__ == "__main__":
    run_cases(cases, solve_case)
