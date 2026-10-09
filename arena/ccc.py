#!/usr/bin/env python3
"""CCC arena CLI: fetch levels, run solvers, submit outputs on codingcontest.org.

Usage (run from anywhere):
  python arena/ccc.py login                    # one-time: log in via Edge window, saves cookies
  python arena/ccc.py games                    # list practice games (slugs)
  python arena/ccc.py train <gameSlug> [--mode exploration|challenge] [--name NAME]
  python arena/ccc.py contest <contestName> [--name NAME]   # contest day
  python arena/ccc.py use <NAME>               # switch active run folder
  python arena/ccc.py info                     # level/file status of active run
  python arena/ccc.py fetch <N>                # download + unzip level N
  python arena/ccc.py run <N> [--only ID]      # run levelN/solve.py on every input -> out/
  python arena/ccc.py submit <N> [--only ID] [--include-example]
  python arena/ccc.py go <N>                   # run + submit (example checked first)
  python arena/ccc.py api <GET|POST> <path> [--game]   # raw API call (debug)
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import requests

BASE = "https://codingcontest.org"
ARENA = Path(__file__).resolve().parent
AUTH = ARENA / ".auth"
RUNS = ARENA / "runs"
COOKIES = AUTH / "cookies.json"
STATE = AUTH / "state.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36 Edg/141.0"


# ---------------------------------------------------------------- state / http
def load_json(p, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def state():
    return load_json(STATE, {"active": None, "runs": {}})


def active_run():
    st = state()
    name = os.environ.get("CCC_RUN") or st.get("active")  # CCC_RUN lets parallel sessions use different runs
    if name and name not in st["runs"]:
        sys.exit(f"Unknown run {name!r}. Known: {', '.join(st['runs'])}")
    if not name:
        sys.exit("No active run. Use `train <gameSlug>` or `contest <contestName>` first.")
    return name, st["runs"][name], st


def platform_session():
    s = requests.Session()
    s.headers["User-Agent"] = UA
    for c in load_json(COOKIES, []):
        s.cookies.set(c["name"], c["value"], domain=c.get("domain"), path=c.get("path", "/"))
    xsrf = s.cookies.get("XSRF-TOKEN")
    if xsrf:
        s.headers["X-XSRF-TOKEN"] = xsrf
    s.headers["Referer"] = BASE + "/"
    s.headers["Origin"] = BASE
    return s


def check(r, what):
    if r.status_code == 401 or r.status_code == 403 and "login" in r.text.lower():
        sys.exit(f"{what}: not logged in ({r.status_code}). Run `python arena/ccc.py login`.")
    if not r.ok:
        sys.exit(f"{what}: HTTP {r.status_code} {r.text[:300]}")
    return r


def game_headers(run):
    origin = run["gameBaseUrl"].rstrip("/")
    return {
        "Authorization": run["token"],
        "X-CCC-SLUG": run["contestSlug"],
        "Referer": origin + "/",
        "Origin": origin,
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": UA,
    }


def refresh_token(name, run, st):
    s = platform_session()
    r = check(s.post(f"{BASE}/api/game-token", json={"contestSlug": run["contestSlug"]}), "game-token")
    run["token"] = r.json()["token"]
    run["tokenAt"] = time.time()
    st["runs"][name] = run
    save_json(STATE, st)
    return run


def game_req(method, path, run_ctx=None, **kw):
    """Request against the game origin; refreshes the game token once on 401/403."""
    name, run, st = run_ctx or active_run()
    if not run.get("token"):
        run = refresh_token(name, run, st)
    url = run["gameBaseUrl"].rstrip("/") + path
    for attempt in range(2):
        r = requests.request(method, url, headers=game_headers(run), timeout=120, **kw)
        if r.status_code in (401, 403) and attempt == 0:
            run = refresh_token(name, run, st)
            continue
        return r
    return r


def run_dir(name):
    d = RUNS / name
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------- commands
def cmd_login(a):
    from playwright.sync_api import sync_playwright

    AUTH.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(AUTH / "edge-profile"), channel="msedge", headless=False, viewport=None
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(BASE + "/login")
        print("Log in in the Edge window (waiting up to 5 min)...")
        deadline = time.time() + 300
        user = None
        while time.time() < deadline:
            r = ctx.request.get(BASE + "/api/auth/current-user")
            if r.ok:
                try:
                    user = r.json()
                except Exception:
                    user = None
                if user and (user.get("username") or user.get("id")):
                    break
            time.sleep(2)
        if not user:
            ctx.close()
            sys.exit("Login not detected.")
        cookies = [c for c in ctx.cookies() if "codingcontest.org" in c["domain"]]
        save_json(COOKIES, cookies)
        ctx.close()
    print(f"Logged in as {user.get('username')} (participant roles: {user.get('roles')}). Cookies saved.")


def cmd_games(a):
    r = check(requests.get(f"{BASE}/api/games", headers={"User-Agent": UA}), "games")
    for g in r.json():
        print(f"{g.get('slug'):45} {g.get('totalLevels')!s:>3} lv  {g.get('title') or g.get('name')}")


def register_run(name, contest_name, extra):
    s = platform_session()
    c = check(s.get(f"{BASE}/api/contests/{contest_name}"), "contest").json()
    gbu = c.get("gameBaseUrl")
    slug = c.get("slug") or contest_name
    if not gbu:
        save_json(run_dir(name) / "contest.json", c)
        sys.exit(f"Contest has no gameBaseUrl yet (game not assigned?). Saved contest.json in runs/{name}.")
    st = state()
    st["runs"][name] = {"contestName": contest_name, "contestSlug": slug, "gameBaseUrl": gbu, "token": None, **extra}
    st["active"] = name
    save_json(STATE, st)
    save_json(run_dir(name) / "contest.json", c)
    print(f"Active run: {name}  (contest {slug}, game {gbu})")
    refresh_token(name, st["runs"][name], st)
    print("Game token OK.")


def cmd_train(a):
    s = platform_session()
    r = s.post(f"{BASE}/api/training/{a.slug}/start", params={"mode": a.mode})
    if r.status_code == 409 or not r.ok:
        act = s.get(f"{BASE}/api/training/active")
        print(f"start -> HTTP {r.status_code} {r.text[:200]}; active training: {act.status_code} {act.text[:300]}")
        if not act.ok or not act.text.strip():
            sys.exit(1)
        data = act.json()
    else:
        data = r.json()
    contest_name = data.get("contestName") or data.get("name") or data.get("slug")
    name = a.name or a.slug.split("-")[-1]
    register_run(name, contest_name, {"gameSlug": a.slug, "mode": a.mode})


def cmd_contest(a):
    register_run(a.name or "contest", a.contest_name, {})


def cmd_use(a):
    st = state()
    if a.name not in st["runs"]:
        sys.exit(f"Unknown run. Known: {', '.join(st['runs'])}")
    st["active"] = a.name
    save_json(STATE, st)
    print(f"Active run: {a.name}")


def contestant_info(ctx=None):
    r = game_req("GET", "/api/contestant/contestant-info", ctx)
    if not r.ok:
        sys.exit(f"contestant-info: HTTP {r.status_code} {r.text[:300]}")
    return r.json()


def cmd_info(a):
    ctx = active_run()
    info = contestant_info(ctx)
    save_json(run_dir(ctx[0]) / "contestant-info.json", info)
    if a.raw:
        print(json.dumps(info, indent=2)[:6000])
        return
    print(f"Run: {ctx[0]}")
    state_ = (info.get("score") or {}).get("state") or {}
    for k in sorted(state_, key=lambda x: int(re.sub(r"\D", "", x) or 0)):
        lv = state_[k]
        passed = lv.get("passedFiles") or {}
        print(f"  {k}: passedAt={lv.get('passedAt')} passedFiles={sorted(f for f, v in passed.items() if v)}")
    for key in ("currentLevel", "maxAccessibleLevel", "level", "levels"):
        if key in info:
            val = info[key]
            print(f"  {key}: {json.dumps(val)[:800]}")


def file_id_for(stem, ids):
    """Mirror the platform rule: exact id in name, else the last number in the filename picks the case."""
    for fid in sorted(ids, key=len, reverse=True):
        if re.search(rf"(^|[^0-9a-z]){re.escape(fid)}$", stem.lower()):
            return fid
    if "example" in stem.lower():
        ex = [i for i in ids if "example" in i]
        if ex:
            return ex[0]
    nums = re.findall(r"\d+", stem)
    if nums:
        last = str(int(nums[-1]))
        for fid in ids:
            if re.match(rf"^0*{last}(-|$)", fid):
                return fid
        return last
    return None


def level_dir(name, n):
    return run_dir(name) / f"level{n}"


def cmd_fetch(a):
    ctx = active_run()
    name, run, _ = ctx
    n = a.level
    d = level_dir(name, n)
    d.mkdir(parents=True, exist_ok=True)
    r = game_req("GET", f"/api/contestant/level/{n}/files", ctx)
    if not r.ok:
        sys.exit(f"files: HTTP {r.status_code} {r.text[:300]}")
    if "application/json" in r.headers.get("content-type", ""):
        url = r.json()["url"]
        r = requests.get(url, timeout=120, headers={"User-Agent": UA})
        r.raise_for_status()
    zpath = d / f"level-{n}.zip"
    zpath.write_bytes(r.content)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(d / "files")
    info = contestant_info(ctx)
    save_json(run_dir(name) / "contestant-info.json", info)
    lv = ((info.get("score") or {}).get("state") or {}).get(f"level{n}") or {}
    scored = list((lv.get("passedFiles") or {}).keys())
    files = sorted(p for p in (d / "files").rglob("*") if p.is_file())
    # 2026 naming: in_level-N_<fileId>.txt, expected example output: out_level-N_0-example.txt
    mapping = {}
    for p in files:
        m = IN_RE.match(p.name)
        if m:
            mapping[str(p.relative_to(d)).replace("\\", "/")] = m.group(2)
    if not mapping:  # unknown naming: fall back to the platform's "last number picks the case" rule
        for p in files:
            if p.suffix.lower() in (".in", ".txt") and not p.stem.lower().startswith("out"):
                mapping[str(p.relative_to(d)).replace("\\", "/")] = file_id_for(p.stem, scored + ["0-example"])
    unscored = sorted(set(mapping.values()) - set(scored)) if scored else [f for f in mapping.values() if "example" in f]
    save_json(d / "map.json", {"scoredFiles": scored, "unscoredFiles": unscored, "inputs": mapping})
    for pdf in [p for p in files if p.suffix.lower() == ".pdf"]:
        try:
            from pypdf import PdfReader
            text = "\n\n".join(pg.extract_text() or "" for pg in PdfReader(str(pdf)).pages)
            (d / "statement.txt").write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"  (pdf text extraction failed: {e})")
    sandbox = game_req("GET", f"/api/contestant/level/{n}/sandbox", ctx)
    if sandbox.ok and sandbox.text.strip() and "html" in sandbox.headers.get("content-type", "") + sandbox.text[:200].lower():
        (d / "sandbox.html").write_text(sandbox.text, encoding="utf-8")
    solve = d / "solve.py"
    if not solve.exists():
        solve.write_text(SOLVE_TEMPLATE, encoding="utf-8")
    print(f"Level {n} -> {d}")
    for p in files:
        print(f"  {p.relative_to(d)}  ({p.stat().st_size} B)")
    print(f"  scored: {scored}  unscored: {unscored}")
    print(f"  input -> fileId: {mapping}")


IN_RE = re.compile(r"^in_level-?(\d+)_(.+)\.[a-z]+$", re.I)


SOLVE_TEMPLATE = '''import sys


def solve(data: str) -> str:
    lines = data.splitlines()
    raise NotImplementedError


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
'''


def norm(s):
    return "\n".join(line.rstrip() for line in s.strip().splitlines())


def inputs_of(d):
    m = load_json(d / "map.json", {"inputs": {}})["inputs"]
    return [(d / rel, fid) for rel, fid in m.items()]


def out_path(d, inp, fid):
    stem = inp.stem[3:] if inp.stem.lower().startswith("in_") else inp.stem
    return d / "out" / f"out_{stem}.txt"


def expected_path(inp):
    if inp.stem.lower().startswith("in_"):
        q = inp.with_name("out_" + inp.name[3:])
        if q.exists():
            return q
    q = inp.with_suffix(".out")
    return q if q.exists() else None


def cmd_run(a):
    name, run, _ = active_run()
    d = level_dir(name, a.level)
    solver = Path(a.solver) if a.solver else d / "solve.py"
    (d / "out").mkdir(exist_ok=True)
    ok_all = True
    for inp, fid in inputs_of(d):
        if a.only and fid not in a.only and inp.stem not in a.only:
            continue
        t0 = time.time()
        p = subprocess.run([sys.executable, str(solver)], stdin=inp.open("rb"), capture_output=True, timeout=a.timeout)
        dt = time.time() - t0
        if p.returncode != 0:
            ok_all = False
            print(f"  {inp.name}: CRASH ({dt:.1f}s)\n{p.stderr.decode(errors='replace')[-1500:]}")
            continue
        out = p.stdout.decode()
        op = out_path(d, inp, fid)
        op.write_text(out, encoding="utf-8", newline="\n")
        status = ""
        exp = expected_path(inp)
        if exp:
            want = norm(exp.read_text(encoding="utf-8"))
            match = want == norm(out)
            status = "EXAMPLE OK" if match else "EXAMPLE MISMATCH"
            ok_all &= match
            if not match:
                print(f"--- expected ({exp.name}) ---\n{want[:1500]}\n--- got ---\n{norm(out)[:1500]}")
        print(f"  {inp.name} -> out/{op.name}  [{fid}]  {dt:.1f}s  {status}")
    return ok_all


def cmd_submit(a):
    ctx = active_run()
    name, run, _ = ctx
    d = level_dir(name, a.level)
    m = load_json(d / "map.json", {"unscoredFiles": []})
    unscored = set(m.get("unscoredFiles") or [])
    results = {}
    for inp, fid in inputs_of(d):
        if fid is None:
            print(f"  {inp.name}: no fileId mapping, skipped")
            continue
        if a.only and fid not in a.only and inp.stem not in a.only:
            continue
        if fid in unscored and not a.include_example:
            continue
        op = out_path(d, inp, fid)
        if not op.exists():
            print(f"  {inp.name}: no output yet, skipped")
            continue
        for _ in range(5):
            r = game_req("POST", f"/api/contestant/submit-{a.level}-{fid}", ctx,
                         files={"solution": (op.name, op.read_bytes(), "text/plain")})
            if r.status_code == 429:
                try:
                    wait = int(r.json().get("cooldownSec") or 0)
                except Exception:
                    wait = int(r.headers.get("Retry-After") or 5)
                print(f"  {fid}: cooldown {wait}s, waiting...")
                time.sleep(max(wait, 1) + 0.5)
                continue
            break
        try:
            body = r.json()
        except Exception:
            body = r.text[:300]
        results[fid] = body
        print(f"  {fid}: {verdict_line(r.status_code, body)}")
    log = d / "submissions.jsonl"
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"t": time.time(), "results": results}) + "\n")


def verdict_line(status, body):
    ev = body.get("evaluation") if isinstance(body, dict) else None
    if not ev:
        return f"HTTP {status} {json.dumps(body)[:400]}"
    cases = ev.get("cases") or []
    bad = [c for c in cases if not c.get("isCorrect")]
    head = "CORRECT" if ev.get("isCorrect") else "WRONG"
    extra = {k: v for k, v in ev.items() if k not in ("isCorrect", "cases")}
    s = f"{head} ({len(cases) - len(bad)}/{len(cases)} cases)"
    if extra:
        s += f" {json.dumps(extra)[:300]}"
    for c in bad[:5]:
        s += f"\n      case lines {c.get('startLineNumber')}-{c.get('endLineNumberExcl')}: {c.get('caseState')} {c.get('caseMessage') or c.get('message') or ''}"
    return s


def cmd_go(a):
    a.only, a.solver, a.include_example = None, None, False
    if not cmd_run(a) and not a.force:
        sys.exit("Example mismatch or crash: not submitting (use --force to override).")
    cmd_submit(a)
    a.raw = False
    cmd_info(a)


def cmd_api(a):
    if a.game:
        r = game_req(a.method, a.path)
    else:
        r = platform_session().request(a.method, BASE + a.path)
    print(r.status_code, r.headers.get("content-type"))
    print(r.text[:5000])


def main():
    ap = argparse.ArgumentParser(description="CCC arena CLI")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("login").set_defaults(f=cmd_login)
    sp.add_parser("games").set_defaults(f=cmd_games)
    p = sp.add_parser("train"); p.add_argument("slug"); p.add_argument("--mode", default="exploration", choices=["exploration", "challenge"]); p.add_argument("--name"); p.set_defaults(f=cmd_train)
    p = sp.add_parser("contest"); p.add_argument("contest_name"); p.add_argument("--name"); p.set_defaults(f=cmd_contest)
    p = sp.add_parser("use"); p.add_argument("name"); p.set_defaults(f=cmd_use)
    p = sp.add_parser("info"); p.add_argument("--raw", action="store_true"); p.set_defaults(f=cmd_info)
    p = sp.add_parser("fetch"); p.add_argument("level", type=int); p.set_defaults(f=cmd_fetch)
    for nm, fn in (("run", cmd_run), ("submit", cmd_submit), ("go", cmd_go)):
        p = sp.add_parser(nm); p.add_argument("level", type=int)
        p.add_argument("--timeout", type=int, default=600)
        if nm != "go":
            p.add_argument("--only", nargs="*")
        if nm == "run":
            p.add_argument("--solver")
        if nm == "submit":
            p.add_argument("--include-example", action="store_true")
        if nm == "go":
            p.add_argument("--force", action="store_true")
        p.set_defaults(f=fn)
    p = sp.add_parser("api"); p.add_argument("method"); p.add_argument("path"); p.add_argument("--game", action="store_true"); p.set_defaults(f=cmd_api)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
