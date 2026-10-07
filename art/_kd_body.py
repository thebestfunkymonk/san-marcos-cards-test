"""art/_kd_body.py — K♦ regalia (brief §H.10): the spur rowel, the Key of the Ford and the
tooled-scroll sprig that dresses the gauntlet cuffs. The garments are in ``_kd_garments``.

* ``rowel``         a spur rowel (§G.22) as ONE gold solid — eight sharp kite
                    points round a core, a paper AXLE HOLE at the hub — with an
                    Aquifer contour (legal on any ground, §C.4);
* ``key_of_ford``   the Key of the Ford (§H.10): a gold ring BOW holding an
                    8-point rowel star (split points, one half hatched, a red
                    hub), a bead collar, a plain stem with collars, and a
                    FAULT-STEP BIT (its outer edge broken by one right-angle
                    step, §G.10) cut with one ward, the lower tread half-hatched;
* ``gauntlet``      a gold cuff carrying ONE unit of TOOLED SCROLL (§G.31: ♦
                    cuffs only; the J♦ cuff sprig: stem, eye volute, leaf).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C

FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR
GOLD, RED, INK, JADE = K.GOLD, K.RED, K.INK, K.JADE


# ---------------------------------------------------------------------------
# the spur rowel (gold solid, Aquifer contour, paper axle hole)
# ---------------------------------------------------------------------------
def rowel_solid(c, r_out, *, points=8, core=None, waist=None, rot=-90.0):
    """An ``points``-point spur rowel as ONE solid silhouette (no hole): a
    core disc and kite points (base inside the core, widest at ``waist`` =
    (radius, width), sharp tip at r_out)."""
    c = K.P(c)
    core = r_out * 0.47 if core is None else core
    wr, ww = waist if waist is not None else (r_out * 0.55, r_out * 0.44)
    parts = [Point(*c).buffer(core, quad_segs=24)]
    for k in range(points):
        a = math.radians(rot + 360.0 * k / points)
        u = np.array([math.cos(a), math.sin(a)])
        v = np.array([-u[1], u[0]])
        p_in = c + u * core * 0.3
        pm = c + u * wr
        parts.append(Polygon([tuple(p_in), tuple(pm + v * ww / 2), tuple(c + u * r_out), tuple(pm - v * ww / 2)]))
    g = shapely.union_all(parts).buffer(0)
    return Polygon(g.exterior) if g.geom_type == "Polygon" else Polygon(max(g.geoms, key=lambda q: q.area).exterior)


def rowel(c, r_out, *, hole=6.4, rot=-90.0, key="rowel") -> tuple:
    """A gold spur rowel with a paper axle hole: (silhouette, Frag). The hole
    is a hole in the gold (paper, never paint), ringed FINE."""
    sil = rowel_solid(c, r_out, rot=rot)
    hole_g = Point(*K.P(c)).buffer(hole / 2, quad_segs=24)
    f = K.fill(sil.difference(hole_g), GOLD, role="rowel") + K.outline(sil, FINE, role="rowel")
    f += C.stroke(C.circle_d(c[0], c[1], hole / 2), FINE, color=INK, role="rowel")
    return sil, f                                   # not atomic: the jade under it is cut to match


# ---------------------------------------------------------------------------
# the Key of the Ford
# ---------------------------------------------------------------------------
def key_of_ford(x=552.0, bow_c=(552.0, 122.0), *, ring_r=(37.0, 27.5), star_r=21.0, core_r=8.0, core_d=6.3,
                star_w=11.0, sliver=0.6,
                stem_hw=8.0, stem_bottom=505.0, collars=(172.0, 246.0, 320.0, 424.0), collar_hw=12.5,
                collar_h=7.4, bit=(436.0, 470.0, 497.0), bit_out=(34.0, 22.0), ward=(454.0, 5.2, 14.0),
                field_color=RED, color=GOLD, stones=(), stone=(13.0, 7.0)) -> K.Part:
    """The Key of the Ford (§H.10): its BOW is a gold ring holding an
    8-point ROWEL STAR (§G.22: each point split on its axis, one half
    hatched; a Gill Red hub) — the paper round the star is one open field
    — a bead collar, a plain stem with bead collars, and a FAULT-STEP BIT
    at the stem's foot: its outer edge broken by one right-angle step
    (§G.10), one ward slot cut into the upper tread, the lower tread
    half-hatched. ``bit`` = (top, step, bottom) y; ``bit_out`` = the two
    treads' reach past the stem; ``ward`` = (y, height, depth)."""
    bc = K.P(bow_c)
    ro, ri = ring_r
    ring_out = Point(*bc).buffer(ro, quad_segs=48)
    ring_in = Point(*bc).buffer(ri, quad_segs=48)
    # §G.22 rowel star: a hub circle and 8 lozenge points, each split on its
    # axis with ONE half hatched (the same side on every point: C8)
    hub_r = core_r
    lozs, axes = [], []
    widest, width = 0.40, star_w
    for k in range(8):
        a_ = -90.0 + 45.0 * k
        u = np.array([math.cos(math.radians(a_)), math.sin(math.radians(a_))])
        v = np.array([-u[1], u[0]])
        p_in, p_out = bc + u * hub_r, bc + u * star_r
        pm = p_in + (p_out - p_in) * widest
        lozs.append(Polygon([tuple(p_in), tuple(pm + v * width / 2), tuple(p_out), tuple(pm - v * width / 2)]))
        axes.append((p_in, p_out, v))
    star = K.U(Point(*bc).buffer(hub_r, quad_segs=32), *lozs).buffer(0)
    stem = K.box(x - stem_hw, bc[1] + ri, x + stem_hw, stem_bottom - 2.0)
    tip = Point(x, stem_bottom - 2.0).buffer(stem_hw, quad_segs=16)
    cols = [K.R(K.rrect(x - collar_hw, y - collar_h / 2, x + collar_hw, y + collar_h / 2, 3.0)) for y in collars]
    yt, ys, yb = bit
    xo1, xo2 = x + stem_hw + bit_out[0], x + stem_hw + bit_out[1]
    bit_p = Polygon([(x - stem_hw, yt), (xo1, yt), (xo1, ys), (xo2, ys), (xo2, yb), (x - stem_hw, yb)])
    wy, wh, wd = ward
    ward_g = K.box(xo1 - wd, wy - wh / 2, xo1 + 5.0, wy + wh / 2)
    bit_p = bit_p.difference(ward_g)
    body = K.U(stem, tip, bit_p, *cols)
    field = ring_in.difference(star)
    # slivers of the field in the V's between the points by the hub (< 3.2 px) join the star
    field_ok = field.buffer(-sliver, join_style=2).buffer(sliver, join_style=2).intersection(field)
    field_ok = (shapely.union_all([g for g in K._polys_of(field_ok) if g.area > 25.0])
                if not field_ok.is_empty else field_ok)
    star = K.U(star, field.difference(field_ok.buffer(0.01))).buffer(0)
    field = field_ok
    shape = K.U(ring_out, body)
    gold = K.U(ring_out.difference(ring_in), star, body)
    hub = Point(*bc).buffer(core_d / 2, quad_segs=24)
    fills = K.fill(gold.difference(hub.buffer(-0.01)), color) + K.fill(hub, RED)
    if field_color:
        fills += K.fill(field, field_color)              # enamel round the star (gold on red: a contoured solid)
    lines = C.Frag()
    lines += K.outline(ring_in)
    lines += K.outline(star, FINE, role="star")          # the motif's own monoline (§G.22)
    for (p_in, p_out, v), lz in zip(axes, lozs):
        lines += K.seg(p_in, p_out, FINE, role="axis")
        half = C.split_region(lz, [tuple(p_in), tuple(p_out)], side=-1)
        ax_deg = math.degrees(math.atan2(p_out[1] - p_in[1], p_out[0] - p_in[0]))
        lines += K.hatch_in(half, angle=ax_deg + 90.0)
    lines += K.clip_out(K.outline(K.U(stem, tip, bit_p)), K.U(ring_out, *cols), eps=-0.5, trap=0.0)
    for cd in cols:
        lines += K.outline(cd)
    lower = K.box(x + stem_hw, ys, xo2, yb)
    lines += K.seg((x + stem_hw, ys), (xo2, ys), MEDIUM, role="bit-joint")
    lines += K.seg((x + stem_hw, yt), (x + stem_hw, yb), MEDIUM, role="bit-root")
    lines += K.hatch_in(lower, angle=-45.0)
    for ys in stones:                                    # ford stones set in the stem (solid Aquifer)
        lines += K.fill(C.lozenge_d(x, ys, stone[0], stone[1], 90.0), INK, role="stone")
    return K.Part(shape, fills, lines, {"star": star, "bit": bit_p, "ring": ring_out, "field": field})


