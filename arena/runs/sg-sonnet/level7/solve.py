import sys, heapq

def parse(data):
    d = data.split()
    mp = int(d[0]); mb = int(d[1]); mc = int(d[2]); n = int(d[3])
    p = list(map(int, d[4:4+n])); i = 4+n
    H = int(d[i]); i += 1
    houses = []
    for _ in range(H):
        m = int(d[i]); i += 1
        ts = []
        for _ in range(m):
            ts.append(tuple(map(int, d[i:i+4]))); i += 4
        houses.append(ts)
    return mp, mb, mc, n, p, houses

def f(p, u, mp):
    return p*u*(mp+u)/mp

def attempt(mp, mc, n, p, houses, order, lam=0):
    H = len(houses)
    gu = [0]*n
    hu = [[0]*n for _ in range(H)]
    hc = [[0]*n for _ in range(H)]
    res = {}
    for hi, (t, w, a, b) in order:
        U = hu[hi]; C = hc[hi]
        h = []
        for k in range(a, b+1):
            if U[k] < mp and C[k] < mc:
                h.append((f(p[k], gu[k]+1, mp)-f(p[k], gu[k], mp)+lam*p[k], k))
        heapq.heapify(h)
        mine = {}
        while w > 0:
            if not h: return None
            c, k = heapq.heappop(h)
            gu[k] += 1; U[k] += 1; w -= 1
            if k not in mine: C[k] += 1
            mine[k] = mine.get(k, 0) + 1
            if U[k] < mp:
                heapq.heappush(h, (f(p[k], gu[k]+1, mp)-f(p[k], gu[k], mp), k))
        res[(hi, t)] = mine
    return res, gu

def bill_of(mp, p, gu):
    return sum(-(-p[k]*u*(mp+u)//mp) for k, u in enumerate(gu) if u)

def solve(data):
    mp, mb, mc, n, p, houses = parse(data)
    flat = [(hi, t) for hi, ts in enumerate(houses) for t in ts]
    orders = [sorted(flat, key=lambda x: (x[1][3]-x[1][2], x[0], x[1][0])),
              sorted(flat, key=lambda x: (x[1][3]-x[1][2])/max(1, x[1][1]))]
    best = None
    for lam in (0, 0.1, 0.3, 1, 3, 10, 100):
        for order in orders:
            r = attempt(mp, mc, n, p, houses, order, lam)
            if r is None: continue
            res, gu = r
            b = bill_of(mp, p, gu)
            if best is None or b < best[0]: best = (b, res)
        if best and best[0] <= mb: break
    res = best[1]
    out = [str(len(houses))]
    for hi, ts in enumerate(houses):
        out.append(str(hi+1)); out.append(str(len(ts)))
        for t, w, a, b in ts:
            out.append(str(t) + " " + " ".join(f"{k} {x}" for k, x in res[(hi, t)].items()))
    return "\n".join(out)

def check(data, out):
    mp, mb, mc, n, p, houses = parse(data)
    L = [l for l in out.split("\n") if l.strip()]
    pos = 0
    if int(L[0]) != len(houses): return False, "H"
    pos = 1
    gu = [0]*n
    for hi, ts in enumerate(houses):
        if int(L[pos]) != hi+1 or int(L[pos+1]) != len(ts): return False, "hdr"
        pos += 2
        U = [0]*n; C = [0]*n
        for (t, w, a, b) in ts:
            v = list(map(int, L[pos].split())); pos += 1
            if v[0] != t: return False, "id"
            s = 0; seen = set()
            for k, x in zip(v[1::2], v[2::2]):
                if k in seen or not (a <= k <= b) or x <= 0: return False, f"bad {hi} {t}"
                seen.add(k); s += x; U[k] += x; C[k] += 1; gu[k] += x
            if s != w: return False, f"sum {t}"
        if max(U) > mp: return False, "cap"
        if max(C) > mc: return False, "conc"
    bill = bill_of(mp, p, gu)
    if bill > mb: return False, f"bill {bill}>{mb}"
    return True, f"bill {bill}/{mb}"

if __name__ == "__main__":
    print(solve(sys.stdin.read()))
