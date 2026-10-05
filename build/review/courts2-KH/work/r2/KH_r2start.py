"""art/KH.py — K♥ · The Ferryman King (creative brief §H.4), built with deck.courtkit.

DRAFT v4 (pass 1: robe border, trim lapels, pole hand).

Court review 2 (hands first): each forearm now continues its wrist
(``_arm``: the cuff square to the line the wrist leaves the hand on, the
elbow just outside the frame) — the pole hand was cocked 114° into an
upright forearm and grew a hooked heel; both heels run straight from the
shaft into the cuff (``_kh_hands.straight_heel``). The pole runs on under
the band again, crosses the crown behind the two outer pearls (x 270.6 at
the frame), and the robe's rings no longer hug the arms or the chalice foot
(``_kh_parts.ring_clear``). Balance kept in band by the robe's run, the
sleeves' flare and the collar.
"""
from __future__ import annotations

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C

from art import _kh_hands as KHN
from art import _kh_head as KHH
from art import _kh_parts as KP
from art import _kh_window as KW

AX = K.AX
HEAD = (AX, 207.0)
FIST = (520.0, 456.0)          # §H.4: the pole rises from the viewer's-right hand (≈ 520, 470)
POLE_TOP = (270.6, 55.0)       # ... cropped by the frame's top edge at x ≈ 280 (270: the edges pass behind the
                               # outer posts, not along them — the least pole edge left in the gaps between posts)
CHAL_X = 233.5                  # 236 → 233.5: the foot's rim tip clears the left lapel edge
CHAL_RIM = 292.0
CHAL_STEM = 84.0                # a bare stem ≥ 5 px above and below the fist (grip 369.5–418)
CHAL_FOOT_DROP = 6.0            # the stem runs on this much below the grip: the heel and the foot's dome
                               # no longer pinch a red sliver between them at the stem
CLASP = (AX, 346.0)
WIN_C = (AX, 432.0)
LENS = K.LensSpec(throat_y=280.0, half_w=88.0, lapel_w=46.0)
LAPEL_X = 306.0
ROBE = K.MantleSpec(neck_y=262.0, neck_heading=170.0, run=140.0, corner_r=34.0, side_heading=97.0)  # run 146 → 140: paper back to 45 % after the arms moved

COLLAR = dict(top_y=231.0, half_w=112.0, shoulder=(-130.0, 304.0))   # 233 → 231, rim 9.5 → 7.5: jade back to 15 %
COLLAR_RIM = 7.5
FACE_KW = dict(age="elder", lids="level", lid_sag=5.4, low_sag=3.0, brow_sag=5.0, brow_dy=-14.0, brow_drop=3.0,
               bow_rise=0.4, bow_sag=-2.2, lip_sag=-2.6, lip_hw=6.5)
