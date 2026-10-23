# usage: pypy3 opt_palrun.py <fid> : palindrome-compress the per-pattern min of best/ + cand/opt_*; writes cand/opt_pal_<fid>.txt
import sys, pathlib, multiprocessing as mp
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import solve, opt_pal

def work(a):
    i, r, pat, cnt, prog = a
    g = solve.Geo(r); pc = solve.pattern_cells(pat)
    toks = [l.split() for l in prog]
    b = opt_pal.compress(g, pc, cnt, toks)
    if len(b) < len(toks) and solve.simulate(g, pc, b) == cnt:
        return i, [" ".join(l) for l in b]
    return i, None

def load(p, n):
    if not p.exists(): return None
    o = p.read_text().strip().split("\n\n")
    return [x.strip().split("\n") for x in o] if len(o) == n else None

if __name__ == "__main__":
    fid = sys.argv[1]
    pats = solve.parse((here / "files" / f"in_level-6_{fid}.txt").read_text())
    best = load(here / "best" / f"out_level-6_{fid}.txt", len(pats))
    res = [b[:] for b in best]
    for p in sorted((here / "cand").glob(f"opt_*_{fid}.txt")):
        o = load(p, len(pats))
        if not o: continue
        for i, ((r, pat, cnt), pr) in enumerate(zip(pats, o)):
            if len(pr) < len(res[i]) and solve.simulate(solve.Geo(r), solve.pattern_cells(pat), [x.split() for x in pr]) == cnt:
                res[i] = pr
    base = sum(map(len, res))
    jobs = [(i, r, pat, cnt, res[i]) for i, (r, pat, cnt) in enumerate(pats) if cnt > 1]
    with mp.Pool(5) as pool:
        for i, l in pool.imap_unordered(work, jobs):
            if l is not None and len(l) < len(res[i]):
                res[i] = l
    out = here / "cand" / f"opt_pal_{fid}.txt"
    out.write_text("\n\n".join("\n".join(b) for b in res) + "\n")
    ok, msg = solve.check((here / "files" / f"in_level-6_{fid}.txt").read_text(), out.read_text())
    print("PAL", fid, "before", base, "after", sum(map(len, res)), "best/", sum(map(len, best)), ok, msg)
