# opt: macro-step greedy planner. Each macro step picks a TARGET configuration (pos+active for all 6 emitters)
import sys
TRACE = 0
# by coordinate ascent maximizing (pattern gain)/(travel ticks); travel is simulated exactly.
import random
from solve import Geo, NB, pattern_cells, simulate

ACT = "-FBT"


def pc(x):
    return bin(x).count("1")


class Ctx:
    def __init__(self, geo, pcells):
        g = geo
        self.g = g
        self.m = g.m
        cells = sorted(g.interior)
        self.cells = cells
        self.bit = {c: 1 << i for i, c in enumerate(cells)}
        P = 0
        for c in pcells:
            P |= self.bit[c]
        S = 0
        for (y, x) in pcells:
            for dy, dx in NB:
                c = (y + dy, x + dx)
                if c not in pcells and c in g.interior:
                    S |= self.bit[c]
        self.P, self.S = P, S
        self.ray = [[0] * g.m for _ in range(7)]
        self.src = [None] + [dict() for _ in range(6)]
        for e in range(1, 7):
            for k in range(g.m):
                mm = 0
                for c in g.rays[(k, e)]:
                    mm |= self.bit[c]
                    self.src[e][c] = k
                self.ray[e][k] = mm
        self.pcl = list(pcells)
        # useful positions per emitter: nonempty rays + one empty park position nearest each
        self.empty = [None] + [[k for k in range(g.m) if self.ray[e][k] == 0] for e in range(1, 7)]

    def dist(self, a, b):
        f = (b - a) % self.m
        return min(f, self.m - f)


def counts(ctx, pos, act):
    g1 = g2 = g3 = 0
    for e in range(1, 7):
        if act[e]:
            mm = ctx.ray[e][pos[e]]
            g3 |= g2 & mm
            g2 |= g1 & mm
            g1 |= mm
    return g1, g2, g3


def tick(ctx, st, combo):
    """st=(pos,act,board,reps). combo: tuple of 6 ints. returns new st, ok(no skirting M)"""
    pos, act, board, reps = st
    pos = list(pos); act = list(act)
    m = ctx.m
    for i in range(6):
        a = combo[i]
        if a == 1:
            pos[i + 1] = (pos[i + 1] + 1) % m
        elif a == 2:
            pos[i + 1] = (pos[i + 1] - 1) % m
        elif a == 3:
            act[i + 1] = not act[i + 1]
    g1, g2, g3 = counts(ctx, pos, act)
    ex2 = g2 & ~g3
    nb = (board | ex2) & ~g3
    ok = not (nb & ctx.S)
    if nb & ctx.P == ctx.P and ok:
        nb &= ~ctx.P
        reps += 1
    return (pos, act, nb, reps), ok


def emitter_plan(ctx, e, k0, a0, k1, a1):
    m = ctx.m
    f = (k1 - k0) % m
    mv = [1] * f if f <= m - f else [2] * (m - f)
    if a0 and not a1:
        return [3] + mv
    if a1 and not a0:
        return mv + [3]
    return mv


def travel(ctx, st, tpos, tact, mode):
    pos, act, board, reps = st
    plans = [emitter_plan(ctx, e, pos[e], act[e], tpos[e], tact[e]) for e in range(1, 7)]
    L = max(len(p) for p in plans)
    if L == 0:
        L = 1
        plans = [[0] for _ in range(6)]
    if mode == 0:  # align ends
        plans = [[0] * (L - len(p)) + p for p in plans]
    elif mode == 1:  # start early
        plans = [p + [0] * (L - len(p)) for p in plans]
    else:  # safe: every active emitter off first, moves, all turn-ons at the final tick
        npl = []
        for e in range(1, 7):
            k0, a0, k1, a1 = pos[e], act[e], tpos[e], tact[e]
            f = (k1 - k0) % ctx.m
            mv = [1] * f if f <= ctx.m - f else [2] * (ctx.m - f)
            p = ([3] if a0 else []) + mv
            npl.append(p)
        L = max([len(p) for p in npl] + [0]) + 1
        plans = []
        for e in range(1, 7):
            p = npl[e - 1] + [0] * (L - 1 - len(npl[e - 1]))
            p.append(3 if tact[e] else 0)
            plans.append(p)
    combos = [tuple(plans[i][t] for i in range(6)) for t in range(L)]
    out = []
    for c in combos:
        st, ok = tick(ctx, st, c)
        out.append(c)
        if not ok:
            return None, None
        if st[3] > reps:
            return st, out  # stop at acceptance
    return st, out


