"""art/_qc_cloak.py — Q♣ · the mantle's Gill Red lining and its knocked-out
grain column.

The lining shows either side of the jade gown. It carries, knocked out to
paper (§C.4: patterns on red are paper knockouts), a column of wild-rice
grains down the middle of each panel: pairs of §G.5 spikelets (3 : 1
vesicas) standing in a V, erect as the female spikelets are — the Drifters
habit of a column of small emblems down a lapel, in the Reed's own
vocabulary (plants as textile, §H.0 care rules).
"""
from __future__ import annotations

import math

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C

P, R, U = K.P, K.R, K.U


def _u(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def grain_column(p0, p1, *, pitch=19.0, length=14.0, width=4.8, spread=27.0, split=2.6, keep=None, dot=0.0):
    """A column of V-pairs of grains from ``p0`` (bottom) to ``p1`` (top):
    each pair = two vesicas ``length`` × ``width`` leaning ±``spread``° off
    the column's upward direction, their bases ``split`` px either side of
    the axis; ``pitch`` px between pairs. ``keep(region)`` → bool filters
    units (e.g. wholly inside the visible panel, with the knockout margin).
    ``dot`` > 0 adds a dot of that diameter above each V. → Frag of FILLs
    (to knock out)."""
    a, b = P(p0), P(p1)
    L = float(np.hypot(*(b - a)))
    up = (b - a) / L
    hd = math.degrees(math.atan2(up[1], up[0]))
    nr = np.array([-up[1], up[0]])
    f = C.Frag()
    s = pitch / 2
    while s < L:
        o = a + up * s
        unit = C.Frag()
        for sd in (-1, 1):
            base = o + nr * sd * split
            u = _u(hd + sd * spread)
            unit += C.fill(C.vesica_d(base, base + u * length, width))
        if dot:
            q = o + up * (length * 0.95 + dot)
            unit += C.fill(C.circle_d(q[0], q[1], dot / 2))
        if keep is None or keep(unit):
            f += unit
        s += pitch
    return f


def panel_keep(panel, margin=3.6):
    """``keep`` for grain_column: the unit lies wholly ``margin`` px inside ``panel``."""
    inner = R(panel).buffer(-margin)

    def ok(unit):
        return inner.contains(unit.shape())
    return ok


def leaf_drift(region, *, heading=55.0, length=22.0, width=5.2, along=34.0, across=15.0, stagger=0.5,
               origin=(375.0, 330.0), keep=None, bend=0.0):
    """A drift of small ribbon-leaf vesicas all streaming ``heading``° (the
    current), on a staggered lattice (``along`` the stream × ``across`` it,
    alternate files shifted ``stagger`` × along); each kept whole or dropped
    (``keep(unit)``). → Frag of FILLs (to knock out)."""
    reg = R(region)
    x0, y0, x1, y1 = reg.bounds
    u = _u(heading)
    v = np.array([-u[1], u[0]])
    o = P(origin)
    corners = np.array([[x0, y0], [x1, y0], [x0, y1], [x1, y1]]) - o
    a0, a1 = (corners @ u).min() - length, (corners @ u).max()
    c0, c1 = (corners @ v).min(), (corners @ v).max()
    f = C.Frag()
    k0 = int(math.floor(c0 / across)) - 1
    k1 = int(math.ceil(c1 / across)) + 1
    for k in range(k0, k1 + 1):
        off = (k % 2) * stagger * along
        j0 = int(math.floor((a0 - off) / along)) - 1
        j1 = int(math.ceil((a1 - off) / along)) + 1
        for j in range(j0, j1 + 1):
            b = o + v * (k * across) + u * (j * along + off)
            if bend:
                d = K.Path(b).sag(b + u * length, 0.0).d
            unit = C.fill(C.vesica_d(b, b + u * length, width))
            if keep is None or keep(unit):
                f += unit
    return f


def mantle(base, *, edge=12.0, edge_color=K.JADE, color=K.RED, knock=None, keep_x=(300.0, 450.0), y_min=0.0):
    """The mantle from ``base`` (a Part from _qc_parts.cloak, for its shape):
    its Gill Red lining (with ``knock`` knocked out) and a turned-back
    border ``edge`` px wide in ``edge_color`` (the mantle's jade outside
    showing at its free edge) along the whole outline outside the band
    ``keep_x`` (x between them: behind the neck, never seen) and below
    ``y_min``; the red is cut where the border lies (jade under red would
    not print, the layer trap), a MEDIUM hem line closes it.
    → Part (meta 'edge', 'lining')."""
    shape = base.shape
    ring = shape.difference(shape.buffer(-edge, quad_segs=16))
    x0, x1 = keep_x
    band = ring.difference(K.box(x0, -100, x1, 2000)).intersection(K.box(0, y_min, 2000, 2000))
    band = band.buffer(0)
    lining = shape.difference(band)
    body_d = K.D(lining)
    if knock is not None:
        body_d = C.knockout(body_d, knock)
    fills = K.fill(body_d, color) + K.fill(band, edge_color)
    hem = C.stroke(K.D(shape.buffer(-edge, quad_segs=16)), K.MEDIUM, role="hem")
    lines = K.outline(shape) + K.clip_in(hem, band.buffer(0.8))
    return K.Part(shape, fills, lines, {"edge": band, "lining": lining})
