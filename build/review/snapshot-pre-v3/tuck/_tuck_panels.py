"""TUCK sides and end flaps (brief §H.20 "Sides", "End flaps", §J.2 copy).

Every panel is authored in its own local frame (0, 0 = its top-left fold
corner, y down) with the box standing upright; ``_tuck_flat`` places them.

SIDE A (225 × 1069)  HEADWATERS · LONG MAY IT FLOW — Barlow Condensed Medium,
    cap 18, +250, set vertically (reading bottom to top) between running-wave
    bands; the line is carried to the bands by a FINE stem ending in rising
    bubble beading (§G.9) — water rising through the side of the box.
SIDE B (225 × 1069)  SEVENTY-TWO DEGREES · EVERY DAY OF THE YEAR, then the
    acknowledgment THE SPRINGS HAVE BEEN CARED FOR BY INDIGENOUS PEOPLES FOR
    MORE THAN 12,000 YEARS (Barlow Condensed Medium cap 18, broken over three
    lines, words and order verbatim).  Words only: no imagery, no
    Indigenous-language text.  **HOLD for Indigenous Cultures Institute review
    before print** — carried as a NON-PRINTING note (``hold_note``).
TOP END (769 × 225)  SAN MARVELOUS (cap 14, +250) with a 40 px diving pig
    drawn at final size (the Easter egg; the seal covers the middle of this
    flap, so the pig sits at the line's end, found when the box is opened).
BOTTOM END (769 × 225)  one OUTLINE-ONLY San Marcos gambusia (no hatch, no
    fill: the ghost fish) above GAMBUSIA GEORGEI · LAST SEEN 1983.

All four share the box border (outer RULE at 34 + FINE companion at 42 from
the folds, as the front and back) so the frame reads continuously round the
box.  One gold foil; the ground is flat board (no emboss on these panels).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import Point, box

from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms as FM
from deck.motifs import geometric as M
from inkkit import geom as G

from tuck import _tuck_common as K

FOIL = K.FOIL
FINE, HAIR, RULE = K.FINE, K.HAIR, K.RULE
GAP = K.GAP
D = K.DEPTH                    # 225
PW, PH = K.PW, K.PH

OUTER, COMPANION = K.FRAME_OUTER, K.FRAME_COMPANION
BAND = 34.0                    # running-wave band depth (as the front / back)

SIDE_A = "HEADWATERS · LONG MAY IT FLOW"
SIDE_B1 = "SEVENTY-TWO DEGREES · EVERY DAY OF THE YEAR"
SIDE_B_ACK = ("THE SPRINGS HAVE BEEN CARED FOR", "BY INDIGENOUS PEOPLES", "FOR MORE THAN 12,000 YEARS")
TOP_LINE = "SAN MARVELOUS"
BOTTOM_LINE = "GAMBUSIA GEORGEI · LAST SEEN 1983"
HOLD_NOTE = ("HOLD - DO NOT PRINT SIDE B ACKNOWLEDGMENT UNTIL REVIEWED AND APPROVED BY THE "
             "INDIGENOUS CULTURES INSTITUTE (SAN MARCOS)")


# =============================================================================
# shared
# =============================================================================
def border(w: float, h: float) -> C.Frag:
    f = C.Frag()
    for inset, sw in ((OUTER, RULE), (COMPANION, FINE)):
        f += C.stroke(K.rect_lines(inset, inset, w - inset, h - inset), sw, style="rule", color=FOIL, role="rule")
    return f


def wave_band(w: float, y_rule: float, *, up: int = -1) -> C.Frag:
    """A running-wave band across a narrow panel: the band's inner rule at
    ``y_rule`` (FINE, companion to companion) and §G.7 waves springing from it,
    mirrored at the axis and flowing OUTWARD from a Ø6.3 bubble on the axis."""
    cx = w / 2
    x0, x1 = COMPANION, w - COMPANION
    f = C.stroke(C.polyline_d([(x0, y_rule), (x1, y_rule)]), FINE, style="rule", color=FOIL, role="rule")
    height = 18.0
    hook = M.wave_hook(height, color=FOIL)
    wd = hook.meta["wave_width"]
    gap = 9.0
    pitch = 28.0
    half = (x1 - x0) / 2 - FINE / 2 - GAP
    n = int((half - gap - wd) // pitch) + 1
    right = M.running_wave(cx + gap, cx + gap + (n - 1) * pitch + wd, y_rule, height=height, pitch=pitch, flow=1,
                           up=up, rule=False, start=cx + gap, color=FOIL)
    f += right + right.mirror_x(cx)
    ymid = y_rule + up * height * 0.62
    f += C.dot(cx, ymid, 6.3, color=FOIL, role="bubble")
    return f


def vtext(text: str, cap: float, x_mid: float, y_mid: float, tracking: float, *, font=K.FONT_SIDE, rules=False,
          rot: float = -90.0):
    """Type set along the vertical: built horizontally (cap middle on y = 0,
    centred on x = 0), then rotated ``rot`` (-90 reads bottom to top) and
    moved so its cap middle runs along x = x_mid, centred on y_mid.
    -> (Frag, bbox (in panel coords))."""
    f, bb = K.type_fill(text, cap, cap / 2, tracking, 0.0, font=font)
    if rules:
        f += K.em_rules(bb, cap)
    f = f.rotate(rot, 0.0, 0.0).translate(x_mid, y_mid)
    return f, f.bbox()


# =============================================================================
# SIDE A
# =============================================================================
def side_a():
    w, h = D, PH
    cx, cy = w / 2, h / 2
    f = border(w, h)
    top_rule = COMPANION + BAND
    f += wave_band(w, top_rule, up=-1)
    f += wave_band(w, h - top_rule, up=1)
    t, bb = vtext(SIDE_A, 18.0, cx, cy, 250.0)
    f += t
    # em-rules (vertical, FINE 24 long, 10 from the ink) + a stem to the bands with rising bubbles
    y0, y1 = bb[1], bb[3]
    f += C.stroke(C.polyline_d([(cx, y0 - 10), (cx, y0 - 34)]) + C.polyline_d([(cx, y1 + 10), (cx, y1 + 34)]),
                  FINE, style="rule", color=FOIL, role="emrule")
    f += _stem(cx, y0 - 34 - 14, top_rule + 30, rise=-1)
    f += _stem(cx, y1 + 34 + 14, h - top_rule - 30, rise=-1)
    return f


def _stem(x, y_from, y_to, *, rise=-1):
    """Bubble beading (§G.9) from y_from toward y_to, growing ×1.2 in the
    direction of rise (up the box, -y)."""
    n = 6
    if rise < 0:
        lo, hi = max(y_from, y_to), min(y_from, y_to)
        return M.bubble_beading((x, lo), (x, hi), 4.2, n=n, d_max=8.4, color=FOIL)
    lo, hi = min(y_from, y_to), max(y_from, y_to)
    return M.bubble_beading((x, lo), (x, hi), 4.2, n=n, d_max=8.4, color=FOIL)


# =============================================================================
# SIDE B
# =============================================================================
B_PITCH = 30.0           # line pitch across the panel (cap 18 + 12 px)
B_SEP = 14.0             # extra space between the statement and the acknowledgment


def side_b():
    """-> (foil Frag, acknowledgment region (panel coords) for the hold note)."""
    w, h = D, PH
    cx, cy = w / 2, h / 2
    f = border(w, h)
    top_rule = COMPANION + BAND
    f += wave_band(w, top_rule, up=-1)
    f += wave_band(w, h - top_rule, up=1)
    # columns (cap-middle x) across the width, reading bottom-to-top: the statement first (leftmost)
    xs = [0.0, B_PITCH + B_SEP, 2 * B_PITCH + B_SEP, 3 * B_PITCH + B_SEP]
    off = cx - (xs[0] + xs[-1]) / 2
    xs = [x + off for x in xs]
    t, bb = vtext(SIDE_B1, 18.0, xs[0], cy, 200.0)
    f += t
    ack = C.Frag()
    for x, line in zip(xs[1:], SIDE_B_ACK):
        a, _ = vtext(line, 18.0, x, cy, 200.0)
        ack += a
    # a single FINE rule with terminals between the statement and the acknowledgment
    xr = (xs[0] + xs[1]) / 2
    ya, yb = bb[1] + 40, bb[3] - 40
    f += C.stroke(C.polyline_d([(xr, ya), (xr, yb)]), HAIR, style="rule", color=FOIL, role="sep")
    f += C.terminal(xr, ya, color=FOIL) + C.terminal(xr, yb, color=FOIL)
    abb = ack.bbox()
    return f + ack, abb


def hold_note_d(x_mid, y_mid, rot=-90.0):
    """The non-printing HOLD note (outlined, registration magenta, dieline plate)."""
    f, _ = vtext(HOLD_NOTE, 9.0, x_mid, y_mid, 100.0, font=K.FONT_MICRO, rot=rot)
    return f.outline()


# =============================================================================
# TOP END: SAN MARVELOUS + the diving pig
# =============================================================================
def pig(x: float, y: float, rot: float = -68.0) -> C.Frag:
    """A 40 px pig diving head-first (the Big Joker's fool, as an Easter egg),
    drawn at final size in FINE foil: a plump body-and-head contour ending
    in the flat disc of the snout, an ear laid back along the head, stubby
    trotters (fore tucked, hind trailing), a curl of tail and an eye dot.
    Authored facing LEFT (40 px long along x), then rotated so the snout
    points down at the water (``rot`` screen degrees; -68 = a steep dive to
    the lower left)."""
    S = lambda d, style="ornament": C.stroke(d, FINE, style=style, color=FOIL, role="pig")
    # one contour: snout top -> forehead -> back -> rump -> belly -> jaw -> snout bottom
    d_body = FM.arc_spline([(-18.4, -3.6), (-12.5, -7.0), (-3.0, -9.6), (7.0, -9.8), (15.0, -7.2),
                            (19.6, -1.2), (17.2, 5.8), (8.0, 9.2), (-3.0, 9.0), (-11.5, 6.2), (-18.4, 3.2)],
                           h_start=-28.0, h_end=160.0)[0]
    f = S(d_body)
    f += S(FM.arc_spline([(-18.4, -3.6), (-20.4, -0.2), (-18.4, 3.2)], h_start=150.0, h_end=30.0)[0])  # snout disc
    f += S(C.vesica_d((-8.6, -9.2), (0.8, -14.6), 4.6), style="point")                     # ear laid back
    f += S(C.polyline_d([(-6.0, 8.6), (-8.6, 13.6)]))                                    # fore trotter
    f += S(C.polyline_d([(10.0, 8.6), (13.0, 13.4)]))                                    # hind trotter
    t = C.Turtle(19.4, -3.2, -70.0)                                                      # the tail's curl
    t.arc(3.6, 210.0)
    f += S(t.d())
    f += C.dot(-9.6, -1.6, 4.2, color=FOIL, role="pig-eye")
    return f.rotate(rot, 0.0, 0.0).translate(x, y)


PIG_ROT = -68.0


def diving_pig(x, y, *, rx=15.0, ry=4.2, drop=7.5):
    """The pig diving at the spring: a flat §G.8 ripple ring ``drop`` px below
    its snout (the surface it is about to break) and two droplet dots thrown
    up beside it.  (x, y) = the pig's centre."""
    p = pig(x, y, PIG_ROT)
    a = math.radians(PIG_ROT)
    tx = x + (-20.4) * math.cos(a)
    ty = y + (-20.4) * math.sin(a)
    ex, ey = tx, ty + drop + ry
    f = p + C.stroke(C.ellipse_d(ex, ey, rx, ry), FINE, color=FOIL, role="ripple")
    for dx, dy in ((-rx - 1.5, -8.5), (rx + 3.5, -8.0)):
        f += C.dot(ex + dx, ey + dy, 4.2, color=FOIL, role="droplet")
    return f


def top_end():
    w, h = PW, D
    cx, cy = w / 2, h / 2
    f = border(w, h)
    t, bb = K.type_fill(TOP_LINE, 14.0, cy + 7.0, 250.0, cx)
    f += t + K.em_rules(bb, 14.0)
    # the pig beyond the right em-rule, diving into a small ripple on the line's axis
    x_rule_end = bb[2] + 10 + 24
    px = x_rule_end + 46.0
    f += diving_pig(px, cy - 12.0)
    return f


# =============================================================================
# BOTTOM END: the ghost gambusia
# =============================================================================
def gambusia(x: float, y: float, L: float = 150.0) -> C.Frag:
    """Gambusia georgei, outline only (§H.20 "no hatch, the ghost fish"):
    a small livebearer facing left — upturned mouth, large eye set high,
    straight back, rounded belly, the single dorsal set far back over the
    anal fin, a deep caudal peduncle and a rounded fan tail.  Authored at
    L = 150 (final size), FINE; no fill, no hatch, no stipple."""
    k = L / 150.0
    P = lambda pts: [(x + px * k, y + py * k) for px, py in pts]
    S = lambda d, style="ornament": C.stroke(d, FINE, style=style, color=FOIL, role="fish")
    f = C.Frag()
    # dorsal contour (snout -> peduncle top), ventral contour (chin -> peduncle bottom)
    back = P([(-74, -4.5), (-62, -11.5), (-40, -16.5), (-12, -18.5), (14, -17.2), (34, -12.6), (50, -9.4)])
    belly = P([(-72, 0.5), (-64, 8.5), (-44, 16.5), (-16, 19.5), (8, 17.8), (32, 11.6), (50, 8.6)])
    f += S(FM.arc_spline(back, h_start=-40.0)[0])
    f += S(FM.arc_spline(belly, h_start=55.0)[0])
    # upturned mouth: the lower jaw closing up onto the snout
    f += S(C.polyline_d(P([(-74, -4.5), (-76.5, -2.2), (-72, 0.5)])), style="point")
    f += S(C.polyline_d(P([(-76.5, -2.2), (-68.5, -1.2)])))
    # caudal fin: a rounded fan from the peduncle
    tail = P([(50, -9.4), (62, -19.5), (73, -13), (76.5, 0), (73, 13), (62, 19.5), (50, 8.6)])
    f += S(FM.arc_spline(tail, h_start=-40.0)[0])
    for py in (-8.0, 0.0, 8.0):      # three rays, outline art (not hatch), clear of the fin's edges
        f += S(C.polyline_d(P([(60.5, py * 0.82), (68.5, py * 1.2)])))
    # dorsal fin (set far back) and anal fin beneath it
    f += S(FM.arc_spline(P([(14, -17.2), (20, -29), (29, -28), (34, -12.6)]), h_start=-70.0)[0])
    f += S(FM.arc_spline(P([(2, 18.8), (10, 30), (18, 28.5), (20, 16.6)]), h_start=70.0)[0])
    # pectoral fin, gill cover, eye ring
    f += S(C.vesica_d(P([(-45, 3)])[0], P([(-28, 7)])[0], 7.5 * k), style="point")
    f += S(FM.arc_spline(P([(-49, -13.5), (-45, 0), (-49, 13.5)]))[0])
    f += C.stroke(C.circle_d(*P([(-60.5, -5.0)])[0], 5.6 * k), FINE, color=FOIL, role="fish-eye")
    return f


def bottom_end():
    w, h = PW, D
    cx, cy = w / 2, h / 2
    f = border(w, h)
    f += gambusia(cx, cy - 20.0)
    t, bb = K.type_fill(BOTTOM_LINE, 14.0, cy + 40.0, 250.0, cx)
    f += t + K.em_rules(bb, 14.0)
    return f


# =============================================================================
# assembly
# =============================================================================
def build():
    b, ack_bb = side_b()
    return dict(side_a=side_a(), side_b=b, top=top_end(), bottom=bottom_end(), ack_bb=ack_bb)


def panel_svg(name: str, f: C.Frag, w: float, h: float, *, dieline: str = "") -> str:
    notes = [f"HEADWATERS tuck {name}, {w:g} x {h:g} px @300 ppi, y down. One gold foil (flat #B08D57) on",
             "Deep Hole board; all type outlined."]
    return K.svg_doc(w, h, emboss=[], foil=K.foil_svg(f), title=f"HEADWATERS tuck {name}", notes=notes,
                     dieline=dieline)
