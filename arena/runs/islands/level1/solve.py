import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *


def cases(data):
    return [data]


def parse(d):
    ls = d.split()
    n = int(ls[0])
    g = ls[1:1 + n]
    k = int(ls[1 + n])
    rest = ls[2 + n:2 + n + k]
    return n, g, [tuple(map(int, t.split(","))) for t in rest]


def solve_case(d):
    n, g, qs = parse(d)
    return "\n".join(g[y][x] for x, y in qs)


if __name__ == "__main__":
    run_cases(cases, solve_case)
