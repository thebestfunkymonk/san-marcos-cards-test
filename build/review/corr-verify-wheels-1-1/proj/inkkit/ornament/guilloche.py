"""Guilloché: spirograph families, rosettes, bands along paths, wave lattices.

All generators return STROKE d (centrelines; draw them with ``fill="none"``
and ``stroke-width`` ≥ 1.05 px at card scale — thinner lines fill in on
press), or FILL outlines when ``width=`` / ``line_width=`` is given (slower:
every line is buffered and unioned).

Curves are sampled finely (≈0.4 px) and closed exactly (integer lobe/wave
counts), then Douglas–Peucker simplified at 0.02 px so files stay small without
visible facets.

Density: at card scale keep ~1.0–1.2 px lines with ≥ 1.5 px between them.
``rosette``, ``rosette_ring`` and ``guilloche_band`` take ``auto_lines=True``
(with ``line_width`` and ``min_gap``) to drop lines until neighbouring curves
never run closer than that — no fused 'ribbon folds' or moiré. Use
:func:`min_line_gap` to measure any STROKE art and :func:`spirograph_fit` to
choose spirograph parameters by radius.
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString

from .. import geom as G
from .. import tokens as T
from ..hatch import _clip, _region

__all__ = ["spirograph", "spiro_rosette", "spirograph_fit", "rosette", "rosette_ring",
           "guilloche_band", "guilloche_frame", "guilloche_strip", "wave_lattice", "wave",
           "min_line_gap"]

_TOL = 0.02


def wave(x, shape: float = 1.0):
    """Periodic wave in [-1,1]. shape=1 sine; <1 squarer (flat crests); >1 peakier."""
    s = np.sin(x)
    if shape == 1.0:
        return s
    return np.sign(s) * np.abs(s) ** shape


def _simp(P, closed):
    if len(P) < 4:
        return G.poly_d(P, closed)
    Q = np.vstack([P, P[:1]]) if closed else P
    c = np.asarray(LineString(Q).simplify(_TOL, preserve_topology=False).coords)
    if closed:
        c = c[:-1]
    return G.poly_d(c, closed)


def _emit(curves, closed, width):
    if width is None:
        return "".join(_simp(P, closed) for P in curves)
    return G.outline([(P, closed) for P in curves], width)


# =============================================================================
# density control
# =============================================================================
def _curve_gap(curves, closed, parallel_deg=20.0, reach=6.0):
    """Minimum distance between points of DIFFERENT curves where the curves run
    nearly parallel (tangents within ``parallel_deg``) — i.e. where two lines
    would fuse into one. Transversal crossings are ignored."""
    pts, tans, ids = [], [], []
    for k, P in enumerate(curves):
        P = np.asarray(P, float)
        cv = G.Curve(P, closed)
        if cv.length <= 0:
            continue
        Q = cv.resample(0.5)
        Tg = cv.tangent(np.linspace(0, 1, len(Q), endpoint=not closed))
        pts.append(Q); tans.append(Tg); ids.append(np.full(len(Q), k))
    if len(pts) < 2:
        return math.inf
    P = np.vstack(pts); Tg = np.vstack(tans); I = np.concatenate(ids)
    tree = cKDTree(P)
    pairs = tree.query_pairs(reach, output_type="ndarray")
    if not len(pairs):
        return math.inf
    i, j = pairs[:, 0], pairs[:, 1]
    other = I[i] != I[j]
    cosang = np.abs(np.sum(Tg[i] * Tg[j], axis=1))
    par = other & (cosang >= math.cos(math.radians(parallel_deg)))
    if not par.any():
        return math.inf
    return float(np.min(np.hypot(*(P[i[par]] - P[j[par]]).T)))


def min_line_gap(x, parallel_deg: float = 20.0, reach: float = 6.0) -> float:
    """Smallest centre-to-centre distance between two different STROKE lines
    of ``x`` where they run nearly parallel (within ``parallel_deg``). Compare
    with line width + print minimum gap to predict lines fusing on press.
    Returns inf when nothing comes closer than ``reach`` px."""
    polys = G.as_polys(x, 0.05)
    closed = all(c for _, c in polys)
    return _curve_gap([p for p, _ in polys], closed, parallel_deg, reach)


def _auto(build, lines, auto_lines, line_width, min_gap, closed):
    """Build with ``lines`` curves; with auto_lines, drop lines until the
    parallel gap is at least line_width + min_gap."""
    curves = build(lines)
    if not auto_lines:
        return curves
    lw = T.MIN_LINE if line_width is None else line_width
    mg = T.MIN_GAP if min_gap is None else min_gap
    need = lw + mg
    n = lines
    while n > 2 and _curve_gap(curves, closed, reach=need * 1.5) < need:
        n -= 1
        curves = build(n)
    return curves


# =============================================================================
# spirograph family
# =============================================================================
def _ratio(R, r):
    return Fraction(R / r).limit_denominator(1000)


def _period(R, r):
    return 2 * math.pi * _ratio(R, r).denominator


def spirograph(cx: float, cy: float, R: float, r: float, d: float, *, kind: str = "hypo",
               rot: float = 0.0, width: float | None = None, step: float = 0.4) -> str:
    """Hypotrochoid (kind='hypo') or epitrochoid ('epi') about (cx, cy).
    R fixed-circle radius, r rolling radius, d pen distance. Closes exactly
    for rational R/r; the curve has ``numerator(R/r)`` petals.
    -> STROKE d (closed)."""
    if kind not in ("hypo", "epi"):
        raise ValueError(f"kind must be 'hypo' or 'epi', not {kind!r}")
    if not (R > 0 and r > 0):
        raise ValueError(f"spirograph: R and r must be > 0, got {R!r}, {r!r}")
    if d < 0:
        raise ValueError("spirograph: d must be >= 0")
    T_ = _period(R, r)
    ext = (R + r + d) if kind == "epi" else (abs(R - r) + d)
    n = int(max(2000, T_ * ext / step))
    t = np.linspace(0, T_, n, endpoint=False)
    if kind == "hypo":
        k = (R - r) / r
        x = (R - r) * np.cos(t) + d * np.cos(k * t)
        y = (R - r) * np.sin(t) - d * np.sin(k * t)
    else:
        k = (R + r) / r
        x = (R + r) * np.cos(t) - d * np.cos(k * t)
        y = (R + r) * np.sin(t) - d * np.sin(k * t)
    a = math.radians(rot)
    X = cx + x * math.cos(a) - y * math.sin(a)
    Y = cy + x * math.sin(a) + y * math.cos(a)
    return _emit([np.column_stack([X, Y])], True, width)


def spirograph_fit(r_min: float, r_max: float, petals: int = 12, loops: int = 5,
                   kind: str = "hypo") -> tuple[float, float, float]:
    """(R, r, d) of a spirograph whose trace fills the annulus r_min..r_max
    exactly, with ``petals`` lobes, the pen circling ``loops`` times
    (petals/loops in lowest terms; hypo needs petals > loops). Use as
    ``spirograph(cx, cy, *spirograph_fit(60, 90, 12, 5))``."""
    if not (0 <= r_min < r_max):
        raise ValueError("spirograph_fit: need 0 <= r_min < r_max")
    if kind not in ("hypo", "epi"):
        raise ValueError(f"kind must be 'hypo' or 'epi', not {kind!r}")
    fr = Fraction(petals, loops)
    p, q = fr.numerator, fr.denominator
    A = (r_max + r_min) / 2
    d = (r_max - r_min) / 2
    if kind == "hypo":
        if p <= q:
            raise ValueError("spirograph_fit: hypo needs petals > loops")
        R = A * p / (p - q)
    else:
        R = A * p / (p + q)
    r = R * q / p
    return R, r, d


def spiro_rosette(cx: float, cy: float, R: float, r: float, d: float, copies: int = 6, *,
                  kind: str = "hypo", width: float | None = None, step: float = 0.4) -> str:
    """``copies`` spirographs rotated evenly within one petal period — the
    dense interlaced banknote rosette. -> STROKE d."""
    if copies < 1:
        raise ValueError("spiro_rosette: copies must be >= 1")
    if not (R > 0 and r > 0):
        raise ValueError("spiro_rosette: R and r must be > 0")
    petals = max(1, _ratio(R, r).numerator)   # rotational symmetry order (hypo and epi)
    return "".join(spirograph(cx, cy, R, r, d, kind=kind, rot=360.0 / petals * k / copies,
                              width=width, step=step) for k in range(copies))


# =============================================================================
# polar sine rosettes
# =============================================================================
def rosette(cx: float, cy: float, r_in: float, r_out: float, *, lobes: int = 18,
            lines: int = 24, phase_span: float = 1.0, shape: float = 1.0,
            mod_lobes: int = 0, mod_amp: float = 0.0, twist: float = 0.0,
            width: float | None = None, step: float = 0.4, auto_lines: bool = False,
            line_width: float | None = None, min_gap: float | None = None) -> str:
    """Guilloché rosette ring: ``lines`` closed curves
        r(θ) = r_mid + A·(1 + mod_amp·sin(mod_lobes θ))·wave(lobes θ + φ_i)
    with phases φ_i spread over ``phase_span`` of a lobe period (1.0 = fully
    woven band, 0.25 = a tight braid). ``twist`` adds a radius-dependent phase
    so crossings lean like a turned rosette. ``auto_lines`` drops lines until
    neighbouring curves keep ``line_width`` + ``min_gap`` apart where they
    run parallel (default 1.05 + 1.2 px). -> STROKE d."""
    if lines < 1 or lobes < 1:
        raise ValueError("rosette: lines and lobes must be >= 1")
    if not r_out > r_in:
        raise ValueError("rosette: r_out must exceed r_in")
    r_mid, A = (r_in + r_out) / 2, (r_out - r_in) / 2
    if mod_amp:
        A = A / (1 + abs(mod_amp))
    n = int(max(720, 2 * math.pi * r_out / step))
    th = np.linspace(0, 2 * math.pi, n, endpoint=False)

    def build(nl):
        curves = []
        for i in range(nl):
            phi = 2 * math.pi * phase_span * i / nl
            amp = A * (1 + mod_amp * np.sin(mod_lobes * th)) if mod_lobes else A
            w = wave(lobes * th + phi, shape)
            rr = r_mid + amp * w
            tt = th + twist * (rr - r_mid) / max(A, 1e-9) * (math.pi / lobes)
            curves.append(np.column_stack([cx + rr * np.cos(tt), cy + rr * np.sin(tt)]))
        return curves
    return _emit(_auto(build, lines, auto_lines, line_width, min_gap, True), True, width)


def rosette_ring(cx: float, cy: float, r_in: float, r_out: float, *, bands: int = 3,
                 lobes=(24, 36, 48), lines: int = 12, gap: float = 1.5, **kw) -> str:
    """Concentric stack of rosette rings (a full medallion) from r_in to r_out.
    ``lobes`` per band (cycled). Other keywords (incl. ``auto_lines``) go to
    :func:`rosette`. -> STROKE d."""
    if bands < 1:
        raise ValueError("rosette_ring: bands must be >= 1")
    h = (r_out - r_in - gap * (bands - 1)) / bands
    if not h > 0:
        raise ValueError("rosette_ring: rings do not fit (reduce bands or gap)")
    out = []
    for b in range(bands):
        a = r_in + b * (h + gap)
        lb = lobes[b % len(lobes)] if isinstance(lobes, (list, tuple)) else lobes
        out.append(rosette(cx, cy, a, a + h, lobes=lb, lines=lines, **kw))
    return "".join(out)


# =============================================================================
# bands along paths
# =============================================================================
def guilloche_band(path, width: float = 12.0, *, wavelength: float = 14.0, lines: int = 8,
                   phase_span: float = 1.0, shape: float = 1.0, amps=None,
                   waves: int | None = None, closed: bool | None = None,
                   line_width: float | None = None, step: float = 0.4,
                   corner_radius: float | None = None, auto_lines: bool = False,
                   min_gap: float | None = None) -> str:
    """Guilloché band following ``path`` (its centreline), ``width`` wide.

    Each line k is the path offset by (width/2)·a_k·wave(2π s/λ + φ_k). On closed
    paths the wavelength is adjusted so an integer number of waves fits (or
    pass ``waves``). ``amps``: optional list of relative amplitudes cycled over
    lines (e.g. (1, .6) for a nested two-tier band). Sharp path corners are
    rounded to ``corner_radius`` (default 1.25·width) so the band never folds.
    ``line_width`` outlines the lines (FILL); ``auto_lines`` thins the family
    as in :func:`rosette`. -> STROKE d (or FILL)."""
    if lines < 1:
        raise ValueError("guilloche_band: lines must be >= 1")
    if amps is not None and len(amps) == 0:
        raise ValueError("guilloche_band: amps must not be empty")
    cv0 = G.curve(path, closed)
    cr = 1.25 * width if corner_radius is None else corner_radius
    cv = G.Curve(G.round_corners(G.poly_d(cv0.pts, cv0.closed), cr), cv0.closed) if cr > 0 else cv0
    L = cv.length
    cl = cv.closed
    if cl:
        nw = waves if waves is not None else max(1, round(L / wavelength))
        lam = L / nw
    else:
        lam = wavelength
    n = int(max(200, L / step))
    s = np.linspace(0, L, n, endpoint=not cl)

    def build(nl):
        curves = []
        for k in range(nl):
            phi = 2 * math.pi * phase_span * k / nl
            a = 1.0 if amps is None else amps[k % len(amps)]
            v = 0.5 * width * a * wave(2 * math.pi * s / lam + phi, shape)
            curves.append(cv.map(np.column_stack([s, v])))
        return curves
    curves = _auto(build, lines, auto_lines, line_width, min_gap, cl)
    return _emit(curves, cl, line_width)


def guilloche_frame(x: float, y: float, w: float, h: float, r: float = 20.0, *,
                    width: float = 12.0, **kw) -> str:
    """Guilloché band running round a rounded rectangle (the band's centreline
    is inset width/2 from the given box). The centreline corner radius is
    kept ≥ 2·width so the outer edge of the band cannot balloon at the corners.
    -> STROKE d."""
    i = width / 2
    rc = max(r - i, 2.0 * width)
    path = G.rect_d(x + i, y + i, w - 2 * i, h - 2 * i, rc)
    kw.setdefault("corner_radius", 0)
    return guilloche_band(path, width, closed=True, **kw)


def guilloche_strip(p0, p1, width: float = 12.0, **kw) -> str:
    """Straight guilloché band from p0 to p1. -> STROKE d."""
    return guilloche_band(np.array([p0, p1], float), width, closed=False, **kw)


def wave_lattice(shape, spacing: float = 6.0, amplitude: float = 3.0, wavelength: float = 24.0,
                 *, angle: float = 0.0, cross: bool = True, shape_power: float = 1.0,
                 width: float | None = None, fill_rule: str = "nonzero", step: float = 0.5) -> str:
    """Wavy-line fill (and, with ``cross``, the mirrored family) clipped to a
    shape — the woven lens-mesh of banknote backgrounds. -> STROKE d
    (FILL with ``width``)."""
    if not (spacing > 0 and wavelength > 0):
        raise ValueError("wave_lattice: spacing and wavelength must be > 0")
    region = _region(shape, fill_rule)
    if region.is_empty:
        return ""
    x0, y0, x1, y1 = region.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + spacing + amplitude
    a = math.radians(angle)
    u = np.array([math.cos(a), math.sin(a)])
    v = np.array([-math.sin(a), math.cos(a)])
    xs = np.arange(-R, R + step, step)
    lines = []
    fams = (1.0, -1.0) if cross else (1.0,)
    for sgn in fams:
        k = -int(R / spacing) - 1
        while k * spacing <= R:
            off = k * spacing
            yy = off + sgn * amplitude * wave(2 * math.pi * xs / wavelength, shape_power)
            P = np.array([cx, cy]) + np.outer(xs, u) + np.outer(yy, v)
            lines.append(P)
            k += 1
    lines = _clip(lines, region)
    if width is None:
        return "".join(_simp(P, False) for P in lines)
    return G.outline(lines, width)
