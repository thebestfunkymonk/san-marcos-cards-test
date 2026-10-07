"""Q♣ whole-card textiles: the red-lined jade cloak, the leaf gown and the laced front.

Everything is point-symmetric about the card centre (375, 525): each outline is a top half with a
vertical tangent on the centre line, united with its mirror and its 180° copy, and every pattern is
drawn once on a lattice that is its own 180° copy (leaf centres on a half-drop grid through the card
centre, rows paired y ↔ 1050 − y), so the 180° copy continues the top half without a visible join.

    cloak     red lining with knocked-out streaming grain, a jade turned-back edge with a paper bead row
    gown      jade, a hatched border, a FINE seam and §G.4 ribbon leaves packed whole, streaming with
              the current (a C2 greedy packing: every leaf has its 180° twin)
    lacing    the gold reed ladder and its red opening, from one figure's neckline to the other's
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon
from shapely.prepared import prep

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms as FM
from deck.motifs import rice as MR
from inkkit import geom as G

P, R, U = K.P, K.R, K.U
AX, CY = K.AX, 525.0
FINE, MEDIUM, CONTOUR = T.FINE, T.MEDIUM, T.CONTOUR

# ---- outlines: top half down to the centre, then C2 ----------------------------------------
CLOAK = dict(neck=(375.0, 264.0), top=(322.0, 270.0), shoulder=(168.0, 286.0), side_x=148.0, corner_r=50.0)
GOWN = dict(neck_c=(375.0, 332.0), neck=(338.0, 300.0), neck_sag=-9.0, shoulder=(226.0, 338.0),
            shoulder_sag=5.0, corner_r=34.0, side_x=200.0)
EDGE = 18.0                  # the cloak's jade turned-back edge
BEAD = dict(d=6.3, pitch=15.0)
GOWN_BORDER = 24.0
STREAM = dict(heading=50.0, ratio=9.0, bend=(12.0, -12.0), gap=7.0, grid=2.0, min_w=13.8,
              lengths=(125.0, 110.0, 100.0, 88.0, 76.0))
DRIFT = dict(heading=50.0, length=22.0, width=5.4, along=30.0, across=13.0)
LANE = dict(lengths=(110.0, 96.0, 84.0, 70.0), w=11.4, tip_gap=14.0)
SOFT_CLEAR = 8.0
DOTS = dict(d=4.4, px=20.0, py=22.0, clear=6.5)
LACE = dict(top=352.0, hw=(21.0, 15.0), rail=7.5, rung=7.0, pitch=24.0, node_every=4, node_over=4.0, node_h=10.0)


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def _u(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def _pts(d, step=0.5):
    return np.asarray(C.sample_d(d, step)[0][0], float)


def c2_frag(f: C.Frag) -> C.Frag:
    r = K.rot180(f)
    marks = [replace(m, role=m.role + "~") if "@" in m.role else m for m in r.marks]
    return f + C.Frag(marks, r.meta)


def drop_short(f: C.Frag, min_len: float = 9.0) -> C.Frag:
    """Remove stroke pieces shorter than ``min_len`` (the stubs a hatch leaves in a pocket)."""
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d:
            out.append(m)
            continue
        d = "".join(C.polyline_d(pts, closed=cl) for pts, cl in G.flatten(m.d, 0.05)
                    if G.Curve(np.asarray(pts), closed=cl).length >= min_len)
        if d:
            out.append(replace(m, d=d))
    return C.Frag(out, f.meta)


def seam_guard(f: C.Frag, seam, margin: float = 4.8) -> C.Frag:
    """Drop stroke pieces with an end within ``margin`` of the seam (the half's clip would cut them
    a hair short of their junction and leave a stub the other half has to finish)."""
    if seam is None:
        return f
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d:
            out.append(m)
            continue
        keep = []
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts)
            if not cl and (Point(*pts[0]).distance(seam) < margin or Point(*pts[-1]).distance(seam) < margin):
                continue
            keep.append(C.polyline_d(pts, closed=cl))
        if keep:
            out.append(replace(m, d="".join(keep)))
    return C.Frag(out, f.meta)


def _whole(half):
    top = U(half, K.mirror(half, AX))
    return top, U(top, rot(top))


def _half_barrel(edge_pts, join_dir, side_x, k0=0.28, k1=0.34):
    """Left half from the axis at the top, along ``edge_pts`` to the corner, then a cubic that falls
    to a vertical tangent on the centre line (side_x, 525) and closes along the axis."""
    p0 = edge_pts[-1]
    d0 = np.asarray(join_dir, float)
    d0 = d0 / np.hypot(*d0)
    p3 = np.array([side_x, CY])
    span = CY - p0[1]
    c1, c2 = p0 + d0 * span * k0, p3 - np.array([0.0, 1.0]) * span * k1
    t = np.linspace(0.0, 1.0, 80)[1:, None]
    cub = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p3
    return Polygon(np.vstack([edge_pts, cub, [[AX, CY]]])).buffer(0)


def cloak_shape():
    """The whole-card cloak: a barrel, rounded shoulders, widest on the centre line."""
    c = CLOAK
    d = K.Path(P(*c["neck"])).sag(P(*c["top"]), -2.0).sag(P(*c["shoulder"]), 6.0).d
    half = _half_barrel(_pts(d), (-24.0, 274.0), c["side_x"])
    _, whole = _whole(half)
    r = c["corner_r"]
    rounded = whole.buffer(-r, join_style=1).buffer(r, join_style=1)
    return U(rounded, whole.intersection(K.box(c["top"][0] - 10, 0, 2 * AX - c["top"][0] + 10, 2000))).buffer(0)


def gown_outline():
    """The whole-card gown and the left half of its top edge (centre front → shoulder)."""
    g = GOWN
    N, S0, Sh = P(*g["neck_c"]), P(*g["neck"]), P(*g["shoulder"])
    d = K.Path(N).sag(S0, g["neck_sag"]).sag(Sh, g["shoulder_sag"]).d
    edge = _pts(d)
    half = _half_barrel(edge, (-26.0, 222.0), g["side_x"])
    _, whole = _whole(half)
    r = g["corner_r"]
    rounded = whole.buffer(-r, join_style=1).buffer(r, join_style=1)
    keep = whole.intersection(K.box(S0[0] - 30, 0, 2 * AX - S0[0] + 30, S0[1] + 60))
    shape = U(rounded, keep).buffer(0)
    top = np.vstack([_pts(K.arc_sag(N, S0, g["neck_sag"])), _pts(K.arc_sag(S0, Sh, g["shoulder_sag"]))[1:]])
    return shape, top


def lacing(*, top=None, hw=None, rail=None, rung=None, pitch=None, node_every=None, node_over=None,
           node_h=None):
    """The laced front as one C2 ladder from ``top`` down to 1050 − ``top``: the opening (red) and the
    gold rails and rungs. The opening narrows to the waist and widens again; rungs sit on rows
    y = 525 + k pitch, a reed node on every ``node_every``-th. → (opening, ladder) regions."""
    p = {**LACE, **{k: v for k, v in dict(top=top, hw=hw, rail=rail, rung=rung, pitch=pitch,
                                          node_every=node_every, node_over=node_over, node_h=node_h).items()
                    if v is not None}}
    top_, hw_, rail_ = p["top"], p["hw"], p["rail"]
    bot = 2 * CY - top_
    ys = np.linspace(top_, bot, 120)

    def hwy(y):
        return hw_[1] + (hw_[0] - hw_[1]) * ((np.asarray(y, float) - CY) / (CY - top_)) ** 2

    strip = Polygon(np.vstack([np.column_stack([AX - hwy(ys), ys]), np.column_stack([AX + hwy(ys), ys])[::-1]]))
    inner = Polygon(np.vstack([np.column_stack([AX - hwy(ys) + rail_, ys]),
                               np.column_stack([AX + hwy(ys) - rail_, ys])[::-1]]))
    rails = strip.difference(inner)
    bars = []
    n = int((CY - top_) // p["pitch"]) + 1
    # rows sit half a pitch off the centre line, so no rung lies on the seam's pivot; m counts
    # rows outward from the centre (rows y and 1050 − y share m)
    for j in range(-n, n):
        y = CY + (j + 0.5) * p["pitch"]
        m = j if j >= 0 else -1 - j
        if y < top_ + 6.0 or y > bot - 6.0:
            continue
        w_ = float(hwy(y))
        if p["node_every"] and m % p["node_every"] == 2:
            bars.append(R(K.rrect(AX - w_ - p["node_over"], y - p["node_h"] / 2, AX + w_ + p["node_over"],
                                  y + p["node_h"] / 2, p["node_h"] / 2 - 0.5)))
        else:
            bars.append(K.box(AX - w_, y - p["rung"] / 2, AX + w_, y + p["rung"] / 2))
    ladder = U(rails, *bars).buffer(0.01).buffer(-0.01)
    return strip, ladder


# ---- ribbon leaves, packed C2 -----------------------------------------------------------------
def leaf_poly(base, heading, length, width, bend):
    _, mid, _ = FM.arc_path(base[0], base[1], heading, [(length / 2, bend[0]), (length / 2, bend[1])])
    hw = FM.vesica_hw(length, width)
    _, _, ol = FM.leaf_edges(np.asarray(mid, float), hw, step=1.5)
    return Polygon(ol).buffer(0)


def _spikes(base, heading, length, bend, reach=5.6):
    """The ends of a ribbon leaf's two miter tips (centreline tip + ``reach`` along the end tangents)."""
    _, mid, _ = FM.arc_path(base[0], base[1], heading, [(length / 2, bend[0]), (length / 2, bend[1])])
    mid = np.asarray(mid, float)
    out = []
    for a, b in ((mid[0], mid[min(3, len(mid) - 1)]), (mid[-1], mid[max(-4, -len(mid))])):
        u = a - b
        n = float(np.hypot(*u))
        out.append(a + u / n * reach if n > 1e-9 else a)
    return out


