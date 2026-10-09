"""art/_js_hands.py — J♠'s cloak-sleeve hands: the bell sleeve that ends in a hand5 wrist, its turn-back
band, edge folds and grain, and the merge of hand + sleeve + held attribute into ONE outline.

Court-private (each court shapes its own sleeves; there is no shared arm helper in the kit).
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck.motifs import core as C


def _n(hand):
    u = hand.wrist_dir
    return np.array([u[1], -u[0]])


def sleeve_end(hand, *, run, zone, reach=0.0, cuff=3.0, flare=12.0, curl=-5.0, elbow_r=9.0, grow=1.0):
    """A bell that opens from the cuff mouth toward the elbow (``run`` px along the forearm axis), cut
    to ``zone`` grown by ``grow`` (the garment it grows from: the garment's outline is the sleeve's far
    end). A sleeve that is united into its garment's silhouette needs ``grow=0``, or the garment's
    contour steps out by ``grow`` along the sleeve's root."""
    u = hand.wrist_dir
    w = K.P(hand.wrist) - u * reach
    n = _n(hand)
    half = hand.wrist_w / 2
    base = w + u * run
    shape = K.R(K.Path(w + n * (half + cuff)).sag(w - n * (half + cuff), curl)
                .sag(base - n * (half + cuff + flare), 1.5).line(base + n * (half + cuff + flare))
                .sag(w + n * (half + cuff), 1.5).close().d)
    shape = shape.buffer(-1.6).buffer(1.6)
    elbow = shape.buffer(-elbow_r).buffer(elbow_r)
    mouth = shape.intersection(Polygon([w - n * 60 - u * 4, w + n * 60 - u * 4,
                                        w + n * 60 + u * 16, w - n * 60 + u * 16]))
    return K.U(elbow, mouth).intersection(zone.buffer(grow) if grow else zone)


def _arc(hand, reach, offset, half, curl):
    u = hand.wrist_dir
    n = _n(hand)
    m = K.P(hand.wrist) - u * reach + u * offset
    path = K.Path(m + n * half).sag(m - n * half, curl)
    return np.asarray(K.C.sample_d(path.d, 0.3)[0][0])


def cuff_band(hand, sleeve, *, reach, width=11.0, curl=-5.0, cuff=3.0):
    """The turn-back band at the sleeve's mouth: (region, MEDIUM back line)."""
    half = hand.wrist_w / 2 + cuff + 8.0
    front = _arc(hand, reach, -5.0, half, curl)
    back = _arc(hand, reach, width, half, curl)
    band = Polygon(np.vstack([front, back[::-1]])).buffer(0).intersection(sleeve)
    band = band.buffer(-0.8).buffer(0.8)
    edge = LineString(back).intersection(sleeve.buffer(0.8))
    line = C.Frag()
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 8.0:
            line += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return band, line


def sleeve_edges(sleeve, keep):
    """The sleeve's long folds: its edges inside the garment (the garment outline carries the rest)."""
    out = C.Frag()
    edge = K.R(sleeve).boundary.intersection(keep)
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 6.0:
            out += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_grain(hand, sleeve, avoid, *, inset=6.5):
    """FINE hatch along the forearm axis, so the sleeve grain differs from the garment's."""
    u = hand.wrist_dir
    ang = float(np.degrees(np.arctan2(u[1], u[0])))
    zone = sleeve.buffer(-inset).difference(avoid)
    return drop_short(K.hatch_in(zone, angle=ang, origin=tuple(hand.wrist)), 10.0)


def drop_short(f, min_len):
    from art import _js_util as U
    return U.drop_short(f, min_len)


def sleeved_hand(hand, sleeve):
    """The hand beyond its cuff mouth; the sleeve's edge is the hand's contour."""
    region = K._biggest(hand.shape.difference(sleeve))
    inner = hand.hand.meta.get("inner", C.Frag())
    return K.Part(region, C.Frag(), K.outline(region) + K.clip_in(inner, region.buffer(-5.0)),
                  {**hand.hand.meta, "hand_region": region})


def held_attribute(attribute, hand_cuff, *, keep=lambda m: m.role != "outline"):
    """One outline at the hand and the held object, without a halo."""
    joined = K.U(attribute.shape, hand_cuff.shape)
    fillet = joined.buffer(1.6).buffer(-1.6).intersection(hand_cuff.shape.buffer(8.0))
    shape = K.U(joined, fillet).simplify(0.02)
    fills = K.clip_in(attribute.fills, attribute.shape.difference(
        hand_cuff.shape.buffer(-K.MEDIUM / 2))) + hand_cuff.fills
    return K.Part(
        shape, fills,
        K.clip_out(attribute.lines.select(keep), hand_cuff.shape, eps=0.2, trap=0.0)
        + hand_cuff.lines.select(lambda m: m.role != "outline")
        + K.clip_in(K.outline(hand_cuff.shape, role="grip-edge"), attribute.shape.buffer(2.0))
        + K.outline(shape, role="contour"), hand_cuff.meta)
