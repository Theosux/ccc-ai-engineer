# ana: TWO-FAMILY sweep. Pair A (axis a) sweeps a contiguous range of a-lines, pair B (axis b) sweeps a
# contiguous range of b-lines IN PARALLEL (2 full lines per tick). Every pattern cell must lie on a swept line.
# The two singles of the third axis c punch holes (single + pair line = count 3 -> O); two parallel singles never
# create matter, so there is zero junk. The crossing of the two pair lines is count 4 -> O (a free hole).
# A cell's final state in a copy = its state at its LAST pair-line event; copies alternate sweep direction.
# Singles are planned by exact DP over (pos,act) x2.
import sys
EXTRA = 2
from solve import Geo, pattern_cells, NB, simulate


def keyf(a, c):
    y, x = c
    return (y, x - y, x + y)[a]


def rdist(m, a, b):
    d = (b - a) % m
    return min(d, m - d)


def step_toward(m, a, b):
    d = (b - a) % m
    if d == 0:
        return "-"
    return "F" if d <= m - d else "B"


class G:
    def __init__(self, r, pcells):
        g = Geo(r)
        self.g, self.m, self.r = g, g.m, r
        P = set(pcells)
        S = set()
        for (y, x) in P:
            for dy, dx in NB:
                c = (y + dy, x + dx)
                if c not in P and c in g.interior:
                    S.add(c)
        self.P, self.S = P, S
        self.R = sorted(P | S)
        self.linepos = {}
        self.lineof = {}
        for (k, e), cells in g.rays.items():
            if cells:
                key = keyf((e - 1) % 3, cells[0])
                self.linepos[(e, key)] = k
                self.lineof[(e, k)] = key


def plan_cost_list(G_, cnt, maxc=40):
    """enumerate candidate (a,b,c, Ra list, Rb list per tick) sorted by cost estimate"""
    P = G_.P
    m, r = G_.m, G_.r
    cands = []
    for c in range(3):
        a, b = [x for x in range(3) if x != c]
        st = 1 if a == 0 else 2
        stb = 1 if b == 0 else 2
        aks = sorted({keyf(a, p) for p in P})
        for i1 in range(len(aks)):
            for i2 in range(i1, len(aks)):
                a1, a2 = aks[i1], aks[i2]
                rest = [p for p in P if not (a1 <= keyf(a, p) <= a2)]
                La = (a2 - a1) // st + 1
                if rest:
                    bks = [keyf(b, p) for p in rest]
                    b1, b2 = min(bks), max(bks)
                    Lb = (b2 - b1) // stb + 1
                else:
                    continue
                K = max(La, Lb)
                Ra = list(range(a1, a2 + st, st))
                Rb = list(range(b1, b2 + stb, stb))
                for Ra2 in (Ra, Ra[::-1]):
                    for Rb2 in (Rb, Rb[::-1]):
                        for K2 in range(K, K + EXTRA + 1):
                            for sa in range(0, K2 - La + 1):
                                A_ = [Ra2[0]] * sa + Ra2 + [Ra2[-1]] * (K2 - La - sa)
                                for sb in range(0, K2 - Lb + 1):
                                    B_ = [Rb2[0]] * sb + Rb2 + [Rb2[-1]] * (K2 - Lb - sb)
                                    pe = [a + 1, a + 4, b + 1, b + 4]
                                    tl = [A_[0], A_[0], B_[0], B_[0]]
                                    ok = True
                                    d = 0
                                    for e, L in zip(pe, tl):
                                        p = G_.linepos.get((e, L))
                                        if p is None:
                                            ok = False
                                            break
                                        d = max(d, rdist(m, (e - 1) * r, p))
                                    if not ok:
                                        continue
                                    cands.append((d + cnt * K2, a, b, c, tuple(A_), tuple(B_)))
    cands = sorted(set(cands))
    return cands[:maxc]


