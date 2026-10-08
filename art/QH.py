"""Q♥ · The Aquamaid Queen: woven robes and two cuff-emerging hands."""
from __future__ import annotations

import numpy as np
import shapely
from dataclasses import replace
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck import frames as F
from deck.motifs import core as C

from art import _qh_attr as A
from art import _qh_body as B
from art import _qh_cap as CP
from art import _qh_face as QF
from art import _qh_continuous as QC
from art import _qh_head as H
from art import _qh_tidy as TD

P = K.P
DOUBLE_HEAD = "continuous"
SEAM = -42
HEAD = (383.0, 204.0)
# the cap sphere sits back on the head (a 3/4-right head shows the back of the
# skull on the viewer's left): centred left of the face so its far limb falls
# just outside the far temple and the gold rim ends there instead of jutting
# past the face like a visor
CAP_C, CAP_R = (362.0, 194.0), 62.0
# the air-hose ribbon (§H.5, director's follow-up): no tube, no nozzle — a
# ribbon of graduated free bubbles on a gentle S: out of the dip behind the
# far shoulder (between the hair's end and the sleeve's crown), a small bow
# toward the stem, a longer one back toward her cap past the flower's near
# petal, and out toward the top-right corner, the last bubble 13.9 px inside
# the gold rule (y 51). Four Ø4.2 dots (the smallest legal dot, §B.2, for the
# brief's Ø3) then FINE rings Ø5.2 → 8 (centreline; the hole ≥ 3 px), the
# clear gaps widening ×1.1 as they rise
AIR = [(497, 299), (505, 262), (499, 212), (485, 165), (485, 124), (495, 94), (511, 71)]
AIR_SIZES = [("dot", 4.2)] * 4 + [("ring", round(5.2 * (8.0 / 5.2) ** (k / 11), 2)) for k in range(12)]
AIR_GROWTH = 1.1
HAIR_N = [(320, 190), (302, 226), (292, 262), (278, 290), (252, 305), (228, 302), (214, 290)]
# ONE ring of eight long petals radiating from the pearl to the rim, each a
# vesica with a FINE midrib and one half hatched across it (§B.2's leaf rule),
# overlapping like a flower seen from above: at 1× it reads as a petal cap,
# where three rows of foreshortened scallops read as a helmet
PETAL_ROWS = (dict(u0=0.02, u1=0.97, n=8, phase=0.5, widen=1.55),)
CAP_KW = dict(yaw=24, pitch=16, tilt=10, t_front=68.5, t_back=112, t_side=100, rim_h=11)
PETAL_KW = dict(lift=0.03, rib=True, tip="vesica", shoulder=0.55, root=0.25, hatch_rel=90.0, min_area=320.0, hatch_side=-1)
PEARL_KW = dict(d=20.0, r=1.0)          # big enough to hide where the petals' roots converge
SNAP = True
RIM_FIRST = False          # True: the petals (tips down) hang over the gold rim
RADIAL = None             # dict(n=, phase=, …): screen-space vesica petals (CP.radial_petals)
# v6: the cap as a flat ROSETTE of the deck's leaf round the pearl (CP.rosette).
# The petal cap read as a helmet or a beanie while its petals followed the
# skull (rows of foreshortened scallops, a smooth dome silhouette); drawn flat,
# nine vesica petals radiate from the gold pearl like a dahlia and lap each
# other PINWHEEL-fashion, so each shows the same hatched half (§B.2's leaf
# rule) and their tips scallop the silhouette all round: at 1× a 1950s petal
# cap. A jade dome (centre, rx, ry) under the petals runs down to the gold
# band, which lies in front of them.
ROSETTE = dict(
    dome=((362.0, 168.0), 62.0, 60.0), pole=(360.0, 136.0), hatch_side=+1, pearl=22.0,
    # the gold band lies IN FRONT: the petals tuck under it (the dome runs to
    # its lower edge), so their edges cross the band's edge steeply, well
    # back from the tips; the band ends square short of the far limb
    rim_front=True, rim_in=1.0, rim_x1=418.0,
    # the base is inset under the petals (the notches between the tips are
    # cut by petal crossing petal) and never stands proud of them
    inset=9.0, core=16.0,
    tiers=[dict(angles=[-70, -30, 10, 50, 90, 130, 170, 210, 250], frac=1.0, over=4.0, width=(0.55, 22.0, 34.0),
                bend=0.0, r0=8.0, seam=90.0, shoulder=0.5)])

