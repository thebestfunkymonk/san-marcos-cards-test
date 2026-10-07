"""K♣ whole-card textiles: the jade barrel robe with buttress staves and the red stole columns.

Everything is point-symmetric about the card centre (375, 525): the barrel outline, the stave scale
S(y) (even about y 525), the two stole columns (each runs from one figure's shoulder to the other's),
the hatch lattice (one direction, one origin) and the atomic bark slits and sprigs (rows are C2
partners of each other), so the 180° copy continues the top half without a visible join.

    barrel        the jade robe: shoulders, then a bowed side with a vertical tangent on the centre line
    S(y)          stave scale, ``barrel half-width / its half-width at y 525``: stole edges, grooves and
                  bark slits all follow it, so they are parallel and widen toward the card centre
    columns       the red stole columns over the shoulders, the piping and the cypress sprigs
    garments      jade (hatched border, FINE seam, fluted staves: plain-edged ridges with paper bark
                  slits, hatched grooves), the red stoles (piping + sprigs) and the sleeve grain
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C
from inkkit import geom as G

P, AX, CY = K.P, K.AX, 525.0
FINE, MEDIUM, CONTOUR = T.FINE, T.MEDIUM, T.CONTOUR
INK, RED, JADE, GOLD = T.INK, T.RED, T.JADE, T.FOIL
GAP, GAP_MARK = K.GAP, K.GAP_MARK

SIDE_X = 148.0                 # robe side at the card centre
BORDER = 34.0                  # hatched jade border inside the outline
X_IN, X_OUT = 13.0, 88.0       # stole column: edges' distance from the axis at y 525
GROOVES = ((104.0, 114.0), (148.0, 158.0))     # hatched grooves, distance from the axis at y 525
RIDGE_FLUTES = (94.0, 125.5, 136.5, 169.5, 181.0)   # FINE flutes inside the plain-edged ridges, at y 525
STRIP_PITCH, STRIP_D = 14.0, 6.3                     # paper dots down the jade strip between the stoles
KNEE_Y = 372.0


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def c2_frag(f: C.Frag) -> C.Frag:
    """``f`` plus its 180° partner (atomic-motif keys of the partner get a suffix)."""
    r = K.rot180(f)
    marks = [replace(m, role=m.role + "~") if "@" in m.role else m for m in r.marks]
    return f + C.Frag(marks, r.meta)


def drop_short(f: C.Frag, min_len: float = 9.0) -> C.Frag:
    """Remove stroke pieces shorter than ``min_len`` (the stubs a hatch leaves in a pocket)."""
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d:
            out.append(m)
            continue
        d = "".join(C.polyline_d(pts, closed=cl) for pts, cl in G.flatten(m.d, 0.05)
                    if G.Curve(np.asarray(pts), closed=cl).length >= min_len)
        if d:
            out.append(replace(m, d=d))
    return C.Frag(out, f.meta)


def seam_guard(f: C.Frag, seam, margin: float = 4.8) -> C.Frag:
    """Drop stroke pieces with an end within ``margin`` of the seam (the half's clip would cut
    them a hair short of their junction and leave a stub the other half has to finish)."""
    if seam is None:
        return f
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d:
            out.append(m)
            continue
        keep = []
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts)
            if not cl and (Point(*pts[0]).distance(seam) < margin or Point(*pts[-1]).distance(seam) < margin):
                continue
            keep.append(C.polyline_d(pts, closed=cl))
        if keep:
            out.append(replace(m, d="".join(keep)))
    return C.Frag(out, f.meta)


# =============================================================================
# the barrel robe and the stave scale
# =============================================================================
def robe_outline(neck_y=262.0, neck_heading=172.0, yoke_r=380.0, yoke_sweep=7.0, run=132.0, corner_r=30.0,
                 side_heading=99.0, bottom=420.0):
    """Left half of the robe outline from the axis at the neck (a turtle walk)."""
    t = C.Turtle(AX, neck_y, neck_heading)
    t.arc(yoke_r, -yoke_sweep)
    t.fd(run)
    t.arc(corner_r, -(neck_heading - yoke_sweep - side_heading))
    y0 = t.pos[1]
    t.fd(max((bottom - y0) / math.sin(math.radians(t.heading)), 0.0))
    return np.asarray(t.pts(0.5)[0])


def _barrel_half():
    pts = robe_outline()
    k = next(i for i, p in enumerate(pts) if p[1] >= 369.0)
    head = pts[:k + 1]
    p0 = head[-1]
    d0 = (head[-1] - head[-2]) / np.hypot(*(head[-1] - head[-2]))
    p3 = np.array([SIDE_X, CY])
    c1, c2 = p0 + d0 * 52.0, p3 - np.array([0.0, 1.0]) * 62.0
    t = np.linspace(0.0, 1.0, 60)[1:, None]
    cub = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p3
    return head, cub


_HEAD, _CUB = _barrel_half()
_EDGE = np.vstack([_HEAD[-1:], _CUB])                    # the side below the corner, y ascending
_EDGE_Y, _EDGE_X = _EDGE[:, 1], _EDGE[:, 0]


def barrel():
    """The whole-card jade robe: shoulders from the neck, a smooth bowed side with a vertical
    tangent on the centre line (no kink at the join)."""
    half = Polygon(np.vstack([_HEAD, _CUB, [[AX, CY]]])).buffer(0)
    top = K.U(half, K.mirror(half, AX))
    return K.U(top, rot(top))


def S(y):
    """Stave scale: the barrel's half-width at ``y`` over its half-width at y 525 (even about 525)."""
    y = np.asarray(y, float)
    u = np.minimum(np.where(y > CY, 2 * CY - y, y), CY)
    x = np.interp(u, _EDGE_Y, _EDGE_X)
    return (AX - x) / (AX - SIDE_X)


