import sys
from PIL import Image
import numpy as np
im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
s = float(sys.argv[2]); cx, cy = float(sys.argv[3]), float(sys.argv[4]); dx, dy = float(sys.argv[5]), float(sys.argv[6])
n = np.hypot(dx, dy); dx/=n; dy/=n
runs=[]; cur=None
for t in np.arange(-12, 12, 0.05):
    x, y = (cx+dx*t)*s, (cy+dy*t)*s
    r,g,b = im[int(y), int(x)]
    dark = (r+g+b) < 200
    if dark and cur is None: cur=t
    if not dark and cur is not None: runs.append((round(cur,2), round(t,2), round(t-cur,2))); cur=None
print(runs)
