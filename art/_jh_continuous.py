"""Continuous textiles and integrated assemblies for the Spring Minstrel."""
from __future__ import annotations

import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from art import _jh_parts as JP


def merge(parts):
    """Keep shared interior edges, trapping each ink into a single plate."""
    front = Polygon()
    fragments = []
    for part in reversed(parts):
        fragments.append(K.clip_out(K.flatten_fills(part.frag), front, eps=-0.2, trap=1.6))
        front = K.U(front, part.shape)
    frag = C.frag(*reversed(fragments))
    fills = C.Frag()
    for color in (K.JADE, K.RED, K.GOLD, K.INK):
        regions = [K.R(m.d) for m in frag.marks if m.kind == "fill" and m.color == color]
        if regions:
            fills += K.fill(shapely.union_all(regions).buffer(0.2).buffer(-0.2), color)
    shape = K.U(*[p.shape for p in parts])
    lines = K.clip_in(frag.select(lambda m: m.kind != "fill"), shape.buffer(-1.6))
    return K.Part(shape, fills, lines + K.outline(shape))


def garments(front, clasp):
    # Both robe and tunic boundaries are whole-card C2 Béziers, never hems
    # clipped at y511. The puffed shoulders flow into the inverted sleeves.
    shape = K.R(
        "M375 298 C320 310 282 306 244 314 C192 318 165 345 159 390 "
        "C152 438 158 486 160 525 C162 564 155 612 161 660 "
        "C167 705 194 732 246 736 C284 744 322 740 375 752 "
        "C430 740 468 744 506 736 C558 732 585 705 591 660 "
        "C598 612 592 564 590 525 C588 486 595 438 589 390 "
        "C583 345 556 318 504 314 C466 306 428 310 375 298 Z")
    tunic = K.R(
        "M375 298 C320 310 282 306 244 314 C272 340 300 378 280 525 "
        "C260 672 238 710 246 736 C284 744 322 740 375 752 "
        "C430 740 468 744 506 736 C478 710 450 672 470 525 "
        "C490 378 512 340 504 314 C466 306 428 310 375 298 Z")
    # The baldric is a curved textile panel, not the double-head seam.
    sash = K.R(
        "M243 306 C274 366 315 451 349 525 C383 599 424 684 455 744 "
        "L507 744 C476 684 435 599 401 525 C367 451 326 366 295 306 Z")
    sash = sash.intersection(shape)
    tab = K.R("M230 312 L294 330 L301 349 L237 331 Z")
    shape = K.U(shape, K.c2(tab))
    sash = K.U(sash, K.c2(tab))
    tunic = K.U(tunic, sash).buffer(3).buffer(-3).intersection(shape)
    jade = shape.difference(tunic)
    blockers = K.c2(front).difference(K.c2(tab))
    slashes = JP.ripple_slashes([
        ((232, 294), (42, 53, 67.3), 38, 142),
        ((222, 376), (38, 49, 63.3), 36, 144),
        ((222, 458), (30, 41, 55.3), 34, 146),
        ((550, 322), (40, 51, 65.3), 38, 134),
        ((558, 408), (36, 47, 61.3), 36, 144),
        ((562, 496), (30, 41, 55.3), 34, 146)])
    slashes = K.clip_in(K.c2(slashes), jade.buffer(-10).difference(sash.buffer(9)))
    slashes = C.Frag([m for m in slashes.marks
                     if not blockers.buffer(8).intersects(K.R(K.G.from_skia(m.skia())))])
    # Whole bubble triads, mirrored as complete motifs, not clipped courses.
    _, pipe = JP.open_spline([(405, 493), (402, 428), (398, 364)])
    pipe_clear = K.c2(LineString(pipe).buffer(12))
    bubbles = JP.powder(tunic, JP.rising, pitch=(30, 34), origin=(400, 330),
                        visible=tunic.intersection(K.box(0, 0, 750, 492)).difference(
                            K.U(sash.buffer(9), blockers.buffer(9), pipe_clear)),
                        clear=9)
    bubbles = K.c2(bubbles)
    jade_fill = K.R(C.knockout(K.D(jade), slashes)).difference(sash)
    red_fill = K.R(C.knockout(K.D(tunic), bubbles)).difference(sash)

    # Festoon supports follow the curved panel; the other half is rotated
    # as a whole so bulbs and wire courses agree across the join.
    center = K.P(375, 525)
    axis = K.P(107, 207)
    axis /= float((axis @ axis) ** 0.5)
    normal = K.P(axis[1], -axis[0])
    wire = C.Frag()
    for k in range(-4, 0):
        a, b = center + axis * (k * 46), center + axis * ((k + 1) * 46)
        low = (a + b) / 2 - normal * 6
        bulb = low - normal * 4
        course = K.line(K.arc3(a, low, b), K.FINE, role="wire")
        course += K.seg(low, bulb, K.FINE, role="socket")
        course += K.dot(bulb, 6.3, K.GOLD, role="bulb")
        course += K.dot(a, 6.3, K.GOLD, role="support")
        if sash.buffer(-5).contains(K.R(K.G.from_skia(course.marks[0].skia()))):
            wire += course
    wire = K.c2(wire)
    piping = JP.bead_chain(pipe, grow=(5.4, 8.4), gap=4.6,
                           keep=tunic.buffer(-8).difference(sash.buffer(8)))
    piping = K.c2(piping)
    gold = K.U(*[K.R(m.d) for m in piping.marks if m.kind == "fill"])
    fills = K.fill(jade_fill, K.JADE) + K.fill(red_fill.difference(gold), K.RED)
    fills += piping.select(lambda m: m.kind == "fill")
    lines = K.outline(shape) + K.outline(tunic) + K.outline(sash)
    lines = K.clip_out(lines, blockers, eps=0, trap=0)
    detail = K.clip_out(wire + piping.select(lambda m: m.kind != "fill"),
                        blockers, eps=8, trap=0)
    robe = K.Part(shape, fills, lines + detail)
    result = merge([robe, clasp])
    return K.Part(result.shape, result.fills, result.lines, {"tab": tab})


