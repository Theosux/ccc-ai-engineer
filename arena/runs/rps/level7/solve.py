import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.tourney import make_fight, champion, rig_bracket
import itertools, random

BEATS = {"R": "SL", "P": "RY", "S": "PL", "Y": "SR", "L": "YP"}  # key beats values (RPSLS, Y=Spock)
fight = make_fight(BEATS)


def parse(data):
    t = data.split()
    n = int(t[0])
    return t[2:2 + n]


def solve(data):
    out = []
    for s in parse(data):
        r = rig_bracket(s, "S", BEATS)
        if r is None:
            print("FAILED", s[:40], file=sys.stderr)
        out.append(r or "?")
    return "\n".join(out) + "\n"


def check(data, out):
    lines = out.split()
    for i, s in enumerate(parse(data)):
        o = lines[i]
        if len(o) != len(s) or any(a != "X" and a != b for a, b in zip(s, o)) or "X" in o:
            return False, f"case {i}: {o[:40]}"
        rng = random.Random(i)  # adversary: random fillings + rig_bracket's exact guarantee
        for _ in range(30):
            f = "".join(rng.choice("RPSYL") if ch == "Z" else ch for ch in o)
            if champion(f, fight) != "S":
                return False, f"case {i}: Z-filling {f[:40]} not S"
    return True, ""


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
