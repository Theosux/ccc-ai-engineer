import sys
d = list(map(int, sys.stdin.read().split()))
n = d[0]; p = d[1:1+n]
print(p.index(min(p)))
