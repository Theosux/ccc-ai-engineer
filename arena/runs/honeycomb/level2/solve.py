import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *

HEX = [(0, -2), (0, 2), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # (drow, dcol) in the ASCII layout


def cases(data):
    ls = [l.strip() for l in data.strip().splitlines()]
    n = int(ls[0])
    rows = [l for l in ls[1:] if l]
    h = len(rows) // n
    return [rows[i * h:(i + 1) * h] for i in range(n)]


def at(g, r, c):
    return g[r][c] if 0 <= r < len(g) and 0 <= c < len(g[r]) else None


def solve_case(g):
    r, c = next((r, row.index("W")) for r, row in enumerate(g) if "W" in row)
    return str(sum(at(g, r + dr, c + dc) == "O" for dr, dc in HEX))


if __name__ == "__main__":
    run_cases(cases, solve_case)
