import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *
from collections import deque

D8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def cases(data):
    return [data]


def parse(d):
    ls = [l.strip() for l in d.split("\n") if l.strip()]
    n = int(ls[0])
    g = ls[1:1 + n]
    k = int(ls[1 + n])
    qs = [[tuple(map(int, t.split(","))) for t in l.split()] for l in ls[2 + n:2 + n + k]]
    return n, g, qs


def route_ok(path):
    """No tile twice, no two diagonal steps crossing in the same 2x2 square."""
    if len(set(path)) != len(path):
        return False
    diag = set()
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        if x1 != x2 and y1 != y2:
            if frozenset(((x2, y1), (x1, y2))) in diag:
                return False
            diag.add(frozenset(((x1, y1), (x2, y2))))
    return True


def sea_bfs(g, a, b):
    n = len(g)
    par = {a: None}
    q = deque([a])
    while q:
        u = q.popleft()
        if u == b:
            break
        for dx, dy in D8:
            v = (u[0] + dx, u[1] + dy)
            if 0 <= v[0] < n and 0 <= v[1] < n and v not in par and g[v[1]][v[0]] == "W":
                par[v] = u
                q.append(v)
    path, u = [], b
    while u is not None:
        path.append(u)
        u = par[u]
    return path[::-1]


def fmt(path):
    return " ".join(f"{x},{y}" for x, y in path)


def solve_case(d):
    n, g, qs = parse(d)
    return "\n".join(fmt(sea_bfs(g, a, b)) for a, b in qs)


def check_route(g, p, a=None, b=None, maxlen=None):
    if a is not None and (p[0] != a or p[-1] != b):
        return "ends"
    if maxlen is not None and len(p) > maxlen:
        return f"length {len(p)} > {maxlen}"
    n = len(g)
    if any(not (0 <= x < n and 0 <= y < n) or g[y][x] != "W" for x, y in p):
        return "land/outside"
    if any(max(abs(x1 - x2), abs(y1 - y2)) != 1 for (x1, y1), (x2, y2) in zip(p, p[1:])):
        return "gap"
    if not route_ok(p):
        return "self-intersection"
    return None


def check(data, out):
    n, g, qs = parse(data)
    ls = [l for l in out.strip().split("\n") if l.strip()]
    if len(ls) != len(qs):
        return False, "line count"
    for i, ((a, b), l) in enumerate(zip(qs, ls)):
        p = [tuple(map(int, t.split(","))) for t in l.split()]
        err = check_route(g, p, a, b, 2 * n)
        if err:
            return False, f"route {i}: {err}"
    return True


if __name__ == "__main__":
    run_cases(cases, solve_case)
