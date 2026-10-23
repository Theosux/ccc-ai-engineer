# med: cycle search. For start-state candidates S0, beam-search a closed rep (board empty -> acceptance -> back at S0).
import sys, pathlib, itertools, time
import multiprocessing as mp
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import solve, tbeam, cyc
ACTS = ("-", "F", "B", "T")
ALL = list(itertools.product(range(4), repeat=6))
pc_ = lambda x: bin(x).count("1")

def closed_rep(geo, pcells, S0, W, maxL):
    T = tbeam.TB(geo, pcells)
    m = geo.m; P, S = T.P, T.S; ray = T.ray; M = P | S
    pos0, act0 = S0
    tgt = tuple(pos0)
    def dist(pos, act):
        ds = []
        for e in range(1, 7):
            f = (pos[e] - tgt[e]) % m
            ds.append(min(f, m - f) + (1 if ((act >> e) & 1) != ((act0 >> e) & 1) else 0))
        return max(ds) * 100 + sum(ds) * 10
    beam = [(tuple(pos0), act0, 0, 0, ())]
    seen = set()
    for t in range(maxL):
        cand = []
        for (pos, act, board, reps, lines) in beam:
            for combo in ALL:
                np = list(pos); na = act
                for i in range(6):
                    a = combo[i]
                    if a == 1: np[i+1] = (np[i+1] + 1) % m
                    elif a == 2: np[i+1] = (np[i+1] - 1) % m
                    elif a == 3: na ^= 1 << (i+1)
                g1 = g2 = g3 = 0
                for e in range(1, 7):
                    if na >> e & 1:
                        mm = ray[e][np[e]]
                        g3 |= g2 & mm; g2 |= g1 & mm; g1 |= mm
                ex2 = g2 & ~g3
                if ex2 & S: continue
                nb = ((board | ex2) & ~g3) & M
                nr = reps
                if nb & P == P and not (nb & S):
                    nb = 0; nr = 1
                tp = tuple(np)
                if nr == 1 and tp == tgt and na == act0:
                    return [" ".join(ACTS[a] for a in c) for c in lines + (combo,)]
                key = (tp, na, nb, nr)
                if key in seen: continue
                seen.add(key)
                if nr == 1:
                    sc = 10000 - dist(tp, na)
                else:
                    sc = pc_(nb & P) * 100 + pc_(g1 & P & ~nb) * 3
                cand.append((sc, combo, tp, na, nb, nr, lines))
        if not cand: return None
        cand.sort(key=lambda z: -z[0])
        beam = [(z[2], z[3], z[4], z[5], z[6] + (z[1],)) for z in cand[:W]]
    return None

def states(geo, pcells, lines):
    mk = cyc.trace(geo, pcells, [l.split() for l in lines])
    return [(list(s[0]), sum(1 << e for e in range(1, 7) if s[1][e])) for t, a, s in mk]

def approach(geo, S0):
    pos0, act0 = S0
    m = geo.m; r = geo.r
    n = 0
    for e in range(1, 7):
        s = (e - 1) * r
        f = (pos0[e] - s) % m
        n = max(n, min(f, m - f) + ((act0 >> e) & 1))
    return n

def approach_lines(geo, S0):
    pos0, act0 = S0
    m = geo.m; r = geo.r
    mv = []
    for e in range(1, 7):
        s = (e - 1) * r
        f = (pos0[e] - s) % m
        mv.append(("F", f) if f <= m - f else ("B", m - f))
    n = max(c for _, c in mv)
    out = []
    for t in range(n):
        out.append([d if t < c else "-" for d, c in mv])
    # toggles at the end
    out.append(["T" if (act0 >> e) & 1 else "-" for e in range(1, 7)])
    return [" ".join(l) for l in out]

def work(args):
    i, r, pat, cnt, bl, W = args
    geo = solve.Geo(r); pc = solve.pattern_cells(pat)
    sts = states(geo, pc, bl)
    cur = len(bl)
    bestp = None
    seen = set()
    for S0 in sts:
        k = (tuple(S0[0]), S0[1])
        if k in seen: continue
        seen.add(k)
        ap = approach(geo, S0) + 1
        # need ap + cnt*L < cur
        maxL = (cur - ap) // cnt
        if maxL < 2: continue
        L = closed_rep(geo, pc, S0, W, maxL)
        if L is None: continue
        prog = approach_lines(geo, S0) + L * cnt
        if len(prog) < (len(bestp) if bestp else cur):
            if solve.simulate(geo, pc, [x.split() for x in prog]) == cnt:
                bestp = prog
    return i, bestp

if __name__ == "__main__":
    W = int(sys.argv[1]); nproc = int(sys.argv[2]); tag = sys.argv[3]
    only = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
    pats = solve.parse((here / "files/in_level-6_2-medium.txt").read_text())
    base = pathlib.Path(here / ("cand/" + sys.argv[5] if len(sys.argv) > 5 else "best/out_level-6_2-medium.txt"))
    best = base.read_text().strip().split("\n\n")
    jobs = [(i, r, pat, cnt, best[i].split("\n"), W) for i, (r, pat, cnt) in enumerate(pats) if cnt >= 3 and (only is None or i in only)]
    jobs.sort(key=lambda j: -len(j[4]))
    res = {}
    t0 = time.time()
    with mp.Pool(nproc) as pool:
        for k, (i, p) in enumerate(pool.imap_unordered(work, jobs)):
            if p: res[i] = p; print("improved", i, len(best[i].split("\n")), "->", len(p), flush=True)
            if k % 10 == 0: print(k, len(jobs), time.time() - t0, flush=True)
    out = [("\n".join(res[i]) if i in res else best[i]) for i in range(len(pats))]
    (here / f"cand/med_{tag}_2-medium.txt").write_text("\n\n".join(out) + "\n")
    print("total", sum(len(o.split("\n")) for o in out))
