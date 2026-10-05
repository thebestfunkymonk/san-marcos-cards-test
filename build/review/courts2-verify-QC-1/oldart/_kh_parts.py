"""art/_kh_parts.py — K♥ · The Ferryman King: the parts the kit does not have.

Every builder returns a ``deck.courtkit.Part`` (shape, fills, lines, meta),
drawn at final size in card px, compass-built (arcs, circles, straight
lines), legal widths only. Nothing paper-coloured is painted: knockouts are
holes in the solid.

    pearl_crown    §H.4 pearl-post crown: a gold circlet carrying seven
                   graduated pearls on short posts, the centre one tallest
    pole           the punting pole (the K♥ 'sword behind the head')
    chalice        a gold chalice engraved with a vent rosette
    bubble_column  five graduated bubbles rising from the chalice (§G.9)
    window         the glass-bottom window breastplate: gold frame, jade
                   field, ripple rings, eelgrass, one fountain darter — all
                   knocked out to paper (the card within the card)
    ripple_field   the robe's ripple-ring repeats knocked out of the red
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import geometric as MG
from deck.motifs import forms as FM
from inkkit import geom as G

P, AX = K.P, K.AX
FINE, MEDIUM, RULE, CONTOUR, HAIR_W = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR, K.HAIR_W
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD


# =============================================================================
# crown
# =============================================================================
def pearl_crown(cx=AX, band_top=156.0, band_h=24.0, band_hw=72.0, bow=4.0, *, pitch=20.5,
                heights=(50.0, 38.0, 29.0, 22.0), pearl_d=(17.0, 15.0, 13.5, 12.5), tip_w=7.0, foot_w=None,
                jewel_r=11.5, lustre=True, hatch=True, posts_sil=True):
    """§H.4 the pearl-post crown: a gold circlet (``crown_band``) carrying
    seven graduated pearls on posts, the centre one tallest. Each post is a
    pointed arch standing on the band (full pitch wide at its foot, so the
    posts close into a coronet rim and nothing shows through below the
    pearls) and half-hatched on its outer half like the K♠ merlons; each
    pearl is a gold sphere set on the post's tip with a paper lustre knocked
    out on its upper left — a set pearl, never a free bubble (§H.4
    must-avoid). Returns (crown Part, pearls Part): the pearls are drawn at
    MEDIUM outside the figure's CONTOUR so a 12–17 px pearl stays gold."""
    band, band_d = K.crown_band(cx, band_top, band_h, band_hw, bow)
    posts, pearls, lus, hatch_f, joints = [], [], [], C.Frag(), C.Frag()
    for k in range(-3, 4):
        i = abs(k)
        x = cx + k * pitch
        yb = band_top - bow * (1 - (k * pitch / band_hw) ** 2) + 2.0
        L = heights[i]
        W = pitch + 1.0 if foot_w is None else foot_w
        tip = P(x, yb - L)
        # pointed arch: two convex arcs from the foot corners to a flat tip tip_w wide
        pa = (K.Path((x - W / 2, yb + 4)).line((x - W / 2, yb)).sag((x - tip_w / 2, tip[1]), -W * 0.10)
              .line((x + tip_w / 2, tip[1])).sag((x + W / 2, yb), -W * 0.10).line((x + W / 2, yb + 4)).close())
        post = K.R(pa.d)
        posts.append(post)
        d = pearl_d[i]
        pc = P(x, tip[1] - d / 2 + 3.0)
        pearls.append(Point(*pc).buffer(d / 2, quad_segs=32))
        if lustre:
            lc = pc + P(-0.22, -0.22) * d
            lus.append(Point(*lc).buffer(2.1, quad_segs=16))
        if hatch and k != 0:
            # outer half hatched, split on the post's axis by a FINE joint
            sd = -1 if k < 0 else 1
            hb = post.intersection(K.box(x, 0, 2000, 2000) if sd > 0 else K.box(0, 0, x, 2000))
            hb = hb.difference(band)
            hatch_f += K.hatch_in(hb, angle=-45.0 if sd < 0 else -135.0, origin=(x, yb))
            joints += K.seg((x, tip[1] + 2.0), (x, yb), FINE, role="joint")
    stone = K.U(*posts)
    jw = K.jewel((cx, band_top + band_h / 2 - bow * 0.5 + 0.5), jewel_r)
    post_lines = K.clip_out(K.outline(stone), band, eps=-0.8, trap=0.0)
    post_lines += K.clip_out(hatch_f + joints, band.buffer(0.0), eps=-0.8, trap=0.0)
    band_lines = K.clip_out(K.outline(band_d), jw.shape, eps=0.0, trap=0.0, extra=jw.shape.buffer(4.3 + MEDIUM))
    pl = K.U(*pearls)
    gold_d = K.D(pl.difference(K.U(*lus))) if lus else K.D(pl)
    if posts_sil:
        shape = K.U(stone, band)
        crown = K.Part(shape.union(jw.shape), K.fill(shape, GOLD) + jw.fills, post_lines + band_lines + jw.lines,
                       {"band": band})
        pearl_part = K.Part(pl, K.fill(gold_d, GOLD), K.outline(pl), {"pearls": pearls})
        return crown, pearl_part
    crown = K.Part(band.union(jw.shape), K.fill(band, GOLD) + jw.fills, band_lines + jw.lines, {"band": band})
    top = K.U(stone.difference(band.buffer(-1.0)), pl)
    fills = K.fill(stone, GOLD) + K.fill(gold_d, GOLD)
    post_lines = K.clip_out(post_lines, pl, eps=-0.8, trap=0.0)
    pearl_part = K.Part(top, fills, post_lines + K.outline(pl), {"pearls": pearls})
    return crown, pearl_part


