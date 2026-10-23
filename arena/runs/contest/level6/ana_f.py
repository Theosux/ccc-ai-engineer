import sys
from solve import parse, pattern_cells
F={}
def add(k,v): F[k]=F.get(k,0)+v
for fid in ['2-medium','3-large','4-enormous']:
    pats=parse(open(f'files/in_level-6_{fid}.txt').read())
    for r,pat,cnt in pats:
        P=pattern_cells(pat)
        keys=[(lambda c:c[0]),(lambda c:(c[1]-c[0])//2),(lambda c:(c[1]+c[0])//2)]
        # center line value for each axis: center cell (r,2r)
        cen=[r,(2*r-r)//2,(2*r+r)//2]
        L=[];D=[]
        for a,k in enumerate(keys):
            vals={k(c) for c in P}
            lo,hi=min(vals),max(vals)
            L.append(len(vals))
            span=hi-lo+1
            c0=cen[a]
            d=0 if lo<=c0<=hi else min(abs(c0-lo),abs(c0-hi))
            D.append((span,d,lo,hi,c0))
        add('rows',cnt*L[0]); add('A',cnt*L[1]); add('B',cnt*L[2])
        add('min',cnt*min(L))
        add('minspan',cnt*min(x[0] for x in D))
        add('min_span_d',min(cnt*x[0]+x[1] for x in D))
        # travel with inside: go to nearer end
        add('min_span_trav',min(cnt*s+(d if d>0 else min(c0-lo,hi-c0)) for s,d,lo,hi,c0 in D))
        add('rows_span',cnt*D[0][0])
        add('min+1',cnt*min(L)+1)
        add('cnt',cnt)
print(F)
