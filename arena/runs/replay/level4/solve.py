import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import Reader, out_lines, find, snake_rows, cells_to_moves, find_cover_start, try_symmetries, ham_path


def construct(g, k_off, entry_bottom):
    """Snake rows above a 2-row band containing the tree, zigzag columns through the band, snake rows below."""
    h, w = len(g), len(g[0])
    t = find(g, "X")
    if t is None:
        return None
    tx, ty = t
    k = ty - k_off  # band = rows k, k+1
    if k < 0 or k + 1 >= h:
        return None
    cells = snake_rows(0, 0, w - 1, k - 1) if k > 0 else []
    left = (k % 2 == 0)  # entering band from the left side?
    if k > 0 and entry_bottom:
        return None
    r = k + (1 if entry_bottom else 0)
    cols = range(w) if left else range(w - 1, -1, -1)
    for c in cols:
        if g[r][c] != ".":
            return None
        cells.append((c, r))
        o = 2 * k + 1 - r
        if g[o][c] == ".":
            cells.append((c, o))
            r = o
    if k + 2 <= h - 1:
        if r != k + 1:
            return None
        start_left = not left  # we're at the far side
        cells += snake_rows(0, k + 2, w - 1, h - 1, start_left=start_left)
    return cells_to_moves(cells)


def ok(g, m):
    return find_cover_start(g, m) is not None


def solve_lawn(g):
    for k_off in (0, 1):
        for eb in (False, True):
            m = try_symmetries(g, lambda gg: construct(gg, k_off, eb), ok)
            if m:
                return m
    p = ham_path(g, time_limit=10)
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
        if find_cover_start(g, paths[i]) is None:
            return False, f"case {i} invalid ({w}x{h})"
    return True, f"{len(paths)} paths valid"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
