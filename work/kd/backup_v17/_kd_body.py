"""art/_kd_body.py — K♦ garments and regalia (brief §H.10).

* ``tabard``        Gill Red, ASHLAR COURSES KNOCKED OUT TO PAPER (§G.20: running
                    bond, 3 px chamfers — the courthouse's rusticated base): the
                    red is the union of the stones, the joints are paper (holes
                    in the red, never paint), inside a plain red hem band;
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
* ``gauntlet``      a gold cuff carrying a TOOLED SCROLL (§G.31: ♦ cuffs only);
* ``mantle_chain``  a §G.23 stepping-stone chain run inside the mantle's
                    silhouette (two FINE rules, solid lozenges between);
* ``ford_stones``   a half-drop brocade of small outlined lozenges.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG

FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR
GOLD, RED, INK, JADE = K.GOLD, K.RED, K.INK, K.JADE


# ---------------------------------------------------------------------------
# tabard
# ---------------------------------------------------------------------------
def tabard(reg, *, base_y=None, string=6.0, block=(44.0, 20.0), joint=3.0, chamfer=4.6, origin=(375.0, 511.0),
           color=RED, heal=1.3) -> K.Part:
    """A red tabard over region ``reg``. Below ``base_y`` its RUSTICATED BASE:
    running-bond ashlar (§G.20) whose JOINTS are knocked out to paper
    (``joint`` px of paper between stones, ≥ 2.5; chamfers open a small paper
    lozenge at every joint crossing); above it a STRINGCOURSE — a ``string``
    px red band between two paper joints — and plain red. (The courthouse:
    a rusticated limestone base under a plain storey.) ``base_y`` None: the
    whole tabard is ashlar."""
    reg = K.R(reg)
    x0, y0, x1, y1 = reg.bounds
    top = y0 - 10.0 if base_y is None else base_y
    bw, bh = block
    px, py = bw + joint, bh + joint
    ox, oy = origin
    c = chamfer
    stones = []
    for j in range(int(math.floor((top - oy) / py)) - 1, int(math.ceil((y1 - oy) / py)) + 2):
        off = px / 2 if j % 2 else 0.0
        for i in range(int(math.floor((x0 - ox - off) / px)) - 1, int(math.ceil((x1 - ox - off) / px)) + 2):
            bx, by = ox + off + i * px + joint / 2 - px / 2, oy + j * py + joint / 2
            if by < top - 0.1:
                continue
            pts = [(bx + c, by), (bx + bw - c, by), (bx + bw, by + c), (bx + bw, by + bh - c),
                   (bx + bw - c, by + bh), (bx + c, by + bh), (bx, by + bh - c), (bx, by + c)]
            stones.append(Polygon(pts))
    # the joint grid starts at the first course's top joint
    first = min(p.bounds[1] for p in stones)
    upper = reg.intersection(K.box(-10, -10, 2000, first - 2 * joint - string))
    band = reg.intersection(K.box(-10, first - joint - string, 2000, first - joint)) if string else None
    st = shapely.union_all(stones).intersection(reg)
    keep = []
    for pg in K._polys_of(st):
        if pg.area < 0.30 * bw * bh or pg.buffer(-2.0).is_empty:
            keep.append(pg.buffer(joint / 2 + 0.3, join_style=2).intersection(K.box(-10, first, 2000, 2000)))
        else:
            keep.append(pg)
    parts = [upper] + ([band] if band is not None else []) + keep
    red = shapely.union_all(parts).intersection(reg)
    red = red.buffer(heal, join_style=2).buffer(-heal, join_style=2).intersection(reg)
    return K.Part(reg, K.fill(red, color), K.outline(reg), {"red": red, "base": first})


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
         color=JADE, trap=1.6) -> K.Part:
    """A jade baldric from p0 toward p1, ``width`` wide, clipped to ``clip``:
    gold rowels (Aquifer contour, paper axle) on its axis every ``pitch``
    px from ``first``, a solid Aquifer ford-stone lozenge half-way between
    each pair. Rowels touching ``avoid`` (a region in front, e.g. the clasp)
    are skipped. The jade is CUT under each rowel (the layer trap)."""
    p0, p1 = K.P(p0), K.P(p1)
    u = (p1 - p0) / np.hypot(*(p1 - p0))
    n = np.array([u[1], -u[0]])
    L = float(np.hypot(*(p1 - p0)))
    a, b = p0 - u * 200, p1 + u * 200
    band = Polygon([a + n * width / 2, b + n * width / 2, b - n * width / 2, a - n * width / 2])
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
                    av is None or not av.intersects(Point(*cs).buffer(stones[0]))):
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
    return K.Part(reg, fills, lines, {"u": u, "n": n})


# ---------------------------------------------------------------------------
# the Key of the Ford
# ---------------------------------------------------------------------------
def key_of_ford(x=552.0, bow_c=(552.0, 122.0), *, ring_r=(37.0, 27.5), star_r=21.0, core_r=8.0, core_d=6.3,
                star_w=11.0, sliver=0.6,
                stem_hw=8.0, stem_bottom=505.0, collars=(172.0, 246.0, 320.0, 424.0), collar_hw=12.5,
                collar_h=7.4, bit=(436.0, 470.0, 497.0), bit_out=(34.0, 22.0), ward=(454.0, 5.2, 14.0),
                field_color=RED, color=GOLD) -> K.Part:
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
    field_ok = max(K._polys_of(field_ok), key=lambda g: g.area) if not field_ok.is_empty else field_ok
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
    return K.Part(shape, fills, lines, {"star": star, "bit": bit_p, "ring": ring_out, "field": field})


# ---------------------------------------------------------------------------
# gauntlet cuff with a tooled scroll
# ---------------------------------------------------------------------------
def cuff_scroll(L=40.0, r0=8.4, leaf=True):
    """One sprig of §G.31 tooled scroll in a local frame (x across the cuff,
    y DOWN the arm; centred on the origin): a stem enters from the left edge,
    swings in one S and rolls into an 'eye' volute on the right; one vesica
    leaf springs from the S's inflection into the space under the volute."""
    f = C.Frag()
    x0 = -L / 2
    vx = L / 2 - 2 * r0 - 1.0
    t = C.Turtle(x0, 3.0, -8.0)
    t.fd(3.0)
    R1 = (vx - x0 - 3.0) / 2.2
    t.arc(R1, 30.0)
    infl, infl_h = t.pos.copy(), t.heading
    t.arc(R1 * 0.72, -112.0)
    f += C.stroke(t.d(), FINE, color=INK, role="stem")
    e = t.pos.copy()
    f += MG.volute(e[0], e[1], r0, heading=t.heading, cw=True, color=INK)
    if leaf:
        ang = math.radians(infl_h + 62.0)
        u = np.array([math.cos(ang), math.sin(ang)])
        p0 = infl + u * (FINE + 2.2)
        p1 = p0 + u * 12.5
        f += C.stroke(C.polyline_d([infl, p0]), FINE, color=INK, role="petiole")
        f += C.stroke(C.vesica_d(p0, p1, 5.6), FINE, style="point", color=INK, role="leaf")
    return f


