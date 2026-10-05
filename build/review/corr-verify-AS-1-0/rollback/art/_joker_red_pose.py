"""JOKER_RED pose: the pig volant in a swine dive, drafted in card px
(brief §H.17; director's pass-2 decision: a SOLID Gill Red silhouette).

Breed: a Tamworth-type bacon pig (the red, prick-eared, long-snouted English
breed) -- a long level back, a deep round barrel with the flank tucked up
before a full ham, short jointed legs, a long straight head ending in a flat
disc, big prick ears (here laid back by the fall), a curled tail.  Seen from
his near (left) side, facing right.

The dive (research/refs/jokers/pig_dive_flickr_*.jpg -- show pigs leaving the
tower; pig_tamworth_*.jpg; boar_heraldic_*.png for the heraldic volant legs;
looked at, never traced): the body pitches head-down at 58 deg, the back one
convex arc (~46 deg at the rump, ~64 at the shoulders); the head is carried a
little higher (~53 deg) so the face stays in profile with the snout leading
the plunge; both fore trotters reach forward under the jaw, the near one
leading and the far one a step behind; the hind legs trail together behind
the ham (thigh back and down, the hock's point proud on the dorsal side, the
cannon back, the trotter pointed); the ears lie back along the neck; the tail
curls up clear of the croup.

Drafting (as in the Little Joker's pose module): everything is drawn in a
bent BODY frame -- u runs forward along the spine arc (arclength), v toward
the belly -- and a straight HEAD frame hung on it at the poll.  Outlines are
G1 chains of circular arcs through the key points below; legs are chains of
joint circles joined by common tangents, ending in trotters with a V cleft
cut between the claws.

Placement against the porthole: the ring's rump-side half crosses the loin as
two gold wires with the red loin showing between them, so the barrel runs on
through the ring into the ham (its thigh line just beyond the outer wire), the
hind legs and the tail; inside the porthole the barrel carries the shoulder
line and the half-hatched belly crescent; the head, collar and forelegs break
out over the ring's lower right.

Proportions (drafting units at S = 1.12, the head at 1.1 x that): barrel
depth D ~ 136; buttock to throat ~1.9 D; head, poll to disc, ~0.83 D; ear
~0.57 D; legs ~0.3 D at the elbow and thigh, ~0.1 D at the pastern.

Lessons from the drafts (build/review/JOKER_RED-2-progress.md and
JOKER_RED-2-critique.md): a collar on a wide paper ground severs the head --
keep only a thin moat round the gold; a ring face across a straight-sided
barrel reads as a bucket -- tuck the flank and bow the belly; a solid paper
ring face (~34 px) across the loin splits the pig in two (the rump reads as a
second small animal) -- let the red run on between the two wires; a broad
hatched belly lens reads as a folded wing or a shell -- keep the belly's
shading to a narrow crescent; a hind leg whose hock
bends the wrong way reads as a waving arm, splayed hind legs as a frog kick;
a head pointing straight down reads as a cow's face seen from the front.
"""
from __future__ import annotations

import math

import numpy as np

from deck.motifs import forms


def unit(h):
    a = math.radians(h)
    return np.array([math.cos(a), math.sin(a)])


class Frame:
    """Drafting frame: origin ``o``; +u along heading ``h``; +v 90 deg
    clockwise of +u (``vsign`` = -1 flips it)."""

    def __init__(self, o, h, vsign=1.0, s=1.0):
        self.o = np.asarray(o, float)
        self.h = float(h)
        self.U = unit(h)
        self.V = unit(h + 90.0) * vsign
        self.vs = vsign
        self.s = float(s)

    def __call__(self, u, v=0.0):
        return self.o + (self.U * u + self.V * v) * self.s

    def pts(self, uv):
        return [self(u, v) for u, v in uv]

    def head(self, deg, u=0.0):
        """Card heading of a local heading ``deg`` (0 = +u, 90 = +v)."""
        return self.h + self.vs * deg

    def local(self, p):
        d = np.asarray(p, float) - self.o
        return np.array([d @ self.U, d @ self.V]) / self.s

    def sub(self, uv, dh, vsign=1.0):
        """A child frame at local point ``uv`` turned ``dh`` deg (+ = ventral)."""
        return Frame(self(*uv), self.head(dh), vsign * self.vs, self.s)


