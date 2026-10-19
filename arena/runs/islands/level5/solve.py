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
    return n, g, [q[0] if len(q) == 1 else q for q in qs]


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


def island_of(g, t):
    n = len(g)
    seen, st = {t}, [t]
    while st:
        x, y = st.pop()
        for dx, dy in D8[:4]:
            v = (x + dx, y + dy)
            if 0 <= v[0] < n and 0 <= v[1] < n and v not in seen and g[v[1]][v[0]] == "L":
                seen.add(v)
                st.append(v)
    return seen


def top_left(isl):
    return min(isl, key=lambda c: (c[1], c[0]))


def crosses(u, v, x0, y0):
    """Does step u->v cross the ray x = x0 - 0.5, y < y0 - 0.5 (up from T's top-left corner)?
    Returns None for the forbidden step through the corner point itself."""
    (x1, y1), (x2, y2) = u, v
    if {x1, x2} != {x0 - 1, x0}:
        return False
    my = (y1 + y2) / 2
    if my == y0 - 0.5:
        return None
    return my < y0 - 0.5


def encircle(g, t, best=False):
    """Loop around t's island: start on a ray cell, BFS without crossing the ray, end on a neighbour across it.
    best=True tries every start on the ray and keeps the shortest loop."""
    n = len(g)
    x0, y0 = top_left(island_of(g, t))
    res = None
    for ys in range(y0 - 1, -1, -1):
        if g[ys][x0] != "W":
            continue
        p = loop_from(g, (x0, ys), x0, y0)
        if p and (res is None or len(p) < len(res)):
            res = p
            if not best:
                break
    return res


def loop_from(g, s, x0, y0):
    n = len(g)
    goals = {v for v in ((s[0] - 1, s[1] + d) for d in (-1, 0, 1))
             if 0 <= v[0] < n and 0 <= v[1] < n and g[v[1]][v[0]] == "W" and crosses(s, v, x0, y0)}
    if not goals:
        return None
    par = {s: None}
    q = deque([s])
    while q:
        u = q.popleft()
        if u in goals:
            path = []
            while u is not None:
                path.append(u)
                u = par[u]
            return path[::-1]
        for dx, dy in D8:
            v = (u[0] + dx, u[1] + dy)
            if 0 <= v[0] < n and 0 <= v[1] < n and v not in par and g[v[1]][v[0]] == "W" \
                    and crosses(u, v, x0, y0) is False:
                if dx and dy and g[u[1]][v[0]] == "L" and g[v[1]][u[0]] == "L":
                    pass  # squeezing between two land tiles diagonally is allowed (islands don't connect diagonally)
                par[v] = u
                q.append(v)
    return None


def solve_case(d):
    n, g, qs = parse(d)
    return "\n".join(fmt(encircle(g, t)) for t in qs)


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
    for i, (t, l) in enumerate(zip(qs, ls)):
        p = [tuple(map(int, s.split(","))) for s in l.split()]
        err = check_route(g, p, None, None, 2 * n)
        if err:
            return False, f"route {i}: {err}"
        if max(abs(p[0][0] - p[-1][0]), abs(p[0][1] - p[-1][1])) != 1:
            return False, f"route {i}: end not next to start"
        x0, y0 = top_left(island_of(g, t))
        cr = [crosses(u, v, x0, y0) for u, v in zip(p, p[1:] + p[:1])]
        if None in cr or sum(cr) % 2 == 0:
            return False, f"route {i}: does not encircle the island"
    return True


if __name__ == "__main__":
    run_cases(cases, solve_case)
