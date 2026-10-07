"""Q♦ whole-card textiles: the Gill Red cape, the jade arcade gown and the sleeves' gold cuffs.

Every outline is point-symmetric about the card centre (375, 525): a top half with a vertical tangent on the
centre line, united with its mirror and its 180° copy. Patterns that read the same upside down (hatch on a grid
through the centre, knocked-out stones drawn on the left half and rotated) are C2 by construction; the arcade
tiers belong to the upper figure and stop well above the seam, so the lower figure's tiers are their copy.

    cape      red, a stepping-stone chain knocked out to paper along its outer and front edges, FINE hatch
              between, a grain along each sleeve and a gold cuff with ink stones at its mouth
    gown      jade, keystoned arcades in FINE (the courthouse's arched windows), hatch between the tiers
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
from art import _qd_parts as Q

AX, CY = K.AX, 525.0
CAPE_PTS = [(375.0, 282.0), (350.0, 284.0), (284.0, 293.0), (210.0, 312.0), (172.0, 340.0), (155.0, 420.0)]
CAPE_SIDE = 148.0                       # the cape's side on the centre line
OPEN_PTS = [(375.0, 291.0), (344.0, 296.0), (312.0, 348.0), (274.0, 430.0)]
OPEN_SIDE = 249.0                       # the opening's side on the centre line
NECK_L, NECK_R, NECK_SAG = (338.0, 306.0), (412.0, 306.0), -8.0
BAND = (14.0, 29.0)                     # the chain's FINE rules, measured in from the red's edges
STONE = (11.0, 6.6)
STONE_PITCH = 23.0
ARCADE = dict(pitch=29.0, a=3.5, jamb=13.0, key=(6.0, 26.0), sills=(513.0, 475.2, 438.7), cornice=402.2,
              on_axis="arch")
ARCADE_AX = 384.0
ROW_PITCH, ROW_STONE, ROW_SMALL = 28.0, (14.0, 8.0), (9.0, 4.4)


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def c2_frag(f: C.Frag) -> C.Frag:
    """``f`` plus its 180° partner; atomic-motif keys of the partner get a suffix so covering one copy
    never deletes the other."""
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
    """Drop stroke pieces with an end within ``margin`` of the seam: the half's clip would cut them a hair
    short of their junction, leaving a stub the other half has to finish."""
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


def _half(edge_pts, side_x, k0=0.30, k1=0.34):
    """Left half from the axis, along the Catmull-Rom edge through ``edge_pts`` to the last point, then a
    cubic that falls to a vertical tangent on the centre line at (side_x, CY) and closes along the axis."""
    pts = K._catmull_rom(edge_pts, 24)
    p0 = pts[-1]
    d0 = (pts[-1] - pts[-4])
    d0 = d0 / np.hypot(*d0)
    p3 = np.array([side_x, CY])
    span = CY - p0[1]
    c1, c2 = p0 + d0 * span * k0, p3 - np.array([0.0, 1.0]) * span * k1
    t = np.linspace(0.0, 1.0, 60)[1:, None]
    cub = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p3
    return Polygon(np.vstack([pts, cub, [[AX, CY]]])).buffer(0)


def _whole(half):
    top = K.U(half, K.mirror(half, AX))
    return K.U(top, rot(top))


def cape_shape():
    return _whole(_half(CAPE_PTS, CAPE_SIDE))


def opening():
    return _whole(_half(OPEN_PTS, OPEN_SIDE))


def gown_shape():
    """The opening below the neckline's arc (and its 180° copy)."""
    top = K.R(K.Path(K.P(*NECK_L)).sag(K.P(*NECK_R), NECK_SAG).line((NECK_R[0] + 200, NECK_R[1] - 200))
              .line((NECK_L[0] - 200, NECK_L[1] - 200)).close().d)
    g = _half(OPEN_PTS, OPEN_SIDE)
    top_half = K.U(g, K.mirror(g, AX)).difference(top)
    return K.U(top_half, rot(top_half))


