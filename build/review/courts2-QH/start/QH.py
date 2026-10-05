"""art/QH.py — Q♥ · The Aquamaid Queen (House of the Fount), brief §H.5.

(draft v3 — composition plan in progress)
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import Polygon

from deck import courtkit as K
from deck.motifs import core as C

from art import _qh_attr as A
from art import _qh_body as B
from art import _qh_cap as CP
from art import _qh_face as QF
from art import _qh_head as H

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
PETIOLE = dict(p0=(550, 304), p1=(566, 268), w=7.0, sag=-6.0)
LEAF = dict(sinus=(568, 262), tilt=9.0, blade=80.0, half_w=23.0, lobe=(21.0, 38.0), notch=(13.0, 22.0), fill_open=3.3)


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
                sweet=[(284, 376), (336, 350), (390, 370), (438, 348), (483, 374)],
                puff_l=None, puff_r=None,
                out_l=[(236, 303), (190, 310), (163, 336), (157, 366), (168, 392), (158, 450), (148, 548)],
                out_r=[(528, 302), (566, 310), (590, 336), (594, 366), (583, 392), (594, 450), (602, 548)])
    sc.part("sleeveL", gw.sleeve(-1, border=17.0, pitch=12.0))
    sc.part("sleeveR", gw.sleeve(+1, border=17.0, pitch=12.0))
    sc.part("torso", gw.torso(scale_r=15.0))
    # strung with 3.4 px of red between the beads: touching beads trap red
    # under their merged contours (4c) and the pair either side of the
    # neckline's cusp overlapped
    sc.part("trim", B.pearls_on(gw.sweet_pts, d_max=9.5, d_min=6.3, gap=3.4))
    sc.part("armletL", gw.armlet(-1, (168, 388), (290, 394), sag=-7.0, d=9.5))
    sc.part("armletR", gw.armlet(+1, (482, 392), (588, 388), sag=-6.0, d=9.5))

    # ---- hair (behind the head), neck, head, cap ---------------------------------------------
    sc.part("hairN", H.lock(HAIR_N, 54.0, n=5, taper=0.42, taper_from=0.45,
                            side=+1, bubbles=(4.2, 5.6, 7.0), bubble_lane=2, bubble_at=0.55))
    sc.part("hairF", H.lock([(426, 188), (437, 218), (441, 250), (440, 278), (451, 300), (469, 304)], 40.0, n=4,
                            side=-1))
    sc.part("neck", K.neck(fc, bottom=299.0, width=35.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    cap = CP.Cap(CAP_C, CAP_R, **CAP_KW)
    if ROSETTE:
        _rosette_cap(sc, cap, ROSETTE)
    else:
        _sphere_cap(sc, cap)

    # ---- pearl collar and the Lion Mark ---------------------------------------------------------
    _collar_and_attrs(sc, gw)
    return sc


def _rosette_cap(sc, cap, cfg):
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


def _collar_and_attrs(sc, gw):
    for k, (y, sag, hw) in enumerate(((285.0, 5.0, 20.0), (297.5, 6.5, 22.0))):
        p0, p1 = P(388 - hw, y - 2), P(388 + hw, y - 3)
        pts = np.asarray(C.sample_d(K.arc_sag(p0, p1, -sag), 0.3)[0][0])
        sc.part(f"collar{k}", B.pearls_on(pts, d_max=7.6, d_min=6.4))
    sc.part("clasp", K.lion_clasp((390.0, 330.0), 40.0))

    # ---- the arrowhead sceptre ---------------------------------------------------------------------
    sc.part("stem", A.stem((546, 548), (546, 116), w=19.0, nodes=(0.53, 0.84)), halo=K.HALO,
            halo_only=("sleeveL", "sleeveR", "armletR"))
    if PETIOLE:
        sc.part("petiole", A.petiole(**PETIOLE), sil=False)
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
    faR = B.forearm((474, 532), WR, width=44.0, wrist_w=30.0, sag=2.0)
    sc.part("armL", faL, halo=K.HALO, halo_only=("sleeveL", "sleeveR"))
    sc.part("armR", faR, halo=K.HALO, halo_only=("sleeveL", "sleeveR"))
    K.flat((300.0, 452.0), -24.0, side=-1, length=72.0, width=31.0, wrist_w=24.0, tips=(5.0, 0.0, 3.0, 10.0),
           knuckle=0.45, thumb_deg=22.0, thumb_len=0.42, stub=K.HAND_STUB).add_to(
        sc, "handL", halo=K.HALO, halo_only=("torso", "trim"))
    K.fist((546.0, 434.0), -90.0, wrist=WR, wrist_w=26.0, **fist_r).add_to(sc, "handR", halo=0.0)
    # the pearl bracelets over the wrists (the hands run on under them)
    sc.part("braceletL", B.bracelet((300, 452), faL.meta["u"], 34.0, d=6.3))
    sc.part("braceletR", B.bracelet(WR, faR.meta["u"], 30.0, d=6.3))
    K.band_guard(sc, "Q")


def build():
    return figure().layers()
