import numpy as np
from PIL import Image
OUT = 'build/review/corr-verify-AS-1-0/'
A = np.asarray(Image.open(OUT+'after_noidx.png').convert('RGBA')).astype(float)/255
S = np.asarray(Image.open(OUT+'before_shift92.png').convert('RGBA')).astype(float)/255
d = np.abs(A - S).max(axis=2)
for (y0, y1) in [(377, 388), (439, 450), (467, 477), (495, 504), (522, 528), (546, 551), (651, 683)]:
    ys, xs = np.nonzero(d[y0:y1] > 0.02)
    pts = sorted(set(zip((ys+y0).tolist(), xs.tolist())))
    big = [(y, x, round(d[y, x], 2), round(A[y,x,3],2), round(S[y,x,3],2)) for (y, x) in pts if d[y, x] > 0.3]
    print((y0, y1), 'n', len(pts), 'big', big[:12])
