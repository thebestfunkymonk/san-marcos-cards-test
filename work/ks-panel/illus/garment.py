"""Court garments, built from hand-placed Bézier knots (bez.py) — shared by
all twelve courts. Every builder returns plain geometry (FILL d strings /
Frags) that a court module drops into the Scene as Parts.

    bell_sleeve(mouth, root_outer, root_inner, ...)   forearm + red-lined mouth
    fold(knots, avoid)                                 drapery line + terminal
    standing_collar(half_knots, rim_half, ...)         fan collar + jade rim
    revers(fold_top, vertex, fold_bottom, outer)      turned-back lining (⟩)
    strata_band(sil, y0, cycles, fault)               §G.11 on a bedding plane
    bubble_column(region, ...)                         §G.9 knocked-out bubbles

Construction rules baked in (each learned from QA 12 / 4c on the K♠):
* a sleeve MOUTH is an ellipse whose major axis is perpendicular to the
  forearm; the sleeve body is drawn to the mouth's two ends, so the opening
  reads as a tube end and the wrist always enters its middle;
* a strata band's top and bottom sit on the bedding plane common to both
  sides of the fault (y0 + h0 + (h0+h1)·k), so no course runs a hair's
  breadth beside a boundary, and hatch that would end in a corner wedge is
  dropped (regalia.drop_corner_hatch);
* revers meet only at the clasp centre, so their edges run radially into a
  round clasp and meet its rim square;
* a collar rim is the top edge's own knots moved down (never a translated
  whole outline: its near-vertical sides would double the contour).
"""
from __future__ import annotations

import numpy as np
import shapely

from deck import tokens as T
from deck.motifs import core as MC
from deck.motifs import geometric as MG
from inkkit import geom as G

from bez import K, path, pts, sym, mirror, rev
import regalia as RG

AXIS = 375.0


# ---------------------------------------------------------------------------
# sleeves
# ---------------------------------------------------------------------------
def mouth_d(m):
    """m = ((cx, cy), rx, ry, rot): rx along the major axis (⊥ forearm)."""
    (cx, cy), rx, ry, rot = m
    return G.ellipse_d(cx, cy, rx, ry, rot)


def mouth_ends(m):
    (cx, cy), rx, ry, rot = m
    u = np.array([np.cos(np.radians(rot)), np.sin(np.radians(rot))])
    return np.array([cx, cy]) - u * rx, np.array([cx, cy]) + u * rx


def bell_sleeve(m, root_a: K, root_b: K, *, a_dirs=(-46, 40), b_dirs=(40, 72), a_li=34.0, b_lo=12.0,
                cuff=15.0):
    """A forearm sleeve from two root knots (below the band / under the
    mantle) to the mouth ``m``. ``root_a`` joins the mouth's first end,
    ``root_b`` its second; ``a_dirs``/``b_dirs`` are the (arrive, leave)
    travel directions at the two mouth ends. Returns dict:
      sil      the sleeve silhouette (body ∪ mouth)
      body     sil minus the cuff band (jade)
      cuff     the red turned-back cuff band (``cuff`` px round the mouth)
      cuff_line  the band's edge line (MEDIUM, clipped to the sleeve)
      mouth    the mouth ellipse (red lining; the wrist enters it)"""
    p0, p1 = mouth_ends(m)
    body = path([root_a, K(*p0, ai=a_dirs[0], ao=a_dirs[1], li=a_li),
                 K(*p1, ai=b_dirs[0], ao=b_dirs[1], lo=b_lo), root_b], closed=True)
    sil = G.union(body, mouth_d(m))
    ring = G.offset(mouth_d(m), cuff)
    band = G.intersection(sil, ring)
    line = MC.clip(MC.stroke(ring, T.MEDIUM, role="cuff"), sil)
    return dict(sil=sil, body=G.difference(sil, band), cuff=band, cuff_line=line,
                mouth=mouth_d(m), cuff_edge=G.from_shape(MC.region(ring).boundary.buffer(T.MEDIUM / 2)))


def fold(knots, avoid=None, *, w=T.MEDIUM):
    """A drapery fold that stops a clear 3 px short of ``avoid`` (e.g. a
    cuff band's edge line) and ends in a Ø6.3 terminal (§B.2)."""
    f = MC.stroke(path(knots), w, role="fold")
    if avoid:
        f = MC.cut(f, avoid, gap=3.0 + w / 2 + T.TERMINAL_D / 2)
    out = MC.Frag()
    for m in f.marks:
        for p_, _ in G.flatten(m.d, 0.05):
            if len(p_) > 1 and G.Curve(p_).length > 8:
                out += MC.stroke(p_, w, role="fold") + MC.terminal(*p_[-1])
    return out


