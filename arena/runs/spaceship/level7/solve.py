# ccc: pypy
import sys
import heapq

ORDER = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]
AREA = 2  # collision if |dx| <= 2 and |dy| <= 2 (visualizer hasShipCollided)


def nxt(v):
    """Legal next paces after pace v (visualizer getValidPaces)."""
    if v == 0:
        return (-5, 0, 5)
    if v == 5:
        return (0, 5, 4)
    if v == -5:
        return (0, -5, -4)
    if v == 1:
        return (2, 1)
    if v == -1:
        return (-2, -1)
    return (v + 1, v, v - 1)


def dur(p):
    return abs(p) if p else 1


def sgn(p):
    return (p > 0) - (p < 0)


PACES = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]


def cost_to_go(M):
    """C[(d, v)]: min ticks from a pace boundary (offset d = target - pos, last pace v) to standing at the
    target after a completed 0 pace. Reverse Dijkstra over the 1-D pace graph."""
    INF = float("inf")
    C = {}
    pq = [(0, 0, 0)]
    prev = {v: [u for u in PACES if v in nxt(u)] for v in PACES}
    while pq:
        c, d, v = heapq.heappop(pq)
        if (d, v) in C:
            continue
        C[(d, v)] = c
        # predecessor (d0, u) chose pace v: d = d0 - sgn(v)  =>  d0 = d + sgn(v); cost dur(v)
        d0 = d + sgn(v)
        if abs(d0) > M:
            continue
        for u in prev[v]:
            if (d0, u) not in C:
                heapq.heappush(pq, (c + dur(v), d0, u))
    return C


def geo_field(tx, ty, blocked, asts):
    """8-connected BFS distance to the target over free cells. Each axis moves at most 1 cell per tick and
    diagonal steps are legal (collision is only checked at tick positions), so D8 is an admissible time bound."""
    xs = [a[0] for a in asts] + [0, tx]
    ys = [a[1] for a in asts] + [0, ty]
    x0, x1, y0, y1 = min(xs) - 6, max(xs) + 6, min(ys) - 6, max(ys) + 6
    D = {(tx, ty): 0}
    q = [(tx, ty)]
    for x, y in q:
        d = D[(x, y)] + 1
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (x + dx, y + dy)
                if n not in D and x0 <= n[0] <= x1 and y0 <= n[1] <= y1 and n not in blocked:
                    D[n] = d
                    q.append(n)
    return D


def plan(tx, ty, lim, blocked, C, w=1.0, D=None, max_pops=2_000_000):
    INF = 10 ** 9

    def h1(d, v, r):  # axis lower bound: finish current pace (r ticks, moves sgn(v)), then optimal
        return r + C.get((d - (sgn(v) if r else 0), v), INF) if r else C.get((d, v), INF)

    # boundary state: (x, y, vx, rx, vy, ry); r = remaining ticks of current pace (0 = choose next)
    start = (0, 0, 0, 0, 0, 0)
    g0 = 1  # every sequence starts with a 0 pace (1 tick, no move)
    best = {start: g0}
    parent = {start: None}
    pq = [(g0 + max(h1(tx, 0, 0), h1(ty, 0, 0)), g0, start)]
    pops = 0
    while pq:
        pops += 1
        if pops > max_pops:
            return None
        f, g, s = heapq.heappop(pq)
        if best.get(s, INF) < g:
            continue
        x, y, vx, rx, vy, ry = s
        if x == tx and y == ty and vx == 0 and vy == 0 and rx == 0 and ry == 0:
            return reconstruct(s, parent)
        px = nxt(vx) if rx == 0 else (vx,)
        py = nxt(vy) if ry == 0 else (vy,)
        for ax in px:
            nrx = dur(ax) if rx == 0 else rx
            for ay in py:
                nry = dur(ay) if ry == 0 else ry
                dt = nrx if nrx < nry else nry
                nx = x + (sgn(ax) if nrx == dt else 0)
                ny = y + (sgn(ay) if nry == dt else 0)
                if (nx, ny) in blocked:
                    continue
                ns = (nx, ny, ax, nrx - dt, ay, nry - dt)
                ng = g + dt
                hh = max(h1(tx - nx, ax, nrx - dt), h1(ty - ny, ay, nry - dt))
                if D is not None:
                    dg = D.get((nx, ny))
                    if dg is None:
                        continue  # cannot reach the target from here
                    if dg > hh:
                        hh = dg
                if ng + hh > lim:
                    continue
                if ng < best.get(ns, INF):
                    best[ns] = ng
                    parent[ns] = (s, ax if rx == 0 else None, ay if ry == 0 else None)
                    heapq.heappush(pq, (ng + w * hh, ng, ns))
    return None


