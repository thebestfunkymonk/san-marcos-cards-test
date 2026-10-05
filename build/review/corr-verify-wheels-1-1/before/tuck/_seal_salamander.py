"""The seal's Texas blind salamander (*Eurycea rathbuni*) — brief §H.20 "Seal".

Owned by the seal finisher.  Drawn from research/refs/smtx/blind_salamander.jpg
and the USFWS / Ryan Hagerty photographs on Wikimedia Commons ("Eurycea
rathbuni FWS 20424–20439": dorsal, frontal and lateral views).

Seen from above, curled in ONE C (≈ 300° of turn; no part of the body passes
over another, so there is no crossing to interlace), gold foil on Gill Red:

* ONE silhouette contour (FINE 2.1): head, body and tail are one shape whose
  boundary is stroked once.  Everything else — limbs, gills, digits, the
  split line, hatch, eyes — only TOUCHES that contour from one side.
* HEAD: broad and flat, the widest part of the animal across the cheeks
  (≈ 1.25 × the trunk), narrowing to a long, flattened, SPATULATE snout with a
  blunt rounded-square "spoon" end.
* EYES: vestigial — two Ø4.2 dots under the skin in the front third of the
  head, 4.2 px clear of the contour.
* GILLS: three short, bushy, feathery rami a side (≈ half the head width
  long) fanned from the neck and sweeping back; each a small SOLID plume whose
  edges carry raked, softened filament lobes — a feather, never antler tines.
* LIMBS: long, spindly and SOLID (≈ 5 px, easing to 4 px at the wrist),
  filleted into the contour, jointed at a rounded elbow / knee and posed in a
  walking stride; 4 fingers and 5 toes as FINE strokes splayed wide.
* THE SPLIT (Jinkins half-hatching, §B.2 / style.md rule 3): one line runs
  from the nape down the spine and eases out to the tail's fin base; the
  OUTER part (the convex side of the C, where the hatch pitch opens, never
  closes) is hatched FINE at the 7.0 pitch:
    - on the trunk, between the limbs, square to the spine — the hatch IS the
      12 costal grooves;
    - on the tail, where the outer part is the FIN (the compressed tail rolls
      as it curls and shows its keel on the outside of the C), at 45° leaning
      toward the tip — the fin membrane.
  Where a part grows too narrow for 4.2 px of paper the detail stops, and the
  tail finishes as a clean outlined point with a solid tip.

All geometry is generated at final size (nothing is scaled).
"""
from __future__ import annotations

import copy
import math

import numpy as np
from scipy.interpolate import PchipInterpolator
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.ops import unary_union

from inkkit import geom as G

from deck import tokens as T
from deck.motifs.core import Frag, dot, fill, polyline_d, stroke

FINE = T.FINE
GAP = T.INTERLACE_GAP            # 4.2: the clear foil gap between parallel strokes
MIN_HALF = FINE + GAP            # 6.3: the least centreline spacing of two parallel strokes

