"""scratch: a wild-rice wreath with per-side blade control (candidate for _aces_reed.wreath)."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point
import shapely

from deck import tokens as T
from deck import motifs as M
from deck.motifs import rice as RI
from deck.motifs import core as MC
from deck.motifs.forms import arc_path
from inkkit import geom as G

from art import _aces_common as A

FINE = T.FINE
GOLD = T.FOIL


def blade(p, a: float, side: int, L: float, W: float, angle: float, bend, pet: float, hatch_out: int = 1,
          split: float | None = 0.5):
    """One ribbon blade springing tangentially from the stem at ``p`` (stem
    heading ``a``) on ``side`` (+1 left of travel): petiole turning ``angle``°
    away over ``pet`` px, then a §G.4 S midrib of two tangent arcs, ``bend`` =
    (b0, b1) degrees, + = away from the stem."""
    _, pp, _ = arc_path(p[0], p[1], a, [(pet, -side * angle)])
    q = pp[-1]
    h = a - side * angle
    lf = RI.ribbon_leaf(q[0], q[1], h, L, W, bend=(-side * bend[0], -side * bend[1]),
                        hatch=0, narrow="tip", full=False, color=GOLD)
    if split is not None:
        lf += RI._tip_half_hatch(lf.meta["mid"], lf.meta["hw"], split=split, color=GOLD)
    unit = M.stroke(M.polyline_d(pp), FINE, color=GOLD, role="petiole") + lf
    reg = M.region(M.polyline_d(lf.meta["outline"], closed=True))
    return unit, reg, q


def wreath(cx, cy, r, *, knot_deg=90.0, tip_deg=30.0, step_deg=14.0, first=0.55, n_pairs=None,
           outer=dict(L=90.0, ratio=13.0, angle=12.0, bend=(10.0, -18.0)),
           inner=dict(L=52.0, ratio=13.0, angle=34.0, bend=(-14.0, 14.0)),
           shrink=0.06, spike=None, hatch_out=1, inner_top=False):
    pts = G.arc_pts(cx, cy, r, knot_deg, tip_deg, n=400)
    cv = G.Curve(pts)
    Ls = cv.length
    pitch = math.radians(step_deg) * r
    stations = []
    s = first * pitch
    while s < Ls - 6:
        stations.append(s)
        s += pitch
    if n_pairs is not None:
        stations = stations[:n_pairs]
    units = []
    bases = []
    for k, s in enumerate(stations):
        sc = (1 - shrink) ** k
        p = cv.at_s(s)
        t = cv.tangent_s(s)
        a = math.degrees(math.atan2(t[1], t[0]))
        pair = []
        for side, spec in ((1, inner), (-1, outer)):          # +1 = left of travel = inside (toward the club)
            L = spec["L"] * sc
            W = L / spec["ratio"]
            pet = spec.get("pet", max(6.0, 0.1 * L))
            u_, reg, q = blade(p, a, side, L, W, spec["angle"], spec["bend"], pet, hatch_out,
                               spec.get("split", 0.5))
            pair.append((u_, reg))
            bases.append(q)
        if inner_top:
            pair = pair[::-1]
        units += pair
    # the stem
    stem = M.stroke(M.polyline_d(pts), FINE, color=GOLD, role="stem")
    p = cv.at_s(Ls)
    t = cv.tangent_s(Ls)
    sk = dict(n_female=3, n_male=0, spikelet_len=12.0, awn=15.0, female_spread=64.0, pedicel=8.0, f_pitch=14.0)
    sk.update(spike or {})
    length = sk.pop("length", 44.0)
    sp = M.rice_stalk(p[0], p[1], math.degrees(math.atan2(t[1], t[0])), length, color=GOLD, **sk)
    # stacking: tip-ward over knot-ward
    lv = M.Frag()
    front = None
    for u_, reg in units[::-1]:
        lv += MC.occlude(u_, front) if front is not None else u_
        front = reg if front is None else front.union(reg)
    lv = MC.cut(lv, sp.shape(), A.CLEAR)
    lv = MC.prune_hatch(MC.drop_specks(lv, 4.2, roles=None), 1.3)
    # stem breaks only where a blade crosses it away from its own base
    line = LineString(pts)
    near = shapely.union_all([Point(q).buffer(12.0) for q in bases])
    cross = [reg for _, reg in units if reg.intersects(line) and not reg.intersection(line).within(near)]
    if cross:
        stem = MC.cut(stem, shapely.union_all(cross).difference(near), A.CLEAR)
    ext = M.polyline_d([p - t * 1.0, p + t * 10.0])
    stem = stem + M.stroke(ext, FINE, color=GOLD, role="stem")
    branch = stem + lv + sp
    out = branch + branch.mirror_x(cx)
    p0 = cv.at_s(0)
    k_f = RI._reed_knot((cx, p0[1]), 90.0, color=GOLD)
    out = MC.drop_specks(MC.occlude(out, k_f.meta["zone"]), 4.2, roles=None) + k_f
    out.meta.update(n_pairs=len(stations), stem=pts)
    return out
