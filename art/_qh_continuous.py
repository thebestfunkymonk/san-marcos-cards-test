"""QH's continuous woven gown and unioned regalia."""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG
from art import _qh_body as B


def merge(parts):
    """Trap adjoining plates and retain their shared interior edges, no halos."""
    fragments = []
    front = Polygon()
    for part in reversed(parts):
        fragments.append(K.clip_out(part.frag, front, eps=-0.2, trap=1.6))
        front = K.U(front, part.shape)
    frag = C.frag(*reversed(fragments))
    # One plate per ink removes anti-aliased seams between same-ink pieces.
    fills = C.Frag()
    for color in (K.JADE, K.RED, K.GOLD, K.INK):
        regions = [K.R(m.d) for m in frag.marks if m.kind == "fill" and m.color == color]
        if regions:
            plate = shapely.union_all(regions).buffer(0.2).buffer(-0.2)
            fills += K.fill(plate, color)
    shape = K.U(*[p.shape for p in parts])
    inner = K.clip_in(frag.select(lambda m: m.kind != "fill"), shape.buffer(-1.6))
    return K.Part(shape, fills, inner + K.outline(shape))


def garments(front, neckline):
    # Both necklines and every robe edge belong to one whole-card C2 path.
    shape = K.R(
        "M369 298 C318 305 266 320 236 303 "
        "C190 310 163 336 157 366 C168 392 155 460 151 525 "
        "C147 590 144 658 157 684 C163 714 184 740 222 748 "
        "C252 734 298 748 344 754 L381 752 "
        "C432 745 484 730 514 747 "
        "C560 740 587 714 593 684 C582 658 595 590 599 525 "
        "C603 460 606 392 593 366 C587 336 566 310 528 302 "
        "C498 316 452 302 406 296 Z")
    bodice = K.R(
        "M369 298 C318 305 286 319 266 320 "
        "C278 352 286 410 292 470 C295 492 294 510 294 525 "
        "C294 540 287 558 282 580 C272 640 266 698 250 734 "
        "C278 748 298 748 344 754 L381 752 "
        "C432 745 464 731 484 730 "
        "C472 698 464 640 458 580 C455 558 456 540 456 525 "
        "C456 510 463 492 468 470 C478 410 484 352 500 316 "
        "C472 302 452 302 406 296 Z")
    jade = shape.difference(bodice)
    # Two inset woven fields face their respective heads. The plain red fold
    # between them is curved, not a divider at the double-head seam.
    fold = K.R("M375 330 C350 415 395 465 375 525 "
               "C355 585 400 635 375 720 L750 720 L750 330 Z")
    left = bodice.buffer(-11).difference(fold.buffer(9))
    lattice = MG.scale_lattice(left, 15.0, w=K.MEDIUM, origin=(375, 380))
    lattice = K.c2(lattice)
    lattice = K.clip_out(lattice, K.c2(front), eps=8.0, trap=0.0)
    courses = C.Frag()
    for m in lattice.marks:
        for pts, _ in K.G.flatten(m.d, 0.05):
            if LineString(pts).length >= 12:
                courses += K.line(C.polyline_d(pts), K.MEDIUM, role="scale")
    # Wave courses are constructed once on the left, then rotated as a whole.
    waves = B.wave_lines(jade.intersection(K.box(0, 0, 375, 1050)).buffer(-12),
                         pitch=14, wl=32, amp=2.3, origin=(375, 322))
    waves = K.clip_out(K.c2(waves), K.c2(front), eps=10.0, trap=0.0)
    wave_lines = []
    for m in waves.marks:
        for pts, _ in K.G.flatten(m.d, 0.05):
            ln = LineString(pts)
            if ln.length >= 12:
                wave_lines.append(ln)
    # Adjacent cropped courses must not leave near-touching free terminals.
    ends = [np.array(q) for ln in wave_lines for q in (ln.coords[0], ln.coords[-1])]
    for i, a in enumerate(ends):
        for b in ends[i + 1:]:
            if 0.1 < np.linalg.norm(a - b) < 7.3:
                bridge = LineString([a, b])
                if jade.contains(bridge) and not K.c2(front).buffer(8).intersects(bridge):
                    wave_lines.append(bridge)
    waves = C.Frag()
    for ln in wave_lines:
        waves += K.line(C.polyline_d(ln.coords), K.FINE, role="wave")
    red = B.fast_knockout(bodice, courses)
    contours = K.outline(shape) + K.outline(bodice)
    contours = K.clip_out(contours, K.c2(front), eps=0, trap=0)
    contours = K.clip_out(contours, K.c2(neckline), eps=0, trap=0)
    return K.Part(shape, K.fill(red, K.RED) + K.fill(jade, K.JADE),
                  contours + waves, {"bodice": bodice})


def held(stem, petiole, leaf, flower, arm):
    shaft = K.U(petiole.shape, stem.shape)
    shaft_part = K.Part(shaft, K.clip_out(petiole.fills, stem.shape, eps=0, trap=0) + stem.fills,
                        K.outline(shaft) + stem.lines.select(lambda m: m.role != "outline"))
    botanical = merge([shaft_part, leaf] + flower)
    # The narrow sinus has no paper island; it belongs to the gold petiole.
    holes = [Polygon(r) for pg in K._polys_of(botanical.shape)
             for r in pg.interiors if Polygon(r).area < 180]
    repair = K.U(*holes)
    botanical = K.Part(K.U(botanical.shape, repair),
                       botanical.fills + K.fill(repair, K.GOLD),
                       K.clip_out(botanical.lines, repair.buffer(3.2), eps=0, trap=0)
                       + K.clip_in(K.outline(leaf.shape), repair.buffer(3.2)))
    jade = K.U(*[K.R(m.d) for m in leaf.fills.marks if m.kind == "fill"])
    old_gold = K.U(*[K.R(m.d) for m in botanical.fills.marks if m.color == K.GOLD])
    sinus = leaf.shape.difference(jade).intersection(shaft.convex_hull)
    gold = K.U(old_gold, repair, sinus).difference(jade)
    gold = K.U(gold, gold.buffer(0.6).intersection(K.box(545, 250, 575, 305))
               .intersection(botanical.shape)).difference(jade)
    # Close the three-way contour junction at the foreshortened lobe.
    botanical = K.Part(botanical.shape,
                       botanical.fills.select(lambda m: m.color != K.GOLD) + K.fill(gold, K.GOLD),
                       botanical.lines + K.outline(leaf.shape, role="contour")
                       + K.dot((548.5, 284), K.RULE, role="leaf-junction"))
    shape = K.U(botanical.shape, arm.shape)
    # The stalk runs under the five curled digits, not through a paper halo.
    fills = K.clip_out(botanical.fills, arm.shape, eps=0, trap=0) + arm.fills
    lines = K.clip_out(botanical.lines, arm.shape, eps=0.2, trap=0)
    lines += arm.lines.select(lambda m: m.role != "outline")
    lines += K.clip_in(K.outline(arm.shape, role="grip-edge"), botanical.shape.buffer(0.2))
    return K.Part(shape, fills, lines + K.outline(shape))
