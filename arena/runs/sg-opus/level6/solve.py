import sys, heapq
import numpy as np


def parse(data):
    d = list(map(int, data.split()))
    mp, mb, C, n = d[:4]
    p = d[4:4+n]
    m = d[4+n]
    t = [tuple(d[5+n+4*k:9+n+4*k]) for k in range(m)]
    return mp, mb, C, n, p, t


def mcost(price, u, mp):
    # ceil(u * price * (1 + u/mp))
    return -((-u * price * (mp + u)) // mp)


def greedy(mp, C, n, p, t, order, K):
    P = np.array(p, dtype=np.float64)
    use = np.zeros(n, dtype=np.int64)
    cnt = np.zeros(n, dtype=np.int64)
    alloc = {}
    for k in order:
        tid, pw, s, e = t[k]
        u = use[s:e+1]
        mc = P[s:e+1] * (mp + 2 * u + 1)
        mc[(cnt[s:e+1] >= C) | (u >= mp)] = np.inf
        kk = min(K, len(mc))
        cand = np.argpartition(mc, kk - 1)[:kk] if kk < len(mc) else np.arange(len(mc))
        cand = [int(c) + s for c in cand if np.isfinite(mc[c])]
        h = [(p[c] * (mp + 2 * int(use[c]) + 1), c) for c in cand]
        heapq.heapify(h)
        need = pw
        a = {}
        refilled = False
        while need:
            if not h:
                if refilled:
                    print("fail task", tid, pw, s, e, "need", need, file=sys.stderr)
                    return None
                refilled = True
                h = [(p[c] * (mp + 2 * int(use[c]) + 1), c) for c in range(s, e + 1)
                     if c not in a and cnt[c] < C and use[c] < mp]
                heapq.heapify(h)
                continue
            v, c = heapq.heappop(h)
            use[c] += 1
            a[c] = a.get(c, 0) + 1
            need -= 1
            if use[c] < mp:
                heapq.heappush(h, (p[c] * (mp + 2 * int(use[c]) + 1), c))
        for c in a:
            cnt[c] += 1
        alloc[tid] = sorted(a.items())
    return alloc


def bill_of(mp, n, p, t, alloc):
    use = [0] * n
    for tid in alloc:
        for c, q in alloc[tid]:
            use[c] += q
    return sum(mcost(p[i], use[i], mp) for i in range(n) if use[i])


def solve(data):
    mp, mb, C, n, p, t = parse(data)
    m = len(t)
    orders = [
        sorted(range(m), key=lambda k: (t[k][3] - t[k][2], -t[k][1])),
        sorted(range(m), key=lambda k: (t[k][3] - t[k][2]) / t[k][1]),
        sorted(range(m), key=lambda k: -t[k][1]),
    ]
    best = None
    for o in orders:
        for K in (C * 4, 64):
            alloc = greedy(mp, C, n, p, t, o, K)
            if alloc is None:
                print("fail", file=sys.stderr)
                continue
            b = bill_of(mp, n, p, t, alloc)
            print("bill", b, mb, file=sys.stderr)
            if best is None or b < best[1]:
                best = (alloc, b)
    alloc = best[0]
    out = [str(m)]
    for tid, pw, s, e in t:
        out.append(f"{tid} " + " ".join(f"{a} {b}" for a, b in alloc[tid]))
    return "\n".join(out)


def check(data, out):
    mp, mb, C, n, p, t = parse(data)
    lines = out.strip().split("\n")
    if int(lines[0]) != len(t):
        return False, "count"
    use = [0] * n
    cnt = [0] * n
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
            tot += q; use[mi] += q; cnt[mi] += 1
        if tot != pw:
            return False, f"power {tid}"
    if len(seen) != len(t):
        return False, "missing"
    if max(use) > mp:
        return False, "maxpower"
    if max(cnt) > C:
        return False, "concurrency"
    bill = sum(mcost(p[i], use[i], mp) for i in range(n) if use[i])
    if bill > mb:
        return False, f"bill {bill} > {mb}"
    return True, f"bill {bill}/{mb}"


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