def post_crown(cx=AX, band_top=146.0, band_h=32.0, band_hw=71.0, bow=4.0, *, pitch=21.5,
               heights=(27.0, 22.0, 17.0, 12.5), pearl_d=(18.4, 16.4, 14.8, 13.4), post_w=(12.0, 6.0),
               point_h=0.0, point_w=9.0, jewel_r=11.0, wave=(15.0, 2.2), vanish=700.0):
    """§H.4 the pearl-post crown: a gold circlet (``crown_band``) carrying
    seven graduated pearls on SHORT tapered posts, the centre one tallest,
    with a small gold point standing between each pair of posts (the rhythm
    of a coronet: pearl, point, pearl). The pearls are SOLID gold with an
    Aquifer contour — a set pearl; a paper disc with a ring would read as a
    bubble finial (§H.4 must-avoid). On the circlet: the vent-rosette jewel
    (§G.1 reduced, red core) and, either side of it, a FINE ripple — the ♥
    partition line in miniature (§F.1). Returns (crown Part — band + points,
    in the silhouette; pearls Part — posts and pearls at MEDIUM, outside the
    CONTOUR, so a 12.6 px pearl stays gold)."""
    band, band_d = K.crown_band(cx, band_top, band_h, band_hw, bow)

    def ytop(x):                     # the band's top edge (it dips ``bow`` at the centre: seen from above)
        return band_top - bow * ((x - cx) / band_hw) ** 2
    posts, pearls, points = [], [], []
    w0, w1 = post_w
    for k in range(-3, 4):
        i = abs(k)
        x = cx + k * pitch
        yb = ytop(x) + 3.0
        yt = ytop(x) - heights[i]
        d = pearl_d[i]
        pc = P(x, yt - d / 2 + 2.6)
        # the post leans on a ray from the vanishing point below (the crown flares, like the K♠'s)
        lean = (x - cx) / (vanish - yb) if vanish else 0.0
        xt = x + lean * (yb - yt)
        pc = P(xt + lean * (d / 2 - 2.6), yt - d / 2 + 2.6)
        posts.append(K.R(K.Path((x - w0 / 2, yb)).sag((xt - w1 / 2, yt), -1.2).line((xt + w1 / 2, yt))
                         .sag((x + w0 / 2, yb), -1.2).close().d))
        pearls.append(Point(*pc).buffer(d / 2, quad_segs=32))
        if point_h and k < 3:
            xm = x + pitch / 2
            ym = ytop(xm) + 2.0
            points.append(K.R(K.Path((xm - point_w / 2, ym)).sag((xm, ym - point_h), -1.4)
                              .sag((xm + point_w / 2, ym), -1.4).close().d))
    jw = K.jewel((cx, band_top + band_h / 2), jewel_r)
    # the ripple along the circlet: one sine each side of the jewel, ends on
    # Ø6.3 terminals, clear of the jewel and the band ends
    lam, amp = wave
    wav = C.Frag()
    for sg in (-1, 1):
        xs = np.linspace(jewel_r + 7.5, band_hw - 9.0, 160)
        ymid = [band_top + band_h / 2 - bow * (xx / band_hw) ** 2 for xx in xs]
        pts = np.column_stack([cx + sg * xs, np.asarray(ymid) + sg * amp * np.sin(2 * np.pi * (xs - xs[0]) / lam)])
        wav += K.line(C.polyline_d(pts), FINE, role="wave")
    pt_s = K.U(*points) if points else Polygon()
    shape = K.U(band, pt_s)
    lines = K.clip_out(K.outline(pt_s), band, eps=-0.8, trap=0.0)
    band_lines = K.clip_out(K.outline(band_d), jw.shape, eps=0.0, trap=0.0, extra=jw.shape.buffer(4.3 + MEDIUM))
    crown = K.Part(shape.union(jw.shape), K.fill(shape, GOLD) + jw.fills, lines + band_lines + wav + jw.lines,
                   {"band": band})
    pl = K.U(*pearls)
    ps = K.U(*posts).difference(pl).difference(band.buffer(-0.6))
    top = K.U(ps, pl)
    p_lines = K.clip_out(K.outline(ps), K.U(pl, band), eps=-0.5, trap=0.0) + K.outline(pl)
    return crown, K.Part(top, K.fill(top, GOLD), p_lines, {"pearls": pearls})


