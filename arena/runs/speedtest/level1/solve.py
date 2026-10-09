import sys


def solve(data: str) -> str:
    t = data.split()
    n = int(t[0])
    return "\n".join(str(int(t[1 + 2 * i]) // 3 * int(t[2 + 2 * i])) for i in range(n)) + "\n"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
