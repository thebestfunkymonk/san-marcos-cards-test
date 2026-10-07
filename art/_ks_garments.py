"""KS whole-card textiles: the jade barrel mantle, red lapels and the karst lens.

Everything here is built so the 180° copy continues the top half without a
visible join: regions are C2 about (375, 525) by construction, and each pattern
is drawn once on the full-height left half (or, for the lens that straddles the
axis, on rows that are C2 partners of each other) and then rotated.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG
from inkkit import geom as G

AX, CY = K.AX, 525.0
BORDER = 38.0                       # patterned jade border inside the outline
LENS_HW, LENS_THROAT = 33.0, 312.0
LAP_X, LAP_R = 274.0, 1450.0        # lapel outer arc: x at the centre, radius (a near-plumb shawl edge)
SIDE_X = 146.0                      # mantle side at the card centre


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def c2_frag(f: C.Frag) -> C.Frag:
    """``f`` plus its 180° partner; atomic-motif keys of the partner get a suffix so
    covering one copy never deletes the other."""
    r = K.rot180(f)
    marks = [replace(m, role=m.role + "~") if "@" in m.role else m for m in r.marks]
    return f + C.Frag(marks, r.meta)


def barrel() -> object:
    """The whole-card jade mantle: shoulders from the neck, a smooth bowed side
    with a vertical tangent on the centre line (no kink at the join)."""
    ms = K.MantleSpec(neck_y=270.0, neck_heading=170.0, run=140.0, corner_r=30.0, side_heading=99.0)
    pts = K.mantle_outline(ms)
    k = next(i for i, p in enumerate(pts) if p[1] >= 369.0)
    head = pts[:k + 1]
    p0 = head[-1]
    d0 = (head[-1] - head[-2]) / np.hypot(*(head[-1] - head[-2]))
    p3 = np.array([SIDE_X, CY])
    c1, c2 = p0 + d0 * 52.0, p3 - np.array([0.0, 1.0]) * 62.0
    t = np.linspace(0.0, 1.0, 40)[1:, None]
    cub = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p3
    half = Polygon(np.vstack([head, cub, [[AX, CY]]])).buffer(0)
    top = K.U(half, K.mirror(half, AX))
    return K.U(top, rot(top))


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
    """Drop stroke pieces with an end within ``margin`` of the seam: the half's clip would cut
    them a hair short of their junction, leaving a sub-3 px stub the other half has to finish."""
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


def lens():
    g = K.lens(K.LensSpec(half_w=LENS_HW, throat_y=LENS_THROAT))
    return K.R(K.circle(g["cL"], g["R"])).intersection(K.R(K.circle(g["cR"], g["R"])))


def lapel_zone(shape):
    """The red shawl band: between the lens and a near-plumb outer arc, both sides."""
    left = K.R(K.circle((LAP_X + LAP_R, CY), LAP_R))
    right = K.R(K.circle((2 * AX - LAP_X - LAP_R, CY), LAP_R))
    return left.intersection(right).intersection(shape)


def karst(inner, *, pitch=(22.0, 16.5), sizes=(6.0, 10.0, 16.0), weights=(0.12, 0.33, 0.55), flood_min=9.5,
          seed=1983, seam=None):
    """§G.12 staggered voids on rows that are C2 partners of each other (row k above
    the centre pairs with row k below it), so the lens reads as one continuous field.
    Returns (jade fills, ink lines) of the TOP half only."""
    px, py = pitch
    cum = np.cumsum(weights) / np.sum(weights)
    placed = []
    fills, lines = C.Frag(), C.Frag()
    n = 0
    w = K.FINE
    for j in range(0, 24):
        cy = CY - py / 2 - j * py
        if cy < LENS_THROAT:
            break
        off = px / 4 + (px / 2 if j % 2 else 0.0)
        for i in range(-3, 4):
            cx = AX + off + i * px
            hsh = ((i * 73856093) ^ (j * 19349663) ^ (seed * 83492791)) & 0xFFFFFF
            k = min(int(np.searchsorted(cum, (hsh % 10007) / 10007.0, side="right")), len(sizes) - 1)
            for kk in range(k, -1, -1):
                d = sizes[kk]
                rx, ry = MG.KARST_ASPECT * d / 2 + w / 2, d / 2 + w / 2
                ell = shapely.affinity.scale(Point(cx, cy).buffer(1.0, quad_segs=32), rx, ry)
                if not inner.contains(ell):
                    continue
                if ell.distance(rot(ell)) < MG_MIN_CLEAR:
                    continue
                if seam is not None and ell.distance(seam) < 6.0:
                    continue
                if any(ell.distance(q) < MG_MIN_CLEAR for q in placed):
                    continue
                placed += [ell, rot(ell)]
                n += 1
                v = MG.karst_void(cx, cy, d, w=w)
                lines += K.atomic(v, f"ks{n}")
                if d >= flood_min:
                    closed = [p for p, cl in G.flatten(v.marks[0].d, 0.05) if cl][0]
                    fills += K.atomic(K.fill(Polygon(closed), K.JADE, role="cavern"), f"ks{n}")
                break
    return fills, lines


MG_MIN_CLEAR = C.MIN_CLEAR


def bubble_field(region_left, *, d_lo=4.2, d_hi=9.5, pitch=21.0, offsets=(13.0, 34.0, 55.0), lens_shape=None,
                 ramp=(30.0, 200.0), seam=None, blockers=None):
    """Rising bubbles (paper dots knocked out of the red): columns along offset curves of
    the lens edge, staggered, growing with the distance from the card centre so the
    top figure's bubbles rise toward ITS head and the 180° copy's toward its own."""
    edge = lens_shape.boundary
    left_edge = LineString(np.asarray(edge.coords)).intersection(K.box(0, 0, AX, 2000))
    arcs = [g for g in K._lines_of(left_edge)]
    arc = max(arcs, key=lambda g: g.length)
    # parametrise the lens' left arc from the bottom tip to the top tip
    pts = np.asarray(arc.coords)
    if pts[0][1] < pts[-1][1]:
        pts = pts[::-1]
    base = LineString(pts[::-1])                     # bottom -> top
    out = C.Frag()
    L = base.length
    zone = region_left.buffer(-4.2 - 1.55)
    for ci, o in enumerate(offsets):
        s = (pitch / 2) * (ci % 2)
        while s < L:
            p = np.array(base.interpolate(s).coords[0])
            q = np.array(base.interpolate(min(s + 0.5, L)).coords[0])
            tan = (q - p) / max(np.hypot(*(q - p)), 1e-9)
            nrm = np.array([-tan[1], tan[0]])        # to the screen-left of travel (outward at left lapel)
            if nrm[0] > 0:
                nrm = -nrm
            c = p + nrm * o
            dist = abs(c[1] - CY)
            t = min(max((dist - ramp[0]) / (ramp[1] - ramp[0]), 0.0), 1.0)
            d = d_lo + (d_hi - d_lo) * t
            if seam is not None and Point(*c).distance(seam) < d / 2 + 7.0:
                s += pitch
                continue
            if blockers is not None and blockers.distance(Point(*c)) < d / 2 + 6.5:
                s += pitch
                continue
            if zone.contains(Point(*c).buffer(d / 2 + 0.5)):
                out += K.atomic(C.dot(c[0], c[1], d, role="bubble"), f"b{ci}_{int(s)}")
            s += pitch
    return out


FAULT = ((282.0, 476.0), (216.0, 556.0))
STRATA_Y0 = 519.0                             # courses 12/19 are symmetric about y 525 from this phase


def _side(p0, p1, sign):
    """Half-plane left (+1) or right (-1) of the directed line p0→p1."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    u = (p1 - p0) / np.hypot(*(p1 - p0))
    n = np.array([-u[1], u[0]]) * sign
    big = 4000.0
    return Polygon([p0 - u * big, p1 + u * big, p1 + u * big + n * big, p0 - u * big + n * big])


