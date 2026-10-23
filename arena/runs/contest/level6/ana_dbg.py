import sys
from solve import *
import ana_line
pats=parse(open('files/in_level-6_4-enormous.txt').read())
r,pat,cnt=pats[int(sys.argv[1])]
pc=pattern_cells(pat); pl=ana_line.Plan(r,pc)
prog=ana_line.solve_axis(pl,cnt,int(sys.argv[2]),False)
print(len(prog))
geo=pl.g
# replay
pos=[0]+[(e-1)*r for e in range(1,7)]; act=[False]*7; matter=set(); acc=0
for t,line in enumerate(prog):
    for e in range(1,7):
        ins=line[e-1]
        if ins=='F': pos[e]=(pos[e]+1)%geo.m
        elif ins=='B': pos[e]=(pos[e]-1)%geo.m
        elif ins=='T': act[e]=not act[e]
    cnt_={}
    for e in range(1,7):
        if act[e]:
            for c in geo.rays[(pos[e],e)]: cnt_[c]=cnt_.get(c,0)+1
    for c,k in cnt_.items():
        if k==2: matter.add(c)
        elif k>=3: matter.discard(c)
    miss=pc-matter; bad=pl.S&matter
    print(t,' '.join(line),[(e,pos[e],act[e]) for e in range(1,7)],'miss',len(miss),'badskirt',sorted(bad))
pos=[0]+[(e-1)*r for e in range(1,7)]; act=[False]*7
X=(5,16)
for t,line in enumerate(prog[:22]):
    for e in range(1,7):
        ins=line[e-1]
        if ins=='F': pos[e]=(pos[e]+1)%geo.m
        elif ins=='B': pos[e]=(pos[e]-1)%geo.m
        elif ins=='T': act[e]=not act[e]
    print(t,[e for e in range(1,7) if act[e] and X in geo.rays[(pos[e],e)]])
