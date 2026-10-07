"""Corner indices — creative-brief §D.1 exactly.

* Rank: Barlow Condensed SemiBold at ``INDEX_FONT_SIZE`` (137.14 px -> cap 96),
  baseline y 142 (cap top 46), glyph ink-bbox centred on the index axis x 84.
  "10" is set with tracking -20/1000 em (extents x 39.0-129.0). J sits on
  the baseline. No glyph surgery, with ONE exception (deck/ART_CONTRACT.md
  "Deviations from brief", D3): Barlow Condensed's Q tail is a vertical
  stub on the index axis that ends 7.7 px above the pip and fuses with it
  at 25 % (the Q reads as a "0" on a stalk). The Q keeps its own bowl
  (the glyph's upper half mirrored about the bowl's centre line, so it
  closes exactly like the O) and takes a diagonal tail of the same weight
  class (``Q_TAIL``), leaving the bowl at 4-5 o'clock and ending at
  y ≈ 153.4, x ≈ 115 — clear of the pip. The bowl, not the ink box, is
  centred on the axis.
* Index pip: u 62 (heart x 1.04), top at y 164, bbox centred on x 84.
* Joker: "JOKER" stacked on x 84, cap 44 (size 62.86), cap tops y 46/96/146/196/246.
* Only top-left and bottom-right: the bottom-right copy is the exact
  rotate(180, 375, 525) of the top-left block (baked into the path data).

API
---
``rank_d(rank)`` / ``index_pip_d(suit)`` -> FILL path of the top-left glyph.
``index_fragments(rank, suit)`` -> {suit layer: [svg fragments]} for both corners.
``joker_index_fragments(color_layer)`` -> {layer: [...]} ("red" or "ink").
``measure()`` -> a table of every rank's extents (run ``python -m deck.index``).
Paths carry ``class="index-rank"`` / ``"index-pip"`` (``data-corner="tl|br"``)
so QA can find them.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from inkkit import geom as G
from inkkit import svg as S
from inkkit.typeset import text_to_path
from deck import tokens as T
from deck import pips as P

__all__ = ["rank_d", "index_pip_d", "index_fragments", "joker_index_fragments",
           "rank_bbox", "measure", "INDEX_BLOCK_BOTTOM"]

_FONT = str(T.FONT_INDEX)
_COLOR_OF_LAYER = {"ink": T.INK, "red": T.RED}

# D3 (see module docstring): the Q's diagonal tail, relative to (axis x 84,
# baseline 142): centreline from (+11, -18) inside the bowl stroke to
# (+25, +8), 14.5 px thick (between the bowl's 13.7 px arches and 15.9 px
# sides), square-cut, its corners rounded 1.6 px like Barlow's terminals.
Q_TAIL = {"from": (11.0, -18.0), "to": (25.0, 8.0), "width": 14.5, "corner_r": 1.6}

# Derived (brief §D.1: "the index block ends by y ≈ 234"): the tallest index
# pip (diamond, 69.44 px) from its top at y 164.
INDEX_BLOCK_BOTTOM = T.INDEX_PIP_TOP + max(P.pip_size(s, T.INDEX_PIP_U)[1] for s in T.SUITS)


def _q_with_diagonal_tail(d: str) -> str:
    """D3: the Q's bowl (upper half mirrored about the counter's centre line)
    plus a diagonal tail (``Q_TAIL``). ``d`` is the native Q, already centred.

    Built with curve-preserving booleans so the bowl keeps the font's exact
    quadratics (a shapely round trip writes it as a visibly faceted polygon).
    The tail is trimmed to the counter so its rounded inner corners never
    poke into it."""
    import shapely
    q = G.to_shape(d)
    holes = [r for p in getattr(q, "geoms", [q]) for r in p.interiors]
    cy = shapely.Polygon(holes[0]).centroid.y if holes else (q.bounds[1] + T.INDEX_BASELINE) / 2
    top = G.intersection(d, G.rect_d(-1e3, -1e3, 2e3, 1e3 + cy))
    bowl = G.union(top, G.mirror_y(top, cy))
    ax, bl = T.INDEX_AXIS_X, T.INDEX_BASELINE
    p0 = np.array([ax + Q_TAIL["from"][0], bl + Q_TAIL["from"][1]])
    p1 = np.array([ax + Q_TAIL["to"][0], bl + Q_TAIL["to"][1]])
    length = float(np.linalg.norm(p1 - p0))
    w = Q_TAIL["width"]
    tail = G.rect_d(0.0, -w / 2, length, w, Q_TAIL["corner_r"])
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    tail = G.translate(G.rotate(tail, ang), p0[0], p0[1])
    # the counter as a solid: every hole subpath of the bowl, re-wound as a fill
    counter = "".join(G.orient(G.cmds_to_d(sub), "cw") for sub in G._split_subpaths(G.parse_d(bowl))
                      if G.signed_area(G.flatten(sub, 0.25)[0][0]) < 0)
    return G.union(bowl, G.difference(tail, counter) if counter else tail)


@lru_cache(maxsize=None)
def rank_d(rank: str) -> str:
    """Top-left rank glyph outline, centred on x = INDEX_AXIS_X (by its ink
    bbox; the Q by its bowl, D3)."""
    tr = T.INDEX_TEN_TRACKING if rank == "10" else 0
    d, bb, _ = text_to_path(_FONT, rank, T.INDEX_FONT_SIZE, 0.0, T.INDEX_BASELINE, tracking=tr)
    dx = T.INDEX_AXIS_X - (bb[0] + bb[2]) / 2
    d = G.translate(d, dx, 0.0)
    if rank == "Q":
        d = _q_with_diagonal_tail(d)
    return d


def rank_bbox(rank: str):
    return G.bbox(rank_d(rank))


@lru_cache(maxsize=None)
def index_pip_d(suit: str) -> str:
    return P.pip_top_d(suit, T.INDEX_PIP_U, T.INDEX_AXIS_X, T.INDEX_PIP_TOP)


def _both(d: str, color: str, cls: str) -> list[str]:
    return [S.path(d, fill=color, class_=cls, data_corner="tl"),
            S.path(G.rotate180(d, T.CX, T.CY), fill=color, class_=cls, data_corner="br")]


def index_fragments(rank: str, suit: str) -> dict:
    """Both corner indices for a card, in the suit's layer."""
    layer = T.SUIT_LAYER[suit]
    col = T.SUIT_COLOR[suit]
    frags = _both(rank_d(rank), col, "index-rank") + _both(index_pip_d(suit), col, "index-pip")
    return {layer: frags}


