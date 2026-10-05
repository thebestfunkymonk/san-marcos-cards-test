import glob, os, math
import xml.etree.ElementTree as ET
from svgelements import Path as SPath
import numpy as np
from shapely.geometry import Polygon, box
NS = "{http://www.w3.org/2000/svg}"
ROOT = "/home/luke/Projects/design/san-marcos-deck"
def geom(d, n=24):
    p = SPath(d); g = None
    for sp in p.as_subpaths():
        pts = []
        for seg in SPath(sp):
            if type(seg).__name__ == "Move": continue
            for t in np.linspace(0, 1, n, endpoint=False):
                q = seg.point(t); pts.append((q.x, q.y))
        if len(pts) < 3: continue
        pg = Polygon(pts).buffer(0)
        g = pg if g is None else g.symmetric_difference(pg)
    return g
L, C, R = 222, 375, 528
R4 = [198, 416, 634, 852]
EXP = {2: [(C,198),(C,852)], 3: [(C,198),(C,525),(C,852)], 4: [(L,198),(R,198),(L,852),(R,852)]}
EXP[5] = EXP[4] + [(C,525)]
EXP[6] = [(x,y) for y in (198,525,852) for x in (L,R)]
EXP[7] = EXP[6] + [(C,361.5)]
EXP[8] = EXP[7] + [(C,688.5)]
EXP[9] = [(x,y) for y in R4 for x in (L,R)] + [(C,525)]
EXP[10] = [(x,y) for y in R4 for x in (L,R)] + [(C,307),(C,743)]
sizes = {}
bad = 0
for suit in "SHCD":
    for n in range(2, 11):
        root = ET.parse(f"{ROOT}/cards/{n}{suit}.svg").getroot()
        pips = [el for el in root.iter(NS+"path") if "pip" in (el.get("class") or "").split()]
        got = []
        for el in pips:
            g = geom(el.get("d"))
            x0, y0, x1, y1 = g.bounds
            h = y1 - y0
            wt = g.intersection(box(x0-1, y0, x1+1, y0 + 0.03*h)).bounds
            wb = g.intersection(box(x0-1, y1 - 0.03*h, x1+1, y1)).bounds
            wtop = wt[2]-wt[0] if wt else 0; wbot = wb[2]-wb[0] if wb else 0
            if suit in "SC": up = wbot > wtop
            elif suit == "H": up = wtop > wbot
            else: up = None
            got.append(((x0+x1)/2, (y0+y1)/2, up, round(x1-x0,2), round(h,2)))
            sizes[suit] = (round(x1-x0,2), round(h,2))
        exp = sorted(EXP[n], key=lambda p: (p[1], p[0]))
        got_s = sorted(got, key=lambda p: (p[1], p[0]))
        if len(exp) != len(got_s):
            print("COUNT", n, suit, len(got_s)); bad += 1; continue
        for (ex, ey), (gx, gy, up, w, h) in zip(exp, got_s):
            want_up = not (ey > 525)
            if abs(ex-gx) > 0.05 or abs(ey-gy) > 0.05 or (up is not None and up != want_up):
                print("BAD", n, suit, (ex, ey), (round(gx,2), round(gy,2)), "up", up, "want", want_up); bad += 1
        # other elements beyond pips/index/stock?
        for g in root:
            if g.tag != NS+"g": continue
            for el in g:
                c = set((el.get("class") or "").split())
                if not c & {"pip", "index-rank", "index-pip", "stock"}:
                    print("EXTRA", n, suit, el.tag); bad += 1
print("field pip sizes (w,h):", sizes, "problems:", bad)
# clearances brief §E.2
for s,(w,h) in sizes.items():
    print(s, "L-col left edge", round(222-w/2,2), "clear of '10' (x1 128.99):", round(222-w/2-128.99,2),
          "| C pip vs side col horiz gap:", round((375-w/2)-(222+w/2),2),
          "| 10 C307 vs L198 vertical overlap:", round((198+h/2)-(307-h/2),2))
