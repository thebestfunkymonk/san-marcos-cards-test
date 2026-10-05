"""Independent spec measurements of cards/*.svg (reviewer scratch)."""
import sys, glob, os, re, math, json
import xml.etree.ElementTree as ET
from svgelements import Path as SPath, Matrix
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

NS = "{http://www.w3.org/2000/svg}"
ROOT = "/home/luke/Projects/design/san-marcos-deck"

def bbox(d, tf=None):
    p = SPath(d)
    if tf: p = p * tf
    return p.bbox()

def els(root, cls, corner=None):
    out = []
    for el in root.iter(NS + "path"):
        c = (el.get("class") or "").split()
        if cls in c and (corner is None or el.get("data-corner") == corner):
            out.append(el)
    return out

def polys(d, n=40):
    """shapely geometry from a filled path (evenodd-ish via symmetric difference of subpaths)"""
    p = SPath(d)
    geoms = []
    for sp in p.as_subpaths():
        sp = SPath(sp)
        pts = []
        for seg in sp:
            if type(seg).__name__ == "Move":
                continue
            for t in np.linspace(0, 1, n, endpoint=False):
                q = seg.point(t)
                pts.append((q.x, q.y))
        if len(pts) >= 3:
            geoms.append(Polygon(pts).buffer(0))
    g = geoms[0]
    for h in geoms[1:]:
        g = g.symmetric_difference(h)
    return g

ranks = ["2","3","4","5","6","7","8","9","10"]
res = {}
# ---- index across all faces
print("== index bboxes (tl) across all faces ==")
rows = {}
for f in sorted(glob.glob(ROOT + "/cards/*.svg")):
    stem = os.path.basename(f)[:-4]
    root = ET.parse(f).getroot()
    r = els(root, "index-rank", "tl"); p = els(root, "index-pip", "tl"); j = els(root, "index-joker", "tl")
    rb = [round(v, 2) for v in bbox(r[0].get("d"))] if r else None
    pb = [round(v, 2) for v in bbox(p[0].get("d"))] if p else None
    jb = [round(v, 2) for v in bbox(j[0].get("d"))] if j else None
    rows[stem] = (rb, pb, jb, [r[0].get("fill") if r else None, p[0].get("fill") if p else None])
    # br must be exact rot180 of tl
    for cls in ("index-rank", "index-pip", "index-joker"):
        tl, br = els(root, cls, "tl"), els(root, cls, "br")
        if tl and br:
            a = bbox(tl[0].get("d")); b = bbox(br[0].get("d"))
            exp = (750 - a[2], 1050 - a[3], 750 - a[0], 1050 - a[1])
            dev = max(abs(x - y) for x, y in zip(b, exp))
            if dev > 0.02:
                print("  BR MISMATCH", stem, cls, dev)
for k, v in rows.items():
    print(f"{k:12} rank {v[0]} pip {v[1]} joker {v[2]} fills {v[3]}")
