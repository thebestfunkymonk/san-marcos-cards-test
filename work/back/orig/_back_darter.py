"""Card-back fountain darter (brief §G.25, §H.19), drawn for the back.

A local drawing (not the library's ``fountain_darter``) tuned for reversed-out
FINE line at orbit size: slender body (length : depth 6 : 1) built from
tangent arcs, a fanned first dorsal of 9 spines with scalloped membrane arcs,
a low soft second dorsal, a rounded caudal split on its axis with the upper
half hatched, a gill-cover arc, a round eye with a dot, the STITCH line of
7 px dashes / 4 px gaps along the flank and 8 short saddle bars across the
back.

Local frame: snout at +x, x 0 (tail edge) .. L (snout), y down, dorsal up.
``darter(x, y, L, heading)`` centres the fish on (x, y) and turns it to
``heading`` (screen degrees; the snout points that way).
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Polygon

from deck import tokens as T
from deck.motifs import core as C
from deck.motifs.forms import arc_spline, scallop_arc, unit
from inkkit import geom as G

FINE = T.FINE

# Design table at L = 100 (x: tail edge 0 → snout 100; y down).
D = dict(
    dorsal=[(18.0, -3.7), (28.0, -5.0), (44.0, -7.4), (62.0, -8.6), (78.0, -8.2), (89.0, -6.9),
            (96.6, -4.9)],
    nose=(100.0, 0.4),
    ventral=[(97.0, 4.6), (89.0, 6.6), (76.0, 7.8), (60.0, 7.9), (44.0, 6.9), (29.0, 5.0), (18.0, 3.7)],
    tail_top=(2.2, -9.4), tail_bot=(2.2, 9.4), rear_bulge=2.6, edge_bow=0.8,
    finbase_bow=1.2, tail_hatch=-60.0,
    eye=dict(c=(90.6, -1.2), r=3.15, dot=4.2),
    gill=dict(top=81.5, bot=80.0, mid=(77.3, 0.6)),
    # first dorsal: 9 spines radiating from a pivot hidden in the back
    d1=dict(pivot=(59.0, 3.0), r=21.5, a0=-141.0, a1=-64.0, scallop=1.1),
    # soft second dorsal (points: x, height above the contour)
    d2=[(41.0, 0.0), (37.0, -5.2), (28.5, -4.4), (23.0, 0.0)],
    anal=[(38.0, 0.0), (33.0, 4.4), (26.0, 0.0)],
    pect=dict(base=(72.0, 3.2), a=(150.0, 128.0), r=10.0),
    stitch=dict(y=1.0, x0=74.0, x1=23.0, on=7.0, off=4.0),
    saddles=dict(n=8, x0=76.0, x1=27.0, stitch_clear=3.2, lean=-22.0),
)


def _contour_y(pts, x, top=True):
    xs = pts[:, 0]
    idx = np.where((xs[:-1] - x) * (xs[1:] - x) <= 0)[0]
    ys = []
    for j in idx:
        a, b = pts[j], pts[j + 1]
        t = 0.0 if b[0] == a[0] else (x - a[0]) / (b[0] - a[0])
        ys.append(float(a[1] + (b[1] - a[1]) * t))
    return (min(ys) if top else max(ys)) if ys else float("nan")


def darter_local(L: float = 100.0, *, spines: int = 9, pect: bool = False) -> C.Frag:
    k = L / 100.0

    def P(p):
        return (p[0] * k, p[1] * k)

    f = C.Frag()
    prof = [P(p) for p in D["ventral"][::-1]]           # peduncle-bottom -> snout
    prof = [P(p) for p in D["dorsal"]]
    # outline: peduncle top -> back -> snout -> belly -> peduncle bottom
    top = [P(p) for p in D["dorsal"]]
    bot = [P(p) for p in D["ventral"]]
    pts = top + [P(D["nose"])] + bot
    d_body, body_pts, _ = arc_spline(pts, headings={len(top): 90.0})
    pt, pb = top[0], bot[-1]
    ct, cb = P(D["tail_top"]), P(D["tail_bot"])
    tail = (scallop_arc(pb, cb, D["edge_bow"] * k, move=False)
            + scallop_arc(cb, ct, D["rear_bulge"] * k, move=False)
            + scallop_arc(ct, pt, D["edge_bow"] * k, move=False))
    f += C.stroke(d_body + tail + "Z", FINE, role="outline")
    # fin base across the peduncle
    f += C.stroke(f"M{pt[0]:.3f} {pt[1]:.3f}" + scallop_arc(pt, pb, -D["finbase_bow"] * k, move=False),
                  FINE, role="finbase")
    # caudal split on its axis, upper half hatched (vertical, 7 px pitch)
    x_base = pt[0] - D["finbase_bow"] * k
    x_rear = ct[0] + D["rear_bulge"] * k
    f += C.stroke(C.polyline_d([(x_base, 0.0), (x_rear, 0.0)]), FINE, role="ray")
    tail_poly = Polygon(C.sample_d(f"M{pt[0]:.3f} {pt[1]:.3f}"
                                   + scallop_arc(pt, pb, -D["finbase_bow"] * k, move=False) + tail, 0.25)[0][0])
    upper = tail_poly.intersection(Polygon([(-50, 0), (200, 0), (200, -200), (-50, -200)]))
    f += C.hatch(upper, D.get("tail_hatch", 90.0), origin=((x_base + x_rear) / 2, 0.0))
    # head: gill arc, eye + pupil
    g = D["gill"]
    g0 = (g["top"] * k, _contour_y(body_pts, g["top"] * k, True))
    g2 = (g["bot"] * k, _contour_y(body_pts, g["bot"] * k, False))
    d_g, _, _ = arc_spline([g0, P(g["mid"]), g2])
    f += C.stroke(d_g, FINE, role="gill")
    ec = np.array(P(D["eye"]["c"]))
    er = D["eye"]["r"] * max(1.0, k)
    f += C.stroke(G.circle_d(ec[0], ec[1], er), FINE, role="eye")
    pdm = D["eye"]["dot"]
    pc = ec + np.array([er - FINE / 2 - pdm / 2, 0.0])
    f += C.dot(pc[0], pc[1], pdm, role="pupil")
    # first dorsal: fanned spines + scalloped membrane
    d1 = D["d1"]
    hub = np.array(P(d1["pivot"]))
    r = d1["r"] * k
    body_poly = Polygon(body_pts)
    tips, rays = [], []
    for a in np.linspace(d1["a0"], d1["a1"], spines):
        tip = hub + unit(a) * r
        seg = LineString([hub, tip]).difference(body_poly)
        if seg.is_empty:
            continue
        c = np.asarray(max(getattr(seg, "geoms", [seg]), key=lambda s_: s_.length).coords)
        start = c[0] if np.hypot(*(c[0] - tip)) > np.hypot(*(c[-1] - tip)) else c[-1]
        tips.append(tip)
        rays.append(C.polyline_d([start, tip]))
    f += C.stroke("".join(rays), FINE, style="point", role="spine")
    memb = f"M{tips[0][0]:.3f} {tips[0][1]:.3f}" + "".join(
        scallop_arc(tips[i], tips[i + 1], d1["scallop"] * k, move=False) for i in range(len(tips) - 1))
    f += C.stroke(memb, FINE, style="point", role="membrane")
    # soft dorsal and anal fins
    for key, is_top in (("d2", True), ("anal", False)):
        pp = [(px * k, _contour_y(body_pts, px * k, is_top) + dh * k) for px, dh in D[key]]
        d_fin, _, _ = arc_spline(pp)
        f += C.stroke(d_fin, FINE, role="fin")
    # stitch line
    st = D["stitch"]
    sy = st["y"] * k
    line = np.array([[st["x0"] * k, sy], [st["x1"] * k, sy]])
    pieces = C.dashes(line, st["on"], st["off"], min_len=3.0)
    f += C.stroke(pieces, FINE, style="rule", role="stitch")
    # saddle bars: from the back toward the stitch line, stopping clear of it
    sd = D["saddles"]
    bars = []
    for xx in np.linspace(sd["x0"] * k, sd["x1"] * k, sd["n"]):
        yt = _contour_y(body_pts, xx, True)
        yb_ = sy - FINE / 2 - sd["stitch_clear"]
        if yb_ - yt < 2.5:
            continue
        ln = yb_ - yt
        lean = math.radians(sd.get("lean", 0.0))
        bars.append(C.polyline_d([(xx, yt), (xx + ln * math.tan(lean), yb_)]))
    f += C.stroke("".join(bars), FINE, style="rule", role="saddle")
    f.meta.update(length=L, body=body_pts)
    return f


def darter(x: float, y: float, L: float = 100.0, heading: float = 0.0, **kw) -> C.Frag:
    """The darter centred on (x, y), snout pointing ``heading`` (screen deg)."""
    f = darter_local(L, **kw).translate(-L / 2, 0.0)
    return f.rotate(heading, 0.0, 0.0).translate(x, y)
