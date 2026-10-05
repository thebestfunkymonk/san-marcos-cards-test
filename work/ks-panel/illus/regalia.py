"""Court regalia, built once and shared: crown base, orb, banded sceptre,
jewel rosettes and the simplified Lion Mark hallmark.

Each builder returns a ``Piece``: silhouette (FILL d) + flat fills
[(d | None, colour)] + interior lines (Frag). Silhouette contours are left
to the Scene (CONTOUR by default), so pieces stay composable and occlude
correctly.

The Lion Mark is drawn locally because ``deck.motifs`` has no ``lion_mark``
yet (checked 2026-09-22); swap in ``M.lion_mark`` when Track B lands it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import shapely

from deck import tokens as T
from deck.motifs import core as MC
from deck.motifs import geometric as MG
from inkkit import geom as G

from bez import K, path, sym, open_sym, mirror


@dataclass
class Piece:
    sil: str
    fills: list = field(default_factory=list)
    lines: MC.Frag = field(default_factory=MC.Frag)
    anchors: dict = field(default_factory=dict)
    parts: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# jewels
# ---------------------------------------------------------------------------
def jewel(cx, cy, r=13.0, *, centre=T.RED, ribs=6, w=T.FINE, dot_r=4.2) -> Piece:
    """A small Source Rosette jewel (§G.1 reduced, D2-safe straight ribs):
    gold disc with straight ribs running from the centre dot's ring to the
    rim (joined, so no near-miss gaps), and a coloured Ø8.4 centre dot that
    is a HOLE in the gold (gold prints above red: §I.25, QA 4c)."""
    sil = G.circle_d(cx, cy, r)
    f = MC.Frag()
    for k in range(ribs):
        a = -90 + 360.0 * k / ribs + 180.0 / ribs
        p0, p1 = MC.polar(cx, cy, dot_r, a), MC.polar(cx, cy, r, a)
        f += MC.stroke(np.array([p0, p1]), w, role="rib")
    dot = G.circle_d(cx, cy, dot_r)
    fills = [(G.difference(sil, dot), T.FOIL), (dot, centre)]
    f += MC.stroke(dot, T.FINE, role="jewel-dot")
    return Piece(sil, fills, f)


def hatch_clean(region, angle=MC.DIAG, *, origin=None, w=T.FINE, edge_w=T.MEDIUM, clear=3.0):
    """FINE hatch (§B.2) that never leaves a sub-resolution wedge: a line
    whose end lands on one edge a few px from a corner would run beside the
    corner's other edge closer than ``clear`` px (QA 12). Such lines are
    dropped; lines through the corner itself are kept (they join both)."""
    g = MC.region(region)
    verts = np.vstack([np.asarray(p.exterior.coords) for p in MC._polys(g)])
    R = (clear + w / 2 + edge_w / 2) / math.sin(math.radians(45)) + 0.5
    keep = []
    for ln in MC.hatch_lines(g, angle, origin=origin):
        ok = True
        for e in (ln[0], ln[-1]):
            dd = np.hypot(*(verts - e).T)
            if ((dd > 0.6) & (dd < R)).any():
                ok = False
        if ok:
            keep.append(ln)
    return MC.stroke(keep, w, style="hatch", role="hatch") if keep else MC.Frag()


def drop_corner_hatch(f: MC.Frag, *, w=T.FINE, edge_w=T.CONTOUR, clear=3.0) -> MC.Frag:
    """Post-filter a pattern Frag (e.g. ``geometric.strata``): drop hatch lines
    that end within a corner's wedge zone — the corners being where its
    course / fault lines end on the region's contour. Lines through a corner
    are kept. Same rule as ``hatch_clean``."""
    corners = []
    for m in f.marks:
        if m.kind == "stroke" and m.role in ("course", "fault", "rule"):
            for p_, closed in G.flatten(m.d, 0.05):
                if not closed and len(p_) > 1:
                    corners += [p_[0], p_[-1]]
    if not corners:
        return f
    C = np.array(corners)
    R = (clear + w / 2 + edge_w / 2) / math.sin(math.radians(45)) + 0.5
    out = []
    from dataclasses import replace as _r
    for m in f.marks:
        if m.kind == "stroke" and m.role == "hatch":
            keep = []
            for p_, closed in G.flatten(m.d, 0.05):
                ok = True
                for e in (p_[0], p_[-1]):
                    dd = np.hypot(*(C - e).T)
                    if ((dd > 0.6) & (dd < R)).any():
                        ok = False
                if ok:
                    keep.append(MC.polyline_d(p_))
            if keep:
                out.append(_r(m, d="".join(keep)))
            continue
        out.append(m)
    return MC.Frag(out, f.meta)


# ---------------------------------------------------------------------------
# crown base: band + merlons (the Escarpment Crown uses 5 limestone merlons)
# ---------------------------------------------------------------------------
def crown(cx, band_top, *, width=136.0, band_h=26.0, merlon_w=19.0, tops=(130.0, 114.0, 96.0),
          merlons=5, merlon_color=None, hatch_side="left", coping=2.5, jewel_r=13.0,
          rims=True, taper=0.0) -> Piece:
    """Band (gold) with rims, carrying ``merlons`` merlons whose tops step up
    to the centre (``tops`` outer → centre, absolute y). Merlons are limestone
    (paper, ``merlon_color`` None) or a colour; each is split on its axis and
    one half hatched at 45° (§H.1). ``coping`` px caps each merlon with a
    slightly wider coping stone (a fault-step on each side). Perfectly
    symmetric about cx."""
    x0 = cx - width / 2
    band = G.rect_d(x0, band_top, width, band_h)
    gap = (width - merlons * merlon_w) / (merlons - 1)
    ms, parts, lines = [], [], MC.Frag()
    for i in range(merlons):
        lvl = min(i, merlons - 1 - i)
        top = tops[lvl]
        mx = x0 + i * (merlon_w + gap)
        # battered like a limestone wall: ``taper`` px narrower each side at the top
        body = G.poly_d([(mx + taper, top), (mx + merlon_w - taper, top),
                         (mx + merlon_w, band_top + 2), (mx, band_top + 2)], closed=True)
        m = G.union(body, G.rect_d(mx - coping, top, merlon_w + 2 * coping, 7.0)) if coping else body
        ms.append(m)
        parts.append((m, mx, top))
    sil = G.union(band, *ms)
    fills = [(band, T.FOIL)]
    for m, mx, top in parts:
        if merlon_color:
            fills.append((m, merlon_color))
        if coping:
            lines += MC.stroke(np.array([(mx - coping, top + 7), (mx + merlon_w + coping, top + 7)]),
                               T.MEDIUM, role="coping")
        # half-hatch: split on the merlon axis, hatch one half
        xm = mx + merlon_w / 2
        lines += MC.stroke(np.array([(xm, top), (xm, band_top)]), T.MEDIUM, role="split")
        half = G.poly_d([(mx + taper, top), (xm, top), (xm, band_top), (mx, band_top)], closed=True) \
            if hatch_side == "left" else \
            G.poly_d([(xm, top), (mx + merlon_w - taper, top), (mx + merlon_w, band_top), (xm, band_top)], closed=True)
        # one hatch line runs exactly through the half's lower corner, so no
        # line end lands a hair's breadth beside the joint (QA 12 wedges)
        corner = (mx, band_top) if hatch_side == "left" else (xm, band_top)
        lines += hatch_clean(half, MC.DIAG, origin=corner)
        # the bed joint where the merlon sits on the band
        lines += MC.stroke(np.array([(mx, band_top), (mx + merlon_w, band_top)]), T.MEDIUM, role="joint")
    if rims:
        # band rims: an upper and a lower fillet line
        lines += MC.stroke(np.array([(x0, band_top + 6.5), (x0 + width, band_top + 6.5)]), T.MEDIUM, role="rim")
        lines += MC.stroke(np.array([(x0, band_top + band_h - 6.5), (x0 + width, band_top + band_h - 6.5)]),
                           T.MEDIUM, role="rim")
    p = Piece(sil, fills, lines, dict(band=(x0, band_top, width, band_h)))
    if jewel_r:
        # the brow jewel hangs from the band over the forehead: >= 4.2 px clear
        # of the merlon joints above, crossing the band's lower edge cleanly
        j = jewel(cx, band_top + band_h, jewel_r)
        p.parts["jewel"] = j
    return p


# ---------------------------------------------------------------------------
# orb: gold sphere, ripple latitudes spreading from a single bubble on top
# ---------------------------------------------------------------------------
def orb(cx, cy, r=31.0, *, bubble_d=17.0, n_lat=3, ratio=1.3, sag=0.22) -> Piece:
    """§H.1 orb: a gold sphere whose latitudes are ripple rings (gaps growing
    ×``ratio`` downward from the pole, like rings spreading from the source)
    with a single bubble in place of a cross."""
    sph = G.circle_d(cx, cy, r)
    # the bubble floats free above the pole, one clear gap (4.2) between the
    # two CONTOUR edges: it has just left the vent
    by = cy - r - T.CONTOUR - 4.2 - bubble_d / 2
    bub = G.circle_d(cx, by, bubble_d / 2)
    sil = G.union(sph, bub)
    f = MC.Frag()
    # latitudes: first at 0.30 r below the pole, gaps ×ratio
    g0 = r * 0.42
    yy = cy - r + g0
    g = g0
    for k in range(n_lat):
        half = math.sqrt(max(r * r - (yy - cy) ** 2, 0))
        if half < 8:
            break
        s = sag * half
        f += MC.clip(MC.stroke(path([K(cx - half - 2, yy - s * 0.2, ao=35, lo=half * 0.5),
                                     K(cx, yy + s, 0, li=half * 0.55, lo=half * 0.55),
                                     K(cx + half + 2, yy - s * 0.2, ai=-35, li=half * 0.5)]),
                               T.MEDIUM if k == 1 else T.FINE, role="latitude"), sph)
        g *= ratio
        yy += g
    br = bubble_d / 2
    return Piece(sil, [(None, T.FOIL)], f, dict(bubble=(cx, by), top=by - br))


# ---------------------------------------------------------------------------
# sceptre: banded core with a rosette finial
# ---------------------------------------------------------------------------
SEG_KINDS = ("strata", "chert", "marl")


def _segment(kind, x, y0, y1, w, lines: MC.Frag):
    """One core segment between two bead collars (y0..y1 = the clear shaft
    between the collars' edges). Every mark either joins the shaft contour or
    keeps >= 3 px of paper-gold from it (QA 12)."""
    x0, x1 = x - w / 2, x + w / 2
    h = y1 - y0
    if kind == "strata":
        # a thin course (hatched) between two bedding lines, joined to the contour
        ya, yb = y0 + h * 0.36, y0 + h * 0.36 + 9.0
        lines += MC.stroke(np.array([(x0, ya), (x1, ya)]), T.FINE, style="rule", role="course")
        lines += MC.stroke(np.array([(x0, yb), (x1, yb)]), T.FINE, style="rule", role="course")
        lines += MC.hatch(G.rect_d(x0, ya, w, yb - ya), MC.DIAG, origin=(x, ya))
    elif kind == "chert":
        # a chert nodule: one vesica on the axis
        lines += MC.stroke(MC.vesica_d((x, y0 + 6.2), (x, y1 - 6.2), 8.4), T.FINE, style="point", role="chert")
    elif kind == "marl":
        # marl: staggered short dashes, clear of contour and collars
        top, bot = y0 + 5.8, y1 - 5.8
        n = max(2, int((bot - top) // 7.5) + 1)
        for k in range(n):
            yy = top + k * (bot - top) / max(n - 1, 1)
            dx = 1.9 if k % 2 else -1.9
            lines += MC.stroke(np.array([(x + dx - 2.4, yy), (x + dx + 2.4, yy)]), T.FINE, role="marl")


def sceptre(x, y_top, y_bot, *, w=18.0, finial_r=25.0, segs=7, seg_bottom=None, collar=8.0,
            bead=2.0) -> Piece:
    """The core sceptre: ``segs`` banded segments (strata, chert, marl,
    repeated) between raised bead collars, a stepped capital, and a small
    Source Rosette finial (gold, ink ribs, a red centre that is a hole in the
    gold). Vertical at x from the finial top y_top down to y_bot."""
    fr = finial_r
    fcy = y_top + fr
    finial = G.circle_d(x, fcy, fr)
    cap_top = fcy + fr - 3
    cap = G.union(G.rect_d(x - w / 2 - 8, cap_top, w + 16, 13), G.rect_d(x - w / 2 - 4, cap_top + 13, w + 8, 8))
    shaft_top = cap_top + 21
    shaft = G.rect_d(x - w / 2, shaft_top - 1, w, y_bot - shaft_top + 1)
    y_end = seg_bottom if seg_bottom else y_bot
    L = (y_end - shaft_top) / segs
    beads = []
    k = 1
    while shaft_top + k * L < y_bot + 20:
        yc = shaft_top + k * L
        beads.append(G.rect_d(x - w / 2 - bead, yc - collar / 2, w + 2 * bead, collar))
        k += 1
    sil = G.union(finial, cap, shaft, *beads)
    lines = MC.Frag()
    lines += MC.stroke(np.array([(x - w / 2 - 4, cap_top + 13), (x + w / 2 + 4, cap_top + 13)]), T.MEDIUM, role="cap")
    lines += MC.stroke(np.array([(x - w / 2, shaft_top), (x + w / 2, shaft_top)]), T.MEDIUM, role="cap")
    kk = 0
    while True:
        s0 = shaft_top + (kk * L + (collar / 2 if kk else 0.0))
        s1 = shaft_top + (kk + 1) * L - collar / 2
        if s0 >= y_bot:
            break
        _segment(SEG_KINDS[kk % 3], x, s0, min(s1, y_bot + 40), w, lines)
        kk += 1
    # finial: reduced Source Rosette with every ring >= 3 px clear of the next
    rh, rc, rd = 5.6, 11.4, 17.6               # hub (= red dot), crater rim, bead ring
    f = MC.stroke(G.circle_d(x, fcy, rh), T.FINE, role="hub")
    f += MC.stroke(G.circle_d(x, fcy, rc), T.FINE, role="rim")
    for kq in range(8):
        a = -90 + 45 * kq + 22.5
        f += MC.stroke(np.array([MC.polar(x, fcy, rh, a), MC.polar(x, fcy, rc, a)]), T.FINE, role="rib")
    for kq in range(12):
        f += MC.dot(*MC.polar(x, fcy, rd, -90 + 30 * kq + 15), 4.2)
    lines += f
    dot = G.circle_d(x, fcy, rh)
    fills = [(G.difference(sil, dot), T.FOIL), (dot, T.RED)]
    return Piece(sil, fills, lines, dict(finial=(x, fcy), shaft_top=shaft_top),
                 parts=dict(finial=finial, cap=cap, shaft=shaft))


# ---------------------------------------------------------------------------
# simplified Lion Mark (§G.2): ≤ 40 px, gold, ≤ 24 strokes
# ---------------------------------------------------------------------------
def lion_mark(cx, cy, size=40.0) -> Piece:
    """Simplified Lion Mark (§G.2), ≤ 40 px, gold with Aquifer lines, built so
    every clearance holds at this size (QA 12):
      * mane — a 12-scallop ring round the head (the silhouette's middle),
      * face — a FINE circle inside it,
      * wings — two sickles rising from behind the mane and curling in over
        the head until they meet (an arch); their three primaries are the
        scallops of the outer edge,
      * a ripple line beneath (returned separately; place it only where it
        has room).
    ``size`` is the overall height (wing tips → ripple)."""
    k = size / 40.0                                     # layout only; strokes stay at token widths
    P = lambda dx, dy: (cx + dx * k, cy + dy * k)
    mc = P(0, 1.0)
    R, n = 11.8 * k, 12
    pts_ = []
    for i in range(n * 16):
        a_ = 2 * math.pi * i / (n * 16)
        rr = R + 1.8 * abs(math.sin(n * a_ / 2))
        pts_.append((mc[0] + rr * math.sin(a_), mc[1] - rr * math.cos(a_)))
    mane = G.poly_d(np.array(pts_), True)
    # left wing: root behind the mane, three primary scallops on the outer
    # edge, tip curling in over the head
    wing_l = path([K(*P(-7, 5), ai=0, ao=196, li=4, lo=5),
                   K(*P(-17.5, 1.5), ai=200, ao=250, li=3, lo=2.5),      # primary 1
                   K(*P(-19.5, -4.5), ai=200, ao=260, li=3, lo=2.5),     # primary 2
                   K(*P(-19, -11), ai=210, ao=-80, li=3, lo=3),          # primary 3
                   K(*P(-11, -18.5), -20, li=5, lo=5),
                   K(*P(0.6, -20), 0, li=5),                             # the wings meet over the head
                   K(*P(0.6, -14.5), ai=90, ao=180),
                   K(*P(-6.5, -12.5), 160, li=3, lo=3),                  # inner edge, tucked into the mane
                   K(*P(-8.2, -6), 95, li=3, lo=4)], closed=True)
    wings = G.union(wing_l, G.mirror_x(wing_l, cx))
    sil = G.union(wings, mane)
    f = MC.Frag()
    f += MC.stroke(G.circle_d(mc[0], mc[1], 4.9 * k), T.FINE, role="face")
    # ripple line under the mark (separate from the silhouette, >= 3 px clear)
    ry = mc[1] + R + 1.8 + T.MEDIUM / 2 + 3.2 + T.FINE / 2
    rip = open_sym([K(cx - 11 * k, ry + 1.2, ao=-35, lo=3), K(cx - 5.5 * k, ry - 0.6, 25, li=3, lo=3),
                    K(cx, ry + 1.4, 0, li=3)], cx)
    over = MC.stroke(rip, T.FINE, role="ripple")
    return Piece(sil, [(None, T.FOIL)], f, dict(ripple=over))


def lion_roundel(cx, cy, r=18.2) -> Piece:
    """The Lion Mark as a ≤ 40 px clasp (§G.2 simplified, §H.1 throat clasp):
    a 12-scallop mane ring (the silhouette, gold, MEDIUM contour) and, inside
    it, the face circle, two wing arcs rising from the face's sides and
    curling in over the head, and a ripple line beneath.

    Radii are solved so every interior mark keeps >= 3 px of gold from its
    neighbours and the rim, and >= 4.2 px where two run parallel (QA 12):
      face fr = 4.2 (FINE), wings wr = fr + FINE + 4.3, rim valley r.
    At this size the wings' five primaries are left out (they cannot hold
    the gaps); the wings are single arcs."""
    n = 12
    pts_ = []
    for i in range(n * 16):
        a_ = 2 * math.pi * i / (n * 16)
        rr = r + 1.6 * abs(math.sin(n * a_ / 2))
        pts_.append((cx + rr * math.sin(a_), cy - rr * math.cos(a_)))
    sil = G.poly_d(np.array(pts_), True)
    f = MC.Frag()
    fr, fy = 4.2, cy - 1.5
    f += MC.stroke(G.circle_d(cx, fy, fr), T.FINE, role="face")
    wr = fr + T.FINE + 4.3
    for a0, a1 in ((196, 246), (294, 344)):
        f += MC.stroke(G.arc_pts(cx, fy, wr, a0, a1, n=40), T.FINE, role="wing")
    ry = fy + fr + T.FINE / 2 + 3.0 + T.FINE / 2 + 0.7
    rip = open_sym([K(cx - 5.0, ry + 0.6, ao=-28, lo=1.8), K(cx - 2.5, ry - 0.5, 18, li=1.6, lo=1.6),
                    K(cx, ry + 0.6, 0, li=1.6)], cx)
    f += MC.stroke(rip, T.FINE, role="ripple")
    return Piece(sil, [(None, T.FOIL)], f)
