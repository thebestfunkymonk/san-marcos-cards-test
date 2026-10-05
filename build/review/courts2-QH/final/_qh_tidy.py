"""art/_qh_tidy.py — Q♥ junction clean-ups (courts2 review).

Small geometric repairs at places where three parts meet, kept apart from the
builders so the builders stay what they were:

* ``fill_temple``: a silhouette pinhole where the cap's gold rim, the face
  contour and the top of the hair lock converge (three contours round a
  pocket of ground only a few px wide, read at 750 as an ink blot by the
  temple) — the lock is run on up under the rim to the face, so only two
  contours meet there (rim / hair, hair / face).
* ``trim_rim_end``: the rim's near end stood ~3 px proud of the line from the
  cap's limb into the hair, a knuckle in the CONTOUR; it now ends flush on
  that line (the convex run from the cap into the hair).
* ``beads_clear``: pearls of an armlet crossed by a haloed attribute are kept
  whole (≥ ``gap`` clear of its paper channel) or dropped — never a bead cut
  into a crescent by the channel.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C



def _rebuild(part: K.Part, shape, color) -> K.Part:
    """``part`` with its region replaced by ``shape`` (a superset): outline
    redrawn, interior lines kept, fill grown by the added area."""
    old_fill = shapely.union_all([K.R(m.d) for m in part.fills.marks if m.kind == "fill"]) \
        if part.fills.marks else part.shape
    add = shape.difference(part.shape)
    fill = old_fill.union(add)
    inner = part.lines.select(lambda m: m.role != "outline")
    return K.Part(shape, K.fill(fill, color), K.outline(shape) + inner, dict(part.meta))


def fill_temple(sc: K.Scene, name: str, part: K.Part, color, *, max_area=300.0, grow=1.2, run_on=None):
    """Run the scene item ``name`` (built from ``part``) on into every small
    hole of the scene's silhouette that it borders (see module doc).
    ``run_on`` = (cap item name prefixes, (x0, y0, x1, y1)): also fill the
    notch under the rim's end — the lock grows to the convex run from the
    cap (those items, below ``y0``) into the lock's top (above ``y1``),
    inside that box (hidden under the rim and the head except in the
    notch)."""
    sil = sc.silhouette()
    holes = [Polygon(r) for pg in K._polys_of(sil) for r in pg.interiors]
    near = [h.buffer(grow, quad_segs=8) for h in holes if h.area < max_area and h.distance(part.shape) < 1.0]
    if run_on is not None:
        prefixes, (x0, y_min, x1, y_max) = run_on
        caps = [it.occ.intersection(K.box(0, y_min, 750, 1050)) for it in sc.items
                if it.occ is not None and it.name.startswith(tuple(prefixes))]
        top = part.shape.intersection(K.box(0, 0, 750, y_max))
        hull = shapely.union_all(caps + [top]).convex_hull
        near.append(hull.intersection(K.box(x0, y_min, x1, y_max)))
    if not near:
        return part
    shape = part.shape.union(shapely.union_all(near))
    shape = max(K._polys_of(shape.buffer(0)), key=lambda g: g.area)
    new = _rebuild(part, shape, color)
    for it in sc.items:
        if it.name == name:
            it.occ = K.R(new.shape)
            it.frag = K.flatten_fills(new.frag)
    return new


def trim_rim_end(rim: K.Part, cap_parts, hair, *, x_max, y_from=0.0) -> K.Part:
    """Cut the rim's end left of ``x_max`` flush with the convex run from the
    cap (``cap_parts``: regions; only their part below ``y_from``, the cap's
    lower limb) into the hair's top (see module doc)."""
    rs = rim.shape
    y1 = rs.bounds[3]
    top_hair = hair.intersection(K.box(0, 0, 750, y1 + 14.0))
    lower = [g.intersection(K.box(0, y_from, 750, 1050)) for g in cap_parts]
    hull = shapely.union_all(lower + [top_hair]).convex_hull
    keep = rs.intersection(hull).union(rs.intersection(K.box(x_max, 0, 750, 1050)))
    keep = max(K._polys_of(keep.buffer(0)), key=lambda g: g.area)
    if keep.area >= rs.area - 0.5:
        return rim
    keep = keep.buffer(-0.6, join_style=2).buffer(0.6, join_style=2)
    keep = max(K._polys_of(keep), key=lambda g: g.area)
    return K.Part(keep, K.fill(keep, K.GOLD), K.outline(keep), dict(rim.meta))


def beads_clear(armlet: K.Part, blocker, *, halo=K.HALO, gap=K.GAP_MARK) -> K.Part:
    """The armlet (``_qh_body.pearls_on`` Part) without the pearls that the
    ``blocker``'s paper channel would cut (see module doc)."""
    chan = K.R(blocker).buffer(halo + K.MEDIUM / 2 + gap + K.FINE / 2, quad_segs=12)
    discs = [d for d in armlet.meta["discs"] if not d.intersects(chan)]
    if not discs:
        return K.Part(Polygon(), C.Frag(), C.Frag(), {"discs": []})
    shape = shapely.union_all(discs)
    lines = C.Frag()
    for g in discs:
        lines += K.outline(g, K.FINE, role="pearl")
    return K.Part(shape, K.fill(shape, K.GOLD), lines, {"discs": discs})


def seam_x(sleeve: K.Part, y: float):
    """x of the sleeve's FINE border seam where it crosses the line ``y``
    (None when it does not)."""
    xs = []
    for m in sleeve.lines.marks:
        if m.role != "seam" or not m.d:
            continue
        for pts, _ in K.G.flatten(m.d, 0.05):
            if len(pts) < 2:
                continue
            g = LineString(pts).intersection(K.box(0, y - 0.01, 750, y + 0.01))
            if not g.is_empty:
                xs.append(g.centroid.x)
    return xs


