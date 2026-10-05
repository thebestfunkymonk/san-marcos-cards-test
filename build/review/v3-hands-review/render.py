"""Scratch: render every specimen cell at 6x singly, plus structural checks."""
import sys, os, json, math, warnings
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
import hand_specimen as HS
from deck import courtkit as K
import shapely
OUT = os.path.join(ROOT, "build/review/v3-hands-review/cells")
os.makedirs(OUT, exist_ok=True)
scale = float(sys.argv[1]) if len(sys.argv) > 1 else 6
rows = HS.rows()
report = []
for ri, (title, calls) in enumerate(rows):
    for ci, c in enumerate(calls):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            hand = getattr(K, c["fn"])(*c["args"], **c["kw"])
        sh = hand.hand.shape
        npoly = len(K._polys_of(sh))
        holes = sum(len(p.interiors) for p in K._polys_of(sh))
        th = hand.thumb
        merged = th.meta.get("merged")
        inner = hand.hand.meta.get("inner")
        nin = len(inner.marks) if inner is not None and hasattr(inner, "marks") else None
        sc, ctr = HS._scene(c)
        svg = HS._svg(sc, ctr, HS.CELL)
        p = os.path.join(OUT, f"{ri:02d}_{ci:02d}.png")
        HS._render(svg, p, HS.CELL * scale)
        report.append(dict(row=ri, cell=ci, label=c.get("label"), polys=npoly, holes=holes, thumb_merged=merged,
                           thumb_empty=(th.shape is None or th.shape.is_empty), inner=nin,
                           wrist_w=round(float(hand.wrist_w), 1), bounds=[round(x,1) for x in sh.bounds]))
for r in report: print(r)
