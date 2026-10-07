"""art/_js_robes.py — J♠'s whole-card jade body: the doublet in flame-stitch (vertical zigzag columns) with
two hanging side panels (§H.3 doublet 'fault-line stepped chevrons knocked out to paper').

Everything is built about the card centre (375, 525) so the seam is only a place where the 180° copy
takes over:

* the BODY is one barrel (EDGE at the shoulders, bowing outward by BOW at the centre); its two long panel
  lines at x PANEL and 750 - PANEL run the whole card height (the top figure's left panel continues into
  the other figure's right one);
* the FLAME-STITCH columns are vertical paper zigzags, mirror-symmetric about the placket and even about
  y 525 (their zig phase peaks on the centre line), so a column's 180° partner is the mirrored column:
  parallel offsets, constant spacing, no crossings;
* alternate cells between columns carry FINE horizontal hatch, the panels the strata courses of the K♠
  mantle, the placket the gold buttons.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG
from art import _js_util as U

AX, CY = K.AX, 525.0
EDGE = 166.0                     # the body's side at the shoulders; the right is 2·AX − EDGE
BOW = 10.0                       # outward bow of the sides at the centre line
PANEL = 238.0                    # inner line of the left hanging panel
COL0, COL_PITCH, N_COLS = 19.0, 20.5, 6      # first column's offset from the axis, pitch, count per side
ZIG_A, ZIG_Q = 6.0, 25.0         # zigzag half-amplitude and half-period (vertical)
PLACKET = 10.0                   # half-width of the plain placket the buttons sit on
BUTTON_PITCH = 25.0
TOP, BOTTOM = 345.0, 2 * CY - 345.0


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def side_x(y):
    """Left edge of the barrel at height y (even about y 525)."""
    t = (y - 352.0) / (2 * CY - 704.0)
    return EDGE - BOW * math.sin(math.pi * min(max(t, 0.0), 1.0))


def body():
    """The whole-card jade barrel; its corners tuck under the two capes."""
    ys = np.linspace(352.0, 2 * CY - 352.0, 80)
    left = np.column_stack([[side_x(y) for y in ys], ys])
    right = np.column_stack([2 * AX - left[:, 0], ys])
    top_l = [(EDGE + 10.0, 334.0), (EDGE + 34.0, 318.0)]
    top_r = [(2 * AX - EDGE - 34.0, 318.0), (2 * AX - EDGE - 10.0, 334.0)]
    pts = np.vstack([left[::-1], np.array(top_l), np.array(top_r), right])
    half = Polygon(pts).buffer(0)
    return K.U(half, rot(half))


def panels():
    b = body()
    return b.intersection(K.box(0, 0, PANEL, 2000)), b.intersection(K.box(2 * AX - PANEL, 0, 2000, 2000))


def doublet():
    return body().intersection(K.box(PANEL, 0, 2 * AX - PANEL, 2000))


def _tri(y):
    s = (y - CY) / ZIG_Q
    s = s - 2.0 * round(s / 2.0)
    return 1.0 - 2.0 * abs(s)


def column_pts(j, sgn, y0=330.0, y1=720.0):
    """Zigzag column j (0 = nearest the placket) on side sgn (−1 left, +1 right) as a polyline."""
    d = COL0 + COL_PITCH * j
    i0, i1 = int(math.floor((y0 - CY) / ZIG_Q)) - 1, int(math.ceil((y1 - CY) / ZIG_Q)) + 1
    ys = [CY + ZIG_Q * i for i in range(i0, i1 + 1)]
    return np.array([(AX + sgn * (d + ZIG_A * _tri(y)), y) for y in ys])


def chevrons(inner):
    """The flame-stitch columns as paper strokes, clipped to ``inner``."""
    f = C.Frag()
    for sgn in (-1, 1):
        for j in range(N_COLS):
            ln = LineString(column_pts(j, sgn)).intersection(inner)
            for g in U.lines_in(ln, 6.0):
                f += C.stroke(np.asarray(g.coords), K.MEDIUM, style="rule", role="chevron")
    return f


def course_hatch(inner, *, inset=1.55 + 3.4):
    """FINE horizontal hatch in every other cell between columns, clear of the columns."""
    f = C.Frag()
    for sgn in (-1, 1):
        for j in (0, 2, 4):
            a, b = column_pts(j, sgn), column_pts(j + 1, sgn)
            cell = Polygon(np.vstack([a, b[::-1]])).buffer(0).intersection(inner).buffer(-inset, join_style=2)
            if cell.is_empty:
                continue
            f += U.drop_short(K.hatch_in(cell, angle=0.0, origin=(AX, CY)), 5.0)
    return f


def buttons():
    """The gold button row down the placket (a lattice symmetric about y 525)."""
    f = C.Frag()
    for j in range(-12, 12):
        y = CY + BUTTON_PITCH * (j + 0.5)
        if y < 330.0 or y > 720.0 or 431.0 < y < 490.0 or 560.0 < y < 619.0:
            continue
        c = Point(AX, y).buffer(5.2, quad_segs=24)
        f += K.atomic(K.fill(c, K.GOLD, role="button") + K.outline(c, K.FINE, role="button"), f"btn{j}")
    return f


def strata_panels(region_l, region_r):
    """The K♠ mantle's strata courses (12/19, thin ones hatched) on one common phase symmetric about y 525."""
    f = C.Frag()
    for reg in (region_l, region_r):
        f += MG.strata(reg, y0=519.0, heights=(12.0, 19.0), hatched="thin", angle=C.DIAG, origin=(AX, CY))
    return f


