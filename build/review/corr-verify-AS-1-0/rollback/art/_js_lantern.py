"""art/_js_lantern.py — J♠'s hexagonal lantern (§H.3): gold frame, ray-lined
panes, a paper vesica flame with a red core, and a cap cast as a coiled San
Marcos salamander in gold, hung on a short chain.

The lantern is a hexagonal prism seen flat-face-on: four posts show (the
corner posts at ±R and the front-pane posts at ±R/2), so the front pane is R
wide and the two side panes R/2 (cos 60°). From the top:

* the BAIL: the salamander coiled round the ring the chain hangs from (the
  'cap cast as a coiled San Marcos salamander, sculpted in gold');
* a drum COLLAR, the hexagonal pyramid ROOF in elevation (two front hip
  ribs, the shaded left facets half-hatched), the CORNICE;
* the BODY: posts and ray-lined paper panes; in the front pane the paper
  vesica FLAME with a red core on a small gold burner; the rays spring
  from the flame and butt on the frame (no free ends);
* the bottom RAIL, a two-tread stepped PLINTH (the ♠ pip's plinth) and a
  stalactite DRIP (§G.13: split on its axis, one half hatched) — the Deep.
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
GOLD, INK, RED = K.GOLD, K.INK, K.RED
P = K.P


class LanternSpec:
    def __init__(self, x=528.0, *, ring=(242.0, 12.5), R=50.0, collar=(256.0, 266.0), eave=292.0,
                 cornice=(290.0, 300.0), body=(300.0, 382.0), rail=(382.0, 391.0), plinth=((391.0, 399.0, 44.0),
                                                                                         (399.0, 406.0, 32.0)),
                 drip=(406.0, 432.0, 9.0), post_w=8.0, flame=(344.0, 38.0, 15.0),
                 cornice_over=8.0):
        self.x = x
        self.ring_c = P(x, ring[0])
        self.ring_r = ring[1]
        self.R = R
        self.collar = collar
        self.eave = eave
        self.cornice = cornice
        self.body = body
        self.rail = rail
        self.plinth = plinth
        self.drip = drip
        self.post_w = post_w
        self.flame = flame
        self.cornice_over = cornice_over


def salamander(s: LanternSpec, *, hw=7.0, a_head=-128.0, sweep=312.0, tail_in=7.0, legs=(0.13, 0.50),
               lift=38.0, head=(19.0, 9.5), gill=True, flecks=3,
               gill_len=9.0, gill_w=4.2, avoid=None):
    """The cap's bail: a San Marcos salamander (§H.3; small, slender, dark in
    life — the Q♠'s pale one's counterpart), cast in gold and coiled round
    the ring the chain hangs from. Seen from the side: the body runs
    clockwise from the head (upper left, raised, looking back at the page)
    round the ring; two near legs splay outward and back, each a bent tube
    ending in a splayed three-toed foot; the tail tapers and spirals in
    under the head; a broad round-snouted head with a large eye and three
    short gill tufts behind it (the species' external gills, §I.23); a row of
    Aquifer flecks down the back. → Part (gold, MEDIUM outline; kept out of
    the CONTOUR silhouette)."""
    c = s.ring_c
    rc = s.ring_r
    n = 300
    t = np.linspace(0, 1, n)
    angs = a_head + sweep * t
    rad = rc - tail_in * np.clip((t - 0.60) / 0.40, 0, 1) ** 1.2
    spine = np.column_stack([c[0] + rad * np.cos(np.radians(angs)), c[1] + rad * np.sin(np.radians(angs))])

    def w(tt):
        if tt < 0.06:
            return hw * 0.80 + (hw - hw * 0.80) * tt / 0.06          # the neck
        if tt < 0.56:
            return hw
        return max(1.0, hw * (1 - (tt - 0.56) / 0.44) ** 0.9)        # the tail tapers to a point
    body, left, right, _ = U.ribbon(spine, w, tip_round=1.0)
    # head: a broad flat round-snouted head beyond the neck, lifted off the ring
    h0 = spine[0]
    tang = spine[0] - spine[4]
    tang = tang / np.hypot(*tang)
    out0 = K.unit(a_head)
    hd = math.degrees(math.atan2(tang[1], tang[0]))
    # turn the head toward the outward radial by ``lift`` degrees
    ho = math.degrees(math.atan2(out0[1], out0[0]))
    dh = ((ho - hd + 180.0) % 360.0) - 180.0
    hd = hd + math.copysign(min(abs(dh), lift), dh)
    u, v = K.unit(hd), K.unit(hd + 90.0)
    hl, hwid = head
    # a broad, blunt, round-snouted head: the hull of the snout disc and the neck
    snout = Point(*(h0 + u * (hl - hwid / 2))).buffer(hwid / 2, quad_segs=24)
    cheeks = Point(*(h0 + u * 5.0)).buffer(hwid / 2 + 0.8, quad_segs=24)
    neck = LineString([tuple(h0 - u * 3.0 + v * hw * 0.8), tuple(h0 - u * 3.0 - v * hw * 0.8)]).buffer(0.5)
    headg = shapely.union_all([snout, cheeks, neck]).convex_hull
    parts = [body, headg]
    # gills: three short rounded tufts fanning back from behind the head (the
    # species keeps its external gills), on the ``gill`` side(s)
    if gill:
        sides = (1.0, -1.0) if gill == "both" else ((1.0,) if gill is True or gill > 0 else (-1.0,))
        for sd in sides:
            base = h0 + u * 3.5 + v * sd * (hwid / 2 - 1.0)
            for k, da in enumerate((100.0, 130.0, 160.0)):
                q0 = base - u * (k * 2.2)
                q1 = q0 + K.unit(hd + sd * (180.0 - da)) * gill_len
                parts.append(LineString([tuple(q0), tuple(q1)]).buffer(gill_w / 2, cap_style=1))
    # the two near legs: bent tubes from the outer edge, splayed back, three-toed feet
    for tl in legs:
        i = int(tl * (n - 1))
        a = angs[i]
        p0 = K.polar(c, rad[i] + hw * 0.5, a)
        out = K.unit(a)
        back = K.unit(a + 90.0 * (1 if sweep > 0 else -1))      # toward the tail
        p1 = p0 + out * 8.5 - back * 1.0
        p2 = p1 + back * 6.5 + out * 2.0
        parts.append(LineString([tuple(p0), tuple(p1), tuple(p2)]).buffer(2.3, cap_style=1, join_style=1))
        # a splayed foot: a small rounded paddle across the end of the shin
        fd = K.ang(p1, p2)
        parts.append(LineString([tuple(p2 + K.unit(fd - 70.0) * 3.2), tuple(p2 + K.unit(fd + 70.0) * 3.2)])
                     .buffer(2.2, cap_style=1))
    shape = shapely.union_all(parts).buffer(0.5, join_style=1).buffer(-0.5, join_style=1)
    shape = U.largest(shape).simplify(0.12)
    fills = K.fill(shape, GOLD)
    lines = K.outline(shape, MEDIUM, role="sal")
    eye = h0 + u * (hl * 0.50) + v * (hwid * 0.10)
    lines += K.dot(eye, 4.2, role="sal-eye")
    # flecks down the back (on the trunk, where the body is full width)
    for tt in np.linspace(0.24, 0.42, flecks) if flecks else []:
        i = int(tt * (n - 1))
        if avoid is not None and Point(*spine[i]).buffer(2.1 + 3.0 + MEDIUM).intersects(avoid):
            continue
        lines += K.dot(spine[i], 4.2, role="sal-fleck")
    return K.Part(shape, fills, lines, {"head": h0, "c": c, "eye": eye})


def chain(top, bottom, *, x=None, link_w=9.0):
    """A short chain from ``top`` (under the fist) to ``bottom`` (the bail
    ring's top): alternate face-on links (MEDIUM rings) and edge-on links
    (MEDIUM capsules), each passing through the next. → Part (not in the
    silhouette)."""
    top, bottom = P(top), P(bottom)
    L = float(np.hypot(*(bottom - top)))
    u = (bottom - top) / L
    k = max(2, int(round(L / 13.0)))
    step = L / k
    f = C.Frag()
    shp = []
    for i in range(k):
        a = top + u * (i * step)
        b = top + u * ((i + 1) * step)
        m = (a + b) / 2
        hl = step / 2 + 2.2
        ang = math.degrees(math.atan2(u[1], u[0]))
        if i % 2 == 0:
            d = C.ellipse_d(m[0], m[1], hl, link_w / 2, ang)
            f += K.line(d, MEDIUM, role="link")
            ring_pts = C.sample_d(d, 0.5)[0][0]
            shp.append(LineString(np.vstack([ring_pts, ring_pts[:1]])).buffer(MEDIUM / 2))
        else:
            p0, p1 = m - u * hl, m + u * hl
            f += K.seg(p0, p1, MEDIUM, role="link")
            shp.append(LineString([tuple(p0), tuple(p1)]).buffer(MEDIUM / 2))
    return K.Part(shapely.union_all(shp), C.Frag(), f, {})


def lantern(s: LanternSpec):
    """The lantern body: collar, roof, cornice, posts, panes (rays, flame,
    burner), rail, plinth, drip. → Part (meta 'panes', 'flame')."""
    x, R = s.x, s.R
    c0, c1 = s.collar
    k0, k1 = s.cornice
    b0, b1 = s.body
    r0, r1 = s.rail
    pw = s.post_w
    # ---- regions
    collar = K.R(K.rrect(x - 9.0, c0, x + 9.0, c1 + 1.0, 2.0))
    roof = Polygon([(x - 12.0, c1), (x + 12.0, c1), (x + R + 5.0, s.eave), (x - R - 5.0, s.eave)])
    co = s.cornice_over
    cornice = K.R(K.rrect(x - R - co, k0, x + R + co, k1, 2.0))
    body = K.box(x - R, b0 - 1.0, x + R, b1 + 1.0)
    rail = K.R(K.rrect(x - R - 5.0, r0, x + R + 5.0, r1, 2.0))
    treads = [K.R(K.rrect(x - hw_, y0 - 0.5, x + hw_, y1, 1.5)) for (y0, y1, hw_) in s.plinth]
    d0, d1, dw = s.drip
    drip = Polygon([(x - dw, d0 - 0.5), (x + dw, d0 - 0.5), (x, d1)])
    shape = shapely.union_all([collar, roof, cornice, body, rail, drip] + treads).buffer(0)
    # ---- posts
    posts = []
    for px in (-R, -R / 2, R / 2, R):
        x0 = x + px - pw / 2 if abs(px) < R else (x + px if px < 0 else x + px - pw)
        posts.append(K.box(x0, b0 - 1.0, x0 + pw, b1 + 1.0))
    frame = shapely.union_all([collar, roof, cornice, rail, drip] + treads + posts).buffer(0)
    panes = body.difference(shapely.union_all(posts)).difference(cornice).difference(rail)
    lines = C.Frag()
    # the frame's lines: its outer outline once, plus every edge between two of its
    # pieces once (a disjoint partition: each piece minus those laid over it), so
    # no two outlines ever run on top of each other into an ink solid
    order = [roof, collar, drip] + treads + [rail] + posts + [cornice]
    cells, above = [], Polygon()
    for g_ in reversed(order):
        cells.append(g_.difference(above))
        above = above.union(g_)
    lines += K.outline(frame, MEDIUM, role="lan")
    inner_edges = shapely.union_all([c_.boundary for c_ in cells if not c_.is_empty])
    inner_edges = inner_edges.difference(frame.boundary.buffer(0.6)).intersection(frame.buffer(-0.3))
    lines += U.stroke_lines(inner_edges, MEDIUM, role="lan", min_len=3.0)
    # roof: the two front hip ribs, the left (shaded) facets half-hatched
    ribL0, ribR0 = P(x - R / 2, s.eave), P(x + R / 2, s.eave)
    ribL1, ribR1 = P(x - 5.0, c1), P(x + 5.0, c1)
    lines += K.seg(ribL0, ribL1, MEDIUM, role="rib") + K.seg(ribR0, ribR1, MEDIUM, role="rib")
    shade = Polygon([tuple(ribL1), tuple(ribL0), (x - R - 5.0, s.eave), (x - 12.0, c1)]).intersection(roof)
    lines += K.hatch_in(shade.buffer(-(MEDIUM / 2)), angle=-60.0)
    # drip: split on its axis, the left half hatched (a stalactite point)
    dl = Polygon([(x - dw, d0 - 0.5), (x, d0 - 0.5), (x, d1)])
    lines += K.seg((x, d0), (x, d1 - 3.2), MEDIUM, role="drip")
    lines += K.hatch_in(dl.buffer(-0.8), angle=0.0)
    # ---- the flame: a paper vesica with a red core, standing in a gold burner
    fy, fh, fw = s.flame
    fl_top, fl_bot = P(x, fy - fh * 0.62), P(x, fy + fh * 0.38)
    flame_d = K.vesica(fl_top, fl_bot, fw)
    flame = K.R(flame_d)
    core_d = K.vesica(P(x, fy - fh * 0.14), fl_bot + P(0, -9.0), fw * 0.34)
    lines += C.stroke(flame_d, MEDIUM, style="point", role="flame")
    fills = C.Frag()
    cup = Polygon([(x - 10.0, fl_bot[1] - 3.0), (x + 10.0, fl_bot[1] - 3.0), (x + 6.5, r0 + 0.5), (x - 6.5, r0 + 0.5)])
    cup = cup.buffer(1.5, join_style=1).buffer(-1.5, join_style=1).difference(flame.buffer(0.0))
    fills += K.fill(cup, GOLD, role="burner")
    lines += K.outline(cup, MEDIUM, role="burner")
    # ---- rays: from the flame's heart out across every pane, butting on the frame
    heart = P(x, fy - fh * 0.05)
    rays = C.Frag()
    zone = panes.difference(flame.buffer(0.2)).difference(cup.buffer(0.2))
    for a in (-90.0, -90.0 - 38.0, -90.0 + 38.0, -90.0 - 70.0, -90.0 + 70.0, 180.0, 0.0, 138.0, 42.0):
        ln = LineString([tuple(heart), tuple(heart + K.unit(a) * 120.0)]).intersection(zone)
        for seg_ in K._lines_of(ln):
            if seg_.length > 4.0:
                rays += K.line(np.asarray(seg_.coords), FINE, style="hatch", role="ray")
    lines += rays
    frame_d = K.D(frame)
    fills = K.fill(frame_d, GOLD) + K.fill(core_d, RED, role="core") + fills
    meta = {"panes": panes, "flame": flame, "shape": shape, "top": c0}
    return K.Part(shape, fills, lines, meta)
