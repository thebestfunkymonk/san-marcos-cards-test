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
    # A raised mantle fold meets the neck grip's short cuff. Its matching
    # inverted fold preserves the existing robe seam and composition.
    fold = K.R("M444 318 C451 296 470 286 492 286 L510 310 L504 330 Z")
    shape = K.U(shape, K.c2(fold))
    enclosure = K.U(shape, K.c2(front))
    pockets = K.U(*[Polygon(r) for p in K._polys_of(enclosure)
                    for r in p.interiors if Polygon(r).area < 120])
    shape = K.U(shape, pockets)
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
    tunic = K.U(tunic, sash).buffer(3).buffer(-3).intersection(shape)
    jade = shape.difference(tunic)
    blockers = K.c2(front)
    slashes = JP.ripple_slashes([
        ((232, 294), (42, 53, 67.3), 38, 142),
        ((222, 376), (38, 49, 63.3), 36, 144),
        ((222, 458), (30, 41, 55.3), 34, 146),
        ((550, 322), (40, 51, 65.3), 38, 134),
        ((558, 408), (36, 47, 61.3), 36, 144),
        ((562, 496), (30, 41, 55.3), 34, 146)])
    slash_zone = jade.buffer(-10).difference(sash.buffer(9))
    slashes = C.Frag([m for m in K.c2(slashes).marks
                     if slash_zone.covers(K.R(K.G.from_skia(m.skia())))
                     and not blockers.buffer(8).intersects(K.R(K.G.from_skia(m.skia())))])
    # Whole bubble triads, mirrored as complete motifs, not clipped courses.
    _, pipe = JP.open_spline([(405, 493), (402, 428), (398, 364)])
    pipe_clear = K.c2(LineString(pipe).buffer(12))
    bubbles = JP.powder(tunic, JP.triad, pitch=(26, 30), origin=(400, 330),
                        visible=tunic.intersection(K.box(0, 0, 750, 525)).difference(
                            K.U(sash.buffer(9), blockers.buffer(9), pipe_clear)),
                        clear=9)
    bubbles = K.c2(bubbles)
    hatch_zone = jade.buffer(-8).difference(
        K.U(sash.buffer(7.3), blockers.buffer(8), slashes.shape().buffer(4.2)))
    hatch = K.hatch_in(hatch_zone, angle=-32, origin=(375, 525))
    # A second textile, with the opposite grain, breaks up every red panel.
    # The centre-anchored whole-card courses are intrinsically C2; unlike
    # clipped half-courses they never acquire endpoints at the join.
    red_zone = tunic.buffer(-8).difference(
        K.U(sash.buffer(7.3), blockers.buffer(8), pipe_clear,
            bubbles.shape().buffer(5.8), K.c2(clasp.shape).buffer(8)))
    red_hatch = K.hatch_in(red_zone, angle=32, origin=(375, 525))
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
    wire = wire.select(lambda m: m.kind != "fill" or
                       not blockers.buffer(8).intersects(K.R(m.d)))
    piping = JP.bead_chain(pipe, grow=(5.4, 8.4), gap=4.6,
                           keep=tunic.buffer(-8).difference(sash.buffer(8)))
    piping = K.c2(piping)
    gold = K.U(*[K.R(m.d) for m in piping.marks if m.kind == "fill"])
    fills = K.fill(jade_fill, K.JADE) + K.fill(red_fill.difference(gold), K.RED)
    fills += piping.select(lambda m: m.kind == "fill")
    lines = K.outline(shape) + K.outline(tunic) + K.outline(sash)
    lines = K.clip_out(lines, blockers, eps=0, trap=0)
    detail = K.clip_out(wire + hatch + red_hatch + piping.select(lambda m: m.kind != "fill"),
                        blockers, eps=8, trap=0)
    robe = K.Part(shape, fills, lines + detail)
    result = merge([robe, clasp])
    return result


def fiddle(fd, cuff):
    neck, body, pegs = fd.neck_part(), fd.body_part(fb_over=True), fd.tpegs_part()
    # Strings meet the transverse borders, with their round caps hidden.
    inserts = K.U(body.meta["fb"], body.meta["tail"])
    strings = K.clip_out(body.lines.select(lambda m: m.role == "string"),
                         inserts, eps=0, trap=0)
    body.lines = body.lines.select(lambda m: m.role != "string") + strings
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
    gold = K.U(*[K.R(m.d) for m in instrument.fills.marks if m.color == K.GOLD])
    engraving = gold.buffer(-7).difference(instrument.lines.shape().buffer(5.5))
    instrument.lines += K.hatch_in(engraving, angle=-35, origin=(530, 400))
    return held(instrument, cuff)


def held(attribute, cuff):
    """One held-object/grip outline, with no paper channel."""
    shape = K.U(attribute.shape, cuff.shape)
    fills = K.clip_out(attribute.fills, cuff.shape, eps=0, trap=0) + cuff.fills
    lines = K.clip_out(attribute.lines, cuff.shape, eps=0.2, trap=0)
    lines += cuff.lines.select(lambda m: m.role != "outline")
    lines += K.clip_in(K.outline(cuff.shape, role="grip-edge"),
                       attribute.shape.buffer(0.2))
    return K.Part(shape, fills, lines + K.outline(shape), cuff.meta)


def trap_under_ink(frag):
    """Remove unprinted colour islands at the fiddle's contour junctions."""
    structural = frag.select(lambda m: m.kind == "stroke" and m.role in
                              ("outline", "contour", "grip-edge"))
    core = structural.shape().buffer(-0.4)
    contacts = {
        K.JADE: K.U(K.box(585, 430, 596, 481), K.box(490, 260, 508, 276)),
        K.GOLD: K.box(497, 289, 524, 310),
    }
    result = frag.select(lambda m: not (m.kind == "fill" and m.color in contacts))
    for color, zone in contacts.items():
        plate = K.U(*[K.R(m.d) for m in frag.marks
                      if m.kind == "fill" and m.color == color])
        plate = plate.difference(core.intersection(K.c2(zone)))
        plate = K.U(*[p for p in K._polys_of(plate)
                      if p.area >= 4 or not K.c2(zone).intersects(p)])
        result += K.fill(plate, color)
    return result
