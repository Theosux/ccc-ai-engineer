import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *


def cases(data):
    return [data]


def parse(d):
    ls = [l.strip() for l in d.split("\n") if l.strip()]
    n = int(ls[0])
    g = ls[1:1 + n]
    k = int(ls[1 + n])
    qs = [[tuple(map(int, t.split(","))) for t in l.split()] for l in ls[2 + n:2 + n + k]]
    return n, g, qs


def route_ok(path):
    """No tile twice, no two diagonal steps crossing in the same 2x2 square."""
    if len(set(path)) != len(path):
        return False
    diag = set()
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        if x1 != x2 and y1 != y2:
            if frozenset(((x2, y1), (x1, y2))) in diag:
                return False
            diag.add(frozenset(((x1, y1), (x2, y2))))
    return True


def solve_case(d):
    n, g, qs = parse(d)
    return "\n".join("VALID" if route_ok(p) else "INVALID" for p in qs)


if __name__ == "__main__":
    run_cases(cases, solve_case)
