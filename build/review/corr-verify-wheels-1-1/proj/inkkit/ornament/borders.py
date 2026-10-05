"""Borders & frames: nested rules, pearls, rope, dentils, Greek key,
egg-and-dart, deco bands (zigzag / ladder / diamond / triangles), corner
rosettes, cartouches and banner ribbons.

Strip motifs are designed in local strip coordinates (u = distance along the
path, v = offset across it) and bent along any path with ``Curve.map``; on
closed paths the pitch is adjusted so a whole number of repeats fits. For
rectangular frames prefer :func:`frame_strip`, which lays the motif out side
by side (a whole number of repeats per side) with a block, rosette or any
motif in each corner, instead of bending one strip round the corners.

Return types: FILL unless noted. Line-art motifs take ``lw`` (line width):
with ``lw=None`` they return STROKE centrelines instead; motifs that also have
solid parts then need ``parts=True`` (-> {'stroke': d, 'fill': d}).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import Polygon, box as sbox

from .. import geom as G
from .. import tokens as T
from ..stroke import stroke

__all__ = ["frame_shape", "frame_path", "frame", "rules", "beaded", "rope", "dentil",
           "greek_key", "greek_key_frame", "egg_and_dart", "band", "frame_strip",
           "corner_block", "corner_rosette", "cartouche", "ribbon", "fit_repeats"]

_CORNERS = ("round", "square", "notch", "chamfer", "step", "step2", None)


# =============================================================================
# helpers
# =============================================================================
def fit_repeats(length: float, pitch: float, closed: bool = True) -> tuple[int, float]:
    """(count, adjusted pitch) so repeats tile ``length`` exactly."""
    if not pitch > 0:
        raise ValueError(f"fit_repeats: pitch must be > 0, got {pitch!r}")
    if not length > 0:
        raise ValueError(f"fit_repeats: length must be > 0, got {length!r}")
    n = max(1, int(round(length / pitch)))
    return n, length / n


def _densify(uv, step=1.0, closed=True):
    P = np.asarray(uv, float)
    Q = np.vstack([P, P[:1]]) if closed else P
    out = []
    for a, b in zip(Q[:-1], Q[1:]):
        n = max(1, int(math.ceil(np.hypot(*(b - a)) / step)))
        out.append(a + np.outer(np.arange(n) / n, b - a))
    if not closed:
        out.append(Q[-1:])
    return np.vstack(out)


def _map(cv: G.Curve, uv, closed=True, step=1.0):
    return cv.map(_densify(uv, step, closed))


def _strip_curve(path, closed, fillet):
    """Curve for strip mapping; sharp corners are rounded (radius ``fillet``,
    0 = off) on open and closed paths so the motif never folds."""
    cv = G.curve(path, closed)
    if fillet:
        if cv.closed:
            # morphological open+close rounds convex AND concave corners at any
            # vertex density (polyline arcs with short segments included)
            d = G.fillet(G.poly_d(cv.pts, True), fillet)
            cv = G.Curve(G.resample(d, 0.5) if d else cv.pts, True)
        else:
            cv = G.Curve(G.round_corners(G.poly_d(cv.pts, False), fillet), False)
    return cv


def _emit(lines, lw, cap="round", join="round"):
    """lines: list of (pts, closed). STROKE if lw None else FILL outline."""
    if lw is None:
        return "".join(G.poly_d(p, c) for p, c in lines)
    if not lw > 0:
        raise ValueError(f"lw must be > 0 (or None for STROKE), got {lw!r}")
    return G.outline(lines, lw, cap=cap, join=join)


def _need_lw(name, lw):
    if lw is None:
        raise ValueError(f"{name} is FILL-only: pass a line width (lw=<px>), not lw=None")


def _parts(stroke_d, fill_d, lw, parts, name):
    if parts:
        return {"stroke": stroke_d if lw is None else "", "fill": fill_d if lw is None else stroke_d + fill_d}
    if lw is None and fill_d:
        raise ValueError(f"{name}(lw=None) has solid parts: pass parts=True to get "
                         "{'stroke': ..., 'fill': ...}, or a numeric lw")
    return stroke_d + fill_d


def _radius_of_curvature(cv: G.Curve, s):
    h = 1.0
    a1 = np.radians(cv.angle(np.clip((s - h) / cv.length, 0, 1)))
    a2 = np.radians(cv.angle(np.clip((s + h) / cv.length, 0, 1)))
    da = np.abs(np.arctan2(np.sin(a2 - a1), np.cos(a2 - a1)))
    return 2 * h / np.maximum(da, 1e-9)


# =============================================================================
# frames and rules
# =============================================================================
def _corner_cut(kind, r):
    if kind == "notch":
        a = np.radians(np.linspace(0, 90, 48))
        return Polygon(np.vstack([[[0, 0]], np.column_stack([r * np.cos(a), r * np.sin(a)])]))
    if kind == "chamfer":
        return Polygon([(0, 0), (r, 0), (0, r)])
    if kind == "step":
        return Polygon([(0, 0), (r, 0), (r, r), (0, r)])
    if kind == "step2":
        h = r / 2
        return Polygon([(0, 0), (r, 0), (r, h), (h, h), (h, r), (0, r)])
    raise ValueError(f"corner must be one of {_CORNERS}, not {kind!r}")


def _base_shape(x, y, w, h, r, corner):
    if corner not in _CORNERS:
        raise ValueError(f"corner must be one of {_CORNERS}, not {corner!r}")
    if not (w > 0 and h > 0):
        raise ValueError("frame: w and h must be > 0")
    if corner in ("square", None) or r <= 0:
        return sbox(x, y, x + w, y + h)
    if corner == "round":
        return G.to_shape(G.rect_d(x, y, w, h, r), tol=0.02)
    b = sbox(x, y, x + w, y + h)
    cut = _corner_cut(corner, r)
    for (cx, cy, sx, sy) in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        c = shapely.affinity.affine_transform(cut, [sx, 0, 0, sy, cx, cy])
        b = b.difference(c)
    return b


def frame_shape(x, y, w, h, r: float = 0.0, corner: str = "round", inset: float = 0.0) -> str:
    """Closed outline of a frame box with corner style
    'round' | 'square' | 'notch' (concave) | 'chamfer' | 'step' | 'step2',
    optionally inset (concentric: notches/steps stay parallel). -> FILL d."""
    b = _base_shape(x, y, w, h, r, corner)
    if inset:
        b = b.buffer(-inset, join_style="mitre", mitre_limit=10, quad_segs=24)
    return G.from_shape(b)


def frame_path(x, y, w, h, r: float = 0.0, corner: str = "round", inset: float = 0.0) -> str:
    """Centreline (closed path d) of a frame at ``inset`` — feed to beaded(),
    rope(), band(), guilloche_band() ... Clockwise on screen, so the Curve
    left normal points outward."""
    b = _base_shape(x, y, w, h, r, corner)
    if inset:
        b = b.buffer(-inset, join_style="mitre", mitre_limit=10, quad_segs=24)
    if b.is_empty:
        raise ValueError("frame_path: inset consumes the frame")
    ring = np.asarray(b.exterior.coords)[:-1]
    return G.poly_d(ring, True, orient="cw")


def rules(x, y, w, h, spec, r: float = 0.0, corner: str = "round") -> str:
    """Nested rule lines: ``spec`` = [(inset, width), ...] measured from the box
    edge. Each rule is an exact ring (outer offset minus inner). -> FILL d."""
    b = _base_shape(x, y, w, h, r, corner)
    out = []
    for inset, width in spec:
        if not width > 0:
            raise ValueError("rules: every rule width must be > 0")
        o = b.buffer(-inset, join_style="mitre", mitre_limit=10, quad_segs=24) if inset else b
        i = b.buffer(-(inset + width), join_style="mitre", mitre_limit=10, quad_segs=24)
        out.append(G.from_shape(o.difference(i)))
    return "".join(out)


_FRAME_PRESETS = ("classic", "triple", "deco", "fine")


def frame(x, y, w, h, *, r: float = 20.0, corner: str = "round", style: str = "classic",
          weight: float = 1.0) -> str:
    """Preset nested frames (weights scale with ``weight``). -> FILL d.

    classic   heavy outer rule + fine rule inside (the playing-card staple)
    triple    fine / heavy / fine
    deco      two fine rules with a wide gap (use corner='step' or 'step2')
    fine      two fine rules
    Rules are never thinner than the print minimum."""
    if style not in _FRAME_PRESETS:
        raise ValueError(f"frame style must be one of {_FRAME_PRESETS}, not {style!r}")
    k = weight
    m = T.MIN_LINE
    presets = {
        "classic": [(0, max(3.2 * k, m)), (6 * k, max(1.2 * k, m))],
        "triple": [(0, max(1.2 * k, m)), (4 * k, max(3.0 * k, m)), (10 * k, max(1.2 * k, m))],
        "deco": [(0, max(1.4 * k, m)), (9 * k, max(1.4 * k, m))],
        "fine": [(0, max(1.1 * k, m)), (3.8 * k, max(1.1 * k, m))],
    }
    return rules(x, y, w, h, presets[style], r, corner)


# =============================================================================
# pearls, rope, dentils
# =============================================================================
def beaded(path, r: float = 2.2, gap: float = 2.2, *, alternate: float | None = None,
           closed: bool | None = None, start: float = 0.0) -> str:
    """Pearls evenly along a path (exact fit on closed paths, centred on open
    ones). ``alternate``: radius of every other pearl (big-small rhythm). -> FILL d."""
    if not r > 0:
        raise ValueError(f"beaded: r must be > 0, got {r!r}")
    if alternate is not None and not alternate > 0:
        raise ValueError("beaded: alternate radius must be > 0")
    cv = G.curve(path, closed)
    pitch = 2 * r + gap if alternate is None else r + alternate + gap
    if not pitch > 0:
        raise ValueError("beaded: pearl pitch must be > 0")
    if cv.closed:
        n, p = fit_repeats(cv.length, pitch)
        s = start + np.arange(n) * p
    else:
        n = int(cv.length // pitch) + 1
        off = (cv.length - (n - 1) * pitch) / 2
        s = off + np.arange(n) * pitch
    P = cv.at_s(s)
    out = []
    for k, (px, py) in enumerate(P):
        rr = r if (alternate is None or k % 2 == 0) else alternate
        out.append(G.circle_d(px, py, rr))
    return "".join(out)


def _repeats(cv, pitch):
    return fit_repeats(cv.length, pitch)


def rope(path, width: float = 8.0, pitch: float = 6.0, *, slant: float = 0.9,
         gap: float = 1.2, closed: bool | None = None, style: str = "fill",
         lw: float | None = 1.05, fillet: float | None = None) -> str:
    """Twisted rope along a path (a whole number of strands on closed AND open
    paths). style 'fill': solid strands separated by paper gaps of ``gap`` px
    (engraved); 'line': rails + S-shaped strand divisions (monoline, ``lw``;
    ``lw=None`` -> STROKE). ``slant`` = how far a strand leans (in widths)."""
    if style not in ("fill", "line"):
        raise ValueError(f"rope style must be 'fill' or 'line', not {style!r}")
    if not (width > 0 and pitch > 0):
        raise ValueError("rope: width and pitch must be > 0")
    cv = _strip_curve(path, closed, width * 0.75 if fillet is None else fillet)
    n, p = _repeats(cv, pitch)
    hw = width / 2
    v = np.linspace(-hw, hw, 24)

    def sep(u0):
        u = u0 + slant * (v / width) * width * 0.5 + 0.25 * p * np.sin(np.pi * (v + hw) / width)
        return np.column_stack([u, v])

    out = []
    if style == "fill":
        for k in range(n):
            a = sep(k * p)
            b = sep((k + 1) * p)
            poly = np.vstack([a, b[::-1]])
            pg = Polygon(poly).buffer(-gap / 2, join_style="round", quad_segs=6)
            pg = pg.buffer(gap * 0.35, join_style="round", quad_segs=6).buffer(-gap * 0.35, quad_segs=6)
            if pg.is_empty:
                continue
            for part in getattr(pg, "geoms", [pg]):
                ring = np.asarray(part.exterior.coords)[:-1]
                out.append(G.poly_d(cv.map(_densify(ring, 0.8, True)), True, orient="cw"))
        return "".join(out)
    lines = []
    for k in range(n + (0 if cv.closed else 1)):
        lines.append((cv.map(sep(k * p)), False))
    s = np.linspace(0, cv.length, max(50, int(cv.length)), endpoint=not cv.closed)
    for side in (-hw, hw):
        lines.append((cv.map(np.column_stack([s, np.full_like(s, side)])), cv.closed))
    return _emit(lines, lw)


def dentil(path, depth: float = 6.0, tooth: float = 5.0, gap: float = 3.0, *,
           rail: float | None = 1.05, closed: bool | None = None, fillet: float | None = None) -> str:
    """Dentil course: rectangular teeth on the left side of the path (outward
    on a clockwise frame path), with an optional rail of width ``rail``; a
    whole number of teeth on open and closed paths. -> FILL."""
    if not (depth > 0 and tooth > 0 and gap >= 0):
        raise ValueError("dentil: depth and tooth must be > 0, gap >= 0")
    cv = _strip_curve(path, closed, depth if fillet is None else fillet)
    pitch = tooth + gap
    n, p = _repeats(cv, pitch)
    t = tooth * p / pitch
    out = []
    for k in range(n):
        u0 = k * p + (p - t) / 2
        quad = [(u0, 0), (u0 + t, 0), (u0 + t, depth), (u0, depth)]
        out.append(G.poly_d(_map(cv, quad, True, 0.8), True, orient="cw"))
    if rail:
        s = np.linspace(0, cv.length, max(50, int(cv.length)), endpoint=not cv.closed)
        out.append(G.outline([(cv.map(np.column_stack([s, np.full_like(s, -rail / 2 - 0.8)])), cv.closed)],
                             rail, cap="flat"))
    return "".join(out)


# =============================================================================
# Greek key
# =============================================================================
_KEY = np.array([(0, 8), (0, 0), (8, 0), (8, 6), (4, 6), (4, 4), (6, 4), (6, 2), (2, 2), (2, 8),
                 (10, 8)], float)


def greek_key(p0, p1, height: float = 14.0, *, lw: float | None = 1.4, repeats: int | None = None,
              flip: bool = False) -> str:
    """Continuous Greek-key meander from p0 to p1, ``height`` tall (grows to the
    left of the direction of travel unless ``flip``). -> FILL (or STROKE if lw None)."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    if L < 1e-9 or not height > 0:
        raise ValueError("greek_key: p0 != p1 and height > 0 required")
    if repeats is not None and repeats < 1:
        raise ValueError("greek_key: repeats must be >= 1")
    g = height / 8
    unit = 10 * g
    n = repeats or max(1, int(round((L - 2 * g) / unit)))
    sx = (L - 2 * g) / (n * 10 * g)
    pts = []
    for k in range(n):
        P = _KEY.copy()
        P[:, 0] = (P[:, 0] + 10 * k) * sx
        pts.append(P if k == 0 else P[1:])
    P = np.vstack(pts)
    P = np.vstack([P, [P[-1, 0] + 0, 8]])
    u = P[:, 0] * g + g
    v = (8 - P[:, 1]) * g * (-1 if flip else 1)
    d = (p1 - p0) / L
    nrm = np.array([d[1], -d[0]])
    Q = p0 + np.outer(u, d) + np.outer(v, nrm)
    Q = np.vstack([p0, Q, p1])
    return _emit([(Q, False)], lw, cap="square", join="mitre")


