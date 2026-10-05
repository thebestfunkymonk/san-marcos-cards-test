"""art/JOKER_BLACK.py: Little Joker · The Trickster (brief §H.18).

A male great-tailed grackle in the sky-pointing display, upright on a
sagging festoon wire hung with three gold bulbs: bill pointed at the sky,
flat crown running into the culmen, gold eye ring round an Aquifer pupil,
the long graduated tail folded into its V and hanging below the wire as a
tall keel. The stolen gold coronet dangles from the tip of his bill, caught
mid-swing, the tip catching its band's rim; five short FINE dash-rays fan
round the back of his head (the call). Inks: Aquifer, jade, gold (§C).

Construction (helpers in art/_joker_black_*.py):

* _joker_black_pose     -- the drafted anatomy in three frames (head along
                           the bill, body axis, tail keel): the body outline
                           as a G1 chain of circular arcs, the bill, the
                           graduated V-keeled tail, the wing frame, the feet.
* _joker_black_plumage  -- ONE Aquifer solid with the feathering knocked out
                           geometrically (MEDIUM paper lines): covert scale
                           rows, the flight feathers as graduated bands with
                           stepped round tips, breast scale arcs, the rectrix
                           edges, the gape. Alternate feather tracts are
                           half-hatched in jade (the lesser coverts; the
                           outer vanes of the outer and central rectrices)
                           as windows in the solid; the gold iris sits in a
                           hole under the pupil.
* _joker_black_props    -- wire, bulbs, legs and gripping feet, coronet,
                           call rays, caption (§F.4, §J.2 verbatim).

Layer logic (contract §2.1): jade and gold only ever live in holes of the
Aquifer solid. Interlace (§B.2): the lower body and tail hang in front of the
wire (it breaks 4.2 px clear of them). The coronet hangs from the bill tip
(client correction 2026-09-24): the tip's point catches the band's bottom
rim beside its left end and lies over it -- ink over gold, a trap, the same
join as the bulb necks under their sockets -- so neither the bill nor the
coronet is cut: band, all five points, the three ball finials and the three
jewels read whole, and the bill keeps its sharp tip and its gape.

Placement (client correction 2026-09-24, with frames.JOKER_DY): the figure
is drafted in the pose/props frame and moved onto the card by ONE rigid
translation, props.FIG_SHIFT -- lowered to sit its lowest ink 50 px above
the lowered joker rule (the Fool's gap) and centre the whole block, and
moved left to balance the bird's and coronet's mass about x 375; the wire's
ends and the bulbs keep their card places (ends symmetric about 375).
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
    """Remove crumbs a cut may leave (pieces too small to print)."""
    parts = [q for q in getattr(g, "geoms", [g]) if q.area >= min_area]
    return shapely.union_all(parts) if parts else g


def build():
    legs, _ = PR.legs()
    pl = PL.build(extra_solid=legs)
    solid = pl["solid"]

    # the coronet hangs whole from the bill tip: the tip's point lies over the
    # band's bottom rim (ink over gold, a trap -- a join, not a crossing), so
    # neither is cut; the coronet keeps its drawn finish (the 1.3 px closing:
    # rounded jewels, filleted valleys and finial necks)
    cor = PR.coronet()
    cor = _drop_crumbs(PL.clean(cor, keep=cor))

    # the lower body and tail hang in front of the wire; the feet stand on it
    lower = PL.tail_shape().union(PL.body_shape()).difference(
        shapely.box(P.FOOT_F[0] - 20.0, 0, 800, 1050))
    wire = M.cut(PR.wire_frag(), lower, GAP)

    ink = M.fill(G.from_shape(solid), color=T.INK, role="bird") + pl["ink"]
    ink += wire + PR.wire_terminals()
    gold = pl["gold"] + M.fill(G.from_shape(cor), color=T.FOIL, role="coronet")
    for x in PR.BULB_X:
        bi, bg = PR.bulb(x)
        ink += bi
        gold += bg
    ink += PR.call_rays()
    fig = (pl["jade"] + gold + ink).translate(*PR.FIG_SHIFT)       # the figure onto the card, rigidly
    f = fig + PR.caption()
    return layers_merge(f.fragments(), {"gold": F.joker_rule_fragments(T.FOIL)})
