"""Card back cypress bough (brief §H.19 "lens tips", §G.18).

A bald-cypress twig stands on the axis above the Source and points into the
top lens tip, where it ends in a round cone (§G.18).  It carries alternate
branchlets, each a comb spray (a rachis with short parallel ticks on both
sides, tick lengths on a vesica envelope).  The bough is deliberately
lopsided: on the clockwise side (screen right at the top) the branchlets
are long and arc over and down toward the 1 o'clock darter, like foliage
combed by the current; on the other side they stay short, leaving the
upper-left to the wild-rice.  With its 180° copy in the bottom tip, the
boughs carry the pinwheel across the axis.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from deck import tokens as T
from deck.motifs import core as C, geometric as M
from deck.motifs.forms import arc_path
from inkkit import geom as G

from art import _back_geo as BG

FINE = T.FINE

BOUGH = dict(
    twig=[("xy", 375.0, 370.0), ("xy", 375.0, 250.0), ("xy", 375.0, 116.0)],
    cone=11.5,
    lead_len=46.0, lead_tick=9.0,
    first=10.0, pitch=16.0, side0=1,               # side +1 = screen right (clockwise side)
    angle={1: 52.0, -1: 50.0},                     # branchlet angle off the twig
    bend={1: 115.0, -1: -24.0},                      # branchlet turn (+ clockwise) over its length
    env={1: (0.0, 0.5, 0.0, 0.0), -1: (0.0, 0.55, 0.0, 0.0)},  # peak len, at, base len, tip len
    tick=9.0, tick_angle=58.0, tick_pitch=7.7,
    min_len=14.0, lip=60.0,
)


def comb(pts, *, tick=11.0, angle=60.0, pitch=7.4, lead=3.0, tail=3.0, env=(0.18, 0.30),
         min_tick=3.5, taper_base=True):
    """§G.18 comb spray on the centreline ``pts`` (base -> tip): short
    parallel ticks on both sides, swept ``angle``° forward, at ``pitch`` px,
    their lengths on a smooth envelope (rising over the first env[0] of the
    length when ``taper_base``, falling over the last env[1]); the rachis is
    trimmed to ``lead`` px before the first tick and ``tail`` px beyond the
    last, so no bare rachis trails past the foliage."""
    cv = G.Curve(np.asarray(pts, float))
    L = cv.length
    sa = math.sin(math.radians(angle))
    pitch = max(pitch, (FINE + 4.2) / sa)
    n = int((L - 2.0) // pitch)
    if n < 1:
        return C.Frag()
    ss = 1.0 + (L - 2.0 - (n - 1) * pitch) / 2 + np.arange(n) * pitch
    f = C.Frag()
    used = []
    for s_ in ss:
        u = s_ / L
        k = 1.0
        if taper_base and u < env[0]:
            k = math.sin(0.5 * math.pi * u / env[0])
        if u > 1 - env[1]:
            k = min(k, math.sin(0.5 * math.pi * (1 - u) / env[1]))
        ln = tick * (0.25 + 0.75 * k)
        if ln < min_tick:
            continue
        p = cv.at_s(s_)
        t = cv.tangent_s(s_)
        a = math.atan2(t[1], t[0])
        for side in (1, -1):
            ang = a - side * math.radians(angle)
            q = p + ln * np.array([math.cos(ang), math.sin(ang)])
            f += C.stroke(C.polyline_d([p, q]), FINE, role="tick")
        used.append(s_)
    if not used:
        return C.Frag()
    s0 = 0.0 if not taper_base else max(0.0, used[0] - lead)
    s1 = min(L, used[-1] + tail)
    f = C.stroke(C.polyline_d(cv.sub(s0 / L, s1 / L).pts), FINE, role="rachis") + f
    return f


def _env(u, peak, at, base, tip):
    if u <= at:
        t = u / at
        return base + (peak - base) * math.sin(0.5 * math.pi * t)
    t = (u - at) / (1 - at)
    return tip + (peak - tip) * math.cos(0.5 * math.pi * t)


def branchlet(p, heading, length, bend, spec):
    _, bp, _ = arc_path(p[0], p[1], heading, [(length, bend)])
    return M.comb_spray(bp, tick=spec["tick"], angle=spec["tick_angle"], pitch=spec["tick_pitch"],
                        start=4.0, min_tick=3.5)


# nested arcs parallel to the right lens wall (centre of that wall's arc, R 463.2)
CASCADE = dict(c=(181.8, 525.0), radii=(420.0, 393.0, 366.0, 339.0, 312.0, 285.0, 258.0), sweep=80.0,
               min_piece=34.0, tick=12.0, angle=60.0, pitch=7.4, window=None)


def _limit_arc(cx, cy, r, a0, sweep, lim):
    """Largest a1 in (a0, a0 + sweep] such that the arc a0..a1 (plus tick
    reach) stays inside ``lim``; coarse march then bisection."""
    reach = BOUGH["tick"] * math.sin(math.radians(BOUGH["tick_angle"])) + FINE / 2
    inner = lim.buffer(-reach)
    step = 0.5
    a = a0
    while a + step <= a0 + sweep:
        p = (cx + r * math.cos(math.radians(a + step)), cy + r * math.sin(math.radians(a + step)))
        if not inner.contains(Point(p)):
            break
        a += step
    return a


def starts_at_twig(pts, twig_x=375.0):
    return abs(pts[0][0] - twig_x) < 1.0


def cascade(spec=CASCADE, others=None, limit=None, twig_x=375.0) -> C.Frag:
    """Right-hand branchlets: arcs parallel to the lens wall, springing
    from the twig and running clockwise to the limit region; each arc is
    broken GAP (+ tick reach) clear of the other motifs, and every piece
    becomes its own comb spray (vesica tick envelope)."""
    lim = limit if limit is not None else BG.limit_region()
    obs = unary_union([o.shape() for o in others]) if others else None
    reach = spec["tick"] * math.sin(math.radians(spec["angle"])) + FINE / 2
    zone = obs.buffer(BG.GAP + reach) if obs is not None else None
    cx, cy = spec["c"]
    f = C.Frag()
    log = []
    for r in spec["radii"]:
        y = cy - math.sqrt(r * r - (twig_x - cx) ** 2)
        a0 = math.degrees(math.atan2(y - cy, twig_x - cx))
        a1 = _limit_arc(cx, cy, r, a0, spec["sweep"], lim)
        line = LineString(C.sample_d(C.arc_d(cx, cy, r, a0, a1), 0.5)[0][0])
        pieces = line.difference(zone) if zone is not None else line
        for k, pc in enumerate(getattr(pieces, "geoms", [pieces])):
            if pc.is_empty or pc.length < spec["min_piece"]:
                continue
            pts = np.asarray(pc.coords)
            # keep the growth direction (clockwise = away from the twig)
            if np.hypot(*(pts[0] - (twig_x, y))) > np.hypot(*(pts[-1] - (twig_x, y))):
                pts = pts[::-1]
            f += comb(pts, tick=spec["tick"], angle=spec["angle"], pitch=spec["pitch"],
                      taper_base=k > 0 or not starts_at_twig(pts))
            log.append((round(r), round(pc.length)))
    f.meta["cascade"] = log
    return f


def bough(spec=BOUGH, others=None, limit=None) -> C.Frag:
    _, twig = BG.pspline(spec["twig"])
    cv = G.Curve(twig)
    L = cv.length
    lead0 = L - spec["lead_len"]
    f = C.Frag()
    f += C.stroke(C.polyline_d(cv.sub(0, lead0 / L).pts), FINE, role="twig")
    p0 = cv.at_s(0.0)
    f += C.dot(p0[0], p0[1], T.TERMINAL_D, role="terminal")
    f += M.comb_spray(cv.sub(lead0 / L, 1.0).pts, tick=spec["lead_tick"], angle=spec["tick_angle"],
                      pitch=spec["tick_pitch"], cone=spec["cone"], start=3.0, min_tick=3.5)
    lim = limit if limit is not None else BG.limit_region()
    obs = unary_union([o.shape() for o in others]) if others else None
    slots = []
    s, side = spec["first"], spec["side0"]
    end = lead0 - 4.0
    while s < end:
        p, t = cv.at_s(s), cv.tangent_s(s)
        h = math.degrees(math.atan2(t[1], t[0])) + side * spec["angle"][side]
        bd = spec["bend"][side]
        cap = _env(s / end, *spec["env"][side])

        def ok(Ln):
            sh = branchlet(p, h, Ln, bd, spec).shape()
            if not lim.contains(sh):
                return False
            return obs is None or sh.distance(obs) >= BG.GAP
        lo, hi = 0.0, cap
        if ok(hi):
            lo = hi
        else:
            while hi - lo > 1.0:
                m = (lo + hi) / 2
                if ok(m):
                    lo = m
                else:
                    hi = m
        slots.append([s, side, p, h, bd, lo])
        s += spec["pitch"]
        side = -side
    for sd in (-1, 1):
        idx = [i for i, sl in enumerate(slots) if sl[1] == sd]
        for _ in range(3):
            for a, b in zip(idx, idx[1:]):
                slots[b][5] = min(slots[b][5], slots[a][5] + spec["lip"])
                slots[a][5] = min(slots[a][5], slots[b][5] + spec["lip"])
    log = []
    for s, side, p, h, bd, Ln in slots:
        if Ln >= spec["min_len"]:
            f += branchlet(p, h, Ln, bd, spec)
            log.append((round(s), side, round(Ln)))
    f.meta["log"] = log
    return f
