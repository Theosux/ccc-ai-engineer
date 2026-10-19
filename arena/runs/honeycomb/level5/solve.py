import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *
import networkx as nx

HEX = [(0, -2), (0, 2), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # (drow, dcol) in the ASCII layout


def cases(data):
    ls = [l.strip() for l in data.strip().splitlines() if l.strip()]
    out, i = [], 1
    for _ in range(int(ls[0])):
        k = int(ls[i]); i += 1
        g = []
        while i < len(ls) and not ls[i].isdigit():
            g.append(ls[i]); i += 1
        out.append((k, g))
    return out


def at(g, r, c):
    return g[r][c] if 0 <= r < len(g) and 0 <= c < len(g[r]) else None


def trapped(g):
    start = next((r, row.index("W")) for r, row in enumerate(g) if "W" in row)
    seen, st = {start}, [start]
    while st:
        r, c = st.pop()
        for dr, dc in HEX:
            v = at(g, r + dr, c + dc)
            if v is None:
                return False
            if v == "O" and (r + dr, c + dc) not in seen:
                seen.add((r + dr, c + dc))
                st.append((r + dr, c + dc))
    return True


def solve_case(case):
    k, g = case
    G = nx.DiGraph()
    W = next((r, row.index("W")) for r, row in enumerate(g) if "W" in row)
    for r, row in enumerate(g):
        for c, ch in enumerate(row):
            if ch not in "OW":
                continue
            if ch == "O":
                G.add_edge(("in", r, c), ("out", r, c), capacity=1)
            u = ("out", r, c) if ch == "O" else "S"
            for dr, dc in HEX:
                v = at(g, r + dr, c + dc)
                if v is None:
                    G.add_edge(u, "T")
                elif v == "O":
                    G.add_edge(u, ("in", r + dr, c + dc))
    cut = []
    if "T" in G and "S" in G:
        val, (S, _) = nx.minimum_cut(G, "S", "T")
        cut = [(r, c) for (r, c) in ((n[1], n[2]) for n in S if isinstance(n, tuple) and n[0] == "in")
               if ("out", r, c) not in S]
    rows = [list(row) for row in g]
    for r, c in cut:
        rows[r][c] = "X"
    return "\n".join("".join(row) for row in rows)


def check(data, out):
    cs = cases(data)
    ls = [l.strip() for l in out.strip().splitlines() if l.strip()]
    if ls[0] != str(len(cs)):
        return False, "first line must be N"
    i = 1
    for n, (k, g) in enumerate(cs):
        h = ls[i:i + len(g)]; i += len(g)
        if len(h) != len(g) or any(len(a) != len(b) for a, b in zip(h, g)):
            return False, f"case {n}: shape"
        added = 0
        for a, b in zip(g, h):
            for x, y in zip(a, b):
                if x != y:
                    if not (x == "O" and y == "X"):
                        return False, f"case {n}: illegal change {x}->{y}"
                    added += 1
        if added > k:
            return False, f"case {n}: {added} barriers > {k}"
        if not trapped(h):
            return False, f"case {n}: not trapped"
    return i == len(ls), "line count"


if __name__ == "__main__":
    run_cases(cases, solve_case, sep="\n\n", header=True)
