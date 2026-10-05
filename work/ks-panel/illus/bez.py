"""Illustrator's pen: hand-placed cubic Béziers from on-curve knots + tangents.

The way a human draws in Illustrator: put an anchor where the line must pass,
drag its handle along the direction the line travels there. This module
turns that into path data, and nothing is automatic beyond one rule —
a handle length left as ``None`` is one third of the chord to the neighbour
(times ``tension``), which gives the fullest curve that never overshoots.

    K(x, y, a)              smooth knot, travel direction a (screen degrees:
                            0 = +x → right, 90 = +y ↓ down)
    K(x, y, a, li, lo)      ... with explicit in / out handle lengths
    K(x, y, ai=.., ao=..)   corner knot: different in / out directions
    K(x, y)                 corner knot with straight (line-like) handles

    path(knots, closed)     → SVG d (M … C … [Z])
    sym(half)               → closed outline symmetric about x = AXIS from the
                              LEFT half, authored top-on-axis → bottom-on-axis
    mirror(knots), rev(knots), shift(knots, dx, dy)

Tangent continuity is by construction: a smooth knot has one direction for
both handles. Nothing here scales anything; everything is at final size.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Sequence

import numpy as np

AXIS = 375.0


@dataclass(frozen=True)
class K:
    x: float
    y: float
    a: float | None = None      # smooth direction (deg); sets ai = ao = a
    li: float | None = None     # in-handle length (None → chord/3)
    lo: float | None = None     # out-handle length (None → chord/3)
    ai: float | None = None     # corner: incoming travel direction
    ao: float | None = None     # corner: outgoing travel direction
    t: float = 1.0              # tension multiplier for auto lengths

    @property
    def p(self) -> np.ndarray:
        return np.array([self.x, self.y], float)

    def din(self):
        return self.ai if self.ai is not None else self.a

    def dout(self):
        return self.ao if self.ao is not None else self.a


def _u(deg: float) -> np.ndarray:
    r = math.radians(deg)
    return np.array([math.cos(r), math.sin(r)])


def _fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _seg(k0: K, k1: K) -> tuple[np.ndarray, np.ndarray]:
    """Control points for the cubic from k0 to k1."""
    p0, p3 = k0.p, k1.p
    chord = float(np.hypot(*(p3 - p0)))
    do, di = k0.dout(), k1.din()
    if do is None:
        c1 = p0 + (p3 - p0) / 3.0 if di is None else p0 + (p3 - p0) / 3.0
    else:
        L = k0.lo if k0.lo is not None else chord / 3.0 * k0.t
        c1 = p0 + _u(do) * L
    if di is None:
        c2 = p3 - (p3 - p0) / 3.0
    else:
        L = k1.li if k1.li is not None else chord / 3.0 * k1.t
        c2 = p3 - _u(di) * L
    return c1, c2


def path(knots: Sequence[K], closed: bool = False) -> str:
    ks = list(knots)
    if len(ks) < 2:
        return ""
    out = [f"M{_fmt(ks[0].x)} {_fmt(ks[0].y)}"]
    pairs = list(zip(ks[:-1], ks[1:])) + ([(ks[-1], ks[0])] if closed else [])
    for a, b in pairs:
        c1, c2 = _seg(a, b)
        out.append("C" + " ".join(_fmt(v) for v in (*c1, *c2, b.x, b.y)))
    if closed:
        out.append("Z")
    return "".join(out)


def pts(knots: Sequence[K], closed: bool = False, step: float = 1.0) -> np.ndarray:
    """Flattened points of the path (for guides, offsets, strip maps)."""
    ks = list(knots)
    pairs = list(zip(ks[:-1], ks[1:])) + ([(ks[-1], ks[0])] if closed else [])
    res = [ks[0].p]
    for a, b in pairs:
        c1, c2 = _seg(a, b)
        p0, p3 = a.p, b.p
        L = np.hypot(*(c1 - p0)) + np.hypot(*(c2 - c1)) + np.hypot(*(p3 - c2))
        n = max(4, int(L / step))
        t = np.linspace(0, 1, n + 1)[1:, None]
        res.append((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t * t * c2 + t ** 3 * p3)
    return np.vstack(res)


# ---------------------------------------------------------------------------
# knot-list transforms
# ---------------------------------------------------------------------------
def _flip(a):
    return None if a is None else (a + 180.0) % 360.0


def rev(knots: Sequence[K]) -> list[K]:
    """Same curve traversed backwards."""
    out = []
    for k in reversed(list(knots)):
        out.append(replace(k, a=_flip(k.a), ai=_flip(k.ao), ao=_flip(k.ai), li=k.lo, lo=k.li))
    return out


def _mir(a):
    return None if a is None else (180.0 - a) % 360.0


def mirror(knots: Sequence[K], axis: float = AXIS) -> list[K]:
    """Mirror about x = axis (directions reflect: a → 180 − a)."""
    return [replace(k, x=2 * axis - k.x, a=_mir(k.a), ai=_mir(k.ai), ao=_mir(k.ao)) for k in knots]


def shift(knots: Sequence[K], dx: float = 0.0, dy: float = 0.0) -> list[K]:
    return [replace(k, x=k.x + dx, y=k.y + dy) for k in knots]


def sym(half: Sequence[K], axis: float = AXIS) -> str:
    """Closed outline, bilaterally symmetric about x = axis. ``half`` is the
    LEFT half drawn from the top knot ON the axis, down the left side, to the
    bottom knot ON the axis. An on-axis knot is smooth if its direction is
    perpendicular to the axis (a = 180 at the top, 0 at the bottom), else a
    symmetric corner (peak, chin point, notch)."""
    h = list(half)
    m = rev(mirror(h, axis))
    n = len(h)
    body = h + m[1:-1]
    body[n - 1] = replace(h[-1], ao=m[0].dout(), lo=m[0].lo, a=None, ai=h[-1].din())
    body[0] = replace(h[0], ai=m[-1].din(), li=m[-1].li, a=None, ao=h[0].dout())
    return path(body, closed=True)


def open_sym(half: Sequence[K], axis: float = AXIS) -> str:
    """Open stroke symmetric about the axis: ``half`` runs from the LEFT end
    to a knot ON the axis; the mirror continues to the right end. The axis
    knot is smooth if horizontal (a = 0), else a symmetric corner."""
    h = list(half)
    m = rev(mirror(h, axis))
    mid = replace(h[-1], a=None, ai=h[-1].din(), ao=m[0].dout(), lo=m[0].lo)
    return path(h[:-1] + [mid] + m[1:])


def arcish(p0, p1, bulge: float) -> list[K]:
    """Two knots making a single smooth arc-like bow from p0 to p1; ``bulge``
    is the sagitta (px, + = to the left of travel on screen)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    ang = math.degrees(math.atan2(d[1], d[0]))
    L = float(np.hypot(*d))
    # tangent turn for a circular arc of that sagitta
    th = 2 * math.degrees(math.atan2(2 * bulge, L))
    h = 4.0 / 3.0 * math.tan(math.radians(th) / 2) * (L / 2) / max(abs(math.sin(math.radians(th))), 1e-9) \
        if abs(th) > 1e-6 else L / 3
    h = abs(h)
    return [K(*p0, ao=ang - th, lo=h), K(*p1, ai=ang + th, li=h)]
