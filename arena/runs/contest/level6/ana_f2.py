from solve import parse, pattern_cells
data=[]
for fid in ['2-medium','3-large','4-enormous']:
    for r,pat,cnt in parse(open(f'files/in_level-6_{fid}.txt').read()):
        P=pattern_cells(pat)
        ax=[]
        for a in range(3):
            ks=sorted({(c[0],(c[1]-c[0])//2,(c[1]+c[0])//2)[a] for c in P})
            c0=[r,r//2,(3*r)//2][a]
            lo,hi=ks[0],ks[-1]
            ax.append((len(ks),hi-lo+1,lo,hi,c0))
        data.append((r,cnt,len(P),ax))
def tot(f): return sum(f(*d) for d in data)
def dist(lo,hi,c0): return 0 if lo<=c0<=hi else min(abs(c0-lo),abs(c0-hi))
def near(lo,hi,c0): return min(abs(c0-lo),abs(c0-hi))
V={
 'L':lambda r,c,n,ax:min(c*a[0] for a in ax),
 'L+d':lambda r,c,n,ax:min(c*a[0]+dist(a[2],a[3],a[4]) for a in ax),
 'L+d-1':lambda r,c,n,ax:min(c*a[0]+max(0,dist(a[2],a[3],a[4])-1) for a in ax),
 'L+near':lambda r,c,n,ax:min(c*a[0]+near(a[2],a[3],a[4]) for a in ax),
 'L+1':lambda r,c,n,ax:min(c*a[0]+1 for a in ax),
 'rowsL+d':lambda r,c,n,ax:c*ax[0][0]+dist(ax[0][2],ax[0][3],ax[0][4]),
 'rowsL+near':lambda r,c,n,ax:c*ax[0][0]+near(ax[0][2],ax[0][3],ax[0][4]),
 'L+d+1':lambda r,c,n,ax:min(c*a[0]+dist(a[2],a[3],a[4])+1 for a in ax),
 'Lmin_then_d':lambda r,c,n,ax:(lambda a:c*a[0]+dist(a[2],a[3],a[4]))(min(ax,key=lambda a:a[0])),
}
for k,f in V.items(): print(k,tot(f))
