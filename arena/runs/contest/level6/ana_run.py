# usage: pypy3 ana_run.py <fid> <k> <K> <W> <maxwait> <tag>  -> cand/ana_parts/<tag>_<fid>_<k>.jsonl
import sys, json, os
import ana_line
from solve import parse
fid, k, K, W, mw, tag = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
mod = __import__(sys.argv[7]) if len(sys.argv) > 7 else ana_line
pats = parse(open(f"files/in_level-6_{fid}.txt").read())
best = [b.strip().split("\n") for b in open(f"best/out_level-6_{fid}.txt").read().strip().split("\n\n")]
os.makedirs("cand/ana_parts", exist_ok=True)
out = open(f"cand/ana_parts/{tag}_{fid}_{k}.jsonl", "a")
for i, (r, pat, cnt) in enumerate(pats):
    if i % K != k or i < int(os.environ.get("ANA_MIN", "0")):
        continue
    p = mod.solve_pat(r, pat, cnt, W=W, maxwait=mw)
    if p is not None and len(p) < len(best[i]):
        out.write(json.dumps({"i": i, "prog": [" ".join(l) for l in p]}) + "\n"); out.flush()
    print(i, len(best[i]), None if p is None else len(p), flush=True)
