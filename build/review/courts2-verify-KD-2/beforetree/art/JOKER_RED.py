"""art/JOKER_RED.py: Big Joker · The Fool (brief §H.17).

A pig volant in a swine dive through a riveted gold porthole ring -- the
Little Joker's sibling: like the grackle he is ONE solid silhouette (here
Gill Red) with his detail knocked out to paper geometrically, half-hatched
tracts and a confident outline (director's pass-2 decision, overriding the
line-only reading of §H.17's "contour MEDIUM, detail FINE").

* The pig (art/_joker_red_pose.py, art/_joker_red_pig.py): a Tamworth-type
  bacon pig -- long level back, deep round barrel, full ham, short jointed
  legs, cloven trotters, a long straight head ending in a flat disc, prick
  ears, a curled tail.  He plunges head-down on a diagonal (body 58 deg at
  mid-barrel, the back one convex arc; the head carried a little higher so the
  face stays in profile), both fore trotters reaching forward under the jaw
  (the near one leading), the hind legs trailing together behind the ham, the
  ears laid back.  Knockouts: eye almond with the Aquifer dot, disc rim + two
  nostrils, mouth, shoulder and ham (thigh) lines, the ear's edge, far-limb
  edges, trotter coronets; the cleft of each trotter is cut in the outline.
  Half-hatched: the ear's inner half and a narrow crescent along the belly.
* The porthole (§H.17): a double circle Ø300 at (375, 330) -- a MEDIUM outer
  rim, a FINE inner rim -- with 16 Ø6.3 rivets between them.  Interlace
  (§B.2, geometric gaps): the ring's rump-side half passes IN FRONT of the
  loin as two wires -- the red solid is cut 4.2 px clear of each gold wire
  only, so the red loin shows between them and the barrel runs on through the
  ring into the ham, hind legs and tail (one pig, not two masses); rivets that
  would land on that red are left out (no gold on red, §C rule 4); the
  snout-side half passes BEHIND the head, collar and forelegs, breaking 4.2 px
  clear of them -- the snout and fore trotters break out below the ring.
* The gold jester collar -- the Fool's crown-collar (redrawn, client
  correction 2026-09-24): a band on an arc across the neck, five equal dags
  on its normals fanning evenly, a whole round bell with a knocked-out mouth
  at each point; it sits in a paper ground that is its own outline offset a
  uniform 4.2 (§C rule 4: no gold on red; no Aquifer contour, since the
  budget keeps Aquifer for the eye).  The ear crosses the band only.
* Water (art/_joker_red_water.py): a bubble trail streaming off the tail's
  curl into a running-wave scroll round the ring's upper right; three
  ripple ellipses marking the water below the head.
* Placement (client correction 2026-09-24, see FIG_SHIFT): the figure is
  drafted about the brief's porthole (375, 330) and moved as one rigid group
  by (+15, +64) -- the porthole now centres on (390, 394) -- so the block
  (figure + the caption lowered by frames.JOKER_DY) is optically centred and
  the figure's mass balances about x 375; the ripples sit on their own at
  (450, 688.5), their lowest ink 50 px above the rule.
* Caption per §F.4 / §J.2: THE FOOL / -- FORTUNE FAVORS THE FOOLHARDY --.

Inks: Gill Red (the pig, title, subline, em-rules), Lion Gold (ring, rivets,
collar, bubbles, scroll, ripples, rule), Aquifer (the eye dot only).
"""
from __future__ import annotations

import importlib
import math

import numpy as np
import shapely
from shapely.geometry import Point

from deck import frames as F
from deck import tokens as T
from deck.cardsvg import layers_merge
from deck.motifs import core as C
from inkkit import geom as G

try:                                    # deck.build imports art.JOKER_RED
    from . import _joker_red_pose as POSE
    from . import _joker_red_pig as PIG
    from . import _joker_red_water as WATER
