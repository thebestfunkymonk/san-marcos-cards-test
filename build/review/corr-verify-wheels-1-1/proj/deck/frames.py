"""Court frame, divider band, rank medallions, house marks (brief §F.1) and
the ace / joker layout constants (§F.3, §F.4) shared by the art modules.

Court frame (§F.1)
------------------
* Outer rule: RULE Aquifer, x 128-622 y 44-1006, 18 px 45° chamfers, miter joins.
* Inner rule: FINE Lion Gold, the exact parallel offset 7 px inside (so its
  chamfer cut is 18 - 7(2-√2) = 13.90 px), miter joins. (3.85 px of paper to
  the RULE: a brief-mandated §I.12 exception, ``RESOLUTIONS["frame_gap"]``.)
* Art window: x 139-611, y 55-511 — i.e. the frame offset 11 px inside,
  chamfered likewise (cut 11.56 px). ``court_clip_d(rank)`` is that window
  above the band's top rule minus the medallion's mask disc.
* Corner pip: u 88, top y 62, centred on the box x 146-234 (x 190); rotated copy.
* Divider band y 511-539: two FINE Aquifer rules running between the gold
  inner rules; the MEDIUM house partition line between them; the rank
  medallion at (375, 525) masks (geometrically cuts) everything beneath it.

The band is a paper strip: court art is clipped at the band's top rule
(y 511, the rule covers the cut), so "the band hides the cut" (§F.1 two-headed
construction). An art module may set ``CUT_Y = 525`` to let an attribute run
visibly into the band; see deck/ART_CONTRACT.md.

Resolved §F.1 details: see ``RESOLUTIONS`` (and deck/ART_CONTRACT.md
"Deviations from brief" D4 for the ♠ step).
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import shapely

from inkkit import geom as G
from inkkit import svg as S
from inkkit.typeset import text_to_path, font_metrics
from deck import tokens as T
from deck import pips as P

# -----------------------------------------------------------------------------
# derived constants (each cites the brief)
# -----------------------------------------------------------------------------
SQ2 = math.sqrt(2.0)
FRAME = (T.FRAME_X0, T.FRAME_Y0, T.FRAME_X1, T.FRAME_Y1)          # §F.1 outer rule
INNER_RULE_INSET = T.FRAME_INNER_INSET                              # §F.1: 7 px
ART_WINDOW_INSET = T.ART_WINDOW[0] - T.FRAME_X0                     # §F.1: 139-128 = 11
BAND_Y0, BAND_Y1 = T.BAND_Y0, T.BAND_Y1                             # §F.1: 511 / 539
BAND_RULE_X0 = T.FRAME_X0 + INNER_RULE_INSET                       # 135: rules run between the gold rules
BAND_RULE_X1 = T.FRAME_X1 - INNER_RULE_INSET                       # 615
CORNER_PIP_CX = (T.COURT_PIP_BOX[0] + T.COURT_PIP_BOX[2]) / 2      # 190
CORNER_PIP_TOP = T.COURT_PIP_BOX[1]                                # 62
CORNER_PIP_CLEAR = 12                                              # §F.1: figures keep >= 12 px clear

# §F.1 rank grade. One spacing rule for every system ornament (§I.12): 4.2 px
# of paper between parallel strokes, >= 3.0 px between separate marks.
GAP_PARALLEL = 4.2           # §I.12 / §B.2
GAP_MARK = 3.0               # §I.12 knockout gap, used for separate marks (dots, beads, ticks)
KING_R_OUTER = 28.0          # Ø 56 outer ring (FINE Aquifer)
KING_R_INNER = KING_R_OUTER - T.FINE - GAP_PARALLEL      # 21.7: "6 px apart" -> 6.3 c-c (paper 4.2)
QUEEN_R = 22.0               # Ø 44 single FINE Aquifer ring = the medallion's edge
QUEEN_BEAD_D = 4.2           # 8 gold beads Ø 4.2, INSIDE the ring (see RESOLUTIONS["queen"])
QUEEN_BEAD_R = QUEEN_R - T.FINE / 2 - GAP_MARK - QUEEN_BEAD_D / 2   # 15.85
QUEEN_BEAD_START = 22.5      # beads at 22.5° + 45° k: the axes stay free for the house mark
MEDALLION_GAP = T.INTERLACE_GAP   # §B.2: what passes under breaks 4.2 px from the over-shape
HOUSE_MARK_SIZE = 26.0       # §F.1 "≈ 26 px" (King); the Queen's is the compact version (≈ 20 px)

# §F.1 partition lines
FAULT_SPACING = T.MEDIUM + GAP_PARALLEL   # 7.3: the pair's lines (paper 4.2, §I.12)
# D4 (deck/ART_CONTRACT.md "Deviations from brief"): the step is one course,
# the largest that keeps 4.2 px of paper to the FINE band rules:
# 2 x (14 - FINE/2 - 4.2 - MEDIUM/2 - FAULT_SPACING/2) = 7.1 (brief: 4).
FAULT_STEP = 2 * ((T.BAND_Y1 - T.BAND_Y0) / 2 - T.FINE / 2 - GAP_PARALLEL - T.MEDIUM / 2 - FAULT_SPACING / 2)
RIPPLE_WAVELENGTH, RIPPLE_AMPLITUDE = 44.0, 5.0
REED_TICK_PITCH, REED_TICK_LEN, REED_NODE_PITCH = 48.0, 12.0, 96.0
REED_NODE_RX, REED_NODE_RY = 7.0, 3.5   # 14 x 7
REED_BLADE_R = 10.0                     # leaf-tick blades: circular arcs of r 10, length 12
FORD_Y = (520.0, 530.0)
FORD_STONE_PITCH, FORD_STONE_H, FORD_STONE_W = 40.0, 10.0, 12.0
# Partition lines stop ~7 px clear of the gold inner rules (whose inner edge is
# at x 136.05 / 613.95) instead of 2.95 px short of them; the ripple spans
# 5.25 wavelengths each side so both ends land on a crest/trough (§I.14).
PARTITION_HALF = 5.25 * RIPPLE_WAVELENGTH                        # 231
PARTITION_X0, PARTITION_X1 = T.CX - PARTITION_HALF - 1, T.CX + PARTITION_HALF + 1   # 143-607
RIPPLE_X0, RIPPLE_X1 = T.CX - PARTITION_HALF, T.CX + PARTITION_HALF                # 144-606

RESOLUTIONS = {
    "band": "Art is clipped at the band's top rule (y 511) so the band is a clean paper strip that "
            "hides the cut; art may still run past 511 in the source (the system clips it).",
    "frame_gap": "§F.1's 7 px (centre to centre) between the RULE frame and the FINE gold rule leaves "
                 "3.85 px of paper, under §I.12's 4.2. Kept as a brief-mandated exception: widening it "
                 "would squeeze the art window (x 139) against the gold rule instead. QA exempts this pair.",
    "fault_step": "The pair is the exact parallel offset (±3.65) of ONE stepped centreline (y 521.45 -> "
                  "528.55 at x 375), so the risers sit at x 378.65 (upper line) and 371.35 (lower line) and "
                  "the paper between the lines is 4.2 px everywhere, riser included (§I.12). Lines 7.3 apart "
                  "(not 6: MEDIUM lines 6 apart leave 2.9 px). Step 7.1 = one course (D4, brief 4): left pair "
                  "y 517.8/525.1, right pair 524.9/532.2, so the middle line runs on through y 525 and the "
                  "strata read as displaced one course (G.10/G.11). On K and Q the medallion covers the riser "
                  "and sits on the fault; with a 4 px step the two halves read as a registration error. "
                  "4.2 px of paper to the band rules; C2 about (375, 525).",
    "partition_ends": "Partition lines run x 143-607 (≈ 7 px clear of the gold rules); the ripple x 144-606 "
                      "(5.25 λ each side) ends on a trough (left, y 530) and a crest (right, y 520), both "
                      "with level tangents. Band rules run between the gold rules (x 135-615).",
    "ford": "10 px lozenge stones (10 tall x 12 wide) with tips on the rules at y 520/530, every 40 px "
            "from x 375.",
    "reed": "Nodes (solid 14 x 7 knots) every 96 px from x 375; paired leaf-ticks every 48 px at 375 + 48k, "
            "so every other pair springs from the ends of a node (the house mark repeated along the "
            "stalk) and the plain pairs sit midway. Each pair is a 12 px circular-arc blade springing "
            "up-right plus its C2 partner down-left. Band nodes are solid Aquifer knots; the gold house "
            "mark's node is a FINE outline (§C.1 restricts flat gold fills).",
    "king": "Double ring r 28 (FINE Aquifer) and r 21.7 (FINE gold): 6.3 px centre to centre so the paper "
            "between them is the §I.12 4.2 px ('6 px apart' as centre spacing would leave 3.9).",
    "queen": "Ø 44 FINE Aquifer ring is the medallion's edge (Ø 46.1 overall < the King's 58.1). The 8 gold "
             "beads (Ø 4.2) ring the inside at r 15.85 (3 px inside the ring), at 22.5° + 45° k, and the "
             "house mark is the compact version (fits r ≤ 10.75 near the beads, r ≤ 13.6 along the axes "
             "and diagonals between them). Queen ♥ mark: a linked chain of bubble rings Ø 5.6 / 10 / 5.6 on the "
             "diagonal, tangent to each other (spaced rings cannot fit inside the beads with 3 px gaps; dots "
             "would read as stray beads).",
    "house_marks": "Gold FINE, same design on K and Q (Q compact); ≥ 3 px between a mark's parts and "
                   "from the rings / beads.",
    "corner_pip": "u 88 pips are top-aligned at y 62 and centred on x 190 (the box centre), like the index. "
                  "With the D1 spade the ♠ corner pip runs to y 169.4 (box y1 159 was the 1.10 u spade).",
    "ace_layers": "A♠/A♣ use layer order paper, jade, red, ink, gold (§K: gold above the suit ink).",
}


# -----------------------------------------------------------------------------
# geometry helpers
# -----------------------------------------------------------------------------
def chamfer_rect_pts(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1),
            (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def chamfer_rect_d(x0, y0, x1, y1, c) -> str:
    return G.poly_d(chamfer_rect_pts(x0, y0, x1, y1, c), closed=True)


def frame_inset_d(inset: float) -> str:
    """The court frame's exact parallel offset ``inset`` px inside (chamfer
    cut shrinks by inset·(2-√2))."""
    x0, y0, x1, y1 = FRAME
    c = T.FRAME_CHAMFER - inset * (2 - SQ2)
    return chamfer_rect_d(x0 + inset, y0 + inset, x1 - inset, y1 - inset, c)


def _stroke(d, color, width, cap="butt", join="miter", miterlimit=4, **kw) -> str:
    return S.path(d, fill="none", stroke=color, stroke_width=width, stroke_linecap=cap,
                  stroke_linejoin=join, stroke_miterlimit=miterlimit if join == "miter" else None, **kw)


def _fill(d, color, **kw) -> str:
    return S.path(d, fill=color, **kw)


def medallion_radius(rank: str) -> float:
    """Outer radius of the medallion's ink (incl. beads), 0 for a Jack."""
    rank = rank.upper()
    if rank == "K":
        return KING_R_OUTER + T.FINE / 2
    if rank == "Q":
        return QUEEN_R + T.FINE / 2
    return 0.0


