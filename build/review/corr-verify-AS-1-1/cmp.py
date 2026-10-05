import re, sys
sys.path.insert(0,'.')
from inkkit import geom as G
import numpy as np
def paths(fn):
    s=open(fn).read()
    out=[]
    for layer in ['paper','jade','red','ink','gold']:
        i=s.index(f'id="{layer}"'); j=s.find('</g>',i)
        seg=s[i:j]
        for d,attrs in re.findall(r'<path d="([^"]+)"([^>]*)>',seg):
            out.append((layer,d,attrs))
    return out
old=paths('build/gallery/svg/AS.svg'); new=paths('cards/AS.svg')
print(len(old),len(new))
same=0; moved=0; diff=[]
for k,((lo,do,ao),(ln,dn,an)) in enumerate(zip(old,new)):
    if do==dn and ao==an: same+=1; continue
    if ao!=an: diff.append((k,'attrs',ao[:80],an[:80])); continue
    try:
        t=G.translate(do,0,92.0)
        po=G.bbox(t); pn=G.bbox(dn)
        if np.allclose(po,pn,atol=0.02):
            # compare point sets
            fo=G.flatten(t,0.05); fn=G.flatten(dn,0.05)
            ok=len(fo)==len(fn) and all(len(a[0])==len(b[0]) and np.allclose(a[0],b[0],atol=0.02) for a,b in zip(fo,fn))
            if ok: moved+=1; continue
        diff.append((k,ln,[round(v,2) for v in G.bbox(do)],[round(v,2) for v in pn]))
    except Exception as e:
        diff.append((k,'err',str(e)))
print('same',same,'moved+92',moved,'other',len(diff))
for x in diff: print(x)
