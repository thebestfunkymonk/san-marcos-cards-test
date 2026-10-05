"""Approximate §C.2 balance from a rendered card PNG: python work/qc/bal.py <png>"""
import sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import frames as F, tokens as T
from deck.motifs import core as C
img = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(float)
H, W, _ = img.shape
s = W / T.W
pts = C.sample_d(F.art_window_d(), 0.5)[0][0]
m = Image.new("L", (W, H), 0)
ImageDraw.Draw(m).polygon([(x * s, y * s) for x, y in pts], fill=1)
mask = np.asarray(m).astype(bool)
mask[int(F.BAND_Y0 * s):int(np.ceil(F.BAND_Y1 * s)), :] = False
pal = {"paper": T.PAPER, "jade": T.JADE, "red": T.RED, "gold": T.FOIL, "ink": T.INK}
cols = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in pal.values()], float)
px = img[mask]
d = ((px[:, None, :] - cols[None, :, :]) ** 2).sum(-1)
k = d.argmin(1)
n = len(px)
out = {name: round(100 * (k == i).sum() / n, 1) for i, name in enumerate(pal)}
print("  ".join(f"{a} {b}" for a, b in out.items()))