def gold_cells(region, avoid):
    """The plain (thick) strata courses of ``region`` as a list of cells, same phase as ``strata_panels``;
    a course ``avoid`` touches stays jade (a gold course edge landing on the seam leaves sub-pixel slivers
    where the two halves' clips meet; a course beside a sleeve or the cape tip makes the heal cut that
    outline back)."""
    x0, _, x1, _ = region.bounds
    cells = []
    n = int(math.ceil(CY / 31.0)) + 1
    for k in range(-n, n + 1):
        y = 531.0 + 31.0 * k
        cell = region.intersection(K.box(x0 - 5, y, x1 + 5, y + 19.0))
        if not cell.is_empty and not cell.intersects(avoid):
            cells.append((y + 9.5, cell))
    return cells


def pearl_rows(cells, front, pitch=12.0, inset=8.0):
    """A row of ink pearls down the middle of each gold course, on a lattice about the axis (so a pearl's
    180° partner is a pearl); a pearl an item in ``front`` would half hide is left out, and a row that keeps fewer than three is dropped."""
    f = C.Frag()
    for ym, cell in cells:
        safe = cell.buffer(-inset)
        if safe.is_empty:
            continue
        x0, _, x1, _ = safe.bounds
        pts = [(AX + pitch * i, ym) for i in range(int(math.floor((x0 - AX) / pitch)), int(math.ceil((x1 - AX) / pitch)) + 1)]
        pts = [p for p in pts if safe.contains(Point(p)) and not front.contains(Point(p))]
        if len(pts) >= 3:
            for p in pts:
                f += K.dot(p)
    return f


def garments(*, sleeves=None, bands=None, cuff_lines=None, grain=None, edges=None, no_gold=None, front=None):
    """→ Part: the jade body (columns knocked out), panel lines, hatch, strata and buttons; with the jade
    sleeves (its own cloth, grain along the forearm) and their red turn-back bands, all C2 about the centre."""
    b = body()
    zone = K.c2(sleeves) if sleeves is not None else Polygon()
    shape = K.U(b, zone)
    if not zone.is_empty:
        shape = K.U(shape, shape.buffer(12).buffer(-12).intersection(zone.buffer(30)))
    pl, pr = panels()
    dbl = doublet()
    chev = chevrons(dbl)
    btn = buttons()
    turn = K.c2(bands).intersection(shape) if bands is not None else Polygon()
    clear = zone.buffer(-0.8)
    reg_l = pl.buffer(0.8).intersection(b).difference(clear)
    reg_r = pr.buffer(0.8).intersection(b).difference(clear)
    avoid = K.U(no_gold if no_gold is not None else Polygon(), zone.buffer(8.0))
    cells = gold_cells(reg_l, avoid) + gold_cells(reg_r, avoid)
    gold = K.U(*[c for _, c in cells]) if cells else Polygon()
    fills = K.fill(C.knockout(K.D(shape.difference(turn).difference(gold)), chev, btn), K.JADE)
    fills += K.fill(gold, K.GOLD, role="course")
    if bands is not None:
        fills += K.fill(turn.buffer(0.5).intersection(shape), K.RED, role="turnback")
    lines = K.outline(shape)
    for x in (PANEL, 2 * AX - PANEL):
        lines += K.seg((x, TOP), (x, BOTTOM), K.MEDIUM, role="panel")
    lines += course_hatch(dbl)
    bz = K.c2(bands).buffer(5.0) if bands is not None else Polygon()
    lines += strata_panels(reg_l.difference(bz), reg_r.difference(bz))
    lines += pearl_rows(cells, K.c2(front) if front is not None else Polygon())
    lines += btn
    for extra in (cuff_lines, grain, edges):
        if extra is not None:
            lines += K.c2(extra)
    return K.Part(shape, fills, lines, {"panels": (pl, pr), "doublet": dbl})