except ImportError:                     # tools/preview.py loads the file directly
    import _joker_red_pose as POSE
    import _joker_red_pig as PIG
    import _joker_red_water as WATER
POSE = importlib.reload(POSE)
PIG = importlib.reload(PIG)
WATER = importlib.reload(WATER)

RED, GOLD, INK = T.RED, T.FOIL, T.INK
GAP = T.INTERLACE_GAP

# --- the porthole ------------------------------------------------------------------
RING_C = (375.0, 330.0)          # §H.17 porthole centre
RING_R_OUT = 150.0               # Ø 300
RING_R_IN = 127.0
RIVET_R, RIVET_D, N_RIVETS = 138.5, 6.3, 16
RING_W = (T.MEDIUM, T.FINE)      # outer rim, inner rim
STUB_MIN = 24.0                  # ring pieces shorter than this are dropped
CRUMB = 40.0                     # red pieces smaller than this (px²) are dropped after a cut


def ring_parts():
    cx, cy = RING_C
    circles = C.stroke(G.circle_d(cx, cy, RING_R_OUT), RING_W[0], color=GOLD, role="ring") + \
        C.stroke(G.circle_d(cx, cy, RING_R_IN), RING_W[1], color=GOLD, role="ring")
    rivets = [(cx + RIVET_R * math.cos(math.radians(a)), cy + RIVET_R * math.sin(math.radians(a)))
              for a in (360.0 / N_RIVETS * (k + 0.5) for k in range(N_RIVETS))]
    return circles, rivets


def ring_wires():
    """The ring's two gold wires as areas (outer MEDIUM, inner FINE)."""
    cx, cy = RING_C
    out = []
    for r, w in ((RING_R_OUT, RING_W[0]), (RING_R_IN, RING_W[1])):
        out.append(Point(cx, cy).buffer(r + w / 2, quad_segs=64).difference(
            Point(cx, cy).buffer(r - w / 2, quad_segs=64)))
    return shapely.union_all(out)


def half_plane(rump_side: bool):
    """The half of the page on the rump side of the line through the ring
    centre perpendicular to the body axis (the ring passes in front of the
    pig there), or the snout side."""
    u = -POSE.BODY.U                      # toward the rump
    n = np.array([-u[1], u[0]])
    c = np.asarray(RING_C)
    big = 2000.0
    s = 1.0 if rump_side else -1.0
    return shapely.Polygon([c - n * big, c + n * big, c + n * big + s * u * big, c - n * big + s * u * big])


def drop_short(f: C.Frag, min_len: float) -> C.Frag:
    out = []
    for m in f.marks:
        if m.kind != "stroke":
            out.append(m)
            continue
        keep = [pts for pts, _ in G.flatten(m.d, 0.05)
                if len(pts) > 1 and np.sum(np.hypot(*np.diff(pts, axis=0).T)) >= min_len]
        if keep:
            from dataclasses import replace
            out.append(replace(m, d="".join(C.polyline_d(k) for k in keep)))
    return C.Frag(out, f.meta)


# --- placement (client correction 2026-09-24) ------------------------------------
# Everything above is drafted about the brief's porthole at (375, 330).  The
# figure group (pig, porthole, rivets, bubble trail and scroll) is then moved
# as one rigid piece so that, with the caption lowered by frames.JOKER_DY, the
# block (figure + caption) is optically centred (bbox middle ~y 523) and the
# figure's mass balances about x 375 (the red rump sits up-left of the ring);
# the ripples are placed on their own, pulled in toward the axis under the
# head so they no longer overhang the rule's right end, their lowest ink ~50 px
# above the rule (the gap both jokers share).
FIG_SHIFT = (15.0, 64.0)
RIPPLE_C = (450.0, 688.5)        # ripple centre (page px)


# --- caption -------------------------------------------------------------------
COUNTER_MIN = 2.65               # micro-type counters >= 2.5 px (+ AA margin), as on the aces
COUNTER_CLOSE = 2.0              # narrower ones (the cap-12 A) are closed, as the press would