def medallion_mask_d(rank: str) -> str:
    """Disc that the medallion masks: its outer edge + the 4.2 px break."""
    r = medallion_radius(rank)
    return G.circle_d(T.CX, T.CY, r + MEDALLION_GAP) if r else ""


def _cut_lines(d: str, rank: str) -> str:
    """STROKE centrelines cut where they pass under the medallion."""
    m = medallion_mask_d(rank)
    return G.clip_out(d, m) if m else d


# -----------------------------------------------------------------------------
# clip regions for art
# -----------------------------------------------------------------------------
@lru_cache(maxsize=None)
def art_window_d() -> str:
    """The chamfered art window (whole court, both halves), 11 px inside."""
    return frame_inset_d(ART_WINDOW_INSET)


@lru_cache(maxsize=None)
def court_clip_d(rank: str = "J", cut_y: float = BAND_Y0) -> str:
    """Top-half clip for court art: the art window above ``cut_y`` minus the
    rank medallion's mask disc. Used by ``cardsvg.two_headed``."""
    win = G.intersection(art_window_d(), G.rect_d(0, 0, T.W, cut_y))
    m = medallion_mask_d(rank)
    return G.difference(win, m) if m else win


# -----------------------------------------------------------------------------
# partition lines (MEDIUM Aquifer, C2 about (375, 525))
# -----------------------------------------------------------------------------
def _fault_step_d(step: float = FAULT_STEP) -> str:
    """♠ double fault-step: the exact parallel offsets (±FAULT_SPACING/2) of
    one stepped centreline (y 525 - step/2 left of x 375, 525 + step/2 right),
    so each line's riser is offset by ∓h in x and the paper between the lines
    is 4.2 px everywhere (§I.12). C2: (xc+h, a-h) maps to (xc-h, b+h)."""
    h = FAULT_SPACING / 2
    a, b = T.CY - step / 2, T.CY + step / 2
    x0, x1, xc = PARTITION_X0, PARTITION_X1, T.CX
    up = G.poly_d([(x0, a - h), (xc + h, a - h), (xc + h, b - h), (x1, b - h)])
    lo = G.poly_d([(x0, a + h), (xc - h, a + h), (xc - h, b + h), (x1, b + h)])
    return up + lo


