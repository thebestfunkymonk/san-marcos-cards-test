"""art/_js_hood.py — J♠'s short-caped hood (§H.3 'a short-caped hood in Gill
Red with a stepped crest and a gold Lion Mark badge'; 'gold hair locks
escape the hood').

A chaperon hood for a PROFILE-RIGHT head, drawn as explicit compass-built
runs (G1 arc splines through pinned points, the J♥/J♣ method):

* the HOOD: the skull + 13 px; its face opening (the RIM) starts on the
  forehead, sweeps back over the temple, down in front of the covered ear,
  round the jaw and under the chin; a turned-back jade LINING band inside
  the rim, its fold a MEDIUM line;
* the stepped CREST: a jade comb on the crown rising toward the back in
  three fault-steps (level treads, plumb risers: the Balcones escarpment, as
  the K♠ crown), its middle course hatched like the strata (§G.11), then one
  fall to the dome;
* the short CAPE over both shoulders, its hem cut into slender stalactite
  dags (§G.13) with concave edges and sharp points;
* the gold LOCKS: a fringe curling out from under the brim over the
  forehead and a side lock rolling at the cheek (tapered ribbons ending in
  rolled curls, §G.24; too slim for an inner current line).

A kit variation: courtkit.cap(kind='hood') is a skull cap with a narrow
fall; the page needs an opening that frames the profile, a crest and a
cape, so it lives here.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from art import _js_util as U

MEDIUM, FINE, CONTOUR, RULE = K.MEDIUM, K.FINE, K.CONTOUR, K.RULE
P = K.P


class HoodGeo:
    """The hood's construction in card px (see the module docstring).

    outer   the silhouette run from the brim over the dome, down the back and
            out over the viewer's-left shoulder to the hem's left end;
    right   the run from the hem's right end over the right shoulder to the
            gorget's front;
    rim     the face opening from the gorget's front back under the chin, up
            the jaw and temple to the brim;
    hem     (left end, right end, sag, dags, depth)."""

    def __init__(self, fc, *, O=(378.0, 207.0), Ro=58.0,
                 outer=((424.0, 171.0), (406.0, 154.0), (378.0, 149.0), (350.0, 156.0), (332.0, 176.0),
                        (322.0, 206.0), (323.0, 238.0), (330.0, 264.0), (326.0, 288.0), (298.0, 306.0),
                        (252.0, 321.0), (214.0, 336.0), (194.0, 356.0), (188.0, 378.0)),
                 right=((578.0, 372.0), (572.0, 350.0), (552.0, 334.0), (508.0, 316.0), (466.0, 305.0),
                        (440.0, 298.0)),
                 rim=((440.0, 298.0), (418.0, 290.0), (392.0, 281.0), (370.0, 262.0), (360.0, 236.0),
                      (362.0, 208.0), (372.0, 186.0), (392.0, 173.0), (412.0, 168.0), (424.0, 171.0)),
                 hem_sag=16.0, dags=9, dag_depth=22.0, dag_concave=3.0, lining=9.0,
                 crest=((404.0, 139.0), (386.0, 129.0), (366.0, 119.0), (346.0, 119.0)), crest_land=-152.0,
                 dag_depths=None, simplify=0.08):
        self.fc = fc
        self.O, self.Ro = P(O), Ro
        _, out_pts = U.open_spline(list(outer))
        _, right_pts = U.open_spline(list(right))
        _, rim_pts = U.open_spline(list(rim))
        self.rim = rim_pts
        self.brim = P(rim[-1])
        self.gorget = P(rim[0])
        # ---- the hem: a sagging arc cut into stalactite dags
        hl, hr = P(outer[-1]), P(right[0])
        hc, hR = K.sag_centre(hl, hr, -hem_sag)
        a0 = K.ang(hc, hl)
        a1 = K.unwrap(a0, K.ang(hc, hr), cw=False)
        self.hem_c, self.hem_R, self.hem_a = hc, hR, (a0, a1)
        roots = [K.polar(hc, hR, a0 + (a1 - a0) * k / dags) for k in range(dags + 1)] if dags else [hl, hr]
        depths = list(dag_depths) if dag_depths is not None else [dag_depth] * dags
        tips = [K.polar(hc, hR + depths[k], a0 + (a1 - a0) * (k + 0.5) / dags) for k in range(dags)]
        if dags:
            hem_pts = [roots[0]]
            for k in range(dags):
                # each dag's edges are concave arcs (a slender stalactite point)
                for pa, pb, sg in ((roots[k], tips[k], 1.0), (tips[k], roots[k + 1], 1.0)):
                    seg_ = C.sample_d(K.arc_sag(pa, pb, sg * dag_concave), 0.5)[0][0]
                    hem_pts += [tuple(q) for q in seg_[1:]]
        else:
            seg_ = C.sample_d(K.arc_c(hc, hR, a0, a1), 0.5)[0][0]
            hem_pts = [tuple(q) for q in seg_]
        self.dag_tips, self.dag_roots = tips, roots
        ring = np.vstack([out_pts, np.asarray(hem_pts[1:-1]), right_pts, rim_pts[1:-1]])
        body = U.largest(Polygon(ring).buffer(0))
        # round every corner except the dag tips (sharp stalactite points)
        soft = body.buffer(2.0, join_style=1).buffer(-2.0, join_style=1)
        if tips:
            tip_zone = shapely.union_all([Point(*t).buffer(dag_depth * 0.5) for t in tips])
            soft = soft.difference(tip_zone).union(body.intersection(tip_zone))
        self.body = U.largest(soft).simplify(simplify)
        # ---- the face opening: everything in front of the rim
        far = [(self.brim[0], 60.0), (self.gorget[0] + 160.0, 60.0), (self.gorget[0] + 160.0, self.gorget[1])]
        self.opening = Polygon(np.vstack([rim_pts, far])).buffer(0)
        # the lining: a band along the rim, two-sided so it covers the body's own
        # (softened) edge there exactly — no red sliver between lining and edge
        band = LineString(rim_pts).buffer(lining, cap_style=2, join_style=1)
        # the lining stops short of the brim's point (no jade wedge under the joined outlines)
        self.lining = U.largest(band.intersection(self.body).difference(Point(*self.brim).buffer(7.0)))
        # ---- the crest: a comb of three fault-steps (level treads, plumb risers)
        # rising toward the back, then one round fall to the nape; its foot hides
        # in the dome (the hood is stacked in front of it)
        self.crest = _crest(self.O, Ro, crest, land=crest_land)
        self.crest_treads = [float(y) for _, y in crest[:-1]]
        self.crest_vis = U.largest(self.crest.difference(self.body))
        self.shape = U.largest(shapely.union_all([self.body, self.crest]).buffer(0.2).buffer(-0.2))
        self.hood_only = self.shape.difference(K.box(0, 300.0, 2000, 2000))


def _crest(O, Ro, steps, land=-150.0, fall_sag=6.0):
    """The stepped comb: ``steps`` = [(x, y), ...] the front x and tread
    height of each step, the last point the back end of the top tread. The
    front riser drops from the first tread into the dome; the back falls in
    one arc (bulging ``fall_sag`` out) to ``land`` (degrees about the dome
    centre O, on the dome of radius Ro); the foot is an arc 12 px inside
    the dome (hidden by the hood). → region."""
    O = P(O)
    xs = [float(x) for x, _ in steps]
    ys = [float(y) for _, y in steps]
    a_front = K.ang(O, (xs[0], O[1] - math.sqrt(max(Ro ** 2 - (xs[0] - O[0]) ** 2, 1.0))))
    foot_front = K.polar(O, Ro - 12.0, a_front)
    pts = [tuple(foot_front), (xs[0], ys[0])]
    for k in range(1, len(steps) - 1):
        pts += [(xs[k], ys[k - 1]), (xs[k], ys[k])]
    x_end, y_top = xs[-1], ys[-2]
    pts.append((x_end, y_top))
    q = K.polar(O, Ro + 1.0, land)
    fall = C.sample_d(K.arc_sag(P(x_end, y_top), q, fall_sag), 0.5)[0][0]
    pts += [tuple(p_) for p_ in fall[1:]]
    for t in np.linspace(land, a_front, 40):
        pts.append(tuple(K.polar(O, Ro - 12.0, t)))
    reg = Polygon(pts).buffer(0)
    reg = reg.buffer(1.5, join_style=2).buffer(-1.5, join_style=2)
    reg = reg.buffer(-2.5, join_style=1).buffer(2.5, join_style=1)      # soften the convex step corners
    return reg


def crest_part(g: HoodGeo, *, color=K.JADE) -> K.Part:
    """The jade stepped comb (behind the hood: its foot hides in the dome),
    its middle course (between the first two treads) hatched FINE 45°."""
    reg = g.crest
    lines = K.outline(reg)
    # the crest is the escarpment in section: its middle course (between the first
    # two treads, behind the second riser) is hatched (§G.11: alternate courses)
    ys = sorted(set(g.crest_treads))
    x0, y0, x1, y1 = reg.bounds
    for ya, yb in zip(ys[1:-1:2], ys[2::2]):
        zone = K.box(x0 - 5, ya, x1 + 5, yb).intersection(g.crest_vis.buffer(-0.2))
        lines += K.hatch_in(zone, angle=-45.0)
    return K.Part(reg, K.fill(reg, color), lines, {})


def hood_part(g: HoodGeo, *, color=K.RED, lining_color=K.JADE) -> K.Part:
    """The hood + cape as one Part: the red body and the jade lining with its
    MEDIUM fold (the lining's inner edge). The dagged hem carries no
    ornament of its own: the stalactite points are the ornament."""
    shape = g.body
    body = U.largest(shape.difference(g.lining.buffer(0.05)))
    fills = K.fill(body, color) + K.fill(g.lining, lining_color)
    lines = K.outline(shape)
    fold = g.lining.boundary.intersection(shape.buffer(-1.0))
    lines += U.stroke_lines(fold, MEDIUM, role="fold", min_len=6.0)
    return K.Part(shape, fills, lines, {"lining": g.lining})


def lock(guide_pts, *, hw=(7.0, 9.0, 4.0), belly=0.35, curl=(7.0, 200.0), side=+1, n=1, stagger=8.0,
         clip=None, color=K.GOLD, curl_deg=110.0, line_edge=+1, h_start=None) -> K.Part:
    """One gold lock (§G.24): a tapered ribbon along the open spline through
    ``guide_pts`` (root → free end) whose end rolls on into a curl (``curl`` =
    radius, degrees, turning toward ``side``: +1 screen-left of travel); half
    widths ``hw`` = (root, belly, tip). ``n`` current lines offset inward
    from the edge on ``line_edge`` (+1 the left edge), rolling into Ø6.3
    terminals. ``clip``: region the lock is cut to (its root hides there)."""
    _, gp = U.open_spline(guide_pts, h_start=h_start)
    if curl:
        gp = K._curl(gp, side, curl[0], curl[1])
    h0, hm, h1 = hw

    def f(t):
        if t < belly:
            return h0 + (hm - h0) * math.sin(math.pi / 2 * t / belly)
        return h1 + (hm - h1) * math.cos(math.pi / 2 * (t - belly) / (1 - belly))
    reg, left, right, pts = U.ribbon(gp, f, tip_round=h1)
    if clip is not None:
        reg = U.largest(reg.intersection(clip))
    lines = C.Frag()
    if n:
        edge = left if line_edge > 0 else right
        lines = K.current_lines(edge[: int(len(edge) * 0.9)], n, reg, side=-line_edge, edge=CONTOUR,
                                stagger=stagger, curl_deg=curl_deg)
    return K.Part(reg, K.fill(reg, color), K.outline(reg, role="lock") + lines, {"guide": pts})
