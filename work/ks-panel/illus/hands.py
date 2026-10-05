"""Court hands (brief §H.0): mitten shapes with 3 finger lines and a separate
thumb, closed round cylindrical attributes. Open hands are avoided.

Each hand is authored ONCE in a local frame with hand-placed Bézier knots,
then placed with a rigid transform (translate / rotate / ±1 mirror — never a
scale), so a queen's sceptre hand and a jack's lantern hand are the same
drawing. Returns a ``Hand``: silhouettes of the mitten and the thumb (FILL d,
paper — skin is never filled), their interior lines (MEDIUM), and anchors
(``wrist``: the point and the forearm direction the sleeve/cuff attaches to).

    fist(x, y, ...)        round a VERTICAL shaft through (x, y); knuckles to
                           the viewer, finger ends toward ``tips`` (±1),
                           thumb over the top, wrist leaving low on the
                           opposite side
    cup(ox, oy, r, ...)    under a sphere of radius r at (ox, oy): palm below,
                           fingers curled up the ``tips`` side, thumb up the
                           other side
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from deck import tokens as T
from deck.motifs import core as MC
from inkkit import geom as G

from bez import K, path, pts


@dataclass
class Hand:
    mitten: str
    thumb: str
    lines: MC.Frag
    thumb_lines: MC.Frag
    anchors: dict = field(default_factory=dict)


def _place(d: str, x, y, mir: bool, rot: float = 0.0) -> str:
    if mir:
        d = G.mirror_x(d, 0.0)
    if rot:
        d = G.rotate(d, rot, 0.0, 0.0)
    return G.translate(d, x, y)


def _place_f(f: MC.Frag, x, y, mir: bool, rot: float = 0.0) -> MC.Frag:
    if mir:
        f = f.mirror_x(0.0)
    if rot:
        f = f.rotate(rot, 0.0, 0.0)
    return f.translate(x, y)


def fist(x: float, y: float, *, tips: int = +1, rot: float = 0.0, shaft_w: float = 18.0) -> Hand:
    """Mitten fist round a vertical shaft centred at (x, y). Local frame:
    finger ends to +x, wrist to −x/+y. ``tips`` = −1 mirrors it."""
    # mitten: 44 w × 46 h, knuckle side round, finger-end side fuller
    mit = path([K(-17, -20, 0, lo=10),               # top, under the thumb
                K(13, -21, 10, li=9),
                K(24, -6, 90, li=8, lo=8),            # finger ends (full, rounded)
                K(22, 16, 105, li=10, lo=6),
                K(10, 24, 180, li=7, lo=8),           # little-finger heel
                K(-6, 23, 185),
                K(-17, 30, ai=120, ao=150, li=6, lo=4),   # wrist, lower edge
                K(-33, 34, ai=160, ao=250, li=6, lo=4),   # wrist cut (under the cuff)
                K(-30, 12, ai=-60, ao=-80, li=6),
                K(-26, -8, -70, li=8, lo=6)], closed=True)
    # three finger lines: from the finger-end edge in toward the knuckles
    fl = MC.Frag()
    for yy, x0 in ((-6.5, 4.0), (4.0, 3.0), (14.0, 1.0)):
        fl += MC.stroke(path([K(x0, yy + 0.8, ao=-6), K(23.2, yy - 0.3, ai=4)]), T.MEDIUM, role="finger")
    # thumb: a separate rounded shape lying across the top, tip toward the finger ends
    th = path([K(-24, -10, ai=200, ao=-70, li=4, lo=6),
               K(-12, -27, -10, li=8, lo=8),
               K(14, -25, 8, li=8, lo=6),
               K(23, -17, ai=70, ao=178, li=4, lo=4),     # rounded tip, well across the shaft
               K(2, -12, 182, li=8, lo=8),
               K(-16, -4, ai=165, ao=150, li=6)], closed=True)
    tl = MC.Frag()                                   # (no nail tick: it crowds the thumb's edge)
    mir = tips < 0
    return Hand(_place(mit, x, y, mir, rot), _place(th, x, y, mir, rot),
                _place_f(fl, x, y, mir, rot), _place_f(tl, x, y, mir, rot),
                dict(wrist=(x + (-31 if not mir else 31), y + 22), shaft_w=shaft_w))


def cup(ox: float, oy: float, r: float, *, tips: int = +1) -> Hand:
    """Hand under a sphere (centre (ox, oy), radius r ≈ 31): the palm below,
    four fingers fanned up IN FRONT of the sphere's lower part (tips on an arc
    that follows the sphere, the middle finger longest), finger lines
    converging toward the palm, the thumb standing apart up the outer side.
    The wrist leaves low on the thumb side. ``tips`` −1 mirrors it."""
    # fingertip centres (x, y, radius) — index, middle, ring, little
    tipc = [(-14.0, 14.0, 6.4), (-2.4, 11.5, 6.4), (9.4, 12.8, 6.2), (19.8, 16.8, 5.6)]
    notch = [(-8.2, 16.8), (3.6, 15.4), (14.8, 19.2)]
    kn = [K(-24, 30, ai=-60, ao=-76, li=6, lo=8)]                  # index finger's outer side
    for i, (x, y, rr) in enumerate(tipc):
        kn.append(K(x, y - rr, 0, li=rr * 0.7, lo=rr * 0.7))        # tip (round, blunt)
        if i < 3:
            nx, ny = notch[i]
            kn.append(K(nx, ny, ai=62, ao=-62, li=2.6, lo=2.6))    # between fingers (shallow)
    kn += [K(25, 23, ai=70, ao=100, li=6, lo=6),                    # little finger's outer side
           K(20, 36, 150, li=8, lo=8),
           K(0, 45, 185, li=10, lo=10),
           K(-26, 44, ai=195, ao=215, li=10, lo=4),                 # heel → wrist
           K(-44, 52, ai=215, ao=-70, li=4, lo=4),                  # wrist cut (in the cuff)
           K(-36, 34, ai=-80, ao=-40, li=6, lo=4)]
    mit = path(kn, closed=True)
    fl = MC.Frag()
    for (nx, ny) in notch:
        # from the notch toward the palm centre (0, 44), 13 px long
        dx, dy = 0 - nx, 46 - ny
        L = (dx * dx + dy * dy) ** 0.5
        fl += MC.stroke(np.array([(nx + dx / L * 1.0, ny + dy / L * 1.0), (nx + dx / L * 8.5, ny + dy / L * 8.5)]),
                        T.MEDIUM, role="finger")
    thumb = path([K(-39, 42, ai=110, ao=-98, li=4, lo=10),
                  K(-42, 14, -90, li=10, lo=7),
                  K(-33, 1, ai=-50, ao=30, li=6, lo=6),      # tip (round, sturdy)
                  K(-23, 12, 98, li=6, lo=8),
                  K(-21, 34, ai=92, ao=160, li=8)], closed=True)
    mir = tips < 0
    return Hand(_place(mit, ox, oy, mir), _place(thumb, ox, oy, mir), _place_f(fl, ox, oy, mir),
                MC.Frag(), dict(wrist=(ox + (-42 if not mir else 42), oy + 46)))
