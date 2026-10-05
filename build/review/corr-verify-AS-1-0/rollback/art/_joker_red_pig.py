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
* The gold jester collar never touches red (§C rule 4): band + five dags
  fanned toward the head, a bell at each point, each gold shape in a thin
  paper moat cut from the neck (the V's closed only next to the band, red
  crumbs between the bells dropped) -- the red neck runs on between the
  dags, so the head stays joined to the body; the ear and the near foreleg
  lie over the collar.
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
GOLD_MOAT = 3.6                    # paper between gold and red (registration >= 3)
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


def _dags(seg, t0, t1, hw):
    """Five dags + bells spread over seg[t0:t1] (arclength)."""
    fwd = H.U
    n = P.DAG_N
    wid = (t1 - t0) / n
    out = []
    for i in range(n):
        s0 = t0 + (t1 - t0) * (i + 0.5) / n
        b = np.asarray(seg.interpolate(s0).coords[0])
        a0 = np.asarray(seg.interpolate(max(s0 - 1.0, 0)).coords[0])
        a1 = np.asarray(seg.interpolate(min(s0 + 1.0, seg.length)).coords[0])
        tan = (a1 - a0) / np.hypot(*(a1 - a0))
        nrm = np.array([-tan[1], tan[0]])
        if nrm @ fwd < 0:
            nrm = -nrm
        k = (i - (n - 1) / 2) / ((n - 1) / 2)
        # the dags hang along the head (toward the snout), the outer ones
        # fanned out along the band by up to DAG_FAN
        along = tan if tan @ (np.asarray(seg.coords[-1]) - np.asarray(seg.coords[0])) >= 0 else -tan
        base = math.degrees(math.atan2(fwd[1], fwd[0]))
        turn = math.degrees(math.atan2(along[1], along[0])) - base
        turn = (turn + 180.0) % 360.0 - 180.0
        d = P.unit(base + k * P.DAG_FAN * (1.0 if turn > 0 else -1.0))
        root = b + nrm * (hw - 0.5)
        tip = root + d * P.DAG_L
        side = np.array([-d[1], d[0]])
        tri = Polygon([root - side * wid * P.DAG_BASE / 2, tip, root + side * wid * P.DAG_BASE / 2])
        bc = tip + d * (P.BELL_D / 2 - 3.0)
        out.append((tri, Point(*bc).buffer(P.BELL_D / 2, quad_segs=24), bc))
    return out


def collar_shape(sil, cover):
    """The gold jester collar: the band (clipped to the neck), and five dags
    with bells spread over the stretch of band where every dag and bell
    clears ``cover`` (the ear and near foreleg lying over the collar)."""
    arc = spline(H.pts(P.COLLAR))
    ln = line(arc)
    hw = P.COLLAR_W / 2
    band = ln.buffer(hw, cap_style="flat", quad_segs=16).intersection(sil.buffer(1.5))
    seg = max(lines_of(ln.intersection(sil.buffer(-2.0))), key=lambda g: g.length)
    keep_out = cover.buffer(GOLD_MOAT + 2.0, quad_segs=16)
    t0, t1 = 0.0, seg.length
    for _ in range(200):
        ds = _dags(seg, t0, t1, hw)
        bad0 = ds[0][0].union(ds[0][1]).intersects(keep_out)
        bad1 = ds[-1][0].union(ds[-1][1]).intersects(keep_out)
        if not (bad0 or bad1):
            break
        t0 += 2.0 if bad0 else 0.0
        t1 -= 2.0 if bad1 else 0.0
    shapes = [band] + [g for tri, bell, _ in ds for g in (tri, bell)]
    return shapely.union_all(shapes), [bc for *_, bc in ds]


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
    # the jester collar: gold in a thin paper moat; the ear and the near
    # foreleg lie over it
    front = ps["ear"].union(ps["fore_near"].difference(ps["torso"]))
    col, _ = collar_shape(sil, front)
    col = col.difference(front.buffer(GOLD_MOAT, quad_segs=16))
    col = shapely.union_all([q for q in polys_of(col) if q.area > 30.0])
    # the collar sits in a thin paper moat; the V's between the dags close
    # only next to the band (no red slivers there), the neck runs on beyond
    ground = close(col.buffer(GOLD_MOAT, quad_segs=16), P.COLLAR_CLOSE)
    # no red crumbs between the collar's ground and the ear lying over it
    ear_ko = ps["ear"].buffer(KO, quad_segs=16)
    ground = ground.union(close(ground.union(ear_ko), 9.0).difference(ground.union(ear_ko).buffer(0.0))
                          .intersection(ear_ko.buffer(12.0)))
    holes = holes.union(ground.difference(ps["ear"]))
    gold += C.fill(G.from_shape(col), color=GOLD, role="collar")
    solid = sil.difference(holes)
    solid = clean(solid, envelope=close(sil, 1.6))
    # no red crumbs left between the bells and dags
    near = col.buffer(GOLD_MOAT + 12.0, quad_segs=16)
    solid = shapely.union_all([q for q in polys_of(solid)
                               if not (q.area < P.COLLAR_CRUMB and q.within(near))])
    for w, ang in windows:
        red += red_hatch(w.difference(solid), solid, ang)
    ink += C.dot(ec[0], ec[1], P.EYE_DOT, color=INK, role="eye")
    return {"red_lines": red, "ink": ink, "gold": gold, "sil": sil, "solid": solid, "parts": ps, "collar": col,
            "snout": H(*P.DISC_C), "tail_pts": tail_centreline()}
