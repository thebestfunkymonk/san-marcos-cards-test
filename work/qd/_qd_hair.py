"""art/_qd_hair.py — Q♦'s hair and bare skin: the swept gold hair (cap and
long tresses, §G.24 current lines), the neck with the spring of the
shoulders, and the pearl choker. Built on deck.courtkit; art/QD.py stacks
them."""
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


def sp(points, h_start=None, h_end=None, step=0.5):
    """Dense points of the kit's G1 arc spline."""
    return C.sample_d(K.spline(list(points), h_start, h_end), step)[0][0]


def neck_chest(axis=380.0, *, top=236.0, hw=14.5, base_y=286.0, shoulder=(346.0, 420.0), spring_y=300.0,
               bottom=380.0, lean=0.0) -> K.Part:
    """Bare skin: the neck column (a slender taper under the jaw) springing
    at its base into the shoulders — each side a tangent arc out to the
    cape's inner edge — and the chest down under the gown's neckline. Paper
    is never painted: the Part only hides what is behind it and draws the
    neck's two MEDIUM side lines."""
    xl, xr = axis - hw, axis + hw
    sl, sr = shoulder
    left = K.Path((xl + 1.0 + lean, top)).line((xl, base_y)).arc3((xl - 5.0, base_y + 9.5), (sl, spring_y))
    right = K.Path((xr - 1.0 + lean, top)).line((xr, base_y)).arc3((xr + 5.0, base_y + 9.5), (sr, spring_y))
    lp = C.sample_d(left.d, 0.5)[0][0]
    rp = C.sample_d(right.d, 0.5)[0][0]
    reg = Polygon(np.vstack([lp, [[sl - 4.0, spring_y + 2.0], [sl - 4.0, bottom], [sr + 4.0, bottom],
                                  [sr + 4.0, spring_y + 2.0]], rp[::-1]])).buffer(0)
    lines = K.line(left.d, MEDIUM, role="neck") + K.line(right.d, MEDIUM, role="neck")
    return K.Part(reg, C.Frag(), lines, {"left": lp, "right": rp})


def pearls(p0, pm, p1, *, d_min=4.2, d_max=6.3, gap=3.2, color=GOLD) -> C.Frag:
    """A graduated pearl strand (§G.29) along the arc p0 → pm → p1: gold beads,
    the largest at the centre, 3 px apart."""
    return MG.pearl_beading(K.arc3(p0, pm, p1), d_min=d_min, d_max=d_max, gap=gap, style="dot", color=color)


def ribbon(spine, w0, w1, *, cap=True, w_mid=None):
    """A lock of hair along ``spine`` (points, root → end), its width
    tapering w0 → (w_mid →) w1, the end rolled (a semicircle). → (region,
    left edge pts, right edge pts, centre pts) — left/right = screen-left /
    screen-right of travel."""
    cv = G.Curve(np.asarray(spine, float))
    pts = cv.resample(0.5)
    n = len(pts)
    t = np.linspace(0, 1, n)
    tang = np.gradient(pts, axis=0)
    tang /= np.hypot(tang[:, 0], tang[:, 1])[:, None]
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
    if w_mid is None:
        w = w0 + (w1 - w0) * t
    else:
        w = np.where(t < 0.5, w0 + (w_mid - w0) * t * 2, w_mid + (w1 - w_mid) * (t - 0.5) * 2)
    hw = (w / 2)[:, None]
    left, right = pts + nrm * hw, pts - nrm * hw
    ring = [left]
    if cap:
        c, r = pts[-1], float(hw[-1, 0])
        a0 = math.degrees(math.atan2(nrm[-1][1], nrm[-1][0]))
        for sgn in (-1, 1):
            th = np.radians(np.linspace(a0, a0 + sgn * 180.0, 40))
            arc = np.column_stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)])
            if np.dot(arc[20] - c, tang[-1]) > 0:
                break
        ring.append(arc)
    ring.append(right[::-1])
    reg = Polygon(np.vstack(ring)).buffer(0)
    return reg, left, right, pts


def lock(spine, w0, w1, *, n=2, side=+1, stagger=9.0, w_mid=None, color=GOLD, edge=CONTOUR,
         curl_deg=80.0) -> K.Part:
    """One long lock (§G.24): a gold ribbon with ``n`` current lines
    following its ``side`` edge (+1: the screen-right edge of travel is the
    guide, lines offset to its left), each rolling into a Ø6.3 terminal."""
    reg, le, ri, _ = ribbon(spine, w0, w1, w_mid=w_mid)
    guide = ri if side > 0 else le
    fl = K.current_lines(guide, n, reg, side=side, edge=edge, stagger=stagger, curl_deg=curl_deg)
    return K.Part(reg, K.fill(reg, color), fl + K.outline(reg), {"left": le, "right": ri})


