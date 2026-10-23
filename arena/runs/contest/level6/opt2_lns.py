# deep: CP-SAT window LNS. Takes an existing valid program, replaces a window of w lines by w' < w lines that
# lead to the SAME emitter state, the same number of acceptances inside the window, and the same board on every
# P|S cell that is not overwritten (count>=2) before the next acceptance. Suffix is replayed unchanged; every
# change is verified with solve.simulate. Works on any file (post-processor for all other agents' programs).
# usage: python deep_lns.py <fid> <tag> <nproc> <w> <tl> [order=gap|len] [only=i,j] [src=path]
import sys, pathlib, time, os
import multiprocessing as mp
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import solve
from deep_sat import Inst
from ortools.sat.python import cp_model


def trace(I, prog):
    """per tick t (1..T): state after (pos, act), counts on R, board after (post removal), acc flag"""
    g = I.g; r = g.r; m = g.m
    pos = [0] + [(e - 1) * r for e in range(1, 7)]
    act = [False] * 7
    Rs = set(I.R)
    board = set()
    states = [(tuple(pos), tuple(act))]
    boards = [frozenset()]
    counts = [None]
    accs = [False]
    for line in prog:
        for e in range(1, 7):
            ins = line[e - 1]
            if ins == "F": pos[e] = (pos[e] + 1) % m
            elif ins == "B": pos[e] = (pos[e] - 1) % m
            elif ins == "T": act[e] = not act[e]
        cnt = {}
        for e in range(1, 7):
            if act[e]:
                for c in g.rays[(pos[e], e)]:
                    if c in Rs:
                        cnt[c] = cnt.get(c, 0) + 1
        for c, k in cnt.items():
            if k == 2: board.add(c)
            elif k >= 3: board.discard(c)
        a = I.P <= board and not (I.S & board)
        if a:
            board -= I.P
        states.append((tuple(pos), tuple(act)))
        boards.append(frozenset(board))
        counts.append(cnt)
        accs.append(a)
    return states, boards, counts, accs


