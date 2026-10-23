# ana: line sweep (one pair writes one full line per tick) with EXACT reachability planning of the 4 hole
# punchers, split into the two parallel puncher pairs (axis A emitters, axis B emitters). Each line's skirt
# holes are partitioned into A-holes / B-holes (<=2 each); full reachable state sets per axis (no beam).
# Wait ticks are inserted when no partition is reachable. A x B junk is not modelled -> final simulate() check.
import sys
from solve import Geo, pattern_cells, NB, simulate
from ana_two import G, keyf, rdist, step_toward


def solve_axis(G_, cnt, a, start_hi, maxwait=12):
    m, r = G_.m, G_.r
    pe, qe = a + 1, a + 4
    others = [x for x in range(3) if x != a]
    P, S = G_.P, G_.S
    keys = sorted({keyf(a, c) for c in P})
    st = 1 if a == 0 else 2
    lines = list(range(keys[0], keys[-1] + st, st))
    for L in lines:
        if (pe, L) not in G_.linepos or (qe, L) not in G_.linepos:
            return None
    # per line: holes (cells) and pattern cells
    holes = {L: [c for c in S if keyf(a, c) == L] for L in lines}
    pats = {L: [c for c in P if keyf(a, c) == L] for L in lines}
    if any(len(h) > 4 for h in holes.values()):
        return None
    # skirts on lines just outside span must never be crossed with count 2 by pair - pair never goes there.
    order = lines[::-1] if start_hi else lines
    seq = []
    for k in range(cnt):
        seq += order if k % 2 == 0 else order[::-1]
    ems = {ax: (ax + 1, ax + 4) for ax in others}
    lo = G_.lineof

    def expand(states, e1, e2):
        new = {}
        for s in states:
            (p1, a1), (p2, a2) = s
            for c1, q1, b1 in (("-", p1, a1), ("F", (p1 + 1) % m, a1), ("B", (p1 - 1) % m, a1), ("T", p1, not a1)):
                for c2, q2, b2 in (("-", p2, a2), ("F", (p2 + 1) % m, a2), ("B", (p2 - 1) % m, a2), ("T", p2, not a2)):
                    ns = ((q1, b1), (q2, b2))
                    if ns not in new:
                        new[ns] = (s, c1, c2)
        return new

    def filt(new, ax, needk, forbk):
        e1, e2 = ems[ax]
        out = {}
        for ns, v in new.items():
            (q1, b1), (q2, b2) = ns
            l1 = lo.get((e1, q1)) if b1 else None
            l2 = lo.get((e2, q2)) if b2 else None
            if l1 is not None and l1 == l2:
                continue
            if l1 in forbk or l2 in forbk:
                continue
            ok = True
            for n in needk:
                if n != l1 and n != l2:
                    ok = False
                    break
            if ok:
                out[ns] = v
        return out

    def nofilt(new, ax):
        e1, e2 = ems[ax]
        out = {}
        for ns, v in new.items():
            (q1, b1), (q2, b2) = ns
            if b1 and b2:
                l1 = lo.get((e1, q1)); l2 = lo.get((e2, q2))
                if l1 is not None and l1 == l2:
                    continue
            out[ns] = v
        return out

    fronts = {ax: {(((ems[ax][0] - 1) * r, False), ((ems[ax][1] - 1) * r, False)): None} for ax in others}
    hist = {ax: [] for ax in others}
    pair_ticks = []
    tinfo = []
    ppos = {pe: (pe - 1) * r, qe: (qe - 1) * r}
    A0, B0 = others
    for ei, L in enumerate(seq):
        tg = {pe: G_.linepos[(pe, L)], qe: G_.linepos[(qe, L)]}
        script = []
        if ei == 0:
            pp = dict(ppos)
            while pp[pe] != tg[pe] or pp[qe] != tg[qe]:
                act = {}
                for e in (pe, qe):
                    ch = step_toward(m, pp[e], tg[e]); act[e] = ch
                    pp[e] = (pp[e] + (1 if ch == "F" else -1 if ch == "B" else 0)) % m
                script.append(act)
            final_act = {pe: "T", qe: "T"}
        else:
            final_act = {}
            for e in (pe, qe):
                assert rdist(m, ppos[e], tg[e]) <= 1
                final_act[e] = step_toward(m, ppos[e], tg[e])
        ppos = tg
        # holes partitions
        hl = holes[L]
        forb = {ax: {keyf(ax, c) for c in pats[L]} for ax in others}
        parts = []
        n = len(hl)
        for mask in range(1 << n):
            ka = [keyf(A0, hl[i]) for i in range(n) if mask >> i & 1]
            kb = [keyf(B0, hl[i]) for i in range(n) if not mask >> i & 1]
            sa, sb = set(ka), set(kb)
            if len(sa) > 2 or len(sb) > 2 or sa & forb[A0] or sb & forb[B0]:
                continue
            parts.append((sa, sb))
        if not parts:
            return None
        # pre-ticks (travel), then waits, then final
        for act in script:
            for ax in others:
                fronts[ax] = nofilt(expand(fronts[ax], *ems[ax]), ax)
                hist[ax].append(fronts[ax])
            pair_ticks.append(act); tinfo.append((L, False, ei, False))
        waits = 0
        while True:
            exA = expand(fronts[A0], *ems[A0])
            exB = expand(fronts[B0], *ems[B0])
            best = None
            for sa, sb in parts:
                fa = filt(exA, A0, sa, forb[A0])
                if not fa:
                    continue
                fb = filt(exB, B0, sb, forb[B0])
                if not fb:
                    continue
                sc = min(len(fa), len(fb)) * 1000 + len(fa) + len(fb)
                if best is None or sc > best[0]:
                    best = (sc, fa, fb)
            if best is not None:
                fronts[A0], fronts[B0] = best[1], best[2]
                hist[A0].append(best[1]); hist[B0].append(best[2])
                pair_ticks.append(final_act); tinfo.append((L, True, ei, True))
                break
            waits += 1
            if waits > maxwait:
                return None
            # wait tick: pair does its move now (first wait) then stays; no constraints
            fronts[A0] = nofilt(exA, A0); fronts[B0] = nofilt(exB, B0)
            hist[A0].append(fronts[A0]); hist[B0].append(fronts[B0])
            if ei == 0:
                pair_ticks.append({}); tinfo.append((L, False, ei, False))
            else:
                pair_ticks.append(final_act); tinfo.append((L, False, ei, True))
                final_act = {}
    return joint(G_, cnt, a, lines, seq, pair_ticks, tinfo, hist, fronts, ems, others)


