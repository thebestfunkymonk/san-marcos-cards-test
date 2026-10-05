"""JOKER_BLACK plumage: the Aquifer silhouette, its geometric knockouts and
the jade half-hatched feather tracts (brief §H.18; contract §2.1, §5).

Model
-----
* The bird is ONE Aquifer solid: head, neck, body, wing, bill, tail, legs
  and feet (§C rule 3: solid Aquifer is allowed on the grackle body).
* Feathering is knocked out of it as MEDIUM (3.1) paper lines (§B.2
  knockout lines in solids; QA §I.12: holes >= 2.5 px, bridges >= 3 px):
    - the covert block of the folded wing: its front edge round the wrist,
      two scale rows (lesser, median) and the greater coverts' scalloped tips;
    - the flight feathers as graduated bands between boundary curves (the
      same construction as the tail): each feather ends in a round tip, the
      tips stepping from the tertials down to the primaries' point on the
      lower edge; inner feather edges show only toward the tips, as a folded
      wing is drawn, so the wing never reads as a stack of planks;
    - scale-arc rows across the breast and belly (rows at constant body-u,
      arcs bulging toward the tail and growing toward the belly), springing
      from the wing's edge line as the breast feathers tuck under the wing;
    - the rectrix edges of the graduated, V-keeled tail; the gape.
* Jade (iridescence): ALTERNATE feather tracts are half-hatched -- the
  covert tract (split by its first scale row: the lesser-covert half, the
  shoulder, where a grackle's gloss is brightest), the flight feathers left
  black, the tail again half-hatched (the outer vane of the outer and the
  central rectrix). Each hatched half is a window in the solid holding FINE
  jade hatch at the 7.0 pitch; jade prints BELOW the ink, so it only ever
  lives in holes of the solid (§2.1). An ink rim keeps every window off the
  silhouette edge.
* The eye is a hole holding a gold iris ring under the Aquifer pupil.
* Hygiene: every knockout end either joins its neighbour or clears it
  (snap), ink slivers < 3.1 px and paper slits < 2.6 px are removed (the
  bill tip and the claws are protected), hatch lines that would graze an ink
  corner (< 3 px registration) are left out.
"""
from __future__ import annotations

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
EDGE = 5.0                          # knockout lines keep this much ink inside the silhouette edge
RIM_EDGE = 4.6                      # ink rim between a jade window and the silhouette edge
TRAP = 0.9                          # jade tucks this far under the ink (print trap)
W = P.WING


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


def dense(d, step=0.4):
    return M.sample_d(d, step)[0][0]


def spline_pts(pts, h0=None, h1=None, step=0.5):
    d, _ = P.open_spline(pts, h0, h1)
    return dense(d, step), d


def wpts(uv):
    return [W(u, v) for u, v in uv]


def largest(g):
    return g if g.geom_type == "Polygon" else max(g.geoms, key=lambda q: q.area)


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
# the folded wing
# ---------------------------------------------------------------------------
class Feather:
    def __init__(self, name, poly, shaft=None, drawn=None):
        self.name, self.poly = name, poly
        self.shaft = None if shaft is None else np.asarray(shaft, float)
        self.drawn = drawn                      # the part of the outline that can show


def coverts_poly():
    """The covert block: from the shoulder round the wrist, along the lower
    edge, to the scalloped rear edge (the greater coverts' tips) slanting
    back across the wing; its top edge is hidden under the back."""
    front, _ = spline_pts(wpts([(10, -46), (-3, -24), (-2, -2), (14, 14), (36, 20)]),
                          W.head(180 - 28), W.head(-4))
    cusps = wpts([(64, 20), (76, 2), (86, -16), (94, -34), (100, -52)])
    rear = [np.asarray(W(40, 20.5))]
    rear += [dense(forms.scallop_arc(p, q, -7.5), 0.5) for p, q in zip(cusps[:-1], cusps[1:])]
    lower = np.array(wpts([(36, 20), (50, 21), (64, 20)]))
    top = np.array(wpts([(100, -52), (60, -62), (10, -58), (10, -46)]))
    rear_pts = np.vstack([p if np.ndim(p) == 2 else p[None] for p in rear[1:]])
    ring = np.vstack([front, lower, rear_pts, top])
    drawn = np.vstack([front, lower, rear_pts])
    return largest(Polygon(ring).buffer(0)), drawn


def covert_rows():
    """Scale rows inside the covert block (lesser, median), arcs bulging
    toward the wing tip (-sag: right of travel from the lower edge up)."""
    out = []
    for cusps, sag in [([(20, 18), (26, 0), (32, -18), (38, -36), (44, -54)], -5.6),
                       ([(42, 20), (50, 1), (58, -18), (66, -37), (72, -56)], -6.6)]:
        pts = wpts(cusps)
        for p, q in zip(pts[:-1], pts[1:]):
            out.append(dense(forms.scallop_arc(p, q, sag), 0.4))
    return out


