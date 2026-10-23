import solve,pathlib
here=pathlib.Path(__file__).resolve().parent
pats=solve.parse((here/"files/in_level-6_2-medium.txt").read_text())
best=(here/"best/out_level-6_2-medium.txt").read_text().strip().split("\n\n")
tb=(here/"cand/tbeam_W16_2-medium.txt").read_text().strip().split("\n\n")
rows=[]
for i,(r,pat,cnt) in enumerate(pats):
    pc=solve.pattern_cells(pat)
    ys=len({y for y,x in pc})
    rows.append((i,r,len(pc),ys,cnt,len(best[i].split("\n")),len(tb[i].split("\n"))))
print(sum(x[5] for x in rows),sum(x[6] for x in rows))
for x in sorted(rows,key=lambda x:-x[5])[:25]:print(x, x[5]/x[4])
