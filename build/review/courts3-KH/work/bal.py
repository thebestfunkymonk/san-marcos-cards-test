"""bal.py [svg]: fast colour balance of the court art window (nearest palette colour, 2x render)."""
import sys, subprocess, io
sys.path.insert(0, '.')
import numpy as np
from PIL import Image, ImageDraw
from deck import frames as F, tokens as T
from inkkit import geom as G
from deck import courtkit as K
svg = sys.argv[1] if len(sys.argv) > 1 else 'cards/KH.svg'
S = 2
png = subprocess.run(['rsvg-convert', '-w', str(750 * S), svg], capture_output=True, check=True).stdout
im = np.asarray(Image.open(io.BytesIO(png)).convert('RGB')).astype(float)
halves = K.R(F.art_window_d()).difference(K.box(0, F.BAND_Y0, T.W, F.BAND_Y1))
mask = Image.new('L', (750 * S, 1050 * S), 0)
dr = ImageDraw.Draw(mask)
for pg in K._polys_of(halves):
    dr.polygon([(x * S, y * S) for x, y in pg.exterior.coords], fill=255)
    for r in pg.interiors:
        dr.polygon([(x * S, y * S) for x, y in r.coords], fill=0)
m = np.asarray(mask) > 127
pal = {'paper': T.PAPER, 'jade': T.JADE, 'red': T.RED, 'gold': T.FOIL, 'ink': T.INK}
cols = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in pal.values()], float)
px = im[m]
d = ((px[:, None, :] - cols[None, :, :]) ** 2).sum(-1)
lab = d.argmin(1)
n = len(lab)
print({k: round(float((lab == i).sum()) / n * 100, 2) for i, k in enumerate(pal)})
