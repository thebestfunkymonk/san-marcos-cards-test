"""Garment / field patterns clipped to any shape: diaper lattice, fish scales,
quatrefoil damask, stripes, ermine, chevrons, checks, polka and a generic
half-drop ``tile`` for repeating any motif.

All return FILL d cut exactly to the shape edge (line work is outlined with
flat caps first and then intersected, so lines end crisply on the boundary).
``lw`` is the line width of line-based patterns: these generators are
FILL-only, so ``lw=None`` raises a clear error. Empty regions return ''.
Repeating motifs are built once and translated, so full-card fills stay fast.
"""
from __future__ import annotations

import math

import numpy as np
import shapely

from .. import geom as G
from .. import tokens as T
from ..hatch import _parallel_lines, _region
from ..stroke import stroke

__all__ = ["diaper", "scales", "quatrefoil", "stripes", "ermine", "chevrons", "checks",
           "polka", "tile", "ermine_spot"]


def _lw(name, lw):
    if lw is None:
        raise ValueError(f"{name} is FILL-only (patterns are cut to the shape): pass lw=<px>")
    if not lw > 0:
        raise ValueError(f"{name}: lw must be > 0, got {lw!r}")


def _pos(name, **vals):
    for k, v in vals.items():
        if not (v is not None and v > 0):
            raise ValueError(f"{name}: {k} must be > 0, got {v!r}")


def _grid(region, cw, ch, drop=0.0, margin=1):
    x0, y0, x1, y1 = region.bounds
    cols = int(math.ceil((x1 - x0) / cw)) + 2 * margin
    rows = int(math.ceil((y1 - y0) / ch)) + 2 * margin
    for j in range(-margin, rows):
        for i in range(-margin, cols):
            yield x0 + i * cw, y0 + j * ch + (drop * ch if i % 2 else 0.0), i, j


def _cut(d, region):
    """Intersect FILL art (d or shapely) with the region."""
    if d is None or (isinstance(d, str) and not d):
        return ""
    if isinstance(d, str):
        return G.from_shape(G.to_shape(d).intersection(region))
    return G.from_shape(d.intersection(region))


def _dots_shape(pts, r):
    if not len(pts):
        return None
    P = np.asarray(pts, float)
    return shapely.union_all(shapely.buffer(shapely.points(P[:, 0], P[:, 1]), r, quad_segs=6))


def _tiled(region, motif_shape, cw, ch, drop=0.0, margin=1):
    """Union-free tiling: translate one shapely motif over the grid, keep only
    cells that touch the region, then cut once."""
    x0, y0, x1, y1 = region.bounds
    mb = motif_shape.bounds
    pieces = []
    for x, y, i, j in _grid(region, cw, ch, drop, margin):
        bx = (mb[0] + x, mb[1] + y, mb[2] + x, mb[3] + y)
        if bx[2] < x0 or bx[0] > x1 or bx[3] < y0 or bx[1] > y1:
            continue
        pieces.append(shapely.affinity.translate(motif_shape, x, y))
    if not pieces:
        return shapely.Polygon()
    return shapely.union_all(pieces)


def diaper(shape, cell: float = 16.0, *, angle: float = 45.0, lw: float = 1.05,
           dots: str | None = "center", dot_r: float = 1.5) -> str:
    """Diamond lattice (two line families at ±angle) with optional dots at
    'center' of each lozenge or at 'nodes'. -> FILL d."""
    _lw("diaper", lw)
    _pos("diaper", cell=cell)
    if dots not in ("center", "nodes", None):
        raise ValueError("diaper: dots must be 'center', 'nodes' or None")
    region = _region(shape)
    if region.is_empty:
        return ""
    lines = _parallel_lines(region, angle, cell) + _parallel_lines(region, -angle, cell)
    geom = G.outline(lines, lw, cap="flat", as_shape=True)
    pts = []
    if dots:
        a = math.radians(angle)
        u = np.array([math.cos(a), math.sin(a)]) * cell / math.sin(2 * a)
        v = np.array([math.cos(-a), math.sin(-a)]) * cell / math.sin(2 * a)
        x0, y0, x1, y1 = region.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        R = math.hypot(x1 - x0, y1 - y0) / 2
        n = int(R / min(np.hypot(*u), np.hypot(*v))) + 2
        off = (u + v) / 2 if dots == "center" else np.zeros(2)
        I, J = np.meshgrid(np.arange(-n, n + 1), np.arange(-n, n + 1))
        P = np.array([cx, cy]) + I.ravel()[:, None] * u + J.ravel()[:, None] * v + off
        keep = (P[:, 0] > x0 - 2) & (P[:, 0] < x1 + 2) & (P[:, 1] > y0 - 2) & (P[:, 1] < y1 + 2)
        pts = P[keep]
    ds = _dots_shape(pts, dot_r)
    if ds is not None:
        geom = geom.union(ds)
    return _cut(geom, region)


