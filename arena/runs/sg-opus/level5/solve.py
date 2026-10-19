import sys
import numpy as np


def parse(data):
    d = list(map(int, data.split()))
    mp, mb, C, n = d[:4]
    p = d[4:4+n]
    m = d[4+n]
    t = [tuple(d[5+n+4*k:9+n+4*k]) for k in range(m)]
    return mp, mb, C, n, p, t


def greedy(mp, C, n, p, t, order):
    P = np.array(p, dtype=np.int64)
    cap = [mp] * n
    cnt = [0] * n
    alloc = {}
    bill = 0
    for k in order:
        tid, pw, s, e = t[k]
        idx = s + np.argsort(P[s:e+1], kind="stable")
        need = pw
        a = []
        for mi in idx.tolist():
            if cnt[mi] >= C or cap[mi] == 0:
                continue
            q = min(cap[mi], need)
            cap[mi] -= q; cnt[mi] += 1; need -= q
            a.append((mi, q)); bill += q * p[mi]
            if need == 0:
                break
        if need:
            return None, None
        alloc[tid] = a
    return alloc, bill


def solve(data):
    mp, mb, C, n, p, t = parse(data)
    m = len(t)
    orders = [
        sorted(range(m), key=lambda k: (t[k][3] - t[k][2], -t[k][1])),
        sorted(range(m), key=lambda k: -t[k][1]),
        sorted(range(m), key=lambda k: (t[k][3] - t[k][2]) / t[k][1]),
        sorted(range(m), key=lambda k: t[k][3]),
    ]
    best = None
    for o in orders:
        alloc, bill = greedy(mp, C, n, p, t, o)
        print("order bill", bill, mb, file=sys.stderr)
        if alloc is not None and (best is None or bill < best[1]):
            best = (alloc, bill)
    alloc = best[0]
    out = [str(m)]
    for tid, pw, s, e in t:
        out.append(f"{tid} " + " ".join(f"{a} {b}" for a, b in sorted(alloc[tid])))
    return "\n".join(out)


def check(data, out):
    mp, mb, C, n, p, t = parse(data)
    lines = out.strip().split("\n")
    if int(lines[0]) != len(t):
        return False, "count"
    use = [0] * n
    cnt = [0] * n
    bill = 0
    seen = set()
    td = {x[0]: x for x in t}
    for ln in lines[1:]:
        v = list(map(int, ln.split()))
        tid = v[0]
        if tid in seen or tid not in td:
            return False, "dup/unknown task"
        seen.add(tid)
        _, pw, s, e = td[tid]
        tot = 0; ms = set()
        for j in range(1, len(v), 2):
            mi, q = v[j], v[j+1]
            if not (s <= mi <= e) or q <= 0 or mi in ms:
                return False, f"bad minute {tid}"
            ms.add(mi)
            tot += q; use[mi] += q; cnt[mi] += 1; bill += q * p[mi]
        if tot != pw:
            return False, f"power {tid}"
    if len(seen) != len(t):
        return False, "missing"
    if max(use) > mp:
        return False, "maxpower"
    if max(cnt) > C:
        return False, "concurrency"
    if bill > mb:
        return False, f"bill {bill} > {mb}"
    return True, f"bill {bill}/{mb}"


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
