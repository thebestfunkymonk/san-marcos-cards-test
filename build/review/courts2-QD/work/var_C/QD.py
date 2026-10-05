"""art/QD.py — Q♦ · The Queen of Scales (House of the Ford), creative brief §H.11.

Justice of the square, after the figure on the courthouse dome: she weighs
the kingdom's water, and this Justice sees. 3/4 right, eyes open and level.

(composition plan: rebuilt in pass r1)
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K          # noqa: E402
from deck.motifs import core as C       # noqa: E402
import _qd_parts as Q                   # noqa: E402
import _qd_hair as H                    # noqa: E402
import _qd_regalia as RG                # noqa: E402
import _qd_finish as FIN                # noqa: E402

HEAD = (372.0, 206.0)
AXF = HEAD[0] + 0.12 * 84.0             # the face's feature axis (3/4 right: +12 % of the head width)
NECK_X = 380.0

CAPE_L = [(350.0, 284.0), (290.0, 296.0), (220.0, 318.0), (190.0, 346.0), (172.0, 420.0), (158.0, 548.0)]
CAPE_R = [(414.0, 284.0), (478.0, 296.0), (546.0, 316.0), (574.0, 344.0), (590.0, 420.0), (602.0, 548.0)]
OPEN_L = [(348.0, 298.0), (316.0, 348.0), (276.0, 430.0), (244.0, 548.0)]
OPEN_R = [(418.0, 298.0), (446.0, 348.0), (478.0, 430.0), (504.0, 548.0)]
NECK_L, NECK_R, NECK_SAG = (344.0, 306.0), (424.0, 306.0), -8.0

CAPE_KW = dict(field=dict(pitch=(22.0, 19.0), stone=(8.0, 5.5), border=22.0), lining=14.0, band_in=21.0)
STOM_TOP = 340.0                        # the stomacher's cap clears the Lion Mark's ripple line (§G.2)
CLASP_Y = 310.0                         # at the neckline; its ripple 5 px clear of the stomacher's cap
# the circlet's lozenges slimmer and a px low: whole between the band's contour and the column feet
DIADEM_STONE = (9.0, 4.4)
DIADEM_KW = dict(cornice=False, stone_dy=1.0)       # no raking cornice: the flat pediment has no room
STAFF_X = 528.0
BEAM_HALF = 47.0                        # right pan rim 598 + CONTOUR: >= 12 px inside the gold rule (x 615)
FIST_R = (STAFF_X, 408.0)
FIST_L_Y = 438.0                        # the thumb clears the paintbrush's lowest bract
# the stem hand: the queen's right, back to us, knuckles out; the staff hand: her LEFT from the
# OUTER side (back=+1, knuckles and cuff outside, the forearm straight up from the band, no kink)
HAND_L = dict(shaft_w=9.0, back=-1, h=34.0, knuckle=12.0, reach=4.0)
HAND_R = dict(shaft_w=18.0, back=+1, h=34.0, knuckle=10.0, reach=6.0)
WRIST_L = dict(bend=50.0, dist=0.95)
WRIST_R = dict(bend=60.0, dist=1.0)
# the forearms lie on the red cape with a clear red strip to its outer contour (no sliver, no
# sleeve edge merging into the silhouette line); the staff forearm stands clear of the staff's halo
SLEEVE_L = dict(base=(193.0, 552.0), sag=5.0, width=40.0, wrist_w=28.0, cuff=16.0)
SLEEVE_R = dict(base=(564.0, 552.0), sag=0.0, width=38.0, wrist_w=28.0, cuff=16.0)
JAW = (16.0, 49.0)                      # chin circle radius, its centre below the egg centre
FACE_OVERRIDES = {}                     # face-study hook (work/qd/face_test.py); empty in the deck
# the gown's stacked arcade: three tiers on one grid about the stomacher's axis
ARCADE = dict(pitch=29.0, a=3.5, jamb=13.0, key=(6.0, 26.0), sills=(494.0, 456.2, 419.7), cornice=383.2,
              on_axis="arch")
PB_BASE, PB_TIP = (241.0, 472.0), (212.0, 222.0)
# the paintbrush spike: overlapping pointed bracts, alternate, bottom → top
# (t along the spike, side, lean°, length, width, red fraction)
PAINTBRUSH = dict(spike=100.0, top=(20.0, 11.0, 0.84), hatch_side=+1, root=4.0, stem_top=0.0, leaves_behind=True,
                  bracts=((0.00, +1, 46.0, 34.0, 17.0, 0.40), (0.09, -1, 38.0, 33.0, 17.0, 0.42),
                          (0.25, +1, 33.0, 30.0, 15.5, 0.48), (0.34, -1, 30.0, 29.0, 15.0, 0.52),
                          (0.49, +1, 24.0, 26.0, 13.5, 0.60), (0.57, -1, 21.0, 24.0, 12.5, 0.66),
                          (0.68, +1, 16.0, 22.0, 11.5, 0.74), (0.75, -1, 13.0, 20.0, 11.0, 0.80)),
                  leaves=((0.43, -1, 34.0, 11.0), (0.68, +1, 32.0, 10.5)))     # the lower leaf clears the thumb

# the hair, dressed up: swept back from the brow over the ear into a knot at
# the nape (the ear and a ♦ drop earring show; the neck is bare)
MANE_OUT = [(318.0, 164.0), (302.0, 184.0), (292.0, 210.0), (288.0, 240.0), (290.0, 270.0), (296.0, 300.0),
            (302.0, 330.0)]
MANE_IN = [(360.0, 166.0), (352.0, 200.0), (352.0, 240.0), (372.0, 274.0), (372.0, 330.0)]
FAR_OUT = [(424.0, 166.0), (431.0, 190.0), (433.0, 220.0), (431.0, 252.0), (434.0, 284.0), (440.0, 320.0)]
FAR_IN = [(396.0, 166.0), (404.0, 200.0), (400.0, 240.0), (388.0, 274.0), (388.0, 320.0)]
EAR = ((332.5, 214.0), (316.0, 226.0), (331.0, 245.0))
EAR_IN = ((329.0, 220.5), (322.5, 228.0), (328.0, 236.0))
EARRING = (331.0, 249.0)


def _on_stem(y):
    (x0, y0), (x1, y1) = PB_BASE, PB_TIP
    return (x0 + (x1 - x0) * (y - y0) / (y1 - y0), y)


def figure():
    sc = K.Scene(rank="Q")
    fkw = dict(sex="f", age="adult", lids="heavy", flick=0.0, brow_dy=-15.0, brow_sag=4.4, mouth_hw=8.5,
               bow_rise=2.0, bow_sag=-0.6, lip_hw=4.8, lip_sag=-2.0, lip_dy=44.0, pupil_tuck=-0.5)
    fkw.update(FACE_OVERRIDES)
    fc = K.face(HEAD, "3/4-right", **fkw)
    # a queen's jaw: the kit egg with a smaller chin circle set a little lower
    hd, _info = K.egg(HEAD, 42.0, chin_dx=0.12 * 84.0 * 0.55, chin_r=JAW[0], chin_dy=JAW[1])
    fc.head, fc.skin = hd, K.R(hd)

    # ---- body, back to front ------------------------------------------------------
    sc.part("collar", K.standing_collar(NECK_X, top_y=226.0, half_w=108.0, neck_y=268.0, shoulder=(-134.0, 320.0),
                                        top_sag=8.0, side_sag=-5.0, rim=9.0, depth=60.0, color=K.JADE,
                                        rim_color=K.GOLD))
    dfr, dcol = RG.portico3(AXF + 1.5, xl=314.0, xr=428.0, top_l=160.0, top_c=162.0, top_r=160.0,
                            band_h=16.0, stone=DIADEM_STONE, stone_pitch=15.0, col_h=30.0, col_w=8.4,
                            cap=(2.6, 2.2), base=(0.0, 0.0), arch_h=8.0, ped_rise=23.0, ped_hw=(58.0, 47.0), vy=260.0,
                            oculus_r=6.0, oculus_at=0.283, oculus_pane=K.RED, **DIADEM_KW)
    sc.part("hair-far", H.mane(outer=FAR_OUT, inner=FAR_IN, n=1, band=dfr.meta["band"]))
    sc.part("hair", H.mane(outer=MANE_OUT, inner=MANE_IN, n=4, band=dfr.meta["band"]))
    cp = Q.cape(CAPE_L, CAPE_R, OPEN_L, OPEN_R, **CAPE_KW)
    sc.part("cape", cp)
    sc.part("neck", H.neck_chest(NECK_X, top=236.0, hw=14.5, base_y=284.0, shoulder=(346.0, 420.0),
                                 spring_y=298.0))
    stom = RG.stomacher3(AXF + 1.0, top=STOM_TOP, hw_top=38.0, hw_mid=33.0, y_mid=440.0, y_point=488.0)
    gw = Q.gown5(cp.meta["opening"], NECK_L, NECK_R, NECK_SAG, avoid=stom.meta["hull"], ox=AXF + 1.0, **ARCADE)
    sc.part("gown", gw)
    sc.part("stomacher", stom)
    sc.part("clasp", K.lion_clasp((AXF + 1.0, CLASP_Y), 40.0))

    # ---- head ------------------------------------------------------------------------
    # the near eye's outer corner runs on into a short lash (the far eye's corner joins the contour)
    eo = K.P(fc.anchors["axis"] - fc.anchors["spec"].eye_dx - fc.anchors["spec"].eye_w / 2, fc.anchors["eye_y"])
    lash = K.seg(eo, eo + K.P(-3.2, 1.2), K.RULE, role="lid")
    sc.add("head", fc.lines + lash + K.outline(fc.head), fc.skin)
    sc.part("ear", H.ear2(*EAR, face=fc.skin, inner=EAR_IN))
    sc.part("earring", H.earring(EARRING, bead=6.3, drop=(15.0, 9.5)))
    sc.part("diadem", dfr)
    sc.part("columns", dcol, sil=False)

    # ---- arms and attributes -------------------------------------------------------------
    ang = math.degrees(math.atan2(PB_TIP[1] - PB_BASE[1], PB_TIP[0] - PB_BASE[0]))
    WL = tuple(K.fist_wrist(_on_stem(FIST_L_Y), ang, **WRIST_L, **HAND_L))
    WR = tuple(K.fist_wrist(FIST_R, -90.0, **WRIST_R, **HAND_R))
    specL = K.SleeveSpec(wrist=WL, color=K.JADE, cuff_color=K.GOLD, **SLEEVE_L)
    specR = K.SleeveSpec(wrist=WR, color=K.JADE, cuff_color=K.GOLD, **SLEEVE_R)
    slL, cfL = K.sleeve(specL)
    slR, cfR = K.sleeve(specR)
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    bal = RG.balance(STAFF_X, half=BEAM_HALF, collars=(236.0, 300.0), pan_hw=23.0, surf_ry=13.0, pan_depth=7.0,
                     foot=None, beam_h=(16.0, 11.0), boss_r=8.0, staff_hw=9.0, pivot=False, neck_hw=2.4,
                     fin_marks=False)
    sc.part("staff", bal["staff"], halo=K.HALO, halo_only=("cape", "gown"))
    sc.part("beam", bal["beam"])
    sc.add("cords", bal["cords"].lines, None, sil=False)
    sc.part("panL", bal["panL"], sil=False)
    sc.part("panR", bal["panR"], sil=False)
    pb = Q.paintbrush7(PB_BASE, PB_TIP, **PAINTBRUSH)
    sc.part("paintbrush", pb, sil=False, halo=K.HALO, halo_only=("gown", "cape", "sleeveL", "hair"))
    for nm, cf, spec in (("cuffL", cfL, specL), ("cuffR", cfR, specR)):
        W = K.P(spec.wrist)
        u = (W - K.P(spec.base)) / math.hypot(*(W - K.P(spec.base)))
        sc.part(nm, Q.cuff_stones(cf, W, u, spec.wrist_w / 2, spec.cuff))
    K.fist(_on_stem(FIST_L_Y), ang, wrist=WL, wrist_w=20.0, **HAND_L).add_to(sc, "handL", halo=0.0)
    K.fist(FIST_R, -90.0, wrist=WR, wrist_w=24.0, **HAND_R).add_to(sc, "handR", halo=0.0)
    # the staff forearm stands right beside the staff: the ground between the staff and the
    # sleeve is the staff's own paper channel, carried down from the heel to the band (no red
    # sliver, no white tab ending under the cuff)
    stf, slv = sc.items[[i.name for i in sc.items].index("staff")].occ, slR.shape.union(cfR.shape)
    x0, x1 = stf.bounds[2], slv.bounds[0] + 12.0
    gap = K.box(x0 - 1.0, WR[1], x1, 530.0).difference(slv).difference(stf)
    gap = max(K._polys_of(gap), key=lambda g: g.area) if not gap.is_empty else gap
    sc.add("staff~sleeveR", C.Frag(), None, sil=False, halo=K.HALO, halo_only=("cape",), halo_zone=gap)
    _clear_cape_stones(sc, cp)
    K.band_guard(sc, "Q")
    return sc


def _clear_cape_stones(sc, cp):
    """Re-knock the cape's stepping stones clear of everything stacked in
    front of it: a stone that would be half under a paper halo (the stem's,
    the staff's, a fist's fingertip channel) or under a sleeve's outline is
    left out whole (§I.12; the kit's clear_of_hand rule, applied to the whole
    front stack)."""
    names = [it.name for it in sc.items]
    k = names.index("cape")
    zones = []
    for it in sc.items[k + 1:]:
        if it.occ is None or it.occ.is_empty:
            if it.halo_zone is not None and "cape" in (it.halo_only or ("cape",)):
                zones.append(it.halo_zone)
            continue
        if it.halo and (it.halo_only is None or "cape" in it.halo_only) and "cape" not in it.halo_skip:
            zones.append(it.halo_zone if it.halo_zone is not None else it.occ.buffer(it.halo + K.MEDIUM / 2))
        else:
            zones.append(it.occ.buffer(K.MEDIUM / 2))
    clear = K.U(*zones)
    new = Q.cape(CAPE_L, CAPE_R, OPEN_L, OPEN_R, clear=clear, **CAPE_KW)
    sc.items[k].frag = K.flatten_fills(new.frag)


def compose_scene(sc):
    return FIN.compose(sc)


def build():
    return K.layers(compose_scene(figure()))