def leaf_pack_c2(allowed, tip_zone, *, heading, lengths, ratio, bend, gap, grid, min_w, seam=None, seam_gap=4.0,
                 lane=None):
    """Greedy packing of whole ribbon leaves inside ``allowed`` (a C2 region), longest first, centres
    on a grid through the card centre. Each leaf placed above the centre line is paired with its 180°
    twin; both keep ``gap`` px from every leaf already placed and from each other.
    → list of (base, length, width, polygon) for the leaves above the centre line, and the Frag of
    all leaves (both halves)."""
    pr = prep(R(allowed))
    prt = prep(R(tip_zone))
    u = _u(heading)
    v = np.array([-u[1], u[0]])
    o = P(AX, CY)
    x0, y0, x1, y1 = R(allowed).bounds
    corners = np.array([[x0, y0], [x1, y0], [x0, y1], [x1, y1]]) - o
    a_rng = (corners @ u).min(), (corners @ u).max()
    c_rng = (corners @ v).min(), (corners @ v).max()
    placed, rings = [], []          # rings: every placed polygon, twins included
    centres = np.empty((0, 2))
    radii = np.empty(0)
    for L in lengths:
        W = max(L / ratio, min_w)
        for c in np.arange(c_rng[0], c_rng[1] + grid, grid):
            for a in np.arange(a_rng[0], a_rng[1] + grid, grid):
                ctr = o + u * a + v * c
                if ctr[1] > CY - 4.0:
                    continue
                base = ctr - u * (L / 2)
                tip = base + u * L
                if not (pr.contains(Point(*ctr)) and pr.contains(Point(*base)) and pr.contains(Point(*tip))):
                    continue
                if len(radii):
                    d = np.hypot(*(centres - ctr).T)
                    near = d < radii + L / 2 + gap + 4.0
                else:
                    near = np.zeros(0, bool)
                pg = leaf_poly(base, heading, L, W, bend)
                if not pr.contains(pg):
                    continue
                if not all(prt.contains(Point(*q)) for q in _spikes(base, heading, L, bend)):
                    continue
                if seam is not None and (pg.distance(seam) < seam_gap or any(
                        Point(*q).distance(seam) < 2.8 for q in _spikes(base, heading, L, bend))):
                    continue
                twin = rot(pg)
                if pg.distance(twin) < gap:
                    continue
                if any(pg.distance(rings[i]) < gap or twin.distance(rings[i]) < gap for i in np.flatnonzero(near)):
                    continue
                placed.append((base, L, W, pg))
                rings += [pg, twin]
                centres = np.vstack([centres, ctr, rot_pt(ctr)])
                radii = np.append(radii, [L / 2, L / 2])
    narrow = []
    if seam is not None and lane:
        # plain (midrib-less) ribbons straddle the seam: nothing hatched is cut there, and each is crossed
        # mid-body so the cut never lands near a tip
        for L in lane["lengths"]:
            W = lane["w"]
            for c in np.arange(c_rng[0], c_rng[1] + grid, grid):
                for a in np.arange(a_rng[0], a_rng[1] + grid, grid):
                    ctr = o + u * a + v * c
                    if ctr[1] > CY - 4.0 or Point(*ctr).distance(seam) > 14.0:
                        continue
                    base = ctr - u * (L / 2)
                    tip = base + u * L
                    if not (pr.contains(Point(*base)) and pr.contains(Point(*tip))):
                        continue
                    pg = leaf_poly(base, heading, L, W, bend)
                    if not pr.contains(pg) or not pg.intersects(seam):
                        continue
                    if any(Point(*q).distance(seam) < lane["tip_gap"] for q in (*_spikes(base, heading, L, bend), base, tip)):
                        continue
                    _, mid, _ = FM.arc_path(base[0], base[1], heading, [(L / 2, bend[0]), (L / 2, bend[1])])
                    cl = LineString(np.asarray(mid, float))
                    hit = cl.intersection(seam)
                    if hit.is_empty or not (0.35 * cl.length <= cl.project(
                            hit if hit.geom_type == "Point" else hit.geoms[0]) <= 0.65 * cl.length):
                        continue
                    twin = rot(pg)
                    if pg.distance(twin) < gap or pg.intersects(twin):
                        continue
                    if any(pg.distance(r_) < gap or twin.distance(r_) < gap for r_ in rings):
                        continue
                    narrow.append((base, L, W, pg))
                    rings += [pg, twin]
    f = C.Frag()
    for base, L, W, _ in placed:
        lf = MR.ribbon_leaf(base[0], base[1], heading, L, W, bend=bend, hatch=1)
        lf = _reseat(lf)
        f += lf + K.rot180(lf)
    for base, L, W, _ in narrow:
        lf = _reseat(MR.ribbon_leaf(base[0], base[1], heading, L, W, bend=bend, hatch=0, narrow="plain"))
        f += lf + K.rot180(lf)
    return placed + narrow, f


