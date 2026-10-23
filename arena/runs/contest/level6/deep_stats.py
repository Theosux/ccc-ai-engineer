# deep: per-pattern stats vs best/
import sys
from solve import parse, pattern_cells, Geo, NB
def load(path):
    return [b.strip().split('\n') for b in open(path).read().strip().split('\n\n')]
for fid in sys.argv[1:]:
    pats=parse(open(f'files/in_level-6_{fid}.txt').read())
    best=load(f'best/out_level-6_{fid}.txt')
    tc=tb=0; rs={}
    rows=[]
    for i,((r,pat,cnt),b) in enumerate(zip(pats,best)):
        P=pattern_cells(pat)
        tc+=cnt; tb+=len(b)
        rs.setdefault(r,[0,0,0]); rs[r][0]+=1; rs[r][1]+=cnt; rs[r][2]+=len(b)
        rows.append((len(b)-cnt,i,r,len(P),cnt,len(b)))
    print(fid,'n',len(pats),'sumcnt',tc,'best',tb,'byr',rs)
    rows.sort(reverse=True)
    for x in rows[:15]: print('  over',x)
