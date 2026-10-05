"""Head test bench for K♥ (not deck art)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import courtkit as K  # noqa: E402
from art import _kh_parts as KP  # noqa: E402
from art import _kh_head as KHH  # noqa: E402

AX = K.AX
HEAD = (AX, 207.0)
VAR = os.environ.get("KHV", "a")


def figure():
    sc = K.Scene(rank="K")
    fc = K.face(HEAD, "frontal", age="elder", lids="level")
    ms = K.MantleSpec(neck_y=272.0, neck_heading=170.0, run=140.0, corner_r=30.0, side_heading=99.0)
    robe = K.mantle(ms, color=K.RED, border=0.0, seam=False)
    sc.part("robe", robe)
    hs = K.HairSpec(bulge=(-60.0, 36.0), bottom=(-50.0, 92.0), ribbons=4)
    for side in (-1, 1):
        sc.part(f"hair{side}", K.hair_fall(fc, side, hs))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    mo = KHH.moustache(fc)
    sc.part("beard", KHH.beard(fc, mo=mo))
    sc.part("moustache", mo)
    cr, pe = KP.pearl_crown(posts_sil=False, foot_w=14.0, hatch=False, pearl_d=(18.0, 16.0, 14.5, 13.0))
    sc.part("crown", cr)
    sc.part("pearls", pe, sil=False)
    K.band_guard(sc, "K")
    return sc


def build():
    return figure().layers()
