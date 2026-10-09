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


def drop_lone_short(f, min_len=9.0, touch=0.6):
    """``drop_short`` for a lattice: a piece shorter than ``min_len`` is removed only when neither of its
    ends meets another piece (a stub in a pocket). A short piece that runs from a cusp to the region's
    edge stays, or the lattice ends in open field a few px short of that edge."""
    from dataclasses import replace
    from inkkit import geom as G
    from shapely.strtree import STRtree
    subs = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d:
            continue
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts, float)
            if len(pts) >= 2:
                subs.append((i, pts, cl, shapely.LineString(pts)))
    tree = STRtree([s[3] for s in subs])
    keep = {}
    for k, (i, pts, cl, ln) in enumerate(subs):
        ok = ln.length >= min_len
        if not ok and not cl:
            for end in (pts[0], pts[-1]):
                q = Point(*end)
                if any(j != k and subs[j][3].distance(q) < touch for j in tree.query(q.buffer(touch))):
                    ok = True
                    break
        if ok:
            keep.setdefault(i, []).append(C.polyline_d(pts, closed=cl))
    out = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d:
            out.append(m)
        elif i in keep:
            out.append(replace(m, d="".join(keep[i])))
    return C.Frag(out, f.meta)


def _ink_lines(f):
    """(LineString, half width) of every ink stroke sub-path of ``f``."""
    from inkkit import geom as G
    out = []
    for i, m in enumerate(f.marks):
        if m.kind != "stroke" or not m.d or m.layer != "ink":
            continue
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts, float)
            if len(pts) >= 2:
                out.append((i, shapely.LineString(np.vstack([pts, pts[:1]]) if cl else pts), m.w / 2))
    return out


def extend_free_ends(f, select, *, zone=None, reach=8.0, back=1.5, ignore=(), bury=None):
    """Run a selected stroke's free end (one that touches no other ink) straight on, along its last
    ``back`` px, to the centre line of the first ink stroke it meets within ``reach`` px: a hatch or
    cuff line the heal cut back so it stops short of the line it belonged against. Only ends inside
    ``zone`` (when given) move; strokes whose role is in ``ignore`` neither hold an end nor stop it.
    ``bury``: an end only counts as held when it lies this far inside the other stroke's edge (a
    round cap that just meets a line's edge leaves a notch at the corner). → Frag."""
    from dataclasses import replace
    from inkkit import geom as G
    from shapely.strtree import STRtree
    ink = [t for t in _ink_lines(f) if f.marks[t[0]].role not in ignore]
    tree = STRtree([g for _, g, _ in ink])
    zp = shapely.prepared.prep(zone) if zone is not None else None
    out = []
    for i, m in enumerate(f.marks):
        if m.kind != "stroke" or not m.d or not select(m):
            out.append(m)
            continue
        changed, subs = False, []
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts, float)
            if cl or len(pts) < 2:
                subs.append(C.polyline_d(pts, closed=cl))
                continue
            me = shapely.LineString(pts)
            for end in (0, -1):
                p = pts[end]
                q = Point(*p)
                if zp is not None and not zp.contains(q):
                    continue
                near = [ink[j] for j in tree.query(q.buffer(reach + 4.0))]
                hold = (lambda hw: hw - bury) if bury is not None else (lambda hw: hw + m.w / 2 + 0.3)
                if any(g.distance(q) < hold(hw) for k, g, hw in near if not (k == i and g.equals(me))):
                    continue
                inner = me.interpolate(back if end == 0 else me.length - back)
                u = p - np.array(inner.coords[0])
                if np.hypot(*u) < 1e-6:
                    continue
                u = u / np.hypot(*u)
                ray = shapely.LineString([p, p + u * reach])
                best = None
                for k, g, hw in near:
                    if k == i and g.equals(me):
                        continue
                    hit = ray.intersection(g)
                    for h in getattr(hit, "geoms", [hit]):
                        if h.is_empty or h.geom_type != "Point":
                            continue
                        dd = q.distance(h)
                        if best is None or dd < best[0]:
                            best = (dd, np.array(h.coords[0]))
                if best is not None:
                    pts = np.vstack([best[1], pts]) if end == 0 else np.vstack([pts, best[1]])
                    me = shapely.LineString(pts)
                    changed = True
            subs.append(C.polyline_d(pts))
        out.append(replace(m, d="".join(subs)) if changed else m)
    return C.Frag(out, f.meta)


def drop_short_where(f, select, zone, min_len, *, horizontal=False):
    """Remove the sub-paths of selected strokes shorter than ``min_len`` that lie in ``zone``
    (``horizontal``: only level ones). → Frag."""
    from dataclasses import replace
    from inkkit import geom as G
    zp = shapely.prepared.prep(zone)
    out = []
    for m in f.marks:
        if m.kind != "stroke" or not m.d or not select(m):
            out.append(m)
            continue
        subs, changed = [], False
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts, float)
            ln = shapely.LineString(pts) if len(pts) >= 2 else None
            if (ln is not None and not cl and ln.length < min_len and zp.contains(ln)
                    and (not horizontal or abs(pts[-1][1] - pts[0][1]) < 0.3)):
                changed = True
                continue
            subs.append(C.polyline_d(pts, closed=cl))
        if not changed:
            out.append(m)
        elif subs:
            out.append(replace(m, d="".join(subs)))
    return C.Frag(out, f.meta)


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