class BendFrame:
    """The body's frame bent along the dive: the spine is a circular arc of
    radius ``R`` (page px) through ``o`` with heading ``h`` there, curving
    toward the belly (+v) -- the back convex, the streamlined arc of a
    diver.  u is arclength along the spine, v the offset toward the belly."""

    def __init__(self, o, h, R, s=1.0):
        self.o = np.asarray(o, float)
        self.h = float(h)
        self.R = float(R)
        self.s = float(s)
        self.U = unit(h)
        self.V = unit(h + 90.0)
        self.c = self.o + self.V * self.R
        self.vs = 1.0

    def _phi(self, u):
        return u * self.s / self.R

    def __call__(self, u, v=0.0):
        a = self._phi(u)
        ca, sa = math.cos(a), math.sin(a)
        w = -self.V
        rw = np.array([ca * w[0] - sa * w[1], sa * w[0] + ca * w[1]])
        return self.c + rw * (self.R - v * self.s)

    def pts(self, uv):
        return [self(u, v) for u, v in uv]

    def head(self, deg, u=0.0):
        """Card heading of the local heading ``deg`` at spine station ``u``."""
        return self.h + math.degrees(self._phi(u)) + deg

    def sub(self, uv, dh, vsign=1.0):
        return Frame(self(*uv), self.head(dh, uv[0]), vsign, self.s)

    def local(self, p):
        d = np.asarray(p, float) - self.c
        r = float(np.hypot(*d))
        w = -self.V
        a = math.atan2(w[0] * d[1] - w[1] * d[0], w @ d)
        return np.array([a * self.R / self.s, (self.R - r) / self.s])


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
    return d, np.asarray(P)


# ---------------------------------------------------------------------------
# placement
# ---------------------------------------------------------------------------
HB = 58.0                          # body heading at mid-barrel (screen deg): down-right
BODY_O = (352.0, 306.0)            # mid-barrel (u 0, v 0)
DIVE_R = 700.0                     # spine arc radius: the back convex
S = 1.12                           # drafting scale (positions and radii; never a stroke)
BODY = BendFrame(BODY_O, HB, DIVE_R, s=S)

# ---------------------------------------------------------------------------
# torso (BODY: u forward, v ventral), from the neck crest back along the
# back, round the rump and ham, forward along the belly to the throat
# ---------------------------------------------------------------------------
TORSO = [
    (98, -44),       # 0  neck crest (under the ear)
    (62, -57),       # 1  withers
    (16, -64),       # 2  back
    (-30, -62),      # 3  back
    (-72, -54),      # 4  loin (a little dip before the croup)
    (-106, -50),     # 5  croup (tail set)
    (-136, -30),     # 6  rump
    (-150, 2),       # 7  buttock
    (-146, 32),      # 8  ham, behind
    (-128, 54),      # 9  ham, below (the leg leaves it)
    (-102, 50),      # 10 stifle / flank fold (tucked up)
    (-66, 58),       # 11 flank
    (-16, 72),       # 12 belly (round)
    (36, 70),        # 13 chest floor
    (82, 48),        # 14 brisket
    (104, 18),       # 15 throat
    (106, -16),      # 16 neck, under the jowl
]

# ---------------------------------------------------------------------------
# head: origin at the poll, carried a little higher than the body's front
# ---------------------------------------------------------------------------
HEAD_AT = (96.0, -42.0)            # the poll (BODY)
HEAD_FLEX = -14.0                  # deg (+ ventral): the head carried a little high
HEAD_SCALE = 1.1                   # the head drawn a little large (heraldic emphasis)
HEAD = Frame(BODY(*HEAD_AT), BODY.head(HEAD_FLEX, HEAD_AT[0]), 1.0, S * HEAD_SCALE)

HEAD_PTS = [
    (0, 0),          # 0  poll
    (22, 3),         # 1  forehead
    (48, 9),         # 2  face (a slight dish)
    (74, 15),        # 3  snout
    (92, 17),        # 4  snout at the disc (top)
    (93, 45),        # 5  under the snout at the disc
    (82, 48),        # 6  upper lip (the disc overhangs the mouth)
    (66, 55),        # 7  chin, set back
    (44, 67),        # 8  jaw
    (18, 84),        # 9  jowl
    (-8, 92),        # 10 throat
    (-30, 50),       # 11 (inside the neck)
    (-20, 8),        # 12 (inside the neck)
]
DISC_C = (95.0, 31.0)              # the disc, turned a little to us (HEAD)
DISC_R = (7.0, 17.0)               # semi-axes along / across the snout
NOSTRILS = [(96.5, 25.5), (96.5, 36.5)]
NOSTRIL_R = (2.1, 3.2)
EYE_C = (34.0, 22.0)
EYE_L, EYE_H = 17.0, 10.4
EYE_DOT = 6.3

