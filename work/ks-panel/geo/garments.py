"""Mantle, lapels (collar lining), tunic and sleeves — compass construction.

The body is one figure of large circles:

* the TUNIC is a vesica (two arcs of one radius) whose tips are the throat
  (375, throat_y) and its 180° image (375, 1050 − throat_y); it is therefore
  two-headed by construction and reads as the Spring Lake lens through the
  card centre;
* each LAPEL (the red lining turned back) is the band between a vesica arc and
  its concentric offset — uniform width, exact circles;
* the MANTLE's outer contour is a tangent arc chain: a long yoke arc from the
  neck, a straight shoulder run, a shoulder-corner arc and a flared drop;
* SLEEVES are panels between two concentric arcs, rising from the waist band
  to the wrist, ended by a cuff band between two radii.

    lens(LensSpec) -> dict        vesica geometry (centres, radius)
    tunic(LensSpec) -> Part
    lapel(LensSpec, side) -> Part
    mantle(MantleSpec) -> Part
    sleeve(SleeveSpec, color) -> (Part sleeve, Part cuff)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import shapely

import kit as K
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import geometric as M
from hair import Part


# =============================================================================
# the lens (tunic) and lapels
# =============================================================================
@dataclass
class LensSpec:
    cx: float = 375.0
    throat_y: float = 318.0     # upper tip of the vesica
    half_w: float = 23.0        # half-width at the card centre line (y 525)
    lapel_w: float = 56.0       # lapel band width (radial) at the waist
    top_cut: float = 286.0      # lapels are hidden above this (under beard and hair)


def lens(s: LensSpec = LensSpec()):
    h = T.CY - s.throat_y                       # half chord
    R = (h * h + s.half_w ** 2) / (2 * s.half_w)
    cL = K.P(s.cx - s.half_w + R, T.CY)         # centre of the LEFT arc (to the right)
    cR = K.P(s.cx + s.half_w - R, T.CY)
    return {"R": R, "cL": cL, "cR": cR, "top": K.P(s.cx, s.throat_y)}


def tunic(s: LensSpec = LensSpec(), voids=True, seed=1983) -> Part:
    """The vesica tunic: paper, patterned with §G.12 karst voids."""
    g = lens(s)
    reg = K.R(K.circle(g["cL"], g["R"])).intersection(K.R(K.circle(g["cR"], g["R"])))
    reg = reg.intersection(K.box(0, 0, 750, 540))
    lines = K.outline(K.D(reg))
    if voids:
        # voids keep 4.2 px + contour clear of the lens edge; staggered from the axis
        vreg = reg.buffer(-(K.MEDIUM / 2 + 3.2)).intersection(K.box(0, 0, 750, T.BAND_Y0 - 0.55 - 3.2))
        vv = M.karst_voids(vreg, pitch=(26.0, 20.0), seed=seed, margin=K.FINE / 2 + 0.2, origin=(s.cx, 330.0))
        lines += vv
    return Part(reg, C.Frag(), lines, g)


def lapel(s: LensSpec = LensSpec(), side: int = -1, mantle_shape=None, shoulder_x: float = 278.0,
          collar_sag: float = -6.0, bubbles: bool = True, bub_top: float = 364.0) -> Part:
    """Left lapel + collar (side −1): the red lining turned back. Inner edge =
    the left vesica arc; outer edge = one arc from the shoulder (x =
    ``shoulder_x`` on the mantle's yoke) to the lens offset ``lapel_w`` at
    the band, bulging outward by ``collar_sag``; top edge = the mantle's own
    yoke. It is a shawl collar: broad on the shoulder, ``lapel_w`` at the waist."""
    g = lens(s)
    c, Rr = g["cL"], g["R"]
    yb = 540.0
    xb = c[0] - math.sqrt((Rr + s.lapel_w) ** 2 - (yb - T.CY) ** 2)
    B_o = K.P(xb, yb)
    ms = mantle_shape if mantle_shape is not None else mantle().shape
    # shoulder point: top of the mantle at shoulder_x
    col = ms.intersection(shapely.LineString([(shoulder_x, 0), (shoulder_x, 700)]))
    S_o = K.P(shoulder_x, col.bounds[1])
    oc, orad = K.sag_centre(S_o, B_o, collar_sag)
    disc = K.R(K.circle(oc, orad))
    reg = (ms.intersection(disc).difference(K.R(K.circle(c, Rr)))
           .intersection(K.box(0, 0, s.cx, 540)))
    fill_d = K.D(reg)
    if bubbles:
        # rising bubbles (§G.9) on the lapel's mid-line — a concentric arc —
        # knocked out of the red as paper dots, growing ×1.2 upward
        rm = Rr + s.lapel_w / 2
        a_bot = K.ang(c, (c[0] - math.sqrt(rm ** 2 - (530 - T.CY) ** 2), 530.0))
        a_top = K.unwrap(a_bot, K.ang(c, (c[0] - math.sqrt(rm ** 2 - (bub_top - T.CY) ** 2), bub_top)), cw=True)
        n = 200
        th = np.radians(np.linspace(a_bot, a_top, n))
        path = np.column_stack([c[0] + rm * np.cos(th), c[1] + rm * np.sin(th)])
        bf = C.bubble_path(path, 4.2, ratio=1.16, gap=None, style="dot", d_max=12.6)
        fill_d = C.knockout(fill_d, bf)
    part = Part(reg, K.fill(fill_d, K.RED), K.outline(K.D(reg)),
                {"c": c, "R": Rr, "w": s.lapel_w, "outer_c": oc, "outer_r": orad, "S_o": S_o, "B_o": B_o})
    return part.mirrored(s.cx) if side > 0 else part


# =============================================================================
# mantle
# =============================================================================
@dataclass
class MantleSpec:
    cx: float = 375.0
    neck_y: float = 300.0        # chain starts on the axis here, heading out
    yoke_r: float = 620.0        # the long shoulder arc
    yoke_sweep: float = 12.0
    run: float = 30.0            # straight shoulder run
    corner_r: float = 72.0       # shoulder corner arc
    drop_heading: float = 90.0   # heading of the side after the corner (straight drop)
    bottom: float = 540.0


def mantle_outline_half(s: MantleSpec):
    t = C.Turtle(s.cx, s.neck_y, 180.0)
    t.arc(s.yoke_r, -s.yoke_sweep)
    t.fd(s.run)
    t.arc(s.corner_r, -(180.0 - s.yoke_sweep - s.drop_heading))
    y0 = t.pos[1]
    L = (s.bottom - y0) / math.sin(math.radians(s.drop_heading))
    t.fd(L)
    return t.d(), t.pts(0.5)[0]


def mantle(s: MantleSpec = MantleSpec(), strata=True, fault=((190.0, 505.0), (268.0, 318.0)), y0=None,
           border: float = 16.0) -> Part:
    """The jade mantle; §G.11 strata bands in Aquifer (12/19 px courses, the
    thin ones hatched) with one diagonal fault: courses on its lower-right
    side drop one course height. A plain jade border band ``border`` px wide
    runs inside the whole outer edge, closed by a FINE seam (the exact
    parallel of the silhouette, 4.2+ px clear of the CONTOUR): the courses end
    on the seam and never graze the sloping shoulder line."""
    d, pts = mantle_outline_half(s)
    left = np.vstack([pts, [[s.cx, s.bottom]]])
    half = shapely.Polygon(left)
    shape = K.U(half, K.mirror(half, s.cx))
    lines = K.outline(K.D(shape))
    if strata:
        inner = shape.buffer(-border, quad_segs=16) if border else shape
        if border:
            lines += C.stroke(K.D(inner), K.FINE, role="seam")
        lines += M.strata(inner, heights=(12.0, 19.0), hatched="thin", fault=fault,
                          y0=s.neck_y if y0 is None else y0)
        if fault is not None:
            # the fault itself, emphasised at MEDIUM over its FINE course break
            p0, p1 = np.asarray(fault[0], float), np.asarray(fault[1], float)
            u = (p1 - p0) / np.hypot(*(p1 - p0))
            ln = shapely.LineString([p0 - u * 2000, p1 + u * 2000]).intersection(inner)
            segs = [np.asarray(g.coords) for g in getattr(ln, "geoms", [ln]) if g.length > 1]
            if segs:
                lines += C.stroke(segs, K.MEDIUM, style="rule", role="fault")
    return Part(shape, K.fill(shape, K.JADE), lines, {"pts": pts})


# =============================================================================
# sleeves
# =============================================================================
@dataclass
class SleeveSpec:
    base: tuple = (232.0, 540.0)   # centre of the sleeve where it leaves the band
    wrist: tuple = (276.0, 462.0)  # centre of the wrist (cuff top)
    sag: float = -10.0             # guide arc bulge (negative: right of travel)
    width: float = 50.0            # at the base
    wrist_w: float = 34.0          # at the wrist (the edges converge: two arcs)
    cuff: float = 11.0             # cuff band depth


def sleeve(s: SleeveSpec, color=K.RED):
    """Sleeve panel from the band up to the wrist + a cuff band. The two long
    edges are arcs with the same sagitta as the guide; the cuff is a band
    between two short arcs struck from the wrist."""
    B, W = K.P(s.base), K.P(s.wrist)
    u = (W - B) / np.hypot(*(W - B))
    n = np.array([u[1], -u[0]])                       # screen-left normal
    bl, br = B + n * s.width / 2, B - n * s.width / 2
    wl, wr = W + n * s.wrist_w / 2, W - n * s.wrist_w / 2
    body = K.Path(bl).sag(wl, s.sag).line(wr).sag(br, -s.sag).close()
    shape = K.R(body.d)
    # cuff: from the wrist line back down by `cuff` along the guide
    cw_l = wl - u * s.cuff
    cw_r = wr - u * s.cuff
    cuff_d = K.Path(wl).sag(wr, -2.5).line(cw_r).sag(cw_l, 2.5).close().d
    cuff = K.R(cuff_d)
    sl = Part(shape, K.fill(shape, color), K.outline(body.d), {"W": W, "u": u, "n": n})
    cf = Part(cuff, C.Frag(), K.outline(cuff_d), {})
    return sl, cf
