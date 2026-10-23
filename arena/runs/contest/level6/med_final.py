import solve,pathlib
here=pathlib.Path(__file__).resolve().parent
pats=solve.parse((here/"files/in_level-6_2-medium.txt").read_text())
c=[(here/f).read_text().strip().split("\n\n") for f in ("cand/med_b_2-medium.txt","cand/med_a_2-medium.txt","best/out_level-6_2-medium.txt")]
out=[];tot=0
for i,(r,pat,cnt) in enumerate(pats):
    g=solve.Geo(r);pc=solve.pattern_cells(pat)
    for k in sorted((x[i] for x in c),key=lambda s:len(s.split("\n"))):
        if solve.simulate(g,pc,[l.split() for l in k.split("\n")])==cnt:
            out.append(k);tot+=len(k.split("\n"));break
    else: raise SystemExit("fail %d"%i)
(here/"cand/med_final_2-medium.txt").write_text("\n\n".join(out)+"\n")
print(len(out),tot)
