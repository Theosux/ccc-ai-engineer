import sys
from solve import *
import ana_relax as ana_line
ana_line.DBG=1
pats=parse(open('files/in_level-6_'+sys.argv[1]+'.txt').read())
r,pat,cnt=pats[int(sys.argv[2])]
pc=pattern_cells(pat); pl=ana_line.Plan(r,pc)
for a in range(3):
    # holes per line
    keys=sorted({ana_line.keyf(a,c) for c in pc})
    hs=[sum(1 for c in pl.S if ana_line.keyf(a,c)==k) for k in range(keys[0],keys[-1]+1,1 if a==0 else 2)]
    print('axis',a,'holes',hs)
    p=ana_line.solve_axis(pl,cnt,a,False,W=24,maxwait=12)
    print('len',None if p is None else len(p))
