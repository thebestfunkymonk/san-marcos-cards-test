"""Card back sand boil (brief §G.27 vent roundel + §G.9 bubble beading).

In the wedge outside each darter a small spring vent -- the §G.27 roundel
with straight ribs -- sends a column of bubbles up along the lens wall
toward the tip, growing x1.2 in the direction of rise (Ø 3-8 px on the
back): Spring Lake's sand boils.  The 7 o'clock vent is the 180° copy.
"""
from __future__ import annotations

import math

import numpy as np

from deck import tokens as T
from deck.motifs import core as C, geometric as M
from inkkit import geom as G

from art import _back_geo as BG

FINE = T.FINE

VENT = dict(c=(262.0, 40.0), d=40.0, inner_d=12.0, ribs=12,
            rise=[(300.0, 26.0), (338.0, 14.0)], d0=3.0, n=7, gap=5.0)


def _size_style(d):
    """Small bubbles solid (Ø 4.2 dot), larger ones rings once the hole keeps >= 3 px."""
    return (4.2, "dot") if d < 5.2 else (d, "ring")


def vent(spec=VENT) -> C.Frag:
    x, y = BG.pol(*spec["c"])
    f = M.vent_roundel(x, y, spec["d"], inner_d=spec["inner_d"], ribs=spec["ribs"])
    start = np.array([x, y])
    _, path = BG.pspline([("xy", x, y)] + list(spec["rise"]))
    cv = G.Curve(path)
    s = spec["d"] / 2 + FINE / 2 + spec["gap"]
    d = spec["d0"]
    prev = 0.0
    for k in range(spec["n"]):
        dd, st = _size_style(d)
        Do = dd if st == "dot" else dd + FINE
        s += Do / 2 + (prev / 2 + spec["gap"] if k else 0.0)
        if s > cv.length:
            break
        p = cv.at_s(s)
        f += C.bubble(p[0], p[1], dd, style=st)
        prev = Do
        s += 0.0
        d = min(8.4, d * 1.2)
        s += 0.0
    return f
