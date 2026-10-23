import sys, collections
import ana_two as T
from solve import parse,pattern_cells
fid,i=sys.argv[1],int(sys.argv[2])
p=parse(open(f'files/in_level-6_{fid}.txt').read())
r,pat,cnt=p[i]
G=T.G(r,pattern_cells(pat))
cl=T.plan_cost_list(G,cnt,maxc=100000)
print(len(cl), cl[0][0])
R=collections.Counter()
for c in cl:
    a,b,cc,A_,B_=c[1:]
    K=len(A_); why='ok'
    for rev in (False,True):
        As = A_[::-1] if rev else A_; Bs = B_[::-1] if rev else B_
        need=[set() for _ in range(K)]; forb=[set() for _ in range(K)]
        for X in G.R:
            ka,kb,kc=T.keyf(a,X),T.keyf(b,X),T.keyf(cc,X)
            last=-1
            for t in range(K-1,-1,-1):
                if As[t]==ka or Bs[t]==kb: last=t;break
            isP=X in G.P
            if last<0:
                if isP: why='uncov'
                continue
            inter=As[last]==ka and Bs[last]==kb
            if isP:
                if inter: why='Pinter'
                forb[last].add(kc)
            elif not inter: need[last].add(kc)
        if why=='ok':
            for t in range(K):
                if len(need[t])>2: why='need>2'
                elif need[t]&forb[t]: why='nf'
        if why!='ok': break
    R[(c[0],why)]+=1
for k in sorted(R)[:30]: print(k,R[k])