# -----------------------------------------------------------------------------
# design table (px, final size).  s = arc length along the spine, snout tip (0)
# to tail tip (L).  "in" = the concave (inside) side of the C, "out" = convex.
# -----------------------------------------------------------------------------
SPEC = dict(
    L=372.0,
    # half-width of the body about the spine (the fin is added on the outer side of the tail)
    hw=[(0.0, 0.0), (5.5, 9.9), (8.8, 10.5), (14.3, 12.2), (20.9, 14.0), (27.5, 15.3),
        (34.1, 16.0), (39.6, 16.2), (44.0, 15.7), (48.4, 14.4), (52.8, 13.0), (58.3, 12.3),
        (68.2, 12.6), (99.0, 12.9), (137.5, 12.9), (170.0, 12.1), (187.0, 10.2), (212.0, 7.9),
        (236.5, 6.5), (275.0, 5.6), (313.5, 4.7), (341.0, 3.7), (360.8, 2.4), (372.0, 0.0)],
    snout_cap=5.5,          # superellipse cap at the snout (the blunt rounded-square spoon end)
    snout_p=2.6,            # its exponent (2 = round, larger = squarer)
    tip_r=1.2,              # tail-tip rounding (a crisp point)
    # curvature of the spine (deg of turn per px; negative = counter-clockwise):
    # the head carried nearly straight, then one even C, the tail tip curling a little tighter
    kappa=[(0.0, -0.09), (39.6, -0.14), (79.2, -0.91), (314.6, -0.91), (372.0, -1.27)],
    head_heading=0.0,
    eyes=(17.5, GAP),       # (s, clear gap from the eye dot to the head's contour stroke): the front third
    # gills: three rami a side rooted on the neck contour at s, fanned (deg from
    # the outward normal, + toward the TAIL), curling back; solid feathery plumes
    gills=dict(s=(44.5, 50.0, 55.5), ang=(-14.0, 26.0, 64.0), length=(16.4, 18.0, 15.9),
               curl=(44.0, 38.0, 30.0), round=0.35,
               plume=dict(hw=2.0, stalk=0.9, tooth=2.8, pitch=2.9, rake=0.96, lean=3.6, root=0.12,
                          tip=0.25, grow=0.3)),
    # limbs: shoulder / hip at s; upper segment l1 at a1 (deg from the outward
    # normal, + toward the head), lower segment l2 at a2; digits splayed about
    # the lower segment's direction (4 fingers, 5 toes)
    limbs=dict(
        fore_out=dict(s=82.0, l1=18.7, a1=8.0, l2=16.5, a2=46.0, digits=4, dl=5.4, spread=40.0),
        fore_in=dict(s=82.0, l1=16.0, a1=-18.0, l2=14.3, a2=24.0, digits=4, dl=5.2, spread=40.0),
        hind_out=dict(s=178.0, l1=19.8, a1=-14.0, l2=17.6, a2=-60.0, digits=5, dl=5.6, spread=36.0),
        hind_in=dict(s=178.0, l1=16.5, a1=-22.0, l2=15.4, a2=-66.0, digits=5, dl=5.2, spread=36.0),
    ),
    limb_mode="solid",      # 'solid': each limb a slim solid shape; 'tube': an outlined tube (bore 4.2)
    limb_solid=(2.7, 2.1, 1.6),   # solid limb: half-width at the root, at the wrist; armpit fillet radius
    limb_hw=(3.5, 3.2),     # 'tube' limbs: half-width at the root and at the wrist (bore ≥ 4.2)
    joint_r=6.6,            # elbow / knee rounding radius (centreline)
    fillet=3.0,             # silhouette fillet
    # the split line (dorsal line -> fin base): from the nape to where a part gets too narrow
    split_s0=55.0,
    split_shift=(182.0, 240.0),   # eases from the spine to the tail core's outer edge over this span
    # the fin: added to the OUTER half-width along the tail (s, px)
    fin=[(179.0, 0.0), (200.0, 3.8), (221.0, 6.8), (250.0, 7.7), (292.0, 8.0), (330.0, 7.4),
         (349.8, 6.8), (363.0, 3.8), (372.0, 0.0)],
    # hatch zones on the outer part: (s0, s1, kind); 'groove' = the 12 costal grooves, 'fin' = fin membrane
    hatch=[(89.5, 167.5, "groove"), (221.0, 440.0, "fin")],
    hatch_angle=dict(groove=0.0, fin=45.0),   # deg from square-to-the-spine (+ leans toward the tail tip): §B.2 45° on blades
    hatch_clear=GAP,        # hatch lines keep this much paper to any limb
)


# -----------------------------------------------------------------------------
# helpers
# -----------------------------------------------------------------------------
def unit(deg: float) -> np.ndarray:
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def ang_of(v) -> float:
    return math.degrees(math.atan2(v[1], v[0]))


def _profile(pts):
    xs = np.array([p[0] for p in pts], float)
    ys = np.array([p[1] for p in pts], float)
    return PchipInterpolator(xs, ys, extrapolate=False)