def open_counters(d: str, min_w: float = COUNTER_MIN, close_below: float = COUNTER_CLOSE) -> str:
    """Micro-type print correction for the cap-12 subline (as on the aces and
    the Little Joker): counters between ``close_below`` and ``min_w`` open
    outward by ~0.1 px a side; the A's (1.73 px) is closed, as the press would."""
    s = G.to_shape(d, tol=0.01)
    out = []
    for pg in getattr(s, "geoms", [s]):
        holes = []
        for ring in pg.interiors:
            hole = shapely.Polygon(ring)
            w = 2 * shapely.maximum_inscribed_circle(hole, 0.01).length
            if w < close_below:
                continue
            if w < min_w:
                hole = hole.buffer((min_w - w) / 2 + 0.02, join_style="mitre", mitre_limit=4)
            holes.append(hole)
        pg = shapely.Polygon(pg.exterior)
        for h in holes:
            pg = pg.difference(h)
        out.append(pg)
    return G.from_shape(shapely.union_all(out))


def caption() -> C.Frag:
    t, s = F.JOKER_TITLE, F.JOKER_SUBLINE
    d_t, _ = F.slab_line("THE FOOL", t["cap"], t["baseline"], t["tracking"])
    d_s, bb = F.type_line("FORTUNE FAVORS THE FOOLHARDY", s["cap"], s["baseline"], s["tracking"])
    rules = F.em_rules_d(bb, s["cap"])
    f = C.fill(d_t, color=RED, role="joker-title")
    f += C.fill(open_counters(d_s), color=RED, role="joker-subline")
    f += C.stroke(rules, T.FINE, style="rule", color=RED, role="em-rule")
    return f


# --- build ---------------------------------------------------------------------
def _drop_crumbs(g, min_area=CRUMB):
    parts = [q for q in PIG.polys_of(g) if q.area >= min_area]
    return shapely.union_all(parts) if parts else shapely.Polygon()


def build():
    pig = PIG.build()
    sil = pig["sil"]

    circles, rivets = ring_parts()
    # the ring's rump-side half passes in front of the pig as two wires: the
    # red is cut GAP clear of each wire only, so the barrel runs on through
    # the ring (red between the wires) into the ham
    front = ring_wires().intersection(half_plane(True))
    solid = pig["solid"].difference(front.buffer(GAP, quad_segs=16))
    solid = _drop_crumbs(PIG.clean(solid, envelope=solid.buffer(0.01)))
    red = C.fill(G.from_shape(solid), color=RED, role="pig") + pig["red_lines"]
    red = C.cut(red, front, GAP) if pig["red_lines"] else red
    gold_pig = C.cut(pig["gold"], front, GAP) if pig["gold"] else pig["gold"]
    # the pig lies over the snout-side half
    over = sil.union(pig["collar"]).intersection(half_plane(False))
    ring = drop_short(C.cut(circles, over, GAP), STUB_MIN)
    riv = C.Frag()
    for x, y in rivets:
        # rivets under the head; and no gold rivet on the red barrel where
        # it shows between the wires (§C rule 4)
        if Point(x, y).distance(over) < RIVET_D / 2 + GAP or Point(x, y).distance(sil) < RIVET_D / 2 + GAP:
            continue
        riv += C.dot(x, y, RIVET_D, color=GOLD, role="rivet")

    water = WATER.water(PIG.tail_tip()[0], RING_C, POSE.TAIL_W, tail=PIG.tail_shape())
    # the figure is drafted about the brief's porthole and placed as one
    # rigid group (a translation of the path data); the ripples on their own
    fig = (red + pig["ink"] + gold_pig + ring + riv + water).translate(*FIG_SHIFT)
    art = fig + WATER.ripples(*RIPPLE_C) + caption()
    return layers_merge(art.fragments(), {"gold": F.joker_rule_fragments(GOLD)})
