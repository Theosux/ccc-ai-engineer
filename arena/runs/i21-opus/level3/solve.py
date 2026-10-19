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
        elif t in ('var', 'set'):
            stmts.append((t, toks[i+1], toks[i+2])); i += 3
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

class Err(Exception):
    pass

def val(t, env):
    return env[t] if t in env else t

def run(stmts, out, env):
    for s in stmts:
        if s[0] == 'print':
            out.append(val(s[1], env))
        elif s[0] == 'return':
            raise Ret(val(s[1], env))
        elif s[0] == 'var':
            if s[1] in env: raise Err()
            env[s[1]] = val(s[2], env)
        elif s[0] == 'set':
            if s[1] not in env: raise Err()
            env[s[1]] = val(s[2], env)
        elif s[0] == 'if':
            c = val(s[1], env)
            if c not in ('true', 'false'): raise Err()
            run(s[2] if c == 'true' else s[3], out, env)

def solve_case(data):
    toks = data.split()[1:]
    i = 0
    res = []
    while i < len(toks):
        assert toks[i] == 'start'
        body, i = parse_block(toks, i+1)
        out = []
        try:
            run(body, out, {})
            res.append(''.join(out))
        except Ret:
            res.append(''.join(out))
        except Err:
            res.append('ERROR')
    return '\n'.join(res)

if __name__ == "__main__":
    run_cases(cases, solve_case)
