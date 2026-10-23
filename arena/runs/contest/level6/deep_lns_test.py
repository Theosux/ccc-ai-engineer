import sys, time, solve, deep_lns
fid=sys.argv[1]; ids=[int(x) for x in sys.argv[2].split(',')]; W=int(sys.argv[3]); tl=float(sys.argv[4])
pats=solve.parse(open(f'files/in_level-6_{fid}.txt').read())
best=deep_lns.load(f'best/out_level-6_{fid}.txt')
for i in ids:
    r,pat,cnt=pats[i]; t=time.time()
    p=deep_lns.improve(r,pat,cnt,best[i],W,tl,workers=2,deadline=time.time()+120,log=print)
    print(fid,i,'best',len(best[i]),'lns',len(p),solve.simulate(solve.Geo(r),solve.pattern_cells(pat),p),round(time.time()-t,1),flush=True)
