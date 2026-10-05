"""art/_kh_head.py — K♥ · The Ferryman King: beard and moustache.

The kit's frontal beard (``courtkit.beard``) is the K♠'s forked beard; the
K♥ brief asks for a "curled gold current-line beard" on a kindly face, so
this module builds a rounded full beard whose current lines roll into
curls, and a short moustache whose tips lift (the kindly set of the mouth),
with the kit's own conventions: compass arcs, the left half drawn and
mirrored, the chin kept paper round the mouth, current lines 7 px apart
rolling into Ø6.3 terminals (§G.24).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import shapely
from shapely.geometry import LineString, Point

from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G

P = K.P


@dataclass
class CurlBeard:
    side_dy: float = 19.0          # sideburn: on the head outline, this far below the egg centre
    bulge: tuple = (-47.0, 64.0)   # outermost point of the outer edge (dx from the axis, dy from the egg centre)
    foot: tuple = (-31.0, 103.0)   # where the outer edge turns into the rounded bottom
    bottom_dy: float = 114.0       # bottom of the beard on the axis
    lip_clear: float = 8.2
    lines: int = 3
    stagger: float = 11.0
    curl_r: float = 5.2
    curl_deg: float = 160.0
    color: str = K.GOLD


def beard(fc, b: CurlBeard = CurlBeard(), mo=None) -> K.Part:
    a = fc.anchors
    ax = float(a["axis"])
    cx, cy = a["center"]
    sy = cy + b.side_dy
    S = P(a["side_x"](sy, -1) + 0.5, sy)
    Bg = P(ax + b.bulge[0], cy + b.bulge[1])
    Ft = P(ax + b.foot[0], cy + b.foot[1])
    Bt = P(ax, cy + b.bottom_dy)
    top_ax = a["lip_y"] + b.lip_clear
    out = K.Path(S).arc3(Bg, Ft)
    # rounded bottom: a circular arc from the foot to the axis, tangent-ish
    out.sag(Bt, -6.0).line((ax, top_ax))
    sp = a["spec"]
    Q = P(ax - sp.mouth_hw - 8.0, a["lip_y"] + 2.0)
    if mo is not None:
        tip, root = mo.meta["tip"], mo.meta["root"]
        Mi = tip + (root - tip) * 0.42 - P(0.0, 3.2)
    else:
        Mi = P(ax - sp.mouth_hw - 4.0, a["mouth_y"] - 4.0)
    out.arc3(Q, Mi).sag(S, -3.0).close()
    half = K.R(out.d).intersection(K.box(0, 0, ax + 0.01, 2000))
    half = max(K._polys_of(half), key=lambda g: g.area)
    shape = K.U(half, K.mirror(half, ax)).buffer(0.05).buffer(-0.05)
    # guide: the outer edge from above the sideburn down round the bottom to the axis
    g = C.sample_d(K.arc3(S, Bg, Ft) + K.arc_sag(Ft, Bt, -6.0, move=False), 0.4)[0][0]
    t0 = g[1] - g[0]
    t0 = t0 / np.hypot(*t0)
    g = np.vstack([g[0] - t0 * 30.0, g])
    lines = K.current_lines(g, b.lines, half, side=+1, first=K.EDGE_MED, edge=K.MEDIUM, stagger=b.stagger,
                            curl_r=b.curl_r, curl_deg=b.curl_deg)
    lines = lines + lines.mirror_x(ax)
    return K.Part(shape, K.fill(shape, b.color), lines + K.outline(shape), {"S": S, "bottom": Bt})


@dataclass
class LiftMoustache:
    root: tuple = (-1.5, 8.5)      # below the nose base
    tip: tuple = (-28.0, 14.0)
    arch: float = 3.2              # upper edge (bulges up)
    under: float = 4.6             # lower edge (bulges down): the tips lift
    color: str = K.GOLD


def moustache(fc, m: LiftMoustache = LiftMoustache()) -> K.Part:
    a = fc.anchors
    ax = float(a["axis"])
    ny = a["nose_y"]
    p0 = P(ax + m.root[0], ny + m.root[1])
    p1 = P(ax + m.tip[0], ny + m.tip[1])
    leaf = K.R(K.Path(p1).sag(p0, m.arch).sag(p1, m.under).close().d)
    shape = K.U(leaf, K.mirror(leaf, ax))
    return K.Part(shape, K.fill(shape, m.color), K.outline(shape), {"tip": p1, "root": p0})


# =============================================================================
# v3: the curled beard — a rounded beard whose lower edge is four scalloped
# lobes, each holding a current line rolled into a curl (§G.24 terminals)
# =============================================================================
@dataclass
class LobeBeard:
    side_dy: float = 19.0            # sideburn on the head outline, below the egg centre
    bulge: tuple = (-50.0, 58.0)     # outermost point of the outer edge (dx, dy from the egg centre)
    lobes: tuple = ((-45.0, 92.0), (-22.0, 110.0), (0.0, 117.0))   # scallop cusps: outer foot, mid cusp, axis
    lobe_sag: tuple = (7.5, 6.5)     # scallop bulge (outer lobe, inner lobe)
    lip_clear: float = 8.2
    curl_r: float = 5.6
    color: str = K.GOLD


def _curl_line(pts, turn_deg, r):
    """Continue a polyline with a tangent arc of radius r turning ``turn_deg``
    (screen degrees; + = clockwise) — the rolled end of a lock."""
    p = pts[-1]
    t = pts[-1] - pts[-2]
    h = math.degrees(math.atan2(t[1], t[0]))
    tu = C.Turtle(p[0], p[1], h)
    tu.arc(r, turn_deg)
    arc = np.asarray(tu.pts(0.4)[0])
    return np.vstack([pts, arc[1:]])


def lobe_beard(fc, b: LobeBeard = LobeBeard(), mo=None, *, lines=None) -> K.Part:
    a = fc.anchors
    ax = float(a["axis"])
    cx, cy = a["center"]
    sy = cy + b.side_dy
    S = P(a["side_x"](sy, -1) + 0.5, sy)
    Bg = P(ax + b.bulge[0], cy + b.bulge[1])
    F0, F1, F2 = [P(ax + dx, cy + dy) for dx, dy in b.lobes]
    top_ax = a["lip_y"] + b.lip_clear
    sp = a["spec"]
    Q = P(ax - sp.mouth_hw - 8.0, a["lip_y"] + 2.0)
    if mo is not None:
        tip, root = mo.meta["tip"], mo.meta["root"]
        Mi = tip + (root - tip) * 0.42 - P(0.0, 3.2)
    else:
        Mi = P(ax - sp.mouth_hw - 4.0, a["mouth_y"] - 4.0)
    # travel S → Bg → F0 → (scallop) F1 → (scallop) F2 → up the axis → round the mouth → Mi → S
    out = (K.Path(S).arc3(Bg, F0).sag(F1, b.lobe_sag[0]).sag(F2, b.lobe_sag[1]).line((ax, top_ax))
           .arc3(Q, Mi).sag(S, -3.0).close())
    half = K.R(out.d).intersection(K.box(0, 0, ax + 0.01, 2000))
    half = max(K._polys_of(half), key=lambda g: g.area)
    shape = K.U(half, K.mirror(half, ax)).buffer(0.05).buffer(-0.05)
    L1 = lines or {}
    if L1.get("mode", "kit") == "kit":
        # current lines: offsets of the smooth outer edge (cheek → bulge → round
        # the bottom to the axis), converging, staggered, each rolled into a curl
        Bt = P(ax, cy + L1.get("bottom_dy", 112.0))
        g = C.sample_d(K.arc3(S, Bg, F0) + K.arc_sag(F0, Bt, L1.get("bottom_sag", -9.0), move=False), 0.4)[0][0]
        t0 = g[1] - g[0]
        t0 = t0 / np.hypot(*t0)
        g = np.vstack([g[0] - t0 * 30.0, g])
        kw = dict(side=+1, edge=K.MEDIUM, curl_r=L1.get("curl_r", 5.2), curl_deg=L1.get("curl_deg", 200.0))
        f = K.current_lines(g, 1, half, first=K.EDGE_MED, stagger=0.0, **kw)
        placed = shapely.union_all([LineString(q).buffer(K.FINE / 2) for q in f.meta["lines"]] +
                                   [Point(*q[-1]).buffer(K.TD / 2) for q in f.meta["lines"]])
        # the inner lines start below the moustache (above it the cheek is one ribbon wide)
        y_in = L1.get("inner_from", a["lip_y"] - 4.0)
        k0 = int(np.argmax(g[:, 1] >= y_in))
        f2 = K.current_lines(g[k0:], L1.get("n", 3) - 1, half, first=K.EDGE_MED + K.PITCH,
                             stagger=L1.get("stagger", 12.0), placed=placed, **kw)
        f = f + f2
        f = f + f.mirror_x(ax)
        return K.Part(shape, K.fill(shape, b.color), f + K.outline(shape), {"S": S, "bottom": F2, "n": f.meta})
    f = C.Frag()
    # explicit locks: (start, mid, end) of a compass arc (dx, dy from the axis
    # and egg centre), then a curl of radius r turning ``turn`` degrees
    locks = L1.get("locks", [((-36.5, 25.0), (-42.5, 55.0), (-37.0, 83.0), -215.0, 5.6),
                             ((-17.5, 66.0), (-18.5, 83.0), (-13.0, 98.0), -215.0, 5.0)])
    for p0, pm, p1, turn, r in locks:
        q = C.sample_d(K.arc3(P(ax + p0[0], cy + p0[1]), P(ax + pm[0], cy + pm[1]), P(ax + p1[0], cy + p1[1])),
                       0.4)[0][0]
        q = _curl_line(q, turn, r)
        f += K.line(C.polyline_d(q), K.FINE, role="current")
        f += K.dot(q[-1], K.TD, role="terminal")
    f = f + f.mirror_x(ax)
    return K.Part(shape, K.fill(shape, b.color), f + K.outline(shape), {"S": S, "bottom": F2})


# =============================================================================
# v4: the curled beard — scalloped lobes, a centre lobe on the axis, and one
# family of current lines (7 px pitch, offsets of the outer edge) whose ends
# roll into curls, one curl seated in each lobe
# =============================================================================
@dataclass
class CurlBeard2:
    side_dy: float = 19.0                  # sideburn on the head outline, below the egg centre
    bulge: tuple = (-49.0, 58.0)           # outermost point of the outer edge (dx, dy)
    cusps: tuple = ((-44.0, 90.0), (-27.0, 107.0), (-13.0, 114.0))   # outer foot, then the lobe cusps
    bottom_dy: float = 121.0               # the centre lobe's lowest point on the axis
    sags: tuple = (6.5, 5.5)               # scallop bulge of the side lobes (outer, inner)
    lip_clear: float = 8.2
    n: int = 3                             # current lines
    first: float = 7.0                     # line 0 inside the outer edge (MEDIUM edge: 7.0)
    ends: tuple = (-35.5, -20.0, -6.5)     # x (dx) where line k starts to curl
    curl_r: tuple = (4.6, 4.2, 3.8)
    curl_deg: tuple = (220.0, 220.0, 200.0)
    inner_from: float = 0.0                # lines k ≥ 1 start below this dy (0: where the region allows)
    color: str = K.GOLD


def curl_beard(fc, b: CurlBeard2 = CurlBeard2(), mo=None) -> K.Part:
    a = fc.anchors
    ax = float(a["axis"])
    cx, cy = a["center"]
    sy = cy + b.side_dy
    S = P(a["side_x"](sy, -1) + 0.5, sy)
    Bg = P(ax + b.bulge[0], cy + b.bulge[1])
    cps = [P(ax + dx, cy + dy) for dx, dy in b.cusps]
    Bt = P(ax, cy + b.bottom_dy)
    top_ax = a["lip_y"] + b.lip_clear
    sp = a["spec"]
    Q = P(ax - sp.mouth_hw - 8.0, a["lip_y"] + 2.0)
    if mo is not None:
        tip, root = mo.meta["tip"], mo.meta["root"]
        Mi = tip + (root - tip) * 0.42 - P(0.0, 3.2)
    else:
        Mi = P(ax - sp.mouth_hw - 4.0, a["mouth_y"] - 4.0)
    # centre lobe: a circle centred on the axis through the last cusp and Bt
    F2 = cps[-1]
    dxc = F2[0] - ax
    yc = ((Bt[1] ** 2) - (F2[1] ** 2) - dxc ** 2) / (2 * (Bt[1] - F2[1]))
    rc = Bt[1] - yc
    pth = K.Path(S).arc3(Bg, cps[0])
    for (p, q), sg in zip(zip(cps[:-1], cps[1:]), b.sags):
        pth = pth.sag(q, sg)
    pth = pth.arc_to((ax, yc), rc, Bt, cw=False).line((ax, top_ax)).arc3(Q, Mi).sag(S, -3.0).close()
    half = K.R(pth.d).intersection(K.box(0, 0, ax + 0.01, 2000))
    half = max(K._polys_of(half), key=lambda g: g.area)
    shape = K.U(half, K.mirror(half, ax)).buffer(0.05).buffer(-0.05)
    # guide: the smooth envelope of the outer edge (cheek → bulge → round the bottom to the axis)
    g = C.sample_d(K.arc3(S, Bg, cps[0]) + K.arc3(cps[0], P(ax - 22.0, Bt[1] - 4.0), P(ax, Bt[1] + 1.0),
                                                   move=False), 0.4)[0][0]
    t0 = g[1] - g[0]
    t0 = t0 / np.hypot(*t0)
    g = np.vstack([g[0] - t0 * 30.0, g])
    cv = G.Curve(g)
    f = C.Frag()
    acc = shapely.geometry.Polygon()
    inner = half.buffer(-(K.MEDIUM / 2 + K.GAP_MARK + K.FINE / 2), quad_segs=12)
    for k in range(b.n):
        off = cv.offset(+(b.first + k * K.PITCH), spacing=0.5)
        ln = LineString(off).intersection(inner)
        pcs = [np.asarray(p.coords) for p in K._lines_of(ln) if p.length > 8.0]
        if not pcs:
            continue
        q = max(pcs, key=lambda p: LineString(p).length)
        if q[0][1] > q[-1][1] and q[0][0] > q[-1][0]:
            q = q[::-1]
        # run down and round the bottom until x reaches the lobe's curl start
        # (measured AFTER the line's outermost point), then roll inward
        xe = ax + b.ends[k]
        i_min = int(np.argmin(q[:, 0]))
        idx = np.where(q[i_min:, 0] >= xe)[0]
        if len(idx):
            q = q[: i_min + idx[0] + 1]
        q = _curl_line(q, -b.curl_deg[k], b.curl_r[k])
        f += K.line(C.polyline_d(q), K.FINE, role="current")
        f += K.dot(q[-1], K.TD, role="terminal")
    f = f + f.mirror_x(ax)
    return K.Part(shape, K.fill(shape, b.color), f + K.outline(shape), {"S": S, "bottom": Bt})
