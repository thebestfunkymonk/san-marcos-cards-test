"""art/JS.py — J♠ · The Lantern Page (House of the Deep), creative brief §H.3.

Built with deck.courtkit (the K♠ hand) plus the page's own parts:
art/_js_face.py (his profile), art/_js_hood.py (hood, crest, cape, locks),
art/_js_lantern.py (lantern, salamander cap, chain), art/_js_rope.py (the
rope coil) and art/_js_garment.py (doublet, sleeves, belt).

Composition plan (top half, card px; the system adds clip, 180° copy, frame,
♠ fault-step band, pips and indices):

| part     | colour | geometry |
|----------|--------|----------|
| head     | paper  | strict profile RIGHT (one-eyed), r 42.5 about (384, 208); eye y 214, chin ≈ 268 |
| face     | ink    | 6 strokes: RULE lid raised, Ø6 pupil at the front (to the light), brow, nostril hook, mouth |
| hood     | red    | skull + 13; rim from the brow back over the temple, round the jaw, under the chin; jade lining 12 |
| crest    | jade   | three fault-steps (treads 139 / 126 / 113) rising to the back, middle course hatched |
| locks    | gold   | a fringe curl under the brim, a side lock rolled at the cheek |
| cape     | red    | over both shoulders (x 166–596, shoulders ≈ 300), six slender stalactite dags |
| livery   | gold   | graduated pearls, the Lion Mark 40 px pendant at (398, 326) |
| doublet  | jade   | Λ chevron rows knocked out; plain placket with 2 gold buttons; right half one course down |
| belt     | gold   | 464–498, karst-void rings, buckle at the front |
| sleeves  | jade   | plain puffed upper sleeves to the band; red forearms (the right one comes out of its sleeve's end: one silhouette line) |
| rope     | paper  | three-turn coil on the viewer's-left shoulder (centre (254, 396.5): its turns cross the forearm clear of the cuff's edges), staggered helix ticks laid against the forearm and re-laid past every tick heal would cut (RP.settle) |
| lantern  | gold   | hexagonal, x 523, R 58: bail 238, roof 258–298, panes 307–396, plinth, drip to 448 |
| salamander | gold | coiled round the bail ring (r 14.5), long flat head raised at the left looking out, two bent legs planted on the collar, tail over the top |
| hands    | paper  | fists: the chain (523, 180), its end inside the fist, the cuff tucked under the back of the hand, red forearm (34 → 27) rising from the hanging sleeve and bowing gently outward so it arrives leaning in (wrist bend 37°); the rope (302, 418), the page's right hand from the back (knuckles and cuff outside), the lobes curling round the coil's far edge, the heel resting on the rope |

Balance (QA 5): paper 49.5, jade 14.4, red 11.3, gold 7.7, ink 17.1 (§C.2 director's waiver ≤ 19; gold 7.5–15 on courts).
"""
from __future__ import annotations

from deck import courtkit as K
from art import _js_face as FACE
from art import _js_hood as H
from art import _js_lantern as LN
from art import _js_rope as RP
from art import _js_garment as GM
from art import _js_util as U

HEAD = (384.0, 208.0)
OUTER = ((419, 170), (410, 155), (386, 146), (356, 150), (334, 166), (322, 192), (320, 222), (322, 246), (312, 266),
         (284, 280), (242, 291), (198, 303), (174, 324), (166, 352))
RIGHT = ((596, 348), (590, 322), (568, 304), (518, 296), (472, 295), (440, 298))
RIM = ((440, 298), (418, 290), (394, 282), (372, 264), (362, 238), (362, 210), (370, 188), (388, 174), (406, 168),
       (419, 170))
LX = 523.0                         # the lantern's axis
FIST_R = (LX, 180.0)               # the chain hand
HAND_R = dict(shaft_w=10.0, back=+1, h=32.0)
# the wrist under the back of the hand, the cuff tucked close under it (a compact raised fist, no
# long bare wrist); the forearm tapers from the hanging sleeve (34) to the cuff (27) and bows
# gently outward (sag −12), so it arrives at the wrist leaning in toward the lantern and the
# hand continues it (wrist bend 47° → 37°) — no straight pole along the frame (right edge
# 606.8 → 596.7); its left edge clear of the salamander cap
WRIST_R = tuple(K.fist_wrist(FIST_R, -90.0, bend=56.0, dist=0.85, **HAND_R))
ARM_R = dict(base=(576.0, 386.0), sag=-12.0, width=34.0, wrist_w=27.0)
FIST_L = (302.0, 418.0)             # on the rope's centreline (x ≈ 305): the fingertip lobes curl past its far edge
HAND_L = dict(shaft_w=31.0, back=-1, h=34.0)      # the page's RIGHT hand, seen from the back: knuckles and cuff outside
WRIST_L = tuple(K.fist_wrist(FIST_L, -96.0, bend=50.0, dist=0.80, **HAND_L))   # cuff close under the heel
COIL = RP.CoilSpec(c=(254.0, 396.5), rx=48.0, ry=80.0, rot=-16.0, strand=10.5, strands=3, lay=58.0, pitch=10.2)


