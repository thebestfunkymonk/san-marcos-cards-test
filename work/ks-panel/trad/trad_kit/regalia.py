"""Regalia: crown base + merlons, jewels, orb, banded sceptre, finial,
simplified Lion Mark. Shapes are shapely polygons (for the Scene); pattern
lines are Frags (FINE Aquifer on gold unless noted)."""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import Point, Polygon

from deck import tokens as T
from deck.motifs import core as MC
from deck.motifs import geometric as MG
from deck.motifs.core import Frag

from inkkit import geom as G

from . import shapes as SH

FINE, MEDIUM = T.FINE, T.MEDIUM


# ---------------------------------------------------------------------------
# crown base (reusable for every crowned court)
# ---------------------------------------------------------------------------
def crown_band(cx: float, y_top: float, y_bot: float, hw_top: float, hw_bot: float, *, sag: float = 0.0):
    """The crown's band: a trapezoid, optionally with both edges sagging
    ``sag`` px at the centre (wrapping the head)."""
    top = np.array([(cx - hw_top, y_top), (cx, y_top + sag), (cx + hw_top, y_top)])
    bot = np.array([(cx + hw_bot, y_bot), (cx, y_bot + sag), (cx - hw_bot, y_bot)])
    if sag:
        ring = np.vstack([SH.spline(top), SH.spline(bot)])
    else:
        ring = np.array([top[0], top[2], bot[0], bot[2]])
    return Polygon(ring)


def merlons(cx: float, base_y: float, spec, gap: float):
    """Symmetric row of rectangular merlons standing on base_y. ``spec`` lists
    (width, height) from the CENTRE outward; the centre merlon straddles cx.
    Returns a list of (polygon, (x0, x1, top)) left-to-right."""
    out = []
    w0, h0 = spec[0]
    items = [(cx - w0 / 2, cx + w0 / 2, base_y - h0)]
    x = w0 / 2
    for w, h in spec[1:]:
        x += gap
        items.append((cx + x, cx + x + w, base_y - h))
        items.append((cx - x - w, cx - x, base_y - h))
        x += w
    items.sort(key=lambda r: r[0])
    for x0, x1, top in items:
        out.append((shapely.box(x0, top, x1, base_y + 2), (x0, x1, top)))
    return out


def stepped_merlons(cx: float, base_y: float, steps, *, tuck: float = 3.0):
    """Abutting limestone blocks rising in fault-steps to a centre peak.
    ``steps`` = [(w, h) centre, (w, h) next, ...]. Each block tucks ``tuck``
    px under its inner neighbour so the Scene draws the joints at the inner
    (MEDIUM) weight. Returned back-to-front (outer blocks first) as
    (polygon, (x0, x1, top, base))."""
    out = []
    w0, h0 = steps[0]
    xs = [(cx - w0 / 2, cx + w0 / 2, base_y - h0)]
    x = w0 / 2
    for w, h in steps[1:]:
        xs.append((cx + x, cx + x + w, base_y - h))
        xs.append((cx - x - w, cx - x, base_y - h))
        x += w
    for x0, x1, top in reversed(xs):
        # tuck under the inner neighbour
        if x1 <= cx + 1e-6 and x0 < cx - w0 / 2 - 1e-6:
            poly = shapely.box(x0, top, x1 + tuck, base_y + 0.5)
        elif x0 >= cx - 1e-6 and x1 > cx + w0 / 2 + 1e-6:
            poly = shapely.box(x0 - tuck, top, x1, base_y + 0.5)
        else:
            poly = shapely.box(x0, top, x1, base_y + 0.5)
        out.append((poly, (x0, x1, top, base_y)))
    return out


