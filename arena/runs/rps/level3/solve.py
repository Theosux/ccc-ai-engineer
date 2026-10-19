import sys, random, re

BEATS = {"R": "S", "S": "P", "P": "R"}  # key beats value


def fight(a, b):
    return a if a == b or BEATS[a] == b else b


def rnd(s):
    return "".join(fight(s[i], s[i + 1]) for i in range(0, len(s), 2))


def ok2(s):
    t = rnd(rnd(s))
    return "R" not in t and "S" in t


def parse(data):
    t = data.split()
    n, m = int(t[0]), int(t[1])
    cases = []
    for i in range(n):
        c = {w[-1]: int(w[:-1]) for w in t[2 + 3 * i: 5 + 3 * i]}
        cases.append((m, c))
    return cases


def build(m, c, rng):
    r, p, s = c.get("R", 0), c.get("P", 0), c.get("S", 0)
    blocks = []
    while r >= 3:
        blocks.append("PRRR"); r -= 3; p -= 1
    part = ("P" + "R" * r) if r else ""
    r = 0
    if part:
        p -= 1
    for _ in range(1000):
        pool = list("P" * p + "S" * s)
        rng.shuffle(pool)
        out = "".join(blocks) + part + "".join(pool)
        if ok2(out):
            return out
    return None


def solve(data):
    rng = random.Random(1)
    return "\n".join(build(m, c, rng) or "?" for m, c in parse(data)) + "\n"


def check(data, out):
    lines = out.split()
    for i, (m, c) in enumerate(parse(data)):
        s = lines[i]
        if len(s) != m or any(s.count(k) != v for k, v in c.items()) or not ok2(s):
            return False, f"case {i}: {s[:40]}"
    return True, ""


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
