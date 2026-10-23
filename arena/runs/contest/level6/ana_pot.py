from solve import parse,pattern_cells,NB,Geo
for fid in ['2-medium','3-large','4-enormous']:
    pats=parse(open(f'files/in_level-6_{fid}.txt').read())
    best=[b.strip().split('\n') for b in open(f'best/out_level-6_{fid}.txt').read().strip().split('\n\n')]
    agg={}
    for (r,pat,cnt),b in zip(pats,best):
        P=pattern_cells(pat); g=Geo(r)
        S={(y+dy,x+dx) for y,x in P for dy,dx in NB}-P; S&=g.interior
        mh=99;L=0
        for a in range(3):
            k=lambda c:(c[0],c[1]-c[0],c[1]+c[0])[a]
            ks={k(c) for c in P}
            h=max(sum(1 for s in S if k(s)==kk) for kk in ks)
            if h<mh or (h==mh and len(ks)<L): mh,L=h,len(ks)
        key=min(mh,7)
        x=agg.setdefault(key,[0,0,0]); x[0]+=1; x[1]+=len(b); x[2]+=cnt*L
    print(fid,sorted(agg.items()))