def _largest(g):
    if isinstance(g, MultiPolygon):
        return max(g.geoms, key=lambda p: p.area)
    return g


class Body:
    """The spine (integrated from the curvature table) and its frame."""

    def __init__(self, spec=SPEC):
        self.spec = spec
        L = spec["L"]
        self.L = L
        s = np.linspace(0.0, L, int(L * 10) + 1)
        kx = [p[0] for p in spec["kappa"]]
        ky = [p[1] for p in spec["kappa"]]
        kap = np.interp(s, kx, ky)
        head = spec["head_heading"] + np.concatenate(
            [[0.0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(s))])
        hr = np.radians(head)
        x = np.concatenate([[0.0], np.cumsum((np.cos(hr[1:]) + np.cos(hr[:-1])) / 2 * np.diff(s))])
        y = np.concatenate([[0.0], np.cumsum((np.sin(hr[1:]) + np.sin(hr[:-1])) / 2 * np.diff(s))])
        self.s = s
        self.P = np.column_stack([x, y])
        self.head = head
        self._hw = _profile(spec["hw"])
        self._fin = _profile(spec["fin"])

    # ---- frame ----------------------------------------------------------------
    def at(self, s):
        s = np.asarray(s, float)
        if s.ndim:
            return np.column_stack([np.interp(s, self.s, self.P[:, 0]), np.interp(s, self.s, self.P[:, 1])])
        return np.array([np.interp(s, self.s, self.P[:, 0]), np.interp(s, self.s, self.P[:, 1])])

    def heading(self, s) -> float:
        return float(np.interp(s, self.s, self.head))

    def tangent(self, s) -> np.ndarray:
        return unit(self.heading(s))

    def normal_in(self, s) -> np.ndarray:
        """Left of travel on screen: the inside of the C (the body turns that way)."""
        t = self.tangent(s)
        return np.array([t[1], -t[0]])

    def out_dir(self, s, side: str) -> np.ndarray:
        n = self.normal_in(s)
        return -n if side == "out" else n

    # ---- widths ---------------------------------------------------------------
    def hw(self, s):
        s = np.asarray(s, float)
        v = np.nan_to_num(self._hw(np.clip(s, 0, self.L)))
        c, p = self.spec["snout_cap"], self.spec["snout_p"]
        w_c = float(self._hw(c))
        cap = w_c * np.power(np.clip(1 - np.power(np.clip((c - s) / c, 0, 1), p), 0, 1), 1 / p)
        v = np.where(s < c, cap, v)
        r = self.spec["tip_r"]
        x = np.clip((s - (self.L - r)) / r, 0, 1)
        tip = float(self._hw(self.L - r)) * np.sqrt(np.clip(1 - x * x, 0, None))
        v = np.where(s > self.L - r, tip, v)
        return np.clip(v, 0, None)

    def fin(self, s):
        s = np.asarray(s, float)
        f0 = self.spec["fin"][0][0]
        v = np.nan_to_num(self._fin(np.clip(s, f0, self.L)))
        return np.where(s < f0, 0.0, np.clip(v, 0, None))

    def hw_out(self, s):
        return self.hw(s) + self.fin(s)

    def edge(self, side: str, s, fin: bool = True):
        s = np.atleast_1d(np.asarray(s, float))
        P = self.at(s)
        th = np.radians(np.interp(s, self.s, self.head))
        N = np.column_stack([np.sin(th), -np.cos(th)])       # inside normal
        w = self.hw(s)
        if side == "in":
            return P + N * w[:, None]
        if fin:
            w = w + self.fin(s)
        return P - N * w[:, None]

    def split_off(self, s):
        """Offset of the split line from the spine toward the OUTER side: 0 on
        the trunk (the dorsal line), easing out to the tail core's outer edge
        (the fin base) over ``split_shift``."""
        s = np.asarray(s, float)
        a, b = self.spec.get("split_shift", (1e9, 1e9 + 1))
        x = np.clip((s - a) / (b - a), 0, 1)
        e = x * x * (3 - 2 * x)
        return e * self.hw(s)

    def split_pts(self, s):
        s = np.atleast_1d(np.asarray(s, float))
        th = np.radians(np.interp(s, self.s, self.head))
        N = np.column_stack([np.sin(th), -np.cos(th)])       # inside normal
        return self.at(s) - N * self.split_off(s)[:, None]

    def split_end(self) -> float:
        """Where the split line must stop: the first s (past the trunk) where
        either part is narrower than 6.3 px centre to centre."""
        ss = self.s[self.s > 150.0]
        m = self.split_off(ss)
        narrow = np.minimum(self.hw(ss) + m, self.hw_out(ss) - m) < MIN_HALF
        idx = np.where(narrow)[0]
        return float(ss[idx[0]]) if len(idx) else self.L


