"""Shared constructions for the FIGURATIVE motifs (Track B2).

Built on :mod:`deck.motifs.core` (Frag / stroke / Turtle / hatch). Everything
is authored at final size from circular arcs and straight lines, or smooth
offsets of them (brief §G preamble, style.md rule 4).

* :func:`arc_path`      tangent-arc centreline from a turn list (exact ``A`` d + dense points)
* :func:`leaf`          a leaf/feather/spikelet on a (curved) midrib with a vesica
                        width profile, split on the midrib, one half hatched
                        PERPENDICULAR to the midrib at each station (§B.2, §G.4)
* :func:`perp_hatch`    the hatch lines of :func:`leaf` alone
* :func:`scallop_arc`   one scallop through two cusps with a given sagitta (exact arc)
* :func:`scallop_ring`  a ring of scallops (exact arcs), cusps on one radius, peaks on another
* :func:`scallop_row`   scallops along any base curve (exact arcs between cusps)
* :func:`tight_spots`   QA: ground gaps narrower than 4.2 px between strokes (§I.12)
"""
from __future__ import annotations

import math
from typing import Callable, Sequence

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from inkkit import geom as G

from deck import tokens as T
from .core import (MIN_CLEAR, MIN_HATCH_LEN, Frag, Turtle, arc_d, polar, polyline_d, region,
                   stroke)

__all__ = ["arc_path", "biarc", "biarc_chain", "arc_spline", "circle_heading", "vesica_hw", "leaf", "leaf_edges", "perp_hatch", "scallop_arc",
           "scallop_ring", "scallop_row", "lock_row", "lock_ring", "tuft_row", "tight_spots", "unit", "rot", "along"]

FINE = T.FINE