def strand(sleeve: K.Part, p0, p1, *, sag=0.0, d=9.5, xs=(), inset=0.6) -> K.Part:
    """A strung pearl armlet (§G.29, gold, Aquifer FINE contours) on the arc
    ``p0`` → ``p1`` (sagitta ``sag``) with its pearls centred at the arc's
    points of abscissa ``xs`` — placed, not spread, so one pearl can sit
    squarely on the border seam (the seam crossing it through its middle,
    never tangent to it) and the strand can break round an attribute with
    the same clearance both sides. Pearls not wholly inside the sleeve
    (inset by ``inset``) are left out. → Part (meta 'discs')."""
    reg = sleeve.meta.get("region", sleeve.shape)
    ok = reg.buffer(-(d / 2 + K.FINE / 2 + inset))
    pts = np.asarray(C.sample_d(K.arc_sag(K.P(p0), K.P(p1), sag), 0.2)[0][0])
    ln = LineString(pts)
    discs = []
    for x in xs:
        g = ln.intersection(K.box(x - 0.01, 0, x + 0.01, 1050))
        if g.is_empty:
            continue
        c = Point(x, g.centroid.y)
        if not ok.contains(c):
            continue
        discs.append(c.buffer(d / 2, quad_segs=24))
    if not discs:
        return K.Part(Polygon(), C.Frag(), C.Frag(), {"discs": []})
    shape = shapely.union_all(discs)
    lines = C.Frag()
    for g in discs:
        lines += K.outline(g, K.FINE, role="pearl")
    return K.Part(shape, K.fill(shape, K.GOLD), lines, {"discs": discs})


def waves_clear(part: K.Part, front, *, peek=7.0, role="wave") -> K.Part:
    """Pattern lines of ``part`` (``role``) that only PEEK out from under a
    region drawn in front (``front``: a trough dipping a few px below a hair
    lock's edge, running along it) are dropped: a piece outside ``front``
    that starts or ends on its edge and never gets ``peek`` px clear of it
    leaves a jade pocket 1-3 px wide under the edge (QA 12) and reads as
    noise. Lines crossing the edge decisively are kept whole. → Part."""
    fr = K.R(front)
    edge = fr.boundary
    keep = []
    for m in part.lines.marks:
        if m.role != role or not m.d:
            keep.append(m)
            continue
        out = []
        for pts, closed in K.G.flatten(m.d, 0.05):
            if len(pts) < 2:
                continue
            ln = LineString(pts)
            if not ln.intersects(fr.buffer(1.0)):
                out.append(np.asarray(pts))
                continue
            drop = []
            for g in K._lines_of(ln.difference(fr)):
                q = np.asarray(g.segmentize(0.5).coords)
                dd = np.array([edge.distance(Point(*v)) for v in q])
                ends_on = min(dd[0], dd[-1]) < 1.0
                if ends_on and dd.max() < peek:
                    drop.append(g.buffer(0.05, cap_style=2))
            res = ln.difference(shapely.union_all(drop)) if drop else ln
            out += [np.asarray(g.coords) for g in K._lines_of(res) if g.length > 0.5]
        if out:
            keep.append(replace(m, d="".join(C.polyline_d(p) for p in out)))
    return K.Part(part.shape, part.fills, C.Frag(keep, part.lines.meta), dict(part.meta))


def beads_inside(strand: K.Part, inside, clear_of=(), *, gap=K.GAP_MARK, edge_w=K.MEDIUM) -> K.Part:
    """The strand without the pearls that would sit within ``gap`` of the edge
    of ``inside`` (a region they lie on: the bodice) or of any region in
    ``clear_of`` drawn in front (a hair lock) — heal opens such a pearl's
    FINE contour into a "C" (bare gold on red, §C.4). Pearls wholly hidden
    under a front region are dropped too. → Part."""
    ins = K.R(inside).buffer(-(edge_w / 2 + gap + K.FINE / 2), quad_segs=12)
    fronts = [K.R(g).buffer(edge_w / 2 + gap + K.FINE / 2, quad_segs=12) for g in clear_of]
    discs = [d for d in strand.meta["discs"] if ins.contains(d) and not any(f.intersects(d) for f in fronts)]
    if not discs:
        return K.Part(Polygon(), C.Frag(), C.Frag(), {"discs": []})
    shape = shapely.union_all(discs)
    lines = C.Frag()
    for g in discs:
        lines += K.outline(g, K.FINE, role="pearl")
    return K.Part(shape, K.fill(shape, K.GOLD), lines, {"discs": discs})



def lines_clear(part: K.Part, zone, *, role="wave", min_len=5.0) -> K.Part:
    """``part`` with its ``role`` lines cut out of ``zone`` (pieces shorter
    than ``min_len`` dropped): a pattern stopping short of something laid on
    it (the forearm's waves stop ≥ 3 px before the bracelet's pearls instead
    of grazing them — heal cut paper wedges out of the gold). → Part."""
    z = K.R(zone)
    keep = []
    for m in part.lines.marks:
        if m.role != role or not m.d:
            keep.append(m)
            continue
        out = []
        for pts, _ in K.G.flatten(m.d, 0.05):
            if len(pts) < 2:
                continue
            for g in K._lines_of(LineString(pts).difference(z)):
                if g.length >= min_len:
                    out.append(np.asarray(g.coords))
        if out:
            keep.append(replace(m, d="".join(C.polyline_d(q) for q in out)))
    return K.Part(part.shape, part.fills, C.Frag(keep, part.lines.meta), dict(part.meta))
