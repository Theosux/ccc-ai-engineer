import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.runner import run_cases


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


def try_assign(gA, aA, gB, aB, lim):
    """A: [0]*w0 + seq(gA); B: seq(d1) + [0]*w1 + seq(gB - d1). Returns (pA, pB) or None."""
    sA = seq(gA)
    tA = ticks(sA)
    insA = [i for i, v in enumerate(tA) if abs(v - aA) <= 2]
    lenA = ptime(sA)
    if lenA > lim:
        return None
    for d1 in sorted(range(-10, 11), key=abs):
        for w1 in range(0, lim):
            pB = (seq(d1) if d1 else []) + [0] * w1 + seq(gB - d1)
            if ptime(pB) > lim:
                break
            if not valid_moves(pB):
                continue
            tB = ticks(pB)
            tB += [tB[-1]] * (lim + 2 - len(tB))
            pre = [0]
            for v in tB:
                pre.append(pre[-1] + (abs(v - aB) <= 2))
            for w0 in range(0, lim - lenA + 1):
                if insA:
                    lo = 0 if insA[0] == 0 else insA[0] + w0
                    hi = lim + 1 if insA[-1] == len(tA) - 1 else insA[-1] + w0
                    if pre[hi + 1] - pre[lo]:
                        continue
                return [0] * w0 + sA, pB
    return None


def solve_case(c):
    gx, gy, lim, asts = c
    (ax, ay), = asts
    r = try_assign(gx, ax, gy, ay, lim)
    if r:
        px, py = r
    else:
        r = try_assign(gy, ay, gx, ax, lim)
        assert r, c
        py, px = r
    return " ".join(map(str, px)) + "\n" + " ".join(map(str, py))


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
        tr = trace(px, py)
        if not (valid_moves(px) and valid_moves(py)):
            return False, f"case {i}: bad pace change"
        if tr[-1] != (x, y):
            return False, f"case {i}: end {tr[-1]} != {(x, y)}"
        if max(ptime(px), ptime(py)) > lim:
            return False, f"case {i}: time {max(ptime(px), ptime(py))} > {lim}"
        if hits(tr, asts):
            return False, f"case {i}: collision"
    return True


if __name__ == "__main__":
    run_cases(cases, solve_case, sep="\n\n")
