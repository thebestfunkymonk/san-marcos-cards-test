"""KH's whole-card textiles and integrated regalia, without a band cutoff."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import shapely.ops
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG
from inkkit import geom as G
from art import _kh_parts as KP
from art import _kh_window as KW


def crown(fill_in=None, cut=None):
    circlet, posts, pearls = KP.post_crown2()
    shape = K.U(circlet.shape, posts.shape, pearls.shape)
    if fill_in is not None:
        shape = K.U(shape, fill_in)
    if cut is not None:
        shape = shape.difference(cut)
    # The posts and pearls grow from the circlet, with one outer silhouette.
    inner = circlet.lines.select(lambda m: m.role != "outline")
    inner += circlet.lines.select(lambda m: m.role == "outline")
    return K.Part(shape, K.fill(shape, K.GOLD) + circlet.fills.select(lambda m: m.layer != "gold"),
                  K.outline(shape) + inner)


def keep_long(f, min_len, roles=None):
    """Drop sub-paths shorter than ``min_len``: crumbs and stub dashes that clipping leaves."""
    out = []
    for m in f.marks:
        if roles is not None and m.role not in roles:
            out.append(m)
            continue
        runs = [(p, c) for p, c in G.flatten(m.d, K.FLAT_TOL)
                if len(p) > 1 and G.Curve(np.asarray(p), closed=c).length >= min_len]
        if runs:
            out.append(replace(m, d="".join(C.polyline_d(np.asarray(p), closed=c) for p, c in runs)))
    return C.Frag(out, f.meta)


def _lens(half_w, throat):
    spec = K.LensSpec(half_w=half_w, throat_y=throat)
    g = K.lens(spec)
    return K.R(K.circle(g["cL"], g["R"])).intersection(K.R(K.circle(g["cR"], g["R"])))


def garments(front, neckline, sleeves, *, pocket_front=None, cuff_bands=None, sleeve_stripes=None,
              skim=None, skim_r=18.0, skim_y=468.0):
    # Union first, outline once: neither mantle carries a hidden horizontal hem.
    shape = K.R("M375 256 C310 271 240 294 195 314 "
                "C170 322 169 340 168 365 C164 423 155 475 155 525 "
                "C155 575 164 627 168 685 C169 710 170 728 195 736 "
                "C240 756 310 779 375 794 C440 779 510 756 555 736 "
                "C580 728 581 710 582 685 C586 627 595 575 595 525 "
                "C595 475 586 423 582 365 C581 340 580 322 555 314 "
                "C510 294 440 271 375 256 Z")
    field = _lens(92.0, 280.0).intersection(shape)
    trim_outer = _lens(138.0, 250.0).intersection(shape)
    # The sleeves are the red cloak's own: carved out of the jade trim so the cloak runs
    # unbroken from the outer edge to the cuff mouth.
    sleeve_zone = K.c2(sleeves)
    trim_outer = trim_outer.difference(sleeve_zone)
    if skim is not None:
        # Where a held shaft runs alongside the trim edge, the trim bulges around it, so the
        # trim outline and the shaft contour never run as a shallow pair of strokes.
        near = K.c2(skim).buffer(skim_r).intersection(trim_outer.buffer(60.0)) \
            .intersection(K.c2(K.box(0.0, 0.0, 750.0, skim_y)))
        trim_outer = trim_outer.union(near).intersection(shape).difference(sleeve_zone)
    if pocket_front is not None:
        # Assign enclosed grip pockets to the lapel, without extending its
        # fillet into the hand's open distal finger notches.
        enclosure = K.U(trim_outer, K.c2(pocket_front))
        pockets = K.U(*[Polygon(ring) for polygon in K._polys_of(enclosure)
                        for ring in polygon.interiors])
        trim_outer = K.U(trim_outer, pockets).intersection(shape)
    trim = trim_outer.difference(field)
    red = shape.difference(trim_outer)
    win = KW.window(K.AX, 432.0, h=94.0, spines=False, grass_solid=True, grass_hw=2.8,
                    grass=[(-47.0, -92.0, 48.0, 30.0, 16.0), (-33.0, -82.0, 42.0, 34.0, 14.0)],
                    rip_c=(24.0, 5.0), rip_ry=(6.0, 13.2, 20.4), rip_aspect=0.5)
    win.lines = win.lines.select(lambda m: m.role != "outline") + K.outline(win.shape, role="contour") \
        + K.outline(win.meta["inner"], role="contour")
    clasp = K.lion_clasp((K.AX, 346.0), 40.0)
    # The ripple is an ink line on jade, not a thin paper aperture.
    decoration = win + clasp
    apertures = K.U(win.shape, clasp.meta["silhouette"])
    blockers = K.c2(K.U(front, win.shape, clasp.shape))

    # The half-drop lattice is centred on the card's rotation centre.
    trim_contour = K.outline(trim_outer, role="_trim-outline")
    contours = K.outline(shape, role="contour") + trim_contour + K.outline(field)
    lines = C.Frag()
    # One entire left course and its rotated right partner, never cut at the join.
    left = trim.intersection(K.box(0.0, 0.0, K.AX, 1050.0))
    lattice = left.buffer(-8.0)
    scales = MG.scale_lattice(lattice, 11.0, origin=(K.AX - 11.0, 250.0))
    scales = K.clip_out(scales, blockers, eps=7.3, trap=0.0)
    runs = [LineString(points) for mark in scales.marks for points, _ in G.flatten(mark.d, 0.05)
            if G.Curve(np.asarray(points)).length >= 10.0]
    crop_edge = lattice.difference(blockers.buffer(7.3)).boundary
    clear = 4.2 + K.FINE
    ends = [(i, k) for i in range(len(runs)) for k in (0, -1)]
    # A scallop that runs on a little past a neighbour's cusp leaves a flick beyond the T, which
    # a bridge would only retrace; it ends at the cusp instead. Longer overruns (over 4 px here)
    # are cropped scallops' own curves and stay.
    trims = {}
    for i, k in ends:
        run = runs[i]
        over = [run.project(p) if k == 0 else run.length - run.project(p)
                for j, l in ends if j != i
                for p in [Point(runs[j].coords[l])] if run.distance(p) < 0.6]
        over = [s for s in over if 0.5 < s <= 3.2]
        if over:
            trims[(i, k)] = min(over)
    runs = [shapely.ops.substring(run, trims.get((i, 0), 0.0), run.length - trims.get((i, -1), 0.0))
            if (i, 0) in trims or (i, -1) in trims else run for i, run in enumerate(runs)]
    cut = {}
    for n, (i, k) in enumerate(ends):
        a = np.asarray(runs[i].coords[k])
        for j, l in ends[n + 1:]:
            b = np.asarray(runs[j].coords[l])
            gap = float(np.linalg.norm(a - b))
            if not 0.1 < gap < 4.2:
                continue
            on_a, on_b = crop_edge.distance(Point(a)) < 0.3, crop_edge.distance(Point(b)) < 0.3
            if on_a != on_b and gap >= K.FINE:
                # A scallop cropped by the lattice edge stops clear of its neighbour's cusp,
                # rather than being bridged into a stub tail along the row.
                r, e = (i, k) if on_a else (j, l)
                cut[(r, e)] = max(cut.get((r, e), 0.0), clear - gap + 0.1)
                continue
            # Adjacent scallops of a row meet their shared cusp as one course.
            bridge = LineString([a, b])
            if trim.contains(bridge) and not blockers.buffer(7.3).intersects(bridge):
                lines += K.line(C.polyline_d([a, b]), K.FINE, role="scale")
    for i, run in enumerate(runs):
        a, b = cut.get((i, 0), 0.0), run.length - cut.get((i, -1), 0.0)
        if (a, b) == (0.0, run.length):
            lines += K.line(C.polyline_d(np.asarray(run.coords)), K.FINE, role="scale")
        elif b - a >= 6.0:
            piece = shapely.ops.substring(run, a, b)
            lines += K.line(C.polyline_d(np.asarray(piece.coords)), K.FINE, role="scale")
    lines = K.c2(lines)

    beads = C.Frag()
    bead_shapes = []
    left_edge = _lens(152.0, 242.0).boundary.intersection(K.box(0.0, 305.0, K.AX, 745.0))
    for edge in K._lines_of(left_edge):
        b, bs = KP.pearl_trim(np.asarray(edge.coords), keep=red.buffer(-4.0),
                              avoid=blockers.buffer(9.0), min_run=2)
        beads += K.c2(b)
        bead_shapes.append(K.c2(bs))
    bead_shape = K.U(*bead_shapes)
    # The chest's diagonal textile has a different rhythm from the lapel scales.
    chest = field.buffer(-7.0).difference(blockers.buffer(7.3))
    lines += K.hatch_in(chest, origin=(K.AX, 525.0))
    # Restore the dense half-drop ripple textile, as a whole-card C2 course.
    avoid = K.U(blockers.buffer(7.0), bead_shape.buffer(4.0), sleeve_zone.buffer(5.0))
    ripple_left = red.intersection(K.box(0, 0, K.AX, 1050))
    rip = KP.ripple_textile(ripple_left, ry=(3.8, 10.2, 16.6), aspect=0.72,
                           pitch=(58.0, 42.0), origin=(K.AX, 294.0), mirror=False)
    starts = rip.meta["starts"]
    rip = KP.close_starts(K.clip_out(rip, avoid, eps=0.0, trap=0.0), starts)
    rip = K.c2(keep_long(rip, 8.0))
    if sleeve_stripes is not None:
        # Pleats along each sleeve, knocked out of the red like the ripple rings.
        rip += K.c2(sleeve_stripes)
    # Knock the pearls into the red plate, without a paper surround.
    bead_fill = K.U(*[K.R(m.d) for m in beads.marks if m.kind == "fill"])
    red_fill = K.R(C.knockout(K.D(red), rip)).difference(bead_fill)
    fills = K.fill(red_fill, K.RED) + K.fill(trim_outer, K.JADE) + beads.select(lambda m: m.kind == "fill")
    lines += beads.select(lambda m: m.kind != "fill")
    lines = K.clip_out(lines, K.c2(front), eps=7.3, trap=0.0)
    scale_lines = lines.select(lambda m: m.role == "scale")
    lines = lines.select(lambda m: m.role != "scale") + K.c2(
        K.clip_in(scale_lines, K.box(0.0, 0.0, K.AX, 1050.0)))
    contours = K.clip_out(contours, K.c2(front), eps=1.6, trap=0.0)
    contours = K.clip_out(contours, K.c2(neckline), eps=0.2, trap=0.0)
    contours = K.clip_out(contours, K.c2(win.shape), eps=7.3, trap=0.0)
    lines += contours
    if cuff_bands is not None:
        lines += K.clip_out(K.c2(cuff_bands), K.c2(front), eps=1.6, trap=0.0)
    # The sleeve's long edges are fold lines that start on the cloak's own outline.
    sleeve_edges = K.clip_in(K.outline(sleeve_zone), shape.buffer(-0.4))
    sleeve_edges = K.clip_out(sleeve_edges, trim_outer.buffer(1.0), eps=0.0, trap=0.0)
    # The edges end under the hand outline, so no round cap sits in the notch at the cuff corner.
    lines += K.clip_out(sleeve_edges, K.c2(front), eps=K.STROKE_EPS, trap=0.0)

    # Both decorations are apertures in the jade chest, not extra Scene plates.
    fills = K.clip_out(fills, apertures, eps=0.0, trap=0.0) + decoration.fills
    lines = K.clip_out(lines, apertures, eps=0.2, trap=0.0)
    cleaned = []
    for mark in lines.marks:
        if mark.role != "_trim-outline":
            cleaned.append(mark)
            continue
        # Tiny, nearly closed hairpins at a covered grip become stray caps.
        # Drop those subpaths, not the longer courses meeting the cuff/foot.
        d = "".join(C.polyline_d(points, closed=closed)
                    for points, closed in G.flatten(mark.d, 0.05)
                    if G.Curve(points, closed=closed).length >= K.MEDIUM)
        if d:
            cleaned.append(replace(mark, d=d, role="outline"))
    lines = keep_long(C.Frag(cleaned, lines.meta), 8.0, roles=("hatch",)) + decoration.lines
    return K.Part(shape, fills, lines)
