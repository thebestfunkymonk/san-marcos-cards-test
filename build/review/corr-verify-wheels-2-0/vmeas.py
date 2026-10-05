"""Independent VECTOR measurement (svgelements parser, not inkkit): the corner wheel's
outer inked extent from the output path data.  Card back: the evenodd jade path's
subpath rings; tucks: foil fills (subpath rings) and stroked paths (bbox + w/2)."""
import re, sys, os
import numpy as np
from svgelements import Path, Move, Close

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/luke/Projects/design/san-marcos-deck"


def group(s, gid):
    m = re.search(r'<g id="%s"[^>]*>(.*?)</g>' % gid, s, re.S)
    return m.group(1)


def subpath_bboxes(d):
    p = Path(d)
    out = []
    for sp in p.as_subpaths():
        sp = Path(sp)
        pts = np.array([(q.x, q.y) for q in sp.as_points()] if hasattr(sp, "as_points") else [])
        bb = sp.bbox()
        if bb:
            out.append(bb)
    return out


def items(svg, gid):
    s = open(svg).read()
    body = group(s, gid)
    res = []
    for pm in re.finditer(r'<path\b([^>]*?)/?>', body):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', pm.group(1)))
        w = float(a.get("stroke-width", 0)) if a.get("fill") == "none" else 0.0
        for bb in subpath_bboxes(a["d"]):
            x0, y0, x1, y1 = bb
            res.append((x0 - w / 2, y0 - w / 2, x1 + w / 2, y1 + w / 2, w))
    return res


def wheels(svg, gid, panels):
    """panels: [(name, ox, oy, W, H)] -> per corner, the ~54 square ring's extent."""
    it = items(svg, gid)
    out = {}
    for name, ox, oy, W, H in panels:
        for x0, y0, x1, y1, w in it:
            if 53.5 < x1 - x0 < 55 and 53.5 < y1 - y0 < 55:
                lx0, ly0, lx1, ly1 = x0 - ox, y0 - oy, x1 - ox, y1 - oy
                if not (-1 < lx0 and lx1 < W + 1 and -1 < ly0 and ly1 < H + 1):
                    continue
                cn = ("T" if ly0 < H / 2 else "B") + ("L" if lx0 < W / 2 else "R")
                side = lx0 if cn[1] == "L" else W - lx1
                topb = ly0 if cn[0] == "T" else H - ly1
                out.setdefault((name, cn), []).append((round(lx0, 3), round(ly0, 3), round(lx1, 3), round(ly1, 3),
                                                       round(side, 3), round(topb, 3), w))
    return out


if __name__ == "__main__":
    J = os.path.join
    sets = [
        ("cards/BACK.svg", "jade", [("card-back", 0, 0, 750, 1050)], 37.5),
        ("build/white/cards/BACK.svg", "jade", [("card-back-white", 0, 0, 750, 1050)], 37.5),
        ("tuck/TUCK-FRONT.svg", "foil", [("tuck-front", 0, 0, 769, 1069)], 0),
        ("tuck/TUCK-BACK.svg", "foil", [("tuck-back", 0, 0, 769, 1069)], 0),
        ("tuck/TUCK-FLAT.svg", "foil", [("flat-front", 225, 405, 769, 1069), ("flat-back", 1219, 405, 769, 1069)], 0),
    ]
    for rel, gid, panels, edge in sets:
        p = J(ROOT, rel)
        if not os.path.exists(p):
            continue
        res = wheels(p, gid, panels)
        for (name, cn), v in sorted(res.items()):
            for lx0, ly0, lx1, ly1, side, topb, w in v:
                print(f"{name:16s} {cn}  extent x {lx0:.3f}-{lx1:.3f}  y {ly0:.3f}-{ly1:.3f}  "
                      f"side gap {side - edge:.3f}  top/bot gap {topb - edge:.3f}  (edge {edge}, stroke {w})")
