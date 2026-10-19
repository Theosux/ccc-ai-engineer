# ccc: pypy
import sys, pathlib, heapq
from collections import deque
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.runner import run_cases

ORDER = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]
IDX = {v: i for i, v in enumerate(ORDER)}
NEXT = {v: [ORDER[j] for j in (IDX[v] - 1, IDX[v], IDX[v] + 1) if 0 <= j < len(ORDER)] for v in ORDER}


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


def axis_opts(p, e):
    """(new_pace, new_el, dpos) options for one tick; e = ticks elapsed in pace p (0 = at boundary)"""
    if e == 0:
        res = []
        for q in NEXT[p]:
            d = abs(q) if q else 1
            if d == 1:
                res.append((q, 0, (1 if q > 0 else -1) if q else 0, q))
            else:
                res.append((q, 1, 0, q))
        return res
    d = abs(p)
    if e + 1 == d:
        return [(p, 0, 1 if p > 0 else -1, None)]
    return [(p, e + 1, 0, None)]


def solve_case(c):
    gx, gy, lim, asts = c
    xs = [a[0] for a in asts] + [0, gx]
    ys = [a[1] for a in asts] + [0, gy]
    M = 12
    x0, y0 = min(xs) - M, min(ys) - M
    W, H = max(xs) + M - x0 + 1, max(ys) + M - y0 + 1
    free = [True] * (W * H)
    for ax, ay in asts:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                free[(ax + dx - x0) * H + (ay + dy - y0)] = False
    INF = 1 << 30
    geo = [INF] * (W * H)
    gi = (gx - x0) * H + (gy - y0)
    geo[gi] = 0
    dq = deque([gi])
    while dq:
        i = dq.popleft()
        cx, cy = divmod(i, H)
        nd = geo[i] + 1
        for dx in (-1, 0, 1):
            nx = cx + dx
            if nx < 0 or nx >= W:
                continue
            for dy in (-1, 0, 1):
                ny = cy + dy
                if 0 <= ny < H:
                    j = nx * H + ny
                    if free[j] and geo[j] > nd:
                        geo[j] = nd
                        dq.append(j)
    sx, sy = -x0, -y0
    for w in (2.0, 1.5, 1.2, 1.0):
        r = astar(sx, sy, gx - x0, gy - y0, W, H, free, geo, w, lim)
        if r and max(ptime(r[0]), ptime(r[1])) <= lim:
            px, py = r
            return " ".join(map(str, px)) + "\n" + " ".join(map(str, py))
    raise AssertionError(f"no path within {lim} for goal {gx},{gy}")


def astar(sx, sy, tx, ty, W, H, free, geo, w, lim):
    start = (sx, sy, 0, 0, 0, 0)  # x, y, px, ex, py, ey   (after the initial 0 step, t=1)
    parent = {start: None}
    g = {start: 1}
    h0 = geo[sx * H + sy]
    heap = [(1 + w * h0, h0, 1, start)]
    while heap:
        f, h, t, s = heapq.heappop(heap)
        if g[s] != t:
            continue
        x, y, px, ex, py, ey = s
        if x == tx and y == ty and px == 0 and py == 0 and ex == 0 and ey == 0:
            # reconstruct emitted paces
            X, Y = [], []
            while s is not None:
                pr = parent[s]
                if pr is None:
                    break
                ps, qx, qy = pr
                if qx is not None:
                    X.append(qx)
                if qy is not None:
                    Y.append(qy)
                s = ps
            return [0] + X[::-1], [0] + Y[::-1]
        if t >= lim:
            continue
        ox = axis_opts(px, ex)
        oy = axis_opts(py, ey)
        nt = t + 1
        for npx, nex, dx, qx in ox:
            nx = x + dx
            if nx < 0 or nx >= W:
                continue
            for npy, ney, dy, qy in oy:
                ny = y + dy
                if ny < 0 or ny >= H:
                    continue
                j = nx * H + ny
                if not free[j]:
                    continue
                ns = (nx, ny, npx, nex, npy, ney)
                if g.get(ns, 1 << 30) <= nt:
                    continue
                hh = geo[j]
                if hh >= 1 << 30:
                    continue
                g[ns] = nt
                parent[ns] = (s, qx, qy)
                heapq.heappush(heap, (nt + w * hh, hh, nt, ns))
    return None


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
        bad = set()
        for ax, ay in asts:
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    bad.add((ax + dx, ay + dy))
        for p in tr:
            if p in bad:
                return False, f"case {i}: collision at {p}"
    return True


if __name__ == "__main__":
    run_cases(cases, solve_case, sep="\n\n")
