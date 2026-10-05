"""art/AH.py: A♥ · The Fount (brief §H.14).

A Gill Red heart (u 280 × 1.04) with its emblem knocked out to paper in
MEDIUM line, 14 px or more inside the edge (paper holes, never paint):

* two offset heart contours at a 12 px pitch — the banks of the pool;
* the Source Rosette (§G.1 reduced to r 40, straight ribs so it stays
  mirror-true) low on the centreline, keeping the back's signature: a free
  hub dot inside the crater, whose 8 straight ribs run in from its rim and
  stop short of the hub (an iris — hub ring + spokes read as a dartboard),
  and the ring of OUTLINED bubbles round the crater (§G.1's bubble ring);
* a column of five graduated bubbles (§G.9, growing ×1.45 as they rise) from
  the crater, out through the halo, to just below the cleft.

The inner contour runs down into the vent: its straight sides meet the
vent's rim TANGENTIALLY and it closes round the vent's lower half, so the
pool deepens to the spring. That lower arc IS the rosette's outer rule
(r 38.45, the rosette's r 40 to the paper edge); above it the rosette is
open to the pool, so the bubbles rise free instead of hanging from a
closed medallion (a closed ring on the axis read as a locket on a chain).
The rosette's centre is solved for the tangency (not hand-set).

Outside, in gold FINE line: the keyline, and three ripple ellipses under
the point, as if the heart had just broken the surface — they pass behind
the heart and stop 4.2 px short of the keyline.

Deviations (geometry the brief's numbers cannot satisfy together):
* Rosette centre y ≈ 505 (brief "≈ 540"): at y 540 the heart is 85 px
  across inside its 14 px margin, and an r-40 rosette cannot sit there.
* Ripple ry 8 / 14.3 / 20.6 (brief 8 / 12 / 16): the brief's 4 px steps
  leave 1.9 px between FINE lines on the minor axis (§I.12 wants 4.2); each
  ellipse is 6.3 px taller than the last, so the gap is exactly 4.2.
* The inner contour is the offset heart above the vent and the vent's rim
  below it (see above), not a sharp-pointed offset all the way down.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.ops import nearest_points

from deck import tokens as T
from deck import motifs as M
from deck.cardsvg import layers_merge
from inkkit import geom as G

from art import _aces_common as A

W = A.KO                                  # 3.1 knockout line
CL = A.CLEAR                              # 4.2 red between parallel paper lines
SUIT = "H"
HEART = A.pip_d(SUIT)
_X0, _TOP, _X1, TIP_Y = G.bbox(HEART)     # top 336.05, tip 603.95
_U = 280.0 * 1.04                         # §E.1 optical heart
CLEFT_Y = _TOP + 0.26 * _U - math.sqrt((0.26 * _U) ** 2 - (0.24 * _U) ** 2)    # 382.7

C1 = A.EDGE + W / 2                       # outer contour centreline inset: paper 14 px from the edge
C2 = C1 + 12.0                            # §H.14: 12 px pitch

# Source Rosette, r 40 overall (outer rule's outer edge), MEDIUM knockout,
# keeping the back's signature (§G.1, §H.19) at this size: the crater — a
# free hub dot and 8 straight ribs running IN from the crater rim and
# stopping short of it, an iris, not the spokes of a wheel — then the ring of
# OUTLINED bubbles, then the outer rule. Neighbours keep >= 3 px of red.
R_OUT = 40.0
R_RULE = R_OUT - W / 2                    # 38.45 outer rule
D_HUB = 6.3                               # hub dot
R_RIM = 19.3                              # crater rim (centreline)
R_RIB_IN = 8.3                            # ribs run from the rim in to here (3.4 px of red between them)
N_RIBS = 8
D_BUB, N_BUB = 9.4, 12                    # bubble ring: 12 outlined bubbles (the 12 o'clock one left out)
R_BUB = 28.9                              # 3.35 px of red to the rim, 3.3 to the rule; eyes 3.2

# bubble column (§G.9): sizes grow ×Q as the bubbles rise, gaps grow too
N_COL, Q = 5, 1.45                        # ×1.45 per bubble: the growth must read at 25 %
GAP_Q = 1.15                              # the gaps widen as the bubbles rise
GAP_END = 3.6                             # a bubble only approaches a line (§I.12: 3.0, + margin)

# §H.14 gold ripples
RIPPLE_RX = (60.0, 90.0, 120.0)
RIPPLE_RY = (8.0, 14.3, 20.6)
RIPPLE_DY = 24.0


def rosette(cx: float, cy: float) -> M.Frag:
    """The reduced Source Rosette: straight ribs (D2, mirror-true), the free
    hub, the crater rim and the ring of outlined bubbles (each a paper ring
    with a red eye, as on the back), the 12 o'clock bubble left out where the
    column rises. Its outer rule is drawn by :func:`pool_contour` (the
    vent's rim)."""
    f = M.dot(cx, cy, D_HUB, role="hub")
    ribs = "".join(M.polyline_d([M.polar(cx, cy, R_RIM, a), M.polar(cx, cy, R_RIB_IN, a)])
                   for a in np.arange(-90.0 + 22.5, 270.0, 360.0 / N_RIBS))
    f += M.stroke(ribs, W, role="rib")
    f += M.stroke(M.circle_d(cx, cy, R_RIM), W, role="crater")
    for k in range(1, N_BUB):
        p = M.polar(cx, cy, R_BUB, -90.0 + 360.0 / N_BUB * k)
        f += M.stroke(M.circle_d(p[0], p[1], (D_BUB - W) / 2), W, role="bubble")
    return f


def tangent_centre(inner_d: str) -> float:
    """Rosette centre on the axis at which the inner contour's straight sides
    are tangent to the rosette's outer rule (both centrelines)."""
    ring = G.to_shape(inner_d, tol=0.01).exterior
    lo, hi = CLEFT_Y + 60.0, TIP_Y - 30.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if shapely.Point(A.CX, mid).distance(ring) > R_RULE:
            lo = mid
        else:
            hi = mid
    return lo


def pool_contour(inner_d: str, cy: float) -> str:
    """The inner contour as ONE closed line: the offset heart down to the
    points where its straight sides touch the vent's rim (r ``R_RULE``, the
    rosette's outer rule), then that rim round the bottom."""
    shape = G.to_shape(inner_d, tol=0.01)
    foot = nearest_points(shapely.Point(A.CX, cy), shape.exterior)[1]
    upper = shape.intersection(shapely.box(0, 0, 750, foot.y))
    disk = shapely.Point(A.CX, cy).buffer(R_RULE, quad_segs=256)
    return G.from_shape(shapely.union_all([upper, disk]).buffer(0))


def column(y_bottom: float, y_top: float) -> M.Frag:
    """Five bubbles filling y_top..y_bottom (outer extents), diameters growing
    ×Q upward and the gaps between them growing ×GAP_Q from 3.0; a bubble
    whose paper ring would keep a >= 3 px red eye is drawn as a ring. A
    steep growth (Ø ≈ 4 → 19) so the column reads as bubbles rising and
    swelling, never as a chain of even beads."""
    n = N_COL
    gaps = [GAP_END * GAP_Q ** k for k in range(n - 1)]
    s0 = (y_bottom - y_top - sum(gaps)) / sum(Q ** k for k in range(n))
    f = M.Frag()
    y = y_bottom
    sizes = []
    for k in range(n):
        s = s0 * Q ** k
        if s - 2 * W >= 3.0:                           # ring: outer s, centreline s - W
            f += M.stroke(M.circle_d(A.CX, y - s / 2, (s - W) / 2), W, role="bubble")
        else:
            f += M.dot(A.CX, y - s / 2, s, role="bubble")
        sizes.append(round(s, 2))
        y -= s + (gaps[k] if k < n - 1 else 0.0)
    f.meta["sizes"] = sizes
    return f


def ripples() -> M.Frag:
    cy = TIP_Y + RIPPLE_DY
    f = M.Frag()
    for rx, ry in zip(RIPPLE_RX, RIPPLE_RY):
        f += M.stroke(M.ellipse_arc_d(A.CX, cy, rx, ry, 0, 360) + "Z", T.FINE, color=T.FOIL, role="ripple")
    return A.behind(f, SUIT)


def emblem() -> M.Frag:
    outer = M.stroke(A.inset_d(SUIT, C1), W, style="point", role="contour")
    inner_d = A.inset_d(SUIT, C2)
    ros_y = tangent_centre(inner_d)
    inner = M.stroke(pool_contour(inner_d, ros_y), W, role="contour")
    # the column rises from just above the crater rim, out through the gap
    # in the halo, to just below the inner contour's cleft
    # the inner contour's own cleft (the offset of a sharp cleft sits lower
    # than CLEFT_Y + C2), measured on the axis
    cleft = G.to_shape(inner_d, tol=0.01).exterior.intersection(
        shapely.LineString([(A.CX, CLEFT_Y), (A.CX, CLEFT_Y + 80.0)]))
    y_cleft = min(p.y for p in getattr(cleft, "geoms", [cleft]))
    y_top = y_cleft + W / 2 + GAP_END
    y_bottom = ros_y - R_RIM - W / 2 - GAP_END
    col = column(y_bottom, y_top)
    ros = rosette(A.CX, ros_y)
    f = outer + inner + ros + col
    f.meta.update(rosette_y=ros_y, column=col.meta["sizes"])
    return f


def build():
    pip = A.knocked_pip(SUIT, emblem(), color=T.RED)
    gold = A.keyline(SUIT) + ripples() + A.caption(SUIT)
    return layers_merge((pip + gold).fragments())
