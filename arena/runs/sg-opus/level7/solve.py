import sys, heapq, random
import numpy as np


def parse(data):
    d = list(map(int, data.split()))
    mp, mb, C, n = d[:4]
    i = 4
    p = d[i:i+n]; i += n
    H = d[i]; i += 1
    houses = []
    for _ in range(H):
        m = d[i]; i += 1
        t = [tuple(d[i+4*k:i+4*k+4]) for k in range(m)]
        i += 4 * m
        houses.append(t)
    return mp, mb, C, n, p, houses


def mcost(price, u, mp):
    return -((-u * price * (mp + u)) // mp)


def greedy(mp, C, n, p, houses, order, K):
    P = np.array(p, dtype=np.float64)
    G = np.zeros(n, dtype=np.int64)
    use = [np.zeros(n, dtype=np.int64) for _ in houses]
    cnt = [np.zeros(n, dtype=np.int64) for _ in houses]
    alloc = {}
    for (h, k) in order:
        tid, pw, s, e = houses[h][k]
        uh = use[h]; ch = cnt[h]
        mc = P[s:e+1] * (mp + 2 * G[s:e+1] + 1)
        mc[(ch[s:e+1] >= C) | (uh[s:e+1] >= mp)] = np.inf
        kk = min(K, len(mc))
        cand = np.argpartition(mc, kk - 1)[:kk] if kk < len(mc) else np.arange(len(mc))
        cand = [int(c) + s for c in cand if np.isfinite(mc[c])]
        hp = [(p[c] * (mp + 2 * int(G[c]) + 1), c) for c in cand]
        heapq.heapify(hp)
        need = pw
        a = {}
        refilled = False
        while need:
            if not hp:
                if refilled:
                    return None
                refilled = True
                hp = [(p[c] * (mp + 2 * int(G[c]) + 1), c) for c in range(s, e + 1)
                      if c not in a and ch[c] < C and uh[c] < mp]
                heapq.heapify(hp)
                continue
            v, c = heapq.heappop(hp)
            cur = p[c] * (mp + 2 * int(G[c]) + 1)
            if cur != v:  # stale (global usage changed) -> reinsert
                heapq.heappush(hp, (cur, c))
                continue
            uh[c] += 1; G[c] += 1
            a[c] = a.get(c, 0) + 1
            need -= 1
            if uh[c] < mp:
                heapq.heappush(hp, (p[c] * (mp + 2 * int(G[c]) + 1), c))
        for c in a:
            ch[c] += 1
        alloc[(h, tid)] = sorted(a.items())
    return alloc, G


def solve(data):
    mp, mb, C, n, p, houses = parse(data)
    allt = [(h, k) for h in range(len(houses)) for k in range(len(houses[h]))]
    T = lambda hk: houses[hk[0]][hk[1]]
    orders = [
        sorted(allt, key=lambda hk: (T(hk)[3] - T(hk)[2], -T(hk)[1])),
        sorted(allt, key=lambda hk: (T(hk)[3] - T(hk)[2]) / T(hk)[1]),
        sorted(allt, key=lambda hk: -T(hk)[1]),
    ]
    rng = random.Random(1)
    for _ in range(4):
        o = orders[1][:]
        o.sort(key=lambda hk: (T(hk)[3] - T(hk)[2]) / T(hk)[1] * rng.uniform(0.7, 1.3))
        orders.append(o)
    best = None
    for o in orders:
        for K in (C * 4, 64):
            r = greedy(mp, C, n, p, houses, o, K)
            if r is None:
                print("fail", file=sys.stderr)
                continue
            alloc, G = r
            b = sum(mcost(p[i], int(G[i]), mp) for i in range(n) if G[i])
            print("bill", b, mb, file=sys.stderr)
            if best is None or b < best[1]:
                best = (alloc, b)
        if best is not None and best[1] <= mb * 0.97:
            break
    alloc = best[0]
    out = [str(len(houses))]
    for h, t in enumerate(houses):
        out.append(str(h + 1))
        out.append(str(len(t)))
        for tid, pw, s, e in t:
            out.append(f"{tid} " + " ".join(f"{a} {b}" for a, b in alloc[(h, tid)]))
    return "\n".join(out)


def check(data, out):
    mp, mb, C, n, p, houses = parse(data)
    v = list(map(int, out.split()))
    lines = [list(map(int, l.split())) for l in out.strip().split("\n")]
    li = 0
    if lines[li][0] != len(houses):
        return False, "H"
    li += 1
    G = [0] * n
    seenh = set()
    for _ in range(len(houses)):
        hid = lines[li][0]; li += 1
        if hid in seenh or not (1 <= hid <= len(houses)):
            return False, "house id"
        seenh.add(hid)
        t = houses[hid - 1]
        m = lines[li][0]; li += 1
        if m != len(t):
            return False, "task count"
        td = {x[0]: x for x in t}
        use = [0] * n; cnt = [0] * n
        seen = set()
        for _ in range(m):
            vv = lines[li]; li += 1
            tid = vv[0]
            if tid in seen or tid not in td:
                return False, "dup/unknown task"
            seen.add(tid)
            _, pw, s, e = td[tid]
            tot = 0; ms = set()
            for j in range(1, len(vv), 2):
                mi, q = vv[j], vv[j+1]
                if not (s <= mi <= e) or q <= 0 or mi in ms:
                    return False, f"bad minute h{hid} t{tid}"
                ms.add(mi)
                tot += q; use[mi] += q; cnt[mi] += 1; G[mi] += q
            if tot != pw:
                return False, f"power h{hid} t{tid}"
        if max(use) > mp:
            return False, "maxpower"
        if max(cnt) > C:
            return False, "concurrency"
    if li != len(lines):
        return False, "trailing lines"
    bill = sum(mcost(p[i], G[i], mp) for i in range(n) if G[i])
    if bill > mb:
        return False, f"bill {bill} > {mb}"
    return True, f"bill {bill}/{mb}"


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