def rot_pt(p):
    return np.array([2 * AX - p[0], 2 * CY - p[1]])


def _reseat(f, roles=("leaf", "spikelet")):
    from art import _qc_parts as Q
    return Q.reseat(f, roles)


# ---- the cloak: red lining, knocked-out grain, jade edge --------------------------------------
def drift(region, *, heading, length, width, along, across, keep):
    """A drift of small vesicas all streaming ``heading``°, on a half-drop lattice whose leaf centres
    include the card centre (so it is its own 180° copy); kept whole or dropped. → Frag of FILLs."""
    reg = R(region)
    x0, y0, x1, y1 = reg.bounds
    u = _u(heading)
    v = np.array([-u[1], u[0]])
    o = P(AX, CY) - u * (length / 2)
    corners = np.array([[x0, y0], [x1, y0], [x0, y1], [x1, y1]]) - o
    a0, a1 = (corners @ u).min() - length, (corners @ u).max()
    c0, c1 = (corners @ v).min(), (corners @ v).max()
    f = C.Frag()
    for k in range(int(math.floor(c0 / across)) - 1, int(math.ceil(c1 / across)) + 2):
        off = (k % 2) * 0.5 * along
        for j in range(int(math.floor((a0 - off) / along)) - 1, int(math.ceil((a1 - off) / along)) + 2):
            b = o + v * (k * across) + u * (j * along + off)
            unit = C.fill(C.vesica_d(b, b + u * length, width))
            if keep(unit):
                f += unit
    return f


