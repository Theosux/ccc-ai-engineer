# Tick-level beam search with bitmask simulation (good for small boards).
import itertools
from solve import Geo, NB, pattern_cells, simulate

ACTS = ("-", "F", "B", "T")
DIST = 0


def popcount(x):
    return bin(x).count("1")


class TB:
    def __init__(self, geo, pcells):
        self.geo = geo
        g = geo
        cells = sorted(g.interior)
        self.bit = {c: 1 << i for i, c in enumerate(cells)}
        self.P = 0
        for c in pcells:
            self.P |= self.bit[c]
        S = 0
        for (y, x) in pcells:
            for dy, dx in NB:
                c = (y + dy, x + dx)
                if c not in pcells and c in g.interior:
                    S |= self.bit[c]
        self.S = S
        self.ray = [[0] * g.m for _ in range(7)]
        for e in range(1, 7):
            for k in range(g.m):
                mm = 0
                for c in g.rays[(k, e)]:
                    mm |= self.bit[c]
                self.ray[e][k] = mm
        # for each pattern cell: per emitter the ring idx whose ray hits it
        self.src = {}
        for e in range(1, 7):
            d = {}
            for k in range(g.m):
                for c in g.rays[(k, e)]:
                    d[c] = k
            self.src[e] = d
        self.pcells = list(pcells)

    def dist_to_cell(self, pos, c):
        """min over emitter pairs (different axes) of max ring distance to cross at c"""
        m = self.geo.m
        ds = []
        for e in range(1, 7):
            k = self.src[e].get(c)
            if k is None:
                ds.append(99)
                continue
            f = (k - pos[e]) % m
            ds.append(min(f, m - f))
        best = 99
        for a in range(6):
            for b in range(a + 1, 6):
                if (a % 3) == (b % 3):
                    continue
                v = max(ds[a], ds[b])
                if v < best:
                    best = v
        return best


def search(geo, pcells, cnt, W=4, maxticks=None):
    T = TB(geo, pcells)
    m = geo.m
    r = geo.r
    P, S = T.P, T.S
    ray = T.ray
    npc = popcount(P)
    maxticks = maxticks or (cnt * (npc * 3 + 4 * r) + 50)
    pos0 = tuple([0] + [(e - 1) * r for e in range(1, 7)])
    # node: (score, pos, act(bitmask over 1..6), board, reps, lines)
    start = (pos0, 0, 0, 0, ())
    beam = [start]
    seen = set()
    acts_all = list(itertools.product(range(4), repeat=6))
    for t in range(maxticks):
        cand = []
        for (pos, act, board, reps, lines) in beam:
            for combo in acts_all:
                np = list(pos)
                na = act
                for i in range(6):
                    a = combo[i]
                    if a == 1:
                        np[i + 1] = (np[i + 1] + 1) % m
                    elif a == 2:
                        np[i + 1] = (np[i + 1] - 1) % m
                    elif a == 3:
                        na ^= 1 << (i + 1)
                g1 = g2 = g3 = 0
                for e in range(1, 7):
                    if na >> e & 1:
                        mm = ray[e][np[e]]
                        g3 |= g2 & mm
                        g2 |= g1 & mm
                        g1 |= mm
                ex2 = g2 & ~g3
                if ex2 & S:
                    continue
                nb = (board | ex2) & ~g3
                nr = reps
                if nb & P == P and not (nb & S):
                    nb &= ~P
                    nr += 1
                key = (tuple(np), na, nb, nr)
                if key in seen:
                    continue
                seen.add(key)
                have = popcount(nb & P)
                onray = popcount(g1 & P & ~nb)
                sc = nr * 10000 + have * 100 + onray * 3
                cand.append((sc, combo, tuple(np), na, nb, nr, lines))
        if not cand:
            return None
        cand.sort(key=lambda z: -z[0])
        if DIST:
            top = cand[:max(W * 8, 40)]
            rer = []
            for z in top:
                nb = z[4]
                md = 99
                for c in T.pcells:
                    if not (nb & T.bit[c]):
                        d = T.dist_to_cell(z[2], c)
                        if d < md:
                            md = d
                            if md == 0:
                                break
                rer.append((z[0] - DIST * (md if md < 99 else 0), z))
            rer.sort(key=lambda q: -q[0])
            cand = [q[1] for q in rer]
        beam = []
        for sc, combo, np, na, nb, nr, lines in cand[:W]:
            nl = lines + (combo,)
            if nr >= cnt:
                return [" ".join(ACTS[a] for a in c) for c in nl]
            beam.append((np, na, nb, nr, nl))
    return None
