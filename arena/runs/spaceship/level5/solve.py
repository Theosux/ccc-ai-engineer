import sys

ORDER = [-1, -2, -3, -4, -5, 0, 5, 4, 3, 2, 1]
AREA = 2  # collision if |dx| <= 2 and |dy| <= 2 (visualizer hasShipCollided)


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


def dur(seq):
    return sum(abs(p) if p else 1 for p in seq)


def ticks(seq):
    """Per-tick position deltas: pace p lasts |p| ticks (0 -> 1 tick); the step happens on its last tick."""
    out = []
    for p in seq:
        n = abs(p) if p else 1
        out += [0] * (n - 1) + [(p > 0) - (p < 0)]
    return out


def simulate(xs, ys):
    dx, dy = ticks(xs), ticks(ys)
    T = max(len(dx), len(dy))
    x = y = 0
    pos = [(0, 0)]
    for t in range(T):
        x += dx[t] if t < len(dx) else 0
        y += dy[t] if t < len(dy) else 0
        pos.append((x, y))
    return pos


def collides(pos, asts):
    return any(abs(px - ax) <= AREA and abs(py - ay) <= AREA for px, py in pos for ax, ay in asts)


def build(waypoints):
    """Axis-aligned legs from (0,0) through waypoints; the idle axis waits with zeros."""
    xs, ys = [0], [0]
    cx = cy = 0
    for wx, wy in waypoints:
        if wx != cx:
            s = seq_for(wx - cx)
            xs += s
            ys += [0] * dur(s)
            cx = wx
        if wy != cy:
            s = seq_for(wy - cy)
            ys += s
            xs += [0] * dur(s)
            cy = wy
    return xs, ys


def candidates(tx, ty, asts):
    yield [(tx, 0), (tx, ty)]
    yield [(0, ty), (tx, ty)]
    offs = sorted({a[1] + d for a in asts for d in (-3, 3, -4, 4)} | {a[0] + d for a in asts for d in (-3, 3, -4, 4)}
                  | set(range(-20, 21)), key=abs)
    for c in offs:
        yield [(0, c), (tx, c), (tx, ty)]
        yield [(c, 0), (c, ty), (tx, ty)]


def plan(tx, ty, lim, asts):
    for wps in candidates(tx, ty, asts):
        xs, ys = build(wps)
        if max(dur(xs), dur(ys)) > lim:
            continue
        if not collides(simulate(xs, ys), asts):
            return xs, ys
    raise RuntimeError(f"no plan for {tx},{ty} lim {lim} asts {asts}")


def parse(data):
    lines = [l for l in data.strip().splitlines() if l.strip()]
    n = int(lines[0])
    cases, i = [], 1
    for _ in range(n):
        xy, lim = lines[i].split()
        tx, ty = map(int, xy.split(","))
        ax, ay = map(int, lines[i + 1].split(","))
        cases.append((tx, ty, int(lim), [(ax, ay)]))
        i += 2
    return cases


def solve(data: str) -> str:
    out = []
    for tx, ty, lim, asts in parse(data):
        xs, ys = plan(tx, ty, lim, asts)
        out.append(" ".join(map(str, xs)) + "\n" + " ".join(map(str, ys)) + "\n")
    return "\n".join(out)


def valid_seq(seq):
    if seq[0] != 0 or seq[-1] != 0:
        return "must start/end with 0"
    for a, b in zip(seq, seq[1:]):
        if abs(ORDER.index(a) - ORDER.index(b)) > 1:
            return f"bad step {a}->{b}"
    return ""


def check(data, out):
    cases = parse(data)
    outs = [o for o in out.strip().splitlines() if o.strip()]
    if len(outs) != 2 * len(cases):
        return False, f"{len(outs)} lines, want {2 * len(cases)}"
    for i, (tx, ty, lim, asts) in enumerate(cases):
        xs, ys = list(map(int, outs[2 * i].split())), list(map(int, outs[2 * i + 1].split()))
        for s in (xs, ys):
            e = valid_seq(s)
            if e:
                return False, f"case {i}: {e}"
        if max(dur(xs), dur(ys)) > lim:
            return False, f"case {i}: time {max(dur(xs), dur(ys))} > {lim}"
        pos = simulate(xs, ys)
        if pos[-1] != (tx, ty):
            return False, f"case {i}: ends at {pos[-1]} not {(tx, ty)}"
        if collides(pos, asts):
            return False, f"case {i}: collision"
    return True


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
