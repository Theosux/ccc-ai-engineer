import sys
d = sys.stdin.read().split("\n")
n = int(d[0])
res = []
for i in range(n):
    p = list(map(int, d[i + 1].split()))
    pos = sum((x > 0) - (x < 0) for x in p)
    t = sum(abs(x) if x else 1 for x in p)
    res.append(f"{pos} {t}")
print("\n".join(res))