@lru_cache(maxsize=None)
def _joker_letters_d() -> str:
    out = []
    for ch, top in zip("JOKER", T.JOKER_INDEX_CAP_TOPS):
        cap = T.JOKER_INDEX_FONT_SIZE * 0.7          # Barlow capHeight 700/1000 -> 44 px
        d, bb, _ = text_to_path(_FONT, ch, T.JOKER_INDEX_FONT_SIZE, 0.0, top + cap)
        out.append(G.translate(d, T.INDEX_AXIS_X - (bb[0] + bb[2]) / 2, 0.0))
    return "".join(out)


def joker_index_fragments(layer: str = "red") -> dict:
    """Vertical JOKER index (§D.1) in Gill Red (Big) or Aquifer (Little)."""
    return {layer: _both(_joker_letters_d(), _COLOR_OF_LAYER[layer], "index-joker")}


def measure() -> list[dict]:
    """Measured extents of every rank glyph and index pip vs the brief."""
    rows = []
    for r in T.RANKS:
        x0, y0, x1, y1 = rank_bbox(r)
        rows.append({"glyph": r, "x0": round(x0, 2), "x1": round(x1, 2), "w": round(x1 - x0, 2),
                     "top": round(y0, 2), "bottom": round(y1, 2)})
    for s in T.SUITS:
        x0, y0, x1, y1 = G.bbox(index_pip_d(s))
        rows.append({"glyph": "pip " + s, "x0": round(x0, 2), "x1": round(x1, 2), "w": round(x1 - x0, 2),
                     "top": round(y0, 2), "bottom": round(y1, 2)})
    x0, y0, x1, y1 = G.bbox(_joker_letters_d())
    rows.append({"glyph": "JOKER", "x0": round(x0, 2), "x1": round(x1, 2), "w": round(x1 - x0, 2),
                 "top": round(y0, 2), "bottom": round(y1, 2)})
    return rows


if __name__ == "__main__":
    print(f"{'glyph':8} {'x0':>7} {'x1':>7} {'w':>6} {'top':>7} {'bottom':>7}")
    for r in measure():
        print(f"{r['glyph']:8} {r['x0']:7.2f} {r['x1']:7.2f} {r['w']:6.2f} {r['top']:7.2f} {r['bottom']:7.2f}")
    print(f"index block bottom: {INDEX_BLOCK_BOTTOM:.2f} (brief: ≈ 234; D1 spade 62 x 75.6)")
