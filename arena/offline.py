"""Offline CCC games: past contests from GitHub archives, played through the SAME ccc.py loop (fetch/go/submit),
judged locally against reference outputs (+ optional per-level judge for non-unique answers).

    python arena/offline.py build pacman          # once: arena/.data/games/pacman/ (zips, expected/, game.json)
    python arena/offline.py start pacman --name pacman   # register an offline run, make it active, fetch level 1
    python arena/ccc.py go 1 ...                  # as usual; levels unlock as you pass them; timing.jsonl logged
    python arena/offline.py list

Sources live in arena/.data/<repo> (gitignored, untrusted: reference scripts run with `python -I`).
Judge for a level (written by a separate agent so the trainee stays unspoiled):
    arena/.data/games/<game>/judges/levelN.py  with  judge(inp: str, out: str) -> (bool, str)
It is used when the output differs from the reference, or when there is no reference.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ARENA = Path(__file__).resolve().parent
DATA = ARENA / ".data"
GAMES = DATA / "games"
GE = DATA / "gergely-elias_ccc"

# name -> how to find statement PDFs, inputs (example first) and reference outputs
SOURCES = {
    "pacman": {"kind": "gergely", "dir": "pacman", "levels": 7},
    "islands": {"kind": "gergely", "dir": "islands", "levels": 7, "untrusted_archive": {6}},  # blu3r4y: L6 unsolved
    "smartgrid": {"kind": "gergely", "dir": "smartgrid", "levels": 7,
                  "scripts": {4: "level4_graph_theory.py"}},
    "interp2021": {"kind": "blu3r4y", "dir": "blu3r4y_ccc-linz-nov2021", "levels": 4},
    "lawnmower-gh": {"kind": "gergely", "dir": "lawn_mower", "levels": 4, "refs_run": "lawnmower"},  # judge replay test
}


def sha(b):
    return hashlib.sha1(b.replace(b"\r\n", b"\n").strip()).hexdigest()


def blu3r4y_outputs():
    """content hash of input -> output bytes, from every blu3r4y archive (their outputs passed the real judge)."""
    m = {}
    for repo in DATA.glob("blu3r4y_*"):
        for inp in (repo / "data").rglob("*.in"):
            out = inp.with_suffix(".out")
            if out.exists():
                m[sha(inp.read_bytes())] = out.read_bytes()
    return m


def level_inputs(src, n):
    """[(fileId, input Path, example output Path or None)], example first."""
    if src["kind"] == "gergely":
        d = GE / src["dir"] / "input" / f"level{n}"
        ex = d / f"level{n}_example.in"
        res = [("0-example", ex, d / f"level{n}_example.out")] if ex.exists() else []
        nums = sorted((p for p in d.glob(f"level{n}_*.in") if p.stem.split("_")[1].isdigit()),
                      key=lambda p: int(p.stem.split("_")[1]))
        return res + [(p.stem.split("_")[1], p, None) for p in nums]
    d = DATA / src["dir"] / "data" / f"level{n}"
    ps = sorted(d.glob(f"level{n}_*.in"), key=lambda p: int(p.stem.split("_")[1]))
    # 2021 archive has no separate example: the first file is shown as the example (with its output)
    return [("0-example" if i == 0 else p.stem.split("_")[1], p, p.with_suffix(".out") if i == 0 else None)
            for i, p in enumerate(ps)]


def level_pdf(src, n):
    base = GE / src["dir"] / "description" if src["kind"] == "gergely" else DATA / src["dir"] / "data"
    p = base / f"Level {n}.pdf"
    return p if p.exists() else None


def ref_script(src, n):
    if src.get("refs_run"):  # our own solvers that passed the real judge
        p = ARENA / "runs" / src["refs_run"] / f"level{n}" / "solve.py"
        return p if p.exists() else None
    if src["kind"] != "gergely":
        return None
    name = (src.get("scripts") or {}).get(n, f"level{n}.py")
    p = GE / src["dir"] / name
    return p if p.exists() else None


def run_ref(script, inp, timeout=600):
    with inp.open("rb") as f:
        p = subprocess.run([sys.executable, "-I", str(script)], stdin=f, capture_output=True, timeout=timeout,
                           cwd=script.parent)
    return p.stdout if p.returncode == 0 else None


def cmd_build(a):
    src = SOURCES[a.game]
    g = GAMES / a.game
    (g / "expected").mkdir(parents=True, exist_ok=True)
    (g / "judges").mkdir(exist_ok=True)
    known = blu3r4y_outputs()
    info = {"name": a.game, "levels": [], "refs": {}}
    for n in range(1, src["levels"] + 1):
        files = level_inputs(src, n)
        pdf = level_pdf(src, n)
        zpath = g / f"level-{n}.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            if pdf:
                z.write(pdf, f"level-{n}.pdf")
            for fid, inp, exp in files:
                z.write(inp, f"in_level-{n}_{fid}.txt")
                if exp and exp.exists():
                    z.write(exp, f"out_level-{n}_{fid}.txt")
        ed = g / "expected" / f"level{n}"
        shutil.rmtree(ed, ignore_errors=True)
        ed.mkdir()
        script, refs = ref_script(src, n), {}
        for fid, inp, exp in files:
            out, how = None, None
            if exp and exp.exists():
                out, how = exp.read_bytes(), "example"
            elif sha(inp.read_bytes()) in known and n not in src.get("untrusted_archive", ()):
                out, how = known[sha(inp.read_bytes())], "archive"
            elif script:
                try:
                    out, how = run_ref(script, inp), "script"
                except subprocess.TimeoutExpired:
                    out = None
            if out:
                (ed / f"{fid}.txt").write_bytes(out.replace(b"\r\n", b"\n"))
                refs[fid] = how
        ids = [fid for fid, _, _ in files]
        info["levels"].append({"inputFiles": ids, "unscoredFiles": [i for i in ids if "example" in i],
                               "sandbox": False, "optimization": False})
        info["refs"][n] = refs
        print(f"level {n}: {len(files)} inputs, pdf={'yes' if pdf else 'NO'}, refs {refs}")
    (g / "game.json").write_text(json.dumps(info, indent=1), encoding="utf-8")


def cmd_start(a):
    sys.path.insert(0, str(ARENA))
    import ccc
    g = GAMES / a.game
    info = json.loads((g / "game.json").read_text(encoding="utf-8"))
    name = a.name or a.game
    if (ccc.RUNS / name).exists() and any((ccc.RUNS / name).glob("level*")) and not a.force:
        ccc.die(f"run {name!r} already exists (use --name or --force)")
    ccc.update_run(name, contestName=f"offline-{a.game}", contestSlug=f"offline-{a.game}", gameBaseUrl="",
                   token=None, offline=True, offlineGame=a.game)
    st = ccc.state()
    st["active"] = name
    ccc.save_json(ccc.STATE, st)
    rd = ccc.run_dir(name)
    ccc.save_json(rd / "game-info.json", {"name": f"offline {a.game}",
                                          "levelsInfo": {"count": len(info["levels"]), "levels": info["levels"]}})
    for f in ("offline-score.json", "timing.jsonl"):
        (rd / f).unlink(missing_ok=True)
    print(f"offline run {name} active: game {a.game}, {len(info['levels'])} levels")
    ccc.fetch_level((name, ccc.state()["runs"][name], ccc.state()), 1)


def cmd_list(a):
    for g in sorted(GAMES.glob("*/game.json")):
        info = json.loads(g.read_text(encoding="utf-8"))
        judges = sorted(p.stem for p in (g.parent / "judges").glob("level*.py"))
        print(f"{info['name']:14} {len(info['levels'])} levels  judges: {judges or '-'}")
        for n, refs in info["refs"].items():
            ids = info["levels"][int(n) - 1]["inputFiles"]
            print(f"   L{n}: refs {len(refs)}/{len(ids)} ({', '.join(sorted(set(refs.values()))) or 'none'})")


def main():
    ap = argparse.ArgumentParser(description="offline CCC games")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("build"); p.add_argument("game", choices=sorted(SOURCES)); p.set_defaults(f=cmd_build)
    p = sp.add_parser("start"); p.add_argument("game"); p.add_argument("--name"); p.add_argument("--force", action="store_true")
    p.set_defaults(f=cmd_start)
    sp.add_parser("list").set_defaults(f=cmd_list)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
