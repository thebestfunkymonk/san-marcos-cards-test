"""KH's whole-card textiles and integrated regalia, without a band cutoff."""
from __future__ import annotations

import numpy as np
from shapely.geometry import LineString

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG
from inkkit import geom as G
from art import _kh_parts as KP
from art import _kh_window as KW


def crown():
    circlet, posts, pearls = KP.post_crown2()
    shape = K.U(circlet.shape, posts.shape, pearls.shape)
    # The posts and pearls grow from the circlet, with one outer silhouette.
    inner = circlet.lines.select(lambda m: m.role != "outline")
    inner += circlet.lines.select(lambda m: m.role == "outline")
    return K.Part(shape, K.fill(shape, K.GOLD) + circlet.fills.select(lambda m: m.layer != "gold"),
                  K.outline(shape) + inner)


def _lens(half_w, throat):
    spec = K.LensSpec(half_w=half_w, throat_y=throat)
    g = K.lens(spec)
    return K.R(K.circle(g["cL"], g["R"])).intersection(K.R(K.circle(g["cR"], g["R"])))


def garments(front, neckline, grip):
    # Union first, outline once: neither mantle carries a hidden horizontal hem.
    shape = K.R("M375 262 C310 277 240 294 195 314 "
                "C170 322 169 340 168 365 C164 423 155 475 155 525 "
                "C155 575 164 627 168 685 C169 710 170 728 195 736 "
                "C240 756 310 773 375 788 C440 773 510 756 555 736 "
                "C580 728 581 710 582 685 C586 627 595 575 595 525 "
                "C595 475 586 423 582 365 C581 340 580 322 555 314 "
                "C510 294 440 277 375 262 Z")
    field = _lens(92.0, 280.0).intersection(shape)
    trim_outer = _lens(138.0, 250.0).intersection(shape)
    # Blend the trim into the grip at its re-entrant corner, so no needle of
    # red is trapped between the little finger and the robe's jade edge.
    joined = trim_outer.union(K.c2(grip))
    trim_outer = joined.buffer(4.0).buffer(-4.0).intersection(shape)
    trim = trim_outer.difference(field)
    red = shape.difference(trim_outer)
    win = KW.window(K.AX, 432.0, h=94.0, spines=False, grass_solid=True, grass_hw=2.8,
                    grass=[(-47.0, -92.0, 48.0, 30.0, 16.0), (-33.0, -82.0, 42.0, 34.0, 14.0)],
                    rip_c=(24.0, 5.0), rip_ry=(6.0, 13.2, 20.4), rip_aspect=0.5)
    clasp = K.lion_clasp((K.AX, 346.0), 40.0)
    # The ripple is an ink line on jade, not a thin paper aperture.
    decoration = win + clasp
    apertures = K.U(win.shape, clasp.meta["silhouette"])
    blockers = K.c2(K.U(front, win.shape, clasp.meta["silhouette"]))

    # The half-drop lattice is centred on the card's rotation centre.
    contours = K.outline(shape) + K.outline(trim_outer) + K.outline(field)
    lines = C.Frag()
    # One entire left course and its rotated right partner, never cut at the join.
    left = trim.intersection(K.box(0.0, 0.0, K.AX, 1050.0))
    scales = MG.scale_lattice(left.buffer(-8.0), 11.0, origin=(K.AX - 11.0, 250.0))
    scales = K.c2(scales)
    scales = K.clip_out(scales, blockers, eps=7.3, trap=0.0)
    ends = []
    for mark in scales.marks:
        for points, _ in G.flatten(mark.d, 0.05):
            if G.Curve(np.asarray(points)).length >= 10.0:
                lines += K.line(C.polyline_d(points), K.FINE, role="scale")
                ends.extend([np.asarray(points[0]), np.asarray(points[-1])])
    # Cropped adjacent scallops meet as a course, rather than leaving tiny
    # gaps between their rounded caps at the curved trim boundary.
    for i, a in enumerate(ends):
        for b in ends[i + 1:]:
            if 0.1 < np.linalg.norm(a - b) < 4.2:
                bridge = LineString([a, b])
                if trim.contains(bridge) and not blockers.buffer(7.3).intersects(bridge):
                    lines += K.line(C.polyline_d([a, b]), K.FINE, role="scale")

    beads = C.Frag()
    bead_shapes = []
    left_edge = _lens(152.0, 242.0).boundary.intersection(K.box(0.0, 305.0, K.AX, 745.0))
    for edge in K._lines_of(left_edge):
        b, bs = KP.pearl_trim(np.asarray(edge.coords), keep=red.buffer(-4.0),
                              avoid=blockers.buffer(9.0), min_run=2)
        beads += K.c2(b)
        bead_shapes.append(K.c2(bs))
    bead_shape = K.U(*bead_shapes)
    # Keep whole concentric courses. Partial rings beside pearls made tiny
    # compound apertures that healing refilled beneath the gold.
    rip = C.Frag()
    keep = red.buffer(-8.0)
    avoid = K.U(blockers.buffer(7.0), bead_shape.buffer(4.0))
    for y in range(345, 750, 60):
        courses = K._lines_of(LineString([(140, y), (K.AX, y)]).intersection(keep.difference(avoid)))
        for course in courses:
            x = course.interpolate(0.5, normalized=True).x
            group = KP.ripple_group((x, float(y)), ry=(3.6, 11.0, 18.4), aspect=0.7)
            rings = [m for m in group.marks if keep.contains(K.R(G.from_skia(m.skia())))
                     and not avoid.intersects(K.R(G.from_skia(m.skia())))]
            if len(rings) >= 2:
                rip += K.c2(C.Frag(rings))
    # Knock the pearls into the red plate, without a paper surround.
    bead_fill = K.U(*[K.R(m.d) for m in beads.marks if m.kind == "fill"])
    red_fill = K.R(C.knockout(K.D(red), rip)).difference(bead_fill)
    fills = K.fill(red_fill, K.RED) + K.fill(trim_outer, K.JADE) + beads.select(lambda m: m.kind == "fill")
    lines += beads.select(lambda m: m.kind != "fill")
    lines = K.clip_out(lines, K.c2(front), eps=7.3, trap=0.0)
    contours = K.clip_out(contours, K.c2(front), eps=0.0, trap=0.0)
    contours = K.clip_out(contours, K.c2(neckline), eps=7.3, trap=0.0)
    lines += contours

    # Both decorations are apertures in the jade chest, not extra Scene plates.
    fills = K.clip_out(fills, apertures, eps=0.0, trap=0.0) + decoration.fills
    lines = K.clip_out(lines, apertures, eps=0.2, trap=0.0) + decoration.lines
    return K.Part(shape, fills, lines)
