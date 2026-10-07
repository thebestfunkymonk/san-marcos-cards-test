"""QS whole-card textiles: the jade barrel mantle, the red lining lens and the paper gown.

Every region is C2 about (375, 525) by construction (a function of y that is odd about the
centre for the axis and even for the half-widths, or a top half united with its 180° copy), so
the seam is only the place where the rotated copy takes over. Patterns are drawn once on the
top-half rows of a grid whose rows are C2 partners of each other, then rotated.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import shapely
from scipy.interpolate import PchipInterpolator
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG
from inkkit import geom as G
from art import _qs_body as B
from art import _qs_garb as GB

AX, CY = K.AX, 525.0
BORDER = 30.0
KARST_PITCH = (22.0, 17.0)
SLOPE = 0.0568                       # the body axis: x = 375 - SLOPE (y - 525), through the neck at (388, 296)

MANTLE_PTS = [(388, 300), (340, 306), (286, 312), (236, 322), (200, 340), (176, 376), (158, 424), (148, 480),
              (146, 525), (146, 620), (604, 620), (604, 525), (603, 480), (598, 424), (594, 376), (574, 340),
              (538, 322), (488, 312), (436, 306)]
# lining outer half-width about the axis (y, h); even about y = 525
LINING_KNOTS = [(298, 15.0), (303, 38.0), (310, 60.0), (330, 73.0), (360, 83.0), (400, 93.0), (450, 99.0),
                (525, 103.0)]
GOWN_W = (13.0, 24.0)                # half-width at the neck / at the centre (flat at the centre)


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def axis_x(y):
    return AX - SLOPE * (np.asarray(y, float) - CY)


def c2_frag(f: C.Frag) -> C.Frag:
    """``f`` plus its 180° partner; atomic-motif keys of the partner get a suffix so covering one
    copy never deletes the other."""
    r = K.rot180(f)
    marks = [replace(m, role=m.role + "~") if "@" in m.role else m for m in r.marks]
    return f + C.Frag(marks, r.meta)


def mantle():
    top = K.R(B.cspline(MANTLE_PTS)).buffer(0)
    return K.U(top, rot(top))


def _half_width_fn():
    ys = np.array([k[0] for k in LINING_KNOTS], float)
    hs = np.array([k[1] for k in LINING_KNOTS], float)
    ys_all = np.concatenate([ys, 1050.0 - ys[::-1][1:]])
    hs_all = np.concatenate([hs, hs[::-1][1:]])
    return PchipInterpolator(ys_all, hs_all)


def lining():
    """The red lining lens: even half-width about the axis, widest (vertical tangent) at the centre."""
    h = _half_width_fn()
    ys = np.linspace(298.0, 752.0, 400)
    x = axis_x(ys)
    left = np.column_stack([x - h(ys), ys])
    right = np.column_stack([x + h(ys), ys])[::-1]
    return Polygon(np.vstack([left, right])).buffer(0)


def gown():
    ys = np.linspace(296.0, 754.0, 300)
    s = (CY - ys) / (CY - 296.0)
    w = GOWN_W[1] - (GOWN_W[1] - GOWN_W[0]) * np.minimum(np.abs(s), 1.0) ** 2
    x = axis_x(ys)
    return Polygon(np.vstack([np.column_stack([x - w, ys]), np.column_stack([x + w, ys])[::-1]])).buffer(0)


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
    """Drop stroke pieces with an end within ``margin`` of the seam: the half's clip would cut them
    a hair short of their junction."""
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


def _group_centre_y(f: C.Frag):
    """Atomic-motif key -> mean y of its marks' bounds."""
    ys = {}
    for m in f.marks:
        if "@" not in m.role or not m.d:
            continue
        b = G.to_shape(m.d, tol=0.1).bounds if m.kind == "fill" else shapely.union_all(
            [LineString(np.vstack([p, p[:1]]) if cl else p) for p, cl in G.flatten(m.d, 0.1) if len(p) > 1]).bounds
        ys.setdefault(m.role.split("@")[1], []).append((b[1] + b[3]) / 2.0)
    return {k: float(np.mean(v)) for k, v in ys.items()}


def karst(region, *, pitch=(28.0, 22.0), seed=1983):
    """§G.12 voids on a grid whose rows are C2 partners (row k above the centre pairs with row k
    below it): drawn on ``region`` (a C2 region), the rows above the centre are kept and rotated."""
    px, py = pitch
    f = K.pattern(region, "karst", origin=(AX - px / 4.0, CY - py / 2.0), pitch=pitch, seed=seed, weights=(0.15, 0.35, 0.50))
    cy = _group_centre_y(f)
    top = C.Frag([m for m in f.marks if ("@" in m.role and cy.get(m.role.split("@")[1], 1e9) < CY)])
    return c2_frag(top)


def drip_field(region, *, pitch=(30.0, 38.0), length=(9.0, 15.0)):
    """§G.14 single drips (FINE stroke into a Ø6.3 terminal) on a C2 half-drop grid; the rows
    above the centre are kept and rotated."""
    px, py = pitch
    f = GB.drops(region, pitch=pitch, origin=(AX - px / 4.0, CY - py / 2.0), length=length)
    cy = _group_centre_y(f)
    top = C.Frag([m for m in f.marks if ("@" in m.role and cy.get(m.role.split("@")[1], 1e9) < CY)])
    return c2_frag(top)


