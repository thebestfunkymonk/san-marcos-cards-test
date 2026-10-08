"""QH's continuous woven gown and unioned regalia."""
from __future__ import annotations

import numpy as np
import shapely
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Polygon
from shapely.ops import substring

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG
from art import _qh_body as B


def merge(parts):
    """Trap adjoining plates and retain their shared interior edges, no halos."""
    fragments = []
    front = Polygon()
    for part in reversed(parts):
        # 1.2 keeps the back plate under a MEDIUM outline (half-width 1.55) too
        fragments.append(K.clip_out(part.frag, front, eps=-0.2, trap=1.2))
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


def _along(courses, a, b, reach=6.0):
    """The path from ``a`` to ``b`` along the original courses: one course,
    or two meeting at a node within ``reach``; None when neither applies."""
    pa, pb = shapely.Point(a), shapely.Point(b)
    on_a = [c for c in courses if c.distance(pa) < 0.05]
    on_b = [c for c in courses if c.distance(pb) < 0.05]
    for c in on_a:
        if c in on_b:
            s0, s1 = c.project(pa), c.project(pb)
            path = substring(c, min(s0, s1), max(s0, s1))
            return path if s0 <= s1 else path.reverse()
    for ca in on_a:
        for cb in on_b:
            nodes = [g for g in getattr(ca.intersection(cb), "geoms", [ca.intersection(cb)])
                     if g.geom_type == "Point"]
            nodes = [n for n in nodes if n.distance(pa) < reach and n.distance(pb) < reach]
            if nodes:
                n = min(nodes, key=lambda n: n.distance(pa) + n.distance(pb))
                sa, na, nb, sb = ca.project(pa), ca.project(n), cb.project(n), cb.project(pb)
                one = substring(ca, min(sa, na), max(sa, na))
                one = one if sa <= na else one.reverse()
                two = substring(cb, min(nb, sb), max(nb, sb))
                two = two if nb <= sb else two.reverse()
                return LineString(list(one.coords) + list(two.coords)[1:])
    return None


def _clear_seam(ln, seam, clear=4.8, cross=1.0):
    """Shorten a free end lying just short of the seam line.

    Each half is clipped just past the seam (~0.5 px), so an end cap stopping
    less than 3 px short of the other half's plate leaves a sub-gap; ends
    either cross the seam (within ``cross``) or stop ``clear`` short of it.
    """
    for end in (0, 1):
        L = ln.length
        s_end = 0.0 if end == 0 else L
        d = seam.distance(shapely.Point(ln.coords[-end]))
        if not cross < d < clear:
            continue
        for k in range(1, 41):
            s = s_end + (k * 0.25 if end == 0 else -k * 0.25)
            if not 0 < s < L:
                break
            if seam.distance(ln.interpolate(s)) >= clear:
                ln = substring(ln, s, L) if end == 0 else substring(ln, 0, s)
                break
    return ln


