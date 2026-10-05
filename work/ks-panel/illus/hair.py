"""Hair and beards as current lines (brief §G.24) — shared by all courts.

A lock mass is authored as TWO GUIDE CURVES (hand-placed Bézier knots, see
bez.py): ``A`` the outer edge and ``B`` the inner edge, both running from the
root (under the crown / at the cheek) to the ends. Everything else is
interpolated between them, so the flow never wobbles:

* ``lock_mass``  n locks between A and B; each lock is a ribbon ending in a
  round cap at its own length (``ends``); the silhouette is their union and
  the divisions between locks are the current lines, each finishing in a
  Ø6.3 terminal where the two locks part.
* ``flow_lines`` just the interpolated lines (for beards, plumes, manes)
  clipped to any silhouette, each ending in a terminal.

Alternate locks may be flat gold (§G.24): ``lock_mass(..., fills=...)``
returns per-lock regions so a caller can colour every other one.
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import Polygon

from deck import tokens as T
from deck.motifs import core as MC
from inkkit import geom as G

from bez import K, pts


def _pair(A, B, n=400):
    """Resample two guide polylines to n points each by arc-length fraction."""
    ca, cb = G.Curve(np.asarray(A, float)), G.Curve(np.asarray(B, float))
    t = np.linspace(0, 1, n)
    return ca.at(t), cb.at(t)


def guide(knots) -> np.ndarray:
    return pts(knots, step=0.5)


def lerp_curve(A, B, f, n=400):
    a, b = _pair(A, B, n)
    return a + (b - a) * f


def _cut(P, t0, t1):
    c = G.Curve(P)
    return c.sub(max(0.0, t0), min(1.0, t1)).pts


def flow_lines(A, B, fracs, *, t0=0.0, t1=1.0, w=T.MEDIUM, color=T.INK, clip=None,
               terminal="end", n=400) -> MC.Frag:
    """Current lines interpolated between guides A and B at ``fracs``
    (0 = A, 1 = B). ``t0``/``t1`` (scalars or one per line) are the arc
    fractions where each line starts / ends; a Ø6.3 terminal sits on the end.
    ``clip`` (FILL d) keeps them inside a silhouette (terminals included)."""
    f = MC.Frag()
    k = len(fracs)
    t0s = t0 if np.ndim(t0) else [t0] * k
    t1s = t1 if np.ndim(t1) else [t1] * k
    for fr, a0, a1 in zip(fracs, t0s, t1s):
        P = _cut(lerp_curve(A, B, fr, n), a0, a1)
        ln = MC.stroke(P, w, color=color, role="current")
        if clip is not None:
            ln = MC.clip(ln, clip)
        f += ln
        if terminal and len(P) > 1:
            e = P[-1] if terminal == "end" else P[0]
            f += MC.terminal(*e, color=color)
    return f


def lock_mass(A, B, n: int, ends, *, w=T.MEDIUM, cap=1.0, color=T.INK, n_s=400, start_line=0.0):
    """``n`` locks between guides A (outer) and B (inner). ``ends`` = arc
    fraction where each lock stops (outer lock first). Each lock gets a round
    cap (``cap`` × half its width, bulging along the flow). Returns
    (silhouette d, division lines Frag, [lock region d])."""
    a, b = _pair(A, B, n_s)
    locks, polys = [], []
    for i in range(n):
        f0, f1 = i / n, (i + 1) / n
        e = ends[i]
        m = max(2, int(e * (n_s - 1)))
        L = a[:m] + (b[:m] - a[:m]) * f0
        R = a[:m] + (b[:m] - a[:m]) * f1
        pL, pR = L[-1], R[-1]
        mid = (pL + pR) / 2
        tang = L[-1] - L[-2]
        tang = tang / (np.hypot(*tang) or 1)
        r = np.hypot(*(pR - pL)) / 2
        # half-ellipse cap from pR round to pL, bulging along the flow
        th = np.linspace(0, np.pi, 24)
        u = (pR - mid) / (r or 1)
        cap_pts = np.array([mid + u * r * np.cos(t) + tang * r * cap * np.sin(t) for t in th])
        ring = np.vstack([L, cap_pts[::-1], R[::-1]])   # root → end, round the cap, back
        pg = Polygon(ring).buffer(0)
        polys.append(pg)
        locks.append(G.from_shape(pg))
    sil = G.from_shape(shapely.union_all(polys))
    lines = MC.Frag()
    for i in range(1, n):
        f = i / n
        e = min(ends[i - 1], ends[i])
        m = max(2, int(e * (n_s - 1)))
        P = (a[:m] + (b[:m] - a[:m]) * f)
        s0 = int(start_line * (m - 1))
        P = P[s0:]
        lines += MC.stroke(P, w, color=color, role="current")
        lines += MC.terminal(*P[-1], color=color)
    return sil, lines, locks


# §G.24 asks for a 7 px pitch; with Ø6.3 terminals that leaves 7 − 3.15 − 1.05 =
# 2.8 px beside the neighbouring line (< the 3 px §I.12 / QA-12 minimum), so
# bundles use 7.4 px — visually the same rhythm, and every gap prints.
CURRENT_PITCH = 7.4


def bundle(guide_pts, n=3, pitch=CURRENT_PITCH, *, side=+1, offset0=0.0, t0=0.0, t1=1.0,
           stagger=0.04, w=T.FINE, color=T.INK, clip=None) -> MC.Frag:
    """§G.24 current lines: ``n`` parallel offset curves at ``pitch`` (7 px)
    from ONE guide, each ending in a Ø6.3 terminal. Offsets go to the guide's
    left (side +1) or right (−1), starting ``offset0`` px from it. Each
    successive line ends ``stagger`` (arc fraction) earlier, so the
    terminals step like water leaving a vent. Lines are clipped to ``clip``
    (terminals are kept only if their centre lies inside it)."""
    c = G.Curve(np.asarray(guide_pts, float))
    f = MC.Frag()
    reg = MC.region(clip) if clip is not None else None
    for k in range(n):
        dist = side * (offset0 + k * pitch)
        P = c.offset(dist)
        e = t1 - k * stagger
        cc = G.Curve(P)
        P = cc.sub(t0, max(t0 + 0.05, e)).pts
        ln = MC.stroke(P, w, color=color, role="current")
        if reg is not None:
            ln = MC.clip(ln, reg)
        f += ln
        end = P[-1]
        if reg is None or reg.contains(shapely.Point(*end)):
            f += MC.terminal(*end, color=color)
    return f
