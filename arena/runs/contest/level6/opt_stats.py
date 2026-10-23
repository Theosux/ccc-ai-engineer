import sys
from solve import parse, pattern_cells, Geo
fid=sys.argv[1]
pats=parse(open(f'files/in_level-6_{fid}.txt').read())
progs=[b.strip().split("\n") for b in open(f'best/out_level-6_{fid}.txt').read().strip().split("\n\n")]
tot=0
for i,((r,pat,cnt),pr) in enumerate(zip(pats,progs)):
    pc=pattern_cells(pat)
    ys={y for y,x in pc}; d1={(x+y)//1 for y,x in pc}; d2={(x-y) for y,x in pc}
    print(i,r,cnt,len(pc),'rows',len(ys),'d',len(d1),len(d2),'lines',len(pr),'perrep %.1f'%(len(pr)/cnt))
    tot+=len(pr)
print(tot)