# the arrowhead leaf on a slim gold petiole into its sinus; the notch between
# the lobes is opened (13 × 22) so the petiole's run up it keeps its gold
# clear of the converging lobe edges, and the jade stops 3.3 px short of the
# sharp lobe tips (a fill wholly under the CONTOUR there is a hidden plate, 4c)
# courts2 review: the near lobe ran down the stem 1-2 px off its left contour
# (a gold sliver, QA 12) and the petiole's square root end drew a pointed
# pocket on the sleeve's crown. The leaf keeps its established tilt and size;
# it sits 3 px higher and 2 px further out, with the near lobe foreshortened
# (18 × 35 against the far lobe's 21 × 36: it turns toward the viewer), so the
# stem shows as a ≥ 5 px gold strip beside it and its tip lies on the stem's
# gold. The petiole comes out from BEHIND the stem (no butt end), leaving it
# at 50° from the vertical ≥ 5 px above the sleeve's crown, and sweeps up on
# one gentle arc into the sinus — a leaf stalk springing from the stem (the
# first round's J, square out of the stem and straight up, read as a hook)
PETIOLE = dict(w=7.0, turtle=((546.0, 299.8), -40.0, (("fd", 20.5), ("arc", 16.0, -41.0), ("fd", 18.0))))
LEAF = dict(sinus=(570.0, 259.0), tilt=9.0, blade=80.0, half_w=23.0, lobe=(21.0, 36.0), lobe_l=(18.0, 35.0),
            notch=(13.0, 22.0), fill_open=3.3, rib_from=-8.0, vein_from=-7.0, vein_dx=0.5)
# A single graduated pearl strand, with end beads tucked into the neck edges.
COLLAR = (((364.5, 283.0), (412.0, 281.0), 5.5, 370.8, 405.05, 6, 7.6, 6.4),)
# the far lock comes out beside the band's square far end with a SHOULDER: from
# the band's top corner along its top edge, round and down into the lock's own
# outer edge — a strip of hair ≥ 5 px wide from the band down (the lock's top
# was a wedge tapering into the face contour, and heal dropped the contour)
FAR_SHOULDER = dict(start=(418.0, 173.6), h0=36.0, join_y=232.0, via=((429.0, 181.0), (435.0, 198.0)),
                    hidden=((410.0, 232.0), (404.0, 200.0), (408.0, 178.0), (416.5, 176.0)))
REST_AT = (334, 424)
HAND_S = 0.82
# the stem sleeve is cut short by the robe's edge: two turn-back bands, no pearl row
RIGHT_TRIM = dict(second_band=20.0)
RIGHT_SLEEVE = dict(run=40.0, reach=0.0, bell=5.0, neck=10.0, curl=-5.0)
LEFT_SLEEVE = dict(run=54.0, reach=0.0, bell=8.0, neck=12.0, curl=-5.0)


def _stem():
    # the upper collar (on paper, under the CONTOUR) keeps its gold 1 px past
    # the shaft (QA 4c); the lower one, inside the sleeve under a MEDIUM
    # outline, is gold to its outline (a trap there left paper slits)
    stem = A.stem((546, 479), (546, 116), w=19.0,
                  nodes=((479 - 334) / 363, (479 - 185) / 363),
                  collar_trap=(None, 1.0))
    for y in (145, 228, 272, 378):
        # The leaf passes over the right side at y228; keep its engraving
        # wholly on the exposed gold, not sticking out of the blade contour.
        x1 = 544.5 if y == 228 else 552.5
        stem.lines += K.seg((539.5, y), (x1, y), K.FINE, role="stem-engraving")
    return stem


