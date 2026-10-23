# Cycle compression: if the full state repeats at two acceptance ticks, repeat the cheapest cycle.
from solve import NB


def trace(geo, pcells, prog):
    r = geo.r
    pos = [0] + [(e - 1) * r for e in range(1, 7)]
    act = [False] * 7
    skirt = set()
    for (y, x) in pcells:
        for dy, dx in NB:
            c = (y + dy, x + dx)
            if c not in pcells and c in geo.interior:
                skirt.add(c)
    matter = set()
    acc = 0
    m = geo.m
    marks = [(0, 0, (tuple(pos), tuple(act)))]
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
            acc += 1
            marks.append((t + 1, acc, (tuple(pos), tuple(act))))
    return marks


def compress(geo, pcells, cnt, lines):
    prog = [l.split() for l in lines]
    marks = trace(geo, pcells, prog)
    if len(marks) < 3:
        return lines
    best = None
    first = {}
    for t, a, s in marks:
        if s in first:
            t0, a0 = first[s]
            k = a - a0
            if k > 0:
                rate = (t - t0) / k
                if best is None or rate < best[0]:
                    best = (rate, t0, a0, t, a)
        else:
            first[s] = (t, a)
    if best is None:
        return lines
    _, t0, a0, t1, a1 = best
    k = a1 - a0
    R = cnt - a0
    q = R // k
    rem = R - q * k
    tail = []
    if rem:
        # continue original program from t0 until rem more acceptances
        need = a0 + rem
        tend = None
        for t, a, s in marks:
            if a == need:
                tend = t
                break
        tail = lines[t0:tend]
    new = lines[:t0] + lines[t0:t1] * q + tail
    return new if len(new) < len(lines) else lines
