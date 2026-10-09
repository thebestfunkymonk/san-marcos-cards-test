"""K♣ · the kingfisher finial (brief §H.7: 'a wrought-gold belted kingfisher
finial at y ≈ 110: ragged crest, dagger bill, sculpted, perched').

A goldsmith's belted kingfisher in strict profile on the staff's knop, facing
the king (viewer's left). Its identity is in the species' own marks, inlaid
as a goldsmith would: the big head under a RAGGED crest raked back off the
crown, the heavy DAGGER bill as long as the head, the white neck ring (paper,
like the faces), the blue-grey breast band (jade enamel: the 'belt'), the
folded wing with scalloped coverts and stepped primaries, the short square
tail. A finial, never a live bird (§H.0 care rules): rigid, upright, its
toes sunk in the knop, its surfaces engraved.

Built in a local frame (feet at the origin on the knop top, facing −x), then
placed rigidly at ``feet`` (no scaling: every size is authored in px).

``kingfisher3`` is the card's bird (director's note: the smooth cut-out read
as a toy): chased covert rows, a banded breast and a ball knop on the staff's
collar. ``kingfisher`` and ``kingfisher2`` are the earlier drafts.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import Point, Polygon

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C

P = K.P
FINE, MEDIUM, CONTOUR = T.FINE, T.MEDIUM, T.CONTOUR
INK, JADE, GOLD = T.INK, T.JADE, T.FOIL
GAP, GAP_MARK = K.GAP, K.GAP_MARK


def _pts(d, step=0.3):
    return C.sample_d(d, step)[0][0]


def _closed(points):
    return Polygon(_pts(K.spline([P(p) for p in points], closed=True), 0.3)).buffer(0)


def kingfisher(feet=(540.0, 176.0), *, knop_r=11.0, belt=JADE, crest=None, bill_tip=(-62.0, -65.0),
               head_c=(0.0, -72.0), head_r=17.0, eye=(-3.0, -75.5), facing=-1, coverts=2, covert_sag=-2.6) -> K.Part:
    fx, fy = feet

    def Q(x, y):
        return P(fx + x, fy + y)

    def poly(pts):
        return Polygon([tuple(Q(*p)) for p in pts]).buffer(0)

    def spl(pts):
        return _closed([Q(*p) for p in pts])

    # ---- the silhouette ---------------------------------------------------------
    hc = Q(*head_c)
    # the head: a big 'hammer' head — steep forehead off the bill, a flat crown,
    # and the RAGGED crest raked back beyond the nape in three jagged points
    head_pts = crest or [(-3.0, -88.5), (20.0, -96.0), (16.5, -85.0), (33.0, -85.5), (22.0, -76.5),
                         (31.0, -66.0), (14.0, -60.0), (0.0, -70.0)]
    head = K.U(Point(*hc).buffer(head_r, quad_segs=32), poly(head_pts))
    bt = bill_tip
    bill = poly([(-15.0, -77.0), (bt[0], bt[1]), (-14.0, -58.0), (-6.0, -66.0)])
    body = spl([(-13.0, -54.0), (-21.0, -38.0), (-18.5, -16.0), (-7.0, -3.0), (6.0, -3.0), (16.5, -12.5),
                (21.5, -30.0), (18.5, -46.0), (9.0, -56.0)])
    tail = poly([(12.0, -6.0), (22.0, -12.0), (36.5, 15.0), (26.5, 20.5)])
    toes = poly([(-10.0, -4.0), (-11.0, 3.5), (-3.0, 5.5), (5.0, 4.0), (6.0, -4.0)])
    sil = K.U(head, bill, body, tail, toes)
    sil = sil.buffer(1.0, quad_segs=8).buffer(-1.0, quad_segs=8)
    kc = Q(0.0, knop_r)
    knop = Point(*kc).buffer(knop_r, quad_segs=24)

    # ---- inlays: the white neck ring (paper) and the breast belt (jade) -----------
    wing = spl([(8.0, -50.0), (-4.0, -43.0), (-9.0, -29.0), (-6.0, -12.0), (5.0, -1.0), (27.0, 13.0),
                (24.0, -8.0), (21.5, -32.0), (16.0, -48.0)])
    # the folded wing lies on the body and its tip crosses the tail: it joins
    # the silhouette (a sculpted wing standing proud of the body)
    sil = K.U(sil, wing).buffer(0.8, quad_segs=8).buffer(-0.8, quad_segs=8)
    wing = wing.intersection(sil.buffer(-0.2))
    wing = max(K._polys_of(wing), key=lambda g: g.area)
    # white throat and collar: the front of the neck down to the belt, and a
    # band round the nape
    ring = sil.intersection(poly([(-40.0, -57.0), (40.0, -62.0), (40.0, -52.0), (4.0, -46.0), (-40.0, -41.5)]))
    ring = ring.difference(bill.buffer(GAP_MARK + 0.5)).difference(wing.buffer(0.3))
    ring = max(K._polys_of(ring), key=lambda g: g.area)
    belt_g = sil.intersection(poly([(-40.0, -44.0), (30.0, -45.5), (30.0, -33.5), (-40.0, -32.0)]))
    belt_g = belt_g.difference(wing.buffer(0.3)).difference(ring)
    belt_g = max(K._polys_of(belt_g), key=lambda g: g.area)

    shape = K.U(sil, knop)
    lines = C.Frag()
    lines += K.clip_out(K.outline(knop), sil, eps=-0.5, trap=0.0)
    lines += K.outline(ring) + K.outline(belt_g) + K.outline(wing)
    # the gape: the bill's parting line from near the tip back into the face
    lines += K.seg(Q(bt[0] + 8.0, bt[1] - 0.5), Q(-12.0, -66.5), MEDIUM, role="gape")
    lines += K.dot(Q(*eye), 6.3, role="eye")
    win = wing.buffer(-(MEDIUM / 2 + GAP + FINE / 2 + 0.2))
    # coverts: one scalloped row across the wing, edge to edge (the covert
    # tips, bulging toward the tail); its ends butt on the wing outline
    for yy in (-33.0,)[:coverts]:
        y_ = fy + yy
        cut = wing.intersection(K.box(0, y_ - 0.5, 2000, y_ + 0.5))
        if cut.is_empty:
            continue
        x0, _, x1, _ = cut.bounds
        pa, pb = P(x0 - 1.0, y_ - 1.0), P(x1 + 1.0, y_ - 3.0)
        n_sc = max(3, int(round((x1 - x0) / 8.5)))
        dd, _ = K._scallops(pa, pb, n_sc, covert_sag)
        lines += K.clip_in(K.line(f"M{pa[0]:.3f} {pa[1]:.3f}" + dd, FINE, role="covert"), wing)
    # primaries: long stepped lines converging on the wing tip
    tip = Q(25.0, 10.0)
    for (a, L) in (((-3.0, -19.0), 0.84), ((4.0, -21.0), 0.80), ((11.0, -23.0), 0.74)):
        p0 = Q(*a)
        p1 = p0 + (tip - p0) * L
        lines += K.clip_in(K.seg(p0, p1, FINE, role="primary"), win)
    # gold everywhere but the inlays
    gold = sil.difference(ring).difference(belt_g)
    kn = knop.difference(sil.buffer(-0.3))
    fills = K.fill(gold, GOLD) + K.fill(belt_g, belt) + K.fill(kn, GOLD)
    part = K.Part(shape, fills, lines, {"head": hc, "knop": kc, "knop_r": knop_r, "sil": sil})
    return part.mirrored(fx) if facing > 0 else part


def kingfisher2(feet=(540.0, 176.0), *, knop_r=11.0, belt=JADE, facing=-1, head_c=(-2.0, -70.0), head_r=19.0,
                bill_tip=(-58.0, -68.0), bill_top=(-15.0, -80.0), bill_bot=(-14.0, -60.0),
                crest=((-8.0, -86.0), (6.0, -97.0), (10.0, -90.0), (22.0, -95.0), (20.0, -85.0), (31.0, -83.0),
                       (19.0, -74.0), (24.0, -64.0), (10.0, -62.0)),
                body=((-17.0, -58.0), (-22.5, -40.0), (-19.0, -18.0), (-8.0, -4.0), (6.0, -4.0), (17.5, -16.0),
                      (21.0, -36.0), (16.0, -54.0)),
                wing=((9.0, -52.0), (-3.0, -44.0), (-6.0, -27.0), (0.0, -10.0), (22.0, 9.0), (22.5, -14.0),
                      (19.5, -38.0), (15.0, -50.0)),
                tail=((10.0, -8.0), (21.0, -14.0), (31.0, 12.0), (21.0, 17.0)),
                collar=(-60.0, -52.0), belt_y=(-47.0, -36.0), eye=(-7.0, -73.5), lore=True, coverts=1,
                primaries=3, vent=None, belt_x_max=4.0, gape_from=18.0) -> K.Part:
    """The wrought-gold belted kingfisher, stockier: a big head sitting
    straight on the body (no neck, as the bird perches), a heavy dagger bill
    as long as the head, a ragged double crest raked back off the crown, a
    broad white collar (paper) right round the neck, the blue-grey breast
    belt (jade enamel) across the breast in front of the folded wing, a short
    square tail. Local frame: feet at the origin on the knop, facing −x."""
    fx, fy = feet

    def Q(x, y):
        return P(fx + x, fy + y)

    def poly(pts):
        return Polygon([tuple(Q(*p)) for p in pts]).buffer(0)

    def spl(pts):
        return _closed([Q(*p) for p in pts])

    hc = Q(*head_c)
    crest_poly = poly(list(crest) + [(head_c[0] + 4.0, head_c[1])])
    head = K.U(Point(*hc).buffer(head_r, quad_segs=32), crest_poly)
    bill = poly([bill_top, bill_tip, bill_bot, (-6.0, -68.0)])
    bod = spl(body)
    tl = poly(tail)
    toes = poly([(-10.0, -4.0), (-11.0, 3.5), (-3.0, 5.5), (5.0, 4.0), (6.0, -4.0)])
    sil = K.U(head, bill, bod, tl, toes, *( [poly(vent)] if vent else [] )).buffer(1.2, quad_segs=8).buffer(-1.2, quad_segs=8)
    kc = Q(0.0, knop_r)
    knop = Point(*kc).buffer(knop_r, quad_segs=24)
    wg = spl(wing)
    sil = K.U(sil, wg).buffer(0.8, quad_segs=8).buffer(-0.8, quad_segs=8)
    wg = wg.intersection(sil.buffer(-0.2))
    wg = max(K._polys_of(wg), key=lambda g: g.area)
    # the white collar: a band right round the neck (under the head, over the breast)
    y0, y1 = collar
    ring = sil.intersection(poly([(-40.0, y1 - 3.0), (40.0, y1 - 8.0), (40.0, y1 + 1.0), (-40.0, y1 + 6.0)]))
    ring = ring.difference(bill.buffer(GAP_MARK + 1.0)).difference(wg.buffer(0.3))
    ring = ring.difference(Point(*hc).buffer(head_r - 0.5, quad_segs=32).difference(K.box(0, fy + y1 - 6.0, 2000, 2000)))
    ring = max(K._polys_of(ring), key=lambda g: g.area) if not ring.is_empty else ring
    b0, b1 = belt_y
    belt_g = sil.intersection(poly([(-40.0, b0), (30.0, b0 - 2.0), (30.0, b1 - 2.0), (-40.0, b1)]))
    belt_g = belt_g.difference(wg.buffer(0.3)).difference(ring)
    # the belt crosses the breast only: it stops at the wing's leading edge
    # (no jade sliver pinched between the wing and the back contour)
    belt_g = belt_g.intersection(K.box(0, 0, fx + belt_x_max, 2000))
    belt_g = max(K._polys_of(belt_g), key=lambda g: g.area)
    shape = K.U(sil, knop)
    lines = C.Frag()
    lines += K.clip_out(K.outline(knop), sil, eps=-0.5, trap=0.0)
    lines += K.outline(ring) + K.outline(belt_g) + K.outline(wg)
    # the head's line where it sits on the collar is the collar's outline; the
    # gape: the bill's parting line from near the tip back into the face
    bt = bill_tip
    lines += K.seg(Q(bt[0] + gape_from, bt[1] - 0.2), Q(-13.0, -68.0), MEDIUM, role="gape")
    lines += K.dot(Q(*eye), 6.3, role="eye")
    lore_ko = None
    win = wg.buffer(-(MEDIUM / 2 + GAP + FINE / 2 + 0.2))
    cy_ = -33.0
    for yy in (cy_,)[:coverts]:
        y_ = fy + yy
        cut = wg.intersection(K.box(0, y_ - 0.5, 2000, y_ + 0.5))
        if cut.is_empty:
            continue
        x0, _, x1, _ = cut.bounds
        pa, pb = P(x0 - 1.0, y_ - 1.0), P(x1 + 1.0, y_ - 3.0)
        n_sc = max(3, int(round((x1 - x0) / 8.5)))
        dd, _ = K._scallops(pa, pb, n_sc, -2.6)
        lines += K.clip_in(K.line(f"M{pa[0]:.3f} {pa[1]:.3f}" + dd, FINE, role="covert"), wg)
    tip = Q(22.0, 8.0)
    for (a, L) in (((-2.0, -20.0), 0.84), ((5.0, -22.0), 0.80), ((12.0, -24.0), 0.74))[:primaries]:
        p0 = Q(*a)
        p1 = p0 + (tip - p0) * L
        lines += K.clip_in(K.seg(p0, p1, FINE, role="primary"), win)
    gold = sil.difference(ring).difference(belt_g)
    if lore:
        # the white spot before the eye (the belted kingfisher's loral spot): a paper knockout
        lp = Q(eye[0] - 8.5, eye[1] - 3.0)
        lore_ko = Point(*lp).buffer(2.4, quad_segs=16)
        gold = gold.difference(lore_ko)
        lines += K.outline(lore_ko, FINE, role="lore")
    # no gold where the bird is thinner than its contour (the bill tip, the
    # crest points): the ink covers them anyway, and a plate hidden under
    # an ink solid is a QA 4c trap
    from art._kc_util import visible_fill
    gold = visible_fill(gold, lines, sil)
    kn = knop.difference(sil.buffer(-0.3))
    fills = K.fill(gold, GOLD) + K.fill(belt_g, belt) + K.fill(kn, GOLD)
    part = K.Part(shape, fills, lines, {"head": hc, "knop": kc, "knop_r": knop_r, "sil": sil})
    return part.mirrored(fx) if facing > 0 else part


def kingfisher3(feet=(540.0, 176.0), *, knop_r=10.5, plate=None, knop_band=True, belt=JADE, facing=-1, head_c=(-2.0, -70.0),
                head_r=19.0, bill_tip=(-58.0, -68.0), bill_top=(-15.0, -80.0), bill_bot=(-14.0, -60.0),
                crest=((-8.0, -86.0), (6.0, -97.0), (10.0, -90.0), (22.0, -95.0), (20.0, -85.0), (31.0, -83.0),
                       (19.0, -74.0), (24.0, -64.0), (10.0, -62.0)),
                body=((-17.0, -58.0), (-22.5, -40.0), (-19.0, -18.0), (-8.0, -4.0), (6.0, -4.0), (17.5, -16.0),
                      (21.0, -36.0), (16.0, -54.0)),
                wing=((9.0, -52.0), (-3.0, -44.0), (-6.0, -27.0), (0.0, -10.0), (22.0, 9.0), (22.5, -14.0),
                      (19.5, -38.0), (15.0, -50.0)),
                tail=((10.0, -8.0), (21.0, -14.0), (31.0, 12.0), (21.0, 17.0)),
                collar=(-60.0, -52.0), belt_y=(-47.0, -36.0), eye=(-7.0, -73.5), vent=None, belt_x_max=4.0,
                gape_from=18.0, toes=((-9.0, -4.0), (-10.0, 2.5), (-3.0, 4.0), (4.0, 2.5), (5.0, -4.0)),
                covert_rows=(-36.5, -28.0), covert_w=8.5, covert_sag=-2.4, covert_rise=3.0,
                primaries=(((-1.0, -19.0), 0.86), ((6.0, -20.5), 0.82), ((13.0, -22.0), 0.76)), prim_tip=(22.0, 8.0),
                bands=(-29.0, -22.0, -15.0, -8.0), band_sag=-1.2, covert_front=5.8, ink_pockets=False) -> K.Part:
    """The wrought-gold belted kingfisher, finished as a goldsmith's piece
    (director's note: the smooth cut-out read as a toy):

    * the folded wing CHASED: ``covert_rows`` staggered rows of scalloped
      coverts (FINE, bulging toward the tail, butting on the wing outline)
      over three stepped primaries converging on the wing tip;
    * the breast BANDED: the jade enamel belt, then FINE chased ``bands``
      across the gold breast from the front contour to the wing's leading
      edge (butting on both: no free ends);
    * a MOUNT where the bird meets the staff: the toes grip a flat perch
      plate (``plate`` = half-width, height), which stands on a ball knop of
      radius ``knop_r`` — the finial's own collar and knop, seated on the
      staff's top collar.

    Local frame: feet at the origin (the plate's top), facing −x."""
    fx, fy = feet

    def Q(x, y):
        return P(fx + x, fy + y)

    def poly(pts):
        return Polygon([tuple(Q(*p)) for p in pts]).buffer(0)

    def spl(pts):
        return _closed([Q(*p) for p in pts])

    hc = Q(*head_c)
    crest_poly = poly(list(crest) + [(head_c[0] + 4.0, head_c[1])])
    head = K.U(Point(*hc).buffer(head_r, quad_segs=32), crest_poly)
    bill = poly([bill_top, bill_tip, bill_bot, (-6.0, -68.0)])
    bod = spl(body)
    tl = poly(tail)
    tz = poly(toes)
    sil = K.U(head, bill, bod, tl, tz, *([poly(vent)] if vent else [])).buffer(1.2, quad_segs=8).buffer(-1.2, quad_segs=8)
    wg = spl(wing)
    sil = K.U(sil, wg).buffer(0.8, quad_segs=8).buffer(-0.8, quad_segs=8)
    wg = wg.intersection(sil.buffer(-0.2))
    wg = max(K._polys_of(wg), key=lambda g: g.area)
    # ---- the mount: perch plate on a ball knop -----------------------------------
    if plate:
        pw, ph = plate
        plate_g = K.R(K.rrect(fx - pw, fy, fx + pw, fy + ph, 2.6))
    else:
        ph, plate_g = 0.0, Polygon()
    kc = Q(0.0, ph + knop_r - 1.0)
    knop = Point(*kc).buffer(knop_r, quad_segs=24)
    # ---- inlays: the white collar (paper) and the breast belt (jade) --------------
    y0, y1 = collar
    ring = sil.intersection(poly([(-40.0, y1 - 3.0), (40.0, y1 - 8.0), (40.0, y1 + 1.0), (-40.0, y1 + 6.0)]))
    ring = ring.difference(bill.buffer(GAP_MARK + 1.0)).difference(wg.buffer(0.3))
    ring = ring.difference(Point(*hc).buffer(head_r - 0.5, quad_segs=32).difference(K.box(0, fy + y1 - 6.0, 2000, 2000)))
    ring = max(K._polys_of(ring), key=lambda g: g.area) if not ring.is_empty else ring
    b0, b1 = belt_y
    belt_g = sil.intersection(poly([(-40.0, b0), (30.0, b0 - 2.0), (30.0, b1 - 2.0), (-40.0, b1)]))
    belt_g = belt_g.difference(wg.buffer(0.3)).difference(ring)
    belt_g = belt_g.intersection(K.box(0, 0, fx + belt_x_max, 2000))
    belt_g = max(K._polys_of(belt_g), key=lambda g: g.area)
    shape = K.U(sil, plate_g, knop)
    lines = C.Frag()
    lines += K.clip_out(K.outline(knop), K.U(sil, plate_g), eps=-0.5, trap=0.0)
    lines += K.clip_out(K.outline(plate_g), sil, eps=-0.5, trap=0.0)
    lines += K.outline(ring) + K.outline(belt_g) + K.outline(wg)
    bt = bill_tip
    lines += K.seg(Q(bt[0] + gape_from, bt[1] - 0.2), Q(-13.0, -68.0), MEDIUM, role="gape")
    lines += K.dot(Q(*eye), 6.3, role="eye")
    # ---- the chased wing: staggered scalloped covert rows, stepped primaries --------
    # the covert rows butt the wing's back edge; at its leading edge they stop
    # ``covert_front`` inside (the breast bands butt that edge from outside)
    wmx = float(wg.centroid.x)
    cov_zone = K.U(wg.buffer(-covert_front), wg.intersection(K.box(wmx, 0, 2000, 2000)))
    for j, yy in enumerate(covert_rows):
        y_ = fy + yy
        cut = cov_zone.intersection(K.box(0, y_ - 0.5, 2000, y_ + 0.5))
        if cut.is_empty:
            continue
        x0, _, x1, _ = cut.bounds
        pa = P(x0, y_)
        pb = P(x1 + 2.0, y_ - covert_rise)
        n_sc = max(2, int(round((pb[0] - pa[0]) / covert_w)))
        dd, _ = K._scallops(pa, pb, n_sc, covert_sag)
        lines += K.clip_in(K.line(f"M{pa[0]:.3f} {pa[1]:.3f}" + dd, FINE, role="covert"), cov_zone)
    win = wg.buffer(-(MEDIUM / 2 + GAP + FINE / 2 + 0.2))
    tip = Q(*prim_tip)
    for (a, L) in primaries:
        p0 = Q(*a)
        p1 = p0 + (tip - p0) * L
        lines += K.clip_in(K.seg(p0, p1, FINE, role="primary"), win)
    # ---- the banded breast: chased bands from the front contour to the wing -----------
    breast = sil.difference(wg).difference(belt_g.buffer(0.2)).difference(ring.buffer(0.2))
    breast = breast.intersection(K.box(0, fy + belt_y[1], fx + belt_x_max + 20.0, fy - 2.0))
    for yy in bands:
        y_ = fy + yy
        d = K.arc_sag(P(fx - 40.0, y_ + 2.0), P(fx + 10.0, y_ - 1.0), band_sag)
        lines += K.clip_in(K.line(d, FINE, style="hatch", role="band"), breast)
    gold = sil.difference(ring).difference(belt_g)
    from art._kc_util import visible_fill
    gold = visible_fill(gold, lines, K.U(sil, plate_g, knop))
    if knop_band:
        # the turned knop's fillet: a FINE band round its equator
        eq = K.clip_in(K.seg(Q(-knop_r - 2.0, ph + knop_r - 1.0), Q(knop_r + 2.0, ph + knop_r - 1.0), FINE,
                             role="knop"), knop)
        lines += K.clip_out(eq, sil, eps=-0.5, trap=0.0)
    mount = K.U(plate_g, knop).difference(sil.buffer(-0.3))
    fills = K.fill(gold, GOLD) + K.fill(belt_g, belt) + K.fill(mount, GOLD)
    if ink_pockets:
        # where the bird is too thin for gold (the dagger bill's tip either side of the gape, the
        # notch between wing tip and tail) the ground showed through inside the contour: ink it
        ink = shapely.union_all([K.G.to_shape(m.d, tol=K.FLAT_TOL) if m.kind == "fill" else K.R(K.G.from_skia(m.skia()))
                                 for m in lines.marks if m.d]
                                + [sil.boundary.buffer(CONTOUR / 2, quad_segs=8)])
        bare = sil.difference(ink).difference(gold).difference(belt_g).difference(ring.buffer(1.0))
        bare = [g for g in K._polys_of(bare) if g.area > 0.05]
        if bare:
            fills += K.fill(K.U(*bare).buffer(1.0, quad_segs=6).intersection(sil), K.INK)
    part = K.Part(shape, fills, lines, {"head": hc, "knop": kc, "knop_r": knop_r, "sil": sil,
                                        "mount_bottom": float(kc[1] + knop_r)})
    return part.mirrored(fx) if facing > 0 else part