# -----------------------------------------------------------------------------
# limbs
# -----------------------------------------------------------------------------
def _round_corner(a, b, c, r: float, n: int = 16):
    a, b, c = (np.asarray(v, float) for v in (a, b, c))
    u1 = (b - a) / np.linalg.norm(b - a)
    u2 = (c - b) / np.linalg.norm(c - b)
    turn = math.acos(float(np.clip(u1 @ u2, -1, 1)))
    if turn < 1e-3:
        return np.array([a, c])
    d = r * math.tan(turn / 2)
    d = min(d, 0.45 * np.linalg.norm(b - a), 0.45 * np.linalg.norm(c - b))
    r = d / math.tan(turn / 2)
    p1 = b - u1 * d
    cross = u1[0] * u2[1] - u1[1] * u2[0]
    nrm = np.array([-u1[1], u1[0]]) * (1 if cross > 0 else -1)
    c0 = p1 + nrm * r
    a0 = math.atan2(p1[1] - c0[1], p1[0] - c0[0])
    p2 = b + u2 * d
    a1 = math.atan2(p2[1] - c0[1], p2[0] - c0[0])
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    arc = [c0 + r * np.array([math.cos(a0 + da * k), math.sin(a0 + da * k)]) for k in np.linspace(0, 1, n)]
    return np.vstack([a, arc, c])


def _resample(pts: np.ndarray, step: float = 0.5) -> np.ndarray:
    d = np.hypot(*np.diff(pts, axis=0).T)
    s = np.concatenate([[0.0], np.cumsum(d)])
    n = max(2, int(math.ceil(s[-1] / step)) + 1)
    ss = np.linspace(0, s[-1], n)
    return np.column_stack([np.interp(ss, s, pts[:, 0]), np.interp(ss, s, pts[:, 1])])


def tapered_tube(pts: np.ndarray, hw0: float, hw1: float, *, taper: float = 1.6) -> Polygon:
    """A limb tube along ``pts``: half-width ``hw0`` at the root easing to
    ``hw1`` at the wrist, closed by a round cap.  ``hw1`` ≥ 3.15 keeps ≥ 4.2
    px clear between the two outline strokes."""
    P = _resample(np.asarray(pts, float), 0.4)
    d = np.gradient(P, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None]
    N = np.column_stack([-d[:, 1], d[:, 0]])
    seg = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    t = seg / seg[-1]
    w = hw1 + (hw0 - hw1) * np.power(1 - t, taper)
    left = P + N * w[:, None]
    right = P - N * w[:, None]
    h = ang_of(d[-1])
    cap = [P[-1] + unit(h - 90 + k) * hw1 for k in np.linspace(0, 180, 25)]
    ringpts = np.vstack([right, np.array(cap), left[::-1]])
    poly = Polygon(ringpts).buffer(0)
    poly = poly.union(Point(P[0]).buffer(hw0, quad_segs=16))  # round root (buried in the body)
    return _largest(poly)


