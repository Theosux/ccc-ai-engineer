# opt2: per-pattern min over best/ + given cand files, verified -> cand/opt2_final_<fid>.txt
import sys, pathlib, glob
import solve
here = pathlib.Path(__file__).resolve().parent
fid = sys.argv[1]
pats = solve.parse((here / "files" / f"in_level-6_{fid}.txt").read_text())
def load(p):
    return [b.strip().split("\n") for b in pathlib.Path(p).read_text().strip().split("\n\n")]
best = load(here / "best" / f"out_level-6_{fid}.txt")
cur = [b[:] for b in best]
srcs = []
for pat in sys.argv[2:]:
    srcs += glob.glob(str(here / pat))
for f in srcs:
    try:
        c = load(f)
    except Exception:
        continue
    if len(c) != len(pats): continue
    for i, (r, pat, cnt) in enumerate(pats):
        if len(c[i]) < len(cur[i]):
            g = solve.Geo(r)
            if solve.simulate(g, solve.pattern_cells(pat), [l.split() for l in c[i]]) == cnt:
                cur[i] = c[i]
(here / "cand" / f"opt2_final_{fid}.txt").write_text("\n\n".join("\n".join(p) for p in cur) + "\n")
print(fid, "best", sum(map(len, best)), "final", sum(map(len, cur)))
