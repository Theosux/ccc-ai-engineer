# usage: pypy3 run_tbeam.py <fid> <W> -> cand/tbeam_W<W>_<fid>.txt (failures filled from best/)
import sys
import pathlib
import multiprocessing as mp

here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import solve
import tbeam


def work(args):
    i, r, pat, cnt, W = args
    g = solve.Geo(r)
    pc = solve.pattern_cells(pat)
    try:
        l = tbeam.search(g, pc, cnt, W=W)
    except Exception:
        l = None
    if l is not None and solve.simulate(g, pc, [x.split() for x in l]) == cnt:
        return i, l
    return i, None


if __name__ == "__main__":
    fid, W = sys.argv[1], int(sys.argv[2])
    pats = solve.parse((here / "files" / f"in_level-6_{fid}.txt").read_text())
    best = (here / "best" / f"out_level-6_{fid}.txt").read_text().strip().split("\n\n")
    res = [None] * len(pats)
    jobs = [(i, r, pat, cnt, W) for i, (r, pat, cnt) in enumerate(pats)]
    jobs.sort(key=lambda j: -j[3] * len(solve.pattern_cells(j[2])))
    with mp.Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 15) as pool:
        for k, (i, l) in enumerate(pool.imap_unordered(work, jobs)):
            res[i] = l
            if k % 20 == 0:
                print(f"{k}/{len(jobs)}", flush=True)
    out = []
    better = 0
    for i, l in enumerate(res):
        b = best[i].strip().split("\n")
        if l is not None and len(l) < len(b):
            better += 1
            out.append("\n".join(l))
        else:
            out.append("\n".join(b))
    (here / "cand").mkdir(exist_ok=True)
    p = here / "cand" / f"tbeam_W{W}_{fid}.txt"
    p.write_text("\n\n".join(out) + "\n")
    print(fid, "W", W, "better", better, "total", sum(len(o.split("\n")) for o in out))
