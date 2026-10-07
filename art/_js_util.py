"""art/_js_util.py — small compass helpers shared by the J♠ modules (open
arc splines, regions from spline runs, tapered ribbons, line strokes)."""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM


def largest(g):
    ps = K._polys_of(g.buffer(0)) if g is not None and not g.is_empty else []
    return max(ps, key=lambda p: p.area) if ps else Polygon()


def lines_in(g, min_len=4.0):
    """The LineStrings of any geometry (merged), longer than min_len."""
    if g is None or g.is_empty:
        return []
    if g.geom_type == "MultiLineString":
        g = shapely.line_merge(g)
    return [ln for ln in K._lines_of(g) if ln.length >= min_len]


def stroke_lines(g, w, *, role="", color=K.INK, style="ornament", min_len=4.0):
    """Stroke every line of a (clipped) geometry."""
    f = C.Frag()
    for ln in lines_in(g, min_len):
        f += C.stroke(np.asarray(ln.coords), w, style=style, color=color, role=role)
    return f


def open_spline(points, headings=None, h_start=None, h_end=None):
    """Open G1 arc spline → (d, dense points)."""
    d, pts, _ = FM.arc_spline([K.P(p) for p in points], h_start, h_end, headings=headings or {})
    return d, np.asarray(pts, float)


def region_of(*runs):
    """A closed region from consecutive runs: each run is a list of points
    (a smooth open spline through them) or ('L', [p0, p1, ...]) (straight
    segments). Runs must join end to start. → shapely."""
    pts = []
    for r in runs:
        if isinstance(r, tuple) and r[0] == "L":
            seg = [K.P(p) for p in r[1]]
            pts.extend(seg if not pts else seg[1:])
        else:
            _, sp = open_spline(r)
            pts.extend(list(sp) if not pts else list(sp[1:]))
    return Polygon(np.asarray(pts)).buffer(0)


def ribbon(guide, hw_fn, *, tip_round=0.0, root_round=0.0):
    """A ribbon region of half-width hw_fn(t) (t 0..1) along a dense guide.
    → (region, left edge, right edge, guide pts) (left = screen-left of travel)."""
    gp = np.asarray(guide, float)
    cv = K.G.Curve(gp)
    L = cv.length
    ss = np.linspace(0, L, max(60, int(L / 0.8)))
    tt = ss / L
    pts = np.array([cv.at_s(s_) for s_ in ss])
    tang = np.gradient(pts, axis=0)
    tang /= np.hypot(*tang.T)[:, None]
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
    hw = np.array([hw_fn(t) for t in tt])
    left = pts + nrm * hw[:, None]
    right = pts - nrm * hw[:, None]
    parts = [Polygon(np.vstack([left, right[::-1]])).buffer(0)]
    if tip_round:
        parts.append(Point(*pts[-1]).buffer(tip_round, quad_segs=16))
    if root_round:
        parts.append(Point(*pts[0]).buffer(root_round, quad_segs=16))
    reg = largest(shapely.union_all(parts).buffer(0.6, quad_segs=8).buffer(-0.6, quad_segs=8))
    return reg, left, right, pts


def pocket(a, others, *, near=None, r=5.0, max_area=120.0):
    """The small ground pockets (narrower than 2 r) enclosed between region
    ``a`` and the ``others`` — the fleck of background a heel, a cuff and a
    rope leave between them — that touch ``a`` and ``near`` (default: any of
    the others), each smaller than ``max_area``. → region (maybe empty)."""
    allr = shapely.union_all([a] + list(others))
    gap = allr.buffer(r, quad_segs=12).buffer(-r, quad_segs=12).difference(allr)
    nr = shapely.union_all(list(others)) if near is None else near
    keep = [g for g in K._polys_of(gap) if g.area < max_area and g.distance(a) < 0.3 and g.distance(nr) < 0.3
            and not g.buffer(-0.05).is_empty]
    return shapely.union_all(keep) if keep else Polygon()


def drop_short(f, min_len=9.0):
    """Remove stroke pieces shorter than ``min_len`` (the stubs a hatch leaves in a pocket)."""
    from dataclasses import replace
    from inkkit import geom as G
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d:
            out.append(m)
            continue
        d = "".join(C.polyline_d(pts, closed=cl) for pts, cl in G.flatten(m.d, 0.05)
                    if G.Curve(np.asarray(pts), closed=cl).length >= min_len)
        if d:
            out.append(replace(m, d=d))
    return C.Frag(out, f.meta)
