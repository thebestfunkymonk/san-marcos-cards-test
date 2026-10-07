"""KD whole-card textiles: the jade open mantle, the red ashlar tabard and the Warden's sash.

Everything is built so the 180° copy continues the top half without a visible join: regions are C2
about (375, 525) by construction, patterns on the mantle are drawn once on the left half and rotated,
the tabard's ashlar courses sit on a grid that is its own 180° copy, and the sash is one straight band
through the card centre whose rowels and ford stones are placed in C2 pairs.
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
from inkkit import geom as G
from art import _kd_body as B

AX, CY = K.AX, 525.0
SIDE_X = 146.0                      # mantle side at the card centre
BORDER = 36.0                       # patterned jade border inside the mantle's edges
LENS_HW, LENS_THROAT = 98.0, 292.0  # the tabard's opening: half-width at the centre, throat y
SASH_ANGLE, SASH_W = 46.0, 52.0     # the baldric: down-right through the centre, width
ASHLAR = dict(joint=3.1)
CHAIN_RULES = (14.0, 29.0)          # FINE rules inside the mantle's edges, stones on the mid-line
STONE_PITCH = 24.0


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def c2_frag(f: C.Frag) -> C.Frag:
    """``f`` plus its 180° partner; atomic-motif keys of the partner get a suffix so covering one
    copy never deletes the other."""
    r = K.rot180(f)
    marks = [replace(m, role=m.role + "~") if "@" in m.role else m for m in r.marks]
    return f + C.Frag(marks, r.meta)


def barrel() -> object:
    """The whole-card jade mantle: shoulders from the neck, a smooth bowed side with a vertical
    tangent on the centre line (no kink at the join)."""
    ms = K.MantleSpec(neck_y=284.0, neck_heading=171.5, run=150.0, corner_r=30.0, side_heading=99.0)
    pts = K.mantle_outline(ms)
    k = next(i for i, p in enumerate(pts) if p[1] >= 369.0)
    head = pts[:k + 1]
    p0 = head[-1]
    d0 = (head[-1] - head[-2]) / np.hypot(*(head[-1] - head[-2]))
    p3 = np.array([SIDE_X, CY])
    c1, c2 = p0 + d0 * 52.0, p3 - np.array([0.0, 1.0]) * 62.0
    t = np.linspace(0.0, 1.0, 40)[1:, None]
    cub = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p3
    half = Polygon(np.vstack([head, cub, [[AX, CY]]])).buffer(0)
    top = K.U(half, K.mirror(half, AX))
    return K.U(top, rot(top))


def lens():
    g = K.lens(K.LensSpec(half_w=LENS_HW, throat_y=LENS_THROAT))
    return K.R(K.circle(g["cL"], g["R"])).intersection(K.R(K.circle(g["cR"], g["R"])))


def sash_axis():
    a = math.radians(SASH_ANGLE)
    u = np.array([math.cos(a), math.sin(a)])
    return np.array([AX, CY]), u, np.array([u[1], -u[0]])


def sash_shape(clip=None):
    c, u, n = sash_axis()
    a, b = c - u * 900, c + u * 900
    band = Polygon([a + n * SASH_W / 2, b + n * SASH_W / 2, b - n * SASH_W / 2, a - n * SASH_W / 2])
    return band.intersection(clip if clip is not None else barrel())


def drop_short(f: C.Frag, min_len: float = 9.0) -> C.Frag:
    """Remove stroke pieces shorter than ``min_len`` (the stubs a hatch leaves in a pocket)."""
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d:
            out.append(m)
            continue
        d = "".join(C.polyline_d(pts, closed=cl) for pts, cl in G.flatten(m.d, 0.05)
                    if G.Curve(np.asarray(pts), closed=cl).length >= min_len)
        if d:
            out.append(replace(m, d=d))
    return C.Frag(out, f.meta)


def seam_guard(f: C.Frag, seam, margin: float = 4.8) -> C.Frag:
    """Drop stroke pieces with an end within ``margin`` of the seam: the half's clip would cut them a
    hair short of their junction, leaving a sub-3 px stub the other half has to finish."""
    if seam is None:
        return f
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d:
            out.append(m)
            continue
        keep = []
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts)
            if not cl and (Point(*pts[0]).distance(seam) < margin or Point(*pts[-1]).distance(seam) < margin):
                continue
            keep.append(C.polyline_d(pts, closed=cl))
        if keep:
            out.append(replace(m, d="".join(keep)))
    return C.Frag(out, f.meta)


# ---------------------------------------------------------------------------
# tabard: ashlar courses knocked out of the red
# ---------------------------------------------------------------------------
HEIGHTS = (36.0, 28.0, 40.0, 30.0, 38.0, 28.0, 42.0, 30.0, 36.0, 32.0)
WIDTHS = (96.0, 70.0, 118.0, 82.0, 104.0, 76.0)


def ashlar_red(region, *, joint, chamfer=2.6):
    """Red blocks of a random-ashlar wall inside ``region``. Course 0 is centred on y 525; heights
    and block widths come from fixed cycles, and a course above the centre is the 180° image of the
    one below it, so the whole wall is its own 180° copy."""
    x0, _, x1, _ = region.bounds
    box = shapely.box
    j2 = joint / 2
    strips = []
    half0 = HEIGHTS[0] / 2
    xs, pos, k = [], AX + 62.0, 0
    while pos < x1 + 100:
        xs += [pos, 2 * AX - pos]
        pos += WIDTHS[k % len(WIDTHS)]
        k += 1
    strips += [box(x - j2, CY - half0, x + j2, CY + half0) for x in xs]
    yb = CY + half0
    for r in range(1, 10):
        h = HEIGHTS[r % len(HEIGHTS)]
        pos, k, xs = x0 - 60 + (r * 37) % 71, r, []
        while pos < x1 + 100:
            xs.append(pos)
            pos += WIDTHS[k % len(WIDTHS)]
            k += 1
        for y_a, y_b, flip in ((yb, yb + h, False), (2 * CY - yb - h, 2 * CY - yb, True)):
            for x in xs:
                xx = 2 * AX - x if flip else x
                strips.append(box(xx - j2, y_a, xx + j2, y_b))
        for yy in (yb, 2 * CY - yb):
            strips.append(box(x0 - 5, yy - j2, x1 + 5, yy + j2))
        yb += h
    for yy in (yb, 2 * CY - yb):
        strips.append(box(x0 - 5, yy - j2, x1 + 5, yy + j2))
    red = region.difference(shapely.union_all(strips))
    red = red.buffer(-chamfer, quad_segs=3).buffer(chamfer, quad_segs=3)
    return red.intersection(region), strips


# ---------------------------------------------------------------------------
# jade mantle ornament (left half, then rotated)
# ---------------------------------------------------------------------------
def _rings(region, d):
    """Closed offset rings (point arrays) of ``region`` inset by ``d``."""
    g = region.buffer(-d, quad_segs=16)
    out = []
    for p in K._polys_of(g):
        for ring in [p.exterior, *p.interiors]:
            out.append(np.asarray(ring.coords))
    return out


def chain_left(jade_left, *, rules=CHAIN_RULES, stone=(11.0, 6.4), pitch=STONE_PITCH, avoid=None, seam=None):
    """§G.23 stepping-stone chain in the mantle's border: two FINE rules and solid lozenges on the
    mid-line, drawn on the left half only (the caller rotates it)."""
    lines, polys = C.Frag(), []
    for d in rules:
        for q in _rings(jade_left, d):
            lines += C.stroke(C.polyline_d(q, closed=True), K.FINE, style="rule", role="chain")
    mid = (rules[0] + rules[1]) / 2
    room = jade_left.buffer(-(stone[0] / 2 + 1.0))
    k = 0
    for q in _rings(jade_left, mid):
        ln = LineString(q)
        n = max(2, int(round(ln.length / pitch)))
        for i in range(n):
            s = (i + 0.5) * ln.length / n
            p = ln.interpolate(s)
            p2, p1 = ln.interpolate(min(s + 1.0, ln.length)), ln.interpolate(max(s - 1.0, 0.0))
            a = math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))
            ld = C.lozenge_d(p.x, p.y, *stone, a)
            lz = K.R(ld)
            if not room.contains(Point(p.x, p.y)) or p.x > AX - 6.0:
                continue
            if seam is not None and lz.distance(seam) < 8.0:
                continue
            if avoid is not None and lz.distance(avoid) < 7.0:
                continue
            k += 1
            lines += K.atomic(K.fill(ld, K.INK, role="stone"), f"cs{k}")
            polys.append(lz)
    return lines, polys


def brocade_left(field_left, *, pitch=(22.0, 18.0), size=(13.0, 8.0), avoid=None, seam=None):
    """A half-drop grid of small outlined lozenges strewn over the field (FINE Aquifer on the jade),
    left half only; each stone is atomic and keeps clear of the field's edge."""
    px, py = pitch
    L, W = size
    inner = field_left.buffer(-(L / 2 + K.FINE / 2 + 4.3))
    x0, y0, x1, y1 = field_left.bounds
    f = C.Frag()
    for j in range(int(math.floor((y0 - CY) / py)) - 1, int(math.ceil((y1 - CY) / py)) + 2):
        off = px / 2 if j % 2 else 0.0
        for i in range(int(math.floor((x0 - AX - off) / px)) - 1, int(math.ceil((x1 - AX - off) / px)) + 2):
            x, y = AX + off + i * px, CY + j * py
            if x > AX - 6.0 or not inner.contains(Point(x, y)):
                continue
            st = K.R(C.lozenge_d(x, y, L, W))
            if seam is not None and st.distance(seam) < 8.0:
                continue
            if avoid is not None and st.distance(avoid) < 6.0:
                continue
            f += K.atomic(C.stroke(C.lozenge_d(x, y, L, W), K.FINE, style="point", color=K.INK, role="stone"),
                          f"fb{i}_{j}")
    return f


