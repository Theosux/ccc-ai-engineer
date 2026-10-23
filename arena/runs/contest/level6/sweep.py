# Row-write sweep planner for level 6.
# A row y is written in one tick when emitter 1 (at the left ring cell of y) and emitter 4 (right ring cell of y)
# are both active: every interior cell of the row gets count 2 -> M. Extras (2,3,5,6) crossing the row add a
# third beam -> O (holes at skirting cells).
import itertools
from solve import Geo, DIRS, NB, pattern_cells, simulate

EXTRAS = (2, 3, 5, 6)
MAX_SUBSETS = 12


def rot_cell(c, r):
    y, x = c
    dy, dx = y - r, x - 2 * r
    q = (dx - dy) // 2
    rr = dy
    s = -q - rr
    q, rr, s = -rr, -s, -q
    return (rr + r, 2 * q + rr + 2 * r)


class Frame:
    def __init__(self, geo, pcells):
        self.geo = geo
        g = geo
        r = g.r
        self.p = pcells
        sk = set()
        for (y, x) in pcells:
            for dy, dx in NB:
                c = (y + dy, x + dx)
                if c not in pcells and c in g.interior:
                    sk.add(c)
        self.skirt = sk
        self.prow = {}
        self.srow = {}
        for c in pcells:
            self.prow.setdefault(c[0], set()).add(c)
        for c in sk:
            self.srow.setdefault(c[0], []).append(c)
        ys = [c[0] for c in pcells]
        self.top, self.bot = min(ys), max(ys)
        # src[e][cell] = ring idx of emitter e whose ray passes through cell
        self.src = {}
        for e in range(1, 7):
            d = {}
            for k in range(g.m):
                for c in g.rays[(k, e)]:
                    d[c] = k
            self.src[e] = d
        self.L = {}
        self.R = {}
        for y in range(1, 2 * r):
            dd = abs(y - r)
            self.L[y] = g.idx[(y, dd)]
            self.R[y] = g.idx[(y, 4 * r - dd)]


def rdist(a, b, m):
    f = (b - a) % m
    bb = (a - b) % m
    return (f, "F") if f <= bb else (bb, "B")


class State:
    __slots__ = ("pos", "act", "board")

    def __init__(self, pos, act, board):
        self.pos = pos
        self.act = act
        self.board = board

    def copy(self):
        return State(self.pos[:], self.act[:], set(self.board))


def step_counts(geo, pos, act):
    cnt = {}
    for e in range(1, 7):
        if act[e]:
            for c in geo.rays[(pos[e], e)]:
                cnt[c] = cnt.get(c, 0) + 1
    return cnt


def apply_line(geo, pos, act, line):
    m = geo.m
    for e in range(1, 7):
        ins = line[e - 1]
        if ins == "F":
            pos[e] = (pos[e] + 1) % m
        elif ins == "B":
            pos[e] = (pos[e] - 1) % m
        elif ins == "T":
            act[e] = not act[e]


def emitter_plan(cur_pos, cur_act, tgt_pos, tgt_act, mode, L, m):
    """Return list of L actions for one emitter, or None if impossible.
    modes: 'right' (moves at end, toggle at end), 'left' (moves at start), 'spread' (T-off first, moves, T-on last)"""
    d, dirc = rdist(cur_pos, tgt_pos, m)
    acts = []
    if mode == "spread":
        if not cur_act or not tgt_act:
            return None
        n = d + 2
        if n > L:
            return None
        return ["T"] + [dirc] * d + ["-"] * (L - n) + ["T"]
    pre = []
    post = []
    if cur_act and not tgt_act:
        pre = ["T"]  # switch off first
    if not cur_act and tgt_act:
        post = ["T"]  # switch on last
    n = len(pre) + d + len(post)
    if n > L:
        return None
    mv = [dirc] * d
    if mode == "right":
        acts = pre + ["-"] * (L - n) + mv + post
    else:
        acts = pre + mv + ["-"] * (L - n) + post
    return acts