def greek_key_frame(x, y, w, h, height: float = 14.0, *, lw: float | None = 1.4,
                    corner_box: bool = True) -> str:
    """Greek key running round a rectangle (inside it), with square corner
    blocks. -> FILL (or STROKE if lw None)."""
    H = height
    out = []
    sides = [((x + H, y + H), (x + w - H, y + H)), ((x + w - H, y + H), (x + w - H, y + h - H)),
             ((x + w - H, y + h - H), (x + H, y + h - H)), ((x + H, y + h - H), (x + H, y + H))]
    for a, b in sides:
        out.append(greek_key(a, b, H, lw=lw, flip=False))
    if corner_box:
        lines = []
        for cx, cy in ((x, y), (x + w - H, y), (x, y + h - H), (x + w - H, y + h - H)):
            lines.append((np.array([(cx, cy), (cx + H, cy), (cx + H, cy + H), (cx, cy + H)]), True))
            q = H * 0.3
            lines.append((np.array([(cx + q, cy + q), (cx + H - q, cy + q), (cx + H - q, cy + H - q),
                                    (cx + q, cy + H - q)]), True))
        out.append(_emit(lines, lw, cap="square", join="mitre"))
    return "".join(out)


# =============================================================================
# egg and dart
# =============================================================================
def egg_and_dart(path, height: float = 16.0, pitch: float | None = None, *, lw: float = 1.2,
                 closed: bool | None = None, fillet: float | None = None, rail: bool = True) -> str:
    """Egg-and-dart moulding along a path, hanging on its left side from a
    rail: ovoid eggs (fuller at the top) sit in open U-shaped shells, with a
    spear dart — shaft and arrow head — between each pair of shells.
    FILL-only (``lw`` is the shell / shaft line width). -> FILL d."""
    _need_lw("egg_and_dart", lw)
    if not height > 0:
        raise ValueError("egg_and_dart: height must be > 0")
    cv = _strip_curve(path, closed, height if fillet is None else fillet)
    pitch = pitch or height * 1.05
    n, p = _repeats(cv, pitch)
    H = height
    solids, lines = [], []
    for k in range(n):
        u0 = (k + 0.5) * p
        # egg: ovoid, fuller toward the rail, narrower toward the tip
        th = np.linspace(0, 2 * math.pi, 96, endpoint=False)
        rx, ry = 0.25 * p, 0.33 * H
        ex = u0 + rx * np.cos(th) * (1 - 0.14 * np.sin(th))
        ey = 0.48 * H + ry * np.sin(th)
        solids.append(G.poly_d(cv.map(np.column_stack([ex, ey])), True, orient="cw"))
        # shell: an open U around the egg, rising to the rail
        a = np.linspace(-0.02 * math.pi, 1.02 * math.pi, 64)
        gx = rx + max(lw * 1.4, 0.07 * p) + lw / 2
        gy = ry + max(lw * 1.4, 0.08 * H) + lw / 2
        sx = u0 + gx * np.cos(a)
        sy = 0.48 * H + gy * np.sin(a)
        shell = np.vstack([[sx[0], 0.0], np.column_stack([sx, sy]), [sx[-1], 0.0]])
        lines.append((cv.map(shell[::-1]), False))
        # dart: shaft from the rail + a spear head
        ud = k * p
        if cv.closed or k > 0:
            lines.append((cv.map(np.array([(ud, 0.0), (ud, 0.62 * H)])), False))
            hw_ = max(0.09 * p, lw * 1.6)
            head = np.array([(ud, 0.95 * H), (ud + hw_, 0.64 * H), (ud, 0.72 * H), (ud - hw_, 0.64 * H)])
            solids.append(G.poly_d(_map(cv, head, True, 0.5), True, orient="cw"))
    if rail:
        s = np.linspace(0, cv.length, max(50, int(cv.length)), endpoint=not cv.closed)
        lines.append((cv.map(np.column_stack([s, np.full_like(s, -lw / 2)])), cv.closed))
    return G.outline(lines, lw) + "".join(solids)


