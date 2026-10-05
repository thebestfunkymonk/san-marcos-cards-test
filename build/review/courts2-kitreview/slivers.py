import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS = None
R = '/home/luke/Projects/design/san-marcos-deck/build/review/courts2-kitreview'
PAL = {'ink': (0x15,0x24,0x2B), 'jade': (0x1D,0x5A,0x55), 'red': (0xAE,0x2F,0x2B), 'gold': (0xB0,0x8D,0x57), 'paper': (0xF4,0xEF,0xE3)}
names = list(PAL); cols = np.array([PAL[k] for k in names], float)
S = 6
def comps(tag, ID):
    im = np.asarray(Image.open(f'{R}/{tag}6/{ID}.png').convert('RGB'), float)
    y0, y1, x0, x1 = 55*S, 511*S, 139*S, 611*S
    im = im[y0:y1, x0:x1]
    d = ((im[:, :, None, :] - cols[None, None]) ** 2).sum(-1)
    lab = d.argmin(-1)
    out = []
    for ci, nm in enumerate(names):
        if nm in ('ink', 'paper'): continue
        m = lab == ci
        L, n = ndi.label(m)
        if n == 0: continue
        dt = ndi.distance_transform_edt(m)
        mx = ndi.maximum(dt, L, index=np.arange(1, n + 1))
        area = ndi.sum(m, L, index=np.arange(1, n + 1))
        sl = ndi.find_objects(L)
        for k in range(n):
            w = 2 * mx[k] / S
            a = area[k] / S / S
            if w < 4.0 and a > 3.0:
                ys, xs = sl[k]
                bb = (xs.start / S + 139, ys.start / S + 55, xs.stop / S + 139, ys.stop / S + 55)
                out.append((nm, round(w, 1), round(a, 1), tuple(round(v, 1) for v in bb)))
    return out
def iou(a, b):
    ax0, ay0, ax1, ay1 = a; bx0, by0, bx1, by1 = b
    ix = max(0, min(ax1, bx1) - max(ax0, bx0)); iy = max(0, min(ay1, by1) - max(ay0, by0))
    I = ix * iy
    U = (ax1-ax0)*(ay1-ay0) + (bx1-bx0)*(by1-by0) - I
    return I / U if U > 0 else 0
for ID in sys.argv[1:]:
    b = comps('b', ID); a = comps('a', ID)
    new = [x for x in a if not any(x[0] == y[0] and iou(x[3], y[3]) > 0.3 for y in b)]
    gone = [y for y in b if not any(x[0] == y[0] and iou(x[3], y[3]) > 0.3 for x in a)]
    print(ID, f'before {len(b)} after {len(a)}')
    for x in new: print('   NEW ', x)
    for x in gone: print('   GONE', x)
