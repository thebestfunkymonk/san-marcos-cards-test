"""Card back emblem (brief §H.19): C2 about (375, 525), deliberately not a mirror."""
from __future__ import annotations

import math

from shapely.geometry import box
import shapely
from shapely.ops import unary_union

from deck import tokens as T
from deck.motifs import core as C, geometric as M
from inkkit import geom as G

from art import _back_geo as BG
from art import _back_darter as BD
from art import _back_rice as BR
from art import _back_bough as BB
from art import _back_bubbles as BU

CX, CY = T.CX, T.CY
FINE = T.FINE


def rosette() -> C.Frag:
    return M.source_rosette(CX, CY, BG.ROSETTE_R)


DARTER = dict(r=175.0, clock=30.0, L=100.0)


def darter_top(spec=DARTER) -> C.Frag:
    x, y = BG.pol(spec["r"], spec["clock"])
    return BD.darter(x, y, spec["L"], BG.cw(spec["clock"]))


BUBBLES = dict(n=6, min_r=13.5, tilt=0.0)


def bubbles(others, spec=BUBBLES, occupied=None) -> C.Frag:
    """Bubble triads in the largest leftover pockets of the top half (each
    with its 180° copy)."""
    occ = occupied if occupied is not None else unary_union([o.shape() for o in others])
    lim = BG.limit_region().intersection(box(0, 0, 750, CY - 1.0))
    f = C.Frag()
    for x, y, r in BU.pockets(occ, lim, BG.GAP, n=spec["n"], min_r=spec["min_r"]):
        # growing outward from the Source, like the rings round it
        f += BU.triad(x, y, math.degrees(math.atan2(y - CY, x - CX)) + spec["tilt"])
    return BG.c2(f)


EMBLEM_KEYS = ("rosette", "darters", "rice", "sprays", "bubbles")
FILLET = 0.85      # fill jade slivers < 1.7 px inside each drawn motif (acute T-junction wedges)


def emblem(with_shape: bool = False):
    """{name: Frag} of the emblem motifs; with ``with_shape`` also the union
    of their marks (shapely), built incrementally (it is needed by the bough,
    the bubbles and the frame's inner echoes)."""
    ros = rosette()
    dar = BG.fillet(BG.c2(darter_top()), FILLET)
    rice = BG.fillet(BG.c2(BR.sheaf()), FILLET)
    occ = shapely.union_all([ros.shape(), dar.shape(), rice.shape()])
    b = BG.fillet(BG.c2(BB.bough(obstacle=occ)), FILLET)
    occ = shapely.union_all([occ, b.shape()])
    out = dict(rosette=ros, darters=dar, rice=rice, sprays=b)
    if BUBBLES.get("n"):
        out["bubbles"] = bubbles(None, occupied=occ)
        if out["bubbles"].marks:
            occ = shapely.union_all([occ, out["bubbles"].shape()])
    return (out, occ) if with_shape else out
