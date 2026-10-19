import sys

def parse(data):
    d = data.split()
    mp = int(d[0]); mb = int(d[1]); mc = int(d[2]); n = int(d[3])
    p = list(map(int, d[4:4+n])); i = 4+n
    m = int(d[i]); i += 1
    tasks = []
    for _ in range(m):
        tasks.append(tuple(map(int, d[i:i+4]))); i += 4
    return mp, mb, mc, n, p, tasks

def attempt(mp, mc, n, p, tasks, order):
    cap = [mp]*n
    cnt = [0]*n
    res = {}
    for t, w, a, b in order:
        mins = sorted(range(a, b+1), key=lambda k: (p[k], k))
        parts = []
        for k in mins:
            if w == 0: break
            if cnt[k] >= mc: continue
            x = min(w, cap[k])
            if x > 0:
                cap[k] -= x; w -= x; cnt[k] += 1; parts.append((k, x))
        if w > 0: return None
        res[t] = parts
    return res

def solve(data):
    mp, mb, mc, n, p, tasks = parse(data)
    order = sorted(tasks, key=lambda t: (t[3]-t[2], t[0]))
    res = attempt(mp, mc, n, p, tasks, order)
    if res is None:
        order = sorted(tasks, key=lambda t: (t[3]-t[2])/max(1, t[1]))
        res = attempt(mp, mc, n, p, tasks, order)
    out = [str(len(tasks))]
    for t, w, a, b in tasks:
        out.append(str(t) + " " + " ".join(f"{k} {x}" for k, x in res[t]))
    return "\n".join(out)

def check(data, out):
    mp, mb, mc, n, p, tasks = parse(data)
    L = [l for l in out.split("\n") if l.strip()]
    if int(L[0]) != len(tasks) or len(L) != len(tasks)+1: return False, "count"
    use = [0]*n; cnt = [0]*n; bill = 0
    for (t, w, a, b), l in zip(tasks, L[1:]):
        v = list(map(int, l.split()))
        if v[0] != t: return False, "id"
        s = 0; seen = set()
        for k, x in zip(v[1::2], v[2::2]):
            if k in seen or not (a <= k <= b) or x <= 0: return False, f"bad {t}"
            seen.add(k); s += x; use[k] += x; cnt[k] += 1; bill += x*p[k]
        if s != w: return False, f"sum {t}"
    if max(use) > mp: return False, "cap"
    if max(cnt) > mc: return False, "conc"
    if bill > mb: return False, f"bill {bill}>{mb}"
    return True, f"bill {bill}/{mb}"

if __name__ == "__main__":
    print(solve(sys.stdin.read()))
