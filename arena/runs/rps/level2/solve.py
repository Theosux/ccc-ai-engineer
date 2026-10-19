import sys

BEATS = {"R": "S", "S": "P", "P": "R"}  # key beats value


def fight(a, b):
    return a if a == b or BEATS[a] == b else b


def rnd(s):
    return "".join(fight(s[i], s[i + 1]) for i in range(0, len(s), 2))


def solve(data):
    t = data.split()
    n = int(t[0])
    return "\n".join(rnd(rnd(s)) for s in t[2:2 + n]) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