def post_crown2(cx=AX, band_top=146.0, band_h=32.0, band_hw=71.0, bow=4.0, *, pitch=21.5,
                heights=(27.0, 22.0, 17.0, 12.5), pearl_d=(18.4, 16.4, 14.8, 13.4), post_w=(12.0, 6.0),
                jewel_r=8.8, wave=(15.0, 2.2), vanish=700.0, sink=4.0):
    """§H.4 the pearl-post crown as three stackable pieces, so the circlet's
    upper edge stays ONE unbroken CONTOUR:

    * ``posts``  seven short tapered posts rising from BEHIND the circlet's
      upper rim (their feet ``sink`` px under it), MEDIUM outlines, not in the
      silhouette — add them before the band;
    * ``band``   the gold circlet (``crown_band``) with the vent-rosette jewel
      (red core) and a FINE ripple either side — the ♥ partition line in
      miniature (§F.1); in the silhouette;
    * ``pearls`` seven graduated SOLID gold pearls (Aquifer MEDIUM contour),
      each set on its post's tip, the centre one tallest — a set pearl, never
      a paper bubble (§H.4 must-avoid); add them after the band, outside the
      silhouette.

    → (band Part, posts Part, pearls Part)."""
    band, band_d = K.crown_band(cx, band_top, band_h, band_hw, bow)

    def ytop(x):
        return band_top - bow * ((x - cx) / band_hw) ** 2
    posts, pearls = [], []
    w0, w1 = post_w
    for k in range(-3, 4):
        i = abs(k)
        x = cx + k * pitch
        yb = ytop(x) + sink
        yt = ytop(x) - heights[i]
        d = pearl_d[i]
        lean = (x - cx) / (vanish - yb) if vanish else 0.0
        xt = x + lean * (yb - yt)
        pc = P(xt + lean * (d / 2 - 2.6), yt - d / 2 + 2.6)
        posts.append(K.R(K.Path((x - w0 / 2, yb)).sag((xt - w1 / 2, yt), -1.2).line((xt + w1 / 2, yt))
                         .sag((x + w0 / 2, yb), -1.2).close().d))
        pearls.append(Point(*pc).buffer(d / 2, quad_segs=32))
    jw = K.jewel((cx, band_top + band_h / 2 + 0.6), jewel_r)
    lam, amp = wave
    wav = C.Frag()
    for sg in (-1, 1):
        xs = np.linspace(jewel_r + 7.5, band_hw - 9.0, 160)
        ymid = [band_top + band_h / 2 - bow * (xx / band_hw) ** 2 for xx in xs]
        pts = np.column_stack([cx + sg * xs, np.asarray(ymid) + sg * amp * np.sin(2 * np.pi * (xs - xs[0]) / lam)])
        wav += K.line(C.polyline_d(pts), FINE, role="wave")
    band_lines = K.outline(band_d)
    band_p = K.Part(band.union(jw.shape), K.fill(band, GOLD) + jw.fills, band_lines + wav + jw.lines, {"band": band})
    pl = K.U(*pearls)
    ps = K.U(*posts).difference(pl)
    post_lines = K.clip_out(K.outline(ps), pl, eps=-0.5, trap=0.0)
    posts_p = K.Part(ps, K.fill(ps, GOLD), post_lines, {"posts": posts})
    pearls_p = K.Part(pl, K.fill(pl, GOLD), K.outline(pl), {"pearls": pearls})
    return band_p, posts_p, pearls_p


