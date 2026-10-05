"""Card back wild-rice sheaf (brief §H.19 "wild-rice pinwheel", §G.4, §G.5).

Texas wild-rice grows in the current: its ribbon leaves stream downstream
while the flowering culm stands up out of the water.  The 10 o'clock sheaf
rises from a crown beside the Source at about 8 o'clock: its culm climbs the
lens wall and carries the panicle up into the top of the lens beside the
cypress twig, and three ribbon leaves (§G.4: an S midrib, a lanceolate
vesica profile 10-14 : 1 with true points at both ends, split on the midrib,
one half hatched perpendicular to it) spring from the culm and stream
clockwise round the Source.  The flowering stalk (§G.5) has erect female
spikelets toward the tip and drooping male florets below them.  The 4
o'clock sheaf is its 180° copy: the two blades of the pinwheel.

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
from deck.motifs.forms import arc_spline, unit
from deck.motifs.rice import spikelet
from inkkit import geom as G

from art import _back_geo as BG

FINE, HAIR = T.FINE, T.HAIRLINE


def lance_hw(L: float, W: float, peak: float = 0.32):
    """Lanceolate half-width: an asymmetric vesica -- two circular arcs of
    different chords meeting (tangent, at full width) at ``peak`` x L, so
    both the base and the long tip are true points (§G.4 vesica profile)."""
    h = W / 2.0
    a1, a2 = peak * L, (1.0 - peak) * L
    R1 = (a1 * a1 + h * h) / (2 * h)
    R2 = (a2 * a2 + h * h) / (2 * h)

    def hw(s):
        s = np.asarray(s, float)
        d = s - a1
        out = np.where(d < 0, np.sqrt(np.maximum(R1 * R1 - d * d, 0.0)) - (R1 - h),
                       np.sqrt(np.maximum(R2 * R2 - d * d, 0.0)) - (R2 - h))
        return np.maximum(out, 0.0)
    return hw


def ribbon(mid, width, hatch=1, peak=0.30) -> C.Frag:
    cv = G.Curve(np.asarray(mid, float))
    hw = lance_hw(cv.length, width, peak)
    return forms.leaf(mid, hw=hw, hatch=hatch, midrib="full", midrib_min_hw=FINE + 4.2,
                      midrib_trim=(0.0, 0.10))


def panicle(mid, *, n_female=7, n_male=4, sl=15.0, awn=12.0, pedicel=6.0, f_pitch=11.0, m_pitch=13.0,
            gap=10.0, side0=1, f_spread=70.0, m_spread=100.0, f_angle=15.0, m_angle=150.0,
            m_pedicel=None) -> C.Frag:
    """§G.5 along the end of centreline ``mid`` (base -> tip): a terminal
    spikelet, erect female spikelets toward the tip (3 : 1 vesicas, axes
    ±15° off the stalk, on pedicels, one HAIRLINE awn), drooping male florets
    below them (±150°).  meta['s_low'] = arc length of the lowest floret."""
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
        f += spikelet(q, a - side * f_angle, sl, awn=awn)
        side, s = -side, s - f_pitch
    s -= gap
    for _ in range(n_male):
        p, t = cv.at_s(s), cv.tangent_s(s)
        a = math.degrees(math.atan2(t[1], t[0]))
        q = p + unit(a - side * m_spread) * (m_pedicel or pedicel)
        f += C.stroke(C.polyline_d([p, q]), FINE, role="pedicel")
        f += spikelet(q, a - side * m_angle, sl * 0.9)
        side, s = -side, s - m_pitch
    f.meta["s_low"] = s + m_pitch
    return f


def spline(pts, h0=None, h1=None):
    _, P, _ = arc_spline([np.asarray(p, float) for p in pts], h0, h1)
    return P


# ---------------------------------------------------------------------------
# the 10 o'clock sheaf (its 180° copy is the 4 o'clock one); card px, y down
# ---------------------------------------------------------------------------
SHEAF = dict(
    # culm: from the crown at ~8 o'clock, hidden behind the blades, out to the lens wall
    # and up; its last ``panicle_len`` px carry the flowering spike, pointing into the top
    # of the lens beside the twig
    culm=dict(way=[(172.0, 240.0), (188.0, 262.0), (198.0, 285.0), (226.0, 304.0), (256.0, 318.0),
                   (283.0, 329.0), (309.0, 339.0)],
              panicle_len=160.0, panicle=dict(n_female=8, n_male=3, sl=16.0, f_pitch=11.5, m_pitch=15.0, gap=6.0,
                                             m_pedicel=10.0, m_spread=115.0)),
    # blades spring from the culm at arc length ``at`` and stream clockwise round the
    # Source through polar stations (r, clock); listed back to front
    leaves=[
        dict(at=95.0, way=[(226.0, 300.0), (240.0, 316.0), (248.0, 336.0)], w=27.0, hatch=1),
        dict(at=40.0, way=[(200.0, 272.0), (204.0, 296.0), (210.0, 322.0), (214.0, 344.0)], w=32.0, hatch=1),
        dict(at=4.0, way=[(172.0, 256.0), (174.0, 285.0), (176.0, 318.0), (178.0, 338.0), (179.0, 348.5)],
             w=32.0, hatch=1),
    ],
)


def _stem_d(cv, s0, s1, h, step=1.0):
    """Closed outline (centreline of the stroke) of a stem of half-width h
    along ``cv`` from arc length s0 to s1, with semicircular ends."""
    n = max(4, int((s1 - s0) / step))
    ss = np.linspace(s0, s1, n)
    P = np.array([cv.at_s(x) for x in ss])
    Tn = np.array([cv.tangent_s(x) for x in ss])
    N = np.stack([-Tn[:, 1], Tn[:, 0]], 1)
    left, right = P + h * N, P - h * N

    def cap(c, t, a_from):
        a = math.atan2(t[1], t[0])
        return [c + h * np.array([math.cos(a + a_from + k), math.sin(a + a_from + k)])
                for k in np.linspace(0.0, -math.pi, 13)[1:-1]]
    ring = list(left) + cap(P[-1], Tn[-1], math.pi / 2) + list(right[::-1]) + cap(P[0], -Tn[0], math.pi / 2)
    return C.polyline_d(np.array(ring), closed=True)


def _xy(q):
    return BG.pol(*q) if len(q) == 2 else q


def sheaf(spec=SHEAF) -> C.Frag:
    """Culm + panicle behind, leaves in front (listed back to front)."""
    cu = spec["culm"]
    cmid = spline([_xy(q) for q in cu["way"]], cu.get("h0"))
    cv = G.Curve(cmid)
    L = cv.length
    h = cu.get("stem")
    if h:
        # the culm below the panicle is a hollow stem: two FINE rules 2h apart with
        # round ends; the panicle's rachis rises from the apex of the upper end
        s_p = L - cu["panicle_len"] - h
        f = C.stroke(_stem_d(cv, 0.0, s_p, h), FINE, role="culm")
        f += C.stroke(C.polyline_d(cv.sub((s_p + h) / L, 1.0).pts), FINE, role="culm")
        f += panicle(cv.sub((s_p + h) / L, 1.0).pts, **cu.get("panicle", {}))
    else:
        f = C.stroke(C.polyline_d(cv.sub(0, 1.0).pts), FINE, role="culm")
        f += panicle(cv.sub(1 - cu["panicle_len"] / L, 1.0).pts, **cu.get("panicle", {}))
        p0 = cv.at_s(0.0)
        f += C.dot(p0[0], p0[1], T.TERMINAL_D, role="terminal")
    for lf in spec["leaves"]:
        s0 = lf["at"]
        p, t = cv.at_s(s0), cv.tangent_s(s0)
        h0 = math.degrees(math.atan2(t[1], t[0])) + lf["dh"] if "dh" in lf else None
        mid = spline([p] + [_xy(q) for q in lf["way"]], h0, lf.get("h1"))
        g = ribbon(mid, lf["w"], lf.get("hatch", 1), lf.get("peak", 0.30))
        f = C.occlude(f, Polygon(g.meta["outline"]).buffer(0))
        f += g
    return f