class Scene(K.Scene):
    """Keep shared outlines intact and join touching pearl plates before healing."""
    def compose(self, *, heal_gaps=True, **kwargs):
        artwork = super().compose(heal_gaps=False, **kwargs)
        gold = artwork.select(lambda m: m.kind == "fill" and m.layer == "gold")
        artwork = artwork.select(lambda m: not (m.kind == "fill" and m.layer == "gold")) \
            + K.fill(gold.shape().buffer(0.6).buffer(-0.6), K.GOLD)
        if heal_gaps:
            self.heal_log = []
            artwork = K.heal(artwork, log=self.heal_log,
                             keep_roles=("contour", "grip-edge", "leaf-vein", "cuffline"))
            # heal trims a web line off both its notch and the palm contour;
            # the short dash it leaves floats in the palm as a stray mark
            artwork = artwork.select(lambda m: not (
                m.role == "finger" and m.kind == "stroke"
                and sum(LineString(pts).length for pts, _ in K.G.flatten(m.d, K.FLAT_TOL)) < 8.0))
        # Finish the three-way fold joins after foreground contour clipping.
        artwork += K.c2(K.dot((491.68, 312.15), K.CONTOUR, role="contour"))
        # Union just the shared junctions. Keep legal FINE textile strokes as
        # strokes, rather than interpreting them as solid knockout bridges.
        ink = artwork.select(lambda m: m.layer == "ink")
        joins = K.c2(K.box(481, 303, 504, 342))
        joined = ink.shape().buffer(1.6).buffer(-1.6).intersection(joins)
        # A stroke end poking a fraction of a px into the box is already drawn
        # by its clipped stroke's cap; as a fill it would be a sub-hairline sliver.
        joined = K.U(*[g for g in K._polys_of(joined) if not g.buffer(-K.HAIR_W / 2).is_empty])
        # A colour crumb walled in by the joined ink (the bodice tip between
        # the lock and mantle outlines) is filled with the ink around it. The
        # plates run on under the ink, so only their visible part is tested.
        crumbs = [g for m in artwork.marks if m.kind == "fill" and m.layer in ("jade", "red", "gold")
                  for g in K._polys_of(K.R(m.d).intersection(joins).difference(joined))
                  if g.area < 60 and g.buffer(1.0).difference(K.U(joined, g)).area < 0.5]
        crumbs = K.U(*crumbs) if crumbs else Polygon()
        artwork = artwork.select(lambda m: m.layer != "ink") \
            + K.clip_out(ink, joins, eps=0, trap=0) \
            + K.fill(K.U(joined, crumbs.buffer(0.3)).intersection(joins), K.INK, role="contour")
        # Retract hidden plate tails only at their local hair/robe contacts.
        # Broad ink-based clipping would carve paper rims along whole edges.
        tails = {"jade": K.c2(K.box(486, 306, 501, 314.5)),
                 "red": K.c2(K.box(486, 309, 500, 338)),
                 "gold": K.c2(K.box(551, 200, 562, 224))}
        ink_core = artwork.select(lambda m: m.layer == "ink").shape().buffer(-0.6)
        fills = artwork.select(lambda m: m.kind == "fill" and m.layer != "ink")
        artwork = artwork.select(lambda m: m.kind != "fill" or m.layer == "ink")
        for color in (K.JADE, K.RED, K.GOLD):
            marks = fills.select(lambda m: m.color == color)
            plate = marks.shape()
            layer = marks.marks[0].layer
            if layer in tails:
                plate = plate.difference(ink_core.intersection(tails[layer]))
            plate = plate.difference(crumbs)
            artwork += K.fill(plate, color)
        return artwork


def sleeve_end(hand, *, run, reach=0.0, bell=9.0, neck=3.0, curl=5.0, soften=3.5):
    """A short bell of the mantle's own jade, running from the cuff mouth back
    toward the mantle edge. It is a lobe of the garment, never a separate cuff."""
    u = hand.wrist_dir
    w = P(hand.wrist) - u * reach
    n = np.array([u[1], -u[0]])
    half = hand.wrist_w / 2
    base = w + u * run
    shape = K.R(K.Path(w + n * (half + bell)).sag(w - n * (half + bell), curl)
                .sag(base - n * (half + neck), -2.0).line(base + n * (half + neck))
                .sag(w + n * (half + bell), -2.0).close().d)
    return shape.buffer(-soften).buffer(soften)