# ---------------------------------------------------------------------------
# the garments Part
# ---------------------------------------------------------------------------
def garments(front, *, sleeves, cuff_fills, cuff_lines, sleeve_grain, sleeve_edges, seam=None):
    """The whole-card robe: jade open mantle (chain border + brocade) and the red ashlar tabard in
    its opening, plus the two sleeves, all as one C2 region set. ``front``: shapes of the items drawn
    over it (head, hands, attributes, the sash)."""
    sleeve_zone = K.c2(sleeves)
    shape = K.U(barrel(), sleeve_zone)
    shape = K.U(shape, shape.buffer(12).buffer(-12))
    lens_s = lens().intersection(shape)
    jade = shape.difference(lens_s)
    blockers = K.c2(front)

    # ---- red tabard: ashlar blocks ----------------------------------------------------
    red, _ = ashlar_red(lens_s, **ASHLAR)
    rust = C.Frag()
    for blk in K._polys_of(red):
        cx, cy = blk.centroid.x, blk.centroid.y
        key = min((round(cx), round(cy)), (round(2 * AX - cx), round(2 * CY - cy)))
        if ((key[0] * 73856093) ^ (key[1] * 19349663)) % 5 in (0, 2):
            rust += drop_short(K.hatch_in(blk.buffer(-5.0), angle=45.0, origin=(AX, CY)), 12.0)

    # ---- jade: chain in the border, brocade inside, drawn left then rotated ----------
    jade_l = jade.intersection(K.box(0, 0, AX, 2000))
    keep_out = K.U(blockers, sleeve_zone.buffer(1.0))
    chain, stones = chain_left(jade_l, avoid=keep_out, seam=seam)
    chain = K.clip_out(chain, sleeve_zone, eps=-0.5, trap=0.0)
    field_l = jade.buffer(-BORDER).intersection(K.box(0, 0, AX, 2000))
    stone_zone = K.U(*stones).buffer(6.0) if stones else Polygon()
    bro = brocade_left(field_l, avoid=K.U(keep_out, stone_zone), seam=seam)
    ornament = c2_frag(chain + bro)

    gold = K.U(*[K.R(m.d) for m in cuff_fills.marks]) if cuff_fills.marks else Polygon()
    fills = K.fill(jade.difference(K.c2(gold).buffer(-1.6)), K.JADE) + K.fill(red, K.RED) + K.c2(cuff_fills)
    lines = K.outline(shape) + K.outline(lens_s)
    lines += ornament + seam_guard(rust, seam)
    lines += K.c2(sleeve_grain) + K.c2(sleeve_edges) + K.c2(cuff_lines)
    return K.Part(shape, fills, lines, {"jade": jade, "lens": lens_s})


