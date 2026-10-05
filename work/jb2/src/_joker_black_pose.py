"""JOKER_BLACK pose (draft 2): the great-tailed grackle in the sky-pointing
display, drafted in card px (brief §H.18).

Drawn from the reference photographs in research/refs/jokers/ (looked at,
never traced): bill pointed at the sky, flat crown running into the culmen,
neck stretched straight up, the body and the long graduated tail one long
blade leaning back behind the perch, the folded wing along the back, the tail
folded into its V (the keel).

Construction
------------
* Outlines are G1 chains of circular arcs through drafted key points
  (``forms.arc_spline``), each point's tangent that of the circle through it
  and its neighbours unless pinned.
* The wing and the tail are LOFTS between two guide curves (both drafted
  as arc splines): a point is (t, f) -- t the arc-length fraction along the
  guides, f the fraction across (0 on the first guide, 1 on the second).
  Feather edges are curves of constant f, so they follow both edges and
  converge where the guides do (toward the wing point, down the tail);
  covert rows run across at constant t.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import Polygon

from inkkit import geom as G
from deck.motifs import forms


def unit(h):
    a = math.radians(h)
    return np.array([math.cos(a), math.sin(a)])


def heading(v):
    return math.degrees(math.atan2(v[1], v[0]))


class Frame:
    """Straight drafting frame: origin ``o``; +u along heading ``h``; +v is
    90 deg clockwise of +u (``vsign`` = -1 flips it)."""

    def __init__(self, o, h, vsign=1.0):
        self.o = np.asarray(o, float)
        self.h = float(h)
        self.U = unit(h)
        self.V = unit(h + 90.0) * vsign
        self.vs = vsign

    def __call__(self, u, v=0.0):
        return self.o + self.U * u + self.V * v

    def head(self, deg):
        return self.h + self.vs * deg

    def local(self, p):
        d = np.asarray(p, float) - self.o
        return np.array([d @ self.U, d @ self.V])


def closed_spline(pts, pins=None):
    pts = [np.asarray(p, float) for p in pts]
    n = len(pts)
    hs = [forms.circle_heading(pts[i - 1], pts[i], pts[(i + 1) % n]) for i in range(n)]
    for i, h in (pins or {}).items():
        hs[i] = h
    d, _ = forms.biarc_chain(pts, hs, closed=True)
    return d


def open_spline(pts, h0=None, h1=None, pins=None):
    d, P, _ = forms.arc_spline([np.asarray(p, float) for p in pts], h0, h1, headings=pins)
    return d, P


def spline_pts(pts, h0=None, h1=None, pins=None):
    return open_spline(pts, h0, h1, pins)[1]


# ---------------------------------------------------------------------------
# lofts
# ---------------------------------------------------------------------------
class Loft:
    """Surface between guide curves A (f = 0) and B (f = 1), both
    parametrised by their own arc-length fraction t."""

    def __init__(self, a_pts, b_pts):
        self.A = G.Curve(np.asarray(a_pts, float))
        self.B = G.Curve(np.asarray(b_pts, float))

    def __call__(self, t, f):
        a = self.A.at(t)
        b = self.B.at(t)
        return a + (b - a) * f

    def heading(self, t, f, dt=0.004):
        p = self(min(t + dt, 1.0), f) - self(max(t - dt, 0.0), f)
        return heading(p)

    def line(self, f, t0=0.0, t1=1.0, n=160):
        """Dense polyline of constant f (f may be a callable of t)."""
        ts = np.linspace(t0, t1, n)
        fs = [f(t) if callable(f) else f for t in ts]
        return np.array([self(t, v) for t, v in zip(ts, fs)])

    def across(self, t, f0=0.0, f1=1.0, n=40):
        return np.array([self(t, v) for v in np.linspace(f0, f1, n)])


def loft_feather(L, f_lo, f_hi, t0, t_tip, depth, apex=0.5, n=120):
    """Polygon of a feather lying along +t of loft ``L`` between f_lo and
    f_hi (numbers or callables of t), from t0 to a ROUNDED tip whose apex is
    at t_tip; ``depth`` = how far back (in px along the feather) the tip
    begins; ``apex`` = where across the feather the apex sits (0 lo .. 1 hi)."""
    flo = f_lo if callable(f_lo) else (lambda t, c=f_lo: c)
    fhi = f_hi if callable(f_hi) else (lambda t, c=f_hi: c)
    fm = lambda t: flo(t) + (fhi(t) - flo(t)) * apex     # noqa: E731
    tip = L(t_tip, fm(t_tip))
    tb = t_tip
    for _ in range(400):
        tb -= 0.001
        if np.hypot(*(L(tb, fm(tb)) - tip)) >= depth or tb <= t0:
            break
    ts = np.linspace(t0, tb, n)
    lo = np.array([L(t, flo(t)) for t in ts])
    hi = np.array([L(t, fhi(t)) for t in ts])
    h_lo = L.heading(tb, flo(tb))
    h_hi = L.heading(tb, fhi(tb))
    cap = spline_pts([lo[-1], tip, hi[-1]], h_lo, h_hi + 180.0)
    ring = np.vstack([lo, cap[1:-1], hi[::-1]])
    g = Polygon(ring).buffer(0)
    return g if g.geom_type == "Polygon" else max(g.geoms, key=lambda q: q.area)


# ---------------------------------------------------------------------------
# head: u along the bill toward its tip, v toward the throat (right)
# ---------------------------------------------------------------------------
BILL_DEG = -83.0
BILL_TIP = np.array([410.0, 94.0])
BILL_LEN = 66.0
HEAD = Frame(BILL_TIP - unit(BILL_DEG) * BILL_LEN, BILL_DEG)
BILL_BASE_HALF = 9.0
EYE_C = HEAD(-12.0, -3.5)
EYE_R = 6.6
PUPIL_D = 6.3

# ---------------------------------------------------------------------------
# body outline (head, neck, body)
# ---------------------------------------------------------------------------
BODY_PTS = [
    HEAD(-2.0, -10.0),        # 0 culmen base (forehead feathering)
    HEAD(-12.0, -14.5),       # 1 forehead
    HEAD(-26.0, -17.5),       # 2 flat crown
    (383.5, 192.0),           # 3 occiput
    (385.0, 216.0),           # 4 nape
    (382.0, 240.0),           # 5 hindneck
    (372.0, 259.0),           # 6 mantle
    (355.0, 278.0),           # 7 shoulder
    (336.0, 305.0),           # 8 scapulars
    (319.0, 340.0),           # 9 back
    (305.0, 380.0),           # 10 back
    (295.0, 422.0),           # 11 back
    (291.0, 456.0),           # 12 rump
    (316.0, 472.0),           # 13 tail base
    (351.0, 468.0),           # 14 under-tail coverts
    (366.0, 448.0),           # 15 vent
    (381.0, 426.0),           # 16 belly
    (399.0, 395.0),           # 17 belly
    (417.0, 360.0),           # 18 breast
    (429.0, 326.0),           # 19 breast
    (434.0, 292.0),           # 20 upper breast
    (434.0, 262.0),           # 21 upper breast
    (430.0, 236.0),           # 22 foreneck
    (425.0, 212.0),           # 23 throat
    (420.0, 188.0),           # 24 throat
    HEAD(-5.0, 11.5),         # 25 chin at the bill base
]
BODY_PINS = {0: HEAD.head(180.0 + 14.0), len(BODY_PTS) - 1: HEAD.head(20.0)}


def body_d():
    return closed_spline(BODY_PTS, BODY_PINS)


def bill_d():
    """Upper mandible: culmen gently decurved to a sharp tip; gonys nearly
    straight. Closed shape."""
    L = BILL_LEN
    top, _ = open_spline([HEAD(-6.0, -BILL_BASE_HALF - 1.5), HEAD(L * 0.5, -5.2), HEAD(L, 0.0)],
                         HEAD.head(-3.0), HEAD.head(12.0))
    bot, _ = open_spline([HEAD(L, 0.0), HEAD(L * 0.5, 4.6), HEAD(-6.0, BILL_BASE_HALF + 1.0)],
                         HEAD.head(180.0 - 7.0), HEAD.head(180.0 + 1.0))
    return top + bot.replace("M", "L", 1) + "Z"


def gape_d():
    d, _ = open_spline([HEAD(-9.0, 2.6), HEAD(6.0, 1.2), HEAD(BILL_LEN * 0.55, 0.6)])
    return d


# ---------------------------------------------------------------------------
# folded wing: loft between the ventral (leading) edge, f = 0, and the
# dorsal edge, f = 1; both run from the shoulder down to the wing point
# ---------------------------------------------------------------------------
WING_TIP = np.array([304.0, 516.0])
WRIST_H = 84.0                  # heading of the leading edge where it leaves the wrist
WING_VEN = [(409.0, 294.0), (407.0, 324.0), (399.0, 352.0), (387.0, 382.0), (371.0, 414.0),
            (354.0, 446.0), (337.0, 474.0), (320.0, 498.0), tuple(WING_TIP)]
WING_DOR = [(352.0, 281.0), (336.0, 305.0), (320.0, 338.0), (306.0, 378.0), (296.0, 420.0),
            (293.0, 452.0), (296.0, 478.0), (300.0, 498.0), tuple(WING_TIP)]
WING_SCAP = [(352.0, 281.0), (372.0, 271.0), (395.0, 276.0), (409.0, 294.0)]   # shoulder arc


def wing_loft():
    return Loft(spline_pts(WING_VEN, WRIST_H, None), spline_pts(WING_DOR))


WING_T_BODY = 0.8               # the loft carries the wing to here; the primaries make the point


def _loft_region(L, t0, t1, f0=0.0, f1=1.0, n=200):
    a = L.line(f0, t0, t1, n)
    b = L.line(f1, t0, t1, n)
    return Polygon(np.vstack([a, b[::-1]])).buffer(0)


def wing_outline_poly():
    L = wing_loft()
    ven = L.line(0.0, 0.0, WING_T_BODY, n=200)
    dor = L.line(1.0, 0.0, WING_T_BODY, n=200)
    scap = spline_pts(WING_SCAP, None, WRIST_H)
    ring = np.vstack([scap, ven[1:], dor[::-1][:-1]])
    g = Polygon(ring).buffer(0)
    g = g if g.geom_type == "Polygon" else max(g.geoms, key=lambda q: q.area)
    prim = [loft_feather(L, lo, hi, 0.5, tt, dp, apex=ap) for _, lo, hi, tt, dp, ap, _ in PRIMARIES]
    return shapely.union_all([g] + prim)


# flight feathers (tertials / secondaries): (name, f of its ventral edge, apex t, tip depth, z)
FLIGHT = [("f3", -0.05, 0.74, 16.0, 15), ("f2", 0.25, 0.66, 18.0, 16), ("f1", 0.50, 0.58, 18.0, 17)]
# primaries: (name, f_lo, f_hi, apex t, depth, z)
PRIMARIES = [("p1", 0.0, 0.62, 0.985, 30.0, 0.42, 10), ("p2", 0.34, 1.0, 0.875, 20.0, 0.55, 11)]
# greater coverts: tips on the line t = t_a (at f 0) .. t_b (at f 1); n feathers
GREATER = dict(t_a=0.215, t_b=0.265, n=4, width=1.22, depth=11.0, z=20)
# lesser-covert patch: its scalloped lower edge from (t_a, f 0) to (t_b, f 1)
LESSER = dict(t_a=0.115, t_b=0.145, n=6, sag=4.6, z=60)


def wing_feathers():
    L = wing_loft()
    out = []
    for nm, lo, hi, tt, dp, ap, z in PRIMARIES:
        out.append((f"wing-{nm}", loft_feather(L, lo, hi, 0.2, tt, dp, apex=ap), z))
    for nm, lo, tt, dp, z in FLIGHT:
        out.append((f"wing-{nm}", loft_feather(L, lo, 1.3, 0.1, tt, dp, apex=0.3), z))
    g = GREATER
    n = g["n"]
    pitch = 1.0 / n
    for k in range(n):
        fc = pitch * (k + 0.5)
        w = pitch * g["width"]
        tt = g["t_a"] + (g["t_b"] - g["t_a"]) * fc
        out.append((f"covert-g{k}", loft_feather(L, fc - w / 2, fc + w / 2, 0.02, tt, g["depth"], apex=0.5),
                    g["z"] + (n - k)))
    return out


# ink scale rows drawn inside the lesser-covert jade window: (t at f 0, t at f 1, n, sag, phase)
LESSER_ROWS = []


def lesser_rows():
    """Cusp lists of the scale rows inside the lesser-covert patch."""
    L = wing_loft()
    out = []
    for ta, tb, n, sag, ph in LESSER_ROWS:
        fs = np.linspace(-1.0 / n, 1.0 + 1.0 / n, n + 3) + ph / n
        out.append(([L(ta + (tb - ta) * f, f) for f in fs], sag))
    return out


# breast: scale rows between the breast outline (f 0) and the wing's leading edge (f 1)
BREAST_OUT = [(433.0, 268.0), (434.0, 294.0), (429.0, 326.0), (417.0, 360.0), (399.0, 395.0), (381.0, 426.0),
              (366.0, 448.0)]
BREAST_ROWS = dict(t0=0.10, t1=0.92, n_rows=9, pitch_f=(0.42, 0.55), sag=(3.6, 5.2), slant=0.05)


def breast_loft():
    A = spline_pts(BREAST_OUT)
    Lw = wing_loft()
    B = Lw.line(0.0, 0.0, 0.62, n=200)
    return Loft(A, B)


def breast_rows():
    """[(cusps, sag)] scale rows across the breast strip, bulging toward the
    tail, growing toward the belly; alternate rows offset half a scale."""
    L = breast_loft()
    c = BREAST_ROWS
    out = []
    for k in range(c["n_rows"]):
        x = k / max(c["n_rows"] - 1, 1)
        t = c["t0"] + (c["t1"] - c["t0"]) * x
        pf = c["pitch_f"][0] + (c["pitch_f"][1] - c["pitch_f"][0]) * x
        sg = c["sag"][0] + (c["sag"][1] - c["sag"][0]) * x
        ph = 0.5 * (k % 2)
        fs = np.arange(-2.0, 1.0 / pf + 2.0) * pf + ph * pf - pf
        out.append(([L(t + c["slant"] * f, f) for f in fs], sg))
    return out


def lesser_chain():
    """Cusps of the lesser-covert patch's scalloped lower edge."""
    L = wing_loft()
    c = LESSER
    n = c["n"]
    return [L(c["t_a"] + (c["t_b"] - c["t_a"]) * f, f) for f in np.linspace(-1.0 / n, 1.0 + 1.0 / n, n + 3)]


