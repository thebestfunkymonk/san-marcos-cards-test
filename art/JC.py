"""art/JC.py — J♣ · The River Squire (House of the Reed), creative brief §H.9: continuous double-head, two cuffed hands.

The red jerkin and its peplum (art/_jc_garments.py) are point-symmetric about the card centre: they run from
one squire's shoulders to the other's, so SEAM (a gentle diagonal through the peplum) is only a place where the
180° copy takes over — no band, medallion or divider.

Hands (both ``K.hand5``, back view, posed by parameters):
  * the squire's LEFT hand (viewer's right) wraps the paddle's loom, thumb up; its wrist leaves the puffed
    jade sleeve at 24°, down and out to the sleeve's elbow;
  * the squire's RIGHT hand (viewer's left) lies on the belt (rest pose, back view), the jade sleeve turning
    down to its wrist from the elbow out at the figure's side.

Head, cap, heron plume, hair, collar, Lion Mark, pecan-husk buckle and paddle are the J♣ parts of art/_jc_*.py.
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString

from deck import courtkit as K
from deck.motifs import core as C
from art import _jc_body as B
from art import _jc_garments as G
from art import _jc_head as H
from art import _jc_paddle as PD
from art import _jc_parts as J

DOUBLE_HEAD = "continuous"
SEAM = -8.0
AX = K.AX
HEAD = (385.0, 207.0)
HAND_SCALE = 0.82
FACE_KW = dict(lids="raised", pupil_dx=-3.0, pupil_tuck=-0.4)
HAIR_ENDS = [168.0, 152.0, 118.0, 98.0]

BELT_Y = 440.0
BELT_RISE = (2.0, 4.0)
BELT_NODES = (47.0, 4.0)
BUCKLE = (358.0, BELT_Y + 4.0)
CLASP = (370.0, 340.0)
BUTTONS = ((363.5, 372.0), (361.2, 396.0))

CAP = dict(roll_c=(388.0, 174.0), roll_r=(50.0, 7.0), roll_h=14.0, crown_c=(398.0, 147.0), crown_r=(68.0, 19.0),
           crown_rot=-2.0)
BROOCH = (448.0, 164.0)
BROOCH_KW = dict(r=12.5, u=12.0, dy=0.0)
PLUME = [(448, 164), (457, 140), (462, 116), (474, 98), (492, 88), (510, 82)]
PLUME_KW = dict(w_max=30.0, w_root=11.0, quill=34.0, quill_w=11.0, quill_back=4.0, swell=0.42, tip_pow=0.8,
                vane_from=24.0, tip_r=4.5, bulb=1.8,
                lines=((-3.8, 42.0, -52.0, -1), (3.8, 40.0, -36.0, -1)), curl_deg=50.0)
COLLAR = dict(top=((344.0, 289.0), (414.0, 286.0)), top_sag=-7.0, foot=((338.0, 314.0), (420.0, 310.0)),
              foot_sag=-7.0)

# the doublet (jade bust, under the jerkin) down to the belt's centre line
TORSO = ([(342, 301), (300, 310), (284, 318), (262, 330), (244, 340)], [(244, 340), (246, 400), (244, BELT_Y + 12)],
         ("L", [(244, BELT_Y + 12), (524, BELT_Y + 12)]), [(524, BELT_Y + 12), (526, 400), (524, 340)],
         [(524, 340), (510, 328), (494, 314), (466, 306), (418, 300)], ("L", [(418, 300), (342, 301)]))
E_L = [(334, 302), (338, 350), (358, BELT_Y - 4.0)]
E_R = [(410, 300), (390, 360), (358, BELT_Y - 4.0)]

TRELLIS = (64.0, 88.0)
SPRIG = dict(hx=TRELLIS[0], hy=TRELLIS[1], heading=-90.0, nut=(13.0, 8.6), nut_spread=24.0,
             leaf_kw=dict(length=36.0, pairs=3, leaflet=(10.0, 3.2), angle=55.0, step=7.0, falcate=0.6, first=6.0,
                          shrink=0.03, bend=1.5))

# ---- the paddle (upright, blade up) and its hand -----------------------------------------------------
PADDLE_X = 538.0
GRIP_P = (PADDLE_X, 398.0)
PADDLE = dict(tip=104.0, square=24.0, hw=27.0, widest=210.0, shoulder=266.0, band=(240.0, 256.0), taper=0.70,
              throat=288.0, grip_rings=((318.0, 3),), blade_color=K.JADE, bottom=494.0)
PADDLE_RUN, PADDLE_REACH, PADDLE_FLARE = 70.0, 4.0, 10.0

# ---- the belt hand ----------------------------------------------------------------------------------
REST_AT, REST_ANGLE = (250.0, 424.0), 40.0
REST_RUN, REST_REACH, REST_FLARE, REST_ELBOW = 90.0, 4.0, 8.0, -14.0

PUFF_SPRAYS_L = [B.spl([(240, 334), (206, 352), (190, 386), (192, 424)]),
                 B.spl([(254, 352), (226, 374), (216, 410)])]
PUFF_SPRAYS_R = [B.spl([(528, 328), (562, 342), (580, 376), (582, 424)]),
                 B.spl([(516, 346), (546, 366), (556, 400)])]

PUFF_L = B.region([(284, 318), (250, 321), (228, 322), (196, 338), (176, 372), (173, 412), (184, 440)],
                  ("L", [(184, 440), (262, BELT_Y + 12)]), [(262, BELT_Y + 12), (262, 400), (262, 340), (284, 318)])
PUFF_R = B.region([(496, 316), (530, 317), (552, 318), (584, 342), (598, 384), (599, 430), (590, 456)],
                  ("L", [(590, 456), (506, BELT_Y + 12)]), [(506, BELT_Y + 12), (506, 400), (506, 340), (496, 316)])


def sleeve_bell(hand, *, run, reach=0.0, cuff=3.0, flare=10.0, curl=-5.0, elbow=0.0):
    """A bell that opens from the cuff mouth (just behind the wrist) toward the elbow, ``run`` px along the
    forearm; its mouth edge bulges toward the hand and its far end ``elbow`` px outward (0: straight)."""
    u = hand.wrist_dir
    w = K.P(hand.wrist) - u * reach
    n = np.array([u[1], -u[0]])
    half = hand.wrist_w / 2
    base = w + u * run
    shape = K.R(K.Path(w + n * (half + cuff)).sag(w - n * (half + cuff), curl)
                .sag(base - n * (half + cuff + flare), 1.5).sag(base + n * (half + cuff + flare), elbow)
                .sag(w + n * (half + cuff), 1.5).close().d)
    return shape.buffer(-1.6).buffer(1.6)


def fillet(shape, r=10.0):
    return shape.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)


def cuff_band(hand, sleeve, *, reach, offset=9.0, curl=-5.0, cuff=3.0):
    """A turn-back line parallel to the cuff mouth, inside the sleeve."""
    u = hand.wrist_dir
    n = np.array([u[1], -u[0]])
    mouth = K.P(hand.wrist) - u * reach + u * offset
    half = hand.wrist_w / 2 + cuff + 8.0
    path = K.Path(mouth + n * half).sag(mouth - n * half, curl)
    pts = np.asarray(C.sample_d(path.d, 0.3)[0][0])
    edge = LineString(pts).intersection(sleeve.buffer(-0.3))
    out = C.Frag()
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 8.0:
            out += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def spray_along(hand, a, b, off=0.0):
    """A comb-spray guide: ``a``..``b`` px out from the wrist along the forearm, ``off`` px to its left."""
    u = hand.wrist_dir
    n = np.array([u[1], -u[0]])
    w = K.P(hand.wrist)
    return K.Path(w + u * a + n * off).line(w + u * b + n * off).d


def sleeve_part(hand, sleeve, keep, *, reach, sprays=(), hide=None):
    """The jade sleeve over the puff behind it: its two long folds (inside ``keep``, the garment it lies on),
    clear of the hand, the turn-back line behind the cuff mouth, and comb sprays down the forearm."""
    edge = K.R(sleeve).boundary.intersection(keep.buffer(-1.0)).difference(
        K.U(hand.shape.buffer(1.2), hide.buffer(3.0)) if hide is not None else hand.shape.buffer(1.2))
    lines = C.Frag()
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 6.0:
            lines += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    lines += cuff_band(hand, sleeve, reach=reach)
    lines += B.comb_ink(sleeve, sprays, avoid=hand.shape.buffer(4.0), pitch=8.0, tick=10.0, angle=52.0)
    return K.Part(sleeve, K.fill(sleeve, K.JADE), lines, {})


def sleeved_hand(hand, sleeve):
    """The hand beyond its cuff mouth; the sleeve's edge is the hand's contour."""
    region = K._biggest(hand.shape.difference(sleeve))
    inner = hand.hand.meta.get("inner", C.Frag())
    return K.Part(region, C.Frag(), K.outline(region) + K.clip_in(inner, region.buffer(-5.0)),
                  {**hand.hand.meta, "hand_region": region})


def held_attribute(attribute, hand_cuff):
    """One outline at the hand and the held object, without a halo."""
    shape = K.U(attribute.shape, hand_cuff.shape).buffer(1.6).buffer(-1.6).simplify(0.02)
    fills = K.clip_in(attribute.fills, attribute.shape.difference(
        hand_cuff.shape.buffer(-K.MEDIUM / 2))) + hand_cuff.fills
    return K.Part(
        shape, fills,
        K.clip_out(attribute.lines.select(lambda m: m.role != "outline"), hand_cuff.shape, eps=0.2, trap=0.0)
        + hand_cuff.lines.select(lambda m: m.role != "outline")
        + K.clip_in(K.outline(hand_cuff.shape, role="grip-edge"), attribute.shape.buffer(2.0))
        + K.outline(shape, role="contour"), hand_cuff.meta)


def with_lines(part, extra):
    return K.Part(part.shape, part.fills, part.lines + extra, part.meta)


def figure():
    sc = K.Scene()
    fc = K.face(HEAD, "3/4-left", age="young", **FACE_KW)
    size = K.hand_size(fc) * HAND_SCALE

    torso = B.region(*TORSO)
    vee = B.region(E_L, E_R[::-1], ("L", [(410, 300), (334, 302)]))
    red = G.jerkin_whole(vee)
    # ---- hands, sleeves, paddle ----------------------------------------------------------------------
    paddle = PD.paddle3(PADDLE_X, **PADDLE)
    paddle = with_lines(paddle, B.comb_ink(
        paddle.shape, [B.spl([(PADDLE_X - 13.0, 128.0), (PADDLE_X - 13.0, 188.0), (PADDLE_X - 13.0, 238.0)])],
        avoid=K.U(paddle.lines.shape(), K.box(PADDLE_X - 2.0, 0.0, 700.0, 520.0)), pitch=9.0, tick=9.0, angle=52.0))
    hP = K.hand5(GRIP_P, -90.0, "wrap", size=size, hand="L", view="back", grip_w=22.0)
    bellP = sleeve_bell(hP, run=PADDLE_RUN, reach=PADDLE_REACH, flare=PADDLE_FLARE)
    sleeveR = bellP.intersection(K.U(PUFF_R, torso)).difference(red)
    handP = sleeved_hand(hP, sleeveR)
    held = held_attribute(paddle, handP)

    hB = K.hand5(REST_AT, REST_ANGLE, "rest", size=size, hand="R", view="back", curl=6.0, spread=3.0)
    bellB = sleeve_bell(hB, run=REST_RUN, reach=REST_REACH, flare=REST_FLARE, elbow=REST_ELBOW)
    sleeveL = bellB.intersection(K.U(PUFF_L, torso)).difference(red)
    handB = sleeved_hand(hB, sleeveL)

    husk = J.pecan_husk(BUCKLE, style="D", s=1.25)
    front = K.U(sleeveL, handB.shape, sleeveR, held.shape, husk.shape)
    belt = B.reed_belt(K.box(262, 0, 536, 1050), y=BELT_Y, h=24.0, sag=4.0, x0=220.0, x1=560.0, front=358.0,
                       rise=BELT_RISE, node_every=BELT_NODES[0], node_phase=BELT_NODES[1],
                       skip=K.box(husk.shape.bounds[0] - 12.0, 400.0, husk.shape.bounds[2] + 10.0, 490.0),
                       avoid=front, cover=front, min_run=20.0)

    body = K.U(PUFF_L, PUFF_R, torso).buffer(0.01).buffer(-0.01)
    body_front = K.U(red, G.rot(red), sleeveL, sleeveR, handB.shape, held.shape)
    sc.add("body", K.fill(body, K.JADE) + K.outline(body) + B.comb_ink(
        body, PUFF_SPRAYS_L + PUFF_SPRAYS_R, avoid=body_front, pitch=8.0, tick=10.0, angle=52.0), body)
    blockers = K.U(front, G.rot(front), belt.shape, G.rot(belt.shape))
    leaves, nuts, hulls = G.trellis_sprigs(red.difference(blockers.buffer(5.0)), **SPRIG)
    net = G.trellis_lines(K.R(red).buffer(-5.0).difference(K.U(blockers.buffer(4.0), hulls.buffer(0.6))), *TRELLIS)
    red_d = C.knockout(K.D(red), leaves, net)
    sc.add("jerkin", K.fill(red_d, K.RED) + K.outline(red) + nuts, red)
    sc.part("belt", belt)

    # ---- head --------------------------------------------------------------------------------------------
    sc.part("hair", H.pageboy(outer=[(446, 170), (472, 192), (480, 228), (478, 266), (470, 298), (454, 318)],
                              inner=[(420, 320), (396, 300), (392, 262), (398, 226), (412, 190), (430, 172),
                                     (446, 170)], n=4, ends=HAIR_ENDS, curl_deg=120.0))
    sc.part("lockF", H.far_lock(outer=[(334.0, 181.0), (315.0, 200.0), (310.0, 226.0), (318.0, 250.0),
                                       (340.0, 266.0)],
                                inner=[(364.0, 268.0), (358.0, 232.0), (354.0, 190.0), (334.0, 181.0)],
                                n=2, first=8.5, ends=[70.0, 56.0], curl_deg=110.0))
    sc.part("neck", K.neck(fc, bottom=312.0, width=33.0))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    sc.part("collar", J.standing_collar(**COLLAR))
    sc.part("ear", J.ear(fc))
    cap = J.bonnet(**CAP)
    sc.part("cap", with_lines(cap, B.comb_ink(
        cap.shape, [B.spl([(356, 152), (390, 144), (426, 144), (452, 152)]), B.spl([(366, 136), (398, 131), (428, 133)])],
        avoid=K.U(cap.lines.shape(), K.box(440.0, 120.0, 480.0, 190.0)), pitch=9.0, tick=9.0, angle=52.0)))
    vane, quill = H.heron_plume3(PLUME, **PLUME_KW)
    sc.part("plume", vane)
    sc.part("quill", quill)
    sc.part("brooch", J.club_brooch(BROOCH, **BROOCH_KW))
    sc.part("clasp", K.lion_clasp(CLASP, 40.0))
    sc.part("buckle", husk)

    # ---- arms ---------------------------------------------------------------------------------------------
    sc.part("sleeveL", sleeve_part(hB, sleeveL, K.U(PUFF_L, torso), reach=REST_REACH,
                                   sprays=[spray_along(hB, 26.0, 84.0, 0.0)]))
    sc.part("sleeveR", sleeve_part(hP, sleeveR, K.U(PUFF_R, torso), reach=PADDLE_REACH,
                                   sprays=[spray_along(hP, 24.0, 66.0, 0.0), spray_along(hP, 26.0, 62.0, 18.0), spray_along(hP, 26.0, 62.0, -18.0)],
                                   hide=paddle.shape))
    sc.part("handL", handB)
    sc.part("paddle+hand", held)
    return sc, fc


def build():
    sc, _ = figure()
    return sc.layers()
