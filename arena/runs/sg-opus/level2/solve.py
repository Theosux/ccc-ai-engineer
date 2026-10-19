import sys
import numpy as np
d = list(map(int, sys.stdin.read().split()))
i = 0
n = d[i]; i += 1
p = np.array(d[i:i+n], dtype=np.int64); i += n
m = d[i]; i += 1
pre = np.concatenate([[0], np.cumsum(p)])
out = [str(m)]
for _ in range(m):
    tid, L = d[i], d[i+1]; i += 2
    sums = pre[L:] - pre[:n-L+1]
    out.append(f"{tid} {int(np.argmin(sums))}")
print("\n".join(out))
