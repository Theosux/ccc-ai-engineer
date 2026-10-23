# ana: line-sweep planner. One pair (1&4 / 2&5 / 3&6) writes one full line of the chosen axis per tick,
# sweeping the pattern's span back and forth (one copy per sweep). The 4 other emitters punch the skirting
# holes on the current line (count 3 -> O). Beam over extras' 256 action combos per tick, local validity check.
import sys
from solve import Geo, pattern_cells, NB, simulate

ACTS = "-FBT"
DBG = 0
LOOK = 5


def keyf(a, c):
    y, x = c
    return (y, x - y, x + y)[a]


class Plan:
    def __init__(self, r, pcells):
        g = Geo(r)
        self.g = g
        self.m = g.m
        P = set(pcells)
        S = set()
        for (y, x) in P:
            for dy, dx in NB:
                c = (y + dy, x + dx)
                if c not in P and c in g.interior:
                    S.add(c)
        self.P, self.S = P, S
        R = sorted(P | S)
        self.R = R
        idx = {c: i for i, c in enumerate(R)}
        self.pm = sum(1 << idx[c] for c in P)
        self.sm = sum(1 << idx[c] for c in S)
        self.ray = {}
        self.linepos = {}  # (e, key) -> pos
        for (k, e), cells in g.rays.items():
            mk = 0
            for c in cells:
                if c in idx:
                    mk |= 1 << idx[c]
            self.ray[(k, e)] = mk
            if cells:
                self.linepos[(e, keyf((e - 1) % 3, cells[0]))] = k
        self.idx = idx

    def linemask(self, a, key):
        mk = 0
        for c, i in self.idx.items():
            if keyf(a, c) == key:
                mk |= 1 << i
        return mk


def rdist(m, a, b):
    d = (b - a) % m
    return min(d, m - d)


def step_toward(m, a, b):
    d = (b - a) % m
    if d == 0:
        return "-"
    return "F" if d <= m - d else "B"


