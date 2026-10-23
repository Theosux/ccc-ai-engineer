# med: tbeam with masked board (P|S only => better dedupe), score variants, bigger W. usage: med_tb2.py W nproc tag topN [wo1,wo2..]
import sys, pathlib, itertools, time
import multiprocessing as mp
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import solve, tbeam
ACTS = ("-", "F", "B", "T")
ALL = list(itertools.product(range(4), repeat=6))
pc_ = lambda x: bin(x).count("1")

def search(geo, pcells, cnt, W, wh, wo, limit):
    T = tbeam.TB(geo, pcells)
    m = geo.m; r = geo.r; P, S = T.P, T.S; ray = T.ray; M = P | S
    pos0 = tuple([0] + [(e - 1) * r for e in range(1, 7)])
    beam = [(pos0, 0, 0, 0, ())]
    seen = set()
    for t in range(limit):
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
                    nb = 0; nr += 1
                tp = tuple(np)
                key = (tp, na, nb, nr)
                if key in seen: continue
                seen.add(key)
                sc = nr * 10000 + pc_(nb & P) * wh + pc_(g1 & P & ~nb) * wo
                cand.append((sc, combo, tp, na, nb, nr, lines))
        if not cand: return None
        cand.sort(key=lambda z: -z[0])
        beam = []
        for sc, combo, tp, na, nb, nr, lines in cand[:W]:
            nl = lines + (combo,)
            if nr >= cnt: return [" ".join(ACTS[a] for a in c) for c in nl]
            beam.append((tp, na, nb, nr, nl))
    return None

def work(args):
    i, r, pat, cnt, cur, W, wos = args
    geo = solve.Geo(r); pc = solve.pattern_cells(pat)
    bestp = None
    for wo in wos:
        L = search(geo, pc, cnt, W, 100, wo, (len(bestp) if bestp else cur) - 1)
        if L and len(L) < (len(bestp) if bestp else cur) and solve.simulate(geo, pc, [x.split() for x in L]) == cnt:
            bestp = L
    return i, bestp

if __name__ == "__main__":
    W = int(sys.argv[1]); nproc = int(sys.argv[2]); tag = sys.argv[3]; topn = int(sys.argv[4])
    wos = [int(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else [3]
    basef = sys.argv[6] if len(sys.argv) > 6 else "best/out_level-6_2-medium.txt"
    pats = solve.parse((here / "files/in_level-6_2-medium.txt").read_text())
    best = (here / basef).read_text().strip().split("\n\n")
    order = sorted(range(len(pats)), key=lambda i: -len(best[i].split("\n")))[:topn]
    jobs = [(i, pats[i][0], pats[i][1], pats[i][2], len(best[i].split("\n")), W, wos) for i in order]
    res = {}; t0 = time.time()
    with mp.Pool(nproc) as pool:
        for k, (i, p) in enumerate(pool.imap_unordered(work, jobs)):
            if p:
                res[i] = p; print("improved", i, len(best[i].split("\n")), "->", len(p), flush=True)
            print(k, len(jobs), int(time.time() - t0), flush=True)
            if k % 10 == 9 or k == len(jobs) - 1:
                out = [("\n".join(res[i]) if i in res else best[i]) for i in range(len(pats))]
                (here / f"cand/med_{tag}_2-medium.txt").write_text("\n\n".join(out) + "\n")
    print("total", sum(len(o.split("\n")) for o in out))
