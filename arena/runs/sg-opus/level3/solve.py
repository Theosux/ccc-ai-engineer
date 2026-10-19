import sys
import numpy as np
d = list(map(int, sys.stdin.read().split()))
i = 0
n = d[i]; i += 1
p = np.array(d[i:i+n], dtype=np.int64); i += n
m = d[i]; i += 1
out = [str(m)]
for _ in range(m):
    tid, pw, s, e = d[i:i+4]; i += 4
    k = s + int(np.argmin(p[s:e+1]))
    out.append(f"{tid} {k} {pw}")
print("\n".join(out))
