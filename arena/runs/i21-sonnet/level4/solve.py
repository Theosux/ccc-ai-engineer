import sys
from collections import deque
sys.setrecursionlimit(100000)
t = sys.stdin.read().split()[1:]
pos = 0

def block():
    global pos
    stmts = []
    while pos < len(t) and t[pos] != "end":
        k = t[pos]
        if k in ("print", "return"):
            stmts.append((k, t[pos + 1])); pos += 2
        elif k in ("var", "set"):
            stmts.append((k, t[pos + 1], t[pos + 2])); pos += 3
        elif k == "postpone":
            pos += 1
            b = block(); pos += 1
            stmts.append(("postpone", b))
        elif k == "if":
            c = t[pos + 1]; pos += 2
            a = block(); pos += 1
            assert t[pos] == "else"; pos += 1
            b = block(); pos += 1
            stmts.append(("if", c, a, b))
        else:
            raise Exception("unknown " + k)
    return stmts

class Err(Exception):
    pass

def run_fn(stmts):
    vars_ = {}
    out = []
    def val(tok):
        return vars_.get(tok, tok)
    def run(ss):
        q = deque(ss)
        while q:
            s = q.popleft()
            k = s[0]
            if k == "print":
                out.append(val(s[1]))
            elif k == "return":
                return True
            elif k == "postpone":
                q.extend(s[1])
            elif k == "var":
                if s[1] in vars_:
                    raise Err()
                vars_[s[1]] = val(s[2])
            elif k == "set":
                if s[1] not in vars_:
                    raise Err()
                vars_[s[1]] = val(s[2])
            else:
                c = val(s[1])
                if c not in ("true", "false"):
                    raise Err()
                if run(s[2] if c == "true" else s[3]):
                    return True
        return False
    try:
        run(stmts)
    except Err:
        return "ERROR"
    return "".join(out)

res = []
while pos < len(t):
    assert t[pos] == "start"
    pos += 1
    b = block()
    pos += 1
    res.append(run_fn(b))
sys.stdout.write("\n".join(res))
