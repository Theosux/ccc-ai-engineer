import sys

def parse(data):
    d = data.split()
    mp = int(d[0]); mb = int(d[1]); n = int(d[2])
    p = list(map(int, d[3:3+n])); i = 3+n
    m = int(d[i]); i += 1
    tasks = []
    for _ in range(m):
        tasks.append(tuple(map(int, d[i:i+4]))); i += 4
    return mp, mb, n, p, tasks

def solve(data):
    mp, mb, n, p, tasks = parse(data)
    cap = [mp]*n
    order = sorted(tasks, key=lambda t: (t[3]-t[2], t[0]))
    res = {}
    for t, w, a, b in order:
        mins = sorted(range(a, b+1), key=lambda k: (p[k], k))
        parts = []
        for k in mins:
            if w == 0: break
            x = min(w, cap[k])
            if x > 0:
                cap[k] -= x; w -= x; parts.append((k, x))
        res[t] = parts
    out = [str(len(tasks))]
    for t, w, a, b in tasks:
        out.append(str(t) + " " + " ".join(f"{k} {x}" for k, x in res[t]))
    return "\n".join(out)

def check(data, out):
    mp, mb, n, p, tasks = parse(data)
    L = out.split("\n")
    L = [l for l in L if l.strip()]
    if int(L[0]) != len(tasks) or len(L) != len(tasks)+1: return False, "count"
    use = [0]*n; bill = 0
    for (t, w, a, b), l in zip(tasks, L[1:]):
        v = list(map(int, l.split()))
        if v[0] != t: return False, "id"
        s = 0; seen = set()
        for k, x in zip(v[1::2], v[2::2]):
            if k in seen or not (a <= k <= b) or x <= 0: return False, f"bad {t}"
            seen.add(k); s += x; use[k] += x; bill += x*p[k]
        if s != w: return False, f"sum {t}"
    if max(use) > mp: return False, "cap"
    if bill > mb: return False, f"bill {bill}>{mb}"
    return True, f"bill {bill}/{mb}"

if __name__ == "__main__":
    print(solve(sys.stdin.read()))
