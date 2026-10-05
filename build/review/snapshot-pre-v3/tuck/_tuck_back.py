"""TUCK-BACK (brief §H.20 "Back"): the card back redrawn in gold foil on board.

Derived at BUILD time from ``art/BACK.py`` (never copied), so any change to
the card back flows into the tuck:

* every mark the card back reverses out of its jade flood (frame + emblem,
  ``BACK.parts()``) becomes a FOIL line on the Deep Hole board — the same
  geometry, the same legal widths, laid 1 : 1 (never scaled), centred on the
  panel (card (375, 525) -> panel (384.5, 534.5));
* the panel is 19 px wider and taller than the card; with no white border on
  a tuck the art sits 59 px in from the folds.  The box's own outer rule
  (RULE at 34 + FINE companion at 42, the same rules as the front, so both
  big faces share one border) closes it, and the extra SIDE width becomes
  vertical REED LADDERS (§G.19): rungs every 26 px spanning the channel
  between the companion and the card art's outer rule, a node ellipse on
  every 4th rung counted from mid-height, stopping clear of the corner
  roundels.  The top and bottom channels stay plain board;
* emboss plate: the Source Rosette (§G.1, R 130) embossed as a sculpted disc
  (level 2) — the ground stays flat.

One foil only; no type on the back (as the card back).
"""
from __future__ import annotations

import shapely
from shapely.geometry import box

from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import geometric as M
from inkkit import geom as G

from tuck import _tuck_common as K

PW, PH, PCX, PCY = K.PW, K.PH, K.PCX, K.PCY
FINE, RULE = K.FINE, K.RULE
GAP = K.GAP
DX, DY = PCX - T.CX, PCY - T.CY          # 9.5, 9.5: card centre -> panel centre

OUTER = K.FRAME_OUTER
COMPANION = K.FRAME_COMPANION
LADDER = dict(pitch=26.0, node_every=4, node_ry=4.5)


def card_parts() -> dict:
    """{name: Frag} of the card back (art/BACK.py), recoloured to foil and
    moved onto the panel (rigid translation only)."""
    from art import BACK
    return {k: f.recolor(K.FOIL).translate(DX, DY) for k, f in BACK.parts().items()}


def _card_outer():
    """Centreline inset of the card art's outer RULE on the panel."""
    from art import _back_frame as BF
    return BF.OUTER + DX


def border(art_shape) -> C.Frag:
    """The box's outer RULE + FINE companion (as on the front), unbroken."""
    f = C.Frag()
    for inset, w in ((OUTER, RULE), (COMPANION, FINE)):
        f += C.stroke(K.rect_lines(inset, inset, PW - inset, PH - inset), w, style="rule", color=K.FOIL,
                      role="rule")
    return f


def side_ladders(art_shape) -> C.Frag:
    """Vertical reed ladders in the side channels between the companion
    (x 42) and the card art's outer rule (x 59), symmetric about mid-height,
    rungs every 26 px, a node on every 4th rung; stops 4.2 px clear of
    anything of the card art (the corner roundels)."""
    x0 = COMPANION + FINE / 2
    x1 = _card_outer() - RULE / 2
    xc = (x0 + x1) / 2
    hw = (x1 - x0) / 2
    f = C.Frag()
    k = 0
    while True:
        y = PCY + LADDER["pitch"] * k
        if k % LADDER["node_every"] == 0:
            # the node: an ellipse across the ladder, tangent to both rails (§G.19), in place of the rung
            g = C.stroke(G.ellipse_d(xc, y, hw, LADDER["node_ry"], 0.0), FINE, color=K.FOIL, role="node")
        else:
            g = C.stroke(C.polyline_d([(x0, y), (x1, y)]), FINE, style="rule", color=K.FOIL, role="rung")
        if g.shape().distance(art_shape) < GAP:
            break
        f += g
        k += 1
    f = f + f.mirror_y(PCY)
    # drop the duplicate mid-height node (mirror of k = 0 lies on itself)
    f = _dedupe(f)
    return f + f.mirror_x(PCX)


def _dedupe(f: C.Frag) -> C.Frag:
    seen, out = set(), []
    for m in f.marks:
        key = (m.kind, m.d, m.w)
        if key in seen:
            continue
        seen.add(key)
        out.append(m)
    return C.Frag(out, f.meta)


def build():
    """-> dict(foil=Frag, emboss=[(d, level)], parts={...})."""
    parts = card_parts()
    art = C.Frag()
    for f in parts.values():
        art += f
    # the card art's outer silhouette near the sides (roundels, outer rule) for the ladder stop
    art_shape = art.shape()
    corner_zone = shapely.union_all([box(0, 0, PW, 125), box(0, PH - 125, PW, PH)])
    art_corner = art_shape.intersection(corner_zone)
    lad = side_ladders(art_corner)
    bord = border(art_shape)
    # the thumb notch (the lid's flap tucks in behind the back): everything keeps NOTCH_CLEAR off the
    # cut; the rules end ON a FINE arch concentric with it, the rest breaks 4.2 px clear of the arch
    r_a = K.NOTCH_R + K.NOTCH_CLEAR + FINE / 2
    disc = shapely.Point(PCX, 0.0).buffer(r_a, quad_segs=64)
    rules_ = C.Frag([m for m in (bord + parts["rules"]).marks])
    others = C.Frag([m for f in [lad] + [v for k, v in parts.items() if k != "rules"] for m in f.marks])
    rules_ = C.occlude(rules_, disc.buffer(-0.5))
    # the top band's fault-step plinth stood where the notch now is: it goes with it
    others = C.Frag([m for m in others.marks
                     if not (m.role in ("plinth", "bedding") and C.Frag([m]).bbox()[1] < PCY)], others.meta)
    others = K.drop_short(C.cut(others, disc.buffer(FINE / 2), GAP), 8.0)
    arch = C.clip(C.stroke(C.circle_d(PCX, 0.0, r_a), FINE, color=K.FOIL, role="rule"),
                  shapely.box(0, OUTER - 0.5, PW, PH))
    art = others + arch
    bord, lad = rules_, C.Frag()
    # the foil plate is the EXACT union of every mark (as the card back knocks out the same union from
    # its flood), so touching marks fuse into one foil piece exactly as they fuse into one paper hole
    from art import BACK
    foil = K.plug(C.fill(BACK.holes_d([bord, lad, art]), color=K.FOIL, role="art"))
    from art import _back_geo as BG
    ros = shapely.Point(PCX, PCY).buffer(BG.ROSETTE_R + FINE / 2 + 1.0, quad_segs=64)
    emboss = [(G.from_shape(ros), 2)]
    return dict(foil=foil, emboss=emboss, parts=dict(card=parts, ladders=lad, border=bord))


def svg(res=None):
    res = res or build()
    notes = ["HEADWATERS tuck BACK panel, 769 x 1069 px @300 ppi, y down.",
             "Derived at build time from art/BACK.py: the card back's reversed-out lines as ONE gold foil",
             "(flat Lion Gold #B08D57) on Deep Hole board; extra side width = reed ladders; the Source",
             "Rosette blind-embossed (emboss plate, non-printing tooling colour). No type."]
    return K.svg_doc(PW, PH, emboss=res["emboss"], foil=K.foil_svg(res["foil"]), title="HEADWATERS tuck back",
                     notes=notes)
