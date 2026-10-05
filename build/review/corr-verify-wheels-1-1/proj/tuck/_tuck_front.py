"""TUCK-FRONT (brief §H.20 front, §D.2 wordmark): the 769 × 1069 front panel.

Bilateral composition with ONE dynamic element, the lion andante.  The frame
is the card back's vocabulary laid out 1 : 1 for the panel (never scaled):
outer RULE + FINE companion, vent-roundel corners (on the corner diagonal, as
on the back), running-wave top/bottom
bands flowing outward from a two-tread fault-step plinth, reed-ladder sides
with a reed-node medallion at mid-height.

Content, top to bottom (panel px):
  kicker      NAMED FOR ST. MARK · 1689 — Barlow SemiBold cap 14, +250, y ≈ 150
  wordmark    HEADWATERS — Roboto Slab 700 cap 60, +60, on a convex lintel arc
              R 1300 whose crown is at y 235; inline + 45° hatched shadow (§D.2)
  subline     PLAYING CARDS OF THE SAN MARCOS SPRINGS — cap 14, +220, y ≈ 285
  lens        330 × 440, y 320–760, holding the lion andante (tuck/_tuck_lion.py),
              with the §G.26 lens offset field spreading into the spandrels
  wreath      §G.6 wild-rice wreath wrapping the lens's lower two-thirds, tied at
              its foot by a LEVEL swallowtail ribbon: NUMQUAM DEFICIT
  foot band   y ≈ 905: ♠ ♥ ♣ ♦ gold OUTLINE pips (u 32) alternating with bubble
              dots, between FINE rules
  place line  SAN MARCOS · TEXAS — cap 16, +250, y ≈ 965

§D.2 engineered for foil (the brief's literal numbers would fill in):
* INLINE — a 0.22 × stem FINE line inset in the ground colour leaves a 1.6 px
  foil border and a 2.1 px knockout, and foil closes any gap under 4.2 px.  The
  inline is therefore cut as a HIGHLIGHT groove along the upper-left edges of
  each letter: a 1.6 px foil border (the foil minimum), a 4.2 px groove, the
  rest solid (≥ 1.6 everywhere; slivers are opened away).
* SHADOW — the letters EXTRUDED (+9, +9) minus the letters grown by the 4.2 px
  foil gap, filled with FINE 45° hatch at 7.0 running with the extrusion.  Light
  from the upper left: highlight top-left, hatched depth bottom-right.

The wordmark is set as a true LINTEL: at 660 px on its arc it is wider than the
frame's clear interior (641), so its end letters rest on the reed-ladder posts,
which break 4.2 px clear of the letters and their shadow; the outer RULE and
its companion run on unbroken.

Blind emboss (own plate): the wordmark (level 1), the lens (level 1 plateau)
with the lion sculpted (level 2), the ribbon (level 1).  The ground stays flat.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
import shapely.ops
from shapely.geometry import LineString, Point, Polygon, box

from deck import tokens as T
from deck import frames as F
from deck import pips as PIPS
from deck.motifs import core as C
from deck.motifs import geometric as M
from deck.motifs import rice as RI
from inkkit import geom as G
from inkkit.typeset import text_on_arc

from art import _back_frame as _BF
from tuck import _tuck_common as K
from tuck import _tuck_lion as LION

FOIL = K.FOIL
FINE, HAIR, RULE = K.FINE, K.HAIR, K.RULE
PW, PH, PCX, PCY = K.PW, K.PH, K.PCX, K.PCY
GAP = K.GAP

# ---- frame (the back's vocabulary, laid out 1:1 for the panel) ---------------------------
OUTER = K.FRAME_OUTER            # outer RULE centreline inset from the fold
COMPANION = K.FRAME_COMPANION    # FINE companion, 8 px inside (as on the back)
BAND_Y = K.FRAME_BAND_Y          # inner rule of the top band (band 42 → 76, as the back's 34 px)
BAND_X = K.FRAME_BAND_X          # inner rule of the side band (band 42 → 64, as the back's 22 px)
# the corner wheel on the corner diagonal, midway between the two band centres (the card back's rule,
# art/_back_frame.wheel_centre): equal clearances to the fold and the outer rules on both axes
ROUNDEL_C = _BF.wheel_centre(COMPANION, BAND_X, BAND_Y)     # (56, 56)
ROUNDEL_D = 52.0
MED_D = 25.5
RULE_BREAK = 4.0
PLINTH = dict(w_top=38.0, w_base=62.0, tread_h=11.0)
WAVE = dict(height=20.0, pitch=30.0, clear=5.0)

# ---- content ------------------------------------------------------------------------------
KICKER = "NAMED FOR ST. MARK · 1689"
SUBLINE = "PLAYING CARDS OF THE SAN MARCOS SPRINGS"
MOTTO = "NUMQUAM DEFICIT"
PLACE = "SAN MARCOS · TEXAS"

KICKER_Y = 157.0             # baseline (cap 14 → cap middle 150)
WORD_CROWN = 235.0           # baseline crown of the lintel arc
WORD_R = 1300.0
SUB_Y = 292.0                # baseline (cap middle 285)
LENS_TOP, LENS_BOT, LENS_W = 320.0, 760.0, 330.0
LENS_C = (PCX, (LENS_TOP + LENS_BOT) / 2)
RIBBON_Y = 791.0             # ribbon face centre line
FOOT_Y = 905.0
PLACE_Y = 973.0              # baseline (cap 16 → cap middle 965)

WORD_CAP, WORD_TRACK = 60.0, 60.0
BORDER = 3.0                 # foil border outside the inline groove (a solid bridge: >= 3.0, §I.12)
GROOVE = 3.0                 # the inline groove (a knockout line: >= 2.5, §I.12)
SHADOW_OFF = (7.0, 7.0)      # §D.2 (+5, +5) → 7: one full hatch pitch, so the 45° hatch reads as
SHADOW_CLEAR = 0.0           # lines, not dashes; it BUTTS on the letters (as hatch butts any contour)


def lens_geo():
    return M.lens_geometry(PCX, LENS_TOP, LENS_BOT, LENS_W)


# =============================================================================
# wordmark (§D.2)
# =============================================================================
def wordmark():
    """-> dict(fill=Frag, shadow=Frag, glyphs=shapely, keep=shapely (letters +
    shadow), letters=shapely, d=str).

    §D.2 for one foil, legal by §I.12 (foil lines >= 1.6, knockouts >= 2.5,
    solid bridges >= 3.0):
    * INLINE: a groove cut into each letter along its upper-left (lit) edges,
      BORDER px in from the edge and GROOVE px wide (knockout, >= 2.5),
      leaving the rest of the stroke solid.  The groove lives inside the
      letter inset by BORDER on every side, so every bridge of foil between
      it and any edge is >= 3.0; groove slivers narrower than GROOVE are
      opened away.
    * SHADOW: each letter EXTRUDED (+SHADOW_OFF) toward the lower right and
      the extrusion (minus the letter, and 4.2 px clear of every OTHER letter)
      filled with FINE 45° hatch at the 7.0 pitch; the hatch butts its letter.
    Glyphs + shadow are centred as one unit on the panel axis."""
    size = F.cap_to_size(K.FONT_SLAB, WORD_CAP, T.SLAB_VARIATIONS)
    cy = WORD_CROWN + WORD_R
    d = text_on_arc(K.FONT_SLAB, "HEADWATERS", size, PCX, cy, WORD_R, baseline="alphabetic",
                    variations=T.SLAB_VARIATIONS, tracking=WORD_TRACK)
    bb = G.bbox(d)
    dx = PCX - (bb[0] + bb[2] + SHADOW_OFF[0]) / 2                  # centre letters + shadow together
    d = G.translate(d, dx, 0.0)
    glyphs = G.to_shape(d, tol=0.02)
    letters_list = sorted(getattr(glyphs, "geoms", [glyphs]), key=lambda g_: g_.bounds[0])
    # ---- inline groove ----------------------------------------------------------------------
    E = glyphs.buffer(-BORDER, join_style="round", quad_segs=16)          # exact erosion: >= BORDER from every edge
    core = E
    for a in np.linspace(0.0, 90.0, 13):
        v = GROOVE * np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        core = core.intersection(shapely.affinity.translate(E, v[0], v[1]))
    groove = E.difference(core)
    ko = GROOVE / 2 - 0.05                                           # open away groove slivers (< GROOVE)
    groove = groove.buffer(-ko, join_style="round").buffer(ko, join_style="round")
    # grooves that come within 3 px of each other merge (no foil sliver < 3 between two knockouts)
    groove = groove.buffer(1.6, join_style="round").buffer(-1.6, join_style="round").intersection(E)
    def _clean(gr):
        return shapely.union_all([g_ for g_ in getattr(gr, "geoms", [gr])
                                  if g_.area > 6.0 and 2 * shapely.maximum_inscribed_circle(g_, 0.05).length >= 2.6])
    groove = _clean(groove)
    for _ in range(4):
        # two groove pieces closer than 3 px would leave a foil neck < 3 (§I.12 solid bridge): join them
        pcs = list(getattr(groove, "geoms", [groove]))
        bridges = []
        for i_ in range(len(pcs)):
            for j_ in range(i_ + 1, len(pcs)):
                dd = pcs[i_].distance(pcs[j_])
                if 0.0 < dd < 3.1:
                    a_, b_ = shapely.ops.nearest_points(pcs[i_], pcs[j_])
                    bridges.append(LineString([a_, b_]).buffer(GROOVE / 2, cap_style="round"))
        if not bridges:
            break
        groove = _clean(groove.union(shapely.union_all(bridges).intersection(E)))
    letters = glyphs.difference(groove)
    fill = C.fill(G.from_shape(letters), color=FOIL, role="wordmark")
    # ---- hatched extrusion shadow ------------------------------------------------------------
    n = 24
    regions = []
    for i, gl in enumerate(letters_list):
        ex = shapely.union_all([shapely.affinity.translate(gl, SHADOW_OFF[0] * t / n, SHADOW_OFF[1] * t / n)
                                for t in range(n + 1)])
        others = shapely.union_all([o for j, o in enumerate(letters_list) if j != i])
        # the hatch starts 1 px INSIDE its own letter (so no pinhole is left where a butt end meets a
        # serif's bracket) and stays 4.2 px clear of every other letter
        regions.append(ex.difference(gl.buffer(-1.0, join_style="mitre")).difference(others.buffer(GAP)))
    sh_in = shapely.union_all(regions)
    shadow = C.hatch(sh_in, 45.0, 7.0, color=FOIL, min_len=3.0)
    shadow = K.drop_short(shadow, 3.0)
    keep = shapely.union_all([glyphs, sh_in])
    return dict(fill=fill, shadow=shadow, glyphs=glyphs, keep=keep, letters=letters, d=d)


# =============================================================================
# frame
# =============================================================================
def _d2(f: C.Frag) -> C.Frag:
    return f + f.mirror_x(PCX) + f.mirror_y(PCY) + f.mirror_x(PCX).mirror_y(PCY)


def roundels():
    return _d2(M.vent_roundel(*ROUNDEL_C, ROUNDEL_D, inner_d=16.0, ribs=12, color=FOIL))


def medallions():
    m = M.reed_node_medallion((COMPANION + BAND_X) / 2, PCY, MED_D, rot=90, color=FOIL)
    return m + m.mirror_x(PCX)


def frame_rules(medallion=True):
    rz = roundels()
    mz = medallions()
    out = C.Frag()
    for inset, w in ((OUTER, RULE), (COMPANION, FINE), (None, FINE)):
        if inset is None:
            x0, y0, x1, y1 = BAND_X, BAND_Y, PW - BAND_X, PH - BAND_Y
        else:
            x0, y0, x1, y1 = inset, inset, PW - inset, PH - inset
        g = C.stroke(K.rect_lines(x0, y0, x1, y1), w, style="rule", color=FOIL, role="rule")
        g = C.cut(g, C.region(rz.outline()), RULE_BREAK)
        if medallion and inset != OUTER:
            g = C.cut(g, C.region(mz.outline()), RULE_BREAK)
        out += g
    return K.drop_short(out, 30.0)


def plinth_top():
    sp = PLINTH
    y_base = COMPANION
    h = sp["tread_h"]
    a, b = sp["w_base"] / 2, sp["w_top"] / 2
    y1, y2 = y_base + h, y_base + 2 * h
    pts = [(PCX - a, y_base), (PCX - a, y1), (PCX - b, y1), (PCX - b, y2), (PCX + b, y2), (PCX + b, y1),
           (PCX + a, y1), (PCX + a, y_base)]
    f = C.stroke(C.polyline_d(pts), FINE, style="rule", color=FOIL, role="plinth")
    f += C.stroke(C.polyline_d([(PCX - b, y1), (PCX + b, y1)]), FINE, style="rule", color=FOIL, role="bedding")
    return f


def top_band():
    sp = WAVE
    hook = M.wave_hook(sp["height"], w=FINE)
    wd = hook.meta["wave_width"]
    x_start = PCX + PLINTH["w_base"] / 2 + FINE + sp["clear"]
    rz = roundels().shape().buffer(RULE_BREAK + FINE / 2)
    n = 0
    while True:
        cand = M.running_wave(x_start, x_start + n * sp["pitch"] + wd, BAND_Y, height=sp["height"],
                              pitch=sp["pitch"], flow=1, rule=False, start=x_start, color=FOIL)
        if cand.shape().intersects(rz):
            break
        n += 1
    right = M.running_wave(x_start, x_start + (n - 1) * sp["pitch"] + wd, BAND_Y, height=sp["height"],
                           pitch=sp["pitch"], flow=1, rule=False, start=x_start, color=FOIL)
    return right + right.mirror_x(PCX) + plinth_top()


def side_ladders():
    """Reed ladders in the side bands: rungs every 26 px symmetric about the
    panel's mid-height, a node ellipse on every 4th rung counted from the
    medallion, stopping clear of the corner roundels."""
    x0, x1 = COMPANION, BAND_X
    xc = (x0 + x1) / 2
    hw = (x1 - x0) / 2
    f = C.Frag()
    rz = roundels().shape()
    mz = medallions().shape()
    k = 1
    while True:
        y = PCY - 26.0 * k
        if y < 0:
            break
        if k % 4 == 2:
            g = C.stroke(G.ellipse_d(xc, y, hw, 4.5, 0.0), FINE, color=FOIL, role="node")
        else:
            g = C.stroke(C.polyline_d([(x0, y), (x1, y)]), FINE, style="rule", color=FOIL, role="rung")
        sh = g.shape()
        if sh.distance(rz) < GAP:
            break
        if sh.distance(mz) >= GAP:
            f += g
        k += 1
    f = f + f.mirror_y(PCY)
    return f + f.mirror_x(PCX)


def post_caps(lintel):
    """y of the two reed-node capitals that end each side post above and
    below the lintel (the wordmark + its shadow), 4.2 px clear of it."""
    band = shapely.union_all([box(COMPANION, 0, BAND_X + FINE, PH), box(PW - BAND_X - FINE, 0, PW - COMPANION, PH)])
    hit = lintel.buffer(GAP + FINE / 2).intersection(band)
    if hit.is_empty:
        return None
    _, y0, _, y1 = hit.bounds
    r = MED_D / 2 + FINE / 2
    return (y0 - r - 1.0, y1 + r + 1.0)


def frame(lintel=None):
    """{name: Frag}.  With ``lintel`` (shapely: the wordmark + shadow) the
    side posts (the reed ladders and the band's inner rule) stop at reed-node
    capitals above and below it: the wordmark rests on the posts as a
    gateway lintel.  The outer RULE and the FINE companion run on unbroken."""
    tb = top_band()
    parts = dict(rules=frame_rules(), roundels=roundels(), bands=tb + tb.mirror_y(PCY), ladders=side_ladders(),
                 medallions=medallions())
    caps = post_caps(lintel) if lintel is not None else None
    if caps:
        y0, y1 = caps
        xc = (COMPANION + BAND_X) / 2
        cf = C.Frag()
        for y in (y0, y1):
            cf += M.reed_node_medallion(xc, y, MED_D, rot=90, color=FOIL)
        cf = cf + cf.mirror_x(PCX)
        capz = C.region(cf.outline())
        gapz = shapely.union_all([box(COMPANION + FINE / 2 + 0.3, y0, BAND_X + FINE, y1),
                                  box(PW - BAND_X - FINE, y0, PW - COMPANION - FINE / 2 - 0.3, y1)])
        # whole rungs / nodes only: an element touching the lintel zone or crowding a capital is left out
        # (never a half node)
        keep = []
        for m in parts["ladders"].marks:
            sh = C.Frag([m]).shape()
            if sh.intersects(gapz) or sh.distance(capz) < GAP:
                continue
            keep.append(m)
        parts["ladders"] = C.Frag(keep, parts["ladders"].meta)
        r = parts["rules"]
        keep_ = r.select(lambda m: m.w == RULE)
        inner = r.select(lambda m: m.w != RULE)
        cut_zone = shapely.union_all([box(BAND_X - 2, y0, BAND_X + 2, y1), box(PW - BAND_X - 2, y0, PW - BAND_X + 2, y1)])
        inner = C.cut(C.occlude(inner, cut_zone), capz, RULE_BREAK)
        parts["rules"] = keep_ + K.drop_short(inner, 6.0)
        parts["caps"] = cf
    return parts


def _mark_x(m):
    """x of a vertical rule mark (nan otherwise)."""
    pts = [p for p, _ in G.flatten(m.d, 0.2)]
    if len(pts) == 1 and len(pts[0]) >= 2 and np.ptp(pts[0][:, 0]) < 0.01:
        return float(pts[0][0, 0])
    return float("nan")


KEY = dict(y=110.0, R=24.0)


def keystone():
    """A reduced Source Rosette (§G.1, D2 variant: straight ribs) hanging under
    the top band's plinth — the keystone of the gateway, the Source."""
    return M.source_rosette(PCX, KEY["y"], KEY["R"], twist=False, color=FOIL)


# =============================================================================
# type
# =============================================================================
def micro_line(text, cap, baseline, tracking, *, rules=True, font=K.FONT_MICRO):
    f, bb = K.type_fill(text, cap, baseline, tracking, PCX, font=font)
    if rules:
        f += K.em_rules(bb, cap)
    return f, bb


# =============================================================================
# wreath + ribbon
# =============================================================================
WREATH = dict(offset=24.0, frac=0.66, pitch=44.0, first=36.0, leaf_len=None, ratio=11.0, angle=22.0,
              bend=(12.0, -5.0), spike_len=46.0, knot=False, knot_dy=0.0)


def lens_wreath_path(geo, offset, frac, knot_y):
    """One branch (the right): from the knot below the lens tip, up the lens's
    right arc offset ``offset`` px outward, for ``frac`` of its height."""
    R = geo["R"]
    c = np.array(geo["c_left"], float)            # the RIGHT arc is centred on the left
    top, bot, cx = geo["top"], geo["bottom"], geo["cx"]
    a_bot = math.degrees(math.atan2(bot - c[1], cx - c[0]))
    y_end = bot - frac * (bot - top)
    a_end = math.degrees(math.asin((y_end - c[1]) / (R + offset)))
    angs = np.linspace(a_bot, a_end, 300)
    pts = np.column_stack([c[0] + (R + offset) * np.cos(np.radians(angs)),
                           c[1] + (R + offset) * np.sin(np.radians(angs))])
    pts = pts[pts[:, 0] > cx + 8]
    knot = np.array([cx, knot_y])
    # a smooth lead from the knot into the arc
    a = pts[0]
    t = pts[1] - pts[0]
    t /= np.hypot(*t)
    mid = knot + (a - knot) * 0.5 + np.array([6.0, 4.0])
    lead = np.array([knot, mid, a])
    from deck.motifs.forms import arc_spline
    _, L, _ = arc_spline([knot, a], 0.0, math.degrees(math.atan2(t[1], t[0])))
    return np.vstack([L[:-1], pts])


def wreath(geo):
    w = WREATH
    P = lens_wreath_path(geo, w["offset"], w["frac"], RIBBON_Y + w.get("knot_dy", 0.0))
    kw = dict(axis=PCX, pitch=w["pitch"], first=w["first"], ratio=w["ratio"], angle=w["angle"], bend=w["bend"],
              spike_len=w["spike_len"], knot=w.get("knot", False), color=FOIL)
    if w.get("leaf_len"):
        kw["leaf_len"] = w["leaf_len"]
    f = RI.rice_wreath(P, **kw)
    # foil cannot hold a 2 px counter inside a 14 px spikelet: the florets are stamped as SOLID
    # grains (small solids are the one gold-fill exception, style.md rule 14)
    from dataclasses import replace
    out = []
    for m in f.marks:
        if m.role == "spikelet" and m.kind == "stroke":
            out.append(replace(m, d=G.from_skia(m.skia()), kind="fill", w=FINE))
        else:
            out.append(m)
    return C.Frag(out, f.meta)


RIB = dict(half=108.0, h=30.0, drop=13.0, tail=56.0, notch=12.0, fold=17.0, cap=12.0, track=250.0)


def ribbon():
    """Level swallowtail ribbon centred on (PCX, RIBBON_Y): the face with the
    motto, the fold (the ribbon's reverse, hatched) and the swallowtail tails
    behind.  → (Frag, face polygon, silhouette polygon)."""
    hx, h, dr, tl, nt, fo = RIB["half"], RIB["h"], RIB["drop"], RIB["tail"], RIB["notch"], RIB["fold"]
    y0, y1 = RIBBON_Y - h / 2, RIBBON_Y + h / 2
    x0, x1 = PCX - hx, PCX + hx
    face = box(x0, y0, x1, y1)
    f = C.Frag()
    f += C.stroke(C.polyline_d([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True), FINE, style="rule",
                  color=FOIL, role="ribbon")
    sil = [face]
    for s in (1, -1):
        xe = PCX + s * hx
        xi = xe - s * fo
        xo = xe + s * tl
        ty0, ty1 = y0 + dr, y1 + dr
        tail_pts = [(xe, ty0), (xo, ty0), (xo - s * nt, (ty0 + ty1) / 2), (xo, ty1), (xi, ty1)]
        f += C.stroke(C.polyline_d(tail_pts), FINE, style="point", color=FOIL, role="ribbon")
        tri = Polygon([(xe, y1), (xi, y1), (xi, ty1)])
        f += C.stroke(C.polyline_d([(xe, y1), (xi, ty1)]), FINE, style="rule", color=FOIL, role="ribbon")
        f += C.hatch(tri, -45.0 if s > 0 else -135.0, 7.0, color=FOIL, min_len=2.5)
        sil.append(Polygon([(xe, ty0), (xo, ty0), (xo - s * nt, (ty0 + ty1) / 2), (xo, ty1), (xi, ty1), (xi, y1),
                            (xe, y1)]).buffer(0))
    t, bb = K.type_fill(MOTTO, RIB["cap"], RIBBON_Y + RIB["cap"] / 2, RIB["track"], PCX)
    f += t
    return f, face, shapely.union_all(sil)


# =============================================================================
# foot band
# =============================================================================
FOOT = dict(u=32.0, pitch=64.0, rule_dy=28.0, rule_half=210.0, dot=6.3)


def foot_band():
    u, p = FOOT["u"], FOOT["pitch"]
    f = C.Frag()
    xs = [PCX + (i - 1.5) * p for i in range(4)]
    for s_, x in zip("SHCD", xs):
        d = PIPS.pip_d(s_, u, x, FOOT_Y)
        f += C.stroke(d, FINE, style="point", color=FOIL, role="pip")
    for i in range(3):
        x = (xs[i] + xs[i + 1]) / 2
        f += C.dot(x, FOOT_Y, FOOT["dot"], color=FOIL, role="bubble")
    # beyond the outer pips: bubble beading rising outward (§G.9, ×1.2)
    for s_ in (1, -1):
        x_in = PCX + s_ * (1.5 * p + u * 0.5 + 14)
        x_out = PCX + s_ * (FOOT["rule_half"] - 8)
        f += M.bubble_beading((x_in, FOOT_Y), (x_out, FOOT_Y), 4.2, n=3, color=FOIL)
    for dy in (-FOOT["rule_dy"], FOOT["rule_dy"]):
        y = FOOT_Y + dy
        f += C.stroke(C.polyline_d([(PCX - FOOT["rule_half"], y), (PCX + FOOT["rule_half"], y)]), FINE,
                      style="rule", color=FOIL, role="rule")
        f += C.terminal(PCX - FOOT["rule_half"], y, color=FOIL) + C.terminal(PCX + FOOT["rule_half"], y, color=FOIL)
    return f


# =============================================================================
# lens field
# =============================================================================
FIELD = dict(count=6, pitch=11.0, solid=2, dash_reach=(150.0, 300.0))


def field(geo, avoid):
    m = FINE / 2 + GAP + HAIR / 2
    zone = box(BAND_X + m, SUB_Y + 16, PW - BAND_X - m, RIBBON_Y)
    zone = zone.difference(avoid.buffer(GAP + HAIR / 2 + FINE / 2))
    corners = [(BAND_X, SUB_Y), (PW - BAND_X, SUB_Y), (BAND_X, FOOT_Y), (PW - BAND_X, FOOT_Y)]
    return M.lens_field(geo, count=FIELD["count"], pitch=FIELD["pitch"], clip_to=zone, corners=corners,
                        solid=FIELD["solid"], dash_reach=FIELD["dash_reach"], color=FOIL)


# =============================================================================
# assembly
# =============================================================================
def build():
    """→ dict(foil=Frag, emboss=[(d, level)], parts={...})."""
    geo = lens_geo()
    wm = wordmark()
    fr = frame(lintel=wm["keep"].buffer(0.0))
    kick, kbb = micro_line(KICKER, 14.0, KICKER_Y, 250.0)
    sub, sbb = micro_line(SUBLINE, 14.0, SUB_Y, 220.0)
    place, pbb = micro_line(PLACE, 16.0, PLACE_Y, 250.0)
    lens = M.lens_cartouche(geo, inner=6.6, color=FOIL)
    lion = LION.lion_andante(*LENS_C)
    wr = wreath(geo)
    rib, rib_face, rib_sil = ribbon()
    # the wreath lies over the lens rule (the rule breaks 4.2 round the leaves); the ribbon lies
    # over the wreath stems (they end on its outline)
    lens = C.cut(lens, wr.shape(), GAP)
    wr = C.occlude(wr, rib_sil)
    foot = foot_band()
    avoid = shapely.union_all([C.region(M._lens_d(geo, 0.0)[0]), wr.shape(), rib_sil])
    fld = field(geo, avoid)
    foil = C.Frag()
    for k in ("rules", "roundels", "bands", "ladders", "medallions", "caps"):
        if k in fr:
            foil += fr[k]
    foil += keystone()
    orn = K.enforce_gaps(K.heal(fld + lens + wr + rib + foot))
    foil += kick + wm["fill"] + wm["shadow"] + sub + orn + lion + place
    foil = K.plug(foil)
    lens_in = C.region(M._lens_d(geo, -6.6 - FINE / 2)[0])
    emb = [(G.from_shape(wm["glyphs"].buffer(0.6)), 1), (G.from_shape(lens_in), 1),
           (G.from_shape(lion.meta["silhouette"].buffer(1.0)), 2), (G.from_shape(rib_sil.buffer(0.6)), 1)]
    parts = dict(wordmark=wm, frame=fr, lens=lens, lion=lion, wreath=wr, ribbon=rib, foot=foot, kicker=kick,
                 subline=sub, place=place, rib_sil=rib_sil, lens_in=lens_in, field=fld)
    return dict(foil=foil, emboss=emb, parts=parts)


def svg(res=None):
    res = res or build()
    notes = ["HEADWATERS tuck FRONT panel, 769 x 1069 px @300 ppi (2.5625 x 3.5625 in), y down.",
             "Plates: board = Deep Hole stock (not printed); emboss = blind-emboss tooling (non-printing,",
             "level 1 plateau / level 2 sculpt); foil = ONE gold foil, flat Lion Gold #B08D57. All type outlined."]
    return K.svg_doc(PW, PH, emboss=res["emboss"], foil=K.foil_svg(res["foil"]), title="HEADWATERS tuck front",
                     notes=notes)


def _dev():
    res = build()
    p = K.write(K.DEV / "front.svg", svg(res))
    s = K.svg_doc(PW, PH, emboss=[], foil=K.foil_svg(res["foil"]))
    p2 = K.write(K.DEV / "front-print.svg", s)
    K.render(p2, K.DEV / "front-print-1x.png", 769)
    K.render(p2, K.DEV / "front-print-3x.png", 769 * 3)
    K.render(p2, K.DEV / "front-print-small.png", 192)
    print("check", C.check(res["foil"])[:5])


if __name__ == "__main__":
    _dev()
