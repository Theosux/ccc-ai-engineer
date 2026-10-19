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
    return (y1 + y2) / 2 <= y0 - 0.5  # ray starts just inside T: a diagonal through T's corner crosses it


def all_islands(g):
    n = len(g)
    seen = [[False] * n for _ in range(n)]
    out = []
    for y in range(n):
        for x in range(n):
            if g[y][x] == "L" and not seen[y][x]:
                isl = island_of(g, (x, y))
                for a, b in isl:
                    seen[b][a] = True
                xs = [a for a, _ in isl]
                ys = [b for _, b in isl]
                out.append(((x, y), (min(xs), min(ys), max(xs), max(ys))))  # row-major: (x, y) is top-left
    return out


def other_rays(isls, x0, y0, tb, R):
    """rays[x] = [(y0J, bit)] for OTHER islands J within Chebyshev distance R of T's bbox tb, keyed by the column
    of J's top-left tile. Farther islands cannot be enclosed by a loop of length <= 2R - 2 that encloses T."""
    rays, k = {}, 0
    for (x, y), (a, b, c, d) in isls:
        if (x, y) == (x0, y0):
            continue
        dist = max(a - tb[2], tb[0] - c, b - tb[3], tb[1] - d, 0)
        if dist <= R:
            rays.setdefault(x, []).append((y, 1 << k))
            k += 1
    return rays


def flip(u, v, rays):
    (x1, y1), (x2, y2) = u, v
    if x1 == x2:
        return 0
    m = 0
    my = (y1 + y2) / 2
    for yj, bit in rays.get(max(x1, x2), ()):
        if my <= yj - 0.5:
            m ^= bit
    return m


def encircle(g, t, best=False, seed=()):
    """Loop around t's island: start on a ray cell, BFS without crossing the ray, end on a neighbour across it.
    Other islands must stay outside: their ray-crossing parities (bitmask) must be even when the loop closes.
    best=True tries every start on the ray and keeps the shortest loop."""
    T = island_of(g, t)
    x0, y0 = top_left(T)
    isls = [tl for tl, _ in all_islands(g) if tl != (x0, y0)]
    allrays = {}
    for k, (x, y) in enumerate(isls):
        allrays.setdefault(x, []).append((y, 1 << k))
    tracked = [k for k, tl in enumerate(isls) if tl in seed]  # constraint generation: only islands a candidate
    # loop enclosed get a parity bit
    while True:
        rays = {}
        for j, k in enumerate(tracked):
            x, y = isls[k]
            rays.setdefault(x, []).append((y, 1 << j))
        res = loop_search(g, x0, y0, rays, best, 10 ** 9)
        if res is None:
            return None
        enc = 0
        for u, v in zip(res, res[1:] + res[:1]):
            enc ^= flip(u, v, allrays)
        new = [k for k in range(len(isls)) if enc >> k & 1 and k not in tracked]
        if not new:
            return res
        tracked += new


def loop_search(g, x0, y0, rays, best, D):
    res = None
    for ys in range(y0 - 1, -1, -1):
        if res and 2 * (y0 - ys) >= len(res):  # a loop through (x0, ys) must reach row y0 and come back
            break
        if g[ys][x0] != "W":
            continue
        p = loop_from(g, (x0, ys), x0, y0, rays, len(res) - 1 if res else D)
        if p and (res is None or len(p) < len(res)):
            res = p
            if not best:
                break
    return res


def loop_from(g, s, x0, y0, rays, limit=10 ** 9):
    """Shortest loop (as tile list) starting at s; only paths with < limit + 1 tiles are searched."""
    n = len(g)
    goals = {v: flip(v, s, rays) for v in ((s[0] - 1, s[1] + d) for d in (-1, 0, 1))
             if 0 <= v[0] < n and 0 <= v[1] < n and g[v[1]][v[0]] == "W" and crosses(s, v, x0, y0)}
    if not goals:
        return None
    st = (s, 0)
    par = {st: None}
    dist = {st: 0}
    q = deque([st])
    while q:
        u = q.popleft()
        if dist[u] >= limit:
            return None
        cell, mask = u
        if cell in goals and mask == goals[cell]:
            path = []
            while u is not None:
                path.append(u[0])
                u = par[u]
            return path[::-1]
        for dx, dy in D8:
            v = (cell[0] + dx, cell[1] + dy)
            if 0 <= v[0] < n and 0 <= v[1] < n and g[v[1]][v[0]] == "W" and crosses(cell, v, x0, y0) is False:
                w = (v, mask ^ flip(cell, v, rays))
                if w not in par:
                    par[w] = u
                    dist[w] = dist[u] + 1
                    q.append(w)
    return None


