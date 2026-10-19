import sys

ORDER = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]


def seq_for(x):
    """Fastest 1-D sequence from 0 to x: ramp 5..k, cruise at k, ramp back to 5, framed by 0s."""
    if x == 0:
        return [0]
    d, s = abs(x), (1 if x > 0 else -1)
    best = None
    for k in range(1, 6):
        up = list(range(5, k - 1, -1))
        down = list(range(k + 1, 6))
        base = len(up) + len(down)
        if base > d:
            continue
        seq = up + [k] * (d - base) + down
        t = sum(seq)
        if best is None or t < best[0]:
            best = (t, seq)
    return [0] + [s * p for p in best[1]] + [0]


def parse(data):
    lines = data.strip().splitlines()
    n = int(lines[0])
    cases = []
    for l in lines[1:1 + n]:
        xy, lim = l.split()
        x, y = map(int, xy.split(","))
        cases.append((x, y, int(lim)))
    return cases


def solve(data: str) -> str:
    out = []
    for x, y, lim in parse(data):
        out.append(" ".join(map(str, seq_for(x))) + "\n" + " ".join(map(str, seq_for(y))) + "\n")
    return "\n".join(out)


def valid(seq, x, lim):
    if seq[0] != 0 or seq[-1] != 0:
        return False, "must start/end with 0"
    for a, b in zip(seq, seq[1:]):
        if abs(ORDER.index(a) - ORDER.index(b)) > 1:
            return False, f"bad step {a}->{b}"
    pos = sum((p > 0) - (p < 0) for p in seq)
    t = sum(abs(p) if p else 1 for p in seq)
    if pos != x:
        return False, f"pos {pos} != {x}"
    if t > lim:
        return False, f"time {t} > {lim}"
    return True, ""


def check(data, out):
    cases = parse(data)
    outs = [o for o in out.strip().splitlines() if o.strip()]
    if len(outs) != 2 * len(cases):
        return False, f"{len(outs)} lines, want {2 * len(cases)}"
    for i, (x, y, lim) in enumerate(cases):
        for axis, target, o in (("x", x, outs[2 * i]), ("y", y, outs[2 * i + 1])):
            ok, msg = valid(list(map(int, o.split())), target, lim)
            if not ok:
                return False, f"case {i} {axis}: {msg}"
    return True


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
