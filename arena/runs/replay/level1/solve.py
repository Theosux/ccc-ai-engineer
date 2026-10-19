import sys


def solve(data: str) -> str:
    lines = data.split()
    n = int(lines[0])
    out = []
    for path in lines[1:1 + n]:
        out.append(" ".join(str(path.count(c)) for c in "WDSA"))
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
