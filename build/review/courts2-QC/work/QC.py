"""art/QC.py — Q♣ · The Wild-Rice Queen (House of the Reed), creative brief §H.8.

Built with deck.courtkit (the K♠'s hand) plus art/_qc_parts.py for the parts
the kit does not have (rice crown, wild-rice sceptre, egret plumes, bertha,
laced front, puffed sleeve caps, leaf textile).

Headwear (§H.8 'rice-spike coronet', director's note): a goldsmith's crown of
rice, never a feather headband (§J) — a solid, flared gold circlet as wide as
the hair it sits on, with a rim and a base moulding and a set jewel on the face
axis; from behind its rim rise three wrought wild-rice sprays, each a wire rod
with small 3 : 1 gold spikelets on branching pedicels and a HAIRLINE awn off
every tip (the sceptre's female head in miniature). Gold hair under the crown
down to the hairline arc, so no paper parting runs up to the circlet.

Composition plan: filled in after the passes (see the table below).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K            # noqa: E402
from deck.motifs import core as C         # noqa: E402

import _qc_parts as Q                     # noqa: E402
import _qc_sceptre as S                   # noqa: E402
import _qc_gown as GW                     # noqa: E402
import _qc_fan as FN                      # noqa: E402
import _qc_cloak as CL                    # noqa: E402

AX = K.AX
HEAD = (386.0, 206.0)

# ---- body -----------------------------------------------------------------------
GOWN = dict(neck_c=(375.0, 332.0), neck=(338.0, 300.0), neck_sag=-9.0, shoulder=(226.0, 338.0), shoulder_sag=5.0,
            corner_r=34.0, hem=(200.0, 560.0))
GOWN_BORDER = 24.0
LEAF_CLEAR = 6.0
PACK = dict(heading=50.0, lengths=(200.0, 170.0, 145.0, 125.0), ratio=9.0, bend=(12.0, -12.0), gap=6.6, grid=2.5)
BERTHA = 35.0
PEARL = dict(d_end=6.3, d_mid=10.0, gap=6.5, margin=34.0)
# the Lion Mark brooch pins the V of the neckline (the neckline arcs pass under its mane at right
# angles) and sits on the red lining, its ripple ≥ 3 px above the lining's lower edge
BROOCH = (375.0, 336.0)
LACE = dict(top=360.0, hw=(21.0, 15.0), rail=7.5, rung=7.0, pitch=24.0, first=18.0)
CLOAK = dict(top=(322.0, 270.0), shoulder=(168.0, 286.0), hem=(144.0, 560.0), corner_r=50.0, side_sag=-4.0)
PUFFS = ()
# the lining's knocked-out grain columns (left panel; mirrored): bottom → top
GRAINS = (((174.0, 530.0), (192.0, 300.0)),)
GRAIN = dict(pitch=19.0, length=14.0, width=4.8, spread=27.0, split=2.6)
GRAIN_MARGIN = 3.8
MANTLE = dict(edge=12.0, keep_x=(300.0, 450.0))
DRIFT = dict(heading=50.0, length=22.0, width=5.4, along=40.0, across=17.0, stagger=0.5, origin=(375.0, 330.0))

# ---- head -----------------------------------------------------------------------
HAIRLINE = ((343.0, 214.0), (371.0, 180.0), (428.0, 205.0))
HAIR_L = dict(outer=[(380, 157), (350, 158), (328, 169), (314, 192), (308, 218), (308, 242), (302, 268), (291, 294),
                     (283, 322), (278, 352)],
              inner=[(380, 157), (372, 180), (356, 193), (352, 212), (356, 235), (364, 252), (370, 266), (370, 284),
                     (364, 310), (354, 336), (346, 352)],
              n=3)
HAIR_R = dict(outer=[(380, 157), (414, 157), (442, 167), (462, 190), (472, 218), (473, 244), (480, 270), (492, 296),
                     (501, 325), (506, 352)],
              inner=[(380, 157), (392, 178), (410, 190), (418, 210), (418, 232), (410, 250), (400, 263), (397, 285),
                     (404, 312), (414, 352)],
              n=3)
FACE = dict(lids="level", pupil_dx=2.4, eye_dy=8.5, mouth_hw=9.5, bow_rise=1.8, bow_sag=-0.9, lip_hw=6.4, lip_sag=-2.6,
            mouth_dy=32.5, lip_dy=41.0, brow_dy=-16.5, brow_sag=5.0, nose_bot_dy=16.0)
FLICK = (5.0, -1.8)
NECK = ([(356, 236), (362, 262), (365, 285), (359, 312), (349, 336)],
        [(410, 236), (404, 262), (403, 285), (410, 312), (420, 336)])
# the rice crown (§H.8, director's note): a solid gold circlet with a rim and a base moulding, a set
# jewel on the face axis, and three wrought wild-rice sprays rising from behind the rim — small 3 : 1
# spikelets on branching MEDIUM pedicels, a HAIRLINE awn off every tip
CROWN = dict(cx=386.5, top=142.0, h=26.0, bow=4.0, hw=(58.0, 54.0), rim=8.5, base=8.0, jewel=(9.5, 144.5, 6.3),
             far=0.85, sink=5.0)
# (dx from the face axis, tilt°, rod, terminal (L, W, awn),
#  side spikelets ((s on the rod, side, pedicel, pedicel°, L, W, spikelet°, awn), …))
SPRAYS = ((-47.0, -2.0, 28.0, (21.0, 7.0, 14.0), ((8.0, -1, 12.0, 64.0, 19.0, 6.3, 12.0, 14.0),
                                                   (14.0, 1, 12.0, 66.0, 18.0, 6.0, 8.0, 13.0))),
          (51.0, 2.0, 28.0, (21.0, 7.0, 14.0), ((8.0, 1, 12.0, 64.0, 19.0, 6.3, 12.0, 14.0),
                                                 (14.0, -1, 12.0, 66.0, 18.0, 6.0, 8.0, 13.0))),
          (0.0, 0.0, 30.0, (23.0, 7.7, 15.0), ((13.0, -1, 12.0, 64.0, 20.0, 6.7, 10.0, 14.0),
                                               (19.0, 1, 13.0, 64.0, 20.0, 6.7, 10.0, 14.0))))

# ---- attributes -------------------------------------------------------------------
SCEPTRE_X = 541.0
FIST_R = (541.0, 428.0)
# §G.5 on the sceptre, bottom to top: the culm and its node collars, the knop, the male branches
# arching out and down with their florets HANGING on pedicels, then the erect female spikelets
# (pedicelled, alternating, a HAIRLINE awn each) and the terminal spikelet.
SCEPTRE = dict(hw=9.5, knop_y=281.0, knop_hw=13.0, knop_h=12.0, nodes=(350.0, 488.0), node_hw=13.0, node_h=9.0,
               striae=False, rachis_hw=3.0, rachis_top=132.0, terminal=(28.0, 8.4, 16.0),
               female=((206.0, -1, 13.0, 62.0, 27.0, 8.6, 13.0, 15.0), (190.0, 1, 13.0, 62.0, 27.0, 8.6, 13.0, 15.0),
                       (174.0, -1, 11.0, 60.0, 26.0, 8.4, 9.0, 15.0), (158.0, 1, 11.0, 60.0, 26.0, 8.4, 9.0, 15.0)),
               arms=((245.0, 62.0, ((18.0, 50.0), (32.0, 60.0), (12.0, 30.0)), 6.0,
                      ((0.35, 7.0, 22.0, 7.6, 0.0), (0.61, 7.0, 22.0, 7.6, 0.0)), (22.0, 7.6)),))
FIST_L = (316.0, 412.0)
FAN_AXIS = -118.0
# egret plumes, back to front: (heading, length, (bend1, bend2), w_max) — each rises from the ferrule and
# droops outward, the leftmost most
PLUMES = ((-166.0, 118.0, (-6.0, -36.0), 23.0), (-144.0, 140.0, (-8.0, -42.0), 25.0),
          (-123.0, 156.0, (-10.0, -46.0), 26.0), (-103.0, 166.0, (-12.0, -50.0), 26.0),
          (-84.0, 160.0, (-12.0, -52.0), 24.0))
# the plumes' vane: two current lines along each spine, each sweeping out into the outline near the tip
FAN_KW = dict(split=0.42, w_root=8.0, peak=0.38, n=2, power=0.8, mode="vane", barb_room=0.0, barb=28.0)


def head_group(sc):
    """head, hair under the crown, hair locks (in front of the head, clipped
    round the face and below the circlet's top edge), rice crown → the Face"""
    fc = K.face(HEAD, "3/4-left", sex="f", **FACE)
    a = fc.anchors
    s = a["spec"]
    # a lash flick on the NEAR eye only (the kit's ``flick`` would push the far
    # eye's corner through the cheek contour): one RULE tick rising outward
    oc = K.P(float(a["axis"]) + s.eye_dx + s.eye_w / 2, a["eye_y"])
    flick = K.seg(oc, oc + K.P(*FLICK), K.RULE, role="lid")
    sc.add("head", fc.lines + flick + K.outline(fc.head), fc.skin)
    zone = K.R(fc.head).intersection(K.R(K.arc3(*HAIRLINE) + "L520 600L240 600Z").buffer(0))
    # the hair under the crown: gold down to the hairline arc, so no paper parting runs up to the circlet
    cap = K.R(fc.head).difference(zone.buffer(0.01))
    sc.part("hairC", K.Part(cap, K.fill(cap, K.GOLD), K.outline(cap), {}))
    cw = CROWN
    xl, xr = cw["cx"] - cw["hw"][0], cw["cx"] + cw["hw"][0]
    above = K.R(K.Path((200.0, -100.0)).line((xl, -100.0)).line((xl, cw["top"] - cw["bow"])).arc3(
        (cw["cx"], cw["top"]), (xr, cw["top"] - cw["bow"])).line((xr, -100.0)).line((600.0, -100.0)).line(
        (600.0, -150.0)).line((200.0, -150.0)).close().d)
    for nm, spec in (("hairL", HAIR_L), ("hairR", HAIR_R)):
        lk = Q.hair_lock(fc, spec["outer"], spec["inner"], n=spec["n"], hairline=K.U(zone, above))
        sc.part(nm, lk)
    band, sprays = Q.rice_crown(fc, sprays=SPRAYS, **CROWN)
    sc.part("crown-sprays", sprays, sil=False)
    sc.part("crown", band)
    return fc


def head_scene():
    sc = K.Scene(rank="Q")
    sc.part("neck", Q.neck_chest(*NECK, bottom=360.0))
    fc = head_group(sc)
    return sc, fc


def fan_group(sc, parts=None):
    for nm, part in (parts or FN.fan(FIST_L, FAN_AXIS, PLUMES, **FAN_KW)):
        sc.part(nm, part)


def _hand_shapes(*hands):
    out = []
    for h in hands:
        for nm in ("hand", "thumb"):
            pt = getattr(h, nm, None)
            if pt is not None:
                out.append(pt)
    return out


def figure():
    sc = K.Scene(rank="Q")

    # ---- mantle (behind), neck, head, hair (the gown's neckline covers the hair's foot) ----
    gshape, top = Q.gown_outline(**GOWN)
    fan_parts = FN.fan(FIST_L, FAN_AXIS, PLUMES, **FAN_KW)
    cl = Q.cloak(**CLOAK)
    ml = CL.mantle(cl, **MANTLE)
    panel = ml.meta["lining"].difference(gshape.buffer(1.0)).difference(
        K.U(*[pt.shape for _, pt in fan_parts]).buffer(2.0))
    keep = CL.panel_keep(panel, margin=GRAIN_MARGIN)
    knock = CL.leaf_drift(panel, keep=keep, **DRIFT)
    sc.part("cloak", CL.mantle(cl, knock=knock, **MANTLE))
    sc.part("neck", Q.neck_chest(*NECK, bottom=360.0))
    fc = head_group(sc)

    # ---- gown, bertha, lacing ---------------------------------------------------------
    brooch = K.lion_clasp(BROOCH, 40.0)
    bertha = Q.bertha(gshape, top, depth=BERTHA, pearl=PEARL, avoid=brooch.shape, avoid_gap=4.5)
    opening, ladder = Q.laced_front(**LACE)
    # the fan hand's wrist a little nearer the fist; the sceptre hand's out along its axis
    # (courtkit.fist_wrist), the forearm clear of the culm's halo and its lower node
    WL = tuple(K.fist_wrist(FIST_L, FAN_AXIS, bend=52.0, dist=0.9, shaft_w=10.0, back=-1, h=32.0))
    WR = tuple(K.fist_wrist(FIST_R, -90.0, bend=45.0, shaft_w=19.0, back=-1, h=34.0))
    slL, cfL = K.sleeve(K.SleeveSpec(base=(236.0, 560.0), wrist=WL, sag=5.0, width=48.0, wrist_w=34.0, cuff=14.0,
                                     color=K.RED, cuff_color=K.JADE))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(476.0, 560.0), wrist=WR, sag=0.0, width=48.0, wrist_w=32.0, cuff=14.0,
                                     color=K.RED, cuff_color=K.JADE))
    handL = K.fist(FIST_L, FAN_AXIS, shaft_w=10.0, back=-1, wrist=WL, wrist_w=26.0, h=32.0)
    handR = K.fist(FIST_R, -90.0, shaft_w=19.0, back=-1, hand="L", wrist=WR, wrist_w=26.0, h=34.0)   # palm view
    sp = S.rice_sceptre(SCEPTRE_X, **SCEPTRE)
    # no leaf of the textile runs under the opening, the lacing, the brooch or the bertha; a leaf may
    # pass under a sleeve, a hand, the fan or the sceptre, but both its tips show and most of it does
    hard = K.U(bertha.shape, opening.shape, ladder.shape, brooch.shape)
    soft = K.U(slL.shape, slR.shape, cfL.shape, cfR.shape, *[pt.shape for _, pt in fan_parts], sp.shape,
               *[h_.shape for h_ in _hand_shapes(handL, handR)])
    sc.part("gown", GW.gown(gshape, border=GOWN_BORDER, exclude=hard.buffer(LEAF_CLEAR), soft=soft, pack=PACK))
    # the laced opening runs up UNDER the neckline lining: the lacing emerges from the bertha's lower edge
    sc.part("opening", opening)
    sc.part("lacing", ladder)
    sc.part("bertha", bertha)
    sc.part("brooch", brooch)

    # ---- arms, attributes, hands --------------------------------------------------------
    sc.part("sleeveL", slL)
    sc.part("sleeveR", slR)
    fan_group(sc, fan_parts)
    halo_on = ("gown", "cloak", "bertha")
    sc.add("culm", C.Frag(), sp.meta["culm"], halo=K.HALO, halo_only=halo_on)     # the stalk joins the silhouette
    sc.add("sceptre", sp.frag, sp.shape, sil=False, halo=K.HALO, halo_only=halo_on)
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    handL.add_to(sc, "handL", halo=0.0)
    handR.add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    return sc, fc


def build():
    sc, _ = figure()
    return K.layers(Q.compose(sc))


def fan_scene():
    """test harness: the cloak, the fan and its hand only"""
    sc = K.Scene(rank="Q")
    sc.part("cloak", Q.cloak(**CLOAK))
    fan_group(sc)
    K.fist(FIST_L, FAN_AXIS, shaft_w=10.0, back=-1, wrist=tuple(K.fist_wrist(FIST_L, FAN_AXIS, bend=52.0, dist=0.9,
           shaft_w=10.0, back=-1, h=32.0)), wrist_w=26.0, h=32.0).add_to(sc, "handL",
                                                                                                        halo=0.0)
    return sc, None


def compose_scene(sc):
    """the composed Frag exactly as build() prints it (for diagnostics)"""
    return Q.compose(sc)