def reconstruct(s, parent):
    xs, ys = [], []
    while parent[s] is not None:
        s, ax, ay = parent[s]
        if ax is not None:
            xs.append(ax)
        if ay is not None:
            ys.append(ay)
    return [0] + xs[::-1], [0] + ys[::-1]


def parse(data):
    lines = [l for l in data.strip().splitlines() if l.strip()]
    n = int(lines[0])
    cases, i = [], 1
    for _ in range(n):
        xy, lim = lines[i].split()
        tx, ty = map(int, xy.split(","))
        na = int(lines[i + 1])
        asts = [tuple(map(int, a.split(","))) for a in lines[i + 2].split()] if na else []
        cases.append((tx, ty, int(lim), asts))
        i += 3
    return cases


def blocked_set(asts):
    b = set()
    for ax, ay in asts:
        for dx in range(-AREA, AREA + 1):
            for dy in range(-AREA, AREA + 1):
                b.add((ax + dx, ay + dy))
    return b


_C = None


def _init(M):
    global _C
    _C = cost_to_go(M)


def solve_case(case):
    tx, ty, lim, asts = case
    b = blocked_set(asts)
    D = geo_field(tx, ty, b, asts)
    for w in (3.0, 2.0, 1.5, 1.2, 1.0):  # greedy weighted A* first (fast), closer to exact as fallback
        res = plan(tx, ty, lim, b, _C, w, D)
        if res:
            return res
    return None


def solve(data: str) -> str:
    cases = parse(data)
    M = max([abs(tx) + abs(ty) for tx, ty, _, _ in cases] + [10]) + 200
    if len(cases) > 4:
        import multiprocessing as mp
        with mp.Pool(min(len(cases), mp.cpu_count()), initializer=_init, initargs=(M,)) as pool:
            results = pool.map(solve_case, cases, chunksize=1)
    else:
        _init(M)
        results = [solve_case(c) for c in cases]
    out = []
    for i, res in enumerate(results):
        if not res:
            print(f"case {i}: no plan within {cases[i][2]}", file=sys.stderr)
            res = ([0], [0])
        xs, ys = res
        out.append(" ".join(map(str, xs)) + "\n" + " ".join(map(str, ys)) + "\n")
    return "\n".join(out)


# ---------------- validator (exact visualizer semantics)
def ticks(seq):
    out = []
    for p in seq:
        n = dur(p)
        out += [0] * (n - 1) + [sgn(p)]
    return out


def simulate(xs, ys):
    dx, dy = ticks(xs), ticks(ys)
    x = y = 0
    pos = [(0, 0)]
    for t in range(max(len(dx), len(dy))):
        x += dx[t] if t < len(dx) else 0
        y += dy[t] if t < len(dy) else 0
        pos.append((x, y))
    return pos


def check(data, out):
    cases = parse(data)
    outs = [o for o in out.strip().splitlines() if o.strip()]
    if len(outs) != 2 * len(cases):
        return False, f"{len(outs)} lines, want {2 * len(cases)}"
    for i, (tx, ty, lim, asts) in enumerate(cases):
        xs, ys = list(map(int, outs[2 * i].split())), list(map(int, outs[2 * i + 1].split()))
        for s in (xs, ys):
            if s[0] != 0 or s[-1] != 0:
                return False, f"case {i}: must start/end with 0"
            for a, b in zip(s, s[1:]):
                if b not in nxt(a):
                    return False, f"case {i}: bad step {a}->{b}"
        T = max(sum(map(dur, xs)), sum(map(dur, ys)))
        if T > lim:
            return False, f"case {i}: time {T} > {lim}"
        pos = simulate(xs, ys)
        if pos[-1] != (tx, ty):
            return False, f"case {i}: ends at {pos[-1]} not {(tx, ty)}"
        b = blocked_set(asts)
        if any(p in b for p in pos):
            return False, f"case {i}: collision"
    return True


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
