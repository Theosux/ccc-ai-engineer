import sys

BEATS = {"R": "S", "S": "P", "P": "R"}  # key beats value


def fight(a, b):
    return a if a == b or BEATS[a] == b else b


def solve(data):
    t = data.split()
    return "\n".join(fight(s[0], s[1]) for s in t[1:1 + int(t[0])]) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
