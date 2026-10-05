"""Current lines — creative brief §G.24 (hair, beards, plumes).

3–5 parallel offset curves at a 7 px pitch from ONE guide, each ending in a
Ø6.3 circle terminal (§B.2). Alternate locks may be flat gold (§C rule 1:
flat gold is allowed on hair locks).

* :func:`current_lines`  the lines (+ terminals, + optional gold locks)
* :func:`lock_band`      the FILL outline between two of the offsets (a gold lock)

The guide is a d-string or points, drawn from the root (hairline, chin) to the
free end. Offsets go to ``side`` (+1 = left of travel on screen). Terminals
are staggered along the lines so neighbouring Ø6.3 dots keep >= 4.2 px clear
(at a 7 px pitch that needs >= 7.8 px of stagger).
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Polygon

from inkkit import geom as G

from deck import tokens as T
from .core import (MIN_CLEAR, Frag, fill, polyline_d, sample_d, stroke, terminal)

__all__ = ["current_lines", "lock_band", "CURRENT_PITCH", "MIN_STAGGER"]

FINE = T.FINE
CURRENT_PITCH = 7.0                                   # §G.24
# two Ø6.3 terminals on neighbouring lines must be >= 6.3 + 4.2 apart (§I.12)
MIN_STAGGER = math.sqrt((T.TERMINAL_D + MIN_CLEAR) ** 2 - CURRENT_PITCH ** 2)


def _pts(guide) -> np.ndarray:
    if isinstance(guide, str):
        return sample_d(guide, 0.25)[0][0]
    if isinstance(guide, G.Curve):
        return guide.pts
    return np.asarray(guide, float)


def _offset(cv: G.Curve, dist: float) -> np.ndarray:
    """Offset polyline with any local loops (radius < dist) removed."""
    if abs(dist) < 1e-9:
        return cv.resample(0.5)
    P = cv.offset(dist, spacing=0.5)
    ln = LineString(P)
    if ln.is_simple:
        return P
    # drop self-intersection loops: keep the longest simple run
    from shapely.ops import unary_union
    parts = list(unary_union(ln).geoms) if hasattr(unary_union(ln), "geoms") else [ln]
    best = max(parts, key=lambda g: g.length)
    return np.asarray(best.coords)


def current_lines(guide, n: int = 4, pitch: float = CURRENT_PITCH, *, side: int = 1,
                  stagger: float = 9.0, trim: float = 0.0, terminals: str = "end",
                  gold: str | None = None, w: float = FINE, color: str = T.INK,
                  layer: str | None = None, gold_color: str = T.FOIL) -> Frag:
    """§G.24 ``n`` (3–5) parallel lines: the guide and its offsets at k·pitch
    to ``side``. Line k is shortened at its free end by k·``stagger`` px (so
    the terminals step back like a lock's layered ends; keep stagger >=
    7.8 at a 7 px pitch) and at its root by ``trim``·k. ``terminals``:
    'end' | 'both' | None — Ø6.3 dots on the free ends.

    ``gold``: None; 'alternate' — the strips between lines 0–1, 2–3, … are
    flat gold fills under the lines (alternate locks gold); 'lock' — the
    whole band between the outermost lines is flat gold.
    ``meta``: lines (list of point arrays)."""
    if not 3 <= n <= 5:
        raise ValueError("§G.24: 3–5 current lines")
    if pitch < w + MIN_CLEAR - 1e-9:
        raise ValueError(f"pitch {pitch} < {w + MIN_CLEAR}: lines would crowd (§I.12)")
    cv = G.Curve(_pts(guide))
    f = Frag()
    lines = []
    warn = []
    for k in range(n):
        P = _offset(cv, side * k * pitch)
        c = G.Curve(P)
        end = c.length - k * stagger
        start = k * trim
        if end - start < 4:
            warn.append(f"current_lines: line {k} vanishes (guide too short for stagger)")
            continue
        sub = c.sub(start / c.length, end / c.length)
        lines.append(sub.pts)
    if stagger < MIN_STAGGER - 1e-6 and terminals:
        warn.append(f"current_lines: stagger {stagger} < {MIN_STAGGER:.1f} — terminals crowd")
    if gold in ("alternate", "lock"):
        pairs = [(0, len(lines) - 1)] if gold == "lock" else [(k, k + 1) for k in range(0, len(lines) - 1, 2)]
        for a, b in pairs:
            band = lock_band(lines[a], lines[b])
            if band:
                f += fill(band, color=gold_color, role="lock")
    for P in lines:
        f += stroke(polyline_d(P), w, color=color, layer=layer, role="current")
        if terminals in ("end", "both"):
            f += terminal(*P[-1], color=color, layer=layer)
        if terminals in ("start", "both"):
            f += terminal(*P[0], color=color, layer=layer)
    f.meta.update(lines=lines)
    if warn:
        f.meta["warnings"] = warn
    return f


def lock_band(a_pts, b_pts) -> str:
    """FILL d of the strip between two roughly parallel polylines (a lock),
    closed straight across at both ends; the ends lie under the lines'
    terminals / root, so no raw edge shows."""
    a = np.asarray(a_pts, float)
    b = np.asarray(b_pts, float)
    poly = Polygon(np.vstack([a, b[::-1]]))
    if not poly.is_valid:
        from shapely import make_valid
        poly = make_valid(poly)
    if poly.is_empty or poly.area < 1:
        return ""
    return G.from_shape(poly)