# ---------------------------------------------------------------------------
# collar, revers
# ---------------------------------------------------------------------------
def standing_collar(half, rim_half):
    """A standing (fan) collar, symmetric about the axis. ``half`` = its LEFT
    outline knots, top-on-axis → foot-on-axis (bez.sym); ``rim_half`` = the
    rim line's LEFT knots (the top edge moved down, starting just outside the
    collar's side). Returns dict(sil, red, rim, rim_line) — the lining is red,
    the turned-over rim jade (the mantle's outside)."""
    sil = sym(half)
    line_knots = list(rim_half) + rev(mirror(rim_half))[1:]
    below = G.poly_d(np.vstack([pts(line_knots), [(AXIS + 425, 900), (AXIS - 425, 900)]]), closed=True)
    rim = G.difference(sil, below)
    return dict(sil=sil, red=G.difference(sil, rim), rim=rim,
                rim_line=MC.stroke(path(line_knots), T.MEDIUM, role="collar-rim"))


def revers(fold_top, vertex, fold_bottom, band_y, outer_bottom_x, outer_mid, outer_top, side=-1):
    """The mantle's front edge turned back to show the lining (LEFT side;
    ``side`` +1 mirrors). The fold line (inner edge) runs fold_top → the
    clasp ``vertex`` → fold_bottom (a ⟩); the outer edge rises from
    (outer_bottom_x, band_y) through ``outer_mid`` to ``outer_top``. Knots
    are (x, y, dir_in, dir_out)."""
    (xt, yt), (vx, vy), (xb, yb) = fold_top, vertex, fold_bottom
    left = path([K(xt, yt, ai=180, ao=68, lo=24),
                 K(vx + 0.5, vy, ai=66, ao=104, li=26, lo=30),
                 K(xb, yb, ai=104, ao=180, li=50),
                 K(outer_bottom_x, band_y, ai=180, ao=-70),
                 K(*outer_mid, -78, li=66, lo=30),
                 K(*outer_top, ai=-94, ao=0, li=30)], closed=True)
    return left if side < 0 else G.mirror_x(left, AXIS)


def bubble_column(region_d, *, y_start, y_stop, d0=4.2, ratio=1.2, d_max=8.4, gap=3.6,
                  side=-1, avoid=None, edge_w=T.MEDIUM):
    """§G.9 bubbles rising (×``ratio``) up the mid-line of ``region_d`` (the
    LEFT one; ``side`` +1 mirrors the positions), as FILL holes to knock out
    of a solid (§C.4 patterns on red). Every hole keeps >= 3 px of solid to
    the region's edge contour and to its neighbours; holes whose clearance
    zone meets ``avoid`` (things in front) are skipped."""
    rv = MC.region(region_d)
    holes = []
    y, d = y_start, d0
    while y > y_stop and d < 99:
        ln = shapely.LineString([(0, y), (AXIS + 5, y)]).intersection(rv)
        if ln.is_empty:
            break
        x0, _, x1, _ = ln.bounds
        x = (x0 + x1) / 2
        if (x1 - x0) / 2 - d / 2 - edge_w / 2 < 3.0:
            break
        xx = x if side < 0 else 2 * AXIS - x
        if avoid is None or not avoid.intersects(shapely.Point(xx, y).buffer(d / 2 + 3.0 + edge_w / 2 + 0.5)):
            holes.append(G.circle_d(xx, y, d / 2))
        nd = min(d * ratio, d_max)
        y -= d / 2 + gap + nd / 2
        d = nd if d < d_max else 99
    return G.union(*holes) if holes else ""


# ---------------------------------------------------------------------------
# strata (§G.11) on a bedding plane
# ---------------------------------------------------------------------------
def strata_band(sil, y0, cycles=2, *, heights=(12.0, 19.0), fault=None):
    """§G.11 strata across ``sil`` in a horizontal band whose top and bottom
    lie on the bedding plane common to both sides of a one-course fault jog:
    top = y0 + h0, bottom = top + cycles·(h0 + h1). Hatch that would end in a
    corner wedge is dropped. Returns (Frag, (top, bottom))."""
    h0, h1 = heights
    top = y0 + h0
    bot = top + cycles * (h0 + h1)
    reg = G.intersection(sil, G.rect_d(AXIS - 300, top - 0.02, 600, bot - top + 0.04))
    f = MG.strata(reg, heights=heights, y0=y0, fault=fault, jog=h0)
    return RG.drop_corner_hatch(f), (top, bot)
