"""K♣ · the Knee Crown (brief §H.7, §G.17) — five gold cypress knees at heights
0.65 / 0.8 / 1.0 / 0.8 / 0.65, fluted with half-hatch, rising from a band of
ripple lines.

§G.17 'cypress-knee crenellation: rounded conical knobs, each two arcs meeting
in a small top fillet'. A knee as it stands in the water: a broad foot that
flares into the waterline (concave), a body that narrows (convex) and a blunt
rounded knob — a cone, never a flame, a feather or a spike. The five stand
apart like merlons (paper between the knobs: a crenellation, not a fan of
plumes), their feet merging where they rise out of the band. The band is the
river they stand in: ripple lines, drawn in FRONT of the knees' feet.

Half-hatch (§G.17 'fluted with half-hatch'; §I.3 '"half-hatched" always means
FINE at a 7.0 pitch in one half only'; director's note: two flute lines were
not half-hatch, the K♠ merlons are): ``flute_mode="half"`` hatches each side
knee's OUTER half at 45° — the lines square to its outer flank, so they butt
on it cleanly and never run into an acute wedge — with the terminator on the
knee's own axis. The centre knee is hatched on its left half only
(``centre_mode="one"``): a chevron about its axis read as a fir tree (§H.7
must-avoid) and a joint line down any knee as a leaf or a feather (the first
draft's quill line), so there is none (``half_joint=False``). The hatch
phase (``hatch_phase``) keeps a line off the junctions where knees overlap.
The older 'axis' / 'side' / 'diag' flute modes are kept for reference.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms as FM

P, AX = K.P, K.AX
FINE, MEDIUM, CONTOUR = T.FINE, T.MEDIUM, T.CONTOUR
GOLD = T.FOIL
GAP = K.GAP


def _pts(d, step=0.3):
    return C.sample_d(d, step)[0][0]


def knee(x, y, h, bw, *, knob=0.24, beta=16.0, flare=55.0, depth=26.0):
    """One knee standing on (x, y) (its waterline), ``h`` tall and ``bw``
    wide at the waterline. The side is one biarc: leaving the waterline
    heading up and out by ``flare``° above horizontal (< 90: the flared,
    concave foot), turning in to meet the knob circle (radius ``knob``·bw)
    tangentially ``beta``° above its widest line (the convex shoulder).
    Closed ``depth`` px below the waterline (the part hidden in the band).
    → (region, knob centre, knob radius)."""
    rt = knob * bw
    kc = P(x, y - h + rt)
    th = math.radians(180.0 + beta)
    Tl = kc + rt * np.array([math.cos(th), math.sin(th)])
    Tr = P(2 * x - Tl[0], Tl[1])
    A = P(x - bw / 2, y)
    B = P(x + bw / 2, y)
    s1, _ = FM.biarc(A, -flare, Tl, -90.0 + beta)
    top = C.arc_between(kc, rt, Tl, Tr, cw=True)
    s2, _ = FM.biarc(Tr, 90.0 - beta, B, flare)
    d = (f"M{A[0]:.3f} {A[1]:.3f}" + s1 + top + s2
         + f"L{B[0]:.3f} {y + depth:.3f}L{A[0]:.3f} {y + depth:.3f}Z")
    return K.R(d), kc, rt


def knee_cone(x, y, h, bw, *, fillet=0.22, side_k=1.5, depth=26.0):
    """§G.17 exactly: two convex side arcs (radius ``side_k``·h) from the
    waterline corners meeting in a top fillet (radius ``fillet``·bw).
    → (region, fillet centre, fillet radius)."""
    from deck.motifs import geometric as MG
    f_r = fillet * bw
    A, c, R, F, tl = MG._knee_geom(x, y, h, bw, f_r, side_k * h)
    Ar = P(2 * x - A[0], A[1])
    cr = P(2 * x - c[0], c[1])
    tr = P(2 * x - tl[0], tl[1])
    d = (f"M{A[0]:.3f} {A[1]:.3f}" + C.arc_between(c, R, A, tl, cw=True)
         + C.arc_between(F, f_r, tl, tr, cw=True) + C.arc_between(cr, R, tr, Ar, cw=True)
         + f"L{Ar[0]:.3f} {y + depth:.3f}L{A[0]:.3f} {y + depth:.3f}Z")
    return K.R(d), P(F), f_r


def _side_half(reg, b, u, sd):
    """The half of ``reg`` on side ``sd`` (−1 screen-left, +1 right) of the
    axis through b along u."""
    n_ = np.array([-u[1], u[0]])
    if n_[0] * sd < 0:
        n_ = -n_
    far = b + n_ * 200.0
    poly = shapely.geometry.Polygon([tuple(b - u * 200.0), tuple(b + u * 400.0), tuple(far + u * 400.0),
                                     tuple(far - u * 200.0)])
    return reg.intersection(poly)


def _drop_short_hatch(f, min_len):
    from dataclasses import replace
    from inkkit import geom as G
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d or m.role != "hatch":
            out.append(m)
            continue
        d = "".join(C.polyline_d(pts, closed=cl) for pts, cl in G.flatten(m.d, 0.05)
                    if G.Curve(np.asarray(pts), closed=cl).length >= min_len)
        if d:
            out.append(replace(m, d=d))
    return C.Frag(out, f.meta)


def _drop_pocket_hatch(shape, f, *, also=None, max_area=6.0, open_r=0.9):
    """Remove the hatch sub-paths that cut a gold pocket too small to print off a knee's corner (the
    acute corner where an outer knee stands on the band): without the line the pocket joins the gold
    beside it instead of showing as a paper fleck. ``also``: other ink that bounds the pockets."""
    from dataclasses import replace
    from inkkit import geom as G
    marks = list(f.marks) + (list(also.marks) if also is not None else [])
    ink = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in marks if m.kind != "fill"]
                            + [K.R(shape).boundary.buffer(CONTOUR / 2, quad_segs=8)])
    vis = K.R(shape).difference(ink)
    pockets = [g for g in K._polys_of(vis)
               if g.area < max_area and g.buffer(-open_r, quad_segs=6).is_empty]
    if not pockets:
        return f
    pk = shapely.union_all(pockets)
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d or m.role != "hatch":
            out.append(m)
            continue
        subs = [C.polyline_d(pts, closed=cl) for pts, cl in G.flatten(m.d, 0.05)
                if LineString(np.asarray(pts)).distance(pk) > m.w / 2 + 0.3]
        if subs:
            out.append(replace(m, d="".join(subs)))
    return C.Frag(out, f.meta)


def _rot(p, c, deg):
    a = math.radians(deg)
    v = np.asarray(p, float) - np.asarray(c, float)
    return np.asarray(c, float) + np.array([v[0] * math.cos(a) - v[1] * math.sin(a),
                                            v[0] * math.sin(a) + v[1] * math.cos(a)])


def knee_crown(cx=AX, *, band_top=152.0, band_h=30.0, band_hw=74.0, bow=4.0, vanish=(AX, 640.0),
               H=64.0, heights=(0.65, 0.8, 1.0, 0.8, 0.65), xs=(-58.0, -30.0, 0.0, 30.0, 58.0),
               widths=(30.0, 33.0, 38.0, 33.0, 30.0), knob=0.22, beta=34.0, flare=62.0, lean_k=1.4,
               flutes=2, centre_off=7.0, ripple=(2, 22.0, 1.8), studs=0, flute_mode="axis", form="cone", side_k=1.5,
               order="front", side_gap=0.0, wave_top=None, bed_k=0.46,
               half_joint=True, centre_mode="chevron", half_gap=0.0, lean_hatch=0.0,
               hatch_phase=(0.0, 0.0), min_hatch=0.0, ripple_offs=None) -> K.Part:
    """The Knee Crown. Knees lean out on rays from ``vanish`` (the crown
    flares like the K♠'s) and the band's ends are rays from the same point.
    Exactly mirror-symmetric. ``min_hatch`` drops hatch pieces shorter than
    it; ``ripple_offs`` sets each ripple line's depth below the band top."""
    v = P(vanish)
    edge = math.degrees(math.atan2(band_hw, v[1] - band_top))
    band, band_d = K.crown_band(cx, band_top, band_h, band_hw, bow, v=v, edge_deg=edge)
    if wave_top:
        # the waterline: the band's top edge is a ripple (λ, A) the knees rise out of
        lam_w, amp_w = wave_top
        x0b, y0b, x1b, y1b = band.bounds
        xs_w = np.linspace(x0b - 5, x1b + 5, 600)
        ys_w = [band_top - bow * ((xx - cx) / band_hw) ** 2 + amp_w * math.cos(2 * math.pi * (xx - cx) / lam_w)
                for xx in xs_w]
        cutter = shapely.geometry.Polygon(list(zip(xs_w, ys_w)) + [(x1b + 5, y1b + 50), (x0b - 5, y1b + 50)]).buffer(0)
        band = band.intersection(cutter)
        band_d = K.D(band)

    def top_y(x):
        t = (x - cx) / band_hw
        return band_top - bow * t * t

    knees = []
    for dx, hk, bw in zip(xs, heights, widths):
        x = cx + dx
        yb = top_y(x) + 1.0
        lean = lean_k * math.degrees(math.atan2(dx, v[1] - yb))
        if form == "cone":
            reg, kc_, rt = knee_cone(x, yb, H * hk, bw, fillet=knob, side_k=side_k)
        else:
            reg, kc_, rt = knee(x, yb, H * hk, bw, knob=knob, beta=beta, flare=flare)
        reg = shapely.affinity.rotate(reg, lean, origin=(x, yb))
        kc_r = _rot(kc_, (x, yb), lean)
        u = np.array([math.sin(math.radians(lean)), -math.cos(math.radians(lean))])   # up the axis
        knees.append(dict(reg=reg, kc=kc_r, rt=rt, base=P(x, yb), u=u, dx=dx))
    kn_all = K.U(*[k["reg"] for k in knees])
    shape = K.U(band, kn_all)
    lines = C.Frag()
    # z-order: 'front' = a clump, the tallest (centre) in front, each outer
    # knee behind its inner neighbour; 'merge' = one silhouette
    zorder = sorted(range(len(knees)), key=lambda i: abs(knees[i]["dx"]))       # front first
    front_of = {}
    acc = None
    for i in zorder:
        front_of[i] = acc
        acc = knees[i]["reg"] if acc is None else acc.union(knees[i]["reg"])
    if order == "merge":
        lines += K.clip_out(K.outline(kn_all), band, eps=-0.5, trap=0.0)
    for i, k in enumerate(knees):
        own = k["reg"]
        cover = band if (order == "merge" or front_of[i] is None) else band.union(front_of[i])
        if order != "merge":
            lines += K.clip_out(K.outline(own), cover, eps=-0.5, trap=0.0)
        u, b = k["u"], k["base"]
        n_ = np.array([-u[1], u[0]])
        sides = (-1, 1) if k["dx"] == 0 else ((1,) if k["dx"] > 0 else (-1,))
        if order == "merge":
            others = K.U(*[o["reg"] for o in knees if o is not k])
            zone = own.difference(others.buffer(CONTOUR / 2 + GAP))
        else:
            zone = own
        if flute_mode == "diag":
            for sd in sides:
                half = _side_half(own, b, u, sd)
                if k["dx"] == 0:
                    half = half.difference(K.box(b[0] - centre_off, 0, b[0] + centre_off, 2000))
                ang = -45.0 if sd < 0 else -135.0
                lines += K.clip_out(K.clip_in(K.hatch_in(half, angle=ang, origin=tuple(b)), zone), cover,
                                    eps=-0.5, trap=0.0)
            continue
        if flute_mode == "half":
            # §B.2 / §G.17 'fluted with half-hatch': each side knee's OUTER
            # half hatched at 45° (FINE, 7.0 pitch, butting on the outline),
            # the terminator on the knee's own axis; ``half_joint`` draws a
            # FINE joint there (the K♠ merlon split). The centre knee
            # (``centre_mode``): 'chevron' — a FINE bedding line, the lower
            # course hatched mirror-wise (the K♠ centre merlon); 'flanks' —
            # both flanks hatched mirror-wise, a lit strip ``centre_off``
            # either side of the axis left plain (a rounded form lit from
            # the front); 'one' — its left half only (asymmetric)
            if k["dx"] != 0:
                sd = 1 if k["dx"] > 0 else -1
                half = _side_half(own, b, u, sd)
                if half_gap:
                    half = half.difference(_side_half(own, b, u, -sd).buffer(half_gap))
                ang = (-45.0 if sd > 0 else -135.0) + (lean_hatch * math.degrees(math.atan2(u[0], -u[1])))
                org = tuple(b + u * 200.0 + np.array([sd * hatch_phase[0], 0.0]))
                lines += K.clip_out(K.clip_in(K.hatch_in(half, angle=ang, origin=org), zone), cover,
                                    eps=-0.5, trap=0.0)
                if half_joint:
                    jl = LineString([tuple(b - u * 40.0), tuple(b + u * 200.0)]).intersection(own)
                    for g in K._lines_of(jl):
                        lines += K.clip_out(K.line(np.asarray(g.coords), FINE, style="hatch", role="joint"), cover,
                                            eps=-0.5, trap=0.0)
            else:
                y_top = own.bounds[1]
                ym = y_top + (b[1] - y_top) * bed_k if centre_mode == "chevron" else -1000.0
                if centre_mode == "chevron":
                    bed = LineString([(b[0] - 200.0, ym), (b[0] + 200.0, ym)]).intersection(own)
                    for g in K._lines_of(bed):
                        lines += K.clip_out(K.line(np.asarray(g.coords), FINE, style="rule", role="bed"), cover,
                                            eps=-0.5, trap=0.0)
                lo = own.intersection(K.box(0, ym, 2000, 2000))
                sides_c = ((-1, -135.0),) if centre_mode == "one" else ((-1, -135.0), (1, -45.0))
                co = centre_off if centre_mode == "flanks" else 0.0
                for sd, ang in sides_c:
                    hh = lo.intersection(K.box(0, 0, b[0] - co, 2000) if sd < 0 else K.box(b[0] + co, 0, 2000, 2000))
                    lines += K.clip_out(K.clip_in(K.hatch_in(hh, angle=ang, origin=(b[0] + hatch_phase[1], y_top)), zone), cover,
                                        eps=-0.5, trap=0.0)
                if half_joint and centre_mode != "flanks":
                    jl = LineString([(b[0], max(ym, y_top - 10)), (b[0], b[1] + 40.0)]).intersection(own)
                    for g in K._lines_of(jl):
                        lines += K.clip_out(K.line(np.asarray(g.coords), FINE, style="hatch", role="joint"), cover,
                                            eps=-0.5, trap=0.0)
            continue
        if flute_mode == "side":
            # flutes follow the knee's own outer side (offset curves of its
            # outline), converging on the knob: bark striations round the form
            for sd in sides:
                nn = n_ if (n_[0] * sd) > 0 else -n_
                half = own.intersection(K.halfplane(tuple(b + u * 200.0), tuple(b - u * 60.0), side=+1 if sd > 0 else -1))
                if half.is_empty or half.area < 1:
                    half = own.intersection(K.halfplane(tuple(b + u * 200.0), tuple(b - u * 60.0), side=-1 if sd > 0 else 1))
                # keep only the half on the outer side
                cands = [g for g in K._polys_of(half)]
                for j in range(flutes):
                    off = K.EDGE_CON + 7.0 * j
                    ring = own.buffer(-off, quad_segs=16).boundary
                    ln = ring.intersection(zone.intersection(_side_half(own, b, u, sd).buffer(-side_gap)))
                    for g in K._lines_of(ln):
                        if g.length > 6:
                            lines += K.clip_out(K.line(np.asarray(g.coords), FINE, style="hatch", role="flute"),
                                                cover.buffer(0.0), eps=-0.5, trap=0.0)
            continue
        for sd in sides:
            nn = n_ if (n_[0] * sd) > 0 else -n_
            for j in range(flutes):
                off = (centre_off + 7.0 * j) if k["dx"] == 0 else 7.0 * (j + 1)
                o = nn * off
                ln = LineString([tuple(b + o - u * 40.0), tuple(b + o + u * 160.0)]).intersection(zone)
                for g in K._lines_of(ln):
                    if g.length > 6:
                        lines += K.clip_out(K.line(np.asarray(g.coords), FINE, style="hatch", role="flute"),
                                            cover, eps=-0.5, trap=0.0)
    if min_hatch:
        # a hatch end in a knee's tip or in the acute corner over the band leaves a stub, and the gold
        # crumb it cuts off is too small for visible_fill, so it shows as a paper fleck
        lines = _drop_short_hatch(lines, min_hatch)
        lines = _drop_pocket_hatch(shape, lines, also=K.outline(band_d))
    lines += K.outline(band_d)
    from art._kc_util import visible_fill
    fills = K.fill(visible_fill(shape, lines, shape), GOLD)
    n_rip, lam, amp = ripple
    inner_band = band.buffer(-(MEDIUM / 2 + GAP + FINE / 2))
    for jj in range(n_rip):
        off = ripple_offs[jj] if ripple_offs else band_h * (jj + 1) / (n_rip + 1)
        xs_ = np.linspace(cx - band_hw - 10, cx + band_hw + 10, 900)
        ys_ = np.array([top_y(xx) + off + amp * math.cos(2 * math.pi * (xx - cx) / lam) for xx in xs_])
        ln = LineString(np.column_stack([xs_, ys_])).intersection(inner_band)
        for l_ in K._lines_of(ln):
            lines += K.line(np.asarray(l_.coords), FINE, role="ripple")
    return K.Part(shape, fills, lines, {"band": band, "top_y": top_y, "knees": knees})
