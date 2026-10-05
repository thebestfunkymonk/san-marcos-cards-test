"""K♣ · the beard (brief §H.7: 'heavy-lidded, sage. A two-pointed beard of flat
comb sprays in gold').

The kit's forked beard SHAPE (it tucks under the moustache and clears the
mouth exactly like the K♠'s) cut into two lobes by a MEDIUM parting on the
axis, from under the lower lip to the fork. Each lobe is one flat §G.18 comb
spray: a FINE rachis from under the moustache tip down the middle of the lobe
to the point, and comb ticks on both sides swept down toward the point,
running out to the lobe's outline like hatch (butt caps, meeting the
contour's centreline): the hair combed out from a parting into two flat
points. Never a leaf or a fern: the outline stays a beard's, smooth, with no
serrations, and the cheeks stay plain gold between the sideburn and the
first tick.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C

P = K.P
FINE, MEDIUM, CONTOUR = T.FINE, T.MEDIUM, T.CONTOUR
GOLD = T.FOIL
GAP, GAP_MARK = K.GAP, K.GAP_MARK


def _pts(d, step=0.4):
    return C.sample_d(d, step)[0][0]


def spray_beard(fc, mo, *, side=(-42.0, 20.0), bulge=(-47.0, 76.0), tip=(-17.0, 130.0), notch_dy=104.0,
                rachis=((-28.0, 70.0), (-27.0, 98.0), (-18.0, 121.0)), angle=32.0, pitch=7.0, parting=True,
                terminal=True, tick_from=4.0, tick_to=4.0, rachis_top=0.0, inner=True, outer=True,
                min_tick=5.0) -> K.Part:
    """→ Part (shape, gold fill, lines). Points are (dx from the face axis,
    dy from the egg centre). ``angle``: ticks' angle to the rachis (small =
    long flowing strands). ``pitch``: perpendicular spacing between ticks
    (7.0, the hatch pitch)."""
    b = K.beard(fc, K.BeardSpec(side=side, bulge=bulge, tip=tip, notch_dy=notch_dy, lines=3), mo=mo)
    a = fc.anchors
    ax = float(a["axis"])
    cx, cy = a["center"]
    half = b.shape.intersection(K.box(0, 0, ax, 2000))
    half = max(K._polys_of(half), key=lambda g: g.area)
    lines = C.Frag()
    # the lobe zone: the left half; the axis is the parting (drawn MEDIUM),
    # so ticks butt on it like on the outline
    zone = half
    if mo is not None:
        zone = zone.difference(mo.shape.buffer(MEDIUM / 2 + GAP + FINE / 2))
    r0, r1, r2 = [P(ax + x, cy + y) for x, y in rachis]
    rp = _pts(K.arc3(r0, r1, r2), 0.4)
    if rachis_top:
        t0 = rp[1] - rp[0]
        t0 = t0 / np.hypot(*t0)
        rp = np.vstack([rp[0] - t0 * rachis_top, rp])
    rz = zone.buffer(-(MEDIUM / 2 + GAP_MARK + FINE / 2 + 0.1))
    rl = LineString(rp).intersection(rz)
    segs = sorted(K._lines_of(rl), key=lambda g: -g.length)
    if not segs:
        return b
    rp = np.asarray(segs[0].coords)
    lines += K.line(rp, FINE, role="rachis")
    end = rp[-1]
    if terminal:
        lines += K.dot(end, K.TD, role="terminal")
    cv = K.G.Curve(rp)
    L = cv.length
    sa = math.sin(math.radians(angle))
    step = pitch / sa                       # along the rachis: ticks 7 px apart, perpendicular
    tick_zone = zone.buffer(-0.01)
    stop = L - (K.TD / 2 + GAP_MARK + FINE / 2 + 0.5 if terminal else tick_to)
    ss = np.arange(tick_from, stop, step)
    for s in ss:
        p = cv.at_s(s)
        t = cv.tangent_s(s)
        a0 = math.atan2(t[1], t[0])
        for sd, on in ((1, outer), (-1, inner)):
            if not on:
                continue
            # travelling down the rachis (toward the point), the outer edge is
            # screen-right of travel on the left lobe (+x is inward)... pick by x
            ang = a0 + sd * math.radians(angle)
            u = np.array([math.cos(ang), math.sin(ang)])
            ln = LineString([tuple(p), tuple(p + u * 120.0)]).intersection(tick_zone)
            pieces = [g for g in K._lines_of(ln) if g.distance(Point(*p)) < 0.6]
            if not pieces:
                continue
            q = np.asarray(pieces[0].coords)
            if LineString(q).length < min_tick:
                continue
            q[0] = p                                  # start ON the rachis centreline (they touch)
            lines += K.line(q, FINE, style="hatch", role="tick")
    lines = lines + lines.mirror_x(ax)
    if parting:
        # the parting: the lobes' inner edges continued up the axis to below the lip
        top = a["lip_y"] + 8.2 + 3.0
        nb = cy + notch_dy
        lines += K.seg(P(ax, top), P(ax, nb - 1.0), MEDIUM, role="parting")
    return K.Part(b.shape, K.fill(b.shape, GOLD), lines + K.outline(b.shape), dict(b.meta))


def spray_lines_beard(fc, mo, *, side=(-42.0, 20.0), bulge=(-47.0, 76.0), tip=(-17.0, 130.0), notch_dy=104.0,
                      n=2, first=9.0, pitch=14.0, tick=5.5, tick_angle=50.0, tick_pitch=6.5, stagger=10.0,
                      tick_start=14.0, both=True) -> K.Part:
    """Variant: the beard's lines ARE comb sprays (§G.18) — as the K♠'s beard
    is drawn in current lines, this one is drawn in ``n`` sprays per lobe:
    rachises that are offsets of the outer edge ``pitch`` apart, flowing
    from the cheek to the point and rolling into Ø6.3 terminals (the cones),
    each carrying short ticks on both sides swept toward the point."""
    b = K.beard(fc, K.BeardSpec(side=side, bulge=bulge, tip=tip, notch_dy=notch_dy, lines=3), mo=mo)
    a = fc.anchors
    ax = float(a["axis"])
    cx, cy = a["center"]
    half = b.shape.intersection(K.box(0, 0, ax, 2000))
    half = max(K._polys_of(half), key=lambda g: g.area)
    S = P(ax + side[0], cy + side[1])
    Bg = P(ax + bulge[0], cy + bulge[1])
    Ft = P(ax + tip[0], cy + tip[1])
    gpts = _pts(K.arc3(S, Bg, Ft), 0.4)
    t0 = gpts[1] - gpts[0]
    t0 = t0 / np.hypot(*t0)
    gpts = np.vstack([gpts[0] - t0 * 30.0, gpts])
    rl = K.current_lines(gpts, n, half, side=+1, first=first, pitch=pitch, edge=MEDIUM, stagger=stagger,
                         end="dot")
    lines = C.Frag() + rl
    sa = math.sin(math.radians(tick_angle))
    inner = half.buffer(-(MEDIUM / 2 + GAP_MARK + FINE / 2 + 0.2))
    for q in rl.meta["lines"]:
        cv = K.G.Curve(np.asarray(q))
        L = cv.length
        step = max(tick_pitch, (FINE + GAP + 0.3) / sa)
        for s in np.arange(tick_start, L - (K.TD / 2 + GAP_MARK + 3.0), step):
            p = cv.at_s(s)
            t = cv.tangent_s(s)
            a0 = math.atan2(t[1], t[0])
            for sd in ((1, -1) if both else (1,)):
                ang = a0 + sd * math.radians(tick_angle)
                u = np.array([math.cos(ang), math.sin(ang)])
                ln = LineString([tuple(p), tuple(p + u * tick)]).intersection(inner)
                pcs = [g for g in K._lines_of(ln) if g.distance(Point(*p)) < 0.6]
                if pcs and pcs[0].length > 3.0:
                    qq = np.asarray(pcs[0].coords)
                    qq[0] = p
                    lines += K.line(qq, FINE, role="tick")
    lines = lines + lines.mirror_x(ax)
    return K.Part(b.shape, K.fill(b.shape, GOLD), lines + K.outline(b.shape), dict(b.meta))
