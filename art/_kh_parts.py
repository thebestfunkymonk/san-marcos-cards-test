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
    ring_clear     the robe's rings against the parts in front (near misses,
                   shallow crossings, a front outline's corners: ``front_corners``)
    band_top_contour  the circlet's top edge as one CONTOUR over the pole
    Scene          courtkit.Scene + over_contour / extra_contour / stroke_ends
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


def band_top_contour(band, region, *, inset=3.0, w=CONTOUR):
    """The circlet's upper edge, stroked ``w`` (the silhouette CONTOUR),
    where it crosses ``region`` (the pole behind it): ``post_crown2`` keeps
    that edge ONE unbroken CONTOUR — a pole passing behind the circlet
    would otherwise stop it on each side in a round cap (a knot at a post's
    foot). ``inset``: px kept off the band's two side ends. → Frag."""
    x0, y0, x1, y1 = band.bounds
    top = band.boundary.intersection(K.box(x0 + inset, y0 - 1.0, x1 - inset, y0 + 6.0))
    top = top.intersection(K.R(region))
    f = C.Frag()
    for ln in K._lines_of(shapely.line_merge(top) if top.geom_type == "MultiLineString" else top):
        if ln.length > 1.0:
            f += K.line(C.polyline_d(np.asarray(ln.coords)), w, role="contour")
    return f


# =============================================================================
# pole
# =============================================================================
def pole(p_low, p_high, w=17.0, *, color=GOLD, bands_y=(), band_gap=7.6, band_n=2, wraps=(), wrap_pitch=8.0,
         wrap_slant=7.0, round_low=False):
    """The punting pole: a straight gold shaft ``w`` wide from ``p_low`` to
    ``p_high`` (both usually beyond the clip), with cord BINDINGS: at each y in
    ``bands_y`` a pair of MEDIUM rings square across the shaft, ``band_gap``
    apart (≥ 4.2 of gold between them), butting its outline — a made pole,
    not a rod or a sword. ``round_low``: the low end is the pole's butt, seen
    just below the hand (a rounded end instead of running out of the clip)."""
    p0, p1 = P(p_low), P(p_high)
    reg = LineString([tuple(p0), tuple(p1)]).buffer(w / 2, cap_style=2)
    if round_low:
        reg = reg.union(Point(*p0).buffer(w / 2, quad_segs=16))
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
            color=GOLD, tip_r=0.0, engrave_gap=3.0):
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
    if tip_r:
        # the foot's rim tips rounded: a knife-edge tip loses its outline to heal
        foot = foot.buffer(-tip_r, quad_segs=12).buffer(tip_r, quad_segs=12)
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
        top = lip + MEDIUM + MEDIUM / 2 + engrave_gap + FINE / 2     # below the lip moulding
        room = Rb - (FINE / 2 + engrave_gap + CONTOUR / 2)           # c + r ≤ yc + room
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
    # every ring's start vertex (where its path opens: see close_starts)
    starts = [(p[0], p[-1]) for m in f.marks for p, c in G.flatten(m.d, 0.1) if c and len(p) > 2]
    f = K.clip_in(f, reg)
    # drop crumbs: arcs shorter than min_piece
    out = []
    for m in f.marks:
        segs = [p for p, _ in G.flatten(m.d, 0.1) if len(p) > 1 and G.Curve(np.asarray(p)).length >= min_piece]
        if segs:
            from dataclasses import replace as _rp
            out.append(_rp(m, d="".join(C.polyline_d(np.asarray(p)) for p in segs)))
    return C.Frag(out, {**(f.meta or {}), "starts": starts})