def garments(front, neckline, *, sleeves=None, inked=None, trim=None, hands=None, clear=None, seam=None):
    # Both necklines and every robe edge belong to one whole-card C2 path.
    # The four outer shoulder/hem nodes are smooth (tangent-continuous); the
    # node under the near lock sits 4 px low so it stays hidden by the hair.
    shape = K.R(
        "M369 298 C318 305 266 320 236 307 "
        "C190 310 153.9 335.6 157 366 C159.6 392.3 155 460 151 525 "
        "C147 590 147.6 656.6 157 684 C167 713 184 740 222 748 "
        "C252 734 298 748 344 754 L381 752 "
        "C432 745 484 730 514 743 "
        "C560 740 596.1 714.4 593 684 C590.4 657.7 595 590 599 525 "
        "C603 460 602.4 393.4 593 366 C583 337 566 310 528 302 "
        "C498 316 452 302 406 296 Z")
    bodice = K.R(
        "M369 298 C318 305 286 319 266 320 "
        "C278 352 286 410 292 470 C294.2 492 294 510 294 525 "
        "C294 540 285.67 558 282 580 C272 640 266 698 250 734 "
        "C278 748 298 748 344 754 L381 752 "
        "C432 745 464 731 484 730 "
        "C472 698 464 640 458 580 C455.8 558 456 540 456 525 "
        "C456 510 464.33 492 468 470 C478 410 484 352 500 316 "
        "C472 302 452 302 406 296 Z")
    mantle = shape.difference(bodice)
    if sleeves is not None:
        # The sleeves are the mantle's own lobes: union them into the jade, with
        # a small fillet where they leave the edge, and carve them out of the
        # bodice so the bodice contour becomes the sleeve outline.
        # an ``inked`` sleeve lies on the mantle and enters through its edge, so
        # it is clipped to the mantle; the others stand off it as bell lobes
        lobes = K.c2(K.U(sleeves, inked.intersection(mantle)) if inked is not None else sleeves)
        grown = K.U(mantle, lobes)
        fillet = grown.buffer(10.0).buffer(-10.0).difference(grown).intersection(lobes.buffer(20.0))
        bodice = bodice.difference(K.U(lobes, fillet))
    jade = shape.difference(bodice)
    # Two inset woven fields face their respective heads. The curved fold
    # between them carries fine stitch hatching, never a divider.
    fold = K.R("M375 330 C350 415 395 465 375 525 "
               "C355 585 400 635 375 720 L750 720 L750 330 Z")
    left = bodice.buffer(-9).difference(fold.buffer(9))
    # ``left`` and its rotation share a strip above the fold's top and below
    # its foot; each strip is woven once, facing the nearer head, or the two
    # lattices cross there.
    shared = left.intersection(K.rot180(left)).intersection(K.box(0, 525, 750, 1050))
    field = left.difference(shared)
    lattice = MG.scale_lattice(field, 15.0, w=K.MEDIUM, origin=(375, 380))
    lattice = K.c2(lattice)
    lattice = K.clip_out(lattice, K.c2(front), eps=8.0, trap=0.0)
    if clear is not None:
        # ink drawn over the bodice (the clasp ripple) keeps a 3 px gap to the paper courses
        lattice = K.clip_out(lattice, K.c2(clear), eps=3.0 + K.MEDIUM / 2, trap=0.0)
    pieces = [pts for m in lattice.marks for pts, _ in K.G.flatten(m.d, K.FLAT_TOL)]
    # The lattice is split at every node where a lower row's arc leaves an
    # upper arc, leaving ~2.5 px pieces at the arc bottoms. A piece joined at
    # both ends is part of a scale, not a crumb: keep it whatever its length
    # (dropping it and bridging the gap drew a flat chord at every arc bottom).
    # Joined means joined to a kept piece: repeat until stable, so a node's
    # short bottom piece whose arms were dropped at a field edge goes too.
    keep = [True] * len(pieces)
    while True:
        tips = np.array([q for pts, k in zip(pieces, keep) if k for q in (pts[0], pts[-1])])
        tree = cKDTree(tips)
        new = [LineString(pts).length >= 12
               or all(len(tree.query_ball_point(pts[j], 0.05)) > 1 for j in (0, -1))
               for pts, k in zip(pieces, keep) if k]
        it = iter(new)
        nxt = [k and next(it) for k in keep]
        if nxt == keep:
            break
        keep = nxt
    kept = [LineString(pts) for pts, k in zip(pieces, keep) if k]
    ends = [(i, j, np.asarray(ln.coords[-j])) for i, ln in enumerate(kept) for j in (0, 1)]
    tree = cKDTree([e[2] for e in ends])
    free = [len(tree.query_ball_point(e[2], 0.05)) == 1 for e in ends]
    # The same lattice on a wider field: a gap at the field edge is closed
    # along the scale's own arcs (a chord drew flat tops and hexagon crumbs).
    whole = [LineString(pts) for m in K.c2(MG.scale_lattice(field.buffer(10), 15.0, w=K.MEDIUM, origin=(375, 380))).marks
             for pts, _ in K.G.flatten(m.d, K.FLAT_TOL)]
    room = bodice.buffer(-(K.MEDIUM + 3.0))
    near_front = K.c2(front).buffer(7.0)
    bridges, cut = [], {}
    for n, (i, j, a) in enumerate(ends):
        for m, (i2, j2, b) in enumerate(ends[n + 1:], n + 1):
            d = np.linalg.norm(a - b)
            if 0.1 < d < 4.5 and (free[n] or free[m]):
                bridge = _along(whole, a, b)
                if bridge is not None and room.contains(bridge) and not near_front.intersects(bridge):
                    bridges.append(bridge)
                    continue
                # ends that cannot be joined along the scale (cut by the
                # hands) are drawn apart to leave a 3 px solid between them;
                # two arcs leaving a cusp part slower than they shorten, so
                # the trim is measured on the trimmed tips
                def tip(k, s, r):
                    return np.asarray(kept[k].interpolate(r if s == 0 else kept[k].length - r).coords[0])
                r = 0.1
                while r < 8.0 and np.linalg.norm(tip(i, j, r * free[n]) - tip(i2, j2, r * free[m])) \
                        < 3.0 + K.MEDIUM + 0.1:
                    r += 0.1
                for key, f in (((i, j), free[n]), ((i2, j2), free[m])):
                    if f:
                        cut[key] = max(cut.get(key, 0.0), r)
    courses = C.Frag()
    for i, ln in enumerate(kept):
        s0, s1 = cut.get((i, 0), 0.0), ln.length - cut.get((i, 1), 0.0)
        if s1 - s0 >= 1.0:
            courses += K.line(C.polyline_d(substring(ln, s0, s1).coords if (s0 or s1 < ln.length) else ln.coords),
                              K.MEDIUM, role="scale")
    for bridge in bridges:
        courses += K.line(C.polyline_d(bridge.coords), K.MEDIUM, role="scale")
    # A sleeve lying wholly on the mantle needs its own edge; one standing off
    # the bodice already has the bodice contour as its outline.
    side = C.Frag()
    blocker = Polygon()
    if inked is not None:
        edge = K.c2(inked.intersection(mantle)).boundary.intersection(mantle.buffer(-1.0)).difference(K.c2(front).buffer(1.0))
        for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
            if g.length > 6.0:
                side += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="contour")
        blocker = K.U(blocker, side.shape().buffer(3.6))
    if trim is not None:
        blocker = K.U(blocker, K.c2(trim.lines).shape().buffer(4.4), K.c2(trim.shape).buffer(5.6))
    # Pearl armlet edging is part of the textile, not a floating strip.
    pearls = B.pearls_on([(184, 391), (272, 391)],
                        d_max=8.0, d_min=8.0, gap=0.0, even=True)
    beads = K.c2(pearls.frag)
    bead_shape = K.c2(pearls.shape)
    beads = K.clip_out(beads, K.c2(front), eps=0, trap=0)
    # The armlet clears the waves before their length filter, so no flick is
    # left beside the end pearls (5.3 = a 3 px gap from the rings' ink).
    blocker = K.U(blocker, bead_shape.buffer(5.3))
    # Wave courses are constructed once on the left, then rotated as a whole.
    waves = B.wave_lines(jade.intersection(K.box(0, 0, 375, 1050)).buffer(-10),
                         pitch=9.2, wl=26, amp=2.3, origin=(375, 322))
    whole = [LineString(pts) for m in K.c2(waves).marks for pts, _ in K.G.flatten(m.d, K.FLAT_TOL)]
    waves = K.clip_out(K.c2(waves), K.c2(front), eps=10.0, trap=0.0)
    wave_lines = []
    for m in waves.marks:
        for pts, _ in K.G.flatten(m.d, K.FLAT_TOL):
            for ln in K._lines_of(LineString(pts).difference(blocker)):
                # beside the armlet a piece under a wavelength reads as a stray flick
                if ln.length >= (20 if ln.distance(bead_shape) < 6.5 else 12):
                    wave_lines.append(ln)
    # Adjacent cropped courses must not leave near-touching free terminals:
    # a gap cut in one course is closed along that course (a straight chord
    # put a kink in the wave).
    ends = [np.array(q) for ln in wave_lines for q in (ln.coords[0], ln.coords[-1])]
    for i, a in enumerate(ends):
        for b in ends[i + 1:]:
            if 0.1 < np.linalg.norm(a - b) < 7.3:
                bridge = LineString([a, b])
                course = next((w for w in whole if w.distance(shapely.Point(a)) < 0.05
                               and w.distance(shapely.Point(b)) < 0.05), None)
                if course is not None:
                    s0, s1 = sorted((course.project(shapely.Point(a)), course.project(shapely.Point(b))))
                    bridge = substring(course, s0, s1)
                if jade.contains(bridge) and not K.c2(front).buffer(8).intersects(bridge):
                    wave_lines.append(bridge)
    if seam is not None:
        wave_lines = [ln for ln in map(lambda ln: _clear_seam(ln, seam), wave_lines) if ln.length >= 12]
    waves = C.Frag()
    for ln in wave_lines:
        waves += K.line(C.polyline_d(ln.coords), K.FINE, role="wave")
    fold_field = bodice.buffer(-9).difference(K.U(left, K.rot180(left)))
    stitches = K.hatch_in(fold_field, origin=(375, 525))
    stitches = K.clip_out(stitches, K.c2(front), eps=8.0, trap=0.0)
    # the stitch's round cap keeps the 3 px solid to the knockout courses
    stitches = K.clip_out(stitches, courses.shape(), eps=3.0 + K.FINE / 2, trap=0.0)
    stitch_courses = C.Frag()
    for mark in stitches.marks:
        for pts, _ in K.G.flatten(mark.d, K.FLAT_TOL):
            if LineString(pts).length >= 7:
                stitch_courses += K.line(C.polyline_d(pts), K.FINE, role="hatch")
    stitches = stitch_courses
    extra = side + (K.c2(trim.lines) if trim is not None else C.Frag())
    red = B.fast_knockout(bodice, courses)
    body_window = K.box(0, 350, 750, 700)
    contours = K.outline(shape) \
        + K.clip_in(K.outline(bodice, role="contour"), body_window) \
        + K.clip_out(K.outline(bodice), body_window, eps=0, trap=0)
    contours = K.clip_out(contours, K.c2(front), eps=0, trap=0)
    if hands is not None:
        # the hand's own outline is the cuff mouth; the garment contour must not run beside it
        contours = K.clip_out(contours, K.c2(hands), eps=1.2, trap=0)
    contours = K.clip_out(contours, K.c2(neckline), eps=0, trap=0)
    fills = K.fill(red, K.RED) + K.fill(jade, K.JADE)
    if trim is not None:
        fills += K.c2(trim.fills)
    return K.Part(shape, fills, contours + waves + stitches + beads + extra, {"bodice": bodice})


