import sys
d = sys.stdin.read().split("\n")
n = int(d[0])
print("\n".join(str(sum(map(int, d[i + 1].split()))) for i in range(n)))
