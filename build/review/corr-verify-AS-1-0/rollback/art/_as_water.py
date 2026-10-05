"""A♠ water and rock (brief §H.13, §G.8, §G.9, §G.10, §G.30): the spring vent
the lion rests its paws on, the conduit rising through the stem, the
plinth's bedding lines, and the gold water outside the spade.

The vertical story, bottom to top: the fault-step plinth (bedding lines, the
lower step half-hatched) -> the conduit rising through the stem with five
bubbles growing Ø3 -> Ø6, the top ones rising free into -> the spring vent
(three elliptical ripple rings spreading from under the paws, the outer the
brief's rx 80 × ry 16 at y 350, with 12 radial ribs) -> the lion.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import Point, box

from deck import frames as F
from deck import tokens as T
from deck.motifs.core import DIAG, Frag, bubble, ellipse_arc_d, hatch, polyline_d, region, stroke

GOLD = T.FOIL
FINE = T.FINE
CX = T.CX
GEO = F.ACE_SPADE_GEOMETRY


def silhouette():
    return region(F.ace_pip_d("S"))


def _span(y):
    """x extent of the silhouette at height y."""
    ln = silhouette().intersection(shapely.geometry.LineString([(0, y), (750, y)]))
    return ln.bounds[0], ln.bounds[2]


# -----------------------------------------------------------------------------
# the spring vent
# -----------------------------------------------------------------------------
VENT = dict(
    # (rx, ry, cy): concentric at (375, 350); the outer ring is the brief's
    # rx 80 x ry 16. Solved so that consecutive rings keep >= 6.4 px centre
    # to centre EVERYWHERE (>= 4.3 px of ground, §I.12 parallel), not just on
    # the axes (ellipses of different eccentricity converge on the flanks);
    # the inner ring is a flat slit, the vent's mouth, its top 4.3 px clear
    # below the paws' soles
    rings=((41.0, 2.6, 350.0), (62.0, 9.6, 350.0), (80.0, 16.0, 350.0)),
    ribs=12, rib_band=(1, 2),
)


def vent(spec=None) -> Frag:
    """The spring vent seen from the front, lying on the water: three full
    elliptical ripple rings (the outer the brief's rx 80 x ry 16 at y 350)
    and 12 straight radial ribs across the outer band, like the vent roundel
    of §G.27 laid in perspective (achiral; none on the axis). The lion rises
    from it: whatever of the far halves lies behind the lion is hidden by the
    caller. meta: ``rim(x)`` -> y of the inner ring's near half; ``zone``
    the vent's filled outline; ``ring(i)`` the filled ellipse of ring i."""
    sp = dict(VENT, **(spec or {}))
    f = Frag()
    for (a, b, cy) in sp["rings"]:
        f += stroke(ellipse_arc_d(CX, cy, a, b, 0.0, 360.0), FINE, color=GOLD, role="ripple")
    i, j = sp["rib_band"]
    (a1, b1, c1), (a2, b2, c2) = sp["rings"][i], sp["rings"][j]
    segs = []
    n = sp["ribs"]
    for k in range(n):
        t = math.radians(360.0 / n * (k + 0.5))
        segs.append(polyline_d([(CX + a1 * math.cos(t), c1 + b1 * math.sin(t)),
                                (CX + a2 * math.cos(t), c2 + b2 * math.sin(t))]))
    f += stroke("".join(segs), FINE, color=GOLD, role="rib")
    a, b, cy = sp["rings"][-1]
    zone = shapely.affinity.scale(Point(CX, cy).buffer(1.0, quad_segs=128), a, b)
    a0, b0, c0 = sp["rings"][0]
    f.meta.update(zone=zone, rim=lambda x: c0 + b0 * math.sqrt(max(0.0, 1 - ((x - CX) / a0) ** 2)),
                  ring=lambda q: shapely.affinity.scale(Point(CX, sp["rings"][q][2]).buffer(1.0, quad_segs=128),
                                                        sp["rings"][q][0], sp["rings"][q][1]))
    return f


# -----------------------------------------------------------------------------
# the conduit in the stem
# -----------------------------------------------------------------------------
def conduit(y_bottom: float = 491.0, rail_top: float | None = None, bubble_top: float = 380.0, *,
            clear: float = 12.0, n: int = 5, d0: float = 3.0, d1: float = 6.0) -> Frag:
    """§H.13 / §G.30 conduit: two FINE rails ``clear`` px apart (clear paper
    between them) rising from the plinth's bedding line to where the stem
    opens into the spade's body; five bubbles growing Ø3 -> Ø6 rise through
    it into the vent, spaced with equal clear gaps. They are solid dots: in
    the 12 px channel a Ø6 dot keeps exactly 3 px to each rail (§I.12),
    where a ring would not."""
    hw = clear / 2 + FINE / 2
    if rail_top is None:            # up to the vent: the rails end ON its outer ripple (a T-junction)
        a, b, cy = VENT["rings"][-1]
        rail_top = cy + b * math.sqrt(1 - (hw / a) ** 2)
    f = stroke(polyline_d([(CX - hw, y_bottom), (CX - hw, rail_top)]) +
               polyline_d([(CX + hw, y_bottom), (CX + hw, rail_top)]), FINE, style="rule", color=GOLD,
               role="rail")
    r = (d1 / d0) ** (1.0 / (n - 1))
    sizes = [d0 * r ** k for k in range(n)]
    y0 = y_bottom - 9.0 - sizes[0] / 2
    gap = (y0 - bubble_top - sum(sizes) + sizes[0] / 2 + sizes[-1] / 2) / (n - 1)
    y = y0
    for k, s_ in enumerate(sizes):
        if k:
            y -= sizes[k - 1] / 2 + gap + s_ / 2
        f += bubble(CX, y, s_, style="dot", color=GOLD)     # solid: a Ø6 dot keeps 3 px to the rails
    f.meta.update(hull=box(CX - hw - FINE / 2, rail_top, CX + hw + FINE / 2, y_bottom), gap=gap)
    return f


# -----------------------------------------------------------------------------
# the plinth: bedding lines, the lower step half-hatched
# -----------------------------------------------------------------------------
def plinth(inset: float = 5.5, style: str = "courses") -> Frag:
    """The fault-step plinth's two steps as gold bedding lines inside the
    silhouette (§H.13). 'courses': each step is a course drawn ``inset`` px
    inside its own outline, the lower course hatched at 45° (FINE, 7.0
    pitch) — one of the two courses, the plinth's half-hatch (§G.10/11); the
    conduit rises from the upper course's bedding line. 'outline': the WIP
    stepped outline + joint line."""
    y0, y1 = GEO["plinth_y"]                      # 483.3 .. 514
    y_mid = 498.6
    ux0, ux1 = _span((y0 + y_mid) / 2)
    lx0, lx1 = _span((y_mid + y1) / 2)
    if style == "outline":
        yt, yb = y0 + inset, y1 - inset
        out = [(lx0 + inset, yb), (lx0 + inset, y_mid), (ux0 + inset, y_mid), (ux0 + inset, yt),
               (ux1 - inset, yt), (ux1 - inset, y_mid), (lx1 - inset, y_mid), (lx1 - inset, yb)]
        f = stroke(polyline_d(out, closed=True), FINE, style="rule", color=GOLD, role="plinth")
        f += stroke(polyline_d([(ux0 + inset, y_mid), (ux1 - inset, y_mid)]), FINE, style="rule", color=GOLD)
        f += hatch(box(lx0 + inset, y_mid, lx1 - inset, yb), DIAG, color=GOLD)
        f.meta.update(top=yt)
        return f
    # courses: upper course = one bedding line; lower course = a hatched band between two
    yu = (y0 + y_mid) / 2                         # 491
    f = stroke(polyline_d([(ux0 + inset + 1.0, yu), (ux1 - inset - 1.0, yu)]), FINE, style="rule", color=GOLD,
               role="bedding")
    ya, yb = y_mid + inset - 1.0, y1 - inset + 1.0
    band = box(lx0 + inset, ya, lx1 - inset, yb)
    f += stroke(polyline_d([(lx0 + inset, ya), (lx1 - inset, ya)]) +
                polyline_d([(lx0 + inset, yb), (lx1 - inset, yb)]), FINE, style="rule", color=GOLD, role="bedding")
    f += stroke(polyline_d([(lx0 + inset, ya), (lx0 + inset, yb)]) +
                polyline_d([(lx1 - inset, ya), (lx1 - inset, yb)]), FINE, style="rule", color=GOLD, role="bedding")
    f += hatch(band, DIAG, color=GOLD)
    f.meta.update(top=yu)
    return f


# -----------------------------------------------------------------------------
# outside the spade
# -----------------------------------------------------------------------------
def waterline(y: float = 350.0, lens=(16.0, 10.0, 6.0), gap: float = 6.0, start: float = 15.0,
              sag: float = 1.4) -> Frag:
    """The broken waterline (§H.13): three short ripple dashes each side at
    y 350, from 15 px to ~55 px beyond the silhouette, shortening outward as
    the surface fades. Each dash is a shallow arc sagging ``sag`` px — the
    same smile as the vent's near-half ripples, so the water surface reads
    straight across the spade."""
    from deck.motifs import forms as FM
    xl, xr = _span(y)
    f = Frag()
    for side, x_edge in ((1, xr), (-1, xl)):
        x = x_edge + side * start
        for L in lens:
            a, b = x + side * FINE / 2, x + side * (L - FINE / 2)
            p, q = (min(a, b), y), (max(a, b), y)
            s_ = sag * (L / lens[0])
            f += stroke(FM.scallop_arc(p, q, -s_), FINE, color=GOLD, role="waterline")
            x += side * (L + gap)
    return f


def bubble_columns(xs=(115.0, 635.0), y0: float = 480.0, y1: float = 260.0, n: int = 9,
                   d0: float = 4.0, d1: float = 12.0) -> Frag:
    """Two columns of 9 bubbles rising y 480 -> 260, growing Ø4 -> Ø12
    (§H.13, §G.9); small ones are dots, big ones rings (a ring keeps a
    >= 3 px hole), spaced with equal clear gaps."""
    r = (d1 / d0) ** (1.0 / (n - 1))
    sizes = [d0 * r ** k for k in range(n)]
    styles = ["dot" if s - FINE < 3.2 else "ring" for s in sizes]
    outer = [s if st == "dot" else s + FINE for s, st in zip(sizes, styles)]
    g = (abs(y0 - y1) - outer[0] / 2 - outer[-1] / 2 - sum(outer[1:-1])) / (n - 1)
    f = Frag()
    for x in xs:
        y = y0
        for k, (s, st, o) in enumerate(zip(sizes, styles, outer)):
            if k:
                y -= outer[k - 1] / 2 + g + o / 2
            f += bubble(x, y, s, style=st, color=GOLD)
    f.meta["gap"] = g
    return f