def try_plan(G_, cnt, a, b, c, A_, B_):
    m, r = G_.m, G_.r
    K = len(A_)
    # check all pair moves adjacent
    pa, pb = (a + 1, a + 4), (b + 1, b + 4)
    for fam, seq in ((pa, A_), (pb, B_)):
        for e in fam:
            for t in range(K):
                if (e, seq[t]) not in G_.linepos:
                    return None
            for t in range(K - 1):
                if rdist(m, G_.linepos[(e, seq[t])], G_.linepos[(e, seq[t + 1])]) > 1:
                    return None
    # need/forbid per copy direction
    reqs = []
    for rev in (False, True):
        As = A_[::-1] if rev else A_
        Bs = B_[::-1] if rev else B_
        need = [set() for _ in range(K)]
        forb = [set() for _ in range(K)]
        for X in G_.R:
            ka, kb, kc = keyf(a, X), keyf(b, X), keyf(c, X)
            last = -1
            for t in range(K - 1, -1, -1):
                if As[t] == ka or Bs[t] == kb:
                    last = t
                    break
            isP = X in G_.P
            if last < 0:
                if isP:
                    return None
                continue
            inter = As[last] == ka and Bs[last] == kb
            if isP:
                if inter:
                    return None
                forb[last].add(kc)
            else:
                if not inter:
                    need[last].add(kc)
        for t in range(K):
            if len(need[t]) > 2 or need[t] & forb[t]:
                return None
        reqs.append((As, Bs, need, forb))
    # travel
    pe = [pa[0], pa[1], pb[0], pb[1]]
    tgt0 = {pa[0]: G_.linepos[(pa[0], A_[0])], pa[1]: G_.linepos[(pa[1], A_[0])],
            pb[0]: G_.linepos[(pb[0], B_[0])], pb[1]: G_.linepos[(pb[1], B_[0])]}
    d = max(rdist(m, (e - 1) * r, tgt0[e]) for e in pe)
    # global tick list: (pair actions dict, need, forb)
    ticks = []
    pos = {e: (e - 1) * r for e in pe}
    for t in range(d):
        act = {}
        for e in pe:
            ch = step_toward(m, pos[e], tgt0[e])
            act[e] = ch
            if ch == "F":
                pos[e] = (pos[e] + 1) % m
            elif ch == "B":
                pos[e] = (pos[e] - 1) % m
        ticks.append((act, set(), set()))
    first = True
    for k in range(cnt):
        As, Bs, need, forb = reqs[k % 2]
        for t in range(K):
            act = {}
            if first:
                for e in pe:
                    act[e] = "T"
                first = False
            else:
                for fam, L in ((pa, As[t]), (pb, Bs[t])):
                    for e in fam:
                        tg = G_.linepos[(e, L)]
                        ch = step_toward(m, pos[e], tg)
                        act[e] = ch
                        if ch == "F":
                            pos[e] = (pos[e] + 1) % m
                        elif ch == "B":
                            pos[e] = (pos[e] - 1) % m
            ticks.append((act, need[t], forb[t]))
    # DP singles
    s1, s2 = c + 1, c + 4
    lo = G_.lineof

    def okst(st, need, forb):
        (p1, a1), (p2, a2) = st
        l1 = lo.get((s1, p1)) if a1 else None
        l2 = lo.get((s2, p2)) if a2 else None
        if l1 is not None and l1 == l2:
            return False
        if l1 in forb or l2 in forb:
            return False
        for n in need:
            if n != l1 and n != l2:
                return False
        return True

    def moves(e, p, ac):
        yield "-", p, ac
        yield "F", (p + 1) % m, ac
        yield "B", (p - 1) % m, ac
        yield "T", p, not ac

    front = {(((s1 - 1) * r, False), ((s2 - 1) * r, False)): None}
    hist = []
    for (act, need, forb) in ticks:
        new = {}
        for st in front:
            (p1, a1), (p2, a2) = st
            for c1, q1, b1 in moves(s1, p1, a1):
                for c2, q2, b2 in moves(s2, p2, a2):
                    ns = ((q1, b1), (q2, b2))
                    if ns in new:
                        continue
                    if not okst(ns, need, forb):
                        continue
                    new[ns] = (st, c1, c2)
        if not new:
            return None
        hist.append(new)
        front = new
    st = next(iter(front))
    sacts = []
    for h in reversed(hist):
        prev, c1, c2 = h[st]
        sacts.append((c1, c2))
        st = prev
    sacts.reverse()
    prog = []
    for (act, _, _), (c1, c2) in zip(ticks, sacts):
        line = ["-"] * 6
        for e, ch in act.items():
            line[e - 1] = ch
        line[s1 - 1] = c1
        line[s2 - 1] = c2
        prog.append(line)
    return prog


def solve_pat(r, pat, cnt, W=4000, maxwait=0, limit=None):
    pc = pattern_cells(pat)
    G_ = G(r, pc)
    best = None
    tried = 0
    for cand in plan_cost_list(G_, cnt, maxc=W):
        cost = cand[0]
        if best is not None and cost >= len(best):
            break
        if limit is not None and cost >= limit:
            break
        prog = try_plan(G_, cnt, *cand[1:])
        tried += 1
        if prog is None:
            continue
        if simulate(G_.g, pc, prog) != cnt:
            sys.stderr.write("verify fail\n")
            continue
        if best is None or len(prog) < len(best):
            best = prog
    return best


if __name__ == "__main__":
    from solve import parse
    fid = sys.argv[1]
    sel = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] != "all" else None
    pats = parse(open(f"files/in_level-6_{fid}.txt").read())
    best = [b.strip().split("\n") for b in open(f"best/out_level-6_{fid}.txt").read().strip().split("\n\n")]
    for i, (r, pat, cnt) in enumerate(pats):
        if sel and i not in sel:
            continue
        p = solve_pat(r, pat, cnt, W=int(sys.argv[3]) if len(sys.argv) > 3 else 4000)
        print(i, r, cnt, len(best[i]), None if p is None else len(p), flush=True)
