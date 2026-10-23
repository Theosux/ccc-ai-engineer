import sys
import ana_line3, ana_two, ana_line
from solve import parse, pattern_cells
ana_line3.DBG=1
pats=parse(open('files/in_level-6_'+sys.argv[1]+'.txt').read())
r,pat,cnt=pats[int(sys.argv[2])]
pc=pattern_cells(pat); G=ana_two.G(r,pc); G.pl=ana_line.Plan(r,pc)
for a in range(3):
    for sh in (False,True):
        p=ana_line3.solve_axis(G,cnt,a,sh)
        print(a,sh,None if p is None else len(p))
print(ana_line3.RJ)