def cloak(front, *, sleeves, seam=None):
    """The cloak Part: Gill Red lining with its streaming grain knocked out to paper, the jade
    turned-back edge round the whole outline (a bead row, a MEDIUM hem line). ``front``: shapes of
    everything drawn over it; ``sleeves``: the sleeve regions (jade, drawn by the held items)."""
    shape = cloak_shape()
    gown, _ = gown_outline()
    ring = shape.difference(shape.buffer(-EDGE, quad_segs=16))
    edge = ring.difference(K.box(300.0, -100.0, 450.0, 2000.0)).buffer(0)
    lining = shape.difference(edge)
    blockers = K.c2(front)
    panel = lining.difference(gown.buffer(1.0)).difference(K.c2(sleeves).buffer(2.0))
    ok = panel.difference(blockers.buffer(5.0)).buffer(-3.8)
    ko = drift(panel, keep=lambda unit: ok.contains(unit.shape()) and (
        seam is None or unit.shape().distance(seam) > 3.4), **DRIFT)
    red_d = C.knockout(K.D(lining), ko)
    # paper beads down the middle of the jade edge on rows that are C2 partners
    beads = bead_row(edge.difference(K.c2(sleeves).buffer(4.0)), shape, seam)
    jade_d = C.knockout(K.D(edge), beads) if beads.marks else K.D(edge)
    hem = C.stroke(K.D(shape.buffer(-EDGE, quad_segs=16)), MEDIUM, role="hem")
    hem_line = shape.buffer(-EDGE, quad_segs=16).boundary.intersection(edge.buffer(0.8)).difference(blockers)
    stubs = U(*[g.buffer(1.5) for g in K._lines_of(shapely.line_merge(hem_line) if hem_line.geom_type == "MultiLineString"
                                                   else hem_line) if g.length < 16.0])
    hem = K.clip_out(K.clip_in(hem, edge.buffer(0.8)), U(K.c2(sleeves), stubs), eps=0.0, trap=0.0)
    lines = K.outline(shape) + hem
    return K.Part(shape, K.fill(red_d, K.RED) + K.fill(jade_d, K.JADE), lines,
                  {"edge": edge, "lining": lining, "panel": panel})


