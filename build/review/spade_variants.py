"""Review scratch: compare the brief's squashed spade with taller variants (circles + lines only)."""
import math, subprocess, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import shapely
from shapely.geometry import Point, Polygon, box
from shapely import affinity
from deck import pips as P
from deck import tokens as T
from inkkit import geom as G

def spade(body_h, lobe_r=0.26, lobe_dx=0.24, stem_bot=None, fillet=0.035):
    # heart construction flipped: apex at y=0, lobe centres at y = body_h - lobe_r
    cy = body_h - lobe_r
    lobes = Point(-lobe_dx, cy).buffer(lobe_r, 256).union(Point(lobe_dx, cy).buffer(lobe_r, 256))
    hull = lobes.union(Point(0, 0).buffer(1e-6)).convex_hull
    below = box(-1, cy, 1, 2).difference(lobes)
    body = hull.difference(below)
    # stem: same taper as brief (0.07 -> 0.20), from the cleft to stem_bot, then plinth 2 x 0.05
    y_top = body_h - 0.18
    sb = stem_bot
    def hw(y): return 0.035 + 0.065 * (y - y_top) / (sb - y_top)
    stem = Polygon([(-hw(y_top - 0.1), y_top - 0.1), (hw(y_top - 0.1), y_top - 0.1), (0.10, sb), (-0.10, sb)])
    pl = box(-0.13, sb, 0.13, sb + 0.05).union(box(-0.18, sb + 0.05, 0.18, sb + 0.10))
    s = body.union(stem).union(pl)
    if fillet:
        R = fillet
        closed = s.buffer(R, 64).buffer(-R, 64)
        s = s.union(closed.difference(s).intersection(box(-1, body_h - 0.3, 1, sb - 0.02)))
    return s

def apex_angle(body_h, r=0.26, dx=0.24):
    d = math.hypot(dx, body_h - r)
    return 2 * math.degrees(math.atan(dx / (body_h - r)) + math.asin(r / d))

variants = [
    ("brief §E.1 (squashed, 1.00 x 1.10)", None),
    ("V1 unsquashed heart body 0.92, 1.00 x 1.22", spade(0.92, stem_bot=1.12)),
    ("V2 body 1.00, 1.00 x 1.28", spade(1.00, stem_bot=1.18)),
]
W = 116  # field u
parts = []
x = 20
H = 190
for label, s in variants:
    if s is None:
        d = P.pip_top_d("S", W, x + W / 2 + 10, 20)
    else:
        s2 = affinity.scale(s, W, W, origin=(0, 0))
        s2 = affinity.translate(s2, x + W / 2 + 10, 20)
        d = G.from_shape(s2)
    parts.append(f'<path d="{d}" fill="{T.INK}"/>')
    x += W + 60
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{x}" height="{H}" viewBox="0 0 {x} {H}">'
       f'<rect width="{x}" height="{H}" fill="{T.PAPER}"/>' + "".join(parts) + "</svg>")
open("/home/luke/Projects/design/san-marcos-deck/build/review/spade_variants.svg", "w").write(svg)
subprocess.run(["rsvg-convert", "-z", "2", "/home/luke/Projects/design/san-marcos-deck/build/review/spade_variants.svg",
                "-o", "/home/luke/Projects/design/san-marcos-deck/build/review/spade_variants.png"], check=True)
print("apex angles: brief squashed", round(2*math.degrees(math.atan(math.tan(math.radians(apex_angle(0.92)/2))/(0.80/0.92))),1),
      "V1", round(apex_angle(0.92),1), "V2", round(apex_angle(1.00),1))
