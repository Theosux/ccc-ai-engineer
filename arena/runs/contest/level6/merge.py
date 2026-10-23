# Per-pattern best-of merge: python merge.py <file-id> <out1> <out2> ... -> writes best/out_level-6_<id>.txt
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import solve

fid = sys.argv[1]
here = pathlib.Path(__file__).resolve().parent
pats = solve.parse((here / "files" / f"in_level-6_{fid}.txt").read_text())
best = [None] * len(pats)
for path in sys.argv[2:]:
    p = pathlib.Path(path)
    if not p.exists():
        continue
    progs = p.read_text().strip().split("\n\n")
    if len(progs) != len(pats):
        print(f"skip {path}: {len(progs)} programs")
        continue
    for i, ((r, pat, cnt), pr) in enumerate(zip(pats, progs)):
        lines = pr.strip().split("\n")
        if best[i] is not None and len(lines) >= len(best[i]):
            continue
        geo = solve.Geo(r)
        if solve.simulate(geo, solve.pattern_cells(pat), [l.split() for l in lines]) == cnt:
            best[i] = lines
assert all(b is not None for b in best)
out = here / "best" / f"out_level-6_{fid}.txt"
out.write_text("\n\n".join("\n".join(b) for b in best) + "\n")
print(fid, "best total", sum(len(b) for b in best))