def bead_row(edge, shape, seam):
    """Paper beads along the middle of the jade edge: placed on the top-left quarter of the outline
    (from the centre line up to the shoulder) at half-pitch offsets, then mirrored and rotated."""
    mid = shape.buffer(-EDGE / 2, quad_segs=16).boundary
    pts = []
    for g in K._lines_of(mid):
        pts.append(np.asarray(g.coords))
    ring = max(pts, key=len)
    cv = G.Curve(ring)
    L = cv.length
    d, pitch = BEAD["d"], BEAD["pitch"]
    out = C.Frag()
    n = int(L // pitch)
    inner = edge.buffer(-(max(K.CONTOUR, MEDIUM) / 2 + 2.0))
    for i in range(n):
        p = cv.at_s(i * pitch + pitch / 2)
        if p[1] > CY - 4.0 or p[0] > AX:
            continue
        dot = Point(*p).buffer(d / 2, quad_segs=12)
        if not inner.contains(dot) or (seam is not None and dot.distance(seam) < 3.4):
            continue
        out += K.atomic(K.dot(tuple(p), d, role="bead"), f"bd{i}")
    out = out + K.mirror(out, AX)
    return c2_frag(out)


# ---- the gown --------------------------------------------------------------------------------
def gown(exclude, *, soft, seam=None, extra=None):
    """The jade gown Part: a hatched border, a FINE seam inside it and the packed leaf textile.
    ``exclude``: regions no leaf may enter (opening, lacing, bertha, brooch), ``soft``: the sleeves,
    hands and attributes drawn over the gown (leaves stay clear of them)."""
    shape, _ = gown_outline()
    inner = shape.buffer(-GOWN_BORDER, quad_segs=16)
    hard = K.c2(K.U(exclude, soft))
    allowed = inner.buffer(-2.5).difference(hard.buffer(5.0)).difference(K.c2(soft).buffer(SOFT_CLEAR))
    tz = inner.buffer(-(3.0 + FINE / 2 + 0.3)).difference(hard.buffer(5.0 - 1.2))
    placed, leaves = leaf_pack_c2(allowed, tz, seam=seam, lane=LANE, **STREAM)
    border = shape.difference(inner)
    border_hatch = drop_short(K.hatch_in(border.buffer(0.25).difference(hard.buffer(2.0)).difference(K.c2(soft).buffer(3.0)), angle=45.0,
                                         origin=(AX, CY)), 24.0)
    if seam is not None:
        border_hatch = seam_guard(border_hatch, seam)
    leaf_union = U(*[pg for *_, pg in placed], *[rot(pg) for *_, pg in placed])
    dots = paper_dots(inner.buffer(-(FINE / 2 + DOTS["clear"])).difference(leaf_union.buffer(DOTS["clear"]))
                      .difference(hard.buffer(DOTS["clear"] + 1.0)), seam)
    seam_line = K.clip_out(K.outline(inner, FINE, role="seam"), K.c2(soft).buffer(5.0), eps=0.0, trap=0.0)
    lines = K.outline(shape) + seam_line + border_hatch + leaves
    return K.Part(shape, K.fill(C.knockout(K.D(shape), dots) if dots.marks else K.D(shape), K.JADE), lines,
                  {"inner": inner, "leaves": placed})


def paper_dots(region, seam):
    """Paper dots on a half-drop lattice through the card centre (its own 180° copy), kept whole inside
    ``region`` and clear of the seam. → Frag of FILLs, for knocking out of a jade sheet."""
    reg = R(region)
    x0, y0, x1, y1 = reg.bounds
    d, px, py = DOTS["d"], DOTS["px"], DOTS["py"]
    f = C.Frag()
    for i in range(int((x0 - AX) // px) - 1, int((x1 - AX) // px) + 2):
        off = (i % 2) * py / 2
        for j in range(int((y0 - CY - off) // py) - 1, int((y1 - CY - off) // py) + 2):
            c = (AX + i * px, CY + j * py + off)
            dot = Point(*c).buffer(d / 2, quad_segs=12)
            if not reg.contains(dot) or (seam is not None and dot.distance(seam) < 3.4):
                continue
            f += K.atomic(K.dot(c, d, role="bubble"), f"gd{i}_{j}")
    return f