def drop_alongside(f, select, edge, gap, *, slope=0.5, step=0.5, min_len=3.0, min_run=6.0):
    """Remove the runs of selected strokes that close on ``edge`` (a line geometry) at a shallow angle:
    every stretch within ``gap`` px of it, at least ``min_run`` px long, whose distance changes by less
    than ``slope`` per px of run.
    Such a line meets the edge in a long taper of ground between the two, too thin to print and too
    long for the heal's knockout cut to clear; a line crossing the edge steeply keeps its join.
    Pieces left shorter than ``min_len`` go too. → Frag."""
    from dataclasses import replace
    import shapely.ops
    from inkkit import geom as G
    ep = shapely.prepared.prep(edge.buffer(gap + 2.0))
    out = []
    for m in f.marks:
        if m.kind != "stroke" or not m.d or not select(m):
            out.append(m)
            continue
        subs, changed = [], False
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts, float)
            ln = shapely.LineString(pts) if len(pts) >= 2 else None
            if ln is None or cl or not ep.intersects(ln):
                subs.append(C.polyline_d(pts, closed=cl))
                continue
            n = max(2, int(np.ceil(ln.length / step)) + 1)
            s = np.linspace(0.0, ln.length, n)
            q = np.array([ln.interpolate(v).coords[0] for v in s])
            dist = shapely.distance(shapely.points(q), edge)
            # one-sided: where the line crosses the edge the distance has a V-shaped minimum
            dd = np.abs(np.diff(dist)) / np.diff(s)
            rate = np.minimum(np.r_[dd[:1], dd], np.r_[dd, dd[-1:]])
            bad = (dist < gap) & (rate < slope)
            if bad.sum() * step < min_run:
                subs.append(C.polyline_d(pts, closed=cl))
                continue
            changed = True
            # a run counts from where it first comes within ``gap``, so its end clears the edge
            near = dist < gap
            lab = np.cumsum(np.r_[0, np.diff(near.astype(int)) != 0])
            drop = np.zeros(n, bool)
            for k in np.unique(lab[bad]):
                drop |= lab == k
            keep = ~drop
            runs = np.split(np.arange(n), np.where(np.diff(keep.astype(int)) != 0)[0] + 1)
            for r in runs:
                if keep[r[0]] and s[r[-1]] - s[r[0]] >= min_len:
                    piece = shapely.ops.substring(ln, s[r[0]], s[r[-1]])
                    subs.append(C.polyline_d(np.asarray(piece.coords)))
        if not changed:
            out.append(m)
        elif subs:
            out.append(replace(m, d="".join(subs)))
    return C.Frag(out, f.meta)


def trim_overshoot(f, select, *, reach=1.6, skip=("hatch", "scale", "lay")):
    """Cut a selected stroke's end back to where it crosses another ink stroke's centre line, when
    that crossing lies within ``reach`` px of the end: an end run past the line it stops on shows
    its round cap as a knob on the line's far side. Strokes whose role is in ``skip`` (pattern
    marks that start on the line) are not lines to stop on. → Frag."""
    from dataclasses import replace
    import shapely.ops
    from inkkit import geom as G
    from shapely.strtree import STRtree
    ink = [t for t in _ink_lines(f) if f.marks[t[0]].role not in skip]
    tree = STRtree([g for _, g, _ in ink])
    out = []
    for i, m in enumerate(f.marks):
        if m.kind != "stroke" or not m.d or not select(m):
            out.append(m)
            continue
        changed, subs = False, []
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts, float)
            if cl or len(pts) < 2:
                subs.append(C.polyline_d(pts, closed=cl))
                continue
            me = shapely.LineString(pts)
            a, b = 0.0, me.length
            for end in (0, -1):
                tip = me.interpolate(0.0 if end == 0 else me.length)
                cut = None
                for k in tree.query(tip.buffer(reach)):
                    j, g, _ = ink[k]
                    if j == i and g.equals(me):
                        continue
                    hit = me.intersection(g)
                    for h in getattr(hit, "geoms", [hit]):
                        if h.is_empty or h.geom_type != "Point":
                            continue
                        s = me.project(h)
                        run = s if end == 0 else me.length - s
                        if 0.05 < run <= reach and (cut is None or run < cut[0]):
                            cut = (run, s)
                if cut is not None:
                    if end == 0:
                        a = cut[1]
                    else:
                        b = cut[1]
            if (a, b) != (0.0, me.length) and b - a > 1.0:
                changed = True
                pts = np.asarray(shapely.ops.substring(me, a, b).coords)
            subs.append(C.polyline_d(pts))
        out.append(replace(m, d="".join(subs)) if changed else m)
    return C.Frag(out, f.meta)
