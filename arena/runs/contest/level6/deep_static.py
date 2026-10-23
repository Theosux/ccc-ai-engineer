# deep: period-1 (static) feasibility in line space: <=2 lines per axis, count==2 on all P, !=2 on S
import sys, itertools
from solve import parse, pattern_cells, Geo, NB
def skirt(g,P):
    S=set()
    for (y,x) in P:
        for dy,dx in NB:
            c=(y+dy,x+dx)
            if c not in P and c in g.interior: S.add(c)
    return S
KEY=[lambda c:c[0], lambda c:c[1]-c[0], lambda c:c[1]+c[0]]
def axis_opts(g,a):
    keys=sorted({KEY[a](c) for c in g.interior})
    opts=[()]+[(k,) for k in keys]+list(itertools.combinations_with_replacement(keys,2))
    return opts
def static_feasible(g,P,S):
    cells=sorted(P|S); idx={c:i for i,c in enumerate(cells)}
    isP=[c in P for c in cells]
    res=[]
    A=[]
    for a in range(3):
        L=[]
        for o in axis_opts(g,a):
            v=[0]*len(cells)
            for i,c in enumerate(cells):
                k=KEY[a](c); v[i]=sum(1 for q in o if q==k)
            L.append((o,v))
        A.append(L)
    n=len(cells)
    for o0,v0 in A[0]:
        for o1,v1 in A[1]:
            v01=[v0[i]+v1[i] for i in range(n)]
            # prune: P cell already >2 impossible
            if any(v01[i]>2 and isP[i] for i in range(n)): continue
            for o2,v2 in A[2]:
                ok=True
                for i in range(n):
                    s=v01[i]+v2[i]
                    if isP[i]:
                        if s!=2: ok=False;break
                    elif s==2: ok=False;break
                if ok: return (o0,o1,o2)
    return None
if __name__=="__main__":
    fid=sys.argv[1]
    pats=parse(open(f'files/in_level-6_{fid}.txt').read())
    nf=0;cc=0
    for i,(r,pat,cnt) in enumerate(pats):
        g=Geo(r); P=pattern_cells(pat); S=skirt(g,P)
        f=static_feasible(g,P,S)
        if f: nf+=1; cc+=cnt; print(i,r,len(P),cnt,f,flush=True)
    print('feasible',nf,'copies',cc)