def window_model(I, w2, st0, b0, st1, kacc, endc, tlimit, workers):
    """st0/st1: (pos, act) tuples; b0: set of M cells on R at start; endc: dict cell -> required value at end."""
    m = I.m
    md = cp_model.CpModel()
    X = [[None] + [[md.NewBoolVar("") for p in range(m)] for e in range(1, 7)] for t in range(w2 + 1)]
    A = [[None] + [md.NewBoolVar("") for e in range(1, 7)] for t in range(w2 + 1)]
    for t in range(w2 + 1):
        for e in range(1, 7):
            md.AddExactlyOne(X[t][e])
    for e in range(1, 7):
        md.Add(X[0][e][st0[0][e]] == 1)
        md.Add(A[0][e] == int(st0[1][e]))
        md.Add(X[w2][e][st1[0][e]] == 1)
        md.Add(A[w2][e] == int(st1[1][e]))
    ACT = [[None] * 7 for t in range(w2 + 1)]
    for t in range(1, w2 + 1):
        for e in range(1, 7):
            s, f, b, tg = [md.NewBoolVar("") for _ in range(4)]
            ACT[t][e] = (s, f, b, tg)
            md.AddExactlyOne([s, f, b, tg])
            for p in range(m):
                x0 = X[t - 1][e][p]
                md.AddBoolOr([x0.Not(), f.Not(), X[t][e][(p + 1) % m]])
                md.AddBoolOr([x0.Not(), b.Not(), X[t][e][(p - 1) % m]])
                md.AddBoolOr([x0.Not(), tg.Not(), X[t][e][p]])
                md.AddBoolOr([x0.Not(), s.Not(), X[t][e][p]])
            md.Add(A[t][e] != A[t - 1][e]).OnlyEnforceIf(tg)
            md.Add(A[t][e] == A[t - 1][e]).OnlyEnforceIf(tg.Not())
    ON = {}
    for t in range(1, w2 + 1):
        for e in range(1, 7):
            for p in I.useful[e]:
                o = md.NewBoolVar("")
                md.AddBoolOr([o.Not(), X[t][e][p]])
                md.AddBoolOr([o.Not(), A[t][e]])
                md.AddBoolOr([o, X[t][e][p].Not(), A[t][e].Not()])
                ON[(t, e, p)] = o
    Pset = I.P
    Bd = {}
    ACC = [None] * (w2 + 1)
    for t in range(1, w2 + 1):
        for c in I.R:
            n = sum(ON[(t, e, p)] for (e, p) in I.cover[c])
            i2 = md.NewBoolVar("")
            g3 = md.NewBoolVar("")
            md.Add(n == 2).OnlyEnforceIf(i2)
            md.Add(n != 2).OnlyEnforceIf(i2.Not())
            md.Add(n >= 3).OnlyEnforceIf(g3)
            md.Add(n <= 2).OnlyEnforceIf(g3.Not())
            bv = md.NewBoolVar("")
            md.AddImplication(i2, bv)
            md.AddImplication(g3, bv.Not())
            if t == 1:
                if c in b0:
                    md.AddBoolOr([g3, bv])  # not g3 -> stays M
                else:
                    md.AddBoolOr([i2, bv.Not()])
            else:
                prev = Bd[(t - 1, c)]
                if c in Pset:
                    pe = md.NewBoolVar("")
                    md.AddBoolOr([pe.Not(), prev])
                    md.AddBoolOr([pe.Not(), ACC[t - 1].Not()])
                    md.AddBoolOr([pe, prev.Not(), ACC[t - 1]])
                    prev = pe
                md.AddBoolOr([i2, g3, bv.Not(), prev])
                md.AddBoolOr([i2, g3, bv, prev.Not()])
            Bd[(t, c)] = bv
        ac = md.NewBoolVar("")
        lits = [Bd[(t, c)] if c in Pset else Bd[(t, c)].Not() for c in I.R]
        for l in lits:
            md.AddImplication(ac, l)
        md.AddBoolOr([ac] + [l.Not() for l in lits])
        ACC[t] = ac
    md.Add(sum(ACC[1:]) == kacc)
    for c, v in endc.items():
        bv = Bd[(w2, c)]
        if c in Pset:
            # effective = bv and not ACC[w2]
            if v:
                md.Add(bv == 1); md.Add(ACC[w2] == 0)
            else:
                md.AddBoolOr([bv.Not(), ACC[w2]])
        else:
            md.Add(bv == int(v))
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = tlimit
    sol.parameters.num_search_workers = workers
    st = sol.Solve(md)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    lines = []
    for t in range(1, w2 + 1):
        l = []
        for e in range(1, 7):
            s, f, b, tg = ACT[t][e]
            l.append("F" if sol.Value(f) else "B" if sol.Value(b) else "T" if sol.Value(tg) else "-")
        lines.append(l)
    return lines


def try_window(I, prog, tr, a, b, tlimit, workers, cnt):
    states, boards, counts, accs = tr
    T = len(prog)
    kacc = sum(1 for t in range(a + 1, b + 1) if accs[t])
    # next acceptance at or after b+1
    nxt = None
    for t in range(b + 1, T + 1):
        if accs[t]:
            nxt = t
            break
    endc = {}
    bend = boards[b]
    if nxt is None:
        if b != T:
            return None
    for c in I.R:
        free = False
        if nxt is not None:
            for t in range(b + 1, nxt + 1):
                if counts[t].get(c, 0) >= 2:
                    free = True
                    break
        if not free:
            endc[c] = c in bend
    best = None
    for w2 in range(b - a - 1, 0, -1):
        L = window_model(I, w2, states[a], boards[a], states[b], kacc, endc, tlimit, workers)
        if L is None:
            break
        np_ = prog[:a] + L + prog[b:]
        if solve.simulate(I.g, I.pc, np_) == cnt:
            best = np_
        else:
            break
    return best


