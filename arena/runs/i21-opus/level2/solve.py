import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import *

def cases(data):
    return [data]

def parse_block(toks, i):
    # parse statements until 'end'; returns (stmts, index after 'end')
    stmts = []
    while toks[i] != 'end':
        t = toks[i]
        if t == 'print':
            stmts.append(('print', toks[i+1])); i += 2
        elif t == 'return':
            stmts.append(('return', toks[i+1])); i += 2
        elif t == 'if':
            cond = toks[i+1]
            a, i = parse_block(toks, i+2)
            assert toks[i] == 'else'
            b, i = parse_block(toks, i+1)
            stmts.append(('if', cond, a, b))
        else:
            raise ValueError('unknown ' + t)
    return stmts, i+1

class Ret(Exception):
    def __init__(self, v): self.v = v

def run(stmts, out):
    for s in stmts:
        if s[0] == 'print':
            out.append(s[1])
        elif s[0] == 'return':
            raise Ret(s[1])
        elif s[0] == 'if':
            run(s[2] if s[1] == 'true' else s[3], out)

def solve_case(data):
    toks = data.split()[1:]
    i = 0
    res = []
    while i < len(toks):
        assert toks[i] == 'start'
        body, i = parse_block(toks, i+1)
        out = []
        try:
            run(body, out)
        except Ret:
            pass
        res.append(''.join(out))
    return '\n'.join(res)

if __name__ == "__main__":
    run_cases(cases, solve_case)
