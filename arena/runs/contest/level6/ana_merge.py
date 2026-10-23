# usage: python ana_merge.py <fid> <outtag> [glob-prefix...] : merges best/ + cand/ana_parts/*<fid>*.jsonl -> cand/ana_<outtag>_<fid>.txt
import sys, json, glob
import solve
fid, tag = sys.argv[1], sys.argv[2]
pats = solve.parse(open(f"files/in_level-6_{fid}.txt").read())
best = [b.strip().split("\n") for b in open(f"best/out_level-6_{fid}.txt").read().strip().split("\n\n")]
base = sum(map(len, best))
for f in glob.glob(f"cand/ana_parts/*_{fid}_*.jsonl"):
    for line in open(f):
        d = json.loads(line); i = d["i"]; p = d["prog"]
        if len(p) < len(best[i]):
            r, pat, cnt = pats[i]
            if solve.simulate(solve.Geo(r), solve.pattern_cells(pat), [l.split() for l in p]) == cnt:
                best[i] = p
open(f"cand/ana_{tag}_{fid}.txt", "w").write("\n\n".join("\n".join(b) for b in best) + "\n")
print(fid, "best/", base, "-> merged", sum(map(len, best)))