def _ripple_d() -> str:
    x = np.linspace(RIPPLE_X0, RIPPLE_X1, int(round((RIPPLE_X1 - RIPPLE_X0) * 2)) + 1)
    y = T.CY - RIPPLE_AMPLITUDE * np.sin(2 * np.pi * (x - T.CX) / RIPPLE_WAVELENGTH)
    return G.poly_d(np.column_stack([x, y]))


def _blade_d(bx: float, by: float, sgn: int) -> str:
    """One reed leaf-tick: a circular-arc blade springing tangentially from
    the stalk at (bx, by) and curling up-right (sgn=1) or, as its exact C2
    partner, down-left (sgn=-1). Arc length ≈ REED_TICK_LEN."""
    R = REED_BLADE_R
    sweep = REED_TICK_LEN / R
    ph = np.linspace(math.pi / 2, math.pi / 2 - sweep, 24)
    pts = np.column_stack([bx + R * np.cos(ph), by - R + R * np.sin(ph)])
    if sgn < 0:
        pts = np.column_stack([2 * bx - pts[:, 0], 2 * by - pts[:, 1]])
    return G.poly_d(pts)


def _reed_parts(keep_out: float = 0.0):
    """(stalk STROKE d, ticks STROKE d, nodes list[(cx, cy)]). Leaf-tick pairs
    sit at 375 + 48k; on node positions (k even) the blades spring from the
    node's ends (x ± 7), elsewhere from the stalk. Ticks and nodes closer
    than ``keep_out`` to the centre are omitted (medallion)."""
    stalk = G.poly_d([(PARTITION_X0, T.CY), (PARTITION_X1, T.CY)])
    nodes, ticks = [], []
    per = int(round(REED_NODE_PITCH / REED_TICK_PITCH))
    for k in range(-12, 13):
        x = T.CX + k * REED_TICK_PITCH
        on_node = k % per == 0
        sp = REED_NODE_RX if on_node else 0.0          # blade root offset from x
        reach = sp + REED_TICK_LEN                     # half-extent of the pair along x
        if x - reach < PARTITION_X0 + 6 or x + reach > PARTITION_X1 - 6:
            continue
        if keep_out and abs(x - T.CX) - reach < keep_out:
            continue
        if on_node:
            nodes.append((x, T.CY))
        ticks.append(_blade_d(x + sp, T.CY, 1) + _blade_d(x - sp, T.CY, -1))
    return stalk, "".join(ticks), nodes


