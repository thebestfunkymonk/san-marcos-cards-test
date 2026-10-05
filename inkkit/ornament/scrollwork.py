"""Scrolls, volutes, acanthus and filigree built from curvature-integrated curves.

Every scroll centreline is produced by integrating a smooth curvature law, so
curls tighten monotonically and never wobble:

* ``law='log'`` (default for volutes): the radius of curvature shrinks
  linearly with arc length — a logarithmic (Ionic) volute whose turns shrink
  by a constant factor ``tighten`` per revolution, so turn spacing stays even
  and the eye never clogs;
* ``law='power'``: kappa(s) = k0 + (k1-k0)(s/L)^power (power=1 is an Euler
  spiral / clothoid) — tighter, more calligraphic eyes.

Strokes are rendered with :func:`inkkit.stroke.styled`, so every generator
takes ``style`` = 'taper' (engraved swell) | 'monoline' (uniform ``lw``, the
Monarchs/Drifters look) | 'outline' | 'inline', and ``min_width`` (default:
the offset-print minimum) so no taper ends in an unprintable needle.

Angles are screen degrees (0 = +x, 90 = down). ``cw=True`` curls clockwise on
screen.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.spatial import cKDTree

from .. import geom as G
from .. import tokens as T
from ..stroke import STYLES, profile_fn, styled

__all__ = ["curl", "volute", "log_spiral", "s_curve", "fit", "flourish", "branch", "scroll",
           "c_scroll", "s_scroll", "acanthus_leaf", "filigree_corner", "filigree_corners",
           "filigree_band", "place_corner", "volute_eye"]


def _check_style(style):
    if style not in STYLES:
        raise ValueError(f"style must be one of {STYLES}, not {style!r}")


# =============================================================================
# centreline generators
# =============================================================================
def _integrate(p0, heading_rad, kappa, ds):
    th = heading_rad + np.concatenate([[0.0], np.cumsum(0.5 * (kappa[1:] + kappa[:-1]) * ds)])
    c, s = np.cos(th), np.sin(th)
    x = p0[0] + np.concatenate([[0.0], np.cumsum(0.5 * (c[1:] + c[:-1]) * ds)])
    y = p0[1] + np.concatenate([[0.0], np.cumsum(0.5 * (s[1:] + s[:-1]) * ds)])
    return np.column_stack([x, y]), th


def curl(p0=(0.0, 0.0), heading: float = 0.0, length: float = 100.0, turns: float = 1.0,
         power: float = 2.0, k0: float = 0.0, cw: bool = True, ds: float = 0.25) -> np.ndarray:
    """Spiral centreline whose curvature grows from ``k0`` as (s/L)^power so the
    total turning is ``turns`` revolutions. Returns (N,2) points (start -> eye)."""
    if not length > 0:
        raise ValueError(f"curl: length must be > 0, got {length!r}")
    if not turns > 0:
        raise ValueError(f"curl: turns must be > 0, got {turns!r}")
    n = max(8, int(length / ds) + 1)
    s = np.linspace(0, length, n)
    total = 2 * math.pi * turns
    k1 = k0 + (total - k0 * length) * (power + 1) / length
    kappa = k0 + (k1 - k0) * (s / length) ** power
    if not cw:
        kappa = -kappa
    pts, _ = _integrate(p0, math.radians(heading), kappa, s[1] - s[0])
    return pts


def _smoothstep(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def _volute_kappa(s, L, rho0, c, k0, entry):
    rho = np.maximum(rho0 - c * s, 1e-6)
    ramp = _smoothstep(s / max(entry * L, 1e-9)) if entry > 0 else np.ones_like(s)
    return k0 + (1.0 / rho - k0) * ramp


def volute(p0=(0.0, 0.0), heading: float = 0.0, length: float = 100.0, turns: float = 1.25, *,
           cw: bool = True, tighten: float = 2.2, entry: float = 0.25, k0: float = 0.0,
           ds: float = 0.25) -> np.ndarray:
    """Ionic (logarithmic) volute centreline of arc ``length`` making ``turns``
    revolutions. The curvature radius shrinks linearly with arc length, so each
    turn is ``tighten``× smaller than the previous one (even, open spacing —
    the eye never clogs). The first ``entry`` fraction eases in from curvature
    ``k0`` (G2 join to whatever precedes it). Returns (N,2) points."""
    if not length > 0:
        raise ValueError(f"volute: length must be > 0, got {length!r}")
    if not turns > 0:
        raise ValueError(f"volute: turns must be > 0, got {turns!r}")
    if not tighten > 1:
        raise ValueError(f"volute: tighten must be > 1, got {tighten!r}")
    n = max(16, int(length / ds) + 1)
    s = np.linspace(0, length, n)
    c = math.log(tighten) / (2 * math.pi)
    target = 2 * math.pi * turns
    k0a = abs(k0)

    def turning(rho0):
        k = _volute_kappa(s, length, rho0, c, k0a, entry)
        return float(np.sum(0.5 * (k[1:] + k[:-1]) * (s[1] - s[0])))

    lo, hi = c * length * (1 + 1e-9) + 1e-9, max(1.0, c * length) * 1e4
    if turning(hi) > target:   # entry curvature alone turns further: just a clothoid
        kappa = np.full_like(s, k0a)
    else:
        for _ in range(80):
            mid = math.sqrt(lo * hi)
            if turning(mid) > target:
                lo = mid
            else:
                hi = mid
        kappa = _volute_kappa(s, length, hi, c, k0a, entry)
    if not cw:
        kappa = -kappa
    pts, _ = _integrate(p0, math.radians(heading), kappa, s[1] - s[0])
    return pts


def volute_eye(pts) -> tuple[np.ndarray, float]:
    """(centre, radius) of the osculating circle at the end of a volute
    centreline — where an 'eye' terminal sits."""
    P = np.asarray(pts, float)
    k = min(len(P) - 1, 16)
    a, b, c = P[-1 - k], P[-1 - k // 2], P[-1]
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return c.copy(), 0.0
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    o = np.array([ux, uy])
    return o, float(np.hypot(*(c - o)))


def log_spiral(center=(0.0, 0.0), r0: float = 60.0, r1: float = 4.0, turns: float = 2.0,
               start_deg: float = 0.0, cw: bool = True, n: int | None = None) -> np.ndarray:
    """Logarithmic spiral from radius r0 to r1 over ``turns`` revolutions."""
    if not (r0 > 0 and r1 > 0):
        raise ValueError(f"log_spiral: radii must be > 0, got {r0!r}, {r1!r}")
    if not turns > 0:
        raise ValueError("log_spiral: turns must be > 0")
    n = n or max(64, int(turns * 360))
    th = np.linspace(0, 2 * math.pi * turns, n)
    b = math.log(r1 / r0) / (2 * math.pi * turns)
    r = r0 * np.exp(b * th)
    a = math.radians(start_deg) + (th if cw else -th)
    return np.column_stack([center[0] + r * np.cos(a), center[1] + r * np.sin(a)])


def _arm(p0, heading, length, turns, cw, law, power, k0, tighten, ds=0.25):
    if law == "log":
        return volute(p0, heading, length, turns, cw=cw, tighten=tighten, k0=k0, ds=ds)
    if law == "power":
        return curl(p0, heading, length, turns, power, k0, cw=cw, ds=ds)
    raise ValueError(f"law must be 'log' or 'power', not {law!r}")


def s_curve(length: float = 200.0, turns=(1.1, 1.1), kind: str = "S", power: float = 2.2,
            k_mid: float = 0.0, split: float = 0.5, ds: float = 0.25, law: str = "power",
            tighten: float = 2.2) -> np.ndarray:
    """Double volute centreline in local coords (middle at origin heading +x).

    kind 'S' curls the ends in opposite rotational senses (point-symmetric),
    'C' curls both ends toward the same side (mirror-symmetric).
    ``split`` = fraction of length in the forward arm. Returns eye1 -> eye2."""
    if kind not in ("S", "C"):
        raise ValueError(f"kind must be 'S' or 'C', not {kind!r}")
    if not length > 0:
        raise ValueError("s_curve: length must be > 0")
    L1 = length * split
    L0 = length - L1
    fwd = _arm((0, 0), 0.0, L1, turns[1], True, law, power, k_mid, tighten, ds)
    back = _arm((0, 0), 180.0, L0, turns[0], kind == "S", law, power, k_mid, tighten, ds)
    return np.vstack([back[::-1], fwd[1:]])


def fit(pts, a, b, flip: bool = False) -> np.ndarray:
    """Similarity-transform points so pts[0] -> a and pts[-1] -> b (optionally
    mirrored across the chord first)."""
    P = np.asarray(pts, float)
    p0, p1 = P[0], P[-1]
    if np.hypot(*(p1 - p0)) < 1e-9:
        raise ValueError("fit: the curve's end points coincide")
    if np.hypot(*(np.asarray(b, float) - np.asarray(a, float))) < 1e-9:
        raise ValueError("fit: target points a and b coincide")
    if flip:
        d = (p1 - p0) / np.hypot(*(p1 - p0))
        rel = P - p0
        along = rel @ d
        perp = rel - np.outer(along, d)
        P = p0 + np.outer(along, d) - perp
    v0 = p1 - p0
    v1 = np.asarray(b, float) - np.asarray(a, float)
    sc = np.hypot(*v1) / max(np.hypot(*v0), 1e-9)
    ang = math.atan2(v1[1], v1[0]) - math.atan2(v0[1], v0[0])
    c, s = math.cos(ang) * sc, math.sin(ang) * sc
    rel = P - p0
    return np.column_stack([a[0] + c * rel[:, 0] - s * rel[:, 1], a[1] + s * rel[:, 0] + c * rel[:, 1]])


def _end_state(P, back=False):
    """Heading (rad) and signed curvature at the end (or start) of a polyline."""
    Q = P[::-1] if back else P
    k = min(len(Q) - 1, 12)
    a, b, c = Q[-1 - 2 * (k // 2)], Q[-1 - k // 2], Q[-1]
    t = c - b
    hd = math.atan2(t[1], t[0])
    v1, v2 = b - a, c - b
    ang = math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1 @ v2)
    ds = 0.5 * (np.hypot(*v1) + np.hypot(*v2))
    return hd, ang / max(ds, 1e-9)


def flourish(points, *, end_turns: float = 1.1, end_size: float | None = None,
             end_cw: bool | None = None, start_turns: float = 0.0,
             start_size: float | None = None, start_cw: bool | None = None,
             power: float = 1.8, tension: float = 0.5, law: str = "log",
             tighten: float = 2.2) -> np.ndarray:
    """Smooth line through ``points`` (Catmull-Rom) that rolls into volutes.

    The end (and optionally start) volute continues the spline's heading and
    curvature (G2 join) and tightens over ``*_turns`` revolutions; ``*_size``
    is the approximate volute diameter; ``*_cw`` forces the curl sense (default:
    keep bending the way the line already bends). Returns centreline points."""
    pts = np.asarray(points, float)
    if len(pts) < 2:
        raise ValueError("flourish needs at least 2 points")
    if np.any(np.hypot(*np.diff(pts, axis=0).T) < 1e-9):
        raise ValueError("flourish: consecutive points coincide")
    P = G.spline(pts, tension=tension, tol=0.01)
    P = G.Curve(P).resample(0.25)
    span = float(np.hypot(*(pts[-1] - pts[0])))

    def vol(P, back, turns, size, cw):
        hd, k = _end_state(P, back)
        if back:
            k = -k
        cwv = (k >= 0) if cw is None else cw
        size = size if size is not None else 0.22 * span
        L = 0.62 * math.pi * size * max(turns, 0.3)
        if law == "log":
            L *= 1.25
        k0 = min(abs(k), 0.8 * 2 * math.pi * turns / L)
        return _arm(P[-1] if not back else P[0], math.degrees(hd), L, turns, cwv, law, power, k0,
                    tighten)

    parts = [P]
    if end_turns > 0:
        parts.append(vol(P, False, end_turns, end_size, end_cw)[1:])
    if start_turns > 0:
        v = vol(P, True, start_turns, start_size, start_cw)
        parts.insert(0, v[::-1][:-1])
    return np.vstack(parts)


def branch(parent, t: float, *, side: int = 1, length: float = 60.0, turns: float = 1.0,
           tighten: float = 2.2, law: str = "log", power: float = 1.8,
           reverse: bool = False, angle: float = 0.0) -> np.ndarray:
    """A scroll that springs TANGENTIALLY from a parent centreline at arc
    fraction ``t`` (G1 at the junction, starting with the parent's curvature)
    and curls to ``side`` (+1 = clockwise on screen, -1 = counter-clockwise).
    ``reverse`` sends it back along the parent's direction; ``angle`` (deg)
    opens the departure away from the parent toward ``side`` (0 = tangent).
    Fillet the crotch of the stroked result with
    :func:`inkkit.geom.fillet_junction`. Returns (N,2) points starting on the
    parent."""
    cv = G.curve(parent)
    p = cv.at(t)
    hd = float(cv.angle(t)) + (180.0 if reverse else 0.0) + (angle if side > 0 else -angle)
    h = max(0.5, cv.length * 0.01)
    a1 = math.radians(float(cv.angle(max(0.0, t - h / cv.length))))
    a2 = math.radians(float(cv.angle(min(1.0, t + h / cv.length))))
    dk = math.atan2(math.sin(a2 - a1), math.cos(a2 - a1)) / (2 * h)
    if reverse:
        dk = -dk
    cw = side > 0
    k0 = dk if (dk > 0) == cw else 0.0
    return _arm(p, hd, length, turns, cw, law, power, abs(k0), tighten)


# =============================================================================
# stroke rendering helpers
# =============================================================================
def _clearance_ok(P, W, gap, skip_turn=1.5):
    """True when successive turns of a curling centreline keep ``gap`` px of
    paper between their stroke edges."""
    seg = np.hypot(*np.diff(P, axis=0).T)
    s = np.r_[0.0, np.cumsum(seg)]
    tree = cKDTree(P)
    rmax = float(W.max()) + gap
    pairs = tree.query_pairs(rmax, output_type="ndarray")
    if not len(pairs):
        return True
    i, j = pairs[:, 0], pairs[:, 1]
    ds = np.abs(s[i] - s[j])
    d = np.hypot(*(P[i] - P[j]).T)
    far = ds > skip_turn * np.pi * np.maximum(d, 1e-6)
    need = 0.5 * (W[i] + W[j]) + gap
    return not np.any(far & (d < need))


def _widths(P, width, profile, min_width, **kw):
    s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    t = s / max(s[-1], 1e-9)
    f = profile_fn(profile, taper=kw.get("taper", 0.3), power=kw.get("power", 1.0),
                   end_ratio=kw.get("end_ratio", 0.12), swell=kw.get("swell", 1.0))
    W = float(width) * np.broadcast_to(np.asarray(f(t), float), t.shape)
    return np.maximum(W, min_width)


def _end_ball(P, W, want_r, gap, min_r):
    """Radius for a ball terminal at the end of P that keeps ``gap`` px from
    the previous turn (0 when there is no room)."""
    seg = np.hypot(*np.diff(P, axis=0).T)
    s = np.r_[0.0, np.cumsum(seg)]
    e = P[-1]
    d = np.hypot(*(P - e).T)
    far = (s[-1] - s) > 1.5 * np.pi * np.maximum(d, 1e-6)
    if not far.any():
        return want_r
    room = np.min(d[far] - W[far] / 2) - gap
    r = min(want_r, room)
    return r if r >= min_r else 0.0


def _render(P, width, profile, *, style="taper", lw=None, min_width=None, terminal=None,
            terminal_r=None, gap=None, **kw):
    """Stroke a scroll centreline with clearance-aware terminals."""
    mw = T.MIN_LINE if min_width is None else min_width
    gp = T.MIN_GAP if gap is None else gap
    P = np.asarray(P, float)
    body = styled(P, width, profile, style=style, lw=lw, min_width=mw, **kw)
    if not terminal:
        return body
    if style == "monoline":
        W = np.full(len(P), lw if lw is not None else T.FINE)
        want = (terminal_r if terminal_r is not None else T.TERMINAL_D / 2)
    else:
        W = _widths(P, width, profile, mw, **kw)
        want = terminal_r if terminal_r is not None else 0.55 * float(width)
    extra = []
    ends = []
    if terminal in ("ball", "ball-end", "ball-both", "eye"):
        ends.append((P, W))
    if terminal in ("ball-start", "ball-both"):
        ends.append((P[::-1], W[::-1]))
    for Q, WQ in ends:
        if terminal == "eye":
            o, rho = volute_eye(Q)
            want_e = rho + 0.3 * WQ[-1]
            dd = np.hypot(*(Q - o).T)
            seg = np.hypot(*np.diff(Q, axis=0).T)
            s = np.r_[0.0, np.cumsum(seg)]
            prev = (s[-1] - s) > 1.2 * 2 * np.pi * max(rho, 1e-6)
            r_e = want_e
            if prev.any():
                r_e = min(want_e, float(np.min(dd[prev] - WQ[prev] / 2)) - gp)
            if r_e >= max(mw, rho * 0.6):
                extra.append(G.circle_d(o[0], o[1], r_e))
            continue
        r = _end_ball(Q, WQ, want, gp, mw * 0.75)
        if r > 0:
            dvec = Q[-1] - Q[-2]
            dvec = dvec / max(np.hypot(*dvec), 1e-9)
            c = Q[-1] - dvec * min(r * 0.35, 0.5 * WQ[-1])
            extra.append(G.circle_d(c[0], c[1], r))
    return G.union(body, *extra) if extra else body


def _fit_turns(build, turns, widths_of, gap, min_turns=0.35):
    """Rebuild a curl with fewer turns until successive turns keep ``gap``."""
    tu = turns
    while True:
        P = build(tu)
        if tu <= min_turns or _clearance_ok(P, widths_of(P), gap):
            return P, tu
        tu = max(min_turns, tu - 0.1)


# =============================================================================
# leaves
# =============================================================================
def acanthus_leaf(base=(0.0, 0.0), heading: float = -60.0, length: float = 30.0,
                  width: float = 9.0, curl_turns: float = 0.26, cw: bool = True,
                  lobes: int = 3, depth: float = 0.5, vein: bool = True,
                  inner_ratio: float = 0.45, *, style: str = "solid", lw: float | None = None,
                  min_size: float | None = None) -> str:
    """Curling acanthus leaf -> FILL d.

    The blade is an outline around a curling midrib: the outer edge (away from
    the curl) is serrated into ``lobes`` forward-pointing lobes of relative
    ``depth``; the inner edge is smooth. style 'solid' (a tapered vein is
    knocked out when the leaf is big enough to hold a printable reversed line)
    or 'outline' (the silhouette drawn at ``lw`` with the midrib). Leaves are
    never drawn smaller than ``min_size`` px wide (default 3× the print
    minimum) so they cannot print as specks."""
    if style not in ("solid", "outline"):
        raise ValueError(f"acanthus_leaf style must be 'solid' or 'outline', not {style!r}")
    if not (length > 0 and width > 0):
        raise ValueError("acanthus_leaf: length and width must be > 0")
    ms = 3 * T.MIN_LINE if min_size is None else min_size
    if width < ms:
        length *= ms / width
        width = ms
    rib = curl(base, heading, length, curl_turns, 1.8, 0.0, cw=cw, ds=0.2)
    cv = G.Curve(rib)
    n = max(80, int(cv.length * 3))
    t = np.linspace(0, 1, n)
    P = cv.at(t)
    Nn = cv.normal(t)
    env = np.sin(np.pi * np.clip(t, 0, 1) ** 0.72) ** 0.85  # swelling, pointed both ends
    if lobes > 0:
        t0 = 0.10
        u = np.clip((t - t0) / (1 - t0), 0, 1) * lobes
        fr = u - np.floor(u)
        bump = np.sin(np.pi * fr ** 2.0) ** 0.7
        serr = (1 - depth) + depth * bump
        serr = np.where(t < t0, 1 - depth, serr)
    else:
        serr = np.ones_like(t)
    w_out = 0.5 * width * env * serr
    w_in = 0.5 * width * inner_ratio * env
    side = 1.0 if cw else -1.0
    outer = P + Nn * (side * w_out)[:, None]
    inner = P - Nn * (side * w_in)[:, None]
    poly = np.vstack([outer, inner[::-1]])
    d = G.resolve(G.poly_d(poly, True))
    if style == "outline":
        w = lw if lw is not None else T.MIN_LINE
        rib_line = cv.sub(0.05, 0.8).pts
        return G.union(G.outline(d, w), G.outline(rib_line, w))
    vw = max(T.MIN_REVERSED, width * 0.085)
    if vein and width >= 5.5 * vw:
        v = cv.sub(0.06, 0.78).pts
        cut = styled(v, vw, "taper-end", taper=0.6, min_width=T.MIN_REVERSED * 0.8)
        d = G.difference(d, cut)
    return d


# =============================================================================
# scrolls
# =============================================================================
def _leaves_along(center_pts, cw, count, size, start=0.18, end=0.62, side=None, width_ratio=0.34):
    cv = G.Curve(center_pts)
    out = []
    for k in range(count):
        t = start + (end - start) * (k / max(1, count - 1) if count > 1 else 0.5)
        p = cv.at(t)
        hd = float(cv.angle(t))
        sz = size * (1 - 0.45 * (t - start) / max(1e-6, end - start))
        outer = (side != "inner")
        lh = hd - 38.0 if (cw == outer) else hd + 38.0
        out.append(acanthus_leaf(p, lh, sz, sz * width_ratio, 0.22, cw=cw if outer else not cw,
                                 lobes=1 if sz < 22 else 2))
    return out


def scroll(p0=(0.0, 0.0), heading: float = 0.0, length: float = 160.0, turns: float = 1.25,
           *, cw: bool = True, law: str = "log", tighten: float = 2.2, power: float = 2.2,
           k0: float = 0.0, width: float = 5.0, profile="scroll", end_ratio: float = 0.3,
           ball: bool = True, terminal: str | None = None, ball_r: float | None = None,
           leaves: int = 0, leaf_size: float | None = None, leaf_side: str | None = None,
           centerline: bool = False, style: str = "taper", lw: float | None = None,
           min_width: float | None = None, gap: float | None = None, auto_turns: bool = True):
    """A single volute scroll: smooth entry that tightens into a spiral eye.

    law        'log' (Ionic volute, even turn spacing; default) | 'power'
    terminal   'ball' (default when ``ball``) | 'eye' (disc filling the volute
               eye) | None. Terminals are sized to keep ``gap`` px (default the
               print minimum gap) from the previous turn.
    auto_turns reduce ``turns`` until successive turns keep ``gap`` of paper
               between their stroke edges (no fused crescents)
    style      'taper' | 'monoline' | 'outline' | 'inline'
    Returns FILL d (with optional acanthus ``leaves`` along the outer side);
    ``centerline=True`` returns (d, points)."""
    _check_style(style)
    if style == "outline":
        solid, pts = scroll(p0, heading, length, turns, cw=cw, law=law, tighten=tighten, power=power, k0=k0,
                            width=width, profile=profile, end_ratio=end_ratio, ball=ball, terminal=terminal,
                            ball_r=ball_r, leaves=leaves, leaf_size=leaf_size, leaf_side=leaf_side,
                            centerline=True, style="taper", min_width=min_width, gap=gap,
                            auto_turns=auto_turns)
        d = G.outline(G.union(solid), lw if lw is not None else T.MIN_LINE)
        return (d, pts) if centerline else d
    if terminal is None and ball:
        terminal = "ball"
    if terminal not in (None, "ball", "eye"):
        raise ValueError(f"terminal must be 'ball', 'eye' or None, not {terminal!r}")
    mw = T.MIN_LINE if min_width is None else min_width
    gp = T.MIN_GAP if gap is None else gap
    build = lambda tu: _arm(p0, heading, length, tu, cw, law, power, k0, tighten)
    if style == "monoline":
        wfun = lambda P: np.full(len(P), lw if lw is not None else T.FINE)
    else:
        wfun = lambda P: _widths(P, width, profile, mw, end_ratio=end_ratio, taper=0.1)
    pts = _fit_turns(build, turns, wfun, gp)[0] if auto_turns else build(turns)
    br = ball_r if ball_r is not None else (width * 0.55 if style != "monoline" else None)
    body = _render(pts, width, profile, style=style, lw=lw, min_width=mw, terminal=terminal,
                   terminal_r=br, gap=gp, end_ratio=end_ratio, taper=0.1)
    parts = [body]
    if leaves:
        parts += _leaves_along(pts, cw, leaves, leaf_size or length * 0.22, side=leaf_side)
    d = "".join(parts)
    return (d, pts) if centerline else d


def _s_profile(end_ratio):
    return lambda t: end_ratio + (1 - end_ratio) * np.sin(np.pi * np.clip(t, 0, 1)) ** 1.1


def _double(a, b, kind, turns, power, width, end_ratio, ball, split, flip, length, centerline,
            style, lw, min_width, law, tighten, gap, factor):
    _check_style(style)
    a = np.asarray(a, float); b = np.asarray(b, float)
    if np.hypot(*(b - a)) < 1e-9:
        raise ValueError(f"{kind.lower()}_scroll: a and b coincide")
    L = length or factor * math.hypot(*(b - a))
    mw = T.MIN_LINE if min_width is None else min_width
    gp = T.MIN_GAP if gap is None else gap
    prof = _s_profile(end_ratio)
    tu = tuple(turns)
    for _ in range(8):
        pts = fit(s_curve(L, tu, kind, power, split=split, law=law, tighten=tighten), a, b, flip)
        W = np.full(len(pts), lw or T.FINE) if style == "monoline" else _widths(pts, width, prof, mw)
        if _clearance_ok(pts, W, gp) or min(tu) <= 0.35:
            break
        tu = tuple(max(0.35, x - 0.1) for x in tu)
    st = "taper" if style == "outline" else style
    d = _render(pts, width, prof, style=st, lw=lw, min_width=mw,
                terminal="ball-both" if ball else None,
                terminal_r=(width * 0.5 if style != "monoline" else None), gap=gp)
    if style == "outline":
        d = G.outline(d, lw if lw is not None else T.MIN_LINE)
    return (d, pts) if centerline else d


def s_scroll(a, b, *, turns=(1.0, 1.0), power: float = 2.2, width: float = 5.0,
             end_ratio: float = 0.25, ball: bool = True, split: float = 0.5, flip: bool = False,
             length: float | None = None, centerline: bool = False, style: str = "taper",
             lw: float | None = None, min_width: float | None = None, law: str = "power",
             tighten: float = 2.2, gap: float | None = None):
    """S-scroll whose two eyes land on points ``a`` and ``b``. -> FILL d."""
    return _double(a, b, "S", turns, power, width, end_ratio, ball, split, flip, length, centerline,
                   style, lw, min_width, law, tighten, gap, 2.2)


def c_scroll(a, b, *, turns=(1.0, 1.0), power: float = 2.2, width: float = 5.0,
             end_ratio: float = 0.25, ball: bool = True, split: float = 0.5, flip: bool = False,
             length: float | None = None, centerline: bool = False, style: str = "taper",
             lw: float | None = None, min_width: float | None = None, law: str = "power",
             tighten: float = 2.2, gap: float | None = None):
    """C-scroll (both ends curl to the same side) with eyes at ``a`` and ``b``."""
    return _double(a, b, "C", turns, power, width, end_ratio, ball, split, flip, length, centerline,
                   style, lw, min_width, law, tighten, gap, 2.4)


# =============================================================================
# filigree corner
# =============================================================================
def _kappa_path(p0, heading_deg, pieces, ds=0.25):
    """Integrate a G2 centreline from pieces [(length, kappa_fn(u in 0..1)), ...]."""
    ks = []
    for L, fn in pieces:
        n = max(2, int(round(L / ds)))
        u = (np.arange(n) + 0.5) / n
        ks.append(np.asarray(fn(u), float) * np.ones(n))
    kappa = np.concatenate(ks)
    L_tot = sum(L for L, _ in pieces)
    ds_eff = L_tot / len(kappa)
    kappa = np.r_[kappa[0], kappa]
    pts, th = _integrate(p0, math.radians(heading_deg), kappa, ds_eff)
    return pts


def _corner_arm(S: float, r_frac: float = 0.16, run_y: float = 0.055, end_turns: float = 1.35):
    """Half of the main arm, local coords (corner at origin, edges along +x/+y,
    ornament mirror-symmetric about y = x). Starts on the diagonal heading
    -45°, rounds the corner on an arc of radius r that eases (G2) into a run
    PARALLEL to the top edge at y = run_y·S, then rolls inward (clockwise)
    into an Ionic volute whose outer edge reaches x ≈ S."""
    r = r_frac * S
    k = 1.0 / r
    s_t = 0.9 * r
    s_a = (math.pi / 4 - k * s_t / 2) / k
    head = [(s_a, lambda u: np.full_like(u, k)), (s_t, lambda u: k * (1 - _smoothstep(u)))]
    probe = _kappa_path((0.0, 0.0), -45.0, head)
    dy = probe[-1, 1] - probe[0, 1]
    dx = probe[-1, 0] - probe[0, 0]
    y0 = run_y * S - dy
    x0 = y0
    vol_len = 0.62 * S
    vol = volute((0.0, 0.0), 0.0, vol_len, end_turns, cw=True, tighten=2.0, entry=0.35)
    reach = float(vol[:, 0].max())
    run_len = max(0.05 * S, S - (x0 + dx) - reach)
    pieces = head + [(run_len, lambda u: np.zeros_like(u))]
    arm = _kappa_path((x0, y0), -45.0, pieces)
    tail = vol + arm[-1]
    n_head = int(np.searchsorted(np.r_[0.0, np.cumsum(np.hypot(*np.diff(arm, axis=0).T))], s_a + s_t))
    return np.vstack([arm, tail[1:]]), n_head, len(arm)


def _mirror_diag(P):
    P = np.asarray(P, float)
    return P[:, ::-1].copy()


def _corner_bud(S, w, style, lw, mw, start, others=None, gap=2.0):
    """Fleur-de-lis bud on the diagonal, pointing into the frame, on a short
    stem from the arm's apex; slid out along the diagonal until it keeps
    ``gap`` px from the other parts."""
    from .radiance import fleuron
    u = np.array([1.0, 1.0]) / math.sqrt(2)
    size = 0.27 * S
    occ = G.to_shape(others) if others else None
    off = 0.19 * S
    for _ in range(30):
        c = u * (off + 0.52 * size)
        d = fleuron(c[0], c[1], size, style="lily", rot=135.0, width=max(size / 16, mw),
                    line_style=style, lw=lw, min_width=mw)
        if occ is None or G.to_shape(d).distance(occ) >= gap:
            break
        off += 0.015 * S
    foot = c - u * 0.30 * size
    p0 = np.asarray(start, float)
    if float((foot - p0) @ u) > 0.5 * w:
        stem = styled(np.array([p0, foot]), max(0.62 * w, mw), "uniform", style=style, lw=lw,
                      min_width=mw)
        return [d, stem]
    return [d]


def filigree_corner(size: float = 150.0, complexity: int = 2, *, x: float = 0.0,
                    y: float = 0.0, corner: str = "tl", width: float | None = None,
                    merge: bool = True, style: str = "taper", lw: float | None = None,
                    min_width: float | None = None, gap: float | None = None,
                    bud: bool = True) -> str:
    """Filigree corner: one continuous G2 scroll hugging the corner and rolling
    into inward Ionic volutes on both edges, mirrored about the diagonal.
    -> FILL d.

    size        arm length in px (how far along each edge it reaches)
    complexity  1: corner arm + fleur-de-lis bud on the diagonal
                2: + inner C-scrolls springing tangentially from the arm where
                   the corner arc meets the runs (filleted crotches)
                3: + reverse scrolls springing back from mid-run and graduated
                   pearls threaded on the runs
    x, y        the frame corner point; ``corner`` in {'tl','tr','bl','br'}
    width       max stroke width (default size/30)
    style       'taper' | 'monoline' (uniform ``lw``, default 2.1) | 'outline' | 'inline'
    min_width   thinnest printed line (default the offset minimum; use
                ``tokens.PRINT_PROFILES['foil']['min_line']`` for foil)"""
    _check_style(style)
    if complexity not in (1, 2, 3):
        raise ValueError(f"complexity must be 1, 2 or 3, not {complexity!r}")
    if corner not in ("tl", "tr", "bl", "br"):
        raise ValueError(f"corner must be one of tl/tr/bl/br, not {corner!r}")
    if not size > 0:
        raise ValueError("filigree_corner: size must be > 0")
    if style == "outline":
        # outline the merged tapered silhouette, so junctions read as one form
        solid = filigree_corner(size, complexity, x=0.0, y=0.0, corner="tl", width=width, merge=True,
                                style="taper", min_width=min_width, gap=gap, bud=bud)
        return place_corner(G.outline(solid, lw if lw is not None else T.MIN_LINE), x, y, corner)
    S = float(size)
    w = width if width is not None else S / 30.0
    mw = T.MIN_LINE if min_width is None else min_width
    gp = T.MIN_GAP if gap is None else gap
    arm, n_head, n_run = _corner_arm(S)
    full = np.vstack([_mirror_diag(arm)[::-1], arm[1:]])
    prof = lambda t: 0.36 + 0.64 * np.sin(np.pi * np.clip(t, 0, 1)) ** 1.2
    parts = [_render(full, w, prof, style=style, lw=lw, min_width=mw, terminal="ball-both",
                     terminal_r=0.62 * w, gap=gp)]
    half = []
    joints = []
    cva = G.Curve(arm)
    t_a = G.Curve(arm[:n_head]).length / cva.length      # arc -> run
    t_b = G.Curve(arm[:n_run]).length / cva.length       # run -> end volute
    if complexity >= 2:
        br = branch(arm, t_a * 0.96, side=1, length=0.46 * S, turns=1.1, tighten=2.3)
        half.append(_render(br, 0.8 * w, "scroll", style=style, lw=lw, min_width=mw,
                            terminal="ball", terminal_r=0.52 * w, gap=gp, end_ratio=0.35, taper=0.06))
        joints.append(br[0])
    if complexity >= 3:
        tr = t_a + (t_b - t_a) * 0.62
        rv = branch(arm, tr, side=-1, reverse=True, length=0.34 * S, turns=0.85, tighten=2.3,
                    angle=28.0)
        half.append(_render(rv, 0.62 * w, "scroll", style=style, lw=lw, min_width=mw,
                            terminal="ball", terminal_r=0.45 * w, gap=gp, end_ratio=0.4, taper=0.08))
        joints.append(rv[0])
        for k, f in enumerate((0.74, 0.84, 0.93)):
            pnt = cva.at(t_a + (t_b - t_a) * f)
            half.append(G.circle_d(pnt[0], pnt[1], max(w * (0.9 - 0.12 * k), mw)))
    parts += half
    for d in half:
        parts.append(G.mirror_line(d, (0, 0), 45))
    if bud:
        parts += _corner_bud(S, w, style, lw, mw, arm[0], "".join(parts), 1.5 * gp)
    if merge:
        d = G.union(*parts)
        if style in ("taper", "monoline"):   # hollow styles must not be closed up
            fw = w if style == "taper" else (lw if lw is not None else T.FINE)
            for j in joints:
                for p in (j, j[::-1]):
                    d = G.fillet_junction(d, p, r=max(0.45 * fw, mw), reach=2.0 * fw)
    else:
        d = "".join(parts)
    return place_corner(d, x, y, corner)


def place_corner(d: str, x: float, y: float, corner: str = "tl") -> str:
    """Move a corner ornament drawn for the top-left (origin corner) into place
    (mirrored copies keep clockwise winding)."""
    if corner == "tl":
        m = (1, 0, 0, 1, x, y)
    elif corner == "tr":
        m = (-1, 0, 0, 1, x, 0 + y)
    elif corner == "bl":
        m = (1, 0, 0, -1, x, y)
    elif corner == "br":
        m = (-1, 0, 0, -1, x, y)
    else:
        raise ValueError(f"corner must be one of tl/tr/bl/br, not {corner!r}")
    return G.transform(d, m)


def filigree_corners(box, size: float = 150.0, complexity: int = 2, **kw) -> str:
    """All four corners of box (x, y, w, h). -> FILL d."""
    x, y, w, h = box
    base = filigree_corner(size, complexity, **kw)
    return "".join([place_corner(base, x, y, "tl"), place_corner(base, x + w, y, "tr"),
                    place_corner(base, x, y + h, "bl"), place_corner(base, x + w, y + h, "br")])


# =============================================================================
# rinceau band
# =============================================================================
def filigree_band(length: float = 400.0, height: float = 40.0, *, x: float = 0.0, y: float = 0.0,
                  angle: float = 0.0, repeats: int | None = None, width: float | None = None,
                  leaves: bool = True, center: str | None = "bud", style: str = "taper",
                  lw: float | None = None, min_width: float | None = None,
                  gap: float | None = None) -> str:
    """Symmetric running-scroll (rinceau) band centred at (x, y), ``length`` long,
    ``height`` tall. A gently waving stem throws alternate volutes that spring
    tangentially from its crests (filleted crotches) and curl into the bays
    above and below it; the right half is mirrored to the left so the band is
    bilaterally symmetric. center: 'bud' | 'pearl' | None. -> FILL d."""
    _check_style(style)
    if center not in ("bud", "pearl", None):
        raise ValueError(f"center must be 'bud', 'pearl' or None, not {center!r}")
    if repeats is not None and repeats < 1:
        raise ValueError("filigree_band: repeats must be >= 1")
    if not (length > 0 and height > 0):
        raise ValueError("filigree_band: length and height must be > 0")
    if style == "outline":
        solid = filigree_band(length, height, repeats=repeats, width=width, leaves=leaves, center=center,
                              style="taper", min_width=min_width, gap=gap)
        d = G.outline(solid, lw if lw is not None else T.MIN_LINE)
        if angle:
            d = G.rotate(d, angle)
        return G.translate(d, x, y)
    mw = T.MIN_LINE if min_width is None else min_width
    gp = T.MIN_GAP if gap is None else gap
    w = width if width is not None else max(height / 13.0, mw * 1.6)
    half = length / 2
    n = repeats if repeats is not None else max(1, int(round(half / (height * 1.3))))
    lam = half / n
    A = height * 0.12
    xs = np.linspace(0, half, max(60, int(half * 2)))
    stem = np.column_stack([xs, -A * np.sin(2 * math.pi * xs / lam)])
    prof = lambda t: 1.0 - 0.35 * np.clip(t, 0, 1) ** 2
    parts = [styled(stem, w * 0.85, prof, style=style, lw=lw, min_width=mw, end_cap="round")]
    joints = []
    cv = G.Curve(stem)
    vol_len = 0.62 * lam
    for k in range(n):
        for up in (True, False):
            xc = (k + (0.25 if up else 0.75)) * lam
            xk = xc - 0.16 * lam
            if xk <= 0.02 * lam or xk > half - 0.05 * lam:
                continue
            t = xk / half
            c = branch(stem, t, side=-1 if up else 1, length=vol_len, turns=1.15, tighten=2.3)
            parts.append(_render(c, w * 0.95, "scroll", style=style, lw=lw, min_width=mw,
                                 terminal="ball", terminal_r=w * 0.62, gap=gp, end_ratio=0.35,
                                 taper=0.05))
            joints.append(c[0])
            if leaves:
                p = cv.at(t)
                hd = float(cv.angle(t))
                lwid = max(height * 0.12, 3 * mw, 1.6 * w)
                parts.append(acanthus_leaf(p, hd + (180 + 30 if up else 180 - 30),
                                           max(height * 0.3, 2.6 * lwid), lwid, 0.2,
                                           cw=(not up), lobes=1, depth=0.4,
                                           style="outline" if style in ("monoline", "outline") else "solid",
                                           lw=lw))
    right = G.union(*parts)
    if style in ("taper", "monoline"):
        fw = w if style == "taper" else (lw if lw is not None else T.FINE)
        for j in joints:
            right = G.fillet_junction(right, j, r=max(0.5 * fw, mw), reach=2.0 * fw)
    left = G.mirror_x(right, 0.0)
    center_parts = []
    if center == "bud":
        u_ = np.array([0.0, -1.0])
        base = np.array([0.0, height * 0.10])
        center_parts.append(styled(np.array([base, base + u_ * height * 0.55]), w * 2.0,
                                   lambda t: np.sin(np.pi * np.clip(t, 0, 1) ** 0.75) ** 0.9,
                                   style=style, lw=lw, min_width=mw))
        center_parts.append(G.circle_d(0, height * 0.30, max(w * 0.75, mw)))
    elif center == "pearl":
        center_parts.append(G.circle_d(0, 0, w * 1.6))
    d = G.union(right, left, *center_parts)
    if angle:
        d = G.rotate(d, angle)
    return G.translate(d, x, y)
