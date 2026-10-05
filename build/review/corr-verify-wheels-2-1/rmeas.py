import sys, json
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/build/review/corr-verify-wheels-2-1')
import numpy as np
from scipy import ndimage
from rtools import render
S = 10
def wheel_bbox(svg, c, kind, keep=None):
    cx, cy = c
    b = (cx - 40, cy - 40, cx + 40, cy + 40)
    if kind == 'back':
        im = np.asarray(render(svg, b, S, drop_stock=True))
        art = im[..., 3] < 128
    else:
        im = np.asarray(render(svg, b, S, keep=keep))
        art = im[..., 3] >= 128
    lab, n = ndimage.label(art)
    sx, sy = int((26) * S), int(40 * S)       # outer ring, left point  (cx-26, cy)
    l = lab[sy, sx] or lab[sy, sx + 3] or lab[sy, sx - 3]
    ys, xs = np.nonzero(lab == l)
    return (b[0] + xs.min() / S, b[1] + ys.min() / S, b[0] + (xs.max() + 1) / S, b[1] + (ys.max() + 1) / S)
def corners(c, W, H, ox=0, oy=0):
    cx, cy = c
    return {'TL': (ox + cx, oy + cy), 'TR': (ox + W - cx, oy + cy), 'BL': (ox + cx, oy + H - cy), 'BR': (ox + W - cx, oy + H - cy)}
def gaps(bb, edges):
    x0, y0, x1, y1 = edges
    return dict(left=round(bb[0] - x0, 2), top=round(bb[1] - y0, 2), right=round(x1 - bb[2], 2), bottom=round(y1 - bb[3], 2))
cases = json.loads(sys.argv[1])
for label, path, kind, keep, c, W, H, ox, oy, edges in cases:
    svg = open(path).read()
    out = []
    for k, cc in corners(c, W, H, ox, oy).items():
        bb = wheel_bbox(svg, cc, kind, keep)
        g = gaps(bb, edges)
        # per corner: side (x) and top/bottom (y) gap to the nearest edges
        side = g['left'] if 'L' in k else g['right']
        tb = g['top'] if 'T' in k else g['bottom']
        out.append(f"{k}: side {side:.2f} / {'top' if 'T' in k else 'bottom'} {tb:.2f}")
    print(label, ' | '.join(out))
