"""Quick §C.2 balance from a rendered card SVG (approximates deck.qa check 5)."""
import subprocess, sys, io
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import tokens as T, frames as F
from inkkit import geom as G
from PIL import ImageDraw

svg = sys.argv[1]
S = 2
png = subprocess.run(["rsvg-convert", "-w", str(750 * S), svg], capture_output=True, check=True).stdout
im = np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(np.int32)
pal = {"paper": T.PAPER, "jade": T.JADE, "red": T.RED, "gold": T.FOIL, "ink": T.INK}
cols = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in pal.values()])
d = ((im[:, :, None, :] - cols[None, None]) ** 2).sum(-1)
lab = d.argmin(-1)
halves = G.difference(F.art_window_d(), G.rect_d(0, F.BAND_Y0, T.W, F.BAND_Y1 - F.BAND_Y0))
shp = G.to_shape(halves, tol=0.2)
mask = Image.new("L", (750 * S, 1050 * S), 0)
dr = ImageDraw.Draw(mask)
for pg in getattr(shp, "geoms", [shp]):
    dr.polygon([(x * S, y * S) for x, y in pg.exterior.coords], fill=255)
    for r in pg.interiors:
        dr.polygon([(x * S, y * S) for x, y in r.coords], fill=0)
m = np.asarray(mask) > 0
n = m.sum()
out = {k: round(float((lab[m] == i).sum()) / n * 100, 1) for i, k in enumerate(pal)}
tgt = {"paper": (45, 50), "jade": (15, 20), "red": (12, 16), "gold": (10, 15), "ink": (8, 19)}
print("  ".join(f"{k} {v}{'' if tgt[k][0] <= v <= tgt[k][1] else '!'}" for k, v in out.items()))