def gauntlet(W, u, *, width=38.0, flare=52.0, depth=42.0, color=GOLD, mirror=False) -> K.Part:
    """A flared gold gauntlet cuff from the wrist W (top edge, across the
    arm) back down the arm (direction −u) ``depth`` px, widening to
    ``flare``; one tooled-scroll sprig (§G.31) across it."""
    W, u = K.P(W), np.asarray(u, float) / np.hypot(*u)
    n = np.array([u[1], -u[0]])
    a0, a1 = W + n * width / 2, W - n * width / 2
    B = W - u * depth
    b0, b1 = B + n * flare / 2, B - n * flare / 2
    d = K.Path(a0).sag(a1, -2.5).line(b1).sag(b0, 3.5).close().d
    reg = K.R(d)
    lines = K.outline(reg)
    sc = cuff_scroll(L=min(width, flare) + 2.0)
    if mirror:
        sc = sc.mirror_x(0.0)
    ang = math.degrees(math.atan2(-n[1], -n[0]))
    C0 = W - u * depth * 0.5
    sc = sc.rotate(ang).translate(C0[0], C0[1])
    lines += K.clip_in(sc, reg.buffer(-(MEDIUM / 2 + K.GAP_MARK + FINE / 2 + 0.1)))
    return K.Part(reg, K.fill(reg, color), lines, {})


# ---------------------------------------------------------------------------
# mantle ornament
# ---------------------------------------------------------------------------
def _offset_path(ext_shape, d, clip):
    """The boundary of ``ext_shape`` inset by ``d``, clipped to ``clip`` → list of point arrays."""
    ring = ext_shape.buffer(-d, quad_segs=16).boundary.intersection(clip)
    return [np.asarray(g.coords) for g in K._lines_of(shapely.line_merge(ring) if ring.geom_type != "LineString"
                                                        else ring) if g.length > 10]


def mantle_chain(shape, ext_shape, *, rules=(20.0, 36.0), stone=(11.0, 6.4), pitch=24.0, clip=None,
                 color=INK) -> C.Frag:
    """§G.23 stepping-stone chain inside the mantle's silhouette: two FINE
    rules at ``rules`` px inside the outline (``ext_shape``: the mantle
    extended below the band, so the chain never runs along the cut), solid
    lozenges on the mid-line every ``pitch`` px (atomic: kept whole)."""
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
            if room.contains(p):
                ld = C.lozenge_d(p.x, p.y, stone[0], stone[1], a)
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
                field=True, color=JADE) -> K.Part:
    """The kit's bilateral mantle (``ms``) with its front OPEN: ``opening``
    (a region, the tabard's visible panel) is cut away, so the mantle's
    fronts lie over the tabard. A plain border ``border`` px wide runs
    inside every edge except the band cut (closed by a FINE seam); a §G.23
    stepping-stone chain runs in it (``chain_rules`` px inside the edge);
    the field carries the ford-stone brocade. meta: 'inner', 'ext'."""
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
        ch = mantle_chain(shape, ext_shape, rules=chain_rules)
        lines += ch
        # (the stones are < 6.8 px wide: not a 'solid' for the layer trap, and a
        # trap hole under them would be a knockout thinner than 2.5 px)
    fills = K.fill(jade, color)
    if field:
        lines += ford_stones(inner)
    return K.Part(shape, fills, lines, {"inner": inner, "ext": ext_shape, "full": full})
