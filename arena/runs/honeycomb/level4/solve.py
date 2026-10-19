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
    start = next((r, row.index("W")) for r, row in enumerate(g) if "W" in row)
    seen, st = {start}, [start]
    while st:  # flood fill over empty cells; FREE if a reached cell borders the outside
        r, c = st.pop()
        for dr, dc in HEX:
            v = at(g, r + dr, c + dc)
            if v is None:
                return "FREE"
            if v == "O" and (r + dr, c + dc) not in seen:
                seen.add((r + dr, c + dc))
                st.append((r + dr, c + dc))
    return "TRAPPED"


if __name__ == "__main__":
    run_cases(cases, solve_case)