def solve_axis(pl, cnt, a, start_hi, W=24, maxwait=8):
    m = pl.m
    r = pl.g.r
    pe, qe = a + 1, a + 4
    ex = [e for e in range(1, 7) if e not in (pe, qe)]
    keys = sorted({keyf(a, c) for c in pl.P})
    lo, hi = keys[0], keys[-1]
    stepk = 1 if a == 0 else 2
    lines = list(range(lo, hi + stepk, stepk))
    for L in lines:
        if (pe, L) not in pl.linepos or (qe, L) not in pl.linepos:
            return None
    lm = {L: pl.linemask(a, L) for L in lines}
    span = 0
    for L in lines:
        span |= lm[L]
    Q = pl.sm & ~span  # skirts outside span lines: always protected
    seq = []
    order = lines[::-1] if start_hi else lines
    for k in range(cnt):
        seq += order if k % 2 == 0 else order[::-1]
    # extras: other axes
    ext_axis = {e: (e - 1) % 3 for e in ex}
    # holes per line: skirt cells -> per extra emitter the target pos
    R = pl.R

    def targets(L):
        need = []
        for c in R:
            if keyf(a, c) == L and c in pl.S:
                opts = {}
                for e in ex:
                    p = pl.linepos.get((e, keyf(ext_axis[e], c)))
                    if p is not None:
                        opts[e] = p
                need.append(opts)
        return need

    tgt = {L: targets(L) for L in lines}
    for L in lines:
        if len(tgt[L]) > 4:
            return None

    def heur(st, L):
        # st: tuple of (pos, act) for ex; cost to cover holes of line L
        need = tgt[L]
        best = [99, 99]

        def rec(i, used, mx, sm):
            if mx >= best[0] and (mx > best[0] or sm >= best[1]):
                return
            if i == len(need):
                best[0], best[1] = mx, sm
                return
            for j, e in enumerate(ex):
                if used >> j & 1:
                    continue
                p = need[i].get(e)
                if p is None:
                    continue
                pos, act = st[j]
                c = rdist(m, pos, p) + (0 if act else 1)
                rec(i + 1, used | 1 << j, max(mx, c), sm + c)
        rec(0, 0, 0, 0)
        # penalty for active extras not used: small
        return best[0] * 10 + best[1]

    # pair script state
    ppos = {pe: (pe - 1) * r, qe: (qe - 1) * r}
    pact = False
    out = []
    # beam states: dict state -> list of action lines (store parent pointers)
    init = tuple(((e - 1) * r, False) for e in ex)
    frontier = {init: None}
    hist = []  # list of dict state->(prevstate, actions)
    F = Q  # protected skirt mask; also protected pattern mask
    Fp = 0
    curL = None

    def heur2(st, ei_):
        L = seq[min(ei_, len(seq) - 1)]
        h = heur(st, L) * 4
        for j in range(1, LOOK):
            if ei_ + j >= len(seq):
                break
            for opts in tgt[seq[ei_ + j]]:
                bc = 99
                for jj, e in enumerate(ex):
                    p = opts.get(e)
                    if p is None:
                        continue
                    pos, act = st[jj]
                    c = rdist(m, pos, p) + (0 if act else 1)
                    if c < bc:
                        bc = c
                if bc > j:
                    h += (bc - j) * (LOOK - j)
        return h

    def expand(front, pairline, pmask_active, Fs, Fpat, L_next, final):
        new = {}
        pm_ray = pmask_active
        for st, _ in front.items():
            # options per extra
            opts = []
            for j, e in enumerate(ex):
                pos, act = st[j]
                o = []
                for ch in ACTS:
                    np_, na = pos, act
                    if ch == "F":
                        np_ = (pos + 1) % m
                    elif ch == "B":
                        np_ = (pos - 1) % m
                    elif ch == "T":
                        na = not act
                    o.append((ch, np_, na, pl.ray[(np_, e)] if na else 0))
                opts.append(o)
            for o0 in opts[0]:
                for o1 in opts[1]:
                    for o2 in opts[2]:
                        for o3 in opts[3]:
                            g1 = g2 = g3 = 0
                            for mk in pm_ray + [o0[3], o1[3], o2[3], o3[3]]:
                                if mk:
                                    g3 |= g2 & mk
                                    g2 |= g1 & mk
                                    g1 |= mk
                            eq2 = g2 & ~g3
                            if eq2 & Fs or g3 & Fpat:
                                continue
                            if final and (pl.pm & lmL[0]) & ~eq2:
                                continue
                            ns = ((o0[1], o0[2]), (o1[1], o1[2]), (o2[1], o2[2]), (o3[1], o3[2]))
                            if ns not in new:
                                new[ns] = (st, (o0[0], o1[0], o2[0], o3[0]))
        if len(new) > W:
            sc = sorted(new, key=lambda s: heur2(s, L_next))
            new = {s: new[s] for s in sc[:W]}
        return new

    lmL = [0]
    lines_out = []  # per tick: (pair actions dict, ) ; extras from backtrack
    pair_ticks = []
    Fs_base = Q
    Fp_base = 0
    fin_s = 0
    fin_p = 0
    for ei, L in enumerate(seq):
        if ei > 0 and ei % len(lines) == 0:
            fin_s, fin_p = 0, 0  # new copy
        target = {pe: pl.linepos[(pe, L)], qe: pl.linepos[(qe, L)]}
        script = []
        # travel
        pp = dict(ppos)
        if ei == 0:
            while pp[pe] != target[pe] or pp[qe] != target[qe]:
                act = {}
                for e in (pe, qe):
                    ch = step_toward(m, pp[e], target[e])
                    act[e] = ch
                    if ch == "F":
                        pp[e] = (pp[e] + 1) % m
                    elif ch == "B":
                        pp[e] = (pp[e] - 1) % m
                script.append((act, False))
            script.append(({pe: "T", qe: "T"}, True))
        else:
            act = {}
            for e in (pe, qe):
                ch = step_toward(m, pp[e], target[e])
                assert rdist(m, pp[e], target[e]) <= 1
                act[e] = ch
                if ch == "F":
                    pp[e] = (pp[e] + 1) % m
                elif ch == "B":
                    pp[e] = (pp[e] - 1) % m
            script.append((act, True))
        move_act = script[0][0]
        lmL[0] = lm[L]
        Ls = fin_s | (pl.sm & lm[L])
        Lp = fin_p | (pl.pm & lm[L])
        ok = False
        front = frontier
        tick_hist = []
        wait = 0
        while True:
            fr = front
            th = []
            for ti, (act, act_on) in enumerate(script):
                isfinal = ti == len(script) - 1
                on = act_on or (ei > 0)
                rays = []
                if on:
                    rays = [pl.ray[(target[pe], pe)], pl.ray[(target[qe], qe)]]
                fr = expand(fr, None, rays, (Ls | Q) if isfinal else (fin_s | Q), Lp if isfinal else fin_p, (ei + 1) if isfinal else ei, isfinal)
                th.append(fr)
                if not fr:
                    break
            if fr:
                ok = True
                break
            wait += 1
            if wait > maxwait:
                return None
            # insert a wait tick (pair stays / or for first event: pair is at target inactive -> keep noop) before final
            last = script[-1]
            if ei == 0:
                script = script[:-1] + [({}, False)] + [last]
            else:
                # pair moves on first tick then stays; final is last
                script = [(move_act, True)] + [({}, True)] * wait
        # commit
        if DBG: sys.stderr.write("ev %d L %d ticks %d\n" % (ei, L, len(script)))
        for ti, (act, act_on) in enumerate(script):
            pair_ticks.append(act)
        hist.extend(th)
        frontier = th[-1]
        ppos = pp
        fin_s = Ls & ~Q
        fin_p = Lp
        if (ei + 1) % len(lines) == 0:
            pass
    # backtrack
    st = next(iter(frontier))
    exacts = []
    for h in reversed(hist):
        prev, acts = h[st]
        exacts.append(acts)
        st = prev
    exacts.reverse()
    prog = []
    for pa, ea in zip(pair_ticks, exacts):
        line = ["-"] * 6
        for e, ch in pa.items():
            line[e - 1] = ch
        for j, e in enumerate(ex):
            line[e - 1] = ea[j]
        prog.append(line)
    return prog


def solve_pat(r, pat, cnt, W=24, maxwait=8):
    pc = pattern_cells(pat)
    pl = Plan(r, pc)
    best = None
    for a in range(3):
        for sh in (False, True):
            try:
                prog = solve_axis(pl, cnt, a, sh, W=W, maxwait=maxwait)
            except Exception as ex:
                import traceback; traceback.print_exc()
                prog = None
            if prog is None:
                continue
            if simulate(pl.g, pc, prog) != cnt:
                sys.stderr.write("verify fail a=%d\n" % a)
                continue
            if best is None or len(prog) < len(best):
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
        p = solve_pat(r, pat, cnt, W=int(sys.argv[3]) if len(sys.argv) > 3 else 24, maxwait=int(sys.argv[4]) if len(sys.argv) > 4 else 8)
        print(i, r, cnt, len(best[i]), None if p is None else len(p), flush=True)
