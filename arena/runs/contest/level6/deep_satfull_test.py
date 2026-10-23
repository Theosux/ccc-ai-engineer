import sys, time, solve, deep_sat
fid=sys.argv[1]; ids=[int(x) for x in sys.argv[2].split(',')]; tl=float(sys.argv[3]); slack=int(sys.argv[4]) if len(sys.argv)>4 else 0
pats=solve.parse(open(f'files/in_level-6_{fid}.txt').read())
best=[b.strip().split('\n') for b in open(f'best/out_level-6_{fid}.txt').read().strip().split('\n\n')]
for i in ids:
    r,pat,cnt=pats[i]; I=deep_sat.Inst(r,pat); t=time.time()
    h=[l.split() for l in best[i]]
    res=deep_sat.build_full(I,len(h)+slack,cnt,deep_sat.init_state(r),hint=h,tlimit=tl)
    if res is None: print(i,r,cnt,'best',len(h),'none',round(time.time()-t,1)); continue
    L,opt=res; ok=solve.simulate(I.g,I.pc,[l.split() for l in L])
    print(i,r,cnt,'best',len(h),'full',len(L),'opt' if opt else '', 'acc',ok,round(time.time()-t,1),flush=True)