def _ford_parts(keep_out: float = 0.0):
    rules = G.poly_d([(PARTITION_X0, FORD_Y[0]), (PARTITION_X1, FORD_Y[0])]) + \
        G.poly_d([(PARTITION_X0, FORD_Y[1]), (PARTITION_X1, FORD_Y[1])])
    stones = []
    for k in range(-12, 13):
        x = T.CX + k * FORD_STONE_PITCH
        if PARTITION_X0 + 10 <= x - FORD_STONE_W / 2 and x + FORD_STONE_W / 2 <= PARTITION_X1 - 10 \
                and (not keep_out or abs(x - T.CX) - FORD_STONE_W / 2 >= keep_out):
            stones.append(x)
    return rules, stones


def _lozenge_d(cx, cy, w, h) -> str:
    return G.poly_d([(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)], closed=True)


def partition_fragments(suit: str, rank: str) -> list[str]:
    """The house partition line (§F.1), masked by the rank medallion."""
    suit, rank = suit.upper(), rank.upper()
    mask = medallion_mask_d(rank)
    # discrete elements (ticks, nodes, stones) are dropped, not cut, near the medallion
    keep_out = (medallion_radius(rank) + MEDALLION_GAP + 6.0) if mask else 0.0
    out = []
    if suit == "S":
        out.append(_stroke(_cut_lines(_fault_step_d(), rank), T.INK, T.MEDIUM, class_="partition"))
    elif suit == "H":
        out.append(_stroke(_cut_lines(_ripple_d(), rank), T.INK, T.MEDIUM, cap="butt", join="round",
                           class_="partition"))
    elif suit == "C":
        stalk, ticks, nodes = _reed_parts(keep_out)
        node_d = "".join(G.ellipse_d(x, y, REED_NODE_RX, REED_NODE_RY) for x, y in nodes)
        # the stalk runs through the nodes: the node is a solid knot on the stalk
        out.append(_stroke(_cut_lines(stalk, rank), T.INK, T.MEDIUM, class_="partition"))
        if ticks:
            out.append(_stroke(ticks, T.INK, T.MEDIUM, cap="round", join="round", class_="partition"))
        if node_d:
            out.append(_fill(node_d, T.INK, class_="partition"))
    elif suit == "D":
        rules, stones = _ford_parts(keep_out)
        out.append(_stroke(_cut_lines(rules, rank), T.INK, T.MEDIUM, class_="partition"))
        sd = "".join(_lozenge_d(x, T.CY, FORD_STONE_W, FORD_STONE_H) for x in stones)
        if sd:
            out.append(_fill(sd, T.INK, class_="partition"))
    else:
        raise ValueError(suit)
    return out