def sleeved_hand(hand, sleeve):
    """The hand beyond its cuff mouth; the sleeve's edge is the hand's contour."""
    region = hand.shape.difference(sleeve)
    # hand5's heel bulges a hair past the sleeve's edge; that thin lens doubles
    # the outline into a lump at the cuff corner, so open it near the sleeve
    near = sleeve.buffer(4.0)
    region = K._biggest(K.U(region.difference(near),
                            region.buffer(-1.6).buffer(1.6).intersection(near)))
    inner = hand.hand.meta.get("inner", C.Frag())
    return K.Part(region, C.Frag(), K.outline(region, role="contour") + K.clip_in(inner, region.buffer(-5.0)),
                  {**hand.hand.meta, "hand_region": region})


def _course(hand, sleeve, sleeve_kw, offset, inset):
    """A curve parallel to the sleeve mouth ``offset`` px behind it, cut by the
    sleeve's edge (shrunk by ``inset``): it meets the sleeve sides squarely."""
    u = hand.wrist_dir
    n = np.array([u[1], -u[0]])
    half = hand.wrist_w / 2 + sleeve_kw["bell"]
    t = np.linspace(-half - 4.0, half + 4.0, 60)
    # the parabola runs on past the mouth corners: flattening it there put a
    # kink in a course that reaches the flared sleeve's sides
    sag = sleeve_kw["curl"] * (1.0 - (t / half) ** 2)
    pts = [P(hand.wrist) - u * sleeve_kw["reach"] + n * a + u * (offset + b) for a, b in zip(t, sag)]
    cut = LineString(pts).intersection(sleeve.buffer(0.5 - inset))
    if cut.geom_type != "LineString":
        cut = max(K._lines_of(cut), key=lambda g: g.length)
    return cut


def cuff_trim(hand, sleeve, sleeve_kw, *, band=10.0, pearl_at=21.0, second_band=None):
    """A turn-back band parallel to the cuff mouth with a row of pearls behind it
    (or, on a sleeve too short for pearls, a second band)."""
    edge = _course(hand, sleeve, sleeve_kw, band, 1.0)
    lines = K.line(C.polyline_d(np.asarray(edge.coords)), K.MEDIUM, role="cuffline")
    if second_band is not None:
        edge2 = _course(hand, sleeve, sleeve_kw, second_band, 1.0)
        lines += K.line(C.polyline_d(np.asarray(edge2.coords)), K.MEDIUM, role="cuffline")
        return K.Part(Polygon(), C.Frag(), lines)
    row = _course(hand, sleeve, sleeve_kw, pearl_at, 9.0)
    pearls = B.pearls_on(np.asarray(row.coords), d_max=7.0, d_min=7.0, gap=0.0, even=True)
    ring = C.Frag([replace(m, role="contour") for m in pearls.lines.marks])
    return K.Part(pearls.shape, pearls.fills, lines + ring)


