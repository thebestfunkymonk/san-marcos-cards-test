"""art/_qc_parts.py — Q♣ · The Wild-Rice Queen: the parts the shared kit does not have.

Everything is built the courtkit way (compass geometry, Parts with an opaque
``shape``, legal widths only, nothing scaled, nothing paper painted):

    gown(...)            the jade gown: a bertha neckline, sloped shoulders, a
                         plain border + FINE seam and the §G.4 ribbon-leaf
                         textile streaming diagonally inside it
    bertha(...)          §H.8 'neckline lining: Gill Red' — the gown's lining
                         turned out as a broad band round the neckline, with
                         paper knockouts
    laced_front(...)     §H.8 bodice lacing: a gold reed ladder (§G.19) across
                         the red lining of the bodice opening
    puff(...)            a slashed puffed sleeve-cap (red, vesica slashes)
    rice_crown(...)      §H.8 rice-spike coronet as a goldsmith's crown of rice:
                         a solid moulded gold circlet with a set jewel and
                         three wild-rice sprays (3 : 1 spikelets on branching
                         pedicels, HAIRLINE awns) rising from behind its rim
    rice_sceptre(...)    §H.8/§G.5 the sceptre wrought as a flowering wild-rice
                         stalk: erect female spikelets at the tip, drooping male
                         florets below, a gold culm with reed nodes
    plume(...)           one egret plume: a paper lock with current lines (§G.24)
    hair_lock(...)       a lock of gold hair between two arc splines
    leaf_field(...)      §G.4 ribbon leaves streaming diagonally (the current)
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from inkkit import geom as G
from deck.motifs import core as C
from deck.motifs import forms as FM
from deck.motifs import rice as MR

P, R, U = K.P, K.R, K.U
FINE, MEDIUM, RULE, CONTOUR, HAIR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR, K.HAIR_W
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD


def ring_mid(d):
    """Re-seat every closed subpath of ``d`` so it starts MID-SIDE, not at a
    sharp tip. A vesica starts at its tip; once ``clip_out`` turns it into a
    polyline the ring's seam is an open end: the render (and heal's skia
    outline) caps it round while QA 12 closes it with a miter spike up to
    10 × w/2 long. Seated mid-side, the seam is smooth, both tips are true
    miter joins, and render, heal and QA agree. → d (closed polylines)."""
    out = ""
    for pts, closed in G.as_polys(d, 0.05):
        pts = np.asarray(pts, float)
        shut = len(pts) > 3 and np.allclose(pts[0], pts[-1])
        if closed or shut:
            ring = pts[:-1] if shut else pts
            k = int(np.argmax(np.hypot(*(ring - ring[0]).T)))
            ring = np.roll(ring, -(k // 2), axis=0)
            out += C.polyline_d(ring, closed=True)
        else:
            out += C.polyline_d(pts)
    return out


def close_rings(f):
    """Every stroke subpath whose ends coincide becomes a true closed ring
    (``Z``). ``clip_out`` re-serialises a ring it touches as an open
    polyline: the renderer (and heal's skia outline) then caps its seam round
    while GEOS — QA 12 — buffers it as a ring with a miter spike there. As a
    closed ring every tip is a miter join everywhere (§B.2 sharp vesica
    tips), so render, heal and QA see the same outline."""
    from dataclasses import replace as _rp
    out = []
    for m in f.marks:
        if m.kind != "stroke" or not m.d:
            out.append(m)
            continue
        polys = G.as_polys(m.d, 0.05)
        fix = any((not c) and len(p) > 3 and np.allclose(p[0], p[-1], atol=0.02) for p, c in polys)
        if not fix:
            out.append(m)
            continue
        d = ""
        for pts, closed in polys:
            pts = np.asarray(pts, float)
            if closed or (len(pts) > 3 and np.allclose(pts[0], pts[-1], atol=0.02)):
                ring = pts[:-1] if np.allclose(pts[0], pts[-1], atol=0.02) else pts
                d += C.polyline_d(ring, closed=True)
            else:
                d += C.polyline_d(pts)
        out.append(_rp(m, d=d))
    return C.Frag(out, f.meta)


def compose(sc, cut_y=511.0):
    """``sc.compose()`` with ``close_rings`` applied BEFORE the heal (the
    kit's compose heals first): the same clip, silhouette and band-rule heal
    as ``Scene.compose``; the heal log lands in ``sc.heal_log``."""
    res = sc.compose(heal_gaps=False)
    res = close_rings(res)
    band = C.stroke(f"M100 {cut_y:g}L650 {cut_y:g}", FINE, style="rule", role="_band")
    log = []
    res = K.heal(res + band, log=log, keep_roles=("contour", "_band"))
    sc.heal_log = log
    return res.select(lambda m: m.role != "_band")


def reseat(f, roles=("leaf", "spikelet")):
    """``ring_mid`` on every stroke mark of ``f`` whose role is in ``roles``."""
    from dataclasses import replace as _rp
    return C.Frag([_rp(m, d=ring_mid(m.d)) if (m.kind == "stroke" and m.role in roles and m.d) else m
                   for m in f.marks], f.meta)


def _u(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def _pts(d, step=0.3):
    return np.asarray(C.sample_d(d, step)[0][0], float)


def _biggest(g):
    ps = K._polys_of(g.buffer(0))
    return max(ps, key=lambda q: q.area) if ps else Polygon()


# =============================================================================
# the gown
# =============================================================================
def gown_outline(*, cx=375.0, neck_c=(375.0, 330.0), neck=(336.0, 300.0), neck_sag=-10.0,
                 shoulder=(226.0, 338.0), shoulder_sag=5.0, corner_r=34.0, hem=(184.0, 560.0)):
    """The gown's outline, bilateral about ``cx``: the neckline arc from the
    centre front ``neck_c`` up to the ``neck`` point, the shoulder line
    (an arc bowing ``shoulder_sag``) out to the ``shoulder`` corner (rounded
    ``corner_r``), the side straight down to ``hem`` below the band.
    → (region, top edge points left half: centre → shoulder)."""
    N, S0, Sh, Hm = P(*neck_c), P(*neck), P(*shoulder), P(*hem)
    d_half = K.Path(N).sag(S0, neck_sag).sag(Sh, shoulder_sag).line(Hm).line((cx, Hm[1])).close().d
    half = R(d_half)
    shape = U(half, K.mirror(half, cx))
    rounded = shape.buffer(-corner_r, join_style=1).buffer(corner_r, join_style=1)
    keep = shape.intersection(K.box(S0[0] - 30, 0, 2 * cx - S0[0] + 30, S0[1] + 60))
    shape = U(rounded, keep).buffer(0)
    top = np.vstack([_pts(K.arc_sag(N, S0, neck_sag)), _pts(K.arc_sag(S0, Sh, shoulder_sag))[1:]])
    return shape, top


def bertha(shape, top, *, cx=375.0, depth=26.0, color=RED, pearl=None, avoid=None, avoid_gap=4.0):
    """§H.8 the neckline lining turned out: the band of the gown within
    ``depth`` px of its neckline + shoulder line (both halves), with a row
    of graduated paper pearls (§G.29, ``pearl`` = kw for ``pearls``)
    knocked out along its middle, none within ``avoid_gap`` of ``avoid``
    (the brooch). → Part (meta 'mid' = the band's centre line, right
    shoulder → left shoulder)."""
    full = np.vstack([np.column_stack([2 * cx - top[::-1, 0], top[::-1, 1]]), top[1:]])
    band = shape.intersection(LineString(full).buffer(depth, cap_style=2, quad_segs=16))
    band = _biggest(band)
    mid = np.asarray(G.Curve(full).offset(depth / 2, spacing=0.5))
    fill_d = K.D(band)
    if pearl is not None:
        pl = pearls(mid, **pearl)
        if avoid is not None:
            # a pearl half under the brooch reads as a stray 'C': keep it whole and clear, or drop it
            zone = R(avoid).buffer(avoid_gap)
            pl = C.Frag([m for m in pl.marks if not R(G.to_shape(m.d, tol=0.05)).intersects(zone)], pl.meta)
        fill_d = C.knockout(fill_d, pl)
    return K.Part(band, K.fill(fill_d, color), K.outline(band), {"line": full, "mid": mid})


def leaf_field(region, *, heading=58.0, length=160.0, width=16.0, row=40.0, step=190.0, stagger=0.5,
               origin=(375.0, 330.0), bend=(10.0, -10.0), hatch=1, whole=False, keep=None):
    """§H.8 ribbon leaves streaming diagonally with the current (§G.4): a
    lattice of S-curved, half-hatched vesicas, all heading ``heading``°,
    rows ``row`` px apart across the stream, leaves ``step`` px apart along
    it, alternate rows shifted ``stagger``·step. Aquifer FINE on the jade;
    clipped to ``region`` (``whole``: only leaves wholly inside, each kept
    or dropped as one motif). → Frag."""
    reg = R(region)
    x0, y0, x1, y1 = reg.bounds
    u = _u(heading)
    v = np.array([-u[1], u[0]])
    o = P(origin)
    f = C.Frag()
    diag = math.hypot(x1 - x0, y1 - y0) + length
    kmax = int(diag / row) + 2
    jmax = int(diag / step) + 2
    inner = reg.buffer(-2.0) if whole else reg
    for k in range(-kmax, kmax + 1):
        off = (k % 2) * stagger * step
        for j in range(-jmax, jmax + 1):
            base = o + v * (k * row) + u * (j * step + off)
            tip = base + u * length
            bb = shapely.box(min(base[0], tip[0]) - 20, min(base[1], tip[1]) - 20,
                             max(base[0], tip[0]) + 20, max(base[1], tip[1]) + 20)
            if not bb.intersects(reg):
                continue
            lf = MR.ribbon_leaf(base[0], base[1], heading, length, width, bend=bend, hatch=hatch)
            if whole:
                if keep is not None and not keep(base, tip):
                    continue
                if inner.contains(R(lf.outline())):
                    f += K.atomic(lf, f"leaf{k}_{j}")
            else:
                f += lf
    return f if whole else K.clip_in(f, reg)


def gown(shape, *, border=24.0, leaves=None, color=JADE):
    """The jade gown Part: the fill, a plain border ``border`` px inside the
    silhouette closed by a FINE seam, and the leaf textile (``leaves`` kw
    for ``leaf_field``) inside it."""
    inner = shape.buffer(-border, quad_segs=16)
    lf = leaf_field(inner, **(leaves or {}))
    lines = K.outline(shape) + C.stroke(K.D(inner), FINE, role="seam") + lf
    return K.Part(shape, K.fill(shape, color), lines, {"inner": inner})


def cloak(*, cx=375.0, top=(300.0, 318.0), shoulder=(196.0, 330.0), hem=(146.0, 560.0), corner_r=30.0,
          side_sag=0.0, color=RED, edge=0.0, edge_color=GOLD, knock=None):
    """The queen's mantle, worn behind the gown and falling from the
    shoulders — we see its Gill Red LINING (§H.8) either side of the gown:
    bilateral about ``cx``; its top edge runs behind the neck from ``top``
    out to the rounded ``shoulder`` and its side falls (bowing ``side_sag``)
    to ``hem`` below the band. ``edge`` > 0: a turned border of that width
    along the falling side (``edge_color``). → Part (meta 'edge')."""
    tp, sh, hm = P(*top), P(*shoulder), P(*hem)
    d_half = K.Path(P(cx, top[1] - 6.0)).sag(tp, -2.0).sag(sh, 6.0).sag(hm, side_sag).line((cx, hem[1])).close().d
    half = R(d_half)
    shape = U(half, K.mirror(half, cx))
    shape = U(shape.buffer(-corner_r, join_style=1).buffer(corner_r, join_style=1),
              shape.intersection(K.box(tp[0] - 10, 0, 2 * cx - tp[0] + 10, 2000))).buffer(0)
    body_d = K.D(shape)
    if knock is not None:
        body_d = C.knockout(body_d, knock)
    fills = K.fill(body_d, color)
    lines = K.outline(shape)
    meta = {}
    if edge:
        side_l = _pts(K.Path(sh).sag(hm, side_sag).d)
        side = np.vstack([side_l, [[side_l[-1][0], side_l[-1][1] + 60]]])
        eb = C.Frag()
        band = U(*[shape.intersection(LineString(s).buffer(edge * 2, cap_style=2)).intersection(
            shape.difference(shape.buffer(-edge))) for s in (side, np.column_stack([2 * cx - side[:, 0], side[:, 1]]))])
        band = band.intersection(K.box(0, sh[1] + corner_r * 0.3, 2000, 2000))
        meta["edge"] = band
        fills = K.fill(C.knockout(body_d, C.fill(K.D(band))) if False else body_d, color) + K.fill(band, edge_color)
        lines += K.clip_in(C.stroke(K.D(shape.buffer(-edge)), MEDIUM, role="hem"), band.buffer(1.0))
    return K.Part(shape, fills, lines, meta)


# =============================================================================
# the laced bodice front
# =============================================================================
def laced_front(*, cx=375.0, top=352.0, bottom=560.0, hw=(19.0, 15.0), rail=7.5, rung=7.0, pitch=24.0,
                first=16.0, node_every=4, node_over=4.0, node_h=10.0, ref_y=511.0, last=486.0, color=RED):
    """§H.8 bodice lacing, a gold reed ladder (§G.19) across the bodice
    opening: the opening (the Gill Red lining, ``hw`` half-wide at ``top``
    and at ``ref_y``) edged by two gold rails ``rail`` wide, crossed by gold
    rungs ``rung`` tall every ``pitch`` px; every ``node_every``-th rung a
    reed node — a rounded collar ``node_over`` px proud of the rails. Gold
    on red only as solids with an Aquifer contour (§C.4).
    → (opening Part (red), ladder Part (gold))."""
    def hwy(y):
        return hw[0] + (hw[1] - hw[0]) * (y - top) / (ref_y - top)
    strip = Polygon([(cx - hwy(top), top), (cx + hwy(top), top), (cx + hwy(bottom), bottom),
                     (cx - hwy(bottom), bottom)])
    inner = Polygon([(cx - hwy(top) + rail, top - 1), (cx + hwy(top) - rail, top - 1),
                     (cx + hwy(bottom) - rail, bottom + 1), (cx - hwy(bottom) + rail, bottom + 1)])
    rails = strip.difference(inner)
    bars = []
    y = top + first
    k = 0
    while y < last:
        k += 1
        w_ = hwy(y)
        if node_every and k % node_every == 0:
            bars.append(R(K.rrect(cx - w_ - node_over, y - node_h / 2, cx + w_ + node_over, y + node_h / 2,
                                  node_h / 2 - 0.5)))
        else:
            bars.append(K.box(cx - w_, y - rung / 2, cx + w_, y + rung / 2))
        y += pitch
    ladder = U(rails, *bars).buffer(0.01).buffer(-0.01)
    return (K.Part(strip, K.fill(strip, color), K.outline(strip), {}),
            K.Part(ladder, K.fill(ladder, GOLD), K.outline(ladder), {}))


# =============================================================================
# sleeves
# =============================================================================
def puff(c, r=30.0, *, squash=0.88, rot=0.0, slashes=3, slash_len=1.25, slash_w=7.0, pitch=11.5, color=JADE,
         slash_color=RED):
    """A puffed sleeve-cap: a slightly squashed round ``r`` about ``c``
    (rotated ``rot``°), with ``slashes`` parallel vesica slashes along the
    arm (``pitch`` apart, ``slash_len`` × r long, ``slash_w`` wide) through
    which the Gill Red lining shows (``slash_color``; None = paper
    knockouts) — Tudor slashing. → Part."""
    c = P(c)
    circ = Point(0, 0).buffer(r, quad_segs=64)
    circ = shapely.affinity.scale(circ, 1.0, squash)
    circ = shapely.affinity.rotate(circ, rot, origin=(0, 0))
    reg = shapely.affinity.translate(circ, c[0], c[1])
    u = _u(90.0 + rot)                       # along the arm (down)
    n = np.array([-u[1], u[0]])
    holes = C.Frag()
    lines = K.outline(reg)
    for k in range(slashes):
        o = c + n * (k - (slashes - 1) / 2) * pitch
        L = r * slash_len * (1.0 - 0.18 * abs(k - (slashes - 1) / 2))
        vd = C.vesica_d(o - u * L / 2, o + u * L / 2, slash_w)
        holes += C.fill(vd)
        if slash_color:
            lines += C.stroke(vd, MEDIUM, style="point", role="slash")
    if slash_color:
        fills = K.fill(reg, color) + holes.recolor(slash_color)
    else:
        fills = K.fill(C.knockout(K.D(reg), holes), color)
    return K.Part(reg, fills, lines, {})


def pearls(line_pts, *, d_end=6.3, d_mid=10.5, gap=5.0, margin=10.0):
    """§G.29 pearl beading along a polyline (from one end to the other):
    circles graduated from ``d_end`` at the ends to ``d_mid`` at the middle,
    ``gap`` px of red between neighbours. → Frag of FILL discs (to knock out)."""
    cv = G.Curve(np.asarray(line_pts, float))
    L = cv.length
    f = C.Frag()
    s = margin
    items = []
    while s < L - margin:
        t = abs(s / L - 0.5) * 2
        d = d_mid + (d_end - d_mid) * t
        items.append((s, d))
        s += d + gap
    # centre the run
    shift = (L - margin - (items[-1][0] + items[-1][1] / 2)) / 2 if items else 0.0
    # where the line turns sharply (the neck point) two pearls can crowd into
    # one blob: working out from the middle, a pearl less than ``gap`` from
    # one already kept is dropped (symmetric for a symmetric line)
    placed = [(cv.at_s(s + shift), d) for s, d in items]
    order = sorted(range(len(placed)), key=lambda i: abs(items[i][0] + shift - L / 2))
    keep = []
    for i in order:
        p, d = placed[i]
        if all(np.hypot(*(p - q)) >= (d + e) / 2 + gap - 0.5 for q, e in (placed[j] for j in keep)):
            keep.append(i)
    for i in sorted(keep):
        p, d = placed[i]
        f += C.fill(C.circle_d(p[0], p[1], d / 2))
    return f


# =============================================================================
# the rice crown
# =============================================================================
def _circlet_d(cx, top, h, hw_top, hw_bot, bow):
    """A flared circlet: top arc (cx ± hw_top at top − bow, through (cx, top)),
    straight ends, bottom arc (cx ± hw_bot at top + h − bow, through
    (cx, top + h)). → d."""
    y0, y1 = top - bow, top + h - bow
    return K.Path((cx - hw_top, y0)).arc3((cx, top), (cx + hw_top, y0)).line((cx + hw_bot, y1)).arc3(
        (cx, top + h), (cx - hw_bot, y1)).close().d


def _circlet_arc(cx, top, hw, bow, dy, x0, x1, n=120):
    """The circlet's top arc (through (cx ± hw, top − bow) and (cx, top))
    shifted ``dy`` down, sampled from x0 to x1. → points."""
    xs = np.linspace(x0, x1, n)
    return np.column_stack([xs, [_arc_y(cx, top, hw, bow, x) + dy for x in xs]])


def rice_crown(fc, *, cx=386.5, top=142.0, h=26.0, bow=4.0, hw=(58.0, 54.0), rim=8.5, base=8.0,
               jewel=(9.5, 144.5, 6.3), sprays=(), far=0.85, sink=5.0):
    """§H.8 the rice-spike coronet as a goldsmith's crown of rice — a METAL
    crown, never a feather headband (director's note, §J):

    * the CIRCLET — a solid gold band ``h`` tall at the front, dipping
      ``bow``, flaring from ``hw[1]`` at its foot to ``hw[0]`` at its rim and
      as wide as the hair it sits on (a crown worn on the head, not a band
      across the brow); a MEDIUM line ``rim`` px under its top edge (the rim
      moulding) and one ``base`` px over its foot (the base moulding), each
      ≥ 4.2 px of gold clear of the edge strokes;
    * a set JEWEL (``jewel`` = (r, centre y, red core Ø)) on the face axis,
      standing proud of the rim, the mouldings stopping on it;
    * the SPRAYS — wrought wild-rice panicles rising from behind the rim
      (their wire rods start ``sink`` px under it, so the rim stays one
      unbroken CONTOUR): ``sprays`` = (dx from the face axis, tilt°, rod
      length, terminal (L, W, awn), side spikelets ((s up the rod, side ±1,
      pedicel, pedicel° off the rod, L, W, spikelet° off the rod, awn), …)).
      Each is a MEDIUM rod ending in a terminal spikelet, with small 3 : 1
      gold spikelets (MEDIUM, sharp miter tips) on MEDIUM pedicels branching
      from it below the terminal (so no two spikelets run side by side) and
      a HAIRLINE awn off every tip. Far-side dx are compressed by ``far``.
      Paint the sprays back to front: the side sprays first.

    → (band Part: circlet + jewel, in the silhouette; sprays Part: add
       BEFORE the band, outside the silhouette)."""
    a = fc.anchors
    ax = float(a["axis"])
    turn = a.get("turn", 0)
    hw_t, hw_b = hw
    band_d = _circlet_d(cx, top, h, hw_t, hw_b, bow)
    band = R(band_d)

    # ---- sprays ------------------------------------------------------------------
    els, ves_ds, wires, awns, tips = [], [], [], C.Frag(), []

    def spikelet(q, v, L, W, aw):
        ves = C.vesica_d(q - v * 1.0, q + v * L, W)
        els.append(R(ves))
        ves_ds.append(ves)
        tip = q + v * L
        if aw:
            awns.marks.extend(C.stroke(C.polyline_d([tip, tip + v * aw]), HAIR, role="awn").marks)
        tips.append(tip + v * aw)

    for (dx, tilt, rod, term, sides) in sprays:
        if turn and dx * turn > 0:
            dx *= far
        x = ax + dx
        u = _u(-90.0 + tilt)
        b = P(x, _arc_y(cx, top, hw_t, bow, x))
        r_top = b + u * rod
        spikelet(r_top, u, *term)
        wires.append((b - u * sink, r_top + u * 1.5))
        for (s_, sd, ped, ped_deg, L, W, deg, aw) in sides:
            p0 = b + u * s_
            q = p0 + _u(-90.0 + tilt + sd * ped_deg) * ped
            v = _u(-90.0 + tilt + sd * deg)
            spikelet(q, v, L, W, aw)
            wires.append((p0, q + v * 1.5))
    stone = U(*els) if els else Polygon()
    wire_l = C.Frag()
    for p_, q_ in wires:
        wire_l += K.seg(p_, q_, MEDIUM, role="pedicel")
    wire_l = K.clip_out(wire_l, stone, eps=-0.5, trap=0.0)
    sp_lines = C.Frag()
    for vd in ves_ds:
        sp_lines += C.stroke(ring_mid(vd), MEDIUM, style="point", role="spikelet")
    spr = K.Part(stone, K.fill(stone, GOLD), sp_lines + wire_l + awns, {"tips": tips})

    # ---- circlet, mouldings, jewel ----------------------------------------------------
    lines = K.outline(band_d)
    for dy in (rim, h - base):
        # each moulding runs parallel to the rim from one flared end to the other
        x0 = cx - (hw_t + (hw_b - hw_t) * dy / h)
        pts = _circlet_arc(cx, top, hw_t, bow, dy, x0 - 2.0, 2 * cx - x0 + 2.0)
        lines += K.clip_in(K.line(C.polyline_d(pts), MEDIUM, role="moulding"), band)
    whole, fills, meta = band, K.fill(band, GOLD), {"band": band}
    if jewel:
        jr, jy, jcore = (tuple(jewel) + (8.4,))[:3]
        jc = P(ax, jy)
        jw = cabochon(jc, jr, core=jcore)
        lines = K.clip_out(lines, jw.shape, eps=-0.5, trap=0.0) + jw.lines
        whole = U(band, jw.shape)
        fills = K.fill(whole, GOLD) + K.dot(jc, jcore, RED)
        meta["jewel"] = jc
    return K.Part(whole, fills, lines, meta), spr


def cabochon(c, r=9.0, core=8.4, color=RED):
    """A small set stone: a gold disc (MEDIUM outline) with a Gill Red core
    cut into the gold (the layer trap, §2.1). → Part."""
    c = P(c)
    disc = R(K.circle(c, r))
    return K.Part(disc, K.fill(disc, GOLD) + K.dot(c, core, color), K.outline(K.circle(c, r)), {})


def _arc_y(cx, y, hw, bow, x):
    """The crown band's top edge (an arc through (cx - hw, y - bow), (cx, y),
    (cx + hw, y - bow)) at x."""
    c, r = K.circ3(P(cx - hw, y - bow), P(cx, y), P(cx + hw, y - bow))
    return c[1] + math.sqrt(max(r * r - (x - c[0]) ** 2, 0.0))


# =============================================================================
# the wild-rice sceptre
# =============================================================================
def rice_sceptre(x=545.0, *, bottom=560.0, hw=7.5, knop_y=268.0, knop_hw=14.0, knop_h=10.0,
                 nodes=(336.0, 476.0), node_hw=12.0, node_h=8.0, rachis_hw=4.2, rachis_top=150.0,
                 terminal=(34.0, 11.0, 22.0),
                 female=((226.0, -1, 16.0, 48.0, 30.0, 10.0, 10.0, 18.0), (204.0, 1, 16.0, 48.0, 30.0, 10.0, 10.0, 18.0),
                         (182.0, -1, 13.0, 44.0, 26.0, 9.2, 8.0, 16.0), (164.0, 1, 12.0, 44.0, 24.0, 8.8, 8.0, 15.0)),
                 arms=((258.0, 50.0, 6.0, 7.0, 6.0, ((0.42, 22.0, 8.0, 10.0), (0.72, 24.0, 8.4, 14.0),
                                                      (1.0, 25.0, 8.6, 18.0))),),
                 color=GOLD):
    """§H.8 / §G.5 the sceptre WROUGHT in gold as a flowering wild-rice
    stalk, botanically ordered along its own axis (``x``):

    * the CULM (``hw``) from below the band up to a reed-node KNOP at
      ``knop_y``, with raised node collars at ``nodes`` (a grass culm);
    * above the knop the RACHIS (``rachis_hw``) carries ERECT FEMALE
      spikelets alternating up the stalk, ``female`` = (rachis y, side,
      pedicel, pedicel° off upright, L, W, axis° off upright, awn), each
      on a visible MEDIUM pedicel with a long HAIRLINE awn, and ends in a
      terminal spikelet (L, W, awn) standing on ``rachis_top``;
    * below them, springing from the knop, the spreading MALE branches:
      ``arms`` = (y at the rachis, reach, rise, sag, width, florets), a wrought
      gold arm ``width`` wide out to each side from which 3 : 1 florets HANG,
      pointing down and out: (t along the arm, L, W, hang° off vertical).

    → Part (meta: culm = the stalk (silhouette piece); head = the flowering
    head: spikelets, pedicels, arms and florets, drawn with MEDIUM edges)."""
    culm = K.box(x - hw, knop_y, x + hw, bottom)
    knop = R(K.rrect(x - knop_hw, knop_y - knop_h / 2, x + knop_hw, knop_y + knop_h / 2, knop_h / 2 - 0.5))
    collars = [R(K.rrect(x - node_hw, yy - node_h / 2, x + node_hw, yy + node_h / 2, 3.2)) for yy in nodes]
    rachis = K.box(x - rachis_hw, rachis_top - 1.0, x + rachis_hw, knop_y)
    els, lines = [], C.Frag()
    L, W, aw = terminal
    p1, p2 = P(x, rachis_top + 1.5), P(x, rachis_top + 1.5 - L)
    ves = C.vesica_d(p1, p2, W)
    els.append(R(ves))
    lines += C.stroke(ves, MEDIUM, style="point", role="spikelet")
    lines += C.stroke(C.polyline_d([p2, p2 + P(0, -aw)]), HAIR, role="awn")
    for (ry, side, ped, ped_deg, L, W, deg, aw) in female:
        for sd in ((-1, 1) if side == 0 else (side,)):
            p0 = P(x + sd * rachis_hw, ry)
            q = p0 + _u(-90.0 + sd * ped_deg) * ped
            u = _u(-90.0 + sd * deg)
            tip = q + u * L
            ves = C.vesica_d(q, tip, W)
            els.append(R(ves))
            lines += C.stroke(ves, MEDIUM, style="point", role="spikelet")
            lines += K.seg(p0 - P(sd * 1.2, 0), q + u * 1.5, MEDIUM, role="pedicel")
            lines += C.stroke(C.polyline_d([tip, tip + u * aw]), HAIR, role="awn")
    arm_regs, arm_l = [], C.Frag()
    for (ay, reach, rise, sag, aw_, florets) in arms:
        for sd in (-1, 1):
            p0 = P(x + sd * (rachis_hw - 1.0), ay)
            q = P(x + sd * (rachis_hw + reach), ay - rise)
            arm_d = K.arc_sag(p0, q, -sag * sd)
            cv = G.Curve(_pts(arm_d, 0.25))
            rg = LineString(cv.pts).buffer(aw_ / 2, cap_style=1, quad_segs=12)
            arm_regs.append(rg)
            for (t, L, W, hang) in florets:
                b = cv.at_s(min(cv.length * t, cv.length - 0.5))
                u = _u(90.0 - sd * hang)
                b0 = b + u * (aw_ / 2 - 1.0)
                ves = C.vesica_d(b0, b0 + u * L, W)
                els.append(R(ves))
                lines += C.stroke(ves, MEDIUM, style="point", role="floret")
    arms_reg = U(*arm_regs)
    stone = U(*els)
    body = U(culm, rachis, knop, *collars)
    head = U(stone, arms_reg)
    fills = K.fill(body, color) + K.fill(head, color)
    bl = K.clip_out(K.outline(culm), U(knop, *collars), eps=-0.5, trap=0.0)
    bl += K.clip_out(K.outline(rachis), U(knop, *els), eps=-0.5, trap=0.0)
    bl += K.outline(knop)
    for cd in collars:
        bl += K.outline(cd)
    bl += K.clip_out(K.outline(arms_reg), U(knop, stone, rachis), eps=-0.5, trap=0.0)
    return K.Part(U(body, head), fills, bl + lines,
                  {"culm": U(culm, knop, *collars), "head": head, "rachis": rachis})


# =============================================================================
# locks: hair and plumes (§G.24)
# =============================================================================
def _left_is_out(po, pi_):
    """True when the outer edge lies to the screen-left of the inner one
    (travelling root → tip)."""
    k = len(po) // 2
    t = po[min(k + 1, len(po) - 1)] - po[max(k - 1, 0)]
    nl = np.array([t[1], -t[0]])
    j = int(np.argmin(np.hypot(*(pi_ - po[k]).T)))
    return float(np.dot(po[k] - pi_[j], nl)) > 0


def hair_lock(fc, outer, inner, *, n=4, stagger=8.0, face_clip=True, hairline=None, h_outer=None, h_inner=None,
              edge=CONTOUR, color=GOLD, curl_r=4.2, curl_deg=80.0, starts=None, ends=None, tip_sag=0.5,
              guide="outer", first=None):
    """A lock (hair, or a plume when ``color`` is None) between the
    ``outer`` and ``inner`` arc splines (root → tip), minus ``hairline``
    (a region: the skin the lock must leave bare). The tip is closed by an
    arc of sagitta ``tip_sag`` × the tip gap.

    Current lines (§G.24) are offsets of the ``guide`` edge, line k at
    ``first`` + 7k px inside it; ``starts`` (one y per line, or None) lets
    inner lines begin lower down; every line rolls into a Ø6.3 terminal
    (``ends``: extra shortening per line, px). → Part."""
    d_o, po, _ = FM.arc_spline(outer, h_outer)
    d_i, pi_, _ = FM.arc_spline(inner, h_inner)
    po, pi_ = np.asarray(po, float), np.asarray(pi_, float)
    gap = float(np.hypot(*(po[-1] - pi_[-1])))
    if gap < 1.0:
        ring = np.vstack([po, pi_[::-1][1:]])
    else:
        sg = 1 if _left_is_out(po, pi_) else -1
        cap = _pts(K.arc_sag(po[-1], pi_[-1], sg * gap * tip_sag))
        ring = np.vstack([po, cap[1:-1], pi_[::-1]])
    reg = _biggest(Polygon(ring).buffer(0))
    if face_clip and hairline is not None:
        reg = _biggest(reg.difference(R(hairline)))
    reg = reg.buffer(0.6, quad_segs=8).buffer(-0.6, quad_segs=8)
    out_left = _left_is_out(po, pi_)
    if guide == "outer":
        g0, side = po, (+1 if not out_left else -1)
    else:
        g0, side = pi_, (-1 if not out_left else +1)
    first0 = (edge / 2 + K.GAP + FINE / 2 + 0.05) if first is None else first
    starts = starts or [None] * n
    ends = ends or [k * stagger for k in range(n)]
    f = C.Frag()
    placed = Polygon()
    for k in range(n):
        g = g0
        if starts[k] is not None:
            i0 = int(np.argmax(g0[:, 1] >= starts[k]))
            g = g0[i0:]
        if ends[k]:
            Lc = np.cumsum(np.r_[0, np.hypot(*np.diff(g, axis=0).T)])
            g = g[Lc <= Lc[-1] - ends[k]]
        if len(g) < 3:
            continue
        ln = K.current_lines(g, 1, reg, side=side, first=first0 + k * K.PITCH, edge=MEDIUM, stagger=0.0,
                             curl_r=curl_r, curl_deg=curl_deg, placed=placed)
        for q in ln.meta.get("lines", []):
            placed = placed.union(LineString(q).buffer(FINE / 2))
        for m in ln.marks:
            if m.role == "terminal":
                placed = placed.union(R(G.from_skia(m.skia())))
        f += ln
    return K.Part(reg, K.fill(reg, color) if color else C.Frag(), K.outline(reg) + f, {"outer": po, "inner": pi_})


def neck_chest(left, right, bottom=345.0):
    """The paper neck and upper chest: two arc-spline sides (top → down) closed
    below ``bottom`` (hidden by the gown). → Part (paper, MEDIUM outline)."""
    _, pl, _ = FM.arc_spline(left)
    _, pr, _ = FM.arc_spline(right)
    pl, pr = np.asarray(pl), np.asarray(pr)
    ring = np.vstack([pl, [[pl[-1][0], bottom], [pr[-1][0], bottom]], pr[::-1]])
    reg = Polygon(ring).buffer(0)
    return K.Part(reg, C.Frag(), K.outline(reg), {})


def plume(root, heading, length, *, w_max=24.0, bend=(10.0, -40.0), split=0.45, n=3, w_root=7.0, peak=0.40,
          tip_w=0.0, stagger=12.0, curl_deg=80.0, offsets=None, curl_side=None, power=0.8):
    """One egret breeding plume (§H.8 'paper, current lines'): its spine is
    two tangent arcs from ``root`` (``heading``; turning ``bend`` degrees
    over the first ``split`` of the length and the rest — rising, then
    drooping outward), its width swells from ``w_root`` to ``w_max`` at
    ``peak`` and tapers to ``tip_w`` at the tip. ``n`` current lines (§G.24)
    run along it at ``offsets`` from the spine (default 7 px apart, centred)
    and roll into Ø6.3 terminals toward the tip, staggered. Paper: no fill.
    → Part (meta 'mid' spine points)."""
    _, mid, _ = FM.arc_path(root[0], root[1], heading, [(length * split, bend[0]), (length * (1 - split), bend[1])])
    mid = np.asarray(mid, float)
    cv = G.Curve(mid)
    L = cv.length
    s = np.linspace(0, L, 400)
    pts = cv.at_s(s)
    nrm = cv.normal_s(s)
    t = s / L
    hw = np.where(t < peak,
                  w_root / 2 + (w_max - w_root) / 2 * np.sin(np.pi / 2 * t / peak),
                  tip_w / 2 + (w_max - tip_w) / 2 * np.cos(np.pi / 2 * (t - peak) / (1 - peak)) ** power)
    left = pts + nrm * hw[:, None]
    right = pts - nrm * hw[:, None]
    reg = _biggest(Polygon(np.vstack([left, right[::-1]])).buffer(0))
    reg = reg.buffer(0.8, quad_segs=8).buffer(-0.8, quad_segs=8)
    offs = offsets if offsets is not None else [(k - (n - 1) / 2) * K.PITCH for k in range(n)]
    f = C.Frag()
    placed = Polygon()
    cs = curl_side if curl_side is not None else (-1 if bend[1] < 0 else +1)
    for k, o in enumerate(sorted(offs, key=lambda v: -v * cs)):
        g = np.asarray(cv.offset(o, spacing=0.5) if o else cv.resample(0.5))
        Lg = np.cumsum(np.r_[0, np.hypot(*np.diff(g, axis=0).T)])
        g = g[Lg <= Lg[-1] - k * stagger]
        ln = K.current_lines(g, 1, reg, side=cs, first=0.0, edge=MEDIUM, stagger=0.0,
                             curl_r=4.2, curl_deg=curl_deg, placed=placed)
        for q in ln.meta.get("lines", []):
            placed = placed.union(LineString(q).buffer(FINE / 2))
        for m in ln.marks:
            if m.role == "terminal":
                placed = placed.union(R(G.from_skia(m.skia())))
        f += ln
    return K.Part(reg, C.Frag(), K.outline(reg) + f, {"mid": mid, "tip": mid[-1]})