# -----------------------------------------------------------------------------
# house marks (≈ 26 px, C2-symmetric, gold FINE) and medallions
# -----------------------------------------------------------------------------
def house_mark_fragments(suit: str, cx: float = T.CX, cy: float = T.CY,
                         color: str = T.FOIL, compact: bool = False) -> list[str]:
    """§F.1 house marks, gold FINE, C2 about (cx, cy): ♠ Z-step, ♥ bubble
    triad, ♣ reed node, ♦ lozenge + dot. ``compact`` is the Queen's version
    (inside her bead ring: r ≤ 10.75 towards the beads at 22.5° + 45° k,
    r ≤ 13.6 along the axes and diagonals). Every paper gap inside a mark is
    ≥ 3 px (≥ 4.2 between its parallel lines)."""
    suit = suit.upper()
    w = T.FINE
    if suit == "S":
        # a double-rule fault-step: the parallel offsets (±3.15, paper 4.2) of one Z-step
        d = (w + GAP_PARALLEL) / 2
        h, x = (2.5, 9.0) if compact else (4.0, 13.0)
        a = G.poly_d([(cx - x, cy - h - d), (cx + d, cy - h - d), (cx + d, cy + h - d), (cx + x, cy + h - d)])
        b = G.poly_d([(cx - x, cy - h + d), (cx - d, cy - h + d), (cx - d, cy + h + d), (cx + x, cy + h + d)])
        return [_stroke(a + b, color, w, class_="house-mark")]
    if suit == "H":
        if compact:
            # a linked chain: Ø 10 bubble with two Ø 5.6 bubbles tangent to it on the
            # diagonal (spaced rings cannot fit inside the beads with 3 px gaps, and
            # dots would read as stray beads)
            rc, rs = 5.0, 2.8
            c = (rc + rs) / SQ2
            dd = G.circle_d(cx, cy, rc) + G.circle_d(cx + c, cy - c, rs) + G.circle_d(cx - c, cy + c, rs)
            return [_stroke(dd, color, w, join="round", class_="house-mark")]
        # bubbles Ø 6 / 10 / 6 (centrelines) rising along the diagonal, 3.1 px apart
        c = (5.0 + 3.0 + w + GAP_MARK + 0.1) / SQ2
        dd = G.circle_d(cx, cy, 5.0) + G.circle_d(cx + c, cy - c, 3.0) + G.circle_d(cx - c, cy + c, 3.0)
        return [_stroke(dd, color, w, join="round", class_="house-mark")]
    if suit == "C":
        # a reed node: an outlined knot on a stalk stub with two opposed arc
        # blades (up-right from the right, down-left from the left: C2)
        # blades spring from the knot's top and bottom (bx = 0), clear of the stubs
        if compact:
            rx, ry, stub, R, L, bx = 6.0, 3.1, 11.5, 6.0, 7.0, 0.0
        else:
            rx, ry, stub, R, L, bx = REED_NODE_RX, REED_NODE_RY, 13.0, 8.0, 11.0, 0.0
        stalk = G.poly_d([(cx - stub, cy), (cx - rx, cy)]) + G.poly_d([(cx + rx, cy), (cx + stub, cy)])
        ph = np.linspace(math.pi / 2, math.pi / 2 - L / R, 20)
        bl = np.column_stack([cx + bx + R * np.cos(ph), cy - ry - R + R * np.sin(ph)])
        blade = G.poly_d(bl) + G.poly_d(np.column_stack([2 * cx - bl[:, 0], 2 * cy - bl[:, 1]]))
        return [_stroke(G.ellipse_d(cx, cy, rx, ry), color, w, join="round", class_="house-mark"),
                _stroke(stalk, color, w, class_="house-mark"),
                _stroke(blade, color, w, cap="round", join="round", class_="house-mark")]
    if suit == "D":
        lw, lh = (16.0, 22.0) if compact else (18.0, 26.0)
        return [_stroke(_lozenge_d(cx, cy, lw, lh), color, w, miterlimit=10, class_="house-mark"),
                _fill(G.circle_d(cx, cy, 2.1), color, class_="house-mark")]
    raise ValueError(suit)


