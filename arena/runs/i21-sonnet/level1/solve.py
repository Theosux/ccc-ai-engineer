import sys
data = sys.stdin.read().split()
t = data[1:]
out = []
i = 0
while i < len(t):
    if t[i] == "print":
        out.append(t[i + 1]); i += 2
    else:
        i += 1
sys.stdout.write("".join(out))
