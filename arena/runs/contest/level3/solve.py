import sys

DIRS = {"1": (0, 2), "2": (1, 1), "3": (1, -1), "4": (0, -2), "5": (-1, -1), "6": (-1, 1)}


def parse(data):
    lines = data.split("\n")
    i = 0
    while not lines[i].strip():
        i += 1
    n = int(lines[i]); i += 1
    boards = []
    for _ in range(n):
        while not lines[i].strip():
            i += 1
        r, h, w = map(int, lines[i].split()); i += 1
        g = [list(lines[i + k].rstrip("\r")) for k in range(h)]
        i += h
        boards.append((r, h, w, g))
    return boards


def fire(g, h, w):
    cnt = {}
    for y in range(h):
        for x in range(len(g[y])):
            c = g[y][x]
            if c in DIRS:
                dy, dx = DIRS[c]
                cy, cx = y + dy, x + dx
                while 0 <= cy < h and 0 <= cx < len(g[cy]):
                    if g[cy][cx] in "OM":
                        cnt[(cy, cx)] = cnt.get((cy, cx), 0) + 1
                    cy += dy; cx += dx
    for (y, x), k in cnt.items():
        if k == 2:
            g[y][x] = "M"
        elif k >= 3:
            g[y][x] = "O"


def main():
    out = []
    for r, h, w, g in parse(sys.stdin.read()):
        fire(g, h, w)
        out.append("\n".join("".join(row) for row in g))
    print("\n\n".join(out))


if __name__ == "__main__":
    main()
