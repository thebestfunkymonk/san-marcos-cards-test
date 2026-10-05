"""art/_kd_body.py — K♦ garments and regalia (brief §H.10).

* ``tabard``        Gill Red with a RUSTICATED HEM BAND: two courses of long
                    ashlar blocks (§G.20: running bond, 3 px chamfers — the
                    courthouse's rusticated base) knocked out to paper under a
                    cap rule (a red string between two paper joints); plain
                    red above, so it reads as a garment's hem, not a wall;
* ``rowel``         a spur rowel (§G.22) as ONE gold solid — eight sharp kite
                    points round a core, a paper AXLE HOLE at the hub — with an
                    Aquifer contour (legal on any ground, §C.4);
* ``sash``          jade baldric: gold rowels on its axis, a solid Aquifer ford
                    stone (the ♦ divider's lozenge) between each pair;
* ``key_of_ford``   the Key of the Ford (§H.10): a gold ring BOW holding an
                    8-point rowel star (split points, one half hatched, a red
                    hub), a bead collar, a plain stem with collars, and a
                    FAULT-STEP BIT (its outer edge broken by one right-angle
                    step, §G.10) cut with one ward, the lower tread half-hatched;
* ``gauntlet``      a gold cuff carrying ONE unit of TOOLED SCROLL (§G.31: ♦
                    cuffs only; the J♦ cuff sprig: stem, eye volute, leaf);
* ``mantle_chain``  a §G.23 stepping-stone chain run inside the mantle's
                    silhouette (two FINE rules, solid lozenges between);
* ``ford_stones``   a half-drop brocade of small outlined lozenges.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG
from deck import motifs as M

FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR
GOLD, RED, INK, JADE = K.GOLD, K.RED, K.INK, K.JADE


# ---------------------------------------------------------------------------
# tabard
# ---------------------------------------------------------------------------
def tabard(reg, courses, *, bottom=511.0, joint=3.0, chamfer=3.0, cap=(3.0, 6.0), color=RED) -> K.Part:
    """A Gill Red tabard over ``reg`` with a RUSTICATED HEM BAND (§G.20, the
    courthouse's rusticated base): a few courses of LONG ashlar blocks
    standing on the waist (``bottom``), their joints knocked out to paper
    (``joint`` px: holes in the red, never paint) and every block's corners
    chamfered ``chamfer`` px, under a CAP RULE — a red string ``cap[1]`` px
    tall on the top joint, then one more paper joint ``cap[0]`` px (a double
    rule: the base's water table). Above the cap the tabard is plain red: a
    garment with a hem, not a wall.

    ``courses``: bottom-up ((height, (joint x, ...)), ...) — each course's
    height and the x of its vertical joints. The joints are placed by hand
    so that they fall in the open (between the arm, the sash and the
    medallion) or wholly under a front object, never in a sliver beside
    one; the bottom course (the plinth) runs on under the band."""
    reg = K.R(reg)
    x0, _, x1, _ = reg.bounds
    c, h2 = chamfer, joint / 2
    stones = []
    yb = bottom
    for k, (bh, jx) in enumerate(courses):
        yt = yb - bh
        edges = [x0 - 50.0] + [x - h2 for x in sorted(jx)] + [x1 + 50.0]
        starts = [x0 - 50.0] + [x + h2 for x in sorted(jx)]
        for a, b in zip(starts, edges[1:]):
            if k == 0:                                  # the plinth: chamfered on top only, runs under the band
                pts = [(a + c, yt), (b - c, yt), (b, yt + c), (b, yb + 40.0), (a, yb + 40.0), (a, yt + c)]
            else:
                pts = [(a + c, yt), (b - c, yt), (b, yt + c), (b, yb - c), (b - c, yb), (a + c, yb), (a, yb - c),
                       (a, yt + c)]
            stones.append(Polygon(pts))
        yb = yt - joint
    top = yb + joint                                   # top edge of the top course
    string_b = top - joint                             # the red string sits on the top joint
    string_t = string_b - cap[1]
    upper = reg.intersection(K.box(-10, -10, 2000, string_t - cap[0]))
    band = reg.intersection(K.box(-10, string_t, 2000, string_b))
    red = shapely.union_all([upper, band] + stones).intersection(reg)
    return K.Part(reg, K.fill(red, color), K.outline(reg), {"red": red, "base": top, "cap": string_t - cap[0]})


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
# sash
# ---------------------------------------------------------------------------
def sash(p0, p1, width, clip, *, rowel_r=14.0, pitch=60.0, first=44.0, avoid=None, stones=(11.0, 6.4),
         color=JADE, trap=1.6, visible_to=511.0, gather=None) -> K.Part:
    """A jade baldric from p0 toward p1, ``width`` wide, clipped to ``clip``:
    gold rowels (Aquifer contour, paper axle) on its axis every ``pitch``
    px from ``first``, a solid Aquifer ford-stone lozenge half-way between
    each pair. Rowels touching ``avoid`` (a region in front, e.g. the clasp)
    are skipped, and a ford stone the band would cut (below ``visible_to``)
    is left out. The jade is CUT under each rowel (the layer trap).
    ``gather`` = dict(s, depth, span, fold, fold_len): a hand grips the
    sash's −n edge at ``s`` px along it — the edge is drawn in toward the
    fist (``depth`` px, easing out over ± ``span``; below ``s`` it may
    ``hold`` its depth that far before easing out over ``span_lo``) and two MEDIUM tension
    folds leave the grip into the cloth (``fold``° either side of the
    across-sash direction, ``fold_len`` long), so the cloth reads as pulled."""
    p0, p1 = K.P(p0), K.P(p1)
    u = (p1 - p0) / np.hypot(*(p1 - p0))
    n = np.array([u[1], -u[0]])
    L = float(np.hypot(*(p1 - p0)))
    a, b = p0 - u * 200, p1 + u * 200
    band = Polygon([a + n * width / 2, b + n * width / 2, b - n * width / 2, a - n * width / 2])
    folds = C.Frag()
    if gather:
        gs, gd, gw = gather["s"], gather.get("depth", 6.0), gather.get("span", 34.0)
        # below the apex the pull can HOLD (the edge runs on through the fist, drawn in) for ``hold``
        # px and then ease out over ``span_lo`` (default: symmetric)
        hold, gw_lo = gather.get("hold", 0.0), gather.get("span_lo", gw)
        ss = np.linspace(-200.0, L + 200.0, 1400)
        t_ = ss - gs
        t_ = np.where(t_ < 0.0, t_ / gw, np.maximum(t_ - hold, 0.0) / gw_lo)
        bump = np.where(np.abs(t_) < 1.0, np.cos(np.clip(t_, -1, 1) * math.pi / 2) ** 2, 0.0)
        edge = [p0 + u * t - n * (width / 2 - gd * k) for t, k in zip(ss, bump)]
        band = Polygon([tuple(a + n * width / 2), tuple(b + n * width / 2)] + [tuple(q) for q in edge[::-1]])
        g = p0 + u * gs - n * (width / 2 - gd)
        if "creases" in gather:
            # hand-placed creases in sash coordinates about the grip: (ds0, n0, ds1, n1, sag) —
            # ds along the sash from the grip (+ = toward p1), n across from the axis (+ = the +n edge)
            for ds0, n0, ds1, n1, sg in gather["creases"]:
                q0 = p0 + u * (gs + ds0) + n * n0
                q1 = p0 + u * (gs + ds1) + n * n1
                folds += K.line(K.arc_sag(q0, q1, sg), MEDIUM, role="fold")
        else:
            for sgn in (-1.0, 1.0):
                ang_f = math.radians(gather.get("fold", 34.0)) * sgn
                d_ = n * math.cos(ang_f) + u * math.sin(ang_f)
                q0 = g + d_ * gather.get("fold_in", 12.0)
                q1 = g + d_ * (gather.get("fold_in", 12.0) + gather.get("fold_len", 20.0))
                folds += K.line(K.arc_sag(q0, q1, -2.0 * sgn), MEDIUM, role="fold")
    reg = band.intersection(K.R(clip))
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    inner = reg.buffer(-(rowel_r + 4.3))
    ang = math.degrees(math.atan2(u[1], u[0]))
    av = K.R(avoid).buffer(K.GAP_MARK + 2.0) if avoid is not None else None
    rows, marks = [], []
    s_ = first
    while s_ < L + 200:
        c = p0 + u * s_
        if inner.contains(Point(*c)) and (av is None or not av.intersects(Point(*c).buffer(rowel_r))):
            rows.append(rowel(c, rowel_r, rot=ang + 22.5, key=f"srow{int(s_)}"))
            cs = c + u * pitch / 2
            if stones and reg.buffer(-(stones[0] / 2 + 4.3)).contains(Point(*cs)) and (
                    av is None or not av.intersects(Point(*cs).buffer(stones[0]))) and (
                    visible_to is None or cs[1] + stones[0] / 2 + K.GAP_MARK <= visible_to):
                ld = C.lozenge_d(cs[0], cs[1], stones[0], stones[1], ang)
                marks.append((K.R(ld), K.fill(ld, INK, role="stone")))
        s_ += pitch
    jade = reg
    for sil, _ in rows:
        jade = jade.difference(sil.buffer(-trap))
    fills = K.fill(jade, color)
    lines = K.outline(reg)
    for _, f in rows:
        fills += f.select(lambda m: m.layer != "ink")
        lines += f.select(lambda m: m.layer == "ink")
    for _, m in marks:
        lines += m
    if folds:
        # the folds stop ≥ 4.2 px clear of the rowels and the stones, inside the edge
        keep = reg.buffer(-(MEDIUM / 2 + 4.3))
        for sil, _ in rows:
            keep = keep.difference(sil.buffer(4.2 + MEDIUM / 2))
        for r_, _ in marks:
            keep = keep.difference(r_.buffer(4.2 + MEDIUM / 2))
        lines += K.clip_in(folds, keep)
    return K.Part(reg, fills, lines, {"u": u, "n": n})


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


def office_chain(A, Bm, Cc, *, link=(14.0, 8.4), pitch=19.0, bead_d=7.0, color=GOLD) -> K.Part:
    """The Warden's chain of office (the law-giver of the square): gold
    FORD-STONE links (the ♦ divider's lozenges) set tip to tip along the
    compass arc A → Bm → Cc, a round gold bead at every joint; one gold
    silhouette with an Aquifer MEDIUM contour (legal on red, §C.4)."""
    ctr, R = K.circ3(A, Bm, Cc)
    a0, am, a1 = K.ang(ctr, A), K.ang(ctr, Bm), K.ang(ctr, Cc)
    # sweep A → C through B
    def unwrap_to(a, ref):
        while a - ref > 180:
            a -= 360
        while a - ref < -180:
            a += 360
        return a
    am = unwrap_to(am, a0)
    a1 = unwrap_to(a1, am)
    L = abs(math.radians(a1 - a0)) * R
    n = max(1, int(round(L / pitch)))
    parts = []
    for k in range(n + 1):
        t = k / n
        a = a0 + (a1 - a0) * t
        q = K.polar(ctr, R, a)
        parts.append(Point(*q).buffer(bead_d / 2, quad_segs=16))
        if k < n:
            ta = a0 + (a1 - a0) * (k + 0.5) / n
            qm = K.polar(ctr, R, ta)
            tang = ta + (90.0 if a1 > a0 else -90.0)
            parts.append(K.R(C.lozenge_d(qm[0], qm[1], link[0], link[1], tang)))
    g = shapely.union_all(parts).buffer(0.4, quad_segs=6).buffer(-0.4, quad_segs=6)
    return K.Part(g, K.fill(g, color), K.outline(g), {"centre": ctr, "R": R})


# ---------------------------------------------------------------------------
# mantle ornament
# ---------------------------------------------------------------------------
def _offset_path(ext_shape, d, clip):
    """The boundary of ``ext_shape`` inset by ``d``, clipped to ``clip`` → list of point arrays."""
    ring = ext_shape.buffer(-d, quad_segs=16).boundary.intersection(clip)
    return [np.asarray(g.coords) for g in K._lines_of(shapely.line_merge(ring) if ring.geom_type != "LineString"
                                                        else ring) if g.length > 10]


def mantle_chain(shape, ext_shape, *, rules=(20.0, 36.0), stone=(11.0, 6.4), pitch=24.0, clip=None,
                 color=INK, avoid=None, visible_to=511.0) -> C.Frag:
    """§G.23 stepping-stone chain inside the mantle's silhouette: two FINE
    rules at ``rules`` px inside the outline (``ext_shape``: the mantle
    extended below the band, so the chain never runs along the cut), solid
    lozenges on the mid-line every ``pitch`` px (atomic: kept whole; one the
    band would cut — reaching below ``visible_to`` less the §I.12 gap — or
    touching ``avoid`` is left out)."""
    clip = shape if clip is None else clip
    f = C.Frag()
    for d in rules:
        for q in _offset_path(ext_shape, d, clip.buffer(-0.5)):
            f += C.stroke(q, FINE, style="rule", color=color, role="chain")
    mid = (rules[0] + rules[1]) / 2
    room = clip.buffer(-(stone[0] / 2 + 1.0))
    polys = []
    for q in _offset_path(ext_shape, mid, clip):
        ln = LineString(q)
        s = pitch / 2
        k = 0
        while s < ln.length:
            p = ln.interpolate(s)
            p2 = ln.interpolate(min(s + 1.0, ln.length))
            p1 = ln.interpolate(max(s - 1.0, 0.0))
            a = math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))
            ld = C.lozenge_d(p.x, p.y, stone[0], stone[1], a)
            low = K.R(ld).bounds[3] + K.GAP_MARK + K.MEDIUM / 2
            if room.contains(p) and (avoid is None or not K.R(avoid).intersects(p.buffer(stone[0] / 2 + K.GAP_MARK))) \
                    and (visible_to is None or low <= visible_to):
                f += K.fill(ld, color, role="stone")         # not atomic: its jade hole is cut to match
                polys.append(K.R(ld))
            s += pitch
            k += 1
    f.meta["stones"] = polys
    return f


def ford_stones(region, *, pitch=(30.0, 26.0), size=(13.0, 8.0), origin=(375.0, 300.0), color=INK) -> C.Frag:
    """A half-drop grid of small outlined lozenges — the ♦ divider's
    stepping stones strewn as a brocade (FINE Aquifer on the jade, §C.4);
    each stone is atomic (kept whole or dropped), ≥ 4.2 px inside the
    region's edge."""
    reg = K.R(region)
    px, py = pitch
    L, W = size
    inner = reg.buffer(-(L / 2 + FINE / 2 + 4.3))
    x0, y0, x1, y1 = reg.bounds
    ox, oy = origin
    f = C.Frag()
    for j in range(int(math.floor((y0 - oy) / py)) - 1, int(math.ceil((y1 - oy) / py)) + 2):
        off = px / 2 if j % 2 else 0.0
        for i in range(int(math.floor((x0 - ox - off) / px)) - 1, int(math.ceil((x1 - ox - off) / px)) + 2):
            x, y = ox + off + i * px, oy + j * py
            if inner.contains(Point(x, y)):
                f += K.atomic(C.stroke(C.lozenge_d(x, y, L, W), FINE, style="point", color=color, role="stone"),
                              f"ford{i}_{j}")
    return f


# ---------------------------------------------------------------------------
# the open mantle
# ---------------------------------------------------------------------------
def open_mantle(ms: K.MantleSpec, opening, *, border=36.0, chain=True, chain_rules=(15.0, 31.0),
                field=True, color=JADE, avoid=None, clear=None) -> K.Part:
    """The kit's bilateral mantle (``ms``) with its front OPEN: ``opening``
    (a region, the tabard's visible panel) is cut away, so the mantle's
    fronts lie over the tabard. A plain border ``border`` px wide runs
    inside every edge except the band cut (closed by a FINE seam); a §G.23
    stepping-stone chain runs in it (``chain_rules`` px inside the edge);
    the field carries the ford-stone brocade. ``avoid``: a region in front
    (hands, arms) no chain stone may touch (each is kept whole or dropped);
    ``clear``: a region left plain (no seam, chain or brocade: its cut ends
    must lie under something in front). meta: 'inner', 'ext'."""
    pts = K.mantle_outline(ms)
    half = Polygon(np.vstack([pts, [[ms.cx, ms.bottom]]])).buffer(0)
    full = K.U(half, K.mirror(half, ms.cx))
    ext = np.vstack([pts, [[pts[-1][0] + (pts[-1][0] - pts[-2][0]) / max(pts[-1][1] - pts[-2][1], 1e-6) * 300.0,
                            ms.bottom + 300.0], [ms.cx, ms.bottom + 300.0]]])
    ext_half = Polygon(ext).buffer(0)
    ext_full = K.U(ext_half, K.mirror(ext_half, ms.cx))
    op = K.R(opening)
    op_ext = op.union(K.box(op.bounds[0] + 5, ms.bottom - 60, op.bounds[2] - 5, ms.bottom + 400)).buffer(0)
    shape = full.difference(op)
    ext_shape = ext_full.difference(op_ext)
    inner = ext_shape.buffer(-border, quad_segs=16).intersection(K.box(0, 0, 2000, ms.bottom + 20))
    lines = K.outline(shape) + C.stroke(K.D(inner), FINE, role="seam")
    jade = shape
    if chain:
        ch = mantle_chain(shape, ext_shape, rules=chain_rules, avoid=avoid)     # avoid: a hand's paper channel
        lines += ch
        # (the stones are < 6.8 px wide: not a 'solid' for the layer trap, and a
        # trap hole under them would be a knockout thinner than 2.5 px)
    fills = K.fill(jade, color)
    if field:
        lines += ford_stones(inner, pitch=(26.0, 22.0), size=(12.0, 7.5))
    if clear is not None:
        orn = lines.select(lambda m: m.role != "outline")
        lines = lines.select(lambda m: m.role == "outline") + K.clip_out(orn, K.R(clear))
    return K.Part(shape, fills, lines, {"inner": inner, "ext": ext_shape, "full": full})


# ---------------------------------------------------------------------------
# local refinements of the kit fist (kept here: the kit is shared)
# ---------------------------------------------------------------------------
def _fist_frame(at, axis_deg, *, shaft_w=22.0, back=+1, h=34.0, reach=7.0, knuckle=11.0, **_):
    """The local frame facts of ``K.fist(at, axis_deg, ...)`` (the same arithmetic): block
    rows, lengths and the local → screen matrix (shapely order)."""
    a = shaft_w / 2.0
    hb = max(K.FIST_H_K * float(h), K.FIST_H_MIN)
    p = hb / 4.0
    t_up = 0.20 * hb
    ytop = -(hb + t_up) / 2.0
    y0 = ytop + t_up
    tip_out = min(max(float(reach), 3.0), K.FIST_TIP_OUT)
    x_tip = -a - tip_out
    Lf = max(K.FIST_LEN_K * hb, 2 * a + tip_out + max(float(knuckle), 12.0))
    M, Mf = K._rigid(at, axis_deg + 90.0, mirror_x=back < 0)
    A, Bm, Cm, Dm, ox, oy = M
    det = A * Dm - Bm * Cm
    Minv = (Dm / det, -Bm / det, -Cm / det, A / det, 0.0, 0.0)
    return dict(a=a, hb=hb, p=p, y0=y0, y1=y0 + hb, x_tip=x_tip, Lf=Lf, x_kn=x_tip + Lf, M=M, Mf=Mf, Minv=Minv,
                o=np.array([ox, oy]))


def _to_loc(F, pts):
    A, Bm, Cm, Dm, _, _ = F["Minv"]
    q = np.asarray(pts, float) - F["o"]
    return np.column_stack([A * q[:, 0] + Bm * q[:, 1], Cm * q[:, 0] + Dm * q[:, 1]])


def _to_scr(F, pts):
    A, Bm, Cm, Dm, ox, oy = F["M"]
    q = np.asarray(pts, float)
    return np.column_stack([A * q[:, 0] + Bm * q[:, 1] + ox, Cm * q[:, 0] + Dm * q[:, 1] + oy])


def refine_fist(hand: "K.Hand", at, axis_deg, *, fkw, smooth=2.4, line_ends=None, tip_join=True) -> "K.Hand":
    """The kit fist with two local refinements (the kit is shared; see COURT_GUIDE):

    * its silhouette SMOOTHED (closing + opening, radius ``smooth``) everywhere
      except the fingertip lobes and the notch at the thumb's tip — the kit's
      heel curve leaves the finger block's underside with a small kink (a
      1–2 px step, visible at 6–10×) that its own junction smoothing skips;
    * ``line_ends`` = {finger line k (2, 3): fraction of the block length from
      the knuckle end where it stops}: SHORTER finger lines on a back-of-hand
      fist — the fingers read as curled segments round the held edge, the
      back of the hand as one broad mass (the Drifters K♠ fist), instead of
      four long straight bands;
    * ``tip_join`` (palm view): the little finger's tip curl, which the kit
      stops 0.1 px short of the outline, is carried on to the block's
      underside (a clean T-junction instead of a near-miss).

    The Hand's ``rebuild`` hook (the kit re-aims a wrist along the sleeve it
    finds) is wrapped, so a rebuilt hand is refined the same way."""
    F = _fist_frame(at, axis_deg, **fkw)
    tipz = hand.hand.meta.get("tipzone")
    rt = 0.60 * F["p"]
    Tc = _to_scr(F, [(F["x_kn"] - 0.56 * F["Lf"], F["y0"] + F["p"] - rt)])[0]
    protect = Point(*Tc).buffer(rt + 5.0, quad_segs=12)
    if tipz is not None:
        protect = protect.union(tipz)

    def lines_of(inner):
        out = []
        for m in inner.marks:
            if m.role == "fingertip" and m.kind != "fill" and tip_join:
                # the palm view's last fingertip curl (the little finger's) stops 3.2 px short of the
                # block's underside in the kit: its round cap then lies 0.1 px inside the outline's
                # (a near-miss blob at 10×). It is carried on to the underside, like the others
                # between their finger lines: one clean T-junction.
                ln = K._stroke_lines(m.d)[0]
                ln = np.asarray(ln.coords) if hasattr(ln, "coords") else np.asarray(ln)
                loc = _to_loc(F, ln[[0, -1]])
                ya, yz = sorted((float(loc[0][1]), float(loc[1][1])))
                if abs(yz - (F["y1"] - 3.2)) < 0.6:
                    xf = float(np.mean(loc[:, 0]))
                    d = K.arc_sag(K.P(xf, ya), K.P(xf, F["y1"]), 0.26 * F["p"])
                    out.extend(K.line(d, m.w, role="fingertip").transformed(F["Mf"]).marks)
                    continue
            out.append(m)
        inner = C.Frag(out, inner.meta)
        if not line_ends:
            return inner
        out = []
        for m in inner.marks:
            if m.role != "finger" or m.kind == "fill":
                out.append(m)
                continue
            segs = []
            for ln in K._stroke_lines(m.d):
                ln = np.asarray(ln.coords) if hasattr(ln, "coords") else np.asarray(ln)
                loc = _to_loc(F, ln)
                k = int(round((float(np.mean(loc[:, 1])) - F["y0"]) / F["p"]))
                if k in line_ends:
                    x_end = F["x_kn"] - line_ends[k] * F["Lf"]
                    g = LineString(loc).intersection(shapely.box(-1e4, -1e4, x_end, 1e4))
                    for piece in K._lines_of(g):
                        if piece.length > 0.3:
                            segs.append(_to_scr(F, np.asarray(piece.coords)))
                else:
                    segs.append(ln)
            if segs:
                out.append(C.replace(m, d="".join(C.polyline_d(s) for s in segs)))
        return C.Frag(out, inner.meta)

    def refine(part):
        s = part.shape
        r = float(smooth)
        if r > 0:
            closed = s.buffer(r, quad_segs=12).buffer(-r, quad_segs=12)
            opened = s.buffer(-r, quad_segs=12).buffer(r, quad_segs=12)
            s = s.union(closed.difference(protect)).difference(s.difference(opened).difference(protect))
            s = max(K._polys_of(s), key=lambda g: g.area)
        inner = lines_of(part.meta["inner"])
        meta = dict(part.meta)
        meta["inner"] = inner
        if "rebuild" in part.meta:
            meta["rebuild"] = lambda u, _rb=part.meta["rebuild"]: refine(_rb(u))
        return K.Part(s, part.fills, K.outline(s) + inner, meta)

    from dataclasses import replace as _rep
    return _rep(hand, hand=refine(hand.hand))


def trim_behind(sc: "K.Scene", front: str, *, pen=1.1, skip=K.ARM_WORDS):
    """Lines of the items behind ``front`` (a hand) that run in under its
    contour are cut so their round caps end ``pen`` px inside its outline
    (the kit cuts them 0.5 px inside the edge, so a MEDIUM cap reaches
    2.05 px in — 0.5 px past the hand's MEDIUM outline: a nub at 6–10×).
    Arm items (the hand's own cuff/sleeve) are left alone."""
    names = [it.name for it in sc.items]
    i = names.index(front)
    zone = sc.items[i].occ
    for it in sc.items[:i]:
        nm = it.name.lower()
        if it.frag is None or not it.frag or any(w in nm for w in skip) or it.name.startswith(front):
            continue
        out, hit = [], False
        for m in it.frag.marks:
            if m.kind == "fill" or "@" in m.role or not m.d:
                out.append(m)
                continue
            lines = K._stroke_lines(m.d, sc.clip_tol)
            if not lines:
                out.append(m)
                continue
            ml = shapely.MultiLineString(lines)
            z = zone.buffer(m.w / 2 - pen, quad_segs=8)
            if not ml.intersects(z):
                out.append(m)
                continue
            hit = True
            res = ml.difference(z)
            try:
                res = shapely.line_merge(res)
            except shapely.errors.GEOSException:
                pass
            pieces = [np.asarray(ln.coords) for ln in K._lines_of(res) if ln.length > 0.3]
            if pieces:
                out.append(C.replace(m, d="".join(C.polyline_d(p) for p in pieces)))
        if hit:
            it.frag = C.Frag(out, it.frag.meta)
    return sc


def fill_heel_pocket(sc: "K.Scene", hand: str, cuff: str, floor_x: float, y_top: float, *, side=+1, reach=16.0):
    """The palm's heel run straight down its shaft to the gauntlet: the pocket the kit leaves
    between a fist's heel curve, the gauntlet's top edge and the shaft's paper halo (a little paper
    tab, 3 × 8 px, with a hooked heel) is taken into the hand, so the heel's inner edge stands on
    ``floor_x`` (the kit's 7.3 px floor off the shaft — its outline then lies exactly along the
    shaft's halo, like the gauntlet and forearm below it) from the finger block's underside
    (``y_top``) down to the gauntlet. ``side`` = +1: the shaft is to the right of the heel."""
    names = [it.name for it in sc.items]
    i = names.index(hand)
    it = sc.items[i]
    cf = sc.items[names.index(cuff)].occ
    x0, x1 = (floor_x - reach, floor_x) if side > 0 else (floor_x, floor_x + reach)
    pocket = K.box(x0, y_top - 0.5, x1, cf.bounds[3]).difference(cf.buffer(0.05))
    near = it.occ.buffer(0.6)
    pocket = shapely.union_all([g for g in K._polys_of(pocket) if g.intersects(near)]) if not pocket.is_empty else pocket
    if pocket.is_empty:
        return sc
    new = it.occ.union(pocket)
    new = new.buffer(0.8, quad_segs=8).buffer(-0.8, quad_segs=8).difference(cf)
    new = max(K._polys_of(new), key=lambda g: g.area)
    frag = it.frag.select(lambda m: m.role != "outline") + K.outline(new)
    sc.items[i] = K.Item(it.name, frag, new, it.sil, it.halo, it.halo_skip, it.halo_only, it.halo_zone)
    return sc


def fist_block_bottom(at, axis_deg, **fkw) -> float:
    """Screen y of a vertical-shaft kit fist's finger-block underside (``K.fist`` arithmetic)."""
    F = _fist_frame(at, axis_deg, **fkw)
    return float(_to_scr(F, [(0.0, F["y1"])])[0][1])
