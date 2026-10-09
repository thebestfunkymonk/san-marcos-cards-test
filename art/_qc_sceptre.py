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

from art import _qc_parts as Q

P, R, U = K.P, K.R, K.U
FINE, MEDIUM, HAIR = K.FINE, K.MEDIUM, K.HAIR_W
GOLD = K.GOLD
TIP_SINK = 8.0    # how far a tip floret's point reaches back up a 6 px arm: there it is the arm's width


def _u(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def _pts(d, step=0.25):
    return np.asarray(C.sample_d(d, step)[0][0], float)


def rice_sceptre(x=545.0, *, bottom=560.0, hw=8.5, knop_y=292.0, knop_hw=15.0, knop_h=12.0,
                 nodes=(352.0, 488.0), node_hw=13.0, node_h=9.0, striae=True,
                 rachis_hw=3.2, rachis_top=128.0, terminal=(26.0, 8.6, 15.0),
                 female=(), arms=(), color=GOLD, knop_w=None, knop_ink=None):
    """The sceptre (see the module docstring).

    ``female`` = (y on the rachis, side ±1, pedicel length, pedicel° off
    upright, L, W, spikelet axis° off upright, awn) — side −1 = viewer's left.
    ``arms`` = (y at the rachis, start heading° above horizontal, [(len, turn°)…]
    arc pieces (turn + = bending down/outward), width, florets, tip floret
    (L, W) or None), florets = [(fraction along the arm, pedicel, L, W, hang°
    off straight-down, outward +)] — drawn for both sides.

    ``knop_w``: the knop's outline weight (default MEDIUM). ``knop_ink``: the depth (px) of an
    Aquifer inner band laid over the knop's LOWER half. A knop that straddles the silhouette line
    has a CONTOUR ring round its upper half (3.1 px deep inside it) and its MEDIUM outline below
    (1.55 px deep): where the thick ring turns into the thin outline, the ring's round join bit
    1.3 px into the gold at both lower corners, and the culm's line caps stood as nubs in the
    knop's base line. A 3.1 px band below makes the visible gold one clean inset (the band lies
    inside the knop's own edge: no ears outside it).

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
    # the rachis's outline runs on into the spikelet's flanks: the spikelet's own tip inside the
    # rachis would stand as an ink wedge in the rachis's 2.9 px gold core, between two capped ends
    lines += K.clip_out(C.stroke(Q.ring_mid(ves), MEDIUM, style="point", role="spikelet"),
                        K.box(x - rachis_hw, rachis_top, x + rachis_hw, knop_y), eps=0.0, trap=0.0)
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
        # the outline opens at the base, under the pedicel's round cap: the pedicel meets the axis
        # at ~50°, and the base's miter spike stood out past it as an ink spur
        lines += K.clip_out(C.stroke(Q.ring_mid(ves), MEDIUM, style="point", role="spikelet"),
                            R(K.circle(tuple(q - u * 1.0), 0.4)), eps=0.0, trap=0.0)
        # (from the rachis's outline centre line: its round cap stays inside that outline — started
        # 1.5 px further in, it stood as a round nub in the rachis's 2.9 px gold core)
        peds.append((p0 + P(sd * 0.3, 0), q - u * 1.0))
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
            if tipf:
                # a flat end, with the tip floret sunk to where it is as wide as the arm: a round
                # cap stood out past the floret's narrow top as a knob on one side
                rg = U(LineString(pts).buffer(aw_ / 2, cap_style=2, quad_segs=12),
                       R(K.circle(tuple(pts[0]), aw_ / 2)))
            else:
                rg = LineString(pts).buffer(aw_ / 2, cap_style=1, quad_segs=12)
            for (fr, ped, L, W, hang) in florets:
                b = cv.at_s(cv.length * fr)
                u = _u(90.0 - sd * hang)
                b0 = b + u * (aw_ / 2 - 0.5)
                q = b0 + u * ped
                ves = C.vesica_d(q - u * 1.0, q + u * L, W)
                els.append(R(ves))
                lines += C.stroke(Q.ring_mid(ves), MEDIUM, style="point", role="floret")
                if ped > 0.5:
                    # (from the arm's outline centre line — a nub in the arm's gold core otherwise)
                    peds.append((b + u * (aw_ / 2 + 0.3), q + u * 1.0))
            if tipf:
                L, W = tipf
                e = pts[-1]
                tg = cv.tangent_s(cv.length)
                ang = math.degrees(math.atan2(tg[1], tg[0]))
                u = _u(ang)
                # one outline round arm + tip floret, filleted 6 px: two outlines meeting at the arm's
                # end, each with its own round cap, stood as knobs on both shoulders of the joint, and
                # unfilleted the arm's edges met the floret's flanks at a notch
                rg = U(rg, R(C.vesica_d(e - u * TIP_SINK, e + u * L, W))).buffer(
                    6.0, quad_segs=16, join_style=2, mitre_limit=10.0).buffer(-6.0, quad_segs=16)
            arm_regs.append(rg)
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
    bl += K.outline(knop) if knop_w is None else C.stroke(K.D(knop), knop_w, role="outline")
    knop_band = C.Frag()
    if knop_ink:
        # (a U open at the top — it joins the silhouette ring's inner edge there; no hole to flood)
        band = knop.difference(knop.buffer(-knop_ink, quad_segs=16)).intersection(
            K.box(x - 100.0, knop_y - 1.0, x + 100.0, knop_y + 50.0))
        # emitted AFTER every stroke: a fill between the outlines splits the one MEDIUM <path> the
        # outlines, florets and pedicels share, and heal then measured the pedicels against the arms'
        # outlines as separate pieces (1.3 px apart) and cut the arms' lower outlines away
        knop_band = K.fill(band, K.INK, role="outline")
    for cd in collars:
        bl += K.outline(cd)
    if arms_reg is not None:
        # the arms' outlines end 0.3 px short of the rachis's edge: their round caps stay inside its
        # outline (cut 0.5 px inside it, they stood as round nubs in its 2.9 px gold core). (One outline
        # round rachis + arms — the gold running on into the arms — splits the arms' two edges, only
        # 2.9 px apart, into an upper and a lower piece, and heal cut one of them away.)
        # (likewise 0.3 px short of the florets they carry: cut 0.5 px inside a floret, the caps stood
        # as two round nubs in its gold where the arm's end enters the tip floret)
        # (mitred: the tip florets' points are in this ring)
        bl += K.clip_out(C.stroke(K.D(arms_reg), MEDIUM, style="point", role="outline"),
                         U(knop, rachis, stone).buffer(0.3, quad_segs=8), eps=0.0, trap=0.0)
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
    return K.Part(shape, fills, bl + lines + ped_l + awns + knop_band,
                  {"culm": U(culm, knop, *collars), "head": head, "rachis": rachis, "top": top,
                   "stone": stone})
