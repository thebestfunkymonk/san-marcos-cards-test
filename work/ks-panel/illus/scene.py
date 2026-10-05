"""Painter's scene with GEOMETRIC occlusion, for court figures.

A court is a stack of Parts, back to front (mantle, collar, hair, face,
beard, hands, attributes...). Each Part has

* ``sil``      its silhouette (FILL d) — what it hides of the parts behind;
* ``fills``    [(d or None, colour)] flat colour regions (None = the whole
               silhouette), clipped to the silhouette;
* ``detail``   a Frag of interior lines / patterns (clipped to the silhouette
               unless ``clip_detail=False``);
* ``contour``  stroke width of its own outline (CONTOUR / MEDIUM / None).

``compose`` walks front → back keeping the union of silhouettes already
placed, and removes it from every fill and line further back. Nothing is
ever painted in paper colour: a paper face in front of gold hair is simply a
hole in the hair (brief §C.4, §I.25). Lines behind are cut on the front
contour's centreline; the front contour covers the cut (same as hatch ends).

``Scene.outline_w`` adds one stroke round the union of every part — the
figure silhouette at CONTOUR weight (§H.0 weights), so the outside edge is
uniformly bold even where parts have lighter own contours.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import shapely

from deck import tokens as T
from deck.motifs import core as MC
from inkkit import geom as G


@dataclass
class Part:
    name: str
    sil: str
    fills: list = field(default_factory=list)
    detail: MC.Frag = field(default_factory=MC.Frag)
    contour: float | None = T.CONTOUR
    contour_color: str = T.INK
    clip_detail: bool = True
    occludes: bool = True
    over: MC.Frag = field(default_factory=MC.Frag)   # lines drawn unclipped by own sil (still occluded)
    in_outline: bool = True                          # part of the figure silhouette


class Scene:
    def __init__(self, outline_w: float | None = T.CONTOUR):
        self.parts: list[Part] = []
        self.outline_w = outline_w
        self.extra = MC.Frag()

    def add(self, part: Part) -> Part:
        self.parts.append(part)
        return part

    # clear colour kept between a front contour's edge and the pattern lines
    # it hides: the §B.2 interlace gap (4.2), which also satisfies the §I.12
    # parallel-stroke minimum where a hidden line runs alongside the edge
    CLEAR = T.INTERLACE_GAP

    def _cut_behind(self, det: MC.Frag, occ_w: dict) -> MC.Frag:
        """Cut DETAIL (patterns, hatch, folds, current lines) of a part behind
        so every line end keeps CLEAR px from the edge of each front contour.
        Terminals/dots touching the zone are dropped whole (no slivers)."""
        from dataclasses import replace as _r
        out = det
        for cw, occ in occ_w.items():
            if occ.is_empty or not out:
                continue
            reach = cw / 2 + self.CLEAR
            zone = occ.buffer(reach, quad_segs=12)
            keep = []
            for m in out.marks:
                if m.kind == "fill":
                    g = MC.Frag([m]).shape()
                    if g.intersects(zone):
                        if m.role in ("terminal", "dot"):
                            continue
                        d = G.from_shape(g.difference(zone))
                        if d:
                            keep.append(_r(m, d=d))
                        continue
                    keep.append(m)
                else:
                    keep.append(m)
            out = MC.cut(MC.Frag(keep, out.meta), occ.buffer(cw / 2, quad_segs=12), gap=self.CLEAR)
        return out

    @staticmethod
    def _clip_contour(con: MC.Frag, w: float, occ_w: dict) -> MC.Frag:
        """Clip a behind contour at the front silhouettes; where the front
        contour is thinner, cut a little further out so this line's round cap
        ends inside the front contour instead of poking past it."""
        for fw, occ in occ_w.items():
            if occ.is_empty:
                continue
            grow = max(0.0, w / 2 - fw / 2)
            con = MC.clip(con, occ.buffer(grow, quad_segs=12) if grow else occ, inside=False)
        return con

    def compose(self) -> MC.Frag:
        fills_out, lines_out = MC.Frag(), MC.Frag()
        occ = shapely.Polygon()
        occ_w: dict = {}
        for p in reversed(self.parts):
            sil = MC.region(p.sil)
            vis = sil.difference(occ) if not occ.is_empty else sil
            for d, color in p.fills:
                reg = vis if d is None else MC.region(d).intersection(vis)
                if reg.is_empty or reg.area < 0.5:
                    continue
                fills_out += MC.fill(G.from_shape(reg), color=color, role=p.name)
            det = p.detail
            if det and p.clip_detail:
                det = MC.clip(det, sil)
            det = det + p.over
            if det and occ_w:
                det = self._cut_behind(det, occ_w)
            con = MC.Frag()
            if p.contour:
                con = MC.stroke(p.sil, p.contour, color=p.contour_color, role=f"contour:{p.name}")
                con = self._clip_contour(con, p.contour, occ_w)
            lines_out += det + con
            if p.occludes:
                occ = occ.union(sil) if not occ.is_empty else sil
                w = p.contour or T.MEDIUM
                occ_w[w] = occ_w[w].union(sil) if w in occ_w else sil
        out = fills_out + lines_out
        if self.outline_w:
            u = shapely.union_all([MC.region(p.sil) for p in self.parts if p.in_outline])
            ol = MC.stroke(G.from_shape(u), self.outline_w, role="outline")
            # attributes held in front of the figure (not part of its outline)
            # hide the outline where they cross it
            front = {}
            for p in self.parts:
                if not p.in_outline and p.occludes:
                    fw = p.contour or T.MEDIUM
                    front[fw] = front[fw].union(MC.region(p.sil)) if fw in front else MC.region(p.sil)
            if front:
                ol = self._clip_contour(ol, self.outline_w, front)
            out += ol
        return out + self.extra

    @staticmethod
    def _no_colour_under_knots(f: MC.Frag) -> MC.Frag:
        """Where contours meet in a solid ink knot wider than a CONTOUR line,
        no colour plate prints beneath it (QA 4c: nothing hidden under a
        higher plate). Knot = what survives an opening of radius
        CONTOUR/2 + 0.3 (the QA's own test), shrunk 1.2 px so every cut stays
        under the ink; fill islands orphaned by a cut are dropped."""
        from dataclasses import replace as _r
        ink = MC.Frag([m for m in f.marks if m.layer == "ink"]).shape()
        rad = T.CONTOUR / 2 + 0.3
        knots = ink.buffer(-rad, quad_segs=8).buffer(rad - 1.2, quad_segs=8)
        if knots.is_empty:
            return f
        out = []
        for m in f.marks:
            if m.kind == "fill" and m.layer in ("jade", "red", "gold"):
                g = MC.Frag([m]).shape()
                if g.intersects(knots):
                    g2 = g.difference(knots)
                    parts = [p for p in getattr(g2, "geoms", [g2]) if p.area >= 20.0]
                    if parts:
                        out.append(_r(m, d=G.from_shape(shapely.union_all(parts))))
                    continue
            out.append(m)
        return MC.Frag(out, f.meta)

    def silhouette(self) -> str:
        return G.from_shape(shapely.union_all([MC.region(p.sil) for p in self.parts]))