def figure():
    sc = Scene()
    fc = QF.queen_face(HEAD, wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)

    # ---- behind everything: the air rising from behind the far shoulder ------------------
    sc.add("bubbles", A.bubble_ribbon(AIR, AIR_SIZES, growth=AIR_GROWTH), None, sil=False)

    hn = H.lock(HAIR_N, 54.0, n=5, taper=0.42, taper_from=0.45,
                side=+1, bubbles=(4.2, 5.6, 7.0), bubble_lane=2, bubble_at=0.55)
    hf = H.lock([(426, 188), (437, 218), (441, 250), (440, 278), (451, 300), (469, 304)], 40.0, n=4, side=-1)
    # Both hands come out of bell sleeves that are lobes of the jade mantle.
    h = K.hand5((546, 434), -90, "wrap", size=K.hand_size(fc) * HAND_S,
                hand="L", view="back", grip_w=19)
    right_sleeve = sleeve_end(h, **RIGHT_SLEEVE)
    right_hand = sleeved_hand(h, right_sleeve)
    # The original wrist (300,452) straddles the approved -42° seam.
    # Shift the same resting gesture up onto the chest, not the seam.
    resting = K.hand5((REST_AT), -24, "rest", size=K.hand_size(fc) * HAND_S,
                      hand="R", view="back", curl=6, spread=3)
    left_sleeve = sleeve_end(resting, **LEFT_SLEEVE)
    left_hand = sleeved_hand(resting, left_sleeve)
    pet = A.petiole(**PETIOLE)
    leaf = _leaf()
    flower = [p for _, p in A.flower3((546, 112), r_petal=50, petal_w=40,
                                     centre_r=12.5, squash=0.78, tilt=-10,
                                     notch=5, centre="scallop", hatch_rel=0)]
    held = QC.held(_stem(), pet, leaf, flower, right_hand)
    trim = K.Part(Polygon(), C.Frag(), C.Frag())
    for hand, sleeve, kw, trim_kw in ((h, right_sleeve, RIGHT_SLEEVE, RIGHT_TRIM),
                                      (resting, left_sleeve, LEFT_SLEEVE, {})):
        part = cuff_trim(hand, sleeve, kw, **trim_kw)
        trim = K.Part(K.U(trim.shape, part.shape), trim.fills + part.fills, trim.lines + part.lines)
    clasp = K.lion_clasp((390, 330), 40)
    robe = QC.garments(K.U(held.shape, left_hand.shape, hn.shape, hf.shape),
                       K.U(hn.shape, hf.shape), sleeves=left_sleeve, inked=right_sleeve, trim=trim,
                       hands=K.U(right_hand.shape, left_hand.shape),
                       clear=clasp.lines.select(lambda m: m.role == "ripple").shape(),
                       seam=LineString(F.seam_points(SEAM)))
    sc.gown_bodice = robe.meta["bodice"]
    robe = K.Part(robe.shape,
                  K.clip_out(robe.fills, clasp.meta["silhouette"], eps=0, trap=0) + clasp.fills,
                  K.clip_out(robe.lines, clasp.meta["silhouette"], eps=0.2, trap=0) + clasp.lines)
    robes = QC.merge([robe, left_hand])
    sc.part("robes", robes)
    sc.part("sagittaria+hand+cuff", held)

    # ---- hair (behind the head), neck, head, cap ---------------------------------------------
    sc.part("hairN", hn)
    sc.part("hairF", hf)
    # A single clear pearl strand, not two rows pinched by the neckline.
    nk = K.neck(fc, bottom=299.0, width=35.0)
    collar = _collar_strand(0, nk.shape)
    nk = K.Part(nk.shape, C.Frag(),
                K.clip_out(nk.lines, collar.shape, eps=0.5, trap=0) + collar.lines)
    sc.part("neck+pearls", K.Part(K.U(nk.shape, collar.shape), collar.fills, nk.lines))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    cap = CP.Cap(CAP_C, CAP_R, **CAP_KW)
    if ROSETTE:
        _rosette_cap(sc, cap, ROSETTE, hair=hn.shape)
    else:
        _sphere_cap(sc, cap)
    # the lock runs on up under the rim to the face: no pinhole where the rim,
    # the hair and the face contour met by the near temple (courts2 review)
    # and fills the notch under the rim's near end (the hair's edge ran 5 px in
    # under the band's end: a knuckle in the CONTOUR)
    TD.fill_temple(sc, "hairN", hn, K.GOLD, run_on=(("capbase", "petal", "rim"), (0.0, 180.0, 330.0, 230.0)))
    # the far lock likewise runs up under the band's square far end (rim end,
    # face and lock top met within 8 px there: an ink knot by the far temple)
    TD.lock_shoulder(sc, "hairF", hf, K.GOLD, **FAR_SHOULDER, face=fc.skin)

    # Petals, gold rim and pearl share one cap silhouette and trapped plates.
    cap_items = [it for it in sc.items if it.name.startswith(("capbase", "petal", "rim", "pearl"))]
    cap_part = QC.merge([K.Part(it.occ,
                                it.frag.select(lambda m: m.kind == "fill"),
                                it.frag.select(lambda m: m.kind != "fill")) for it in cap_items])
    far_hair = next(it.occ for it in sc.items if it.name == "hairF")
    cap_part = K.Part(cap_part.shape, cap_part.fills,
                      K.clip_out(cap_part.lines, far_hair.buffer(-0.2), eps=0, trap=0))
    sc.items = [it for it in sc.items if it not in cap_items]
    sc.part("petal-cap", cap_part)
    # Hair, skin, pearls and cap are one portrait, with one gold plate and
    # no barely abutting same-ink patches at the temples.
    portrait_items = sc.items[3:]
    portrait = QC.merge([K.Part(it.occ,
                               it.frag.select(lambda m: m.kind == "fill"),
                               it.frag.select(lambda m: m.kind != "fill"))
                         for it in portrait_items])
    face_region = K.R(fc.head).difference(cap_part.shape)
    portrait = K.Part(portrait.shape, portrait.fills,
                       portrait.lines + K.outline(face_region, role="face-edge"))
    # The gold lock and gown meet here under one outline, not a paper wedge.
    lock_gold = portrait.fills.select(lambda m: m.layer == "gold").shape()
    portrait.fills += K.fill(lock_gold.buffer(2.5).intersection(
        K.box(481, 306, 493, 320)).intersection(portrait.shape), K.GOLD)
    portrait.fills += K.fill(K.box(483, 309, 488, 315).intersection(
        K.U(portrait.shape, portrait.lines.shape())), K.GOLD)
    sc.items = sc.items[:3]
    sc.part("portrait", portrait)
    return sc


