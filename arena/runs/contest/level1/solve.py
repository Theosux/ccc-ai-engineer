import sys


def board(r):
    rows = []
    for i in range(2 * r + 1):
        d = abs(i - r)
        n = 2 * r + 1 - d
        if d == r:
            toks = ["*"] * n
        else:
            toks = ["*"] + ["O"] * (n - 2) + ["*"]
        rows.append("-" * d + "-".join(toks) + "-" * d)
    return "\n".join(rows)


def main():
    t = sys.stdin.read().split()
    n = int(t[0])
    print("\n\n".join(board(int(x)) for x in t[1:1 + n]))


if __name__ == "__main__":
    main()