# ---------------------------------------------------------------------------
# the sash
# ---------------------------------------------------------------------------
ROWEL_R, SASH_PITCH = 15.0, 56.0


def sash(*, clasp, avoid, seam=None):
    """The Warden's baldric: one straight band through the card centre. Rowels sit at offsets
    56 k along it (the k = 0 rowel is on the card centre, where the seam crosses it as its own
    180° copy) and ford stones at ±(28 + 56 k), so the band is its own 180° copy; the rowel nearest
    the Lion Mark's offset is left out for the clasp."""
    c, u, n = sash_axis()
    reg = sash_shape()
    inner = reg.buffer(-(ROWEL_R + 4.6))
    ang = math.degrees(math.atan2(u[1], u[0]))
    av = K.R(avoid).buffer(K.GAP_MARK + 2.0)
    clasp_s = float(np.dot(np.asarray(clasp) - c, u))
    rows, marks = [], []
    for k in range(0, 12):
        for sgn in (1, -1):
            ss = sgn * k * SASH_PITCH
            if k == 0 and sgn < 0:
                continue
            p = c + u * ss
            if abs(ss - clasp_s) < 20 or abs(ss + clasp_s) < 20:
                continue
            if inner.contains(Point(*p)) and not av.intersects(Point(*p).buffer(ROWEL_R)) \
                    and not av.intersects(rot(Point(*p)).buffer(ROWEL_R)):
                rows.append(B.rowel(p, ROWEL_R, rot=ang + 22.5, key=f"sr{k}{sgn}"))
    stones = [sgn * (SASH_PITCH / 2 + k * SASH_PITCH) for k in range(0, 12) for sgn in (1, -1)]
    room = reg.buffer(-(5.5 + 4.3))
    for ss in stones:
        p = c + u * ss
        ld = C.lozenge_d(p[0], p[1], 11.0, 6.4, ang)
        lz = K.R(ld)
        if room.contains(Point(*p)) and not av.intersects(lz) and not av.intersects(rot(lz)):
            marks.append((lz, K.fill(ld, K.INK, role="stone")))
    jade = reg
    for sil, _ in rows:
        jade = jade.difference(sil.buffer(-1.6))
    fills = K.fill(jade, K.JADE)
    lines = K.outline(reg)
    for _, f in rows:
        fills += f.select(lambda m: m.layer != "ink")
        lines += f.select(lambda m: m.layer == "ink")
    for _, m in marks:
        lines += m
    keep = reg.buffer(-6.5)
    for sil, _ in rows:
        keep = keep.difference(sil.buffer(6.0))
    for lz, _ in marks:
        keep = keep.difference(lz.buffer(6.0))
    keep = keep.difference(av.buffer(4.0))
    grain = drop_short(K.hatch_in(keep, angle=ang + 90.0, origin=(AX, CY)), 12.0)
    lines += seam_guard(grain, seam)
    return K.Part(reg, fills, lines, {"u": u, "n": n})
