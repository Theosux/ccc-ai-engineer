import sys

DIRS = {1: (0, 2), 2: (1, 1), 3: (1, -1), 4: (0, -2), 5: (-1, -1), 6: (-1, 1)}


def ring(r):
    # border cells clockwise, starting at left corner (r, 0)
    cells = []
    y, x = r, 0
    moves = [(-1, 1), (0, 2), (1, 1), (1, -1), (0, -2), (-1, -1)]
    for dy, dx in moves:
        for _ in range(r):
            cells.append((y, x))
            y += dy; x += dx
    return cells


def parse(data):
    t = data.split("\n")
    lines = [l.strip() for l in t if l.strip()]
    n = int(lines[0]); i = 1
    progs = []
    for _ in range(n):
        r = int(lines[i].split()[0]); hh = int(lines[i].split()[1]); i += 1
        pat = lines[i:i + hh]; i += hh
        L = int(lines[i]); i += 1
        prog = [lines[i + k].split() for k in range(L)]
        i += L
        progs.append((r, pat, prog))
    return progs


def simulate(r, pat, prog):
    pcells = {(y, x) for y, row in enumerate(pat) for x, ch in enumerate(row) if ch == "M"}
    nb = set()
    for (y, x) in pcells:
        for dy, dx in ((0, 2), (0, -2), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            c = (y + dy, x + dx)
            if c not in pcells:
                nb.add(c)
    subs = 0
    h, w = 2 * r + 1, 4 * r + 1
    rg = ring(r)
    idx = {c: k for k, c in enumerate(rg)}
    # corners: 1 left (r,0), 2 top-left (0,r), 3 top-right (0,3r), 4 right (r,4r), 5 bottom-right (2r,3r), 6 bottom-left (2r,r)
    corner = {1: (r, 0), 2: (0, r), 3: (0, 3 * r), 4: (r, 4 * r), 5: (2 * r, 3 * r), 6: (2 * r, r)}
    pos = {e: idx[corner[e]] for e in range(1, 7)}
    act = {e: False for e in range(1, 7)}
    interior = set()
    for y in range(1, 2 * r):
        d = abs(y - r)
        n = 2 * r + 1 - d
        for k in range(1, n - 1):
            interior.add((y, d + 2 * k))
    matter = set()
    m = len(rg)
    for line in prog:
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
            if not act[e]:
                continue
            dy, dx = DIRS[e]
            y, x = rg[pos[e]]
            y += dy; x += dx
            while 0 <= y < h and 0 <= x < w:
                if (y, x) in interior:
                    cnt[(y, x)] = cnt.get((y, x), 0) + 1
                y += dy; x += dx
        for c, k in cnt.items():
            if k == 2:
                matter.add(c)
            elif k >= 3:
                matter.discard(c)
        if pcells <= matter and not (nb & matter):
            matter -= pcells
            subs += 1
    return str(subs)
    rows = []
    for y in range(h):
        d = abs(y - r)
        n = 2 * r + 1 - d
        toks = []
        for k in range(n):
            c = (y, d + 2 * k)
            if c in interior:
                toks.append("M" if c in matter else "O")
            else:
                toks.append("*")
        rows.append("-" * d + "-".join(toks) + "-" * d)
    return "\n".join(rows)


def main():
    print("\n".join(simulate(*a) for a in parse(sys.stdin.read())))


if __name__ == "__main__":
    main()
