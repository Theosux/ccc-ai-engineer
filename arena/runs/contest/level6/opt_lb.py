import sys
from solve import parse, pattern_cells, Geo, NB
def skirt(geo,pc):
    s=set()
    for (y,x) in pc:
        for dy,dx in NB:
            c=(y+dy,x+dx)
            if c not in pc and c in geo.interior: s.add(c)
    return s
keys=[lambda c:c[0],lambda c:c[1]+c[0],lambda c:c[1]-c[0]]
for fid in sys.argv[1:]:
    pats=parse(open(f'files/in_level-6_{fid}.txt').read())
    progs=[b.strip().split("\n") for b in open(f'best/out_level-6_{fid}.txt').read().strip().split("\n\n")]
    T=0;T2=0;B=0
    for i,((r,p,c),pr) in enumerate(zip(pats,progs)):
        g=Geo(r);pc=pattern_cells(p);sk=skirt(g,pc)
        best=10**9
        for k in keys:
            lines={k(q) for q in pc}
            cost=0
            for L in lines:
                s=sum(1 for q in sk if k(q)==L)
                cost+=max(1,-(-s//4))
            best=min(best,cost)
        T+=best*c; B+=len(pr)
        T2+= -(-len(pc)//12)*c
    print(fid,'rowLB',T,'cross12LB',T2,'best',B)