def figure(forbid=None):
    sc = K.Scene(rank="J")
    fc = FACE.page_profile(HEAD, +1, r=42.5, nose_len=10.0)
    g = H.HoodGeo(fc, outer=OUTER, right=RIGHT, rim=RIM, O=(380.0, 206.0), Ro=60.0, hem_sag=13.0, dags=6,
                  dag_depth=36.0, dag_concave=3.8, lining=12.0,
                  crest=((406.0, 139.0), (386.0, 126.0), (364.0, 113.0), (340.0, 113.0)), crest_land=-156.0)
    XC = HEAD[0] + 2.0                                     # the doublet's centre front (the fault)

    # ---- build every part first: the doublet's powder is placed against what stays visible
    sleeveL = U.region_of([(236, 318), (198, 328), (172, 356), (160, 410), (162, 470), (168, 545)],
                          ("L", [(168, 545), (250, 545)]), [(250, 545), (248, 460), (246, 380), (236, 318)])
    # the hanging sleeve's outer edge runs on from the red forearm's base corner (the forearm
    # comes out of the sleeve's end: one silhouette line, no corner knob), hidden above it
    fb = K.sleeve(K.SleeveSpec(wrist=WRIST_R, **ARM_R))[0].meta
    corner = K.P(ARM_R["base"]) - fb["n"] * ARM_R["width"] / 2
    sleeveR = U.region_of([(514, 316), (558, 320), (584, 344), (corner[0] - 2.6, corner[1] - 16.0), tuple(corner),
                           (601, 420), (603, 450), (603, 545)],
                          ("L", [(603, 545), (536, 545)]), [(536, 545), (534, 450), (528, 380), (514, 316)])
    # the doublet's left edge runs under the rope coil (hidden) and leaves it steeply below
    # (it used to run 0–4 px beside the coil's inner edge for 60 px: a long jade sliver)
    doublet = U.region_of([(240, 310), (220, 360), (210, 405), (212, 450), (219, 545)], ("L", [(219, 545), (548, 545)]),
                          [(548, 545), (546, 430), (542, 360), (530, 310)], ("L", [(530, 310), (240, 310)]))
    belt = GM.belt(doublet, 464.0, 498.0, xc=XC)
    buckle = GM.buckle((XC, 480.0), w=38.0, h=46.0)
    buttons = [K.R(K.circle((XC, y), 5.2)) for y in (418.0, 442.0)]
    hood = H.hood_part(g)
    badge = K.lion_clasp((398.0, 326.0), 40.0)
    slL, cfL = K.sleeve(K.SleeveSpec(base=(282.0, 552.0), wrist=WRIST_L, sag=0.0, width=40.0, wrist_w=29.0,
                                     cuff=12.0, color=K.RED, cuff_color=K.RED, folds=0))
    # the helix is laid against the red forearm lying over the coil: every tick either keeps
    # clear of it or runs under its edge (those are stacked just in front of it, see below)
    coil = RP.coil(COIL, front=K.U(slL.shape, cfL.shape), front_min_vis=9.0,
                   front_fills=(slL.shape.difference(cfL.shape.buffer(0.3)), cfL.shape), forbid=forbid)
    sc.coil_ticks = coil.meta["ticks"]
    handL = K.fist(FIST_L, -96.0, wrist=WRIST_L, wrist_w=26.0, **HAND_L)
    slR, cfR = K.sleeve(K.SleeveSpec(wrist=WRIST_R, **ARM_R, cuff=13.0, color=K.RED, cuff_color=K.JADE, folds=0))
    ls = LN.LanternSpec(x=LX, ring=(238.0, 14.5), R=58.0, collar=(258.0, 273.0), eave=298.0, cornice=(296.0, 307.0),
                        body=(307.0, 396.0), rail=(396.0, 405.0), plinth=((405.0, 413.0, 50.0), (413.0, 421.0, 36.0)),
                        drip=(421.0, 448.0, 10.0), post_w=10.0, flame=(351.0, 44.0, 18.0), cornice_over=6.0,
                        collar_hw=12.0)
    lantern = LN.lantern(ls)
    livery = GM.livery([(262, 294), (314, 316), (398, 336), (470, 316), (512, 302)], d=(8.4, 11.6),
                       keep=g.body.difference(g.lining.buffer(1.0)).buffer(-K.CONTOUR / 2),
                       skip=K.U(badge.shape.buffer(1.0),
                                K.U(coil.shape, lantern.shape, slR.shape, cfR.shape).buffer(K.CONTOUR / 2)),
                       links=None, small=6.3)
    front = K.U(belt.shape, buckle.shape, hood.shape, coil.shape, slL.shape, cfL.shape,
                handL.hand.shape, lantern.shape, slR.shape, cfR.shape, K.box(0, 505.0, 750, 600))
    dbl = GM.doublet(doublet, XC, border=0.0, placket=10.0, y_top=330.0, y_bot=520.0, pitch=25.0, slope_deg=26.0,
                     faults=(0.0,), step=7.0, up=True, front=front)

    # ---- the stack, back to front --------------------------------------------------------
    sc.part("sleeveL", GM.sleeve_part(sleeveL))
    sc.part("sleeveR", GM.sleeve_part(sleeveR))
    sc.part("doublet", dbl)
    for k, b in enumerate(buttons):
        sc.add(f"button{k}", K.fill(b, K.GOLD) + K.outline(b, K.FINE), K.R(b).buffer(K.FINE / 2), sil=False)
    sc.part("belt", belt)
    sc.part("buckle", buckle)

    crest = H.crest_part(g)
    # the crest's fall runs 0.2–0.5 px outside the hood's back for its last 8 px and its rounded
    # foot stood proud there (a nub in the silhouette at (325, 180)): below where the two edges
    # meet, the crest is cut to the hood, so the silhouette runs on along the hood in one curve
    creg = U.largest(crest.shape.difference(K.box(300.0, 172.0, 340.0, 196.0).difference(hood.shape)))
    crest = K.Part(creg, K.fill(creg, K.JADE), K.outline(creg) + crest.lines.select(lambda m: m.role != "outline"))
    sc.part("crest", crest)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    clip = g.opening.union(g.lining.buffer(3.0))
    sc.part("lockS", H.lock([(374, 184), (368, 206), (368, 232), (376, 252)], hw=(6.0, 8.0, 5.0), curl=(6.0, 160.0),
                            side=+1, n=0, clip=clip, line_edge=-1))
    sc.part("lockF", H.lock([(390, 165), (404, 173), (411, 184)], hw=(6.5, 8.0, 5.0), curl=(5.5, 150.0),
                            side=-1, n=0, clip=clip, line_edge=+1))
    sc.part("hood", hood)
    sc.part("livery", livery, sil=False)
    sc.part("badge", badge)

    # the rope coil over the left shoulder, the left hand gripping it
    sc.part("coil", coil)
    sc.part("forearmL", slL)
    sc.part("cuffL", cfL)
    sc.add("coil-ticks", coil.meta["front_ticks"], None, sil=False)      # ending inside the forearm's outline
    # the heel of the hand rests on the rope: the pocket the kit leaves between the heel, the
    # cuff and the coil's inner edge (a 4.6 × 1.1 px fleck of doublet inside the ink) is the palm's
    hpL = handL.tucked(sc)
    heel = U.pocket(hpL.shape, [cfL.shape, slL.shape, coil.shape], near=K.U(cfL.shape, coil.shape), r=5.0)
    shL = U.largest(hpL.shape.union(heel.buffer(0.05)))
    sc.add("handL", K.outline(shL) + hpL.meta["inner"], shL)

    # the lantern arm: the forearm rises from the right to the fist on the chain
    sc.part("forearmR", slR)
    sc.part("cuffR", cfR)
    sc.part("chain", LN.chain((LX, FIST_R[1] - 5.0), (LX, 238.0 - 3.0), link_w=11.0), sil=False)   # its end inside the fist
    sc.part("salamander", LN.salamander(ls, avoid=lantern.shape.union(slR.shape)), sil=False)
    sc.part("lantern", lantern)
    K.fist(FIST_R, -90.0, wrist=WRIST_R, wrist_w=26.0, **HAND_R).add_to(sc, "handR", halo=0.0)
    return sc


def build():
    # the rope's helix is laid again past the places heal had to cut a tick (RP.settle); any
    # tick still cut is dropped whole (no half ticks)
    _, res = RP.settle(figure)
    return K.layers(RP.drop_free_ticks(res))