# ---------------------------------------------------------------------------
# gauntlet cuff with one unit of tooled scroll (the J♦ cuff sprig)
# ---------------------------------------------------------------------------
def scroll_unit(x_first=4.5, yc=0.5, *, r0=8.4, q=7.0, flat=2.5, leaf=(14.0, 5.6), pet=0.9, lead_x=-40.0, tail=40.0,
                keep=None, w=FINE, free=False) -> C.Frag:
    """ONE unit of §G.31 tooled scroll (the J♦ belt's running scroll, n = 1 —
    the House of the Ford's cuff sprig), in a local frame (x across, y down):
    a stem along a base line ``q`` px below the volute's centre line ``yc``
    rises in a CCW quarter (radius ``q``) to the volute's left foot, rolls
    over it in a CW half circle (radius ``r0``, centre x ``x_first``) and at
    its right foot FORKS: the eye half turn (r0/2) curls back to the centre
    into a Ø6.3 terminal, while a CCW quarter carries the stem back down to
    the base line and on ``tail`` px. One vesica leaf (``leaf`` = (length,
    width)) stands upright before the volute, sessile in the stem when
    ``pet`` < FINE. The stem starts at ``lead_x``: both ends run out under
    the cuff's sides. ``free``: a self-contained sprig instead — the stem
    springs from the leaf's foot and runs on over the volute straight into
    its eye (no fork, no ends at the cuff's edges, so nothing beyond the
    cuff can crowd them). The leaf is atomic, kept only inside ``keep``."""
    yb = yc + q
    xm = x_first - r0 - q - flat / 2
    f = C.Frag()
    if free:
        t = C.Turtle(xm, yb, 0.0)
        t.line_to(x_first - r0 - q, yb)
        t.arc(q, -90.0)                                # up to the left foot
        t.arc(r0, 180.0)                               # over the volute (CW)
        t.arc(r0 / 2, 180.0)                           # and on into the eye
        f += K.dot(t.pos, K.TD, role="terminal")
        f = C.stroke(t.d(), w, role="stem") + f
    else:
        t = C.Turtle(lead_x, yb, 0.0)
        t.line_to(x_first - r0 - q, yb)
        t.arc(q, -90.0)                                # up to the left foot
        t.arc(r0, 180.0)                               # over the volute (CW)
        e = C.Turtle(*t.pos, 90.0)
        e.arc(r0 / 2, 180.0)                           # the eye half turn back to the centre
        f += C.stroke(e.d(), w, role="volute")
        f += K.dot(e.pos, K.TD, role="terminal")
        t.arc(q, -90.0)                                # down to the base line (CCW)
        t.fd(tail)
        f = C.stroke(t.d(), w, role="stem") + f
    Lf, Wf = leaf
    b = K.P(xm, yb)
    p0 = b + K.P(0.0, -pet)
    p1 = p0 + K.P(0.0, -Lf)
    lf = C.stroke(C.polyline_d([b, p0]), w, role="petiole") if pet > w else C.Frag()
    lf += C.stroke(C.vesica_d(p0, p1, Wf), w, style="point", role="leaf")
    if keep is None or K.R(keep).contains(lf.shape()):
        f += K.atomic(lf, "cuffleaf")
    return f


