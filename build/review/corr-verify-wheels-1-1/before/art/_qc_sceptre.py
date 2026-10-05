"""art/_qc_sceptre.py — Q♣ · the sceptre wrought as a flowering wild-rice stalk (§H.8, §G.5).

Botanically ordered along its own axis, bottom to top (san-marcos.md §2.1:
"drooping male florets below and stiffly erect female spikelets above"):

    culm      the gold stalk from below the band up to a reed-node knop, with
              raised node collars (a grass culm) and a FINE striation between
              them;
    knop      the node the panicle springs from;
    male      two arching branches (one each side) spreading from the knop and
              curving down; the male florets HANG from them on short pedicels
              (§G.5 "the same vesicas hung at ±150°"), the branch tip itself
              ending in a hanging floret: the fountain / chandelier silhouette
              no wheat ear has;
    female    above them, the erect female spikelets: slender 3 : 1 vesicas on
              visible pedicels, alternating up a thin rachis, each standing
              nearly upright with one HAIRLINE awn; a terminal spikelet.

Everything is a gold solid with an Aquifer MEDIUM contour (legal where it
crosses red), nothing scaled, every width legal.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM
from inkkit import geom as G

import _qc_parts as Q

P, R, U = K.P, K.R, K.U
FINE, MEDIUM, HAIR = K.FINE, K.MEDIUM, K.HAIR_W
GOLD = K.GOLD


def _u(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def _pts(d, step=0.25):
    return np.asarray(C.sample_d(d, step)[0][0], float)


def rice_sceptre(x=545.0, *, bottom=560.0, hw=8.5, knop_y=292.0, knop_hw=15.0, knop_h=12.0,
                 nodes=(352.0, 488.0), node_hw=13.0, node_h=9.0, striae=True,
                 rachis_hw=3.2, rachis_top=128.0, terminal=(26.0, 8.6, 15.0),
                 female=(), arms=(), color=GOLD):
    """The sceptre (see the module docstring).

    ``female`` = (y on the rachis, side ±1, pedicel length, pedicel° off
    upright, L, W, spikelet axis° off upright, awn) — side −1 = viewer's left.
    ``arms`` = (y at the rachis, start heading° above horizontal, [(len, turn°)…]
    arc pieces (turn + = bending down/outward), width, florets, tip floret
    (L, W) or None), florets = [(fraction along the arm, pedicel, L, W, hang°
    off straight-down, outward +)] — drawn for both sides.

    → Part(shape, fills, lines, meta: culm (silhouette piece), head, rachis,
    top (highest point incl. the awn))."""
    culm = K.box(x - hw, knop_y, x + hw, bottom)
    knop = R(K.rrect(x - knop_hw, knop_y - knop_h / 2, x + knop_hw, knop_y + knop_h / 2, knop_h / 2 - 0.5))
    collars = [R(K.rrect(x - node_hw, yy - node_h / 2, x + node_hw, yy + node_h / 2, node_h / 2 - 0.5))
               for yy in nodes]
    rachis = K.box(x - rachis_hw, rachis_top, x + rachis_hw, knop_y)
    els, lines, awns = [], C.Frag(), C.Frag()

    # terminal spikelet
    L, W, aw = terminal
    p1, p2 = P(x, rachis_top + 2.0), P(x, rachis_top + 2.0 - L)
    ves = C.vesica_d(p1, p2, W)
    els.append(R(ves))
    lines += C.stroke(Q.ring_mid(ves), MEDIUM, style="point", role="spikelet")
    top = p2[1]
    if aw:
        awns += C.stroke(C.polyline_d([p2, p2 + P(0, -aw)]), HAIR, role="awn")
        top = p2[1] - aw

    # erect female spikelets on pedicels
    peds = []
    for (ry, sd, ped, ped_deg, L, W, deg, aw) in female:
        p0 = P(x + sd * rachis_hw, ry)
        q = p0 + _u(-90.0 + sd * ped_deg) * ped
        u = _u(-90.0 + sd * deg)
        tip = q + u * L
        ves = C.vesica_d(q - u * 1.0, tip, W)
        els.append(R(ves))
        lines += C.stroke(Q.ring_mid(ves), MEDIUM, style="point", role="spikelet")
        peds.append((p0 - P(sd * 1.5, 0), q + u * 1.0))
        if aw:
            awns += C.stroke(C.polyline_d([tip, tip + u * aw]), HAIR, role="awn")

    # arching male branches with hanging florets
    arm_regs = []
    for (ay, h0, pieces, aw_, florets, tipf) in arms:
        for sd in (-1, 1):
            heading = -h0 if sd > 0 else 180.0 + h0
            turns = [(Lp, tr * sd) for (Lp, tr) in pieces]
            _, pts, t = FM.arc_path(x + sd * (rachis_hw - 1.0), ay, heading, turns)
            pts = np.asarray(pts, float)
            cv = G.Curve(pts)
            rg = LineString(pts).buffer(aw_ / 2, cap_style=1, quad_segs=12)
            arm_regs.append(rg)
            for (fr, ped, L, W, hang) in florets:
                b = cv.at_s(cv.length * fr)
                u = _u(90.0 - sd * hang)
                b0 = b + u * (aw_ / 2 - 0.5)
                q = b0 + u * ped
                ves = C.vesica_d(q - u * 1.0, q + u * L, W)
                els.append(R(ves))
                lines += C.stroke(ves, MEDIUM, style="point", role="floret")
                if ped > 0.5:
                    peds.append((b0 - u * 1.0, q + u * 1.0))
            if tipf:
                L, W = tipf
                e = pts[-1]
                tg = cv.tangent_s(cv.length)
                ang = math.degrees(math.atan2(tg[1], tg[0]))
                u = _u(ang)
                ves = C.vesica_d(e - u * (aw_ / 2 + 1.0), e + u * L, W)
                els.append(R(ves))
                lines += C.stroke(ves, MEDIUM, style="point", role="floret")
    arms_reg = U(*arm_regs) if arm_regs else None
    stone = U(*els)
    body = U(culm, rachis, knop, *collars)
    head = U(stone, arms_reg) if arms_reg is not None else stone
    ped_l = C.Frag()
    for a_, b_ in peds:
        ped_l += K.seg(a_, b_, MEDIUM, role="pedicel")
    ped_l = K.clip_out(ped_l, stone, eps=-0.5, trap=0.0)
    fills = K.fill(body, color) + K.fill(head, color)
    bl = K.clip_out(K.outline(culm), U(knop, *collars), eps=-0.5, trap=0.0)
    bl += K.clip_out(K.outline(rachis), U(knop, stone), eps=-0.5, trap=0.0)
    bl += K.outline(knop)
    for cd in collars:
        bl += K.outline(cd)
    if arms_reg is not None:
        bl += K.clip_out(K.outline(arms_reg), U(knop, stone, rachis), eps=-0.5, trap=0.0)
    if striae:
        ys = [knop_y] + list(nodes) + [bottom]
        st = C.Frag()
        for a_, b_ in zip(ys[:-1], ys[1:]):
            y0 = a_ + (knop_h if a_ == knop_y else node_h) / 2 + 8.0
            y1 = b_ - node_h / 2 - 8.0
            if y1 - y0 > 12.0:
                st += K.seg(P(x, y0), P(x, y1), FINE, role="stria")
        bl += st
    shape = U(body, head)
    return K.Part(shape, fills, bl + lines + ped_l + awns,
                  {"culm": U(culm, knop, *collars), "head": head, "rachis": rachis, "top": top,
                   "stone": stone})