def improve(r, pat, cnt, prog, W, tlimit, workers=1, deadline=None, log=None):
    I = Inst(r, pat)
    prog = [l[:] for l in prog]
    rev = os.environ.get("OPT2_REV") == "1"
    a = 0 if not rev else max(0, len(prog) - W)
    while True:
        if deadline and time.time() > deadline:
            break
        T = len(prog)
        if a >= T - 1 or a < 0:
            break
        b = min(T, a + W)
        tr = trace(I, prog)
        res = try_window(I, prog, tr, a, b, tlimit, workers, cnt)
        if res is not None:
            if log: log(f"   win {a}-{b}: {len(prog)} -> {len(res)}")
            prog = res
            continue  # retry same a (window now covers more)
        if rev:
            if a == 0: break
            a = max(0, a - max(1, W // 2))
        else:
            a += max(1, W // 2)
    return prog


def load(path):
    return [[l.split() for l in b.strip().split("\n")] for b in pathlib.Path(path).read_text().strip().split("\n\n")]


def work(args):
    i, r, pat, cnt, prog, W, tl, dl = args
    cap = float(os.environ.get("OPT2_CAP", "1e9")); dl = min(dl or 1e18, time.time() + cap)
    t0 = time.time()
    try:
        p = improve(r, pat, cnt, prog, W, tl, workers=1, deadline=dl)
    except Exception as ex:
        sys.stderr.write(f"err {i}: {ex!r}\n")
        return i, None, 0
    g = solve.Geo(r)
    if len(p) < len(prog) and solve.simulate(g, solve.pattern_cells(pat), p) == cnt:
        return i, p, time.time() - t0
    return i, None, time.time() - t0


if __name__ == "__main__":
    fid, tag, nproc, W, tl = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
    order = "gap"; only = None; src = None; stop = None
    for a in sys.argv[6:]:
        if a.startswith("order="): order = a[6:]
        if a.startswith("only="): only = [int(v) for v in a[5:].split(",")]
        if a.startswith("src="): src = a[4:]
        if a.startswith("stop="): stop = float(a[5:])  # epoch seconds
    pats = solve.parse((here / "files" / f"in_level-6_{fid}.txt").read_text())
    bestf = here / "best" / f"out_level-6_{fid}.txt"
    base = load(src or bestf)
    ids = list(range(len(pats))) if only is None else only
    if order == "gap":
        ids.sort(key=lambda i: -(len(base[i]) - pats[i][2]))
    elif order == "len":
        ids.sort(key=lambda i: -len(base[i]))
    jobs = [(i, pats[i][0], pats[i][1], pats[i][2], base[i], W, tl, stop) for i in ids]
    res = {}
    outp = here / "cand" / f"opt2_{tag}_{fid}.txt"
    t0 = time.time()
    gain = 0

    def flush():
        cur = load(bestf)
        out = []
        for k in range(len(pats)):
            if k in res and len(res[k]) < len(cur[k]):
                out.append("\n".join(" ".join(l) for l in res[k]))
            else:
                out.append("\n".join(" ".join(l) for l in cur[k]))
        tmp = outp.with_suffix(".tmp")
        tmp.write_text("\n\n".join(out) + "\n")
        tmp.replace(outp)
        return sum(len(o.split("\n")) for o in out), sum(len(c) for c in cur)

    with mp.Pool(nproc) as pool:
        for k, (i, p, dt) in enumerate(pool.imap_unordered(work, jobs)):
            if p is not None:
                res[i] = p
                gain += len(base[i]) - len(p)
                print("improved", i, len(base[i]), "->", len(p), round(dt), flush=True)
            if k % 3 == 2 or k == len(jobs) - 1 or p is not None:
                tot, bt = flush()
                print(f"{k+1}/{len(jobs)} t={int(time.time()-t0)} gain={gain} cand={tot} best={bt}", flush=True)
    tot, bt = flush()
    print("FINAL", fid, tag, "cand", tot, "best", bt, flush=True)
