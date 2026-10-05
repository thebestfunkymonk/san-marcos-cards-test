"""art/QH.py — Q♥ · The Aquamaid Queen (House of the Fount), brief §H.5.

(draft v3 — composition plan in progress)
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import Polygon

from deck import courtkit as K
from deck.motifs import core as C

from art import _qh_attr as A
from art import _qh_body as B
from art import _qh_cap as CP
from art import _qh_face as QF
from art import _qh_hand as QHH
from art import _qh_head as H
from art import _qh_tidy as TD

P = K.P
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
# courts2 review: the leaf's near lobe ran down the stem 1-2 px off its left
# contour (a gold sliver, QA 12) and the petiole's square root end drew a
# pointed pocket on the sleeve's crown. The leaf now stands 8 px higher and 4°
# more upright with lobes 2 px shorter, so the stem shows as a ≥ 4.2 px strip
# beside the near lobe and the blade's edge still crosses the stem's far edge
# steeply (a shallow crossing merged the two contours into an ink slab, QA 4c);
# the petiole comes out from BEHIND the stem (drawn first) ~8 px above the
# crown and curves up into the sinus with paper both sides of it
PETIOLE = dict(w=7.0, turtle=((548.0, 291.0), 0.0, (("fd", 10.5), ("arc", 10.0, -88.0), ("fd", 52.0))))
PETIOLE_ORDER = "behind"          # "behind" the stem, or in "front" of it (under the leaf)
LEAF = dict(sinus=(568.5, 250), tilt=5.0, blade=80.0, half_w=23.0, lobe=(19.0, 38.0), notch=(13.0, 22.0),
            fill_open=3.3, rib_from=0.0)
# clear gap between the neckline pearls: 3 px of red + both FINE contours
TRIM_GAP = 3.0 + 2 * 2.1 / 2 + 0.2
# the pearl collar: (centre x, y, sag, half-width, Ø max, Ø min) per strand
# (both were centred on x 388: the neck's inside, between its CONTOUR on the
# near side and its MEDIUM edge against the far lock, is centred further left)
# the pearl collar: per strand the arc (p0, p1, sag). The upper strand, on the
# neck, runs from a pearl tucked under the near neck CONTOUR to one tucked
# under the far neck contour (first / last pearl centre x, n pearls, Ø max /
# min; it stopped 4 px short of the far contour); the lower strand lies across
# the neck's base on the bodice, its end pearl 3 px clear of the far lock's
# edge (1.4 px from it, heal opened that pearl into a "C" of bare gold on red)
COLLAR = (((364.5, 283.0), (412.0, 281.0), 5.5, 370.8, 405.05, 6, 7.6, 6.4),
          ((363.5, 296.5), (403.5, 297.5), 6.5, 370.06, 396.0, 5, 7.6, 6.4))
# the plain band under the pearl armlets (card y; the sleeves' wave rows lie at
# y = 322 + 12k, so this drops the rows at 382 and 394)
ARMLET_BAND = [(380.0, 396.0)]
# the right armlet's arc (p0, p1, sag): the pearls right of the stem sit at
# y ≈ 387, where the seam crosses the first ~3 px off its centre and the
# sleeve's CONTOUR cuts the second decisively
ARMLET_R = ((484.0, 386.0), (592.0, 384.0), -4.0)
# the stem's collars: the lower one sat on the sleeve's crown (its paper channel
# bit a box out of the contour); it now sits well inside the sleeve
NODES = (0.495, 0.875)
# the far lock comes out beside the band's square far end with a SHOULDER: from
# the band's top corner along its top edge, round and down into the lock's own
# outer edge — a strip of hair ≥ 5 px wide from the band down (the lock's top
# was a wedge tapering into the face contour, and heal dropped the contour)
FAR_SHOULDER = dict(start=(418.0, 173.6), h0=36.0, join_y=232.0, via=((429.0, 181.0), (435.0, 198.0)),
                    hidden=((410.0, 232.0), (404.0, 200.0), (408.0, 178.0), (416.5, 176.0)))
# the queen's right hand on the bodice (courtkit.flat via _qh_hand.bodice_hand)
HAND_L = dict(side=-1, length=72.0, width=31.0, wrist_w=24.0, tips=(5.0, 0.0, 3.0, 10.0), knuckle=0.45,
              thumb_deg=32.0, thumb_len=0.40, stub=K.HAND_STUB)


def _stem():
    # the upper collar (on paper, under the CONTOUR) keeps its gold 1 px past
    # the shaft (QA 4c); the lower one, inside the sleeve under a MEDIUM
    # outline, is gold to its outline (a trap there left paper slits)
    return A.stem((546, 548), (546, 116), w=19.0, nodes=NODES, collar_trap=(None, 1.0))


def figure():
    sc = K.Scene(rank="Q")
    fc = QF.queen_face(HEAD, wing_mode="hook", wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)

    # ---- behind everything: the air rising from behind the far shoulder ------------------
    sc.add("bubbles", A.bubble_ribbon(AIR, AIR_SIZES, growth=AIR_GROWTH), None, sil=False)

    # ---- the gown -------------------------------------------------------------------------
    gw = B.Gown(neck_l=(369, 298), neck_r=(406, 296),
                shoulder_l=[(318, 305), (266, 320)], shoulder_r=[(452, 302), (500, 316)],
                hole_l=[(278, 352), (286, 410), (292, 470), (294, 548)],
                hole_r=[(488, 350), (484, 410), (480, 470), (478, 548)],
                sweet=[(284, 376), (336, 350), (390, 370), (438, 351), (483, 374)],
                puff_l=None, puff_r=None,
                out_l=[(236, 303), (190, 310), (163, 336), (157, 366), (168, 392), (158, 450), (148, 548)],
                out_r=[(528, 302), (566, 310), (590, 336), (594, 366), (583, 392), (594, 450), (602, 548)])
    # the two wave rows under the pearl armlets are left out: the strand lies on
    # a plain gathered band (rows at a 12 px pitch cannot clear an 11.6 px strand
    # laid along them — their crests grazed the pearls, and heal cut paper
    # crescents out of the gold; courts2 review)
    slL = gw.sleeve(-1, border=17.0, pitch=12.0, skip_y=ARMLET_BAND)
    slR = gw.sleeve(+1, border=17.0, pitch=12.0, skip_y=ARMLET_BAND)
    # the lock over the near shoulder is in front: wave troughs that only peek
    # out from under its edge are left out (a 2 px jade pocket there, QA 12)
    hn = H.lock(HAIR_N, 54.0, n=5, taper=0.42, taper_from=0.45,
                side=+1, bubbles=(4.2, 5.6, 7.0), bubble_lane=2, bubble_at=0.55)
    hf = H.lock([(426, 188), (437, 218), (441, 250), (440, 278), (451, 300), (469, 304)], 40.0, n=4, side=-1)
    slL = TD.waves_clear(slL, hn.shape)
    # pearls PLACED, not spread: one squarely on each border seam (the seam
    # crosses it near its middle — it was tangent to the end pearl), and the
    # right strand breaks round the stem's paper channel with 3 px of jade each
    # side (the channel had cut two pearls into crescents). Right of the stem
    # the strand dips a little as it turns round the arm: one pearl on the
    # seam and the next TUCKED under the sleeve's CONTOUR (a lone pearl there
    # read as an orphan dot; two whole pearls cannot fit the 17 px border)
    sx = TD.seam_x(slL, 388.0)[0]
    armL = TD.strand(slL, (168, 385), (290, 385), sag=-5.0, d=9.5, inset=4.0,
                     xs=[sx + 9.5 * k for k in range(-2, 13)])
    ch = 19.0 / 2 + K.HALO + K.MEDIUM / 2 + 3.0 + 9.5 / 2 + K.FINE / 2      # stem axis → pearl centre
    armR = TD.strand(slR, ARMLET_R[0], ARMLET_R[1], sag=ARMLET_R[2], d=9.5, inset=4.0, tuck=K.CONTOUR / 2,
                     xs=[546.0 - ch - 9.5 * k for k in range(0, 6)] + [546.0 + ch, 546.0 + ch + 9.5])
    # the seams stop 0.55 px short of the pearls, so their round caps end
    # under the pearls' FINE outlines (cut at the pearl's edge they poked
    # 0.5 px into the gold); on the right sleeve, wave crests that only peek
    # into the strip between the stem's paper channel and the seam as stubs
    # are dropped (≥ 8 px pieces stay)
    slL = TD.lines_clear(slL, armL.shape.buffer(0.55), role="seam", min_len=2.0)
    slR = TD.lines_clear(slR, armR.shape.buffer(0.55), role="seam", min_len=2.0)
    chan = K.box(546.0 - 19.0 / 2 - K.HALO - K.MEDIUM / 2 - 0.5, 0, 546.0 + 19.0 / 2 + K.HALO + K.MEDIUM / 2 + 0.5, 1050)
    slR = TD.lines_clear(slR, chan, role="wave", min_len=8.0)
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    sc.part("torso", gw.torso(scale_r=15.0))
    # strung with red between the beads: touching beads trap red under their
    # merged contours (4c) and the pair either side of the neckline's cusp
    # overlapped. courts2 review: at 3.4 px the two FINE contours kept only
    # 1.3 px of red between them, so heal opened every pearl's contour into a
    # "C" (bare gold on red, §C.4); TRIM_GAP keeps 3 px of red between them
    sc.part("trim", TD.beads_inside(B.pearls_on(gw.sweet_pts, d_max=9.5, d_min=6.3, gap=TRIM_GAP),
                                    gw.torso_shape, clear_of=(hn.shape, hf.shape)))
    sc.part("armletL", armL)
    sc.part("armletR", armR)

    # ---- hair (behind the head), neck, head, cap ---------------------------------------------
    sc.part("hairN", hn)
    sc.part("hairF", hf)
    # the lower pearl strand lies across the neck's base: between its end
    # pearls' centres the base runs along the strand's centreline, hidden
    # through the pearls' middles (at y 299 it grazed the tops of the lower
    # pearls between them); beyond them it stays at 299 and T's into the end
    # pearls
    nk = K.neck(fc, bottom=299.0, width=35.0)
    c1 = COLLAR[1]
    lo = _collar_path(1)
    lo = lo[lo[:, 0] <= c1[4]]
    # past the end pearl's centre the base runs straight to the far corner
    lo = np.vstack([lo, [(412.0, 298.6)]])
    above = Polygon(np.vstack([[(0.0, lo[0][1])], lo, [(750.0, lo[-1][1]), (750.0, 0.0), (0.0, 0.0)]])).buffer(0)
    low = K.neck(fc, bottom=308.0, width=35.0).shape.intersection(above).intersection(K.box(c1[3], 0, 750, 1050))
    nsh = max(K._polys_of(nk.shape.union(low).buffer(0)), key=lambda g: g.area)
    # its line stops 0.5 px short of the pearls (its round cap then ends under
    # a pearl's FINE outline instead of poking into the gold)
    nk = TD.lines_clear(K.Part(nsh, C.Frag(), K.outline(nsh), {}), _collar_strand(1, K.box(0, 0, 750, 1050)).shape
                        .buffer(0.5), role="outline", min_len=2.0)
    sc.part("neck", nk)
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

    # ---- pearl collar and the Lion Mark ---------------------------------------------------------
    _collar_and_attrs(sc, gw, nk.shape)
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


def _collar_path(k):
    c = COLLAR[k]
    return np.asarray(C.sample_d(K.arc_sag(P(c[0]), P(c[1]), -c[2]), 0.3)[0][0])


def _collar_strand(k, zone):
    """Strand ``k`` of the pearl collar (see COLLAR), seen inside ``zone``."""
    c = COLLAR[k]
    return TD.strand_span(_collar_path(k), c[3], c[4], c[5], c[6], c[7], zone)


def _collar_and_attrs(sc, gw, neck):
    # courts2 review: the strands' end pearls stopped 0.2–1 px short of the
    # neck's contours and heal opened them into "C"s (bare gold edges). Each
    # strand now runs from a pearl tucked under the near neck CONTOUR to one
    # tucked under the far neck contour (it stopped 4 px short of it, and the
    # lower strand's end pearl was a "C" with the neck's base line running
    # into it): it wraps round behind the neck at both ends (TD.strand_span)
    seen = (neck, neck.union(gw.torso_shape.difference(sc.region(["hairF"]))))
    for k in range(len(COLLAR)):
        sc.part(f"collar{k}", _collar_strand(k, seen[k]))
    sc.part("clasp", K.lion_clasp((390.0, 330.0), 40.0))

    # ---- the arrowhead sceptre ---------------------------------------------------------------------
    # the petiole runs out from BEHIND the stem (no butt end drawn across the
    # gold) and leaves its right edge well above the sleeve's crown
    pet = None
    if PETIOLE:
        # its gold stops short of the sinus (the notch's apex is an ink knot)
        pt = A.petiole(**PETIOLE)
        g = pt.shape.difference(K.R(K.circle(LEAF["sinus"], K.MEDIUM + 2.0)))
        pet = K.Part(pt.shape, K.fill(g, K.GOLD), pt.lines, pt.meta)
    if pet is not None and PETIOLE_ORDER == "behind":
        sc.part("petiole", pet, sil=False)
    sc.part("stem", _stem(), halo=K.HALO, halo_only=("sleeveL", "sleeveR", "armletR"))
    if pet is not None and PETIOLE_ORDER == "front":
        sc.part("petiole", pet, sil=False)
    sc.part("leaf", A.arrow_leaf2(**LEAF))
    for nm, pt in A.flower3((546, 112), r_petal=50.0, petal_w=40.0, centre_r=12.5, squash=0.78, tilt=-10.0,
                            notch=5.0, centre="scallop", hatch_rel=0.0):
        sc.part("flower-" + nm, pt)

    # ---- arms and hands ------------------------------------------------------------------------------
    # the queen's LEFT hand grips the stem from the body side (palm view, courtkit.fist hand='L'),
    # its wrist out along the hand's axis; the right hand lies on the bodice (courtkit.flat)
    fist_r = dict(shaft_w=19.0, back=-1, hand="L", h=36.0)
    WR = tuple(K.fist_wrist((546.0, 434.0), -90.0, bend=44.0, shaft_w=19.0, back=-1, h=36.0))
    faL = B.forearm((232, 532), (300, 452), width=50.0, wrist_w=34.0, sag=-3.0)
    # the right cuff opens to the left's 34 px and its bracelet sits 2.5 px up
    # the cuff (across the wrist junction at 30 px, the end pearls hung a
    # fraction of a px off the cuff's edges and the hand's heel, and heal
    # opened them into "C"s of bare gold; courts2 review)
    faR = B.forearm((474, 532), WR, width=44.0, wrist_w=34.0, sag=2.0)
    brL = B.bracelet((300, 452), faL.meta["u"], 34.0, d=6.3)
    brR = B.bracelet(WR, faR.meta["u"], 30.0, d=6.3, back=2.5)
    # the cuffs' waves stop ≥ 3 px short of the bracelets' pearls (they grazed
    # them, and heal cut paper wedges out of the gold)
    clear = K.GAP_MARK + K.FINE + 0.2
    faL = TD.lines_clear(faL, brL.shape.buffer(clear))
    faR = TD.lines_clear(faR, brR.shape.buffer(clear))
    sc.part("armL", faL, halo=K.HALO, halo_only=("sleeveL", "sleeveR"))
    sc.part("armR", faR, halo=K.HALO, halo_only=("sleeveL", "sleeveR"))
    # the kit's flat hand, its thumb opened off the index finger (a clear web V
    # instead of the thumb's tip pressing the index root) with one crease from
    # the web toward the wrist, the little-finger side one smooth edge
    QHH.bodice_hand((300.0, 452.0), -24.0, **HAND_L).add_to(sc, "handL", halo=K.HALO, halo_only=("torso", "trim"))
    K.fist((546.0, 434.0), -90.0, wrist=WR, wrist_w=26.0, **fist_r).add_to(sc, "handR", halo=0.0)
    # the pearl bracelets over the wrists (the hands run on under them)
    sc.part("braceletL", brL)
    sc.part("braceletR", brR)
    K.band_guard(sc, "Q")


def build():
    return figure().layers()
LEAF = dict(sinus=(570.0, 259.0), tilt=9.0, blade=80.0, half_w=23.0, lobe=(21.0, 36.0), lobe_l=(18.0, 35.0), notch=(13.0, 22.0), fill_open=3.3, rib_from=0.0)
PETIOLE = dict(w=7.0, turtle=((546.0, 299.8), -40.0, (("fd", 20.5), ("arc", 16.0, -41.0), ("fd", 18.0))))
