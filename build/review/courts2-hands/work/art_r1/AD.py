"""art/AD.py: A♦ · The Ford (brief §H.16).

A Gill Red concave diamond (u 280, 224 × 314) with an eight-point compass
rose knocked out to paper in MEDIUM line:

* the cardinal star: N/S/E/W points whose paper tips stop 18 px short of
  the diamond's tips (the miter reach is solved for, not guessed), waists
  on the diagonals at r 28 (slim, so the diagonal star shows);
* the diagonal star BEHIND it, 60 % long (of the mean cardinal): each
  diagonal point is the visible arm of a second 4-point star (waists on the
  cardinal axes, r 26), so its edges emerge from the cardinal edges;
* every point a split lozenge: its axis runs from the hub (the diagonal
  axes continue the cardinal star's valley lines), and ONE half — the
  clockwise half, the same on all eight, so the rose turns — is hatched
  in MEDIUM paper lines at a 7 px pitch (3.9 px of red between them): at
  45° to the axis on the long cardinal points (the brief's blade angle),
  square across the axis on the short diagonals (a 45° line would be a
  stub there); hatch lines that would leave a red island under 3.2 px, or
  that are shorter than 10 px, are dropped (the hatching stops short of
  the tip, as an engraver's would);
* the axis lines stop short of each tip so every point ends in one clean
  wedge (no three-line knot); a small vent circle at the hub.
No arrows, no fleur, no N: a rose, not a map pin (§H.16 must-avoid).

Outside, in gold FINE line ("The Crossing"), both passing BEHIND the
diamond (broken 4.2 px clear of the keyline):
* a triple wave-line river, x 165–585, crossing at the diamond's centre:
  three in-phase waves (λ 50, amplitude 6, 12 px apart: 7.5 px clear at
  the steepest slope), the outer two half a wave shorter so each bank
  tapers into the plain; every line ends on a node in a Ø6.3 terminal
  (§B.2 free end) and passes behind the keyline at its other end;
* the road, a dotted line on the vertical axis, y 200–720, whole 6/6 dashes
  (each run starts with a whole dash at its outer end).
The diamond sits exactly at the ford: road and river cross at (375, 470).
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import Polygon

from deck import tokens as T
from deck import motifs as M
from deck.cardsvg import layers_merge
from inkkit import geom as G

from art import _aces_common as A

SUIT = "D"
W = A.KO
C = np.array([A.CX, A.CY], float)
X0, Y0, X1, Y1 = G.bbox(A.pip_d(SUIT))           # 263, 313.2, 487, 626.8
TIP_GAP = 18.0                                   # §H.16: N/S/E/W to within 18 px of the tips
R_WAIST = 33.0                                   # cardinal star waist (on the diagonals)
DIAG = 0.60                                      # §H.16: diagonals 60 % long
DIAG_WAIST = 30.0                                # diagonal star waist (on the cardinal axes)
HUB_R, HUB_DOT = 11.0, 6.3                       # the vent circle at the hub
HATCH_TURN = 45.0                                # hatch angle relative to each point's axis
DIAG_HATCH_TURN = 90.0                           # ... on the short diagonals: rungs across the half
AXIS_END_RED = 3.2                               # red kept either side of an axis line's end
HATCH_MIN = 10.0                                 # shorter hatch lines are dropped (a stub is not tone:
                                                 # at 6 the tip-most rung left a red pill by each tip)
CARD = (-90.0, 0.0, 90.0, 180.0)                 # N, E, S, W (screen degrees)
NEXT = {-90.0: 0.0, 0.0: 90.0, 90.0: 180.0, 180.0: -90.0}

RIVER_X = (165.0, 585.0)                         # §H.16
RIVER_PITCH, RIVER_AMP, RIVER_LAMBDA = 12.0, 6.0, 50.0
ROAD_Y = (200.0, 720.0)                          # §H.16, dashes 6/6


def u(a: float) -> np.ndarray:
    return A.unit(a)


def cardinal_lengths() -> dict:
    """Axis length of each cardinal point such that the paper tip (vertex +
    miter reach of the MEDIUM outline) is exactly TIP_GAP short of the tip."""
    reach = {-90.0: C[1] - Y0, 0.0: X1 - C[0], 90.0: Y1 - C[1], 180.0: C[0] - X0}
    out = {}
    for a, R in reach.items():
        L = R - TIP_GAP
        for _ in range(12):
            tip = C + u(a) * L
            L = R - TIP_GAP - A.miter_reach(tip, C + u(a - 45) * R_WAIST, C + u(a + 45) * R_WAIST)
        out[a] = L
    return out


def _axis_stop(tip, axis_deg, other) -> float:
    """How far short of ``tip`` an axis line must end so the red on either
    side of its (round) end stays >= AXIS_END_RED wide."""
    ax = u(axis_deg)
    e = np.asarray(other, float) - tip
    e = e / np.linalg.norm(e)
    half = math.asin(abs(A.cross2(ax, e)))
    return (W + AXIS_END_RED) / math.tan(half)


def compass() -> M.Frag:
    Ls = cardinal_lengths()
    tips = {a: C + u(a) * Ls[a] for a in CARD}
    waists = {a: C + u(a + 45) * R_WAIST for a in CARD}      # the waist clockwise of each cardinal
    ring = []
    for a in CARD:
        ring += [tips[a], waists[a]]
    star = M.stroke(M.polyline_d(ring, closed=True), W, style="point", role="point")

    axes = M.Frag()
    for a in CARD:
        stop = _axis_stop(tips[a], a, waists[a])
        axes += M.stroke(M.polyline_d([C, tips[a] - u(a) * stop]), W, style="point", role="axis")

    # the diagonal star, behind: tip at 60 %, waists on the cardinal axes
    Ld = DIAG * float(np.mean(list(Ls.values())))
    diag = M.Frag()
    dhalf = {}
    for a in CARD:
        ad = a + 45.0
        dt = C + u(ad) * Ld
        w_ccw = C + u(a) * DIAG_WAIST                  # diagonal waist on the cardinal a
        w_cw = C + u(NEXT[a]) * DIAG_WAIST             # ... and on the next cardinal
        # where the diagonal's edges emerge from behind the cardinal edges
        p_ccw = A.line_x(dt, w_ccw, waists[a], tips[a])
        p_cw = A.line_x(dt, w_cw, waists[a], tips[NEXT[a]])
        diag += M.stroke(M.polyline_d([p_ccw, dt, p_cw]), W, style="point", role="point")
        stop = _axis_stop(dt, ad, p_cw)
        # the valley line of the cardinal star runs on as the diagonal's axis
        diag += M.stroke(M.polyline_d([C, dt - u(ad) * stop]), W, style="point", role="axis")
        dhalf[a] = Polygon([waists[a], dt, p_cw])       # its clockwise half

    lines = star + axes + diag
    hatch = M.Frag()
    for a in CARD:
        hatch += A.ko_hatch(Polygon([C, tips[a], waists[a]]), a + HATCH_TURN,
                            boundary=lines, origin=tuple(C), min_len=HATCH_MIN)
        hatch += A.ko_hatch(dhalf[a], a + 45.0 + DIAG_HATCH_TURN, boundary=lines, origin=tuple(C),
                            min_len=HATCH_MIN)
    rose = lines + hatch
    hub = M.stroke(M.circle_d(*C, HUB_R), W, role="hub") + M.dot(*C, HUB_DOT)
    return M.clip(rose, M.circle_d(*C, HUB_R), inside=False) + hub


def river() -> M.Frag:
    """Three in-phase wave lines; the outer two half a wave shorter; each
    run starts on a node at its outer end."""
    f = M.Frag()
    for dy in (-RIVER_PITCH, 0.0, RIVER_PITCH):
        short = RIVER_LAMBDA / 2 if dy else 0.0
        for sgn in (-1.0, 1.0):
            x_node = A.CX + sgn * (A.CX - RIVER_X[0])          # common phase: all in step
            x_out = A.CX + sgn * (A.CX - RIVER_X[0] - short)
            xs = np.linspace(x_out, A.CX, 1800)
            ys = A.CY + dy - RIVER_AMP * np.sin(2 * math.pi * np.abs(xs - x_node) / RIVER_LAMBDA)
            f += M.stroke(np.c_[xs, ys], T.FINE, color=T.FOIL, role="river")
            f += M.terminal(xs[0], ys[0], color=T.FOIL)          # §B.2: a free end takes a Ø6.3 terminal
    return f


def road() -> M.Frag:
    runs = A.dash_run(ROAD_Y[0], A.CY, A.CX) + A.dash_run(ROAD_Y[1], A.CY, A.CX)
    return M.stroke(runs, T.FINE, style="rule", color=T.FOIL, role="road")


def crossing() -> M.Frag:
    """River and road, behind the diamond; a road dash the cut would shorten
    below its 6 px is dropped whole."""
    f = A.behind(river(), SUIT)
    rd = M.cut(road(), A.keyline_zone(SUIT), A.CLEAR)
    return f + A.drop_short(rd, 5.9)


def build():
    pip = A.knocked_pip(SUIT, compass(), color=T.RED)
    gold = A.keyline(SUIT) + crossing() + A.caption(SUIT)
    return layers_merge((pip + gold).fragments())