def lion_mark_fragments(cx: float, cy: float, size: float = 40.0):
    """Hook for the simplified Lion Mark (§G.2, built by Track B in
    ``deck.motifs``). Returns {layer: [fragments]} or None while the motif
    is unavailable. The medallion accepts it via ``medallion_fragments(...,
    mark=lambda cx, cy: lion_mark_fragments(cx, cy, 24))``."""
    try:
        from deck import motifs as M  # noqa: F401  (Track B)
        fn = getattr(M, "lion_mark", None) or getattr(M, "lion_mark_simplified", None)
    except Exception:
        return None
    if fn is None:
        return None
    try:
        res = fn(cx, cy, size)
    except TypeError:
        res = fn(cx=cx, cy=cy, size=size)
    if isinstance(res, str):
        return {"gold": [res]}
    return res


def medallion_fragments(rank: str, suit: str, mark=None) -> dict:
    """Rank-grade medallion at (375, 525) (§F.1). ``mark`` (optional) is a
    callable (cx, cy) -> {layer: [fragments]} replacing the house mark.
    K: Ø 56 FINE Aquifer ring + FINE gold ring 6.3 inside + house mark.
    Q: Ø 44 FINE Aquifer ring, 8 gold beads Ø 4.2 inside it, compact mark."""
    rank = rank.upper()
    out = {"ink": [], "gold": []}
    if rank not in ("K", "Q"):
        return out
    if rank == "K":
        out["ink"].append(_stroke(G.circle_d(T.CX, T.CY, KING_R_OUTER), T.INK, T.FINE, join="round",
                                  class_="medallion"))
        out["gold"].append(_stroke(G.circle_d(T.CX, T.CY, KING_R_INNER), T.FOIL, T.FINE, join="round",
                                   class_="medallion"))
    else:
        out["ink"].append(_stroke(G.circle_d(T.CX, T.CY, QUEEN_R), T.INK, T.FINE, join="round",
                                  class_="medallion"))
        beads = "".join(G.circle_d(T.CX + QUEEN_BEAD_R * math.cos(math.radians(a)),
                                   T.CY + QUEEN_BEAD_R * math.sin(math.radians(a)), QUEEN_BEAD_D / 2)
                        for a in np.arange(QUEEN_BEAD_START, 360, 45))
        out["gold"].append(_fill(beads, T.FOIL, class_="medallion"))
    if mark is not None:
        extra = mark(T.CX, T.CY) or {}
        for k, v in extra.items():
            out.setdefault(k, []).extend(v)
    else:
        out["gold"] += house_mark_fragments(suit, compact=(rank == "Q"))
    return out


# -----------------------------------------------------------------------------
# the whole court frame system
# -----------------------------------------------------------------------------
def corner_pip_d(suit: str) -> str:
    return P.pip_top_d(suit, T.PIP_U_COURT, CORNER_PIP_CX, CORNER_PIP_TOP)


def corner_pip_fragments(suit: str) -> dict:
    d = corner_pip_d(suit)
    col = T.SUIT_COLOR[suit]
    return {T.SUIT_LAYER[suit]: [_fill(d, col, class_="corner-pip", data_corner="tl"),
                                 _fill(G.rotate180(d, T.CX, T.CY), col, class_="corner-pip",
                                       data_corner="br")]}


def band_fragments(suit: str, rank: str) -> dict:
    rules = G.poly_d([(BAND_RULE_X0, BAND_Y0), (BAND_RULE_X1, BAND_Y0)]) + \
        G.poly_d([(BAND_RULE_X0, BAND_Y1), (BAND_RULE_X1, BAND_Y1)])
    ink = [_stroke(_cut_lines(rules, rank), T.INK, T.FINE, class_="band-rule")]
    ink += partition_fragments(suit, rank)
    return {"ink": ink}


def frame_rule_fragments() -> dict:
    x0, y0, x1, y1 = FRAME
    outer = chamfer_rect_d(x0, y0, x1, y1, T.FRAME_CHAMFER)
    return {"ink": [_stroke(outer, T.INK, T.RULE, class_="frame")],
            "gold": [_stroke(frame_inset_d(INNER_RULE_INSET), T.FOIL, T.FINE, class_="frame-inner")]}


def court_frame_fragments(rank: str, suit: str, mark=None) -> dict:
    """Everything the system draws on a court except the indices and art:
    frame rules, divider band + partition line, medallion, corner pips."""
    from deck.cardsvg import layers_merge
    return layers_merge(frame_rule_fragments(), band_fragments(suit, rank),
                        medallion_fragments(rank, suit, mark), corner_pip_fragments(suit))


