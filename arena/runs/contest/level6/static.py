# Static configuration search: one tick creates the whole pattern; then it is re-accepted every tick.
from tbeam import TB, popcount


def search_static(geo, pcells, cnt, limit=3000000):
    T = TB(geo, pcells)
    m = geo.m
    r = geo.r
    P, S = T.P, T.S
    ray = T.ray
    start = [0] + [(e - 1) * r for e in range(1, 7)]
    opts = {}
    for e in range(1, 7):
        o = [None]
        for k in range(m):
            if ray[e][k] & P:
                o.append(k)
        opts[e] = o
    best = [None]
    nodes = [0]

    def cost_of(cfg):
        L = 0
        for e in range(1, 7):
            k = cfg[e]
            if k is None:
                continue
            f = (k - start[e]) % m
            d = min(f, m - f)
            L = max(L, d + 1)
        return L

    cfg = [None] * 7

    def dfs(e, g1, g2, g3):
        nodes[0] += 1
        if nodes[0] > limit:
            return
        if g3 & P:
            return
        if e == 7:
            ex2 = g2 & ~g3
            if (ex2 & P) == P and not (ex2 & S):
                c = cost_of(cfg)
                if best[0] is None or c < best[0][0]:
                    best[0] = (c, cfg[:])
            return
        # remaining emitters can add at most (7-e) rays to each cell: need P cells with count <2 coverable
        need = P & ~g2
        if need and (7 - e) == 0:
            return
        for k in opts[e]:
            cfg[e] = k
            if k is None:
                dfs(e + 1, g1, g2, g3)
            else:
                mm = ray[e][k]
                dfs(e + 1, g1 | mm, g2 | (g1 & mm), g3 | (g2 & mm))
        cfg[e] = None

    dfs(1, 0, 0, 0)
    if best[0] is None:
        return None
    c, cfg = best[0]
    # build program: move inactive, then toggle on at tick L
    L = c
    plans = {}
    for e in range(1, 7):
        k = cfg[e]
        if k is None:
            plans[e] = ["-"] * L
            continue
        f = (k - start[e]) % m
        if f <= m - f:
            mv = ["F"] * f
        else:
            mv = ["B"] * (m - f)
        plans[e] = mv + ["-"] * (L - 1 - len(mv)) + ["T"]
    lines = [" ".join(plans[e][i] for e in range(1, 7)) for i in range(L)]
    lines += ["- - - - - -"] * (cnt - 1)
    return lines
