"""HEADWATERS geometric ornament vocabulary (creative brief §G).

Every function builds its motif at FINAL size from circles, arcs and straight
lines, and returns a :class:`deck.motifs.core.Frag` (line mode via
``.svg()``/``.layers()``, knockout mode via ``core.knockout(solid, frag)``).

Common keyword arguments (every motif):
  w       stroke width — must be a legal token (§B.2); default FINE (2.1)
  color   palette colour (§C); the print layer follows from it
  layer   override the layer (rarely needed)

Placement: motifs take their anchor position(s) directly; most also take
``rot`` (screen degrees, clockwise positive) applied about their anchor.

Spacing: generators keep >= 4.2 px clear between parallel strokes (§I.12)
at their defaults and record any compromise in ``frag.meta['warnings']``.
"""
from __future__ import annotations

import math
from typing import Sequence

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box

from inkkit import geom as G

from deck import tokens as T
from .core import (DIAG, MIN_CLEAR, Frag, Turtle, arc_between, arc_d, bubble, bubble_path,
                   bubble_row, bubble_sizes, circle_d, cut, dashes, dot, ellipse_arc_d,
                   frag, half_hatch, hatch, lozenge_d, polar, polyline_d, region,
                   sample_d, split_region, stroke, terminal)

__all__ = [
    "source_rosette", "rosette_spec", "crater", "rib_band", "bubble_ring", "concentric_rings",
    "wave_hook", "running_wave", "running_wave_d2", "running_wave_ring", "WAVE_HOOK",
    "ripple_rings", "bubble_beading",
    "fault_step", "fault_plinth",
    "strata", "karst_void", "karst_voids", "stalactite", "drip_fringe",
    "scale_lattice", "cypress_knee", "knee_crenellation",
    "comb_spray", "cypress_cone", "reed_ladder", "reed_node", "reed_node_medallion",
    "ashlar", "arch", "arcade", "rowel_star", "stepping_stones",
    "lens_geometry", "lens_cartouche", "lens_field",
    "vent_roundel", "festoon", "pearl_beading", "conduit", "conduit_break",
    "volute", "tooled_scroll",
]

FINE, MEDIUM, HAIR, RULE = T.FINE, T.MEDIUM, T.HAIRLINE, T.RULE
TD = T.TERMINAL_D


def _warn(f: Frag, msg: str) -> Frag:
    f.meta.setdefault("warnings", []).append(msg)
    return f


# =============================================================================
# §G.7 running-wave scroll (Vitruvian wave)
# =============================================================================
# A wave "hook": a quarter circle (radius a) springs TANGENTIALLY off the band
# rule and rises, then a semicircle (radius b) curls over the crest, then an
# inner semicircle (radius b/2) turns the curl in on itself so its free end —
# finished with the Ø6.3 terminal (§B.2) — sits exactly at the crest's centre,
# the "eye" of the wave. Height above the rule = a + b; width = a + 2b.
# Defaults (§G.7: 30 px pitch, 10 px amplitude → 20 px crest height) keep
# >= 4.2 px clear everywhere: eye to crest = b − 4.2 = 4.8; eye to rule =
# a − 4.2 = 6.8; inner curl to rule = a − b/2 − 2.1 = 4.4.
WAVE_HOOK = dict(height=20.0, a=11.0, pitch=30.0)


