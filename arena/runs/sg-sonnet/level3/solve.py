import sys
d = sys.stdin.read().split()
n = int(d[0]); p = list(map(int, d[1:1+n]))
m = int(d[1+n]); i = 2+n
out = [str(m)]
for _ in range(m):
    t, w, a, b = map(int, d[i:i+4]); i += 4
    best = min(range(a, b+1), key=lambda k: (p[k], k))
    out.append(f"{t} {best} {w}")
print("\n".join(out))
