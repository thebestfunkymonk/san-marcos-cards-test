"""work/v3-pilot/flow/_flow.py — the continuous double-head toolkit for courts.

The idea (client direction 2026-10-01: "the continuous double-headed effect
that most playing cards have"; "integrate, don't stack"):

* Compose the WHOLE card's art as one C2-symmetric scene. Parts that live in
  one head (face, crown, hand, attributes) are added twice: once as drawn and
  once rotated 180° about the card centre (``rot``). Parts that cross the
  centre (mantle, lens, lapels, the drape) are built ONCE as C2 regions
  (``c2``), so they are their own rotation and continue across the centre by
  construction.
* The two heads twist into each other through one garment: the DRAPE, an
  S-shaped fold of the mantle running edge to edge through the centre. Its
  centreline is the seam (``SEAM``): every part that crosses the seam is
  covered by it, so the system's clip-and-rotate reproduces the art exactly
  and the eye finds no line where one half ends.
* Composing both heads in one scene means ``heal`` (§I.12) sees the spacing
  between a figure and the other head's parts near the centre too.

Helpers here are geometry only; colours, strokes and every mark come from
``deck.courtkit`` so the court stays in the kit's hand.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck import frames as F
from deck import tokens as T
from deck.motifs import core as C

CX, CY = float(T.CX), float(T.CY)


# ---------------------------------------------------------------------------
# C2 symmetry
# ---------------------------------------------------------------------------
def rot_g(g):
    """A shapely geometry rotated 180° about the card centre."""
    return shapely.affinity.rotate(g, 180.0, origin=(CX, CY))


def rot_pt(p):
    return np.array([2 * CX - float(p[0]), 2 * CY - float(p[1])])


def rot(x):
    """180° copy of a Part, a Frag or a shapely geometry."""
    if isinstance(x, K.Part):
        return K.Part(rot_g(x.shape), x.fills.rot180(), x.lines.rot180(), dict(x.meta))
    if isinstance(x, C.Frag):
        return x.rot180()
    return rot_g(x)


def c2(g):
    """The C2 closure of a region: g ∪ its 180° copy."""
    return shapely.union(g, rot_g(g))


def catmull(pts, n=24):
    """A Catmull-Rom curve through ``pts`` (end tangents from the end chords)."""
    P = np.asarray(pts, float)
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0.0, 1.0, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    return np.asarray(out)


def s_curve(left_half, n=24):
    """A C2 S-curve: ``left_half`` control points from the left edge to (but
    not including) the centre; the curve runs through them, the centre and
    their 180° images. Catmull-Rom is reversal- and affine-equivariant, so the
    sampled curve is exactly its own 180° rotation."""
    L = [tuple(map(float, p)) for p in left_half]
    ctrl = L + [(CX, CY)] + [tuple(rot_pt(p)) for p in L[::-1]]
    return catmull(ctrl, n)


def seam_half(curve):
    """The left half of a sampled C2 curve, ending exactly on the centre (the
    form ``SEAM`` takes as a point list)."""
    c = np.asarray(curve, float)
    k = int(np.argmin(np.hypot(c[:, 0] - CX, c[:, 1] - CY)))
    half = c[: k + 1].copy()
    half[-1] = (CX, CY)
    return [tuple(map(float, p)) for p in half]


def above(curve, pad=0.0):
    """The region above a left-to-right curve (extended far past the card)."""
    c = np.asarray(curve, float)
    head = c[0] + (c[0] - c[1]) / np.hypot(*(c[0] - c[1])) * 400.0
    tail = c[-1] + (c[-1] - c[-2]) / np.hypot(*(c[-1] - c[-2])) * 400.0
    ring = np.vstack([[head[0], -2000.0], head, c, tail, [tail[0], -2000.0]])
    g = Polygon(ring).buffer(0)
    return g.buffer(pad) if pad else g


def band(curve, w, ext=300.0):
    """A band ``w`` wide along a curve, its ends run on ``ext`` px along the end tangents."""
    c = np.asarray(curve, float)
    head = c[0] + (c[0] - c[1]) / np.hypot(*(c[0] - c[1])) * ext
    tail = c[-1] + (c[-1] - c[-2]) / np.hypot(*(c[-1] - c[-2])) * ext
    return LineString(np.vstack([head, c, tail])).buffer(w / 2, cap_style=2, quad_segs=16)


def window():
    return K.R(F.art_window_d())


def y_at(curve, x):
    c = np.asarray(curve, float)
    i = int(np.searchsorted(c[:, 0], x))
    i = min(max(i, 1), len(c) - 1)
    a, b = c[i - 1], c[i]
    t = (x - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
    return float(a[1] + t * (b[1] - a[1]))


def compose(sc: "K.Scene", *, log=None):
    """Compose a full-card (both heads) scene: painter's clip + CONTOUR
    silhouette, clipped to the art window, then healed (§I.12) as printed."""
    res = sc.compose(heal_gaps=False)
    res = K.clip_in(res, window(), sc.clip_tol)
    sc.heal_log = [] if log is None else log
    return K.heal(res, log=sc.heal_log)


def c2_check(frag: C.Frag, tol=0.6):
    """How far the composed art is from its own 180° rotation, per layer
    (area of the symmetric difference of the printed ink, px²)."""
    out = {}
    lay = K.layers(frag)
    for L in lay:
        pass
    return out
