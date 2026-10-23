import sys
from solve import parse, pattern_cells
for fid in ['2-medium','3-large','4-enormous']:
    pats=parse(open(f'files/in_level-6_{fid}.txt').read())
    best=[b.strip().split('\n') for b in open(f'best/out_level-6_{fid}.txt').read().strip().split('\n\n')]
    rows=[]
    for i,((r,pat,cnt),b) in enumerate(zip(pats,best)):
        P=pattern_cells(pat)
        L=[len({(c[0],c[1]-c[0],c[1]+c[0])[a] for c in P}) for a in range(3)]
        rows.append((len(b)-cnt*min(L),i,r,cnt,len(P),min(L),len(b)))
    rows.sort(reverse=True)
    pos=sum(x[0] for x in rows if x[0]>0); neg=sum(x[0] for x in rows if x[0]<0)
    print(fid,'gap+',pos,'gap-',neg)
    # buckets by cnt
    from collections import defaultdict
    B=defaultdict(lambda:[0,0,0,0])
    for g,i,r,cnt,n,ml,bl in rows:
        k=min(cnt,9); B[k][0]+=1;B[k][1]+=bl;B[k][2]+=cnt*ml;B[k][3]+=n*cnt
    for k in sorted(B): print('  cnt',k,B[k])
    print(rows[:8])
