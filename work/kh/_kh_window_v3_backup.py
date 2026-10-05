"""art/_kh_window.py — K♥ · the glass-bottom window breastplate (§H.4).

"A gold-framed glass-bottom window (a rectangle ≈ 120 × 90 with rounded
corners) on a jade field, showing ripple rings, two eelgrass ribbons and one
fountain darter in paper line with its stitch line. This is the card-within-
a-card." — and the colour map: "Window: jade (paper line)".

The view is a miniature of the card back (a jade flood with its lines
reversed out to paper): every line inside the frame is a MEDIUM (3.1)
PAPER line, a hole in the jade field (geometry, §5), with ≥ 3 px of jade
between any two (§I.12: knockout lines ≥ 2.5, bridges ≥ 3).

    darter   §G.25 at 94 px, length : depth ≈ 6 : 1, facing left (the
             refs/smtx photo): blunt rounded snout, the eye, the gill-cover
             arc, a rounded spiny first dorsal and a long low second dorsal
             standing on the back line, the rounded caudal fin on a narrow
             peduncle, and the STITCH LINE along the flank (7 on / 4 off,
             butt ends) — the species' signature (§I.23). At MEDIUM the
             nine-spine fan and the saddle bars cannot keep 3 px of jade, so
             the fins are drawn as outlines.
    eelgrass two strap ribbons rising from the lake bed on the right,
             passing behind the fish's tail with a 4.2 px interlace gap.
    ripples  §G.8 a vent boil at the bottom left: three flat concentric
             rings (gaps ×1.3) rising into view through the glass.
    frame    gold, 13 px, MEDIUM outlines and a FINE Aquifer mid-rule (a
             moulded frame).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM
from inkkit import geom as G

P = K.P
MEDIUM, FINE, GAP = K.MEDIUM, K.FINE, K.GAP
KO = MEDIUM                      # paper line width
STITCH_W = 2.6                   # the stitch dashes: knockout holes (≥ 2.5)

# the darter facing LEFT in units of its length (L = 100): snout at x 0, axis y 0
DARTER = dict(
    dorsal=[(0.0, 0.6), (1.8, -4.4), (6.0, -7.4), (13.0, -8.6), (24.0, -8.8), (40.0, -7.8), (56.0, -5.8),
            (69.0, -3.8)],
    ventral=[(0.0, 0.6), (2.4, 4.6), (8.0, 7.1), (20.0, 8.1), (38.0, 7.5), (56.0, 5.4), (69.0, 3.8)],
    tail=dict(top=(96.0, -10.2), bot=(96.0, 10.2), rear=-4.6),
    d1=[(20.0, -8.8), (22.4, -15.8), (29.0, -18.0), (35.2, -16.2), (38.6, -8.0)],
    d2=[(42.0, -7.6), (44.6, -14.6), (52.0, -15.2), (59.0, -12.6), (61.5, -5.2)],
    eye=(9.0, -0.4),
    gill=[(17.2, -8.7), (14.6, -0.2), (17.2, 8.0)],
    stitch=dict(y=0.9, x0=21.0, x1=53.0),
)


def _sp(pts):
    d, dense, _ = FM.arc_spline([P(p) for p in pts])
    return d, np.asarray(dense)


def darter_lines(c, length=94.0, facing=-1):
    """The fountain darter in paper line: → (Frag of ink marks to knock out of
    the jade, the fish's region)."""
    D = DARTER
    k = length / 100.0
    c = np.asarray(c, float)
    L = 98.0

    def T(pts):
        a = (np.asarray(pts, float) - np.array([L / 2, 0.0])) * k
        if facing > 0:
            a = a * np.array([-1.0, 1.0])
        return a + c
    _, top = _sp(D["dorsal"])
    _, bot = _sp(D["ventral"])
    tt, tb = P(D["tail"]["top"]), P(D["tail"]["bot"])
    pt_, pb_ = P(D["dorsal"][-1]), P(D["ventral"][-1])
    # tail: peduncle corners out to the fan tips, the rear edge a convex arc
    tail_top = np.array([pt_, tt])
    rear = C.sample_d(K.arc_sag(tt, tb, D["tail"]["rear"]), 0.3)[0][0]
    tail_bot = np.array([tb, pb_])
    ring = np.vstack([top, tail_top[1:], rear[1:], tail_bot[1:], bot[::-1][1:]])
    body = T(ring)
    f = C.Frag()
    f += K.line(C.polyline_d(body, True), KO, role="darter")
    for key in ("d1", "d2"):
        _, fin = _sp(D[key])
        f += K.line(C.polyline_d(T(fin)), KO, role="fin")
    _, gill = _sp(D["gill"])
    f += K.line(C.polyline_d(T(gill)), KO, role="gill")
    e = T([D["eye"]])[0]
    f += K.dot(e, 4.2, role="eye")
    # the stitch line: 7 on / 4 off, cut as 2.6 px holes (≥ 2.5, §I.12) with butt
    # ends, only where the flank keeps ≥ 3 px of jade either side of a dash
    st = D["stitch"]
    line = T([(st["x0"], st["y"]), (st["x1"], st["y"])])
    stitch = shapely.union_all([LineString(pc).buffer(STITCH_W / 2, cap_style=2)
                                for pc in C.dashes(line, 7.0, 4.0, min_len=6.0)])
    fins = [Polygon(T(_sp(D[key])[1])).buffer(0) for key in ("d1", "d2")]
    region = shapely.union_all([Polygon(body).buffer(0)] + fins).buffer(KO / 2)
    return f, region, stitch


def eelgrass(base, heading, length, hw=3.8, bend=-40.0):
    """One eelgrass ribbon (a strap leaf) rising from ``base`` at ``heading``
    (screen degrees), bending ``bend`` degrees along its length, ``hw``
    half-wide, tapering to a rounded point: its OUTLINE as a paper line (the
    strap's jade inside stays ≥ 3 px wide) and its region."""
    t = C.Turtle(base[0], base[1], heading)
    n = 24
    for _ in range(n):
        t.arc(length / (math.radians(abs(bend)) + 1e-9), bend / n) if abs(bend) > 0.1 else t.fd(length / n)
    mid = np.asarray(t.pts(0.5)[0])
    cv = G.Curve(mid)
    Lc = cv.length
    left, right = [], []
    for s in np.linspace(0, Lc, 120):
        p = cv.at_s(s)
        tg = cv.tangent_s(s)
        nrm = np.array([tg[1], -tg[0]])
        u = s / Lc
        w = hw * (1.0 if u < 0.70 else max(0.0, math.cos((u - 0.70) / 0.30 * math.pi / 2)) ** 0.7)
        left.append(p + nrm * w)
        right.append(p - nrm * w)
    ring = np.vstack([left, right[::-1]])
    reg = Polygon(ring).buffer(0)
    return K.line(C.polyline_d(ring), KO, role="eelgrass"), reg


def window(cx, cy, w=136.0, h=100.0, r=15.0, *, frame=13.0, darter_c=None, darter_len=94.0,
           rip_ry=(4.0, 10.2, 18.0), rip_aspect=0.56, grass_in=12.0, grass_head=12.0, grass_len=40.0,
           grass_bend=38.0):
    """The breastplate: a gold frame ``frame`` px wide (MEDIUM Aquifer
    outlines, a FINE mid-rule) round a jade field whose paper-line view is
    knocked out of it. → courtkit Part (meta: 'inner')."""
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    outer_d = K.rrect(x0, y0, x1, y1, r)
    inner_d = K.rrect(x0 + frame, y0 + frame, x1 - frame, y1 - frame, max(r - frame + 3.0, 4.0))
    mid_d = K.rrect(x0 + frame / 2, y0 + frame / 2, x1 - frame / 2, y1 - frame / 2, max(r - frame / 2 + 1.5, 4.0))
    outer, inner = K.R(outer_d), K.R(inner_d)
    ring = outer.difference(inner)
    fx0, fy0, fx1, fy1 = inner.bounds
    # --- the view ---------------------------------------------------------------------
    dc = P(cx - 1.0, fy0 + 24.0) if darter_c is None else P(darter_c)
    fish, fish_reg, stitch = darter_lines(dc, darter_len, facing=-1)
    keep_out = fish_reg.buffer(GAP + KO / 2)
    # the vent boil below the fish (§G.8: three rings, gaps ×1.3), rising into view
    boil = P(cx, fy1 + 2.0)
    rip = C.Frag()
    for ry in rip_ry:
        rip += K.line(C.ellipse_d(boil[0], boil[1], ry / rip_aspect, ry), KO, role="ripple")
    # two eelgrass ribbons from the lower corners, curving in round the boil
    grass = C.Frag()
    regs = []
    for sg in (-1, 1):
        base = (cx + sg * (w / 2 - frame - grass_in), fy1 + 6.0)
        g_, r_ = eelgrass(base, -90.0 - sg * grass_head, grass_len, hw=3.8, bend=-sg * grass_bend)
        grass += g_
        regs.append(r_)
    grass = K.clip_out(grass, keep_out, eps=0.0, trap=0.0)
    rip = K.clip_out(rip, keep_out, eps=0.0, trap=0.0)
    rip = K.clip_out(rip, K.U(*regs).buffer(GAP + KO / 2), eps=0.0, trap=0.0)
    view = K.clip_in(grass + rip, inner.buffer(-(MEDIUM / 2 + 3.0 + KO / 2)).union(
        K.box(0, fy1 - 30.0, 750, 700).intersection(inner)))
    view = view + fish
    field = K.R(C.knockout(inner_d, view)).difference(stitch)
    fills = K.fill(ring, K.GOLD) + K.fill(field, K.JADE)
    lines = K.outline(outer_d) + K.outline(inner_d) + K.line(mid_d, FINE, role="moulding")
    return K.Part(outer, fills, lines, {"inner": inner, "inner_d": inner_d})