def _rings(region, d):
    """Closed offset rings (point arrays) of ``region`` inset by ``d``."""
    g = region.buffer(-d, quad_segs=16)
    out = []
    for p in K._polys_of(g):
        for ring in [p.exterior, *p.interiors]:
            out.append(np.asarray(ring.coords))
    return out


def chain_left(red_left, *, avoid=None, seam=None):
    """§G.23 stepping-stone chain in the cape's border: two FINE rules and lozenge stones knocked out to
    paper on the mid-line, drawn on the left half only (the caller rotates it). → (rules Frag, stone
    polygons)."""
    lines, stones = C.Frag(), []
    for d in BAND:
        for q in _rings(red_left, d):
            lines += C.stroke(C.polyline_d(q, closed=True), K.FINE, style="rule", role="chain")
    mid = sum(BAND) / 2
    room = red_left.buffer(-(STONE[0] / 2 + 1.0))
    for q in _rings(red_left, mid):
        ln = LineString(q)
        n = max(2, int(round(ln.length / STONE_PITCH)))
        for i in range(n):
            s = (i + 0.5) * ln.length / n
            p = ln.interpolate(s)
            p2, p1 = ln.interpolate(min(s + 1.0, ln.length)), ln.interpolate(max(s - 1.0, 0.0))
            a = math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))
            lz = K.R(C.lozenge_d(p.x, p.y, *STONE, a))
            if not room.contains(Point(p.x, p.y)) or p.x > AX - 6.0:
                continue
            if seam is not None and lz.distance(seam) < 8.0:
                continue
            if avoid is not None and lz.distance(avoid) < 7.0:
                continue
            stones.append(lz)
    return lines, stones


def arcade(reg, *, avoid):
    """The gown's stacked arcades for the upper figure: every tier keeps the bays that fit whole inside the
    gown, in contiguous runs (the gown5 construction of the pre-rework art, minus its fill and outline)."""
    inner = reg.buffer(-(K.MEDIUM / 2 + K.GAP_MARK + K.FINE / 2 + 1.0))
    inner = inner.difference(avoid.buffer(K.GAP + K.FINE / 2 + K.MEDIUM / 2 + 1.0))
    ends = reg.buffer(0.8)
    pitch, a, jamb, key = (ARCADE[k] for k in ("pitch", "a", "jamb", "key"))
    r = pitch / 2 - a
    pat, foot = C.Frag(), []
    ks = range(-int(400 / pitch), int(400 / pitch) + 1)
    for j, sill in enumerate(ARCADE["sills"]):
        ok = [k for k in ks if inner.contains(Q._bay_footprint(ARCADE_AX + k * pitch, sill, r=r, a=a, jamb=jamb,
                                                               key=key, pitch=pitch))]
        runs, cur = [], []
        for k in ok:
            if cur and k != cur[-1] + 1:
                runs.append(cur)
                cur = []
            cur.append(k)
        if cur:
            runs.append(cur)
        for run in runs:
            xb = [ARCADE_AX + k * pitch for k in run]
            ys = sill - jamb
            sl = a if inner.contains(LineString([(xb[0] - pitch / 2 - a, ys), (xb[0] - pitch / 2, ys)])) else 0.0
            sr = a if inner.contains(LineString([(xb[-1] + pitch / 2, ys), (xb[-1] + pitch / 2 + a, ys)])) else 0.0
            pat += K.atomic(Q._arcade_run(xb, sill, r=r, a=a, jamb=jamb, key=key, stub_l=sl, stub_r=sr),
                            f"arcade{j}_{run[0]}")
            foot += [Q._bay_footprint(x, sill, r=r, a=a, jamb=jamb, key=key, pitch=pitch) for x in xb]
        ln = LineString([(0, sill), (750, sill)]).intersection(ends)
        for g in K._lines_of(ln):
            if g.length > 12:
                pat += Q._own_path(K.line(np.asarray(g.coords), K.FINE, style="rule", role="sill"))
                foot.append(g)
    ln = LineString([(0, ARCADE["cornice"]), (750, ARCADE["cornice"])]).intersection(ends)
    for g in K._lines_of(ln):
        if g.length > 12:
            pat += Q._own_path(K.line(np.asarray(g.coords), K.FINE, style="rule", role="cornice"))
            foot.append(g)
    return pat, K.U(*foot) if foot else Polygon()


