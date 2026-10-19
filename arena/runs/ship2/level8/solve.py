# ccc: pypy
import sys, pathlib, heapq
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.runner import run_cases

ORDER = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]
IDX = {v: i for i, v in enumerate(ORDER)}
NEXT = {v: [ORDER[j] for j in (IDX[v] - 1, IDX[v], IDX[v] + 1) if 0 <= j < len(ORDER)] for v in ORDER}
K = 1 << 12
OFF = 2048


def ptime(p):
    return sum(abs(x) if x else 1 for x in p)


def valid_moves(p):
    return p[0] == 0 and p[-1] == 0 and all(abs(IDX[a] - IDX[b]) <= 1 for a, b in zip(p, p[1:]))


def ticks(p):
    pos, out = 0, [0]
    for v in p:
        if v == 0:
            out.append(pos)
        else:
            out.extend([pos] * (abs(v) - 1))
            pos += 1 if v > 0 else -1
            out.append(pos)
    return out


def trace(px, py):
    tx, ty = ticks(px), ticks(py)
    n = max(len(tx), len(ty))
    tx += [tx[-1]] * (n - len(tx))
    ty += [ty[-1]] * (n - len(ty))
    return list(zip(tx, ty))


def step(p0, v, t):
    if v == 0:
        return p0
    return p0 + (t // v if v > 0 else -(t // -v))


class Field:
    def __init__(self, asts):
        self.asts = asts
        self.cache = {}

    def blocked(self, t):
        b = self.cache.get(t)
        if b is None:
            b = set()
            for ax, ay, vx, vy in self.asts:
                cx, cy = step(ax, vx, t), step(ay, vy, t)
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        b.add((cx + dx + OFF) * K + cy + dy + OFF)
            self.cache[t] = b
        return b


def axis_opts(p, e):
    if e == 0:
        res = []
        for q in NEXT[p]:
            d = abs(q) if q else 1
            if d == 1:
                res.append((q, 0, (1 if q > 0 else -1) if q else 0, q))
            else:
                res.append((q, 1, 0, q))
        return res
    if e + 1 == abs(p):
        return [(p, 0, 1 if p > 0 else -1, None)]
    return [(p, e + 1, 0, None)]


def astar(gx, gy, lim, field, w, timed):
    start = (0, 0, 0, 0, 0, 0)
    if (OFF * K + OFF) in field.blocked(0) or (OFF * K + OFF) in field.blocked(1):
        return None
    key0 = (start, 1) if timed else start
    parent = {key0: None}
    g = {key0: 1}
    h0 = max(abs(gx), abs(gy))
    heap = [(1 + w * h0, h0, 1, start)]
    pops = 0
    closed = set()
    while heap:
        f, h, t, s = heapq.heappop(heap)
        key = (s, t) if timed else s
        if g[key] != t or key in closed:
            continue
        closed.add(key)
        pops += 1
        if pops > 400000:
            return None
        x, y, px, ex, py, ey = s
        if x == gx and y == gy and px == 0 and py == 0 and ex == 0 and ey == 0:
            X, Y = [], []
            k = key
            while True:
                pr = parent[k]
                if pr is None:
                    break
                k, qx, qy = pr
                if qx is not None:
                    X.append(qx)
                if qy is not None:
                    Y.append(qy)
            return [0] + X[::-1], [0] + Y[::-1]
        if t >= lim:
            continue
        nt = t + 1
        bl = field.blocked(nt)
        for npx, nex, dx, qx in axis_opts(px, ex):
            nx = x + dx
            for npy, ney, dy, qy in axis_opts(py, ey):
                ny = y + dy
                if (nx + OFF) * K + ny + OFF in bl:
                    continue
                ns = (nx, ny, npx, nex, npy, ney)
                nk = (ns, nt) if timed else ns
                if nk in closed or g.get(nk, 1 << 30) <= nt:
                    continue
                hh = max(abs(gx - nx), abs(gy - ny))
                if nt + hh > lim:
                    continue
                g[nk] = nt
                parent[nk] = (key, qx, qy)
                heapq.heappush(heap, (nt + w * hh, hh, nt, ns))
    return None


def solve_case(c):
    gx, gy, lim, asts = c
    field = Field(asts)
    for timed in (False, True):
        for w in (2.0, 1.5, 1.2):
            r = astar(gx, gy, lim, field, w, timed)
            if r and max(ptime(r[0]), ptime(r[1])) <= lim:
                px, py = r
                return " ".join(map(str, px)) + "\n" + " ".join(map(str, py))
    raise AssertionError(f"no path within {lim} for goal {gx},{gy}")


def parse(data):
    d = data.split("\n")
    n = int(d[0])
    cs = []
    for i in range(n):
        xy, lim = d[3 * i + 1].split()
        x, y = map(int, xy.split(","))
        a = int(d[3 * i + 2])
        asts = [tuple(map(int, s.split(","))) for s in d[3 * i + 3].split()][:a]
        cs.append((x, y, int(lim), asts))
    return cs


def cases(data):
    return parse(data)


def check(data, out):
    cs = parse(data)
    o = [l for l in out.strip().split("\n") if l.strip()]
    if len(o) != 2 * len(cs):
        return False, "line count"
    for i, (x, y, lim, asts) in enumerate(cs):
        px = list(map(int, o[2 * i].split()))
        py = list(map(int, o[2 * i + 1].split()))
        if not (valid_moves(px) and valid_moves(py)):
            return False, f"case {i}: bad pace change"
        tr = trace(px, py)
        if tr[-1] != (x, y):
            return False, f"case {i}: end {tr[-1]} != {(x, y)}"
        if max(ptime(px), ptime(py)) > lim:
            return False, f"case {i}: time {max(ptime(px), ptime(py))} > {lim}"
        for t, (sx, sy) in enumerate(tr):
            for ax, ay, vx, vy in asts:
                if abs(sx - step(ax, vx, t)) <= 2 and abs(sy - step(ay, vy, t)) <= 2:
                    return False, f"case {i}: collision t={t} at {(sx, sy)}"
    return True


if __name__ == "__main__":
    run_cases(cases, solve_case, sep="\n\n")
