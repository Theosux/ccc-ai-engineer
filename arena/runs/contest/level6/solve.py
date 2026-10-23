# ccc: pypy
import sys

DIRS = {1: (0, 2), 2: (1, 1), 3: (1, -1), 4: (0, -2), 5: (-1, -1), 6: (-1, 1)}
NB = ((0, 2), (0, -2), (1, 1), (1, -1), (-1, 1), (-1, -1))


def ring(r):
    cells = []
    y, x = r, 0
    for dy, dx in [(-1, 1), (0, 2), (1, 1), (1, -1), (0, -2), (-1, -1)]:
        for _ in range(r):
            cells.append((y, x))
            y += dy; x += dx
    return cells


def parse(data):
    lines = [l.strip() for l in data.split("\n") if l.strip()]
    n = int(lines[0]); i = 1
    pats = []
    for _ in range(n):
        r, h, w, cnt = map(int, lines[i].split()); i += 1
        pat = lines[i:i + h]; i += h
        pats.append((r, pat, cnt))
    return pats


def pattern_cells(pat):
    return {(y, x) for y, row in enumerate(pat) for x, ch in enumerate(row) if ch == "M"}


class Geo:
    def __init__(self, r):
        self.r = r
        self.h, self.w = 2 * r + 1, 4 * r + 1
        self.rg = ring(r)
        self.m = len(self.rg)
        self.idx = {c: k for k, c in enumerate(self.rg)}
        self.interior = set()
        for y in range(1, 2 * r):
            d = abs(y - r)
            n = 2 * r + 1 - d
            for k in range(1, n - 1):
                self.interior.add((y, d + 2 * k))
        # ray cells (interior only) for (ring idx, emitter)
        self.rays = {}
        for k, (y0, x0) in enumerate(self.rg):
            for e, (dy, dx) in DIRS.items():
                cells = []
                y, x = y0 + dy, x0 + dx
                while 0 <= y < self.h and 0 <= x < self.w:
                    if (y, x) in self.interior:
                        cells.append((y, x))
                    y += dy; x += dx
                self.rays[(k, e)] = cells


def simulate(geo, pcells, prog):
    """Exact sandbox semantics. Returns number of accepted patterns."""
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
    return acc


class Prog:
    def __init__(self, geo):
        self.geo = geo
        r = geo.r
        self.pos = [0] + [(e - 1) * r for e in range(1, 7)]
        self.act = [False] * 7
        self.lines = []

    def emit(self, line):
        # line: dict e -> ins
        for e, ins in line.items():
            if ins == "F":
                self.pos[e] = (self.pos[e] + 1) % self.geo.m
            elif ins == "B":
                self.pos[e] = (self.pos[e] - 1) % self.geo.m
            elif ins == "T":
                self.act[e] = not self.act[e]
        self.lines.append(" ".join(line.get(e, "-") for e in range(1, 7)))

    def moves(self, e, target):
        m = self.geo.m
        f = (target - self.pos[e]) % m
        b = (self.pos[e] - target) % m
        return ["F"] * f if f <= b else ["B"] * b


def plan_baseline(geo, pcells, P):
    """Rows with emitter 1 (row beam) x emitter 3 (diag beam), snake order."""
    r = geo.r
    rows = {}
    for (y, x) in pcells:
        rows.setdefault(y, []).append(x)
    order = sorted(rows)
    segs = []  # list of (row idx for emitter1, list of emitter3 ring idx in creation order)
    for i, y in enumerate(order):
        xs = sorted(rows[y])
        if i % 2 == 1:
            xs = xs[::-1]
        runs = []
        for x in xs:
            if runs and abs(x - runs[-1][-1]) == 2:
                runs[-1].append(x)
            else:
                runs.append([x])
        e1 = geo.idx[(y, abs(y - r))]
        for run in runs:
            segs.append((e1, [(x + y + r) // 2 for x in run]))
    for e1, s3 in segs:
        seq1 = []
        if P.act[1]:
            seq1.append("T")
        seq1 += P.moves(1, e1)
        seq1.append("T")
        mv3 = P.moves(3, s3[0])
        if not P.act[3]:
            mv3 = ["T"] + mv3
        L = max(len(seq1), len(mv3))
        seq1 = seq1[:-1] + ["-"] * (L - len(seq1)) + ["T"]
        seq3 = ["-"] * (L - len(mv3)) + mv3
        for k in range(L):
            line = {}
            if seq1[k] != "-":
                line[1] = seq1[k]
            if seq3[k] != "-":
                line[3] = seq3[k]
            P.emit(line)
        for s in s3[1:]:
            P.emit({3: P.moves(3, s)[0]})


def solve_one(r, pat, cnt):
    geo = Geo(r)
    pcells = pattern_cells(pat)
    P = Prog(geo)
    for _ in range(cnt):
        plan_baseline(geo, pcells, P)
    best = P.lines
    import sweep
    for fn in (sweep.best_sweep, sweep.best_sweep2):
        try:
            s = fn(geo, pcells, cnt)
            if s is not None and len(s) < len(best):
                best = s
        except Exception as ex:  # keep baseline on any planner bug
            sys.stderr.write(f"sweep error: {ex!r}\n")
    return best


def solve_case(c):
    return "\n".join(solve_one(*c))


def check(data, out):
    pats = parse(data)
    progs = [b.strip().split("\n") for b in out.strip().split("\n\n")]
    if len(progs) != len(pats):
        return False, f"{len(progs)} programs for {len(pats)} patterns"
    total = 0
    for i, ((r, pat, cnt), prog) in enumerate(zip(pats, progs)):
        geo = Geo(r)
        rows = [l.split() for l in prog]
        if any(len(l) != 6 or any(t not in "FBT-" for t in l) for l in rows):
            return False, f"pattern {i}: bad line"
        acc = simulate(geo, pattern_cells(pat), rows)
        if acc != cnt:
            return False, f"pattern {i}: accepted {acc} != {cnt}"
        total += len(rows)
    return True, f"score {total}"


def main():
    data = sys.stdin.read()
    out = []
    for r, pat, cnt in parse(data):
        out.append("\n".join(solve_one(r, pat, cnt)))
    print("\n\n".join(out))


if __name__ == "__main__":
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
    from lib.runner import run_cases
    run_cases(parse, solve_case, sep="\n\n")