class Planner:
    def __init__(self, frame):
        self.f = frame
        self.g = frame.geo

    def check_ticks(self, st, lines, goal, protected_rows):
        """Simulate lines from state st (no mutation). True if no damage and goal(cnt) holds at the final tick."""
        g, f = self.g, self.f
        pos = st.pos[:]
        act = st.act[:]
        over = {}
        board = st.board
        n = len(lines)
        for i, line in enumerate(lines):
            apply_line(g, pos, act, line)
            cnt = step_counts(g, pos, act)
            for c, k in cnt.items():
                if k == 2:
                    newv = True
                elif k >= 3:
                    newv = False
                else:
                    continue
                cy = c[0]
                if cy in protected_rows:
                    if c in f.p:
                        if not newv:
                            return None
                    elif c in f.skirt:
                        if newv and not over.get(c, c in board):
                            return None
                over[c] = newv
            if i == n - 1 and not goal(cnt):
                return None
        return True

    def row_goal(self, y, holes):
        f = self.f
        prow = f.prow.get(y, ())

        def goal(cnt):
            for c in prow:
                if cnt.get(c, 0) != 2:
                    return False
            for c in holes:
                if cnt.get(c, 0) < 3:
                    return False
            return True
        return goal

    def erase_candidates(self, st, y, X):
        f, g = self.f, self.g
        m = g.m
        out = []
        for re in (1, 4):
            o = 5 - re
            for d in (2, 5):
                for a in (3, 6):
                    others = [e for e in EXTRAS if e not in (d, a)]
                    opts = [[(o, "keep"), (o, "off")] if st.act[o] else [(o, "keep")]]
                    for e in others:
                        opts.append([(e, "keep"), (e, "off")] if st.act[e] else [(e, "keep")])
                    for combo in itertools.product(*opts):
                        tp = st.pos[:]
                        ta = st.act[:]
                        tp[re] = f.L[y] if re == 1 else f.R[y]; ta[re] = True
                        tp[d] = f.src[d][X]; ta[d] = True
                        tp[a] = f.src[a][X]; ta[a] = True
                        for e, op in combo:
                            if op == "off":
                                ta[e] = False
                        lb = 0
                        for e in range(1, 7):
                            dd, _ = rdist(st.pos[e], tp[e], m)
                            lb = max(lb, dd + (1 if st.act[e] != ta[e] else 0))
                        out.append((lb, tp, ta))
        out.sort(key=lambda t: t[0])
        return out

    def candidates(self, st, y, holes=None):
        f, g = self.f, self.g
        if holes is None:
            holes = f.srow.get(y, [])
        if len(holes) > 4:
            return []
        m = g.m
        out = []
        for perm in itertools.permutations(EXTRAS, len(holes)):
            assign = dict(zip(perm, holes))
            rest = [e for e in EXTRAS if e not in assign]
            # options for unassigned: keep (as is) or off
            rest_opts = []
            for e in rest:
                if st.act[e]:
                    rest_opts.append([(e, "keep"), (e, "off")])
                else:
                    rest_opts.append([(e, "keep")])
            for combo in itertools.product(*rest_opts):
                tgt_pos = st.pos[:]
                tgt_act = st.act[:]
                tgt_pos[1] = f.L[y]; tgt_act[1] = True
                tgt_pos[4] = f.R[y]; tgt_act[4] = True
                for e, h in assign.items():
                    tgt_pos[e] = f.src[e][h]; tgt_act[e] = True
                for e, o in combo:
                    if o == "off":
                        tgt_act[e] = False
                lb = 0
                for e in range(1, 7):
                    d, _ = rdist(st.pos[e], tgt_pos[e], m)
                    n = d + (1 if st.act[e] != tgt_act[e] else 0)
                    lb = max(lb, n)
                out.append((lb, tgt_pos, tgt_act))
        out.sort(key=lambda t: t[0])
        return out

    STRATS = [
        # (mode for 1, mode for 4, mode for extras)
        ("right", "right", "right"),
        ("right", "left", "right"),
        ("right", "left", "left"),
        ("spread", "left", "right"),
        ("spread", "left", "left"),
        ("left", "right", "right"),
        ("spread", "spread", "right"),
        ("spread", "left", "spread"),
    ]

    def plan_row(self, st, y, protected_rows, holes=None):
        if holes is None:
            holes = self.f.srow.get(y, [])
        return self.plan_op(st, self.candidates(st, y, holes), self.row_goal(y, holes), protected_rows)

    def plan_erase(self, st, y, X, protected_rows):
        return self.plan_op(st, self.erase_candidates(st, y, X), lambda cnt: cnt.get(X, 0) >= 3, protected_rows)

    def plan_op(self, st, cands, goal, protected_rows):
        g = self.g
        m = g.m
        if not cands:
            return None
        for L in range(max(1, cands[0][0]), max(1, cands[0][0]) + 6):
            for lb, tp, ta in cands:
                if lb > L:
                    break
                for s1, s4, sx in self.STRATS:
                    plans = {}
                    okk = True
                    for e in range(1, 7):
                        mode = s1 if e == 1 else s4 if e == 4 else sx
                        pl = emitter_plan(st.pos[e], st.act[e], tp[e], ta[e], mode, L, m)
                        if pl is None and mode == "spread":
                            pl = emitter_plan(st.pos[e], st.act[e], tp[e], ta[e], "right", L, m)
                        if pl is None:
                            okk = False
                            break
                        plans[e] = pl
                    if not okk:
                        continue
                    lines = [[plans[e][i] for e in range(1, 7)] for i in range(L)]
                    res = self.check_ticks(st, lines, goal, protected_rows)
                    if res is not None:
                        return lines
        return None