HAIR = K.HairSpec(bulge=(-64.0, 34.0), bottom=(-52.0, 66.0), ribbons=4, over=12.0)
MOUSTACHE = KHH.LiftMoustache(tip=(-30.0, 9.0), arch=3.4, under=5.6)
BEARD = KHH.LobeBeard()
BEARD_LOCKS = {"mode": "manual", "locks": [            # (start, mid, end) dx/dy from the axis/egg centre, turn°, r
    ((-36.0, 30.0), (-41.4, 57.0), (-38.5, 81.0), -180.0, 4.8),     # curl 7 px higher: clear of the pole's edge
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
GRIP_L = (CHAL_X, CHAL_RIM + 44.0 + 9.0 + 16.0 + 6.5 + 2.0 + (CHAL_STEM - 9.0 - 16.0 - 6.5 - 4.0) / 2)   # centre of the grip


def _arm(at, axis_deg, hand_kw, bend, dist, reach=110.0):
    """A fist's wrist (courtkit.fist_wrist: ``dist`` × the block height from
    the back of the hand, ``bend``° off the knuckle axis toward the shaft's
    lower end) and the forearm's base ``reach`` px on along the SAME line:
    the forearm continues the wrist (no kink at the cuff, no hooked heel).
    → (wrist, base)."""
    g = K.fist_geom(at, axis_deg, **hand_kw)
    b = np.radians(bend)
    d = np.cos(b) * g["axis"] + np.sin(b) * g["down"]
    w = g["Bs"] + g["hb"] * dist * d
    return tuple(w), tuple(w + reach * d)


# the two forearms rise from the lower corners (the elbows just outside the
# frame, under the robe's fall) along the line of each wrist: the chalice
# hand's forearm 45° below the horizontal, the pole hand's 23° — a wrist
# cocked more than ≈ 55° off the knuckles reads as broken (the old pole hand
# was bent 114° into an upright forearm and grew a hook at the heel)
(WL, ARM_L_BASE), (WR, ARM_R_BASE) = _arm(GRIP_L, -90.0, HAND_L, 45.0, 1.10), _arm(FIST, POLE_DEG, HAND_R, 55.0, 1.02)
WRISTS = (WL, WR)
POLE_BUTT = None                # the pole runs on under the band (None), or a rounded butt this far below the fist
SLEEVE_L = dict(base=ARM_L_BASE, sag=0.0, width=84.0, wrist_w=40.0, cuff=20.0)   # flaring to the elbow
SLEEVE_R = dict(base=ARM_R_BASE, sag=0.0, width=82.0, wrist_w=38.0, cuff=20.0)
HEEL_FIX = ("L", "R")           # hands whose heel notch is filled (KHN.straight_heel)
RING_CLEAR = True               # cut robe rings that hug a front part's outline (KP.ring_clear)
CHAL_FOOT = (7.0, 21.5)          # foot half-widths (top, rim): the rim tip ≥ 6 px off the lapel edge
CHAL_TIP_R = 2.2                # the chalice foot's rim tips rounded (a knife edge loses its outline)
CHAL_ENGRAVE_GAP = 4.3          # rosette ≥ 4.2 px of gold clear of the lip moulding and the bowl (was 3.0: ring cut)
TRIM_MIN_RUN = 2                # no lone pearl left between the pole and the band


def _pole_line():
    p0, p1 = K.P(FIST), K.P(POLE_TOP)
    u = (p1 - p0) / float(np.hypot(*(p1 - p0)))
    if POLE_BUTT is None:
        return p0 - u * ((560.0 - p0[1]) / -u[1]), p1 + u * 40.0
    return p0 - u * POLE_BUTT, p1 + u * 40.0          # the butt shows just below the fist (clear of the forearm)


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
    pole = KP.pole(lo, hi, round_low=POLE_BUTT is not None, **POLE_KW)
    hair = [K.hair_fall(fc, s, HAIR) for s in (-1, 1)]
    mo = KHH.moustache(fc, MOUSTACHE)
    beard = KHH.lobe_beard(fc, BEARD, mo=mo, lines=BEARD_LOCKS)
    crown, posts, pearls = KP.post_crown2()
    clasp = K.lion_clasp(CLASP, 40.0)
    win = KW.window(*WIN_C, **WIN_KW)
    WL, WR = WRISTS
    slL, cfL = K.sleeve(K.SleeveSpec(wrist=WL, color=K.JADE, cuff_color=K.JADE, **SLEEVE_L))
    slR, cfR = K.sleeve(K.SleeveSpec(wrist=WR, color=K.JADE, cuff_color=K.JADE, **SLEEVE_R))
    cfL, cfR = KP.lattice_cuff(cfL), KP.lattice_cuff(cfR)
    chal = KP.chalice(CHAL_X, CHAL_RIM, rim_hw=29.0, bowl_h=44.0, stem_len=CHAL_STEM + CHAL_FOOT_DROP,
                      foot_hw=CHAL_FOOT,
                      tip_r=CHAL_TIP_R, engrave_gap=CHAL_ENGRAVE_GAP)
    by = CHAL_RIM - 12.0
    bub = KP.bubble_column([(CHAL_X - 2, by), (CHAL_X - 6, by - 15), (CHAL_X - 11, by - 33), (CHAL_X - 17, by - 54),
                            (CHAL_X - 24, by - 79)], [6.3, 8.4, 10.5, 12.6, 15.2])
    g0, g1 = chal.meta["grip"]
    assert abs((g0 + g1 - CHAL_FOOT_DROP) / 2 - GRIP_L[1]) < 0.01
    hL = K.fist(GRIP_L, -90.0, wrist=WL, wrist_w=26.0, **HAND_L)
    hR = K.fist(FIST, POLE_DEG, wrist=WR, wrist_w=27.0, **HAND_R)
    if "L" in HEEL_FIX:
        hL = KHN.straight_heel(hL, GRIP_L, -90.0, **HAND_L)
    if "R" in HEEL_FIX:
        hR = KHN.straight_heel(hR, FIST, POLE_DEG, **HAND_R)

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
                               avoid=blockers.buffer(3.0 + K.MEDIUM / 2 + 0.2), mirror=False, min_run=TRIM_MIN_RUN)
        trim_f += f_
        trim_s.append(s_)
    trim_s = K.U(*trim_s)
    # ---- the robe: red, ripple rings knocked out where nothing in front covers them ------
    front = K.U(tun.shape, *[lp.shape for lp in lapels])
    rip = K.clip_out(rip, K.U(front.buffer(1.0), trim_s.buffer(4.6)), eps=0.0, trap=0.0)
    # no ring may graze the band: a knockout running into y 511 at a shallow
    # angle leaves a red sliver under it (QA 12 raster); stop them 5.6 px above
    rip = K.clip_in(rip, K.box(0.0, 0.0, 750.0, 511.0 - 5.6))
    if RING_CLEAR:
        # no paper ring hugs an arm, the chalice or the pole (heal would trim THEIR outlines)
        # (the lapels and their pearls already keep the rings off: clip_out above; round the
        # chalice's stem and knop the rings pass behind as they should — only its foot counts)
        foot = chal.shape.intersection(K.box(0.0, g1 - 4.0, 750.0, 750.0))
        fr = K.U(slL.shape, slR.shape, cfL.shape, cfR.shape, foot, hL.hand.shape, hR.hand.shape)
        rip = KP.ring_clear(rip, fr, hide=K.U(pole.shape, chal.shape, bub.shape))
    robe_fill = C.knockout(K.D(robe_shape), rip)
    # the border seam: no stub left between a forearm and the band (a lone tick)
    robe_lines = KP.drop_stubs(robe_m.lines, K.U(slL.shape, slR.shape, cfL.shape, cfR.shape, hL.hand.shape,
                                                 hR.hand.shape, pole.shape, K.box(0.0, 511.0, 750.0, 1050.0)),
                               roles=("seam",), min_vis=30.0)
    robe = K.Part(robe_shape, K.fill(robe_fill, K.RED), robe_lines, {})

    # ---- stack, back to front ------------------------------------------------------------
    # the posts hide the silhouette CONTOUR behind them, except along the band's own top
    # edge (kept whole under the post feet) — but where a foot stands on the POLE the
    # CONTOUR there is the pole's edge: hide it too (no heavy stub at the foot)
    sc = KP.Scene(rank="K", over_contour={"pearls": 1.6, "bubbles": 1.6,
                                          "posts": (1.6, crown.meta["band"].buffer(3.5).difference(pole.shape))})
    sc.part("collar", K.standing_collar(top_y=COLLAR["top_y"], half_w=COLLAR["half_w"], neck_y=262.0,
                                        shoulder=COLLAR["shoulder"], side_sag=-3.0, rim=COLLAR_RIM, color=K.JADE,
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
