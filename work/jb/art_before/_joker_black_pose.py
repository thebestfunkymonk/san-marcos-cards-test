"""JOKER_BLACK pose: the great-tailed grackle, drafted in card px.

A male in the sky-pointing display, facing right: bill pointed at the sky
(64 deg above the horizon), neck stretched, body inclined 50 deg, the long
V-folded tail carried down and back (27 deg below the horizon) as a deep keel.

Every outline is a G1 chain of circular arcs (biarcs) through drafted key
points; each point's tangent is the tangent of the circle through it and its
two neighbours (convex runs never wobble) unless pinned. Coordinates are card
px (y down); headings are screen degrees (0 = +x, 90 = down).

Anatomy (research/refs/jokers/grackle_*, looked at, never traced): flat crown
running straight into the culmen; bill a little longer than the head, deep
at the base, culmen gently decurved; pale eye just above and behind the gape
corner; thick neck stretched in display; slim body; folded wing lying along
the body side with the primaries projecting past the rump onto the tail;
long graduated tail folded into a V -- seen from the side a deep blade whose
lower edge is the keel (the long central pair) and whose tip steps back
feather by feather to the short outer pair; long bare tarsi, big feet.
"""
from __future__ import annotations

import math

import numpy as np

from deck.motifs import forms


# ---------------------------------------------------------------------------
# frames
# ---------------------------------------------------------------------------
def unit(h):
    a = math.radians(h)
    return np.array([math.cos(a), math.sin(a)])


class Frame:
    """Drafting frame: origin ``o``; +u along heading ``h``; +v is 90 deg
    clockwise of +u (``vsign`` = -1 flips it)."""

    def __init__(self, o, h, vsign=1.0):
        self.o = np.asarray(o, float)
        self.h = float(h)
        self.U = unit(h)
        self.V = unit(h + 90.0) * vsign
        self.vs = vsign

    def __call__(self, u, v=0.0):
        return self.o + self.U * u + self.V * v

    def head(self, deg):
        """Heading in card space of a local heading ``deg`` (0 = +u, 90 = +v)."""
        return self.h + self.vs * deg

    def local(self, p):
        d = np.asarray(p, float) - self.o
        return np.array([d @ self.U, d @ self.V])


def closed_spline(pts, pins=None):
    pts = [np.asarray(p, float) for p in pts]
    n = len(pts)
    hs = [forms.circle_heading(pts[i - 1], pts[i], pts[(i + 1) % n]) for i in range(n)]
    for i, h in (pins or {}).items():
        hs[i] = h
    d, _ = forms.biarc_chain(pts, hs, closed=True)
    return d


def open_spline(pts, h0=None, h1=None, pins=None):
    d, P, _ = forms.arc_spline([np.asarray(p, float) for p in pts], h0, h1, headings=pins)
    return d, P


# ---------------------------------------------------------------------------
# head (u forward along the bill, v toward the throat) and body frame
# (u along the body axis toward the neck, v toward the belly)
# ---------------------------------------------------------------------------
BILL_DEG = -64.0
HEAD = Frame((508.0, 176.0), BILL_DEG)
BILL_LEN = 70.0
BILL_TIP = HEAD(BILL_LEN, 0.6)
EYE_C = HEAD(-24.0, -6.5)
EYE_R = 6.8                      # iris (gold) outer radius
PUPIL_D = 6.3
CALL_C = HEAD(-24.0, 0.0)        # centre the call rays radiate from

BODY = Frame((450.0, 366.0), -50.0)

BODY_PTS = [
    HEAD(-1.0, -10.6),           # 0 culmen base (forehead feathering)
    HEAD(-20.0, -18.6),          # 1 forehead
    HEAD(-42.0, -24.2),          # 2 flat crown
    HEAD(-62.0, -25.0),          # 3 occiput
    HEAD(-84.0, -23.5),          # 4 nape
    (453.0, 276.0),              # 5 hindneck
    BODY(44.0, -53.0),           # 6 mantle
    BODY(-12.0, -51.0),          # 7 back
    BODY(-62.0, -43.0),          # 8 lower back
    BODY(-100.0, -29.0),         # 9 rump
    BODY(-122.0, -17.0),         # 10 tail base (top)
    BODY(-116.0, 19.0),          # 11 under-tail coverts (keel)
    BODY(-76.0, 41.0),           # 12 vent
    BODY(-18.0, 53.0),           # 13 belly
    BODY(42.0, 52.0),            # 14 lower breast
    BODY(92.0, 40.0),            # 15 breast
    HEAD(-96.0, 37.0),           # 16 foreneck
    HEAD(-60.0, 31.0),           # 17 throat
    HEAD(-26.0, 24.0),           # 18 chin
    HEAD(-1.0, 10.4),            # 19 chin at the bill base
]
BODY_PINS = {0: HEAD.head(180.0 + 14.0), 19: HEAD.head(8.0)}


def body_d():
    return closed_spline(BODY_PTS, BODY_PINS)


def bill_d():
    """Upper mandible: culmen gently decurved to a sharp tip; lower mandible:
    gonys nearly straight. Closed shape including the gape (knocked out)."""
    L = BILL_LEN
    top, _ = open_spline([HEAD(-4.0, -10.2), HEAD(L * 0.45, -6.6), BILL_TIP],
                         HEAD.head(-3.0), HEAD.head(14.0))
    bot, _ = open_spline([BILL_TIP, HEAD(L * 0.5, 5.4), HEAD(-4.0, 10.4)],
                         HEAD.head(180.0 - 8.0), HEAD.head(180.0 + 2.0))
    return top + bot.replace("M", "L", 1) + "Z"


