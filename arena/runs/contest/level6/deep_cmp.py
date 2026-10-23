# deep: compare deep_tb variants (no limit pruning) on chosen patterns. usage: deep_cmp.py fid W "wo:wd,.." i,j,k
import sys, time, multiprocessing as mp
import solve, deep_tb
def w(a):
    fid,W,vs,i=a
    pats=solve.parse(open(f'files/in_level-6_{fid}.txt').read()); r,pat,cnt=pats[i]
    g=solve.Geo(r); pc=solve.pattern_cells(pat); out=[]
    for wo,wd in vs:
        t=time.time(); L=deep_tb.search(g,pc,cnt,W,wo,wd,400)
        ok = L is not None and solve.simulate(g,pc,[x.split() for x in L])==cnt
        out.append((wo,wd,len(L) if L else None,ok,round(time.time()-t,1)))
    return i,out
if __name__=="__main__":
    fid=sys.argv[1]; W=int(sys.argv[2]); vs=[tuple(int(v) for v in x.split(':')) for x in sys.argv[3].split(',')]
    ids=[int(x) for x in sys.argv[4].split(',')]
    best=[b.strip().split('\n') for b in open(f'best/out_level-6_{fid}.txt').read().strip().split('\n\n')]
    with mp.Pool(4) as p:
        for i,o in p.imap_unordered(w,[(fid,W,vs,i) for i in ids]): print(i,'best',len(best[i]),o,flush=True)