def _plan_op_multi(self, st, cands, goal, protected_rows, n, slack=1):
    m = self.g.m
    res = []
    bestL = None
    for lb, tp, ta in cands:
        if bestL is not None and lb > bestL + slack:
            break
        if len(res) >= n and lb > bestL:
            break
        found = None
        for L in range(max(1, lb), max(1, lb) + 5):
            if bestL is not None and L > bestL + slack:
                break
            for s1, s4, sx in self.STRATS:
                plans = {}
                okk = True
                for e in range(1, 7):
                    mode = s1 if e == 1 else s4 if e == 4 else sx
                    pl = emitter_plan(st.pos[e], st.act[e], tp[e], ta[e], mode, L, m)
                    if pl is None and mode == "spread":
                        pl = emitter_plan(st.pos[e], st.act[e], tp[e], ta[e], "right", L, m)
                    if pl is None:
                        okk = False
                        break
                    plans[e] = pl
                if not okk:
                    continue
                lines = [[plans[e][i] for e in range(1, 7)] for i in range(L)]
                if self.check_ticks(st, lines, goal, protected_rows) is not None:
                    found = lines
                    break
            if found:
                break
        if found:
            res.append(found)
            if bestL is None or len(found) < bestL:
                bestL = len(found)
    res.sort(key=len)
    return res[:n]


Planner.plan_op_multi = _plan_op_multi


def _create_candidates(self, st, y, cells):
    """Row emitter (1 or 4) alone on row y + extras crossing at `cells` (count 2 -> M)."""
    f, g = self.f, self.g
    m = g.m
    out = []
    for re in (1, 4):
        o = 5 - re
        for perm in itertools.permutations(EXTRAS, len(cells)):
            assign = dict(zip(perm, cells))
            rest = [e for e in EXTRAS if e not in assign]
            opts = [[(o, "keep"), (o, "off")] if st.act[o] else [(o, "keep")]]
            for e in rest:
                opts.append([(e, "keep"), (e, "off")] if st.act[e] else [(e, "keep")])
            for combo in itertools.product(*opts):
                tp = st.pos[:]
                ta = st.act[:]
                tp[re] = f.L[y] if re == 1 else f.R[y]; ta[re] = True
                for e, c in assign.items():
                    tp[e] = f.src[e][c]; ta[e] = True
                for e, op in combo:
                    if op == "off":
                        ta[e] = False
                lb = 0
                for e in range(1, 7):
                    dd, _ = rdist(st.pos[e], tp[e], m)
                    lb = max(lb, dd + (1 if st.act[e] != ta[e] else 0))
                out.append((lb, tp, ta))
    out.sort(key=lambda t: t[0])
    return out


Planner.create_candidates = _create_candidates


def create_mode(f, y):
    return len(f.srow.get(y, ())) > 4 and len(f.prow.get(y, ())) <= CREATE_MAX


CREATE_MAX = 8

BEAM_K = 6
BEAM_CHILD = 3


class Node:
    __slots__ = ("st", "out", "acc")

    def __init__(self, st, out, acc):
        self.st = st
        self.out = out
        self.acc = acc


