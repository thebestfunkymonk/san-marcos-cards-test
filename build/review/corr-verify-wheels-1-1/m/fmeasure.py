"""Raster-measure corner wheels in the FOIL plate of a tuck svg.
args: svg out ox oy pw ph cx cy   (panel origin, panel size, wheel centre in panel coords)"""
import re, sys, subprocess, numpy as np
from PIL import Image
from scipy import ndimage
svg, out = sys.argv[1], sys.argv[2]
ox, oy, pw, ph, cx0, cy0 = map(float, sys.argv[3:9])
import os; Z = int(os.environ.get("Z", 8)); Image.MAX_IMAGE_PIXELS = None
s = open(svg).read()
vb = re.search(r'viewBox="([^"]+)"', s).group(1).split()
vx, vy = float(vb[0]), float(vb[1])
foil = re.search(r'(<g id="foil".*?</g>)', s, re.S).group(1)
head = s[:s.index('>', s.index('<svg')) + 1]
doc = head + foil + '</svg>'
open(out + '.svg', 'w').write(doc)
subprocess.run(['rsvg-convert', '-z', str(Z), '-o', out + '.png', out + '.svg'], check=True)
a = np.asarray(Image.open(out + '.png'))[..., 3].astype(float) / 255
ink = a >= 0.5
lab, n = ndimage.label(ink)
def P(x, y):  # user -> pixel
    return int((x - vx) * Z), int((y - vy) * Z)
for sx, sy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
    cx = ox + (cx0 if sx == 1 else pw - cx0)
    cy = oy + (cy0 if sy == 1 else ph - cy0)
    labs = set()
    for px, py in [(cx - 26, cy), (cx + 26, cy), (cx, cy - 26), (cx, cy + 26)]:
        X, Y = P(px, py)
        l = lab[Y, X]
        if l: labs.add(l)
    m = np.isin(lab, list(labs))
    ys, xs = np.nonzero(m)
    x0 = xs.min() / Z + vx; x1 = (xs.max() + 1) / Z + vx; y0 = ys.min() / Z + vy; y1 = (ys.max() + 1) / Z + vy
    side = (x0 - ox) if sx == 1 else (ox + pw - x1)
    top = (y0 - oy) if sy == 1 else (oy + ph - y1)
    w, h = x1 - x0, y1 - y0
    print(f"  corner {sx:+d}{sy:+d}: comps {len(labs)} bbox x {x0:.3f}-{x1:.3f} y {y0:.3f}-{y1:.3f} ({w:.2f}x{h:.2f})  to-fold side {side:.3f} top/bot {top:.3f}")
