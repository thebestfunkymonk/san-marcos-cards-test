"""Card back frame (brief §H.19 items 1-6): D2 about (375, 525).

Everything here is line art (``Frag``) that ``art/BACK.py`` knocks out of
the jade flood.  Every part is authored once (a quadrant, a band or a side)
and completed by exact mirrors, so the frame is D2 by construction.

From the flood edge inward:

1. outer RULE at inset 12 (x/y 49.5) and a FINE companion 8 px inside it
   (57.5);
2. top / bottom bands (57.5-91.5): a running wave flowing OUTWARD from the
   axis, where a two-tread fault-step plinth stands in the band, its narrow
   tread facing -- receiving -- the lens tip;
3. side bands (57.5-79.5): a reed ladder (rungs every 26 px, symmetric
   about y 525, a node on every 4th rung) with a reed-node medallion at
   y 525;
4. corners: a vent roundel centred on the crossing of the two bands; every
   rule breaks 4 px round it and ends there;
5. the lens cartouche (Spring Lake in plan) and its inner rule;
6. spandrels: the lens offset field -- HAIRLINE echoes of the lens at an
   11 px pitch, dashing toward the corners -- and, in the far corners, a
   §G.8 ripple group spreading from each corner vent.

Deviations (smallest changes that keep §I.12 spacing):
* corner roundel Ø 52, not 56: at the band crossing (68.5, 74.5) a Ø 56
  ring leaves 1.95 px of jade to the flood edge (knockout bridges need 3);
  Ø 52 leaves 3.95 and keeps the roundel centred on both bands;
* side medallion Ø 25.5, not 26: Ø 26 comes 2.85 px from the outer RULE
  (approach minimum 3.0); Ø 25.5 clears it by 3.1 so the outer rule runs
  unbroken past it.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, Point, box

from deck import tokens as T
from deck.motifs import core as C, geometric as M
from inkkit import geom as G

CX, CY = T.CX, T.CY
FINE, HAIR, RULE = T.FINE, T.HAIRLINE, T.RULE

# ---- §H.19 frame geometry ----------------------------------------------------
FLOOD = (37.5, 37.5, 712.5, 1012.5)
FLOOD_R = 18.0
OUTER = 49.5            # RULE, inset 12 from the flood edge
COMPANION = 57.5        # FINE, 8 px inside the outer rule
BAND_Y = 91.5           # top band 57.5-91.5 (its inner rule)
BAND_X = 79.5           # side band 57.5-79.5 (its inner rule)
LENS = dict(top=104.0, bottom=946.0, width=540.0)

ROUNDEL_C = ((COMPANION + BAND_X) / 2, (COMPANION + BAND_Y) / 2)     # (68.5, 74.5)
ROUNDEL_D = 52.0
RULE_BREAK = 4.0        # "the rules break 4 px around it"
MED_D = 25.5            # side-band reed-node medallion
LADDER_PITCH = 26.0

PLINTH = dict(w_top=38.0, w_base=62.0, tread_h=11.0, hatch=True)


def flood_d() -> str:
    x0, y0, x1, y1 = FLOOD
    return G.rect_d(x0, y0, x1 - x0, y1 - y0, FLOOD_R)


def lens_geo():
    return M.lens_geometry(CX, LENS["top"], LENS["bottom"], LENS["width"])


def d2(f: C.Frag) -> C.Frag:
    return f + f.mirror_x(CX) + f.mirror_y(CY) + f.mirror_x(CX).mirror_y(CY)


def roundel_tl() -> C.Frag:
    return M.vent_roundel(*ROUNDEL_C, ROUNDEL_D, inner_d=16.0, ribs=12)


def roundels() -> C.Frag:
    return d2(roundel_tl())


def medallion_l() -> C.Frag:
    xc = (COMPANION + BAND_X) / 2
    return M.reed_node_medallion(xc, CY, MED_D, rot=90)


def medallions() -> C.Frag:
    m = medallion_l()
    return m + m.mirror_x(CX)


# ---- plinth --------------------------------------------------------------------
def plinth_top() -> C.Frag:
    """Two-tread fault-step plinth on the axis (§G.10, the Balcones step):
    in the bottom band it stands on the companion rule, wide tread below,
    narrow tread above, with the lens tip resting over it; the top band has
    the mirror image (authored here).  Closed slabs with a bedding line
    between them."""
    sp = PLINTH
    y_base = COMPANION                    # top band: the base is the companion rule
    h = sp["tread_h"]
    a, b = sp["w_base"] / 2, sp["w_top"] / 2
    y1, y2 = y_base + h, y_base + 2 * h
    pts = [(CX - a, y_base), (CX - a, y1), (CX - b, y1), (CX - b, y2), (CX + b, y2), (CX + b, y1),
           (CX + a, y1), (CX + a, y_base)]
    f = C.stroke(C.polyline_d(pts), FINE, style="rule", role="plinth")
    f += C.stroke(C.polyline_d([(CX - b, y1), (CX + b, y1)]), FINE, style="rule", role="bedding")
    # the lower (wide) tread half-hatched at 45° like the A♠ plinth -- as a chevron
    # meeting on the axis, so the frame stays D2
    if PLINTH.get("hatch"):
        for sgn in (-1, 1):
            xa, xb = sorted((CX, CX + sgn * a))
            # the V points sit on the tread's rules (9.9 px apart on the axis), which cover them
            yv = (y_base + y1) / 2 - T.HATCH_PITCH * math.sqrt(2) / 2
            f += C.hatch(box(xa, y_base, xb, y1), 45.0 * sgn, T.HATCH_PITCH, origin=(CX, yv))
    f.meta["plinth"] = dict(a=a, b=b, bottom=y2)
    return f


def plinth_zone():
    return plinth_top().shape()


# ---- rules ---------------------------------------------------------------------
def _cut_rules(f: C.Frag, medallion: bool = True) -> C.Frag:
    f = C.cut(f, C.region(roundels().outline()), RULE_BREAK)
    if medallion:
        f = C.cut(f, C.region(medallions().outline()), RULE_BREAK)
    return f


def rules() -> C.Frag:
    """The nested rectangles as straight butt-capped runs, broken 4 px round
    the corner roundels (and the band rules round the side medallions).
    The band's inner rule is broken where the plinth's narrow tread stands
    on it (the tread is drawn by the plinth)."""
    f = C.Frag()
    for inset, w in ((OUTER, RULE), (COMPANION, FINE), (None, FINE)):
        if inset is None:
            x0, y0, x1, y1 = BAND_X, BAND_Y, 2 * CX - BAND_X, 2 * CY - BAND_Y
        else:
            x0, y0, x1, y1 = inset, inset, 2 * CX - inset, 2 * CY - inset
        runs = [[(x0, y0), (x1, y0)], [(x0, y1), (x1, y1)], [(x0, y0), (x0, y1)], [(x1, y0), (x1, y1)]]
        g = C.stroke("".join(C.polyline_d(r) for r in runs), w, style="rule", role="rule")
        # the outer RULE runs unbroken past the side medallions (3.1 px clear)
        f += _cut_rules(g, medallion=inset != OUTER)
    # every piece that remains must be a full run between two breaks (no corner stubs)
    out = C.Frag()
    for m in f.marks:
        keep = [p for p, _ in G.flatten(m.d, 0.05) if len(p) > 1 and LineString(p).length >= 40.0]
        if keep:
            out += C.stroke([np.asarray(p) for p in keep], m.w, style="rule", role="rule")
    return out


# ---- top / bottom bands ------------------------------------------------------------
WAVE = dict(height=20.0, pitch=30.0, clear=5.0)


def top_band() -> C.Frag:
    """Running wave springing from the band's inner rule and flowing outward
    from the plinth; as many whole waves as fit between the plinth and the
    corner roundel."""
    sp = WAVE
    hook = M.wave_hook(sp["height"], w=FINE)
    wd = hook.meta["wave_width"]
    a = PLINTH["w_base"] / 2
    x_start = CX + a + FINE + sp["clear"]                    # first spring point
    # the roundel's clearance zone along the band
    rz = roundels().shape().buffer(RULE_BREAK + FINE / 2)
    n = 0
    while True:
        cand = M.running_wave(x_start, x_start + n * sp["pitch"] + wd, BAND_Y, height=sp["height"],
                              pitch=sp["pitch"], flow=1, rule=False, start=x_start)
        if cand.shape().intersects(rz):
            break
        n += 1
    right = M.running_wave(x_start, x_start + (n - 1) * sp["pitch"] + wd, BAND_Y, height=sp["height"],
                           pitch=sp["pitch"], flow=1, rule=False, start=x_start)
    f = right + right.mirror_x(CX) + plinth_top()
    f.meta["n_waves"] = 2 * n
    return f


def bands() -> C.Frag:
    b = top_band()
    return b + b.mirror_y(CY)


# ---- side bands -----------------------------------------------------------------
def side_band_upper() -> C.Frag:
    """Left side band, upper half: rungs at y = 525 - 26 k across the band
    (the band rules are the ladder's rails), a node ellipse on every 4th
    rung counted from the medallion (k = 2, 6, 10, ...), stopping clear of
    the corner roundel."""
    x0, x1 = COMPANION, BAND_X
    xc = (x0 + x1) / 2
    hw = (x1 - x0) / 2
    f = C.Frag()
    rz = roundels().shape()
    mz = medallions().shape()
    k = 1
    while True:
        y = CY - LADDER_PITCH * k
        if y < 0:
            break
        if k % 4 == 2:
            g = C.stroke(G.ellipse_d(xc, y, hw, 4.5, 0.0), FINE, role="node")
        else:
            g = C.stroke(C.polyline_d([(x0, y), (x1, y)]), FINE, style="rule", role="rung")
        sh = g.shape()
        if sh.distance(rz) < 4.2 or sh.distance(mz) < 4.2:
            if sh.distance(rz) < 4.2:
                break
        else:
            f += g
        k += 1
    return f


def sides() -> C.Frag:
    s = side_band_upper()
    s = s + s.mirror_y(CY)
    return s + s.mirror_x(CX) + medallions()


# ---- lens + spandrels --------------------------------------------------------------
def lens() -> C.Frag:
    return M.lens_cartouche(lens_geo())


def spandrel_region():
    """Inside the band rules (4.2 clear of them, HAIRLINE allowed for), clear
    of the plinths and the corner roundels, outside the lens."""
    m = FINE / 2 + 4.2 + HAIR / 2
    inner = box(BAND_X + m, BAND_Y + m, 2 * CX - BAND_X - m, 2 * CY - BAND_Y - m)
    pl = plinth_zone().buffer(4.2 + HAIR / 2)
    pl = shapely.union_all([pl, shapely.affinity.scale(pl, 1, -1, origin=(CX, CY))])
    rz = roundels().shape().buffer(4.2 + HAIR / 2)
    return inner.difference(pl).difference(rz)


FIELD = dict(count=7, pitch=11.0, solid=6, dash_reach=(150.0, 330.0))


def field(spec=FIELD) -> C.Frag:
    geo = lens_geo()
    clip = spandrel_region().difference(C.region(lens().outline(grow=4.2 + HAIR / 2)))
    corners = [(BAND_X, BAND_Y), (2 * CX - BAND_X, BAND_Y),
               (BAND_X, 2 * CY - BAND_Y), (2 * CX - BAND_X, 2 * CY - BAND_Y)]
    kw = {k: v for k, v in spec.items() if k != "count"}
    return M.lens_field(geo, count=spec["count"], clip_to=clip, corners=corners, **kw)


CORNER = dict(radii=(34.0, 40.5, 47.6, 55.5, 64.2, 73.8, 84.4, 96.0, 109.0, 124.0), dashed=(),
              w=FINE, gap=6.0)


def corner_ripples(spec=CORNER) -> C.Frag:
    """§G.8 ripples spreading from the corner vent: arcs about the roundel,
    gaps growing x1.26 outward, clipped to the spandrel and stopped ``gap``
    px short of the lens field."""
    geo = lens_geo()
    n = FIELD["count"]
    reach = n * FIELD["pitch"] + HAIR / 2 + spec["gap"] + spec["w"] / 2
    zone = spandrel_region().difference(C.region(M._lens_d(geo, reach)[0]))
    zone = zone.intersection(box(0, 0, CX, CY))
    f = C.Frag()
    for r in spec["radii"]:
        f += C.stroke(C.circle_d(*ROUNDEL_C, r), spec["w"], role="ripple")
    f = C.clip(f, zone)
    out = C.Frag()
    for m in f.marks:
        keep = [p for p, _ in G.flatten(m.d, 0.05) if len(p) > 1 and LineString(p).length >= 12.0]
        if keep:
            out += C.stroke([np.asarray(p) for p in keep], m.w, role="ripple")
    # beyond them the ripples fade to HAIRLINE dashes (§B.2 dashed spandrel contours),
    # as the lens field does toward the corners: the two ring systems meet in dashes
    for r in spec.get("dashed", ()):
        arc = LineString(C.sample_d(C.circle_d(*ROUNDEL_C, r), 0.5)[0][0]).intersection(
            zone.buffer(-(HAIR / 2 + 0.01)))
        for g in getattr(arc, "geoms", [arc]):
            if g.is_empty or g.length < 20.0:
                continue
            P = np.asarray(g.coords)
            # dashes run from the band ends toward the diagonal, symmetric about it
            for dp in C.dashes(P, 8.0, 6.0, min_len=4.8):
                out += C.stroke(C.polyline_d(dp), HAIR, style="rule", role="dash")
    return d2(out)


INNER = dict(count=6, pitch=8.4, clear=20.1, min_len=60.0, w=FINE)


def inner_ripples(spec=INNER, occupied=None) -> C.Frag:
    """The lens field continued INSIDE the lens, as depth contours along
    Spring Lake's shore: echoes of the lens inner rule at the field's 11 px
    pitch -- FINE, as solid ornament on the back (§B.2 keeps HAIRLINE for
    the dashed spandrel contours) -- wherever the emblem leaves room -- kept ``clear``
    px (the §H.19 20 px of flat jade) from ``occupied`` (the emblem's
    marks; default: its whole limit region).  Pieces shorter than
    ``min_len`` are dropped."""
    from art import _back_geo as BG
    geo = lens_geo()
    inner = BG.LENS_IN - FINE / 2          # centre of the inner rule, inside the lens outline
    if occupied is None:
        occupied = BG.limit_region()
    keep_out = occupied.buffer(spec["clear"] + spec.get("w", HAIR) / 2, quad_segs=16)
    f = C.Frag()
    for k in range(1, spec["count"] + 1):
        d, _, _ = M._lens_d(geo, -(inner + spec.get("first", spec["pitch"]) + (k - 1) * spec["pitch"]))
        pts = C.sample_d(d, 0.5)[0][0]
        ring = LineString(np.vstack([pts, pts[:1]]))
        rest = ring.difference(keep_out)
        if rest.geom_type == "MultiLineString":
            rest = shapely.line_merge(rest)
        for g in getattr(rest, "geoms", [rest]):
            if g.is_empty or g.length < spec["min_len"]:
                continue
            f += C.stroke(C.polyline_d(np.asarray(g.coords)), spec.get("w", HAIR), role="inner")
    return f


def frame(emblem_shape=None) -> dict:
    """{name: Frag} of the frame parts, already cut where they meet.
    ``emblem_shape`` (shapely) lets the inner echoes run wherever the emblem
    leaves 20 px of jade, not just outside its limit region."""
    d = dict(rules=rules(), roundels=roundels(), bands=bands(), sides=sides(), lens=lens(),
             field=field())
    if CORNER:
        d["corner"] = corner_ripples()
    if INNER and INNER.get("count"):
        d["inner"] = inner_ripples(occupied=emblem_shape)
    return d
