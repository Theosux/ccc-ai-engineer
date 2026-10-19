import sys
d = sys.stdin.read().split()
n = int(d[0]); p = list(map(int, d[1:1+n]))
pre = [0]
for x in p: pre.append(pre[-1]+x)
m = int(d[1+n]); i = 2+n
out = [str(m)]
for _ in range(m):
    t, c = int(d[i]), int(d[i+1]); i += 2
    best = None; bs = 0
    for s in range(n-c+1):
        v = pre[s+c]-pre[s]
        if best is None or v < best:
            best = v; bs = s
    out.append(f"{t} {bs}")
print("\n".join(out))