# =============================================================================
# deco bands (Monarchs-style)
# =============================================================================
_BAND_FILLS = ("zigzag", "triangles", "ladder", "diamond", "chevron", "dots", "none")


def band(path, width: float = 10.0, fill: str = "zigzag", pitch: float | None = None, *,
         rails: bool = True, lw: float | None = 1.2, closed: bool | None = None,
         fillet: float | None = None, parts: bool = False):
    """Two-rail band along a path with an infill motif:
    'zigzag' | 'triangles' (every other triangle solid) | 'ladder' | 'diamond' |
    'chevron' | 'dots' | 'none'. Sharp corners are rounded (``fillet``,
    default 0.75*width) and solid motifs that would fall on a bend tighter
    than the band are left out (so nothing smears into blobs) — for
    rectangles use :func:`frame_strip`. -> FILL d; with ``lw=None`` the line
    work is STROKE and solid motifs need ``parts=True``
    (-> {'stroke': d, 'fill': d})."""
    if fill not in _BAND_FILLS:
        raise ValueError(f"band fill must be one of {_BAND_FILLS}, not {fill!r}")
    if not width > 0:
        raise ValueError("band: width must be > 0")
    cv = _strip_curve(path, closed, width * 0.75 if fillet is None else fillet)
    pitch = pitch or width
    n, p = _repeats(cv, pitch)
    hw = width / 2
    lines = []
    solids = []

    def tight(u_a, u_b):
        s = np.linspace(u_a, u_b, 7)
        if cv.closed:
            s = np.mod(s, cv.length)
        return float(np.min(_radius_of_curvature(cv, s))) < 1.1 * width

    if rails:
        s = np.linspace(0, cv.length, max(50, int(cv.length)), endpoint=not cv.closed)
        for side in (-hw, hw):
            lines.append((cv.map(np.column_stack([s, np.full_like(s, side)])), cv.closed))
    if fill in ("zigzag", "triangles"):
        if cv.closed and n % 2 == 1:
            n, p = n + 1, cv.length / (n + 1)
        pts = [(k * p, -hw if k % 2 == 0 else hw) for k in range(n + 1)]
        Z = _densify(np.array(pts), 0.8, False)
        lines.append((cv.map(Z), False))
        if fill == "triangles":
            for k in range(0, n, 2):
                if (k + 2) * p > cv.length + 1e-6 and not cv.closed:
                    continue
                if tight(k * p, (k + 2) * p):
                    continue
                tri = [(k * p, -hw), ((k + 2) * p, -hw), ((k + 1) * p, hw)]
                solids.append(G.poly_d(_map(cv, tri, True, 0.6), True, orient="cw"))
    elif fill == "ladder":
        for k in range(n + (0 if cv.closed else 1)):
            lines.append((cv.map(_densify(np.array([(k * p, -hw), (k * p, hw)]), 0.8, False)), False))
    elif fill == "diamond":
        for k in range(n):
            if tight(k * p, (k + 1) * p):
                continue
            dm = np.array([(k * p, 0), ((k + 0.5) * p, -hw), ((k + 1) * p, 0), ((k + 0.5) * p, hw)])
            lines.append((_map(cv, dm, True, 0.8), True))
    elif fill == "chevron":
        for k in range(n + (0 if cv.closed else 1)):
            ch = np.array([(k * p - 0.35 * p, -hw), (k * p, 0), (k * p - 0.35 * p, hw)])
            lines.append((cv.map(_densify(ch, 0.8, False)), False))
    elif fill == "dots":
        for k in range(n):
            q = cv.at_s((k + 0.5) * p)
            solids.append(G.circle_d(q[0], q[1], width * 0.18))
    st = _emit(lines, lw)
    return _parts(st, "".join(solids), lw, parts, "band")


