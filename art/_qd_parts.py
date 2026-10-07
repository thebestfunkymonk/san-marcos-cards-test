"""art/_qd_parts.py — Q♦ · The Queen of Scales: the builders that are hers
alone (brief §H.11). Every builder returns a deck.courtkit Part (shape,
fills, lines, meta) drawn at final size in card px, compass-built from the
kit's primitives; art/QD.py stacks them.

    paintbrush7  a sprig of Texas paintbrush: overlapping pointed bracts,
                 red-dipped over paper bases, one half of the spike hatched;
                 jade leaves (regalia, not a picked rarity: Castilleja
                 indivisa is common)
    cape         the Gill Red cape, its front edges carrying a stepping-stone
                 chain knocked out to paper (§G.23)
    gown5        the jade gown with a stacked arcade (§G.21): three tiers of
                 continuous keystoned arcades on shared jambs, one grid about
                 the stomacher's axis
    (paintbrush2–6 and gown–gown4 are earlier passes, kept for reference)
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import shapely
from shapely.geometry import LineString, MultiLineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G

P, R, U, D = K.P, K.R, K.U, K.D
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD
GAP, GAP_MARK = K.GAP, K.GAP_MARK


# =============================================================================
# arcades and the paintbrush
# =============================================================================


def _arcade_run(x_bays, sill, *, r, a, jamb, key, stub_l, stub_r, w=FINE, color=INK):
    """One continuous run of arches (§G.21) on the sill line ``sill``: bays
    centred at ``x_bays`` (one pitch apart); the arches spring from short
    impost bars (half-width ``a``) that cap SHARED jambs, one jamb per pier
    (a pier sits half a pitch either side of each bay). The springing line,
    the impost bars and the arches are one path per keystone gap (miter
    joins, butt caps); each keystone (``key`` = height above the arch, full
    angle) straddles the arch line, which breaks under it. ``stub_l`` /
    ``stub_r``: the outer impost stub at each end of the run (a or 0)."""
    kh, kang = key
    half = kang / 2
    a_l, a_r = -90.0 - half, -90.0 + half
    ys = sill - jamb                                   # springing line
    f = C.Frag()
    pitch = (x_bays[1] - x_bays[0]) if len(x_bays) > 1 else 2 * (r + a)
    piers = [x_bays[0] - pitch / 2] + [x + pitch / 2 for x in x_bays]
    # the springing path, broken at every keystone; an end pier without an
    # outer stub turns down into its jamb in the same path (a mitred corner)
    start = [(piers[0] - stub_l, ys)] if stub_l > 0 else [(piers[0], sill), (piers[0], ys)]
    d = C.polyline_d(start + [(piers[0] + a, ys)]) + C.arc_d(x_bays[0], ys, r, 180.0, 360.0 + a_l, move=False)
    for i, x in enumerate(x_bays):
        d_i = C.arc_d(x, ys, r, a_r, 0.0, move=True)
        if i + 1 < len(x_bays):
            nx = x_bays[i + 1]
            d_i += f"L{nx - r:.3f} {ys:.3f}" + C.arc_d(nx, ys, r, 180.0, 360.0 + a_l, move=False)
        elif stub_r > 0:
            d_i += f"L{piers[-1] + stub_r:.3f} {ys:.3f}"
        else:
            d_i += f"L{piers[-1]:.3f} {ys:.3f}L{piers[-1]:.3f} {sill:.3f}"
        d += d_i
    f += C.stroke(d, w, style="rule", color=color, role="arch")
    for k, p in enumerate(piers):
        if (k == 0 and stub_l <= 0) or (k == len(piers) - 1 and stub_r <= 0):
            continue
        f += C.stroke(C.polyline_d([(p, ys), (p, sill)]), w, style="rule", color=color, role="jamb")
    r_foot, r_top = r - 0.6 * kh, r + kh
    for x in x_bays:
        pl0, pr0 = C.polar(x, ys, r_foot, a_l), C.polar(x, ys, r_foot, a_r)
        pl1, pr1 = C.polar(x, ys, r_top, a_l), C.polar(x, ys, r_top, a_r)
        ty = min(pl1[1], pr1[1])
        kd = C.polyline_d([pl0, (pl1[0], ty), (pr1[0], ty), pr0]) + C.arc_d(x, ys, r_foot, a_r, a_l, move=False) + "Z"
        f += C.stroke(kd, w, style="rule", color=color, role="keystone")
    return f


def _bay_footprint(x, sill, *, r, a, jamb, key, pitch):
    """Centre-line footprint of one bay (its arch, keystone, both jambs and
    impost bars) for the fit test."""
    kh, kang = key
    ys = sill - jamb
    th = np.radians(np.linspace(180.0, 360.0, 49))
    arc = np.column_stack([x + r * np.cos(th), ys + r * np.sin(th)])
    a_l, a_r = -90.0 - kang / 2, -90.0 + kang / 2
    pl1, pr1 = C.polar(x, ys, r + kh, a_l), C.polar(x, ys, r + kh, a_r)
    ty = min(pl1[1], pr1[1])
    keystone = Polygon([tuple(C.polar(x, ys, r - 0.6 * kh, a_l)), (pl1[0], ty), (pr1[0], ty),
                        tuple(C.polar(x, ys, r - 0.6 * kh, a_r))])
    parts = [LineString(arc), keystone]
    for p, sg in ((x - pitch / 2, +1), (x + pitch / 2, -1)):
        parts.append(LineString([(p, ys), (p, sill - 0.5)]))
        parts.append(LineString([(p, ys), (p + sg * a, ys)]))        # the bay's own half of the impost
    return shapely.unary_union(parts)


def _own_path(f: C.Frag) -> C.Frag:
    """Give rules their own SVG <path> (a style key the arcades do not share:
    miter limit 4.01, invisible on a straight line), so heal and QA 12 see a
    sill as its own piece: a trim at a sill's end re-serialises only the
    sill, never the mitred arcade standing on it."""
    return C.Frag([replace(m, miter=4.01) for m in f.marks], f.meta)


def _square_hatch(f: C.Frag, own, front, min_deg=40.0) -> C.Frag:
    """Drop the hatch lines that a bract in front cuts at a glancing angle
    (< ``min_deg`` to its outline) — also where the hatch ends at the
    crossing of its own outline with the front one: the paper wedge between
    them is a §I.12 narrow gap. Lines ending on their own outline stay."""
    fb = front.boundary
    out = []
    for m in f.marks:
        pcs = []
        for ln in K._lines_of(MultiLineString(K._stroke_lines(m.d))):
            xy = np.asarray(ln.coords)
            ok = True
            for end, nxt in ((xy[0], xy[1]), (xy[-1], xy[-2])):
                pe = Point(*end)
                if fb.distance(pe) > 1.2:
                    continue                    # ends on its own outline, clear of the front one
                s_ = fb.project(pe)
                a, b = fb.interpolate(s_ - 1.5), fb.interpolate(s_ + 1.5)
                t = np.array([b.x - a.x, b.y - a.y])
                h = end - nxt
                if np.hypot(*t) < 1e-6 or np.hypot(*h) < 1e-6:
                    continue
                c = abs(float(t @ h)) / (np.hypot(*t) * np.hypot(*h))
                if math.degrees(math.acos(min(1.0, c))) < min_deg:
                    ok = False
            if ok:
                pcs.append(xy)
        if pcs:
            out.append(replace(m, d="".join(C.polyline_d(q) for q in pcs)))
    return C.Frag(out, f.meta)


def paintbrush7(base, tip, *, spike=96.0, bracts=(), top=(21.0, 11.0, 0.86), stem_w=8.4, stem_top=0.3,
                leaves=((0.30, -1, 34.0, 11.0), (0.62, +1, 32.0, 10.5)), leaf_deg=32.0, hatch_side=+1,
                midribs=True, min_base=6.0, root=6.0, leaves_behind=False):
    """Texas paintbrush, v7 (§H.11 'a sprig of Texas paintbrush with
    red-dipped bracts and jade leaves'; Castilleja: the colour is in the
    BRACTS). The spike is a cone of OVERLAPPING POINTED BRACTS (``bracts``:
    (t along the spike, side, lean°, length, width, red fraction), bottom →
    top) set alternately left and right up the axis — each a vesica (the
    deck's leaf) springing ``root`` px across the axis, leaning out less and
    growing smaller toward the top, every lower bract in front of the ones
    above it — crowned by one upright bract (``top`` = length, width, red
    fraction). Every bract is dipped:
    Gill Red from its tip down its red fraction (more red toward the top,
    as the plant is), a paper base, a MEDIUM dip line between. The spike is
    split along its axis and ONE half hatched: the paper bases of the bracts
    on ``hatch_side`` carry FINE hatch perpendicular to their midribs
    (§B hatching: leaves), 7 px from the dip line. Stem a jade band (hidden
    inside the spike above ``stem_top``); leaves alternate sessile jade
    vesicas with FINE midribs.

    Built for heal / QA 12: the visible red is ONE fill (no red-to-red near
    misses); bract outlines and dip lines share one stroke style, so they
    form one connected piece; hatch lines that would end in a near miss or
    a glancing wedge are left out whole rather than trimmed."""
    b, t = P(base), P(tip)
    u = (t - b) / np.hypot(*(t - b))
    nrm = np.array([u[1], -u[0]])
    L = float(np.hypot(*(t - b)))
    s0 = t - u * spike

    def dirv(a):
        a = math.radians(a)
        return u * math.cos(a) + nrm * math.sin(a)

    def bract(p0, d, ln, w, rf, hatch):
        bd = C.vesica_d(tuple(p0), tuple(p0 + d * ln), w)
        reg = R(bd)
        cut = p0 + d * ln * (1 - rf)
        side = np.array([-d[1], d[0]])
        tipward = K.halfplane(cut, cut + side, side=-1)
        if not tipward.contains(Point(*(p0 + d * (ln - 1.0)))):
            tipward = K.halfplane(cut, cut + side, side=+1)
        red = reg.intersection(tipward)
        paper = reg.difference(tipward)
        lines = C.stroke(bd, MEDIUM, style="point", role="bract")
        hatch_f = C.Frag()
        if rf < 0.98:
            for g in K._lines_of(LineString([tuple(cut - side * 30), tuple(cut + side * 30)]).intersection(reg)):
                if g.length > 2:
                    lines += C.stroke(np.asarray(g.coords), MEDIUM, style="point", role="dip")
            if hatch and ln * (1 - rf) > min_base:
                ang = math.degrees(math.atan2(side[1], side[0]))
                hatch_f = K.hatch_in(paper, angle=ang, origin=tuple(cut))
        return dict(reg=reg, red=red, lines=lines, hatch=hatch_f)

    spike_items = []                               # back → front
    tl, tw, trf = top
    spike_items.append(bract(t - u * tl, u, tl, tw, trf, False))
    for (tt, sg, lean, ln, w, rf) in sorted(bracts, key=lambda x: -x[0]):   # higher bracts behind
        dd = dirv(sg * lean)
        # the bract springs from just across the axis, so its body (not its
        # point) covers the axis and the stem inside the spike
        spike_items.append(bract(s0 + u * spike * tt - dd * root, dd, ln, w, rf, sg == hatch_side))
    stem = LineString([tuple(b), tuple(s0 + u * spike * stem_top)]).buffer(stem_w / 2, cap_style=1)
    back = [dict(reg=stem, red=Polygon(), jade=stem, lines=K.outline(stem, MEDIUM, role="stem"), hatch=C.Frag())]
    for (tt, sg, ll, lw) in leaves:
        at = b + u * (L - spike) * tt
        d = dirv(sg * leaf_deg)
        p0, p1 = at, at + d * ll
        vd = C.vesica_d(tuple(p0), tuple(p1), lw)
        reg = R(vd)
        ln = C.stroke(vd, MEDIUM, style="point", role="leaf")
        if midribs:
            ln += K.seg(p0 + d * 8.0, p1 - d * 10.0, FINE, role="midrib")
        back.append(dict(reg=reg, red=Polygon(), jade=reg, lines=ln, hatch=C.Frag()))
    if leaves_behind:
        # the leaves spring from BEHIND the stem (their pointed bases hidden by it, the stem's
        # edge unbroken — never a leaf point 4 px from the stem's outline)
        back = back[1:] + back[:1]
    items = back + spike_items
    reds, jades, strokes, hatches = [], [], C.Frag(), C.Frag()
    acc = Polygon()
    for it in reversed(items):                     # front → back
        vis = it["reg"].difference(acc) if not acc.is_empty else it["reg"]
        if not it["red"].is_empty:
            reds.append(it["red"].intersection(vis))
        if it.get("jade") is not None:
            jades.append(K.clip_out(K.fill(it["jade"], JADE), acc) if not acc.is_empty else K.fill(it["jade"], JADE))
        strokes = (K.clip_out(it["lines"], acc) if not acc.is_empty else it["lines"]) + strokes
        if it["hatch"].marks and not acc.is_empty:
            hatches = _square_hatch(K.clip_out(it["hatch"], acc), it["reg"], acc) + hatches
        else:
            hatches = it["hatch"] + hatches
        acc = acc.union(it["reg"].buffer(0.3))
    # one style run for the bract outlines + dips (one connected piece); the
    # hatch, then the stem and the leaves after it
    pt = strokes.select(lambda m: m.role.split("@")[0] in ("bract", "dip"))
    rest = strokes.select(lambda m: m.role.split("@")[0] not in ("bract", "dip"))
    # visible red, closed across the hairline seams under the outlines (the
    # front bract's region is grown 0.3 px in ``acc``): one piece per run
    red = U(*[r for r in reds if not r.is_empty]).buffer(0.6, join_style=2).buffer(-0.6, join_style=2)
    red = red.intersection(U(*[it["red"] for it in items if not it["red"].is_empty]))
    # §I.12 for the hatch, judged as heal / QA 12 will judge it: a hatch
    # line may touch a red piece (it ends on an outline the red runs under)
    # but not come within 3 px of one without touching — which happens where
    # the layer trap (_qd_finish.trap_cut) cuts the red back under an ink
    # junction (a front bract's outline meeting its dip line). The same for
    # the stem's outline, which ends under a bract's outline. Such a line is
    # dropped whole (a trimmed hatch end would float).
    ink_all = (pt + rest).shape()
    hide = 3.125 + 0.3
    blobs = ink_all.buffer(-hide, quad_segs=8).buffer(hide - 1.4, quad_segs=8)
    red_pcs = K._polys_of(red.difference(blobs)) if not blobs.is_empty else K._polys_of(red)
    stem_ink = C.Frag([m for m in rest.marks if m.role.split("@")[0] == "stem"]).shape()
    jade_pcs = [g for j in jades for m in j.marks if m.d for g in K._polys_of(G.to_shape(m.d, tol=0.05))]
    near = red_pcs + K._polys_of(stem_ink) + jade_pcs

    def near_miss(ink):
        return any(0.05 < ink.distance(g) < GAP_MARK + 0.1 for g in near)
    keep = []
    for m in hatches.marks:
        pcs = []
        for ln in K._lines_of(MultiLineString(K._stroke_lines(m.d))):
            if near_miss(ln.buffer(m.w / 2, cap_style=1)):
                continue
            pcs.append(np.asarray(ln.coords))
        if pcs:
            keep.append(replace(m, d="".join(C.polyline_d(q) for q in pcs)))
    hatches = C.Frag(keep)
    fills = K.fill(red, RED) if not red.is_empty else C.Frag()
    for j in jades:
        fills += j
    shape = U(*[it["reg"] for it in items])
    return K.Part(shape, fills, pt + hatches + rest, {"spike_base": s0, "u": u, "stem": stem})


def standing_collar2(cx, *, top_y, half_w, neck_y, shoulder, shoulder_r=None, top_sag=7.0, side_sag=-6.0,
                     rim=8.0, depth=120.0, color=K.RED, rim_color=K.JADE) -> K.Part:
    """The kit's standing_collar with the FAR (viewer's-right) wing's
    shoulder point set on its own (``shoulder_r`` = (dx, y), dx measured
    outward like ``shoulder``'s, i.e. negative): a 3/4-right figure's far
    wing is foreshortened, and on Q♦ the symmetric wing's outer edge ran
    down into the scales' staff at a 1–2 px paper wedge where it met the
    cape's shoulder. Same construction as the kit (compass arcs, pointed
    corners, rim band along the top edge, fold line at the rim)."""
    shoulder_r = shoulder if shoulder_r is None else shoulder_r
    A = P(cx, neck_y)
    Cn = P(cx - half_w, top_y)

    def half(sh):
        Sh = P(cx + sh[0], sh[1])
        top = K.Path(A).sag(Cn, top_sag)
        return R(top.sag(Sh, side_sag).line((Sh[0], Sh[1] + depth)).line((cx, Sh[1] + depth)).close().d)

    hl, hr = half(shoulder), K.mirror(half(shoulder_r), cx)
    shape = U(hl, hr)
    edge = C.sample_d(K.arc_sag(A, Cn, top_sag), 0.3)[0][0]
    edge = np.vstack([edge, [Cn + (Cn - edge[-2]) / np.hypot(*(Cn - edge[-2])) * 30.0]])
    bl = LineString(edge).buffer(rim, cap_style=2, quad_segs=12)
    band = U(bl.intersection(hl), K.mirror(bl, cx).intersection(hr)).intersection(shape)
    body = shape.difference(band)
    fills = K.fill(body, color) + K.fill(band, rim_color)
    lines = K.outline(shape)
    fold = R(band).buffer(0).boundary.intersection(shape.buffer(-0.6))
    for ln in K._lines_of(shapely.line_merge(fold) if fold.geom_type != "LineString" else fold):
        if ln.length > 4:
            lines += K.line(np.asarray(ln.coords), MEDIUM, role="fold")
    return K.Part(shape, fills, lines, {"rim": band, "corner": Cn})