def pearl_trim(path_pts, *, d=8.4, gap=4.6, color=GOLD, outline_w=FINE, start=0.0, end=None, keep=None,
               avoid=None, mirror=False, min_run=1):
    """Gold pearl beading (§G.29) along a polyline: solid gold pearls Ø``d``
    with an Aquifer FINE contour (legal on red, §C.4), ``gap`` clear between
    contours. A pearl is kept only inside ``keep`` and clear of ``avoid``
    (never half a pearl); ``mirror`` adds the mirror image about the axis
    (a pearl is kept only if its twin is too). Each pearl is atomic.
    ``min_run``: pearls are kept only in runs of at least this many
    consecutive places (a lone pearl cut off by the pole reads as a stray dot).
    → (Frag, shapely region)."""
    cv = G.Curve(np.asarray(path_pts, float))
    L = cv.length if end is None else end
    step = d + outline_w + gap
    f = C.Frag()
    shapes = []
    s = start + d / 2 + outline_w
    n = 0
    rr = d / 2 + outline_w / 2
    slots = []                      # (cands, discs) or None, one per place along the path
    while s <= L - d / 2 - outline_w:
        p = cv.at_s(s)
        s += step
        cands = [p] + ([P(2 * AX - p[0], p[1])] if mirror else [])
        disc = [Point(*q).buffer(rr, quad_segs=16) for q in cands]
        ok = not (keep is not None and not all(keep.contains(g) for g in disc))
        ok = ok and not (avoid is not None and any(avoid.intersects(g) for g in disc))
        slots.append((cands, disc) if ok else None)
    runs, cur = [], []
    for sl in slots + [None]:
        if sl is None:
            if cur:
                runs.append(cur)
            cur = []
        else:
            cur.append(sl)
    for run in runs:
        if len(run) < min_run:
            continue
        for cands, disc in run:
            for q, g in zip(cands, disc):
                m = K.fill(K.circle(q, d / 2), color, role="pearl") + K.outline(K.circle(q, d / 2), outline_w,
                                                                               role="pearl")
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


def tuck_lens(lp: K.Part, pole: K.Part, cx=AX, *, r=7.0, scales=True, min_gap=4.6):
    """The lens of lapel the pole leaves on its far side, tucked under the
    pole instead of running into its edge at a ≈ 20° taper: near the lens tip
    the lapel's outer edge leaves its arc on a fillet of radius ``r`` that
    meets the pole's edge SQUARE (the fillet's centre lies on that edge), so
    the red it gives back meets the pole at 90° too — no wedge. ``scales``:
    the lens keeps its share of the lattice (the pattern runs on across the
    pole) except FINE pieces that would end < ``min_gap`` from the pole's
    outline without reaching it. → (Part, tip point or None)."""
    rest = sorted(K._polys_of(lp.shape.difference(pole.shape)), key=lambda g: g.area)
    if len(rest) < 2:
        return lp, None
    lens = rest[0]
    u = P(pole.meta["u"])                      # up the pole
    w = float(pole.meta["w"])
    n = P(u[1], -u[0])
    p0 = P(pole.meta["p0"])
    if (P(lens.centroid.coords[0]) - p0) @ n < 0:
        n = -n                                   # toward the lens
    e0 = p0 + n * (w / 2)                        # a point on the pole's lens-side edge
    oc, orad = P(lp.meta["outer_c"]), float(lp.meta["outer_r"])
    so = P(lp.meta["S_o"])
    if abs(float(np.hypot(*(so - oc))) - orad) > 0.5:
        oc = P(2 * cx - oc[0], oc[1])            # a mirrored lapel that kept the other side's centre
    # the edge line x(t) = e0 + t u meets the outer circle: |e0 + t u - oc| = orad
    d0 = e0 - oc
    b, c = float(d0 @ u), float(d0 @ d0) - orad ** 2
    disc = b * b - c
    if disc <= 0:
        return lp, None
    ts = [-b - np.sqrt(disc), -b + np.sqrt(disc)]
    cand = [e0 + t * u for t in ts]
    X = min(cand, key=lambda q: Point(*q).distance(lens))
    if Point(*X).distance(lens) > 1.0:
        return lp, None
    # the fillet: centre C = X + t u on the edge line, |C - oc| = orad - r (inside the arc's circle)
    # or orad + r — whichever side the lens lies on
    inside = Point(*(oc + (P(lens.representative_point().coords[0]) - oc))).distance(Point(*oc)) < orad
    target = orad - r if inside else orad + r
    lo_t, hi_t = 0.0, 200.0
    sgn = 1.0 if (P(lens.centroid.coords[0]) - X) @ u > 0 else -1.0
    f = lambda t: float(np.hypot(*(X + sgn * t * u - oc))) - target
    if f(lo_t) * f(hi_t) > 0:
        return lp, None
    for _ in range(60):
        mid = (lo_t + hi_t) / 2
        if f(lo_t) * f(mid) <= 0:
            hi_t = mid
        else:
            lo_t = mid
    C_ = X + sgn * hi_t * u
    T = oc + (C_ - oc) / np.hypot(*(C_ - oc)) * orad       # tangent point on the arc
    Pp = C_ - sgn * r * u                                   # square on the pole's edge
    # cut: the lens on X's side of the chord T–Pp, outside the fillet disc
    m = (T + Pp) / 2
    dn = P(-(Pp - T)[1], (Pp - T)[0])
    if (X - m) @ dn < 0:
        dn = -dn
    dn = dn / np.hypot(*dn)
    half = shapely.Polygon([tuple(T - (Pp - T) * 3), tuple(Pp + (Pp - T) * 3),
                            tuple(Pp + (Pp - T) * 3 + dn * 80), tuple(T - (Pp - T) * 3 + dn * 80)])
    cut = lens.intersection(half).difference(Point(*C_).buffer(r, quad_segs=32))
    shape = lp.shape.difference(cut.buffer(0.02))
    shape = max(K._polys_of(shape), key=lambda g: g.area) if shape.geom_type != "Polygon" else shape
    sc_ = lp.lines.select(lambda mk: mk.role == "scale")
    others = lp.lines.select(lambda mk: mk.role not in ("scale", "outline"))
    if scales:
        sc_ = K.clip_in(sc_, shape)
        sc_ = _scales_clear(sc_, lens, pole.shape, min_gap)
    else:
        sc_ = K.clip_in(sc_, shape.difference(lens.buffer(0.5)))
    fills = K.fill(shape, lp.fills.marks[0].color) if lp.fills.marks else C.Frag()
    return K.Part(shape, fills, K.outline(shape) + others + sc_, lp.meta), (T, Pp, C_)


