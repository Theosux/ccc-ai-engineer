import sys

D = {"W": (0, -1), "D": (1, 0), "S": (0, 1), "A": (-1, 0)}


def solve(data: str) -> str:
    tok = data.split()
    n = int(tok[0])
    out = []
    for path in tok[1:1 + n]:
        x = y = 0
        xs, ys = [0], [0]
        for c in path:
            dx, dy = D[c]
            x += dx
            y += dy
            xs.append(x)
            ys.append(y)
        out.append(f"{max(xs) - min(xs) + 1} {max(ys) - min(ys) + 1}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
