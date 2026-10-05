"""Painter's-algorithm compositor for court figures.

A court is a stack of :class:`Item` s added BACK TO FRONT. Each item is a
closed region with:

* ``fill``    a palette colour (jade / red / gold / ink) or None for paper.
              Paper is never painted: a paper item is simply a hole cut in
              everything behind it (brief §C / ART_CONTRACT §5).
* ``outer``   contour width where the item's edge is figure silhouette
              (against the ground or against nothing behind it) — CONTOUR.
* ``inner``   contour width where the item's edge lies over another item
              behind it — MEDIUM. (So the weight system of §H.0 falls out of
              the stacking: bold silhouettes, medium interior divisions.)
* ``detail``  a Frag (or callable(visible_region) -> Frag) of lines drawn
              inside the item; clipped to what is visible of it, so hatch and
              patterns butt onto the contours of whatever is in front.
* ``knock``   a Frag (or callable) knocked OUT of the fill (paper lines on
              red / jade), done as geometry.

``Scene.render()`` returns {layer: svg} with occlusion resolved exactly:
each fill = region − union(front regions) − knockouts; each contour =
boundary − union(front regions), split into outer/inner weights; each
detail clipped to the visible region.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import shapely
from shapely.geometry import MultiLineString, LineString, Polygon

from deck import tokens as T
from deck.motifs import core as MC
from deck.motifs.core import Frag, Mark

from . import shapes as SH

INNER_ERODE = 1.0      # px: an edge counts as 'inner' when inside back items by this much
KO_MARGIN = 3.0        # px of solid kept between a knockout and a front item's edge (§I.12)


@dataclass
class Item:
    name: str
    shape: object                      # shapely geometry or d-string
    fill: str | None = None            # palette colour or None (paper)
    outer: float | None = T.CONTOUR    # silhouette weight (None = no line)
    inner: float | None = T.MEDIUM     # interior-edge weight (None = no line)
    detail: object = None              # Frag | callable(region) -> Frag
    knock: object = None               # Frag | callable(region) -> Frag
    occludes: bool = True              # hides what is behind it
    line_color: str = T.INK
    meta: dict = field(default_factory=dict)

    def geom(self):
        if not hasattr(self, "_g"):
            self._g = SH.shp(self.shape)
        return self._g


class Scene:
    def __init__(self):
        self.items: list[Item] = []
        self.over: list[Frag] = []      # frags drawn last, unclipped

    def add(self, *items: Item) -> "Scene":
        for it in items:
            if it is not None:
                self.items.append(it)
        return self

    def top(self, f: Frag) -> "Scene":
        if f:
            self.over.append(f)
        return self

    def get(self, name: str) -> Item:
        for it in self.items:
            if it.name == name:
                return it
        raise KeyError(name)

    # ------------------------------------------------------------------
    def fronts(self) -> list:
        """union of regions in front of each item (index-aligned)."""
        n = len(self.items)
        out = [None] * n
        acc = Polygon()
        for i in range(n - 1, -1, -1):
            out[i] = acc
            it = self.items[i]
            if it.occludes:
                acc = shapely.union_all([acc, it.geom()]) if not acc.is_empty else it.geom()
        return out

    def backs(self) -> list:
        n = len(self.items)
        out = [None] * n
        acc = Polygon()
        for i in range(n):
            out[i] = acc
            it = self.items[i]
            if it.occludes:
                acc = shapely.union_all([acc, it.geom()]) if not acc.is_empty else it.geom()
        return out

    def visible(self, name: str):
        fr = self.fronts()
        for i, it in enumerate(self.items):
            if it.name == name:
                return it.geom().difference(fr[i]) if not fr[i].is_empty else it.geom()
        raise KeyError(name)

    def render(self) -> tuple[Frag, dict]:
        """-> (Frag of everything, info). Use ``.layers()`` on the Frag."""
        fr = self.fronts()
        bk = self.backs()
        fills = Frag()
        lines = Frag()
        info = {}
        for i, it in enumerate(self.items):
            g = it.geom()
            vis = g.difference(fr[i]) if not fr[i].is_empty else g
            vis = shapely.make_valid(vis)
            info[it.name] = vis
            # ---- fill ------------------------------------------------------
            if it.fill is not None and not vis.is_empty:
                fg = vis
                kn = it.knock(vis) if callable(it.knock) else it.knock
                if kn:
                    kn = _settle(kn, vis, KO_MARGIN)
                    if kn:
                        fg = fg.difference(kn.shape())
                d = SH.dstr(fg)
                if d:
                    fills += MC.fill(d, color=it.fill, role=it.name)
            # ---- contour ---------------------------------------------------
            if it.outer or it.inner:
                rings = SH.boundary_lines(g)
                if rings:
                    ml = MultiLineString([LineString(r) for r in rings])
                    visb = ml.difference(fr[i]) if not fr[i].is_empty else ml
                    back = bk[i].buffer(-INNER_ERODE) if not bk[i].is_empty else Polygon()
                    if back.is_empty:
                        inner_l, outer_l = Polygon(), visb
                    else:
                        inner_l = visb.intersection(back)
                        outer_l = visb.difference(back)
                    for part, w in ((outer_l, it.outer), (inner_l, it.inner)):
                        if not w:
                            continue
                        segs = [p for p in SH.lines_of(_merge(part)) if len(p) >= 2 and _len(p) > 0.8]
                        if segs:
                            d = "".join(G_poly(p) for p in segs)
                            lines.marks.append(Mark(d, "stroke", MC.legal_width(w), "round", "round", 4.0,
                                                    it.line_color, MC.LAYER_OF[it.line_color], "contour"))
            # ---- detail ----------------------------------------------------
            det = it.detail(vis) if callable(it.detail) else it.detail
            if det and not vis.is_empty:
                lines += _settle(det, vis, 0.0)
        out = fills + lines
        for f in self.over:
            out += f
        return out, info


def _merge(g):
    try:
        return shapely.line_merge(g) if not g.is_empty and g.geom_type in ("MultiLineString",) else g
    except Exception:  # pragma: no cover
        return g


def _len(p):
    return float(np.hypot(*np.diff(p, axis=0).T).sum())


def G_poly(p):
    closed = np.hypot(*(p[0] - p[-1])) < 1e-6
    return MC.polyline_d(p[:-1] if closed else p, closed=closed)


def _settle(f: Frag, vis, margin: float) -> Frag:
    """Fit a detail / knockout Frag into the visible region ``vis``:
    * small closed marks (dots, terminals, bubbles, voids) are kept whole if
      they sit inside ``vis`` (shrunk by ``margin`` + half their width) and
      dropped otherwise — never clipped into slivers;
    * open strokes are clipped to ``vis`` shrunk by ``margin`` (+ their half
      width when margin > 0), so knockout lines stop short of front edges."""
    out = []
    cache = {}
    for m in f.marks:
        if not m.d:
            continue
        g = SH.shp(m.d) if m.kind == "fill" else None
        closed_small = False
        if m.kind == "fill":
            closed_small = g is not None and not g.is_empty and max(g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1]) < 40
        else:
            polys_ = [p for p, c in G_flat(m.d)]
            cl = [c for p, c in G_flat(m.d)]
            if cl and all(cl):
                P = np.vstack(polys_)
                closed_small = (np.ptp(P[:, 0]) < 40 and np.ptp(P[:, 1]) < 40)
        if closed_small:
            key = ("s", round(margin + (m.w / 2 if m.kind == "stroke" else 0), 3))
            zone = cache.setdefault(key, vis.buffer(-key[1]) if key[1] > 0 else vis)
            mg = MC.Frag([m]).shape()
            if zone.contains(mg):
                out.append(m)
            continue
        if m.kind == "fill":
            gg = g.intersection(vis)
            d = SH.dstr(gg)
            if d:
                out.append(Mark(d, "fill", m.w, m.cap, m.join, m.miter, m.color, m.layer, m.role))
            continue
        sh = margin + m.w / 2 if margin > 0 else 0.0
        zone = cache.setdefault(("l", round(sh, 3)), vis.buffer(-sh) if sh > 0 else vis)
        out += MC.clip(Frag([m]), zone).marks
    return Frag(out, f.meta)


def G_flat(d):
    from inkkit import geom as _G
    return _G.flatten(d, 0.1)
