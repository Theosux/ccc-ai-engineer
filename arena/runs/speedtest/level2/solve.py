import sys


def solve(data: str) -> str:
    t = list(map(int, data.split()))
    n, out = t[0], []
    for i in range(n):
        x, y, k = t[1 + 3 * i: 4 + 3 * i]
        per = x // 3
        rows = []
        for r in range(y):
            rows.append(" ".join(str(r * per + c // 3 + 1) for c in range(x)))
        out.append("\n".join(rows))
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