def _rosette_cap(sc, cap, cfg, hair=None):
    (cx, cy), rx, ry = cfg["dome"]
    rim = cap.rim()
    if cfg.get("rim_x1"):
        # end the band square short of the far limb (its taper was a gold sliver)
        rs = rim.shape.intersection(K.box(0, 0, cfg["rim_x1"], 1050))
        rs = max(K._polys_of(rs), key=lambda g: g.area)
        rim = K.Part(rs, K.fill(rs, K.GOLD), K.outline(rs), {})
    dome = K.R(C.ellipse_d(cx, cy, rx, ry))
    # the dome stands on the rim's middle line (the back tier's tips hang
    # over the upper half of the band)
    rs = rim.shape
    x0r, _, x1r, _ = rs.bounds
    xs = np.linspace(x0r + 1.0, x1r - 1.0, 60)
    mid = []
    for x in xs:
        g = rs.intersection(K.box(x - 0.01, 0, x + 0.01, 1050))
        if g.is_empty:
            continue
        b = g.bounds
        mid.append((x, b[1] + cfg.get("rim_in", 0.5) * (b[3] - b[1])))
    mid = [(0.0, mid[0][1])] + mid + [(750.0, mid[-1][1])]
    above = Polygon(mid + [(750.0, 0.0), (0.0, 0.0)])
    dome = dome.intersection(above)
    # the jade base fills the notches between the petals: inset from the free
    # silhouette (so the tips scallop it) but running down under the rim (a
    # base edge alongside the band would trap a jade sliver: QA 4c)
    ins = cfg.get("inset", 7.0)
    band = dome.difference(dome.buffer(-ins))
    base = dome.difference(band.difference(rim.shape.buffer(ins + 6.0)))
    if cfg.get("core"):
        # away from the rim the base shrinks under the petals: the notches
        # between the tips are then cut by petal crossing petal (no base edge
        # meeting a petal edge at a shallow angle under the CONTOUR: QA 4c)
        base = dome.buffer(-cfg["core"]).union(base.intersection(rim.shape.buffer(ins + 6.0)))
    base = max(K._polys_of(base.buffer(-0.5).buffer(0.5)), key=lambda g: g.area)
    petals = CP.rosette(cfg["pole"], dome, cfg["tiers"], hatch_side=cfg.get("hatch_side", +1),
                        stop=rim.shape if cfg.get("stop_gap") else None, stop_gap=cfg.get("stop_gap") or 0.0,
                        clip=above if cfg.get("rim_front") else None)
    if cfg.get("core"):
        # ... and never stands proud of the petals by the rim either
        hull = K.U(*[pt.shape for _, pt in petals]).convex_hull
        base = max(K._polys_of(base.intersection(hull.buffer(-1.0))), key=lambda g: g.area)
    if hair is not None:
        # the band's near end ends flush on the run from the cap into the hair
        # (it stood 3 px proud there: a knuckle in the CONTOUR)
        rim = TD.trim_rim_end(rim, [base] + [pt.shape for _, pt in petals], hair, x_max=314.0, y_from=180.0)
    sc.part("capbase", K.Part(base, K.fill(base, K.JADE), K.outline(base), {}))
    if not cfg.get("rim_front"):
        sc.part("rim", rim)
    for nm, pt in petals:
        sc.part(nm, pt)
    if cfg.get("rim_front"):
        # the band in front: the petals tuck under it (their edges cross the
        # band's edge steeply, well back from the tips)
        sc.part("rim", rim)
    d = cfg.get("pearl", 18.0)
    pc = P(cfg["pole"])
    disc = K.R(K.circle(pc, d / 2))
    hole = K.R(K.circle(pc + P(-d * 0.18, -d * 0.18), 4.2 / 2))
    sc.part("pearl", K.Part(disc, K.fill(disc.difference(hole), K.GOLD), K.outline(disc), {"c": pc}))


