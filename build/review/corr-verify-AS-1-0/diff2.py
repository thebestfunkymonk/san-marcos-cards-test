import numpy as np
from PIL import Image
OUT = 'build/review/corr-verify-AS-1-0/'
def pm(p):
    a = np.asarray(Image.open(p).convert('RGBA')).astype(float)/255
    return np.concatenate([a[..., :3]*a[..., 3:4], a[..., 3:4]], axis=2)
A = pm(OUT+'after_noidx.png'); S = pm(OUT+'before_shift92.png')
d = np.abs(A - S).max(axis=2)
ys, xs = np.nonzero(d > 0.02)
rows = sorted(set(ys.tolist()))
bands = []; s = rows[0]; p = rows[0]
for y in rows[1:]:
    if y > p+3: bands.append((s, p)); s = y
    p = y
bands.append((s, p))
for b in bands:
    m = (ys >= b[0]) & (ys <= b[1])
    print('band y', b, 'x', xs[m].min(), xs[m].max(), 'n', m.sum(), 'maxdiff', d[ys[m], xs[m]].max().round(3))
# non legend region: y < 640
print('max premult diff y<640:', d[:640].max(), 'pixels>0.05:', (d[:640] > 0.05).sum())
