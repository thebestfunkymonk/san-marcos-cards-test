"""Regalia for the K♠, constructed with compass and ruler.

    crown_band(...)               reusable gold band (two parallel arcs) + jewel seat
    escarpment_crown(CrownSpec)   the three-step limestone crown (§H.1)
    brow_jewel(c, r)              small Source Rosette jewel, gold + red centre
    vent_orb(c, r)                gold orb, ripple latitudes, one bubble (§H.1)
    core_sceptre(SceptreSpec)     seven banded segments + rosette finial (§H.1)
    lion_clasp(c, r)              the simplified Lion Mark as a gold clasp (§G.2)

Each returns a hair.Part (shape, fills, lines, meta).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import shapely

import kit as K
from deck.motifs import core as C
from deck.motifs import geometric as M
from hair import Part


# =============================================================================
# crown
# =============================================================================
@dataclass
class CrownSpec:
    cx: float = 375.0
    band_top: float = 166.0      # band top edge on the axis
    band_h: float = 22.0
    band_hw: float = 68.0        # half-width of the band at its top edge
    band_bow: float = 4.0        # the band's edges dip this much at the centre
    vanish: tuple = (375.0, 700.0)  # merlon edges are rays from this point (the flare)
    # merlon half-angles (degrees from the vertical) of each edge, left half,
    # outer → inner: outer merlon, crenel, middle merlon, crenel, centre merlon
    edges: tuple = (7.315, 5.36, 4.243, 2.27, 1.146)
    tops: tuple = (134.0, 111.0, 88.0)   # outer, middle, centre merlon tops — three fault-steps
    crenel_depth: float = 12.0
    jewel_r: float = 14.0         # a cabochon overlapping both band edges; crown lines break 3 px clear
    hatch: bool = True
    gold_stone: bool = True      # merlons in gold (the colour map) with limestone hatch


def crown_band(cx, top, h, hw, bow, v=None, edge_deg=None):
    """Gold band: region between two parallel arcs (same sagitta, ``h``
    apart) — seen slightly from above, the band dips at the centre. With a
    vanishing point ``v`` and ``edge_deg`` its ends are rays from v (so they
    continue the crown's flared outer edges without a step)."""
    y0, y1 = top - bow, top + h - bow
    if v is not None:
        xl0, xl1 = _ray_x(v, -edge_deg, y0), _ray_x(v, -edge_deg, y1)
    else:
        xl0 = xl1 = cx - hw
    a0, a1 = K.P(xl0, y0), K.P(2 * cx - xl0, y0)
    b0, b1 = K.P(xl1, y1), K.P(2 * cx - xl1, y1)
    d = K.Path(a0).arc3((cx, top), a1).line(b1).arc3((cx, top + h), b0).close().d
    return K.R(d), d


def _ray_x(v, deg, y):
    """x where the ray from the vanishing point v at ``deg`` from the vertical
    (negative = left) meets the horizontal line y."""
    return v[0] + math.tan(math.radians(deg)) * (v[1] - y)


def brow_jewel(c, r=14.0, ribs=8) -> Part:
    """Small Source Rosette jewel (§H.1): a gold disc, ``ribs`` straight
    Aquifer ribs from the rim toward the centre (the crater), and a Gill Red
    Ø8.4 centre dot cut into the gold (layer trap). The ribs stop 3 px short
    of the red dot."""
    c = K.P(c)
    disc = K.R(K.circle(c, r))
    lines = K.outline(K.circle(c, r))
    r_in = 4.2 + 3.0 + K.FINE / 2
    for k in range(ribs):
        a = -90 + 360 * k / ribs + 180 / ribs
        p0, p1 = K.polar(c, r, a), K.polar(c, r_in, a)
        lines += K.line(f"M{p0[0]} {p0[1]}L{p1[0]} {p1[1]}", K.FINE)
    fills = K.fill(disc, K.GOLD) + K.dot(c, 8.4, K.RED)
    return Part(disc, fills, lines, {})


def escarpment_crown(s: CrownSpec = CrownSpec()) -> Part:
    cx = s.cx
    v = K.P(s.vanish)
    band, band_d = crown_band(cx, s.band_top, s.band_h, s.band_hw, s.band_bow, v=K.P(s.vanish), edge_deg=s.edges[0])
    e = s.edges
    # left-half merlon edge angles (outer, inner) and tops; the centre merlon straddles the axis
    L = [(-e[0], -e[1], s.tops[0]), (-e[2], -e[3], s.tops[1])]
    Cm = (-e[4], e[4], s.tops[2])
    merl = L + [Cm] + [(-b, -a, t) for (a, b, t) in reversed(L)]
    base = s.band_top + 8.0            # merlons run down behind the band

    def wedge(a, b, t, bottom=base):
        return shapely.Polygon([(_ray_x(v, a, t), t), (_ray_x(v, b, t), t),
                                (_ray_x(v, b, bottom), bottom), (_ray_x(v, a, bottom), bottom)])

    blocks = [wedge(a, b, t) for (a, b, t) in merl]
    # wall body between merlons: fills each crenel up to (lower top + crenel depth)
    walls = []
    for k in range(4):
        a = merl[k][1]
        b = merl[k + 1][0]
        t = max(merl[k][2], merl[k + 1][2]) + s.crenel_depth
        walls.append(wedge(a - 0.3, b + 0.3, t))
    wall = K.U(*walls)
    stone = K.U(*blocks, wall)
    above_band = shapely.Polygon([(0, 0), (750, 0), (750, 400), (0, 400)]).difference(
        band.union(K.box(0, s.band_top + s.band_h - s.band_bow, 750, 400)))
    stone = stone.intersection(above_band.buffer(1.6))      # runs 1.6 under the band's contour (trap)
    shape = K.U(stone, band)

    fills = K.fill(band, K.GOLD) + (K.fill(stone, K.GOLD) if s.gold_stone else C.Frag())
    lines = C.Frag()
    # joints: the ray lines under each crenel down to the band (merlon boundaries)
    for k in range(4):
        a = merl[k][1]
        b = merl[k + 1][0]
        t = max(merl[k][2], merl[k + 1][2]) + s.crenel_depth
        mid = (a + b) / 2
        x0, x1 = _ray_x(v, mid, t), _ray_x(v, mid, base)
        seg = shapely.LineString([(x0, t), (x1, base)]).difference(band)
        lines += K.line(np.asarray(seg.coords), K.MEDIUM)
    # half-hatch: side merlons on their outer half; the centre merlon on its upper half
    if s.hatch:
        for k, (a, b, t) in enumerate(merl):
            if k in (0, 1, 3, 4):
                # region between the outer edge and the merlon's mid-ray, down to the crenel joint
                mid = (a + b) / 2
                if k < 2:
                    half = wedge(a, mid, t, s.band_top + 2)
                    ang_h = -45.0
                else:
                    half = wedge(mid, b, t, s.band_top + 2)
                    ang_h = -135.0
                half = half.difference(band)
                lines += K.hatch_in(half, angle=ang_h)
                x0, x1 = _ray_x(v, mid, t), _ray_x(v, mid, base)
                seg = shapely.LineString([(x0, t), (x1, base)]).difference(band)
                lines += K.line(np.asarray(seg.coords), K.FINE)
            else:
                # centre merlon: its upper half carries horizontal bedding hatch
                # (horizontal hatch keeps the crown mirror-symmetric)
                ym = t + (s.band_top - t) * 0.40
                up = wedge(a, b, t, ym)
                lines += K.hatch_in(up, angle=0.0)
                xa, xb = _ray_x(v, a, ym), _ray_x(v, b, ym)
                lines += K.line(f"M{xa} {ym}L{xb} {ym}", K.FINE)
    lines += K.clip_out(K.outline(K.D(stone)), band, eps=-0.8, trap=0.0)   # the band's own line is the joint
    lines += K.outline(band_d)
    # jewel on the band: a small Source Rosette; the crown's lines break 3 px clear of it
    jy = s.band_top + s.band_h / 2
    jw = brow_jewel((cx, jy), s.jewel_r)
    lines = K.clip_out(lines, jw.shape, eps=0.0, trap=0.0, extra=jw.shape.buffer(4.3 + 2 * K.MEDIUM / 2))
    # studs: two dots either side on the band
    studs = C.Frag()
    for dx in (26.0, 44.0):
        for sg in (-1, 1):
            yy = s.band_top + s.band_h / 2 - s.band_bow * (1 - (dx / s.band_hw) ** 2)
            studs += K.dot((cx + sg * dx, yy), 6.3)
    return Part(shape.union(jw.shape), fills + jw.fills, lines + studs + jw.lines,
                {"band": band, "stone": stone, "blocks": blocks})


# =============================================================================
# orb
# =============================================================================
def vent_orb(c, r=32.0, bubble_d=14.0) -> Part:
    c = K.P(c)
    body = K.R(K.circle(c, r))
    neck_h = 5.0
    bc = c + K.P(0, -r - neck_h - bubble_d / 2)
    neck = K.box(c[0] - 3.2, c[1] - r - neck_h - 1.5, c[0] + 3.2, c[1] - r + 2)
    bub = K.R(K.circle(bc, bubble_d / 2 + K.MEDIUM / 2))
    shape = K.U(body, neck, bub)
    fills = K.fill(body, K.GOLD) + K.fill(neck, K.GOLD)
    lines = K.outline(K.circle(c, r)) + K.outline(K.D(neck))
    lines += K.line(K.circle(bc, bubble_d / 2), K.MEDIUM)
    # ripple latitudes (§G.8): three arcs across the sphere bowing down, the
    # gaps growing ×1.3, kept in the upper two-thirds (the hand holds the rest)
    ys = [c[1] - 9.0, c[1] + 0.0, c[1] + 11.7]
    for y in ys:
        dx = math.sqrt(max(r * r - (y - c[1]) ** 2, 0))
        lines += K.line(K.arc_sag((c[0] - dx, y), (c[0] + dx, y), -(4.5 + 0.1 * (y - c[1]))), K.FINE)
    return Part(shape, fills, lines, {"c": c, "r": r})


# =============================================================================
# sceptre
# =============================================================================
@dataclass
class SceptreSpec:
    x: float = 540.0
    hw: float = 11.0              # shaft half-width (the chert vesica keeps 4.2 from the edges)
    top: float = 160.0            # shaft top (under the knop)
    bottom: float = 532.0
    finial_c: tuple = (540.0, 114.0)
    finial_r: float = 29.0
    segments: int = 7
    collar_hw: float = 13.5
    collar_h: float = 7.0


def _segment_pattern(kind, x, y0, y1, hw):
    """Pattern inside one shaft segment (Aquifer on gold):
    'strata' — a course line with its thin course hatched;
    'chert'  — a vertical vesica (a chert nodule) on the axis;
    'marl'   — short horizontal dashes stacked (marl partings)."""
    f = C.Frag()
    ym = (y0 + y1) / 2
    if kind == "strata":
        ya, yb = ym - 6.0, ym + 6.0
        f += K.line(f"M{x - hw} {ya}L{x + hw} {ya}", K.FINE, style="rule")
        f += K.line(f"M{x - hw} {yb}L{x + hw} {yb}", K.FINE, style="rule")
        f += K.hatch_in(K.box(x - hw, ya, x + hw, yb), angle=-45.0)
    elif kind == "chert":
        h = (y1 - y0) / 2 - 7.0
        f += C.stroke(K.vesica((x, ym - h), (x, ym + h), 8.4), K.FINE, style="point")
    else:
        for yy in (ym - 9.0, ym, ym + 9.0):
            f += K.line(f"M{x - 3.2} {yy}L{x + 3.2} {yy}", K.MEDIUM)
    return f


def core_sceptre(s: SceptreSpec = SceptreSpec(), kinds=("marl", "strata", "chert")) -> Part:
    """The core sceptre (§H.1): a drill core in seven banded segments between
    gold collars — strata, chert vesicas, marl dashes, repeated — capped by a
    Source Rosette finial on a knop."""
    x = s.x
    shaft = K.box(x - s.hw, s.top, x + s.hw, s.bottom)
    fc = K.P(s.finial_c)
    fin = K.R(K.circle(fc, s.finial_r))
    knop_c = K.P(x, fc[1] + s.finial_r + 11.0)      # its top 1 px inside the finial rim
    knop = K.R(K.circle(knop_c, 12.0))
    seg_len = (s.bottom - s.top) / s.segments
    ys = [s.top + k * seg_len for k in range(s.segments + 1)]
    # collars: one under the knop, then gold rings between segments drawn as
    # lenticular bands (two arcs) slightly proud of the shaft
    collars = []
    shape = K.U(shaft, fin, knop)
    fills = K.fill(shape, K.GOLD)
    lines = C.Frag()
    lines += K.outline(K.D(shaft))
    for k in range(s.segments):
        y0 = ys[k] + s.collar_h / 2
        y1 = ys[k + 1] - s.collar_h / 2
        lines += _segment_pattern(kinds[k % len(kinds)], x, y0, y1, s.hw)
    for y in ys[1:-1]:                     # segment joints: double rules 4.2 clear
        for dy in (-3.15, 3.15):
            lines += K.line(f"M{x - s.hw} {y + dy}L{x + s.hw} {y + dy}", K.FINE, style="rule")
    lines += K.outline(K.D(knop))
    lines += K.outline(K.circle(fc, s.finial_r))
    lines += M.source_rosette(fc[0], fc[1], s.finial_r - K.CONTOUR / 2 - 4.2 - K.FINE / 2 - 0.1)
    return Part(shape, fills, lines, {"seg_len": seg_len, "ys": ys})


# =============================================================================
# the simplified Lion Mark clasp (§G.2) — drawn locally until deck.motifs has it
# =============================================================================
def lion_clasp(c, size=40.0, span=36.0) -> Part:
    """The simplified Lion Mark (§G.2) as a winged MORSE (the clasp of a
    mantle), ≤ 40 px tall, built so every gap honours §I.12 at this size:

    * mane — a ring of 12 scallops (arcs struck between cusps on r 16.6,
      each bulging to r 19.5), solid gold with a MEDIUM Aquifer contour;
    * face — a paper disc (r 10.5) knocked out of the gold, contoured, with
      two Ø4.2 Aquifer eye dots (3.1 px apart, 3.1 px inside the face line);
    * wings — the clasp's two arms, spread level across the lapels: an upper
      arc from behind the mane to a round tip ``span`` px out, and a lower
      edge of three scallops (the three primaries), solid gold with an
      Aquifer contour (gold on red only as contoured solids, §C.4); a short
      FINE feather line rises from each inner scallop cusp.
    Drawn locally until deck.motifs provides lion_mark()."""
    c = K.P(c)
    n = 12
    rc, rp = 16.6, 19.5
    cusps = [K.polar(c, rc, -90 + 15 + 30 * k) for k in range(n + 1)]
    p = K.Path(cusps[0])
    mid_r = rc * math.cos(math.radians(15))
    for a, b in zip(cusps[:-1], cusps[1:]):
        p.sag(b, rp - mid_r)             # bulge outward (clockwise ring: outward is screen-left)
    mane = K.R(p.close().d)
    face = shapely.Point(*c).buffer(10.5, quad_segs=32)
    wings, feathers = [], C.Frag()
    for sg in (-1, 1):
        root_up = c + K.P(sg * 12.0, -9.0)
        tip = c + K.P(sg * span, -8.0)
        root_lo = c + K.P(sg * 12.0, 9.0)
        # upper edge: an arc bulging up; lower edge: three scallops tip → root
        wp = K.Path(root_up).sag(tip, 4.0 * sg)
        pts = [tip + (root_lo - tip) * k / 3 for k in range(4)]
        for a, b in zip(pts[:-1], pts[1:]):
            wp.sag(b, 3.2 * sg)
        wd = wp.close().d
        w = K.R(wd).union(shapely.Point(*tip).buffer(4.2, quad_segs=16))
        wings.append(w)
        for q in pts[1:3]:
            up = q + K.P(sg * 2.0, -6.5)
            feathers += K.line(f"M{q[0]} {q[1]}L{up[0]} {up[1]}", K.FINE)
    shape = K.U(mane, *wings)
    gold = shape.difference(face)
    fills = K.fill(gold, K.GOLD)
    lines = K.outline(K.D(shape), K.MEDIUM) + K.outline(K.D(mane), K.MEDIUM)
    lines += K.outline(K.D(face), K.MEDIUM) + feathers
    for sg in (-1, 1):
        lines += K.dot(c + K.P(sg * 3.65, -1.0), 4.2)          # the eyes
    return Part(shape, fills, lines, {})
