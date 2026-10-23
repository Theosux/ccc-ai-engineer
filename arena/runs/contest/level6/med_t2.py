import solve,pathlib
here=pathlib.Path(__file__).resolve().parent
for f in ["2-medium","3-large","4-enormous"]:
    pats=solve.parse((here/f"files/in_level-6_{f}.txt").read_text())
    a=b=c=reps=0
    for r,pat,cnt in pats:
        pc=solve.pattern_cells(pat)
        spans=[]
        for fn in (lambda y,x:y, lambda y,x:(x+y), lambda y,x:(x-y)):
            v={fn(y,x) for y,x in pc}
            spans.append(len(v))
        a+=cnt*spans[0]; b+=cnt*min(spans); reps+=cnt
    print(f,len(pats),"reps",reps,"rows*cnt",a,"min3*cnt",b)