# Flight feathers as graduated bands between boundary curves (wing-uv),
# like the tail: boundary k runs from under the coverts toward the tip;
# feather i lies between boundaries i and i+1 and ends in a round tip at
# u = WING_TIPS[i]. The tips step out to the primaries' point and back.
WING_B = [
    [(56, -52), (104, -50), (140, -46)],          # 0 top edge (under the back)
    [(58, -36), (116, -34), (162, -29)],          # 1
    [(60, -20), (124, -18), (186, -12)],          # 2
    [(61, -5), (130, -2), (208, 2)],              # 3
    [(60, 9), (130, 12), (228, 12)],              # 4
    [(40, 20.5), (110, 23), (228, 26)],           # 5 lower edge
]
WING_TIPS = [140.0, 162.0, 186.0, 208.0, 228.0]
WING_TIP_SAG = 6.0
WING_EDGE_SHOW = 58.0             # inner feather edges show this far back from the shorter tip
_WB = {}


def wing_boundary_pts(k):
    """Dense points of boundary k (extended 30 px past its last station) and
    their wing-u."""
    if k not in _WB:
        uv = WING_B[k]
        (u1, v1), (u2, v2) = uv[-2], uv[-1]
        du, dv = u2 - u1, v2 - v1
        n = np.hypot(du, dv)
        ext = (u2 + du / n * 30.0, v2 + dv / n * 30.0)
        (a1, b1), (a2, b2) = uv[0], uv[1]
        n0 = np.hypot(a2 - a1, b2 - b1)
        pre = (a1 - (a2 - a1) / n0 * 30.0, b1 - (b2 - b1) / n0 * 30.0)
        pts, _ = spline_pts(wpts([pre] + list(uv) + [ext]))
        _WB[k] = (pts, np.array([W.local(p)[0] for p in pts]))
    return _WB[k]


def wing_boundary(k, u0, u1):
    pts, us = wing_boundary_pts(k)
    m = (us >= u0) & (us <= u1)
    ends = [np.array([np.interp(x, us, pts[:, 0]), np.interp(x, us, pts[:, 1])]) for x in (u0, u1)]
    out = np.vstack([ends[0], pts[m], ends[1]])
    keep = np.r_[True, np.hypot(*np.diff(out, axis=0).T) > 1e-6]
    return out[keep]


def _wtip(p, q):
    ch = q - p
    left = np.array([ch[1], -ch[0]])
    sg = WING_TIP_SAG if left @ W.U > 0 else -WING_TIP_SAG
    return dense(forms.scallop_arc(p, q, sg), 0.4)


def wing_feather(i, u0=20.0):
    """Closed outline of flight feather i (a polygon)."""
    ue = WING_TIPS[i]
    a = wing_boundary(i, u0, ue)
    b = wing_boundary(i + 1, u0, ue)
    ring = np.vstack([a, _wtip(a[-1], b[-1])[1:-1], b[::-1]])
    return largest(Polygon(ring).buffer(0))


def wing_lines_raw():
    """Visible flight-feather lines: each inner boundary up to the longer of
    its two feathers' tips, the outer boundaries up to their feather's tip,
    and every tip arc."""
    out = []
    n = len(WING_TIPS)
    for k in range(n + 1):
        if k == 0:
            u0, ue = 20.0, WING_TIPS[0]
        elif k == n:
            u0, ue = 20.0, WING_TIPS[-1]
        else:
            ue = max(WING_TIPS[k - 1], WING_TIPS[k])
            u0 = min(WING_TIPS[k - 1], WING_TIPS[k]) - WING_EDGE_SHOW
        out.append(wing_boundary(k, u0, ue))
    for i, ue in enumerate(WING_TIPS):
        out.append(_wtip(wing_boundary(i, 20.0, ue)[-1], wing_boundary(i + 1, 20.0, ue)[-1]))
    return out


def wing_feathers():
    fs = []
    names = ["tertial-1", "tertial-2", "secondary", "primary-2", "primary-1"]
    for i, name in enumerate(names):
        poly = wing_feather(i)
        ue = WING_TIPS[i]
        uu = np.linspace(20.0, ue + 20.0, 80)
        pa, ua = wing_boundary_pts(i)
        pb, ub = wing_boundary_pts(i + 1)
        A = np.column_stack([np.interp(uu, ua, pa[:, 0]), np.interp(uu, ua, pa[:, 1])])
        B = np.column_stack([np.interp(uu, ub, pb[:, 0]), np.interp(uu, ub, pb[:, 1])])
        sh = (A + B) / 2
        sh = sh[np.r_[True, np.hypot(*np.diff(sh, axis=0).T) > 1e-6]]
        fs.append(Feather(name, poly, sh))
    return fs


