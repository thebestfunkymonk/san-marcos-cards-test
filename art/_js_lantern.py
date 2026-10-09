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
  from the flame and butt on the frame (no free ends): ≥ 32° apart where
  they leave the flame and ≥ 30° below the horizontal clear of the burner's
  corners, so heal never cuts one back into a floating dash;
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
ROOF_HATCH = 45.0


class LanternSpec:
    def __init__(self, x=528.0, *, ring=(242.0, 12.5), R=50.0, collar=(256.0, 266.0), eave=292.0,
                 cornice=(290.0, 300.0), body=(300.0, 382.0), rail=(382.0, 391.0), plinth=((391.0, 399.0, 44.0),
                                                                                         (399.0, 406.0, 32.0)),
                 drip=(406.0, 432.0, 9.0), post_w=8.0, flame=(344.0, 38.0, 15.0),
                 cornice_over=8.0, collar_hw=9.0,
                 rays=(-90.0, -130.0, -50.0, -162.0, -18.0, 150.0, 30.0)):
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
        self.collar_hw = collar_hw
        self.rays = rays


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
    ch = s.collar_hw
    collar = K.R(K.rrect(x - ch, c0, x + ch, c1 + 1.0, 2.0))
    roof = Polygon([(x - ch - 3.0, c1), (x + ch + 3.0, c1), (x + R + 5.0, s.eave), (x - R - 5.0, s.eave)])
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
    # the ribs butt on the cornice's top line (not 2 px past it: no knob under the eave)
    ribL0, ribR0 = P(x - R / 2, k0), P(x + R / 2, k0)
    ribL1, ribR1 = P(x - ch * 5.0 / 9.0, c1), P(x + ch * 5.0 / 9.0, c1)
    lines += K.seg(ribL0, ribL1, MEDIUM, role="rib") + K.seg(ribR0, ribR1, MEDIUM, role="rib")
    shade = Polygon([tuple(ribL1), tuple(ribL0), (x - R - 5.0, s.eave), (x - ch - 3.0, c1)]).intersection(roof)
    # hatched across the rib (never near-parallel to it: no long ink wedge where they meet); the dashes
    # run to the facet's edge lines' centres (ended at their inner edge, the heal cut them to stubs)
    lines += K.hatch_in(shade, angle=ROOF_HATCH)
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
    for a in s.rays:
        ln = LineString([tuple(heart), tuple(heart + K.unit(a) * 120.0)]).intersection(zone)
        for seg_ in K._lines_of(ln):
            if seg_.length > 4.0:
                rays += K.line(np.asarray(seg_.coords), FINE, style="hatch", role="ray")
    lines += rays
    frame_d = K.D(frame)
    fills = K.fill(frame_d, GOLD) + K.fill(core_d, RED, role="core") + fills
    meta = {"panes": panes, "flame": flame, "shape": shape, "top": c0}
    return K.Part(shape, fills, lines, meta)


def _leg(root, out, fwd, *, kind, L=(7.0, 6.5), w=2.3, toe=(3.6, 1.35, 36.0), dirs=None):
    """A salamander's near leg as a gold region: a bent limb from ``root``
    (on the body's outer edge) and a small splayed three-toed foot.
    ``out``: outward from the body; ``fwd``: along the body toward the head.
    Front leg: the upper arm out and a little back, the forearm reaching
    forward; hind leg: the thigh out and a little forward, the shin kicking
    back. → (region, foot point, foot direction)."""
    out, fwd = K.P(out), K.P(fwd)
    if kind == "front":
        d1 = out - fwd * 0.30
        d2 = fwd * 0.85 + out * 0.55
    else:
        d1 = out + fwd * 0.30
        d2 = -fwd * 0.85 + out * 0.55
    if dirs is not None:
        d1, d2 = K.unit(dirs[0]), K.unit(dirs[1])
    d1 = d1 / np.hypot(*d1)
    d2 = d2 / np.hypot(*d2)
    p0 = K.P(root)
    p1 = p0 + d1 * L[0]
    p2 = p1 + d2 * L[1]
    limb = LineString([tuple(p0 - d1 * 2.0), tuple(p1), tuple(p2)]).buffer(w, cap_style=1, join_style=1)
    tl, tw, spread = toe
    hd = math.degrees(math.atan2(d2[1], d2[0]))
    toes = [LineString([tuple(p2), tuple(p2 + K.unit(hd + a) * (tl + w * 0.6))]).buffer(tw, cap_style=1)
            for a in (-spread, 0.0, spread)]
    return shapely.union_all([limb] + toes), p2, d2