JW = 600
RJ = [0, 0, 0]
DBG = 0


def joint(G_, cnt, a, lines, seq, pair_ticks, tinfo, hist, fronts, ems, others):
    import random
    m, r = G_.m, G_.r
    pl = G_.pl
    pe, qe = a + 1, a + 4
    T = len(pair_ticks)
    A0, B0 = others
    # backward feasible sets per axis
    def succ(s):
        (p1, a1), (p2, a2) = s
        for c1, q1, b1 in (("-", p1, a1), ("F", (p1 + 1) % m, a1), ("B", (p1 - 1) % m, a1), ("T", p1, not a1)):
            for c2, q2, b2 in (("-", p2, a2), ("F", (p2 + 1) % m, a2), ("B", (p2 - 1) % m, a2), ("T", p2, not a2)):
                yield (c1, c2), ((q1, b1), (q2, b2))
    feas = {}
    for ax in others:
        Bt = [None] * T
        Bt[T - 1] = set(hist[ax][T - 1].keys())
        for t in range(T - 2, -1, -1):
            nxt = Bt[t + 1]
            Bt[t] = {s for s in hist[ax][t] if any(ns in nxt for _, ns in succ(s))}
        feas[ax] = Bt
    # masks per tick
    lm = {L: pl.linemask(a, L) for L in lines}
    span = 0
    for L in lines:
        span |= lm[L]
    Q = pl.sm & ~span
    nl = len(lines)
    ppos = {pe: (pe - 1) * r, qe: (qe - 1) * r}
    pon = False
    fin_s = fin_p = 0
    cur_ei = -1
    init = tuple(((ems[ax][0] - 1) * r, False) for ax in others) + tuple(((ems[ax][1] - 1) * r, False) for ax in others)
    init = ((((ems[A0][0] - 1) * r, False), ((ems[A0][1] - 1) * r, False)), (((ems[B0][0] - 1) * r, False), ((ems[B0][1] - 1) * r, False)))
    front = {init: None}
    jh = []
    rng = random.Random(1)
    for t in range(T):
        act = pair_ticks[t]
        L, final, ei, on = tinfo[t]
        if ei != cur_ei:
            if ei > 0 and ei % nl == 0:
                fin_s = fin_p = 0
            cur_ei = ei
        for e, ch in act.items():
            if ch == "F":
                ppos[e] = (ppos[e] + 1) % m
            elif ch == "B":
                ppos[e] = (ppos[e] - 1) % m
        if pe in act and act[pe] == "T":
            pon = not pon
        prays = [pl.ray[(ppos[pe], pe)], pl.ray[(ppos[qe], qe)]] if pon else []
        if final:
            Fs = fin_s | (pl.sm & lm[L]) | Q
            Fp = fin_p | (pl.pm & lm[L])
        else:
            Fs = fin_s | Q
            Fp = fin_p
        fa, fb = feas[A0][t], feas[B0][t]
        new = {}
        items = list(front.keys())
        for js in items:
            sa, sb = js
            la = [(c, ns) for c, ns in succ(sa) if ns in fa]
            lb = [(c, ns) for c, ns in succ(sb) if ns in fb]
            for ca, na in la:
                ma = 0
                g1a = g2a = g3a = 0
                for mk in prays + [pl.ray[(na[0][0], ems[A0][0])] if na[0][1] else 0, pl.ray[(na[1][0], ems[A0][1])] if na[1][1] else 0]:
                    if mk:
                        g3a |= g2a & mk; g2a |= g1a & mk; g1a |= mk
                for cb, nb in lb:
                    key = (na, nb)
                    if key in new:
                        continue
                    g1, g2, g3 = g1a, g2a, g3a
                    for mk in (pl.ray[(nb[0][0], ems[B0][0])] if nb[0][1] else 0, pl.ray[(nb[1][0], ems[B0][1])] if nb[1][1] else 0):
                        if mk:
                            g3 |= g2 & mk; g2 |= g1 & mk; g1 |= mk
                    eq2 = g2 & ~g3
                    if eq2 & Fs:
                        RJ[0] += 1
                        continue
                    if g3 & Fp:
                        RJ[1] += 1
                        continue
                    if final and (pl.pm & lm[L]) & ~eq2:
                        RJ[2] += 1
                        continue
                    new[key] = (js, ca, cb)
        if not new:
            if DBG: sys.stderr.write("joint dead t=%d/%d final=%s L=%s fa=%d fb=%d front=%d\n" % (t, T, final, L, len(fa), len(fb), len(front)))
            return None
        if len(new) > JW:
            ks = list(new.keys())
            # prefer fewer active extras, then random
            ks.sort(key=lambda k: (sum(1 for x in (k[0][0], k[0][1], k[1][0], k[1][1]) if x[1]), rng.random()))
            new = {k: new[k] for k in ks[:JW]}
        jh.append(new)
        front = new
        if final:
            fin_s = (fin_s | (pl.sm & lm[L])) & ~Q
            fin_p = fin_p | (pl.pm & lm[L])
    st = next(iter(front))
    acts = []
    for h in reversed(jh):
        prev, ca, cb = h[st]
        acts.append((ca, cb)); st = prev
    acts.reverse()
    prog = []
    for t, pa in enumerate(pair_ticks):
        line = ["-"] * 6
        for e, ch in pa.items():
            line[e - 1] = ch
        ca, cb = acts[t]
        line[ems[A0][0] - 1], line[ems[A0][1] - 1] = ca
        line[ems[B0][0] - 1], line[ems[B0][1] - 1] = cb
        prog.append(line)
    return prog


def solve_pat(r, pat, cnt, W=0, maxwait=12):
    pc = pattern_cells(pat)
    G_ = G(r, pc)
    import ana_line
    G_.pl = ana_line.Plan(r, pc)
    best = None
    for a in range(3):
        for sh in (False, True):
            prog = solve_axis(G_, cnt, a, sh, maxwait)
            if prog is None:
                continue
            if best is not None and len(prog) >= len(best):
                continue
            if simulate(G_.g, pc, prog) != cnt:
                sys.stderr.write("verify fail\n")
                continue
            best = prog
    return best


if __name__ == "__main__":
    from solve import parse
    fid = sys.argv[1]
    sel = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    pats = parse(open(f"files/in_level-6_{fid}.txt").read())
    best = [b.strip().split("\n") for b in open(f"best/out_level-6_{fid}.txt").read().strip().split("\n\n")]
    for i, (r, pat, cnt) in enumerate(pats):
        if sel and i not in sel:
            continue
        p = solve_pat(r, pat, cnt)
        print(i, r, cnt, len(best[i]), None if p is None else len(p), flush=True)