def limb_geometry(body: Body, key: str, spec=SPEC):
    ls = spec["limbs"][key]
    side = "out" if key.endswith("out") else "in"
    s = ls["s"]
    p = body.at(s)
    o = body.out_dir(s, side)
    head_dir = -body.tangent(s)

    def rotv(deg):
        a = math.radians(deg)
        v = o * math.cos(a) + head_dir * math.sin(a)
        return v / np.linalg.norm(v)

    root = p + o * (float(body.hw(s)) - 4.0)
    shoulder = p + o * float(body.hw(s))
    elbow = shoulder + rotv(ls["a1"]) * ls["l1"]
    wrist = elbow + rotv(ls["a2"]) * ls["l2"]
    pts = _round_corner(root, elbow, wrist, spec["joint_r"])
    return dict(pts=pts, wrist=wrist, fwd=rotv(ls["a2"]), side=side, spec=ls, elbow=elbow)


# -----------------------------------------------------------------------------
# gills
# -----------------------------------------------------------------------------
def _rachis(p, h0: float, curl: float, length: float, n: int = 90) -> np.ndarray:
    """An arc from p at heading h0 turning ``curl`` degrees over ``length``."""
    hs = h0 + curl * np.linspace(0, 1, n) ** 1.15
    step = length / (n - 1)
    pts = [np.asarray(p, float)]
    for h in hs[:-1]:
        pts.append(pts[-1] + unit(h) * step)
    return np.array(pts)


def plume_polygon(pts: np.ndarray, *, hw: float = 2.0, stalk: float = 1.2, tooth: float = 1.5,
                  pitch: float = 2.6, rake: float = 0.8, lean: float = 0.0, sides=(1, -1),
                  root: float = 0.18, tip: float = 0.22, grow: float = 0.3) -> Polygon:
    """A SOLID feathery gill ramus on the rachis ``pts`` (root → tip): a
    curved plume of half-width ``hw`` (a slim ``stalk`` at the root, full
    width after ``grow`` of the length, rounding off over the last ``tip``)
    whose edges carry the filament fringe — lobes ``tooth`` deep at ``pitch``,
    staggered side to side, each rising slowly toward the ramus tip then
    dropping back sharply, its point leaning ``lean`` px toward the tip: a
    feather's barbs, raked forward, never fir needles or antler tines."""
    cv = G.Curve(np.asarray(pts, float))
    Lg = cv.length
    m = 900
    t = np.linspace(0, 1, m)
    s = t * Lg
    P = cv.at_s(s)
    Tt = cv.tangent_s(s)
    N = np.column_stack([Tt[:, 1], -Tt[:, 0]])
    g = np.clip(t / max(grow, 1e-6), 0, 1)
    g = 0.5 - 0.5 * np.cos(np.pi * g)
    tz = np.clip((t - (1 - tip)) / tip, 0, 1)
    rnd = np.sqrt(np.clip(1 - tz ** 2, 0, 1))
    core = (stalk + (hw - stalk) * g) * rnd
    edges = []
    for sd, phase in ((1, 0.0), (-1, 0.5)):
        u = (s - root * Lg) / pitch + phase
        fr = u - np.floor(u)
        saw = np.where(fr < rake, fr / rake, 1 - (fr - rake) / (1 - rake))
        on = 1.0 if sd in sides else 0.0
        amp = on * np.where(s < root * Lg, 0.0, 1.0) * np.clip(g * 1.4, 0, 1) * rnd
        edges.append(P + N * sd * (core + tooth * saw * amp)[:, None] + Tt * (lean * saw * amp)[:, None])
    poly = Polygon(np.vstack([edges[0], edges[1][::-1]])).buffer(0)
    poly = poly.buffer(0.35, quad_segs=6).buffer(-0.35, quad_segs=6)
    return _largest(poly)


def gill_polys(body: Body, g: dict) -> list:
    polys = []
    for side in ("out", "in"):
        for k, sv in enumerate(g["s"]):
            o = body.out_dir(sv, side)
            tail = body.tangent(sv)
            a = math.radians(g["ang"][k])
            d0 = o * math.cos(a) + tail * math.sin(a)
            p = body.edge(side, [sv], fin=False)[0] - o * 1.0
            cross = d0[0] * tail[1] - d0[1] * tail[0]
            sgn = 1.0 if cross > 0 else -1.0                  # curl toward the tail
            pts = _rachis(p, ang_of(d0), g["curl"][k] * sgn, g["length"][k])
            pg = plume_polygon(pts, **g["plume"])
            r = g.get("round", 0.0)
            if r:              # soften every barb tip and notch (foil-friendly, feathery not spiky)
                pg = _largest(pg.buffer(r, quad_segs=8).buffer(-2 * r, quad_segs=8).buffer(r, quad_segs=8))
            polys.append(pg)
    return polys


