# ccc: pypy
import sys
import heapq

AREA = 2  # collision if |dx| <= 2 and |dy| <= 2 at any tick (visualizer hasShipCollided)
PACES = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]


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


def cost_to_go(M):
    """C[(d, v)]: min ticks from a pace boundary (offset d = target - pos, last pace v) to standing at the
    target after a completed 0 pace (obstacle-free). Reverse Dijkstra over the 1-D pace graph."""
    C = {}
    pq = [(0, 0, 0)]
    prev = {v: [u for u in PACES if v in nxt(u)] for v in PACES}
    while pq:
        c, d, v = heapq.heappop(pq)
        if (d, v) in C:
            continue
        C[(d, v)] = c
        d0 = d + sgn(v)
        if abs(d0) > M:
            continue
        for u in prev[v]:
            if (d0, u) not in C:
                heapq.heappush(pq, (c + dur(v), d0, u))
    return C


def ast_pos(a, t):
    """Visualizer applyStepIndexEntity: p = p0 + trunc(t / v) per axis (v = pace; 0 = static)."""
    x, y, vx, vy = a
    return (x + (int(t / vx) if vx else 0), y + (int(t / vy) if vy else 0))


class Field:
    """Lazily cached per-tick asteroid cells; collision = any asteroid within the 5x5 box."""

    def __init__(self, asts):
        self.asts = asts
        self.cache = {}

    def at(self, t):
        s = self.cache.get(t)
        if s is None:
            s = set()
            for a in self.asts:
                s.add(ast_pos(a, t))
            self.cache[t] = s
        return s

    def hit(self, x, y, t):
        s = self.at(t)
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                if (x + dx, y + dy) in s:
                    return True
        return False


def plan(tx, ty, lim, F, C, w=1.0, max_pops=1_500_000):
    INF = 10 ** 9

    def h1(d, v, r):
        return r + C.get((d - (sgn(v) if r else 0), v), INF) if r else C.get((d, v), INF)

    if F.hit(0, 0, 0) or F.hit(0, 0, 1):
        return None
    start = (0, 0, 0, 0, 0, 0)
    g0 = 1  # the first pace of each sequence is 0 (1 tick)
    best = {(start, g0): g0}
    parent = {(start, g0): None}
    pq = [(g0 + max(h1(tx, 0, 0), h1(ty, 0, 0)), g0, start)]
    seen = set()
    pops = 0
    while pq:
        f, g, s = heapq.heappop(pq)
        if (s, g) in seen:
            continue
        seen.add((s, g))
        pops += 1
        if pops > max_pops:
            return None
        x, y, vx, rx, vy, ry = s
        if x == tx and y == ty and vx == 0 and vy == 0 and rx == 0 and ry == 0:
            return reconstruct((s, g), parent)
        px = nxt(vx) if rx == 0 else (vx,)
        py = nxt(vy) if ry == 0 else (vy,)
        for ax in px:
            nrx = dur(ax) if rx == 0 else rx
            for ay in py:
                nry = dur(ay) if ry == 0 else ry
                dt = nrx if nrx < nry else nry
                nx = x + (sgn(ax) if nrx == dt else 0)
                ny = y + (sgn(ay) if nry == dt else 0)
                ng = g + dt
                hh = max(h1(tx - nx, ax, nrx - dt), h1(ty - ny, ay, nry - dt))
                if ng + hh > lim:
                    continue
                # ship holds (x, y) during ticks g+1 .. ng-1, is at (nx, ny) at tick ng
                bad = False
                for t in range(g + 1, ng):
                    if F.hit(x, y, t):
                        bad = True
                        break
                if bad or F.hit(nx, ny, ng):
                    continue
                ns = (nx, ny, ax, nrx - dt, ay, nry - dt)
                key = (ns, ng)
                if key not in parent:
                    parent[key] = ((s, g), ax if rx == 0 else None, ay if ry == 0 else None)
                    heapq.heappush(pq, (ng + w * hh, ng, ns))
    return None


def reconstruct(k, parent):
    xs, ys = [], []
    while parent[k] is not None:
        k, ax, ay = parent[k]
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


_C = None


def _init(M):
    global _C
    _C = cost_to_go(M)


def solve_case(case):
    tx, ty, lim, asts = case
    F = Field(asts)
    for w in (2.0, 1.5, 1.2, 1.0):
        res = plan(tx, ty, lim, F, _C, w)
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
        out += [0] * (dur(p) - 1) + [sgn(p)]
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
        for t, (px, py) in enumerate(pos):
            for a in asts:
                ax, ay = ast_pos(a, t)
                if abs(px - ax) <= AREA and abs(py - ay) <= AREA:
                    return False, f"case {i}: collision at tick {t} with asteroid {a}"
    return True


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
