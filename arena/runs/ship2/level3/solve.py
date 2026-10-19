import sys


def seq(x):
    if x == 0:
        return [0]
    s = 1 if x > 0 else -1
    a = abs(x)
    best = None
    for p in range(5, 0, -1):
        need = 11 - 2 * p
        if a < need:
            continue
        body = list(range(5, p - 1, -1)) + [p] * (a - need) + list(range(p + 1, 6))
        t = sum(body)
        if best is None or t < best[0]:
            best = (t, body)
    return [0] + [s * v for v in best[1]] + [0]


def sim(p):
    return sum((x > 0) - (x < 0) for x in p), sum(abs(x) if x else 1 for x in p)


def valid_moves(p):
    order = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]
    idx = {v: i for i, v in enumerate(order)}
    return p[0] == 0 and p[-1] == 0 and all(abs(idx[a] - idx[b]) <= 1 for a, b in zip(p, p[1:]))


def check(data, out):
    d = data.split("\n")
    o = out.strip().split("\n")
    n = int(d[0])
    if len(o) != n:
        return False, "line count"
    for i in range(n):
        x, lim = map(int, d[i + 1].split())
        p = list(map(int, o[i].split()))
        pos, t = sim(p)
        if pos != x or t > lim or not valid_moves(p):
            return False, f"case {i}: pos {pos}/{x} t {t}/{lim}"
    return True


if __name__ == "__main__":
    d = sys.stdin.read().split("\n")
    n = int(d[0])
    print("\n".join(" ".join(map(str, seq(int(d[i + 1].split()[0])))) for i in range(n)))