def strata_field(region):
    """Whole-card strata with the Balcones fault: the fault and its 180° partner split the card
    into three blocks on one common course phase (symmetric about y 525, so any 12/19 jog would
    leave 7 px slivers); the displacement reads as the hatch grain turning across the fault."""
    p0, p1 = FAULT
    d = np.array(p1) - np.array(p0)
    fault_l = LineString([np.array(p0) - d * 6, np.array(p1) + d * 6])
    left_zone = _side(p0, p1, -1)               # screen-left of the fault (x smaller)
    right_zone = rot(left_zone)
    mid = region.difference(left_zone).difference(right_zone)
    out = C.Frag()
    for zone, angle in ((mid, C.DIAG), (region.intersection(left_zone), -C.DIAG),
                        (region.intersection(right_zone), -C.DIAG)):
        if not zone.is_empty:
            out += MG.strata(zone, y0=STRATA_Y0, heights=(12.0, 19.0), hatched="thin", angle=angle,
                             origin=(AX, CY))
    for ln in (fault_l, rot(fault_l)):
        for g in K._lines_of(ln.intersection(region)):
            if g.length > 1.0:
                out += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="fault")
    return out


def garments(front, *, sleeves, cuff_bands, sleeve_grain, sleeve_edges, seam=None):
    """The whole-card robe: jade barrel mantle (strata + fault inside a hatched border), red lapels
    (rising bubbles + hatch), the karst lens, and the two jade sleeves, all as one C2 region set.
    ``front``: shapes of the items drawn over it (head, hands, attributes) — atomic motifs and
    pattern ends keep clear of them."""
    sleeve_zone = K.c2(sleeves)
    shape = K.U(barrel(), sleeve_zone)
    shape = K.U(shape, shape.buffer(12).buffer(-12).intersection(sleeve_zone.buffer(30)))
    lens_s = lens().intersection(shape)
    zone = lapel_zone(shape)
    red = zone.difference(lens_s).difference(sleeve_zone)
    jade = shape.difference(lens_s).difference(red)
    blockers = K.c2(front)

    # ---- jade: hatched border, FINE seam, strata + fault inside --------------------------
    inner_shape = barrel().buffer(-BORDER, quad_segs=16)
    border = jade.difference(inner_shape).difference(sleeve_zone)
    seam_line = K.outline(inner_shape, K.FINE, role="seam")
    seam_line = K.clip_in(seam_line, jade.buffer(-0.2).difference(sleeve_zone.buffer(0.4)))
    border_hatch = drop_short(K.hatch_in(border.buffer(0.25), angle=45.0, origin=(AX, CY)), 26.0)
    # grown 0.8 px under the lapel/lens/sleeve outlines so course lines overlap them instead of
    # stopping a hair short of the stroke
    strata_zone = jade.intersection(inner_shape).buffer(0.8).intersection(inner_shape).difference(sleeve_zone.buffer(-0.8))
    strata = strata_field(strata_zone)
    strata = drop_short(strata.select(lambda m: m.role == "hatch"), 19.0) + strata.select(lambda m: m.role != "hatch")

    # ---- red lapels: rising bubbles knocked out, hatch between ---------------------------
    left_red = red.intersection(K.box(0, 0, AX, 2000))
    bubbles = bubble_field(left_red, lens_shape=lens_s, offsets=(20.0, 47.0), pitch=24.0, d_hi=8.4, seam=seam,
                           blockers=blockers)
    bubbles = c2_frag(bubbles)
    bub_shape = K.U(*[K.R(m.d) for m in bubbles.marks if m.kind == "fill"]) if bubbles.marks else Polygon()
    red_hatch = K.hatch_in(red, angle=-45.0, origin=(AX, CY))
    red_hatch = drop_short(K.clip_out(red_hatch, K.U(bub_shape, blockers), eps=6.2, trap=0.0), 12.0)
    red_fill = K.R(C.knockout(K.D(red), bubbles))

    # ---- the lens: karst voids, flooded caverns ------------------------------------------
    inner = lens_s.buffer(-(K.MEDIUM / 2 + 3.2))
    cav, voids = karst(inner, seam=seam)
    cav, voids = c2_frag(cav), c2_frag(voids)

    # ---- sleeves --------------------------------------------------------------------------
    fills = K.fill(jade, K.JADE) + K.fill(red_fill, K.RED) + cav.select(lambda m: m.kind == "fill")
    lines = K.outline(shape) + K.outline(lens_s) + K.outline(red)
    textile = seam_guard(border_hatch + strata + red_hatch, seam)
    lines += seam_line + textile + voids + bubbles.select(lambda m: m.kind != "fill")
    lines += K.c2(cuff_bands) + K.c2(sleeve_grain) + K.c2(sleeve_edges)
    return K.Part(shape, fills, lines, {"jade": jade, "red": red, "lens": lens_s})