def stave(X, y0=232.0, y1=2 * CY - 232.0, side=-1, step=1.0):
    """Centreline of the stave ``X`` px from the axis at y 525 (side -1 = viewer's left)."""
    ys = np.arange(y0, y1 + step, step)
    return np.column_stack([AX + side * X * S(ys), ys])


def band(a, b, y0=232.0, y1=2 * CY - 232.0, side=-1):
    """The strip between staves ``a`` and ``b``."""
    A, B = stave(a, y0, y1, side), stave(b, y0, y1, side)
    return Polygon(np.vstack([A, B[::-1]])).buffer(0)


# =============================================================================
# the red stole columns
# =============================================================================
def _column_half(shoulder=(270.5, 292.0), y_end=2 * CY - 372.0 + 60.0):
    """One stole as it hangs from the left shoulder, running past the card centre; the outer edge
    follows the staves from KNEE_Y on."""
    sh = P(shoulder)
    k = float(S(KNEE_Y))
    xk = AX - X_OUT * k
    ys = np.arange(KNEE_Y, y_end + 1.0, 1.0)
    outer_tail = np.column_stack([AX - X_OUT * S(ys), ys])
    arc = K.Path(P(sh[0] - 30.0, sh[1] - 40.0)).line(sh).arc3(
        P((sh[0] + xk) / 2 + 3.0, (sh[1] + KNEE_Y) / 2), P(xk, KNEE_Y)).d
    head_pts = np.asarray(C.sample_d(arc, 0.5)[0][0])
    inner = np.column_stack([AX - X_IN * S(ys), ys])[::-1]
    top_in = [(AX - X_IN * float(S(KNEE_Y)), sh[1] - 60.0)]
    return Polygon(np.vstack([head_pts, outer_tail[1:], inner, top_in])).buffer(0)


def columns(within):
    """Both stole columns: each is one stole from above, its 180° partner from below."""
    a = _column_half()
    left = K.U(a, rot(K.mirror(a, AX))).intersection(K.R(within))
    left = max(K._polys_of(left), key=lambda g: g.area)
    return left, K.mirror(left, AX)


def sprigs(left_col, blockers, *, seam, rows=(507.0, 471.0, 435.0, 399.0), spray_len=40.0, spray_angle=32.0,
           spray_sag=2.5, tick=9.0, cone_d=7.6, keep_frac=0.8):
    """Cypress sprigs knocked out of the stoles: §G.18 comb sprays tilted tip up and out, each with
    its round cone. Rows are C2 partners (row y above the centre pairs with 1050 - y below), a sprig
    shows whole or not at all."""
    a = math.radians(spray_angle)
    ko_all = C.Frag()
    for y in rows:
        xc = AX - 0.5 * (X_IN + X_OUT) * float(S(y))
        base = P(xc + spray_len * 0.5 * math.sin(a) * 0.9, y)
        tip = base + spray_len * np.array([-math.sin(a), -math.cos(a)])
        sp = spray_ko(base, tip, tick=tick, sag=spray_sag)
        u = (tip - base) / np.hypot(*(tip - base))
        sp += K.dot(tip + u * (cone_d / 2 + 1.0), cone_d, role="cone")
        ink = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in sp.marks])
        if not left_col.buffer(-(MEDIUM / 2 + GAP_MARK + MEDIUM / 2 + 0.2)).contains(ink):
            continue
        if blockers is not None:
            vis = ink.difference(blockers.buffer(MEDIUM / 2 + GAP_MARK))
            if vis.area < keep_frac * ink.area:
                continue
        ko_all += K.atomic(sp, f"sp{int(y)}")
    return ko_all


