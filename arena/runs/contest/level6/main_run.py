# usage: pypy3 opt_run.py <fid> <variant> [nseed] [seed] [base_cand]
# runs opt_macro.plan on every pattern (5 procs), keeps per-pattern min vs best/ (and base_cand), writes cand/opt_<variant>_<fid>.txt
import sys
import pathlib
import multiprocessing as mp
import time

here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import solve


def work(args):
    i, r, pat, cnt, nseed, seed, mod = args
    import importlib
    M = importlib.import_module(mod)
    g = solve.Geo(r)
    pc = solve.pattern_cells(pat)
    best = None
    try:
        import os, json; l = M.plan(g, pc, cnt, nseed=nseed, seed=seed, **json.loads(os.environ.get("MAIN_KW", "{}")))
    except Exception as ex:
        sys.stderr.write(f"err {i}: {ex!r}\n")
        l = None
    if l is not None and solve.simulate(g, pc, [x.split() for x in l]) == cnt:
        best = l
    return i, best


def load(path, n):
    p = pathlib.Path(path)
    if not p.exists():
        return None
    progs = p.read_text().strip().split("\n\n")
    if len(progs) != n:
        return None
    return [x.strip().split("\n") for x in progs]


if __name__ == "__main__":
    fid, var = sys.argv[1], sys.argv[2]
    nseed = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    mod = sys.argv[5] if len(sys.argv) > 5 else "opt_macro"
    pats = solve.parse((here / "files" / f"in_level-6_{fid}.txt").read_text())
    best = load(here / "best" / f"out_level-6_{fid}.txt", len(pats))
    res = [b[:] for b in best]
    src = ["best"] * len(pats)
    # also fold in my previous candidates
    for p in sorted((here / "cand").glob(f"*_{fid}.txt")):
        o = load(p, len(pats))
        if not o:
            continue
        for i, ((r, pat, cnt), pr) in enumerate(zip(pats, o)):
            if len(pr) < len(res[i]) and solve.simulate(solve.Geo(r), solve.pattern_cells(pat), [x.split() for x in pr]) == cnt:
                res[i] = pr
                src[i] = p.name
    jobs = [(i, r, pat, cnt, nseed, seed, mod) for i, (r, pat, cnt) in enumerate(pats)]
    jobs.sort(key=lambda j: -len(best[j[0]])); jobs = jobs[int(sys.argv[7]) if len(sys.argv) > 7 else 0:]
    t0 = time.time()
    imp = 0
    out = here / "cand" / f"main_{var}_{fid}.txt"
    donef = here / f"main_done_{var}_{fid}.txt"
    done = set(int(x) for x in donef.read_text().split()) if donef.exists() else set()
    jobs = [j for j in jobs if j[0] not in done]
    print("jobs", len(jobs), flush=True)
    with mp.Pool(int(sys.argv[6]) if len(sys.argv) > 6 else 5) as pool:
        for k, (i, l) in enumerate(pool.imap_unordered(work, jobs)):
            with open(donef, "a") as fh: fh.write(f"{i} ")
            if l is not None and len(l) < len(res[i]):
                imp += len(res[i]) - len(l)
                res[i] = l
                src[i] = var
            if True:
                out.write_text("\n\n".join("\n".join(b) for b in res) + "\n")
                print(f"{k+1}/{len(jobs)} total {sum(map(len, res))} best {sum(map(len, best))} t={time.time()-t0:.0f}s", flush=True)
    out.write_text("\n\n".join("\n".join(b) for b in res) + "\n")
    ok, msg = solve.check((here / "files" / f"in_level-6_{fid}.txt").read_text(), out.read_text())
    print("FINAL", fid, var, "total", sum(map(len, res)), "best", sum(map(len, best)), ok, msg)
