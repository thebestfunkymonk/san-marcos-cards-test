"""art/_jc_garments.py — J♣ · The River Squire: the whole-card textiles.

The red jerkin and its skirt run from one figure's shoulders to the other's, so they are drawn once as
a point-symmetric (C2) region about the card centre (375, 525): the top figure's half is built here, its
180° copy is the other figure's, and the diagonal seam only marks where the copy takes over. The pecan
sprigs knocked out of the red sit on a half-drop lattice that is its own 180° copy.
"""
from __future__ import annotations

import math

import numpy as np
import shapely

from deck import courtkit as K
from deck.motifs import core as C
from art import _jc_body as B

AX, CY = K.AX, 525.0
FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def c2_frag(f):
    return f + K.rot180(f)


# the jerkin's top half: neckline, the far (viewer's-left) armhole edge down to the waist, the peplum that
# flares from under the belt to a vertical tangent on the centre row, and the near armhole edge back up.
# x_left(525) + x_right(525) = 750, so the 180° copy continues both edges.
JERK_NECK = [(342, 301), (304, 306), (276, 316)]
JERK_L = [(276, 316), (268, 346), (272, 390), (278, 428)]
JERK_L_LOW = ("S", [(278, 428), (268, 466), (256, 525)], 108.0, 90.0)
JERK_R_LOW = ("S", [(494, 525), (486, 480), (476, 432)], -90.0, -122.0)
JERK_R_HIGH = [(476, 432), (480, 408), (489, 385), (498, 362), (504, 340), (500, 314)]
JERK_SHOULDER_R = [(500, 314), (464, 305), (418, 300)]


def jerkin_half():
    return B.region(JERK_NECK, JERK_L, JERK_L_LOW, ("L", [(256, 525), (494, 525)]), JERK_R_LOW, JERK_R_HIGH,
                    JERK_SHOULDER_R, ("L", [(418, 300), (342, 301)]))


def jerkin_whole(vee):
    half = jerkin_half()
    whole = K.U(half, rot(half)).buffer(0.01).buffer(-0.01)
    return whole.difference(K.U(vee, rot(vee)))


# ---- quilted trellis with a pecan sprig in each cell ---------------------------------------------------
def trellis_lines(zone, hx, hy, w=MEDIUM, min_len=10.0):
    """Both diagonal families of the trellis dx/hx ± dy/hy = k (dx, dy from the card centre), clipped to
    ``zone``. The line set is its own 180° copy, so one pass over the whole card is C2."""
    out = C.Frag()
    reach = 1400.0
    for fam in (+1, -1):
        for k in range(-40, 41):
            a = K.P(AX + k * hx - reach * hx / hy * 0.0, CY)
            d = K.P(hx, -fam * hy) / math.hypot(hx, hy)
            seg = shapely.LineString([a - d * reach, a + d * reach]).intersection(zone)
            for g in K._lines_of(shapely.line_merge(seg) if seg.geom_type == "MultiLineString" else seg):
                if g.length >= min_len:
                    out += K.line(C.polyline_d(np.asarray(g.coords)), w, role="trellis")
    return out


def trellis_sprigs(allowed, *, hx, hy, heading, leaf_kw, nut, nut_spread, line_w=MEDIUM, clear=5.0, margin=3.0):
    """A pecan leaf in every trellis cell and a pair of gold nuts hanging at every trellis node, kept whole
    inside ``allowed`` and ``clear`` px from the trellis lines (a nearer leaf would be healed away). Cell
    centres are (AX + (j + ½)·hx, CY + i·hy) and (AX + j·hx, CY + (i + ½)·hy), nodes (AX + j·hx, CY + i·hy)
    and (AX + (j + ½)·hx, CY + (i + ½)·hy): both lattices are their own 180° copy. Only those above the
    centre row are built here, the rest are their rot180. → (leaf Frag, nut Frag, nut hulls) for the whole card."""
    L = leaf_kw.get("length", 60.0)
    inner = K.R(allowed).buffer(-margin)
    lines = trellis_lines(inner.buffer(40.0), hx, hy, line_w, min_len=0.0).shape().buffer(clear)
    leaves, nuts, zone = C.Frag(), C.Frag(), []
    for i2 in range(-60, 1):
        cy = CY + i2 * hy / 2.0
        if cy < 100:
            continue
        for j2 in range(-30, 31):
            cx = AX + j2 * hx / 2.0
            if i2 == 0:
                continue
            cell = (i2 + j2) % 2 != 0
            if cell:
                base = K.P(cx, cy) - K.unit(heading) * L / 2
                lf, _, _ = B.pecan_sprig(base, heading, leaf_kw=leaf_kw, nut=nut, nut_spread=nut_spread)
                sh = lf.shape()
                if inner.contains(sh) and inner.contains(rot(sh)) and not sh.intersects(lines):
                    leaves += K.atomic(lf, f"lf{j2}_{i2}")
            else:
                base = K.P(cx, cy) - K.unit(heading) * 0.3 * 9.0 - K.P(0, 13.0)
                _, nf, nr = B.pecan_sprig(base, heading, leaf_kw=leaf_kw, nut=nut, nut_spread=nut_spread)
                if inner.contains(nr.buffer(FINE)) and inner.contains(rot(nr.buffer(FINE))):
                    nuts += K.atomic(nf, f"nt{j2}_{i2}")
                    zone.append(nr.convex_hull)
    hulls = shapely.unary_union(zone + [rot(z) for z in zone]) if zone else shapely.Polygon()
    return c2_frag(leaves), c2_frag(nuts), hulls