# -----------------------------------------------------------------------------
# the drawing
# -----------------------------------------------------------------------------
def silhouette(body: Body, spec=SPEC):
    L = body.L
    s = np.linspace(0, L, 3000)
    left = body.edge("in", s)
    right = body.edge("out", s)
    body_poly = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    limbs = {}
    polys = [body_poly]
    for key in spec["limbs"]:
        lg = limb_geometry(body, key, spec)
        limbs[key] = lg
        if spec.get("limb_mode", "tube") == "tube":
            polys.append(tapered_tube(lg["pts"], *spec["limb_hw"]))
    sil = unary_union(polys)
    r = spec["fillet"]
    sil = sil.buffer(r, quad_segs=24, join_style="round").buffer(-r, quad_segs=24, join_style="round")
    # ease any convex kink (snout cap, tube caps) — nothing drawn is finer than 1.5 px radius
    sil = sil.buffer(-1.5, quad_segs=24, join_style="round").buffer(1.5, quad_segs=24, join_style="round")
    return _largest(sil), limbs, body_poly


def salamander(spec=SPEC, *, color: str = T.FOIL):
    """The salamander in its local frame (snout tip at the origin, body along +x)."""
    body = Body(spec)
    sil, limbs, body_poly = silhouette(body, spec)
    rings = [np.asarray(sil.exterior.coords)] + [np.asarray(r.coords) for r in sil.interiors]
    f = Frag()
    for rg in rings:
        f += stroke(polyline_d(rg, closed=True), FINE, color=color, role="contour")

    mode = spec.get("limb_mode", "tube")
    limb_shapes = []
    if mode == "solid":
        h0, h1, fr = spec["limb_solid"]
        interior = sil.buffer(-FINE / 2 + 0.05)
        band = sil.exterior.buffer(FINE / 2, quad_segs=8)
        for key, lg in limbs.items():
            tube = tapered_tube(lg["pts"], h0, h1, taper=1.2)
            shape = unary_union([tube, band]).buffer(fr, quad_segs=12).buffer(-fr, quad_segs=12)
            shape = shape.difference(interior).intersection(tube.buffer(fr + 2.0))
            shape = shape.difference(band.difference(tube.buffer(fr + 0.5)))
            shape = _largest(shape.buffer(0))
            f += fill(G.from_shape(shape), color=color, role="limb")
            limb_shapes.append(tube)
        r_hand = h1
    else:
        for lg in limbs.values():
            limb_shapes.append(tapered_tube(lg["pts"], *spec["limb_hw"]))
        r_hand = spec["limb_hw"][1]

    # digits: short strokes splayed from the wrist
    for key, lg in limbs.items():
        ls = lg["spec"]
        base = ang_of(lg["fwd"])
        n = ls["digits"]
        for i in range(n):
            u = (i - (n - 1) / 2) / ((n - 1) / 2)             # −1 … +1 across the hand
            a = base + u * ls["spread"] * (n - 1) / 2
            ln = ls["dl"] * (1.0 - 0.22 * u * u)
            p0 = lg["wrist"] + unit(a) * (r_hand - 0.6)
            p1 = lg["wrist"] + unit(a) * (r_hand + ln)
            f += stroke(polyline_d([p0, p1]), FINE, color=color, role="digit")

    # eyes: two dots under the skin, as wide-set as the foil gap allows
    es, eg = spec["eyes"]
    pe = body.at(es)
    ne = body.normal_in(es)
    off = float(body.hw(es)) - FINE / 2 - eg - 4.2 / 2
    for sg in (1, -1):
        e = pe + ne * off * sg
        f += dot(e[0], e[1], 4.2, color=color, role="eye")

    # gills
    gp = gill_polys(body, spec["gills"])
    for pg in gp:
        f += fill(G.from_shape(pg), color=color, role="gill")

    # the split line: nape -> tail, down the spine
    s0 = spec["split_s0"]
    s1 = body.split_end() if spec.get("split_s1") is None else spec["split_s1"]
    ss = np.linspace(s0, s1, int((s1 - s0) * 2) + 2)
    split = body.split_pts(ss)
    f += stroke(polyline_d(split), FINE, color=color, role="split")

    # the half-hatch on the outer half at the 7.0 pitch (square to the spine,
    # or leaning toward the tail tip); lines run centreline to centreline
    # (split -> outer contour), butt-capped, and keep 4.2 px clear of limbs
    limb_zone = unary_union(limb_shapes).difference(body_poly.buffer(-0.5)) if limb_shapes else Polygon()
    clear = limb_zone.buffer(FINE / 2 + spec["hatch_clear"] - 0.2) if not limb_zone.is_empty else Polygon()
    hatch_n = {}
    for (h0, h1, kind) in spec["hatch"]:
        h1 = min(h1, s1 - 6.0)             # no hatch hooked onto the split line's end cap
        lean = float(spec["hatch_angle"].get(kind, 0.0))
        step = T.HATCH_PITCH / math.cos(math.radians(lean))
        n = int(math.floor((h1 - h0) / step + 1e-6))
        start = h0 + ((h1 - h0) - n * step) / 2
        cnt = 0
        for k in range(n + 1):
            sv = start + k * step
            p = body.split_pts([sv])[0]
            o = body.out_dir(sv, "out")
            t = body.tangent(sv)                                # toward the tail
            a = math.radians(lean)
            v = o * math.cos(a) + t * math.sin(a)
            w = float(body.hw_out(sv))
            ray = LineString([p, p + v * (w / max(math.cos(a), 0.3) + 12.0)])
            hit = ray.intersection(sil.exterior)
            if hit.is_empty:
                continue
            pts = [np.array(g.coords[0]) for g in getattr(hit, "geoms", [hit])]
            q = min(pts, key=lambda v_: float(np.hypot(*(v_ - p))))
            seg = LineString([p, q])
            if not clear.is_empty and seg.intersects(clear):
                continue
            f += stroke(polyline_d([p, q]), FINE, style="hatch", color=color, role=f"hatch-{kind}")
            cnt += 1
        hatch_n[kind] = cnt

    # the tail tip: where the tail grows too slender to keep a 4.2 px bore
    # between its two contour strokes it is drawn SOLID — a crisp gold point
    bore = body.hw(body.s) + body.hw_out(body.s) - FINE
    thin = np.where((bore < GAP) & (body.s > body.L * 0.6))[0]
    if len(thin):
        s_tip = float(body.s[thin[0]])
        st = np.linspace(s_tip, body.L, 200)
        tip_poly = Polygon(np.vstack([body.edge("in", st), body.edge("out", st)[::-1]])).buffer(0)
        tip_poly = tip_poly.intersection(sil)
        if not tip_poly.is_empty:
            f += fill(G.from_shape(tip_poly), color=color, role="tail-tip")

    f.meta.update(body=body, silhouette=sil, limbs=limbs, gill_polys=gp, split_end=s1, hatch_n=hatch_n)
    return f