def wing_shape():
    fs = wing_feathers()
    cov, _ = coverts_poly()
    g = shapely.union_all([f.poly for f in fs] + [cov])
    # the wing never changes the silhouette: it lies on the body and tail
    return largest(g.intersection(shapely.union_all([body_shape(), tail_shape()])))


# ---------------------------------------------------------------------------
# breast / belly scale arcs
# ---------------------------------------------------------------------------
def scallops(p_from, p_to, n, sag, bulge_dir, stagger=0.0):
    """``n`` scallop arcs whose cusps sit on the straight row p_from -> p_to,
    each bulging ``sag`` px toward the unit vector ``bulge_dir``; ``stagger``
    (0..1) shifts the cusps by that fraction of the pitch."""
    p0, p1 = np.asarray(p_from, float), np.asarray(p_to, float)
    L = float(np.hypot(*(p1 - p0)))
    u = (p1 - p0) / L
    pitch = L / n
    out = []
    for i in range(-1, n + 1):
        a = p0 + u * pitch * (i + stagger)
        b = a + u * pitch
        nl = np.array([u[1], -u[0]])
        sg = sag if nl @ bulge_dir > 0 else -sag
        out.append(dense(forms.scallop_arc(a, b, sg), 0.4))
    return out


def breast_lines(region):
    """Scale-arc rows across the breast and belly: rows at constant body-u,
    arcs bulging toward the tail, growing toward the belly. Arcs mostly
    outside ``region`` are dropped; the rest are clipped by it."""
    B = P.BODY
    tail_dir = -B.U
    lines = []
    u0, u1 = BREAST_U0, -74.0
    u, k = u0, 0
    while u > u1:
        t = (u0 - u) / (u0 - u1)
        pitch = BREAST_PITCH[0] + (BREAST_PITCH[1] - BREAST_PITCH[0]) * t
        sag = BREAST_SAG[0] + (BREAST_SAG[1] - BREAST_SAG[0]) * t
        n = int(140 / pitch) + 2
        a = B(u, -30.0)
        b = B(u, -30.0 + n * pitch)
        for arc in scallops(a, b, n, sag, tail_dir, stagger=0.5 * (k % 2)):
            ln = pts_line(arc)
            if ln.intersection(region).length >= 0.6 * ln.length:
                lines.append(arc)
        u -= BREAST_STEP[0] + (BREAST_STEP[1] - BREAST_STEP[0]) * t
        k += 1
    return lines


BREAST_U0 = 78.0
BREAST_PITCH = (17.0, 23.0)
BREAST_SAG = (5.4, 7.2)
BREAST_STEP = (13.5, 17.5)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def _snap(ml, reach=KO + 3.1):
    """Close near-miss joins: a free end of a line stopping within ``reach``
    px of ANOTHER line is joined to it by a short segment."""
    lines = _lines_of(ml)
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
                    best = d
                    bp = shapely.ops.nearest_points(o, e)[0]
            if bp is not None:
                extra.append(LineString([end, (bp.x, bp.y)]))
    return shapely.union_all(lines + extra)


def _extended(pts, d):
    """A shaft polyline extended ``d`` px beyond both ends."""
    pts = np.asarray(pts, float)
    a = pts[0] - pts[1]
    b = pts[-1] - pts[-2]
    return np.vstack([pts[0] + a / np.hypot(*a) * d, pts, pts[-1] + b / np.hypot(*b) * d])


def _rectrix_shaft(i, u0=-40.0, u1=None, ext=30.0):
    u1 = (P.tail_end_u(i + 1) if u1 is None else u1) + ext
    return np.array([P.TAIL(u, (P.tail_v(i, u) + P.tail_v(i + 1, u)) / 2)
                     for u in np.linspace(u0, u1, 80)])


COVERT_SIDE = -1                   # the lesser-covert (wrist) side of the first scale row
RECT_VANE = {0: 1, 1: 1, 2: -1}    # which vane of each rectrix is the jade window (the outer one)
COVERT_HATCH = 90.0 + 45.0


