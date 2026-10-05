"""art/KH.py — K♥ · The Ferryman King (creative brief §H.4), built with deck.courtkit.

DRAFT v3 (pass 1: body restructure).
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
FIST = (508.0, 404.0)
POLE_TOP = (280.0, 55.0)
CHAL_X = 244.0
CHAL_RIM = 300.0
CLASP = (AX, 348.0)
WIN_C = (AX, 428.0)
LENS = K.LensSpec(throat_y=280.0, half_w=70.0, lapel_w=56.0)
LAPEL_X = 296.0


POLE_DEG = float(np.degrees(np.arctan2(POLE_TOP[1] - FIST[1], POLE_TOP[0] - FIST[0])))


def _pole_line():
    p0, p1 = K.P(FIST), K.P(POLE_TOP)
    u = (p1 - p0) / float(np.hypot(*(p1 - p0)))
    return p0 - u * 140.0, p1 + u * 40.0


def figure():
    sc = KP.Scene(rank="K", over_contour=("pearls", "bubbles"))
    fc = K.face(HEAD, "frontal", age="elder", lids="level", brow_sag=4.2, low_sag=4.4)

    # ---- garments ------------------------------------------------------------------------
    ms = K.MantleSpec(neck_y=262.0, neck_heading=170.0, run=146.0, corner_r=34.0, side_heading=97.0)
    robe_shape = K.mantle(ms).shape
    tun = K.tunic(LENS, pattern_kind=None)
    tun = K.Part(tun.shape, K.fill(tun.shape, K.JADE), tun.lines, tun.meta)
    lapels = [KP.trim_lapel(LENS, s, robe_shape, shoulder_x=LAPEL_X, collar_sag=-4.0, r=10.5) for s in (-1, 1)]
    lo, hi = _pole_line()
    pole = KP.pole(lo, hi, 18.0, bands_y=(84.0, 352.0, 466.0))
    hs = K.HairSpec(bulge=(-65.0, 40.0), bottom=(-54.0, 98.0), ribbons=4, over=4.0)
    hair = [K.hair_fall(fc, s, hs) for s in (-1, 1)]
    mo = KHH.moustache(fc, KHH.LiftMoustache(tip=(-30.0, 9.0), arch=3.4, under=5.6))
    beard = KHH.lobe_beard(fc, mo=mo, lines={"mode": "manual", "locks": [
        ((-36.0, 25.0), (-41.0, 55.0), (-36.0, 83.0), -215.0, 5.6),
        ((-19.5, 72.0), (-20.5, 87.0), (-16.0, 99.0), -200.0, 4.8)]})
    crown, pearls = KP.post_crown()
    clasp = K.lion_clasp(CLASP, 40.0)
    win = KW.window(*WIN_C)
    WL, WR = (214.0, 424.0), (544.0, 440.0)
    slL, cfL = K.sleeve(K.SleeveSpec(base=(160.0, 552.0), wrist=WL, sag=7.0, width=58.0, wrist_w=36.0, cuff=14.0,
                                     color=K.JADE, cuff_color=K.GOLD))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(580.0, 552.0), wrist=WR, sag=-7.0, width=58.0, wrist_w=36.0, cuff=14.0,
                                     color=K.JADE, cuff_color=K.GOLD))
    chal = KP.chalice(CHAL_X, CHAL_RIM, rim_hw=29.0, bowl_h=39.0, stem_len=62.0, foot_hw=(7.0, 24.0))
    by = CHAL_RIM - 12.0
    bub = KP.bubble_column([(CHAL_X - 1, by), (CHAL_X - 3, by - 15), (CHAL_X - 6, by - 33), (CHAL_X - 10, by - 54),
                            (CHAL_X - 15, by - 79)], [6.3, 8.4, 10.5, 12.6, 15.2])
    g0, g1 = chal.meta["grip"]
    hL = K.fist((CHAL_X, (g0 + g1) / 2), -90.0, shaft_w=10.4, back=-1, wrist=WL, wrist_w=26.0, h=min(32.0, g1 - g0))
    hR = K.fist(FIST, POLE_DEG, shaft_w=17.0, back=+1, wrist=WR, wrist_w=26.0, h=34.0)

    # pearl beading (gold on red: solid beads, Aquifer contour) along the lapels' outer edges
    blockers = K.U(pole.shape, *[h.shape for h in hair], beard.shape, clasp.shape, chal.shape, bub.shape,
                   hL.hand.shape, hL.thumb.shape, hR.hand.shape, hR.thumb.shape, slL.shape, slR.shape,
                   cfL.shape, cfR.shape)
    trim_f, trim_s = C.Frag(), []
    for lp in lapels:
        f_, s_ = KP.pearl_trim(lp.meta["outer_pts"], d=8.4, gap=4.4, start=4.0, keep=robe_shape.buffer(-9.0),
                               avoid=blockers.buffer(3.6), mirror=False)
        trim_f += f_
        trim_s.append(s_)
    trim_s = K.U(*trim_s)
    # ---- the robe: red, ripple rings knocked out where nothing in front covers them ------
    front = K.U(tun.shape, *[lp.shape for lp in lapels])
    hard = K.U(front, trim_s, clasp.shape, bub.shape)
    soft = K.U(pole.shape, slL.shape, slR.shape, cfL.shape, cfR.shape, chal.shape, hL.hand.shape, hL.thumb.shape,
               hR.hand.shape, hR.thumb.shape)
    rip = KP.ripple_textile(robe_shape, origin=(AX, 318.0), pitch=(96.0, 41.0))
    robe_fill = C.knockout(K.D(robe_shape), rip)
    robe = K.Part(robe_shape, K.fill(robe_fill, K.RED), K.outline(robe_shape), {})

    # ---- stack, back to front ------------------------------------------------------------
    sc.part("collar", K.standing_collar(top_y=236.0, half_w=104.0, neck_y=262.0, shoulder=(-122.0, 300.0),
                                        side_sag=-3.0, rim=9.5, color=K.JADE, rim_color=K.RED))
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
