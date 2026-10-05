"""Independent verifier measurement of the corner wheels from OUTPUT SVGs (vector).

For each file: parse every painted path of the relevant plate into shapely
(fills with their fill rule; strokes buffered by w/2 with their caps), union,
split into connected components, and pick in each corner the component whose
bbox is ~54 px square (the Ø52 FINE wheel).  Report its bbox and the gaps to
the container edges (flood / fold / rules).
"""
import re, sys, json
import numpy as np
import shapely
from shapely.geometry import LineString, LinearRing, Polygon, box, Point
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from inkkit import geom as G

ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')


def paths(svg, group):
    s = open(svg).read()
    m = re.search(r'<g id="%s"[^>]*>(.*?)</g>' % group, s, re.S)
    body = m.group(1)
    out = []
    for pm in re.finditer(r'<path\b([^>]*)/?>', body):
        a = dict(ATTR.findall(pm.group(1)))
        out.append(a)
    return out


def shape_of(a):
    d = a["d"]
    if a.get("stroke") and a.get("fill", "") == "none":
        w = float(a["stroke-width"])
        cap = {"butt": "flat", "round": "round", "square": "square"}[a.get("stroke-linecap", "butt")]
        join = {"miter": "mitre", "round": "round", "bevel": "bevel"}[a.get("stroke-linejoin", "miter")]
        geoms = []
        for pts, closed in G.flatten(d, 0.02):
            pts = np.asarray(pts)
            if len(pts) < 2:
                continue
            if closed:
                ring = LinearRing(pts) if len(pts) >= 3 else LineString(pts)
                geoms.append(ring.buffer(w / 2, join_style=join, mitre_limit=float(a.get("stroke-miterlimit", 4)), quad_segs=16))
            else:
                geoms.append(LineString(pts).buffer(w / 2, cap_style=cap, join_style=join,
                                                    mitre_limit=float(a.get("stroke-miterlimit", 4)), quad_segs=16))
        return shapely.union_all(geoms)
    return G.to_shape(d, fill_rule=a.get("fill-rule", "nonzero"), tol=0.02)


def comps(g):
    return list(getattr(g, "geoms", [g]))


def fmt(b):
    return "(%.2f, %.2f)-(%.2f, %.2f)" % tuple(b)


def wheel_components(geom, W, H, corner=140):
    res = {}
    for name, (cx, cy) in dict(TL=(0, 0), TR=(W, 0), BL=(0, H), BR=(W, H)).items():
        reg = box(min(cx, W - corner * (cx > 0) if cx else 0), 0, 0, 0)
    out = {}
    for c in comps(geom):
        x0, y0, x1, y1 = c.bounds
        w, h = x1 - x0, y1 - y0
        if 50 < w < 60 and 50 < h < 60:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            key = ("T" if my < H / 2 else "B") + ("L" if mx < W / 2 else "R")
            out.setdefault(key, []).append(c)
    return out


def back_card():
    a = [p for p in paths("cards/BACK.svg", "jade")][0]
    jade = shape_of(a)
    # the flood exterior and the paper holes
    polys = comps(jade)
    big = max(polys, key=lambda p: p.area)
    ext = Polygon(big.exterior)
    holes = [Polygon(r) for r in big.interiors]
    fx0, fy0, fx1, fy1 = ext.bounds
    print("card back: flood exterior bounds", fmt(ext.bounds), " holes:", len(holes))
    W, H = 750, 1050
    wheels = {}
    for h in holes:
        x0, y0, x1, y1 = h.bounds
        if 50 < x1 - x0 < 60 and 50 < y1 - y0 < 60:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            key = ("T" if my < H / 2 else "B") + ("L" if mx < W / 2 else "R")
            wheels.setdefault(key, []).append(h)
    rows = []
    for k in ("TL", "TR", "BL", "BR"):
        hs = wheels.get(k, [])
        # the corner one = nearest to the corner
        h = min(hs, key=lambda g: min(g.bounds[0] - fx0, fx1 - g.bounds[2]) + min(g.bounds[1] - fy0, fy1 - g.bounds[3]))
        x0, y0, x1, y1 = h.bounds
        side = x0 - fx0 if k[1] == "L" else fx1 - x1
        tb = y0 - fy0 if k[0] == "T" else fy1 - y1
        # true minimum distances to the straight flood edges (as lines)
        el = LineString([(fx0, 0), (fx0, H)]) if k[1] == "L" else LineString([(fx1, 0), (fx1, H)])
        et = LineString([(0, fy0), (W, fy0)]) if k[0] == "T" else LineString([(0, fy1), (W, fy1)])
        dmin_flood = h.exterior.distance(ext.exterior)
        c = h.centroid
        rows.append(dict(corner=k, bbox=[round(v, 3) for v in h.bounds], centroid=(round(c.x, 3), round(c.y, 3)),
                         side_gap=round(side, 3), tb_gap=round(tb, 3), side_line=round(h.distance(el), 3),
                         tb_line=round(h.distance(et), 3), min_to_flood_outline=round(dmin_flood, 3)))
    for r in rows:
        print(" ", r)
    # the outer RULE pieces near TL: holes with long thin bbox near x/y 49.5
    return rows, holes, ext


def foil_geom(svg):
    ps = paths(svg, "foil")
    return shapely.union_all([shape_of(a) for a in ps])


def tuck_panel(svg, W, H, ox=0.0, oy=0.0, label=""):
    g = foil_geom(svg) if isinstance(svg, str) else svg
    # clip to the panel (flat: the panel window)
    win = box(ox, oy, ox + W, oy + H)
    g = g.intersection(win)
    out = []
    for c in comps(g):
        x0, y0, x1, y1 = c.bounds
        if 50 < x1 - x0 < 60 and 50 < y1 - y0 < 60:
            mx, my = (x0 + x1) / 2 - ox, (y0 + y1) / 2 - oy
            # corner wheels only: within 150 px of both a side and an end fold
            if min(mx, W - mx) < 150 and min(my, H - my) < 150:
                key = ("T" if my < H / 2 else "B") + ("L" if mx < W / 2 else "R")
                side = (x0 - ox) if key[1] == "L" else (ox + W - x1)
                tb = (y0 - oy) if key[0] == "T" else (oy + H - y1)
                cc = c.centroid
                out.append(dict(corner=key, bbox=[round(x0 - ox, 3), round(y0 - oy, 3), round(x1 - ox, 3), round(y1 - oy, 3)],
                                centroid=(round(cc.x - ox, 3), round(cc.y - oy, 3)), side_to_fold=round(side, 3),
                                tb_to_fold=round(tb, 3)))
    out.sort(key=lambda r: r["corner"])
    print(label, "corner-wheel components:", len(out))
    for r in out:
        print(" ", r)
    return out, g


if __name__ == "__main__":
    import os
    os.chdir("/home/luke/Projects/design/san-marcos-deck")
    res = {}
    res["back"] = back_card()[0]
    res["front"] = tuck_panel("tuck/TUCK-FRONT.svg", 769, 1069, label="TUCK-FRONT")[0]
    res["tback"] = tuck_panel("tuck/TUCK-BACK.svg", 769, 1069, label="TUCK-BACK")[0]
    flat = foil_geom("tuck/TUCK-FLAT.svg")
    res["flat_front"] = tuck_panel(flat, 769, 1069, 225, 405, label="FLAT front panel")[0]
    res["flat_back"] = tuck_panel(flat, 769, 1069, 1219, 405, label="FLAT back panel")[0]
    json.dump(res, open("build/review/corr-verify-wheels-1-0/vmeasure.json", "w"), indent=1)