def encircle_cut(g, t):
    """Shortest loop around t's island that encloses NO other island = minimum set of water cells 4-separating
    T from (other land + far border): node-split max flow (OR-Tools), on a window around T that grows until
    the cut (loop length c) is shorter than 2 * margin (a loop leaving the window would be longer)."""
    n = len(g)
    T = island_of(g, t)
    x0, y0 = top_left(T)
    isls = [tl for tl, _ in all_islands(g) if tl != (x0, y0)]
    def attempt(hard):
        cut = min_cut(g, T, hard)
        g2 = ["".join("W" if (x, y) in cut else ("L" if (x, y) in T else "X") for x in range(n)) for y in range(n)]
        res = encircle(g2, t, best=True)
        return res, (enclosed(res, isls) if res else None)

    hard = set()  # uncuttable water corridors: island -> map edge, so the island must stay outside the loop
    res, enc = attempt(hard)
    for _ in range(12):
        if res and not enc:
            return res  # a single loop of exactly the min-cut size (given the corridors)
        best = None
        for J in enc or ():  # try each corridor direction for the first enclosed island, keep the shortest result
            for edge in range(4):
                h2 = hard | corridor(g, T, J, edge)
                r2, e2 = attempt(h2)
                if r2 and (best is None or (len(e2), len(r2)) < (len(best[2]), len(best[1]))):
                    best = (h2, r2, e2)
            break
        if best is None:
            break
        hard, res, enc = best
    return encircle(g, t, best=True, seed=enc or ())  # exact parity search (slow) as the last resort


def corridor(g, T, J, edge):
    """Water cells of a shortest 4-path from island J to one map edge (0 left, 1 right, 2 top, 3 bottom),
    keeping 1 tile away from T."""
    n = len(g)
    near = {(a + dx, b + dy) for a, b in T for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    Jt = island_of(g, J)
    par = {c: None for c in Jt}
    q = deque(Jt)
    while q:
        u = q.popleft()
        if (u[0], n - 1 - u[0], u[1], n - 1 - u[1])[edge] == 0:
            out = set()
            while u is not None:
                if g[u[1]][u[0]] == "W":
                    out.add(u)
                u = par[u]
            return out
        for dx, dy in D8[:4]:
            v = (u[0] + dx, u[1] + dy)
            if 0 <= v[0] < n and 0 <= v[1] < n and v not in par and v not in near:
                par[v] = u
                q.append(v)
    return set()


def min_cut(g, T, hard):
    from ortools.graph.python import max_flow
    n = len(g)
    bx0, by0 = min(a for a, _ in T), min(b for _, b in T)
    bx1, by1 = max(a for a, _ in T), max(b for _, b in T)
    m = 4
    while True:
        X0, Y0, X1, Y1 = max(0, bx0 - m), max(0, by0 - m), min(n - 1, bx1 + m), min(n - 1, by1 + m)
        W = X1 - X0 + 1
        idx = lambda x, y: (y - Y0) * W + (x - X0)
        N = W * (Y1 - Y0 + 1)
        SRC, SNK = 2 * N, 2 * N + 1
        INF = 10 ** 6
        f = max_flow.SimpleMaxFlow()
        for y in range(Y0, Y1 + 1):
            for x in range(X0, X1 + 1):
                i = idx(x, y)
                land = g[y][x] == "L"
                f.add_arc_with_capacity(2 * i, 2 * i + 1, INF if land or (x, y) in hard else 1)
                if (x, y) in T:
                    f.add_arc_with_capacity(SRC, 2 * i, INF)
                elif land or x in (X0, X1) or y in (Y0, Y1):
                    f.add_arc_with_capacity(2 * i + 1, SNK, INF)
                for dx, dy in ((1, 0), (0, 1)):
                    if x + dx <= X1 and y + dy <= Y1:
                        j = idx(x + dx, y + dy)
                        f.add_arc_with_capacity(2 * i + 1, 2 * j, INF)
                        f.add_arc_with_capacity(2 * j + 1, 2 * i, INF)
        f.solve(SRC, SNK)
        c = f.optimal_flow()
        if 2 * m > c + 2 or (X0, Y0, X1, Y1) == (0, 0, n - 1, n - 1):
            break
        m = c // 2 + 3
    side = set(f.get_source_side_min_cut())
    return {(x, y) for y in range(Y0, Y1 + 1) for x in range(X0, X1 + 1)
            if 2 * idx(x, y) in side and 2 * idx(x, y) + 1 not in side}


def enclosed(loop, isls):
    allrays = {}
    for k, (x, y) in enumerate(isls):
        allrays.setdefault(x, []).append((y, 1 << k))
    e = 0
    for u, v in zip(loop, loop[1:] + loop[:1]):
        e ^= flip(u, v, allrays)
    return {isls[k] for k in range(len(isls)) if e >> k & 1}


def cases(data):
    n, g, qs = parse(data)
    return [(g, t) for t in qs]


def solve_case(c):
    g, t = c
    return fmt(encircle_cut(g, t))


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
