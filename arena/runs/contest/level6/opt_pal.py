# opt: palindrome/cycle compression. Given a program, take the prefix up to the j-th acceptance and a core segment
# L[s:t]; continue with reversed core (F<->B, reversed order), core, reversed core, ... until cnt acceptances.
# Verified by exact simulation; returns the shortest found.
from solve import Geo, NB, pattern_cells

INV = {"F": "B", "B": "F", "T": "T", "-": "-"}


def acc_times(geo, pcells, prog):
    """returns list of tick indices (0-based) at which acceptance happened"""
    r = geo.r
    m = geo.m
    pos = [0] + [(e - 1) * r for e in range(1, 7)]
    act = [False] * 7
    skirt = set()
    for (y, x) in pcells:
        for dy, dx in NB:
            c = (y + dy, x + dx)
            if c not in pcells and c in geo.interior:
                skirt.add(c)
    matter = set()
    out = []
    for t, line in enumerate(prog):
        for e in range(1, 7):
            ins = line[e - 1]
            if ins == "F":
                pos[e] = (pos[e] + 1) % m
            elif ins == "B":
                pos[e] = (pos[e] - 1) % m
            elif ins == "T":
                act[e] = not act[e]
        cnt = {}
        for e in range(1, 7):
            if act[e]:
                for c in geo.rays[(pos[e], e)]:
                    cnt[c] = cnt.get(c, 0) + 1
        for c, k in cnt.items():
            if k == 2:
                matter.add(c)
            elif k >= 3:
                matter.discard(c)
        if pcells <= matter and not (skirt & matter):
            matter -= pcells
            out.append(t)
    return out


def rev(seg):
    return [[INV[a] for a in l] for l in reversed(seg)]


class Fast:
    """bitmask simulator that can stop early"""

    def __init__(self, geo, pcells):
        cells = sorted(geo.interior)
        self.bit = {c: 1 << i for i, c in enumerate(cells)}
        self.P = 0
        for c in pcells:
            self.P |= self.bit[c]
        S = 0
        for (y, x) in pcells:
            for dy, dx in NB:
                c = (y + dy, x + dx)
                if c not in pcells and c in geo.interior:
                    S |= self.bit[c]
        self.S = S
        self.m = geo.m
        self.r = geo.r
        self.ray = [[0] * geo.m for _ in range(7)]
        for e in range(1, 7):
            for k in range(geo.m):
                mm = 0
                for c in geo.rays[(k, e)]:
                    mm |= self.bit[c]
                self.ray[e][k] = mm

    def run(self, prog, cnt):
        """returns tick count needed to reach cnt acceptances, or None; prog is iterable of lines"""
        r, m = self.r, self.m
        pos = [0] + [(e - 1) * r for e in range(1, 7)]
        act = [False] * 7
        board = 0
        acc = 0
        P, S = self.P, self.S
        for t, line in enumerate(prog):
            for e in range(1, 7):
                ins = line[e - 1]
                if ins == "F":
                    pos[e] = (pos[e] + 1) % m
                elif ins == "B":
                    pos[e] = (pos[e] - 1) % m
                elif ins == "T":
                    act[e] = not act[e]
            g1 = g2 = g3 = 0
            for e in range(1, 7):
                if act[e]:
                    mm = self.ray[e][pos[e]]
                    g3 |= g2 & mm
                    g2 |= g1 & mm
                    g1 |= mm
            board = (board | (g2 & ~g3)) & ~g3
            if board & P == P and not (board & S):
                board &= ~P
                acc += 1
                if acc == cnt:
                    return t + 1
        return None


def gen(prefix, core, limit):
    for l in prefix:
        yield l
    rc = rev(core)
    n = len(prefix)
    while n < limit:
        for l in rc:
            yield l
        n += len(rc)
        for l in core:
            yield l
        n += len(core)


def gen_rep(prefix, core, limit):
    for l in prefix:
        yield l
    n = len(prefix)
    while n < limit:
        for l in core:
            yield l
        n += len(core)


def compress(geo, pcells, cnt, prog):
    """prog: list of token lists. returns best token-list program (maybe the same)."""
    if cnt < 2:
        return prog
    F = Fast(geo, pcells)
    best = prog
    acc = acc_times(geo, pcells, prog)
    if len(acc) < cnt:
        return prog
    for j in range(min(cnt - 1, 3)):
        t = acc[j] + 1  # prefix length through j-th acceptance
        for s in range(0 if j == 0 else acc[j - 1] + 1, t):
            core = prog[s:t]
            for g in (gen, gen_rep):
                lim = len(best)
                n = F.run(g(prog[:t], core, lim + len(core) * 2), cnt)
                if n is not None and n < len(best):
                    best = list(g(prog[:t], core, n + 2 * len(core)))[:n]
    return best
