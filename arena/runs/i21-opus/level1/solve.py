import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *

def cases(data):
    return [data]

def solve_case(data):
    toks = data.split()[1:]
    out = []
    i = 0
    while i < len(toks):
        if toks[i] == 'print':
            out.append(toks[i+1]); i += 2
        else:
            i += 1
    return ''.join(out)

if __name__ == "__main__":
    run_cases(cases, solve_case)
