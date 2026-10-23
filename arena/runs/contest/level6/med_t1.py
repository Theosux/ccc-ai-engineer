import sys,time
from med_cyc import *
pats = solve.parse((here / "files/in_level-6_2-medium.txt").read_text())
best = (here/"best/out_level-6_2-medium.txt").read_text().strip().split("\n\n")
for i in map(int,sys.argv[1].split(",")):
    r,pat,cnt=pats[i]; geo=solve.Geo(r); pc=solve.pattern_cells(pat)
    bl=best[i].split("\n")
    sts=states(geo,pc,bl)
    print(i,"cnt",cnt,"best",len(bl),"first-rep acc ticks",len(bl)/cnt, "cells",len(pc))
    for S0 in sts[:3]:
        t=time.time()
        for W in (8,32):
            L=closed_rep(geo,pc,S0,W,80)
            print(" W",W,"L",None if L is None else len(L),time.time()-t)
