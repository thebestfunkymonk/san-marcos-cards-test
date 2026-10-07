"""JD whole-card textiles: the jade doublet-and-sleeve mantle and the red chain-edged tabard.

Every region and pattern set here is its own 180° copy about (375, 525), so the inverted herald continues
the upright one with no visible join: the regions are built C2 (``U(x, rot(x))``), the ford-stone brocade
and the stepping-stone chain are drawn for the left half of the card and rotated, and the rowel grid sits on
points that map onto each other.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G
from art import _jd_parts as J

AX, CY = K.AX, 525.0
SIDE_X = 146.0                      # mantle side at the card centre
TAB_X0, TAB_X1 = 290.0, 460.0       # the tabard's edges (a column, its own 180° copy)
TAB_BOTTOM = 640.0                  # the upper tabard runs on past the seam, under its partner
V_TIP, V_HALF = (385.0, 345.0), 78.0
CHAIN = dict(d_in=8.0, band=12.0, stone=11.0, pitch=20.0)
ROWELS = dict(pitch=(32.0, 30.0), r=11.5)
BROCADE = dict(pitch=(22.0, 18.0), size=(13.0, 8.0))
HATCH_JADE, HATCH_RED = -45.0, 45.0


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def c2_frag(f: C.Frag) -> C.Frag:
    """``f`` plus its 180° partner; atomic-motif keys of the partner get a suffix so covering one
    copy never deletes the other."""
    r = K.rot180(f)
    marks = [replace(m, role=m.role + "~") if "@" in m.role else m for m in r.marks]
    return f + C.Frag(marks, r.meta)


def drop_short(f: C.Frag, min_len: float = 9.0) -> C.Frag:
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
    """Drop stroke pieces with an end within ``margin`` of the seam: the half's clip would cut them a
    hair short of their junction, leaving a sub-3 px stub the other half has to finish."""
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


def barrel():
    """The whole-card jade mantle: shoulders from the neck, a bowed side with a vertical tangent on the
    centre line (no kink at the join)."""
    ms = K.MantleSpec(neck_y=296.0, neck_heading=171.5, run=150.0, corner_r=30.0, side_heading=99.0)
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


def tabard_shape(clip=None):
    """The red tabard: a column with a V neck at each end (the lower one is the upper one's 180° copy),
    cut to the mantle's shoulder line."""
    vx, vy = V_TIP
    ytop = vy - 85.0
    yr = vy - (TAB_X1 - vx) * 85.0 / V_HALF
    a = Polygon([(TAB_X0, ytop), (vx - V_HALF, ytop), (vx, vy), (TAB_X1, yr), (TAB_X1, TAB_BOTTOM),
                 (TAB_X0, TAB_BOTTOM)])
    both = K.U(a, rot(a))
    return both.intersection(clip if clip is not None else barrel())


# ---------------------------------------------------------------------------
# tabard: stepping-stone chain and rowels
# ---------------------------------------------------------------------------
def chain_frag(tab, *, d_in, band, stone, pitch, avoid=None, seam=None, turn=22.0):
    """The §G.23 chain run round the inside of the tabard: two MEDIUM rails and lozenge stones between
    them, as paper knocked out of the red. Rails come from the (C2) region; stones are placed for the left
    half of the card and rotated, so the ring needs no start phase that breaks the 180° copy."""
    f = C.Frag()
    cut = Polygon()
    if avoid is not None:
        cut = K.R(avoid)
    for d in (d_in, d_in + band):
        ring = tab.buffer(-d, quad_segs=16).boundary
        for ln in K._lines_of(shapely.line_merge(ring) if ring.geom_type != "LineString" else ring):
            if ln.length > 6:
                f += C.stroke(np.asarray(ln.coords), K.MEDIUM, style="rule", color=K.INK, role="rail")
    mid = tab.buffer(-(d_in + band / 2), quad_segs=16).boundary
    stones = C.Frag()
    k = 0
    for ln in K._lines_of(shapely.line_merge(mid) if mid.geom_type != "LineString" else mid):
        Lm = ln.length
        n = max(1, int(Lm // pitch))
        st = (Lm - (n - 1) * pitch) / 2 if n > 1 else Lm / 2
        for i in range(n):
            sp = st + i * pitch
            p = ln.interpolate(sp)
            if p.x >= AX - 6.0:
                continue
            q, o = ln.interpolate(min(sp + 1.0, Lm)), ln.interpolate(max(sp - 1.0, 0.0))
            ang = math.degrees(math.atan2(q.y - o.y, q.x - o.x))
            qa, qb = ln.interpolate(max(sp - stone, 0.0)), ln.interpolate(max(sp - stone + 1.0, 0.0))
            ra, rb = ln.interpolate(min(sp + stone - 1.0, Lm)), ln.interpolate(min(sp + stone, Lm))
            a0 = math.degrees(math.atan2(qb.y - qa.y, qb.x - qa.x))
            a1 = math.degrees(math.atan2(rb.y - ra.y, rb.x - ra.x))
            if abs(((a1 - a0) + 180.0) % 360.0 - 180.0) > turn:
                continue
            ld = C.lozenge_d(p.x, p.y, stone, band, ang)
            lz = K.R(ld)
            if seam is not None and lz.distance(seam) < 8.0:
                continue
            if not cut.is_empty and (lz.distance(cut) < 6.0 or rot(lz).distance(cut) < 6.0):
                continue
            k += 1
            stones += C.fill(ld, color=K.INK, role="stone")
    return f, stones


def rowel_sites(tab, *, pitch, r, front, seam=None, margin=0.0):
    """Rowels in a half-drop grid on points that map onto each other under the 180° turn (columns at
    375 + i·px, rows at 525 + j·py, odd columns dropped half a pitch), each kept whole inside the chain."""
    px, py = pitch
    inner = tab.buffer(-(CHAIN["d_in"] + CHAIN["band"] + K.MEDIUM / 2 + 3.2 + K.FINE / 2 + margin), quad_segs=12)
    x0, y0, x1, y1 = tab.bounds
    out = []
    for i in range(-6, 7):
        off = py / 2 if i % 2 else 0.0
        for j in range(-20, 21):
            x, y = AX + i * px, CY + off + j * py
            sil = J.rowel_solid((x, y), r)
            if not inner.contains(sil):
                continue
            if front is not None and sil.buffer(3.4).intersects(front):
                continue
            if seam is not None and sil.distance(seam) < 8.0 and not (i == 0 and j == 0):
                continue
            out.append((x, y))
    return out


def brocade_left(field_left, *, pitch, size, avoid=None, seam=None):
    """A half-drop grid of small outlined lozenges (FINE Aquifer on the jade), left half only; each
    stone is atomic and keeps clear of the field's edge."""
    px, py = pitch
    L, W = size
    inner = field_left.buffer(-(L / 2 + K.FINE / 2 + 4.3))
    x0, y0, x1, y1 = field_left.bounds
    f = C.Frag()
    for j in range(int(math.floor((y0 - CY) / py)) - 1, int(math.ceil((y1 - CY) / py)) + 2):
        off = px / 2 if j % 2 else 0.0
        for i in range(int(math.floor((x0 - AX - off) / px)) - 1, int(math.ceil((x1 - AX - off) / px)) + 2):
            x, y = AX + off + i * px, CY + j * py
            if x > AX - 6.0 or not inner.contains(Point(x, y)):
                continue
            st = K.R(C.lozenge_d(x, y, L, W))
            if seam is not None and st.distance(seam) < 8.0:
                continue
            if avoid is not None and st.distance(avoid) < 6.0:
                continue
            f += K.atomic(C.stroke(C.lozenge_d(x, y, L, W), K.FINE, style="point", color=K.INK, role="stone"),
                          f"fb{i}_{j}")
    return f


# ---------------------------------------------------------------------------
# the garments Part
# ---------------------------------------------------------------------------
def garments(front, *, sleeves, cuff_fills, cuff_lines, sleeve_grain, sleeve_edges, collar=None, seam=None):
    """The whole-card robe: jade mantle (brocade) and the red tabard column on it (chain edging and
    gold rowels), plus the two sleeves, all one C2 region set. ``front``: shapes of the items drawn over it
    (head, hands, attributes, belt, map)."""
    sleeve_zone = K.c2(sleeves)
    shape = K.U(barrel(), sleeve_zone)
    shape = K.U(shape, shape.buffer(12).buffer(-12))
    tab = tabard_shape(shape)
    if collar is not None:
        shape = K.U(shape, collar)
    jade = shape.difference(tab)
    blockers = K.c2(front)

    chain, stones = chain_frag(tab, **CHAIN, avoid=blockers, seam=seam)
    sites = rowel_sites(tab, **ROWELS, front=blockers, seam=seam)
    rowels, rowel_cores = C.Frag(), []
    for (x, y) in sites:
        sil, fr = J.rowel((x, y), ROWELS["r"])
        rowels += fr
        rowel_cores.append(sil.buffer(-3.6, quad_segs=8).buffer(3.6, quad_segs=8))
    red = tab
    for cg in rowel_cores:
        red = red.difference(cg.buffer(-1.6))
    red_d = C.knockout(K.D(red), chain, stones)

    jade_l = jade.intersection(K.box(0, 0, AX, 2000))
    keep_out = K.U(blockers, sleeve_zone.buffer(1.0))
    bro = brocade_left(jade_l.buffer(-K.CONTOUR / 2 - 4.0), **BROCADE, avoid=keep_out, seam=seam)
    stone_zone = K.U(*[K.R(m.d) for m in bro.marks]).buffer(5.5) if bro.marks else Polygon()
    ornament = c2_frag(bro)
    jade_field = jade.buffer(-(K.CONTOUR / 2 + 4.0)).difference(K.c2(stone_zone)).difference(
        blockers.buffer(4.4)).difference(sleeve_zone.buffer(5.5))
    jade_hatch = drop_short(K.hatch_in(jade_field, angle=HATCH_JADE, origin=(AX, CY)), 14.0)
    red_field = tab.buffer(-(CHAIN["d_in"] + CHAIN["band"] + K.MEDIUM / 2 + 4.4)).difference(
        K.U(*[J.rowel_solid(c, ROWELS["r"]) for c in sites]).buffer(5.0) if sites else Polygon()).difference(
        blockers.buffer(4.4))
    red_hatch = drop_short(K.hatch_in(red_field, angle=HATCH_RED, origin=(AX, CY)), 14.0)

    gold = K.U(*[K.R(m.d) for m in cuff_fills.marks]) if cuff_fills.marks else Polygon()
    fills = K.fill(jade.difference(K.c2(gold).buffer(-1.6)), K.JADE) + C.fill(red_d, color=K.RED, role="fill")
    fills += K.c2(cuff_fills) + rowels.select(lambda m: m.layer != "ink")
    lines = K.outline(shape) + K.outline(tab) + rowels.select(lambda m: m.layer == "ink")
    lines += ornament + seam_guard(jade_hatch, seam) + seam_guard(red_hatch, seam)
    lines += K.c2(sleeve_grain) + K.c2(sleeve_edges) + K.c2(cuff_lines)
    return K.Part(shape, fills, lines, {"jade": jade, "tab": tab})