def salamander(s: LanternSpec, *, hw=6.4, a_head=-168.0, sweep=-305.0, tail_from=0.62, tail_in=1.5,
               head_len=18.0, head_w=12.0, snout_r=3.9, look=-158.0,
               legs=((0.15, "front", 155.0, 110.0), (0.50, "hind", 30.0, 88.0)),
               leg_L=(7.5, 7.0), leg_w=3.0, toe=(4.4, 1.3, 40.0),
               fillet=3.0, flecks=3, fleck_span=(0.24, 0.40), eye_at=(0.56, 2.7), avoid=None):
    """The cap's bail: a San Marcos salamander (§H.3; small, slender, dark in
    life — the Q♠'s pale one's counterpart) cast in gold, coiled round the
    ring the chain hangs from, seen from the side and perched on the collar.
    From the head (at the ring's left, raised, looking out toward the page)
    the body runs down round the bottom of the ring, up its right side and
    over the top as the tail, which tapers late (the chain hooks over a tail
    still ≈ 5 px thick) and ends just past the top, its tip clear of the
    neck. The head is a salamander's: long, low and flat, the jaw wider than
    the blunt rounded snout (never the round 'duck' head), the eye hanging
    from its crown. Two near legs planted on the collar's shoulders, each a
    bent limb (``legs``: (t, kind, upper°, lower°)) ending in a small splayed
    three-toed foot — never the L/T stubs that read as a tap's handles.
    The limbs are 6 px (≥ 3 px of gold inside the MEDIUM outline: a thinner
    limb is a gold hairline, QA 12) and splay clear of the collar's sides.
    Flecks down the trunk where it is clear of ``avoid``. → Part (gold,
    MEDIUM outline; kept out of the CONTOUR silhouette)."""
    c = s.ring_c
    rc = s.ring_r
    n = 320
    t = np.linspace(0, 1, n)
    angs = a_head + sweep * t
    rad = rc - tail_in * np.clip((t - 0.70) / 0.30, 0, 1) ** 1.4
    spine = np.column_stack([c[0] + rad * np.cos(np.radians(angs)), c[1] + rad * np.sin(np.radians(angs))])

    def w(tt):
        if tt < 0.05:
            return hw * 0.84 + hw * 0.16 * tt / 0.05                   # the neck
        if tt < tail_from:
            return hw
        return max(1.1, hw * (1 - (tt - tail_from) / (1 - tail_from)) ** 0.75)
    body, _, _, _ = U.ribbon(spine, w, tip_round=1.1)
    h0 = spine[0]
    u = K.unit(look)
    v = K.unit(look + 90.0)
    if v[1] > 0:
        v = -v                                                        # v: the crown side (up on the card)
    # the head: long, low, flat; jaw wider than the blunt snout
    neck = Point(*(h0 - u * 1.0)).buffer(hw * 0.84, quad_segs=24)
    jaw = Point(*(h0 + u * 5.0 - v * 0.4)).buffer(head_w / 2, quad_segs=24)
    snout = Point(*(h0 + u * (head_len - snout_r) + v * 0.6)).buffer(snout_r, quad_segs=24)
    headg = shapely.union_all([neck, jaw, snout]).convex_hull
    parts = [body, headg]
    feet, roots = [], []
    sgn = 1.0 if sweep > 0 else -1.0
    for spec in legs:
        tl, kind = spec[0], spec[1]
        dirs = tuple(spec[2:4]) if len(spec) >= 4 else None
        i = int(tl * (n - 1))
        a = angs[i]
        root = K.polar(c, rad[i] + w(tl) * 0.45, a)
        out = K.unit(a)
        fwd = K.unit(a - 90.0 * sgn)                                  # along the body toward the head
        lg, p2, d2 = _leg(root, out, fwd, kind=kind, L=leg_L, w=leg_w, toe=toe, dirs=dirs)
        parts.append(lg)
        feet.append((p2, d2))
        roots.append(root)
    shape = shapely.union_all(parts)
    # fillet the armpits: the leg leaves the body in a round concave curve, never an
    # acute paper wedge between the limb and the belly
    closed = shape.buffer(fillet, join_style=1).buffer(-fillet, join_style=1)
    near = shapely.union_all([Point(*q).buffer(7.5) for q in roots]) if roots else Polygon()
    shape = shape.union(closed.difference(shape).intersection(near))
    shape = shape.buffer(0.6, join_style=1).buffer(-0.6, join_style=1)
    shape = U.largest(shape).simplify(0.12)
    fills = K.fill(shape, GOLD)
    lines = K.outline(shape, MEDIUM, role="sal")
    # the eye hangs from the crown of the head: the dot's top runs into the outline (an ink
    # dot 1–2 px short of the outline would leave a gold sliver), ``eye_at`` = (fraction of
    # the head length, px from the top edge to the dot's centre)
    q = h0 + u * (head_len * eye_at[0])
    ray = LineString([tuple(q), tuple(q + v * 20.0)]).intersection(headg.boundary)
    hits = [np.asarray(g.coords[0], float) for g in getattr(ray, "geoms", [ray])] if not ray.is_empty else []
    top = min(hits, key=lambda z: float(np.hypot(*(z - q)))) if hits else q + v * head_w * 0.4
    eye = np.asarray(top, float) - v * eye_at[1]
    lines += K.dot(eye, 4.2, role="sal-eye")
    for tt in np.linspace(fleck_span[0], fleck_span[1], flecks) if flecks else []:
        i = int(tt * (n - 1))
        if avoid is not None and Point(*spine[i]).buffer(2.1 + 3.0 + MEDIUM).intersects(avoid):
            continue
        lines += K.dot(spine[i], 4.2, role="sal-fleck")
    return K.Part(shape, fills, lines, {"head": h0, "c": c, "eye": eye, "feet": feet, "spine": spine})
