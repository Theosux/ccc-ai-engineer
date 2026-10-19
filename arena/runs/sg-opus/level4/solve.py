import sys
import numpy as np
from ortools.graph.python import min_cost_flow


def parse(data):
    d = list(map(int, data.split()))
    i = 0
    mp, mb, n = d[0], d[1], d[2]; i = 3
    p = d[i:i+n]; i += n
    m = d[i]; i += 1
    t = []
    for _ in range(m):
        t.append(tuple(d[i:i+4])); i += 4
    return mp, mb, n, p, t


def solve(data):
    mp, mb, n, p, t = parse(data)
    m = len(t)
    # nodes: 0 src, 1 sink, 2..2+m tasks, 2+m.. minutes
    S, T = 0, 1
    tails, heads, caps, costs = [], [], [], []
    for k, (tid, pw, s, e) in enumerate(t):
        tails.append(np.array([S])); heads.append(np.array([2 + k])); caps.append(np.array([pw])); costs.append(np.array([0]))
        mins = np.arange(s, e + 1)
        tails.append(np.full(len(mins), 2 + k)); heads.append(2 + m + mins)
        caps.append(np.full(len(mins), pw)); costs.append(np.zeros(len(mins), dtype=np.int64))
    tails.append(2 + m + np.arange(n)); heads.append(np.full(n, T))
    caps.append(np.full(n, mp)); costs.append(np.array(p, dtype=np.int64))
    tails = np.concatenate(tails).astype(np.int32); heads = np.concatenate(heads).astype(np.int32)
    caps = np.concatenate(caps).astype(np.int64); costs = np.concatenate(costs).astype(np.int64)
    f = min_cost_flow.SimpleMinCostFlow()
    arcs = f.add_arcs_with_capacity_and_unit_cost(tails, heads, caps, costs)
    tot = sum(x[1] for x in t)
    f.set_node_supply(S, tot); f.set_node_supply(T, -tot)
    st = f.solve()
    assert st == f.OPTIMAL, st
    flows = f.flows(arcs)
    alloc = [[] for _ in range(m)]
    sel = np.nonzero((flows > 0) & (tails >= 2) & (tails < 2 + m))[0]
    for a in sel:
        alloc[tails[a] - 2].append((int(heads[a]) - 2 - m, int(flows[a])))
    out = [str(m)]
    for k, (tid, pw, s, e) in enumerate(t):
        out.append(f"{tid} " + " ".join(f"{a} {b}" for a, b in sorted(alloc[k])))
    return "\n".join(out)


def check(data, out):
    mp, mb, n, p, t = parse(data)
    lines = out.strip().split("\n")
    if int(lines[0]) != len(t):
        return False, "count"
    use = [0] * n
    bill = 0
    seen = set()
    for ln in lines[1:]:
        v = list(map(int, ln.split()))
        tid = v[0]
        if tid in seen:
            return False, "dup task"
        seen.add(tid)
        _, pw, s, e = next(x for x in t if x[0] == tid)
        tot = 0; ms = set()
        for j in range(1, len(v), 2):
            mi, q = v[j], v[j+1]
            if not (s <= mi <= e) or q <= 0 or mi in ms:
                return False, f"bad minute {tid}"
            ms.add(mi)
            tot += q; use[mi] += q; bill += q * p[mi]
        if tot != pw:
            return False, f"power {tid}"
    if len(seen) != len(t):
        return False, "missing"
    if max(use) > mp:
        return False, "maxpower"
    if bill > mb:
        return False, f"bill {bill} > {mb}"
    return True, f"bill {bill}/{mb}"


if __name__ == "__main__":
    print(solve(sys.stdin.read()))
