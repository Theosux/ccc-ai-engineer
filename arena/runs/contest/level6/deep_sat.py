# deep: exact CP-SAT model of the level-6 machine (OR-tools, CPython).
# Program = prefix (T0 lines, first acceptance at line T0) + cycle (k lines, acceptance at its end, emitter state
# returns to the post-prefix state) repeated cnt-1 times. Board on P|S is clean after every acceptance, so the cycle
# is exactly periodic. Total = T0 + k*(cnt-1).
import sys, pathlib, time
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import solve
from ortools.sat.python import cp_model

ACTS = "-FBT"


class Inst:
    def __init__(self, r, pat):
        self.g = g = solve.Geo(r)
        self.r = r
        self.m = g.m
        P = solve.pattern_cells(pat)
        S = set()
        for (y, x) in P:
            for dy, dx in solve.NB:
                c = (y + dy, x + dx)
                if c not in P and c in g.interior:
                    S.add(c)
        self.P, self.S = P, S
        self.R = sorted(P | S)
        self.pc = P
        # cover[c] = list of (e, p)
        self.cover = {c: [] for c in self.R}
        self.useful = {}  # (e) -> set of p with nonempty ray in R
        for e in range(1, 7):
            us = set()
            for p in range(g.m):
                for c in g.rays[(p, e)]:
                    if c in self.cover:
                        self.cover[c].append((e, p))
                        us.add(p)
            self.useful[e] = us


def build(I, N, acc, start=None, closure=None, workers=4, tlimit=60.0, hint=None):
    """ticks 0..N; state[0] = start (None = free). acc: set of ticks with acceptance (board clean before t=1).
    closure: tick j with state[N] == state[j]. Returns list of lines or None/'unknown'."""
    m = I.m
    md = cp_model.CpModel()
    X = [[[md.NewBoolVar("") for p in range(m)] for e in range(7)] for t in range(N + 1)]
    A = [[md.NewBoolVar("") for e in range(7)] for t in range(N + 1)]
    for t in range(N + 1):
        for e in range(1, 7):
            md.AddExactlyOne(X[t][e])
    if start is not None:
        pos, act = start
        for e in range(1, 7):
            md.Add(X[0][e][pos[e]] == 1)
            md.Add(A[0][e] == int(act[e]))
    ACT = [[None] * 7 for t in range(N + 1)]
    for t in range(1, N + 1):
        for e in range(1, 7):
            f, b, tg, s = [md.NewBoolVar("") for _ in range(4)]
            ACT[t][e] = (s, f, b, tg)
            md.AddExactlyOne([f, b, tg, s])
            for p in range(m):
                x0 = X[t - 1][e][p]
                md.AddBoolOr([x0.Not(), f.Not(), X[t][e][(p + 1) % m]])
                md.AddBoolOr([x0.Not(), b.Not(), X[t][e][(p - 1) % m]])
                md.AddBoolOr([x0.Not(), tg.Not(), X[t][e][p]])
                md.AddBoolOr([x0.Not(), s.Not(), X[t][e][p]])
            md.Add(A[t][e] != A[t - 1][e]).OnlyEnforceIf(tg)
            md.Add(A[t][e] == A[t - 1][e]).OnlyEnforceIf(tg.Not())
    if closure is not None:
        for e in range(1, 7):
            for p in range(m):
                md.Add(X[N][e][p] == X[closure][e][p])
            md.Add(A[N][e] == A[closure][e])
    # On vars
    ON = {}
    for t in range(1, N + 1):
        for e in range(1, 7):
            for p in I.useful[e]:
                o = md.NewBoolVar("")
                md.AddBoolOr([o.Not(), X[t][e][p]])
                md.AddBoolOr([o.Not(), A[t][e]])
                md.AddBoolOr([o, X[t][e][p].Not(), A[t][e].Not()])
                ON[(t, e, p)] = o
    Pset = I.P
    Bd = {}
    for c in I.R:
        Bd[(0, c)] = None  # clean
    for t in range(1, N + 1):
        for c in I.R:
            n = sum(ON[(t, e, p)] for (e, p) in I.cover[c])
            i2 = md.NewBoolVar("")
            g3 = md.NewBoolVar("")
            md.Add(n == 2).OnlyEnforceIf(i2)
            md.Add(n != 2).OnlyEnforceIf(i2.Not())
            md.Add(n >= 3).OnlyEnforceIf(g3)
            md.Add(n <= 2).OnlyEnforceIf(g3.Not())
            bv = md.NewBoolVar("")
            prev = Bd[(t - 1, c)]
            if (t - 1) in acc and c in Pset:
                prev = None
            md.AddImplication(i2, bv)
            md.AddImplication(g3, bv.Not())
            if prev is None:
                md.AddBoolOr([i2, bv.Not()])  # not i2 and not g3 -> b = 0 ; i.e. bv -> i2
            else:
                # not i2 and not g3 -> bv == prev
                md.AddBoolOr([i2, g3, bv.Not(), prev])
                md.AddBoolOr([i2, g3, bv, prev.Not()])
            Bd[(t, c)] = bv
    for t in range(1, N + 1):
        if t in acc:
            for c in I.R:
                if c in Pset:
                    md.Add(Bd[(t, c)] == 1)
                else:
                    md.Add(Bd[(t, c)] == 0)
        else:
            md.AddBoolOr([Bd[(t, c)].Not() if c in Pset else Bd[(t, c)] for c in I.R])
    if hint is not None:
        pass
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = tlimit
    sol.parameters.num_search_workers = workers
    st = sol.Solve(md)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return "unknown" if st == cp_model.UNKNOWN else None
    lines = []
    for t in range(1, N + 1):
        l = []
        for e in range(1, 7):
            s, f, b, tg = ACT[t][e]
            l.append("F" if sol.Value(f) else "B" if sol.Value(b) else "T" if sol.Value(tg) else "-")
        lines.append(l)
    # start state
    pos = [0] * 7
    act = [False] * 7
    for e in range(1, 7):
        for p in range(m):
            if sol.Value(X[0][e][p]):
                pos[e] = p
        act[e] = bool(sol.Value(A[0][e]))
    return lines, (pos, act)