# -----------------------------------------------------------------------------
# §F.3 aces and §F.4 jokers: constants + small shared helpers
# -----------------------------------------------------------------------------
ACE_PIP_CX = 375                  # §F.3 pip centred at x 375
ACE_PIP_CY = 470                  # A♥/A♣/A♦ pip centre y
ACE_SPADE_TOP = 140               # §F.3 / §H.13 A♠ spade top y
ACE_SPADE_U = P.ACE_SPADE_U       # 306.56: D1 spade keeps the §H.13 height 374 (y 140-514)
ACE_CAPTION_BASELINES = (760, 790)    # §F.3 (A♥, A♣, A♦; the A♠ has its own legend)
ACE_KEYLINE_OFFSET = 10           # gold FINE keyline 10 px outside the silhouette (not on A♠)
# §H.14 caption settings (cap px, tracking /1000 em, Barlow Condensed SemiBold,
# gold). The brief sets them only for A♥; A♣ and A♦ reuse them (same system).
ACE_CAPTION = {
    "line1": {"cap": 16, "tracking": 220, "baseline": 760},
    "line2": {"cap": 12, "tracking": 200, "baseline": 790},
}
ACE_CAPTION_TEXT = {              # §J.2 verbatim
    "H": ("HOUSE OF THE FOUNT", "SPRING LAKE · SEVENTY-TWO DEGREES"),
    "C": ("HOUSE OF THE REED", "WILD-RICE · FOUND NOWHERE ELSE"),
    "D": ("HOUSE OF THE FORD", "EL CAMINO REAL · THE RIVER CROSSING"),
}
# §H.13 A♠ legend (gold, centred on x 375). ``em_rules``: drawn FINE em-rules
# (24 px, 10 px gap, §D) flank the line. Line 4 sits on a SAGGING arc (concave
# up) of radius 600 whose lowest point is at y 735 — never a rising arc.
ACE_SPADE_LEGEND = (
    {"text": "HEADWATERS", "font": "slab", "cap": 30, "tracking": 120, "baseline": 590, "em_rules": False},
    {"text": "PLAYING CARDS OF THE SAN MARCOS SPRINGS", "font": "barlow", "cap": 12, "tracking": 200,
     "baseline": 625, "em_rules": True},
    {"text": "NEVER KNOWN TO CEASE", "font": "barlow", "cap": 14, "tracking": 250, "baseline": 660,
     "em_rules": True},
    {"text": "NAMED FOR ST. MARK · MDCLXXXIX", "font": "barlow", "cap": 13, "tracking": 220,
     "arc": {"radius": 600, "lowest_y": 735, "sagging": True}, "em_rules": False},
)
# §H.13 geometry table re-derived for the D1 spade at u 306.56, top y 140
# (measured from ace_pip_d("S"); the brief's u-340 numbers in brackets).
ACE_SPADE_GEOMETRY = {
    "apex_y": 140.0,                                   # [140]
    "width_at_200": 107.0, "x_at_200": (321.5, 428.5),  # [124, 313-437]
    "width_at_262": 217.4,                             # [250]
    "widest_y": 342.3, "widest": 306.6, "x_widest": (221.8, 528.3),   # [335, 340, 205-545]
    "lobe_bottom_y": 422.0,                            # [≈ 412]
    "cleft_y": 397.5,                                  # [≈ 392]: stem/lobe crotches (sharp)
    "stem_width_at_400": 32.8, "stem_width_at_480": 60.2,             # [40, 68]
    "plinth_y": (483.3, 514.0),                        # [480-514]; upper tread 92 wide to 498.6, lower 122.6
    "silhouette_x_at_350": (221.9, 528.1),             # waterline dashes 15-55 px beyond: x 167-207, 543-583
}

# §F.4 joker layout, lowered by JOKER_DY (client correction 2026-09-24): with the brief's
# numbers the figure + caption block sat ~75 px above the card centre (measured block
# middles y 454 / 447). JOKER_DY centres the block optically (≈ y 520) on both jokers.
JOKER_DY = 72
JOKER_FIGURE_Y = (90 + JOKER_DY, 640 + JOKER_DY)    # figure band (was §F.4 90-640)
JOKER_INDEX_CLEAR_Y = 310         # above this y the figure keeps x >= 130 (index zone; not shifted)
JOKER_INDEX_CLEAR_X = 130
JOKER_RULE_Y = 690 + JOKER_DY
JOKER_RULE_LEN = 360
JOKER_RULE_X = (T.CX - JOKER_RULE_LEN / 2, T.CX + JOKER_RULE_LEN / 2)    # 195-555
JOKER_TITLE = {"baseline": 745 + JOKER_DY, "cap": 28, "tracking": 200}   # Roboto Slab 700
JOKER_SUBLINE = {"baseline": 785 + JOKER_DY, "cap": 12, "tracking": 200}  # Barlow Condensed SemiBold

EM_RULE_LEN, EM_RULE_GAP = 24.0, 10.0                                   # §D micro-type em-rules


