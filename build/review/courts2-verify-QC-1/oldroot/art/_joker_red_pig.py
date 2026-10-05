"""JOKER_RED pig: ONE Gill Red solid with its detail knocked out to paper
(brief §H.17; director's pass-2 decision; contract §2.1, §5) -- the Little
Joker's construction, in red.

* Silhouette: the torso and head (G1 arc chains through the pose tables),
  the disc, the leaf-shaped prick ear, four legs (joint circles joined by
  common tangents, creases closed, a hock point on the hind legs) ending in
  trotters with a dewclaw and a V cleft between the claws, the spiral tail;
  filleted where the legs, ear and tail spring from the body.  The solid's
  edge IS the contour.
* Knockouts (MEDIUM 3.1 paper lines, kept EDGE px inside the silhouette,
  §I.12 bridges >= 3): shoulder and ham lines, the mouth,
  the disc's rim with two nostril holes, the ear's edge where it lies on the
  head and neck, the far limbs' edges where the near limbs and torso cover
  them, each trotter's coronet.
* The eye: a paper almond holding the Aquifer dot (the card's only Aquifer),
  >= 3 px of paper all round the dot.
* Half-hatched tracts (§B.2: FINE red hatch at the 7.0 pitch in paper
  windows rimmed with red): the ear's inner half, split on its midrib and
  hatched across it; a narrow crescent along the belly edge (the barrel's
  shaded underside, <= BELLY_W px wide, tapering to both ends), hatched at
  45 deg to the body axis.
* The gold jester collar -- the Fool's crown-collar (client correction
  2026-09-24) -- is one regular figure: a band on a circular arc across the
  neck, bowed toward the head; five equal isosceles dags standing on its
  normals at an even pitch, so they fan symmetrically; a whole round bell at
  each point with its mouth (a round hole) knocked out.  It never touches red
  (§C rule 4): its paper ground is its own outline offset a uniform GOLD_GAP
  (4.2), so the red neck shows as a V between each pair of dags and between
  the bells.  The ear crosses the band's dorsal end only (a 4.2 px interlace
  gap); at the ventral end the band runs round the throat to the near
  foreleg's outline against the far one.  Every dag and bell keeps >= 3.1 px
  of red to both.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.ops
from shapely.geometry import LineString, Point, Polygon

from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms
from inkkit import geom as G

try:
    from . import _joker_red_pose as P
except ImportError:
    import _joker_red_pose as P

RED, GOLD, INK = T.RED, T.FOIL, T.INK
KO = T.MEDIUM


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def shape(d):
    g = G.to_shape(d, tol=0.03)
    if not g.is_valid:
        g = shapely.make_valid(g)
    return g


def dense(d, step=0.4):
    return C.sample_d(d, step)[0][0]


def spline(pts, h0=None, h1=None, pins=None):
    _, p = P.open_spline(pts, h0, h1, pins)
    return np.asarray(p)


def line(pts):
    return LineString(np.asarray(pts, float))


def polys_of(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    out = []
    for q in getattr(g, "geoms", []):
        out += polys_of(q)
    return out


def lines_of(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "LinearRing":
        return [LineString(g.coords)]
    out = []
    for q in getattr(g, "geoms", []):
        out += lines_of(q)
    return out


def largest(g):
    ps = polys_of(g)
    return max(ps, key=lambda q: q.area) if ps else Polygon()


def ellipse(c, a, b, h, n=96):
    """Ellipse centred ``c``, semi-axis ``a`` along heading ``h``, ``b`` across."""
    U, V = P.unit(h), P.unit(h + 90.0)
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return Polygon([np.asarray(c) + U * a * math.cos(s) + V * b * math.sin(s) for s in t])


def capsule(c0, r0, c1, r1):
    return shapely.union_all([Point(*c0).buffer(r0, quad_segs=32),
                              Point(*c1).buffer(r1, quad_segs=32)]).convex_hull


def close(g, r):
    return g.buffer(r, quad_segs=24).buffer(-r, quad_segs=24)


def opening(g, r):
    return g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)


# ---------------------------------------------------------------------------
# silhouette parts
# ---------------------------------------------------------------------------
B, H = P.BODY, P.HEAD


def torso_shape():
    return shape(P.closed_spline(B.pts(P.TORSO)))


def disc_shape():
    return ellipse(H(*P.DISC_C), P.DISC_R[0] * H.s, P.DISC_R[1] * H.s, H.h)


def head_shape():
    return shape(P.closed_spline(H.pts(P.HEAD_PTS))).union(disc_shape())


def _bulge(p, q, sag, cen):
    ab = q - p
    nl = np.array([ab[1], -ab[0]])
    sgn = 1.0 if nl @ ((p + q) / 2 - cen) > 0 else -1.0
    return dense(forms.scallop_arc(p, q, sgn * sag))


def ear_parts():
    e = P.EAR
    R, F, Tp = H(*e["rear"]), H(*e["front"]), H(*e["tip"])
    cen = (R + F + Tp) / 3.0
    front = _bulge(F, Tp, e["front_sag"], cen)
    rear = _bulge(Tp, R, e["rear_sag"], cen)
    poly = largest(Polygon(np.vstack([front, rear[1:]])).buffer(0))
    return poly, np.array([(R + F) / 2, Tp])


def ear_shape():
    return ear_parts()[0]


def leg_frame(joints, hoof, frame=None):
    frame = frame or B
    cs = [(frame(u, v), r * frame.s) for u, v, r in joints]
    h_deg, L = hoof
    hf = P.Frame(cs[-1][0], frame.head(h_deg, joints[-1][0]))
    return cs, hf, L * frame.s


def hoof_poly(hf, L, r, dewclaw=True):
    """Cloven trotter in its frame (x toward the toe, +y the sole side): the
    pastern swelling a little to the coronet, the near claw's wall running
    to its point, the far claw's point a little behind, the sole back to the
    heel; a small dewclaw knob behind the fetlock.  The cleft between the
    claws is cut afterwards (``hoof_cleft``) so no closing fills it."""
    ring = [hf(-2.0, -r), hf(0.35 * L, -1.08 * r), hf(0.72 * L, -0.92 * r), hf(L, -0.30 * r),
            hf(0.97 * L, 0.20 * r), hf(0.92 * L, 0.74 * r), hf(0.40 * L, 1.04 * r), hf(-2.0, r)]
    g = opening(Polygon(ring).buffer(0), 1.3)
    if dewclaw:
        g = g.union(Point(*hf(-4.0, 1.0 * r)).buffer(0.40 * r, quad_segs=16))
    return g


def hoof_cleft(hf, L, r):
    """The V between the two claws, from its apex (HOOF_NOTCH) out past the
    toe (the §I.12 hygiene pass rounds the apex where it narrows below a
    knockout's width)."""
    ax, ay = P.HOOF_NOTCH
    apex = hf(ax * L, ay * r)
    w = P.HOOF_CLEFT_W
    tri = Polygon([apex, hf(1.4 * L, ay * r - w * r), hf(1.4 * L, ay * r + w * r)])
    return tri


def leg_shape(joints, hoof, hock=None):
    cs, hf, L = leg_frame(joints, hoof)
    parts = [capsule(cs[i][0], cs[i][1], cs[i + 1][0], cs[i + 1][1]) for i in range(len(cs) - 1)]
    if hock is not None:
        (c0, r0), (c1, r1) = cs[hock - 1], cs[hock]
        d = (c1 - c0) / np.hypot(*(c1 - c0))
        parts.append(capsule(c1, r1, c1 + d * r1 * 0.7, r1 * 0.6))
    parts.append(hoof_poly(hf, L, cs[-1][1], dewclaw=True))
    g = close(shapely.union_all(parts), 3.0).difference(hoof_cleft(hf, L, cs[-1][1]))
    return opening(g, 1.2), cs, hf, L


def tail_centreline():
    t = C.Turtle(*B(*P.TAIL_ROOT), B.head(P.TAIL_H0, P.TAIL_ROOT[0]))
    for a, b in P.TAIL_CURL:
        if b is None:
            t.fd(a * B.s)
        else:
            t.arc(a * B.s, b)
    return np.asarray(t.pts(0.3)[0])


def tail_tip():
    c = tail_centreline()
    v = c[-1] - c[-4]
    return c[-1], math.degrees(math.atan2(v[1], v[0]))


def tail_shape():
    """The curl as a round-ended band; if the curl crosses its own stalk the
    end passes OVER it and the stalk breaks TAIL_GAP px clear (§B.2)."""
    c = tail_centreline()
    ln = line(c)
    w = P.TAIL_W / 2
    if ln.is_simple:
        return ln.buffer(w, quad_segs=16)
    s_split = ln.length - P.TAIL_OVER
    under = shapely.ops.substring(ln, 0.0, s_split).buffer(w, quad_segs=16)
    over = shapely.ops.substring(ln, s_split - 0.5, ln.length).buffer(w, quad_segs=16)
    split_pt = Point(*shapely.ops.substring(ln, s_split, s_split).coords[0])
    zone = over.buffer(P.TAIL_GAP, quad_segs=16).difference(split_pt.buffer(3.2 * w + P.TAIL_GAP))
    return under.difference(zone).union(over)


LEGS = {
    "fore_far": (P.FORE_FAR, P.FORE_FAR_HOOF),
    "hind_far": (P.HIND_FAR, P.HIND_FAR_HOOF),
    "fore_near": (P.FORE_NEAR, P.FORE_NEAR_HOOF),
    "hind_near": (P.HIND_NEAR, P.HIND_NEAR_HOOF),
}


def parts():
    out = {"torso": torso_shape(), "head": head_shape(), "ear": ear_shape(), "tail": tail_shape()}
    for k, (j, h) in LEGS.items():
        out[k] = leg_shape(j, h, P.HOCKS.get(k))[0]
    return out


def silhouette(ps=None):
    ps = ps or parts()
    body = close(ps["torso"].union(ps["head"]), 10.0)
    for k in ("fore_near", "fore_far", "hind_near", "hind_far"):
        # fillet the leg into the torso only near the torso (a closing
        # further out would fill the trotters' clefts)
        fillet = close(ps["torso"].union(ps[k]), 7.0).difference(ps["torso"]).intersection(ps["torso"].buffer(24.0))
        body = body.union(fillet).union(ps[k])
    # fillets where the ear and the tail spring from the body
    root = Point(*B(*P.TAIL_ROOT)).buffer(8.0)
    for k, r, zone in (("ear", 4.0, ps["ear"].buffer(12.0)), ("tail", 5.0, root)):
        joined = body.union(ps[k])
        body = joined.union(close(joined, r).intersection(zone))
    return body


# ---------------------------------------------------------------------------
# knockouts
# ---------------------------------------------------------------------------
EDGE = 5.0                         # knockout lines keep this much red inside the silhouette
RIM_EDGE = 3.6                     # red rim between a hatch window and the silhouette edge
EYE_MOAT = 3.4                     # paper round the Aquifer dot
FRAMES = {"BODY": B, "HEAD": H}


def _extend(pts, which, d=40.0):
    pts = np.asarray(pts, float)
    if "0" in which:
        t = pts[0] - pts[1]
        pts = np.vstack([pts[0] + t / np.hypot(*t) * d, pts])
    if "1" in which:
        t = pts[-1] - pts[-2]
        pts = np.vstack([pts, pts[-1] + t / np.hypot(*t) * d])
    return pts


def clip_line(pts, sil, open_ends="", edge=EDGE):
    """A knockout centreline kept ``edge`` (+ half its width) inside the
    silhouette, except at ``open_ends`` where it runs out through the edge."""
    pts = _extend(pts, open_ends)
    ln = line(pts)
    zone = sil.buffer(-(edge + KO / 2), quad_segs=16)
    for k, idx in (("0", 0), ("1", -1)):
        if k in open_ends:
            zone = zone.union(Point(*pts[idx]).buffer(60.0).intersection(sil.buffer(2.0)))
    return ln.intersection(zone)


def designed_lines(sil):
    out = []
    for name, (fr, pts, open_) in P.KO_LINES.items():
        out += lines_of(clip_line(spline(FRAMES[fr].pts(pts)), sil, open_))
    return out


def overlap_lines(ps):
    """Edges where a nearer part lies on a farther red part (cut paper)."""
    torso, head = ps["torso"], ps["head"]
    out = []

    def edge(front, back, trim=None):
        g = front.boundary.intersection(back.buffer(-0.5))
        if trim is not None:
            g = g.difference(trim)
        return lines_of(g)
    for far, near in (("fore_far", "fore_near"), ("hind_far", "hind_near")):
        out += edge(torso, ps[far].difference(ps[near]))
        out += edge(ps[near], ps[far], trim=torso.buffer(-1.0))
    out += edge(ps["ear"], head.union(torso))
    return out


def hoof_geom(k):
    j, h = LEGS[k]
    _, cs, hf, L = leg_shape(j, h)
    return hf, L, cs[-1][1]


HOOF_COR = 0.12                    # coronet station (x / L)


def hoof_lines(sil):
    """The coronet: a short paper arc across the pastern at the hoof's top
    (the cleft is cut in the outline, ``hoof_cleft``)."""
    out = []
    for k in ("fore_near", "fore_far", "hind_near", "hind_far"):
        hf, L, r = hoof_geom(k)
        c = HOOF_COR * L
        cor = [hf(c + 3.0, -1.3 * r), hf(c, 0.0), hf(c + 3.0, 1.3 * r)]
        out += lines_of(clip_line(spline(cor), sil, "", edge=3.4))
    return out


def disc_lines(sil):
    """The disc's rim where it meets the snout."""
    c = np.asarray(P.DISC_C)
    a, b = P.DISC_R
    t = np.radians(np.linspace(96, 264, 60))
    pts = [H(c[0] + a * math.cos(s), c[1] + b * math.sin(s)) for s in t]
    return lines_of(clip_line(pts, sil, edge=3.8))


def eye_shape():
    """Paper almond: pointed corners, the upper lid a little flatter."""
    c = np.asarray(P.EYE_C, float)
    L, Hh = P.EYE_L / 2, P.EYE_H / 2
    back, front = H(c[0] - L, c[1] + 0.8), H(c[0] + L, c[1] - 0.4)
    _, upper = P.open_spline([back, H(c[0], c[1] - Hh), front])
    _, lower = P.open_spline([front, H(c[0], c[1] + Hh), back])
    return Polygon(np.vstack([upper, lower[1:]])).buffer(0)


def nostrils():
    return shapely.union_all([ellipse(H(*n), P.NOSTRIL_R[0] * H.s, P.NOSTRIL_R[1] * H.s, H.h) for n in P.NOSTRILS])


def red_hatch(window, solid, angle):
    """FINE red hatch at the 7.0 pitch in a paper ``window`` of the solid;
    the lines run 0.9 px into the red rim (same ink, they fuse)."""
    lines = C.hatch_lines(window.buffer(0.9, quad_segs=8), angle, T.HATCH_PITCH)
    keep = []
    for c in lines:
        st = LineString(c).buffer(T.FINE / 2, cap_style="flat")
        if all(not (0.0 < g.distance(st) < 3.0) for g in polys_of(solid)):
            keep.append(c)
    return C.stroke(keep, T.FINE, style="hatch", color=RED, role="hatch") if keep else C.Frag()


def ear_window(sil):
    """The ear's inner half: split by its midrib, the half toward the neck."""
    poly, mid = ear_parts()
    half = C.split_region(poly, [tuple(mid[0]), tuple(mid[1])], side=1)
    return half.intersection(sil.buffer(-RIM_EDGE)).intersection(poly.buffer(-(RIM_EDGE + KO / 2 + 0.4)))


def belly_crescent(sil, ps):
    """The belly's shaded underside: a narrow crescent window along the
    belly line (BELLY_SPAN in BODY u), a RIM_EDGE red rim off the belly edge,
    at most BELLY_W px wide at its middle and tapering to both ends."""
    inset = sil.buffer(-RIM_EDGE, quad_segs=16).intersection(ps["torso"])
    u0, u1 = P.BELLY_SPAN
    us = np.linspace(u0, u1, 120)
    edge, inner = [], []
    for u in us:
        # the inset belly edge at station u: the most ventral point inside
        ray = LineString([B(u, 0.0), B(u, 140.0)])
        hit = ray.intersection(inset)
        segs = lines_of(hit)
        if not segs:
            continue
        far = max((np.asarray(g.coords) for g in segs), key=lambda c: B.local(c[-1])[1])
        v_e = max(B.local(q)[1] for q in far)
        t = (u - u0) / (u1 - u0)
        w = P.BELLY_W * math.sin(math.pi * t) ** P.BELLY_TAPER / B.s
        edge.append(B(u, v_e + 1.0))
        inner.append(B(u, v_e - w))
    win = Polygon(np.vstack([edge, inner[::-1]])).buffer(0).intersection(inset)
    return largest(win)


def snap(lines, reach=KO + 3.1):
    """Join near-miss ends to the nearest other line."""
    extra = []
    for i, l in enumerate(lines):
        c = np.asarray(l.coords)
        for end in (c[0], c[-1]):
            e = Point(*end)
            best, bp = reach, None
            for j, o in enumerate(lines):
                if j == i:
                    continue
                d = o.distance(e)
                if 1e-6 < d < best:
                    best, bp = d, shapely.ops.nearest_points(o, e)[0]
            if bp is not None:
                extra.append(LineString([end, (bp.x, bp.y)]))
    return shapely.union_all(lines + extra)


def clean(solid, keep=None, bridge=3.1, slit=2.6, envelope=None):
    """§I.12 hygiene: drop red slivers thinner than ``bridge``, close paper
    slits narrower than ``slit``."""
    r = bridge / 2
    opened = solid.buffer(-r, quad_segs=8).buffer(r, quad_segs=8)
    if keep is not None:
        opened = opened.union(solid.intersection(keep))
    c = slit / 2
    closed = opened.buffer(c, quad_segs=8).buffer(-c, quad_segs=8)
    return closed if envelope is None else closed.intersection(envelope)


def collar_frame():
    """(centre, radius, middle heading) of the collar band's centreline arc
    (page px); the centre lies on the body side, so the band bows toward
    the head and the dags on its normals fan out evenly."""
    m = H(*P.COLLAR_MID)
    ax = H.head(P.COLLAR_AXIS)
    return m - P.unit(ax) * P.COLLAR_R, P.COLLAR_R, ax


def collar_band():
    """The band: an annular sector COLLAR_W wide, COLLAR_SPAN long (the
    neck, the ear and the near foreleg trim it)."""
    ctr, R, ax = collar_frame()
    hw = P.COLLAR_W / 2
    half = math.degrees(P.COLLAR_SPAN / 2 / R)
    a = np.radians(np.linspace(ax - half, ax + half, 241))
    cs = np.c_[np.cos(a), np.sin(a)]
    return Polygon(np.vstack([ctr + (R + hw) * cs, (ctr + (R - hw) * cs)[::-1]]))


def collar_dags():
    """The five dags, equal isosceles triangles standing on the band's
    normals at DAG_PITCH, each ending in a round bell whose centre is the
    dag's apex; the bell's mouth, a round hole, is knocked out a little
    beyond its centre.  -> [(triangle, bell, hole, bell centre, heading)]."""
    ctr, R, ax = collar_frame()
    hw = P.COLLAR_W / 2
    step = math.degrees(P.DAG_PITCH / R)
    off, hd = P.BELL_HOLE
    out = []
    for i in range(P.DAG_N):
        th = ax + (i - (P.DAG_N - 1) / 2) * step
        d, side = P.unit(th), P.unit(th + 90.0)
        root = ctr + d * (R + hw - 0.6)
        bc = ctr + d * (R + hw + P.DAG_L)
        tri = Polygon([root - side * P.DAG_BASE / 2, bc, root + side * P.DAG_BASE / 2])
        bell = Point(*bc).buffer(P.BELL_D / 2, quad_segs=32)
        hole = Point(*(bc + d * off)).buffer(hd / 2, quad_segs=24)
        out.append((tri, bell, hole, bc, th))
    return out


def collar_over(ps):
    """What the collar's band passes under, each with the inset of its
    visible red edge (both edges carry a KO-wide knockout line): the ear at
    the dorsal end; at the ventral end the band runs round the throat to the
    outline the near foreleg makes against the far one and turns out of
    sight there."""
    return [(ps["ear"], KO / 2), (ps["fore_far"].difference(ps["fore_near"]), KO / 2)]


def collar(sil, over):
    """The gold collar and its paper ground.

    ``over``: [(shape, inset)] from ``collar_over``.  The band keeps the
    stretch between them, GOLD_GAP clear of their visible red (a geometric
    interlace: they cross the band only); every dag and bell keeps a red
    bridge of at least COLLAR_BRIDGE between its ground and them.  The ground
    is the collar's own outline offset GOLD_GAP (the parts lying over it stay
    red), so no gold touches red (§C rule 4).
    -> (gold, ground, [bell centres])."""
    gap = P.GOLD_GAP
    zone = shapely.union_all([g.buffer(gap - ins, quad_segs=16) for g, ins in over])
    band = collar_band().intersection(sil.buffer(1.5)).difference(zone)
    mid = Point(*H(*P.COLLAR_MID))
    band = min(polys_of(band), key=lambda q: q.distance(mid))
    ds = collar_dags()
    for i, (tri, bell, *_) in enumerate(ds):
        for g, ins in over:
            red = tri.union(bell).distance(g) - gap - ins
            if red < P.COLLAR_BRIDGE:
                raise ValueError(f"collar: dag {i} leaves only {red:.2f} px of red to a part lying over the band")
    solid = shapely.union_all([band] + [g for tri, bell, *_ in ds for g in (tri, bell)])
    gold = solid.difference(shapely.union_all([hole for _, _, hole, *_ in ds]))
    ground = solid.buffer(gap, quad_segs=24).difference(shapely.union_all([g for g, _ in over]))
    return gold, ground, [bc for *_, bc, _ in ds]


def build():
    ps = parts()
    sil = silhouette(ps)
    ink, red, gold = C.Frag(), C.Frag(), C.Frag()

    ko = designed_lines(sil) + overlap_lines(ps) + hoof_lines(sil) + disc_lines(sil)
    holes = snap(ko).buffer(KO / 2, quad_segs=8).union(nostrils())
    ec = H(*P.EYE_C)
    holes = holes.union(eye_shape())
    windows = []
    ew = ear_window(sil)
    if not ew.is_empty:
        _, mid = ear_parts()
        windows.append((opening(ew, 2.6), math.degrees(math.atan2(*(mid[1] - mid[0])[::-1])) + 90.0))
    bw = belly_crescent(sil, ps)
    if not bw.is_empty:
        ang = B.head(P.BELLY_HATCH, sum(P.BELLY_SPAN) / 2)
        windows.append((opening(bw, 2.6), ang))
    windows = [(w, a) for w, a in windows if not w.is_empty]
    for w, _ in windows:
        holes = holes.union(w)
    # the jester collar: gold in a paper ground offset GOLD_GAP round it;
    # the ear crosses the band's dorsal end, the band runs round the throat
    # to the forelegs' outline
    col, ground, _ = collar(sil, collar_over(ps))
    holes = holes.union(ground)
    gold += C.fill(G.from_shape(col), color=GOLD, role="collar")
    solid = sil.difference(holes)
    solid = clean(solid, envelope=close(sil, 1.6))
    # no red crumbs left in the collar's ground
    near = ground.buffer(6.0, quad_segs=16)
    solid = shapely.union_all([q for q in polys_of(solid)
                               if not (q.area < P.COLLAR_CRUMB and q.within(near))])
    for w, ang in windows:
        red += red_hatch(w.difference(solid), solid, ang)
    ink += C.dot(ec[0], ec[1], P.EYE_DOT, color=INK, role="eye")
    return {"red_lines": red, "ink": ink, "gold": gold, "sil": sil, "solid": solid, "parts": ps, "collar": col,
            "snout": H(*P.DISC_C), "tail_pts": tail_centreline()}
