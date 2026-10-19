import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *
from collections import deque


def cases(data):
    return [data]


def parse(d):
    ls = d.split("\n")
    ls = [l.strip() for l in ls if l.strip()]
    n = int(ls[0])
    g = ls[1:1 + n]
    k = int(ls[1 + n])
    qs = [[tuple(map(int, t.split(","))) for t in l.split()] for l in ls[2 + n:2 + n + k]]
    return n, g, qs


def labels(g, ch="L"):
    n, m = len(g), len(g[0])
    lab = [[-1] * m for _ in range(n)]
    k = 0
    for y in range(n):
        for x in range(m):
            if g[y][x] == ch and lab[y][x] < 0:
                lab[y][x] = k
                q = deque([(x, y)])
                while q:
                    a, b = q.popleft()
                    for c, d in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if 0 <= c < m and 0 <= d < n and g[d][c] == ch and lab[d][c] < 0:
                            lab[d][c] = k
                            q.append((c, d))
                k += 1
    return lab


def solve_case(d):
    n, g, qs = parse(d)
    lab = labels(g)
    return "\n".join("SAME" if lab[y1][x1] == lab[y2][x2] else "DIFFERENT" for (x1, y1), (x2, y2) in qs)


if __name__ == "__main__":
    run_cases(cases, solve_case)
