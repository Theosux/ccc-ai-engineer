import sys


def solve(data: str) -> str:
    lines = data.strip().splitlines()
    n = int(lines[0])
    return "\n".join(str(sum(map(int, l.split()))) for l in lines[1:1 + n]) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
