# deep: tick beam (masked board P|S) with OPTIONAL temporary skirt dirt (cleaned before acceptance),
# nested-loop action enumeration (faster), multi-variant per pattern.
# usage: pypy3 deep_tb.py <fid> <W> <nproc> <tag> <variants "wo:wd,wo:wd"> [topn] [only=i,j]
#   wd<0 => dirt forbidden (classic tbeam); wd>=0 => dirt allowed, penalty wd per dirty skirt cell.
import sys, pathlib, time
import multiprocessing as mp
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import solve

ACTS = ("-", "F", "B", "T")


def pc_(x):
    return bin(x).count("1")


def prep(geo, pcells):
    cells = sorted(geo.interior)
    bit = {c: 1 << i for i, c in enumerate(cells)}
    P = 0
    for c in pcells:
        P |= bit[c]
    S = 0
    for (y, x) in pcells:
        for dy, dx in solve.NB:
            c = (y + dy, x + dx)
            if c not in pcells and c in geo.interior:
                S |= bit[c]
    M = P | S
    ray = [[0] * geo.m for _ in range(7)]
    for e in range(1, 7):
        for k in range(geo.m):
            mm = 0
            for c in geo.rays[(k, e)]:
                mm |= bit[c]
            ray[e][k] = mm & M
    return P, S, M, ray


def search(geo, pcells, cnt, W, wo, wd, limit, wh=100):
    P, S, M, ray = prep(geo, pcells)
    m = geo.m
    r = geo.r
    allow = wd >= 0
    pos0 = tuple([(e - 1) * r for e in range(1, 7)])  # index 0..5
    beam = [(pos0, 0, 0, 0, ())]
    seen = set()
    for t in range(limit):
        cand = []
        for (pos, act, board, reps, lines) in beam:
            # per emitter options: (action, newpos, newactbit, mask)
            opts = []
            for i in range(6):
                p = pos[i]
                a = (act >> i) & 1
                e = i + 1
                o = []
                for ac in range(4):
                    np_ = p; na = a
                    if ac == 1:
                        np_ = (p + 1) % m
                    elif ac == 2:
                        np_ = (p - 1) % m
                    elif ac == 3:
                        na = 1 - a
                    o.append((ac, np_, na, ray[e][np_] if na else 0))
                opts.append(o)
            o0, o1, o2, o3, o4, o5 = opts
            for (c0, p0, n0, m0) in o0:
                for (c1, p1, n1, m1) in o1:
                    h1a = m0 | m1; h2a = m0 & m1
                    for (c2, p2, n2, m2) in o2:
                        h1b = h1a | m2; h2b = h2a | (h1a & m2); h3b = h2a & m2
                        for (c3, p3, n3, m3) in o3:
                            h1c = h1b | m3; h2c = h2b | (h1b & m3); h3c = h3b | (h2b & m3)
                            for (c4, p4, n4, m4) in o4:
                                h1d = h1c | m4; h2d = h2c | (h1c & m4); h3d = h3c | (h2c & m4)
                                for (c5, p5, n5, m5) in o5:
                                    g1 = h1d | m5; g2 = h2d | (h1d & m5); g3 = h3d | (h2d & m5)
                                    ex2 = g2 & ~g3
                                    if not allow and (ex2 & S):
                                        continue
                                    nb = (board | ex2) & ~g3
                                    nr = reps
                                    if (nb & P) == P and not (nb & S):
                                        nb = 0
                                        nr += 1
                                    na = n0 | (n1 << 1) | (n2 << 2) | (n3 << 3) | (n4 << 4) | (n5 << 5)
                                    tp = (p0, p1, p2, p3, p4, p5)
                                    key = (tp, na, nb, nr)
                                    if key in seen:
                                        continue
                                    seen.add(key)
                                    sc = nr * 100000 + pc_(nb & P) * wh + pc_(g1 & P & ~nb) * wo
                                    if allow:
                                        sc -= pc_(nb & S) * wd
                                    cand.append((sc, (c0, c1, c2, c3, c4, c5), tp, na, nb, nr, lines))
        if not cand:
            return None
        cand.sort(key=lambda z: -z[0])
        beam = []
        for sc, combo, tp, na, nb, nr, lines in cand[:W]:
            nl = lines + (combo,)
            if nr >= cnt:
                return [" ".join(ACTS[a] for a in c) for c in nl]
            beam.append((tp, na, nb, nr, nl))
        if len(seen) > 3000000:
            seen = set()
    return None


def work(args):
    i, r, pat, cnt, cur, W, variants = args
    geo = solve.Geo(r)
    pc = solve.pattern_cells(pat)
    bestp = None
    info = []
    for wo, wd in variants:
        lim = (len(bestp) if bestp else cur) - 1
        L = search(geo, pc, cnt, W, wo, wd, lim)
        info.append((wo, wd, len(L) if L else None))
        if L and len(L) <= lim and solve.simulate(geo, pc, [x.split() for x in L]) == cnt:
            bestp = L
    return i, bestp, info


def load(path):
    return [b.strip().split("\n") for b in pathlib.Path(path).read_text().strip().split("\n\n")]


if __name__ == "__main__":
    fid = sys.argv[1]; W = int(sys.argv[2]); nproc = int(sys.argv[3]); tag = sys.argv[4]
    variants = [tuple(int(v) for v in x.split(":")) for x in sys.argv[5].split(",")]
    topn = int(sys.argv[6]) if len(sys.argv) > 6 else 10 ** 9
    only = None
    for a in sys.argv[7:]:
        if a.startswith("only="):
            only = [int(v) for v in a[5:].split(",")]
    pats = solve.parse((here / "files" / f"in_level-6_{fid}.txt").read_text())
    bestf = here / "best" / f"out_level-6_{fid}.txt"
    best = load(bestf)
    order = sorted(range(len(pats)), key=lambda i: -(len(best[i]) - pats[i][2]))
    if only is not None:
        order = [i for i in order if i in only]
    order = order[:topn]
    jobs = [(i, pats[i][0], pats[i][1], pats[i][2], len(best[i]), W, variants) for i in order]
    res = {}
    t0 = time.time()
    outp = here / "cand" / f"deep_{tag}_{fid}.txt"
    gain = 0

    def flush():
        cur = load(bestf)  # always merge onto the latest best/
        out = []
        for k in range(len(pats)):
            if k in res and len(res[k]) < len(cur[k]):
                out.append("\n".join(res[k]))
            else:
                out.append("\n".join(cur[k]))
        tmp = outp.with_suffix(".tmp")
        tmp.write_text("\n\n".join(out) + "\n")
        tmp.replace(outp)
        return sum(len(o.split("\n")) for o in out), sum(len(c) for c in cur)

    with mp.Pool(nproc) as pool:
        for k, (i, p, info) in enumerate(pool.imap_unordered(work, jobs)):
            if p:
                res[i] = p
                gain += len(best[i]) - len(p)
                print("improved", i, len(best[i]), "->", len(p), info, flush=True)
            else:
                print("nogain", i, len(best[i]), info, flush=True)
            if k % 5 == 4 or k == len(jobs) - 1:
                tot, bt = flush()
                print(f"{k+1}/{len(jobs)} t={int(time.time()-t0)} gain={gain} cand={tot} best={bt}", flush=True)
    tot, bt = flush()
    print("FINAL", fid, tag, "cand", tot, "best", bt)
