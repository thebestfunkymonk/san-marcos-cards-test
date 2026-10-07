"""art/_js_garment.py — J♠'s belt and buckle: a gold band set with karst-void rings (§G.12) in Aquifer FINE,
and the clasp that interrupts it (§H.3)."""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG

MEDIUM, FINE, CONTOUR = K.MEDIUM, K.FINE, K.CONTOUR


def belt(torso_shape, y0, y1, *, color=K.GOLD, voids=(16.0, 6.0, 10.0, 6.0), gap=5.0, xc=None):
    """A gold belt band y0–y1 across the torso, set with a running row of
    karst-void rings (Aquifer FINE) on its centre line. → Part."""
    band = torso_shape.intersection(K.box(0, y0, 2000, y1)).buffer(0)
    band = max(K._polys_of(band), key=lambda p: p.area)
    lines = K.outline(band)
    x0, _, x1, _ = band.bounds
    ym = (y0 + y1) / 2
    room = band.buffer(-(MEDIUM / 2 + K.GAP_MARK + FINE / 2))
    xs = []
    x = (x0 + x1) / 2 if xc is None else xc
    # lay voids outward from the centre both ways (the row reads symmetric at the buckle)
    seq = list(voids)
    out = C.Frag()
    placed = []
    for sgn in (+1, -1):
        k = 0
        xx = x if sgn > 0 else x - (MG.KARST_ASPECT * seq[0] / 2 + gap + MG.KARST_ASPECT * seq[-1] / 2)
        kk = 0 if sgn > 0 else len(seq) - 1
        while x0 < xx < x1:
            d = seq[kk % len(seq)]
            rx = MG.KARST_ASPECT * d / 2
            ell = shapely.affinity.scale(Point(xx, ym).buffer(1.0, quad_segs=32), rx + FINE / 2, d / 2 + FINE / 2)
            if room.contains(ell):
                out += K.atomic(MG.karst_void(xx, ym, d), f"belt{sgn}{k}")
            nd = seq[(kk + sgn) % len(seq)]
            xx += sgn * (rx + gap + FINE + MG.KARST_ASPECT * nd / 2)
            kk += sgn
            k += 1
    return K.Part(band, K.fill(band, color), lines + out, {"band": band})


def buckle(c, w=34.0, h=46.0, *, color=K.GOLD):
    """The belt's buckle, a gold clasp (§C.1): a rounded frame with its
    opening (an Aquifer MEDIUM inner frame) and the tongue bar across it."""
    c = K.P(c)
    outer = K.R(K.rrect(c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2, 7.0))
    iw, ih = w - 16.0, h - 18.0
    inner_d = K.rrect(c[0] - iw / 2, c[1] - ih / 2, c[0] + iw / 2, c[1] + ih / 2, 3.5)
    lines = K.outline(outer) + K.outline(inner_d, MEDIUM, role="buckle")
    lines += K.seg((c[0], c[1] - ih / 2), (c[0], c[1] + ih / 2), MEDIUM, role="tongue")
    return K.Part(outer, K.fill(outer, color), lines, {})