def _scales_clear(sc_: C.Frag, lens, front, min_gap, tol=0.05):
    """Scale-lattice strokes inside ``lens`` (a strip beside ``front``) that
    end — or run — within ``min_gap`` of ``front``'s outline without running
    under it (a graze: heal would cut them into free caps) lose those runs.
    → Frag."""
    front = K.R(front)
    fin = front.buffer(-0.3, quad_segs=6)
    near = front.buffer(min_gap, quad_segs=8).intersection(lens.buffer(1.0))
    out = []
    from dataclasses import replace as _rp
    for mk in sc_.marks:
        keep = []
        for p, closed in G.flatten(mk.d, tol):
            if len(p) < 2:
                continue
            ln = LineString(np.vstack([p, p[:1]]) if closed else p)
            vis = ln.difference(fin)
            bad = []
            for comp in K._lines_of(shapely.line_merge(vis.intersection(near)) if not vis.is_empty else vis):
                if comp.length < 0.3:
                    continue
                if comp.distance(front) > 0.4:          # a near miss: never reaches the pole
                    bad.append(comp)
                elif comp.length > 2.5 * min_gap:       # slides along the pole's edge
                    bad.append(comp)
            if bad:
                ln = ln.difference(shapely.union_all([bb.buffer(0.9, cap_style=2) for bb in bad]))
            for piece in K._lines_of(shapely.line_merge(ln) if ln.geom_type != "LineString" else ln):
                if piece.difference(fin).length >= 3.0:
                    keep.append(np.asarray(piece.coords))
        if keep:
            out.append(_rp(mk, d="".join(C.polyline_d(q) for q in keep)))
    return C.Frag(out, sc_.meta)


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

    def __init__(self, *a, over_contour=(), extra_contour=None, stroke_ends=None, fillets=(), **kw):
        super().__init__(*a, **kw)
        # [(point, r)]: the silhouette's re-entrant corner at ``point`` filled on radius r
        # before it is stroked — where the robe's shoulder meets the chalice bowl, the
        # CONTOUR's round join (Ø 6.25) pushed a 1.5 px nub into the gold below it, past
        # the bowl's MEDIUM outline; on the fillet the join is smooth and stays inside
        self.fillets = list(fillets)
        self.over_contour = dict(over_contour) if isinstance(over_contour, dict) else tuple(over_contour)
        # CONTOUR strokes added after the over_contour cuts (a silhouette edge kept whole where
        # something behind it — the pole behind the crown's circlet — would break it)
        self.extra_contour = extra_contour
        # {item name: eps}: every STROKE behind that item ends eps px OUTSIDE its region
        # (on its MEDIUM outline) instead of the kit's 0.2 px inside — a line meeting a
        # small convex front shape (a fist) no longer shows its round cap as a nub
        # inside the outline (the chalice stem and the pole on the fists)
        self.stroke_ends = dict(stroke_ends or {})

    def _end_strokes(self):
        names = [it.name for it in self.items]
        for tname, eps in self.stroke_ends.items():
            if tname not in names:
                continue
            k = names.index(tname)
            zone = self.items[k].occ
            if zone is None or zone.is_empty:
                continue
            for it in self.items[:k]:
                if not it.frag or not it.frag.marks:
                    continue
                st = it.frag.select(lambda m: m.kind == "stroke")
                if not st.marks:
                    continue
                g = shapely.union_all([K.R(G.from_skia(m.skia())) for m in st.marks])
                if not g.intersects(zone.buffer(eps + 3.5)):
                    continue
                rest = it.frag.select(lambda m: m.kind != "stroke")
                it.frag = rest + K.clip_out(st, zone, eps=eps, trap=0.0)

    def compose(self, contour=CONTOUR, extra_front=None, heal_gaps=True):
        if self.stroke_ends:
            self._end_strokes()
            self.stroke_ends = {}          # once (compose may be called again)
        res = super().compose(contour=None, extra_front=extra_front, heal_gaps=False)
        if contour:
            sil = self.silhouette()
            for q, r in self.fillets:
                zone = Point(*q).buffer(3.0 * r, quad_segs=16)
                sil = sil.union(sil.buffer(r, quad_segs=24).buffer(-r, quad_segs=24).intersection(zone))
            sl = K.silhouette_line(sil, contour)
            oc = self.over_contour if isinstance(self.over_contour, dict) else {n: -0.8 for n in self.over_contour}
            for name, eps in oc.items():
                mask = self.region((name,))
                if isinstance(eps, tuple):          # (eps, region the mask must stay out of)
                    eps, away = eps
                    mask = mask.difference(away)
                if mask.is_empty:
                    continue
                # eps > 0: the CONTOUR's centreline stops eps px OUTSIDE the
                # item, so its round cap ends on the item's MEDIUM outline
                # instead of intruding into its fill
                sl = K.clip_out(sl, mask, eps=eps, trap=0.0)
            res += sl
            if self.extra_contour is not None:
                res += self.extra_contour
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
    lines = cuff.lines + sc
    return K.Part(reg, K.fill(reg, color), lines + plug_pockets(reg, lines), cuff.meta)


