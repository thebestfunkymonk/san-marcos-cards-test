"""art/BACK.py: the card back, "The Source" (brief §H.19).

One Spring Jade flood (inset 37.5, r 18) with every line reversed out
geometrically: the frame (D2) and the emblem (C2 only) are built as line art
and subtracted from the flood, so the jade layer is a single FILL path whose
holes are the paper lines.
"""
from __future__ import annotations

from deck import tokens as T
from deck.motifs import core as C
from inkkit import geom as G

from art import _back_frame as BF
from art import _back_emblem as BE


def parts() -> dict:
    """{name: Frag} for every motif on the back (frame + emblem)."""
    p = dict(BF.frame())
    p.update(BE.emblem())
    return p


def holes_d(frags) -> str:
    """Exact union of every mark as FILL d.

    Unions mark by mark with pathops ops (``G.union``) rather than
    ``Frag.outline()``: the single WINDING simplify there mis-fills some
    closed contours (e.g. the darter's body once its fin membrane is added
    at rot 210), which would paint a whole fish solid paper."""
    return G.union(*[G.from_skia(m.skia()) for f in frags for m in f.marks if m.d])


def build():
    ko = G.difference(BF.flood_d(), holes_d(parts().values()))
    return {"jade": [f'<path d="{ko}" fill="{T.JADE}" fill-rule="nonzero"/>']}
