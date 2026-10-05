"""art/_qc_gown.py — Q♣ · the current-streamed leaf gown (§H.8, §G.4).

§H.8: "Gown: jade, overlaid with ribbon leaves streaming diagonally with the
current. Each is a half-hatched vesica in Aquifer line."

A lattice clipped to the panel cuts most leaves into ladder-like strips (the
half-hatch of a 10 : 1 leaf is a row of short rungs; only the whole vesica
— both sharp tips, the S of the midrib — says "leaf"). So the textile is
PACKED instead: whole §G.4 ribbon leaves, all streaming the same way, placed
greedily across the stream wherever a whole leaf fits inside the panel (the
band may cut them: the band hides the cut, and the 180° copy continues the
stream), each ``gap`` px clear of its neighbours.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.prepared import prep

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM
from deck.motifs import rice as MR

import _qc_parts as Q

P, R, U = K.P, K.R, K.U
FINE_HW = K.FINE / 2


def _u(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def _spikes(base, heading, length, bend, reach=5.6):
    """the ends of a ribbon leaf's two miter tips (centreline tip + ``reach``
    along the midrib's end tangents)."""
    _, mid, _ = FM.arc_path(base[0], base[1], heading, [(length / 2, bend[0]), (length / 2, bend[1])])
    mid = np.asarray(mid, float)
    out = []
    for a, b in ((mid[0], mid[min(3, len(mid) - 1)]), (mid[-1], mid[max(-4, -len(mid))])):
        u = a - b
        n = float(np.hypot(*u))
        out.append(a + u / n * reach if n > 1e-9 else a)
    return out


def leaf_poly(base, heading, length, width, bend):
    """The outline polygon of a §G.4 ribbon leaf (cheap: no strokes)."""
    _, mid, _ = FM.arc_path(base[0], base[1], heading, [(length / 2, bend[0]), (length / 2, bend[1])])
    hw = FM.vesica_hw(length, width)
    _, _, ol = FM.leaf_edges(np.asarray(mid, float), hw, step=1.5)
    return Polygon(ol).buffer(0)


def _grazes(pg, vis, soft_r, r, max_area):
    """True when leaf ``pg`` (visible part ``vis``) meets the soft region at a grazing angle: the
    jade gap between the leaf and the object narrower than 2 r, or the leaf's visible part thinner
    than 2 r along the object's edge (its own tips excluded: they are away from the object) — any
    one such piece larger than ``max_area`` (the small wedges where an edge CROSSES the object's
    are not grazes)."""
    soft_r = soft_r.intersection(K.box(*pg.buffer(3 * r + 2.0).bounds))      # (local: fast)
    near = soft_r.buffer(r + 1.0)
    both = pg.union(soft_r)
    gap = both.buffer(r, quad_segs=8).buffer(-r, quad_segs=8).difference(both).intersection(pg.buffer(r + 1.0))
    thin = vis.difference(vis.buffer(-r, quad_segs=8).buffer(r, quad_segs=8)).intersection(near)
    big = [g.area for g in K._polys_of(gap)] + [g.area for g in K._polys_of(thin)]
    return max(big, default=0.0) > max_area


