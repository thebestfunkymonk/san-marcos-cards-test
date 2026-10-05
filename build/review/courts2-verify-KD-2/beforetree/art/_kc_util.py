"""K♣ · small shared helpers (candidates for deck.courtkit)."""
from __future__ import annotations

import shapely

from deck import courtkit as K
from deck import tokens as T

CONTOUR = T.CONTOUR


def visible_fill(region, lines, sil=None, *, open_r=0.9, min_area=6.0, trap=1.7, hole_min=30.0):
    """Trim a fill ``region`` to where it can be SEEN: minus the ink of
    ``lines`` (a Frag) and of the silhouette contour (``sil``'s boundary at
    CONTOUR, since the Scene strokes it), opened by ``open_r`` and without
    crumbs, then grown back ``trap`` px under the lines. A plate left under an
    ink solid (a pointed tip, a notch between two knobs, a sliver pinched
    between two outlines) is what QA 4c flags: this cuts it out."""
    reg = K.R(region)
    parts = [K.R(K.G.from_skia(m.skia())) for m in lines.marks]
    if sil is not None:
        parts.append(K.R(sil).boundary.buffer(CONTOUR / 2, quad_segs=8))
    ink_u = shapely.union_all(parts) if parts else shapely.geometry.Polygon()
    vis = reg.difference(ink_u).buffer(-open_r, quad_segs=6).buffer(open_r, quad_segs=6)
    vis = K.U(*[g for g in K._polys_of(vis) if g.area > min_area])
    out = reg.intersection(vis.buffer(trap, quad_segs=8))
    # holes smaller than ``hole_min`` px² sit wholly under ink: close them (a
    # pin-hole in a plate reads to QA 12 as a knockout line too thin)
    polys = []
    for g in K._polys_of(out):
        keep = [h for h in g.interiors if shapely.geometry.Polygon(h).area >= hole_min]
        polys.append(shapely.geometry.Polygon(g.exterior, keep))
    return K.U(*polys) if polys else out
