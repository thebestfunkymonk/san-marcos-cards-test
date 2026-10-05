"""art/_qd_hair.py — Q♦'s hair and bare skin: the chignon, the neck with its
shoulders' spring, and the pearl choker. Built on deck.courtkit (current
lines, arcs); art/QD.py stacks them."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from inkkit import geom as G
from deck.motifs import core as C
from deck.motifs import geometric as MG

P, R, U, D = K.P, K.R, K.U, K.D
FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR
GOLD, INK = K.GOLD, K.INK


def bun(c, r=21.0, *, n=2, a0=-60.0, sweep=290.0, color=GOLD) -> K.Part:
    """A low chignon at the back of a 3/4 head: a gold disc whose current
    lines (§G.24) coil inward from its rim, each rolling into a Ø6.3
    terminal — a wound knot of hair."""
    c = P(c)
    disc = R(K.circle(c, r))
    th = np.radians(np.linspace(a0, a0 + sweep, 400))
    guide = np.column_stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)])
    lines = K.current_lines(guide, n, disc, side=-1, edge=CONTOUR, stagger=22.0, curl_r=4.2, curl_deg=80.0)
    return K.Part(disc, K.fill(disc, color), lines + K.outline(disc), {"c": c, "r": r})


def neck_chest(axis=385.0, *, top=240.0, hw=15.5, base_y=282.0, shoulder=(348.0, 426.0), spring_y=298.0,
               bottom=380.0) -> K.Part:
    """Bare skin: the neck column (a slender taper under the jaw) springing
    at its base into the shoulders — each side a tangent arc out to the
    cape's inner edge — and the chest down under the gown's neckline. Paper
    is never painted: the Part only hides what is behind it and draws the
    neck's two MEDIUM side lines."""
    xl, xr = axis - hw, axis + hw
    sl, sr = shoulder
    left = K.Path((xl + 1.0, top)).line((xl, base_y)).arc3((xl - 6.0, base_y + 10.5), (sl, spring_y))
    left_d = left.d
    right = K.Path((xr - 1.0, top)).line((xr, base_y)).arc3((xr + 6.0, base_y + 10.5), (sr, spring_y))
    right_d = right.d
    lp = C.sample_d(left_d, 0.5)[0][0]
    rp = C.sample_d(right_d, 0.5)[0][0]
    reg = Polygon(np.vstack([lp, [[sl - 4.0, spring_y + 2.0], [sl - 4.0, bottom], [sr + 4.0, bottom],
                                  [sr + 4.0, spring_y + 2.0]], rp[::-1]])).buffer(0)
    lines = K.line(left_d, MEDIUM, role="neck") + K.line(right_d, MEDIUM, role="neck")
    return K.Part(reg, C.Frag(), lines, {})


def pearls(p0, pm, p1, *, d_min=4.2, d_max=6.3, gap=3.2, color=GOLD) -> C.Frag:
    """A graduated pearl strand (§G.29) along the arc p0 → pm → p1: gold beads,
    the largest at the centre, 3 px apart."""
    d = K.arc3(p0, pm, p1)
    return MG.pearl_beading(d, d_min=d_min, d_max=d_max, gap=gap, style="dot", color=color)


def _ribbon(spine, w0, w1, *, cap=True):
    """A lock of hair along ``spine`` (points, root → end): its width tapers
    w0 → w1; the end is rolled (a semicircle). → (region, left edge pts,
    right edge pts) — left/right = screen-left/right of travel."""
    cv = G.Curve(np.asarray(spine, float))
    pts = cv.resample(0.5)
    n = len(pts)
    t = np.linspace(0, 1, n)
    tang = np.gradient(pts, axis=0)
    tang /= np.hypot(tang[:, 0], tang[:, 1])[:, None]
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])          # screen-left of travel
    hw = (w0 + (w1 - w0) * t)[:, None] / 2
    left, right = pts + nrm * hw, pts - nrm * hw
    ring = [left]
    if cap:
        c, r = pts[-1], float(hw[-1, 0])
        a0 = math.degrees(math.atan2(nrm[-1][1], nrm[-1][0]))
        th = np.radians(np.linspace(a0, a0 - 180.0, 40))       # round the end (through the forward direction)
        arc = np.column_stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)])
        if np.dot(arc[20] - c, tang[-1]) < 0:
            th = np.radians(np.linspace(a0, a0 + 180.0, 40))
            arc = np.column_stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)])
        ring.append(arc)
    ring.append(right[::-1])
    reg = Polygon(np.vstack(ring)).buffer(0)
    return reg, left, right