def options(ctx, e, pos, act):
    m = ctx.m
    opts = [(False, pos[e])]
    for k in range(m):
        if ctx.ray[e][k] or k == pos[e]:
            opts.append((True, k))
    # nearest empty park positions in each direction
    for d in (1, -1):
        for s in range(m):
            k = (pos[e] + d * s) % m
            if ctx.ray[e][k] == 0:
                opts.append((True, k))
                break
    return opts


def ascend(ctx, st, cfg, rng, opts_cache, viol_w=3.0):
    pos, act, board, reps = st
    P, S = ctx.P, ctx.S
    miss = P & ~board
    done = P & board
    ray = ctx.ray
    cost = [0] * 7
    for e in range(1, 7):
        a, k = cfg[e]
        cost[e] = ctx.dist(pos[e], k) + (1 if a != act[e] else 0)

    def score_full(cfg):
        g1 = g2 = g3 = 0
        for e in range(1, 7):
            a, k = cfg[e]
            if a:
                mm = ray[e][k]
                g3 |= g2 & mm
                g2 |= g1 & mm
                g1 |= mm
        ex2 = g2 & ~g3
        gain = pc(ex2 & miss) - pc(g3 & done) - viol_w * pc(ex2 & S)
        return gain

    best_s = None
    improved = True
    passes = 0
    order = list(range(1, 7))
    while improved and passes < 4:
        improved = False
        passes += 1
        rng.shuffle(order)
        for e in order:
            # counts of others
            o1 = o2 = o3 = 0
            for f in range(1, 7):
                if f != e:
                    a, k = cfg[f]
                    if a:
                        mm = ray[f][k]
                        o3 |= o2 & mm
                        o2 |= o1 & mm
                        o1 |= mm
            othert = max([cost[f] for f in range(1, 7) if f != e] + [0])
            cur = cfg[e]
            bs = None
            bo = None
            for (a, k) in opts_cache[e]:
                if a:
                    R = ray[e][k]
                    t3 = o3 | (o2 & R)
                    t2 = (o2 & ~R) | (o1 & R)
                    t2 &= ~t3
                else:
                    t3 = o3
                    t2 = o2 & ~o3
                gain = pc(t2 & miss) - pc(t3 & done) - viol_w * pc(t2 & S)
                c = ctx.dist(pos[e], k) + (1 if a != act[e] else 0)
                T = max(othert, c, 1)
                s = gain / (T + 0.3)
                if bs is None or s > bs + 1e-9 or (abs(s - bs) < 1e-9 and (a, k) == cur):
                    bs = s
                    bo = (a, k)
            if bo != cur:
                cfg[e] = bo
                cost[e] = ctx.dist(pos[e], bo[1]) + (1 if bo[0] != act[e] else 0)
                improved = True
            best_s = bs
    return cfg, best_s


def seeds(ctx, st, rng, nseed):
    pos, act, board, reps = st
    miss = [c for c in ctx.pcl if not (board & ctx.bit[c])]
    base = [None] + [(act[e], pos[e]) for e in range(1, 7)]
    off = [None] + [(False, pos[e]) for e in range(1, 7)]
    out = [base[:], off[:]]
    for _ in range(nseed):
        cfg = (base if rng.random() < 0.5 else off)[:]
        c = rng.choice(miss)
        kind = rng.random()
        if kind < 0.5:
            # pair line on an axis
            ax = rng.randrange(3)
            e1, e2 = (1, 4) if ax == 0 else ((2, 5) if ax == 1 else (3, 6))
            for e in (e1, e2):
                k = ctx.src[e].get(c)
                if k is not None:
                    cfg[e] = (True, k)
        else:
            es = rng.sample(range(1, 7), 2)
            if (es[0] - es[1]) % 3 == 0:
                es[1] = es[1] % 6 + 1
            for e in es:
                k = ctx.src[e].get(c)
                if k is not None:
                    cfg[e] = (True, k)
        out.append(cfg)
    return out


