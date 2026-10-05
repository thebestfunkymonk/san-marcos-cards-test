"""Card back emblem (brief §H.19): C2 about (375, 525), deliberately not a mirror."""
from __future__ import annotations

from deck import tokens as T
from deck.motifs import core as C, geometric as M
from inkkit import geom as G

from art import _back_geo as BG
from art import _back_darter as BD
from art import _back_rice as BR
from art import _back_spray as BS

CX, CY = T.CX, T.CY
FINE = T.FINE


def rosette() -> C.Frag:
    return M.source_rosette(CX, CY, BG.ROSETTE_R)


DARTER = dict(r=175.0, clock=30.0, L=100.0)


def darter_top(spec=DARTER) -> C.Frag:
    x, y = BG.pol(spec["r"], spec["clock"])
    return BD.darter(x, y, spec["L"], BG.cw(spec["clock"]))


SPRAY = dict(y0=368.0, y1=118.0, cone=11.0, tick=16.0)


def spray(spec=SPRAY) -> C.Frag:
    return M.comb_spray(C.polyline_d([(CX, spec["y0"]), (CX, spec["y1"])]), tick=spec["tick"],
                        cone=spec["cone"], angle=55.0)


def emblem() -> dict:
    ros, dar, rice = rosette(), BG.c2(darter_top()), BG.c2(BR.sheaf())
    b = BS.bough(others=[ros, dar, rice])
    b += BS.cascade(others=[ros, dar, rice])
    return dict(rosette=ros, darters=dar, rice=rice, sprays=BG.c2(b))
