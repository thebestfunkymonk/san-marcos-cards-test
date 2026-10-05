"""A♠ legend (brief §H.13 table, §D, §J.2 verbatim copy), all gold, all outlined.

  1  HEADWATERS                               Roboto Slab 700, cap 30, +120, baseline 590
  2  PLAYING CARDS OF THE SAN MARCOS SPRINGS  Barlow, cap 12, +200, baseline 625, FINE em-rules
  3  NEVER KNOWN TO CEASE                     Barlow, cap 14, +250, baseline 660, FINE em-rules
  4  NAMED FOR ST. MARK · MDCLXXXIX           Barlow, cap 13, +220, on a SAGGING arc (concave up),
                                              radius 600, the baseline's lowest point at y 718.6
                                              (brief 735; see below)

(These are the legend's own coordinates; art/AS.py moves the whole
composition down by AS.COMPOSITION_DY.)

The em-rules are drawn (FINE, 24 px long, 10 px from the ink, §D), never
typed. Line 4 is set glyph by glyph on the lower arc of a circle r 600, so
its baseline dips at the centre and rises toward both ends (a smile, never
a rising arch).

Spacing correction (client, 2026-09-24): with the brief's lowest point 735
the arc's ends sat 51.4 px below line 3 (the other lines are on a 35 px
baseline pitch), so line 4 floated away from the block (ink gap 38.7 px at
the ends, ~62 at the dip, against 20.7–22.5 between lines 1–3). The arc is
now raised so its END baselines (x 208 / 542, under line 3's em-rule ends)
sit one pitch below line 3 (y 695): lowest point 718.6, ink gap 22.3 at the
ends and ≈ 45 at the dip — the same as the plinth-to-HEADWATERS gap. The
radius, setting and smile are unchanged. The straight lines are centred on
their INK (type_line centres the advance run, 0.2 px right on lines 2–3).

Micro-type print correction (as on the sibling aces): Barlow's counters at
cap 12–14 are 1.7–2.5 px, under §I.12's 2.5 px of paper inside a solid, and
in metallic ink they plug. Counters between 2.0 and 2.65 px are opened
outward to 2.65 px (≈0.1–0.3 px a side, invisible); the A's counter (under
2.0 px) cannot open without thinning its legs, so it is closed, as the
press would close it.
"""
from __future__ import annotations

import math

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


def arc_row(rows=F.ACE_SPADE_LEGEND) -> dict:
    """Line 4's row with its lowest point set so the arc's ENDS keep the
    legend's baseline pitch: the end baselines (at the run's ink ends) sit one
    pitch (line 3 - line 2) below line 3. Brief 735 -> 718.6."""
    straight = [r for r in rows if "arc" not in r]
    row = next(r for r in rows if "arc" in r)
    pitch = straight[-1]["baseline"] - straight[-2]["baseline"]            # 35
    x0, _, x1, _ = G.bbox(_arc_line(row))                                  # x extent: independent of y
    R, half = float(row["arc"]["radius"]), (x1 - x0) / 2
    low = straight[-1]["baseline"] + pitch + R - math.sqrt(R * R - half * half)
    return dict(row, arc=dict(row["arc"], lowest_y=round(low, 1)))


def legend() -> Frag:
    f = Frag()
    for row in F.ACE_SPADE_LEGEND:
        if "arc" in row:
            f += fill(open_counters(_arc_line(arc_row())), color=GOLD, role="type")
            continue
        d, bb = _line(row)
        if row["font"] != "slab":
            d = open_counters(d)
        x0, _, x1, _ = G.bbox(d)
        dx = T.CX - (x0 + x1) / 2                          # centre the line (and its em-rules) on its ink
        line = fill(d, color=GOLD, role="type")
        if row.get("em_rules"):
            line += stroke(F.em_rules_d(bb, row["cap"]), T.FINE, style="rule", color=GOLD, role="em-rule")
        f += line.translate(dx, 0.0)
    return f


# =============================================================================
# v3 layout (client, 2026-10-01): the spade CENTRED on the card, the legend
# split round it like the lettering round the Drifters A♠ — two concentric
# ARCHES above (HEADWATERS, then line 2 inside it), two concentric SMILES
# below (line 3, then line 4 outside it: §H.13's sagging arc kept). CARD
# coordinates (not shifted by AS.COMPOSITION_DY). Copy verbatim (§J.2).
# =============================================================================
from art import _aces_common as A          # noqa: E402

V3 = dict(
    R_TOP=560.0, R_BOT=600.0,              # arc radii (the outer line of each pair)
    head_apex=254.0,                       # HEADWATERS arch: apex baseline y
    pitch_top=44.0,                        # line 2's arch: concentric, this much inside
    l3_apex=764.0,                         # NEVER KNOWN TO CEASE smile: lowest baseline y
    pitch_bot=42.0,                        # line 4's smile: concentric, this much outside
)


def legend_v3(spec=None) -> Frag:
    sp = dict(V3, **(spec or {}))
    rows = {r["text"]: r for r in F.ACE_SPADE_LEGEND}
    t1, t2, t3, t4 = (r["text"] for r in F.ACE_SPADE_LEGEND)
    r1, r2, r3, r4 = (rows[t] for t in (t1, t2, t3, t4))
    f = A.arc_type(t1, r1["cap"], r1["tracking"], sp["head_apex"], sp["R_TOP"], arch=True, font="slab",
                   role="type")
    f += A.arc_ribbon(f, r1["cap"], arch=True, pad=9.0, margin=26.0, notch=16.0)
    f += A.arc_type(t2, r2["cap"], r2["tracking"], sp["head_apex"] + sp["pitch_top"],
                    sp["R_TOP"] - sp["pitch_top"], arch=True, em_rules=True, role="type")
    f += A.arc_type(t3, r3["cap"], r3["tracking"], sp["l3_apex"], sp["R_BOT"], arch=False, em_rules=True,
                    role="type")
    l4 = A.arc_type(t4, r4["cap"], r4["tracking"], sp["l3_apex"] + sp["pitch_bot"],
                    sp["R_BOT"] + sp["pitch_bot"], arch=False, role="type")
    f += l4 + A.arc_ribbon(l4, r4["cap"], arch=False)
    return f
