"""draft"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shapely
from deck import tokens as T, frames as F
from deck.cardsvg import layers_merge
from inkkit import geom as G
from deck import motifs as M
import _joker_black_pose as P
import _joker_black_plumage as PL
import _joker_black_props as PR

GAP = T.INTERLACE_GAP


def _drop_crumbs(g, min_area=20.0):
    parts = [q for q in getattr(g, "geoms", [g]) if q.area >= min_area]
    return shapely.union_all(parts) if parts else g


def build():
    legs, toes = PR.legs()
    pl = PL.build(extra_solid=legs)
    solid = pl["solid"]
    bill = shapely.Point(P.BILL_TIP).buffer(60.0).intersection(solid)
    cor = PR.coronet().difference(bill.buffer(GAP))
    away = cor.difference(bill.buffer(GAP + 8.0))
    cor = _drop_crumbs(PL.clean(cor, keep=away))
    lower = PL.tail_shape().union(PL.body_shape()).difference(shapely.box(P.FOOT_F[0] - 20.0, 0, 800, 1050))
    wire = M.cut(PR.wire_frag(), lower, GAP)
    ink = M.fill(G.from_shape(solid), color=T.INK, role="bird") + pl["ink"]
    ink += toes + wire + PR.wire_terminals()
    gold = pl["gold"] + M.fill(G.from_shape(cor), color=T.FOIL, role="coronet")
    for x in PR.BULB_X:
        bi, bg = PR.bulb(x)
        ink += bi
        gold += bg
    ink += PR.call_rays() + PR.caption()
    f = pl["jade"] + gold + ink
    return layers_merge(f.fragments(), {"gold": F.joker_rule_fragments(T.FOIL)})