def cap(fc, *, crown, r_back, back_low, hairline, far_outer, hairline_far, n=3, n_far=1, stagger=9.0,
        color=GOLD, back_pts=None) -> K.Part:
    """The hair over the skull of a 3/4-right head, swept back from the face.

    near (back) side: the outer contour an arc about ``crown`` (radius
    ``r_back``) from the top round the back of the skull to ``back_low``
    (or through ``back_pts``), the hairline a spline (``hairline``: from
    under the diadem at the front, over the temple and the ear, to the jaw).
    Current lines run PARALLEL TO THE HAIRLINE — the hair swept back — each
    rolling into a terminal toward the nape.
    far side: a narrow band beyond the far cheek (``far_outer`` / its
    ``hairline_far``), plain or with ``n_far`` lines."""
    cx, cy = crown
    top = P(cx, cy - r_back)
    if back_pts is None:
        a1 = K.ang(P(crown), P(back_low))
        a1 = K.unwrap(-90.0, a1, cw=False)
        th = np.radians(np.linspace(-90.0, a1, 200))
        outer = np.column_stack([cx + r_back * np.cos(th), cy + r_back * np.sin(th)])
    else:
        outer = sp([tuple(top)] + list(back_pts), h_start=180.0)
    hl = sp(hairline)
    near = Polygon(np.vstack([outer, hl[::-1]])).buffer(0)
    fo = sp([tuple(top)] + list(far_outer), h_start=0.0)
    hf = sp(hairline_far)
    far = Polygon(np.vstack([fo, hf[::-1]])).buffer(0)
    reg = U(near, far).buffer(0.4).buffer(-0.4)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    lines = K.current_lines(hl, n, near, side=-1 if hl[-1][1] > hl[0][1] else +1, edge=MEDIUM, stagger=stagger)
    if not lines.meta.get("lines"):
        lines = K.current_lines(hl, n, near, side=+1, edge=MEDIUM, stagger=stagger)
    if n_far:
        lines += K.current_lines(hf, n_far, far, side=+1, edge=MEDIUM, stagger=stagger)
    return K.Part(reg, K.fill(reg, color), lines + K.outline(reg), {"near": near, "far": far, "hairline": hl})


def tress(inner, outer, *, n=4, stagger=10.0, curl_deg=80.0, color=GOLD, end_r=None, side=+1, first=None,
          guide="inner", h_in=None, h_out=None, guide_from=None, guide_pts=None) -> K.Part:
    """One continuous mass of hair from the face to a rolled end: the region
    between the ``inner`` edge (points from the root at the brow, over the
    temple and down the tress — the side against the face and neck) and the
    ``outer`` edge (the same direction, round the back of the skull and down
    the tress), closed at the root by a straight cut (hidden under the
    diadem) and at the end by a round cap. Current lines (§G.24) run the
    whole length parallel to the ``guide`` edge, staggered and curled at
    their ends. ``side``: +1 when the outer edge is to the screen-left of
    travel along the inner edge."""
    pi = sp(inner, h_start=h_in)
    po = sp(outer, h_start=h_out)
    a, b = pi[-1], po[-1]
    c = (a + b) / 2
    r = float(np.hypot(*(b - a))) / 2 if end_r is None else end_r
    # round end: a semicircle from the outer end to the inner end, bulging forward
    tang = pi[-1] - pi[-6]
    tang = tang / np.hypot(*tang)
    mid = c + tang * r
    cap = C.sample_d(K.arc3(tuple(b), tuple(mid), tuple(a)), 0.5)[0][0]
    ring = np.vstack([pi, cap[::-1][1:-1][::-1] if False else cap[::-1], po[::-1]])
    ring = np.vstack([pi, cap[::-1], po[::-1]]) if np.hypot(*(cap[0] - pi[-1])) > np.hypot(*(cap[-1] - pi[-1])) \
        else np.vstack([pi, cap, po[::-1]])
    reg = Polygon(ring).buffer(0)
    if reg.geom_type != "Polygon":
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    g = pi if guide == "inner" else po
    if guide_pts is not None:
        g = sp(guide_pts)
    if guide_from is not None:                    # start the lines below the root (where the mass is wide)
        g = g[np.argmin(np.hypot(g[:, 0] - guide_from[0], g[:, 1] - guide_from[1])):]
    sd = side if guide == "inner" else -side
    fl = K.current_lines(g, n, reg, side=sd, edge=MEDIUM if guide == "inner" else CONTOUR, stagger=stagger,
                         curl_deg=curl_deg, first=first)
    return K.Part(reg, K.fill(reg, color), fl + K.outline(reg), {"inner": pi, "outer": po})
