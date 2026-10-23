import sys, opt_macro
from solve import parse, Geo, pattern_cells
opt_macro.TRACE=1
fid=sys.argv[1]; i=int(sys.argv[2])
r,pat,cnt=parse(open(f"files/in_level-6_{fid}.txt").read())[i]
l=opt_macro.plan(Geo(r),pattern_cells(pat),cnt)
print(len(l))