def queen_hair(fc, *, crown=(374.0, 204.0), r_near=55.0, r_far=49.0, part=(374.0, 160.0), far_outer=None,
               near_low=(334.0, 250.0), hairline_near=((372.0, 175.0), (348.0, 186.0), (338.0, 206.0),
                                                       (340.0, 232.0), (352.0, 250.0)),
               far_low=(426.0, 236.0), hairline_far=((372.0, 175.0), (400.0, 176.0), (418.0, 196.0),
                                                     (423.0, 220.0), (421.0, 236.0)),
               fall=((344.0, 236.0), (336.0, 266.0), (322.0, 298.0), (314.0, 330.0)), fall_w=(34.0, 26.0),
               n_cap=3, n_fall=3, color=GOLD):
    """Q♦'s hair: swept from a side parting over both temples (covering the
    near ear), the back gathered into one long lock that falls over the near
    shoulder — gold, in §G.24 current lines. → (cap Part, fall Part): add
    the FALL behind the head (in front of the cape), the CAP in front of the
    head."""
    cx, cy = crown
    oc = P(cx, cy)
    # ---- cap: outer contour = two circles (near side fuller), hairline splines
    def arc_pts(r, a0, a1, cw):
        a1 = K.unwrap(a0, a1, cw)
        th = np.radians(np.linspace(a0, a1, 200))
        return np.column_stack([cx + r * np.cos(th), cy + r * np.sin(th)])
    a_top = -90.0
    near_o = arc_pts(r_near, a_top, K.ang(oc, near_low), cw=False)      # top → back-left, anticlockwise
    if far_outer is None:
        far_o = arc_pts(r_far, a_top, K.ang(oc, far_low), cw=True)      # top → far side, clockwise
    else:
        top_pt = P(cx, cy - r_near)
        far_o = C.sample_d(K.spline([tuple(top_pt)] + list(far_outer), h_start=0.0), 0.5)[0][0]
    hl_n = C.sample_d(K.spline(list(hairline_near)), 0.5)[0][0]
    hl_f = C.sample_d(K.spline(list(hairline_far)), 0.5)[0][0]
    near = Polygon(np.vstack([near_o, hl_n[::-1]])).buffer(0)
    far = Polygon(np.vstack([far_o, hl_f[::-1]])).buffer(0)
    cap = U(near, far).buffer(0.4).buffer(-0.4)
    cap = max(K._polys_of(cap), key=lambda g: g.area)
    lines = C.Frag()
    # near side: lines follow the outer contour from the crown down the back
    lines += K.current_lines(near_o, n_cap, near, side=+1, edge=CONTOUR, stagger=10.0)
    lines += K.current_lines(far_o, max(n_cap - 2, 1), far, side=-1, edge=CONTOUR, stagger=8.0)
    capP = K.Part(cap, K.fill(cap, color), lines + K.outline(cap), {"part": P(part)})
    # ---- the long lock over the near shoulder
    reg, le, ri = _ribbon(C.sample_d(K.spline(list(fall)), 0.5)[0][0], fall_w[0], fall_w[1])
    fl = K.current_lines(ri, n_fall, reg, side=+1, edge=CONTOUR, stagger=9.0)
    fallP = K.Part(reg, K.fill(reg, color), fl + K.outline(reg), {})
    return capP, fallP
