"""JOKER_BLACK pose: the great-tailed grackle in the sky-pointing display,
drafted in card px (brief §H.18).

A male facing right, upright on the wire: bill pointed at the sky (72 deg
above the horizon), crown flat and running straight into the culmen, neck
stretched, body nearly upright and sleeked, the folded wing lying along the
back with the primaries projecting onto the tail, and the long graduated tail
folded into its V and hanging as a tall keel (the lower body and tail hang
in front of the wire, as a displaying bird's do below its perch).

Every outline is a G1 chain of circular arcs (biarcs) through drafted key
points; each point's tangent is the tangent of the circle through it and its
two neighbours (convex runs never wobble) unless pinned. Coordinates are card
px (y down); headings are screen degrees (0 = +x, 90 = down).

Anatomy (research/refs/jokers/grackle_*, looked at, never traced): flat crown
and culmen in one line; bill a little longer than the head, deep at the base,
culmen gently decurved to a sharp tip; pale eye above and behind the gape
corner; thick neck; slim body; folded wing with the primaries past the rump;
long graduated tail folded into a V -- seen from the side a deep blade whose
ventral edge is the keel (the long central pair) and whose end steps back,
feather by feather, to the short outer pair on the dorsal edge; long bare
tarsi, big feet.
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
# head (u forward along the bill, v toward the throat)
# ---------------------------------------------------------------------------
BILL_DEG = -76.0
HEAD = Frame((437.0, 190.0), BILL_DEG)
BILL_LEN = 72.0
BILL_TIP = HEAD(BILL_LEN, 0.4)
EYE_C = HEAD(-22.0, -5.5)
EYE_R = 7.2                      # iris (gold) outer radius
PUPIL_D = 6.3
CALL_C = HEAD(-30.0, 0.0)        # centre the call rays radiate from

# body frame: u along the body axis toward the neck, v toward the belly
BODY = Frame((388.0, 394.0), -60.0)

BODY_PTS = [
    HEAD(-1.0, -11.4),           # 0 culmen base (forehead feathering)
    HEAD(-19.0, -18.4),          # 1 forehead
    HEAD(-39.0, -22.6),          # 2 flat crown
    HEAD(-58.0, -24.0),          # 3 occiput
    HEAD(-78.0, -22.6),          # 4 nape
    BODY(100.0, -34.0),          # 5 hindneck (a shallow dip)
    BODY(62.0, -48.0),           # 6 mantle
    BODY(14.0, -52.5),           # 7 back
    BODY(-38.0, -48.0),          # 8 lower back
    BODY(-82.0, -32.0),          # 9 rump (tail base, dorsal)
    BODY(-100.0, 6.0),           # 10 under-tail coverts (tail base, keel)
    BODY(-78.0, 34.0),           # 11 vent
    BODY(-30.0, 50.0),           # 12 belly
    BODY(28.0, 52.0),            # 13 breast
    BODY(80.0, 40.0),            # 14 upper breast
    HEAD(-82.0, 32.0),           # 15 foreneck
    HEAD(-49.0, 27.0),           # 16 throat
    HEAD(-23.0, 20.6),           # 17 chin
    HEAD(-1.0, 11.2),            # 18 chin at the bill base
]
BODY_PINS = {0: HEAD.head(180.0 + 12.0), len(BODY_PTS) - 1: HEAD.head(6.0)}


def body_d():
    return closed_spline(BODY_PTS, BODY_PINS)


def bill_d():
    """Upper mandible: culmen gently decurved to a sharp tip; lower mandible:
    gonys nearly straight. Closed shape (the gape is knocked out)."""
    L = BILL_LEN
    top, _ = open_spline([HEAD(-4.0, -10.6), HEAD(L * 0.45, -6.8), BILL_TIP],
                         HEAD.head(-3.0), HEAD.head(13.0))
    bot, _ = open_spline([BILL_TIP, HEAD(L * 0.5, 5.6), HEAD(-4.0, 10.8)],
                         HEAD.head(180.0 - 8.0), HEAD.head(180.0 + 2.0))
    return top + bot.replace("M", "L", 1) + "Z"


def gape_d():
    """Commissure: from the gape corner (below the eye) toward the tip."""
    d, _ = open_spline([HEAD(-13.0, 2.4), HEAD(4.0, 1.3), HEAD(BILL_LEN * 0.52, 0.5)])
    return d


# ---------------------------------------------------------------------------
# tail: the keel (u along the tail, v toward the keel -- right / down)
# ---------------------------------------------------------------------------
TAIL_DEG = 110.0
TAIL = Frame(BODY(-88.0, -12.0), TAIL_DEG, vsign=-1.0)          # +v = keel side
N_RECT = 3                         # rectrices shown on the near arm of the V
TAIL_TOP = (-23.0, -35.0)          # dorsal edge v at base / end
TAIL_KEEL = (24.0, 46.0)           # keel edge v at base / end
TAIL_U_TOP, TAIL_U_KEEL = 118.0, 174.0      # graduated: outer pair short, central pair long
TAIL_BOW = 9.0                     # the keel edge bows (convex) toward the keel


def tail_v(k, u):
    """v of feather boundary k (0 = dorsal edge ... N_RECT = keel) at u."""
    t = k / N_RECT
    v0 = TAIL_TOP[0] + (TAIL_KEEL[0] - TAIL_TOP[0]) * t
    v1 = TAIL_TOP[1] + (TAIL_KEEL[1] - TAIL_TOP[1]) * t
    x = min(max(u / TAIL_U_KEEL, 0.0), 1.1)
    e = x ** 1.2
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


def tail_boundary(k, u0=-20.0, u1=None):
    """The part of boundary k between tail-u ``u0`` and ``u1`` (its end)."""
    pts, us = _boundary_curve(k)
    u1 = tail_end_u(k) if u1 is None else u1
    m = (us >= u0) & (us <= u1)
    out = pts[m]
    a = np.array([np.interp(u0, us, pts[:, 0]), np.interp(u0, us, pts[:, 1])])
    return np.vstack([a, out]) if u0 > us[0] else out


TIP_SAG = 7.0


def _tip_arc(p, q):
    from deck.motifs.forms import scallop_arc
    ch = q - p
    left = np.array([ch[1], -ch[0]])
    sg = TIP_SAG if left @ TAIL.U > 0 else -TIP_SAG
    return scallop_arc(p, q, sg, move=False)


def rectrix_d(i, u0=-40.0):
    """Closed outline of rectrix i (between boundaries i and i+1): its dorsal
    edge, the round tip arc, back along its keel-side edge."""
    a = tail_boundary(i, u0=u0)
    d = "M" + "L".join(f"{x:.3f} {y:.3f}" for x, y in a)
    p = a[-1]
    q = tail_boundary(i + 1)[-1]
    d += _tip_arc(p, q)
    d += "".join(f"L{x:.3f} {y:.3f}" for x, y in tail_boundary(i + 1, u0=u0)[::-1])
    return d + "Z"


def tail_outline_d():
    """Dorsal edge -> stepped round feather tips -> keel edge -> back to base."""
    top = tail_boundary(0)
    d = "M" + "L".join(f"{x:.3f} {y:.3f}" for x, y in top)
    for i in range(N_RECT):
        d += _tip_arc(tail_boundary(i)[-1], tail_boundary(i + 1)[-1])
    keel = tail_boundary(N_RECT)[::-1]
    d += "".join(f"L{x:.3f} {y:.3f}" for x, y in keel)
    return d + "Z"


# ---------------------------------------------------------------------------
# folded wing (u from the wrist toward the tip, v toward the lower edge)
# ---------------------------------------------------------------------------
WING_DEG = 120.0
WING = Frame(BODY(74.0, -2.0), WING_DEG, vsign=-1.0)    # origin at the wrist; +v = lower (belly) edge
WING_LEN = 228.0


# ---------------------------------------------------------------------------
# feet (x on the wire; the props module hangs them on it)
# ---------------------------------------------------------------------------
FOOT_N = np.array([458.0, 0.0])        # near foot, stepping forward
FOOT_F = np.array([413.0, 0.0])        # far foot
