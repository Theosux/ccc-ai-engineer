import sys
d = sys.stdin.read().split()
n = int(d[0]); p = list(map(int, d[1:1+n]))
print(p.index(min(p)))