def cape(front, *, sleeves, cuff_fills, cuff_lines, sleeve_grain, sleeve_edges, seam=None):
    """The red cape as one C2 region set, its sleeves lobes of its own outline. ``front``: shapes of the
    items drawn over it (head, hands, attributes)."""
    sleeve_zone = K.c2(sleeves)
    shape = K.U(cape_shape(), sleeve_zone)
    red = shape.difference(opening())
    blockers = K.c2(front)

    red_l = red.intersection(K.box(0, 0, AX, 2000))
    keep_out = K.U(blockers, sleeve_zone.buffer(1.0))
    chain, stones = chain_left(red_l, avoid=keep_out, seam=seam)
    chain = K.clip_out(chain, sleeve_zone, eps=-0.5, trap=0.0)
    stone_union = K.U(*stones) if stones else Polygon()
    stone_fill = K.U(*[s for s in stones])
    ornament = c2_frag(chain)
    knock = K.U(stone_union, rot(stone_union)) if stones else Polygon()

    gold = K.U(*[K.R(m.d) for m in cuff_fills.marks]) if cuff_fills.marks else Polygon()
    red_fill = red.difference(K.c2(gold).buffer(-1.6)).difference(knock)

    field = red.buffer(-(BAND[1] + 7.0)).difference(sleeve_zone.buffer(5.0))
    hatch = K.hatch_in(field, origin=(AX, CY))
    hatch = K.clip_out(hatch, blockers.buffer(4.6), eps=0, trap=0)
    hatch = seam_guard(drop_short(hatch, 12.0), seam)

    fills = K.fill(red_fill, K.RED) + K.c2(cuff_fills)
    lines = ornament + hatch + K.c2(sleeve_grain) + K.c2(sleeve_edges) + K.c2(cuff_lines)
    return K.Part(shape, fills, lines, {"red": red})


def centre_row(reg, seam):
    """The row between the two figures' lowest sills: paper lozenges on the centre line (the cape's stone
    motif), the two nearest the seam smaller, C2 about the centre because their positions are symmetric about it. A lozenge the seam cuts, or
    comes within 1.6 px of, would leave a hairline bridge to its partner, so the seam's own stretch stays plain."""
    room = reg.buffer(-(K.MEDIUM / 2 + 6.0))
    out = []
    for k in range(-12, 13):
        lz = K.R(C.lozenge_d(AX + k * ROW_PITCH, CY, *(ROW_SMALL if abs(k) == 1 else ROW_STONE), 0.0))
        if room.contains(lz) and (seam is None or lz.distance(seam) > 1.6):
            out.append(lz)
    return K.U(*out) if out else Polygon()


def gown(front, *, seam=None):
    """The jade gown (whole card): outline, the upper figure's arcade tiers, FINE hatch between them, and a
    row of paper lozenges where the two figures' tiers meet."""
    reg = gown_shape()
    upper = reg.intersection(K.box(0, 0, 750, CY))
    pat, foot = arcade(upper, avoid=front)
    row = centre_row(reg, seam)
    hatch_zone = reg.buffer(-(K.MEDIUM / 2 + 4.6)).difference(K.c2(foot).buffer(5.0)).difference(
        K.c2(front).buffer(5.0)).difference(row.buffer(5.0)).difference(
        K.box(0, ARCADE["sills"][0] - 2.0, 750, 2 * CY - ARCADE["sills"][0] + 2.0))
    hatch = K.hatch_in(hatch_zone, origin=(AX, CY))
    hatch = seam_guard(drop_short(hatch, 16.0), seam)
    lines = K.outline(reg) + c2_frag(seam_guard(pat, seam)) + hatch
    return K.Part(reg, K.fill(reg.difference(row), K.JADE), lines, {})