# ear (HEAD): base rear, base front, tip -- a broad triangle laid back
EAR = dict(rear=(-6.0, 1.0), front=(26.0, 5.0), tip=(-60.0, -38.0), front_sag=17.0, rear_sag=9.0)

# ---------------------------------------------------------------------------
# legs: joint circles (u, v, r) in BODY, root -> fetlock; then the trotter
# (heading in BODY degrees at the last joint, length)
# ---------------------------------------------------------------------------
FORE_NEAR = [(60, 38, 20), (80, 60, 14), (124, 58, 9.5), (158, 48, 7.5)]
FORE_NEAR_HOOF = (-16.0, 24.0)
FORE_FAR = [(52, 42, 19), (70, 66, 13), (110, 76, 9.5), (142, 70, 7.5)]
FORE_FAR_HOOF = (-12.0, 23.0)
HIND_NEAR = [(-116, 22, 22), (-138, 38, 13), (-172, 20, 8.5), (-200, 20, 6.5)]
HIND_NEAR_HOOF = (190.0, 23.0)
HIND_FAR = [(-110, 30, 20), (-130, 50, 12), (-162, 38, 8.0), (-190, 40, 6.5)]
HIND_FAR_HOOF = (186.0, 22.0)
HOOF_NOTCH = (0.56, 0.20)          # the cleft's apex (x / L, y / r) in the trotter frame
HOOF_CLEFT_W = 0.85                # the cleft's half-spread at x = 1.4 L (x r)
HOCKS = {"hind_near": 2, "hind_far": 2}

# tail: root on the croup (BODY), heading, then a curl turning away from the rump
TAIL_ROOT = (-122, -38)
TAIL_H0 = 200.0
TAIL_W = 5.2
TAIL_CURL = [(12.0, None), (12.0, 250.0), (7.0, 170.0)]
TAIL_OVER = 20.0
TAIL_GAP = 3.2

# ---------------------------------------------------------------------------
# knockout lines (paper, MEDIUM): frame, points, open ends ("0", "1", "")
# ---------------------------------------------------------------------------
KO_LINES = {
    # shoulder: from behind the withers, round behind the shoulder blade and
    # upper arm, forward to the elbow
    "shoulder": ("BODY", [(30, -50), (22, -22), (26, 8), (42, 34)], ""),
    # ham: the thigh's front, from the stifle fold up and back toward the hip
    # (beyond the ring's outer wire, bowing toward the head against its arc)
    "ham": ("BODY", [(-113, 44), (-115, 22), (-123, 4), (-136, -10)], ""),
    # mouth: from under the disc back toward the eye
    "mouth": ("HEAD", [(83, 40.5), (66, 47.0), (46, 57.0)], ""),
}
# the belly crescent: a narrow half-hatched window along the belly edge (the
# barrel's shaded underside), from the flank inside the ring to the chest
# floor, at most BELLY_W px wide and tapering to both ends, hatched at
# BELLY_HATCH (BODY deg, 45 to the axis)
BELLY_SPAN = (-58.0, 36.0)         # BODY u, flank -> chest floor
BELLY_W = 12.5                     # px, the crescent's width at its middle
BELLY_TAPER = 0.7                  # width profile: sin(pi t) ** BELLY_TAPER
BELLY_HATCH = 45.0

# ---------------------------------------------------------------------------
# the jester collar (gold): a band round the neck behind the jowl, five
# broad dags fanned toward the head, a bell at each point.  Gold never
# touches red (§C rule 4): every gold shape sits in a thin paper moat cut
# from the solid, and the red neck runs on between the dags.
# ---------------------------------------------------------------------------
COLLAR = [(-34.0, -14.0), (-26.0, 46.0), (-24.0, 106.0)]   # band centreline (HEAD), dorsal -> ventral
COLLAR_W = 7.0                     # band width (px)
DAG_N = 5
DAG_BASE = 0.80                    # dag base width / dag spacing
DAG_L = 24.0                       # dag length beyond the band's edge (px)
DAG_FAN = 22.0                     # the outer dags fan out this far (deg)
BELL_D = 10.0                      # bell diameter (px)
COLLAR_CLOSE = 4.0                 # the paper ground closes the V's between dags near the band
COLLAR_CRUMB = 400.0               # red islands smaller than this (px^2) inside the collar are paper
