import sys, re
sys.path.insert(0, 'build/review/corr-verify-JOKER_BLACK-1-1')
import numpy as np
from PIL import Image
from measure import strip, render
gal = open('build/gallery/svg/JOKER-BLACK.svg').read()
aft = open('cards/JOKER-BLACK.svg').read()
def fig_only(t):
    t = strip(t)
    return t
A = render(fig_only(gal))
B = render(fig_only(aft))
# shift B back by (+8, -73)
Bs = np.zeros_like(B)
Bs[0:1050-73, 8:750] = B[73:1050, 0:742]
ga = A[..., 3]; gb = Bs[..., 3]
# figure region only (drafting frame y < 700)
d = np.abs(A[..., :3]*ga[..., None] - Bs[..., :3]*gb[..., None]).sum(-1) + np.abs(ga-gb)
d[700:] = 0
m = d > 0.3
ys, xs = np.nonzero(m)
print('diff pixels', m.sum())
# cluster by coarse grid
from scipy import ndimage
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=4))
for i in range(1, n+1):
    yy, xx = np.nonzero((lab == i) & m)
    if len(yy) < 3: continue
    print(f'  region x {xx.min()}-{xx.max()} y {yy.min()}-{yy.max()} px {len(yy)}')
img = np.ones((1050, 750, 3))
img[..., :] = 1
img[ga > 0.3] = [0.6, 0.6, 0.6]
img[m] = [1, 0, 0]
Image.fromarray((img*255).astype(np.uint8)).save('build/review/corr-verify-JOKER_BLACK-1-1/regdiff.png')