def plan_pattern_beam(geo, pcells, cnt, K=None, C=None):
    K = K or BEAM_K
    C = C or BEAM_CHILD
    f = Frame(geo, pcells)
    P = Planner(f)
    r = geo.r
    rows = list(range(f.top, f.bot + 1))
    allrows = set(range(1, 2 * r))
    crows = {y for y in rows if create_mode(f, y)}
    outside = (allrows - set(rows)) | crows
    skirt = f.skirt
    pc = f.p

    def create_row(ch, y, prot):
        """Greedy: create remaining pattern cells of row y. Returns 'fin', 'ok' or 'fail'."""
        while True:
            rem = sorted((c for c in f.prow.get(y, ()) if c not in ch.st.board), key=lambda c: c[1])
            if not rem:
                return "ok"
            k = min(4, len(rem))
            subs = list(itertools.combinations(rem, k))
            if len(subs) > 6:
                subs = [tuple(rem[i:i + k]) for i in range(len(rem) - k + 1)]
            bestl = None
            for sub in subs:
                cells = list(sub)
                goal = (lambda cs: (lambda cnt: all(cnt.get(c, 0) == 2 for c in cs)))(cells)
                for lines in P.plan_op_multi(ch.st, P.create_candidates(ch.st, y, cells), goal, prot, 1):
                    if bestl is None or len(lines) < len(bestl):
                        bestl = lines
            if bestl is None:
                if k == 1:
                    return "fail"
                # fall back to single cells
                for c in rem:
                    goal = (lambda cc: (lambda cnt: cnt.get(cc, 0) == 2))(c)
                    for lines in P.plan_op_multi(ch.st, P.create_candidates(ch.st, y, [c]), goal, prot, 1):
                        if bestl is None or len(lines) < len(bestl):
                            bestl = lines
                if bestl is None:
                    return "fail"
            if execute(ch, bestl):
                return "fin"

    def execute(node, lines):
        st = node.st
        for line in lines:
            apply_line(geo, st.pos, st.act, line)
            cnts = step_counts(geo, st.pos, st.act)
            for c, k in cnts.items():
                if k == 2:
                    st.board.add(c)
                elif k >= 3:
                    st.board.discard(c)
            node.out.append(" ".join(line))
            if pc <= st.board and not (skirt & st.board):
                st.board -= pc
                node.acc += 1
                return True
        return False

    def clone(node):
        return Node(node.st.copy(), node.out[:], node.acc)

    best = Node(State([0] + [(e - 1) * r for e in range(1, 7)], [False] * 7, set()), [], 0)
    while best.acc < cnt:
        cur = None
        for y in range(1, 2 * r):
            if f.L[y] == best.st.pos[1]:
                cur = y
        if cur is not None and abs(cur - f.bot) < abs(cur - f.top):
            order = rows[::-1]
        else:
            order = rows
        start_acc = best.acc
        nodes = [best]
        finished = []
        written = set()
        for y in order:
            prot = outside | written
            holes = f.srow.get(y, [])
            children = []
            for node in nodes:
                st = node.st
                if y in crows:
                    ch = clone(node)
                    res = create_row(ch, y, prot)
                    if res == "fin":
                        finished.append(ch)
                    elif res == "ok":
                        children.append(ch)
                elif len(holes) <= 4:
                    opts = P.plan_op_multi(st, P.candidates(st, y, holes), P.row_goal(y, holes), prot, C)
                    for lines in opts:
                        ch = clone(node)
                        if execute(ch, lines):
                            finished.append(ch)
                        else:
                            children.append(ch)
                else:
                    hs = sorted(holes, key=lambda c: c[1])
                    subsets = list(itertools.combinations(range(len(hs)), 4))
                    if len(subsets) > MAX_SUBSETS:
                        subsets = subsets[:: max(1, len(subsets) // MAX_SUBSETS)]
                    wopts = []
                    for sub in subsets:
                        H = [hs[i] for i in sub]
                        for lines in P.plan_op_multi(st, P.candidates(st, y, H), P.row_goal(y, H), prot, 1):
                            wopts.append((len(lines), lines, H))
                    wopts.sort(key=lambda t: t[0])
                    for _, lines, H in wopts[:C]:
                        ch = clone(node)
                        if execute(ch, lines):
                            finished.append(ch)
                            continue
                        prot2 = prot | {y}
                        rest = [c for c in hs if c not in H]
                        ok = True
                        fin = False
                        while rest:
                            eo = []
                            for X in rest:
                                el = P.plan_erase(ch.st, y, X, prot2)
                                if el is not None:
                                    eo.append((len(el), X, el))
                            if not eo:
                                ok = False
                                break
                            eo.sort(key=lambda t: t[0])
                            _, X, el = eo[0]
                            rest.remove(X)
                            if execute(ch, el):
                                fin = True
                                break
                        if fin:
                            finished.append(ch)
                        elif ok:
                            children.append(ch)
            written.add(y)
            children.sort(key=lambda n: len(n.out))
            nodes = children[:K]
            if not nodes:
                break
        if not finished:
            return None
        finished.sort(key=lambda n: len(n.out))
        best = finished[0]
        if best.acc <= start_acc:
            return None
    return best.out


def plan_pattern(geo, pcells, cnt):
    """Returns list of instruction lines (strings) or None."""
    f = Frame(geo, pcells)
    P = Planner(f)
    r = geo.r
    st = State([0] + [(e - 1) * r for e in range(1, 7)], [False] * 7, set())
    out = []
    rows = list(range(f.top, f.bot + 1))
    allrows = set(range(1, 2 * r))
    acc = 0
    skirt = f.skirt
    pc = f.p
    guard = 0
    while acc < cnt:
        guard += 1
        if guard > cnt + 3:
            return None
        # choose direction: start near emitter 1's current row
        cur = None
        for y in range(1, 2 * r):
            if f.L[y] == st.pos[1]:
                cur = y
        if cur is not None and abs(cur - f.bot) < abs(cur - f.top):
            order = rows[::-1]
        else:
            order = rows
        written = set()
        done = False

        def execute(lines):
            nonlocal acc
            for line in lines:
                apply_line(geo, st.pos, st.act, line)
                cnts = step_counts(geo, st.pos, st.act)
                for c, k in cnts.items():
                    if k == 2:
                        st.board.add(c)
                    elif k >= 3:
                        st.board.discard(c)
                out.append(" ".join(line))
                if pc <= st.board and not (skirt & st.board):
                    st.board -= pc
                    acc += 1
                    return True
            return False

        for y in order:
            prot = (allrows - set(rows)) | written
            holes = f.srow.get(y, [])
            if len(holes) <= 4:
                lines = P.plan_row(st, y, prot)
                if lines is None:
                    return None
                if execute(lines):
                    done = True
                    break
            else:
                hs = sorted(holes, key=lambda c: c[1])
                best = None
                subsets = list(itertools.combinations(range(len(hs)), 4))
                if len(subsets) > MAX_SUBSETS:
                    subsets = subsets[:: max(1, len(subsets) // MAX_SUBSETS)]
                for sub in subsets:
                    H = [hs[i] for i in sub]
                    lines = P.plan_row(st, y, prot, H)
                    if lines is not None and (best is None or len(lines) < len(best[0])):
                        best = (lines, H)
                if best is None:
                    return None
                if execute(best[0]):
                    done = True
                    break
                prot2 = prot | {y}
                rest = [c for c in hs if c not in best[1]]
                while rest:
                    opts = []
                    for X in rest:
                        lines = P.plan_erase(st, y, X, prot2)
                        if lines is not None:
                            opts.append((len(lines), X, lines))
                    if not opts:
                        return None
                    opts.sort(key=lambda t: t[0])
                    _, X, lines = opts[0]
                    rest.remove(X)
                    if execute(lines):
                        done = True
                        break
                if done:
                    break
            written.add(y)
        if not done:
            return None
    return out


def rotate_pattern(pcells, r, k):
    out = set(pcells)
    for _ in range(k):
        out = {rot_cell(c, r) for c in out}
    return out


def relabel(lines, k):
    res = []
    for l in lines:
        t = l.split()
        nt = ["-"] * 6
        for e in range(6):
            nt[(e - k) % 6] = t[e]
        res.append(" ".join(nt))
    return res


def best_sweep2(geo, pcells, cnt):
    """Variant search: rotations x create thresholds with a cheap beam, then refine the best 2 with a wide beam."""
    global CREATE_MAX
    res = []
    for k in range(6):
        pc = rotate_pattern(pcells, geo.r, k)
        for cm in (0, 4, 8, 99):
            CREATE_MAX = cm
            try:
                lines = plan_pattern_beam(geo, pc, cnt, K=2, C=2)
            except Exception:
                lines = None
            if lines is not None:
                res.append((len(lines), k, cm, lines))
    res.sort(key=lambda t: t[0])
    best = None
    for n, k, cm, lines in res[:2]:
        pc = rotate_pattern(pcells, geo.r, k)
        CREATE_MAX = cm
        try:
            l2 = plan_pattern_beam(geo, pc, cnt, K=6, C=3)
        except Exception:
            l2 = None
        for cand in (lines, l2):
            if cand is None:
                continue
            orig = relabel(cand, k)
            if best is not None and len(orig) >= len(best):
                continue
            if simulate(geo, pcells, [l.split() for l in orig]) == cnt:
                best = orig
    return best


def best_sweep(geo, pcells, cnt):
    best = None
    for k in range(6):
        pc = rotate_pattern(pcells, geo.r, k)
        lines = plan_pattern(geo, pc, cnt)
        if lines is None:
            continue
        orig = relabel(lines, k)
        if simulate(geo, pcells, [l.split() for l in orig]) != cnt:
            continue
        if best is None or len(orig) < len(best):
            best = orig
    return best
