import sys
from solve import *
import ana_line3, ana_two
pats=parse(open('files/in_level-6_'+sys.argv[1]+'.txt').read())
r,pat,cnt=pats[int(sys.argv[2])]
pc=pattern_cells(pat); G=ana_two.G(r,pc); geo=G.g
prog=ana_line3.solve_axis(G,cnt,int(sys.argv[3]),False)
print(len(prog) if prog else None, 'cnt',cnt)
pos=[0]+[(e-1)*r for e in range(1,7)]; act=[False]*7; matter=set(); acc=0
for t,line in enumerate(prog):
    for e in range(1,7):
        ins=line[e-1]
        if ins=='F': pos[e]=(pos[e]+1)%geo.m
        elif ins=='B': pos[e]=(pos[e]-1)%geo.m
        elif ins=='T': act[e]=not act[e]
    c_={}
    for e in range(1,7):
        if act[e]:
            for c in geo.rays[(pos[e],e)]: c_[c]=c_.get(c,0)+1
    for c,k in c_.items():
        if k==2: matter.add(c)
        elif k>=3: matter.discard(c)
    ok= pc<=matter and not (G.S&matter)
    if ok: matter-=pc; acc+=1
    print(t,' '.join(line),'row',pos[1],'miss',sorted(pc-matter)[:4],'bad',sorted(G.S&matter)[:4],'ACC' if ok else '')
