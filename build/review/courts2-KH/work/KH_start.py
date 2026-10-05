"""art/KH.py — K♥ · The Ferryman King (creative brief §H.4), built with deck.courtkit.

DRAFT v4 (pass 1: robe border, trim lapels, pole hand).
"""
from __future__ import annotations

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C

from art import _kh_head as KHH
from art import _kh_parts as KP
from art import _kh_window as KW

AX = K.AX
HEAD = (AX, 207.0)
FIST = (520.0, 456.0)          # §H.4: the pole rises from the viewer's-right hand (≈ 520, 470)
POLE_TOP = (280.0, 55.0)       # ... and is cropped by the frame's top edge at x ≈ 280
CHAL_X = 236.0
CHAL_RIM = 292.0
CHAL_STEM = 84.0                # a bare stem ≥ 5 px above and below the fist (grip 369.5–418)
CLASP = (AX, 346.0)
WIN_C = (AX, 432.0)
LENS = K.LensSpec(throat_y=280.0, half_w=88.0, lapel_w=46.0)
LAPEL_X = 306.0
ROBE = K.MantleSpec(neck_y=262.0, neck_heading=170.0, run=146.0, corner_r=34.0, side_heading=97.0)

ARM_R_BASE, ARM_R_SAG, HAND_R_BACK = (578.0, 556.0), -5.0, +1
COLLAR = dict(top_y=233.0, half_w=112.0, shoulder=(-130.0, 304.0))
FACE_KW = dict(age="elder", lids="level", lid_sag=5.4, low_sag=3.0, brow_sag=5.0, brow_dy=-14.0, brow_drop=3.0,
               bow_rise=0.4, bow_sag=-2.2, lip_sag=-2.6, lip_hw=6.5)
HAIR = K.HairSpec(bulge=(-64.0, 34.0), bottom=(-52.0, 66.0), ribbons=4, over=12.0)
MOUSTACHE = KHH.LiftMoustache(tip=(-30.0, 9.0), arch=3.4, under=5.6)
BEARD = KHH.LobeBeard()
BEARD_LOCKS = {"mode": "manual", "locks": [            # (start, mid, end) dx/dy from the axis/egg centre, turn°, r
    ((-36.0, 30.0), (-41.2, 60.0), (-37.0, 88.0), -180.0, 4.8),
    ((-19.0, 76.0), (-18.4, 89.0), (-14.5, 99.0), -180.0, 4.0)]}

# the view: the darter above; two eelgrass blades (solid paper, the card
# back's knockout) rising from the bed at the left and swaying right with the
# current — outlined pairs read as prongs; and the vent boil (§G.8's three
# flat rings) rising into view from the bed at the right — whole rings read
# as a target
WIN_KW = dict(h=112.0, spines=False, grass_solid=True, grass_hw=2.8,
              grass=[(-47.0, -92.0, 62.0, 30.0, 16.0), (-33.0, -82.0, 52.0, 34.0, 14.0)],
              rip_c=(24.0, 5.0), rip_ry=(6.0, 13.2, 20.4), rip_aspect=0.5)
# the punting pole: cord bindings (ring pairs) at the top and the shoulder,
# and a spiral cord WRAP for the grip just above the fist — a made pole
POLE_KW = dict(w=18.0, bands_y=(84.0, 352.0), wraps=((378.0, 426.0),))

POLE_DEG = float(np.degrees(np.arctan2(POLE_TOP[1] - FIST[1], POLE_TOP[0] - FIST[0])))
HAND_L = dict(shaft_w=10.4, back=-1, h=34.0)
HAND_R = dict(shaft_w=17.0, back=+1, h=34.0)
GRIP_L = (CHAL_X, CHAL_RIM + 44.0 + 9.0 + 16.0 + 6.5 + 2.0 + (CHAL_STEM - 9.0 - 16.0 - 6.5 - 4.0) / 2)
# each wrist out along its hand's axis (courtkit.fist_wrist), the cuff up the forearm
WRISTS = (tuple(K.fist_wrist(GRIP_L, -90.0, bend=42.0, **HAND_L)), tuple(K.fist_wrist(FIST, POLE_DEG, bend=60.0, dist=1.1, **HAND_R)))


def _pole_line():
    p0, p1 = K.P(FIST), K.P(POLE_TOP)
    u = (p1 - p0) / float(np.hypot(*(p1 - p0)))
    return p0 - u * 36.0, p1 + u * 40.0          # the butt shows just below the fist (clear of the forearm)