def corner_block(cx: float, cy: float, size: float, *, lw: float | None = 1.2,
                 style: str = "square") -> str:
    """Corner block for :func:`frame_strip`: 'square' (square in a square with
    a centre pearl), 'diamond' (lozenge in a square) or 'pearl'. -> FILL d
    (STROKE outlines with lw=None; the pearl stays FILL)."""
    if style not in ("square", "diamond", "pearl"):
        raise ValueError("corner_block style must be 'square', 'diamond' or 'pearl'")
    h = size / 2
    if style == "pearl":
        return G.circle_d(cx, cy, size * 0.3)
    lines = [(np.array([(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]), True)]
    q = h * 0.55
    if style == "square":
        lines.append((np.array([(cx - q, cy - q), (cx + q, cy - q), (cx + q, cy + q), (cx - q, cy + q)]), True))
    else:
        lines.append((np.array([(cx, cy - q), (cx + q, cy), (cx, cy + q), (cx - q, cy)]), True))
    out = _emit(lines, lw, cap="square", join="mitre")
    if lw is not None:
        out += G.circle_d(cx, cy, max(size * 0.1, T.MIN_LINE))
    return out


_STRIPS = ("band", "rope", "dentil", "egg_and_dart", "beaded", "greek_key")


def frame_strip(x, y, w, h, motif="band", width: float = 10.0, *, inset: float = 0.0,
                corner="square", **kw) -> str:
    """Lay a strip motif round a rectangle SIDE BY SIDE: each side is a straight
    run with its own whole number of repeats (``fit_repeats`` per side) and each
    corner gets a ``corner`` motif, so nothing is bent round a corner.

    motif   'band' | 'rope' | 'dentil' | 'egg_and_dart' | 'beaded' | 'greek_key'
            or callable(path_pts (2,2) array, width, **kw) -> d
    width   margin the strip occupies inside the box (inset by ``inset``)
    corner  'square' | 'diamond' | 'pearl' (see :func:`corner_block`),
            'rosette', None, or callable(cx, cy, size) -> d
    Extra keywords go to the motif (e.g. ``fill='triangles', lw=1.2``). -> FILL d."""
    if not (callable(motif) or motif in _STRIPS):
        raise ValueError(f"motif must be one of {_STRIPS} or a callable, not {motif!r}")
    X0, Y0, X1, Y1 = x + inset, y + inset, x + w - inset, y + h - inset
    if not (X1 - X0 > 2 * width and Y1 - Y0 > 2 * width):
        raise ValueError("frame_strip: the box is too small for the strip width")
    m = width / 2
    # clockwise runs, centred in the margin; each run stops at the corner squares
    runs = [((X0 + width, Y0 + m), (X1 - width, Y0 + m)), ((X1 - m, Y0 + width), (X1 - m, Y1 - width)),
            ((X1 - width, Y1 - m), (X0 + width, Y1 - m)), ((X0 + m, Y1 - width), (X0 + m, Y0 + width))]
    out = []
    for a, b in runs:
        a = np.asarray(a, float); b = np.asarray(b, float)
        dvec = (b - a) / np.hypot(*(b - a))
        nrm = np.array([dvec[1], -dvec[0]])   # left normal = outward on a clockwise run
        if callable(motif):
            out.append(motif(np.array([a, b]), width, **kw))
        elif motif == "band":
            out.append(band(np.array([a, b]), width * 0.8, closed=False, fillet=0, **kw))
        elif motif == "rope":
            out.append(rope(np.array([a, b]), width * 0.8, closed=False, fillet=0, **kw))
        elif motif == "beaded":
            r = kw.get("r", width * 0.28)
            out.append(beaded(np.array([a, b]), r, kw.get("gap", r * 0.9), closed=False,
                              alternate=kw.get("alternate")))
        elif motif == "greek_key":
            aa, bb = a + nrm * m * 0.8, b + nrm * m * 0.8
            out.append(greek_key(aa, bb, width * 0.8, lw=kw.get("lw", 1.4), flip=True))
        elif motif in ("dentil", "egg_and_dart"):
            # hang inward from a rail on the outer edge: run reversed so its
            # left side faces the frame interior
            aa, bb = b + nrm * m * 0.9, a + nrm * m * 0.9
            if motif == "dentil":
                out.append(dentil(np.array([aa, bb]), kw.get("depth", width * 0.7),
                                  kw.get("tooth", width * 0.45), kw.get("gap", width * 0.3),
                                  rail=kw.get("rail", 1.05), closed=False, fillet=0))
            else:
                out.append(egg_and_dart(np.array([aa, bb]), width * 0.85, kw.get("pitch"),
                                        lw=kw.get("lw", 1.2), closed=False, fillet=0))
    corners = [(X0 + m, Y0 + m), (X1 - m, Y0 + m), (X1 - m, Y1 - m), (X0 + m, Y1 - m)]
    for cx, cy in corners:
        if corner is None:
            continue
        if callable(corner):
            out.append(corner(cx, cy, width))
        elif corner == "rosette":
            out.append(corner_rosette(cx, cy, width * 0.45, style="flower", lw=kw.get("lw", 1.2) or 1.2))
        else:
            out.append(corner_block(cx, cy, width * 0.8, lw=kw.get("lw", 1.2), style=corner))
    return "".join(out)


# =============================================================================
# rosettes & cartouches
# =============================================================================
def corner_rosette(cx: float, cy: float, r: float, *, petals: int = 8, style: str = "flower",
                   lw: float | None = 1.05, rot: float = -90.0) -> str:
    """Small rosette for frame corners / medallions. style 'flower' (lens
    petals + ring; FILL-only), 'star' (faceted compass star; FILL-only),
    'daisy' (outlined petals; STROKE with lw=None). -> FILL d."""
    if style not in ("flower", "daisy", "star"):
        raise ValueError(f"corner_rosette style must be 'flower', 'daisy' or 'star', not {style!r}")
    if petals < 2 or not r > 0:
        raise ValueError("corner_rosette: petals >= 2 and r > 0 required")
    out = []
    if style == "flower":
        _need_lw("corner_rosette(style='flower')", lw)
        for k in range(petals):
            a = math.radians(rot + 360 * k / petals)
            u = np.array([math.cos(a), math.sin(a)])
            out.append(stroke(np.array([(cx, cy) + u * r * 0.22, (cx, cy) + u * r * 0.86]), r * 0.34,
                              "swell", min_width=T.MIN_LINE))
        out.append(G.circle_d(cx, cy, r * 0.16))
        out.append(G.outline([(G.arc_pts(cx, cy, r, 0, 360)[:-1], True)], lw))
        return "".join(out)
    if style == "daisy":
        lines = []
        for k in range(petals):
            a = math.radians(rot + 360 * k / petals)
            u = np.array([math.cos(a), math.sin(a)]); nn = np.array([-u[1], u[0]])
            t = np.linspace(0, 1, 40)
            wd = np.sin(np.pi * t) ** 0.8 * r * 0.2
            c = np.array([cx, cy]) + np.outer(r * (0.25 + 0.7 * t), u)
            poly = np.vstack([c + np.outer(wd, nn), (c - np.outer(wd, nn))[::-1]])
            lines.append((poly, True))
        lines.append((G.arc_pts(cx, cy, r * 0.2, 0, 360)[:-1], True))
        return _emit(lines, lw)
    _need_lw("corner_rosette(style='star')", lw)
    from .radiance import starburst
    return starburst(cx, cy, r, r * 0.38, points=petals, rot=rot, lw=lw)


_CARTOUCHES = ("tab", "oval", "ogee", "bracket", "scroll", "shield")


def cartouche(cx: float, cy: float, w: float, h: float, style: str = "tab", *,
              r: float | None = None) -> str:
    """Closed plaque outline centred at (cx, cy) (stroke it, fill it, or use it
    as a clip). style:
    'tab'     rectangle with concave notched corners (ticket)
    'oval'    ellipse
    'ogee'    label with pointed ogee ends (end length clamped to w/2)
    'bracket' concave half-round ends with round corner knobs ('scroll' alias)
    'shield'  heater shield
    -> FILL d (closed, clockwise outline)."""
    if style not in _CARTOUCHES:
        raise ValueError(f"cartouche style must be one of {_CARTOUCHES}, not {style!r}")
    if not (w > 0 and h > 0):
        raise ValueError("cartouche: w and h must be > 0")
    x0, y0 = cx - w / 2, cy - h / 2
    if style == "tab":
        rr = r if r is not None else h * 0.28
        return frame_shape(x0, y0, w, h, min(rr, 0.49 * min(w, h)), "notch")
    if style == "oval":
        return G.ellipse_d(cx, cy, w / 2, h / 2)
    if style == "ogee":
        e = r if r is not None else h * 0.6
        e = min(e, w / 2)
        pts = [(x0 + e, y0), (x0 + w - e, y0)]
        right = [("C", x0 + w - e * 0.35, y0, x0 + w - e * 0.55, cy, x0 + w, cy),
                 ("C", x0 + w - e * 0.55, cy, x0 + w - e * 0.35, y0 + h, x0 + w - e, y0 + h)]
        left = [("C", x0 + e * 0.35, y0 + h, x0 + e * 0.55, cy, x0, cy),
                ("C", x0 + e * 0.55, cy, x0 + e * 0.35, y0, x0 + e, y0)]
        cmds = [("M", *pts[0]), ("L", *pts[1]), *right, ("L", x0 + e, y0 + h), *left, ("Z",)]
        return G.cmds_to_d(cmds)
    if style in ("bracket", "scroll"):
        kr = r if r is not None else h * 0.16
        body = G.rect_d(x0 + kr, y0, w - 2 * kr, h, 0)
        bites = [G.circle_d(x0 + kr * 0.2, cy, h * 0.5 - kr * 1.2), G.circle_d(x0 + w - kr * 0.2, cy, h * 0.5 - kr * 1.2)]
        knobs = [G.circle_d(xx, yy, kr) for xx in (x0 + kr, x0 + w - kr) for yy in (y0 + kr, y0 + h - kr)]
        side = [G.rect_d(x0, y0 + kr, kr * 2, h - 2 * kr), G.rect_d(x0 + w - 2 * kr, y0 + kr, kr * 2, h - 2 * kr)]
        return G.difference(G.union(body, *knobs, *side), *bites)
    cmds = [("M", x0, y0), ("L", x0 + w, y0), ("L", x0 + w, y0 + h * 0.45),
            ("C", x0 + w, y0 + h * 0.75, cx + w * 0.2, y0 + h * 0.9, cx, y0 + h),
            ("C", cx - w * 0.2, y0 + h * 0.9, x0, y0 + h * 0.75, x0, y0 + h * 0.45), ("Z",)]
    return G.cmds_to_d(cmds)


# =============================================================================
# ribbon
# =============================================================================
def ribbon(x0: float, x1: float, y: float, height: float = 22.0, *, sag: float = 0.0,
           tail: float | None = None, lw: float | None = 1.4, fork: bool = True,
           ends: str = "fold", drop: float | None = None, lift: float = 0.0) -> dict:
    """Banner ribbon from x0 to x1 at centre height y (``sag`` bows it, + =
    down) with, at each end, either folded forked tails (``ends='fold'``,
    the 'REGIS' banner) or rolled scroll ends (``ends='roll'``).

    Tails follow the end tangent of the (sagging) front; the fold is a true
    parallelogram (the back face of the ribbon, hatch it) and nothing hidden
    behind the front is drawn. ``lift`` raises the tails' outer ends (px).

    Returns {'front', 'tails', 'back', 'silhouette', 'lines', 'path'}:
    closed FILL regions (tails and back exclude everything the front covers),
    the union silhouette (use it to knock out what lies behind the ribbon),
    ``lines`` = all visible outlines (FILL at ``lw``, STROKE if lw None) and
    ``path``, the centreline for ``text_on_path``."""
    if ends not in ("fold", "roll"):
        raise ValueError(f"ribbon ends must be 'fold' or 'roll', not {ends!r}")
    if not x1 - x0 > 1e-6:
        raise ValueError("ribbon: x1 must be greater than x0")
    if not height > 0:
        raise ValueError("ribbon: height must be > 0")
    H = height
    tl = tail if tail is not None else H * 1.6
    dp = drop if drop is not None else H * 0.38
    xs = np.linspace(x0, x1, 120)
    t = (xs - x0) / (x1 - x0)
    yc = y + sag * (1 - (2 * t - 1) ** 2)
    mid = np.column_stack([xs, yc])
    cv = G.Curve(mid)
    tt = np.linspace(0, 1, 120)
    C = cv.at(tt)
    N = -cv.normal(tt)            # screen 'down' side of the band
    top, bot = C - N * H / 2, C + N * H / 2
    front_pg = Polygon(np.vstack([top, bot[::-1]]))
    tails, backs, extra_lines = [], [], []
    for side in (-1, 1):
        k = 0 if side < 0 else -1
        T_end = cv.tangent(0.0 if side < 0 else 1.0) * (-1 if side < 0 else 1)   # outward
        Nn = N[k]
        e_top, e_bot = top[k], bot[k]
        if ends == "fold":
            inset = H * 0.45
            # tail strip: behind the front, dropped by dp along N, running outward
            b_top = e_top + Nn * dp - T_end * inset
            b_bot = e_bot + Nn * dp - T_end * inset
            o_top = e_top + Nn * dp + T_end * tl - Nn * lift
            o_bot = e_bot + Nn * dp + T_end * tl - Nn * lift
            notch = (o_top + o_bot) / 2 - T_end * (H * 0.4 if fork else 0.0)
            tail_poly = Polygon([b_top, o_top, notch, o_bot, b_bot]).buffer(0)
            # fold: the back face between the front's end edge and the tail start
            # the crease runs from the front's end corner to the tail's inner corner;
            # the triangle beyond it (under the front's edge) is the back face
            fold_poly = Polygon([e_bot, e_bot - T_end * inset, b_bot]).buffer(0)
            fold_poly = fold_poly.difference(front_pg)
            tail_vis = tail_poly.difference(front_pg).difference(fold_poly)
            if not tail_vis.is_empty:
                tails.append(tail_vis)
            if not fold_poly.is_empty:
                backs.append(fold_poly)
        else:
            # rolled end: the band curls back under itself into a scroll
            from .scrollwork import volute
            c0 = C[k]
            hd = math.degrees(math.atan2(T_end[1], T_end[0]))
            cw = side > 0
            roll = volute(c0, hd, H * 1.5, 0.95, cw=cw, tighten=2.2, entry=0.1)
            rv = G.to_shape(stroke(roll, H, lambda u: 1 - 0.55 * np.clip(u, 0, 1), cap="round"))
            tails.append(rv.difference(front_pg))
            extra_lines.append((roll[int(len(roll) * 0.35):], False))
    front_d = G.from_shape(front_pg)
    tails_d = "".join(G.from_shape(tp) for tp in tails)
    back_d = "".join(G.from_shape(bp) for bp in backs)
    sil = shapely.union_all([front_pg] + tails + backs)
    lines = [(np.asarray(front_pg.exterior.coords)[:-1], True)]
    for gm in tails + backs:
        for pg in getattr(gm, "geoms", [gm]):
            if pg.geom_type == "Polygon" and not pg.is_empty:
                lines.append((np.asarray(pg.exterior.coords)[:-1], True))
    # clip every outline to what is actually visible (front on top)
    vis_lines = []
    for pts, closed in lines[1:] + extra_lines:
        seg = G.clip_out([(pts, closed)], front_pg.buffer(-0.01))
        vis_lines += [(p, False) for p, _ in G.as_polys(seg)]
    vis_lines.insert(0, lines[0])
    return {"front": front_d, "tails": tails_d, "back": back_d, "silhouette": G.from_shape(sil),
            "lines": _emit(vis_lines, lw), "path": G.poly_d(mid)}