def plug_pockets(reg, lines: C.Frag, *, max_area=0.6, thin=0.55, w=FINE):
    """Aquifer plugs for the crumbs of ground a lattice leaves inside ``reg``
    between its own strokes (a jade speck < ``max_area`` px² AND thinner
    than 2 × ``thin``): invisible at print size, but heal measures them as
    separate pieces and cuts back the NEIGHBOUR's outline — the hand in front
    of K♥'s right cuff lost 3.9 px of its wrist line to a 0.3 px² jade crumb
    (a red speck at the junction). Each plug is a FINE dot/dash of the
    lattice's own style (it joins the lattice's piece: heal never sees it
    alone) lying wholly inside the crumb and the ink round it — no ink is
    added anywhere it shows. → Frag (strokes, role 'scale')."""
    st = [K.R(G.from_skia(m.skia())) for m in lines.marks if m.kind == "stroke" and m.d]
    if not st:
        return C.Frag()
    ink = shapely.union_all(st)
    ground = K.R(reg).difference(ink)
    out = C.Frag()
    for pg in K._polys_of(ground):
        if not (pg.area < max_area and pg.buffer(-thin).is_empty):
            continue                             # (larger crescents stay: plugging them makes an ink
                                                 # solid wider than a CONTOUR over the jade, QA 4c)
        rect = np.asarray(pg.minimum_rotated_rectangle.exterior.coords)[:4]
        e1, e2 = rect[1] - rect[0], rect[2] - rect[1]
        ax_ = e1 if np.hypot(*e1) >= np.hypot(*e2) else e2
        L = float(np.hypot(*ax_))
        u = ax_ / max(L, 1e-9)
        c = np.asarray(pg.minimum_rotated_rectangle.centroid.coords[0])
        allowed = ink.union(pg).buffer(0.05)
        for k in range(12):
            half = max(0.0, L / 2 - w / 2) * (1 - k / 11)
            a, b = c - u * half, c + u * half
            seg = LineString([a, b]) if half > 0 else Point(*c)
            dab = seg.buffer(w / 2, quad_segs=12)
            if dab.contains(pg.buffer(-0.02)) and allowed.contains(dab):
                out += C.stroke(C.polyline_d([a, b if half > 0 else a + u * 1e-3]), w, role="scale")
                break
    return out