def curl_centre(body: Body, s0: float = 70.0, s1: float = 300.0) -> np.ndarray:
    """Centre of the circle best fitting the spine between s0 and s1 (the C's own centre)."""
    ss = np.linspace(s0, min(s1, body.L), 200)
    P = body.at(ss)
    A = np.column_stack([2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))])
    b = (P ** 2).sum(axis=1)
    cx, cy, _ = np.linalg.lstsq(A, b, rcond=None)[0]
    return np.array([cx, cy])


def min_enclosing_centre(f: Frag) -> np.ndarray:
    """Centre of the smallest circle enclosing all the ink."""
    from scipy.optimize import minimize
    sh = f.shape()
    hull = np.asarray(sh.convex_hull.exterior.coords)
    x0 = hull.mean(axis=0)
    res = minimize(lambda c: np.max(np.hypot(hull[:, 0] - c[0], hull[:, 1] - c[1])), x0,
                   method="Nelder-Mead", options=dict(xatol=1e-3, fatol=1e-4, maxiter=4000))
    return np.asarray(res.x)


def placed(cx: float, cy: float, facing_deg: float = 0.0, spec=SPEC, *, mirror: bool = False,
           offset=(0.0, 0.0), centre: str = "mec", **kw) -> Frag:
    """The salamander turned so that its snout points along screen angle
    ``facing_deg`` (0 = right), with its C centred on (cx, cy)
    (``centre='mec'``: the smallest circle round all the ink; ``'curl'``: the
    spine's fitted circle; ``'bbox'``), then nudged by ``offset``."""
    f = salamander(spec, **kw)
    meta = dict(f.meta)
    body = meta["body"]
    c = curl_centre(body)
    face = -body.tangent(12.0)
    if mirror:
        f = f.mirror_y(0.0)
        c = np.array([c[0], -c[1]])
        face = np.array([face[0], -face[1]])
    rot = facing_deg - ang_of(face)
    f = f.rotate(rot, c[0], c[1])
    if centre == "bbox":
        x0, y0, x1, y1 = f.bbox()
        c = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
    elif centre == "mec":
        c = min_enclosing_centre(f)
    dx, dy = cx - c[0] + offset[0], cy - c[1] + offset[1]
    f = f.translate(dx, dy)
    # the C's own centre (the spine's fitted circle — the rotation pivot, so
    # only the translation moves it) in placed coordinates
    cc = curl_centre(body)
    if mirror:
        cc = np.array([cc[0], -cc[1]])
    meta.update(rot=rot, mirror=mirror, curl_centre=(float(cc[0] + dx), float(cc[1] + dy)))
    f.meta.update(meta)
    return f