def plan(geo, pcells, cnt, nseed=40, topk=6, seed=1, maxlen=2000):
    ctx = Ctx(geo, pcells)
    rng = random.Random(seed)
    r = geo.r
    st = ([0] + [(e - 1) * r for e in range(1, 7)], [False] * 7, 0, 0)
    lines = []
    while st[3] < cnt:
        if len(lines) > maxlen:
            return None
        pos, act = st[0], st[1]
        oc = [None] + [options(ctx, e, pos, act) for e in range(1, 7)]
        cands = []
        seen = set()
        for cfg in seeds(ctx, st, rng, nseed):
            cfg, s = ascend(ctx, st, cfg, rng, oc)
            key = tuple(cfg[1:])
            if key in seen:
                continue
            seen.add(key)
            cands.append((s, cfg))
        # exact feasibility of the target config itself
        feas = []
        for sc, cfg in cands:
            tp = [0] + [cfg[e][1] for e in range(1, 7)]
            ta = [False] + [cfg[e][0] for e in range(1, 7)]
            g1, g2, g3 = counts(ctx, tp, ta)
            ex2 = g2 & ~g3
            if ex2 & ctx.S:
                continue
            feas.append((sc, cfg))
        # fallback crossings at a few missing cells
        miss = [c for c in ctx.pcl if not (st[2] & ctx.bit[c])]
        for c in rng.sample(miss, min(4, len(miss))):
            for e1 in range(1, 7):
                for e2 in range(e1 + 1, 7):
                    if (e1 - e2) % 3 == 0:
                        continue
                    k1, k2 = ctx.src[e1].get(c), ctx.src[e2].get(c)
                    if k1 is None or k2 is None:
                        continue
                    cfg = [None] + [(False, pos[e]) for e in range(1, 7)]
                    cfg[e1] = (True, k1); cfg[e2] = (True, k2)
                    T = max(ctx.dist(pos[e1], k1), ctx.dist(pos[e2], k2)) + 2
                    feas.append((1.0 / T - 10, cfg))
        cands = feas
        cands.sort(key=lambda z: -z[0])
        before = pc(st[2] & ctx.P)
        bestv = None
        for s, cfg in cands[:topk] + [z for z in cands[topk:] if z[0] < -5][:8]:
            tpos = [0] + [cfg[e][1] for e in range(1, 7)]
            tact = [False] + [cfg[e][0] for e in range(1, 7)]
            for mode in (0, 1, 2):
                nst, seq = travel(ctx, st, tpos, tact, mode)
                if nst is None:
                    continue
                g = (nst[3] - st[3]) * 100000 + pc(nst[2] & ctx.P) - before
                if nst[3] > st[3]:
                    g = 10 ** 6
                v = g / len(seq)
                if g > 0 and (bestv is None or v > bestv[0]):
                    bestv = (v, nst, seq)
            if bestv is not None and s < -5 and len(cands) > topk:
                break
        if bestv is None:
            # fallback: safe single cell creation
            return None
        _, st, seq = bestv
        lines.extend(seq)
        if TRACE: print(len(seq), pc(st[2] & ctx.P) - before, st[3], file=sys.stderr)
    return [" ".join(ACT[a] for a in c) for c in lines]


if __name__ == "__main__":
    import sys, time
    from solve import parse
    fid = sys.argv[1]
    idx = [int(x) for x in sys.argv[2].split(",")]
    pats = parse(open(f"files/in_level-6_{fid}.txt").read())
    best = open(f"best/out_level-6_{fid}.txt").read().strip().split("\n\n")
    for i in idx:
        r, pat, cnt = pats[i]
        g = Geo(r)
        pcs = pattern_cells(pat)
        t = time.time()
        l = plan(g, pcs, cnt)
        ok = l is not None and simulate(g, pcs, [x.split() for x in l]) == cnt
        print(i, r, cnt, len(pcs), "best", len(best[i].split("\n")), "macro", len(l) if l else None, ok, "%.1fs" % (time.time() - t), flush=True)