def scales(shape, r: float = 9.0, *, lw: float = 1.05, inner: int = 1, dots: bool = False) -> str:
    """Fish-scale (imbrication): rows of semicircular arcs, alternate rows
    offset half a scale; ``inner`` concentric inner arcs per scale. -> FILL."""
    _lw("scales", lw)
    _pos("scales", r=r)
    region = _region(shape)
    if region.is_empty:
        return ""
    lines = []
    for k in range(inner + 1):
        rr = r * (1 - 0.34 * k)
        lines.append((G.arc_pts(0, 0, rr, 0, 180, n=max(16, int(rr * 2.2))), False))
    unit = G.outline(lines, lw, cap="flat", as_shape=True)
    if dots:
        unit = unit.union(shapely.Point(0, r * 0.55).buffer(r * 0.12, quad_segs=6))
    rows = []
    x0, y0, x1, y1 = region.bounds
    # two row types (offset by half a scale) tiled on a 2r x 2r grid
    row_a = _tiled(region, unit, 2 * r, 2 * r, 0.0, margin=2)
    row_b = _tiled(region, shapely.affinity.translate(unit, r, r), 2 * r, 2 * r, 0.0, margin=2)
    rows = row_a.union(row_b)
    return _cut(rows, region)


def quatrefoil(shape, cell: float = 24.0, *, lw: float = 1.05, lobe: float = 0.27,
               filled: bool = False, diamonds: bool = True) -> str:
    """Quatrefoil damask: four-lobed rosettes on a half-drop grid with small
    diamonds between them. -> FILL."""
    _lw("quatrefoil", lw)
    _pos("quatrefoil", cell=cell)
    region = _region(shape)
    if region.is_empty:
        return ""
    cx, cy = cell / 2, cell / 2
    a = cell * lobe
    lobes = shapely.union_all([shapely.Point(cx + dx * a, cy + dy * a).buffer(a * 0.98, quad_segs=16)
                               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                              + [shapely.box(cx - a, cy - a, cx + a, cy + a)])
    if filled:
        motif = lobes.difference(shapely.Point(cx, cy).buffer(a * 0.45, quad_segs=12))
    else:
        motif = lobes.difference(lobes.buffer(-lw)).union(shapely.Point(cx, cy).buffer(a * 0.3, quad_segs=12))
    if diamonds:
        s = cell * 0.09
        motif = motif.union(shapely.Polygon([(0, cell / 2 - s), (s, cell / 2), (0, cell / 2 + s), (-s, cell / 2)]))
    return _cut(_tiled(region, motif, cell, cell, 0.5), region)


def stripes(shape, width: float = 4.0, gap: float = 4.0, *, angle: float = 90.0,
            pinstripe: float | None = None) -> str:
    """Solid stripes (``width`` on, ``gap`` off) at ``angle``; optional hairline
    ``pinstripe`` centred in each gap. -> FILL."""
    _pos("stripes", width=width, gap=gap)
    region = _region(shape)
    if region.is_empty:
        return ""
    pitch = width + gap
    centres = _parallel_lines(region, angle, pitch)
    geom = G.outline(centres, width, cap="flat", as_shape=True)
    if pinstripe:
        geom = geom.union(G.outline(_parallel_lines(region, angle, pitch, offset=pitch / 2), pinstripe,
                                    cap="flat", as_shape=True))
    return _cut(geom, region)


def ermine_spot(cx: float, cy: float, size: float = 10.0) -> str:
    """Heraldic ermine spot: a flared three-tailed body under three dots. -> FILL."""
    _pos("ermine_spot", size=size)
    s = size
    parts = [stroke(np.array([(cx, cy - s * 0.1), (cx, cy + s * 0.55)]), s * 0.34, "teardrop")]
    for sg in (-1, 1):
        parts.append(stroke(np.array([(cx, cy + s * 0.05), (cx + sg * s * 0.28, cy + s * 0.5)]),
                            s * 0.2, "teardrop"))
    for dx, dy in ((0, -0.42), (-0.24, -0.24), (0.24, -0.24)):
        parts.append(G.circle_d(cx + dx * s, cy + dy * s, s * 0.1))
    return G.union(*parts)


def ermine(shape, cell: float = 26.0, *, size: float | None = None) -> str:
    """Ermine: spots on a half-drop grid. -> FILL."""
    _pos("ermine", cell=cell)
    region = _region(shape)
    if region.is_empty:
        return ""
    sz = size or cell * 0.42
    base = G.to_shape(ermine_spot(cell / 2, cell / 2, sz))
    return _cut(_tiled(region, base, cell, cell, 0.5), region)


def chevrons(shape, cell: float = 12.0, height: float = 6.0, *, lw: float = 1.05,
             angle: float = 0.0) -> str:
    """Nested zigzag (chevron) lines, ``cell`` apart, each zig ``height`` tall. -> FILL."""
    _lw("chevrons", lw)
    _pos("chevrons", cell=cell)
    region = _region(shape)
    if region.is_empty:
        return ""
    x0, y0, x1, y1 = region.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + cell
    xs = np.arange(-R, R + cell, cell)
    lines = []
    k = -int(R / cell) - 1
    while k * cell <= R:
        ys = k * cell + np.where(np.arange(len(xs)) % 2 == 0, -height / 2, height / 2)
        P = np.column_stack([xs, ys])
        if angle:
            P = G.rotate(P, angle)
        lines.append(P + np.array([cx, cy]))
        k += 1
    return _cut(G.outline(lines, lw, cap="flat", join="miter", as_shape=True), region)


def checks(shape, cell: float = 10.0, *, angle: float = 0.0) -> str:
    """Checkerboard (alternate squares solid; ``angle`` 45 for harlequin). -> FILL."""
    _pos("checks", cell=cell)
    region = _region(shape)
    if region.is_empty:
        return ""
    x0, y0, x1, y1 = region.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + cell
    n = int(R / cell) + 1
    sq = []
    for i in range(-n, n):
        for j in range(-n, n):
            if (i + j) % 2:
                continue
            q = np.array([(i * cell, j * cell), ((i + 1) * cell, j * cell), ((i + 1) * cell, (j + 1) * cell),
                          (i * cell, (j + 1) * cell)])
            if angle:
                q = G.rotate(q, angle)
            sq.append(shapely.Polygon(q + np.array([cx, cy])))
    return _cut(shapely.union_all(sq), region)


def polka(shape, spacing: float = 10.0, r: float = 2.0, *, grid: str = "hex") -> str:
    """Polka dots (whole dots only). -> FILL."""
    from ..hatch import dot_screen
    return dot_screen(shape, spacing, r, grid=grid)


def tile(shape, motif: str, cell_w: float, cell_h: float | None = None, *, drop: float = 0.5,
         origin=(0.0, 0.0), clip: bool = True, alternate: str | None = None) -> str:
    """Repeat a motif (FILL d centred on the origin) over a shape on a
    half-drop grid (``drop`` 0 = straight grid). ``alternate`` motif is used on
    odd columns (e.g. a smaller flower). Clipped to the shape. -> FILL."""
    _pos("tile", cell_w=cell_w)
    region = _region(shape)
    if region.is_empty or not motif:
        return ""
    ch = cell_h or cell_w
    out = []
    for x, y, i, j in _grid(region, cell_w, ch, drop):
        m = alternate if (alternate and i % 2) else motif
        out.append(G.translate(m, x + origin[0] + cell_w / 2, y + origin[1] + ch / 2))
    d = "".join(out)
    return _cut(d, region) if clip else d
