import numpy as np
from PIL import Image
OUT = 'build/review/corr-verify-AS-1-0/'
for name, f, y0 in [('before', 'before_noidx.png', 500), ('after', 'after_noidx.png', 592)]:
    a = np.asarray(Image.open(OUT+f).convert('RGBA')).astype(float)[..., 3]/255
    rows = (a[y0:] > 0.05).any(axis=1)
    runs = []; inrun = False
    for i, v in enumerate(rows):
        y = i + y0
        if v and not inrun: s = y; inrun = True
        if not v and inrun: runs.append((s, y)); inrun = False
    if inrun: runs.append((s, y0+len(rows)))
    print(name, 'ink row runs:', runs)
    for (s, e) in runs:
        cols = np.nonzero((a[s:e] > 0.05).any(axis=0))[0]
        w = a[s:e].sum(axis=0); X = np.arange(a.shape[1]) + 0.5
        print(f'   y {s}-{e}: x {cols.min()}-{cols.max()+1} bbox-mid {(cols.min()+cols.max()+1)/2:.2f} centroid-x {(w*X).sum()/w.sum():.2f}')
    print('   gaps:', [runs[i+1][0]-runs[i][1] for i in range(len(runs)-1)])
