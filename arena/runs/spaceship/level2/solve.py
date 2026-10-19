import sys


def solve(data: str) -> str:
    lines = data.strip().splitlines()
    n = int(lines[0])
    out = []
    for l in lines[1:1 + n]:
        ps = list(map(int, l.split()))
        pos = sum((p > 0) - (p < 0) for p in ps)
        t = sum(abs(p) if p else 1 for p in ps)
        out.append(f"{pos} {t}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
