import sys


def seq(x):
    if x == 0:
        return [0]
    s = 1 if x > 0 else -1
    a = abs(x)
    best = None
    for p in range(5, 0, -1):
        need = 11 - 2 * p
        if a < need:
            continue
        body = list(range(5, p - 1, -1)) + [p] * (a - need) + list(range(p + 1, 6))
        t = sum(body)
        if best is None or t < best[0]:
            best = (t, body)
    return [0] + [s * v for v in best[1]] + [0]


def ptime(p):
    return sum(abs(x) if x else 1 for x in p)


ORDER = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]
IDX = {v: i for i, v in enumerate(ORDER)}


def valid_moves(p):
    return p[0] == 0 and p[-1] == 0 and all(abs(IDX[a] - IDX[b]) <= 1 for a, b in zip(p, p[1:]))


def ticks(p):
    """position after each tick (index 0 = start)"""
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


def hits(tr, asts):
    return any(abs(x - ax) <= 2 and abs(y - ay) <= 2 for x, y in tr for ax, ay in asts)


def build(waypoints):
    """axis-aligned legs through waypoints; one axis moves while the other holds 0"""
    px, py = [], []
    cx, cy = 0, 0
    for wx, wy in waypoints:
        if wx != cx:
            s = seq(wx - cx)
            px += s
            py += [0] * ptime(s)
            cx = wx
        if wy != cy:
            s = seq(wy - cy)
            py += s
            px += [0] * ptime(s)
            cy = wy
    return px or [0], py or [0]


def solve_case(gx, gy, lim, asts):
    cands = [[(gx, 0), (gx, gy)], [(0, gy), (gx, gy)]]
    for d in range(-15, 16):
        cands.append([(0, d), (gx, d), (gx, gy)])
        cands.append([(d, 0), (d, gy), (gx, gy)])
    best = None
    for wp in cands:
        px, py = build(wp)
        t = max(ptime(px), ptime(py))
        if t > lim or (best and t >= best[0]):
            continue
        if hits(trace(px, py), asts):
            continue
        best = (t, px, py)
    assert best, (gx, gy, lim, asts)
    return best[1], best[2]


def parse(data):
    d = data.split("\n")
    n = int(d[0])
    cs = []
    for i in range(n):
        xy, lim = d[2 * i + 1].split()
        x, y = map(int, xy.split(","))
        ax, ay = map(int, d[2 * i + 2].split(","))
        cs.append((x, y, int(lim), [(ax, ay)]))
    return cs


def check(data, out):
    cs = parse(data)
    o = [l for l in out.strip().split("\n") if l.strip()]
    if len(o) != 2 * len(cs):
        return False, "line count"
    for i, (x, y, lim, asts) in enumerate(cs):
        px = list(map(int, o[2 * i].split()))
        py = list(map(int, o[2 * i + 1].split()))
        tr = trace(px, py)
        if not (valid_moves(px) and valid_moves(py)):
            return False, f"case {i}: bad pace change"
        if tr[-1] != (x, y):
            return False, f"case {i}: end {tr[-1]} != {(x, y)}"
        if max(ptime(px), ptime(py)) > lim:
            return False, f"case {i}: time"
        if hits(tr, asts):
            return False, f"case {i}: collision"
    return True


if __name__ == "__main__":
    cs = parse(sys.stdin.read())
    res = []
    for x, y, lim, asts in cs:
        px, py = solve_case(x, y, lim, asts)
        res.append(" ".join(map(str, px)) + "\n" + " ".join(map(str, py)))
    print("\n\n".join(res))