def wave_hook(height: float = 20.0, a: float | None = None, *, eye: bool = True,
              w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """One wave hook in LOCAL coordinates: springs from (0, 0) heading +x
    (flow direction) and rises toward −y. ``height`` = crest above the rule
    (centreline), ``a`` = rise radius (default 0.55·height)."""
    a = 0.55 * height if a is None else a
    b = height - a
    t = Turtle(0.0, 0.0, 0.0)
    t.arc(a, -90).arc(b, 180).arc(b / 2, 180)
    f = stroke(t.d(), w, color=color, layer=layer, role="wave")
    if eye:
        f += terminal(*t.pos, color=color, layer=layer)
    f.meta.update(wave_a=a, wave_b=b, wave_width=a + 2 * b, wave_eye=tuple(t.pos))
    return f


def running_wave(x0: float, x1: float, y: float, *, height: float = 20.0, pitch: float = 30.0,
                 a: float | None = None, flow: int = 1, up: int = -1, rule: bool = True,
                 start: float | None = None, eye: bool = True, w: float = FINE,
                 color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.7 running wave along the horizontal rule y from x0 to x1.

    flow  +1 waves curl toward +x, −1 toward −x
    up    −1 crests rise toward −y (up the page), +1 toward +y
    rule  draw the band rule (the waves spring tangentially from it)
    start first spring point (default: centred so equal lead-in/out)
    The number of waves is as many whole pitches as fit."""
    hook = wave_hook(height, a, eye=eye, w=w, color=color, layer=layer)
    width = hook.meta["wave_width"]
    L = abs(x1 - x0)
    n = int((L - width) // pitch) + 1 if L >= width else 0
    f = Frag()
    if rule:
        f += stroke(polyline_d([(x0, y), (x1, y)]), w, style="rule", color=color, layer=layer, role="rule")
    if n <= 0:
        return _warn(f, "running_wave: band too short for one wave")
    used = (n - 1) * pitch + width
    lo = min(x0, x1)
    s0 = lo + (L - used) / 2 if start is None else start
    for k in range(n):
        h = hook
        if flow < 0:
            h = h.mirror_x(0.0)
        if up > 0:
            h = h.mirror_y(0.0)
        if flow > 0:
            f += h.translate(s0 + k * pitch, y)
        else:
            f += h.translate(lo + L - (s0 - lo) - k * pitch, y)
    f.meta.update(n_waves=n, wave_pitch=pitch)
    return f


def running_wave_d2(cx: float, y: float, half_len: float, *, gap: float = 30.0, **kw) -> Frag:
    """Straight band mirrored at the axis x = cx, flowing OUTWARD (§G.7):
    waves start flush at ``gap`` px from the axis (the clear zone for the
    fault-step plinth) and run toward ±half_len; the left half is the mirror
    of the right. Other keywords as :func:`running_wave`; the rule runs the
    full length unless ``rule=False``."""
    rule = kw.pop("rule", True)
    w = kw.get("w", FINE)
    color, layer = kw.get("color", T.INK), kw.get("layer")
    pitch = kw.get("pitch", 30.0)
    wd = wave_hook(kw.get("height", 20.0), kw.get("a"), w=w).meta["wave_width"]
    n = int((half_len - gap - wd) // pitch) + 1
    right = running_wave(cx + gap, cx + gap + (n - 1) * pitch + wd, y, flow=1, rule=False,
                         start=cx + gap, **kw)
    f = right + right.mirror_x(cx)
    if rule:
        f += stroke(polyline_d([(cx - half_len, y), (cx + half_len, y)]), w, style="rule",
                    color=color, layer=layer, role="rule")
    f.meta.update(n_waves=2 * n)
    return f


def running_wave_ring(cx: float, cy: float, r_base: float, *, n: int | None = None,
                      r_limit: float | None = None, height: float = 20.0, a: float | None = None,
                      clockwise: bool = True, mirrored: bool = False, rule: bool = True,
                      eye: bool = True, w: float = FINE, color: str = T.INK,
                      layer: str | None = None) -> Frag:
    """§G.7 on a ring: rigid wave hooks springing tangentially OUTWARD from
    the circle r_base (true arcs; exact C_n symmetry), flowing clockwise.

    r_limit  if given, the hook height is reduced until every hook stays
             inside r_limit − w/2 (use outer_rule − 4.2 − w).
    mirrored D2 version: waves flow away from 12 and 6 o'clock toward 3 and 9,
             where a Ø6.3 dot receives them (achiral; for straight-rib rosettes).
    """
    hgt = height
    for _ in range(40):
        hook = wave_hook(hgt, None if a is None else a * hgt / height, eye=eye, w=w, color=color, layer=layer)
        # hook in local coords springs at (0,0) heading +x, rising to −y.
        # place at top of circle: spring point (cx, cy − r_base), heading +x = clockwise.
        placed = hook.translate(cx, cy - r_base)
        g = placed.shape()                      # max radius from the exact outline
        rmax = max(math.hypot(px - cx, py - cy) for px, py in np.asarray(g.convex_hull.exterior.coords))
        if r_limit is None or rmax <= r_limit + 1e-6:
            break
        hgt -= 0.1
    width = hook.meta["wave_width"]
    if n is None:
        n = max(4, int(round(2 * math.pi * r_base / (width + 5.0))))
    f = Frag()
    if rule:
        f += stroke(circle_d(cx, cy, r_base), w, color=color, layer=layer, role="rule")
    if not mirrored:
        unit = hook if clockwise else hook.mirror_x(0.0)
        unit = unit.translate(cx, cy - r_base)
        for k in range(n):
            f += unit.rotate(360.0 * k / n, cx, cy)
    else:
        # quadrant 12→3 flowing clockwise; mirror for the rest
        dot_d = TD
        m = max(1, n // 4)
        span = 90.0
        unit = hook.translate(cx, cy - r_base)
        quad = Frag()
        # angular width of a hook at r_base
        ang_w = math.degrees(width / r_base)
        step = (span - ang_w - math.degrees((dot_d / 2 + 4.2 + w) / r_base)) / max(m - 0.5, 1)
        for k in range(m):
            quad += unit.rotate(math.degrees(3.0 / r_base) + k * step + step / 2, cx, cy)
        f += quad + quad.mirror_x(cx) + quad.mirror_y(cy) + quad.rot180(cx, cy)
        f += dot(cx + r_base, cy, dot_d, color=color, layer=layer) + dot(cx - r_base, cy, dot_d, color=color, layer=layer)
    f.meta.update(n_waves=n, wave_height=hgt, wave_rmax=rmax)
    if hgt < height - 1e-6:
        _warn(f, f"running_wave_ring: height reduced {height} → {hgt:.1f} to clear r_limit")
    return f


# =============================================================================
# §G.1 Source Rosette
# =============================================================================
def crater(cx: float, cy: float, r: float, *, n: int = 8, hub: float = 8.0, twist: float = 30.0,
           dot_d: float | None = 4.2, rim: bool = True, w: float = FINE, color: str = T.INK,
           layer: str | None = None) -> Frag:
    """The vent crater: rim circle r, hub circle ``hub``, ``n`` ribs between
    them. ``twist`` > 0 makes each rib a circular arc whose outer end is
    rotated clockwise by ``twist`` degrees (C_n); 0 = straight radial ribs
    (D_n). ``dot_d`` puts a solid dot at the centre."""
    f = Frag()
    if rim:
        f += stroke(circle_d(cx, cy, r), w, color=color, layer=layer)
    if hub:
        f += stroke(circle_d(cx, cy, hub), w, color=color, layer=layer)
    if dot_d:
        f += dot(cx, cy, dot_d, color=color, layer=layer)
    f += _ribs(cx, cy, hub if hub else 0.0, r, n, twist, w=w, color=color, layer=layer)
    return f


RIB_BOW = 0.14   # rib sagitta / chord: a gentle turbine sweep (not a hook)


def _rib_d(cx, cy, r0, r1, theta, twist, bow=RIB_BOW):
    """One rib from (r0, theta) to (r1, theta + twist): a circular arc with
    sagitta ``bow``·chord, bowing toward the counter-clockwise side (so the
    band reads as turning clockwise), or a straight line when twist = 0."""
    p0 = polar(cx, cy, r0, theta)
    p1 = polar(cx, cy, r1, theta + twist)
    if abs(twist) < 1e-9 or bow <= 0:
        return polyline_d([p0, p1]), None
    ch = p1 - p0
    L = float(np.hypot(*ch))
    s = bow * L * (1 if twist > 0 else -1)
    R = (L * L / 4 + s * s) / (2 * abs(s))
    # screen-left normal of p0→p1 (y down): (ch_y, −ch_x)/L; bow to the left
    nl = np.array([ch[1], -ch[0]]) / L
    mid = (p0 + p1) / 2
    c = mid - nl * np.sign(s) * (R - abs(s))
    a0 = math.degrees(math.atan2(p0[1] - c[1], p0[0] - c[0]))
    a1 = math.degrees(math.atan2(p1[1] - c[1], p1[0] - c[0]))
    sweep = (a1 - a0 + 180.0) % 360.0 - 180.0      # the minor arc
    return f"M{p0[0]:.3f} {p0[1]:.3f}" + arc_d(c[0], c[1], R, a0, a0 + sweep, move=False), (c, R, sweep > 0)


def _ribs(cx, cy, r0, r1, n, twist, start=-90.0, **kw):
    d = "".join(_rib_d(cx, cy, r0, r1, start + 360.0 * k / n, twist)[0] for k in range(n))
    return stroke(d, kw.pop("w", FINE), **kw, role="rib")


def rib_band(cx: float, cy: float, r0: float, r1: float, *, n: int = 24, twist: float = 25.0,
             hatch_cells: str | None = "alternate", hatch_angle: str | float = "rung",
             rules: bool = True, start: float = -90.0, w: float = FINE, color: str = T.INK,
             layer: str | None = None) -> Frag:
    """Pinwheel band between rules r0 and r1: ``n`` ribs twisted clockwise by
    ``twist`` degrees (0 = straight, D2-safe). ``hatch_cells`` 'alternate'
    hatches every other cell (FINE, 7.0 pitch, butt on the rib and rule
    centrelines); None leaves all open. ``hatch_angle`` 'rung' = lines across
    the cell perpendicular to the ribs' mean direction (rotates with the cell,
    so C_n symmetry holds); or a fixed angle relative to the radius."""
    f = Frag()
    if rules:
        f += stroke(circle_d(cx, cy, r0), w, color=color, layer=layer, role="rule")
        f += stroke(circle_d(cx, cy, r1), w, color=color, layer=layer, role="rule")
    f += _ribs(cx, cy, r0, r1, n, twist, start=start, w=w, color=color, layer=layer)
    if hatch_cells:
        # one cell polygon (between rib 0 and rib 1), hatched once and rotated
        cell = _band_cell(cx, cy, r0, r1, start, 360.0 / n, twist)
        mid = start + 180.0 / n + twist / 2
        if hatch_angle == "rung":
            ang = mid + 90 + twist * 0.6         # across the twisted cell
        else:
            ang = mid + float(hatch_angle)
        h = hatch(cell, ang, color=color, layer=layer)
        for k in range(0, n, 2):
            f += h.rotate(360.0 * k / n, cx, cy)
    return f


def _band_cell(cx, cy, r0, r1, a0, da, twist, step=0.25):
    def rib_pts(theta):
        return sample_d(_rib_d(cx, cy, r0, r1, theta, twist)[0], step)[0][0]
    ra = rib_pts(a0)
    rb = rib_pts(a0 + da)
    outer = G.arc_pts(cx, cy, r1, a0 + twist, a0 + da + twist)
    inner = G.arc_pts(cx, cy, r0, a0 + da, a0)
    ring = np.vstack([ra, outer, rb[::-1], inner])
    pg = Polygon(ring)
    return pg if pg.is_valid else shapely.make_valid(pg)


def bubble_ring(cx: float, cy: float, r: float, n: int = 24, d: float = 7.0, *, start: float = -90.0,
                style: str = "ring", w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """``n`` bubbles (centreline Ø ``d``) evenly on the circle r (§G.1)."""
    f = Frag()
    for k in range(n):
        p = polar(cx, cy, r, start + 360.0 * k / n)
        f += bubble(*p, d, style=style, w=w, color=color, layer=layer)
    return f


def concentric_rings(cx: float, cy: float, radii: Sequence[float], *, w: float = FINE,
                     color: str = T.INK, layer: str | None = None) -> Frag:
    return frag(*[stroke(circle_d(cx, cy, r), w, color=color, layer=layer, role="ring") for r in radii])


# Rosette recipes (§G.1). Each is designed at a natural size and only ever
# scaled UP (radii × R/R_design, dot sizes fixed), so no gap ever shrinks:
#   full   R 130 — the back, the brief's exact radii
#   medium R 90  — crater, 2 rings, bubble ring, 20-rib band (tuck-size)
#   small  R 40  — A♥ (MEDIUM knockout): the vent dot, a ring of six Ø7 bubbles
#                  (the rosette's signature bubble ring — no bullseye rings,
#                  which read as a dartboard), a 12-rib band
#   tiny   R 16  — jewels/finials: centre dot + a ring of bubble dots inside
#                  the rim (a spring vent in miniature; swirling blades read
#                  as a camera aperture)
# ``bubble_style`` 'ring' = stroked circles of centreline Ø; 'dot' = solid dots.
_RECIPES = {
    "full": dict(R=130.0, hub=8.0, dot=4.2, crater=20.0, crater_ribs=8, rings=(30.0, 39.0, 50.0),
                 bubbles=(62.0, 24, 7.0), band=(72.0, 104.0, 24), wave=True, rule=130.0),
    "medium": dict(R=90.0, hub=8.0, dot=4.2, crater=18.0, crater_ribs=8, rings=(27.0, 36.0),
                   bubbles=(46.0, 18, 6.3), band=(56.0, 90.0, 20), wave=False, rule=90.0),
    "small": dict(R=40.0, hub=0.0, dot=8.4, crater=0.0, crater_ribs=0, rings=(),
                  bubbles=(14.0, 6, 7.0), bubble_style="ring", band=(25.0, 40.0, 12), wave=False, rule=40.0),
    "tiny": dict(R=16.0, hub=0.0, dot=4.2, crater=0.0, crater_ribs=0, rings=(), bubbles=(8.5, 6, 4.2),
                 bubble_style="dot", band=None, wave=False, rule=16.0),
}


def _scaled(name, R, w=FINE):
    rc = _RECIPES[name]
    k = R / rc["R"]
    sp = dict(rc)
    sp["R"] = R
    for key in ("hub", "crater"):
        sp[key] = rc[key] * k if rc[key] else rc[key]
    sp["rings"] = tuple(r * k for r in rc["rings"])
    if rc["bubbles"]:
        rb, nb, db = rc["bubbles"]
        sp["bubbles"] = (rb * k, nb, db)
    if rc["band"]:
        r0, r1, nb = rc["band"]
        sp["band"] = (r0 * k, r1 * k, nb)
    sp["rule"] = rc["rule"] * k if rc["rule"] else None
    if name == "tiny":
        # the bubble ring fills the annulus between the centre dot and the rim,
        # 4.2 px clear of both: the largest legal dot (Ø6.3 / Ø4.2) that fits,
        # as many as keep 4.2 px between neighbours (even, so D2 holds)
        lo = sp["dot"] / 2 + MIN_CLEAR
        hi = R - w / 2 - MIN_CLEAR
        db = 6.3 if hi - lo >= 6.3 else 4.2
        rb = (lo + hi) / 2
        nb = max(6, 2 * int(2 * math.pi * rb / (db + MIN_CLEAR) // 2))
        nb = min(nb, 8)
        sp["bubbles"] = (rb, nb, db)
    return sp


def rosette_spec(R: float = 130.0, w: float = FINE, detail: str | None = None) -> dict:
    """The band recipe for a rosette of outer radius R drawn at width w.

    detail: 'full' (the back, R >= 130), 'medium' (R >= 90), 'small'
    (R >= 40), 'tiny' (R >= 16), or None to pick the richest recipe whose
    design size is <= R and whose gaps all stay >= 4.2 px clear at width w.
    Recipes scale up only. Returns a dict (radii in px) with 'detail'."""
    s = w + MIN_CLEAR
    order = ["full", "medium", "small", "tiny"]
    cands = [detail] if detail else order
    for name in cands:
        if R < _RECIPES[name]["R"] - 1e-9 and not detail:
            continue
        sp = _scaled(name, R, w)
        if _spec_ok(sp, w, s) or detail:
            return {**sp, "detail": name}
    return {**_scaled("tiny", max(R, 16.0), w), "detail": "tiny"}


def _spec_ok(sp, w, s) -> bool:
    radii = []
    if sp.get("dot"):
        radii.append(("dot", sp["dot"] / 2))
    if sp.get("hub"):
        radii.append(("r", sp["hub"]))
    if sp.get("crater") and sp.get("crater") != sp.get("R"):
        radii.append(("r", sp["crater"]))
    radii += [("r", r) for r in sp.get("rings", ())]
    if sp.get("bubbles"):
        rb, nb, db = sp["bubbles"]
        do = db if sp.get("bubble_style") == "dot" else db + w      # outer diameter
        radii.append(("b", rb, do - w))
        if 2 * math.pi * rb / nb - do < 4.2 - 1e-6:
            return False
    if sp.get("band"):
        radii.append(("r", sp["band"][0]))
        radii.append(("r", sp["band"][1]))
        r0, r1, nb = sp["band"]
        if 2 * math.pi * r0 / nb - w < 4.2 or r1 - r0 < 1.8 * s:
            return False
    # outward edge / inward edge per element
    prev_out = 0.0
    for item in radii:
        if item[0] == "dot":
            lo, hi = 0.0, item[1]
        elif item[0] == "r":
            lo, hi = item[1] - w / 2, item[1] + w / 2
        else:
            lo, hi = item[1] - (item[2] + w) / 2, item[1] + (item[2] + w) / 2
        if lo - prev_out < MIN_CLEAR - 1e-6 and prev_out > 0:
            return False
        prev_out = hi
    if sp.get("rule") and sp.get("rule") != (sp.get("band") or (0, 0))[1] and not sp.get("wave"):
        if sp["rule"] - w / 2 - prev_out < MIN_CLEAR - 1e-6:
            return False
    if sp.get("crater_ribs") and sp.get("hub"):
        if 2 * math.pi * sp["hub"] / sp["crater_ribs"] < s - 0.05:   # rib ends meet the hub (a junction)
            return False
    return True


def source_rosette(cx: float = T.CX, cy: float = T.CY, R: float = 130.0, *, twist: bool = True,
                   detail: str | None = None, spec: dict | None = None, hatch_cells: bool = True,
                   w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.1 Source Rosette. At R = 130 (the back) the radii are exactly the
    brief's: crater r20 with 8 curved ribs (hub r8 + Ø4.2 dot), ripple rings
    30/39/50, bubble ring r62 (24 × Ø7), pinwheel band 72–104 (24 ribs twisted
    25° clockwise, alternate cells hatched), running-wave ring flowing
    clockwise springing from r104 (crests kept 4.2 clear of the rule), outer
    rule r130. ``twist=False`` gives the D2 version (mirror-symmetric about
    both axes through the centre, verified by area in test_motifs): straight
    ribs with a cell centred on each axis, and the wave ring mirrored
    (flowing from 12/6 o'clock toward 3/9).
    Smaller R picks a reduced recipe (see :func:`rosette_spec`): 'small'
    (R >= 40: centre dot, six Ø7 bubbles, 12-rib band) and 'tiny'
    (R >= 16: centre dot and a ring of bubble dots inside the rim)."""
    sp = spec or rosette_spec(R, w, detail)
    f = Frag(meta={"rosette": sp})
    kw = dict(w=w, color=color, layer=layer)
    if sp.get("crater_ribs"):
        f += crater(cx, cy, sp["crater"], n=sp["crater_ribs"], hub=sp["hub"] or 0.0,
                    twist=30.0 if twist else 0.0, dot_d=sp.get("dot"),
                    rim=sp.get("crater") != sp.get("rule"), **kw)
    elif sp.get("dot"):
        f += dot(cx, cy, sp["dot"], color=color, layer=layer)
    f += concentric_rings(cx, cy, sp.get("rings", ()), **kw)
    if sp.get("bubbles"):
        rb, nb, db = sp["bubbles"]
        f += bubble_ring(cx, cy, rb, nb, db, style=sp.get("bubble_style", "ring"), **kw)
    if sp.get("band"):
        r0, r1, nb = sp["band"]
        # D2 (straight ribs): a CELL is centred on each axis, so a mirror maps
        # cell k to −k (about x) and to n/2 − k (about y) — the same parity, so
        # the alternate hatching is mirror-true (n = 12 / 20 / 24). The C_N
        # band keeps a rib on the axis.
        f += rib_band(cx, cy, r0, r1, n=nb, twist=25.0 if twist else 0.0,
                      hatch_cells="alternate" if hatch_cells else None,
                      start=-90.0 if twist else -90.0 - 180.0 / nb, **kw)
    if sp.get("wave"):
        r0, r1, nb = sp["band"]
        f += running_wave_ring(cx, cy, r1, n=nb, r_limit=sp["rule"] - w / 2 - MIN_CLEAR - w / 2,
                               rule=False, mirrored=not twist, **kw)
    if sp.get("rule") and sp.get("rule") != (sp.get("band") or (0, 0))[1]:
        f += stroke(circle_d(cx, cy, sp["rule"]), w, color=color, layer=layer, role="rule")
    return f


# =============================================================================
# §G.8 ripple rings, §G.9 bubble beading
# =============================================================================
def ripple_rings(cx: float, cy: float, r0: float, gap0: float = 8.0, *, n: int = 3, ratio: float = 1.3,
                 ry_ratio: float = 1.0, arc: tuple[float, float] | None = None, rot: float = 0.0,
                 mode: str = "offset", w: float = FINE, color: str = T.INK,
                 layer: str | None = None) -> Frag:
    """§G.8 a group of ``n`` concentric circles / ellipses / arcs, the gaps
    growing ×``ratio`` outward (first centre-to-centre gap ``gap0``).

    ry_ratio  ellipse ry/rx of the innermost ring
    mode      'offset' — every ring adds the same Δ to rx and ry (even gaps);
              'similar' — rings are scaled copies (ry gaps shrink by ry_ratio)
    arc       (a0, a1) parametric angles to draw arcs instead of full rings."""
    f = Frag()
    rx = r0
    ry = r0 * ry_ratio
    delta = 0.0
    g = gap0
    for k in range(n):
        if k:
            delta += g
            g *= ratio
        if mode == "similar":
            s = (r0 + delta) / r0
            RX, RY = r0 * s, r0 * ry_ratio * s
        else:
            RX, RY = rx + delta, ry + delta
        if arc is None:
            d = ellipse_arc_d(cx, cy, RX, RY, 0, 360, rot) + "Z"
        else:
            d = ellipse_arc_d(cx, cy, RX, RY, arc[0], arc[1], rot)
        f += stroke(d, w, color=color, layer=layer, role="ripple")
    if mode == "similar" and ry_ratio < 1:
        g_min = gap0 * ry_ratio - w
        if g_min < MIN_CLEAR:
            _warn(f, f"ripple_rings: minor-axis clear gap {g_min:.1f} < 4.2")
    return f


def bubble_beading(p0, p1, d0: float = 3.0, *, ratio: float = 1.2, n: int | None = None,
                   d_max: float = 8.0, style: str = "auto", w: float = FINE, color: str = T.INK,
                   layer: str | None = None) -> Frag:
    """§G.9 a row of bubbles growing ×1.2 in the direction of rise p0 → p1
    (Ø3–8 on the back/tuck). With ``n`` the row fills p0..p1 exactly;
    otherwise as many as fit with ~0.6·Ø clear gaps."""
    if n is not None:
        return bubble_row(p0, p1, [min(d_max, s) for s in bubble_sizes(d0, n, ratio)],
                          style=style, w=w, color=color, layer=layer)
    return bubble_path(np.array([p0, p1], float), d0, ratio=ratio, d_max=d_max, style=style,
                       w=w, color=color, layer=layer)


# =============================================================================
# §G.10 fault-step
# =============================================================================
def fault_step(x0: float, x1: float, y: float, *, at: float | None = None, rise: float | None = None,
               double: float | None = None, w: float = FINE, color: str = T.INK,
               layer: str | None = None) -> Frag:
    """§G.10 a horizontal line x0→x1 broken by ONE right-angle step at x =
    ``at`` (default the middle): the part after the step is ``rise`` px
    higher (negative rise = lower). Default rise 4.5 × w (4–5× the stroke).
    ``double`` adds a parallel copy that many px below. Miter joins, butt caps."""
    at = (x0 + x1) / 2 if at is None else at
    rise = 4.5 * w if rise is None else rise
    pts = [(x0, y), (at, y), (at, y - rise), (x1, y - rise)]
    f = stroke(polyline_d(pts), w, style="rule", color=color, layer=layer, role="fault")
    if double:
        f += f.translate(0, double)
        if double - w < MIN_CLEAR - 1e-6:
            _warn(f, f"fault_step: double spacing clear {double - w:.1f} < 4.2")
    return f


def fault_plinth(cx: float, y: float, width: float = 60.0, *, steps: int = 2, riser: float | None = None,
                 tread: float | None = None, up: int = -1, base: bool = True, hatch_step: int | None = 0,
                 hatch_angle: float = DIAG, w: float = FINE, color: str = T.INK,
                 layer: str | None = None) -> Frag:
    """A stepped plinth (the Balcones step) standing on the line y, centred at
    cx: ``steps`` treads, each ``riser`` tall (default 4.5·w, §G.10) and set in
    by ``tread`` per side (default width/(2·steps+2)). ``up`` −1 rises toward
    −y. Bedding lines separate the steps, and ``base`` (default) closes the
    foot, so any hatch ends on a line. ``hatch_step`` = index of the step
    slab (0 = lowest) to hatch at 45° (None = none) — with the plain steps
    above it that is the plinth's half-hatch. The top tread is
    ``meta['top']`` = (y, x0, x1)."""
    riser = 4.5 * w if riser is None else riser
    tread = width / (2 * steps + 2) if tread is None else tread
    pts_l = []
    x = cx - width / 2
    yy = y
    for k in range(steps):
        pts_l.append((x, yy))
        yy += up * riser
        pts_l.append((x, yy))
        x += tread
    top_y = yy
    right = [(2 * cx - px, py) for px, py in reversed(pts_l)]
    pts = pts_l + right
    f = stroke(polyline_d(pts, closed=base), w, style="rule", color=color, layer=layer, role="plinth")
    # bedding lines: the top of every lower step runs full width under the step
    # above, so each step is a slab and hatch always ends on a line (§B.2)
    for k in range(1, steps):
        xl = cx - width / 2 + (k - 1) * tread
        yb = y + up * riser * k
        f += stroke(polyline_d([(xl + tread, yb), (2 * cx - xl - tread, yb)]), w, style="rule",
                    color=color, layer=layer, role="bedding")
    if hatch_step is not None:
        k = hatch_step
        xl = cx - width / 2 + k * tread
        y_lo = y + up * riser * k
        y_hi = y_lo + up * riser
        cell = box(xl, min(y_lo, y_hi), 2 * cx - xl, max(y_lo, y_hi))
        f += hatch(cell, hatch_angle, color=color, layer=layer)
    f.meta["top"] = (top_y, cx - width / 2 + steps * tread, cx + width / 2 - steps * tread)
    return f


# =============================================================================
# §G.11 strata bands (+ fault jog)
# =============================================================================
def strata(reg, *, y0: float | None = None, heights=(12.0, 19.0), hatched: str = "thin",
           angle: float = DIAG, fault=None, jog: float | None = None, origin=None,
           w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.11 horizontal courses alternating ``heights`` (12/19 px), every other
    course hatched at 45° (FINE, 7.0 pitch), clipped to the region ``reg``.

    hatched 'thin' | 'thick' — which courses carry hatch
    fault   ((x0, y0), (x1, y1)): a single diagonal fault line; the courses on
            its right-hand side (screen, looking p0→p1) drop by ``jog`` px
            (default: one course height, heights[0]); the fault is drawn.
    The region's own contour is NOT drawn (the caller owns it); course lines
    and hatch end on it (butt)."""
    g = region(reg)
    x0b, y0b, x1b, y1b = g.bounds
    y0 = y0b if y0 is None else y0
    jog = heights[0] if jog is None else jog
    f = Frag()

    def build(sub, shift):
        out = Frag()
        # boundaries from well above to well below
        ys, kinds = [], []
        per = sum(heights)
        n0 = int(math.floor((y0b - (y0 + shift)) / per)) - 1
        yy = y0 + shift + n0 * per
        k = 0
        while yy <= y1b + per:
            ys.append(yy)
            kinds.append(k % len(heights))
            yy += heights[k % len(heights)]
            k += 1
        lines = [LineString([(x0b - 5, yv), (x1b + 5, yv)]) for yv in ys]
        cl = shapely.intersection(shapely.MultiLineString(lines), sub)
        segs = [np.asarray(l.coords) for l in _lines(cl) if l.length > 1.0]
        if segs:
            out += stroke(segs, w, style="rule", color=color, layer=layer, role="course")
        thin_idx = int(np.argmin(heights))
        for yv, kd, yn in zip(ys[:-1], kinds[:-1], ys[1:]):
            is_thin = kd == thin_idx
            if (hatched == "thin") != is_thin:
                continue
            cell = sub.intersection(box(x0b - 5, yv, x1b + 5, yn))
            if cell.is_empty:
                continue
            o = (origin[0], origin[1] + shift) if origin is not None else (x0b, y0 + shift)
            out += hatch(cell, angle, origin=o, color=color, layer=layer)
        return out

    if fault is None:
        f += build(g, 0.0)
    else:
        p0, p1 = np.asarray(fault[0], float), np.asarray(fault[1], float)
        left = split_region(g, (tuple(p0), tuple(p1)), side=+1)
        right = split_region(g, (tuple(p0), tuple(p1)), side=-1)
        f += build(left, 0.0)
        f += build(right, jog)
        # fault line, clipped to the region
        u = (p1 - p0) / np.hypot(*(p1 - p0))
        big = 4 * (x1b - x0b + y1b - y0b)
        ln = LineString([p0 - u * big, p1 + u * big]).intersection(g)
        segs = [np.asarray(l.coords) for l in _lines(ln) if l.length > 1.0]
        if segs:
            f += stroke(segs, w, style="rule", color=color, layer=layer, role="fault")
    return f


def _lines(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    out = []
    for p in getattr(g, "geoms", []):
        out += _lines(p)
    return out


# =============================================================================
# §G.12 karst voids
# =============================================================================
KARST_ASPECT = 1.3        # voids are horizontal ellipses: width = 1.3 × Ø (Ø = height)


def karst_void(x: float, y: float, d: float, *, inner: bool | None = None, aspect: float = KARST_ASPECT,
               w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """One void: an outlined horizontal ellipse, height ``d`` (centreline),
    width aspect·d. ``inner`` (default: d >= 16) adds the FINE inner offset —
    drawn as the void's own contour shifted down by w + 4.2 and kept inside,
    i.e. a crescent 'ceiling' line 4.2 px clear at its crown that meets the
    rim at both ends (a concentric offset would collapse at Ø16)."""
    rx, ry = aspect * d / 2, d / 2
    f = stroke(G.ellipse_d(x, y, rx, ry), w, color=color, layer=layer, role="void")
    if inner is None:
        inner = d >= 16 - 1e-9
    if inner:
        sh = w + MIN_CLEAR
        body = Polygon(G.arc_pts(x, y, rx, 0, 360, n=720, ry=ry))
        pts = [np.asarray(l.coords) for l in _lines(LineString(G.arc_pts(x, y + sh, rx, 180, 360, n=720, ry=ry)).intersection(body))]
        if pts:
            f += stroke(pts, w, color=color, layer=layer, role="void")
    return f


def karst_voids(reg, *, pitch: tuple[float, float] = (28.0, 21.0), sizes=(6.0, 10.0, 16.0),
                weights=(0.45, 0.35, 0.20), seed: int = 1983, margin: float | None = None, origin=None,
                aspect: float = KARST_ASPECT, w: float = FINE, color: str = T.INK,
                layer: str | None = None) -> Frag:
    """§G.12 a staggered (half-drop) grid of outlined ellipses in three sizes,
    clipped to ``reg``. Each grid site draws a size from ``weights`` with a
    deterministic hash (``seed``), then steps down to a smaller size — or is
    left empty — until it keeps >= 4.2 px clear of every void already placed
    and ``margin`` (default 4.2 + w) of the region edge."""
    g = region(reg)
    margin = MIN_CLEAR + w if margin is None else margin
    inner = g.buffer(-margin)
    x0, y0, x1, y1 = g.bounds
    ox, oy = (x0, y0) if origin is None else origin
    px, py = pitch
    cum = np.cumsum(weights) / np.sum(weights)
    placed = []            # shapely outer outlines (stroke outer edge)
    f = Frag()
    j0 = int(math.floor((y0 - oy) / py)) - 1
    j1 = int(math.ceil((y1 - oy) / py)) + 1
    for j in range(j0, j1 + 1):
        off = (px / 2) if j % 2 else 0.0
        i0 = int(math.floor((x0 - ox - off) / px)) - 1
        i1 = int(math.ceil((x1 - ox - off) / px)) + 1
        for i in range(i0, i1 + 1):
            cx, cy = ox + off + i * px, oy + j * py
            hsh = ((i * 73856093) ^ (j * 19349663) ^ (seed * 83492791)) & 0xFFFFFF
            k = int(np.searchsorted(cum, (hsh % 10007) / 10007.0, side="right"))
            k = min(k, len(sizes) - 1)
            for kk in range(k, -1, -1):
                d = sizes[kk]
                rx, ry = aspect * d / 2 + w / 2, d / 2 + w / 2
                ell = shapely.affinity.scale(Point(cx, cy).buffer(1.0, quad_segs=32), rx, ry)
                if not inner.contains(ell):
                    continue
                if any(ell.distance(q) < MIN_CLEAR for q in placed if abs(q.centroid.x - cx) < 40 and abs(q.centroid.y - cy) < 40):
                    continue
                placed.append(ell)
                f += karst_void(cx, cy, d, aspect=aspect, w=w, color=color, layer=layer)
                break
    return f


# =============================================================================
# §G.13 stalactite point, §G.14 drip fringe
# =============================================================================
def stalactite(x: float, y: float, length: float = 64.0, width: float = 20.0, *, head: float = 0.2,
               rings: int = 3, hatch_side: str | None = "left", rot: float = 0.0, w: float = FINE,
               color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.13 a tall isosceles kite hanging from its top vertex (x, y) to the
    tip at y + length, widest (``width``) at ``head``·length, split on its
    axis. One half (``hatch_side``) is hatched perpendicular to the axis;
    the other half carries the ``rings`` growth-ring arcs (bowed toward the
    tip), so hatch and rings never cross. Miter joins, limit 10.

    Small points degrade gracefully (the Q♠ diadem hangs nine graduated
    ones), always preferring the half-hatch, which is what defines the
    motif, over the rings:

    * rings stop where the half-width falls below w + 4.2 and are THINNED to
      fit their span (>= w + 4.2 between neighbours) — 2, 1 or none;
    * the hatch runs down as far as the axis (hatch is tone: it needs no
      4.2 px clearance from the axis); the axis stops where the half-width
      falls below w + 3 (the knockout gap), so the tip is a clean point;
    * below a half-width of w + 3 (the knockout gap beside the axis) the
      axis, hatch and rings go and the point is a plain kite outline.

    Every reduction is recorded in ``meta['warnings']``; ``meta['detail']``
    is 'full' | 'reduced' | 'outline'."""
    top = np.array([x, y])
    yw = y + head * length
    Lp, Rp, B = np.array([x - width / 2, yw]), np.array([x + width / 2, yw]), np.array([x, y + length])
    f = stroke(polyline_d([top, Rp, B, Lp], closed=True), w, style="point", color=color, layer=layer, role="kite")
    hw = width / 2
    detail = "full"
    if hw < w + 3.0:
        # too slim to split: a clean kite (the axis would fuse with the edges)
        _warn(f, f"stalactite: half-width {hw:.1f} < {w + 3.0:.1f} — plain kite (no axis, rings or hatch)")
        f.meta["detail"] = "outline"
        return f.rotate(rot, x, y) if rot else f
    kite_poly = Polygon([top, Rp, B, Lp])
    ring_side = 1 if hatch_side != "right" else -1       # +1: rings on the right half

    def y_at(h):                                         # height below the widest point where the half-width is h
        return B[1] - (B[1] - yw) * min(h, hw) / hw
    # the axis stops where the point is too slim to keep the knockout gap beside it,
    # so the tip stays one clean converging point (no three-line wedge; cf. leaf midribs)
    f += stroke(polyline_d([top, (x, y_at(w + 3.0))]), w, style="point", color=color, layer=layer, role="axis")

    if rings:
        hw_min = w + MIN_CLEAR                           # rings stop where the half narrows below this
        span = y_at(hw_min) - yw if hw >= hw_min else 0.0
        fit = int(span // (w + MIN_CLEAR)) if span > 0 else 0
        n_r = min(rings, fit)
        if n_r < rings:
            detail = "reduced"
            _warn(f, f"stalactite: {n_r} of {rings} growth rings fit a {length:g} × {width:g} point")
        half_poly = kite_poly.intersection(box(x, y - 1, x + width, y + length + 1) if ring_side > 0
                                           else box(x - width, y - 1, x, y + length + 1))
        for k in range(1, n_r + 1):
            yy = yw + span * (k - 0.35) / n_r
            half = hw * (B[1] - yy) / (B[1] - yw)
            bow = 0.5 * half
            R = (half * half + bow * bow) / (2 * bow)
            c = (x, yy + bow - R)
            pts = G.arc_pts(c[0], c[1], R, 0, 180, n=180)
            ln = LineString(pts).intersection(half_poly)
            segs = [np.asarray(l.coords) for l in _lines(ln) if l.length > 1]
            if segs:
                f += stroke(segs, w, color=color, layer=layer, role="ring")
    if hatch_side:
        # hatch is tone: it runs down as far as the drawn axis (its lines butt on it)
        upper = kite_poly.intersection(box(x - width, y - 1, x + width, y_at(w + 3.0)))
        h = half_hatch(upper, [tuple(top), tuple(B)], "perp", side=-ring_side, color=color, layer=layer)
        if not h:
            detail = "reduced"
            _warn(f, f"stalactite: no hatch line fits a {length:g} × {width:g} point")
        f += h
    f.meta["detail"] = detail
    return f.rotate(rot, x, y) if rot else f


def drip_fringe(x0: float, x1: float, y: float, *, pitch: float = 12.0, l_min: float = 8.0,
                l_max: float = 26.0, periods: float = 1.0, phase: float = 0.0, down: int = 1,
                rule: bool = True, w: float = FINE, color: str = T.INK,
                layer: str | None = None) -> Frag:
    """§G.14 vertical strokes hanging from the line y (x0..x1) whose lengths
    follow a slow sine envelope (``periods`` full cycles across the run,
    between l_min and l_max), each ending in a Ø6.3 terminal. ``pitch`` >=
    10.5 keeps the terminals 4.2 clear. Symmetric about the run's centre when
    phase = 0 and periods is whole."""
    n = int((x1 - x0) // pitch) + 1
    xs = (x0 + x1) / 2 + (np.arange(n) - (n - 1) / 2) * pitch
    f = Frag()
    if rule:
        f += stroke(polyline_d([(x0, y), (x1, y)]), w, style="rule", color=color, layer=layer, role="rule")
    for xv in xs:
        t = (xv - x0) / max(x1 - x0, 1e-9)
        env = 0.5 - 0.5 * math.cos(2 * math.pi * (periods * t) + math.radians(phase))
        L = l_min + (l_max - l_min) * env
        f += stroke(polyline_d([(xv, y), (xv, y + down * L)]), w, color=color, layer=layer, role="drip",
                    terminals="end")
    if pitch - TD < MIN_CLEAR:
        _warn(f, f"drip_fringe: terminals only {pitch - TD:.1f} px apart")
    return f


# =============================================================================
# §G.16 scale lattice
# =============================================================================
def scale_lattice(reg, r: float = 10.0, *, step: float = 0.6, origin=None, w: float = FINE,
                  color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.16 rows of semicircular arcs (the lower half of circles of radius r,
    centres 2r apart), each row offset half a pitch and stepped down by
    ``step``·r; each row overlaps the row below it like shingles (the lower
    row's arcs are hidden inside the upper row's discs), clipped to ``reg``.
    Needs r >= 5.25 so arcs two rows apart keep 4.2 clear."""
    g = region(reg)
    x0, y0, x1, y1 = g.bounds
    ox, oy = (x0, y0) if origin is None else origin
    dy = step * r
    lines = []
    prev_discs = None
    j0 = int(math.floor((y0 - oy) / dy)) - 2
    j1 = int(math.ceil((y1 - oy) / dy)) + 2
    for j in range(j0, j1 + 1):
        cy = oy + j * dy
        off = r if j % 2 else 0.0
        i0 = int(math.floor((x0 - ox - off) / (2 * r))) - 1
        i1 = int(math.ceil((x1 - ox - off) / (2 * r))) + 1
        arcs, discs = [], []
        for i in range(i0, i1 + 1):
            cx = ox + off + 2 * i * r
            arcs.append(LineString(G.arc_pts(cx, cy, r, 0, 180, n=120)))
            discs.append(Point(cx, cy).buffer(r, quad_segs=64))
        ml = shapely.MultiLineString(arcs)
        if prev_discs is not None:
            ml = ml.difference(prev_discs)
        lines.append(ml)
        # everything above this row's arc line is covered for the next row
        prev_discs = shapely.union_all(discs + [box(x0 - 4 * r, y0 - 10 * r, x1 + 4 * r, cy)])
    res = shapely.intersection(shapely.union_all(lines), g)
    segs = [np.asarray(l.coords) for l in _lines(shapely.line_merge(res) if not res.is_empty else res)
            if l.length > 1.0]
    f = stroke(segs, w, color=color, layer=layer, role="scale") if segs else Frag()
    if 2 * dy - w < MIN_CLEAR:
        _warn(f, f"scale_lattice: r={r} too small for 4.2 clear")
    return f


# =============================================================================
# §G.17 cypress-knee crenellation
# =============================================================================
def _knee_geom(x, y, h, bw, f_r, side_r):
    """Left side circle through (x−bw/2, y) and apex (x, y−h), convex outward,
    radius side_r; fillet circle radius f_r on the axis tangent to both."""
    A = np.array([x - bw / 2, y])
    P = np.array([x, y - h])
    m = (A + P) / 2
    ch = P - A
    L = np.hypot(*ch)
    R = max(side_r, L / 2 + 1e-6)
    nrm = np.array([ch[1], -ch[0]]) / L
    # the knob's inside is toward +x of its left side: the centre lies that way (convex side)
    if nrm[0] < 0:
        nrm = -nrm
    c = m + nrm * math.sqrt(R * R - (L / 2) ** 2)
    # fillet centre on the axis x: |F − c| = R − f
    dx = x - c[0]
    yf = c[1] - math.sqrt(max((R - f_r) ** 2 - dx * dx, 0.0))
    F = np.array([x, yf])
    tl = c + (F - c) / np.hypot(*(F - c)) * R
    return A, c, R, F, tl


def cypress_knee(x: float, y: float, h: float = 40.0, base_w: float = 34.0, *, fillet: float | None = None,
                 side_r: float | None = None, base: bool = False, hatch_side: str | None = None,
                 hatch_angle: float = 0.0, w: float = FINE, color: str = T.INK,
                 layer: str | None = None) -> Frag:
    """§G.17 one knob standing on (x, y): two side arcs (convex, radius
    ``side_r``, default 1.5·h — a full cone) meeting in a top fillet (default 0.26·base_w). ``hatch_side``
    'left'|'right' half-hatches that side of the axis (FINE, 7.0 pitch):
    ``hatch_angle`` 0 = across the axis (shaded cone, default), 90 = flutes."""
    side_r = 1.5 * h if side_r is None else side_r
    fillet = 0.26 * base_w if fillet is None else fillet
    A, c, R, F, tl = _knee_geom(x, y, h, base_w, fillet, side_r)
    Ar = np.array([2 * x - A[0], A[1]])
    cr = np.array([2 * x - c[0], c[1]])
    tr = np.array([2 * x - tl[0], tl[1]])
    d = (f"M{A[0]:.3f} {A[1]:.3f}" + arc_between(c, R, A, tl, cw=True)
         + arc_between(F, fillet, tl, tr, cw=True) + arc_between(cr, R, tr, Ar, cw=True))
    if base:
        d += "Z"
    f = stroke(d, w, color=color, layer=layer, role="knee")
    if hatch_side:
        pts = sample_d(d + ("" if base else "Z"), 0.25)[0][0]
        pg = Polygon(pts)
        f += half_hatch(pg, [(x, y - h - 1), (x, y + 1)], hatch_angle,
                        side=-1 if hatch_side == "left" else 1, color=color, layer=layer)
        f += stroke(polyline_d([(x, F[1] - fillet), (x, y)]), w, color=color, layer=layer)
    f.meta["knee_top"] = F[1] - fillet
    return f


def knee_crenellation(x0: float, x1: float, y: float, *, h: float = 40.0, heights=(0.65, 0.8, 1.0, 0.8, 0.65),
                      base_w: float = 34.0, gap: float | None = None, hatch_side: str | None = "right",
                      rule: bool = True, w: float = FINE, color: str = T.INK,
                      layer: str | None = None) -> Frag:
    """§G.17 a row of cypress knees on the line y between x0 and x1, heights
    ``heights`` × h (1.0 / 0.8 / 0.65), evenly spaced. With ``rule`` the base
    line runs between the knees (the knees spring from it)."""
    n = len(heights)
    free = (x1 - x0) - n * base_w
    gap = free / (n + 1) if gap is None else gap
    f = Frag()
    xs = []
    xx = x0 + (x1 - x0 - (n * base_w + (n - 1) * gap)) / 2
    for k, hk in enumerate(heights):
        cx = xx + base_w / 2
        xs.append(cx)
        f += cypress_knee(cx, y, hk * h, base_w, hatch_side=hatch_side, w=w, color=color, layer=layer)
        xx += base_w + gap
    if rule:
        segs = [(x0, xs[0] - base_w / 2)] + [(xs[k] + base_w / 2, xs[k + 1] - base_w / 2) for k in range(n - 1)] \
            + [(xs[-1] + base_w / 2, x1)]
        d = "".join(polyline_d([(a, y), (b, y)]) for a, b in segs if b - a > 0.1)
        f += stroke(d, w, style="rule", color=color, layer=layer, role="rule")
    return f


# =============================================================================
# §G.18 comb spray (+ cone), §G.19 reed ladder
# =============================================================================
def cypress_cone(x: float, y: float, r: float = 11.0, *, rot: float = 0.0, w: float = FINE,
                 color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.18 a round cypress cone: a circle with 4 scale arcs. The arcs join
    four rim points (every 90°) and bow inward, leaving a curved-square
    centre scale and four rim scales — cracked-plate texture with no X
    crossings."""
    f = stroke(circle_d(x, y, r), w, color=color, layer=layer, role="cone")
    for k in range(4):
        a0 = rot + 45 + 90 * k
        p0, p1 = polar(x, y, r, a0), polar(x, y, r, a0 + 90)
        # arc bowing toward the centre: sagitta so the midpoint sits at 0.42 r
        mid = polar(x, y, 0.42 * r, a0 + 45)
        c_ch = (p0 + p1) / 2
        half = np.hypot(*(p1 - p0)) / 2
        s = np.hypot(*(c_ch - np.array([x, y]))) - 0.42 * r
        R = (half * half + s * s) / (2 * s)
        u = (c_ch - np.array([x, y])) / np.hypot(*(c_ch - np.array([x, y])))
        cc = mid + u * R
        d = f"M{p0[0]:.3f} {p0[1]:.3f}" + arc_between(cc, R, p0, p1, cw=False)
        f += stroke(d, w, color=color, layer=layer, role="cone")
    return f


def comb_spray(path, *, pitch: float = 7.5, tick: float = 9.0, angle: float = 55.0, both: bool = True,
               start: float = 6.0, end_gap: float | None = None, cone: float | None = None, min_tick: float = 3.0,
               w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.18 cypress comb spray: a rachis (``path``: d-string or points, drawn
    from base to tip) with evenly spaced short parallel ticks on both sides,
    swept ``angle`` degrees forward from the rachis. Tick lengths follow a
    vesica envelope peaking at ``tick`` (the tick tips trace two circular
    arcs). ``cone`` = radius of a round cone carried at the tip (the rachis
    stops at its rim). Perpendicular tick spacing = pitch·sin(angle) must be
    >= 6.3 (default 7.5·sin55° = 6.1 → pitch auto-raised); on a curved
    rachis the pitch is raised further by R / (R − reach) at the tightest
    bend so the ticks on the concave side keep 4.2 px clear too
    (``meta['pitch']``)."""
    pts = sample_d(path, 0.25)[0][0] if isinstance(path, str) else np.asarray(path, float)
    cv = G.Curve(pts)
    sa = math.sin(math.radians(angle))
    pitch_in = pitch
    pitch = max(pitch, (w + MIN_CLEAR) / sa)
    # a curved rachis crowds the ticks on its CONCAVE side (their tips converge):
    # raise the pitch by R / (R − reach) at the tightest bend, so they keep 4.2 clear
    ss_ = np.linspace(0, cv.length, max(8, int(cv.length / 2.0)))
    T_ = np.array([cv.tangent_s(v) for v in ss_])
    ang_ = np.unwrap(np.arctan2(T_[:, 1], T_[:, 0]))
    kap = np.gradient(ang_, ss_)[1:-1]              # signed: > 0 turns clockwise on screen (concave side = right)
    if not both:
        kap = kap[kap < 0]                          # ticks only on the screen-left: concave where turning left
    kmax = float(np.max(np.abs(kap))) if len(kap) else 0.0
    reach_ = tick * sa
    warn_curve = None
    if kmax > 1e-4:
        Rm = 1.0 / kmax
        if Rm > reach_ + 1.0:
            need = (w + MIN_CLEAR) / sa * Rm / (Rm - reach_)
            if need > pitch + 1e-6:
                pitch = need
        else:
            warn_curve = f"comb_spray: rachis radius {Rm:.1f} < tick reach {reach_:.1f} — concave ticks converge"
    Lr = cv.length - (2 * cone if cone else 0.0)
    f = Frag()
    rach = cv.sub(0, Lr / cv.length) if cone else cv
    f += stroke(polyline_d(rach.pts), w, color=color, layer=layer, role="rachis")
    # vesica envelope of the tick TIPS (perpendicular reach), chord = [start, Lr - end_gap]
    end_gap = (1.2 * cone if cone else 0.0) if end_gap is None else end_gap
    s0, s1 = start, Lr - end_gap
    chord = s1 - s0
    reach = tick * sa
    Rv = ((chord / 2) ** 2 + reach ** 2) / (2 * reach)
    n = int(chord // pitch)
    ss = s0 + (chord - n * pitch) / 2 + np.arange(n + 1) * pitch
    for s in ss:
        xm = s - (s0 + s1) / 2
        hw = math.sqrt(max(Rv * Rv - xm * xm, 0.0)) - (Rv - reach)
        L = hw / sa
        if L < min_tick:
            continue
        p = cv.at_s(s)
        tdir = cv.tangent_s(s)
        a = math.atan2(tdir[1], tdir[0])
        for side in ((1, -1) if both else (1,)):
            ang = a - side * math.radians(angle)     # side +1: tick to the screen-left
            q = p + L * np.array([math.cos(ang), math.sin(ang)])
            f += stroke(polyline_d([p, q]), w, color=color, layer=layer, role="tick")
    if cone:
        tip = cv.at_s(Lr)
        tdir = cv.tangent_s(Lr)
        c = tip + tdir * cone
        f += cypress_cone(*c, cone, rot=math.degrees(math.atan2(tdir[1], tdir[0])), w=w, color=color, layer=layer)
    f.meta["pitch"] = pitch
    if pitch > max(pitch_in, (w + MIN_CLEAR) / sa) + 1e-6:
        f.meta["pitch_raised"] = True
    if warn_curve:
        _warn(f, warn_curve)
    return f


def reed_ladder(p0, p1, *, width: float = 16.0, rung: float = 26.0, node_every: int = 4,
                node_ry: float = 4.5, rails: bool = True, phase: float | None = None,
                w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.19 two rails ``width`` apart along p0→p1, rungs every ``rung`` px,
    and on every ``node_every``-th rung a node ellipse (major axis across the
    ladder, tangent to both rails, minor semi-axis ``node_ry``) in place of
    the rung. Rungs are centred on the run unless ``phase`` (px from p0)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    u = (p1 - p0) / L
    v = np.array([-u[1], u[0]])
    hw = width / 2
    f = Frag()
    if rails:
        f += stroke(polyline_d([p0 + v * hw, p1 + v * hw]) + polyline_d([p0 - v * hw, p1 - v * hw]), w,
                    style="rule", color=color, layer=layer, role="rail")
    n = int(L // rung)
    s0 = (L - n * rung) / 2 if phase is None else phase
    mid = n // 2
    ang = math.degrees(math.atan2(v[1], v[0]))
    for k in range(n + 1):
        s = s0 + k * rung
        if s < -1e-9 or s > L + 1e-9:
            continue
        c = p0 + u * s
        if node_every and (k - mid) % node_every == 0:
            f += stroke(G.ellipse_d(c[0], c[1], hw, node_ry, ang), w, color=color, layer=layer, role="node")
        else:
            f += stroke(polyline_d([c - v * hw, c + v * hw]), w, style="rule", color=color, layer=layer,
                        role="rung")
    return f


def reed_node(x: float, y: float, *, rx: float = 6.3, ry: float = 3.4, stalk: float = 7.0,
              tick: float = 8.0, tick_angle: float = 55.0, tick_at: float = 0.3, rot: float = 0.0,
              w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """The reed-node mark (♣ house mark, §F.1; ≈ 26 px wide at defaults): a
    node ellipse on a stalk (``stalk`` px beyond each end) with two opposed
    leaf ticks springing from the stalk — up-right on the right, down-left on
    the left, as in the ♣ divider — so the mark is C2-symmetric and the ticks
    never line up into one stroke through the node. ``tick`` 0 omits them;
    ``rot`` turns the mark (90 = vertical stalk)."""
    f = stroke(G.ellipse_d(x, y, rx, ry), w, color=color, layer=layer, role="node")
    if stalk > 0:
        f += stroke(polyline_d([(x + rx, y), (x + rx + stalk, y)]) + polyline_d([(x - rx, y), (x - rx - stalk, y)]),
                    w, color=color, layer=layer, role="stalk")
    if tick > 0 and stalk > 0:
        a = math.radians(-tick_angle)
        p = np.array([x + rx + tick_at * stalk, y])
        q = p + tick * np.array([math.cos(a), math.sin(a)])
        c = np.array([x, y])
        f += stroke(polyline_d([p, q]), w, color=color, layer=layer, role="tick")
        f += stroke(polyline_d([2 * c - p, 2 * c - q]), w, color=color, layer=layer, role="tick")
    return f.rotate(rot, x, y) if rot else f


def reed_node_medallion(x: float, y: float, d: float = 26.0, *, rot: float = 0.0, w: float = FINE,
                        color: str = T.INK, layer: str | None = None) -> Frag:
    """A medallion ring of diameter ``d`` holding a reed node on a stalk that
    runs ring to ring (``rot`` 90 = vertical stalk, e.g. in a side band).
    Leaf ticks are added only when the ring is big enough (d >= 36) for
    them to keep 4.2 px clear (the back's side-band medallion, §H.19)."""
    r = d / 2
    f = stroke(circle_d(x, y, r), w, color=color, layer=layer, role="medallion")
    big = d >= 36
    rx = max(4.2, (0.36 if big else 0.42) * r)
    ry = max(w / 2 + 2.3, 0.26 * r)
    # ticks need room between the stalk and the ring: only on larger medallions,
    # and only as long as keeps their round cap 4.2 clear of the ring
    tick = 0.0
    if d >= 36:
        ds = rx + 0.1 * (r - rx)
        ua = np.array([math.cos(math.radians(-55)), math.sin(math.radians(-55))])
        lim = r - w - MIN_CLEAR                  # tick centreline end radius
        bq = 2 * ds * ua[0]
        tick = max(0.0, (-bq + math.sqrt(bq * bq - 4 * (ds * ds - lim * lim))) / 2)
    node = reed_node(x, y, rx=rx, ry=ry, tick=tick, tick_at=0.1, stalk=r - rx, w=w, color=color, layer=layer)
    f += node.rotate(rot, x, y) if rot else node
    return f


# =============================================================================
# §G.20 ashlar, §G.21 arcade
# =============================================================================
def ashlar(reg, *, block: tuple[float, float] = (42.0, 18.0), joint: float = 7.0, chamfer: float = 3.0,
           origin=None, min_frac: float = 0.3, w: float = FINE, color: str = T.INK,
           layer: str | None = None) -> Frag:
    """§G.20 running-bond courses of rectangles with 3 px chamfered corners
    (rusticated limestone), clipped to ``reg``. ``joint`` = centreline gap
    between neighbouring stones (>= w + 4.2). Stones cut by the region edge
    are kept if at least ``min_frac`` of the stone is inside; their outline
    then ends on the region edge (butt), where the caller's contour covers it."""
    g = region(reg)
    x0, y0, x1, y1 = g.bounds
    ox, oy = (x0, y0) if origin is None else origin
    bw, bh = block
    px, py = bw + joint, bh + joint
    f = Frag()
    c = chamfer
    j0 = int(math.floor((y0 - oy) / py)) - 1
    j1 = int(math.ceil((y1 - oy) / py)) + 1
    for j in range(j0, j1 + 1):
        off = px / 2 if j % 2 else 0.0
        i0 = int(math.floor((x0 - ox - off) / px)) - 1
        i1 = int(math.ceil((x1 - ox - off) / px)) + 1
        for i in range(i0, i1 + 1):
            bx, by = ox + off + i * px + joint / 2, oy + j * py + joint / 2
            pts = [(bx + c, by), (bx + bw - c, by), (bx + bw, by + c), (bx + bw, by + bh - c),
                   (bx + bw - c, by + bh), (bx + c, by + bh), (bx, by + bh - c), (bx, by + c)]
            pg = Polygon(pts)
            inter = pg.intersection(g)
            if inter.is_empty or inter.area < min_frac * pg.area:
                continue
            if g.contains(pg):
                f += stroke(polyline_d(pts, closed=True), w, style="rule", color=color, layer=layer, role="stone")
            else:
                ln = LineString(pts + [pts[0]]).intersection(g)
                segs = [np.asarray(l.coords) for l in _lines(shapely.line_merge(ln) if ln.geom_type != "LineString" else ln)
                        if l.length > 1.0]
                if segs:
                    f += stroke(segs, w, style="rule", color=color, layer=layer, role="stone")
    if joint - w < MIN_CLEAR:
        _warn(f, f"ashlar: joint clear {joint - w:.1f} < 4.2")
    return f


def arch(x: float, y: float, span: float = 30.0, jamb: float = 12.0, *, key: tuple[float, float] = (7.0, 22.0),
         ring: float | None = 6.3, w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.21 one round arch standing on the line y, centred at x: two jambs
    ``jamb`` px tall, a semicircle of diameter ``span``, and a keystone wedge
    at the crown (``key`` = (height above the arch, full angle in degrees);
    radial sides, flat top). ``ring`` adds an extrados ring that far outside
    (the keystone spans it). Miter joins, butt caps."""
    r = span / 2
    ys = y - jamb
    kh, kang = key
    half = kang / 2
    r_top = r + (ring or 0.0) + kh
    # arch line broken under the keystone
    a_l, a_r = -90 - half, -90 + half
    d = polyline_d([(x - r, y), (x - r, ys)]) + arc_d(x, ys, r, 180, 360 + a_l, move=False)
    f = stroke(d, w, style="rule", color=color, layer=layer, role="arch")
    f += stroke(arc_d(x, ys, r, a_r, 0, move=True) + f"L{x + r:.3f} {y:.3f}", w, style="rule",
                color=color, layer=layer, role="arch")
    if ring:
        rr = r + ring
        f += stroke(polyline_d([(x - rr, y), (x - rr, ys)]) + arc_d(x, ys, rr, 180, 360 + a_l, move=False), w,
                    style="rule", color=color, layer=layer, role="arch")
        f += stroke(arc_d(x, ys, rr, a_r, 0) + f"L{x + rr:.3f} {y:.3f}", w, style="rule", color=color,
                    layer=layer, role="arch")
    # keystone: radial sides from its foot to r_top, flat top. With a ring the
    # foot is the intrados; on a single-line arch the wedge straddles the line
    # (foot 0.6·kh inside it) so it reads as set INTO the arch, not capping it.
    r_foot = r if ring else r - 0.6 * kh
    pl0, pr0 = polar(x, ys, r_foot, a_l), polar(x, ys, r_foot, a_r)
    pl1, pr1 = polar(x, ys, r_top, a_l), polar(x, ys, r_top, a_r)
    top_y = min(pl1[1], pr1[1])
    pl1 = np.array([pl1[0], top_y]); pr1 = np.array([pr1[0], top_y])
    kd = polyline_d([pl0, pl1, pr1, pr0]) + arc_d(x, ys, r_foot, a_r, a_l, move=False) + "Z"
    f += stroke(kd, w, style="rule", color=color, layer=layer, role="keystone")
    return f


def arcade(x0: float, x1: float, y: float, *, span: float = 30.0, pier: float | None = None,
           jamb: float = 12.0, base: bool = True, **kw) -> Frag:
    """§G.21 a row of arches on the line y between x0 and x1 (as many as fit,
    centred), separated by piers of width ``pier`` (default and minimum: the
    extrados rings of neighbours keep 4.2 px clear). ``base`` draws the sill."""
    ring = kw.get("ring", 6.3) or 0.0
    w = kw.get("w", FINE)
    pmin = 2 * ring + w + MIN_CLEAR
    pier = max(pmin, 12.0) if pier is None else max(pier, pmin)
    pitch = span + pier
    n = int((x1 - x0 + pier) // pitch)
    used = n * pitch - pier
    s = x0 + (x1 - x0 - used) / 2 + span / 2
    f = Frag()
    for k in range(n):
        f += arch(s + k * pitch, y, span, jamb, **kw)
    if base:
        f += stroke(polyline_d([(x0, y), (x1, y)]), kw.get("w", FINE), style="rule",
                    color=kw.get("color", T.INK), layer=kw.get("layer"), role="sill")
    return f


# =============================================================================
# §G.22 rowel star, §G.23 stepping-stone chain
# =============================================================================
def rowel_star(x: float, y: float, r_out: float = 40.0, *, points: int = 8, hub: float | None = None,
               width: float | None = None, lengths: Sequence[float] = (1.0,), widest: float = 0.4,
               hatch_side: int | None = -1, hub_dot: float | None = 4.2, rot: float = -90.0,
               solid: bool = False, w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.22 an ``points``-point star wheel around a hub circle. Each point is
    a lozenge from the hub rim to r_out (× ``lengths`` cycling, e.g. (1, 0.6)
    for the A♦ compass rose), widest at ``widest`` of its length, split on its
    axis with ONE half hatched (``hatch_side`` −1 = counter-clockwise half; the
    same side on every point, so the star is C_n). Default width leaves
    >= 4.2 clear between neighbouring points at their widest.
    ``solid=True`` returns the filled silhouette instead (small gold rowels
    on red, §C rule 4 — contour it in Aquifer separately).

    ``hub`` defaults to 9 px, but never more than r_out / 4, so small
    rowels keep real points. Line mode degrades by the room each point has
    (``meta['detail']``):

    * 'full'    — split lozenges, one half hatched (point width >= 2(w + 3));
    * 'outline' — plain lozenge outlines (the axis would crowd the edges);
    * 'star'    — below that (r_out ≲ 26 at FINE) one closed star outline
      (points at r_out, valleys at 0.42 r_out) with a centre dot where it
      fits: still a rowel, nothing knots into a ring.
    Reductions are recorded in ``meta['warnings']``."""
    hub = min(9.0, 0.25 * r_out) if hub is None else float(hub)
    r_w = hub + widest * (r_out - hub)
    natural = 2 * math.pi * r_w / points - w - MIN_CLEAR - 0.2      # widest point keeping 4.2 clear of its neighbours
    if width is None:
        width = max(2 * (w + 3.0), natural) if (solid or natural >= 2 * (w + 3.0)) else natural
    f = Frag()
    lozs = []
    for k in range(points):
        a = rot + 360.0 * k / points
        Lk = hub + (r_out - hub) * lengths[k % len(lengths)]
        u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        v = np.array([-u[1], u[0]])
        p_in = np.array([x, y]) + u * hub
        p_out = np.array([x, y]) + u * Lk
        pm = p_in + (p_out - p_in) * widest
        wk = width * min(1.0, lengths[k % len(lengths)] ** 0.5)
        pl, pr = pm - v * wk / 2, pm + v * wk / 2
        lozs.append((p_in, pr, p_out, pl))
    if solid:
        from .core import fill as _fill
        core = hub + 0.55 * (r_w - hub)          # fills the V between points near the hub
        sil = G.union(circle_d(x, y, core), *[polyline_d(l, closed=True) for l in lozs])
        return _fill(sil, color=color, layer=layer, role="rowel")
    if width - w < 3.0 or r_out - hub < 3 * w:
        # STAR: too small for lozenges round a hub (their interiors would close and the
        # hub knot into a ring) — one closed star outline, points at r_out and valleys at
        # r_v, miter-sharp, with a centre dot where it keeps 4.2 px clear of the valleys
        r_v = max(0.42 * r_out, w + 1.0)
        pts = []
        for k in range(points):
            a = rot + 360.0 * k / points
            Lk = hub + (r_out - hub) * lengths[k % len(lengths)] if lengths != (1.0,) else r_out
            pts.append(polar(x, y, max(Lk, r_v + w), a))
            pts.append(polar(x, y, r_v, a + 180.0 / points))
        f += stroke(polyline_d(pts, closed=True), w, style="point", color=color, layer=layer, role="point")
        if hub_dot and r_v - w / 2 - hub_dot / 2 >= MIN_CLEAR - 1e-6:
            f += dot(x, y, hub_dot, color=color, layer=layer, role="hub")
        _warn(f, f"rowel_star: r_out {r_out:g} too small for lozenge points — star outline")
        f.meta["detail"] = "star"
        return f
    split = width >= 2 * (w + 3.0) and hatch_side is not None
    f += stroke(circle_d(x, y, hub), w, color=color, layer=layer, role="hub")
    if hub_dot and hub - w / 2 - hub_dot / 2 >= 3.0 - 1e-6:
        f += dot(x, y, hub_dot, color=color, layer=layer)
    for p_in, pr, p_out, pl in lozs:
        f += stroke(polyline_d([p_in, pr, p_out, pl], closed=True), w, style="point", color=color,
                    layer=layer, role="point")
        if split or (hatch_side is None and width >= 2 * (w + 3.0)):
            f += stroke(polyline_d([p_in, p_out]), w, style="point", color=color, layer=layer, role="axis")
        if split:
            f += half_hatch(Polygon([p_in, pr, p_out, pl]), [tuple(p_in), tuple(p_out)], "perp",
                            side=hatch_side, color=color, layer=layer)
    if not split and hatch_side is not None:
        _warn(f, f"rowel_star: points {width:.1f} px wide (< {2 * (w + 3.0):.1f}) — outline only, no split/hatch")
    f.meta["detail"] = "full" if split or hatch_side is None else "outline"
    return f


def stepping_stones(x0: float, x1: float, y: float, *, band: float = 18.0, pitch: float = 24.0,
                    stone: tuple[float, float] = (12.0, 7.0), centre: tuple[float, float] | None = (22.0, 13.0),
                    solid: bool = True, rails: bool = True, w: float = FINE, color: str = T.INK,
                    layer: str | None = None) -> Frag:
    """§G.23 lozenges (length × width) evenly spaced between a double rule
    ``band`` px apart, with a larger centre stone. If the centre stone is
    taller than the band leaves room for, the rails break 4.2 px clear of it.
    ``solid`` stones are filled (small); otherwise outlined."""
    xc = (x0 + x1) / 2
    f = Frag()
    stones = Frag()
    half_n = int(((x1 - x0) / 2 - (centre[0] / 2 if centre else 0) - stone[0] / 2) // pitch)
    xs = [xc + s * k * pitch for k in range(1, half_n + 1) for s in (1, -1)]
    if not centre:
        xs = [xc + (k + 0.5) * pitch * s for k in range(half_n) for s in (1, -1)]

    def mk(cx, L, W):
        d = lozenge_d(cx, y, L, W)
        if solid:
            from .core import fill as _fill
            return _fill(d, color=color, layer=layer, role="stone")
        return stroke(d, w, style="rule", color=color, layer=layer, role="stone")
    for xv in xs:
        stones += mk(xv, *stone)
    if centre:
        cst = mk(xc, *centre)
        stones += cst
    f += stones
    if rails:
        r = stroke(polyline_d([(x0, y - band / 2), (x1, y - band / 2)]) + polyline_d([(x0, y + band / 2), (x1, y + band / 2)]),
                   w, style="rule", color=color, layer=layer, role="rail")
        if centre and centre[1] / 2 + MIN_CLEAR + w > band / 2:
            r = cut(r, cst, MIN_CLEAR)
        f += r
    clear = band / 2 - w / 2 - stone[1] / 2 - (0 if solid else w / 2)
    if clear < 3.0:
        _warn(f, f"stepping_stones: stone-to-rail clear {clear:.1f} < 3")
    return f


# =============================================================================
# §G.26 Spring Lake lens + lens offset field
# =============================================================================
def lens_geometry(cx: float = T.CX, top: float = 104.0, bottom: float = 946.0, width: float = 540.0) -> dict:
    """Vesica through the tips (cx, top), (cx, bottom) with max ``width``.
    Returns dict(R, cy, c_left, c_right, d) — for the back: R = 463.2,
    arc centres (181.8, 525) and (568.2, 525) (§H.19)."""
    c = (bottom - top) / 2
    s = width / 2
    R = (c * c + s * s) / (2 * s)
    cy = (top + bottom) / 2
    off = R - s
    cl, cr = (cx - off, cy), (cx + off, cy)       # cl carries the RIGHT arc, cr the LEFT arc
    d = (f"M{cx:.3f} {top:.3f}A{R:.3f} {R:.3f} 0 0 1 {cx:.3f} {bottom:.3f}"
         f"A{R:.3f} {R:.3f} 0 0 1 {cx:.3f} {top:.3f}Z")
    return dict(R=R, cx=cx, cy=cy, top=top, bottom=bottom, width=width, c_left=cl, c_right=cr, d=d)


def _lens_d(geo, dr):
    """Lens bounded by arcs of radius R + dr about the same centres."""
    R = geo["R"] + dr
    cx, cy = geo["cx"], geo["cy"]
    off = geo["R"] - geo["width"] / 2
    h = math.sqrt(max(R * R - off * off, 0.0))
    top, bot = cy - h, cy + h
    return (f"M{cx:.3f} {top:.3f}A{R:.3f} {R:.3f} 0 0 1 {cx:.3f} {bot:.3f}"
            f"A{R:.3f} {R:.3f} 0 0 1 {cx:.3f} {top:.3f}Z"), top, bot


def lens_cartouche(geo: dict | None = None, *, inner: float | None = None, w: float = FINE,
                   color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.26/§H.19 the lens rule plus a parallel rule inside it. ``inner`` =
    centre-to-centre inset; default w + 4.2 = 6.3 (the brief's "6 px",
    rounded up to keep 4.2 px clear, §I.12). Sharp tips (miter limit 10)."""
    geo = geo or lens_geometry()
    inner = (w + MIN_CLEAR) if inner is None else inner
    f = stroke(geo["d"], w, style="point", color=color, layer=layer, role="lens")
    d_in, _, _ = _lens_d(geo, -inner)
    f += stroke(d_in, w, style="point", color=color, layer=layer, role="lens")
    if inner - w < MIN_CLEAR - 1e-9:
        _warn(f, f"lens_cartouche: inner rule clear {inner - w:.1f} < 4.2")
    f.meta["lens"] = geo
    return f


def lens_field(geo: dict | None = None, *, count: int = 7, pitch: float = 11.0, clip_to=None,
               corners: Sequence[tuple[float, float]] | None = None, solid: int = 2,
               dash_reach: tuple[float, float] = (150.0, 330.0), on: float = 8.0, off: float = 6.0,
               min_len: float = 8.0, w: float = HAIR, color: str = T.INK,
               layer: str | None = None) -> Frag:
    """§G.26 lens offset field: ``count`` outward offset contours of the lens
    at ``pitch`` px (arcs of radius R + k·pitch about the lens centres, so the
    echoes stay pointed), HAIRLINE, clipped to ``clip_to`` (the spandrel
    region; default the lens' bbox grown by the field). They turn to dashes
    (``on``/``off``) progressively toward the ``corners``: contour k is
    dashed wherever it lies within a radius of the nearest corner that grows
    linearly from dash_reach[0] (k = solid+1) to dash_reach[1] (k = count);
    the first ``solid`` contours never dash. Pieces shorter than ``min_len``
    (after clipping) are dropped."""
    geo = geo or lens_geometry()
    if clip_to is None:
        x0, y0, x1, y1 = G.bbox(geo["d"])
        m = count * pitch + 10
        clip_to = box(x0 - m, y0 - m, x1 + m, y1 + m)
    reg = region(clip_to).difference(region(geo["d"]))
    corners = corners if corners is not None else []
    f = Frag()
    for k in range(1, count + 1):
        d, _, _ = _lens_d(geo, k * pitch)
        pts = sample_d(d, 0.5)[0][0]
        ring = LineString(np.vstack([pts, pts[:1]]))
        inside = ring.intersection(reg)
        pieces = [np.asarray(l.coords) for l in _lines(shapely.line_merge(inside) if inside.geom_type == "MultiLineString" else inside)
                  if l.length >= min_len]
        if k <= solid or not corners:
            if pieces:
                f += stroke(pieces, w, color=color, layer=layer, role="field")
            continue
        t = (k - solid - 1) / max(count - solid - 1, 1)
        reach = dash_reach[0] + (dash_reach[1] - dash_reach[0]) * t
        C = np.asarray(corners, float)
        for P in pieces:
            dmin = np.min(np.hypot(P[:, None, 0] - C[None, :, 0], P[:, None, 1] - C[None, :, 1]), axis=1)
            dashed = dmin < reach
            # split into runs
            runs, cur, state = [], [P[0]], dashed[0]
            for p, dsh in zip(P[1:], dashed[1:]):
                cur.append(p)
                if dsh != state:
                    runs.append((state, np.array(cur)))
                    cur, state = [p], dsh
            runs.append((state, np.array(cur)))
            for is_d, R_ in runs:
                if len(R_) < 2:
                    continue
                cvL = G.Curve(R_).length
                if not is_d:
                    if cvL >= min_len:
                        f += stroke(polyline_d(R_), w, color=color, layer=layer, role="field")
                else:
                    # dashes start one 'off' after a solid run, and align from the corner side
                    for dp in dashes(R_, on, off, phase=-off if cvL > on + off else 0.0, min_len=on * 0.6):
                        f += stroke(polyline_d(dp), w, style="rule", color=color, layer=layer, role="dash")
    return f


# =============================================================================
# §G.27 vent roundel, §G.28 festoon, §G.29 pearl beading
# =============================================================================
def vent_roundel(x: float, y: float, d: float = 56.0, *, inner_d: float = 16.0, ribs: int = 12,
                 dot_d: float | None = None, w: float = FINE, color: str = T.INK,
                 layer: str | None = None) -> Frag:
    """§G.27 outer circle Ø``d``, inner circle Ø``inner_d`` and ``ribs``
    STRAIGHT radial ribs between them (achiral, D2-safe). Ribs start on the
    inner circle's centreline; a rib is aligned with each axis."""
    R, r = d / 2, inner_d / 2
    f = stroke(circle_d(x, y, R), w, color=color, layer=layer, role="roundel")
    f += stroke(circle_d(x, y, r), w, color=color, layer=layer, role="roundel")
    f += _ribs(x, y, r, R, ribs, 0.0, start=-90.0, w=w, color=color, layer=layer)
    if dot_d:
        f += dot(x, y, dot_d, color=color, layer=layer)
    return f


def _catenary(p0, p1, sag):
    """Catenary through p0, p1 (screen, y down) whose low point is ``sag`` px
    below the lower support. Returns (points, low_point)."""
    from scipy.optimize import brentq
    (x0, y0), (x1, y1) = p0, p1
    ylow = max(y0, y1) + sag
    h0, h1 = ylow - y0, ylow - y1          # heights of supports above the low point (>0)

    def xs_for(a):
        # distance from the low point to each support horizontally
        return a * math.acosh(1 + h0 / a), a * math.acosh(1 + h1 / a)

    span = abs(x1 - x0)

    def fn(a):
        d0, d1 = xs_for(a)
        return d0 + d1 - span
    a = brentq(fn, 1e-3, 1e6)
    d0, d1 = xs_for(a)
    sgn = 1 if x1 > x0 else -1
    xm = x0 + sgn * d0
    xx = np.linspace(x0, x1, max(20, int(span / 0.5)))
    yy = ylow - a * (np.cosh((xx - xm) / a) - 1)
    yy = 2 * ylow - (ylow + a * (np.cosh((xx - xm) / a) - 1))   # y down: supports ABOVE low point
    return np.column_stack([xx, yy]), (xm, ylow)


def festoon(supports: Sequence[tuple[float, float]], sag: float = 18.0, *, bulb_d: float = TD,
            joins: bool = True, low: bool = True, drop: float = 0.0, w: float = FINE,
            color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.28 string lights: catenary arcs between consecutive ``supports``
    (each sagging ``sag`` px below its lower support) with bulbs (solid Ø6.3
    dots — the brief's 5–6 px rounded to the legal dot) at each low point and
    at the joins. ``drop`` > 0 hangs each low bulb on a short drop line."""
    f = Frag()
    for p0, p1 in zip(supports[:-1], supports[1:]):
        pts, lowp = _catenary(p0, p1, sag)
        f += stroke(polyline_d(pts), w, color=color, layer=layer, role="wire")
        if low:
            bx, by = lowp
            if drop:
                f += stroke(polyline_d([(bx, by), (bx, by + drop)]), w, color=color, layer=layer)
                by += drop
            f += dot(bx, by, bulb_d, color=color, layer=layer, role="bulb")
    if joins:
        for p in supports:
            f += dot(*p, bulb_d, color=color, layer=layer, role="bulb")
    return f


def pearl_beading(path, *, d_min: float = 4.2, d_max: float = 8.4, n: int | None = None,
                  gap: float = 3.5, power: float = 1.0, style: str = "dot", w: float = FINE,
                  color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.29 graduated pearls along a path (d-string or points), largest at
    the centre, equal clear ``gap``. With ``n`` omitted, as many as fit.
    Symmetric about the path's midpoint."""
    pts = sample_d(path, 0.25)[0][0] if isinstance(path, str) else np.asarray(path, float)
    cv = G.Curve(pts)
    L = cv.length

    def sizes(m):
        if m == 1:
            return [d_max]
        t = np.abs(np.linspace(-1, 1, m))
        return list(d_min + (d_max - d_min) * (1 - t) ** power)

    def outer(dd):
        return dd if style == "dot" else dd + w

    if n is None:
        n = 1
        while True:
            s = sizes(n + 2)
            if sum(outer(v) for v in s) + (n + 1) * gap > L:
                break
            n += 2
    ds = sizes(n)
    total = sum(outer(v) for v in ds) + (n - 1) * gap
    s = (L - total) / 2
    f = Frag()
    for dd in ds:
        s += outer(dd) / 2
        f += bubble(*cv.at_s(s), dd, style=style, w=w, color=color, layer=layer)
        s += outer(dd) / 2 + gap
    return f


# =============================================================================
# §G.30 conduit
# =============================================================================
def conduit(path, width: float = 14.0, *, d0: float = 3.0, ratio: float = 1.2, n: int | None = None,
            d_max: float | None = None, bubbles: bool = True, style: str = "dot", end_gap: float = 6.0,
            w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.30 two parallel FINE rails ``width`` px apart (12–18) along ``path``
    (start = bottom of the rise) carrying ``n`` bubbles that grow ×``ratio``
    upward (capped at ``d_max``, default: 3 px clear of each rail), spread
    along the whole run with equal clear gaps. ``meta['hull']`` is the band's
    outline — pass the conduit to :func:`conduit_break` to break anything it
    crosses with a 4 px gap."""
    pts = sample_d(path, 0.25)[0][0] if isinstance(path, str) else np.asarray(path, float)
    cv = G.Curve(pts)
    hw = width / 2
    left = cv.offset(hw)
    right = cv.offset(-hw)
    f = stroke(polyline_d(left) + polyline_d(right), w, style="rule", color=color, layer=layer, role="rail")
    clear_in = width - w                     # clear width between the rails
    if bubbles:
        room = clear_in - 2 * 3.0            # outer diameter allowed
        dm_auto = room if style == "dot" else room - w
        dm = dm_auto if d_max is None else d_max
        if n is None:
            n = max(2, int(cv.length / (2.2 * (d0 + dm) / 2)))
        sizes = [min(dm, d0 * ratio ** k) for k in range(n)]
        outer = [sz if style == "dot" else sz + w for sz in sizes]
        usable = cv.length - 2 * end_gap
        gap = (usable - sum(outer)) / max(n - 1, 1)
        if gap < 3.0:
            _warn(f, f"conduit: bubble gap {gap:.1f} < 3 (too many bubbles)")
        sv = end_gap
        for sz, do in zip(sizes, outer):
            sv += do / 2
            f += bubble(*cv.at_s(sv), sz, style=style, w=w, color=color, layer=layer)
            sv += do / 2 + gap
        side_clear = (clear_in - max(outer)) / 2
        if side_clear < 3.0 - 1e-6:
            _warn(f, f"conduit: bubble-to-rail clear {side_clear:.1f} < 3")
    hull = LineString(cv.pts).buffer(hw + w / 2, cap_style="flat")
    f.meta["hull"] = hull
    return f


def conduit_break(f: Frag, conduit_frag: Frag, gap: float = 4.0) -> Frag:
    """Break ``f`` where the conduit crosses it: removed across the whole
    conduit band plus ``gap`` px (4 px, §G.30)."""
    return cut(f, conduit_frag.meta["hull"], gap)


# =============================================================================
# §G.31 tooled scroll
# =============================================================================
def volute(x: float, y: float, r0: float = 12.0, *, heading: float = -90.0, cw: bool = True,
           turns: float = 1.0, q: float = 0.72, eye: bool = True, w: float = FINE, color: str = T.INK,
           layer: str | None = None) -> Frag:
    """A volute of tangent circular arcs entered at (x, y) with ``heading``,
    curling clockwise on screen if ``cw``.

    turns = 1.0 (default) — the deck's 'eye' volute (shared with the wave
      hook, §G.7): a half turn at radius r0 then a half turn at r0/2, which
      lands exactly on the first arc's centre; the Ø6.3 terminal sits there,
      r0 − 4.2 px clear of the coil (needs r0 >= 8.4).
    turns > 1 — a half turn at r0 then quarter arcs shrinking ×``q``.
    ``meta``: 'centre' (first arc centre), 'exit' (point, heading) where the
    first half turn ends — the place to branch a tangent link from."""
    t = Turtle(x, y, heading)
    sg = 1 if cw else -1
    t.arc(r0, sg * 180)
    exit_ = (tuple(t.pos), t.heading)
    if abs(turns - 1.0) < 1e-9:
        t.arc(r0 / 2, sg * 180)
    else:
        r = r0 * q
        for _ in range(int(round((turns - 0.5) * 4))):
            t.arc(r, sg * 90)
            r *= q
    f = stroke(t.d(), w, color=color, layer=layer, role="volute")
    if eye:
        f += terminal(*t.pos, color=color, layer=layer)
    hr = math.radians(heading + sg * 90)
    f.meta.update(centre=(x + r0 * math.cos(hr), y + r0 * math.sin(hr)), exit=exit_, end=(tuple(t.pos), t.heading))
    if eye and r0 - TD / 2 - w / 2 < MIN_CLEAR - 1e-6:
        _warn(f, f"volute: eye only {r0 - TD / 2 - w / 2:.1f} px clear (r0 < 8.4)")
    return f


def tooled_scroll(x0: float, x1: float, y: float, *, height: float = 40.0, n: int | None = None,
                  leaf: bool = True, w: float = FINE, color: str = T.INK,
                  layer: str | None = None) -> Frag:
    """§G.31 vaquero tooled scroll band (♦ cuffs and belts ONLY; replaces
    acanthus) from x0 to x1, centred on y, ``height`` tall.

    A running spiral: 'eye' volutes (see :func:`volute`) alternate above and
    below the centre line, each entered tangentially at its outer side. The
    link to the next volute BRANCHES tangentially off the far side of the
    current one (where its first half turn ends) and is an S of two equal
    arcs of <= 90°, so no stroke doubles back. One vesica leaf (on a short
    petiole; midrib only when it fits 4.2 clear) springs from each S's inflection into the empty space opposite
    the next volute. Lead-in/out stems join the band line at both ends."""
    H = height
    r0 = 0.28 * H                                # volute radius
    a = H / 2 - r0 - w / 2                       # volute centres at y ± a
    L = x1 - x0
    lead = 0.35 * H
    run = L - 2 * lead - 2 * r0
    pmax = 2 * r0 + 2 * a                        # S arcs of exactly 90°
    if n is None:
        n = max(1, int(math.ceil(run / pmax)) + 1)
    p = run / (n - 1) if n > 1 else 0.0
    gapx = p - 2 * r0
    theta = 2 * math.degrees(math.atan2(gapx, 2 * a)) if n > 1 else 0.0
    rho = a / math.sin(math.radians(theta)) if n > 1 and theta > 1e-6 else 0.0
    f = Frag()
    for k in range(n):
        up = k % 2 == 0
        side = 1 if up else -1                   # +1: volute above, curling clockwise
        cx = x0 + lead + r0 + k * p
        cyv = y - a if up else y + a
        entry = (cx - r0, cyv)
        v = volute(*entry, r0, heading=-90.0 if up else 90.0, cw=up, w=w, color=color, layer=layer)
        f += v
        exit_pt, exit_head = v.meta["exit"]
        if k == 0:
            t = Turtle(x0, y, 0.0)
            ri = min(lead, abs(y - cyv))
            t.fd(max(entry[0] - x0 - ri, 0.0)).arc(ri, -side * 90)
            f += stroke(t.d(), w, color=color, layer=layer, role="stem")
        if k < n - 1:
            s_t = Turtle(*exit_pt, exit_head)
            s_t.arc(rho, -side * theta)
            infl, infl_head = s_t.pos.copy(), s_t.heading
            s_t.arc(rho, side * theta)
            f += stroke(s_t.d(), w, color=color, layer=layer, role="stem")
            if leaf:
                from .core import vesica_d
                ang = math.radians(infl_head - side * 70.0)
                u = np.array([math.cos(ang), math.sin(ang)])
                Lf = 1.4 * r0
                Wf = 0.4 * Lf
                pet = w + 2.5                    # petiole
                p0 = infl + u * pet
                p1 = p0 + u * Lf
                # midrib only when it keeps 4.2 clear inside the leaf
                rib_to = 0.55 if Wf / 2 - w >= MIN_CLEAR else 0.0
                f += stroke(polyline_d([infl, p0 + u * rib_to * Lf]), w, color=color, layer=layer, role="petiole")
                f += stroke(vesica_d(p0, p1, Wf), w, style="point", color=color, layer=layer, role="leaf")
        else:
            t = Turtle(*exit_pt, exit_head)
            ro = min(lead, abs(y - cyv))
            t.arc(ro, -side * 90)
            t.line_to(x1, y)
            f += stroke(t.d(), w, color=color, layer=layer, role="stem")
    f.meta.update(n_volutes=n, pitch=p, s_angle=theta)
    return f
