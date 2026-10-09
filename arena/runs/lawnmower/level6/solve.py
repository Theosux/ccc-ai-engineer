import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import Reader, out_lines, find, cells_to_moves, valid_cover, try_symmetries, ham_path


def construct(g, k_off):
    """Cycle: row 0 left->right, then strips over cols 1..W-1 (single rows + one 2-row zigzag band
    holding the tree), alternating direction, ending at (1,H-1), then up column 0 to (0,1)."""
    h, w = len(g), len(g[0])
    tx, ty = find(g, "X")
    k = ty - k_off
    if tx == 0 or ty == 0 or k < 1 or k + 1 > h - 1:
        return None
    cells = [(x, 0) for x in range(w)]
    leftward = True
    y = 1
    while y <= h - 1:
        xs = list(range(w - 1, 0, -1)) if leftward else list(range(1, w))
        if y == k:
            r = k
            for c in xs:
                if g[r][c] != ".":
                    return None
                cells.append((c, r))
                o = 2 * k + 1 - r
                if g[o][c] == ".":
                    cells.append((c, o))
                    r = o
            if r != k + 1:
                return None
            y += 2
        else:
            cells += [(x, y) for x in xs]
            y += 1
        leftward = not leftward
    if cells[-1] != (1, h - 1):
        return None
    cells += [(0, yy) for yy in range(h - 1, 0, -1)]
    return cells_to_moves(cells)


def solve_lawn(g):
    for k_off in (0, 1):
        m = try_symmetries(g, lambda gg: construct(gg, k_off), lambda gr, mo: valid_cover(gr, mo, cycle=True))
        if m:
            return m
    print("fallback", file=sys.stderr)
    p = ham_path(g, time_limit=20, cycle=True)
    return cells_to_moves(p) if p else "FAIL"


def solve(data):
    r = Reader(data)
    out = []
    for _ in range(r.int()):
        w, h = r.ints(2)
        out.append(solve_lawn(r.grid(h)))
    return out_lines(out)


def check(data, out):
    r = Reader(data)
    paths = out.split()
    for i in range(r.int()):
        w, h = r.ints(2)
        g = r.grid(h)
        if not valid_cover(g, paths[i], cycle=True):
            return False, f"case {i} invalid ({w}x{h})"
    return True, f"{len(paths)} cycles valid"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
