import re, subprocess, sys, io
import numpy as np
from PIL import Image
S=4
def layer_only(svg, keep):
    out=svg
    for lid in ['paper','jade','red','gold','ink']:
        if lid not in keep:
            out=out.replace(f'<g id="{lid}"', f'<g id="{lid}" display="none"',1)
    return out
for cid,suitlayer in [('AS','ink'),('AH','red'),('AC','ink'),('AD','red')]:
    svg=open(f'cards/{cid}.svg').read()
    for keep in [[suitlayer],['gold'],[suitlayer,'gold']]:
        s=layer_only(svg,keep)
        png=subprocess.run(['resvg','-z',str(S),'-','-c'],input=s.encode(),capture_output=True).stdout
        a=np.array(Image.open(io.BytesIO(png)).convert('RGBA'))[...,3].astype(float)/255
        # central region excluding indices
        a[:, :int(150*S)]=0; a[:, int(600*S):]=0
        a[:int(150*S),:]=0; a[int(900*S):,:]=0
        ys,xs=np.nonzero(a>0.5)
        x0,x1,y0,y1=xs.min()/S,(xs.max()+1)/S,ys.min()/S,(ys.max()+1)/S
        w=a.sum(); cy=(a.sum(1)*np.arange(a.shape[0])).sum()/w/S; cx=(a.sum(0)*np.arange(a.shape[1])).sum()/w/S
        print(cid,'+'.join(keep),f'bbox x {x0:.2f}-{x1:.2f} y {y0:.2f}-{y1:.2f} centre ({(x0+x1)/2:.2f},{(y0+y1)/2:.2f})  mass-centroid ({cx:.1f},{cy:.1f})')
