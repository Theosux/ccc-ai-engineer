import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib import Reader, out_lines, cells_to_moves, valid_cover, ham_cycle, ham_path


def solve_lawn(g):
    p = ham_cycle(g, time_limit=120)
    if not p:
        print("FAIL", len(g[0]), len(g), file=sys.stderr)
    return cells_to_moves(p) if p else "FAIL"


def solve(data):
    r = Reader(data)
    out = []
    for _ in range(r.int()):
        w, h = r.ints(2)
        out.append(solve_lawn(r.grid(h)))
    return out_lines(out)


def check(data, out):
    r = Reader(data)
    paths = out.split()
    bad = []
    for i in range(r.int()):
        w, h = r.ints(2)
        g = r.grid(h)
        if not valid_cover(g, paths[i], cycle=True):
            bad.append(i)
    return not bad, f"bad cases {bad}"


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