# ---------------------------------------------------------------------------
# small vector helpers
# ---------------------------------------------------------------------------
def unit(deg: float) -> np.ndarray:
    """Unit vector at screen angle ``deg``."""
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def rot(v, deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    v = np.asarray(v, float)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def along(p, deg: float, dist: float) -> np.ndarray:
    return np.asarray(p, float) + unit(deg) * dist


# ---------------------------------------------------------------------------
# tangent-arc centrelines
# ---------------------------------------------------------------------------
def arc_path(x: float, y: float, heading: float, turns: Sequence[tuple[float, float]]):
    """Tangent-continuous centreline from (x, y) at ``heading`` through a list
    of ``(length, turn_deg)`` pieces: turn 0 = straight, otherwise a circular
    arc of that length turning ``turn_deg`` (+ = clockwise on screen).
    Returns ``(d, pts, turtle)`` — exact path data, dense points, the Turtle."""
    t = Turtle(x, y, heading)
    for L, tr in turns:
        if abs(tr) < 1e-9:
            t.fd(L)
        else:
            r = L / math.radians(abs(tr))
            t.arc(r, tr)
    return t.d(), t.pts(0.25)[0], t


def _arc_from(p, t, q):
    """Circle tangent to unit ``t`` at ``p`` passing through ``q``: returns
    (svg 'A' command to q, centre, radius, signed sweep deg) or a line."""
    p, t, q = np.asarray(p, float), np.asarray(t, float), np.asarray(q, float)
    v = q - p
    n = np.array([-t[1], t[0]])                     # +90° (clockwise on screen) normal
    den = 2 * float(v @ n)
    if abs(den) < 1e-9:
        return f"L{q[0]:.3f} {q[1]:.3f}", None, math.inf, 0.0
    r = float(v @ v) / den                           # signed: >0 centre on the n side
    c = p + n * r
    a0 = math.atan2(p[1] - c[1], p[0] - c[0])
    a1 = math.atan2(q[1] - c[1], q[0] - c[0])
    # travel direction: r > 0 ⇒ turning clockwise on screen
    if r > 0:
        sw = (a1 - a0) % (2 * math.pi)
    else:
        sw = -((a0 - a1) % (2 * math.pi))
    R = abs(r)
    large = 1 if abs(sw) > math.pi else 0
    sweep = 1 if sw > 0 else 0
    return (f"A{R:.3f} {R:.3f} 0 {large} {sweep} {q[0]:.3f} {q[1]:.3f}", c, R, math.degrees(sw))


def biarc(p0, h0: float, p1, h1: float):
    """Two tangent circular arcs from ``p0`` (heading ``h0`` screen degrees)
    to ``p1`` (arriving with heading ``h1``), G1-continuous (equal tangent
    lengths). Returns (d without the initial M, joint point)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    t0, t1 = unit(h0), unit(h1)
    v = p1 - p0
    tt = t0 + t1
    denom = 2 * (1 - float(t0 @ t1))
    vt = float(v @ tt)
    if abs(denom) < 1e-9:
        d = float(v @ v) / (4 * float(v @ t1)) if abs(float(v @ t1)) > 1e-9 else float(np.hypot(*v)) / 2
    else:
        d = (-vt + math.sqrt(vt * vt + denom * float(v @ v))) / denom
    q0 = p0 + t0 * d
    q1 = p1 - t1 * d
    j = (q0 + q1) / 2
    a1, *_ = _arc_from(p0, t0, j)
    # second arc: tangent at p1 is t1; build it backward from p1 and reverse
    tj = (q1 - q0)
    nj = float(np.hypot(*tj))
    tj = tj / nj if nj > 1e-12 else t0
    a2, *_ = _arc_from(j, tj, p1)
    return a1 + a2, j


def circle_heading(a, b, c) -> float:
    """Heading at ``b`` of the circle through a, b, c, travelling a → c
    (the chord direction when the points are collinear)."""
    a, b, c = (np.asarray(p, float) for p in (a, b, c))
    ab, bc = b - a, c - b
    cr = ab[0] * bc[1] - ab[1] * bc[0]
    if abs(cr) < 1e-9:
        v = c - a
        return math.degrees(math.atan2(v[1], v[0]))
    ctr, _ = _circle3_(a, b, c)
    rv = b - ctr
    t = np.array([-rv[1], rv[0]]) if cr > 0 else np.array([rv[1], -rv[0]])
    return math.degrees(math.atan2(t[1], t[0]))


def _circle3_(p, q, r):
    ax, ay = p
    bx, by = q
    cx, cy = r
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return np.array([ux, uy]), math.hypot(ax - ux, ay - uy)


def arc_spline(points, h_start: float | None = None, h_end: float | None = None, *,
               headings: dict | None = None) -> tuple[str, np.ndarray, list[float]]:
    """Smooth G1 curve of circular arcs through ``points``. Interior tangents
    come from the circle through each point and its neighbours (no spurious
    wiggles on convex runs); end tangents are ``h_start`` / ``h_end`` or the
    mirror of the neighbouring chord. ``headings`` {index: deg} pins any
    tangent. Returns (d, dense points, headings used)."""
    pts = [np.asarray(p, float) for p in points]
    n = len(pts)
    hs = [0.0] * n
    for i in range(1, n - 1):
        hs[i] = circle_heading(pts[i - 1], pts[i], pts[i + 1])

    def chord(i, j):
        v = pts[j] - pts[i]
        return math.degrees(math.atan2(v[1], v[0]))
    if n == 2:
        hs[0] = h_start if h_start is not None else chord(0, 1)
        hs[1] = h_end if h_end is not None else chord(0, 1)
    else:
        hs[0] = h_start if h_start is not None else 2 * chord(0, 1) - _near(hs[1], chord(0, 1))
        hs[-1] = h_end if h_end is not None else 2 * chord(n - 2, n - 1) - _near(hs[-2], chord(n - 2, n - 1))
    for i, h in (headings or {}).items():
        hs[i] = h
    d, P = biarc_chain(pts, hs)
    return d, P, hs


def _near(a: float, ref: float) -> float:
    """``a`` shifted by multiples of 360 to be within 180 of ``ref``."""
    while a - ref > 180:
        a -= 360
    while ref - a > 180:
        a += 360
    return a


def biarc_chain(points, headings, *, closed: bool = False) -> tuple[str, np.ndarray]:
    """G1 chain of biarcs through ``points`` with the given tangent
    ``headings`` (screen degrees) at each. Returns (d, dense points)."""
    pts = [np.asarray(p, float) for p in points]
    d = [f"M{pts[0][0]:.3f} {pts[0][1]:.3f}"]
    n = len(pts)
    rng = range(n if closed else n - 1)
    for i in rng:
        j = (i + 1) % n
        seg, _ = biarc(pts[i], headings[i], pts[j], headings[j])
        d.append(seg)
    if closed:
        d.append("Z")
    dd = "".join(d)
    from .core import sample_d
    return dd, sample_d(dd, 0.25)[0][0]


# ---------------------------------------------------------------------------
# leaves on a curved midrib
# ---------------------------------------------------------------------------
def vesica_hw(L: float, W: float) -> Callable[[np.ndarray], np.ndarray]:
    """Half-width of a vesica of length ``L`` and width ``W`` at arc position
    s (0..L): two circular arcs, as §G.4 'vesica-width profile'."""
    s_ = W / 2.0
    c = L / 2.0
    R = (c * c + s_ * s_) / (2 * s_)

    def hw(s):
        s = np.asarray(s, float)
        return np.maximum(np.sqrt(np.maximum(R * R - (s - c) ** 2, 0.0)) - (R - s_), 0.0)
    return hw


def _normals(cv: G.Curve, s: np.ndarray) -> np.ndarray:
    return cv.normal_s(s)          # left of travel on screen


def leaf_edges(mid_pts, hw: Callable, step: float = 0.35):
    """(left, right, closed_outline) point arrays of a leaf whose midrib is
    ``mid_pts`` (base → tip) and half-width function ``hw(s)``."""
    cv = G.Curve(np.asarray(mid_pts, float))
    n = max(8, int(math.ceil(cv.length / step)))
    s = np.linspace(0, cv.length, n + 1)
    P = cv.at_s(s)
    N = _normals(cv, s)
    h = hw(s)[:, None]
    left = P + N * h
    right = P - N * h
    left[0] = right[0] = P[0]
    left[-1] = right[-1] = P[-1]
    outline = np.vstack([left, right[::-1][1:-1]])
    return left, right, outline


def perp_hatch(mid_pts, hw: Callable, side: int = 1, *, pitch: float = T.HATCH_PITCH,
               s_range: tuple[float, float] | None = None, min_len: float = MIN_HATCH_LEN,
               w_edge: float = FINE, phase: float | None = None) -> list[np.ndarray]:
    """Hatch segments perpendicular to a curved midrib at ``pitch`` px of
    arc length, from the midrib centreline to the leaf edge centreline on
    ``side`` (+1 = left of travel base→tip, −1 = right). Butt-capped by the
    caller (style 'hatch'). Stations whose centreline length is below
    ``min_len`` are dropped (no specks at the tips)."""
    cv = G.Curve(np.asarray(mid_pts, float))
    L = cv.length
    a, b = s_range if s_range else (0.0, L)
    span = b - a
    if phase is None:
        k = max(1, int(round(span / pitch)) - 1)
        ss = (a + b) / 2 + (np.arange(k) - (k - 1) / 2) * pitch
    else:
        ss = np.arange(a + phase, b, pitch)
    out = []
    for s in ss:
        h = float(hw(np.array([s]))[0])
        if h < min_len:
            continue
        p = cv.at_s(s)
        nrm = _normals(cv, np.array([s]))[0] * side
        out.append(np.array([p, p + nrm * h]))
    return out


def leaf(mid_pts, width: float | None = None, *, hw: Callable | None = None, hatch: int = 1,
         midrib: str | None = "full", midrib_trim: tuple[float, float] = (0.0, 0.14),
         hatch_range: tuple[float, float] | None = None, pitch: float = T.HATCH_PITCH,
         w: float = FINE, color: str = T.INK, layer: str | None = None, outline: bool = True,
         style: str = "point", rake: float | None = None, rake_mode: str = "chord",
         midrib_min_hw: float | None = None) -> Frag:
    """A leaf / feather / spikelet: vesica-profile outline around a (curved)
    midrib, split on the midrib, ONE half hatched perpendicular to the
    midrib (§B.2, §G.4). ``hatch`` +1/−1 picks the half (left/right of
    travel base→tip), 0 = none. ``midrib`` 'full' draws the midrib from the
    base, stopping ``midrib_trim[1]`` × length short of the tip (a clean
    point, no three-line knot); None omits it. The outline is one closed
    stroke with sharp (miter-10) tips. ``meta``: base, tip, outline, mid.

    ``midrib_min_hw`` stops the midrib (and so the hatch) wherever the half-
    width falls below it — pass ``w + 4.2`` to keep the un-hatched half clear.

    ``rake`` (degrees) switches to FEATHER hatching: straight parallel lines
    (7 px pitch) at ``rake``° to the base→tip chord, leaning toward the tip
    like a feather's barbs, clipped exactly to the chosen half (between the
    midrib and that edge). ``rake_mode='local'`` measures the rake from the
    midrib's LOCAL tangent instead (barbs spring from the drawn midrib at
    stations 7/sin(rake) apart, so the pitch across them stays 7.0, and run
    to the edge) — right for long curved feathers.

    Hatch never ends in mid-air (§B.2): stations are limited to the DRAWN
    midrib (``midrib_trim``), so every line runs from the midrib to the
    outline centreline."""
    mid = np.asarray(mid_pts, float)
    cv = G.Curve(mid)
    L = cv.length
    if hw is None:
        hw = vesica_hw(L, width if width else L / 12.0)
    left, right, ol = leaf_edges(mid, hw)
    f = Frag()
    if outline:
        f += stroke(polyline_d(ol, closed=True), w, style=style, color=color, layer=layer, role="leaf")
    t0, t1 = midrib_trim if midrib else (0.0, 0.0)
    if midrib and midrib_min_hw:
        # stop the midrib where the leaf is too narrow to keep it clear of the edges (§I.12)
        ss_ = np.linspace(0, L, max(8, int(L / 0.5)))
        ok = hw(ss_) >= midrib_min_hw
        if ok.any():
            i_ok = np.where(ok)[0]
            t0 = max(t0, ss_[i_ok[0]] / L)
            t1 = max(t1, 1 - ss_[i_ok[-1]] / L)
        else:
            midrib = None
    if midrib:
        sub = cv.sub(t0, 1 - t1) if (t0 or t1) else cv
        f += stroke(polyline_d(sub.pts), w, style="ornament", color=color, layer=layer, role="midrib")
    drawn = (t0 * L, (1 - t1) * L) if midrib else (0.0, L)
    edge = left if hatch > 0 else right
    if hatch and rake is not None and rake_mode == "local":
        half = Polygon(np.vstack([edge, mid[::-1]])).buffer(0.01)
        step = pitch / math.sin(math.radians(rake))
        lines = []
        a_, b_ = hatch_range if hatch_range else drawn
        a_, b_ = max(a_, drawn[0]), min(b_, drawn[1])
        n_ = max(0, int((b_ - a_) / step))
        ss = (a_ + b_) / 2 + (np.arange(n_) - (n_ - 1) / 2) * step if n_ else []
        for s0 in ss:
            p = cv.at_s(s0)
            t = cv.tangent_s(s0)
            nrm = np.array([t[1], -t[0]]) * hatch            # toward the hatched half
            a = math.radians(rake)
            v = t * math.cos(a) + nrm * math.sin(a)          # leaning toward the tip
            seg = LineString([p, p + v * 400]).intersection(half)
            for g in getattr(seg, "geoms", [seg]):
                if g.is_empty or g.geom_type != "LineString":
                    continue
                c = np.asarray(g.coords)
                if np.hypot(*(c[0] - p)) < 0.3 and g.length >= MIN_HATCH_LEN:
                    lines.append(c[[0, -1]])
                    break
        if lines:
            f += stroke(lines, w, style="hatch", color=color, layer=layer, role="hatch")
    elif hatch and rake is not None:
        from .core import hatch_lines
        half = Polygon(np.vstack([edge, mid[::-1]])).buffer(0)
        ch = mid[-1] - mid[0]
        head = math.degrees(math.atan2(ch[1], ch[0]))
        lines = hatch_lines(half, head - hatch * rake, pitch)
        if lines:
            f += stroke(lines, w, style="hatch", color=color, layer=layer, role="hatch")
    elif hatch:
        # hatch lines butt on the outline centreline and on the DRAWN midrib
        rng = hatch_range if hatch_range else drawn
        rng = (max(rng[0], drawn[0]), min(rng[1], drawn[1]))
        lines = perp_hatch(mid, hw, hatch, pitch=pitch, s_range=rng)
        if lines:
            f += stroke(lines, w, style="hatch", color=color, layer=layer, role="hatch")
    f.meta.update(base=tuple(mid[0]), tip=tuple(mid[-1]), outline=ol, mid=mid, hw=hw)
    return f


# ---------------------------------------------------------------------------
# scallops (exact arcs)
# ---------------------------------------------------------------------------
def _circle3(p, q, r):
    """Centre and radius of the circle through three points."""
    ax, ay = p
    bx, by = q
    cx, cy = r
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return np.array([ux, uy]), math.hypot(ax - ux, ay - uy)


def scallop_arc(p, q, sag: float, *, move: bool = True) -> str:
    """Exact arc from cusp ``p`` to cusp ``q`` bulging ``sag`` px to the LEFT
    of p→q on screen (negative = right)."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    m = (p + q) / 2
    u = q - p
    L = float(np.hypot(*u))
    if abs(sag) < 1e-6 or L < 1e-9:                  # straight
        head = f"M{p[0]:.3f} {p[1]:.3f}" if move else ""
        return head + f"L{q[0]:.3f} {q[1]:.3f}"
    u = u / L
    nl = np.array([u[1], -u[0]])            # screen-left of p→q
    peak = m + nl * sag
    c, R = _circle3(p, q, peak)
    large = 1 if abs(sag) > L / 2 else 0
    sweep = 1 if sag > 0 else 0              # left bulge = clockwise on screen (SVG sweep 1)
    head = f"M{p[0]:.3f} {p[1]:.3f}" if move else ""
    return head + f"A{R:.3f} {R:.3f} 0 {large} {sweep} {q[0]:.3f} {q[1]:.3f}"


