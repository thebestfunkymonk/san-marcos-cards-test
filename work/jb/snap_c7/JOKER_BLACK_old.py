"""art/JOKER_BLACK.py: Little Joker · The Trickster (brief §H.18).

A male great-tailed grackle in the sky-pointing display, strutting along a
sagging festoon wire hung with three gold bulbs; the stolen gold coronet he
has lifted hangs from the tip of his bill; five short dash-rays are his call.

Construction (helpers in art/_joker_black_*.py):

* _joker_black_pose     -- the drafted anatomy: head / body / tail / wing
                           frames, the body outline as a G1 chain of circular
                           arcs, the bill, the graduated V-keeled tail.
* _joker_black_plumage  -- ONE Aquifer solid with the feathering knocked out
                           geometrically (MEDIUM paper lines: breast and
                           covert scale arcs, the folded wing as a painter's
                           stack of feathers, the rectrices, the gape); the
                           two jade tracts (upper tertial, outer rectrix) are
                           windows in the solid holding FINE jade hatch; the
                           gold iris sits in a hole under the Aquifer pupil.
* _joker_black_props    -- wire, bulbs, legs and feet, coronet, call rays,
                           caption (§F.4, §J.2 verbatim).

Layer logic (contract §2.1): jade and gold only ever live in holes of the
Aquifer solid. Interlace (§B.2): the tail hangs in front of the wire (the
wire breaks 4.2 px clear of it); the bill passes in front of the coronet
(the gold breaks 4.2 px clear of the bill).
"""
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


def _drop_crumbs(g, min_area=20.0):
    """Remove gold crumbs a cut may leave (pieces too small to print)."""
    parts = [q for q in getattr(g, "geoms", [g]) if q.area >= min_area]
    return shapely.union_all(parts) if parts else g


def build():
    legs, toes = PR.legs()
    pl = PL.build(extra_solid=legs)
    solid = pl["solid"]

    # the coronet hangs from the bill tip, behind the bill
    bill = shapely.Point(P.BILL_TIP).buffer(60.0).intersection(solid)
    cor = PR.coronet().difference(bill.buffer(GAP))
    away = cor.difference(bill.buffer(GAP + 8.0))            # hygiene only where the bill cuts
    cor = _drop_crumbs(PL.clean(cor, keep=away))

    # the tail hangs in front of the wire; the toes lie on the wire and merge with it
    tail_sil = PL.tail_shape().difference(shapely.box(P.FOOT_F[0] - 30.0, 0, 800, 1050))
    wire = M.cut(PR.wire_frag(), tail_sil, GAP)

    ink = M.fill(G.from_shape(solid), color=T.INK, role="bird") + pl["ink"]
    ink += toes + wire + PR.wire_terminals()
    gold = pl["gold"] + M.fill(G.from_shape(cor), color=T.FOIL, role="coronet")
    for x in PR.BULB_X:
        bi, bg = PR.bulb(x)
        ink += bi
        gold += bg
    ink += PR.call_rays()
    ink += PR.caption()
    f = pl["jade"] + gold + ink
    return layers_merge(f.fragments(), {"gold": F.joker_rule_fragments(T.FOIL)})