# =============================================================================
# the robe's rings against everything in front of the robe
# =============================================================================
def front_corners(front, *, turn=38.0, min_seg=0.6):
    """The sharp corners of ``front``'s outline (every ring of every
    polygon): vertices where the outline turns more than ``turn``° — the
    junctions of a hand and its cuff, a cuff's corners, a foot's tips.
    → list of screen points."""
    out = []
    for pg in K._polys_of(K.R(front)):
        for ring in (pg.exterior, *pg.interiors):
            c = np.asarray(ring.coords)[:-1]
            n = len(c)
            if n < 3:
                continue
            for i in range(n):
                a, b, d = c[i - 1], c[i], c[(i + 1) % n]
                v1, v2 = b - a, d - b
                l1, l2 = float(np.hypot(*v1)), float(np.hypot(*v2))
                if l1 < min_seg or l2 < min_seg:
                    continue
                t = math.degrees(math.acos(max(-1.0, min(1.0, float(v1 @ v2) / l1 / l2))))
                if t > turn:
                    out.append(P(b))
    return out


def ring_clear(rip: C.Frag, front, *, near=7.3, cross_max=14.6, min_vis=10.0, tol=0.1, hide=None,
               corners=(), corner_r=7.3):
    """The robe's ripple rings (ink marks to be knocked out of the red)
    against the parts in front of the robe (``front``: their union). Where a
    ring's VISIBLE run comes within ``near`` px of a front outline without
    going under it (a near miss: a paper ring hugging a chalice foot or a
    sleeve), or slides under it at a shallow angle (a run > ``cross_max`` px
    inside that band), the ring is cut there — heal would otherwise trim the
    front part's OUTLINE, not the ring. Visible remnants shorter than
    ``min_vis`` are dropped (no paper crumbs); ``hide``: parts in front that
    only hide rings (counted for the crumbs, never cut against). ``corners``:
    points (a hand meeting its cuff, a cuff's corner) no visible ring may
    come within ``corner_r`` of — a ring slipping under the outline AT a
    corner pinches a red wedge there and heal trims the outline. → Frag."""
    front = K.R(front)
    fz = front.buffer(near, quad_segs=8)
    fin = front.buffer(-0.3, quad_segs=6)
    fin_all = fin.union(K.R(hide).buffer(-0.3, quad_segs=6)) if hide is not None else fin
    bad = []
    if len(corners):
        bad.append(shapely.union_all([Point(*q).buffer(corner_r, quad_segs=8) for q in corners]).difference(fin))
    for m in rip.marks:
        for p, closed in G.flatten(m.d, tol):
            if len(p) < 2:
                continue
            pts = np.vstack([p, p[:1]]) if closed else np.asarray(p)
            ln = LineString(pts)
            vis = ln.difference(fin)
            if vis.is_empty:
                continue
            nearv = vis.intersection(fz)
            if vis.length < 3.0 * near and nearv.length > 0.7 * vis.length:
                # a short arc that only dips under a front part's corner: all of it hugs
                bad.append(vis.buffer(0.9, cap_style=2))
                continue
            for comp in K._lines_of(shapely.line_merge(nearv)):
                if comp.length < 0.5:
                    continue
                touches = comp.distance(front) < 0.4
                if (not touches) or comp.length > cross_max:
                    bad.append(comp.buffer(0.9, cap_style=2))
    if bad:
        rip = K.clip_out(rip, shapely.union_all(bad), eps=0.0, trap=0.0)
    # every visible run shorter than a crumb goes (a ring end peeping 1–3 px out
    # from under a hand or a sleeve reads as a paper speck on its outline)
    short = []
    for m in rip.marks:
        for p, closed in G.flatten(m.d, tol):
            if len(p) < 2:
                continue
            pts = np.vstack([p, p[:1]]) if closed else np.asarray(p)
            for comp in K._lines_of(shapely.line_merge(LineString(pts).difference(fin_all))):
                if comp.length < min_vis:
                    short.append(comp.buffer(0.9, cap_style=2))
    if short:
        rip = K.clip_out(rip, shapely.union_all(short), eps=0.0, trap=0.0)
    # drop remnants whose visible length is a crumb
    out = []
    for m in rip.marks:
        keep = []
        for p, closed in G.flatten(m.d, tol):
            if len(p) < 2:
                continue
            pts = np.vstack([p, p[:1]]) if closed else np.asarray(p)
            ln = LineString(pts)
            if ln.difference(fin_all).length >= min_vis:
                keep.append(pts)
        if keep:
            from dataclasses import replace as _rp
            out.append(_rp(m, d="".join(C.polyline_d(q) for q in keep)))
    return C.Frag(out, rip.meta)