def held(stem, petiole, leaf, flower, cuff):
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
    # Trap jade under ink at the blade and sepal contacts; the gold plate
    # must not leak along their exact shared edge.
    leaf_contacts = K.U(K.box(532, 128, 563, 145), K.box(551, 195, 563, 224))
    gold = gold.difference(jade.buffer(0.3).intersection(leaf_contacts))
    # Close the three-way contour junction at the foreshortened lobe.
    botanical = K.Part(botanical.shape,
                       botanical.fills.select(lambda m: m.color != K.GOLD) + K.fill(gold, K.GOLD),
                       botanical.lines + K.outline(leaf.shape, role="contour")
                       + K.dot((548.5, 284), K.RULE, role="leaf-junction"))
    notch = K.box(569, 258, 582, 278)
    # the lobe edge that borders the petiole's gold inside the notch stays drawn
    botanical.lines = K.clip_out(botanical.lines, notch, eps=0, trap=0) \
        + K.clip_in(K.outline(botanical.shape, role="contour"), notch) \
        + K.clip_in(K.outline(leaf.shape, role="contour"), notch.intersection(botanical.shape.buffer(-0.5)))
    shape = K.U(botanical.shape, cuff.shape)
    # The stalk runs under the five curled digits, not through a paper halo.
    fills = K.clip_out(botanical.fills, cuff.shape, eps=0, trap=0) + cuff.fills
    lines = K.clip_out(botanical.lines, cuff.shape, eps=0.2, trap=0)
    lines += cuff.lines.select(lambda m: m.role != "outline")
    lines += K.clip_in(K.outline(cuff.shape, role="grip-edge"), botanical.shape.buffer(0.2))
    return K.Part(shape, fills, lines + K.outline(shape))
