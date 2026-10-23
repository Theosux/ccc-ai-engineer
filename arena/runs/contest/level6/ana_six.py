# ana: 6-singles lattice experiment. All 6 emitters active as single rays (2 per axis); crossings of
# different-axis rays = count 2 -> M; triple points -> O. Beam over 729 move combos (F/B/- per emitter) +
# optional toggles; never allow a skirt cell to be M at end of a tick (strict).
import sys
from solve import Geo, pattern_cells, NB, simulate

def build(r, pcells):
    g = Geo(r)
    P = set(pcells)
    S = set()
    for (y, x) in P:
        for dy, dx in NB:
            c = (y + dy, x + dx)
            if c not in P and c in g.interior:
                S.add(c)
    R = sorted(P | S)
    idx = {c: i for i, c in enumerate(R)}
    pm = sum(1 << idx[c] for c in P)
    sm = sum(1 << idx[c] for c in S)
    ray = {}
    for (k, e), cells in g.rays.items():
        mk = 0
        for c in cells:
            if c in idx:
                mk |= 1 << idx[c]
        ray[(k, e)] = mk
    return g, pm, sm, ray


def popc(x):
    return bin(x).count("1")


def run(r, pat, cnt, W=30, maxT=400):
    pc = pattern_cells(pat)
    g, pm, sm, ray = build(r, pc)
    m = g.m
    ACT = "-FBT"
    # state: (pos tuple, act tuple, board, acc)
    init = (tuple((e - 1) * r for e in range(1, 7)), (False,) * 6, 0, 0)
    beam = [(0, init, [])]
    for t in range(maxT):
        cand = {}
        for sc0, (pos, act, board, acc), prog in beam:
            # per emitter options
            opts = []
            for e in range(6):
                o = []
                for ch in ACT:
                    p, a = pos[e], act[e]
                    if ch == "F": p = (p + 1) % m
                    elif ch == "B": p = (p - 1) % m
                    elif ch == "T": a = not a
                    o.append((ch, p, a, ray[(p, e + 1)] if a else 0))
                opts.append(o)
            # enumerate 4^6 = 4096
            def rec(i, g1, g2, g3, chs, ps, as_):
                if i == 6:
                    eq2 = g2 & ~g3
                    nb = (board | eq2) & ~g3
                    if nb & sm:
                        return
                    nacc = acc
                    if nb & pm == pm:
                        nb &= ~pm
                        nacc += 1
                        if nacc > cnt:
                            return
                    key = (tuple(ps), tuple(as_), nb)
                    gain = popc(nb & pm) + nacc * 10000
                    if key not in cand or cand[key][0] < gain:
                        cand[key] = (gain, nacc, prog + [" ".join(chs)])
                    return
                for ch, p, a, mk in opts[i]:
                    h3 = g3 | (g2 & mk); h2 = g2 | (g1 & mk); h1 = g1 | mk
                    rec(i + 1, h1, h2, h3, chs + [ch], ps + [p], as_ + [a])
            rec(0, 0, 0, 0, [], [], [])
        if not cand:
            return None
        items = sorted(cand.items(), key=lambda kv: -kv[1][0])[:W]
        beam = []
        for (ps, as_, nb), (gain, nacc, prog) in items:
            if nacc == cnt:
                return prog
            beam.append((gain, (ps, as_, nb, nacc), prog))
    return None


if __name__ == "__main__":
    from solve import parse
    fid = sys.argv[1]
    sel = [int(x) for x in sys.argv[2].split(",")]
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    pats = parse(open(f"files/in_level-6_{fid}.txt").read())
    best = [b.strip().split("\n") for b in open(f"best/out_level-6_{fid}.txt").read().strip().split("\n\n")]
    for i in sel:
        r, pat, cnt = pats[i]
        p = run(r, pat, cnt, W=W)
        ok = None
        if p:
            ok = simulate(Geo(r), pattern_cells(pat), [l.split() for l in p]) == cnt
        print(i, r, cnt, len(best[i]), None if p is None else len(p), ok, flush=True)