# =============================================================================
# pole
# =============================================================================
def pole(p_low, p_high, w=17.0, *, color=GOLD, bands_y=(), band_gap=7.6, band_n=2, wraps=(), wrap_pitch=8.0,
         wrap_slant=7.0):
    """The punting pole: a straight gold shaft ``w`` wide from ``p_low`` to
    ``p_high`` (both usually beyond the clip), with cord BINDINGS: at each y in
    ``bands_y`` a pair of MEDIUM rings square across the shaft, ``band_gap``
    apart (≥ 4.2 of gold between them), butting its outline — a made pole,
    not a rod or a sword."""
    p0, p1 = P(p_low), P(p_high)
    reg = LineString([tuple(p0), tuple(p1)]).buffer(w / 2, cap_style=2)
    u = (p1 - p0) / float(np.hypot(*(p1 - p0)))
    n = np.array([u[1], -u[0]])
    lines = K.outline(reg)
    for y in bands_y:
        t = (y - p0[1]) / u[1]
        c = p0 + u * t
        for k in np.arange(band_n) - (band_n - 1) / 2:
            q = c + u * k * band_gap
            lines += K.clip_in(K.seg(q - n * w, q + n * w, MEDIUM, role="binding"), reg)
    # cord WRAPS (the grip): a spiral of MEDIUM turns ``wrap_pitch`` apart
    # (≥ 4.2 px of gold between parallel strokes), each turn slanting
    # ``wrap_slant`` px along the shaft from one edge to the other, closed
    # by a binding ring at each end
    for (y0, y1) in wraps:
        t0, t1 = sorted(((y0 - p0[1]) / u[1], (y1 - p0[1]) / u[1]))
        for t in np.arange(t0, t1 - wrap_slant + 0.01, wrap_pitch):
            a = p0 + u * t + n * (w / 2 + 2)
            b = p0 + u * (t + wrap_slant) - n * (w / 2 + 2)
            lines += K.clip_in(K.seg(a, b, MEDIUM, role="wrap"), reg)
    return K.Part(reg, K.fill(reg, color), lines, {"p0": p0, "p1": p1, "w": w, "u": u})


