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


ORDER = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]
IDX = {v: i for i, v in enumerate(ORDER)}


def valid_moves(p):
    return p[0] == 0 and p[-1] == 0 and all(abs(IDX[a] - IDX[b]) <= 1 for a, b in zip(p, p[1:]))


def parse(data):
    d = data.split("\n")
    n = int(d[0])
    cs = []
    for i in range(n):
        xy, lim = d[i + 1].split()
        x, y = map(int, xy.split(","))
        cs.append((x, y, int(lim)))
    return cs


def check(data, out):
    cs = parse(data)
    o = [l for l in out.strip().split("\n") if l.strip()]
    if len(o) != 2 * len(cs):
        return False, "line count"
    for i, (x, y, lim) in enumerate(cs):
        for k, tgt in enumerate((x, y)):
            p = list(map(int, o[2 * i + k].split()))
            pos, t = sim(p)
            if pos != tgt or t > lim or not valid_moves(p):
                return False, f"case {i} axis {k}: pos {pos}/{tgt} t {t}/{lim}"
    return True


if __name__ == "__main__":
    cs = parse(sys.stdin.read())
    print("\n\n".join(" ".join(map(str, seq(x))) + "\n" + " ".join(map(str, seq(y))) for x, y, _ in cs))