def gape_d():
    """Commissure: from the gape corner (below the eye) toward the tip."""
    d, _ = open_spline([HEAD(-15.0, 2.6), HEAD(4.0, 1.4), HEAD(BILL_LEN * 0.5, 0.5)])
    return d


# ---------------------------------------------------------------------------
# tail: the keel (u along the tail, v toward the keel -- down / forward)
# ---------------------------------------------------------------------------
TAIL_DEG = 153.0
TAIL = Frame(BODY(-120.0, 0.0), TAIL_DEG, vsign=-1.0)       # +v = keel side
N_RECT = 3                         # rectrices shown on the near arm of the V
TAIL_TOP = (-17.0, -24.0)          # top edge v at base / end
TAIL_KEEL = (20.0, 55.0)           # keel edge v at base / end
TAIL_U_TOP, TAIL_U_KEEL = 212.0, 280.0      # graduated: outer pair short, central pair long
TAIL_BOW = 17.0                     # the keel edge bows (convex) toward the keel


def tail_v(k, u):
    """v of feather boundary k (0 = top edge ... N_RECT = keel) at u."""
    t = k / N_RECT
    v0 = TAIL_TOP[0] + (TAIL_KEEL[0] - TAIL_TOP[0]) * t
    v1 = TAIL_TOP[1] + (TAIL_KEEL[1] - TAIL_TOP[1]) * t
    x = min(max(u / TAIL_U_KEEL, 0.0), 1.1)
    # depth opens toward the end (easing), keel side bowing
    e = x ** 1.25
    return v0 + (v1 - v0) * e + TAIL_BOW * t * math.sin(math.pi * min(x, 1.0))


def tail_end_u(k):
    t = k / N_RECT
    return TAIL_U_TOP + (TAIL_U_KEEL - TAIL_U_TOP) * t


_TB = {}


def _boundary_curve(k):
    """Feather boundary k as ONE G1 chain of circular arcs through five
    drafted stations (u from under the rump to the feather's end)."""
    if k not in _TB:
        E = tail_end_u(k)
        us = [-40.0, 0.22 * E, 0.48 * E, 0.74 * E, E]
        d, _ = open_spline([TAIL(u, tail_v(k, u)) for u in us])
        from deck.motifs import sample_d
        pts = sample_d(d, 0.5)[0][0]
        _TB[k] = (pts, np.array([TAIL.local(p)[0] for p in pts]))
    return _TB[k]


def tail_boundary(k, u0=-20.0, u1=None, n=None):
    """The part of boundary k between tail-u ``u0`` and ``u1`` (its end)."""
    pts, us = _boundary_curve(k)
    u1 = tail_end_u(k) if u1 is None else u1
    m = (us >= u0) & (us <= u1)
    out = pts[m]
    a = np.array([np.interp(u0, us, pts[:, 0]), np.interp(u0, us, pts[:, 1])])
    return np.vstack([a, out]) if u0 > us[0] else out


TIP_SAG = 5.0


def rectrix_d(i, u0=-40.0):
    """Closed outline of rectrix i (between boundaries i and i+1): its upper
    edge, the round tip arc, back along its lower edge."""
    from deck.motifs.forms import scallop_arc
    a = tail_boundary(i, u0=u0)
    b = tail_boundary(i + 1, u0=u0)
    p, q = a[-1], b[-1]
    ch = q - p
    left = np.array([ch[1], -ch[0]])
    sg = TIP_SAG if left @ TAIL.U > 0 else -TIP_SAG
    d = "M" + "L".join(f"{x:.3f} {y:.3f}" for x, y in a)
    d += scallop_arc(p, q, sg, move=False)
    d += "".join(f"L{x:.3f} {y:.3f}" for x, y in tail_boundary(i + 1, u0=u0, u1=tail_end_u(i + 1))[::-1])
    return d + "Z"


def tail_outline_d():
    """Top edge -> stepped round feather tips -> keel edge -> back to base."""
    from deck.motifs.forms import scallop_arc
    top = tail_boundary(0)
    d = "M" + "L".join(f"{x:.3f} {y:.3f}" for x, y in top)
    for i in range(N_RECT):
        p = tail_boundary(i)[-1]
        q = tail_boundary(i + 1)[-1]
        # bulge outward (toward +u, the tip direction)
        ch = q - p
        left = np.array([ch[1], -ch[0]])
        sg = TIP_SAG if left @ TAIL.U > 0 else -TIP_SAG
        d += scallop_arc(p, q, sg, move=False)
    keel = tail_boundary(N_RECT)[::-1]
    d += "".join(f"L{x:.3f} {y:.3f}" for x, y in keel)
    return d + "Z"


# ---------------------------------------------------------------------------
# folded wing (u from the wrist toward the tip, v toward the belly edge)
# ---------------------------------------------------------------------------
WING_DEG = 131.0
WING = Frame(BODY(62.0, -8.0), WING_DEG, vsign=-1.0)    # origin at the wrist; +v = lower edge
WING_LEN = 236.0                 # wrist to the primary tip (the feathers: _joker_black_plumage)


# ---------------------------------------------------------------------------
# feet (x on the wire; the props module hangs them on it)
# ---------------------------------------------------------------------------
FOOT_N = np.array([500.0, 0.0])        # near foot, stepping forward
FOOT_F = np.array([444.0, 0.0])        # far foot
