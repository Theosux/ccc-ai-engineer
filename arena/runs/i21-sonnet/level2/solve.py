import sys
t = sys.stdin.read().split()[1:]
pos = 0

def block():
    global pos
    stmts = []
    while pos < len(t) and t[pos] not in ("end",):
        k = t[pos]
        if k == "print":
            stmts.append(("print", t[pos + 1])); pos += 2
        elif k == "return":
            stmts.append(("return", t[pos + 1])); pos += 2
        elif k == "if":
            c = t[pos + 1]; pos += 2
            a = block(); pos += 1  # end
            assert t[pos] == "else"; pos += 1
            b = block(); pos += 1  # end
            stmts.append(("if", c, a, b))
        else:
            raise Exception("unknown " + k)
    return stmts

assert t[0] == "start"
pos = 1
prog = block()
out = []

def run(stmts):
    for s in stmts:
        if s[0] == "print":
            out.append(s[1])
        elif s[0] == "return":
            return True
        else:
            if run(s[2] if s[1] == "true" else s[3]):
                return True
    return False

run(prog)
sys.stdout.write("".join(out))