def init_state(r):
    return ([0] + [(e - 1) * r for e in range(1, 7)], [False] * 7)


def solve_pattern(r, pat, cnt, cur, workers=4, tl=30.0, log=print):
    """returns best program (list of str) with len < cur, or None"""
    I = Inst(r, pat)
    st0 = init_state(r)
    best = None
    bestlen = cur
    if cnt == 1:
        for T0 in range(1, cur):
            res = build(I, T0, {T0}, start=st0, workers=workers, tlimit=tl)
            if res is None:
                continue
            if res == "unknown":
                log(f"  T0={T0} unknown")
                continue
            lines, _ = res
            return [" ".join(l) for l in lines]
        return None
    # minimal cycle length k (free start)
    kmin = None
    for k in range(1, 30):
        if k * (cnt - 1) >= bestlen:
            break
        res = build(I, k, {k}, start=None, closure=0, workers=workers, tlimit=tl)
        if res is None:
            continue
        if res == "unknown":
            log(f"  k={k} unknown")
            continue
        kmin = k
        break
    if kmin is None:
        return None
    log(f"  kmin={kmin}")
    for k in (kmin, kmin + 1):
        for T0 in range(1, bestlen - k * (cnt - 1)):
            N = T0 + k
            res = build(I, N, {T0, N}, start=st0, closure=T0, workers=workers, tlimit=tl)
            if res is None:
                continue
            if res == "unknown":
                log(f"  k={k} T0={T0} unknown")
                continue
            lines, _ = res
            prog = lines[:T0] + lines[T0:] * (cnt - 1)
            if len(prog) < bestlen:
                best = [" ".join(l) for l in prog]
                bestlen = len(prog)
            break
    return best