# =============================================================================
# chalice
# =============================================================================
def chalice(cx, rim_y, *, rim_hw=26.0, bowl_h=36.0, collar=(9.0, 6.0), stem_hw=5.2, knop=(9.5, 6.5),
            knop_dy=16.0, stem_len=73.0, foot_hw=(7.0, 23.0), foot_h=14.0, lip=5.0, rosette=True,
            color=GOLD):
    """A gold chalice (frontal): a rounded bowl (rim chord at ``rim_y``,
    ``rim_hw`` half-wide, ``bowl_h`` deep) with a lip moulding under the rim,
    a collar under the bowl, a stem with a flattened knop, and a spreading
    bell foot. The bowl is ENGRAVED with a vent rosette (§G.27: outer
    circle, inner ring, straight radial ribs), Aquifer FINE on the gold.
    meta: 'rim' (mouth centre), 'grip' (y range of bare stem for the hand)."""
    x = cx
    yb = rim_y + bowl_h
    stem_bottom = rim_y + bowl_h + stem_len
    # bowl: rim chord, then one circular arc through the bottom
    bowl = K.Path((x - rim_hw, rim_y)).line((x + rim_hw, rim_y)).arc3((x, yb), (x - rim_hw, rim_y)).close()
    bowl_s = K.R(bowl.d)
    ch, cw = collar
    col = K.R(K.rrect(x - cw, yb - 4.0, x + cw, yb + ch, 2.5))
    stem = K.box(x - stem_hw, yb + ch - 1, x + stem_hw, stem_bottom + 2)
    kw, kh = knop
    ky = yb + ch + knop_dy
    kn = K.R(C.ellipse_d(x, ky, kw, kh))
    f0, f1 = foot_hw
    foot = K.R(K.Path((x - f0, stem_bottom)).line((x + f0, stem_bottom))
               .sag((x + f1, stem_bottom + foot_h), 3.5).line((x - f1, stem_bottom + foot_h))
               .sag((x - f0, stem_bottom), 3.5).close().d)
    shape = K.U(bowl_s, col, stem, kn, foot)
    lines = K.outline(shape)
    # lip moulding: a MEDIUM line across the bowl ``lip`` below the rim
    ly = rim_y + lip + MEDIUM
    lip_ln = LineString([(x - rim_hw - 5, ly), (x + rim_hw + 5, ly)]).intersection(bowl_s)
    for ln in K._lines_of(lip_ln):
        lines += K.line(np.asarray(ln.coords), MEDIUM, role="lip")
    # interior division lines: collar top, knop, foot top butt the outline
    lines += K.clip_in(K.seg((x - cw - 3, yb + ch - 1), (x + cw + 3, yb + ch - 1), MEDIUM, role="joint"), col)
    if rosette:
        # the vent rosette (§G.1's crater: rim, hub and curved ribs turning
        # like the boil over a spring vent — straight spokes read as a ship's
        # wheel, the sailor kitsch §H.4 forbids), engraved Aquifer FINE, in
        # the largest circle that keeps 3 px of gold to the lip moulding and
        # to the bowl's CONTOUR (the bowl is one circle through the rim
        # corners and its bottom)
        yc = (rim_hw ** 2 - bowl_h ** 2) / (-2.0 * bowl_h)          # bowl circle centre below the rim
        Rb = bowl_h - yc
        top = lip + MEDIUM + MEDIUM / 2 + 3.0 + FINE / 2             # below the lip moulding
        room = Rb - (FINE / 2 + 3.0 + CONTOUR / 2)                   # c + r ≤ yc + room
        rr = (yc + room - top) / 2
        rc = P(x, rim_y + top + rr)
        lines += MG.crater(rc[0], rc[1], rr, n=6, hub=5.0, twist=48.0, dot_d=None)
    meta = {"rim": P(x, rim_y), "grip": (ky + kh + 2, stem_bottom - 2), "stem_hw": stem_hw}
    return K.Part(shape, K.fill(shape, color), lines, meta)


def bubble_column(pts, sizes, *, w=MEDIUM):
    """Graduated bubbles (§G.9) at points ``pts`` (rising), diameters
    ``sizes``: paper discs with an Aquifer ring (dots below the ring minimum)."""
    shapes, lines = [], C.Frag()
    for p, d in zip(pts, sizes):
        if d - w < 3.0:
            lines += K.dot(p, 6.3)
            shapes.append(Point(*p).buffer(3.15, quad_segs=16))
        else:
            lines += K.line(K.circle(p, d / 2), w, role="bubble")
            shapes.append(Point(*p).buffer(d / 2 + w / 2, quad_segs=24))
    shape = K.U(*shapes)
    return K.Part(shape, C.Frag(), lines, {})


# =============================================================================
# window
# =============================================================================
def window(cx, cy, w=116.0, h=88.0, r=12.0, *, frame=10.0):
    """The glass-bottom window breastplate: a gold frame ``frame`` px wide
    round a jade field (rounded rectangle ``w`` × ``h``, corner ``r``)."""
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    outer_d = K.rrect(x0, y0, x1, y1, r)
    inner_d = K.rrect(x0 + frame, y0 + frame, x1 - frame, y1 - frame, max(r - frame, 3.0))
    outer, inner = K.R(outer_d), K.R(inner_d)
    ring = outer.difference(inner)
    fills = K.fill(ring, GOLD) + K.fill(inner, JADE)
    lines = K.outline(outer_d) + K.outline(inner_d)
    return K.Part(outer, fills, lines, {"inner": inner, "inner_d": inner_d})


# =============================================================================
# robe patterns and trims
# =============================================================================
def _erode(reg, se):
    """Minkowski erosion of ``reg`` by the symmetric structuring element
    ``se`` (a convex region centred on the origin): the points p such that
    se + p lies inside reg."""
    import shapely.affinity as SA
    outside = K.box(-2000, -2000, 3000, 3000).difference(reg)
    ring = []
    for g in K._polys_of(outside):
        ring.append(g)
    # dilate the outside by se (convex): union of se placed along the outside's boundary + outside itself
    bd = outside.boundary
    pts = []
    for ln in K._lines_of(bd):
        L = ln.length
        n = max(2, int(L / 1.5))
        pts += [ln.interpolate(t * L / n) for t in range(n + 1)]
    placed = [SA.translate(se, p.x, p.y) for p in pts]
    grown = shapely.union_all(placed + [outside])
    return reg.difference(grown)


