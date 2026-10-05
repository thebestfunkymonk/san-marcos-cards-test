"""Radiance: sunbursts with tapered spikes, fans, faceted starbursts, fleurons.

Angles are screen degrees (0 = +x, -90 = up). All return FILL d unless noted;
these generators are FILL-only (``lw=None`` is rejected with a clear error),
except :func:`fan`, which can return STROKE parts.
"""
from __future__ import annotations

import math

import numpy as np
import shapely

from .. import geom as G
from .. import tokens as T
from ..stroke import STYLES, styled
from .scrollwork import _render, curl, flourish

__all__ = ["sunburst", "fan", "starburst", "fleuron"]


def _need_lw(name, lw):
    if lw is None:
        raise ValueError(f"{name} is FILL-only: pass a line width (lw=<px>), not lw=None")
    if not lw > 0:
        raise ValueError(f"{name}: lw must be > 0, got {lw!r}")


def _angles(n, rot, arc):
    if arc is None:
        return rot + 360.0 * np.arange(n) / n
    a0, a1 = arc
    return np.linspace(a0, a1, n)


def sunburst(cx: float, cy: float, r_in: float, r_out: float, n: int = 36, *,
             lengths=(1.0, 0.72), base_width: float | None = None, style: str = "spike",
             rot: float = -90.0, arc=None, concave: float = 1.25, lw: float = 1.2,
             min_width: float | None = None) -> str:
    """Rays from r_in outwards. ``lengths`` cycles relative ray lengths
    (long/short rhythm). style:
    'spike'  solid tapered spikes with slightly concave flanks (``concave`` >1)
    'line'   hairline rays tapering to a point (width ``lw``)
    'wedge'  alternate solid wedges (sunrise / Japanese flag)
    ``arc``=(a0, a1) limits rays to a fan. Tips end in a round cap of
    ``min_width`` (default the print minimum). -> FILL d."""
    if n < 1:
        raise ValueError("sunburst: n must be >= 1")
    if style not in ("spike", "line", "wedge"):
        raise ValueError(f"sunburst style must be 'spike', 'line' or 'wedge', not {style!r}")
    if style == "line":
        _need_lw("sunburst(style='line')", lw)
    mw = T.MIN_LINE if min_width is None else min_width
    A = _angles(n, rot, arc)
    out = []
    if style == "wedge":
        step = (A[1] - A[0]) if len(A) > 1 else 360.0 / n
        for k, a in enumerate(A):
            if k % 2:
                continue
            L = r_in + (r_out - r_in) * lengths[k // 2 % len(lengths)]
            a0, a1 = a - step / 2, a + step / 2
            outer = G.arc_pts(cx, cy, L, a0, a1)
            inner = G.arc_pts(cx, cy, r_in, a1, a0) if r_in > 0 else np.array([[cx, cy]])
            out.append(G.poly_d(np.vstack([outer, inner]), True, orient="cw"))
        return "".join(out)
    bw = base_width if base_width is not None else 2 * math.pi * max(r_in, 1) / n * 0.55
    for k, a in enumerate(A):
        L = r_in + (r_out - r_in) * lengths[k % len(lengths)]
        u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        p0 = np.array([cx, cy]) + u * r_in
        p1 = np.array([cx, cy]) + u * L
        if style == "spike":
            out.append(styled(np.array([p0, p1]), bw, lambda t: (1 - np.clip(t, 0, 1)) ** concave,
                              cap="flat", end_cap="round", min_width=mw))
        else:
            out.append(styled(np.array([p0, p1]), lw, "taper-end", taper=0.5, min_width=mw))
    return "".join(out)


def fan(cx: float, cy: float, r: float, a0: float = 180.0, a1: float = 270.0, n: int = 9, *,
        r_in: float = 0.0, rims=(1.0,), lw: float | None = 1.2, hub: float | None = None,
        parts: bool = False):
    """Deco fan (Monarchs-style corner sunburst): straight rays between a0 and
    a1 plus concentric rim arcs at the given relative radii and an optional
    solid hub. -> FILL d. With ``lw=None`` the line work is STROKE and the
    solid hub FILL, so it must be requested as ``parts=True``
    -> {'stroke': d, 'fill': d} (``parts`` also works with a numeric lw)."""
    if n < 1:
        raise ValueError("fan: n must be >= 1")
    lines = []
    for a in np.linspace(a0, a1, n):
        u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        lines.append((np.array([np.array([cx, cy]) + u * max(r_in, hub or 0), np.array([cx, cy]) + u * r]), False))
    for rr in rims:
        lines.append((G.arc_pts(cx, cy, r * rr, a0, a1), False))
    if r_in > 0:
        lines.append((G.arc_pts(cx, cy, r_in, a0, a1), False))
    hub_d = G.poly_d(np.vstack([[[cx, cy]], G.arc_pts(cx, cy, hub, a0, a1)]), True, orient="cw") if hub else ""
    if lw is None:
        if hub and not parts:
            raise ValueError("fan(lw=None) mixes STROKE rays with a FILL hub: pass parts=True "
                             "(or hub=None, or a numeric lw)")
        st = G.polys_d(lines)
        return {"stroke": st, "fill": hub_d} if parts else st
    body = G.outline(lines, lw)
    if parts:
        return {"stroke": "", "fill": body + hub_d}
    return body + hub_d


def starburst(cx: float, cy: float, r_out: float, r_in: float | None = None, points: int = 8, *,
              rot: float = -90.0, facets: bool = True, layers: int = 1, layer_scale: float = 0.62,
              lw: float = 1.0) -> str:
    """Faceted (engraved compass) star. Each point is split along its axis:
    one half solid, the other outlined — reads as a bevelled 3-D star.
    ``layers`` >1 adds smaller stars rotated half a step behind (each layer
    knocks a paper gap out of the one behind it). -> FILL d."""
    if points < 2:
        raise ValueError("starburst: points must be >= 2")
    _need_lw("starburst", lw)
    r_in = r_in if r_in is not None else r_out * 0.4
    out = []
    for L in range(layers):
        ro = r_out * (layer_scale ** L)
        ri = r_in * (layer_scale ** L)
        rt = rot + (180.0 / points) * L
        tips, vals = [], []
        for k in range(points):
            a = math.radians(rt + 360.0 * k / points)
            tips.append((cx + ro * math.cos(a), cy + ro * math.sin(a)))
            b = math.radians(rt + 360.0 * (k + 0.5) / points)
            vals.append((cx + ri * math.cos(b), cy + ri * math.sin(b)))
        star = []
        for k in range(points):
            star += [tips[k], vals[k]]
        star = np.array(star)
        star_pg = shapely.Polygon(star)
        if facets:
            outline = shapely.LinearRing(star).buffer(lw / 2, join_style="mitre", mitre_limit=10)
            solid = shapely.union_all([shapely.Polygon([(cx, cy), tips[k], vals[k]]) for k in range(points)])
            # grow the facets by lw/2 inside the star so they meet the outline
            # without nicks at the valley vertices
            solid = solid.buffer(lw / 2, join_style="mitre", mitre_limit=10).intersection(
                star_pg.buffer(lw / 2, join_style="mitre", mitre_limit=10))
            axes = shapely.union_all([shapely.LineString([(cx, cy), vals[k - 1]]).buffer(lw * 0.4, cap_style="flat")
                                      for k in range(points)])
            gm = shapely.union_all([outline, solid, axes])
            out.append((G.from_shape(gm), star_pg.buffer(lw * 1.5, join_style="mitre", mitre_limit=10)))
        else:
            out.append((G.poly_d(star, True, orient="cw"), star_pg.buffer(lw * 1.5)))
    if layers == 1:
        return out[0][0]
    # draw back to front: each nearer layer knocks a paper gap out of those behind
    res = ""
    for k in range(len(out) - 1, -1, -1):
        d_k = out[k][0]
        nearer = [out[j][1] for j in range(k)]
        if nearer:
            d_k = G.difference(d_k, G.from_shape(shapely.union_all(nearer)))
        res += d_k
    return res


# =============================================================================
# fleurons
# =============================================================================
def _lance(base, tip, width, prof_pow=(0.62, 0.8)):
    """Solid lanceolate petal from base to tip (pointed tip, rounded belly)."""
    base = np.asarray(base, float); tip = np.asarray(tip, float)
    t = np.linspace(0, 1, 90)
    P = base + np.outer(t, tip - base)
    d = (tip - base) / max(np.hypot(*(tip - base)), 1e-9)
    nrm = np.array([-d[1], d[0]])
    w = 0.5 * width * np.sin(np.pi * t ** prof_pow[0]) ** prof_pow[1]
    w[0] = max(w[0], 0.18 * width)
    poly = np.vstack([P + np.outer(w, nrm), (P - np.outer(w, nrm))[::-1]])
    return G.poly_d(poly, True, orient="cw")


def fleuron(cx: float, cy: float, size: float = 40.0, *, style: str = "lily", rot: float = 0.0,
            width: float | None = None, line_style: str = "taper", lw: float | None = None,
            min_width: float | None = None) -> str:
    """Bilaterally symmetric ornament centred at (cx, cy), pointing up (rotate
    with ``rot`` degrees). styles:

    'lily'      fleur-de-lis: lance petal, two side petals that rise and roll
                outward into volutes, a collar band and a three-lobed foot
    'palmette'  fan of five lanceolate lobes over a pair of base volutes
    'heart'     hedera (ivy-leaf) with a curled stem
    'scroll'    lyre: twin C-scrolls rolling outward round a lance

    ``line_style`` ('taper' | 'monoline' | 'outline' | 'inline') styles the
    scroll strokes. -> FILL d."""
    if style not in ("lily", "palmette", "heart", "scroll"):
        raise ValueError(f"fleuron style must be lily|palmette|heart|scroll, not {style!r}")
    if line_style not in STYLES:
        raise ValueError(f"line_style must be one of {STYLES}")
    if not size > 0:
        raise ValueError("fleuron: size must be > 0")
    if line_style == "outline":
        solid = fleuron(0, 0, size, style=style, width=width, line_style="taper", min_width=min_width)
        d = G.outline(solid, lw if lw is not None else T.MIN_LINE)
        return G.translate(G.rotate(d, rot) if rot else d, cx, cy)
    S = size
    w = width if width is not None else S / 14
    mw = T.MIN_LINE if min_width is None else min_width
    parts = []
    mirror = []
    if style == "lily":
        parts.append(_lance((0, S * 0.02), (0, -S * 0.52), S * 0.22))
        # side petal: rises from the collar, bows outward, rolls down and out
        pts = np.array([[S * 0.05, S * 0.02], [S * 0.12, -S * 0.12], [S * 0.25, -S * 0.24],
                        [S * 0.37, -S * 0.17]])
        v = flourish(pts, end_turns=1.0, end_size=S * 0.2, end_cw=True, tighten=2.2)
        prof = lambda t: 0.28 + 0.72 * (1 - np.clip(t, 0, 1)) ** 1.1
        mirror.append(_render(v, w * 1.35, prof, style=line_style, lw=lw, min_width=mw,
                              terminal="ball", terminal_r=w * 0.6))
        # foot: small curls under the collar
        fpts = np.array([[S * 0.03, S * 0.1], [S * 0.1, S * 0.19], [S * 0.2, S * 0.22]])
        fv = flourish(fpts, end_turns=0.9, end_size=S * 0.11, end_cw=False, tighten=2.3)
        mirror.append(_render(fv, w * 0.9, "taper-end", style=line_style, lw=lw, min_width=mw,
                              terminal="ball", terminal_r=w * 0.45, taper=0.9))
        parts.append(_lance((0, S * 0.08), (0, S * 0.32), S * 0.09, (0.9, 0.9)))
        parts.append(G.rect_d(-S * 0.16, S * 0.02, S * 0.32, S * 0.07, S * 0.03))
    elif style == "palmette":
        base = np.array([0.0, S * 0.2])
        for ang, L, wid in ((-90, 0.68, 0.15), (-64, 0.56, 0.13), (-40, 0.44, 0.11)):
            a = math.radians(ang)
            tip = base + np.array([math.cos(a), math.sin(a)]) * S * L
            d = _lance(base, tip, S * wid)
            (parts if ang == -90 else mirror).append(d)
        # base: a pair of volutes rolling outward and down (Ionic cup)
        pts = np.array([[0.0, S * 0.27], [S * 0.14, S * 0.23], [S * 0.28, S * 0.22]])
        v = flourish(pts, end_turns=1.0, end_size=S * 0.14, end_cw=True, tighten=2.2)
        mirror.append(_render(v, w * 1.1, lambda t: 1 - 0.65 * np.clip(t, 0, 1), style=line_style,
                              lw=lw, min_width=mw, terminal="ball", terminal_r=w * 0.55))
        parts.append(G.ellipse_d(0, S * 0.24, S * 0.06, S * 0.045))
    elif style == "heart":
        t = np.linspace(0, 2 * math.pi, 240)
        x = 16 * np.sin(t) ** 3
        y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
        heart = np.column_stack([x, -y]) * (S / 34.0)
        heart[:, 1] -= S * 0.05
        notch = float(heart[0, 1])
        parts.append(G.poly_d(heart, True, orient="cw"))
        stem = curl((0, notch - S * 0.04), 90, S * 0.55, 0.42, 3.0, 0.0, cw=True)
        parts.append(styled(stem, w * 1.1, "taper-end", taper=0.7, min_width=mw))
        vein = np.array([[0, notch - S * 0.02], [0, -S * 0.4]])
        cut = styled(vein, max(w * 0.5, T.MIN_REVERSED), "taper-end", taper=0.85,
                     min_width=T.MIN_REVERSED * 0.8)
        return G.translate(G.rotate(G.difference(G.union(*parts), cut), rot), cx, cy)
    else:  # scroll / lyre
        pts = np.array([[0, S * 0.34], [S * 0.12, S * 0.12], [S * 0.13, -S * 0.12], [S * 0.2, -S * 0.3]])
        v = flourish(pts, end_turns=1.1, end_size=S * 0.2, end_cw=True, tighten=2.2)
        mirror.append(_render(v, w * 0.95, lambda t: 0.35 + 0.65 * np.sin(np.pi * np.clip(t, 0, 1) ** 0.8),
                              style=line_style, lw=lw, min_width=mw, terminal="ball",
                              terminal_r=w * 0.6))
        parts.append(_lance((0, S * 0.1), (0, -S * 0.42), S * 0.13))
        parts.append(styled(np.array([[0, S * 0.3], [0, S * 0.5]]), w * 1.7, "teardrop-rev",
                            min_width=mw))
    for d in mirror:
        parts += [d, G.mirror_x(d, 0)]
    d = G.union(*parts)
    if rot:
        d = G.rotate(d, rot)
    return G.translate(d, cx, cy)
