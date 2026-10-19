import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *


def cases(data):
    return [data]


def solve_case(d):
    return str(d.count("O"))


if __name__ == "__main__":
    run_cases(cases, solve_case)
