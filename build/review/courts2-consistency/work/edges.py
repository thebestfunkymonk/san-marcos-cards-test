import sys
from PIL import Image
import numpy as np
D='build/review/courts2-consistency'
paper=np.array([0xf2,0xee,0xe3])
def runs(col):
    out=[];start=None
    for i,v in enumerate(col):
        if v and start is None: start=i
        if not v and start is not None: out.append((start,i));start=None
    if start is not None: out.append((start,len(col)))
    return out
for c in "KS QS JS KH QH JH KC QC JC KD QD JD".split():
    res=[]
    for v in ('before','after'):
        im=np.asarray(Image.open(f'{D}/{v}_3x/{c}.png').convert('RGB')).astype(int)
        p=im[0,0]  # maybe not paper
        for name,x in (('L',3*140+3),('R',3*610-3)):
            col=im[3*56:3*510,x]
            # paper-ish: close to card paper colour sampled at (3*145,3*60)?
            ref=im[3*300,3*20]
            nonp=np.abs(col-ref).sum(1)>40
            r=[(round((a+3*56)/3),round((b+3*56)/3)) for a,b in runs(nonp) if b-a>3]
            res.append(f"{v[0]}{name}:{r}")
    print(c, *res, sep='\n  ')
