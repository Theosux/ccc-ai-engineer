import sys, heapq

def parse(data):
    d = data.split()
    mp = int(d[0]); mb = int(d[1]); mc = int(d[2]); n = int(d[3])
    p = list(map(int, d[4:4+n])); i = 4+n
    m = int(d[i]); i += 1
    tasks = []
    for _ in range(m):
        tasks.append(tuple(map(int, d[i:i+4]))); i += 4
    return mp, mb, mc, n, p, tasks

def f(p, u, mp):
    return p*u*(mp+u)/mp

def attempt(mp, mc, n, p, tasks, order, lam=0):
    use = [0]*n
    cnt = [0]*n
    res = {}
    for t, w, a, b in order:
        h = []
        for k in range(a, b+1):
            if use[k] < mp and cnt[k] < mc:
                h.append((f(p[k], use[k]+1, mp)-f(p[k], use[k], mp)+lam*p[k], k))
        heapq.heapify(h)
        mine = {}
        while w > 0:
            if not h: return None
            c, k = heapq.heappop(h)
            use[k] += 1; w -= 1
            if k not in mine: cnt[k] += 1
            mine[k] = mine.get(k, 0) + 1
            if use[k] < mp:
                heapq.heappush(h, (f(p[k], use[k]+1, mp)-f(p[k], use[k], mp), k))
        res[t] = mine
    return res

def bill(mp, n, p, res):
    use = [0]*n
    for mine in res.values():
        for k, x in mine.items(): use[k] += x
    return sum(-(-p[k]*u*(mp+u)//mp) for k, u in enumerate(use) if u)

def solve(data):
    mp, mb, mc, n, p, tasks = parse(data)
    orders = [sorted(tasks, key=lambda t: (t[3]-t[2], t[0])),
              sorted(tasks, key=lambda t: (t[3]-t[2])/max(1, t[1]))]
    best = None
    for lam in (0, 0.1, 0.3, 1, 3, 10, 100):
        for order in orders:
            res = attempt(mp, mc, n, p, tasks, order, lam)
            if res is None: continue
            b = bill(mp, n, p, res)
            if best is None or b < best[0]: best = (b, res)
        if best and best[0] <= mb: break
    res = best[1]
    out = [str(len(tasks))]
    for t, w, a, b in tasks:
        out.append(str(t) + " " + " ".join(f"{k} {x}" for k, x in res[t].items()))
    return "\n".join(out)

def check(data, out):
    mp, mb, mc, n, p, tasks = parse(data)
    L = [l for l in out.split("\n") if l.strip()]
    if int(L[0]) != len(tasks) or len(L) != len(tasks)+1: return False, "count"
    use = [0]*n; cnt = [0]*n
    for (t, w, a, b), l in zip(tasks, L[1:]):
        v = list(map(int, l.split()))
        if v[0] != t: return False, "id"
        s = 0; seen = set()
        for k, x in zip(v[1::2], v[2::2]):
            if k in seen or not (a <= k <= b) or x <= 0: return False, f"bad {t}"
            seen.add(k); s += x; use[k] += x; cnt[k] += 1
        if s != w: return False, f"sum {t}"
    if max(use) > mp: return False, "cap"
    if max(cnt) > mc: return False, "conc"
    bill = 0; bill_r = 0
    for k in range(n):
        u = use[k]
        if u:
            bill += -(-p[k]*u*(mp+u)//mp)
            bill_r += (2*p[k]*u*(mp+u)+mp)//(2*mp)
    if bill > mb: return False, f"bill {bill}>{mb}"
    return True, f"bill ceil {bill} round {bill_r} /{mb}"

if __name__ == "__main__":
    print(solve(sys.stdin.read()))
