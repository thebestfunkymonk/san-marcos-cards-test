"""Card back cypress bough (brief §H.19 "lens tips", §G.18 comb spray + cone).

A bald-cypress twig stands on the vertical axis above the Source and points
into the top lens tip, where it ends in a short comb spray and a round cone
(§G.18).  Along the twig, alternate branchlets -- each a comb spray (a
rachis with short parallel ticks on both sides, tick lengths on a vesica
envelope) -- spring from the twig.  The bough is deliberately C2, not
mirrored: the branchlets on the clockwise side (screen right at the top) are
long and sweep round the Source on orbits concentric with it, arching over
the 1 o'clock darter like foliage combed by the current; those on the other
side are short and lean toward the tip.  Its 180° copy fills the bottom tip.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from deck import tokens as T
from deck.motifs import core as C, geometric as M
from deck.motifs.forms import arc_spline, unit
from inkkit import geom as G

from art import _back_geo as BG

FINE = T.FINE
CX, CY = T.CX, T.CY


# ---------------------------------------------------------------------------
# the comb spray
# ---------------------------------------------------------------------------
def envelope(u, peak=0.4, base=0.25, tip=0.0):
    """Relative tick length along a spray (u = 0 base .. 1 tip): a vesica-
    like swell (circular-arc profile each side of ``peak``), never below
    ``base`` at the base and falling to ``tip`` at the end."""
    u = float(np.clip(u, 0, 1))
    if u <= peak:
        t = 1 - u / peak
        return base + (1 - base) * math.sqrt(max(0.0, 1 - t * t))
    t = (u - peak) / (1 - peak)
    return tip + (1 - tip) * math.sqrt(max(0.0, 1 - t * t))


def comb(pts, *, tick=10.0, angle=55.0, pitch=8.6, peak=0.4, base=0.3, tip=0.0, s_first=None,
         min_tick=3.2, sides=(1, -1), tail=2.0, bare=None, role="spray", stagger=False):
    """§G.18 comb spray on the centreline ``pts`` (base -> tip): parallel
    ticks swept ``angle``° toward the tip, both sides, ``pitch`` px apart
    along the rachis (perpendicular spacing pitch·sin(angle) >= 6.3), their
    lengths on :func:`envelope`.  The rachis starts at pts[0] (on the twig)
    and ends ``tail`` px past the last tick station, so the spray closes in
    a point of converging ticks rather than a bare stalk.  ``s_first`` is
    the first tick station (default: one pitch); ``bare`` = (s0, s1) arc-
    length intervals left without ticks."""
    pts = np.asarray(pts, float)
    cv = G.Curve(pts)
    L = cv.length
    sa = math.sin(math.radians(angle))
    pitch = max(pitch, (FINE + 4.2) / sa)
    s0 = pitch if s_first is None else s_first
    f = C.Frag()
    last = None
    ticks = []
    s = s0
    while s < L - 1.0:
        u = (s - s0) / max(L - s0, 1e-6)
        ln = tick * envelope(u, peak, base, tip)
        if ln >= min_tick and not (bare and any(a <= s <= b for a, b in bare)):
            p = cv.at_s(s)
            t = cv.tangent_s(s)
            a = math.atan2(t[1], t[0])
            for side in sides:
                if stagger and side == sides[-1] and len(sides) > 1:
                    s2 = s + pitch / 2
                    if s2 >= L - 1.0:
                        continue
                    p2, t2 = cv.at_s(s2), cv.tangent_s(s2)
                    a2 = math.atan2(t2[1], t2[0])
                    ang = a2 - side * math.radians(angle)
                    q = p2 + ln * np.array([math.cos(ang), math.sin(ang)])
                    ticks.append(C.polyline_d([p2, q]))
                    last = max(last or 0.0, s2)
                    continue
                ang = a - side * math.radians(angle)
                q = p + ln * np.array([math.cos(ang), math.sin(ang)])
                ticks.append(C.polyline_d([p, q]))
            last = max(last or 0.0, s)
        s += pitch
    if last is None:
        return C.Frag()
    s_end = min(L, last + tail)
    f += C.stroke(C.polyline_d(cv.sub(0, s_end / L).pts), FINE, role="rachis")
    f += C.stroke("".join(ticks), FINE, role="tick")
    f.meta["end"] = cv.at_s(s_end)
    return f


# ---------------------------------------------------------------------------
# geometry of the lens tip
# ---------------------------------------------------------------------------
def tip_centre(r_cone, gap):
    """Centre on the axis of a circle of radius ``r_cone`` (+ stroke) that
    keeps ``gap`` px of jade to the lens inner rule near the top tip."""
    lim = C.region(G.offset(BG.lens_d(), -(BG.LENS_IN + gap + r_cone + FINE / 2)))
    y0 = lim.bounds[1]
    return (CX, y0 + 0.5)


# ---------------------------------------------------------------------------
# the bough
# ---------------------------------------------------------------------------
CONE = 7.5                         # radius of the cones some branchlets carry (§G.18)

BOUGH = dict(
    y_base=372.0,                 # twig foot (terminal) above the rosette
    stem=3.15,                    # the twig drawn as a stem 6.3 px wide (two FINE rules, 4.2 apart)
    cone=10.5, cone_gap=20.5,     # the cone in the tip, 20 px of jade from the lens
    lead=dict(len=26.0, tick=8.0, pitch=8.6),   # short spray below the cone
    tick=dict(tick=12.0, angle=55.0, pitch=7.8, base=0.45),
    # clockwise-side branchlets: spring from the twig at y, head h0 (screen deg), then
    # follow the orbit of radius r about the Source clockwise to the limit
    right=[dict(y=315.0 - 26.0 * i, r=222.0 + 26.0 * i, h0=-14.0, cone=CONE if i in (1, 3) else None)
           for i in range(8)],
    # counter-clockwise side: shorter sprays leaning toward the tip
    left=[dict(y=330.0 - 48.0 * i, h0=-166.0, turn=48.0, L=116.0, cone=CONE if i == 1 else None)
          for i in range(4)],
    sweep_max=100.0,              # clock degrees an orbit branchlet may run
    min_len=24.0,
    clear=4.2,                    # paper-to-paper clearance between branchlets (§I.12)
)


def orbit_path(y0, r, h0, clock_max, n=40):
    """Branchlet centreline: from the twig at (375, y0) heading h0, easing
    onto the orbit of radius r about the Source and following it clockwise
    up to ``clock_max``."""
    c1 = 12.0
    way = [("xy", CX, y0)] + [(r, c) for c in np.linspace(c1, clock_max, max(3, int((clock_max - c1) / 6) + 1))]
    return BG.pspline(way, h0, None)[1]


def _trim(pts, keep):
    """Longest leading run of ``pts`` (from the twig) inside ``keep``."""
    ls = LineString(pts)
    inside = ls.intersection(keep)
    best = None
    for g in getattr(inside, "geoms", [inside]):
        if g.is_empty or g.geom_type != "LineString":
            continue
        c = np.asarray(g.coords)
        if np.hypot(*(c[0] - pts[0])) < 1.0:
            best = c
    return best


_TWIG_STRIP = box(CX - 8.0, 0.0, CX + 8.0, 2 * CY)


def _spray(cv, Ln, tk, cone=None):
    """Comb spray on the first ``Ln`` px of ``cv``; with ``cone`` (radius)
    the spray ends in a round cypress cone (§G.18) whose rim the rachis
    meets, the ticks stopping 3 px short of it."""
    L = cv.length
    if not cone:
        return comb(cv.sub(0, min(1.0, Ln / L)).pts, **tk)
    s_c = Ln - cone - FINE / 2                    # cone centre (arc length)
    s_t = s_c - cone - 4.0                        # last tick station
    if s_t < 16.0:
        return comb(cv.sub(0, min(1.0, Ln / L)).pts, **tk)
    f = comb(cv.sub(0, s_t / L).pts, **dict(tk, tail=0.0))
    # the rachis runs on (overlapping the comb's own) to the cone's rim
    f += C.stroke(C.polyline_d(cv.sub(max(0.0, s_t - 12.0) / L, (s_c - cone) / L).pts), FINE, role="rachis")
    c, t = cv.at_s(s_c), cv.tangent_s(s_c)
    f += M.cypress_cone(c[0], c[1], cone, rot=math.degrees(math.atan2(t[1], t[0])))
    return f


def _fit(pts, tk, placed, clear, min_len, cone=None):
    """The longest comb spray along a leading part of ``pts`` that stays
    ``clear`` px from the ``placed`` branchlets (None if under min_len)."""
    cv = G.Curve(pts)
    L = cv.length

    def ok(g):
        # branchlets meet only at the twig: the 8 px strip round it is not checked
        return placed is None or g.shape().difference(_TWIG_STRIP).distance(placed) >= clear
    g = _spray(cv, L, tk, cone)
    if ok(g):
        return g, L
    lo, hi = 0.0, L
    best = None
    while hi - lo > 2.0:
        m = (lo + hi) / 2
        g = _spray(cv, m, tk, cone)
        if m >= min_len and ok(g):
            lo, best = m, (g, m)
        else:
            hi = m
    return best if best else (None, 0.0)


def bough(spec=BOUGH, others=(), limit=None, obstacle=None) -> C.Frag:
    """Twig on the axis from the terminal at ``y_base`` up to the cone in the
    lens tip, a lead spray under the cone, and alternate branchlets: long
    orbit sprays on the clockwise side, shorter sprays leaning toward the tip
    on the other.  Each branchlet is trimmed to the limit region (tick reach
    inside it), kept BG.GAP clear of the ``others`` motifs, and shortened
    until it stays ``clear`` px from the branchlets already placed (placed
    from the foot of the twig upward)."""
    lim = limit if limit is not None else BG.limit_region()
    obs = obstacle if obstacle is not None else (unary_union([o.shape() for o in others]) if others else None)
    tk = spec["tick"]
    reach = tk["tick"] * math.sin(math.radians(tk["angle"])) + FINE / 2
    keep = lim.buffer(-reach)
    if obs is not None:
        keep = keep.difference(obs.simplify(0.1).buffer(BG.GAP + reach + 1.0))
    f = C.Frag()
    # twig + lead spray + cone
    cc = tip_centre(spec["cone"], spec["cone_gap"])
    y_top = cc[1] + spec["cone"]
    ld = spec["lead"]
    h = spec.get("stem")
    if h:
        # the twig as a stem with body: two rules 2h apart closed by round ends, the
        # lead spray's rachis rising from the apex of the upper end
        y0, y1 = spec["y_base"] - h, y_top + ld["len"] + h
        f += C.stroke(f"M{CX - h:.3f} {y1:.3f}L{CX - h:.3f} {y0:.3f}"
                      f"A{h:.3f} {h:.3f} 0 0 0 {CX + h:.3f} {y0:.3f}L{CX + h:.3f} {y1:.3f}"
                      f"A{h:.3f} {h:.3f} 0 0 0 {CX - h:.3f} {y1:.3f}Z", FINE, role="twig")
    else:
        f += C.stroke(C.polyline_d([(CX, spec["y_base"]), (CX, y_top)]), FINE, role="twig")
        f += C.dot(CX, spec["y_base"], T.TERMINAL_D, role="terminal")
    head = M.cypress_cone(cc[0], cc[1], spec["cone"], rot=-90.0)
    lead_pts = np.array([(CX, y_top + ld["len"]), (CX, y_top)])
    head += comb(lead_pts, tick=ld["tick"], angle=ld.get("angle", tk["angle"]), pitch=ld["pitch"], peak=0.35,
                 base=0.5, tip=0.35, s_first=4.0, tail=0.0, sides=ld.get("sides", (1, -1)))
    f += head
    # candidate branchlets, foot of the twig first
    cands = []
    for b in spec["right"]:
        cands.append((b["y"], "R", orbit_path(b["y"], b["r"], b["h0"], spec["sweep_max"]), b.get("cone")))
    for b in spec["left"]:
        cands.append((b["y"], "L", arc_spline_turn(CX, b["y"], b["h0"], b["L"], b["turn"])[1], b.get("cone")))
    cands.sort(key=lambda c: -c[0])
    placed = head.shape()
    log = []
    for y, side, pts, cone in cands:
        pts = _trim(pts, keep.union(Point(CX, y).buffer(reach + 2)))
        if pts is not None and h:
            # branchlets spring from the stem's outer rule
            out = np.abs(pts[:, 0] - CX) >= h
            if out.any():
                i = int(np.argmax(out))
                if i > 0:
                    a, b = pts[i - 1], pts[i]
                    t = (h - abs(a[0] - CX)) / max(abs(b[0] - a[0]), 1e-9)
                    pts = np.vstack([a + (b - a) * t, pts[i:]])
            else:
                pts = None
        if pts is None or G.Curve(pts).length < spec["min_len"]:
            continue
        g, Ln = _fit(pts, tk, placed, spec["clear"], spec["min_len"], cone)
        if g is None:
            continue
        f += g
        placed = placed.union(g.shape().difference(_TWIG_STRIP))
        log.append((side, round(y), round(Ln)))
    f.meta["log"] = log
    return f


def arc_spline_turn(x, y, h0, L, turn):
    """A circular arc from (x, y) heading h0 turning ``turn`` degrees
    (+ clockwise) over length L."""
    from deck.motifs.forms import arc_path
    return arc_path(x, y, h0, [(L, turn)])
