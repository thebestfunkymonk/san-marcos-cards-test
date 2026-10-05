"""JOKER_BLACK plumage: the Aquifer silhouette, its geometric knockouts and
the jade half-hatched feather tracts (brief §H.18; contract §2.1, §5).

Model
-----
* The bird is ONE Aquifer solid: head, neck, body, wing, bill, tail, legs.
* Feathering is knocked out of it as MEDIUM (3.1) paper lines (§B.2
  knockout lines in solids; QA §I.12: holes >= 2.5 px, bridges >= 3 px):
    - scale arcs: rows across the breast (perpendicular to the body axis,
      growing toward the belly) and two covert rows on the wing, all
      bulging toward the tail;
    - the folded wing as a painter's stack of feathers (coverts block,
      two tertials, two secondaries, the primary projection): every
      visible feather edge more than 10 px inside the silhouette is a line,
      so the tips step down the wing's lower edge as they do in the bird;
    - the rectrix edges of the graduated, V-keeled tail; the gape.
* The jade tracts: one lit feather in each -- the upper tertial and the
  outer rectrix of the near arm of the keel -- are windows in the solid,
  each holding FINE jade hatch at the 7.0 pitch raked toward the feather tip
  like barbs (45 deg to the tract's axis). The window is the feather plus
  the outer half of its own outline, so the hatch butts onto the next
  feather's ink; an ink rim keeps it off the silhouette edge. Jade prints
  BELOW the ink, so it only ever lives in holes of the solid (§2.1).
* The eye is a hole holding a gold iris ring under the Aquifer pupil.
* Hygiene: near-miss joins are snapped shut, ink slivers < 3.1 px and paper
  slits < 2.6 px are removed, hatch lines that would graze an ink corner
  (< 3 px registration) are left out.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.ops
from shapely.geometry import LineString, Point, Polygon

from inkkit import geom as G
from deck import tokens as T
from deck import motifs as M
from deck.motifs import forms

import _joker_black_pose as P

KO = T.MEDIUM                       # knockout line width
RIM = 3.3                           # ink rim framing a hatched window (bridge >= 3)
EDGE = 5.0                          # knockouts keep this much ink inside the silhouette edge
TRAP = 0.9                          # jade tucks this far under the ink (print trap)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def shape(d):
    g = G.to_shape(d, tol=0.03)
    if not g.is_valid:
        g = shapely.make_valid(g)
    return g


def pts_line(pts):
    return LineString(np.asarray(pts, float))


def spline_pts(pts, h0=None, h1=None, step=0.5):
    d, _ = P.open_spline(pts, h0, h1)
    return M.sample_d(d, step)[0][0], d


def scallops(p_from, p_to, n, sag, bulge_dir, stagger=0.0):
    """``n`` scallop arcs whose cusps sit on the straight row p_from -> p_to,
    each bulging ``sag`` px toward the unit vector ``bulge_dir``. ``stagger``
    (0..1) shifts the cusps by that fraction of the pitch (the row's first
    and last arcs are then clipped by the region). -> list of point arrays."""
    p0, p1 = np.asarray(p_from, float), np.asarray(p_to, float)
    L = float(np.hypot(*(p1 - p0)))
    u = (p1 - p0) / L
    pitch = L / n
    out = []
    for i in range(-1, n + 1):
        a = p0 + u * pitch * (i + stagger)
        b = a + u * pitch
        nl = np.array([u[1], -u[0]])                  # screen-left of travel
        sg = sag if nl @ bulge_dir > 0 else -sag
        d = forms.scallop_arc(a, b, sg)
        out.append(M.sample_d(d, 0.4)[0][0])
    return out


# ---------------------------------------------------------------------------
# the silhouette parts
# ---------------------------------------------------------------------------
def body_shape():
    return shape(P.body_d())


def tail_shape():
    return shape(P.tail_outline_d())


def silhouette(extra=()):
    return shapely.union_all([body_shape(), shape(P.bill_d()), tail_shape(), wing_shape()] + list(extra))


# ---------------------------------------------------------------------------
# the folded wing: painter's stack of feathers (nearest first)
# ---------------------------------------------------------------------------
W = P.WING


class Feather:
    def __init__(self, name, poly, shaft=None):
        self.name, self.poly = name, poly
        self.shaft = None if shaft is None else np.asarray(shaft, float)


def feather_poly(shaft, hw0, hw1=None, tip="round"):
    """A feather along ``shaft`` (base -> tip): a swept circle whose radius
    eases from hw0 to hw1 (a round tip); tip='point' adds a pointed end."""
    hw1 = hw0 if hw1 is None else hw1
    cv = G.Curve(np.asarray(shaft, float))
    L = cv.length
    s = np.linspace(0, L, 40)
    hw = hw0 + (hw1 - hw0) * (s / L)
    Pp = cv.at_s(s)
    circles = [Point(*p).buffer(r, quad_segs=24) for p, r in zip(Pp, hw)]
    parts = [shapely.union_all([a, b]).convex_hull for a, b in zip(circles[:-1], circles[1:])]
    g = shapely.union_all(parts)
    if tip == "point":
        tv = cv.tangent_s(L)
        nv = np.array([-tv[1], tv[0]])
        tipp = Pp[-1] + tv * hw1 * 1.8
        g = g.union(Polygon([Pp[-1] + nv * hw1, tipp, Pp[-1] - nv * hw1]))
    return g


WING_KU = 0.93                      # the feather plan is drawn for a 254 px wing; scaled along u


def _wpts(uv):
    return [W(u * WING_KU, v) for u, v in uv]


def wing_feathers():
    """Flight feathers, nearest first: the tertials (lying along the back),
    the secondaries (their tips stepping down the lower edge) and the
    primaries (projecting past them onto the tail)."""
    fs = []
    # (name, shaft in wing uv, half-width at base, at tip)
    spec = [
        ("tertial-1",   [(60, -22), (120, -19), (172, -5)],  11.5, 10.5),
        ("tertial-2",   [(66, -6), (130, -4), (196, 4)],     11.0, 10.0),
        ("secondary-1", [(60, 10), (110, 13), (160, 15)],    10.5, 9.5),
        ("secondary-2", [(58, 22), (100, 24), (136, 23)],    9.0, 8.5),
        ("primary",     [(110, 4), (190, 5), (244, 6)],      9.8, 7.0),
    ]
    for name, uv, hw0, hw1 in spec:
        sh, _ = spline_pts(_wpts(uv))
        fs.append(Feather(name, feather_poly(sh, hw0, hw1), sh))
    return fs


def coverts_poly():
    """The covert block: from the shoulder round the wrist to a scalloped
    rear edge (the greater coverts' tips) slanting across the wing."""
    fr = _wpts([(14, -34), (-4, -6), (4, 20), (30, 34)])
    d, _ = P.open_spline(fr, W.head(180 - 30), W.head(10))
    front = M.sample_d(d, 0.5)[0][0]
    cusps = _wpts([(70, 34), (78, 12), (84, -10), (88, -34)])
    rear = []
    lower = np.array(_wpts([(30, 34), (50, 35), (70, 34)]))
    for p, q in zip(cusps[:-1], cusps[1:]):
        rear.append(M.sample_d(forms.scallop_arc(p, q, 9.0), 0.5)[0][0])
    top = np.array(_wpts([(88, -34), (50, -40), (14, -34)]))
    ring = np.vstack([front, lower, np.vstack(rear), top])
    coverts_poly.drawn = np.vstack([front, lower, np.vstack(rear)])     # the top edge is hidden
    g = Polygon(ring).buffer(0)
    return g if g.geom_type == "Polygon" else max(g.geoms, key=lambda q: q.area)


def covert_rows():
    """Scale rows inside the covert block (lesser, median), arcs bulging
    toward the wing tip."""
    out = []
    for cusps, sag in [([(26, -40), (30, -18), (32, 4), (34, 26)], 6.0),
                       ([(52, -40), (56, -16), (60, 8), (62, 32)], 7.5)]:
        pts = _wpts(cusps)
        for p, q in zip(pts[:-1], pts[1:]):
            out.append(M.sample_d(forms.scallop_arc(p, q, sag), 0.5)[0][0])
    return out


def wing_shape():
    fs = wing_feathers()
    g = shapely.union_all([f.poly for f in fs] + [coverts_poly()])
    return g if g.geom_type == "Polygon" else max(g.geoms, key=lambda q: q.area)


def breast_lines(region):
    """Scale-arc rows across the lower neck, breast and flank: rows at
    constant body-u (perpendicular to the body axis), arcs bulging toward
    the tail, growing toward the belly. Arcs mostly outside ``region`` are
    dropped; the rest are clipped by it (and butt onto the wing's edge)."""
    B = P.BODY
    tail_dir = -B.U
    lines = []
    u, k = 96.0, 0
    while u > 4.0:
        t = (96.0 - u) / 92.0
        pitch = 16.0 + 5.0 * t
        sag = 5.2 + 1.6 * t
        n = int(120 / pitch) + 2
        a = B(u, -40.0)
        b = B(u, -40.0 + n * pitch)
        for arc in scallops(a, b, n, sag, tail_dir, stagger=0.5 * (k % 2)):
            ln = pts_line(arc)
            if ln.intersection(region).length >= 0.6 * ln.length:
                lines.append(arc)
        u -= 12.5 + 2.5 * t
        k += 1
    return lines


def tail_lines():
    """The rectrix edge between the middle and central feathers (the outer
    feather's edge is drawn by its jade window)."""
    return [P.tail_boundary(k, u0=-6.0) for k in range(2, P.N_RECT)]


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def _lines_of(g):
    """Flatten a (multi)line / collection into LineStrings."""
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "LinearRing":
        return [LineString(g.coords)]
    out = []
    for q in getattr(g, "geoms", []):
        out += _lines_of(q)
    return out


def _snap(ml, reach=KO + 3.1):
    """Close near-miss joins: every free end of a line in ``ml`` that stops
    within ``reach`` px of ANOTHER line is joined to it by a short segment."""
    lines = _lines_of(ml)
    extra = []
    for i, l in enumerate(lines):
        c = np.asarray(l.coords)
        for end, nxt in ((c[0], c[1]), (c[-1], c[-2])):
            e = Point(*end)
            best, bp = reach, None
            for j, o in enumerate(lines):
                if j == i:
                    continue
                d = o.distance(e)
                if 1e-6 < d < best:
                    best = d
                    bp = shapely.ops.nearest_points(o, e)[0]
            if bp is not None:
                extra.append(LineString([end, (bp.x, bp.y)]))
    return shapely.union_all(lines + extra)


def _extended(pts, d):
    """A shaft polyline extended ``d`` px beyond both ends (to split a whole feather)."""
    pts = np.asarray(pts, float)
    a = pts[0] - pts[1]
    b = pts[-1] - pts[-2]
    return np.vstack([pts[0] + a / np.hypot(*a) * d, pts, pts[-1] + b / np.hypot(*b) * d])


def _side(split_pts, side):
    """Half-plane-like region on ``side`` of an extended polyline."""
    return M.split_region(Polygon([(-2000, -2000), (3000, -2000), (3000, 3000), (-2000, 3000)]),
                          np.asarray(split_pts, float), side=side)


RIM_EDGE = 4.6                      # ink rim between a window and the silhouette edge
TAIL_WIN_U0 = 70.0                  # the tail's sheen starts this far down the tail (clear of the wing tip)


def build(extra_solid=()):
    sil = silhouette(extra_solid)
    body = body_shape()
    wing = wing_shape()
    tail = tail_shape()
    inner = sil.buffer(-EDGE)
    back_zone = sil.buffer(-10.0)          # wing lines keep clear of the back (scapulars)

    # ---------------------------------------------------------------- lines
    # every knockout centreline, as LineStrings, before clipping
    wing_lines = []
    cov = coverts_poly()
    stack = [Feather("coverts", cov)] + wing_feathers()
    above = Polygon()
    for f in stack:
        outline = pts_line(coverts_poly.drawn) if f.name == "coverts" else f.poly.exterior
        edge = outline.difference(above.buffer(-0.05))
        wing_lines += _lines_of(edge)
        above = above.union(f.poly)
    rows = shapely.union_all([pts_line(l) for l in covert_rows()]).intersection(cov)
    wing_lines += _lines_of(rows)
    wing_ml = _snap(shapely.union_all(wing_lines).intersection(back_zone))

    breast_region = body.difference(wing).intersection(inner)
    breast_region = breast_region.difference(Point(*P.HEAD(-40.0, 0.0)).buffer(70.0))
    front = Polygon([P.BODY(-400, -2), P.BODY(400, -2), P.BODY(400, 300), P.BODY(-400, 300)])
    breast_region = breast_region.intersection(front)          # the breast, not the mantle
    br_ml = shapely.union_all([pts_line(l) for l in breast_lines(breast_region)]).intersection(breast_region)

    tail_raw = shapely.union_all([pts_line(l) for l in tail_lines()])
    tail_raw = tail_raw.difference(body.buffer(2.0)).difference(wing.buffer(KO / 2 + 3.2))
    tail_ml = tail_raw.intersection(tail.buffer(-(KO / 2 + 3.2)))       # ends >= 3.2 px from the edge
    tail_ml = tail_ml.difference(wing_ml.buffer(KO + 3.2))                # ... and from the wing's lines

    gape_ml = pts_line(M.sample_d(P.gape_d(), 0.4)[0][0])

    # -------------------------------------------------------------- windows
    # one lit feather in each jade tract: the upper tertial, the outer rectrix.
    # Each window is the feather plus the outer half of its own outline, so
    # the hatch butts onto the neighbouring feather's ink; an ink rim keeps it
    # off the silhouette edge.
    fs = {f.name: f for f in wing_feathers()}
    t1 = fs["tertial-1"]
    t1_shaft = _extended(t1.shaft, 40.0)
    wing_win = (M.split_region(t1.poly.buffer(KO / 2, quad_segs=16), t1_shaft, side=1)
                .difference(cov.buffer(-KO / 2, quad_segs=16))
                .intersection(sil.buffer(-RIM_EDGE)))
    r0 = shape(P.rectrix_d(0))
    r0_shaft = np.array([P.TAIL(u, (P.tail_v(0, u) + P.tail_v(1, u)) / 2)
                         for u in np.linspace(-40.0, P.tail_end_u(1) + 30.0, 60)])
    beyond = _side([P.TAIL(TAIL_WIN_U0 - 30.0, -200.0), P.TAIL(TAIL_WIN_U0 - 30.0, 200.0)], -1)
    if beyond.intersection(Point(*P.TAIL(TAIL_WIN_U0 + 50.0, 0.0))).is_empty:
        beyond = _side([P.TAIL(TAIL_WIN_U0 - 30.0, -200.0), P.TAIL(TAIL_WIN_U0 - 30.0, 200.0)], 1)
    # the sheen begins beyond the rounded tip of an upper-tail covert
    vc = (P.tail_v(0, TAIL_WIN_U0) + P.tail_v(1, TAIL_WIN_U0)) / 2
    beyond = beyond.difference(Point(*P.TAIL(TAIL_WIN_U0 - 30.0, vc)).buffer(30.0, quad_segs=32))
    tail_win = (M.split_region(r0.buffer(KO / 2, quad_segs=16), r0_shaft, side=1).intersection(beyond)
                .difference(wing.buffer(KO / 2 + RIM + 6.0))
                .intersection(tail.buffer(-RIM_EDGE)))
    # barbs of a lower vane leave the shaft heading toward the tip: 45 deg off the axis
    windows = [(g, ang) for g, ang in ((wing_win, P.WING.h - 45.0), (tail_win, P.TAIL.h - 45.0))
               if not g.is_empty]
    win_all = shapely.union_all([g for g, _ in windows]) if windows else Polygon()

    # ---------------------------------------------------------------- solid
    ko_ml = shapely.union_all([wing_ml, br_ml, tail_ml, gape_ml])
    ko_out = ko_ml.difference(win_all)                     # paper lines in the solid
    holes = shapely.union_all([ko_out.buffer(KO / 2, quad_segs=8), win_all])
    solid = sil.difference(holes)
    solid = clean(solid, keep=Point(*P.BILL_TIP).buffer(40.0), envelope=sil)

    # --- eye: hole, gold iris ring under the Aquifer pupil
    ex, ey = P.EYE_C
    solid = solid.difference(Point(ex, ey).buffer(P.EYE_R, quad_segs=32))
    gold = M.dot(ex, ey, 2 * (P.EYE_R + TRAP), color=T.FOIL, role="iris")
    ink = M.dot(ex, ey, P.PUPIL_D, color=T.INK, role="pupil")
    jade = M.Frag()
    for g, ang in windows:
        paper = g.difference(solid)                       # what is really open in this window
        jade += jade_hatch(paper, solid, ang)
    return {"solid": solid, "ink": ink, "jade": jade, "gold": gold, "windows": win_all}


def jade_hatch(paper, solid, angle):
    """FINE jade hatch in ``paper`` (tucked TRAP px under the ink at its
    ends). §I.12: a hatch line must either meet an ink piece or keep the
    3 px registration gap from it -- a line grazing an ink corner is left out."""
    lines = M.hatch_lines(paper.buffer(TRAP, quad_segs=8), angle, T.HATCH_PITCH)
    pieces = [g for g in getattr(solid, "geoms", [solid])]
    keep = []
    for c in lines:
        stroke = LineString(c).buffer(T.FINE / 2, cap_style="flat")
        ok = True
        for g in pieces:
            d = g.distance(stroke)
            if 0.0 < d < 3.0:
                ok = False
                break
        if ok:
            keep.append(c)
    return M.stroke(keep, T.FINE, style="hatch", color=T.JADE, role="hatch") if keep else M.Frag()


def clean(solid, keep=None, bridge=3.1, slit=2.6, envelope=None):
    """Spacing hygiene (§I.12): drop ink slivers thinner than ``bridge``
    (where knockout lines meet at shallow angles) and close paper slits
    narrower than ``slit``. ``keep`` protects a zone (the needle bill tip)."""
    r = bridge / 2
    opened = solid.buffer(-r, quad_segs=8).buffer(r, quad_segs=8)
    if keep is not None:
        opened = opened.union(solid.intersection(keep))
    c = slit / 2
    closed = opened.buffer(c, quad_segs=8).buffer(-c, quad_segs=8)
    return closed if envelope is None else closed.intersection(envelope)
