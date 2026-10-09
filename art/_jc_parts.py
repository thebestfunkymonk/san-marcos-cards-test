"""art/_jc_parts.py — J♣ · The River Squire: the parts the kit does not have.

Built only from deck.courtkit / deck.motifs primitives (compass arcs, G1 arc
splines, vesicas, legal strokes), at final size, in card px (top half).
Every builder returns a courtkit Part (shape, fills, lines, meta).
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM

P = K.P
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR








def pts_of(d, step=0.4):
    return C.sample_d(d, step)[0][0]








# ---------------------------------------------------------------------------
# the near ear (a paper C joined to the cheek, its inner curl)
# ---------------------------------------------------------------------------
def ear(fc, *, c=(431.0, 226.0), rx=8.5, ry=13.0):
    """The near ear of a 3/4 head: a paper ellipse overlapping the cheek
    contour; only its OUTER edge is drawn (it joins the cheek, no closed
    ring on the face), plus one MEDIUM inner fold (the helix) springing from
    the cheek — a C inside a C."""
    c = P(c)
    reg = shapely.affinity.scale(Point(*c).buffer(1.0, quad_segs=32), rx, ry)
    head = fc.skin
    outer = K.clip_out(K.outline(reg), head.buffer(-0.5), eps=0.0, trap=0.0)
    curl = K.line(K.arc_c(c + P(-0.5, 0.5), 5.2, -75.0, 70.0), MEDIUM, role="ear")
    return K.Part(reg, C.Frag(), outer + curl, {"c": c})














def _leaf_region(mid_d, width):
    """A vesica-profile leaf round a (curved) midrib d."""
    from deck.motifs import forms as FM
    mid = pts_of(mid_d, 0.3)
    _, _, ring = FM.leaf_edges(mid, FM.vesica_hw(K.G.Curve(mid).length, width))
    return Polygon(ring).buffer(0)




def _valve(root, tip, width, bow):
    """One husk valve: a leaf from ``root`` to ``tip`` whose midrib bows
    ``bow`` px to the screen-left of travel (recurved), ``width`` wide."""
    root, tip = P(root), P(tip)
    mid = (root + tip) / 2 + K.left_normal(root, tip) * bow
    d = K.spline([root, mid, tip])
    return _leaf_region(d, width), pts_of(d, 0.3)


def pecan_husk(c, *, style="A", s=1.0):
    """The buckle (§H.9): a gold pecan husk splitting open. The NUT (a
    pointed ovoid, one half hatched — the dark-streaked shell) stands in
    the middle; the husk's VALVES (four, split along their sutures) peel
    back round it, each half-hatched on its inner half. Solid gold with an
    Aquifer contour (legal on red, §C.4).

    style A: nut upright, the side valves and the front valve recurved down
             and out round its foot (the husk after it opens);
    style B: nut in the husk's cup, the side valves spreading up and out,
             their tips curling back;
    style C: seen from the apex: four valves as an X round the nut."""
    c = P(c)
    k = s
    parts, hatch_regs = [], []
    if style == "D":
        # the four valves spread in an X behind a nut lying along the belt
        nut = K.R(K.vesica(c + P(-24 * k, 0), c + P(22 * k, 0), 21 * k)).buffer(2.5 * k).buffer(-2.5 * k)
        for ang_, bow in ((-126.0, -4.0), (-54.0, 4.0), (54.0, -4.0), (126.0, 4.0)):
            reg, mp = _valve(c + K.unit(ang_) * 2 * k, c + K.unit(ang_) * 31 * k, 17 * k, bow * k)
            parts.append((reg, mp))
    elif style == "C":
        nut = K.R(K.vesica(c + P(0, -16 * k), c + P(0, 16 * k), 17 * k))
        for ang_ in (-135.0, -45.0, 45.0, 135.0):
            reg, mp = _valve(c + K.unit(ang_) * 6 * k, c + K.unit(ang_) * 27 * k, 13 * k, 3.0 * k)
            parts.append((reg, mp))
    else:
        nut = K.R(K.vesica(c + P(0, -28 * k), c + P(0, 14 * k), 23 * k))
        if style == "A":
            for sg in (-1, 1):
                reg, mp = _valve(c + P(sg * 7 * k, -1 * k), c + P(sg * 28 * k, 17 * k), 16 * k, -sg * 8.0 * k)
                parts.append((reg, mp))
            reg, mp = _valve(c + P(0, 3 * k), c + P(0, 29 * k), 18 * k, 0.0)
            parts.append((reg, mp))
        else:
            cup = K.R(K.Path(c + P(-14 * k, 4 * k)).sag(c + P(14 * k, 4 * k), 11 * k).close().d) if False else None
            for sg in (-1, 1):
                reg, mp = _valve(c + P(sg * 4 * k, 18 * k), c + P(sg * 25 * k, -16 * k), 12.5 * k, sg * 7.0 * k)
                parts.append((reg, mp))
            reg, mp = _valve(c + P(0, 22 * k), c + P(0, 4 * k), 22 * k, 0.0)
            parts.append((reg, mp))
    valves = [r for r, _ in parts]
    shape = K.U(nut, *valves).buffer(1.0, join_style=1).buffer(-1.0, join_style=1)
    vu = K.U(*valves)
    if style == "D":
        lines = K.outline(nut)
        husk = K.U(*[r for r, _ in parts]).buffer(1.0, join_style=1).buffer(-1.0, join_style=1)
        lines += K.clip_out(K.outline(husk), nut, eps=-0.5, trap=0.0)
        for r, mp in parts:
            rib = LineString(mp)
            # one half of each valve hatched, butting onto its rib (the wing ridge)
            side = K.halfplane(mp[0], mp[-1], side=+1)
            wedge = K.halfplane(mp[0], mp[-1], side=+1).intersection(Point(*c).buffer(40.0 * k))
            others = K.U(*[r2 for r2, m2 in parts if m2 is not mp])
            half = r.intersection(wedge).difference(nut).difference(others.difference(r.buffer(-0.01)))
            lines += K.clip_out(K.line(C.polyline_d(mp), MEDIUM, role="valve-rib"), nut, eps=-0.5, trap=0.0)
        # the nut: its suture along the length
        lines += K.seg(c + P(-12 * k, 0.6 * k), c + P(11 * k, 0.6 * k), FINE, role="suture")
        return K.Part(shape, K.fill(shape, GOLD), lines, {"c": c})
    lines = K.clip_out(K.outline(nut), vu, eps=-0.5, trap=0.0)
    for r, _ in parts:
        lines += K.outline(r)
    # the nut: split on its axis, the left half hatched (the streaked shell)
    nut_vis = nut.difference(vu.buffer(0.1))
    ax = K.seg(c + P(0, -27 * k if style != "C" else -16 * k), c + P(0, 13 * k), FINE, role="suture")
    lines += K.clip_in(ax, nut_vis.buffer(-1.0))
    lines += K.hatch_in(nut_vis.intersection(K.box(0, 0, c[0], 2000)), angle=-45.0)
    for r, mp in parts:
        lines += K.clip_in(K.line(C.polyline_d(mp), FINE, role="valve-rib"), r.buffer(-3.5))
    return K.Part(shape, K.fill(shape, GOLD), lines, {"c": c})












# ---------------------------------------------------------------------------
# the river squire's flat cap (follow-up: no Robin-Hood peak): a soft flat
# crown with a half-hatched underside on a rolled brim round the brow; the
# standing collar; the club brooch that pins the heron plume
# ---------------------------------------------------------------------------
def _ell(c, rx, ry, rot=0.0):
    g = shapely.affinity.scale(Point(0.0, 0.0).buffer(1.0, quad_segs=64), rx, ry, origin=(0, 0))
    if rot:
        g = shapely.affinity.rotate(g, rot, origin=(0, 0))
    return shapely.affinity.translate(g, c[0], c[1])


def _ell_arc(c, rx, ry, a0, a1, n=120, rot=0.0):
    """Points on the ellipse (c, rx, ry, rotated ``rot``°) from angle a0 to a1
    (degrees, screen: 90 = the FRONT / lowest point)."""
    t = np.radians(np.linspace(a0, a1, n))
    x, y = rx * np.cos(t), ry * np.sin(t)
    r = math.radians(rot)
    return np.column_stack([c[0] + x * math.cos(r) - y * math.sin(r), c[1] + x * math.sin(r) + y * math.cos(r)])


def bonnet(*, roll_c=(388.0, 176.0), roll_r=(50.0, 7.0), roll_h=14.0, roll_span=(10.0, 170.0),
           crown_c=(398.0, 148.0), crown_r=(68.0, 19.0), crown_rot=5.0, rim_span=0.86, split=True, round_r=0.8):
    """§H.9 'a jade brimmed cap' as the Tudor squire's FLAT CAP (no peak):
    a narrow ROLLED BRIM round the brow — a band ``roll_h`` px deep along
    the front arc of the ellipse ``roll_r`` about ``roll_c`` (angles
    ``roll_span``, round ends: a torus seen in 3/4), split on its middle
    with the lower half hatched (the roll's underside, §B.2) — under a soft,
    wide, flat crown: an ellipse ``crown_r`` about ``crown_c`` tilted
    ``crown_rot``° (down toward the back), its gathered underside falling
    from the rim (± ``rim_span`` of its width) to the roll. The rim's front
    edge is drawn where it overhangs the underside. → Part (meta 'roll',
    'crown', 'rim')."""
    rc = P(roll_c)
    rx, ry = roll_r
    mid = _ell_arc(rc, rx, ry, roll_span[0], roll_span[1])
    roll = LineString(mid).buffer(roll_h / 2, cap_style=1, quad_segs=16)
    top_edge = K.G.Curve(mid).offset(roll_h / 2, spacing=0.5)          # screen-left of right→left travel = up
    if np.mean(top_edge[:, 1]) > np.mean(mid[:, 1]):
        top_edge = K.G.Curve(mid).offset(-roll_h / 2, spacing=0.5)
    cc = P(crown_c)
    disc = _ell(cc, crown_r[0], crown_r[1], crown_rot)
    a = math.degrees(math.acos(rim_span))
    rim = _ell_arc(cc, crown_r[0], crown_r[1], a, 180.0 - a, rot=crown_rot)       # right → front → left
    te = top_edge if top_edge[0][0] < top_edge[-1][0] else top_edge[::-1]          # left → right
    under = Polygon(np.vstack([rim, te])).buffer(0)                                   # rim runs right → left
    tight = K.U(disc, under, roll).buffer(0.8, join_style=1).buffer(-0.8, join_style=1)
    shape = K.U(disc, under, roll).buffer(round_r, join_style=1).buffer(-round_r, join_style=1)
    lines = K.outline(shape)
    inner = shape.buffer(-0.6)
    # the rim's edge over the underside; the roll's top edge against it
    rim_full = _ell_arc(cc, crown_r[0], crown_r[1], 0.0, 180.0, rot=crown_rot)
    lines += K.clip_in(K.line(C.polyline_d(rim_full), MEDIUM, role="cap-rim"), inner.difference(roll.buffer(0.3)))
    lines += K.clip_in(K.outline(roll), inner)
    hatch = C.Frag()
    if split:
        # the crown split by its rim: the gathered underside (in shade) is
        # the hatched half (§B.2), the flat top plain
        # the band as drawn before any corner rounding: hatch run into a rounded-off notch ends against the
        # silhouette in a stub
        uh = tight.difference(disc).difference(roll)
        # where the band pinches out at the brim's end a hatch piece shows only as a stub between the rim
        # and roll lines: keep the pieces with a clear run between them
        seen = uh.buffer(-MEDIUM / 2)
        hatch = C.Frag()
        for m in K.hatch_in(uh, angle=-45.0).marks:
            keep = [pts for pts, _cl in C.sample_d(m.d, 0.3) if LineString(pts).intersection(seen).length >= 5.0]
            if keep:
                hatch += C.Frag([replace(m, d="".join(C.polyline_d(np.asarray(q)) for q in keep))])
    fills = K.fill(shape, JADE)
    return K.Part(shape, fills, lines + hatch, {"roll": roll, "crown": disc, "rim": rim})


def standing_collar(*, top=((344.0, 289.0), (414.0, 286.0)), top_sag=-7.0, foot=((338.0, 314.0), (420.0, 310.0)),
                    foot_sag=-7.0, color=JADE, hem=None):
    """The squire's standing collar: a short cylinder round the neck seen a
    little from above — its top edge an arc dipping ``top_sag`` at the
    front, its foot an arc dipping ``foot_sag`` (hidden edges under the
    jerkin); ``hem`` px under the top a FINE line (the turned edge).
    → Part."""
    (a0, a1), (b0, b1) = [P(p) for p in top], [P(p) for p in foot]
    d = K.Path(a0).sag(a1, top_sag).line(b1).sag(b0, -foot_sag).close().d
    reg = K.R(d).buffer(1.5, join_style=1).buffer(-1.5, join_style=1)
    lines = K.outline(reg)
    if hem:
        hp = pts_of(K.arc_sag(a0 + P(-2, hem), a1 + P(2, hem), top_sag), 0.4)
        lines += K.clip_in(K.line(C.polyline_d(hp), FINE, role="hem"), reg.buffer(-(MEDIUM / 2 + 3.2)))
    return K.Part(reg, K.fill(reg, color), lines, {})


def club_brooch(c, *, r=11.0, u=13.0, dy=0.6, plinth=False):
    """The cap brooch that pins the heron plume (the jacks' suit brooch: J♥
    a heart, J♦ a lozenge): a round GOLD boss (``r``) with an Aquifer
    contour, and the deck's ♣ pip (``u``) set in it in Aquifer (a solid
    accent, §C.3). → Part."""
    from deck import pips as PP
    c = P(c)
    boss = Point(*c).buffer(r, quad_segs=32)
    club = K.R(PP.pip_d("C", u, c[0], c[1] + dy))
    if not plinth:
        # the stem without its foot bar: no narrow gold slots beside the stem
        x0, y0, x1, y1 = club.bounds
        club = club.intersection(K.box(0, 0, 2000, y1 - (y1 - y0) * 0.09))
    fills = K.fill(boss.difference(club), GOLD) + K.fill(club, INK)
    return K.Part(boss, fills, K.outline(boss, MEDIUM), {"club": club})
