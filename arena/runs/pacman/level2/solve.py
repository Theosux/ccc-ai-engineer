import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *

MV = {"L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)}


def cases(data):
    return [data]


def solve_case(d):
    r = Reader(d)
    n = r.int()
    g = [list(row) for row in r.grid(n)]
    pr, pc = r.int() - 1, r.int() - 1
    r.int()
    seq = "".join(r.rest())
    got = 0
    for m in seq:
        dr, dc = MV[m]
        pr, pc = pr + dr, pc + dc
        if g[pr][pc] == "C":
            got += 1
            g[pr][pc] = "."
    return str(got)


if __name__ == "__main__":
    run_cases(cases, solve_case)
