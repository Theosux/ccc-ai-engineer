import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.pack import pack_rects, render_rects, check_rects_grid

GAP = 1


def rooms(data):
    t = list(map(int, data.split()))
    return [t[1 + 4 * i: 5 + 4 * i] for i in range(t[0])]


def solve(data):
    out = []
    for x, y, k, s in rooms(data):
        R = pack_rects(x, y, [(s, 1)], gap=GAP, target=k)[:k]
        out.append("\n".join(render_rects(x, y, R)))
    return "\n\n".join(out) + "\n"


def check(data, out):
    rows = [l.strip() for l in out.split("\n") if l.strip()]
    pos = 0
    for i, (x, y, k, s) in enumerate(rooms(data)):
        g = rows[pos:pos + y]; pos += y
        ok, msg = check_rects_grid(g, x, y, [(s, 1)], GAP, k)
        if not ok:
            return False, f"room {i} ({x}x{y},{k},{s}): {msg}"
    return pos == len(rows), "extra lines"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
