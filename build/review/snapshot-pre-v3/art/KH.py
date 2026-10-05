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

Round 2 (verifier): the robe's side CONTOUR met the cuffs' outer corners
(heal cut both cuff outlines open) — the arms are re-seated and the cuffs
are 14 deep, so the contour meets each sleeve ≥ 11 px beyond its cuff; a
ring that slipped under a hand/cuff junction is cut (``ring_clear``
corners). The crown's circlet keeps ONE unbroken CONTOUR over the pole (no
knots at the post feet) and the pole's edges meet the two outer pearls
squarer (x 271.5); lines behind the fists end on their outlines (no cap
nubs: ``Scene(stroke_ends=…)``); the lens of right lapel beside the pole is
plain (scale fragments there grazed the pole into free caps).
"""
from __future__ import annotations

import numpy as np
import shapely

from deck import courtkit as K
from deck.motifs import core as C

from art import _kh_hands as KHN
from art import _kh_head as KHH
from art import _kh_parts as KP
from art import _kh_window as KW

AX = K.AX
HEAD = (AX, 207.0)
FIST = (520.0, 456.0)          # §H.4: the pole rises from the viewer's-right hand (≈ 520, 470)
POLE_TOP = (271.5, 55.0)       # ... cropped by the frame's top edge at x ≈ 280 (270–271.5: each edge vanishes
                               # into one pearl and stays hidden behind its post down to the circlet — no stubs
                               # between post and band; 271.5 meets the pearls at 56° / 71°, the squarest pair)
CHAL_X = 233.5                  # 236 → 233.5: the foot's rim tip clears the left lapel edge
CHAL_RIM = 292.0
CHAL_STEM = 84.0                # a bare stem ≥ 5 px above and below the fist (grip 369.5–418)
CHAL_FOOT_DROP = 6.0            # the stem runs on this much below the grip: the heel and the foot's dome
                               # no longer pinch a red sliver between them at the stem
CLASP = (AX, 346.0)
WIN_C = (AX, 432.0)
LENS = K.LensSpec(throat_y=280.0, half_w=92.0, lapel_w=46.0)   # (r3) 88 → 92: jade back over 15 % after the
                                # lens beside the pole went (the chalice foot still clears the lapel by 6.0)
LAPEL_X = 306.0
ROBE = K.MantleSpec(neck_y=262.0, neck_heading=170.0, run=140.0, corner_r=34.0, side_heading=97.0)  # run 146 → 140: paper back to 45 % after the arms moved

COLLAR = dict(top_y=231.0, half_w=112.0, shoulder=(-130.0, 304.0))   # 233 → 231: jade back to 15 %
COLLAR_RIM = 9.5                # (r3) 7.5 → 9.5 again: 4.8 px of red lining between the CONTOUR and the fold
                                # (§I.12 ≥ 4.2; at 7.5 it was a 2.8 px pinstripe, the thinnest rim in the deck)
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
# hand's forearm 48° below the horizontal, the pole hand's 32° — within the
# kit's 65° wrist limit (the old pole hand was bent 114° into an upright
# forearm and grew a hook at the heel)
# (round 2) the cuffs sit ≥ 10 px inside the robe's silhouette: the robe's side
# CONTOUR meets each sleeve's top edge on the plain sleeve beyond the cuff (it
# landed on the cuffs' outer corners: heal cut the cuff outline open there),
# the border seam slips under the back of the hand ≥ 8 px from the cuff, and
# the cuffs are 14 deep (K♣ 14, K♠ 16) — scanned: work/r2/scan*.py
ARM_L = dict(bend=48.0, dist=1.05)
ARM_R = dict(bend=64.0, dist=1.10)


def _arms():
    """((wrist, base) of the chalice arm, (wrist, base) of the pole arm)."""
    return _arm(GRIP_L, -90.0, HAND_L, **ARM_L), _arm(FIST, POLE_DEG, HAND_R, **ARM_R)


POLE_BUTT = None                # the pole runs on under the band (None), or a rounded butt this far below the fist
SLEEVE_L = dict(sag=0.0, width=80.0, wrist_w=36.0, cuff=14.0)   # flaring to the elbow ((r3) 74 → 80, 62 → 68:
SLEEVE_R = dict(sag=0.0, width=68.0, wrist_w=32.0, cuff=14.0)   # jade; the wrists and cuffs are unchanged)
HEEL_FIX = ("L", "R")           # hands whose heel notch is filled (KHN.straight_heel)
RING_CLEAR = True               # cut robe rings that hug a front part's outline (KP.ring_clear)
CLOSE_RINGS = True              # (r3) no pinch where a ring's path opens (KP.close_starts)
RING_CORNERS = True             # ... or pass within 7.3 px of one of its corners (a hand meeting its cuff)
CHAL_FOOT = (7.0, 21.5)          # foot half-widths (top, rim): the rim tip ≥ 6 px off the lapel edge
CHAL_TIP_R = 2.2                # the chalice foot's rim tips rounded (a knife edge loses its outline)
CHAL_ENGRAVE_GAP = 4.3          # rosette ≥ 4.2 px of gold clear of the lip moulding and the bowl (was 3.0: ring cut)
TRIM_MIN_RUN = 2                # no lone pearl left between the pole and the band
LAPEL_PLAIN = False             # the lens of right lapel beside the pole carries no scales (r3: it does again)
LAPEL_TUCK = "hide"                # (r3) the lens's tip turns square into the pole on this radius (KP.tuck_lens):
                                # its outer edge ran into the pole's at 20°, a long tapering jade wedge
END_EPS = 0.4                   # lines behind a fist end this far OUTSIDE it, on its outline (no cap nubs)
END_ALSO = ("chalice",)         # (r3) ... and behind the chalice: the robe's neckline ended 0.2 px inside the
                                # lip's right corner and its round cap poked into the gold of the lip
BAND_WHOLE = True               # the circlet's top edge one unbroken CONTOUR over the pole (no knots at the post feet)
POST_POLE = 3.0                 # the posts hide the pole-edge CONTOUR right down to the circlet within this of the pole
SLEEVE_JADE = True              # (r3) the sleeves' jade starts halfway down the cuffs (_sleeve_jade)
CONTOUR_FILLET = 6.0            # (r3) the CONTOUR's corner where the robe's shoulder meets the chalice: filleted
PEARL_EPS = 2.2                 # the pole's edge CONTOUR stops this far outside a pearl's ring (its round
                                # cap reaches into the ring's ink, not through it into the gold)


def _sleeve_jade(sl, wrist, base, cuff):
    """The sleeve's jade starts halfway down its cuff: the cuff (jade, its own
    fill and outline) hides everything nearer the wrist, and the jade that ran
    on under the cuff's top edge — the sleeve's lip, and the trap band the
    stack leaves along that edge — ended 1.6 px from the fist's outline at the
    hand/cuff corner, so heal cut 3.9 px out of the fist's wrist line (a red
    speck at the junction). → Part (shape and lines unchanged)."""
    W, B = K.P(wrist), K.P(base)
    d = (B - W) / float(np.hypot(*(B - W)))
    n = K.P(d[1], -d[0])
    c = W + d * (cuff / 2.0)
    far = K.R(K.D(shapely.Polygon([tuple(c + n * 300), tuple(c - n * 300),
                                   tuple(c - n * 300 + d * 400), tuple(c + n * 300 + d * 400)])))
    body = sl.shape.intersection(far)
    rest = sl.fills.select(lambda m: m.layer != "jade")
    return K.Part(sl.shape, K.fill(body, K.JADE) + rest, sl.lines, sl.meta)


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
    ring_starts = rip.meta.get("starts", ())
    robe_shape = robe_m.shape
    tun = K.tunic(LENS, pattern_kind=None)
    tun = K.Part(tun.shape, K.fill(tun.shape, K.JADE), tun.lines, tun.meta)
    lapels = [KP.trim_lapel(LENS, s, robe_shape, shoulder_x=LAPEL_X, collar_sag=-4.0, r=11.0, bead_off=11.4)
              for s in (-1, 1)]
    lo, hi = _pole_line()
    pole = KP.pole(lo, hi, round_low=POLE_BUTT is not None, **POLE_KW)
    if LAPEL_TUCK == "hide":
        # the lens of right lapel beyond the pole goes: the lapel's outer edge runs on under the
        # pole from the collar down (it met the pole's edge at 20°: a long tapering jade wedge)
        lp = lapels[1]
        rest = sorted(K._polys_of(lp.shape.difference(pole.shape)), key=lambda g: g.area)
        if len(rest) > 1:
            shp = lp.shape.difference(rest[0].buffer(1.0))     # (its new edge 1 px under the pole)
            shp = max(K._polys_of(shp), key=lambda g: g.area)
            lapels[1] = K.Part(shp, K.fill(shp, K.JADE),
                               K.outline(shp) + K.clip_in(lp.lines.select(lambda m: m.role == "scale"), shp),
                               lp.meta)
    elif LAPEL_TUCK:
        lapels[1], _tuck = KP.tuck_lens(lapels[1], pole, r=LAPEL_TUCK, scales=not LAPEL_PLAIN)
    elif LAPEL_PLAIN:
        # the pole crosses the right lapel's outer edge twice, leaving a lens of lapel
        # (≤ 20 px wide) between its right edge and the robe: scale fragments there
        # grazed the pole and heal cut them into free caps — the lens is left plain
        lp = lapels[1]
        rest = sorted(K._polys_of(lp.shape.difference(pole.shape)), key=lambda g: g.area)
        if len(rest) > 1:
            sc_ = lp.lines.select(lambda m: m.role == "scale")
            lapels[1] = K.Part(lp.shape, lp.fills, lp.lines.select(lambda m: m.role != "scale")
                               + K.clip_out(sc_, rest[0].buffer(0.5), eps=0.0, trap=0.0), lp.meta)
    hair = [K.hair_fall(fc, s, HAIR) for s in (-1, 1)]
    mo = KHH.moustache(fc, MOUSTACHE)
    beard = KHH.lobe_beard(fc, BEARD, mo=mo, lines=BEARD_LOCKS)
    crown, posts, pearls = KP.post_crown2()
    clasp = K.lion_clasp(CLASP, 40.0)
    win = KW.window(*WIN_C, **WIN_KW)
    (WL, BL), (WR, BR) = _arms()
    slL, cfL = K.sleeve(K.SleeveSpec(wrist=WL, base=BL, color=K.JADE, cuff_color=K.JADE, **SLEEVE_L))
    slR, cfR = K.sleeve(K.SleeveSpec(wrist=WR, base=BR, color=K.JADE, cuff_color=K.JADE, **SLEEVE_R))
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
    if SLEEVE_JADE:
        slL = _sleeve_jade(slL, WL, BL, SLEEVE_L["cuff"])
        slR = _sleeve_jade(slR, WR, BR, SLEEVE_R["cuff"])

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
        rip = KP.ring_clear(rip, fr, hide=K.U(pole.shape, chal.shape, bub.shape),
                            corners=KP.front_corners(fr) if RING_CORNERS else ())
    if CLOSE_RINGS:
        rip = KP.close_starts(rip, ring_starts)
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
    band_ct = KP.band_top_contour(crown.meta["band"], pole.shape.buffer(K.CONTOUR)) if BAND_WHOLE else None
    sc = KP.Scene(rank="K", over_contour={"pearls": PEARL_EPS, "bubbles": 1.6,
                                          "posts": (1.6, crown.meta["band"].buffer(3.5).difference(
                                              pole.shape.buffer(POST_POLE)))},
                  extra_contour=band_ct,
                  stroke_ends={n: END_EPS for n in ("handL", "handL-thumb", "handR", "handR-thumb") + END_ALSO}
                  if END_EPS else None)
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
    if CONTOUR_FILLET:
        # where the robe's shoulder meets the chalice bowl on the silhouette (KP.Scene fillets)
        sil_b = sc.silhouette().boundary
        hits = robe_shape.exterior.intersection(chal.shape.exterior)
        pts = [q for q in getattr(hits, "geoms", [hits]) if q.geom_type == "Point" and sil_b.distance(q) < 0.05]
        sc.fillets = [((q.x, q.y), CONTOUR_FILLET) for q in pts]
    return sc


def build():
    return figure().layers()
