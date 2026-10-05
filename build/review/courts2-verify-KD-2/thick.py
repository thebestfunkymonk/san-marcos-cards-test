import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS = None
def comps(path, s=10, lo=1.9, hi=2.95):
    im = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    y0, y1, x0, x1 = int(55*s), int(511*s), int(139*s), int(611*s)
    im = im[y0:y1, x0:x1]
    dark = im.sum(axis=2) < 200
    dt = ndi.distance_transform_edt(dark) / s
    mx = ndi.maximum_filter(dt, size=5)
    ridge = (dt >= mx - 1e-6) & (dt >= lo) & (dt <= hi)
    lab, n = ndi.label(ndi.binary_dilation(ridge, iterations=int(s*0.8)))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        m = (lab[sl] == i) & ridge[sl]
        cnt = m.sum()
        if cnt < s*1.5: continue
        ys, xs = np.nonzero(m)
        bx0, bx1 = (sl[1].start + xs.min())/s + 139, (sl[1].start + xs.max())/s + 139
        by0, by1 = (sl[0].start + ys.min())/s + 55, (sl[0].start + ys.max())/s + 55
        out.append((round(bx0,1), round(by0,1), round(bx1,1), round(by1,1), round(float(dt[sl][m].max()*2),2), int(cnt)))
    return out
A = comps(sys.argv[2]); B = comps(sys.argv[1])
def ov(a, b, pad=2):
    return not (a[2]+pad < b[0] or b[2]+pad < a[0] or a[3]+pad < b[1] or b[3]+pad < a[1])
print("AFTER thick components (x0,y0,x1,y1,max width,len) not in BEFORE:")
for a in A:
    if not any(ov(a, b) for b in B): print("  NEW", a)
print("AFTER all count", len(A), "BEFORE count", len(B))
for a in A: print("  ", a)
