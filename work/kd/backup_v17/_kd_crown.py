"""art/_kd_crown.py — K♦ Dome Crown (brief §H.10), after the Hays County
Courthouse dome: a gold brow circlet set with ford stones, an ARCADED DRUM,
a cornice ring, a RIBBED DOME, and a LANTERN FINIAL (arched lantern, cap
dome, finial bead).

A dome is a solid of revolution, so the crown reads the same in profile as
from the front: it is drawn as an elevation, mirror-symmetric about its own
axis ``ax`` (which sits over the profile skull, not on the card axis).
Everything is a compass construction (lines + circular arcs), authored at
final size.

Ribs: the brief's dome has 7 ribs. Seen in elevation, the two outermost
meridians run on the dome's own silhouette; the other five are drawn as
projected meridians (compass arcs through three points of each meridian's
projection), bowing round the dome as a real dome's ribs do.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import shapely

from deck import courtkit as K
from deck.motifs import core as C

FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR
GOLD, RED, INK, JADE = K.GOLD, K.RED, K.INK, K.JADE


@dataclass
class DomeSpec:
    ax: float = 393.0              # crown axis (over the profile skull)
    base: float = 188.0            # bottom of the brow circlet
    circlet_h: float = 16.0
    circlet_hw: float = 56.0
    drum_h: float = 23.0
    drum_hw: float = 46.0
    cornice_h: float = 7.0
    cornice_hw: float = 53.0
    dome_hw: float = 51.0          # dome half-width at its springing
    dome_h: float = 45.0           # springing -> apex
    ribs: int = 5                  # drawn ribs (+ the two limb ribs on the silhouette = 7)
    rib_w: float = MEDIUM
    rib_span: float = 38.0         # azimuth of the outermost drawn rib (deg)
    plinth_hw: float = 21.0        # lantern plinth (the ribs end under it)
    plinth_h: float = 7.0
    lantern_hw: float = 13.0
    lantern_h: float = 12.0
    cap_r: float = 11.0
    finial_d: float = 11.0
    windows: int = 3               # drum arcade openings (foreshortened)
    window_w: float = 13.0
    window_color: str = RED
    stones: int = 5                # ford stones on the circlet


def _arch_d(x, y_foot, w, h):
    """A round-headed opening: jambs + semicircle, standing on y_foot."""
    r = w / 2
    ys = y_foot - (h - r)
    return K.Path((x - r, y_foot)).line((x - r, ys)).sag((x + r, ys), r).line((x + r, y_foot)).close().d


def dome_crown(s: DomeSpec = DomeSpec()) -> K.Part:
    ax = s.ax
    y_c1 = s.base
    y_c0 = y_c1 - s.circlet_h                  # circlet top / drum foot
    y_d0 = y_c0 - s.drum_h                     # drum top / cornice foot
    y_k0 = y_d0 - s.cornice_h                  # cornice top = dome springing
    apex = y_k0 - s.dome_h
    circlet = K.R(K.rrect(ax - s.circlet_hw, y_c0, ax + s.circlet_hw, y_c1, 4.0))
    drum = K.box(ax - s.drum_hw, y_d0 - 1.0, ax + s.drum_hw, y_c0 + 1.0)
    cornice = K.R(K.rrect(ax - s.cornice_hw, y_k0, ax + s.cornice_hw, y_d0, 2.5))
    # dome: one arc through the springing points and the apex (a little more
    # than a half circle when dome_h > dome_hw: the courthouse's full dome)
    L, Rt, A = K.P(ax - s.dome_hw, y_k0 + 1.0), K.P(ax + s.dome_hw, y_k0 + 1.0), K.P(ax, apex)
    dome = K.R(K.Path(L).arc3(A, Rt).close().d)
    # lantern
    y_p1 = apex + 5.0                          # plinth bottom (below the apex: it sits IN the dome)
    y_p0 = y_p1 - s.plinth_h
    plinth = K.R(K.rrect(ax - s.plinth_hw, y_p0, ax + s.plinth_hw, y_p1, 2.0))
    y_l0 = y_p0 - s.lantern_h
    lantern = K.box(ax - s.lantern_hw, y_l0, ax + s.lantern_hw, y_p0 + 1.0)
    cap = K.R(K.Path((ax - s.cap_r, y_l0 + 0.5)).sag((ax + s.cap_r, y_l0 + 0.5), s.cap_r).close().d)
    fin_c = K.P(ax, y_l0 - s.cap_r - s.finial_d / 2 + 1.0)
    finial = shapely.Point(*fin_c).buffer(s.finial_d / 2, quad_segs=24)
    shape = K.U(circlet, drum, cornice, dome, plinth, lantern, cap, finial)

    stones_g = []
    if s.stones:
        ym = (y_c0 + y_c1) / 2
        span = s.circlet_hw - 15.0
        for k in range(s.stones):
            t = -1 + 2 * k / (s.stones - 1)
            stones_g.append(K.R(C.lozenge_d(ax + t * span, ym, 10.0, 5.6)))
    fills = K.fill(shape, GOLD)                  # (stones < 6.8 px wide: no trap hole — it would be < 2.5 px)
    lines = C.Frag()
    # stacked outlines, each hidden where a nearer piece covers it
    front = shapely.Polygon()
    for reg in (circlet, cornice, drum, plinth, dome, lantern, cap, finial):
        ol = K.outline(reg)
        if not front.is_empty:
            ol = K.clip_out(ol, front, eps=-0.8, trap=0.0)
        lines += ol
        front = front.union(reg)

    # ribs: projected meridians. A meridian at azimuth phi on a dome of
    # half-width R and height H projects to x = R sin(phi) cos(t),
    # y = springing - H sin(t); each is the compass arc through its foot, its
    # half-way point and the point where it meets the lantern plinth.
    n = s.ribs
    half = (n - 1) / 2
    phis = [math.radians(s.rib_span * (k - half) / half) if half else 0.0 for k in range(n)]
    yb = y_k0 + 0.5
    yt = y_p1 + 0.8
    t_top = math.asin(min(1.0, (yb - yt) / s.dome_h))
    ins = CONTOUR / 2 + K.GAP_MARK + s.rib_w / 2 + 0.3
    rib_zone = (dome.buffer(-ins).union(K.box(ax - s.dome_hw + ins, y_k0 - 14.0, ax + s.dome_hw - ins, y_k0 + 3.0))
                .union(K.box(0, yt - 4, 2000, yt + 6)))
    for phi in phis:
        sx = s.dome_hw * math.sin(phi)
        pts = [(ax + sx * math.cos(t), yb - s.dome_h * math.sin(t)) for t in (0.0, t_top * 0.5, t_top)]
        if abs(sx) < 1e-6:
            d = f"M{pts[0][0]:.3f} {pts[0][1]:.3f}L{pts[2][0]:.3f} {pts[2][1]:.3f}"
        else:
            d = K.arc3(*pts)
        lines += K.clip_in(K.line(d, s.rib_w, role="rib"), rib_zone)

    # drum arcade: foreshortened round-headed openings, red cut into the gold
    wins = []
    if s.windows:
        hw_ = (s.windows - 1) / 2
        for k in range(s.windows):
            t = (k - hw_) / hw_ if hw_ else 0.0
            phi = t * math.radians(44.0)
            x = ax + (s.drum_hw - 3.0) * math.sin(phi) * 0.95
            w = s.window_w * math.cos(phi) ** 0.8
            wins.append(K.R(_arch_d(x, y_c0 + 0.5, w, s.drum_h - 5.0)))
    if wins:
        wr = K.U(*wins)
        fills += K.fill(wr, s.window_color)
        lines += K.outline(wr)
    # the lantern's frontal opening
    lr = K.R(_arch_d(ax, y_p0 - 2.5, 6.6, s.lantern_h - 4.5))
    fills += K.fill(lr, s.window_color)
    lines += K.outline(lr)
    # ford stones on the circlet: small solid Aquifer lozenges (the ♦ divider's stones)
    for pg in stones_g:
        lines += K.fill(pg, INK, role="stone")
    return K.Part(shape, fills, lines, {"top": float(fin_c[1] - s.finial_d / 2), "apex": apex,
                                        "circlet": circlet, "base": y_c1, "springing": y_k0})
