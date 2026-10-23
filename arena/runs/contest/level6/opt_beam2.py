# opt: time-bucketed beam over macro moves (opt_macro targets) + one-tick moves (all 4096 combos).
import random
import itertools
import opt_macro2 as OM
from opt_macro2 import val, Ctx, counts, tick, travel, options, ascend, seeds, pc
from solve import Geo, pattern_cells, simulate

ACT = "-FBT"
COMBOS = list(itertools.product(range(4), repeat=6))


def one_tick(ctx, st, nkeep):
    pos, act, board, reps = st
    m = ctx.m
    P, S = ctx.P, ctx.S
    before = val(ctx, board)
    opt = []
    for e in range(1, 7):
        o = []
        for a in range(4):
            k = pos[e]; ac = act[e]
            if a == 1:
                k = (k + 1) % m
            elif a == 2:
                k = (k - 1) % m
            elif a == 3:
                ac = not ac
            o.append(ctx.ray[e][k] if ac else 0)
        opt.append(o)
    res = []
    for combo in COMBOS:
        g1 = g2 = g3 = 0
        for i in range(6):
            mm = opt[i][combo[i]]
            if mm:
                g3 |= g2 & mm
                g2 |= g1 & mm
                g1 |= mm
        ex2 = g2 & ~g3
        if ex2 & S and not OM.LAM:
            continue
        nb = (board | ex2) & ~g3
        if nb & P == P and not (nb & S):
            g = 10 ** 6
        else:
            g = val(ctx, nb) - before
        if g > 0:
            res.append((g, combo))
    res.sort(key=lambda z: -z[0])
    out = []
    for g, combo in res[:nkeep]:
        nst, ok = tick(ctx, st, combo)
        out.append(([combo], nst))
    return out


def macro(ctx, st, rng, nseed, topk):
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
        tp = [0] + [cfg[e][1] for e in range(1, 7)]
        ta = [False] + [cfg[e][0] for e in range(1, 7)]
        g1, g2, g3 = counts(ctx, tp, ta)
        if (g2 & ~g3) & ctx.S and not OM.LAM:
            continue
        cands.append((s, tp, ta))
    miss = [c for c in ctx.pcl if not (st[2] & ctx.bit[c])]
    fb = []
    for c in (rng.sample(miss, min(3, len(miss))) if miss else []):
        for e1 in range(1, 7):
            for e2 in range(e1 + 1, 7):
                if (e1 - e2) % 3 == 0:
                    continue
                k1, k2 = ctx.src[e1].get(c), ctx.src[e2].get(c)
                if k1 is None or k2 is None:
                    continue
                tp = list(pos); ta = [False] * 7
                tp[e1] = k1; tp[e2] = k2; ta[e1] = ta[e2] = True
                T = max(ctx.dist(pos[e1], k1), ctx.dist(pos[e2], k2))
                fb.append((-T, tp, ta))
    cands.sort(key=lambda z: -z[0])
    fb.sort(key=lambda z: -z[0])
    before = val(ctx, st[2])
    out = []
    for s, tp, ta in cands[:topk] + fb[:4]:
        for mode in (0, 1, 2):
            nst, seq = travel(ctx, st, tp, ta, mode)
            if nst is None:
                continue
            g = val(ctx, nst[2]) - before
            if nst[3] > st[3] or g > 0:
                out.append((seq, nst))
    return out


def prog_key(st):
    return st[3] * 100000 + pc(st[2] & CTXP[0])


CTXP = [0]


def plan(geo, pcells, cnt, nseed=30, seed=1, W=4, topk=5, n1=3, maxlen=1500, keepper=3, lam=None):
    if lam is not None:
        OM.LAM = lam
    ctx = Ctx(geo, pcells)
    CTXP[0] = ctx.P
    rng = random.Random(seed)
    r = geo.r
    st0 = ([0] + [(e - 1) * r for e in range(1, 7)], [False] * 7, 0, 0)
    buckets = {0: [(st0, None)]}
    t = 0
    seen = set()
    while t <= maxlen:
        if t not in buckets:
            t += 1
            continue
        lst = buckets.pop(t)
        # rank and dedupe
        lst.sort(key=lambda z: -(z[0][3] * 100000 + val(ctx, z[0][2])))
        keep = []
        for st, lk in lst:
            key = (tuple(st[0]), tuple(st[1]), st[2], st[3])
            if key in seen:
                continue
            seen.add(key)
            keep.append((st, lk))
            if len(keep) >= W:
                break
        for st, lk in keep:
            if st[3] >= cnt:
                # reconstruct
                seqs = []
                while lk is not None:
                    seqs.append(lk[0])
                    lk = lk[1]
                lines = [c for s in reversed(seqs) for c in s]
                return [" ".join(ACT[a] for a in c) for c in lines]
        # prune buckets: drop states dominated? (cheap) keep growing
        for st, lk in keep:
            exps = one_tick(ctx, st, n1) + macro(ctx, st, rng, nseed, topk)
            # keep best few expansions per state by rate
            base = st[3] * 100000 + val(ctx, st[2])
            sc = []
            for seq, nst in exps:
                g = nst[3] * 100000 + val(ctx, nst[2]) - base
                if nst[3] > st[3]:
                    g = 10 ** 6
                sc.append((g / len(seq), seq, nst))
            sc.sort(key=lambda z: -z[0])
            for v, seq, nst in sc[:keepper]:
                buckets.setdefault(t + len(seq), []).append((nst, (seq, lk)))
        t += 1
    return None


if __name__ == "__main__":
    import sys, time
    from solve import parse
    fid = sys.argv[1]
    idx = [int(x) for x in sys.argv[2].split(",")]
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    pats = parse(open(f"files/in_level-6_{fid}.txt").read())
    best = open(f"best/out_level-6_{fid}.txt").read().strip().split("\n\n")
    for i in idx:
        r, pat, cnt = pats[i]
        g = Geo(r)
        pcs = pattern_cells(pat)
        t = time.time()
        l = plan(g, pcs, cnt, W=W, lam=float(sys.argv[4]) if len(sys.argv) > 4 else None)
        ok = l is not None and simulate(g, pcs, [x.split() for x in l]) == cnt
        print(i, r, cnt, len(pcs), "best", len(best[i].split("\n")), "beam", len(l) if l else None, ok, "%.1fs" % (time.time() - t), flush=True)