def build(extra_solid=(), jade_tracts=("coverts", "rect-0", "rect-2")):
    sil = silhouette(extra_solid)
    body = body_shape()
    wing = wing_shape()
    tail = tail_shape()
    inner = sil.buffer(-EDGE)

    # ---------------------------------------------------------------- wing
    cov, cov_drawn = coverts_poly()
    wing_lines = _lines_of(pts_line(cov_drawn))
    flight = shapely.union_all([pts_line(l) for l in wing_lines_raw()]).difference(cov.buffer(-0.05))
    wing_lines += _lines_of(flight)
    rows = shapely.union_all([pts_line(l) for l in covert_rows()]).intersection(cov)
    wing_lines += _lines_of(rows)
    wing_ml = _snap(shapely.union_all(wing_lines).intersection(inner))

    # -------------------------------------------------------------- breast
    breast_region = body.difference(wing).intersection(inner)      # rows spring from the wing's edge line
    neck_cut = Polygon([P.BODY(92, -300), P.BODY(92, 300), P.BODY(400, 300), P.BODY(400, -300)])
    breast_region = breast_region.difference(neck_cut)
    front_half = Polygon([P.BODY(-400, -16), P.BODY(400, -16), P.BODY(400, 300), P.BODY(-400, 300)])
    breast_region = breast_region.intersection(front_half)          # the breast, not the mantle
    br_ml = shapely.union_all([pts_line(l) for l in breast_lines(breast_region)]).intersection(breast_region)

    # ---------------------------------------------------------------- tail
    tail_raw = shapely.union_all([pts_line(P.tail_boundary(k, u0=-10.0)) for k in range(1, P.N_RECT)])
    tail_raw = tail_raw.difference(body.buffer(2.0)).difference(wing.buffer(KO / 2 + 3.2))
    tail_ml = tail_raw.intersection(tail.buffer(-(KO / 2 + 3.2)))

    gape_ml = pts_line(dense(P.gape_d()))

    # -------------------------------------------------------------- windows
    fs = {f.name: f for f in wing_feathers()}
    windows = []
    for name in jade_tracts:
        if name == "coverts":
            # the covert tract split by its first scale row: the lesser
            # coverts (wrist side) are the hatched half
            row1 = np.vstack(covert_rows()[:4])
            win = (M.split_region(cov.buffer(KO / 2, quad_segs=16), row1, side=COVERT_SIDE)
                   .intersection(sil.buffer(-RIM_EDGE)))
            ang = W.h + COVERT_HATCH
        elif name.startswith("rect-"):
            i = int(name.split("-")[1])
            r = shape(P.rectrix_d(i))
            sh = _rectrix_shaft(i)
            side = RECT_VANE[i]
            win = (M.split_region(r.buffer(KO / 2, quad_segs=16), sh, side=side)
                   .difference(body.buffer(KO / 2 + 3.0))
                   .difference(wing.buffer(KO / 2 + 3.4))
                   .intersection(tail.buffer(-RIM_EDGE)))
            ang = P.TAIL.h + (45.0 if side > 0 else -45.0)
        else:
            f = fs[name]
            nearer = cov
            i = [g.name for g in wing_feathers()].index(name)
            u_from = WING_TIPS[i] - WING_EDGE_SHOW - 6.0
            beyond = Polygon([W(u_from, -300), W(u_from + 400, -300), W(u_from + 400, 300), W(u_from, 300)])
            win = (M.split_region(f.poly.buffer(KO / 2, quad_segs=16), _extended(f.shaft, 40.0), side=1)
                   .intersection(beyond)
                   .difference(nearer.buffer(KO / 2, quad_segs=16))
                   .intersection(sil.buffer(-RIM_EDGE)))
            ang = W.h - 45.0
        if not win.is_empty:
            windows.append((win, ang))
    win_all = shapely.union_all([g for g, _ in windows]) if windows else Polygon()

    # ---------------------------------------------------------------- solid
    ko_ml = _snap(shapely.union_all([wing_ml, br_ml, tail_ml]))       # every end joins or clears (§I.12)
    ko_ml = shapely.union_all([ko_ml, gape_ml])
    ko_out = ko_ml.difference(win_all)
    holes = shapely.union_all([ko_out.buffer(KO / 2, quad_segs=8), win_all])
    solid = sil.difference(holes)
    keep = shapely.union_all([Point(*P.BILL_TIP).buffer(40.0)] + [g.difference(body.buffer(2.0)) for g in extra_solid])
    solid = clean(solid, keep=keep, envelope=sil)

    # --- eye: hole, gold iris ring under the Aquifer pupil
    ex, ey = P.EYE_C
    solid = solid.difference(Point(ex, ey).buffer(P.EYE_R, quad_segs=32))
    gold = M.dot(ex, ey, 2 * (P.EYE_R + TRAP), color=T.FOIL, role="iris")
    ink = M.dot(ex, ey, P.PUPIL_D, color=T.INK, role="pupil")
    jade = M.Frag()
    for g, ang in windows:
        paper = g.difference(solid)
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
