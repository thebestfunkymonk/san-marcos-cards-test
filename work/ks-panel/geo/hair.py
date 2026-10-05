"""Hair, beards and moustaches as §G.24 current lines — compass construction.

A lock mass is a FAN: an annulus sector about one centre (outer radius R,
n ribbons of 7 px inward). Its current lines are the CONCENTRIC offsets of
the guide arc (the exact compass offset of an arc is an arc), so every line
is a true circle segment, 7 px apart (FINE, 4.9 px clear), each ending in a
Ø6.3 terminal (§B.2). The fan's end is a round cap (a semicircle across the
ribbons): the rolled curl.

    fan(c, R, n, a0, a1, ...)      generic lock fan (region + lines)
    hair_fall(fs, HairSpec, side)  hair from under the crown to the shoulder
    beard_forked(fs, BeardSpec)    two mirrored fans meeting on the axis
    moustache(fs, MoustacheSpec)   two crescents whose lower arcs are the lip bow
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import shapely

import kit as K
from deck.motifs import core as C
from face import FaceSpec


@dataclass
class Part:
    shape: object
    fills: C.Frag
    lines: C.Frag
    meta: dict = field(default_factory=dict)

    @property
    def frag(self):
        return self.fills + self.lines

    def mirrored(self, axis=K.AX):
        return Part(K.mirror(self.shape, axis), self.fills.mirror_x(axis), self.lines.mirror_x(axis), dict(self.meta))


# -----------------------------------------------------------------------------
# the generic fan
# -----------------------------------------------------------------------------
def fan_region(c, r_out, r_in, a0, a1, cap=True):
    """Annulus sector a0→a1 (screen degrees) between r_in and r_out; with
    ``cap`` the a1 end is a semicircle across the ribbons (a rolled end)."""
    c = K.P(c)
    cw = a1 > a0
    p_o0, p_o1 = K.polar(c, r_out, a0), K.polar(c, r_out, a1)
    p_i0, p_i1 = K.polar(c, r_in, a0), K.polar(c, r_in, a1)
    p = K.Path(p_o0).arc_to(c, r_out, p_o1, cw=cw)
    if cap:
        h = (r_out - r_in) / 2
        p.sag(p_i1, h if cw else -h)
    else:
        p.line(p_i1)
    p.arc_to(c, r_in, p_i0, cw=not cw).close()
    return K.R(p.d)


EDGE = K.CONTOUR / 2 + 4.2 + K.FINE / 2    # first line's offset from a silhouette edge (8.4)


def fan_lines(c, r_out, n, a0, a1, region, *, pitch=K.PITCH, term_inset=6.0, end="a1", edge=EDGE, stagger=9.0):
    """The internal current lines of a fan of n ribbons (the first ``edge`` px
    inside the outer arc so it clears a CONTOUR silhouette by 4.2), clipped to
    ``region``, each with a Ø6.3 terminal at ``end``."""
    radii = [r_out - edge - k * pitch for k in range(0, n - 1)]
    return K.current_lines(c, radii, a0, a1, region, end=end, term_inset=term_inset, stagger=stagger)


# -----------------------------------------------------------------------------
# hair falling beside the face (one side)
# -----------------------------------------------------------------------------
@dataclass
class HairSpec:
    top: tuple = (-52.0, 176.0)      # outer edge under the crown band end (dx, y)
    bulge: tuple = (-76.0, 250.0)    # outermost point
    bottom: tuple = (-62.0, 326.0)   # outer edge at the curl
    ribbons: int = 6
    over: float = 12.0               # degrees the fan starts above ``top`` (hidden under the band)


def hair_fall(fs: FaceSpec, h: HairSpec = HairSpec(), side: int = -1) -> Part:
    ax = fs.cx
    T0 = K.P(ax + h.top[0], h.top[1])
    Bg = K.P(ax + h.bulge[0], h.bulge[1])
    B0 = K.P(ax + h.bottom[0], h.bottom[1])
    c, R = K.circ3(T0, Bg, B0)
    a_top, a_bot = K.ang(c, T0), K.ang(c, B0)
    # the fan runs anticlockwise on screen (down the left side): a0 > a1
    a0 = a_top + h.over
    a1 = K.unwrap(a0, a_bot, cw=False)
    r_in = R - (EDGE + K.PITCH * (h.ribbons - 2) + 7.0)     # last line 7 px inside a MEDIUM edge
    reg = fan_region(c, R, r_in, a0, a1)
    lines = fan_lines(c, R, h.ribbons, a0, a1, reg, term_inset=4.3)   # dot overlaps the cap contour
    part = Part(reg, K.fill(reg, K.GOLD), lines + K.outline(K.D(reg)), {"c": c, "R": R, "a": (a0, a1)})
    return part.mirrored(ax) if side > 0 else part


# -----------------------------------------------------------------------------
# beard
# -----------------------------------------------------------------------------
@dataclass
class BeardSpec:
    side: tuple = (-40.0, 232.0) # sideburn point (dx, y) on the head's side
    tip: tuple = (-21.0, 342.0)  # fork tip (dx, y)
    notch_y: float = 306.0       # fork notch on the axis
    mouth_dx: float = 17.0       # beard top meets the moustache here
    mouth_y: float = 264.0
    chin_y: float = 274.5        # beard top on the axis (under the lower lip)
    cheek_pt: tuple = (-29.0, 250.0)
    term_inset: float = 4.5
    stagger: float = 8.0         # alternate lines end this much earlier (dots 7 px apart would touch)
    r_min: float = 30.0          # inner chin stays plain gold (no fingerprint loops)


def beard_forked(fs: FaceSpec, b: BeardSpec = BeardSpec()) -> Part:
    """Forked beard: each half is a PIE SLICE of one circle whose centre lies
    on the prolongation of the fork edge, so the fork edge is a radius and
    every current line (a concentric arc) meets it square, ending in a Ø6.3
    terminal. Lines that reach the axis meet their mirror image there in a
    chevron (no free end, no terminal)."""
    ax = fs.cx
    Ft = K.P(ax + b.tip[0], b.tip[1])
    N = K.P(ax, b.notch_y)
    S = K.P(ax + b.side[0], b.side[1])
    # fan centre: on the prolonged fork edge (N + t·(N − Ft)), equidistant from
    # the sideburn S and the tip Ft — the compass point that makes the outer
    # arc pass through both and the fork edge a radius
    u = N - Ft
    a = N - S
    bb = N - Ft
    t = (bb @ bb - a @ a) / (2 * (a @ u) - 2 * (bb @ u))
    oc = N + u * t
    orad = float(np.hypot(*(Ft - oc)))
    Ch = K.P(ax, b.chin_y)
    M = K.P(ax - b.mouth_dx, b.mouth_y)
    Cp = K.P(ax + b.cheek_pt[0], b.cheek_pt[1])
    a_s = K.ang(oc, S)
    a_f = K.unwrap(a_s, K.ang(oc, Ft), cw=False)
    # pie slice (centre, S, around the left to Ft) ∩ below the cheek/mouth line
    pie = K.Path(oc).line(S).arc_to(oc, orad, Ft, cw=False).close().d
    top_cut = K.Path(S).arc3(Cp, M).sag(Ch, 2.5).line((ax + 40, b.chin_y)).line((ax + 40, 600)) \
        .line((S[0] - 60, 600)).line((S[0] - 60, S[1] - 30)).line((S[0], S[1] - 30)).close().d
    half = K.R(pie).intersection(K.R(top_cut)).intersection(K.box(0, 0, ax, 1000))
    shape = K.U(half, K.mirror(half, ax))
    fork = shapely.LineString([tuple(oc), tuple(Ft + (Ft - oc) * 0.1)])
    radii = [orad - EDGE - k * K.PITCH for k in range(0, 40) if orad - EDGE - k * K.PITCH >= b.r_min]
    raw = K.current_lines(oc, radii, a_s + 10, a_f, half.buffer(-0.01), end=None)
    lines = C.Frag()
    for m in raw.marks:
        for pts, _ in G_flat(m.d):
            q = np.asarray(pts)
            rr = float(np.hypot(*(q[len(q) // 2] - oc)))
            k_r = int(round((orad - EDGE - rr) / K.PITCH))
            inset = b.term_inset + (b.stagger if k_r % 2 else 0.0)
            if fork.distance(shapely.Point(q[-1])) < 1.5:
                cv = K.G.Curve(q)
                if cv.length > inset + 6:
                    q = cv.sub(0, 1 - inset / cv.length).pts
                lines += K.line(q, K.FINE) + K.dot(q[-1])
            elif fork.distance(shapely.Point(q[0])) < 1.5:
                cv = K.G.Curve(q)
                if cv.length > inset + 6:
                    q = cv.sub(inset / cv.length, 1).pts
                lines += K.line(q, K.FINE) + K.dot(q[0])
            else:
                lines += K.line(q, K.FINE)
    lines = K.bi(lines, ax)
    return Part(shape, K.fill(shape, K.GOLD), lines + K.outline(K.D(shape)),
                {"outer_c": oc, "outer_r": orad, "S": S, "tip": Ft})


def G_flat(d):
    return K.G.flatten(d, 0.05)


# -----------------------------------------------------------------------------
# moustache
# -----------------------------------------------------------------------------
@dataclass
class MoustacheSpec:
    root: tuple = (-3.5, 251.5)   # inner tip of each leaf (dx, y), under the nose
    tip: tuple = (-31.0, 264.0)   # outer tip (dx, y)
    width: float = 10.0           # vesica width
    droop: float = 2.5            # the leaf's axis bows down by this (the leaf is a vesica on an arc)


def moustache(fs: FaceSpec, m: MoustacheSpec = MoustacheSpec()) -> Part:
    """Two vesica leaves (the deck's leaf: two arcs of equal radius), mirrored
    about the axis, from under the nose out to the drooping tips — a flat,
    dignified moustache; the paper between the roots is the philtrum."""
    ax = fs.cx
    p0 = K.P(ax + m.root[0], m.root[1])
    p1 = K.P(ax + m.tip[0], m.tip[1])
    leaf = K.R(K.vesica(p0, p1, m.width))
    shape = K.U(leaf, K.mirror(leaf, ax))
    d = K.D(shape)
    return Part(shape, K.fill(shape, K.GOLD), K.outline(d), {})
