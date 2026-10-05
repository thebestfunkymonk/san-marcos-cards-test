"""Raster (10x, from rmeas windows): corner end of every rail along its centreline, all 4 corners."""
import sys, numpy as np
from PIL import Image
sys.path.insert(0, '.')
from rmeas import SCALE
def alpha(fn): return np.asarray(Image.open(fn).convert("RGBA"))[:, :, 3] / 255.0
def ends(pref, inst, W, H, xs, ys, knockout):
    out = {}
    for cn in ("TL", "TR", "BL", "BR"):
        a = alpha(f"raster/{pref}-{inst}-{cn}.png")
        ink = (a < 0.5) if knockout else (a > 0.5)
        n = a.shape[0]
        # window origin in panel coords
        wx = 0 if cn[1] == "L" else W - 140
        wy = 0 if cn[0] == "T" else H - 140
        row = []
        for x in xs:
            px = x if cn[1] == "L" else W - x
            ci = int((px - wx) * SCALE)
            col = ink[:, ci] if cn[0] == "T" else ink[::-1, ci]
            # the rail's run that reaches the window's inner end
            j = n - 1
            while j > 0 and col[j]: j -= 1
            # distance from the near edge (panel top/bottom) to where the rail starts
            row.append(round((j + 1) / SCALE if cn[0] == "T" else (j + 1) / SCALE, 2))
        for y in ys:
            py = y if cn[0] == "T" else H - y
            ri = int((py - wy) * SCALE)
            r = ink[ri, :] if cn[1] == "L" else ink[ri, ::-1]
            j = n - 1
            while j > 0 and r[j]: j -= 1
            row.append(round((j + 1) / SCALE, 2))
        out[cn] = row
    return out
if __name__ == "__main__":
    pref = sys.argv[1]
    print("card back: vertical rails x=49.5(outer),57.5(comp),79.5(inner) -> corner end y | horizontal rails y=49.5,57.5,91.5 -> end x (from the near edges)")
    for k, v in ends(pref, "card-back", 750, 1050, (49.5, 57.5, 79.5), (49.5, 57.5, 91.5), True).items(): print("  ", k, v)
    print("tuck front: x=34,42,64 | y=34,42,76")
    for k, v in ends(pref, "tuck-front", 769, 1069, (34, 42, 64), (34, 42, 76), False).items(): print("  ", k, v)
    print("tuck back (card art +9.5): x=59,67,89 | y=59,67,101")
    for k, v in ends(pref, "tuck-back", 769, 1069, (59, 67, 89), (59, 67, 101), False).items(): print("  ", k, v)
    print("flat back panel:")
    for k, v in ends(pref, "flat-back", 769, 1069, (59, 67, 89), (59, 67, 101), False).items(): print("  ", k, v)
    print("flat front panel:")
    for k, v in ends(pref, "flat-front", 769, 1069, (34, 42, 64), (34, 42, 76), False).items(): print("  ", k, v)
