# deep: acceptance intervals in best programs
import sys
from solve import parse, pattern_cells, Geo, NB
def accticks(geo,pcells,prog):
    r=geo.r; pos=[0]+[(e-1)*r for e in range(1,7)]; act=[False]*7
    skirt=set()
    for (y,x) in pcells:
        for dy,dx in NB:
            c=(y+dy,x+dx)
            if c not in pcells and c in geo.interior: skirt.add(c)
    matter=set(); out=[]; m=geo.m
    for t,line in enumerate(prog):
        for e in range(1,7):
            ins=line[e-1]
            if ins=="F": pos[e]=(pos[e]+1)%m
            elif ins=="B": pos[e]=(pos[e]-1)%m
            elif ins=="T": act[e]=not act[e]
        cnt={}
        for e in range(1,7):
            if act[e]:
                for c in geo.rays[(pos[e],e)]: cnt[c]=cnt.get(c,0)+1
        for c,k in cnt.items():
            if k==2: matter.add(c)
            elif k>=3: matter.discard(c)
        if pcells<=matter and not (skirt&matter):
            matter-=pcells; out.append(t)
    return out
fid=sys.argv[1]
pats=parse(open(f'files/in_level-6_{fid}.txt').read())
best=[b.strip().split('\n') for b in open(f'best/out_level-6_{fid}.txt').read().strip().split('\n\n')]
agg={}
for i,((r,pat,cnt),b) in enumerate(zip(pats,best)):
    g=Geo(r); P=pattern_cells(pat)
    a=accticks(g,P,[l.split() for l in b])
    iv=[a[0]+1]+[a[k]-a[k-1] for k in range(1,len(a))]
    if len(sys.argv)>2 and (int(sys.argv[2])==r or int(sys.argv[2])<0): print(i,r,len(P),cnt,len(b),iv)
    d=agg.setdefault(r,[0,0,0]); d[0]+=iv[0]; d[1]+=sum(iv[1:]); d[2]+=len(iv)-1
print(fid,{r:(v[0],v[1],v[2],round(v[1]/max(1,v[2]),2)) for r,v in agg.items()})