def _sphere_cap(sc, cap):
    sc.part("capbase", cap.base())
    if RIM_FIRST:
        sc.part("rim", cap.rim())
    if RADIAL:
        dome = cap.base().shape
        for phi, pt in CP.radial_petals(cap, clip=dome, **RADIAL):
            sc.part(f"petal_{phi:.0f}", pt)
    else:
        dome = cap.base().shape
        for k, rw in enumerate(PETAL_ROWS):
            for phi, pt in cap.petals(**{**PETAL_KW, **rw}):
                sc.part(f"petal{k}_{phi:.0f}", CP.snap_to_limb(pt, dome) if SNAP else pt)
    if not RIM_FIRST:
        sc.part("rim", cap.rim())
    sc.part("pearl", cap.pearl(**PEARL_KW))


def _leaf():
    """The arrowhead leaf (A.arrow_leaf2) laid on the stem: where its jade
    stops short of the near lobe's sharp tip (fill_open, for tips under a
    CONTOUR), the tip now lies on the stem's gold, so the leaf no longer hides
    the stem there (paper showed through); and its jade is cut out of the
    stem's far CONTOUR above the point where the blade's edge crosses it
    (there the two contours merge into one ink solid, and jade under it is a
    hidden plate, QA 4c)."""
    lf = A.arrow_leaf2(**LEAF)
    hatch = C.Frag()
    for mark in lf.lines.select(lambda m: m.role == "hatch").marks:
        for pts, _ in K.G.flatten(mark.d, 0.05):
            # The course at the stalk crossing would end beside its gold
            # plate; omit that course rather than leave a crowded terminal.
            if not 220 < pts[0][1] < 230:
                hatch += K.line(C.polyline_d(pts), K.FINE, role="leaf-vein")
    lf.lines = lf.lines.select(lambda m: m.role != "hatch") + hatch
    lf.lines = lf.lines.select(lambda m: m.role != "vein") + K.clip_in(
        lf.lines.select(lambda m: m.role == "vein"), lf.shape.buffer(-8.5))
    jade = shapely.union_all([K.R(m.d) for m in lf.fills.marks if m.kind == "fill"])
    x_edge = 546.0 + 19.0 / 2
    stem = K.box(546.0 - 19.0 / 2, 0, x_edge, 1050)
    bare = lf.shape.difference(jade.buffer(0.05)).intersection(stem)
    occ = lf.shape.difference(bare) if not bare.is_empty else lf.shape
    y_cross = lf.shape.intersection(LineString([(x_edge, 0.0), (x_edge, 600.0)])).bounds[1]
    cut = K.box(x_edge - K.CONTOUR / 2 - 0.6, 0, x_edge + K.CONTOUR / 2 + 0.6, y_cross + 1.0)
    cut = cut.intersection(K.U(K.outline(lf.shape).shape(),
                              K.outline(stem).shape()).buffer(-0.6))
    return K.Part(max(K._polys_of(occ.buffer(0)), key=lambda g: g.area), K.fill(jade.difference(cut), K.JADE),
                  lf.lines, dict(lf.meta))


def _collar_path(k):
    c = COLLAR[k]
    return np.asarray(C.sample_d(K.arc_sag(P(c[0]), P(c[1]), -c[2]), 0.3)[0][0])


def _collar_strand(k, zone):
    """Strand ``k`` of the pearl collar (see COLLAR), seen inside ``zone``."""
    c = COLLAR[k]
    return TD.strand_span(_collar_path(k), c[3], c[4], c[5], c[6], c[7], zone)


def build():
    return figure().layers()