def scallop_ring(cx: float, cy: float, r_cusp: float, r_peak: float, n: int, *, phase: float = -90.0,
                 span: tuple[float, float] | None = None) -> tuple[str, list[np.ndarray], list[np.ndarray]]:
    """A ring (or partial ring, ``span`` = (a0, a1) screen degrees, a1 > a0)
    of ``n``-per-turn scallops: cusps on radius ``r_cusp`` at ``phase`` +
    k·360/n, each an exact arc bulging outward to ``r_peak`` at its middle.
    Returns (d, cusps, peaks)."""
    step = 360.0 / n
    if span is None:
        angs = [phase + k * step for k in range(n + 1)]
    else:
        a0, a1 = span
        k0 = math.ceil((a0 - phase) / step - 1e-9)
        k1 = math.floor((a1 - phase) / step + 1e-9)
        angs = [phase + k * step for k in range(k0, k1 + 1)]
    cusps = [polar(cx, cy, r_cusp, a) for a in angs]
    peaks = [polar(cx, cy, r_peak, a + step / 2) for a in angs[:-1]]
    d = []
    for i, (p, q, m) in enumerate(zip(cusps[:-1], cusps[1:], peaks)):
        c, R = _circle3(p, m, q)
        chord = float(np.hypot(*(q - p)))
        sag = float(np.hypot(*(m - (p + q) / 2)))
        large = 1 if sag > chord / 2 else 0
        head = f"M{p[0]:.3f} {p[1]:.3f}" if i == 0 else ""
        d.append(head + f"A{R:.3f} {R:.3f} 0 {large} 1 {q[0]:.3f} {q[1]:.3f}")
    return "".join(d), cusps, peaks