if __name__ == "__main__":
    fid = sys.argv[1]
    ids = [int(x) for x in sys.argv[2].split(",")]
    pats = solve.parse((here / "files" / f"in_level-6_{fid}.txt").read_text())
    bestp = [b.strip().split("\n") for b in (here / "best" / f"out_level-6_{fid}.txt").read_text().strip().split("\n\n")]
    for i in ids:
        r, pat, cnt = pats[i]
        t = time.time()
        p = solve_pattern(r, pat, cnt, len(bestp[i]))
        ok = None
        if p:
            g = solve.Geo(r)
            ok = solve.simulate(g, solve.pattern_cells(pat), [l.split() for l in p]) == cnt
        print(i, r, cnt, "best", len(bestp[i]), "sat", len(p) if p else None, ok, round(time.time() - t, 1), flush=True)


def build_full(I, N, cnt, start, hint=None, workers=4, tlimit=60.0, log=None):
    """Exact model, horizon N, variable acceptance times (true semantics), minimise completion tick.
    hint: list of lines (list of 6 chars) of a known valid program (len <= N)."""
    m = I.m
    md = cp_model.CpModel()
    X = [[None] + [[md.NewBoolVar("") for p in range(m)] for e in range(1, 7)] for t in range(N + 1)]
    A = [[None] + [md.NewBoolVar("") for e in range(1, 7)] for t in range(N + 1)]
    for t in range(N + 1):
        for e in range(1, 7):
            md.AddExactlyOne(X[t][e])
    pos, act = start
    for e in range(1, 7):
        md.Add(X[0][e][pos[e]] == 1)
        md.Add(A[0][e] == int(act[e]))
    ACT = [[None] * 7 for t in range(N + 1)]
    for t in range(1, N + 1):
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
    for t in range(1, N + 1):
        for e in range(1, 7):
            for p in I.useful[e]:
                o = md.NewBoolVar("")
                md.AddBoolOr([o.Not(), X[t][e][p]])
                md.AddBoolOr([o.Not(), A[t][e]])
                md.AddBoolOr([o, X[t][e][p].Not(), A[t][e].Not()])
                ON[(t, e, p)] = o
    Pset = I.P
    Bd = {}
    ACC = [None] * (N + 1)
    for t in range(1, N + 1):
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
                md.AddBoolOr([i2, bv.Not()])
            else:
                prev = Bd[(t - 1, c)]
                if c in Pset:
                    # effective prev = prev and not acc[t-1]
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
    # done_t: cumulative acceptances >= cnt
    DONE = [None] * (N + 1)
    for t in range(1, N + 1):
        d = md.NewBoolVar("")
        sm = sum(ACC[1:t + 1])
        md.Add(sm >= cnt).OnlyEnforceIf(d)
        md.Add(sm <= cnt - 1).OnlyEnforceIf(d.Not())
        DONE[t] = d
    md.Add(DONE[N] == 1)
    md.Minimize(sum(1 - DONE[t] for t in range(1, N + 1)))
    if hint is not None:
        p = list(pos); a = list(act)
        for t in range(1, N + 1):
            line = hint[t - 1] if t - 1 < len(hint) else ["-"] * 6
            for e in range(1, 7):
                ch = line[e - 1]
                s, f, b, tg = ACT[t][e]
                md.AddHint(s, int(ch == "-")); md.AddHint(f, int(ch == "F"))
                md.AddHint(b, int(ch == "B")); md.AddHint(tg, int(ch == "T"))
                if ch == "F": p[e] = (p[e] + 1) % m
                elif ch == "B": p[e] = (p[e] - 1) % m
                elif ch == "T": a[e] = not a[e]
                for q in range(m):
                    md.AddHint(X[t][e][q], int(q == p[e]))
                md.AddHint(A[t][e], int(a[e]))
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = tlimit
    sol.parameters.num_search_workers = workers
    st = sol.Solve(md)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    T = int(round(sol.ObjectiveValue())) + 1
    lines = []
    for t in range(1, T + 1):
        l = []
        for e in range(1, 7):
            s, f, b, tg = ACT[t][e]
            l.append("F" if sol.Value(f) else "B" if sol.Value(b) else "T" if sol.Value(tg) else "-")
        lines.append(" ".join(l))
    return lines, st == cp_model.OPTIMAL
