"""Card back wild-rice sheaf (brief §H.19 "wild-rice pinwheel", §G.4, §G.5).

Texas wild-rice grows in the current: its ribbon leaves stream downstream
while the flowering culm stands up out of the water.  The 10 o'clock sheaf
rises from the orbit beside the Source and streams clockwise up the lens
wall -- three half-hatched ribbon leaves (§G.4: S midrib, vesica profile
10-14 : 1, one half hatched perpendicular to the midrib) and one flowering
stalk (§G.5: erect female spikelets toward the tip, drooping male florets
below).  The 4 o'clock sheaf is its 180° copy: the two blades of the
pinwheel.

Leaves are listed back to front; each later element hides the earlier ones
by T-junction (the front contour's centreline ends the lines behind it).
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import Polygon

from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms
from deck.motifs.forms import unit
from deck.motifs.rice import spikelet
from inkkit import geom as G

from art import _back_geo as BG

FINE, HAIR = T.FINE, T.HAIRLINE


def ribbon_hw(L: float, W: float, peak: float = 0.42, base: float = 0.0):
    """Half-width profile of a ribbon leaf: two circular-ish arcs meeting at
    ``peak`` (fraction of L) -- a vesica leaned toward the base, so the
    blade runs long and fine to its tip.  ``base`` keeps a little width at
    s = 0 (the sheath)."""
    hw0 = W / 2

    def hw(s):
        s = np.asarray(s, float)
        u = np.clip(s / L, 0, 1)
        a = np.where(u < peak, u / peak, (1 - u) / (1 - peak))
        # circular-arc profile on each side of the peak (vesica-like)
        prof = np.sqrt(np.clip(1 - (1 - a) ** 2, 0, 1))
        out = hw0 * prof
        if base:
            out = np.where(u < peak, np.maximum(out, base * hw0 * (1 - u / peak) + out * (u / peak)), out)
        return out
    return hw


def leaf_mid(way, h0=None, h1=None):
    """Arc spline through polar stations; ``h1`` is the end heading measured
    off the clockwise tangent at the last station (+ = turning outward)."""
    if h1 is not None:
        h1 = BG.cw(way[-1][1]) - h1
    _, pts = BG.pspline(way, h0, h1)
    return pts


def ribbon(mid, width, hatch=1, peak=0.42, **kw) -> C.Frag:
    cv = G.Curve(np.asarray(mid, float))
    hw = ribbon_hw(cv.length, width, peak)
    return forms.leaf(mid, hw=hw, hatch=hatch, midrib="full", midrib_min_hw=FINE + 4.2,
                      midrib_trim=(0.0, 0.10), **kw)


def panicle(mid, *, n_female=6, n_male=4, sl=16.0, awn=12.0, pedicel=6.0, f_pitch=11.0, m_pitch=12.5,
            gap=9.0, side0=1, f_spread=70.0, m_spread=95.0) -> C.Frag:
    """§G.5 along the end of centreline ``mid`` (base -> tip): a terminal
    spikelet, erect female spikelets toward the tip (3 : 1 vesicas, axes
    ±15° off the stalk, on pedicels, one HAIRLINE awn), drooping male florets
    below them (±150°).  Returns the Frag; meta['s_low'] = arc length of the
    lowest floret."""
    cv = G.Curve(np.asarray(mid, float))
    L = cv.length
    f = C.Frag()
    tp, td = cv.at_s(L), cv.tangent_s(L)
    f += spikelet(tp, math.degrees(math.atan2(td[1], td[0])), sl, awn=awn)
    side, s = side0, L - f_pitch * 0.9
    for _ in range(n_female):
        p, t = cv.at_s(s), cv.tangent_s(s)
        a = math.degrees(math.atan2(t[1], t[0]))
        q = p + unit(a - side * f_spread) * pedicel
        f += C.stroke(C.polyline_d([p, q]), FINE, role="pedicel")
        f += spikelet(q, a - side * 15.0, sl, awn=awn)
        side, s = -side, s - f_pitch
    s -= gap
    for _ in range(n_male):
        p, t = cv.at_s(s), cv.tangent_s(s)
        a = math.degrees(math.atan2(t[1], t[0]))
        q = p + unit(a - side * m_spread) * pedicel
        f += C.stroke(C.polyline_d([p, q]), FINE, role="pedicel")
        f += spikelet(q, a - side * 150.0, sl * 0.9)
        side, s = -side, s - m_pitch
    f.meta["s_low"] = s + m_pitch
    return f


# ---------------------------------------------------------------------------
# the 10 o'clock sheaf (its 180° copy is the 4 o'clock one)
# waypoints are (r, clock) about the card centre; clock 0 = 12 o'clock,
# increasing clockwise.
# ---------------------------------------------------------------------------
SHEAF = dict(
    # the culm: root beside the orbit at ~8:20, up the wall behind the blades, then turning
    # clockwise so the panicle stands in the open, pointing into the top of the lens
    culm=dict(way=[(166.0, 248.0), (190.0, 264.0), (206.0, 283.0), (226.0, 300.0), (256.0, 314.0),
                   (282.0, 325.0), (302.0, 335.0), (318.0, 344.0), (330.0, 351.0)],
              panicle=dict(n_female=8, n_male=4, m_pitch=15.0), panicle_len=132.0),
    # blades spring from the culm at arc length ``at`` (heading ``dh`` degrees inward of the culm)
    # and stream clockwise through polar stations; h1 = end heading off the clockwise tangent
    leaves=[
        dict(at=150.0, dh=14.0, way=[(240.0, 318.0), (250.0, 330.0), (258.0, 339.0)], h1=16.0, w=30.0,
             hatch=-1),
        dict(at=80.0, dh=20.0, way=[(198.0, 300.0), (206.0, 320.0), (224.0, 338.0), (246.0, 350.0)], h1=22.0,
             w=32.0, hatch=-1),
        dict(at=14.0, dh=26.0, way=[(170.0, 270.0), (172.0, 294.0), (178.0, 316.0), (188.0, 335.0),
                                    (200.0, 349.0)], h1=28.0, w=32.0, hatch=-1),
    ],
)


def sheaf(spec=SHEAF) -> C.Frag:
    """Culm + panicle behind, leaves in front (listed back to front)."""
    cu = spec["culm"]
    cmid = leaf_mid(cu["way"])
    cv = G.Curve(cmid)
    L = cv.length
    f = C.stroke(C.polyline_d(cmid), FINE, role="culm")
    f += panicle(cv.sub(1 - cu["panicle_len"] / L, 1.0).pts, **cu.get("panicle", {}))
    p0 = cv.at_s(0.0)
    f += C.dot(p0[0], p0[1], T.TERMINAL_D, role="terminal")
    for lf in spec["leaves"]:
        s0 = lf["at"]
        p, t = cv.at_s(s0), cv.tangent_s(s0)
        h0 = math.degrees(math.atan2(t[1], t[0])) + lf["dh"]
        h1 = BG.cw(lf["way"][-1][1]) - lf["h1"]
        _, mid = BG.pspline([("xy", p[0], p[1])] + list(lf["way"]), h0, h1)
        g = ribbon(mid, lf["w"], lf.get("hatch", 1), lf.get("peak", 0.42))
        f = C.occlude(f, Polygon(g.meta["outline"]).buffer(0))
        f += g
    return f
