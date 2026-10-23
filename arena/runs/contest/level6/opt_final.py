# usage: pypy3 opt_final.py <fid>: per-pattern min of best/ + cand/opt_* (verified) -> cand/opt_final_<fid>.txt
import sys, pathlib
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import solve
fid = sys.argv[1]
pats = solve.parse((here / "files" / f"in_level-6_{fid}.txt").read_text())
def load(p):
    o = p.read_text().strip().split("\n\n")
    return [x.strip().split("\n") for x in o] if len(o) == len(pats) else None
best = load(here / "best" / f"out_level-6_{fid}.txt")
res = [b[:] for b in best]
for p in sorted((here / "cand").glob(f"opt_*_{fid}.txt")):
    if "final" in p.name: continue
    o = load(p)
    if not o: continue
    for i, ((r, pat, cnt), pr) in enumerate(zip(pats, o)):
        if len(pr) < len(res[i]) and solve.simulate(solve.Geo(r), solve.pattern_cells(pat), [x.split() for x in pr]) == cnt:
            res[i] = pr
out = here / "cand" / f"opt_final_{fid}.txt"
out.write_text("\n\n".join("\n".join(b) for b in res) + "\n")
print(fid, "final", sum(map(len, res)), "best/", sum(map(len, best)), solve.check((here / "files" / f"in_level-6_{fid}.txt").read_text(), out.read_text()))