def merlon_hatch(box, cx: float, *, part: str = "lower"):
    """Half-hatch one merlon: a FINE bedding line at mid-height and 45° hatch
    in the lower course, mirrored across the axis (a centre block gets a
    FINE joint on the axis, each cell hatched mirror-wise) so the crown
    stays bilaterally symmetric."""
    x0, x1, top, base = box
    ym = (top + base) / 2
    f = MC.stroke(SH.seg((x0, ym), (x1, ym)), FINE, style="rule")
    lo, hi = (ym, base) if part == "lower" else (top, ym)
    mid = (x0 + x1) / 2
    if abs(mid - cx) < 1e-6:
        f += MC.stroke(SH.seg((cx, lo), (cx, hi)), FINE, style="rule")
        f += MC.hatch(shapely.box(x0, lo, cx, hi), -45.0, origin=(cx, lo))
        f += MC.hatch(shapely.box(cx, lo, x1, hi), 45.0, origin=(cx, lo))
    else:
        ang = -45.0 if mid < cx else 45.0
        org = (x1, lo) if mid < cx else (x0, lo)
        f += MC.hatch(shapely.box(x0, lo, x1, hi), ang, origin=org)
    return f


def band_beads(cx, y, hw, jr, *, d=4.2, pitch=11.0, margin=9.0):
    """A row of Ø4.2 Aquifer dots along the band either side of the jewel."""
    f = Frag()
    x = jr + margin
    while x <= hw - margin + 1e-6:
        for s in (-1, 1):
            f += MC.dot(cx + s * x, y, d)
        x += pitch
    return f


# ---------------------------------------------------------------------------
# Source Rosette jewels / finials (reduced recipes of §G.1)
# ---------------------------------------------------------------------------
def rosette_small(cx, cy, R, *, rings=(), ribs=(None, None, 0), bubbles=None, twist=25.0,
                  w=FINE, color=T.INK) -> Frag:
    """A reduced Source Rosette drawn INSIDE a disc of radius R (whose rim is
    the caller's contour). ``rings`` radii; ``ribs`` = (r0, r1, n) pinwheel
    band (alternate cells hatched); ``bubbles`` = (r, n, d)."""
    f = Frag()
    for r in rings:
        f += MC.stroke(MC.circle_d(cx, cy, r), w, color=color)
    if bubbles:
        r, n, d = bubbles
        f += MG.bubble_ring(cx, cy, r, n, d, w=w, color=color)
    r0, r1, n = ribs
    if n:
        f += MG.rib_band(cx, cy, r0, r1, n=n, twist=twist, rules=False, w=w, color=color)
    return f


def jewel(cx, cy, r, *, dot_d=8.4, n=8, twist=30.0):
    """Brow jewel: gold disc r with a pinwheel of n ribs from a hub ring to
    the rim and a Gill Red centre dot (a separate red Item). Returns
    (disc, dot_shape, detail)."""
    disc = Point(cx, cy).buffer(r, quad_segs=48)
    dot = Point(cx, cy).buffer(dot_d / 2, quad_segs=32)
    hub = dot_d / 2 + 1.6 + FINE / 2
    det = MG._ribs(cx, cy, hub, r, n, twist, w=FINE, color=T.INK)
    det += MC.stroke(MC.circle_d(cx, cy, hub), FINE)
    return disc, dot, det


def rosette_finial(cx, cy, R, *, lobes=12, w=FINE):
    """Sceptre finial as a reduced Source Rosette (§G.1) with a lobed rim:
    returns (shape, detail). The silhouette is a disc with ``lobes`` rounded
    scallops (outer radius R); inside, a ripple ring and the vent crater
    (hub ring, 8 ribs twisted clockwise, Ø8.4 centre dot); each lobe carries
    a FINE inner arc (its growth line)."""
    rl = math.pi * (R - 6.5) / lobes * 1.02          # lobe radius
    rc = R - rl                                       # lobe centre radius
    shape = shapely.union_all([Point(cx, cy).buffer(rc, quad_segs=48)] +
                              [Point(*MC.polar(cx, cy, rc, -90 + 360 * (i + 0.5) / lobes)).buffer(rl, quad_segs=16)
                               for i in range(lobes)])
    f = MG.crater(cx, cy, 13.0, n=8, hub=8.6, twist=30.0, dot_d=6.3, w=w)
    f += MC.stroke(MC.circle_d(cx, cy, rc - 3.2), w)
    return shape, f