def leaf_pack(allowed, *, heading=60.0, lengths=(170.0, 140.0, 110.0), ratio=10.0, bend=(14.0, -14.0),
              gap=7.0, grid=4.0, origin=(375.0, 330.0), hatch=1, alt_bend=False, max_n=40, pref=None,
              soft=None, tip_clear=9.0, min_visible=0.5, tip_zone=None, min_piece=0.0, no_show=None,
              sliver=None, min_w=0.0, hide=None, hide_in=7.0, reverse_rows=False, max_pieces=2,
              min_piece_frac=0.0):
    """Greedy packing of whole ribbon leaves inside ``allowed``.

    Candidates sit on a ``grid`` lattice aligned with the stream (``heading``)
    and are visited row by row ACROSS the stream (so leaves line up in
    streaming files), upstream end first; at each the longest of ``lengths``
    whose whole outline fits in ``allowed`` and keeps ``gap`` px from every
    leaf already placed is taken. ``alt_bend`` flips the S of alternate files.
    A leaf passing under ``soft`` objects shows ≤ 2 pieces, together ≥
    ``min_visible`` of it, each ≥ ``min_piece`` px² (no mid-leaf sliver in a
    notch between a hand and its cuff), and no visible part of it inside
    ``no_show`` (e.g. the corners where a wrist meets its cuff). ``sliver`` = (r, max_area): a
    leaf whose edge runs into a soft object at a grazing angle — leaving a tapering jade sliver
    (narrower than 2 r) between its outline and the object's, or a thin taper of the leaf itself
    along the object's edge — is refused when that sliver exceeds ``max_area`` px². ``min_w``: the
    least leaf width (a short leaf is made wider rather than let fall below the width at which a
    §G.4 ribbon leaf keeps its midrib and half-hatch, rice.LEAF_FULL_MIN_W). ``hide``: a region
    (a sleeve — the arm is in front of the gown) under which ONE end of a leaf may run out of
    sight, its tip at least ``hide_in`` px inside it (never ending near its edge).
    ``reverse_rows``: visit the rows across the stream from the other side. ``min_piece_frac``:
    each visible piece of a leaf cut by an object is at least this fraction of the leaf (a tip
    poking out beside a cuff, or a hatched scrap, does not read as a leaf).
    → (Frag, list of (base, length, width, bend, polygon))."""
    reg = R(allowed)
    pr = prep(reg)
    # where a miter tip's end may lie: 3 px paper + the neighbour's half width
    pr_t = prep(R(tip_zone)) if tip_zone is not None else None
    u = _u(heading)
    v = np.array([-u[1], u[0]])
    o = P(origin)
    x0, y0, x1, y1 = reg.bounds
    corners = np.array([[x0, y0], [x1, y0], [x0, y1], [x1, y1]]) - o
    along = corners @ u
    across = corners @ v
    a_min, a_max = along.min() - max(lengths), along.max()
    c_min, c_max = across.min(), across.max()
    placed, polys = [], []
    occ = Polygon()
    soft_r = R(soft) if soft is not None else None
    soft_p = prep(soft_r.buffer(tip_clear)) if soft_r is not None else None
    soft_s = prep(soft_r.buffer(3.0 + K.MEDIUM / 2 + 0.3)) if (soft_r is not None and tip_zone is not None) else None
    hide_p = prep(R(hide).buffer(-hide_in)) if hide is not None else None

    def _hidden(q):
        return hide_p is not None and hide_p.contains(Point(*q))
    rows = np.arange(c_min, c_max + grid, grid)
    if reverse_rows:                        # start from the other side of the stream
        rows = rows[::-1]
    cols = np.arange(a_min, a_max + grid, grid)
    for L in lengths:                       # longest leaves first, everywhere
        for ri, c in enumerate(rows):
            for a in cols:
                base = o + u * a + v * c
                if not pr.contains(Point(*base)):
                    continue
                if not pr.contains(Point(*(base + u * L))) or not pr.contains(Point(*(base + u * L / 2))):
                    continue
                W = max(L / ratio, min_w)
                bd = bend
                if alt_bend and (int(round(c / grid)) // 6) % 2:
                    bd = (-bend[0], -bend[1])
                hid = [_hidden(base), _hidden(base + u * L)]
                if sum(hid) > 1:
                    continue
                if soft_p is not None and any(soft_p.contains(Point(*q)) and not h_
                                              for q, h_ in zip((base, base + u * L), hid)):
                    continue
                pg = leaf_poly(base, heading, L, W, bd)
                if not pr.contains(pg):
                    continue
                # the FINE outline's sharp miter tips reach ~5 px past the
                # centreline tips: they must stay 3 px clear too (§I.12 at the
                # seam and the opening)
                if pr_t is not None:
                    sp = _spikes(base, heading, L, bd)
                    if not all(pr_t.contains(Point(*q)) for q in sp):
                        continue
                    if soft_s is not None and any(soft_s.contains(Point(*q)) and not _hidden(q) for q in sp):
                        continue
                    if sum(_hidden(q) for q in sp) > 1:
                        continue
                if soft_r is not None and pg.intersects(soft_r):
                    vis = pg.difference(soft_r)
                    pcs = K._polys_of(vis)
                    if vis.area < min_visible * pg.area or len(pcs) > max_pieces:
                        continue
                    if min_piece and any(q.area < min_piece for q in pcs):
                        continue
                    if min_piece_frac and any(q.area < min_piece_frac * pg.area for q in pcs):
                        continue
                    if no_show is not None and vis.intersects(no_show):
                        continue
                    if sliver is not None and _grazes(pg, vis, soft_r, *sliver):
                        continue
                if not occ.is_empty and pg.distance(occ) < gap:
                    continue
                placed.append((base, L, W, bd, pg))
                occ = occ.union(pg)
                if len(placed) >= max_n:
                    break
    f = C.Frag()
    for i, (b, L, W, bd, pg) in enumerate(placed):
        lf = MR.ribbon_leaf(b[0], b[1], heading, L, W, bend=bd, hatch=hatch)
        f += Q.reseat(lf)
    return f, placed


def gown(shape, *, border=24.0, color=K.JADE, exclude=None, soft=None, pack=None):
    """The jade gown Part: the fill, a plain border ``border`` px inside the
    silhouette closed by a FINE seam, and the packed leaf textile inside it
    (``pack`` kw for ``leaf_pack``; ``exclude`` = a region no leaf may enter,
    e.g. the laced opening and the bertha that will cover it)."""
    inner = shape.buffer(-border, quad_segs=16)
    allowed = inner.buffer(-2.5)
    if exclude is not None:
        allowed = allowed.difference(R(exclude))
    tz = inner.buffer(-(3.0 + K.FINE / 2 + 0.3))
    if exclude is not None:
        tz = tz.difference(R(exclude).buffer(-1.2))
    lf, placed = leaf_pack(allowed, soft=soft, tip_zone=tz, **(pack or {}))
    lines = K.outline(shape) + C.stroke(K.D(inner), K.FINE, role="seam") + lf
    return K.Part(shape, K.fill(shape, color), lines, {"inner": inner, "leaves": placed})