def fiddle(fd, arm):
    neck, body, pegs = fd.neck_part(), fd.body_part(fb_over=True), fd.tpegs_part()
    neck_pegs = merge([pegs, neck])
    neck_pegs = K.Part(neck_pegs.shape, neck_pegs.fills,
                       neck_pegs.lines.select(lambda m: m.role != "outline")
                       + K.outline(neck_pegs.shape)
                       + K.outline(neck.meta["fingerboard"]))
    # A peg touching the scroll shoulder has no invisible gold island
    # under the ink junction. Retain a small trap beneath its printed edge.
    junction = pegs.meta["pegs"][0].buffer(K.CONTOUR / 2).intersection(
        neck.meta["head"].buffer(K.CONTOUR / 2))
    ink_core = neck_pegs.lines.shape().buffer(-0.4).intersection(junction)
    gold = K.U(*[K.R(m.d) for m in neck_pegs.fills.marks if m.color == K.GOLD])
    neck_pegs = K.Part(neck_pegs.shape,
                       neck_pegs.fills.select(lambda m: m.color != K.GOLD)
                       + K.fill(gold.difference(ink_core), K.GOLD), neck_pegs.lines)
    instrument = merge([neck_pegs, body])
    shape = K.U(instrument.shape, arm.shape)
    fills = K.clip_out(instrument.fills, arm.shape, eps=0, trap=0) + arm.fills
    lines = K.clip_out(instrument.lines, arm.shape, eps=0.2, trap=0)
    lines += arm.lines.select(lambda m: m.role != "outline")
    lines += K.clip_in(K.outline(arm.shape, role="grip-edge"), instrument.shape.buffer(0.2))
    return K.Part(shape, fills, lines + K.outline(shape))


def trap_under_ink(frag):
    """Trap jade under the fiddle's outer two contour junctions."""
    structural = frag.select(lambda m: m.kind == "stroke" and m.role in
                              ("outline", "contour", "grip-edge"))
    core = structural.shape().buffer(-0.4).intersection(
        K.c2(K.box(585, 430, 596, 481)))
    jade = K.U(*[K.R(m.d) for m in frag.marks if m.kind == "fill" and m.color == K.JADE])
    return (frag.select(lambda m: not (m.kind == "fill" and m.color == K.JADE))
            + K.fill(jade.difference(core), K.JADE))
