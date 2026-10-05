import sys
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS=None
im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
s = float(sys.argv[2]); cx, cy = float(sys.argv[3]), float(sys.argv[4]); dx, dy = float(sys.argv[5]), float(sys.argv[6]); L=float(sys.argv[7])
n = np.hypot(dx, dy); dx/=n; dy/=n
runs=[]; cur=None; prev=None
def cls(p):
    r,g,b=p
    if r+g+b<200: return "ink"
    if r>230 and g>225: return "paper"
    return "col"
for t in np.arange(-L, L, 0.05):
    x, y = (cx+dx*t)*s, (cy+dy*t)*s
    c = cls(im[int(y), int(x)])
    if c!=prev:
        if prev is not None: runs.append((prev, round(t-start,2)))
        start=t; prev=c
runs.append((prev, round(L-start,2)))
print(runs)
