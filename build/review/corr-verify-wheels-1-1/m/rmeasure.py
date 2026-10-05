"""Raster-measure the four corner wheels on a BACK svg: render the jade layer only at Z x,
flood-fill the knockout component seeded on the wheel's outer ring, report its bbox and
clearances to the flood edges."""
import re, sys, subprocess, numpy as np
from PIL import Image
from scipy import ndimage
svg, out, cx0, cy0 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
Z = 8
s = open(svg).read()
s = re.sub(r'<g id="paper".*?</g>', '', s, flags=re.S)
open(out + '.svg', 'w').write(s)
subprocess.run(['rsvg-convert', '-z', str(Z), '-o', out + '.png', out + '.svg'], check=True)
a = np.asarray(Image.open(out + '.png'))[..., 3].astype(float) / 255
H, W = a.shape
flood = (37.5, 37.5, 712.5, 1012.5)
ko = a < 0.5
# restrict to inside flood rect (straight part)
yy, xx = np.mgrid[0:H, 0:W]
inside = (xx + .5 >= flood[0] * Z) & (xx + .5 <= flood[2] * Z) & (yy + .5 >= flood[1] * Z) & (yy + .5 <= flood[3] * Z)
ko &= inside
lab, n = ndimage.label(ko)
res = []
for sx, sy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
    cx = cx0 if sx == 1 else 750 - cx0
    cy = cy0 if sy == 1 else 1050 - cy0
    # seed: on the ring, 26 px from centre along the axis toward the centre of the card? use left/top side point
    seeds = [(cx - sx * 26, cy), (cx, cy - sy * 26), (cx + sx * 26, cy)]
    labs = set()
    for px, py in seeds:
        l = lab[int(py * Z), int(px * Z)]
        if l: labs.add(l)
    m = np.isin(lab, list(labs))
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min() / Z, (xs.max() + 1) / Z, ys.min() / Z, (ys.max() + 1) / Z
    # weighted centroid
    ccx, ccy = (xs.mean() + .5) / Z, (ys.mean() + .5) / Z
    side = x0 - flood[0] if sx == 1 else flood[2] - x1
    top = y0 - flood[1] if sy == 1 else flood[3] - y1
    res.append((sx, sy, labs, round(x0, 3), round(x1, 3), round(y0, 3), round(y1, 3), round(ccx, 2), round(ccy, 2), round(side, 3), round(top, 3)))
    print(f"corner sx={sx:+d} sy={sy:+d} comps={len(labs)} bbox x {x0:.3f}-{x1:.3f} y {y0:.3f}-{y1:.3f} centroid ({ccx:.2f},{ccy:.2f})  side gap {side:.3f}  top/bot gap {top:.3f}")
