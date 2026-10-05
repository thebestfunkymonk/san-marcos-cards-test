"""art/BACK.py: the card back, "The Source" (brief §H.19).

One Spring Jade flood (inset 37.5, r 18) with every line reversed out
geometrically: the frame (D2) and the emblem (C2 only) are built as line art
and subtracted from the flood, so the jade layer is a single FILL path whose
holes are the paper lines.
"""
from __future__ import annotations

import shapely

from deck import tokens as T
from deck.motifs import core as C
from inkkit import geom as G

from art import _back_frame as BF
from art import _back_emblem as BE


def parts() -> dict:
    """{name: Frag} for every motif on the back (frame + emblem)."""
    return _parts()[0]


def _parts():
    em, occ = BE.emblem(with_shape=True)
    p = dict(BF.frame(emblem_shape=occ))
    p.update(em)
    return p, occ


def holes_d(frags, occupied=None) -> str:
    """Exact union of every mark as FILL d (polygons flattened at 0.02 px).

    The union is the GEOS union of each Frag's ``shape()`` -- itself the
    union of every mark's own resolved outline -- never one WINDING
    simplify of all the marks together, which mis-fills some closed
    contours (e.g. the darter's body with its fin membrane at rot 210) and
    would paint a whole fish solid paper.  ``occupied``: an already-known
    union to include (the emblem's)."""
    shapes = [f.shape() for f in frags]
    if occupied is not None:
        shapes.append(occupied)
    return G.from_shape(shapely.union_all(shapes))


def build():
    """The flood with every mark as a hole.  The union of the marks lies wholly
    inside the flood and is non-overlapping, so ``flood + holes`` under the
    even-odd rule IS the exact difference -- one FILL path."""
    p, occ = _parts()
    frame = [f for k, f in p.items() if k not in BE.EMBLEM_KEYS]
    ko = BF.flood_d() + holes_d(frame, occupied=occ)
    return {"jade": [f'<path d="{ko}" fill="{T.JADE}" fill-rule="evenodd"/>']}
