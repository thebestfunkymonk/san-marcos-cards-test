"""Q♥ · The Aquamaid Queen: continuous woven robes and one sagittaria grip."""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck.motifs import core as C

from art import _qh_attr as A
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
AIR = [(497, 302), (505, 262), (499, 212), (485, 165), (485, 124), (495, 94), (511, 71)]
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
def _stem():
    # the upper collar (on paper, under the CONTOUR) keeps its gold 1 px past
    # the shaft (QA 4c); the lower one, inside the sleeve under a MEDIUM
    # outline, is gold to its outline (a trap there left paper slits)
    return A.stem((546, 479), (546, 116), w=19.0,
                  nodes=((479 - 334) / 363, (479 - 185) / 363), collar_trap=(None, 1.0))


def figure():
    sc = K.Scene()
    fc = QF.queen_face(HEAD, wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)

    # ---- behind everything: the air rising from behind the far shoulder ------------------
    sc.add("bubbles", A.bubble_ribbon(AIR, AIR_SIZES, growth=AIR_GROWTH), None, sil=False)

    hn = H.lock(HAIR_N, 54.0, n=5, taper=0.42, taper_from=0.45,
                side=+1, bubbles=(4.2, 5.6, 7.0), bubble_lane=2, bubble_at=0.55)
    hf = H.lock([(426, 188), (437, 218), (441, 250), (440, 278), (451, 300), (469, 304)], 40.0, n=4, side=-1)
    # Use the downward stem axis so the wrist runs inward to the shoulder.
    h = K.hand5((546, 434), 90, "wrap", size=K.hand_size(fc),
                hand="L", view="palm", grip_w=19)
    base = P(h.wrist) + h.wrist_dir * 84
    sleeve, _ = K.sleeve(K.SleeveSpec(wrist=h.wrist, base=base, width=62,
                                     wrist_w=h.wrist_w, cuff=0, color=K.JADE, folds=0))
    arm = h.with_sleeve(sleeve)
    arm = K.Part(arm.shape, K.fill(arm.shape.difference(arm.meta["hand_region"]), K.JADE),
                 arm.lines, arm.meta)
    pet = A.petiole(**PETIOLE)
    leaf = _leaf()
    flower = [p for _, p in A.flower3((546, 112), r_petal=50, petal_w=40,
                                     centre_r=12.5, squash=0.78, tilt=-10,
                                     notch=5, centre="scallop", hatch_rel=0)]
    held = QC.held(_stem(), pet, leaf, flower, arm)
    robe = QC.garments(K.U(held.shape, hn.shape, hf.shape), K.U(hn.shape, hf.shape))
    clasp = K.lion_clasp((390, 330), 40)
    robe = K.Part(robe.shape,
                  K.clip_out(robe.fills, clasp.meta["silhouette"], eps=0, trap=0) + clasp.fills,
                  K.clip_out(robe.lines, clasp.meta["silhouette"], eps=0.2, trap=0) + clasp.lines)
    sc.part("robes", robe)
    sc.part("sagittaria+hand+sleeve", held)

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
    jade = shapely.union_all([K.R(m.d) for m in lf.fills.marks if m.kind == "fill"])
    x_edge = 546.0 + 19.0 / 2
    stem = K.box(546.0 - 19.0 / 2, 0, x_edge, 1050)
    bare = lf.shape.difference(jade.buffer(0.05)).intersection(stem)
    occ = lf.shape.difference(bare) if not bare.is_empty else lf.shape
    y_cross = lf.shape.intersection(LineString([(x_edge, 0.0), (x_edge, 600.0)])).bounds[1]
    cut = K.box(x_edge - K.CONTOUR / 2 - 0.6, 0, x_edge + K.CONTOUR / 2 + 0.6, y_cross + 1.0)
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
