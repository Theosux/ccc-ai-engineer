import sys

D = {"W": (0, -1), "D": (1, 0), "S": (0, 1), "A": (-1, 0)}


def valid(w, h, grid, path):
    free = sum(row.count(".") for row in grid)
    if len(path) + 1 != free:
        return False
    for sy in range(h):
        for sx in range(w):
            if grid[sy][sx] != ".":
                continue
            x, y = sx, sy
            seen = {(x, y)}
            ok = True
            for c in path:
                dx, dy = D[c]
                x += dx
                y += dy
                if not (0 <= x < w and 0 <= y < h) or grid[y][x] != "." or (x, y) in seen:
                    ok = False
                    break
                seen.add((x, y))
            if ok:
                return True
    return False


def solve(data: str) -> str:
    tok = data.split()
    i = 0
    n = int(tok[i]); i += 1
    out = []
    for _ in range(n):
        w, h = int(tok[i]), int(tok[i + 1]); i += 2
        grid = tok[i:i + h]; i += h
        path = tok[i]; i += 1
        out.append("VALID" if valid(w, h, grid, path) else "INVALID")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
