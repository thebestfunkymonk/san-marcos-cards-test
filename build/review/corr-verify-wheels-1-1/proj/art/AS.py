"""art/AS.py: A♠ · The Lion of the Source (brief §H.13) — the deck's showpiece.

A solid Aquifer spade (deck.frames.ace_pip_d('S'), no keyline) carrying a
gold emblem: the winged lion of St. Mark in moleca, its forepaws on a spring
vent, the water rising to it through a conduit in the stem from the rock of
the fault-step plinth. Outside the spade, in gold: the broken waterline, two
bubble columns, and the four-line legend. Gold prints ABOVE the ink on this
card (§K; the system orders the layers).

Placement (client correction, 2026-09-24): drawn on the brief's grid (spade
top y 140, §F.3/§H.13) the composition's rendered block ran y 140–735
(middle 437.5, 88 px above the card centre) and left the lower third empty.
The whole composition — spade, emblem, water, bubble columns and legend —
is moved down as one rigid unit by COMPOSITION_DY (applied to the path data;
nothing is redrawn), so the block (y 232–811 with the legend's arc
correction, see _as_legend) centres on y 521.5, x 375. Spade top y 232,
plinth bottom 606, waterline y 442, bubble columns y 572 -> 352.
"""
from __future__ import annotations

import shapely

from deck import frames as F
from deck import tokens as T
from deck.cardsvg import layers_merge
from inkkit import geom as G
from inkkit import svg as SV

from art import _as_legend as L
from art import _as_lion as LION
from art import _as_water as W

COMPOSITION_DY = 92.0      # the whole A♠ composition moves down as one unit (see the docstring)


def emblem():
    """Front to back: face > mane > paws > wings > vent; the conduit rises
    into the vent from the plinth's bedding line."""
    hd, sil = LION.head()
    pw, paw_shape = LION.paws()
    pw = LION.behind(pw, sil)                                  # the paws come out from under the beard
    front = sil.union(paw_shape)
    wr = LION.wing()
    wr = LION.behind(wr, front)
    wings = LION.mirror(wr)
    vt = W.vent()
    # the paws stand in the vent: its far rims pass behind them, ending on
    # the paws' sides (each paw's hull, so no ripple peeps between the toes);
    # the vent's ends pass behind the wings
    hulls = shapely.union_all([g.convex_hull for g in getattr(paw_shape, "geoms", [paw_shape])])
    vt = LION.behind(vt, front.union(hulls).union(LION.mirror_shape(wr.meta["shape"])))
    lion = LION.drop_specks(LION.prune_hatch(wings + vt + hd + pw))
    # covert scallops half-hidden by the mane: keep only what still reads as a scallop
    # (a lone 1½-scallop hook by the crown reads as a stray "?")
    lion = LION.drop_specks(lion, 16.0, roles=("covert",))
    return lion + W.conduit() + W.plinth()


def build(dy: float = COMPOSITION_DY):
    spade = G.translate(F.ace_pip_d("S"), 0.0, dy)
    ink = {"ink": [SV.path(spade, fill=T.INK, class_="ace-pip")]}
    gold = (emblem() + W.waterline() + W.bubble_columns() + L.legend()).translate(0.0, dy)
    return layers_merge(ink, gold.fragments())