def scaled(spec, k: float, kw: float | None = None):
    """The drawing enlarged by ``k`` along its LENGTH (spine, positions, limb
    and gill lengths) and ``kw`` across its WIDTH (body and fin half-widths).
    Stroke widths, dot sizes, the limb tubes' bore, the eye clearance and the
    hatch pitch never scale: nothing that governs a line weight or a 4.2 px
    gap is touched."""
    kw = k if kw is None else kw
    sp = copy.deepcopy(spec)
    sp["L"] *= k
    sp["hw"] = [(a * k, b * kw) for a, b in sp["hw"]]
    sp["fin"] = [(a * k, b * kw) for a, b in sp["fin"]]
    sp["kappa"] = [(a * k, b / k) for a, b in sp["kappa"]]
    sp["snout_cap"] *= k
    sp["tip_r"] *= k
    sp["eyes"] = (sp["eyes"][0] * k, sp["eyes"][1])
    g = sp["gills"]
    g["s"] = tuple(v * k for v in g["s"])
    g["length"] = tuple(v * kw for v in g["length"])
    for ls in sp["limbs"].values():
        for key in ("s", "l1", "l2"):
            ls[key] *= k
    sp["joint_r"] *= k
    sp["split_s0"] *= k
    sp["split_shift"] = tuple(v * k for v in sp["split_shift"])
    sp["hatch"] = [(a * k, b * k, c) for a, b, c in sp["hatch"]]
    return sp


def variant(**changes):
    """A deep copy of SPEC with top-level / nested changes applied."""
    sp = copy.deepcopy(SPEC)
    for k, v in changes.items():
        if isinstance(v, dict) and isinstance(sp.get(k), dict):
            for kk, vv in v.items():
                if isinstance(vv, dict) and isinstance(sp[k].get(kk), dict):
                    sp[k][kk].update(vv)
                else:
                    sp[k][kk] = vv
        else:
            sp[k] = v
    return sp


def seal_spec():
    return copy.deepcopy(SPEC)
