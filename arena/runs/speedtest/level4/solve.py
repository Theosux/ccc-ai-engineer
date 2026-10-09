import sys


def layout(x, y):
    g = [[0] * x for _ in range(y)]
    d = 0
    for r in range(y):
        for c in range(0, x - x % 3, 3):
            d += 1
            g[r][c] = g[r][c + 1] = g[r][c + 2] = d
    for c in range(x - x % 3, x):
        for r in range(0, y - y % 3, 3):
            d += 1
            g[r][c] = g[r + 1][c] = g[r + 2][c] = d
    return g, d


def solve(data: str) -> str:
    t = list(map(int, data.split()))
    out = []
    for i in range(t[0]):
        x, y, k = t[1 + 3 * i: 4 + 3 * i]
        g, d = layout(x, y)
        if d < k:
            gt, d = layout(y, x)  # gt has x rows, y cols -> transpose
            g = [[gt[c][r] for c in range(x)] for r in range(y)]
        out.append("\n".join(" ".join(map(str, row)) for row in g))
    return "\n\n".join(out) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))


def check(data, out):
    t = list(map(int, data.split()))
    rooms = [l for l in out.strip().split("\n") if l.strip()]
    pos = 0
    for i in range(t[0]):
        x, y, k = t[1 + 3 * i: 4 + 3 * i]
        g = [list(map(int, r.split())) for r in rooms[pos:pos + y]]
        pos += y
        if len(g) != y or any(len(r) != x for r in g):
            return False, f"room {i}: bad shape"
        cells = {}
        for r in range(y):
            for c in range(x):
                if g[r][c]:
                    cells.setdefault(g[r][c], []).append((r, c))
        if sorted(cells) != list(range(1, k + 1)):
            return False, f"room {i}: ids != 1..{k}"
        for d, cs in cells.items():
            rs, cols = {a for a, _ in cs}, {b for _, b in cs}
            if len(cs) != 3 or not ((len(rs) == 1 and max(cols) - min(cols) == 2) or (len(cols) == 1 and max(rs) - min(rs) == 2)):
                return False, f"room {i}: desk {d} not 1x3"
    return True, ""
