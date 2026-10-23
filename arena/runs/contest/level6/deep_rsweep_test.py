import sys, time, solve, deep_rsweep
fid=sys.argv[1]; ids=[int(x) for x in sys.argv[2].split(',')]
pats=solve.parse(open(f'files/in_level-6_{fid}.txt').read())
best=[b.strip().split('\n') for b in open(f'best/out_level-6_{fid}.txt').read().strip().split('\n\n')]
for i in ids:
    r,pat,cnt=pats[i]; g=solve.Geo(r); pc=solve.pattern_cells(pat); t=time.time()
    try: L=deep_rsweep.best_sweep2(g,pc,cnt)
    except Exception as ex: L=None; print('err',ex)
    ok = L is not None and solve.simulate(g,pc,[l.split() for l in L])==cnt
    print(fid,i,'best',len(best[i]),'rsweep',len(L) if L else None,ok,round(time.time()-t,1),flush=True)
