"""Variable-width (tapered / swelled / calligraphic) strokes -> filled outlines.

The outline is the exact envelope of a moving disc of radius w(t)/2 along the
centreline (with the dr/ds correction so steep tapers stay tangent-continuous).
Wherever the inner offset would fold (curvature * radius > ~0.6, or sharp
corners) the fold region is rebuilt from tangent-capsules between consecutive
discs and unioned with skia-pathops, so tight spirals and hairpins never show
notches or self-intersection artefacts.

    from inkkit.stroke import stroke
    d = stroke("M100 500 C 200 300 400 700 500 500", width=6, profile="taper-both")
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np
import pathops
from shapely.geometry import LineString

from . import geom as G

__all__ = ["stroke", "stroke_many", "variable_stroke", "profile_fn", "PROFILES", "ease",
           "styled", "STYLES"]


# =============================================================================
# width profiles  (t in [0,1] arc-length fraction -> factor in [0,1])
# =============================================================================
def ease(u, power: float = 1.0):
    """Taper ramp: 0 at u=0, 1 at u>=1, zero slope at u=1 (no kink where the
    taper meets the full-width section) and finite slope at 0 (a clean point).
    power<1 gives a blunter (rounder) tip, >1 a finer needle tip. Steep ramps
    are handled by :func:`variable_stroke`, which rebuilds any end whose
    radius changes faster than the arc length from exact disc hulls."""
    u = np.clip(np.asarray(u, float), 0.0, 1.0)
    return np.sin(u * (math.pi / 2)) ** power


def _beta(t, a, b):
    t = np.clip(t, 0, 1)
    m = a / (a + b)
    peak = m ** a * (1 - m) ** b
    return (t ** a * (1 - t) ** b) / peak


def profile_fn(profile="uniform", taper: float = 0.3, power: float = 1.0,
               end_ratio: float = 0.12, swell: float = 1.0, **_) -> Callable:
    """Return f(t)->factor for a named profile (or pass a callable through).

    uniform     constant width
    taper-both  pointed both ends, taper over ``taper`` fraction each end
    taper-end   full start (round cap) -> point at end
    taper-start point at start -> full end
    swell       lens: sin(pi t)^swell (pointed both ends, fattest mid)
    teardrop    heavy rounded head at 25%, long fine tail (comma/stroke of a leaf)
    scroll      short pointed entry, full early, thins to ``end_ratio`` hairline
    hairline-end full -> ``end_ratio`` (no point, for ball terminals)
    nib         uniform base; combine with nib_angle for calligraphic contrast
    """
    if callable(profile):
        return profile
    a = max(1e-3, float(taper))
    if profile in ("uniform", "mono", "nib", None):
        return lambda t: np.ones_like(np.asarray(t, float))
    if profile == "taper-both":
        return lambda t: ease(np.asarray(t) / a, power) * ease((1 - np.asarray(t)) / a, power)
    if profile == "taper-end":
        return lambda t: ease((1 - np.asarray(t)) / a, power)
    if profile == "taper-start":
        return lambda t: ease(np.asarray(t) / a, power)
    if profile == "swell":
        return lambda t: np.sin(np.pi * np.clip(t, 0, 1)) ** swell
    if profile == "teardrop":
        return lambda t: _beta(np.asarray(t, float), 0.45, 1.35)
    if profile == "teardrop-rev":
        return lambda t: _beta(1 - np.asarray(t, float), 0.45, 1.35)
    if profile == "scroll":
        def f(t):
            t = np.asarray(t, float)
            body = 1 - (1 - end_ratio) * (t ** 0.85)
            return ease(t / min(a, 0.12), power) * body
        return f
    if profile == "hairline-end":
        return lambda t: 1 - (1 - end_ratio) * ease(np.asarray(t, float), 1.0) ** 1.0
    raise ValueError(f"unknown profile {profile!r}")


PROFILES = ("uniform", "taper-both", "taper-end", "taper-start", "swell", "teardrop",
            "teardrop-rev", "scroll", "hairline-end", "nib")


# =============================================================================
# envelope construction
# =============================================================================
def _arc(c, r, a0, a1, tol=0.02):
    span = a1 - a0
    if r <= 1e-6:
        return np.array([c])
    step = 2 * math.acos(max(-1.0, 1 - tol / r)) if r > tol else math.pi / 2
    n = max(2, int(math.ceil(abs(span) / max(step, 1e-3))) + 1)
    a = np.linspace(a0, a1, n)
    return np.column_stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)])


def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def _cap(c, r, p_from, p_to, direction, tol):
    """Arc on circle (c, r) from p_from to p_to passing through ``direction``."""
    if r <= 1e-3:
        return np.array([c])
    a0 = math.atan2(p_from[1] - c[1], p_from[0] - c[0])
    a1 = math.atan2(p_to[1] - c[1], p_to[0] - c[0])
    ad = math.atan2(direction[1], direction[0])
    # choose sweep sign so the arc passes through ad
    s = 1.0 if _wrap(ad - a0) >= 0 else -1.0
    sweep = (a1 - a0) * s % (2 * math.pi)
    return _arc(c, r, a0, a0 + s * sweep, tol)


def _capsule(c1, r1, c2, r2, tol):
    """Convex hull of two discs as a consistently oriented polygon."""
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    if d <= abs(r1 - r2) + 1e-9:
        c, r = (c1, r1) if r1 >= r2 else (c2, r2)
        return _arc(c, max(r, 1e-3), 0, 2 * math.pi, tol)[:-1]
    phi = math.atan2(dy, dx)
    beta = math.acos(max(-1.0, min(1.0, (r1 - r2) / d)))
    a1 = _arc(c1, r1, phi + beta, phi + 2 * math.pi - beta, tol)
    a2 = _arc(c2, r2, phi - beta, phi + beta, tol)
    return np.vstack([a1, a2])


def _signed_area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _dp(P, tol):
    if len(P) < 3 or tol <= 0:
        return P
    return np.asarray(LineString(P).simplify(tol, preserve_topology=False).coords)


def _add_contour(path: pathops.Path, P, orient=1.0):
    if len(P) < 3:
        return
    if _signed_area(P) * orient < 0:
        P = P[::-1]
    path.moveTo(float(P[0, 0]), float(P[0, 1]))
    for x, y in P[1:]:
        path.lineTo(float(x), float(y))
    path.close()


def variable_stroke(pts, radii, *, closed: bool = False, start_cap: str = "round",
                    end_cap: str = "round", tol: float = 0.04, fold: float = 0.6,
                    as_skia: bool = False):
    """Low-level: outline of discs of radius ``radii[i]`` centred on ``pts[i]``.

    ``pts`` should already be densely sampled (<=1px). Caps: 'round' | 'flat'.
    Returns d (FILL) or a pathops.Path when ``as_skia``."""
    P = np.asarray(pts, float)
    R = np.maximum(np.asarray(radii, float), 0.0)
    out = pathops.Path(fillType=pathops.FillType.WINDING)
    if len(P) < 2:
        if len(P) == 1 and R[0] > 0:
            _add_contour(out, _arc(P[0], R[0], 0, 2 * math.pi, tol)[:-1])
        return out if as_skia else G.from_skia(out)
    if closed:
        P2 = np.vstack([P[-1:], P, P[:1]])
        T = (P2[2:] - P2[:-2])
    else:
        T = np.gradient(P, axis=0)
    Tn = np.hypot(T[:, 0], T[:, 1])[:, None]
    T = T / np.where(Tn == 0, 1, Tn)
    N = np.column_stack([T[:, 1], -T[:, 0]])
    seg = np.hypot(*np.diff(P, axis=0).T)
    s = np.r_[0.0, np.cumsum(seg)]
    if closed:
        segc = np.r_[seg, math.hypot(*(P[0] - P[-1]))]
        dsl = np.r_[segc[-1], segc[:-1]]
        R2 = np.r_[R[-1], R, R[0]]
        dr = (R2[2:] - R2[:-2]) / np.maximum(dsl + segc, 1e-9)
    else:
        dr = np.gradient(R, s) if len(P) > 2 else np.full(len(P), (R[1] - R[0]) / max(seg[0], 1e-9))
    # |dr/ds| near 1 means one disc (almost) swallows the next: the two-sided
    # envelope does not exist there and the offset points fold back behind the
    # tip (swallowtails / fishtails). Such samples are rebuilt from disc hulls.
    steep = np.abs(dr) > 0.85
    dr = np.clip(dr, -0.97, 0.97)
    cs = np.sqrt(1 - dr * dr)
    L = P + R[:, None] * (-dr[:, None] * T + cs[:, None] * N)
    Rt = P + R[:, None] * (-dr[:, None] * T - cs[:, None] * N)

    # --- fold detection: turning per unit length * radius -----------------------
    if closed:
        Tp, Tq = T, np.roll(T, -1, axis=0)
        dsx = np.r_[seg, math.hypot(*(P[0] - P[-1]))]
    else:
        Tp, Tq = T[:-1], T[1:]
        dsx = seg
    cross = Tp[:, 0] * Tq[:, 1] - Tp[:, 1] * Tq[:, 0]
    dot = np.clip((Tp * Tq).sum(1), -1, 1)
    turn = np.abs(np.arctan2(cross, dot))
    kappa = turn / np.maximum(dsx, 1e-9)
    rr = np.maximum(R[:len(kappa)], R[(np.arange(len(kappa)) + 1) % len(R)])
    flag = (kappa * rr > fold) | (turn > 0.5)
    flag |= steep[:len(flag)] | steep[(np.arange(len(flag)) + 1) % len(steep)]
    bad = np.where(flag)[0]

    # --- body contour --------------------------------------------------------------
    if closed:
        _add_contour(out, _dp(np.vstack([L, L[:1]]), tol)[:-1], 1.0)
        _add_contour(out, _dp(np.vstack([Rt, Rt[:1]]), tol)[:-1], -1.0)
        # region between rings: orient so the ring area has winding != 0
        body = out
    else:
        pieces = [_dp(L, tol)]
        if end_cap == "round" and R[-1] > 1e-3:
            pieces.append(_cap(P[-1], R[-1], L[-1], Rt[-1], T[-1], tol)[1:-1])
        pieces.append(_dp(Rt[::-1], tol))
        if start_cap == "round" and R[0] > 1e-3:
            pieces.append(_cap(P[0], R[0], Rt[0], L[0], -T[0], tol)[1:-1])
        C = np.vstack(pieces)
        body = pathops.Path(fillType=pathops.FillType.WINDING)
        _add_contour(body, C, 1.0)
    try:
        body.simplify(fix_winding=True)
    except pathops.PathOpsError:
        pass

    if len(bad):
        # expand each flagged index to cover the fold's reach (~2r of arc length)
        n = len(P)
        mark = np.zeros(n, bool)
        spacing = max(float(np.median(seg)) if len(seg) else 1.0, 1e-3)
        for i in bad:
            reach = int(math.ceil(2.2 * max(R[i], R[(i + 1) % n]) / spacing)) + 2
            lo, hi = i - reach, i + reach + 2
            if closed:
                mark[np.arange(lo, hi) % n] = True
            else:
                mark[max(0, lo):min(n, hi)] = True
        caps = pathops.Path(fillType=pathops.FillType.WINDING)
        # capsule stations: consecutive discs are hulled pairwise. Stations are
        # spaced so the chord sagitta stays < ~0.03 px (dense where curvature
        # or radius change is high, sparse on wide gentle folds -> fast).
        kap_n = np.r_[kappa, kappa[-1:]] if len(kappa) < n else kappa[:n]
        idx = np.where(mark)[0]
        runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1) if len(idx) else []
        if closed and len(runs) > 1 and runs[0][0] == 0 and runs[-1][-1] == n - 1:
            runs = [np.r_[runs[-1], runs[0]]] + runs[1:-1]
        s_ext = np.r_[s, s[-1] + (segc[-1] if closed else 0.0)] if closed else s
        for run in runs:
            if len(run) == 0:
                continue
            if closed:
                run = np.r_[run, run[0]] if len(run) >= n else np.r_[run, (run[-1] + 1) % n]
            elif run[-1] + 1 < n:
                run = np.r_[run, run[-1] + 1]
            stations = [int(run[0])]
            acc = 0.0
            for a, b in zip(run[:-1], run[1:]):
                a, b = int(a), int(b)
                ds = (s[b] - s[a]) if b > a else (s_ext[-1] - s[a] + s[b])
                acc += abs(ds)
                k = max(kap_n[a], 1e-6)
                lim = min(math.sqrt(8 * 0.03 / k), 0.35 * max(min(R[a], R[b]), 1e-3))
                lim = max(lim, spacing * 1.01)
                steep_here = steep[a] or steep[b]
                if acc >= lim or steep_here or b == int(run[-1]):
                    stations.append(b)
                    acc = 0.0
            for i, j in zip(stations[:-1], stations[1:]):
                if R[i] <= 1e-4 and R[j] <= 1e-4:
                    continue
                cap = _capsule(P[i], max(R[i], 1e-4), P[j], max(R[j], 1e-4), tol)
                _add_contour(caps, cap, 1.0)
        try:
            caps.simplify(fix_winding=True)
        except pathops.PathOpsError:
            pass
        body = G._sk_op(body, caps, pathops.PathOp.UNION)
    return body if as_skia else G.from_skia(body)


# =============================================================================
# public API
# =============================================================================
_CAPS = ("round", "flat", "butt", "pointed")
_TERMINALS = (None, "ball", "ball-end", "ball-start", "ball-both")


def _width_array(width, t):
    """Evaluate a scalar or callable width on t; always an array shaped like t."""
    if callable(width):
        return np.array(np.broadcast_to(np.asarray(width(t), float), np.shape(t)), float)
    return np.full(np.shape(t), float(width))


def stroke(path, width=2.0, profile="uniform", *, taper: float = 0.3,
           taper_len: float | None = None, power: float = 1.0, swell: float = 1.0,
           end_ratio: float = 0.12, cap: str = "round", start_cap: str | None = None,
           end_cap: str | None = None, min_width: float = 0.0,
           nib_angle: float | None = None, nib_min: float = 0.22,
           terminal: str | None = None, terminal_r: float | None = None,
           spacing: float | None = None, tol: float = 0.04, keep_corners: float = 25.0,
           merge: bool = False) -> str:
    """Variable-width stroke of a centreline -> FILL d (clockwise outlines).

    path       d-string (curves ok) / points / any pathlike (each subpath stroked)
    width      max width in px, or callable(t)->px (then ``profile`` multiplies it)
    profile    see :func:`profile_fn` (name or callable(t)->0..1)
    taper      taper length as fraction of the length per end (clamped to 0.5);
               or ``taper_len`` px
    cap        'round' | 'flat' ('butt') | 'pointed' (adds a short taper at that end)
    nib_angle  degrees: broad-nib calligraphic contrast; width *= nib_min + (1-nib_min)*|sin(dir-angle)|
    terminal   'ball' adds a round terminal at the end ('ball-start' / 'ball-both')
    min_width  floor on width: tapers end in a round cap of this width instead of
               a zero-width needle (use the print minimum, ~1.05 px offset / 2.4 px foil)
    merge      union all subpaths into one clean outline (slower)
    """
    for nm, v in (("cap", cap), ("start_cap", start_cap or cap), ("end_cap", end_cap or cap)):
        if v not in _CAPS:
            raise ValueError(f"{nm} must be one of {_CAPS}, not {v!r}")
    if terminal not in _TERMINALS:
        raise ValueError(f"terminal must be one of {_TERMINALS}, not {terminal!r}")
    if not callable(width) and not (float(width) > 0):
        raise ValueError(f"width must be > 0, got {width!r}")
    taper = float(np.clip(taper, 1e-3, 0.5))
    polys = G.as_polys(path, tol=0.02)
    out = []
    for pts, closed in polys:
        if len(pts) < 2:
            continue
        cv = G.Curve(pts, closed)
        if cv.length < 1e-6:
            continue
        if callable(width):
            wmax = float(np.max(_width_array(width, np.linspace(0, 1, 33))))
        else:
            wmax = float(width)
        if not wmax > 0:
            continue
        sc = start_cap or cap
        ec = end_cap or cap
        simple = (not callable(width) and not callable(profile) and profile in ("uniform", "mono", None)
                  and nib_angle is None and sc == ec and sc in ("round", "flat", "butt"))
        if simple:
            # uniform width: shapely's exact buffer (fast at any width)
            sk = G.to_skia(G.outline([(pts, closed)], max(wmax, min_width), cap=sc, simplify=0.01))
        else:
            sp = spacing or float(np.clip(wmax / 6.0, 0.2, 0.9))
            P = cv.resample(sp, keep_corners=keep_corners)
            if closed:
                seg = np.hypot(*np.diff(np.vstack([P, P[:1]]), axis=0).T)
                s = np.r_[0.0, np.cumsum(seg)][:-1]
                t = s / max(cv.length, 1e-9)
            else:
                seg = np.hypot(*np.diff(P, axis=0).T)
                s = np.r_[0.0, np.cumsum(seg)]
                t = s / max(s[-1], 1e-9)
            tp = taper
            if taper_len is not None:
                tp = float(np.clip(taper_len / max(cv.length, 1e-9), 1e-3, 0.5))
            f = profile_fn(profile, taper=tp, power=power, end_ratio=end_ratio, swell=swell)
            W = _width_array(width, t) * np.broadcast_to(np.asarray(f(t), float), t.shape)
            if nib_angle is not None:
                T = np.gradient(P, axis=0)
                ang = np.arctan2(T[:, 1], T[:, 0])
                W = W * (nib_min + (1 - nib_min) * np.abs(np.sin(ang - math.radians(nib_angle))))
            if not closed:
                L = s[-1]
                tl = taper_len if taper_len is not None else min(3.0 * wmax, 0.3 * L)
                if sc == "pointed":
                    W = W * ease(s / max(tl, 1e-6), power)
                    sc = "round"
                if ec == "pointed":
                    W = W * ease((L - s) / max(tl, 1e-6), power)
                    ec = "round"
            if min_width:
                W = np.maximum(W, min_width)
            sc = "flat" if sc == "butt" else sc
            ec = "flat" if ec == "butt" else ec
            sk = variable_stroke(P, W / 2, closed=closed, start_cap=sc, end_cap=ec, tol=tol,
                                 as_skia=True)
        if terminal and not closed:
            P = cv.pts
            tr = terminal_r if terminal_r is not None else 0.55 * wmax
            ends = []
            if terminal in ("ball", "ball-end", "ball-both"):
                ends.append((P[-1], P[-1] - P[-2]))
            if terminal in ("ball-start", "ball-both"):
                ends.append((P[0], P[0] - P[1]))
            for c, dvec in ends:
                dn = dvec / max(np.hypot(*dvec), 1e-9)
                cc = c - dn * tr * 0.35  # sit the ball slightly back so the line flows into it
                ball = pathops.Path(fillType=pathops.FillType.WINDING)
                _add_contour(ball, _arc(cc, tr, 0, 2 * math.pi, tol)[:-1], 1.0)
                sk = G._sk_op(sk, ball, pathops.PathOp.UNION)
        out.append(sk)
    if not out:
        return ""
    if merge and len(out) > 1:
        return G.from_skia(G._sk_union_all(out))
    return "".join(G.from_skia(sk) for sk in out)


def stroke_many(paths, **kw) -> str:
    """Stroke each pathlike in ``paths`` with the same settings; returns one d."""
    return "".join(stroke(p, **kw) for p in paths)


# =============================================================================
# ornament line styles
# =============================================================================
STYLES = ("taper", "monoline", "outline", "inline")


def styled(path, width=4.0, profile="uniform", *, style: str = "taper", lw: float | None = None,
           inline: float | None = None, min_width: float = 0.0, cap: str = "round", **kw) -> str:
    """Draw a centreline in one of the ornament line styles -> FILL d.

    taper     variable-width engraved stroke (:func:`stroke`, ``profile``)
    monoline  uniform ``lw`` (default 2.1 px) with round caps — the Monarchs /
              Drifters monoline look; ``profile`` and terminals are ignored
              except ball terminals, drawn as discs of ``lw``·1.5
    outline   the tapered envelope drawn as an ``lw`` (default 1.05 px) line — a
              hollow, 'open-face' stroke
    inline    tapered stroke with a centre hairline (``inline`` px, default
              max(0.9, 0.16·width)) knocked out where the stroke is wide
              enough to hold it
    """
    if style not in STYLES:
        raise ValueError(f"style must be one of {STYLES}, not {style!r}")
    if style == "taper":
        return stroke(path, width, profile, min_width=min_width, cap=cap, **kw)
    if style == "monoline":
        w = lw if lw is not None else 2.1
        d = G.outline(path, w, cap="flat" if cap in ("flat", "butt") else "round")
        term = kw.get("terminal")
        if term:
            tr = kw.get("terminal_r") or w * 0.75
            tr = max(tr, w * 0.75)
            for pts, closed in G.as_polys(path, 0.02):
                if closed or len(pts) < 2:
                    continue
                ends = []
                if term in ("ball", "ball-end", "ball-both"):
                    ends.append(pts[-1])
                if term in ("ball-start", "ball-both"):
                    ends.append(pts[0])
                d += "".join(G.circle_d(e[0], e[1], tr) for e in ends)
        return d
    body = stroke(path, width, profile, min_width=min_width, cap=cap, **kw)
    if not body:
        return ""
    if style == "outline":
        w = lw if lw is not None else 1.05
        return G.outline(body, w, join="round")
    # inline: knock a centre hairline out of the wide parts
    iw = inline if inline is not None else max(0.9, 0.16 * (float(width) if not callable(width) else 4.0))
    cuts = []
    for pts, closed in G.as_polys(path, 0.02):
        if len(pts) < 2:
            continue
        cv = G.Curve(pts, closed)
        t = np.linspace(0, 1, max(8, int(cv.length / 0.8)))
        f = profile_fn(profile, taper=kw.get("taper", 0.3), power=kw.get("power", 1.0),
                       end_ratio=kw.get("end_ratio", 0.12), swell=kw.get("swell", 1.0))
        W = _width_array(width, t) * np.broadcast_to(np.asarray(f(t), float), t.shape)
        ok = W >= 3.4 * iw
        if not ok.any():
            continue
        idx = np.where(ok)[0]
        for run in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):
            if len(run) < 3:
                continue
            sub = cv.sub(t[run[0]], t[run[-1]])
            if sub.length > 4 * iw:
                cuts.append(stroke(sub.pts, iw, "taper-both", taper=0.35))
    return G.difference(body, *cuts) if cuts else body
