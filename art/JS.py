"""art/JS.py — J♠ · The Lantern Page (House of the Deep), creative brief §H.3: continuous double-head.

Whole-card jade body (art/_js_robes.py: flame-stitch doublet, strata panels, belt row) about the card
centre, so the SEAM (a gentle diagonal through the body) is only a place where the 180° copy takes over.
The page's red short-caped hood keeps its profile head, crest and gold locks (art/_js_hood.py, _js_face.py).

Hands (both ``K.hand5``, back view, posed by parameters only):
  * the page's LEFT hand (viewer's right) wraps the lantern's chain, thumb up; the cape rises over his
    raised arm and its sleeve ends in the turn-back cuff beside the hand;
  * the page's RIGHT hand (viewer's left) wraps the left side of the rope coil; the jade sleeve opens
    from the body's outer edge and ends in a red turn-back cuff.
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import LineString, Point

from deck import courtkit as K
from deck import frames as F
from deck.motifs import core as C
from art import _js_face as FACE
from art import _js_hood as H
from art import _js_garment as GM
from art import _js_hands as JH
from art import _js_lantern as LN
from art import _js_robes as RB
from art import _js_rope as RP
from art import _js_util as U

DOUBLE_HEAD = "continuous"
SEAM = -10.0
SEAM_STRIP = LineString([(0.0, 525.0 + 375.0 * np.tan(np.radians(SEAM))),
                         (750.0, 525.0 - 375.0 * np.tan(np.radians(SEAM)))]).buffer(4.0)
HEAD = (384.0, 208.0)
XC = 375.0
HAND_SCALE = 0.82
OUTER = ((419, 170), (410, 155), (386, 146), (356, 150), (334, 166), (322, 192), (320, 222), (322, 246), (312, 266),
         (284, 280), (242, 291), (198, 303), (174, 324), (166, 352))
RIGHT = ((600, 354), (606, 322), (598, 288), (580, 264), (552, 252), (520, 258), (488, 274), (462, 288), (440, 298))
RIM = ((440, 298), (418, 290), (394, 282), (372, 264), (362, 238), (362, 210), (370, 188), (388, 174), (406, 168),
       (419, 170))

LX = 508.0                          # the lantern's axis
GRIP_L = (LX, 272.0)                # the page's left hand on the chain
LAN_RING_Y, LAN_S = 345.0, 0.80     # bail ring height and the lantern's body scale
COIL = RP.CoilSpec(c=(292.0, 392.0), rx=40.0, ry=68.0, rot=6.0, strand=9.5, strands=3, lay=58.0, pitch=9.6)
BADGE_AT = (398.0, 326.0)           # the lion clasp, on a plain red roundel
BADGE_R = 31.0
GRIP_R = (254.0, 424.0)             # the page's right hand round the coil's left bundle
RUN, REACH = 80.0, 4.0


def lantern_spec():
    """The lantern of b4e26982 (ring, collar … drip) rescaled to LAN_S below its bail ring."""
    s, y0 = LAN_S, LAN_RING_Y

    def f(y):
        return y0 + 20.0 + (y - 258.0) * s
    return LN.LanternSpec(x=LX, ring=(y0, 14.5), R=58.0 * s, collar=(f(258.0), f(273.0)), eave=f(298.0),
                          cornice=(f(296.0), f(307.0)), body=(f(307.0), f(396.0)), rail=(f(396.0), f(405.0)),
                          plinth=((f(405.0), f(413.0), 50.0 * s), (f(413.0), f(421.0), 36.0 * s)),
                          drip=(f(421.0), f(448.0), 10.0 * s), post_w=9.0, flame=(f(351.0), 44.0 * s, 18.0 * s),
                          cornice_over=6.0, collar_hw=12.0 * s)


def figure(forbid=None):
    sc = K.Scene()
    fc = FACE.page_profile(HEAD, +1, r=42.5, nose_len=10.0)
    size = K.hand_size(fc) * HAND_SCALE
    g = H.HoodGeo(fc, outer=OUTER, right=RIGHT, rim=RIM, O=(380.0, 206.0), Ro=60.0, hem_sag=13.0, dags=6,
                  dag_depth=36.0, dag_concave=3.8, lining=12.0,
                  crest=((406.0, 139.0), (386.0, 126.0), (364.0, 113.0), (340.0, 113.0)), crest_land=-156.0)
    hood = H.hood_part(g)
    body = RB.body()

    # ---- the lantern hand (viewer's right): L / back / wrap on the chain, thumb up, forearm 24 deg
    h_ln = K.hand5(GRIP_L, -90.0, "wrap", size=size, hand="L", view="back", grip_w=11.0)
    sl_ln = JH.sleeve_end(h_ln, run=RUN, zone=g.body, reach=REACH, flare=10.0)
    band_ln, cuff_ln = JH.cuff_band(h_ln, sl_ln, reach=REACH)
    hand_ln = JH.sleeved_hand(h_ln, sl_ln)
    ls = lantern_spec()
    lantern = LN.lantern(ls)
    chain = LN.chain((LX, GRIP_L[1] - 16.0), (LX, LAN_RING_Y - 14.5 - 3.0), link_w=9.0)
    sal = LN.salamander(ls, avoid=lantern.shape)

    # ---- the rope hand (viewer's left): R / back / wrap on the coil's left bundle, forearm 156 deg
    h_rp = K.hand5(GRIP_R, -90.0, "wrap", size=size, hand="R", view="back", grip_w=26.0)
    sl_rp = JH.sleeve_end(h_rp, run=RUN, zone=body, reach=REACH, flare=10.0)
    band_rp, cuff_rp = JH.cuff_band(h_rp, sl_rp, reach=REACH)
    hand_rp = JH.sleeved_hand(h_rp, sl_rp)
    coil = RP.coil(COIL, front=hand_rp.shape, front_min_vis=9.0, front_fills=(hand_rp.shape,), forbid=forbid)
    sc.coil_ticks = coil.meta["ticks"]
    held_rp = JH.held_attribute(coil, hand_rp, keep=lambda m: m.role != "outline")

    # ---- the cape, with the lantern sleeve and its pattern
    badge = K.lion_clasp(BADGE_AT, 40.0)
    cape = cape_part(g, hood, sl_ln, band_ln, cuff_ln, h_ln, BADGE_AT,
                     chain.shape.buffer(7.0).difference(hand_ln.shape.buffer(8.0)))

    robes = RB.garments(sleeves=sl_rp, bands=band_rp, cuff_lines=cuff_rp, no_gold=K.U(SEAM_STRIP, K.c2(cape.shape.buffer(7.0))),
                        front=K.U(lantern.shape, held_rp.shape).buffer(9.0),
                        grain=JH.sleeve_grain(h_rp, sl_rp, band_rp),
                        edges=JH.sleeve_edges(sl_rp, body.buffer(-0.4)))
    belt = GM.belt(RB.doublet(), 440.0, 474.0, xc=XC)
    buckle = GM.buckle((XC, 457.0), w=38.0, h=48.0)
    bshape = K.U(belt.shape, buckle.shape)
    near = buckle.shape.buffer(4.0)
    voids = belt.lines.select(lambda m: m.role != "outline" and not C.Frag([m]).shape().intersects(near))
    belt = K.Part(bshape, K.fill(bshape, K.GOLD), K.outline(bshape) + voids
                  + buckle.lines.select(lambda m: m.role != "outline"), {})
    crest = H.crest_part(g)
    creg = U.largest(crest.shape.difference(K.box(300.0, 172.0, 340.0, 196.0).difference(hood.shape)))
    crest = K.Part(creg, K.fill(creg, K.JADE), K.outline(creg) + crest.lines.select(lambda m: m.role != "outline"))
    clip = g.opening.union(g.lining.buffer(3.0))
    lockS = H.lock([(374, 184), (368, 206), (368, 232), (376, 252)], hw=(6.0, 8.0, 5.0), curl=(6.0, 160.0),
                   side=+1, n=0, clip=clip, line_edge=-1)
    lockF = H.lock([(390, 165), (404, 173), (411, 184)], hw=(6.5, 8.0, 5.0), curl=(5.5, 150.0),
                   side=-1, n=0, clip=clip, line_edge=+1)

    sc.part("robes", robes)
    sc.part("belt+buckle", belt)
    sc.part("crest", crest)
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("lockS", lockS)
    sc.part("lockF", lockF)
    sc.part("cape", cape)
    sc.part("badge", badge)
    sc.part("coil+hand", held_rp)
    sc.add("coil-ticks", coil.meta["front_ticks"], None, sil=False)
    # the chain is a thin line: its knockout stays inside its own ink, or a paper slit shows beside it
    sc.add("chain", chain.frag, chain.shape.buffer(-0.9), sil=False)
    sc.part("salamander", sal, sil=False)
    sc.part("lantern", lantern)
    sc.part("hand", hand_ln)
    return sc


def cape_part(g, hood, sleeve, band, cuff_line, hand, badge_at, bare):
    """The hood and cape with the lantern arm's sleeve: the scale lattice over the red, ending on the sleeve's
    outline, on the clasp's roundel ring and clear of ``bare`` (the chain, which would vanish into it) (a lattice stopping 2 px short of an outline makes the heal cut
    that outline back; the items drawn over the cape clip the lattice themselves), the sleeve's folds and
    grain, the jade turn-back."""
    body = g.body
    red = U.largest(body.difference(g.lining.buffer(0.05)).difference(band))
    disc = K.R(K.circle(badge_at, BADGE_R))
    free = red.buffer(-0.3).difference(sleeve.buffer(-0.6)).difference(disc.buffer(-1.0)).difference(bare)
    scales = U.drop_short(K.pattern(free, "scales", r=9.0, origin=(XC, 525.0)), 9.0)
    fills = K.fill(red, K.RED) + K.fill(g.lining, K.JADE) + K.fill(band, K.JADE, role="turnback")
    lines = hood.lines + scales + K.outline(disc) + cuff_line + JH.sleeve_edges(sleeve, body.buffer(-0.4)) \
        + JH.sleeve_grain(hand, sleeve, band)
    return K.Part(body, fills, lines, {"lining": g.lining})


def build():
    _, res = RP.settle(figure)
    return K.layers(RP.drop_free_ticks(res))