def gauntlet(W, u, *, width=36.0, flare=46.0, depth=36.0, color=GOLD, mirror=False, top_sag=-2.5,
             bottom_sag=3.5, sprig=None, gap=K.GAP_MARK, sprig_rot=0.0, keep_in=None) -> K.Part:
    """A flared gold gauntlet cuff from the wrist W (top edge, across the
    arm) back down the arm (direction −u) ``depth`` px, widening to
    ``flare``; ONE unit of §G.31 tooled scroll across its middle
    (``scroll_unit``; ``sprig`` = its kwargs, x across the cuff, y down the
    arm from the cuff's middle): the stem runs in under one side and out
    under the other; the leaf is kept only ≥ ``gap`` px clear inside every
    edge. ``mirror`` flips the unit for the other arm; ``sprig_rot`` turns
    it (screen degrees, about the cuff's middle) so a pair of cuffs on arms
    at different angles carry the unit the same way up (on a steep diagonal
    cuff the unit, drawn across the arm, reads as a letter S). ``keep_in``: a
    screen region the unit must stay inside (the part of a cuff left visible
    when an attribute in front cuts it)."""
    W, u = K.P(W), np.asarray(u, float) / np.hypot(*u)
    nrm = np.array([u[1], -u[0]])
    a0, a1 = W + nrm * width / 2, W - nrm * width / 2
    B = W - u * depth
    b0, b1 = B + nrm * flare / 2, B - nrm * flare / 2
    d = K.Path(a0).sag(a1, top_sag).line(b1).sag(b0, bottom_sag).close().d
    reg = K.R(d)
    lines = K.outline(reg)
    ex, ey = -nrm, -u
    C0 = W - u * depth * 0.5
    loc = shapely.transform(reg, lambda xy: np.column_stack([(xy - C0) @ ex, (xy - C0) @ ey]))
    if mirror:
        loc = shapely.transform(loc, lambda xy: xy * np.array([-1.0, 1.0]))
    kw = dict(sprig or {})
    L = max(width, flare)
    kw.setdefault("lead_x", -L)
    kw.setdefault("tail", L)
    keep = loc.buffer(-(MEDIUM / 2 + gap + FINE / 2 + 0.3))
    if keep_in is not None:
        vis = shapely.transform(K.R(keep_in).intersection(reg),
                                lambda xy: np.column_stack([(xy - C0) @ ex, (xy - C0) @ ey]))
        if mirror:
            vis = shapely.transform(vis, lambda xy: xy * np.array([-1.0, 1.0]))
        keep = keep.intersection(vis.buffer(-(gap + FINE / 2 + 0.3)))
    if sprig_rot:
        keep = shapely.affinity.rotate(keep, sprig_rot if mirror else -sprig_rot, origin=(0.0, 0.0))
    sc = scroll_unit(keep=keep, **kw)
    if mirror:
        sc = sc.mirror_x(0.0)
    ang = math.degrees(math.atan2(-nrm[1], -nrm[0]))
    sc = sc.rotate(ang + sprig_rot).translate(C0[0], C0[1])
    lines += K.clip_in(sc, reg.buffer(-0.2))
    return K.Part(reg, K.fill(reg, color), lines, {"local": loc})