def ripple_group(c, ry=(4.8, 11.2, 19.5), aspect=0.58, dot_d=0.0, w=MEDIUM):
    """One §G.8 ripple-ring group seen on the water: concentric ELLIPSES
    (scaled copies, ry/rx = ``aspect``) whose gaps grow ×1.3 outward, as
    ink marks (to be knocked out of the red). Ellipses read as rings
    spreading on a lake; circles with a centre dot read as a target."""
    f = K.dot(c, dot_d) if dot_d else C.Frag()
    for r in ry:
        f += K.line(C.ellipse_d(c[0], c[1], r / aspect, r), w, role="ripple")
    return f


def ripple_field(region, avoid=None, *, pitch=(50.0, 42.0), origin=(AX, 300.0), ry=(4.8, 11.2, 19.5), aspect=0.58,
                 dot_d=0.0, w=MEDIUM, clear=4.2, mirror=True, under_band=505.0, soft=None, min_visible=0.5):
    """The robe's ripple-ring repeats (§H.4, §G.8) on a half-drop grid,
    mirror-symmetric about the figure axis: a group is placed only where it
    lies wholly inside ``region`` (shrunk by ``clear`` + half the ring
    weight) and clear of ``avoid`` — a ripple is never cut by an arm or a
    trim. → Frag of ink marks (knock them out of the red)."""
    reg = K.R(region)
    rx, ry_ = max(ry) / aspect + w / 2, max(ry) + w / 2
    grp = shapely.affinity.scale(Point(0, 0).buffer(1.0, quad_segs=32), rx + clear, ry_ + clear)
    # the centres where a whole group fits: an erosion by the group's own ellipse
    inner = reg.difference(avoid) if (avoid is not None and not avoid.is_empty) else reg
    if under_band:
        # the band hides the cut: a group may run on under it (like the K♠ strata)
        inner = inner.union(K.box(0, under_band, 750, 700).intersection(reg.buffer(0.0)))
        if avoid is not None and not avoid.is_empty:
            inner = inner.difference(avoid)
    inner = _erode(inner, grp)
    px, py = pitch
    ox, oy = origin
    x0, y0, x1, y1 = reg.bounds
    f = C.Frag()
    seen = set()
    for j in range(int((y0 - oy) // py) - 1, int((y1 - oy) // py) + 2):
        off = px / 2 if j % 2 else 0.0
        for i in range(int((x0 - ox) // px) - 2, int((x1 - ox) // px) + 3):
            x, y = ox + off + i * px, oy + j * py
            if x > AX + 0.01 and mirror:
                continue
            if not inner.contains(Point(x, y)):
                continue
            key = (round(x, 2), round(y, 2))
            if key in seen:
                continue
            seen.add(key)
            g = ripple_group((x, y), ry, aspect, dot_d, w)
            if soft is not None and not soft.is_empty:
                # a group may pass behind an arm or the pole (the cloth runs on
                # under it) but never mostly hidden: keep it only if at least
                # ``min_visible`` of its ellipse shows
                ell = shapely.affinity.scale(Point(x, y).buffer(1.0, quad_segs=32), rx, ry_)
                vis = ell.difference(soft).intersection(K.box(0, 0, 750, 511)).area / ell.area
                if vis < min_visible:
                    continue
            f += g
            if mirror and abs(x - AX) > 0.01 and inner.contains(Point(2 * AX - x, y)):
                f += g.mirror_x(AX)
    return f


def ripple_textile(region, *, ry=(3.6, 9.8, 17.8), aspect=0.46, pitch=(96.0, 34.0), origin=(AX, 300.0), w=MEDIUM,
                   inset=9.0, mirror=True, min_piece=10.0):
    """The robe's ripple-ring repeat (§H.4 'ripple-ring repeats', §G.8) as a
    TEXTILE: groups of three concentric flat ellipses (rings spreading on a
    lake, seen in perspective; gaps ≥ 6.2 on the minor axis so ≥ 3 px of red
    stays between the knockout lines) on a half-drop lattice whose rows nest
    like scales, clipped to ``region`` inset ``inset`` px (a plain edge: no
    ring grazes the silhouette). Garments and arms in front occlude it like
    cloth. Mirror-symmetric about the axis. → Frag of ink marks to knock out."""
    reg = K.R(region).buffer(-inset)
    px, py = pitch
    ox, oy = origin
    x0, y0, x1, y1 = reg.bounds
    f = C.Frag()
    for j in range(int((y0 - oy) // py) - 2, int((y1 - oy) // py) + 3):
        off = px / 2 if j % 2 else 0.0
        for i in range(int((x0 - ox) // px) - 2, int((x1 - ox) // px) + 3):
            x, y = ox + off + i * px, oy + j * py
            if mirror and x > AX + 0.01:
                continue
            g = ripple_group((x, y), ry, aspect, 0.0, w)
            if mirror and abs(x - AX) > 0.01:
                g = g + g.mirror_x(AX)
            f += g
    f = K.clip_in(f, reg)
    # drop crumbs: arcs shorter than min_piece
    out = []
    for m in f.marks:
        segs = [p for p, _ in G.flatten(m.d, 0.1) if len(p) > 1 and G.Curve(np.asarray(p)).length >= min_piece]
        if segs:
            from dataclasses import replace as _rp
            out.append(_rp(m, d="".join(C.polyline_d(np.asarray(p)) for p in segs)))
    return C.Frag(out, f.meta)


def pearl_trim(path_pts, *, d=8.4, gap=4.6, color=GOLD, outline_w=FINE, start=0.0, end=None, keep=None,
               avoid=None, mirror=False):
    """Gold pearl beading (§G.29) along a polyline: solid gold pearls Ø``d``
    with an Aquifer FINE contour (legal on red, §C.4), ``gap`` clear between
    contours. A pearl is kept only inside ``keep`` and clear of ``avoid``
    (never half a pearl); ``mirror`` adds the mirror image about the axis
    (a pearl is kept only if its twin is too). Each pearl is atomic.
    → (Frag, shapely region)."""
    cv = G.Curve(np.asarray(path_pts, float))
    L = cv.length if end is None else end
    step = d + outline_w + gap
    f = C.Frag()
    shapes = []
    s = start + d / 2 + outline_w
    n = 0
    rr = d / 2 + outline_w / 2
    while s <= L - d / 2 - outline_w:
        p = cv.at_s(s)
        s += step
        cands = [p] + ([P(2 * AX - p[0], p[1])] if mirror else [])
        disc = [Point(*q).buffer(rr, quad_segs=16) for q in cands]
        if keep is not None and not all(keep.contains(g) for g in disc):
            continue
        if avoid is not None and any(avoid.intersects(g) for g in disc):
            continue
        for q, g in zip(cands, disc):
            m = K.fill(K.circle(q, d / 2), color, role="pearl") + K.outline(K.circle(q, d / 2), outline_w, role="pearl")
            f += K.atomic(m, f"pearl{n}_{round(q[0])}_{round(q[1])}")
            shapes.append(g)
        n += 1
    return f, K.U(*shapes)


# =============================================================================
# lapels: the §G.16 scale-lattice trim
# =============================================================================
def trim_lapel(ls, side, robe_shape, *, shoulder_x=300.0, collar_sag=-4.0, r=9.0, color=JADE, bead_off=10.6):
    """The robe's front trim (§H.4 robe; §G.16 'scale lattice … K♥'s trim'):
    the kit's lapel band on the lens arc, in jade, carrying a scale lattice
    in Aquifer FINE that butts its outline. meta 'outer_pts': a polyline
    ``bead_off`` px outside the band's outer edge (on the red), from the
    shoulder to the band, for the pearl beading."""
    lp = K.lapel(ls, -1, robe_shape, shoulder_x=shoulder_x, collar_sag=collar_sag, bubbles=False, color=color)
    reg = lp.shape
    sc = MG.scale_lattice(reg, r, origin=(ls.cx - r, 250.0))
    oc, orad = lp.meta["outer_c"], lp.meta["outer_r"]
    S_o, B_o = lp.meta["S_o"], lp.meta["B_o"]
    a0, a1 = K.ang(oc, S_o), K.ang(oc, B_o)
    if abs(a1 - a0) > 180:
        a1 += 360 if a1 < a0 else -360
    th = np.radians(np.linspace(a0, a1, 300))
    rr = orad + bead_off
    pts = np.column_stack([oc[0] + rr * np.cos(th), oc[1] + rr * np.sin(th)])
    part = K.Part(reg, lp.fills, lp.lines + sc, {**lp.meta, "outer_pts": pts})
    if side > 0:
        part = part.mirrored(ls.cx)
        part.meta["outer_pts"] = np.column_stack([2 * ls.cx - pts[:, 0], pts[:, 1]])
    return part


# =============================================================================
# scene: the CONTOUR stops under designated non-silhouette parts
# =============================================================================
class Scene(K.Scene):
    """courtkit.Scene, plus ``over_contour``: names of NON-silhouette items
    (drawn at MEDIUM: the crown's pearl posts, the bubbles) that lie in
    front of a silhouette edge. The kit strokes the silhouette CONTOUR on top
    of everything; here that CONTOUR stops under those items' outlines, so a
    pearl in front of the pole or a bubble rising across the neckline stays
    whole. (Upstream candidate: ``Scene.add(..., over_contour=True)``.)"""

    def __init__(self, *a, over_contour=(), **kw):
        super().__init__(*a, **kw)
        self.over_contour = dict(over_contour) if isinstance(over_contour, dict) else tuple(over_contour)

    def compose(self, contour=CONTOUR, extra_front=None, heal_gaps=True):
        res = super().compose(contour=None, extra_front=extra_front, heal_gaps=False)
        if contour:
            sl = K.silhouette_line(self.silhouette(), contour)
            oc = self.over_contour if isinstance(self.over_contour, dict) else {n: -0.8 for n in self.over_contour}
            for name, eps in oc.items():
                mask = self.region((name,))
                if isinstance(eps, tuple):          # (eps, region the mask must stay out of)
                    eps, away = eps
                    mask = mask.difference(away)
                if not mask.is_empty:
                    # eps > 0: the CONTOUR's centreline stops eps px OUTSIDE the
                    # item, so its round cap ends on the item's MEDIUM outline
                    # instead of intruding into its fill
                    sl = K.clip_out(sl, mask, eps=eps, trap=0.0)
            res += sl
        if self.rank is not None:
            from deck import frames as _F
            res = K.clip_in(res, K.R(_F.court_clip_d(self.rank, self.cut_y)), self.clip_tol)
        if heal_gaps:
            self.heal_log = []
            if self.rank is not None:
                band = C.stroke(f"M100 {self.cut_y:.3f}L650 {self.cut_y:.3f}", FINE, style="rule", role="_band")
                res = K.heal(res + band, log=self.heal_log, keep_roles=("contour", "_band"))
                res = res.select(lambda m: m.role != "_band")
            else:
                res = K.heal(res, log=self.heal_log)
        return res


# =============================================================================
# v4: the robe with a plain border, and the trimmed cuffs
# =============================================================================
def robe(ms, *, border=32.0, ry=(3.6, 9.8, 17.8), aspect=0.46, pitch=(96.0, 34.0), origin=(AX, 300.0),
         inset=1.6, color=RED):
    """The Gill Red robe (§H.4): the kit mantle outline, a plain border
    ``border`` px wide inside the whole outer edge closed by a FINE Aquifer
    seam (the K♠ construction: no pattern line ever grazes the silhouette),
    and inside it the ripple-ring repeat knocked out to paper (§G.8 groups
    of three flat ellipses on a half-drop lattice, cut by the seam like a
    printed textile). → (Part, ripple Frag, inner region). The robe's fill is
    built later (``robe_fill``) so the rings are knocked out only where
    nothing in front hides them."""
    m = K.mantle(ms, color=color, border=border, seam=True)
    inner = m.meta["inner"]
    rip = ripple_textile(inner, ry=ry, aspect=aspect, pitch=pitch, origin=origin, inset=inset)
    return m, rip, inner


def lattice_cuff(cuff: K.Part, *, r=6.0, origin=None, color=JADE):
    """A cuff in the trim cloth: ``color`` with the §G.16 scale lattice
    (Aquifer FINE) that the robe's front trims carry."""
    reg = cuff.shape
    x0, y0, x1, y1 = reg.bounds
    sc = MG.scale_lattice(reg, r, origin=origin or (x0, y0 - r))
    return K.Part(reg, K.fill(reg, color), cuff.lines + sc, cuff.meta)