def close_starts(rip: C.Frag, starts, *, tol=0.05) -> C.Frag:
    """Close the seam every ripple ring carries at its start vertex (its left
    vertex; the right one when mirrored): ``ripple_textile`` re-emits each ring
    as an OPEN polyline, so the flattened ring's last segment — last point →
    start vertex, ≈ 1 px — is missing, and two round-capped ends meet on the
    ellipse's vertex: once knocked out of the red, a 0.5–1 px pinch.
    ``starts``: (start vertex, last point) of every ring. Here a run starting
    on a start vertex takes back the run (or its own other end) that stops on
    that ring's last point — the missing segment, nothing a clip removed;
    which pieces are visible is NOT changed (every clip upstream saw the open
    rings). → Frag."""
    S = [np.asarray(q[0], float) for q in (starts or ())]
    LAST = [np.asarray(q[1], float) for q in (starts or ())]
    if not S:
        return rip
    tree = shapely.STRtree([Point(*q) for q in S])
    from dataclasses import replace as _rp
    out = []
    for m in rip.marks:
        runs = [np.asarray(p, float) for p, c in G.flatten(m.d, 0.02) if len(p) >= 2]
        closed = [False] * len(runs)
        changed = True
        while changed:
            changed = False
            for i, a in enumerate(runs):
                if a is None or closed[i]:
                    continue
                for k in tree.query(Point(*a[0]).buffer(tol)):
                    sv, lv = S[int(k)], LAST[int(k)]
                    if np.hypot(*(a[0] - sv)) > tol:
                        continue
                    # this run starts on a ring's start vertex: find the run that stops just short of it
                    best = None
                    for j, b in enumerate(runs):
                        if b is None or closed[j]:
                            continue
                        for rev in (False, True):
                            e = b[0] if rev else b[-1]
                            dd = float(np.hypot(*(e - lv)))
                            if dd <= tol and (best is None or dd < best[0]):
                                best = (dd, j, rev)
                    if best is None:
                        continue
                    _, j, rev = best
                    b = runs[j][::-1] if rev else runs[j]
                    if j == i:
                        closed[i] = True               # a whole ring: its own end is the one short of it
                    else:
                        runs[i] = np.vstack([b, a])     # b ... (missing segment) ... a
                        runs[j] = None
                    changed = True
                    break
                if changed:
                    break
        d = "".join(C.polyline_d(r, closed=c) for r, c in zip(runs, closed) if r is not None)
        out.append(_rp(m, d=d) if d else m)
    return C.Frag(out, rip.meta)


def drop_stubs(f: C.Frag, front, *, roles=(), min_vis=14.0, tol=0.1):
    """Lines of ``roles`` in ``f`` whose VISIBLE runs (outside ``front``) are
    shorter than ``min_vis`` px lose those runs: a seam peeping out for a few
    px between an arm and the band reads as a stray tick. → Frag."""
    front = K.R(front).buffer(-0.3, quad_segs=6)
    sel = f.select(lambda m: m.role in roles)
    rest = f.select(lambda m: m.role not in roles)
    cut = []
    for m in sel.marks:
        for p, closed in G.flatten(m.d, tol):
            if len(p) < 2:
                continue
            pts = np.vstack([p, p[:1]]) if closed else np.asarray(p)
            for comp in K._lines_of(shapely.line_merge(LineString(pts).difference(front))):
                if comp.length < min_vis:
                    cut.append(comp.buffer(1.5, cap_style=2))
    if cut:
        sel = K.clip_out(sel, shapely.union_all(cut), eps=0.0, trap=0.0)
    return rest + sel