def ace_pip_d(suit: str) -> str:
    """The ace's big pip in its §F.3 position (A♠ u 306.56 [D1] top 140; others u 280 at y 470)."""
    if suit.upper() == "S":
        return P.pip_top_d("S", ACE_SPADE_U, ACE_PIP_CX, ACE_SPADE_TOP)
    return P.pip_d(suit, T.PIP_U_ACE, ACE_PIP_CX, ACE_PIP_CY)


def ace_keyline_d(suit: str, offset: float = ACE_KEYLINE_OFFSET) -> str:
    """Closed centreline of the ace's gold keyline (§F.3): the silhouette
    offset ``offset`` px outward, sharp (mitred) at tips and corners.
    Draw with stroke FINE gold, linejoin miter, miterlimit 10."""
    return G.offset(ace_pip_d(suit), offset, join="miter", miter_limit=10)


def cap_to_size(font: str, cap: float, variations: dict | None = None) -> float:
    m = font_metrics(font, variations)
    return cap * m["upm"] / m["capHeight"]


def type_line(text: str, cap: float, baseline: float, tracking: float = 0.0, x: float = T.CX,
              font: str = str(T.FONT_INDEX), variations: dict | None = None, anchor: str = "middle"):
    """Outlined type (FILL d, bbox). Tracking in 1/1000 em. When centred,
    the trailing tracking is excluded so the ink is optically centred."""
    size = cap_to_size(font, cap, variations)
    d, bb, adv = text_to_path(font, text, size, x, baseline, anchor=anchor, variations=variations,
                              tracking=tracking)
    return d, bb


def slab_line(text: str, cap: float, baseline: float, tracking: float = 0.0, x: float = T.CX):
    """Roboto Slab 700 (wordmark / headlines / joker titles)."""
    return type_line(text, cap, baseline, tracking, x, font=str(T.FONT_SLAB),
                     variations=T.SLAB_VARIATIONS)


def em_rules_d(bbox, cap: float) -> str:
    """STROKE d of the two FINE em-rules (24 px, 10 px gap) flanking a
    micro-type line whose ink bbox is ``bbox``; drawn at the cap middle."""
    x0, y0, x1, y1 = bbox
    base = y1 if abs(y1 - y0 - cap) < 3 else y0 + cap
    ym = base - cap / 2
    return (G.poly_d([(x0 - EM_RULE_GAP - EM_RULE_LEN, ym), (x0 - EM_RULE_GAP, ym)]) +
            G.poly_d([(x1 + EM_RULE_GAP, ym), (x1 + EM_RULE_GAP + EM_RULE_LEN, ym)]))


def joker_rule_fragments(color: str = T.FOIL) -> list[str]:
    """§F.4 FINE rule, 360 long at y JOKER_RULE_Y, with Ø 6.3 circle terminals."""
    x0, x1 = JOKER_RULE_X
    r = T.TERMINAL_D / 2
    return [_stroke(G.poly_d([(x0, JOKER_RULE_Y), (x1, JOKER_RULE_Y)]), color, T.FINE, class_="joker-rule"),
            _fill(G.circle_d(x0, JOKER_RULE_Y, r) + G.circle_d(x1, JOKER_RULE_Y, r), color,
                  class_="joker-rule")]


# -----------------------------------------------------------------------------
# preview:  .venv/bin/python -m deck.frames  -> build/specimen/bands.png
# -----------------------------------------------------------------------------
def specimen(out_dir=None) -> str:
    import os
    import subprocess
    out_dir = out_dir or os.path.join(T.ROOT, "build", "specimen")
    os.makedirs(out_dir, exist_ok=True)
    rows = [(s, r) for s in T.SUITS for r in "KQJ"]
    rh = 70
    Wd, Hd = 520, rh * len(rows)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd * 2}" height="{Hd * 2}" '
             f'viewBox="0 0 {Wd} {Hd}"><rect width="{Wd}" height="{Hd}" fill="{T.PAPER}"/>']
    for i, (s, r) in enumerate(rows):
        f = court_frame_fragments(r, s)
        body = "".join(f.get("gold", [])) + "".join(f.get("ink", []))
        # show just the band region, translated to the row
        parts.append(f'<g transform="translate({-115} {i * rh - 525 + rh / 2})">'
                     f'<clipPath id="c{i}"><rect x="120" y="485" width="510" height="80"/></clipPath>'
                     f'<g clip-path="url(#c{i})">{body}</g></g>')
    parts.append("</svg>")
    svg = os.path.join(out_dir, "bands.svg")
    png = os.path.join(out_dir, "bands.png")
    open(svg, "w").write("\n".join(parts))
    subprocess.run(["rsvg-convert", svg, "-o", png], check=True)
    return png


if __name__ == "__main__":
    print(specimen())
