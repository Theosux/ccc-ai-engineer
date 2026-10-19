import sys

ORDER = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]


def seq_for(x):
    """Fastest 1-D sequence from 0 to x: ramp 5..k, cruise at k, ramp back to 5, framed by 0s."""
    if x == 0:
        return [0]
    d, s = abs(x), (1 if x > 0 else -1)
    best = None
    for k in range(1, 6):
        up = list(range(5, k - 1, -1))          # 5,4,...,k
        down = list(range(k + 1, 6))            # k+1..5
        base = len(up) + len(down)
        if base > d:
            continue
        mid = [k] * (d - base)
        seq = up + mid + down
        t = sum(seq)
        if best is None or t < best[0]:
            best = (t, seq)
    return [0] + [s * p for p in best[1]] + [0]


def solve(data: str) -> str:
    lines = data.strip().splitlines()
    n = int(lines[0])
    out = []
    for l in lines[1:1 + n]:
        x, lim = map(int, l.split())
        out.append(" ".join(map(str, seq_for(x))))
    return "\n".join(out) + "\n"


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
    lines = data.strip().splitlines()
    outs = out.strip().splitlines()
    n = int(lines[0])
    if len(outs) != n:
        return False, f"{len(outs)} lines, want {n}"
    for i, (l, o) in enumerate(zip(lines[1:1 + n], outs)):
        x, lim = map(int, l.split())
        ok, msg = valid(list(map(int, o.split())), x, lim)
        if not ok:
            return False, f"case {i}: {msg}"
    return True


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
