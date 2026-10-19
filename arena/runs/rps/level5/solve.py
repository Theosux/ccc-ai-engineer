import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.tourney import make_fight, champion, build_bracket

BEATS = {"R": "SL", "P": "RY", "S": "PL", "Y": "SR", "L": "YP"}  # key beats values (RPSLS, Y=Spock)
fight = make_fight(BEATS)


def parse(data):
    L = data.strip().splitlines()
    n, m = map(int, L[0].split())
    return [(m, {w[-1]: int(w[:-1]) for w in L[1 + i].split()}) for i in range(n)]


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
