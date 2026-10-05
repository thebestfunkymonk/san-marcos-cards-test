"""art/AS.py: A♠ · The Lion of the Source (brief §H.13) — the deck's showpiece.

A solid Aquifer spade (deck.frames.ace_pip_d('S'), no keyline) carrying a
gold emblem: the winged lion of St. Mark in moleca, its forepaws on a spring
vent, the water rising to it through a conduit in the stem from the rock of
the fault-step plinth. Outside the spade, in gold: the broken waterline, two
bubble columns, and the four-line legend. Gold prints ABOVE the ink on this
card (§K; the system orders the layers).
"""
from __future__ import annotations

import shapely

from deck import frames as F
from deck import tokens as T
from deck.cardsvg import layers_merge
from inkkit import svg as SV

import _as_legend_bak as L
from art import _as_lion as LION
from art import _as_water as W


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


def build():
    spade = F.ace_pip_d("S")
    ink = {"ink": [SV.path(spade, fill=T.INK, class_="ace-pip")]}
    gold = emblem() + W.waterline() + W.bubble_columns() + L.legend()
    return layers_merge(ink, gold.fragments())
