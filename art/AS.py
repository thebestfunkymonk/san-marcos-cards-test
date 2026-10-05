"""art/AS.py: A♠ · The Lion of the Source (brief §H.13) — the deck's showpiece.

A solid Aquifer spade (deck.frames.ace_pip_d('S'), no keyline) carrying a
gold emblem: the winged lion of St. Mark in moleca, its forepaws on a spring
vent, the water rising to it through a conduit in the stem from the rock of
the fault-step plinth. Outside the spade, in gold: the broken waterline, two
bubble columns, and the four-line legend. Gold prints ABOVE the ink on this
card (§K; the system orders the layers).

Placement (v3, client 2026-10-01): the spade is CENTRED on the card — the
whole spade/emblem/water composition moves down COMPOSITION_DY = 198 as one
rigid unit, so its bbox (apex 338 to plinth foot 712) centres on (375, 525).
The legend is split round it like the lettering round the Drifters A♠
(_as_legend.legend_v3): HEADWATERS in a monoline swallowtail ribbon on an arch
with PLAYING CARDS OF THE SAN MARCOS SPRINGS on a concentric arch inside it
above; NEVER KNOWN TO CEASE on a smile and NAMED FOR ST. MARK · MDCLXXXIX (the
§H.13 sagging arc) in a ribbon outside it below.
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

# v3 (client, 2026-10-01): the spade is CENTRED on the card — its bbox
# (apex 140 to plinth foot 514 in §H.13 coordinates) centres on y 525
COMPOSITION_DY = 525.0 - (F.ACE_SPADE_TOP + F.ACE_SPADE_GEOMETRY["plinth_y"][1]) / 2     # 198


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
    gold = (emblem() + W.waterline() + W.bubble_columns()).translate(0.0, dy) + L.legend_v3()
    return layers_merge(ink, gold.fragments())
