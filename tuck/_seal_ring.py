"""The seal's ring furniture — §H.20 "Seal", §B.1 (Ø330).

* ``die_d``        the 24-lobe ripple-scalloped die-cut edge (non-printing).
* ``rings``        the foil ring rules.
* ``legend``       NUSQUAM ALIBI arched over the top, SAN MARCOS · TEXAS under
                   the bottom (Barlow Condensed SemiBold, tracked caps, outlined
                   with inkkit.typeset.text_on_arc) — §J.2 copy, verbatim.
* ``bubble_strings``  the two separators: strings of rising bubbles (§G.9,
                   growing ×1.2 toward the top) at 3 and 9 o'clock.

All geometry is about the seal centre (cx, cy) and generated at final size.
"""
from __future__ import annotations

import math

import numpy as np

from inkkit import geom as G
from inkkit import typeset as TS

from deck import tokens as T
from deck.motifs.core import Frag, circle_d, dot, fill, stroke

# -----------------------------------------------------------------------------
# geometry table (px; the seal is Ø330 = 1.1 in at 300 ppi, §B.1)
# -----------------------------------------------------------------------------
R_PEAK = 165.0            # die-cut lobe crests (Ø330)
LOBES = 24                # §H.20 "24-lobe ripple-scalloped"
RIPPLE = 6.0              # crest-to-trough depth of the ripple (troughs at r 159)
R_OUTER_RULE = 146.0      # RULE ring: 10.9 px inside the die's troughs (registration margin)
R_TEXT = 130.0            # cap-middle radius of both legends
CAP = 16.0                # cap height of the legends (px): the brief's micro-type maximum, for the widest foil counters
TRACK_TOP = 250           # 1/1000 em
TRACK_BOTTOM = 250
R_INNER_RULE = 115.0      # FINE ring that closes the field

TOP_TEXT = "NUSQUAM ALIBI"            # §J.2 (seal)
BOTTOM_TEXT = "SAN MARCOS · TEXAS"    # §J.2 (tuck, seal)


def die_points(cx: float, cy: float, n: int = 2880) -> np.ndarray:
    """The ripple edge: r(θ) = R_mid + A·cos(24 θ), a crest at 12 o'clock.
    Smooth throughout (crest radius ≈ 11 px, trough radius ≈ 11.5 px —
    comfortably above a steel-rule die's minimum)."""
    A = RIPPLE / 2
    Rm = R_PEAK - A
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = Rm + A * np.cos(LOBES * (th + np.pi / 2))
    return np.column_stack([cx + r * np.cos(th), cy + r * np.sin(th)])


def die_d(cx: float, cy: float) -> str:
    P = die_points(cx, cy)
    return G.poly_d(P, closed=True)


def rings(cx: float, cy: float, color: str = T.FOIL) -> Frag:
    f = stroke(circle_d(cx, cy, R_OUTER_RULE), T.RULE, style="rule", color=color, role="rule")
    f += stroke(circle_d(cx, cy, R_INNER_RULE), T.FINE, style="rule", color=color, role="rule")
    return f


def cap_size(cap: float = CAP) -> float:
    m = TS.font_metrics(str(T.FONT_INDEX))
    return cap * m["upm"] / m["capHeight"]


def legend_text(cx: float, cy: float, color: str = T.FOIL) -> tuple[Frag, dict]:
    size = cap_size()
    font = str(T.FONT_INDEX)
    top = TS.text_on_arc(font, TOP_TEXT, size, cx, cy, R_TEXT, tracking=TRACK_TOP, missing="raise")
    bot = TS.text_on_arc(font, BOTTOM_TEXT, size, cx, cy, R_TEXT, bottom=True, tracking=TRACK_BOTTOM,
                         missing="raise")
    w_top = TS.measure(font, TOP_TEXT, size, tracking=TRACK_TOP)
    w_bot = TS.measure(font, BOTTOM_TEXT, size, tracking=TRACK_BOTTOM)
    span_top = math.degrees(w_top / R_TEXT)
    span_bot = math.degrees(w_bot / R_TEXT)
    f = fill(top, color=color, role="type") + fill(bot, color=color, role="type")
    return f, dict(size=size, span_top=span_top, span_bot=span_bot)


def bubble_string(cx: float, cy: float, a_lo: float, a_hi: float, sizes, *, gap: float,
                  color: str = T.FOIL) -> Frag:
    """Bubbles on the text circle from angle a_lo (lower end) toward a_hi
    (upper end), sizes growing upward, equal clear gaps, centred between the
    two angles. A size given as ('dot', d) is a solid dot, ('ring', d) a FINE
    ring of centreline Ø d."""
    outer = [d if k == "dot" else d + T.FINE for k, d in sizes]
    total = sum(outer) + gap * (len(sizes) - 1)
    span = math.degrees(total / R_TEXT)
    mid = (a_lo + a_hi) / 2
    direction = 1.0 if a_hi > a_lo else -1.0
    a = mid - direction * span / 2
    f = Frag()
    for (kind, d), o in zip(sizes, outer):
        a_c = a + direction * math.degrees(o / 2 / R_TEXT)
        x = cx + R_TEXT * math.cos(math.radians(a_c))
        y = cy + R_TEXT * math.sin(math.radians(a_c))
        if kind == "dot":
            f += dot(x, y, d, color=color, role="bubble")
        else:
            f += stroke(circle_d(x, y, d / 2), T.FINE, color=color, role="bubble")
        a = a + direction * math.degrees((o + gap) / R_TEXT)
    return f


BUBBLES = (("dot", 4.2), ("dot", 6.3), ("ring", 7.6), ("ring", 9.1), ("ring", 10.9), ("ring", 13.1))
BUBBLE_GAP = 4.6


def bubble_strings(cx: float, cy: float, span_top: float, span_bot: float, *, pad: float = 7.0,
                   color: str = T.FOIL) -> Frag:
    """Both separators. Right side: from the end of the bottom legend up to the
    start of the top legend; the left is its mirror image."""
    # right side: screen angles grow clockwise; "up" = toward -90
    top_end = -90 + span_top / 2 + pad
    bot_end = 90 - span_bot / 2 - pad
    right = bubble_string(cx, cy, bot_end, top_end, BUBBLES, gap=BUBBLE_GAP, color=color)
    left = right.mirror_x(cx)
    return right + left

