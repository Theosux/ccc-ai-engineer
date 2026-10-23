# Coordinator: merge all cand/ into best/ per file; submit files that improved by >= MIN_GAIN lines.
# python coord.py [min_gain]   (run from level6/)
import pathlib
import subprocess
import sys

here = pathlib.Path(__file__).resolve().parent
arena = here.parents[2]
MIN_GAIN = int(sys.argv[1]) if len(sys.argv) > 1 else 50
PYPY = str(arena / ".tools" / "pypy" / "pypy3.exe")
submitted = here / "best" / "submitted.txt"
sub = dict(l.split() for l in submitted.read_text().split("\n") if l.strip()) if submitted.exists() else {}


def total(p):
    return sum(len(pr.strip().split("\n")) for pr in p.read_text().strip().split("\n\n"))


changed = []
for fid in ["2-medium", "3-large", "4-enormous"]:
    b = here / "best" / f"out_level-6_{fid}.txt"
    cands = sorted(str(c) for c in (here / "cand").glob(f"*_{fid}.txt"))
    subprocess.run([PYPY, str(here / "merge.py"), fid, str(b)] + cands, check=True)
    t = total(b)
    old = int(sub.get(fid, 10**9))
    print(fid, "best", t, "submitted", old)
    if old - t >= MIN_GAIN:
        (here / "out" / b.name).write_bytes(b.read_bytes())
        changed.append(fid)
for fid in changed:
    r = subprocess.run([sys.executable, str(arena / "ccc.py"), "submit", "6", "--only", fid],
                       cwd=str(arena), capture_output=True, text=True)
    print(r.stdout[-400:])
    if "CORRECT" in r.stdout:
        sub[fid] = str(total(here / "best" / f"out_level-6_{fid}.txt"))
submitted.write_text("\n".join(f"{k} {v}" for k, v in sub.items()) + "\n")
print("SUBMITTED TOTAL", sum(int(v) for v in sub.values()))