def pearls(left_col, avoid, *, d=4.2, pitch=12.0, inset=12.0, seam=None, tag=""):
    """A row of paper pearls down the inner edge of the left stole column (``inset`` px off the strip
    edge, on rows that are C2 partners: y = 525 + (j + 1/2) pitch). Returns the left-column marks above the centre (the 180° partner supplies the rest)."""
    out = C.Frag()
    body = left_col.buffer(-(MEDIUM / 2 + GAP_MARK + 0.3))
    n = int((CY - 232.0) // pitch) + 1
    for j in range(-n, 0):
        y = CY + (j + 0.5) * pitch
        c = (AX - (X_IN + inset) * float(S(y)), y)
        dot = Point(*c).buffer(d / 2)
        if not body.contains(dot) or dot.distance(avoid) < 6.0:
            continue
        if seam is not None and any(Point(x, yy).buffer(d / 2).distance(seam) < 3.2
                                    for x, yy in ((c[0], y), (2 * AX - c[0], y), (2 * AX - c[0], 2 * CY - y))):
            continue
        out += K.atomic(K.dot(c, d, role="bubble"), f"pr{tag}{j}")
    return out


def spray_ko(p0, p1, *, tick=9.0, angle=50.0, pitch=None, w=MEDIUM, end_gap=3.0, both=True, sag=0.0,
             start=4.0):
    """One cypress branchlet for knocking out of red (§G.18 comb spray at MEDIUM, so each knockout
    line is ≥ 2.5 px): a rachis from p0 (base) to p1 (tip), straight or bowed by ``sag``, and ticks
    both sides swept ``angle``° toward the tip, their lengths on a vesica envelope; the pitch keeps
    ≥ 3 px of red between neighbouring ticks. → Frag."""
    p0, p1 = P(p0), P(p1)
    d = K.arc_sag(p0, p1, sag) if abs(sag) > 1e-6 else f"M{p0[0]:.3f} {p0[1]:.3f}L{p1[0]:.3f} {p1[1]:.3f}"
    pts = C.sample_d(d, 0.25)[0][0]
    cv = K.G.Curve(pts)
    L = cv.length
    sa = math.sin(math.radians(angle))
    pitch = pitch or (w + GAP_MARK + 0.3) / sa
    f = K.line(d, w, role="rachis")
    s0, s1 = start, L - end_gap
    chord = s1 - s0
    reach = tick * sa
    Rv = ((chord / 2) ** 2 + reach ** 2) / (2 * reach)
    n = int(chord // pitch)
    ss = s0 + (chord - n * pitch) / 2 + np.arange(n + 1) * pitch
    for s in ss:
        xm = s - (s0 + s1) / 2
        hw = math.sqrt(max(Rv * Rv - xm * xm, 0.0)) - (Rv - reach)
        Lt = hw / sa
        if Lt < 3.0:
            continue
        p = cv.at_s(s)
        t = cv.tangent_s(s)
        a = math.atan2(t[1], t[0])
        for sd in ((1, -1) if both else (1,)):
            ang = a - sd * math.radians(angle)
            q = p + Lt * np.array([math.cos(ang), math.sin(ang)])
            f += K.seg(p, q, w, role="tick")
    return f


# =============================================================================
# jade patterns
# =============================================================================
def strip_dots(zone, *, seam, blockers):
    """A column of paper dots down the jade strip between the stoles, on rows that are C2 partners of
    each other (row y pairs with 1050 - y). Returns the dots of the whole strip."""
    out = []
    n = int((CY - 232.0) // STRIP_PITCH)
    for j in range(-n, n + 1):
        y = CY + j * STRIP_PITCH
        dot = Point(AX, y).buffer(STRIP_D / 2, quad_segs=12)
        if not zone.contains(dot):
            continue
        if blockers is not None and dot.distance(blockers) < 6.5:
            continue
        out.append(dot)
    return out


def _tag(f: C.Frag, suffix: str) -> C.Frag:
    return C.Frag([replace(m, role=m.role + suffix) if "@" in m.role else m for m in f.marks], f.meta)


def garments(front, *, near=None, sleeves, cuff_bands, sleeve_grain, sleeve_edges, seam=None):
    """The whole-card robe. ``front``: shapes of the items drawn over it (head, hands, attributes):
    atomic motifs keep clear of them."""
    sleeve_zone = K.c2(sleeves)
    shape = barrel()
    shape = K.U(shape, shape.buffer(12).buffer(-12).intersection(sleeve_zone.buffer(30)))
    left_col, right_col = columns(barrel())
    red = K.U(left_col, right_col).intersection(shape).difference(sleeve_zone)
    jade = shape.difference(red)
    blockers = K.c2(front)

    # ---- jade: hatched border, FINE seam, staves ----------------------------------------------
    inner_shape = barrel().buffer(-BORDER, quad_segs=16)
    border = jade.difference(inner_shape).difference(sleeve_zone)
    seam_line = K.outline(inner_shape, FINE, role="seam")
    seam_line = K.clip_in(seam_line, jade.buffer(-0.2).difference(sleeve_zone.buffer(0.4)))
    border_hatch = drop_short(K.hatch_in(border.buffer(0.25), angle=45.0, origin=(AX, CY)), 26.0)

    stave_zone = jade.intersection(inner_shape).difference(sleeve_zone.buffer(-0.8))
    flutes = C.Frag()
    hatch = C.Frag()
    for (a, b) in GROOVES:
        for side in (-1, 1):
            bd = band(a, b, side=side).intersection(stave_zone.buffer(0.8).intersection(inner_shape))
            if bd.is_empty:
                continue
            hatch += drop_short(K.hatch_in(bd.buffer(0.25), angle=-45.0, origin=(AX, CY)), 9.0)
            for X in (a, b):
                for g in K._lines_of(LineString(stave(X, side=side)).intersection(stave_zone.buffer(0.4))):
                    if g.length > 6.0:
                        flutes += K.line(np.asarray(g.coords), FINE, role="flute")

    for X in RIDGE_FLUTES:
        for side in (-1, 1):
            for g in K._lines_of(LineString(stave(X, side=side)).intersection(stave_zone.buffer(0.4))):
                if g.length > 6.0:
                    flutes += K.line(np.asarray(g.coords), FINE, role="flute")

    # ---- red: piping on the outer edge, sprigs ------------------------------------------------
    piping = C.Frag()
    for col, keepx in ((left_col, K.box(0, 0, AX - 50.0, 2000)), (right_col, K.box(AX + 50.0, 0, 2000, 2000))):
        pz = col.buffer(-5.6, quad_segs=12)
        keep = K.box(0, 312.0, 2000, 2 * CY - 312.0).intersection(keepx)
        for g in K._lines_of(pz.boundary):
            piping += K.clip_in(K.line(np.asarray(g.coords), MEDIUM, role="piping"), keep)
    spr_l = sprigs(left_col, blockers, seam=seam)
    spr = c2_frag(spr_l + _tag(K.mirror(spr_l, AX), "m"))
    spr_shape = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in spr.marks]) if spr.marks else Polygon()
    pr_l = pearls(left_col, K.U(spr_shape, blockers), seam=seam)
    pr_l += pearls(left_col, K.U(spr_shape, blockers), seam=seam, inset=62.0, tag="o")
    if seam is not None:
        # a dot centred on the seam, mid-column: the blend crosses the red without a bare band
        xc = AX - 0.5 * (X_IN + X_OUT) * float(S(CY))
        hit = seam.intersection(LineString([(xc, 0.0), (xc, 2000.0)]))
        if not hit.is_empty:
            pr_l += K.atomic(K.dot((xc, hit.y), 6.0, role="bubble"), "prc")
    pr = c2_frag(pr_l + _tag(K.mirror(pr_l, AX), "m"))
    ko = piping + spr + pr
    ko_shape = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in ko.marks])

    # ---- the jade strip between the stoles: a column of paper dots ---------------------------
    strip = jade.intersection(K.box(AX - 40.0, 0, AX + 40.0, 2000)).intersection(inner_shape).buffer(-(MEDIUM / 2 + 3.5))
    dots = K.U(*strip_dots(strip, seam=seam, blockers=blockers))

    red_fill = K.R(C.knockout(K.D(red), ko))
    jade_fill = jade.difference(dots)
    fills = K.fill(jade_fill, K.JADE) + K.fill(red_fill, K.RED)
    lines = K.outline(shape) + K.outline(red)
    if near is not None:
        # stave lines run under held attributes at a shallow angle: end them clear instead of grazing
        keep_out = K.c2(near).buffer(7.0)
        flutes = K.clip_out(flutes, keep_out, eps=0.0, trap=0.0)
        hatch = K.clip_out(hatch, keep_out, eps=0.0, trap=0.0)
    lines += seam_line + seam_guard(border_hatch + hatch, seam) + flutes
    lines += K.c2(cuff_bands) + K.c2(sleeve_grain) + K.c2(sleeve_edges)
    return K.Part(shape, fills, lines, {"jade": jade, "red": red})