def vent_finial(cx, cy, R, *, w=FINE):
    """Sceptre finial as a reduced Source Rosette (§G.1): Ø8.4 centre dot,
    a vent crater (hub ring + 8 twisted ribs + rim r 15), and a ring of
    Ø6.3 bubbles; drawn inside a disc of radius R (its contour is the rim)."""
    f = MG.crater(cx, cy, 15.0, n=8, hub=9.5, twist=30.0, dot_d=8.4, w=w)
    rb = (15.0 + w / 2 + 4.2 + 3.15 + (R - 3.125 - 4.2 - 3.15)) / 2
    n = int(2 * math.pi * rb // (6.3 + 4.4))
    for k in range(n):
        p = MC.polar(cx, cy, rb, -90 + 360 * k / n)
        f += MC.dot(p[0], p[1], 6.3)
    return f


def bubble_column(x, y_bottom, y_top, *, d0=5.5, ratio=1.2, gap=4.4, w=MEDIUM):
    """§G.9 bubble beading as a rising column: rings growing ×ratio upward
    from y_bottom until y_top (for knockouts use w ≥ 2.5)."""
    f = Frag()
    y = y_bottom
    d = d0
    while True:
        r = d / 2 + w / 2
        if y - r < y_top:
            break
        f += MC.stroke(MC.circle_d(x, y - r, d / 2), w)
        y = y - 2 * r - gap
        d *= ratio
    return f


# ---------------------------------------------------------------------------
# orb: gold sphere, ripple latitudes, a single bubble for the cross
# ---------------------------------------------------------------------------
def spring_orb(cx, cy, r, *, bubble_d=14.0, tilt=18.0, lats=(58.0, 34.0, 4.0), collar=(15.0, 7.0)):
    """A spring-vent orb. Returns (sphere, bubble, vent_collar, detail).

    Latitudes are ripple rings (§G.8) spreading from the vent at the top
    pole, seen from slightly above (``tilt`` degrees): each is the front
    (lower) half of the projected ellipse. Default polar angles 58/34/4°
    give gaps growing ≈×1.3 down the sphere. One bubble (paper, ringed)
    rises from the vent collar in place of the cross."""
    sphere = Point(cx, cy).buffer(r, quad_segs=64)
    cw, ch = collar
    top = cy - r * math.cos(math.radians(tilt))
    col = SH.smooth_poly(shapely.box(cx - cw / 2, top - ch + 1, cx + cw / 2, top + 4), 2.0)
    by = top - ch + 1 - bubble_d / 2 - 0.5
    bub = Point(cx, by).buffer(bubble_d / 2, quad_segs=32)
    det = Frag()
    st = math.sin(math.radians(tilt))
    ct = math.cos(math.radians(tilt))
    for phi in lats:
        p = math.radians(phi)
        rx = r * math.cos(p)
        ry = rx * st
        yc = cy - r * math.sin(p) * ct
        det += MC.stroke(SH.arc(cx, yc, rx, 0, 180, ry=ry, n=120), FINE)
    return sphere, bub, col, det
# ---------------------------------------------------------------------------
# sceptre: banded shaft (strata / chert vesicas / marl dashes, repeated)
# ---------------------------------------------------------------------------
def banded_shaft(x, y_top, y_bot, w, n=7, *, collar=6.0, collar_w=None):
    """Returns (shaft_shape, collars_shape, detail). ``n`` banded segments
    between y_top and y_bot, separated by collar rings (wider than the
    shaft). Segment k pattern cycles strata -> chert -> marl."""
    collar_w = collar_w or w + 8
    L = y_bot - y_top
    seg_len = (L - (n - 1) * collar) / n
    shaft = shapely.box(x - w / 2, y_top, x + w / 2, y_bot)
    cols = []
    det = Frag()
    y = y_top
    for k in range(n):
        a, b = y, y + seg_len
        det += _segment(x, a, b, w, k % 3)
        y = b
        if k < n - 1:
            if collar_w > w + 0.5:
                cols.append(SH.smooth_poly(shapely.box(x - collar_w / 2, y - 0.5, x + collar_w / 2, y + collar + 0.5), 2.0))
            else:       # flush divider: a double rule across the shaft
                for yy in (y, y + collar):
                    det += MC.stroke(SH.seg((x - w / 2, yy), (x + w / 2, yy)), MEDIUM if yy == y else FINE, style="rule")
            y += collar
    return shaft, shapely.union_all(cols) if cols else Polygon(), det


def _segment(x, a, b, w, kind):
    f = Frag()
    x0, x1 = x - w / 2, x + w / 2
    if kind == 0:        # strata: two courses, one hatched
        m = (a + b) / 2
        f += MC.stroke(SH.seg((x0, m), (x1, m)), FINE, style="rule")
        f += MC.hatch(shapely.box(x0, a, x1, m), MC.DIAG)
    elif kind == 1:      # chert nodules: vesicas along the axis
        n = max(1, int((b - a - 4) // 13))
        ys = np.linspace(a, b, n + 2)[1:-1]
        for y in ys:
            f += MC.stroke(MC.vesica_d((x - w * 0.24, y), (x + w * 0.24, y), 5.6), FINE, style="point")
    else:                # marl: staggered dashes
        n = max(1, int((b - a) // 7.2) - 1)
        ys = np.linspace(a, b, n + 2)[1:-1]
        for i, y in enumerate(ys):
            if i % 2 == 0:
                f += MC.stroke(SH.seg((x - w * 0.22, y), (x + w * 0.22, y)), FINE)
            else:
                f += MC.stroke(SH.seg((x0 + 2.5, y), (x - w * 0.1, y)), FINE) + \
                     MC.stroke(SH.seg((x + w * 0.1, y), (x1 - 2.5, y)), FINE)
    return f


# ---------------------------------------------------------------------------
# simplified Lion Mark (§G.2) — local stand-in until deck.motifs.lion_mark lands
# ---------------------------------------------------------------------------
def lion_mark(cx, cy, size=40.0):
    """The simplified Lion Mark (§G.2) as a gold COIN of diameter ``size``
    (≤ 40 on courts): Aquifer FINE face circle, a 12-scallop mane ring, two
    wing arcs rising from behind the mane and curling in over the head, each
    with 3 primaries, and a ripple line beneath — 20 strokes. (Local stand-in
    until deck.motifs provides lion_mark.) Returns (disc, detail, disc)."""
    R = size / 2
    disc = Point(cx, cy).buffer(R, quad_segs=48)
    k = size / 40.0
    fy = cy - 1.2 * k
    det = Frag()
    det += MC.stroke(MC.circle_d(cx, fy, 3.6 * k), FINE)                  # face
    n, r0, bulge = 12, 7.6 * k, 2.2 * k                                   # mane
    pts = []
    for i in range(n):
        a0 = -90 + 360 * i / n
        a1 = a0 + 360 / n
        p0 = MC.polar(cx, fy, r0, a0)
        p1 = MC.polar(cx, fy, r0, a1)
        pm = MC.polar(cx, fy, r0 + bulge, (a0 + a1) / 2)
        pts.append(SH.spline([p0, pm, p1])[:-1])
    ring = np.vstack(pts + [pts[0][:1]])
    det += MC.stroke(ring, FINE)
    for s in (-1, 1):                                                     # wings
        wing = SH.spline([(cx + s * 9.0 * k, fy + 9.5 * k), (cx + s * 14.6 * k, fy + 1.0 * k),
                          (cx + s * 13.4 * k, fy - 8.5 * k), (cx + s * 6.4 * k, fy - 13.8 * k)])
        det += MC.stroke(wing, FINE)
        cv = G.Curve(wing)
        for t in (0.30, 0.55, 0.80):
            p = cv.at(t)
            nn = cv.normal(t) * (-s)
            det += MC.stroke(SH.seg(p, p - nn * 3.6 * k), FINE)
    rip = SH.spline([(cx - 8 * k, cy + 14.2 * k), (cx - 4 * k, cy + 12.6 * k), (cx, cy + 14.2 * k),
                     (cx + 4 * k, cy + 15.8 * k), (cx + 8 * k, cy + 14.2 * k)])
    det += MC.stroke(rip, FINE)
    return disc, det, disc
