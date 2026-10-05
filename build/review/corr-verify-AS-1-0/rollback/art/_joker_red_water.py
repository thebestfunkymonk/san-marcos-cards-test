"""Water for JOKER_RED (brief §H.17), all gold FINE:

* the bubble trail (§G.9): from the tip of the tail's curl a Ø4.2 dot, then
  rings growing x1.2 with equal clear gaps, streaming back off the tail as a
  wake along a circle concentric with the porthole (the tail's tip lies on
  it, heading along it);
* the running-wave scroll (§G.7): the trail runs on round the same circle as
  a FINE rule, clockwise over the ring's upper right, rigid copies of the
  library's wave_hook springing outward from it; the rule ends in a Ø6.3
  terminal;
* three ripple ellipses (§G.8) at y ~600 under the snout: similar ellipses,
  ry/rx 0.3, the gaps growing x1.3 outward.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point

from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms as FM
from deck.motifs import geometric as GM
from inkkit import geom as G

GOLD = T.FOIL
FINE, MED = T.FINE, T.MEDIUM

RIPPLE_Y = 604.0
RIPPLE = dict(r0=24.0, gap0=22.0, ratio=1.3, ry_ratio=0.30)

BUBBLES = (4.2, 6.3, 7.6, 9.1, 10.9)   # Ø4.2 dot, then rings x1.2 (§G.9)
BUBBLE_GAP = 4.6                 # clear gap between bubbles
TRAIL_LEAD = 5.0                 # clear distance from the tail to the first bubble
SCROLL_GAP = 6.0                 # clear distance from the last bubble to the scroll's rule
SCROLL_END = -22.0                # polar angle (deg, screen) where the rule ends
WAVE_H = 24.0
WAVE_PITCH = 40.0


def ripples(cx: float) -> C.Frag:
    return GM.ripple_rings(cx, RIPPLE_Y, RIPPLE["r0"], RIPPLE["gap0"], ratio=RIPPLE["ratio"],
                           ry_ratio=RIPPLE["ry_ratio"], mode="similar", color=GOLD)


def _polar(c, p):
    v = np.asarray(p, float) - c
    return math.hypot(*v), math.degrees(math.atan2(v[1], v[0]))


def trail_path(tip, ring_c):
    """Dense centreline: one circle concentric with the porthole through the
    tail's tip, clockwise from the tip to SCROLL_END -- the bubbles stream
    back off the tail as a wake round the top of the ring and run on into
    the scroll."""
    c = np.asarray(ring_c, float)
    R, a0 = _polar(c, tip)
    arc = np.array([c + R * np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
                    for a in np.arange(a0, SCROLL_END + 0.01, 0.2)])
    return arc, R


def water(snout, tail_tip, ring_c, tail_w=6.25, tail=None):
    """``snout``: the disc centre (page); ``tail_tip``: the tail's end (page);
    ``ring_c``: the porthole centre; ``tail_w``: the tail's width; ``tail``:
    the tail's shape (the first bubble clears all of it)."""
    c = np.asarray(ring_c, float)
    f = ripples(float(snout[0]))
    path, R = trail_path(tail_tip, c)
    cv = G.Curve(path)
    tip = Point(*tail_tip)
    outer = [d if i == 0 else d + FINE for i, d in enumerate(BUBBLES)]
    s = 0.0
    clear = tail if tail is not None else tip.buffer(tail_w / 2)
    while clear.distance(Point(*cv.at_s(s))) < TRAIL_LEAD + outer[0] / 2:
        s += 0.2
    for i, d in enumerate(BUBBLES):
        if i:
            s += outer[i - 1] / 2 + BUBBLE_GAP + outer[i] / 2
        x, y = cv.at_s(s)
        f += C.bubble(x, y, d, style="dot" if i == 0 else "ring", color=GOLD)
    s += outer[-1] / 2 + SCROLL_GAP + FINE / 2
    # the scroll: the rule from after the last bubble to the path's end,
    # hooks springing outward, flowing clockwise, a terminal at the end
    total = LineString(path).length
    ss = np.arange(s, total, 0.5)
    rule = np.array([cv.at_s(x) for x in ss] + [path[-1]])
    f += C.stroke(C.polyline_d(rule), FINE, color=GOLD, role="wave-rule")
    f += C.terminal(*path[-1], color=GOLD)
    hook = GM.wave_hook(WAVE_H, color=GOLD)
    width = hook.meta["wave_width"]
    _, a_start = _polar(c, cv.at_s(s))
    L = math.radians(SCROLL_END - a_start) * R
    n = int((L - width - 16.0) // WAVE_PITCH) + 1
    lead = (L - (n - 1) * WAVE_PITCH - width) / 2
    for i in range(n):
        th = a_start + math.degrees((lead + i * WAVE_PITCH) / R)
        x, y = c + R * np.array([math.cos(math.radians(th)), math.sin(math.radians(th))])
        f += hook.rotate(th + 90.0).translate(x, y)
    f.meta.update(n_waves=n, scroll_r=R)
    return f
