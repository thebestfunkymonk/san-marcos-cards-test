"""JOKER_BLACK plumage (draft 2): feathers as stacked shapes; the knockout
lines are their VISIBLE edges, so every line emerges from under the feather
above it (T-joins, no dangling ends) -- brief §H.18, §I.12, §I.14.
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from inkkit import geom as G
from deck import tokens as T
from deck import motifs as M
from deck.motifs import forms

import _joker_black_pose as P

KO = T.MEDIUM                 # knockout (paper) line width
INSET = 5.2                   # knockout lines keep this much ink inside the silhouette edge


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def shp(d):
    g = G.to_shape(d, tol=0.03)
    if not g.is_valid:
        g = shapely.make_valid(g)
    return g


def dense(d, step=0.4):
    return M.sample_d(d, step)[0][0]


def lines_of(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "LinearRing":
        return [LineString(g.coords)]
    out = []
    for q in getattr(g, "geoms", []):
        out += lines_of(q)
    return out


def polys_of(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    out = []
    for q in getattr(g, "geoms", []):
        out += polys_of(q)
    return out


def scallop_chain(cusps, sag, step=0.4):
    """Dense points of consecutive scallop arcs through ``cusps``, each
    bulging ``sag`` px to the LEFT of travel (negative: right)."""
    out = []
    for i, (p, q) in enumerate(zip(cusps[:-1], cusps[1:])):
        pts = dense(forms.scallop_arc(p, q, sag), step)
        out.append(pts if i == 0 else pts[1:])
    return np.vstack(out)


def cusps_along(p0, p1, pitch, phase=0.0, extend=1):
    """Cusp points on the straight line p0 -> p1 every ``pitch`` px,
    starting ``phase`` px before p0 and running ``extend`` pitches past p1."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    u = (p1 - p0) / L
    s0 = -phase - extend * pitch
    n = int(np.ceil((L - s0) / pitch)) + extend
    return [p0 + u * (s0 + k * pitch) for k in range(n + 1)]


def side_poly(chain, toward, big=900.0):
    """Polygon of the half-plane-ish region on one side of an open chain:
    the chain closed by a far loop displaced by ``toward`` (unit vector)."""
    chain = np.asarray(chain, float)
    t = np.asarray(toward, float)
    a, b = chain[0], chain[-1]
    ta = chain[0] - chain[1]
    ta /= np.hypot(*ta)
    tb = chain[-1] - chain[-2]
    tb /= np.hypot(*tb)
    ring = np.vstack([a + ta * big, chain, b + tb * big, b + tb * big + t * big, a + ta * big + t * big])
    return Polygon(ring).buffer(0)


# ---------------------------------------------------------------------------
# the feather stack
# ---------------------------------------------------------------------------
class Feather:
    def __init__(self, name, poly, z, jade=None):
        self.name, self.poly, self.z = name, poly, z
        self.jade = jade            # optional (window polygon, hatch angle)


def visible_edges(stack, inner):
    """Visible part of each feather's outline: minus every feather above it,
    inside ``inner``. Returns a list of LineStrings."""
    out = []
    ordered = sorted(stack, key=lambda f: f.z)
    for i, f in enumerate(ordered):
        above = [g.poly for g in ordered[i + 1:]]
        edge = f.poly.boundary
        if above:
            edge = edge.difference(shapely.union_all(above).buffer(0.05))
        edge = edge.intersection(inner)
        out += lines_of(edge)
    return out


# ---------------------------------------------------------------------------
# anatomy -> stack
# ---------------------------------------------------------------------------
def covert_polys(wing_all):
    """Covert rows as regions on the wrist side of their scalloped tip lines."""
    out = []
    Uw = P.WG.U
    for name, a, b, pitch, sag, z in P.COVERT_ROWS:
        p0, p1 = P.WG(*a), P.WG(*b)
        cz = cusps_along(p0, p1, pitch, phase=pitch * 0.5, extend=1)
        chain = scallop_chain(cz, sag)
        reg = side_poly(chain, -Uw).intersection(wing_all)
        out.append((f"covert-{name}", reg, z, chain))
    return out


def anatomy():
    body = shp(P.body_d())
    bill = shp(P.bill_d())
    tfs = P.tail_feathers()
    tail = shapely.union_all([p for _, p, _ in tfs])
    core = shapely.union_all([body, bill, tail])
    wing_all = P.wing_outline_poly()
    core = core.union(wing_all)
    stack = [Feather(n, p, z) for n, p, z in tfs]
    stack.append(Feather("body", body, 5))
    stack.append(Feather("wing", wing_all, 9))
    for n, p, z in P.wing_feathers():
        stack.append(Feather(n, p.intersection(wing_all), z))
    chain = scallop_chain(P.lesser_chain(), P.LESSER["sag"])
    L = P.wing_loft()
    toward = L(0.0, 0.5) - L(0.3, 0.5)
    toward = toward / np.hypot(*toward)
    lesser = side_poly(chain, toward).intersection(wing_all)
    stack.append(Feather("lesser", lesser, P.LESSER["z"]))
    bill_f = Feather("bill", bill, 99)
    bill_f.draw = False
    stack.append(bill_f)
    return {"body": body, "bill": bill, "tail": tail, "core": core, "wing": wing_all,
            "stack": stack, "lesser": lesser}


def visible_lines(stack, inner):
    out = []
    ordered = sorted(stack, key=lambda f: f.z)
    for i, f in enumerate(ordered):
        if getattr(f, "draw", True) is False:
            continue
        above = [g.poly for g in ordered[i + 1:]]
        edge = f.poly.boundary
        if above:
            edge = edge.difference(shapely.union_all(above).buffer(0.05))
        out += lines_of(edge.intersection(inner))
    return out