def lining_columns(*, r=(2.8, 4.4), fracs=(0.34, 0.68), y0=332.0):
    """Knocked-out water drops in columns across the red lining of the top half (graduated toward
    the centre); returns the union of their shapes (top half only)."""
    h = _half_width_fn()
    holes = []
    band = lining().difference(gown()).intersection(K.box(0, 0, 750, CY))
    for side in (-1, 1):
        for fr in fracs:
            pts = []
            for y in np.linspace(y0, CY - 6.0, 24):
                x0 = float(axis_x(y))
                w = GOWN_W[1] - (GOWN_W[1] - GOWN_W[0]) * min(abs((CY - y) / (CY - 296.0)), 1.0) ** 2
                pts.append((x0 + side * (w + fr * (float(h(y)) - w)), y))
            holes.append(GB.drop_column(band, pts, r=r, gap=3.0))
    return K.U(*[g for g in holes if not g.is_empty])


def gown_marks():
    """The gown's paper detail (top half): a FINE fold on the axis and a dotted seam that
    converges on it at the centre (odd about the centre, so the partner continues it)."""
    f = C.Frag()
    ys = np.linspace(352.0, 698.0, 120)
    f += K.line(C.polyline_d(np.column_stack([axis_x(ys), ys])), K.FINE, role="gown-fold")
    return f


def seam_dots(y_top=364.0, step=10.0, off=9.0):
    """Dots down the gown: offset from the axis by ``off`` at the neck, crossing it at the centre."""
    f = C.Frag()
    y = y_top
    while y <= 686.0:
        d = off * (CY - y) / (CY - y_top)
        f += K.dot((float(axis_x(y)) + d, y), K.TD, role="seam-dot")
        y += step
    return f


def garments(front, *, sleeves, bands, band_lines, drips, sleeve_grain, sleeve_edges, seam=None):
    """The whole-card robe: jade barrel mantle (karst voids inside a hatched border), the red
    lining (water-drop columns + hatch), the paper gown and the jade sleeves, all as one C2 set.
    ``front``: shapes of the items drawn over it (head, hands, attributes)."""
    sleeve_zone = K.c2(sleeves)
    band_zone = K.c2(bands)
    shape = K.U(mantle(), sleeve_zone)
    shape = K.U(shape, shape.buffer(12).buffer(-12).intersection(sleeve_zone.buffer(30)))
    gown_r = gown().intersection(shape)
    lin = lining().intersection(shape)
    red = lin.difference(gown_r).difference(sleeve_zone)
    jade = shape.difference(red).difference(gown_r)
    jade_fill = jade.difference(band_zone.buffer(-0.4))
    blockers = K.c2(front)

    # ---- jade: hatched border, FINE seam, karst voids inside ---------------------------
    inner_shape = mantle().buffer(-BORDER, quad_segs=16)
    border = jade.difference(inner_shape).difference(sleeve_zone)
    seam_line = K.outline(inner_shape, K.FINE, role="seam")
    seam_line = K.clip_in(seam_line, jade.buffer(-0.2).difference(sleeve_zone.buffer(0.4)))
    border_hatch = drop_short(K.hatch_in(border.buffer(0.25), angle=45.0, origin=(AX, CY)), 24.0)
    field = jade.intersection(inner_shape).difference(sleeve_zone.buffer(5.0)).difference(red.buffer(3.0))
    voids = karst(field, pitch=KARST_PITCH)
    drip_marks = drip_field(field)
    drip_marks = K.clip_out(drip_marks, voids.shape().buffer(K.MIN_CLEAR if hasattr(K, "MIN_CLEAR") else 4.2),
                            eps=0.0, trap=0.0)
    voids = K.clip_out(voids + drip_marks, blockers.buffer(6.0), eps=0.0, trap=0.0)

    # ---- red lining: water-drop columns knocked out, hatch between --------------------------
    cols = lining_columns()
    cols = K.U(cols, rot(cols))
    cols = cols.intersection(red.buffer(-1.0)) if not cols.is_empty else cols
    red_hatch = K.hatch_in(red, angle=-45.0, origin=(AX, CY))
    red_hatch = drop_short(K.clip_out(red_hatch, K.U(cols.buffer(3.4), blockers.buffer(4.0)) if not cols.is_empty
                                      else blockers.buffer(4.0), eps=0.0, trap=0.0), 12.0)
    red_fill = red.difference(cols) if not cols.is_empty else red

    # ---- gown ------------------------------------------------------------------------------
    gline = gown_marks()
    dots = seam_dots()

    drip_zone = K.c2(drips)
    fills = K.fill(jade_fill.difference(drip_zone), K.JADE) + K.fill(red_fill, K.RED) + K.fill(band_zone, K.RED)
    lines = K.outline(shape) + K.outline(red) + K.outline(gown_r)
    lines += seam_line + border_hatch + voids + red_hatch + gline + dots
    lines += K.c2(sleeve_grain) + K.c2(sleeve_edges) + K.c2(band_lines)
    return K.Part(shape, fills, lines, {"jade": jade, "red": red, "gown": gown_r})
