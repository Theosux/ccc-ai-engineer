import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *

MV = {"L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)}


def cases(data):
    return [data]


def parse(d):
    r = Reader(d)
    n = r.int()
    g = [list(row) for row in r.grid(n)]
    p = (r.int() - 1, r.int() - 1)
    r.int()
    seq = r.word()
    ghosts = []
    for _ in range(r.int()):
        gp = (r.int() - 1, r.int() - 1)
        r.int()
        ghosts.append((gp, r.word()))
    return g, p, seq, ghosts


def solve_case(d):
    g, (pr, pc), seq, ghosts = parse(d)
    gpos = [gp for gp, _ in ghosts]
    got, alive = 0, True
    for t, m in enumerate(seq):
        dr, dc = MV[m]
        pr, pc = pr + dr, pc + dc
        gpos = [(r + MV[s[t]][0], c + MV[s[t]][1]) if t < len(s) else (r, c) for (r, c), (_, s) in zip(gpos, ghosts)]
        if g[pr][pc] == "W" or (pr, pc) in gpos:
            alive = False
            break
        if g[pr][pc] == "C":
            got += 1
            g[pr][pc] = "."
    return f"{got} {'YES' if alive else 'NO'}"


if __name__ == "__main__":
    run_cases(cases, solve_case)
