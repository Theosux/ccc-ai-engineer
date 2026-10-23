import sys
from solve import parse, pattern_cells, Geo, NB
def runs(vals):
    vals=sorted(vals); n=0; prev=None
    for v in vals:
        if prev is None or v-prev!=2: n+=1
        prev=v
    return n
def stats(r,pat,cnt):
    P=pattern_cells(pat)
    ax=[lambda c:c[0], lambda c:c[1]-c[0], lambda c:c[1]+c[0]]
    pos=[lambda c:c[1], lambda c:c[0], lambda c:c[0]]
    res=[]
    for a,p in zip(ax,pos):
        lines={}
        for c in P: lines.setdefault(a(c),[]).append(c)
        nl=len(lines)
        # runs along line, position step: rows x step2; diags y step1
        nr=0
        for k,cs in lines.items():
            vs=sorted(p(c) for c in cs); prev=None
            step=2 if a is ax[0] else 1
            for v in vs:
                if prev is None or v-prev!=step: nr+=1
                prev=v
        res.append((nl,nr))
    return len(P),res
fid=sys.argv[1]
pats=parse(open(f'files/in_level-6_{fid}.txt').read())
best=[b.strip().split('\n') for b in open(f'best/out_level-6_{fid}.txt').read().strip().split('\n\n')]
T={}
def add(k,v): T[k]=T.get(k,0)+v
for (r,pat,cnt),b in zip(pats,best):
    n,res=stats(r,pat,cnt)
    add('cnt',cnt); add('cells',n); add('cells*cnt',n*cnt); add('best',len(b))
    add('rows*cnt',res[0][0]*cnt); add('minlines*cnt',min(x[0] for x in res)*cnt)
    add('minruns*cnt',min(x[1] for x in res)*cnt); add('rowruns*cnt',res[0][1]*cnt)
    add('sumlines/?',0)
    add('n',1)
    add('ceil3',-(-min(x[0] for x in res)//3)*cnt)
    if len(sys.argv)>2: print(r,cnt,n,res,len(b))
print(fid,T)
