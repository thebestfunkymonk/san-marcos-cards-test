"""A♠ legend (brief §H.13 table, §D, §J.2 verbatim copy), all gold, all outlined.

  1  HEADWATERS                               Roboto Slab 700, cap 30, +120, baseline 590
  2  PLAYING CARDS OF THE SAN MARCOS SPRINGS  Barlow, cap 12, +200, baseline 625, FINE em-rules
  3  NEVER KNOWN TO CEASE                     Barlow, cap 14, +250, baseline 660, FINE em-rules
  4  NAMED FOR ST. MARK · MDCLXXXIX           Barlow, cap 13, +220, on a SAGGING arc (concave up),
                                              radius 600, the baseline's lowest point at y 735

The em-rules are drawn (FINE, 24 px long, 10 px from the ink, §D), never
typed. Line 4 is set glyph by glyph on the lower arc of a circle centred
(375, 135) r 600, so its baseline dips to y 735 at the centre and rises
toward both ends (a smile, never a rising arch).

Micro-type print correction (as on the sibling aces): Barlow's counters at
cap 12–14 are 1.7–2.5 px, under §I.12's 2.5 px of paper inside a solid, and
in metallic ink they plug. Counters between 2.0 and 2.65 px are opened
outward to 2.65 px (≈0.1–0.3 px a side, invisible); the A's counter (under
2.0 px) cannot open without thinning its legs, so it is closed, as the
press would close it.
"""
from __future__ import annotations

import numpy as np
import shapely

from deck import frames as F
from deck import tokens as T
from deck.motifs.core import Frag, fill, stroke
from inkkit import geom as G
from inkkit import typeset as TY

GOLD = T.FOIL
COUNTER_MIN = 2.65
COUNTER_CLOSE = 2.0


def open_counters(d: str, min_w: float = COUNTER_MIN, close_below: float = COUNTER_CLOSE) -> str:
    s = G.to_shape(d, tol=0.01)
    out = []
    for pg in getattr(s, "geoms", [s]):
        holes = []
        for ring in pg.interiors:
            hole = shapely.Polygon(ring)
            w = 2 * shapely.maximum_inscribed_circle(hole, 0.01).length
            if w < close_below:
                continue                                   # closed
            if w < min_w:
                hole = hole.buffer((min_w - w) / 2 + 0.02, join_style="mitre", mitre_limit=4)
            holes.append(hole)
        pg = shapely.Polygon(pg.exterior)
        for h in holes:
            pg = pg.difference(h)
        out.append(pg)
    return G.from_shape(shapely.union_all(out))


def _line(row) -> tuple[str, tuple]:
    if row["font"] == "slab":
        return F.slab_line(row["text"], row["cap"], row["baseline"], row["tracking"])
    return F.type_line(row["text"], row["cap"], row["baseline"], row["tracking"])


def _arc_line(row) -> str:
    """Line 4 on the sagging arc: glyphs laid out with the font's own advances
    and kerning (inkkit), their baseline on the circle, each glyph turned to
    the local tangent. The run is centred on its INK (trailing tracking and
    side bearings excluded) so the dip sits exactly under x 375."""
    arc = row["arc"]
    R, low = float(arc["radius"]), float(arc["lowest_y"])
    cx, cy = T.CX, low - R
    size = F.cap_to_size(str(T.FONT_INDEX), row["cap"])
    a = np.radians(np.linspace(180.0, 0.0, 4001))            # the circle's lower arc, left -> right
    pts = np.column_stack([cx + R * np.cos(a), cy + R * np.sin(a)])

    def setd(shift: float) -> str:
        cv = G.Curve(pts)
        at = 0.5 + shift / cv.length
        return TY.text_on_path(str(T.FONT_INDEX), row["text"], size, pts, at=at, align="middle",
                               baseline="alphabetic", tracking=row["tracking"])
    d = setd(0.0)
    x0, _, x1, _ = G.bbox(d)
    return setd(T.CX - (x0 + x1) / 2)


def legend() -> Frag:
    f = Frag()
    for row in F.ACE_SPADE_LEGEND:
        if "arc" in row:
            f += fill(open_counters(_arc_line(row)), color=GOLD, role="type")
            continue
        d, bb = _line(row)
        if row["font"] != "slab":
            d = open_counters(d)
        f += fill(d, color=GOLD, role="type")
        if row.get("em_rules"):
            f += stroke(F.em_rules_d(bb, row["cap"]), T.FINE, style="rule", color=GOLD, role="em-rule")
    return f