# ---------------------------------------------------------------------------
# tail: loft between the keel edge (f = 0, the long central pair) and the
# dorsal edge of the far vane (f = 1); the near vane is f 0..TAIL_V, the far
# vane (the inside of the V) f TAIL_V..1
# ---------------------------------------------------------------------------
TAIL_KEEL = [(351.0, 464.0), (336.0, 496.0), (322.0, 540.0), (314.0, 588.0), (306.0, 622.0), (296.0, 638.0)]
TAIL_DORS = [(298.0, 450.0), (283.0, 490.0), (271.0, 538.0), (263.0, 580.0), (259.0, 600.0)]
TAIL_V = 0.66
# (name, f_lo, f_hi, apex t, depth, apex, z)
TAIL_FEATHERS = [
    ("tail-far", 0.55, 1.0, 1.0, 16.0, 0.6, 0),
    ("tail-n1", -0.02, TAIL_V, 1.0, 20.0, 0.30, 1),
    ("tail-n2", 0.34, TAIL_V, 0.94, 16.0, 0.45, 2),
]


def tail_loft():
    return Loft(spline_pts(TAIL_KEEL), spline_pts(TAIL_DORS))


def tail_feathers():
    L = tail_loft()
    return [(nm, loft_feather(L, lo, hi, 0.0, tt, dp, apex=ap), z)
            for nm, lo, hi, tt, dp, ap, z in TAIL_FEATHERS]


def tail_d():
    g = shapely.union_all([p for _, p, _ in tail_feathers()])
    return G.from_shape(g)


FOOT_N = np.array([396.0, 0.0])
FOOT_F = np.array([380.0, 0.0])