def figure():
    fc = K.face(HEAD, "frontal", **FACE_KW)

    # ---- garments ------------------------------------------------------------------------
    robe_m, rip, robe_inner = KP.robe(ROBE, border=30.0, pitch=(96.0, 36.0), origin=(AX, 312.0))
    robe_shape = robe_m.shape
    tun = K.tunic(LENS, pattern_kind=None)
    tun = K.Part(tun.shape, K.fill(tun.shape, K.JADE), tun.lines, tun.meta)
    lapels = [KP.trim_lapel(LENS, s, robe_shape, shoulder_x=LAPEL_X, collar_sag=-4.0, r=11.0, bead_off=11.4)
              for s in (-1, 1)]
    lo, hi = _pole_line()
    pole = KP.pole(lo, hi, round_low=True, **POLE_KW)
    hair = [K.hair_fall(fc, s, HAIR) for s in (-1, 1)]
    mo = KHH.moustache(fc, MOUSTACHE)
    beard = KHH.lobe_beard(fc, BEARD, mo=mo, lines=BEARD_LOCKS)
    crown, posts, pearls = KP.post_crown2()
    clasp = K.lion_clasp(CLASP, 40.0)
    win = KW.window(*WIN_C, **WIN_KW)
    WL, WR = WRISTS
    slL, cfL = K.sleeve(K.SleeveSpec(base=(176.0, 552.0), wrist=WL, sag=7.0, width=64.0, wrist_w=38.0, cuff=15.0,
                                     color=K.JADE, cuff_color=K.JADE))
    slR, cfR = K.sleeve(K.SleeveSpec(base=ARM_R_BASE, wrist=WR, sag=ARM_R_SAG, width=50.0, wrist_w=36.0, cuff=15.0,
                                     color=K.JADE, cuff_color=K.JADE))
    cfL, cfR = KP.lattice_cuff(cfL), KP.lattice_cuff(cfR)
    chal = KP.chalice(CHAL_X, CHAL_RIM, rim_hw=29.0, bowl_h=44.0, stem_len=CHAL_STEM, foot_hw=(7.0, 24.0))
    by = CHAL_RIM - 12.0
    bub = KP.bubble_column([(CHAL_X - 2, by), (CHAL_X - 6, by - 15), (CHAL_X - 11, by - 33), (CHAL_X - 17, by - 54),
                            (CHAL_X - 24, by - 79)], [6.3, 8.4, 10.5, 12.6, 15.2])
    g0, g1 = chal.meta["grip"]
    assert abs((g0 + g1) / 2 - GRIP_L[1]) < 0.01
    hL = K.fist(GRIP_L, -90.0, wrist=WL, wrist_w=26.0, **HAND_L)
    hR = K.fist(FIST, POLE_DEG, wrist=WR, wrist_w=27.0, **HAND_R)

    # pearl beading (gold on red: solid beads, Aquifer contour) along the trims' outer edges
    blockers = K.U(pole.shape, *[h.shape for h in hair], beard.shape, clasp.shape, chal.shape, bub.shape,
                   hL.hand.shape, hL.thumb.shape, hR.hand.shape, hR.thumb.shape, slL.shape, slR.shape,
                   cfL.shape, cfR.shape)
    trim_f, trim_s = C.Frag(), []
    for lp in lapels:
        # whole pearls only: 3 px of red to the border seam, the pole and the
        # band (a pearl clipped by heal reads as a 'C')
        keep = robe_inner.buffer(-(3.0 + K.FINE / 2)).intersection(K.box(0.0, 0.0, 750.0, 511.0 - 4.1))
        f_, s_ = KP.pearl_trim(lp.meta["outer_pts"], d=8.4, gap=4.4, start=4.0, keep=keep,
                               avoid=blockers.buffer(3.0 + K.MEDIUM / 2 + 0.2), mirror=False)
        trim_f += f_
        trim_s.append(s_)
    trim_s = K.U(*trim_s)
    # ---- the robe: red, ripple rings knocked out where nothing in front covers them ------
    front = K.U(tun.shape, *[lp.shape for lp in lapels])
    rip = K.clip_out(rip, K.U(front.buffer(1.0), trim_s.buffer(4.6)), eps=0.0, trap=0.0)
    # no ring may graze the band: a knockout running into y 511 at a shallow
    # angle leaves a red sliver under it (QA 12 raster); stop them 5.6 px above
    rip = K.clip_in(rip, K.box(0.0, 0.0, 750.0, 511.0 - 5.6))
    robe_fill = C.knockout(K.D(robe_shape), rip)
    robe = K.Part(robe_shape, K.fill(robe_fill, K.RED), robe_m.lines, {})

    # ---- stack, back to front ------------------------------------------------------------
    sc = KP.Scene(rank="K", over_contour={"pearls": 1.6, "bubbles": 1.6,
                                          "posts": (1.6, crown.meta["band"].buffer(3.5))})
    sc.part("collar", K.standing_collar(top_y=COLLAR["top_y"], half_w=COLLAR["half_w"], neck_y=262.0,
                                        shoulder=COLLAR["shoulder"], side_sag=-3.0, rim=9.5, color=K.JADE,
                                        rim_color=K.RED))
    sc.part("robe", robe)
    sc.part("tunic", tun)
    for s, lp in zip((-1, 1), lapels):
        sc.part(f"lapel{s}", lp)
    sc.add("trim", trim_f, trim_s)
    sc.part("pole", pole)
    for s, h in zip((-1, 1), hair):
        sc.part(f"hair{s}", h)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("beard", beard)
    sc.part("moustache", mo)
    sc.part("posts", posts, sil=False)
    sc.part("crown", crown)
    sc.part("pearls", pearls, sil=False)
    sc.part("clasp", clasp)
    sc.part("window", win)
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    sc.part("chalice", chal)
    sc.part("bubbles", bub, sil=False)
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    hL.add_to(sc, "handL", halo=0.0)
    hR.add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "K")
    return sc


def build():
    return figure().layers()