# ---------------------------------------------------------------------------
# jade windows (alternate tracts, half-hatched: the lesser coverts on the
# shoulder, the far vane of the tail -- the inside of its V)
# ---------------------------------------------------------------------------
BREAST = False                # breast scale rows (tried: the strip is too narrow -- they read as worms)
RIM = 4.6                     # ink rim kept between a window and the silhouette edge
TRAP = 0.9                    # jade tucks this far under the ink
HATCH_ANGLE = 45.0            # screen degrees ("\\")


def tail_far_window(A):
    L = P.tail_loft()
    fv = [f for f in A["stack"] if f.name == "tail-far"][0].poly
    near = shapely.union_all([f.poly for f in A["stack"] if f.name.startswith("tail-n")])
    win = fv.difference(near).difference(A["wing"]).difference(A["body"])
    return win


import os as _os
JADE_SET = _os.environ.get("JB_JADE", "lesser,tail-far").split(",")


def visible_region(A, name):
    """The part of feather ``name`` not covered by any feather above it."""
    st = sorted(A["stack"], key=lambda f: f.z)
    i = [f.name for f in st].index(name)
    above = [f.poly for f in st[i + 1:] if getattr(f, "draw", True) is not False or f.name == "bill"]
    g = st[i].poly
    return g.difference(shapely.union_all(above)) if above else g


def windows(A):
    out = []
    for nm in JADE_SET:
        if nm == "lesser":
            out.append(("lesser", A["lesser"], HATCH_ANGLE))
        elif nm == "tail-far":
            out.append(("tail-far", tail_far_window(A), HATCH_ANGLE))
        elif nm == "greater":
            g = shapely.union_all([visible_region(A, f.name) for f in A["stack"] if f.name.startswith("covert-g")])
            out.append(("greater", g, HATCH_ANGLE))
        else:
            out.append((nm, visible_region(A, nm), HATCH_ANGLE))
    return out


def clean(solid, keep=None, bridge=3.1, slit=2.6, envelope=None):
    """Spacing hygiene (§I.12): drop ink slivers thinner than ``bridge`` and
    close paper slits narrower than ``slit``; ``keep`` protects a zone."""
    r = bridge / 2
    opened = solid.buffer(-r, quad_segs=8).buffer(r, quad_segs=8)
    if keep is not None:
        opened = opened.union(solid.intersection(keep))
    c = slit / 2
    closed = opened.buffer(c, quad_segs=8).buffer(-c, quad_segs=8)
    return closed if envelope is None else closed.intersection(envelope)


def jade_hatch(paper, solid, angle):
    """FINE jade hatch in ``paper`` (tucked TRAP under the ink). A line that
    would graze an ink corner (< 3 px, registration) is left out."""
    lines = M.hatch_lines(paper.buffer(TRAP, quad_segs=8), angle, T.HATCH_PITCH)
    pieces = list(getattr(solid, "geoms", [solid]))
    keep = []
    for c in lines:
        st = LineString(c).buffer(T.FINE / 2, cap_style="flat")
        if all(not (0.0 < g.distance(st) < 3.0) for g in pieces):
            keep.append(c)
    return M.stroke(keep, T.FINE, style="hatch", color=T.JADE, role="hatch") if keep else M.Frag()


def build(extra_solid=()):
    A = anatomy()
    sil = shapely.union_all([A["core"]] + list(extra_solid))
    inner = sil.buffer(-INSET)
    lines = visible_lines(A["stack"], inner)
    lines.append(LineString(dense(P.gape_d())))
    # breast scale rows: only on the breast (not the wing), inside the rim
    breast = A["body"].difference(A["wing"].buffer(KO / 2 + 0.2)).intersection(inner)
    for cz, sg in (P.breast_rows() if BREAST else []):
        ch = LineString(scallop_chain(cz, sg))
        lines += lines_of(ch.intersection(breast))
    ko = shapely.union_all(lines)
    wins = windows(A)
    rim_in = sil.buffer(-RIM)
    win_geoms = []
    for name, g, ang in wins:
        g = g.buffer(KO / 2, quad_segs=8).intersection(rim_in)
        win_geoms.append((name, g, ang))
    win_all = shapely.union_all([g for _, g, _ in win_geoms])
    holes = shapely.union_all([ko.buffer(KO / 2, quad_segs=8), win_all])
    solid = sil.difference(holes)
    # ink scale rows inside the lesser window
    if "lesser" in JADE_SET:
        rows = [LineString(scallop_chain(c, sg)) for c, sg in P.lesser_rows()]
        rl = shapely.union_all(rows).buffer(KO / 2, quad_segs=8).intersection(
            [g for n, g, _ in win_geoms if n == "lesser"][0].buffer(0.6))
        solid = solid.union(rl)
    keep = shapely.union_all([Point(*P.BILL_TIP).buffer(40.0)] +
                             [g.difference(A["body"].buffer(2.0)) for g in extra_solid])
    solid = clean(solid, keep=keep, envelope=sil)
    ex, ey = P.EYE_C
    solid = solid.difference(Point(ex, ey).buffer(P.EYE_R, quad_segs=32))
    gold = M.dot(ex, ey, 2 * (P.EYE_R + TRAP), color=T.FOIL, role="iris")
    ink = M.dot(ex, ey, P.PUPIL_D, color=T.INK, role="pupil")
    jade = M.Frag()
    for name, g, ang in win_geoms:
        jade += jade_hatch(g.difference(solid), solid, ang)
    return {"solid": solid, "ink": ink, "jade": jade, "gold": gold, "windows": win_all, "A": A, "sil": sil}
