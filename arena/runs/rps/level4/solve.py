import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.tourney import make_fight, champion, build_bracket

BEATS = {"R": "S", "S": "P", "P": "R"}  # key beats value
fight = make_fight(BEATS)


def parse(data):
    t = data.split()
    n, m = int(t[0]), int(t[1])
    return [(m, {w[-1]: int(w[:-1]) for w in t[2 + 3 * i: 5 + 3 * i]}) for i in range(n)]


def solve(data):
    out = []
    for m, c in parse(data):
        s = build_bracket(c, "S", BEATS)
        if s is None:
            print("FAILED", m, c, file=sys.stderr)
        out.append(s or "?")
    return "\n".join(out) + "\n"


def check(data, out):
    lines = out.split()
    for i, (m, c) in enumerate(parse(data)):
        s = lines[i]
        if len(s) != m or any(s.count(k) != v for k, v in c.items()) or champion(s, fight) != "S":
            return False, f"case {i}: {c} {s[:40]}"
    return True, ""


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