def scallop_row(base_pts, pitch: float, sag: float, *, side: int = 1, start: float = 0.0,
                end: float | None = None, sag_fn: Callable[[float], float] | None = None) -> tuple[str, list, list]:
    """Scallops along a base curve: cusps every ``pitch`` px of arc length
    from ``start`` to ``end``; each scallop is an exact arc between two
    consecutive cusps bulging ``sag`` px (or ``sag_fn(s_mid)``) to ``side``
    (+1 = left of travel). Returns (d, cusps, peaks)."""
    cv = G.Curve(np.asarray(base_pts, float))
    end = cv.length if end is None else end
    n = max(1, int(round((end - start) / pitch)))
    ss = np.linspace(start, end, n + 1)
    cusps = [cv.at_s(s) for s in ss]
    d, peaks = [], []
    for i in range(n):
        p, q = cusps[i], cusps[i + 1]
        sg = sag_fn((ss[i] + ss[i + 1]) / 2) if sag_fn else sag
        sg = sg * side
        d.append(scallop_arc(p, q, sg, move=(i == 0)))
        u = (q - p) / np.hypot(*(q - p))
        peaks.append((p + q) / 2 + np.array([u[1], -u[0]]) * sg)
    return "".join(d), cusps, peaks


# ---------------------------------------------------------------------------
# QA: tight gaps
# ---------------------------------------------------------------------------
def tight_spots(f: Frag, min_gap: float = MIN_CLEAR, *, res: float = 0.25, pad: float = 6.0,
                ignore_junction: float = 0.0) -> dict:
    """Ground gaps narrower than ``min_gap`` between the marks of ``f`` (line
    mode, §I.12): rasterises the union of all marks at ``res`` px and
    returns the ground area that vanishes under a morphological opening of
    diameter ``min_gap``. Converging V-junctions and tips always show a
    little; look at ``mask`` (bool raster) / ``extent`` to judge.
    Returns {area, mask, extent}."""
    from scipy import ndimage
    x0, y0, x1, y1 = f.bbox()
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    W = int(math.ceil((x1 - x0) / res))
    H = int(math.ceil((y1 - y0) / res))
    xs = x0 + (np.arange(W) + 0.5) * res
    ys = y0 + (np.arange(H) + 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    ink = shapely.contains_xy(f.shape(), X, Y)
    ground = ~ink
    k = int(math.ceil(min_gap / 2 / res))
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    disk = (xx * res) ** 2 + (yy * res) ** 2 <= (min_gap / 2 * 0.98) ** 2
    opened = ndimage.binary_opening(ground, structure=disk)
    thin = ground & ~opened
    # the outer border region counts as open ground
    thin[:k + 1, :] = thin[-k - 1:, :] = False
    thin[:, :k + 1] = thin[:, -k - 1:] = False
    return {"area": float(thin.sum() * res * res), "mask": thin, "extent": (x0, y0, x1, y1), "res": res}


def lock_row(base_pts, pitch: float, depth: float, *, side: int = 1, skew: float = 0.68,
             rise: float = 22.0, dive: float = 62.0, start: float = 0.0, end: float | None = None,
             depth_fn: Callable[[float], float] | None = None) -> tuple[str, list, list]:
    """Mane / fur LOCKS along a base curve: like :func:`scallop_row` but each
    scallop is lopsided — it rises gently from its first cusp, peaks at
    ``skew`` of the way along and dives steeply into the next cusp, so the
    row reads as locks flowing in the direction of travel (flame-like, never
    wool or petals). Each lock is two tangent circular arcs (arc spline).
    ``side`` +1 bulges left of travel. Returns (d, cusps, peaks)."""
    cv = G.Curve(np.asarray(base_pts, float))
    end = cv.length if end is None else end
    n = max(1, int(round((end - start) / pitch)))
    ss = np.linspace(start, end, n + 1)
    cusps = [cv.at_s(s) for s in ss]
    out, peaks = [], []
    for i in range(n):
        p, q = cusps[i], cusps[i + 1]
        t = (q - p) / np.hypot(*(q - p))
        nl = np.array([t[1], -t[0]]) * side                  # outward normal
        dep = depth_fn((ss[i] + ss[i + 1]) / 2) if depth_fn else depth
        pk = p + (q - p) * skew + nl * dep
        h0 = math.degrees(math.atan2(t[1], t[0]))
        h_s = h0 - side * rise
        h_e = h0 + side * dive
        d, _, _ = arc_spline([p, pk, q], h_start=h_s, h_end=h_e)
        out.append(d if i == 0 else d.replace("M", "L", 1))
        peaks.append(pk)
    return "".join(out), cusps, peaks


def tuft_row(base_pts, pitch: float, depth: float, *, side: int = 1, skew: float = 0.62,
             bow: float = 0.16, start: float = 0.0, end: float | None = None,
             depth_fn: Callable[[float], float] | None = None) -> tuple[str, list, list]:
    """Pointed TUFTS (fur, mane) along a base curve: each tuft is two convex
    circular arcs meeting in a sharp tip ``depth`` px out, the tip leaning
    ``skew`` of the way toward the next cusp (the direction of flow). Round
    scallops read as fleece in profile; pointed tufts read as a mane.
    ``bow`` = each arc's sagitta as a fraction of its chord. Draw with style
    'point' so the tips stay sharp. Returns (d, cusps, tips)."""
    cv = G.Curve(np.asarray(base_pts, float))
    end = cv.length if end is None else end
    n = max(1, int(round((end - start) / pitch)))
    ss = np.linspace(start, end, n + 1)
    cusps = [cv.at_s(s) for s in ss]
    out, tips = [], []
    for i in range(n):
        p, q = cusps[i], cusps[i + 1]
        t = (q - p) / np.hypot(*(q - p))
        nl = np.array([t[1], -t[0]]) * side
        dep = depth_fn((ss[i] + ss[i + 1]) / 2) if depth_fn else depth
        tip = p + (q - p) * skew + nl * dep
        c1 = float(np.hypot(*(tip - p)))
        c2 = float(np.hypot(*(q - tip)))
        a = scallop_arc(p, tip, side * bow * c1, move=(i == 0))
        b = scallop_arc(tip, q, side * bow * c2, move=False)
        out.append(a + b)
        tips.append(tip)
    return "".join(out), cusps, tips


def lock_ring(cx: float, cy: float, r_cusp: float, r_peak: float, n: int = 12, *, skew: float = 0.66,
              rise: float = 24.0, dive: float = 64.0, top: str = "cusp") -> tuple[str, "Polygon"]:
    """A closed, bilaterally symmetric ring of ``n`` (even) lopsided LOCKS — a
    scalloped ring whose scallops flow from the crown DOWN both sides (the
    frontal mane, §G.2 "rings of scalloped arcs"): each lock rises gently
    from its upper cusp, peaks ``skew`` of the way along and dives steeply
    into the next cusp (two tangent circular arcs, :func:`lock_row`). The
    right half runs clockwise from the top of the axis to the bottom; the
    left half is its mirror. ``top`` 'cusp' puts cusps on the axis (n/2
    locks a side); 'mound' centres one symmetric scallop on the axis at the
    top and the bottom (n/2 − 1 lopsided locks a side), for alternate rings.
    Returns (d — two open halves meeting on the axis, filled Polygon)."""
    half = n // 2
    if top == "cusp":
        a0, a1, k = -90.0, 90.0, half
    else:
        a0, a1, k = -90.0 + 180.0 / n, 90.0 - 180.0 / n, half - 1
    ang = np.radians(np.linspace(a0, a1, 600))
    base = np.column_stack([cx + r_cusp * np.cos(ang), cy + r_cusp * np.sin(ang)])
    L = G.Curve(base).length
    d_r, _, _ = lock_row(base, L / k, r_peak - r_cusp, side=1, skew=skew, rise=rise, dive=dive)
    parts = [d_r]
    if top != "cusp":
        # symmetric mounds centred on the axis at the top and the bottom
        for a in (-90.0, 90.0):
            p = polar(cx, cy, r_cusp, a - 180.0 / n)
            q = polar(cx, cy, r_cusp, a + 180.0 / n)
            c = float(np.hypot(*(q - p)))
            sag = r_peak - r_cusp + (r_cusp - math.sqrt(max(r_cusp ** 2 - c * c / 4, 0)))
            parts.append(scallop_arc(p, q, sag))
    d_half = "".join(parts)
    d_l = G.mirror_x(d_r, cx)
    d = d_half + d_l
    from .core import sample_d as _sd
    wedges = [shapely.geometry.Point(cx, cy).buffer(r_cusp, quad_segs=64)]
    for pp, _ in _sd(d, 0.3):
        wedges.append(Polygon(np.vstack([pp, [(cx, cy)]])).buffer(0))
    poly = shapely.union_all(wedges).buffer(0)
    return d, poly
