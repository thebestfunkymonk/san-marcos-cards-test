"""art/_kh_window.py — K♥ · the glass-bottom window breastplate (§H.4).

"A gold-framed glass-bottom window (a rectangle ≈ 120 × 90 with rounded
corners) on a jade field, showing ripple rings, two eelgrass ribbons and one
fountain darter in paper line with its stitch line. This is the card-within-
a-card." — and the colour map: "Window: jade (paper line)".

The view is a miniature of the card back (a jade flood with its lines
reversed out to paper): every line inside the frame is a MEDIUM (3.1)
PAPER line, a hole in the jade field (geometry, §5), with ≥ 3 px of jade
between any two (§I.12: knockout lines ≥ 2.5, bridges ≥ 3).

    darter   §G.25 at 100 px, length : depth ≈ 6 : 1, facing left (the
             refs/smtx photo): blunt rounded snout, a large eye set high
             (a paper disc), the gill-cover arc, a FANNED spiny first
             dorsal (scalloped membrane between three spines) and a lower
             soft second dorsal standing on the back line, the fan-shaped
             caudal fin on a narrow peduncle with one centre ray, and the
             STITCH LINE along the flank (7 on / 4 off, butt ends) — the
             species' signature (§I.23). The eight saddle bars cannot keep
             3 px of jade at this size and are left out.
    eelgrass two strap blades rising from the lake bed at the lower left and
             bending right in the current (the fish swims against it) —
             solid paper, or (``grass_solid=False``, K♥) paper-outlined
             ribbons like the fish, tapering to a point, clear of the fish.
    ripples  §G.8 a vent boil on the lake bed: three flat concentric rings
             (≥ 3.3 px of jade between them, or heal refills the holes) —
             rising into view at the bottom edge, or (K♥) whole, above it.
    ``spines=False`` leaves the dorsal fins as scalloped outlines: at 100 px
             the spines cut the fins' jade into slivers heal drops.
    frame    gold, 14 px, MEDIUM outlines and ten Ø4.2 Aquifer rivets on its
             centreline (a glass-bottom boat's window).
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
    dorsal=[(0.0, 1.0), (2.0, -4.0), (7.5, -7.8), (16.0, -9.4), (30.0, -9.4), (46.0, -8.0), (62.0, -5.6),
            (73.0, -4.0)],
    ventral=[(0.0, 1.0), (2.8, 5.6), (11.0, 8.6), (28.0, 8.8), (46.0, 7.3), (62.0, 5.0), (73.0, 4.0)],
    tail=dict(top=(95.0, -10.6), bot=(95.0, 10.6), rear=-3.4, ray=(79.0, 98.4)),
    # first dorsal: the base on the back, the spine tips (front → rear), membrane sag between tips
    d1=dict(base=(19.5, 42.0), tips=[(25.0, -19.2), (32.0, -20.0), (39.2, -17.0)], rear=(43.5, -9.2),
            sag=1.0),
    d2=dict(base=(47.0, 67.5), tips=[(52.0, -15.4), (59.0, -14.6), (65.4, -11.4)], rear=(68.5, -5.0),
            sag=0.9),
    eye=(8.8, 0.2),
    eye_d=5.0,
    gill=[(19.0, -8.9), (16.6, -0.2), (18.8, 8.3)],
    stitch=dict(y=-0.4, x0=23.0, x1=56.0),
)


def _sp(pts, h0=None, h1=None):
    d, dense, _ = FM.arc_spline([P(p) for p in pts], h0, h1)
    return d, np.asarray(dense)


def _fin(base, tips, rear, sag, back_y):
    """A fin standing on the back line: the front edge from the base up to the
    first tip, a scalloped membrane (arcs sagging ``sag`` between the tips),
    the rear edge down to the back, plus straight spines from the base to each
    inner tip. → (outline polyline, list of spine polylines), in fish units."""
    x0, x1 = base
    tips = [P(t) for t in tips]
    ring = [P(x0, back_y(x0))]
    ring += [tips[0]]
    for a, b in zip(tips[:-1], tips[1:]):
        seg = C.sample_d(K.arc_sag(a, b, -sag), 0.2)[0][0]
        ring += list(seg[1:])
    rear = P(rear)
    ring += list(C.sample_d(K.arc_sag(tips[-1], rear, -sag * 1.6), 0.2)[0][0][1:])
    outline = np.asarray(ring)
    spines = []
    n = len(tips)
    for k in range(1, n):
        xb = x0 + (x1 - x0) * k / n
        spines.append(np.asarray([P(xb, back_y(xb)), tips[k]]))
    return outline, spines


def darter_lines(c, length=100.0, facing=-1, spines=True):
    """The fountain darter in paper line: → (Frag of ink marks to knock out of
    the jade, the fish's region, the stitch holes region)."""
    D = DARTER
    k = length / 100.0
    c = np.asarray(c, float)
    Lc = 97.0                      # the fish's extent (snout 0 → tail tip 95)

    def T(pts):
        a = (np.asarray(pts, float) - np.array([Lc / 2, 0.0])) * k
        if facing > 0:
            a = a * np.array([-1.0, 1.0])
        return a + c
    _, top = _sp(D["dorsal"], -80.0, None)
    _, bot = _sp(D["ventral"], 80.0, None)
    top_ls = LineString(top)

    def back_y(x):
        g = top_ls.intersection(LineString([(x, -50.0), (x, 50.0)]))
        return float(min(p.y for p in (g.geoms if hasattr(g, "geoms") else [g])))
    tt, tb = P(D["tail"]["top"]), P(D["tail"]["bot"])
    pt_, pb_ = P(D["dorsal"][-1]), P(D["ventral"][-1])
    rear = C.sample_d(K.arc_sag(tt, tb, D["tail"]["rear"]), 0.3)[0][0]
    ring = np.vstack([top, [tt], rear[1:], [pb_], bot[::-1][1:]])
    body = T(ring)
    f = C.Frag()
    f += K.line(C.polyline_d(body, True), KO, role="darter")
    fins = []
    for key in ("d1", "d2"):
        fd = D[key]
        ol, spines_ = _fin(fd["base"], fd["tips"], fd["rear"], fd["sag"], back_y)
        f += K.line(C.polyline_d(T(ol)), KO, role="fin")
        for sp in (spines_ if spines else []):
            f += K.line(C.polyline_d(T(sp)), KO, role="spine")
        fins.append(Polygon(T(np.vstack([ol, [ol[0]]]))).buffer(0))
    # the caudal's centre ray, from the peduncle to the rear edge
    r0, _ = D["tail"]["ray"]
    rx = float(rear[np.argmin(np.abs(rear[:, 1])), 0])
    f += K.line(C.polyline_d(T([(r0, 0.0), (rx, 0.0)])), KO, role="ray")
    _, gill = _sp(D["gill"])
    f += K.line(C.polyline_d(T(gill)), KO, role="gill")
    e = T([D["eye"]])[0]
    f += K.dot(e, D["eye_d"], role="eye")
    # the stitch line: 7 on / 4 off, cut as 2.6 px holes (≥ 2.5, §I.12) with butt ends
    st = D["stitch"]
    line = T([(st["x0"], st["y"]), (st["x1"], st["y"])])
    stitch = shapely.union_all([LineString(pc).buffer(STITCH_W / 2, cap_style=2)
                                for pc in C.dashes(line, 7.0, 4.0, min_len=6.0)])
    region = shapely.union_all([Polygon(body).buffer(0)] + fins).buffer(KO / 2)
    return f, region, stitch


def eelgrass(base, heading, length, hw=3.8, bend=-40.0, wave=0.0, solid=False):
    """One eelgrass ribbon (a strap leaf) rising from ``base`` at ``heading``
    (screen degrees), bending ``bend`` degrees along its length (``wave``:
    an S — the first half bends ``wave`` the other way), ``hw`` half-wide,
    tapering to a rounded point: its OUTLINE as a paper line (the strap's
    jade inside stays ≥ 3 px wide) and its region."""
    t = C.Turtle(base[0], base[1], heading)
    n = 24
    for i in range(n):
        b = bend / n + (wave * (-2.0 if i < n // 2 else 2.0) / n if wave else 0.0)
        if abs(b) > 1e-6:
            t.arc(length / n / math.radians(abs(b)), b)
        else:
            t.fd(length / n)
    mid = np.asarray(t.pts(0.5)[0])
    cv = G.Curve(mid)
    Lc = cv.length
    left, right = [], []
    for s in np.linspace(0, Lc, 140):
        p = cv.at_s(s)
        tg = cv.tangent_s(s)
        nrm = np.array([tg[1], -tg[0]])
        u = s / Lc
        w = hw * (1.0 if u < 0.72 else max(0.0, math.cos((u - 0.72) / 0.28 * math.pi / 2)) ** 0.7)
        left.append(p + nrm * w)
        right.append(p - nrm * w)
    ring = np.vstack([left, right[::-1]])
    reg = Polygon(ring).buffer(0)
    if solid:
        # a solid paper blade (a hole in the jade): the region itself
        return K.fill(K.D(reg), K.INK, role="eelgrass"), reg
    return K.line(C.polyline_d(ring), KO, role="eelgrass"), reg


def window(cx, cy, w=142.0, h=104.0, r=16.0, *, frame=14.0, darter_c=None, darter_len=100.0, rivets=True,
           rivet_dx=(26.0,),
           rip_ry=(3.2, 9.4, 17.4), rip_aspect=0.52, rip_c=(28.0, 4.0), grass=None, grass_hw=3.0,
           grass_solid=True, fish_dy=26.0, fish_dx=1.0, spines=True):
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
    dc = P(cx + fish_dx, fy0 + fish_dy) if darter_c is None else P(darter_c)
    fish, fish_reg, stitch = darter_lines(dc, darter_len, facing=-1, spines=spines)
    keep_out = fish_reg.buffer(GAP + KO / 2)
    # the vent boil on the lake bed (§G.8: three rings, gaps ×1.3), rising into view
    boil = P(cx + rip_c[0], fy1 + rip_c[1])
    rip = C.Frag()
    for ry in rip_ry:
        rip += K.line(C.ellipse_d(boil[0], boil[1], ry / rip_aspect, ry), KO, role="ripple")
    # two eelgrass ribbons rising from the bed, swaying, behind the fish
    grass = grass or [(-44.0, -70.0, 54.0, 50.0, 14.0), (-26.0, -76.0, 44.0, 44.0, 12.0)]
    gl = C.Frag()
    regs = []
    for dx, head, length, bend, wave in grass:
        g_, r_ = eelgrass((cx + dx, fy1 + 8.0), head, length, hw=grass_hw, bend=bend, wave=wave, solid=grass_solid)
        gl += g_
        regs.append(r_)
    gl = K.clip_out(gl, keep_out, eps=0.0, trap=0.0)
    rip = K.clip_out(rip, keep_out, eps=0.0, trap=0.0)
    rip = K.clip_out(rip, K.U(*regs).buffer(GAP + KO / 2), eps=0.0, trap=0.0)
    view = K.clip_in(gl + rip, inner.buffer(-(MEDIUM / 2 + 3.0 + KO / 2)).union(
        K.box(0, fy1 - 30.0, 750, 700).intersection(inner)))
    view = view + fish
    field = K.R(C.knockout(inner_d, view)).difference(stitch)
    fills = K.fill(ring, K.GOLD) + K.fill(field, K.JADE)
    lines = K.outline(outer_d) + K.outline(inner_d)
    if rivets:
        # brass rivets on the frame's centreline: the four corners (45° on the
        # corner arcs), the long sides at ±``rivet_dx``, the short sides' middles
        rm = max(r - frame / 2, 1.0)
        m = frame / 2
        k45 = rm * (1 - math.sqrt(0.5))
        pts = [(x0 + m + k45, y0 + m + k45), (x1 - m - k45, y0 + m + k45),
               (x0 + m + k45, y1 - m - k45), (x1 - m - k45, y1 - m - k45)]
        for dx in rivet_dx:
            pts += [(cx - dx, y0 + m), (cx + dx, y0 + m), (cx - dx, y1 - m), (cx + dx, y1 - m)]
        pts += [(x0 + m, cy), (x1 - m, cy)]
        for q in pts:
            lines += K.dot(q, 4.2, role="rivet")
    else:
        lines += K.line(mid_d, FINE, role="moulding")
    return K.Part(outer, fills, lines, {"inner": inner, "inner_d": inner_d})
