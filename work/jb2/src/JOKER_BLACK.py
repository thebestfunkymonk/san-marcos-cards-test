"""art/JOKER_BLACK.py: Little Joker · The Trickster (brief §H.18). Draft 2."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import shapely                                               # noqa: E402

from deck import tokens as T, frames as F                   # noqa: E402
from deck.cardsvg import layers_merge                        # noqa: E402
from inkkit import geom as G                                 # noqa: E402
from deck import motifs as M                                 # noqa: E402

import _joker_black_pose as P                                # noqa: E402
import _joker_black_plumage as PL                            # noqa: E402
import _joker_black_props as PR                              # noqa: E402

GAP = T.INTERLACE_GAP


def build():
    legs = PR.legs()
    pl = PL.build(extra_solid=legs)
    solid = pl["solid"]
    sil = pl["sil"]

    # the coronet: gripped in the bill tip; the bill lies in front of it
    bill = shapely.Point(*P.BILL_TIP).buffer(70.0).intersection(sil)
    cor = PR.coronet().difference(bill.buffer(0.0))

    # the wire passes behind the bird (the feet clasp it in front)
    wire = M.cut(PR.wire_frag(), sil, GAP)

    ink = M.fill(G.from_shape(solid), color=T.INK, role="bird") + pl["ink"]
    ink += wire + PR.wire_terminals()
    gold = pl["gold"] + M.fill(G.from_shape(cor), color=T.FOIL, role="coronet")
    for x in PR.BULB_X:
        bi, bg = PR.bulb(x)
        ink += bi
        gold += bg
    ink += PR.call_rays() + PR.caption()
    f = pl["jade"] + gold + ink
    return layers_merge(f.fragments(), {"gold": F.joker_rule_fragments(T.FOIL)})
