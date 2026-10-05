"""K♣ · The Cypress King — the parts the shared kit does not have (brief §H.7).

Everything here is built the kit's way (deck.courtkit): compass arcs and
tangent-arc splines, final size, legal widths, no paint in paper. Each
builder returns a courtkit ``Part`` (opaque shape, fills, lines, meta) that
art/KC.py stacks in a ``Scene``.

    knee_crown     the Knee Crown: five gold cypress knees on a ripple band
    comb_beard     the two-pointed beard of flat comb sprays (gold)
    robe           the jade robe: buttress silhouette + vertical buttress fluting
    stole          one Gill Red stole band with comb sprays knocked out
    spray_collar   the gold comb-spray collar (a collar of office: sprays and
                   cones) carrying the Lion Mark
    cone_orb       the orb: a gold bald-cypress cone of wrinkled scale plates
    cypress_staff  the fluted cypress staff (paper wood, gold ferrules)
    kingfisher     the wrought-gold belted kingfisher finial (sculpture, perched)
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import geometric as MG

P, AX = K.P, K.AX
FINE, MEDIUM, RULE, CONTOUR, HAIR = T.FINE, T.MEDIUM, T.RULE, T.CONTOUR, T.HAIRLINE
INK, RED, JADE, GOLD = T.INK, T.RED, T.JADE, T.FOIL
GAP, GAP_MARK = K.GAP, K.GAP_MARK


def _unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def _pts(d, step=0.4):
    return C.sample_d(d, step)[0][0]


def _rot(p, c, deg):
    """Rotate point p about c by deg (screen, clockwise)."""
    a = math.radians(deg)
    v = np.asarray(p, float) - np.asarray(c, float)
    return np.asarray(c, float) + np.array([v[0] * math.cos(a) - v[1] * math.sin(a),
                                            v[0] * math.sin(a) + v[1] * math.cos(a)])


# =============================================================================
# the Knee Crown (§H.7, §G.17)
# =============================================================================
def knee_region(x, y, h, base_w, fillet=None, side_r=None, depth=14.0):
    """One cypress knee standing on (x, y) as a closed region: two convex side
    arcs meeting in a top fillet (§G.17), closed ``depth`` px below its base
    (the part hidden behind the band)."""
    f = MG.cypress_knee(x, y, h, base_w, fillet=fillet, side_r=side_r)
    d = f.marks[0].d
    pts = _pts(d, 0.3)
    pts = np.vstack([pts, [[pts[-1][0], y + depth], [pts[0][0], y + depth]]])
    return Polygon(pts).buffer(0), f.meta["knee_top"]


def knee_bell(x, y, h, bw, knob_r=9.0, beta=14.0, flare=28.0, depth=24.0):
    """A cypress knee as it stands in water (§G.17 read botanically): a
    buttressed base flaring into the waterline (concave sides, biarcs) and a
    rounded knob at the top, slightly swollen above a gentle neck. Standing
    on (x, y), ``h`` tall, ``bw`` wide at the waterline. → (region, knob
    centre)."""
    from deck.motifs import forms as FM
    kc = P(x, y - h + knob_r)
    th = math.radians(180.0 - beta)
    Tl = kc + knob_r * np.array([math.cos(th), math.sin(th)])
    Tr = P(2 * x - Tl[0], Tl[1])
    A = P(x - bw / 2, y)
    B = P(x + bw / 2, y)
    s1, _ = FM.biarc(A, -flare, Tl, -90.0 - beta)
    knob = C.arc_between(kc, knob_r, Tl, Tr, cw=True)
    s2, _ = FM.biarc(Tr, 90.0 + beta, B, flare)
    d = f"M{A[0]:.3f} {A[1]:.3f}" + s1 + knob + s2 + f"L{B[0]:.3f} {y + depth:.3f}L{A[0]:.3f} {y + depth:.3f}Z"
    return K.R(d), kc


def knee_crown(cx=AX, *, band_top=150.0, band_h=30.0, band_hw=68.0, bow=4.0, vanish=(AX, 700.0),
               H=64.0, heights=(0.65, 0.8, 1.0, 0.8, 0.65), xs=(-50.0, -26.0, 0.0, 26.0, 50.0),
               widths=(28.0, 32.0, 34.0, 32.0, 28.0), ripple=(2, 20.0, 1.7), fillet_k=0.30, side_k=1.5,
               flute_offs=(7.0,), jewel=None, shape="bell", knob_k=0.30, beta=14.0, flare=28.0,
               joint=True, flute_mode="parallel", conv=0.25) -> K.Part:
    """The Knee Crown (§H.7, §G.17): a CLUMP of five gold cypress knees at
    heights 0.65 / 0.8 / 1.0 / 0.8 / 0.65 rising from a gold band of ripple
    lines (the water they stand in). Knees grow in clumps, so they overlap:
    the centre knee in front, each outer pair behind the next — five
    rounded peaks in one crown silhouette. Each knee leans out on a ray
    from ``vanish`` (the crown flares like the K♠'s).

    Fluted with half-hatch: every side knee is split on its axis by a FINE
    joint and its OUTER (visible) half carries flutes — FINE lines parallel
    to the knee's axis at a 7 px pitch; the centre knee, seen whole, is
    fluted symmetrically either side of its joint (a single-sided hatch
    cannot be mirror-symmetric, the K♠ centre-merlon rule). Exactly
    mirror-symmetric."""
    v = P(vanish)
    edge = math.degrees(math.atan2(band_hw, v[1] - band_top))
    band, band_d = K.crown_band(cx, band_top, band_h, band_hw, bow, v=v, edge_deg=edge)

    def top_y(x):
        t = (x - cx) / band_hw
        return band_top - bow * t * t

    order = sorted(range(len(xs)), key=lambda k: -abs(xs[k]))          # back (outer) to front (centre)
    knees = {}
    for k in order:
        dx, hk, bw = xs[k], heights[k], widths[k]
        x = cx + dx
        yb = top_y(x) + 1.0
        lean = math.degrees(math.atan2(dx, v[1] - yb))
        if shape == "bell":
            reg, kc_ = knee_bell(x, yb, H * hk, bw, knob_r=knob_k * bw, beta=beta, flare=flare)
            ktop = kc_[1] - knob_k * bw
        else:
            reg, ktop = knee_region(x, yb, H * hk, bw, fillet=fillet_k * bw, side_r=side_k * H * hk, depth=24.0)
        reg = shapely.affinity.rotate(reg, lean, origin=(x, yb))
        a_top = _rot((x, ktop), (x, yb), lean)
        a_bot = _rot((x, yb + 20.0), (x, yb), lean)
        knees[k] = (reg, a_top, a_bot, dx)
    fills, lines = C.Frag(), C.Frag()
    acc = band                                               # what is in front, built front to back
    for k in reversed(order):                                # front (centre) first
        reg, a_top, a_bot, dx = knees[k]
        u = (a_bot - a_top) / np.hypot(*(a_bot - a_top))
        n = np.array([-u[1], u[0]])                          # +x side for a downward axis
        if n[0] < 0:
            n = -n
        own = C.Frag()
        own += K.outline(reg)
        # flutes: the hatched half (outer half; both halves for the centre knee)
        sides = (-1, 1) if dx == 0 else ((1,) if dx > 0 else (-1,))
        inner = reg.buffer(-(CONTOUR / 2 + GAP + FINE / 2 + 0.05))
        for sd in sides:
            if flute_mode == "across":
                half_ = reg.intersection(K.halfplane(a_top, a_bot, side=+1 if sd * n[0] * (1 if u[1] > 0 else -1) < 0 else -1))
                half_ = half_.difference(band.buffer(-0.5))
                own += K.hatch_in(half_, angle=math.degrees(math.atan2(n[1], n[0])), origin=tuple(a_top))
                continue
            for o in flute_offs:
                if flute_mode == "converge":
                    base_p = a_bot - u * 20.0 + n * sd * o
                    top_p = a_top + n * sd * o * conv
                    v_ = (top_p - base_p) / np.hypot(*(top_p - base_p))
                    p0, p1 = top_p + v_ * 2.0, base_p - v_ * 12.0
                else:
                    p0 = a_top + n * sd * o - u * 30.0
                    p1 = a_bot + n * sd * o + u * 10.0
                ln = LineString([tuple(p0), tuple(p1)]).intersection(inner)
                for l_ in K._lines_of(ln):
                    if l_.length > 8:
                        own += K.line(np.asarray(l_.coords), FINE, style="hatch", role="flute")
        # the axis joint (the split of the half-hatch), from below the fillet
        if joint:
            j0 = a_top + u * (fillet_k * widths[k] + 5.0)
            own += K.line(np.vstack([j0, a_bot]), FINE, role="joint")
        own = K.clip_out(own, acc, eps=-0.5, trap=0.0)
        fl = K.clip_out(K.fill(reg, GOLD), acc, trap=1.6)
        lines += own
        fills += fl
        acc = acc.union(reg.buffer(0.3))
    shape = K.U(band, *[knees[k][0] for k in knees])
    fills = fills + K.fill(band, GOLD)
    lines = lines + K.outline(band_d)
    # ripple lines along the band (the water): phase-locked cosines, so they
    # are mirror-symmetric and keep a constant pitch
    n_rip, lam, amp = ripple
    inner_band = band.buffer(-(MEDIUM / 2 + GAP + FINE / 2))
    for jj in range(n_rip):
        off = band_h * (jj + 1) / (n_rip + 1)
        xs_ = np.linspace(cx - band_hw - 10, cx + band_hw + 10, 900)
        ys_ = np.array([top_y(xx) + off + amp * math.cos(2 * math.pi * (xx - cx) / lam) for xx in xs_])
        ln = LineString(np.column_stack([xs_, ys_])).intersection(inner_band)
        for l_ in K._lines_of(ln):
            lines += K.line(np.asarray(l_.coords), FINE, role="ripple")
    return K.Part(shape, fills, lines, {"band": band, "top_y": top_y})


# =============================================================================
# the comb-spray beard (§H.7: 'a two-pointed beard of flat comb sprays in gold')
# =============================================================================
def comb_ticks(rachis, region, *, pitch=8.0, angle=48.0, start=6.0, end=4.0, clear=None, w=FINE,
               sides=(1, -1), max_len=None, min_len=3.5, color=INK, role="tick", edge_w=MEDIUM):
    """Comb-spray ticks (§G.18) off a rachis (points, base → tip), swept
    ``angle`` toward the tip, each running until it comes ``clear`` px from
    the region's edge (default: 4.2 px of paper inside a MEDIUM edge, so a
    tick that ends running alongside the edge still keeps §I.12's parallel
    gap). The pitch is raised so neighbouring ticks keep 4.2 px. → Frag of
    FINE strokes (free ends: the comb's teeth)."""
    cv = K.G.Curve(np.asarray(rachis, float))
    reg = K.R(region)
    clear = (edge_w / 2 + GAP + w / 2 + 0.2) if clear is None else clear
    inner = reg.buffer(-clear, quad_segs=12)
    f = C.Frag()
    sa = math.sin(math.radians(angle))
    pitch = max(pitch, (w + GAP + 0.3) / sa)
    L = cv.length
    ss = np.arange(start, L - end, pitch)
    for s in ss:
        p = cv.at_s(s)
        t = cv.tangent_s(s)
        a = math.atan2(t[1], t[0])
        for sd in sides:
            ang = a - sd * math.radians(angle)
            u = np.array([math.cos(ang), math.sin(ang)])
            Lmax = max_len if max_len else 200.0
            ln = LineString([tuple(p + u * 0.1), tuple(p + u * Lmax)]).intersection(inner)
            segs = [g for g in K._lines_of(ln) if g.distance(Point(*p)) < 1.0]
            if not segs:
                continue
            g = segs[0]
            if g.length < min_len:
                continue
            q = np.asarray(g.coords)
            f += K.line(np.vstack([p, q[-1]]) if np.hypot(*(q[0] - p)) < 1.0 else q, w, role=role, color=color)
    return f


def comb_beard(fc, mo, *, side=(-42.0, 20.0), bulge=(-46.0, 76.0), tip=(-17.0, 130.0), notch_dy=106.0,
               rachis=((-27.0, 58.0), (-23.0, 90.0), (-16.0, 118.0)), pitch=7.6, angle=45.0, max_len=16.0,
               terminal=True) -> K.Part:
    """The two-pointed beard (§H.7 'a two-pointed beard of flat comb sprays
    in gold'). Its SHAPE is the kit's forked beard (it tucks under the
    moustache and clears the mouth exactly like the K♠'s); each lobe carries
    one flat §G.18 comb spray hanging from under the mouth to the point: a
    FINE rachis rolling into a Ø6.3 terminal above the point (hair's
    language, not a leaf's), and comb ticks both sides swept toward the
    point, each stopping 4.2 px inside the lobe's edge. The beard's outline
    stays a beard's (smooth, no serrations) and the cheeks stay plain gold,
    so it never reads as a leaf-face."""
    b = K.beard(fc, K.BeardSpec(side=side, bulge=bulge, tip=tip, notch_dy=notch_dy, lines=3), mo=mo)
    ax = float(fc.anchors["axis"])
    cx, cy = fc.anchors["center"]
    half = b.shape.intersection(K.box(0, 0, ax, 2000))
    half = max(K._polys_of(half), key=lambda g: g.area)
    r0, r1, r2 = [P(ax + a, cy + c) for a, c in rachis]
    rp = _pts(K.arc3(r0, r1, r2), 0.4)
    lines = K.line(rp, FINE, role="rachis")
    if terminal:
        lines += K.dot(rp[-1], K.TD, role="terminal")
    zone = half.difference(K.box(ax - 2.0, 0, 2000, 2000))
    lines += comb_ticks(rp, zone, pitch=pitch, angle=angle, start=4.0, end=9.0 if terminal else 3.0,
                        max_len=max_len)
    lines = lines + lines.mirror_x(ax)
    return K.Part(b.shape, K.fill(b.shape, GOLD), lines + K.outline(b.shape), dict(b.meta))


def comb_beard_edge(fc, mo, *, side=(-42.0, 20.0), bulge=(-46.0, 76.0), tip=(-17.0, 130.0), notch_dy=106.0,
                    first=9.5, pitch=7.6, angle=40.0, max_len=18.0, start=20.0, end=16.0, axis_gap=2.0,
                    rachis_line=True) -> K.Part:
    """Variant: each lobe a one-sided comb spray whose rachis follows the
    OUTER edge (a current line rolling into its terminal at the point) and
    whose teeth sweep down and IN toward the point — the two lobes' teeth
    make V chevrons converging on the fork (hair combed to the points,
    never a fir tree's Λ)."""
    b = K.beard(fc, K.BeardSpec(side=side, bulge=bulge, tip=tip, notch_dy=notch_dy, lines=3), mo=mo)
    ax = float(fc.anchors["axis"])
    cx, cy = fc.anchors["center"]
    half = b.shape.intersection(K.box(0, 0, ax, 2000))
    half = max(K._polys_of(half), key=lambda g: g.area)
    S = P(ax + side[0], cy + side[1])
    Bg = P(ax + bulge[0], cy + bulge[1])
    Ft = P(ax + tip[0], cy + tip[1])
    gpts = _pts(K.arc3(S, Bg, Ft), 0.4)
    t0 = gpts[1] - gpts[0]
    t0 = t0 / np.hypot(*t0)
    gpts = np.vstack([gpts[0] - t0 * 30.0, gpts])
    rl = K.current_lines(gpts, 1, half, side=+1, first=first, edge=MEDIUM, stagger=0.0)
    lines = rl if rachis_line else C.Frag()
    q = rl.meta["lines"][0]
    zone = half.difference(K.box(ax - axis_gap, 0, 2000, 2000))
    lines += comb_ticks(q, zone, pitch=pitch, angle=angle, start=start, end=end, sides=(1,), max_len=max_len)
    lines = lines + lines.mirror_x(ax)
    return K.Part(b.shape, K.fill(b.shape, GOLD), lines + K.outline(b.shape), dict(b.meta))


# =============================================================================
# the robe: a buttressed trunk (§H.7 'jade, with vertical buttress fluting')
# =============================================================================
def robe_outline(neck_y=284.0, neck_heading=171.0, yoke_r=380.0, yoke_sweep=7.0, run=136.0, corner_r=30.0,
                 side_heading=92.0, flare_r=420.0, flare=14.0, bottom=548.0):
    """Left half of the robe outline, from the axis at the neck: the yoke,
    the shoulder corner, then the side FLARING outward in a concave arc like
    a bald cypress's buttressed base (heading ``side_heading`` → +``flare``)."""
    t = C.Turtle(AX, neck_y, neck_heading)
    t.arc(yoke_r, -yoke_sweep)
    t.fd(run)
    t.arc(corner_r, -(neck_heading - yoke_sweep - side_heading))
    t.arc(flare_r, flare)
    y0 = t.pos[1]
    Lr = (bottom - y0) / math.sin(math.radians(t.heading))
    t.fd(max(Lr, 0.0))
    return np.asarray(t.pts(0.5)[0])


def flute_u(xt, yt, xb, yb, w_top=6.3, w_bot=11.0):
    """One flute (a fluted column's groove): a long narrow U — two FINE lines
    from the bottom up to a round top of Ø ``w_top`` (centre to centre, so
    4.2 px of ground stays inside it), widening to ``w_bot`` at the bottom.
    → path d (one stroke, no free ends above the clip)."""
    c = P(xt, yt + w_top / 2)
    L0 = P(xb - w_bot / 2, yb)
    R0 = P(xb + w_bot / 2, yb)
    Lt = P(xt - w_top / 2, yt + w_top / 2)
    Rt = P(xt + w_top / 2, yt + w_top / 2)
    return (f"M{L0[0]:.3f} {L0[1]:.3f}L{Lt[0]:.3f} {Lt[1]:.3f}" + C.arc_between(c, w_top / 2, Lt, Rt, cw=True)
            + f"L{R0[0]:.3f} {R0[1]:.3f}")


def robe(*, border=30.0, pitch0=20.0, vanish_y=-420.0, w_top=6.3, w_bot=11.5, long_drop=12.0, short_drop=44.0,
         **kw) -> K.Part:
    """The jade robe (§H.7 'jade, with vertical buttress fluting in Aquifer,
    widening downward'): a bilateral silhouette whose sides flare out in a
    concave arc to the band like a bald cypress's buttressed base; a plain
    border band + FINE seam (so no flute grazes a sloping contour); inside
    it the fluting — long narrow U-grooves on rays from a point high above
    the head, so they spread and each groove widens downward; alternate
    grooves start lower (the buttress rhythm of a fluted trunk)."""
    pts = robe_outline(**kw)
    bottom = pts[-1][1]
    half = Polygon(np.vstack([pts, [[AX, bottom]]])).buffer(0)
    shape = K.U(half, K.mirror(half))
    ext = np.vstack([pts, [[pts[-1][0] - 60.0, bottom + 300.0], [AX, bottom + 300.0]]])
    ext_half = Polygon(ext).buffer(0)
    ext_shape = K.U(ext_half, K.mirror(ext_half))
    inner = ext_shape.buffer(-border, quad_segs=16).intersection(K.box(0, 0, 2000, bottom + 20))
    lines = K.outline(shape)
    lines += C.stroke(K.D(inner), FINE, role="seam")
    zone = inner.buffer(-0.01)
    y_ref = 300.0
    f = C.Frag()
    for k in range(-14, 15):
        xr = AX + k * pitch0
        u = P(xr - AX, y_ref - vanish_y)
        # the seam's y above this ray: first inside point
        ys = np.arange(250.0, 520.0, 0.5)
        xs_ = AX + (xr - AX) * (ys - vanish_y) / (y_ref - vanish_y)
        ins = [zone.contains(Point(x_, y_)) for x_, y_ in zip(xs_, ys)]
        if not any(ins):
            continue
        y_in = ys[int(np.argmax(ins))]
        yt = y_in + (long_drop if k % 2 == 0 else short_drop)
        xt = AX + (xr - AX) * (yt - vanish_y) / (y_ref - vanish_y)
        yb = bottom + 10.0
        xb = AX + (xr - AX) * (yb - vanish_y) / (y_ref - vanish_y)
        d = flute_u(xt, yt, xb, yb, w_top, w_bot)
        fl = K.clip_in(K.line(d, FINE, role="flute"), zone)
        f += fl
    lines += f
    return K.Part(shape, K.fill(shape, JADE), lines, {"inner": inner, "half": pts})


# =============================================================================
# the stole (§H.7 'Gill Red, with comb sprays knocked out')
# =============================================================================
def stole(side=-1, *, within=None, x_in=356.0, x_out=306.0, shoulder=(286.0, 300.0), knee_y=372.0,
          bottom=548.0, sprays=((344.0, 424.0), (436.0, 516.0)), tick=18.0, pitch=9.5, angle=50.0,
          cone_r=6.3) -> K.Part:
    """One side of the stole (§H.7 'Stole: Gill Red, with comb sprays knocked
    out'; left, ``side`` +1 mirrors): a broad red band that comes over the
    shoulder from behind the neck (its top is the robe's own neckline, so it
    shows on the shoulder line), sweeps in to hang straight from
    ``knee_y`` to the band between ``x_out`` and ``x_in``. Down its mid-line
    a column of comb sprays (§G.18) pointing down, each ending in a round
    cone, KNOCKED OUT to paper at MEDIUM (knockout lines ≥ 2.5 px) — the red
    stays one solid with holes."""
    # outer edge: from the shoulder point, an arc sweeping in to x_out, then plumb
    sh = P(shoulder)
    outer = K.Path(P(sh[0] - 30.0, sh[1] - 40.0)).line(sh).arc3(
        P((sh[0] + x_out) / 2 + 3.0, (sh[1] + knee_y) / 2), P(x_out, knee_y)).line((x_out, bottom))
    reg = K.R(outer.line((x_in, bottom)).line((x_in, sh[1] - 60.0)).close().d)
    if within is not None:
        reg = reg.intersection(K.R(within))
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    xc = (x_in + x_out) / 2
    ko = C.Frag()
    for (ya, yb) in sprays:
        rach = np.array([[xc, yb], [xc, ya]])          # base at the bottom: the sprays point UP (a fern's V, never a fir's Λ)
        ko += MG.comb_spray(rach, pitch=pitch, tick=tick, angle=angle, start=4.0, cone=cone_r, min_tick=4.0,
                            w=MEDIUM)
    fill_d = C.knockout(K.D(reg), ko)
    part = K.Part(reg, K.fill(fill_d, RED), K.outline(reg), {"x": (x_out, x_in)})
    return part.mirrored(AX) if side > 0 else part


# =============================================================================
# the comb-spray collar of office (§H.7 'Collar: a gold comb-spray collar')
# =============================================================================
def spray_link(p0, p1, width=15.0, r=5.0):
    """One collar link: a flat gold plaque (a rounded oblong — not a leaf)
    engraved with a comb spray: a FINE rachis end to end and comb ticks
    both sides swept toward p1, butting onto the plaque's edge like hatch.
    → (region, lines)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    u = (p1 - p0) / L
    n = np.array([-u[1], u[0]])
    hw = width / 2
    reg = shapely.affinity.affine_transform(K.R(K.rrect(0, 0, L, width, r)),
                                            (u[0], n[0], u[1], n[1], p0[0] - n[0] * hw, p0[1] - n[1] * hw))
    a = p0 + u * 4.0
    b = p1 - u * 4.0
    lines = K.line(np.vstack([a, b]), FINE, role="rachis")
    inner = reg.buffer(-(MEDIUM / 2 - 0.3))
    sa = math.radians(58.0)
    pitch = (FINE + GAP + 0.3) / math.sin(sa)
    s = 5.0
    while s < L - 6.0:
        p = p0 + u * s
        for sd in (-1, 1):
            v = u * math.cos(sa) + n * sd * math.sin(sa)
            ln = LineString([tuple(p), tuple(p + v * 30)]).intersection(inner)
            for l_ in K._lines_of(ln):
                if l_.length > 3:
                    lines += K.line(np.asarray(l_.coords), FINE, style="hatch", role="tick")
        s += pitch
    return reg, lines


def spray_collar(*, through=(250.0, 292.0), low=(AX, 366.0), n_links=4, link_len=30.0, link_w=15.0,
                 bead_r=7.5, gap=1.0, centre_gap=19.0, within=None) -> K.Part:
    """The collar of office (§H.7 'a gold comb-spray collar'): a livery
    collar lying on the shoulders and hanging to the chest along one circular
    arc through ``low``, alternating round cypress-cone beads and flat
    comb-spray links, all solid gold with an Aquifer contour (legal where it
    crosses the red stole, §C.4). ``within`` (the robe): the collar is
    clipped to it — it goes over the shoulders and on behind."""
    L = P(through)
    Rr_ = P(2 * AX - through[0], through[1])
    c, r = K.circ3(L, P(low), Rr_)
    a_low = 90.0
    regs, lines = [], C.Frag()
    s = centre_gap
    for i in range(n_links):
        a = a_low + math.degrees((s + bead_r) / r)
        bc = K.polar(c, r, a)
        regs.append(Point(*bc).buffer(bead_r, quad_segs=24))
        lines += K.dot(bc, 4.2, role="umbo")
        s += 2 * bead_r + gap
        a0 = a_low + math.degrees(s / r)
        a1 = a_low + math.degrees((s + link_len) / r)
        p0, p1 = K.polar(c, r, a0), K.polar(c, r, a1)
        reg, ln = spray_link(p0, p1, link_w)
        regs.append(reg)
        lines += ln
        s += link_len + gap
    a = a_low + math.degrees((s + bead_r) / r)
    regs.append(Point(*K.polar(c, r, a)).buffer(bead_r, quad_segs=24))
    lines += K.dot(K.polar(c, r, a), 4.2, role="umbo")
    left = K.U(*regs)
    shape = K.U(left, K.mirror(left))
    lines = lines + lines.mirror_x(AX)
    if within is not None:
        zone = K.R(within).buffer(-0.5)
        shape = shape.intersection(zone)
        shape = K.U(*[g for g in K._polys_of(shape) if g.area > 60.0])
        keep = zone.buffer(-(CONTOUR / 2 + GAP_MARK + FINE / 2 + 1.0))
        lines = C.Frag([m for m in lines.marks if m.role != "umbo" or keep.contains(K.R(K.G.from_skia(m.skia())))])
        lines = K.clip_in(lines, keep)
    fills = K.fill(shape, GOLD)
    lines = K.outline(shape, MEDIUM) + lines
    return K.Part(shape, fills, lines, {"c": c, "r": r})


# =============================================================================
# the cone orb (§H.7 'a gold cypress cone, a sphere of wrinkled scale-plates')
# =============================================================================
def cone_orb(c, r=32.0, *, inner=0.52, n_rim=8, rot=0.0, stalk=True) -> K.Part:
    """The orb (§H.7 'a gold cypress cone, a sphere of wrinkled
    scale-plates'): a gold sphere cracked into peltate scale plates — a
    centre plate (a curved square, its edges bowed out) ringed by
    ``n_rim`` rim plates (MEDIUM seams from the centre plate's corners and
    edge-midpoints to the rim). Each plate carries its umbo (the scale's
    point: an Aquifer dot) with FINE wrinkles radiating from it. A short
    stalk stub on top (the cone's peduncle) stands where an orb's cross
    would."""
    c = P(c)
    body = K.R(K.circle(c, r))
    lines = K.outline(K.circle(c, r))
    ri = inner * r
    corners = [K.polar(c, ri, rot - 90 + 45 + 90 * k) for k in range(4)]
    cp = K.Path(corners[0])
    for k in range(1, 5):
        cp.sag(corners[k % 4], -2.2)
    centre_plate = K.R(cp.close().d)
    lines += K.outline(centre_plate)
    seams = C.Frag()
    angs = [rot - 90 + 360 * k / n_rim for k in range(n_rim)]
    for k, a in enumerate(angs):
        # from the centre plate's boundary out to the rim
        p_out = K.polar(c, r, a + 22.5)
        ln = LineString([tuple(c), tuple(p_out)]).difference(centre_plate)
        for l_ in K._lines_of(ln):
            seams += K.line(np.asarray(l_.coords), MEDIUM, role="seam")
    lines += seams
    f = C.Frag()
    f += K.dot(c, 6.3, role="umbo")
    for k in range(4):
        a = rot - 90 + 45 + 90 * k
        f += K.line(np.vstack([K.polar(c, 3.0, a), K.polar(c, ri - 6.2, a)]), FINE, role="wrinkle")
    for k, a in enumerate(angs):
        am = a + 45.0
        um = K.polar(c, (ri + r) / 2 + 0.5, am)
        f += K.dot(um, 4.2, role="umbo")
    lines += f
    shape = body
    fills = K.fill(body, GOLD)
    if stalk:
        top = c[1] - r
        st = K.R(K.rrect(c[0] - 4.2, top - 9.0, c[0] + 4.2, top + 3.0, 2.0))
        shape = K.U(body, st)
        fills = K.fill(shape, GOLD)
        lines += K.clip_out(K.outline(st), body, eps=-0.5, trap=0.0)
    return K.Part(shape, fills, lines, {"c": c, "r": r})


# =============================================================================
# the staff (§H.7 'a fluted cypress staff')
# =============================================================================
def cypress_staff(x=540.0, top=185.0, bottom=548.0, hw=13.0, ferrules=(194.0, 300.0), ferrule_hw=17.0,
                  ferrule_h=10.0, flute_dx=5.2, color=RED) -> K.Part:
    """The fluted cypress staff (§H.7): red cypress heartwood with two flutes
    KNOCKED OUT at MEDIUM (a pattern on red is a knockout, §C.4), bound by
    gold ferrules (solid gold with an Aquifer contour — the legal gold on
    red). The flutes stop 3 px short of each ferrule."""
    shaft = K.box(x - hw, top, x + hw, bottom)
    fer = [K.R(K.rrect(x - ferrule_hw, y - ferrule_h / 2, x + ferrule_hw, y + ferrule_h / 2, 3.2)) for y in ferrules]
    shape = K.U(shaft, *fer)
    lines = K.clip_out(K.outline(shaft), K.U(*fer), eps=-0.5, trap=0.0)
    ko = C.Frag()
    ys = [top] + list(ferrules) + [bottom + 20.0]
    for dx in (-flute_dx, flute_dx):
        ko += K.seg(P(x + dx, top - 10), P(x + dx, bottom + 20), MEDIUM, role="flute")
    ko = K.clip_out(ko, K.U(*fer).buffer(GAP_MARK + MEDIUM / 2 + 1.0), eps=0.0, trap=0.0)
    wood = shaft.difference(K.U(*fer).buffer(-0.5))
    fill_d = C.knockout(K.D(wood), ko)
    fills = K.fill(fill_d, color) + C.Frag().add(*[K.fill(g, GOLD) for g in fer])
    lines += C.Frag().add(*[K.outline(g) for g in fer])
    return K.Part(shape, fills, lines, {})


# =============================================================================
# the kingfisher finial (§H.7: wrought gold, ragged crest, dagger bill, perched)
# =============================================================================
def kingfisher(feet=(540.0, 170.0), facing=-1, *, belt=JADE, s=1.0) -> K.Part:
    """The wrought-gold belted kingfisher finial (§H.7: 'ragged crest,
    dagger bill, sculpted, perched'): a gold sculpture in profile on the
    staff's knop, facing ``facing`` (−1: toward the king). Built facing left
    about the feet. The belted kingfisher's own marks, as a goldsmith would
    inlay them: the big head under a ragged double crest, the cap line, the
    white neck ring (paper, like the faces), the breast band (``belt``:
    jade enamel — the male's blue-grey belt), the folded wing with scalloped
    coverts and stepped primaries, the short square tail. A finial, never a
    live bird: rigid on its knop, feet sunk in it."""
    fx, fy = feet

    def Q(x, y):
        return P(fx + x * s, fy + y * s)

    def sp(pts):
        return Polygon(_pts(K.spline(pts, closed=True), 0.4)).buffer(0)

    hc = Q(-4, -60)
    hr = 18.5 * s
    head = Point(*hc).buffer(hr, quad_segs=32)
    # ragged double crest raked back off the crown of the head
    crest = Polygon([tuple(Q(-14, -74)), tuple(Q(-7, -91)), tuple(Q(0, -80)), tuple(Q(8, -93)),
                     tuple(Q(11, -80)), tuple(Q(22, -87)), tuple(Q(19, -72)), tuple(Q(30, -71)),
                     tuple(Q(14, -56)), tuple(Q(-4, -60))])
    bill = Polygon([tuple(Q(-18, -69)), tuple(Q(-63, -56.5)), tuple(Q(-18, -49))])
    body = sp([Q(-18, -44), Q(-23, -26), Q(-17, -8), Q(-4, 1), Q(10, -1), Q(19, -12), Q(21, -32),
               Q(13, -46), Q(-2, -50)])
    tail = Polygon([tuple(Q(8, -8)), tuple(Q(19, 15)), tuple(Q(30, 10)), tuple(Q(21, -16))])
    knop_c = Q(0, 11)
    knop = Point(*knop_c).buffer(11.0 * s, quad_segs=24)
    sil = K.U(head, crest, bill, body, tail).buffer(1.5, quad_segs=8).buffer(-1.5, quad_segs=8)
    # toes gripping the knop: two small gold scallops sunk into it
    toes = sil.union(Polygon([tuple(Q(-9, -4)), tuple(Q(-10, 4)), tuple(Q(-2, 6)), tuple(Q(6, 4)), tuple(Q(5, -4))]))
    sil = toes
    # the white neck ring (a paper band between head and body)
    n0, n1 = -46.0, -39.0
    ring_poly = Polygon([tuple(Q(-40, n0 - 2)), tuple(Q(40, n0 + 6)), tuple(Q(40, n1 + 6)), tuple(Q(-40, n1 - 2))])
    ring = sil.intersection(ring_poly).difference(bill.buffer(4.0))
    ring = max(K._polys_of(ring), key=lambda g: g.area)
    gold = sil.difference(ring)
    shape = K.U(sil, knop)
    lines = K.outline(sil) + K.clip_out(K.outline(knop), sil, eps=-0.5, trap=0.0)
    lines += K.outline(ring)
    # the folded wing
    wing = sp([Q(4, -38), Q(-7, -22), Q(-2, -8), Q(13, 4), Q(21, -10), Q(20, -28), Q(12, -40)])
    wing = wing.intersection(sil.buffer(-0.5))
    lines += K.outline(wing)
    # the breast band (jade enamel), throat side of the wing
    band = sil.intersection(Polygon([tuple(Q(-40, -33)), tuple(Q(20, -26)), tuple(Q(20, -17)),
                                     tuple(Q(-40, -24))])).difference(wing.buffer(0.3))
    band = max(K._polys_of(band), key=lambda g: g.area)
    lines += K.outline(band)
    win = wing.buffer(-(MEDIUM / 2 + GAP_MARK + FINE / 2 + 0.2))
    for yy in (-27.0, -18.0):
        a, b = Q(-4, yy + 2), Q(18, yy - 3)
        d, _ = K._scallops(a, b, 3, -3.0 * s)
        lines += K.clip_in(K.line(f"M{a[0]:.3f} {a[1]:.3f}" + d, FINE, role="covert"), win)
    for (x0, y0), (x1, y1) in (((1, -9), (11, 1)), ((8, -11), (16, -3))):
        lines += K.clip_in(K.seg(Q(x0, y0), Q(x1, y1), FINE, role="primary"), win)
    # the cap line: from the bill base over the eye to the nape (the crest's dark cap)
    lines += K.clip_in(K.line(K.arc3(Q(-16, -66), Q(0, -68.5), Q(15, -60)), MEDIUM, role="cap"),
                       sil.buffer(-(CONTOUR / 2)))
    lines += K.seg(Q(-58, -57.2), Q(-16, -59.2), MEDIUM, role="gape")
    lines += K.dot(Q(-7, -60.5), 6.3, role="eye")
    # tail bar
    pa = Q(8, -8) + (Q(19, 15) - Q(8, -8)) * 0.55
    pb = Q(21, -16) + (Q(30, 10) - Q(21, -16)) * 0.55
    lines += K.clip_in(K.seg(pa, pb, FINE, role="bar"), sil.buffer(-(CONTOUR / 2 + GAP_MARK + FINE / 2)))
    # no gold where the CONTOUR covers the whole width (the bill tip, crest points)
    gold = gold.buffer(-3.0, quad_segs=8).buffer(3.0, quad_segs=8).intersection(gold)
    kn = knop.difference(sil.buffer(-0.3))
    fills = K.fill(gold, GOLD) + K.fill(band, belt) + K.fill(kn, GOLD)
    part = K.Part(shape, fills, lines, {"head": hc})
    return part.mirrored(fx) if facing > 0 else part


def spray_beard(fc, mo, *, side=(-42.0, 20.0), bulge=(-47.0, 76.0), tip=(-17.0, 130.0), notch_dy=104.0,
                rachis=((-33.0, 66.0), (-30.0, 96.0), (-19.0, 120.0)), pitch=7.0, angle=48.0, max_len=None,
                ends="butt", inner=True, terminal=True, axis_gap=3.2, w_rachis=FINE, start=3.0) -> K.Part:
    """The two-pointed beard (§H.7 'a two-pointed beard of flat comb sprays
    in gold'): the kit's forked beard SHAPE (it tucks under the moustache and
    clears the mouth like the K♠'s), and in each lobe one flat §G.18 comb
    spray — a rachis down the lobe from under the moustache tip to the point,
    with comb ticks both sides swept toward the point. ``ends`` 'butt': the
    ticks run to the lobe's outline like hatch (a herringbone beard, no free
    ends); 'free': comb teeth stopping 4.2 px inside it. The rachis ends in
    a Ø6.3 terminal above the point (the spray's round cone)."""
    b = K.beard(fc, K.BeardSpec(side=side, bulge=bulge, tip=tip, notch_dy=notch_dy, lines=3), mo=mo)
    ax = float(fc.anchors["axis"])
    cx, cy = fc.anchors["center"]
    half = b.shape.intersection(K.box(0, 0, ax, 2000))
    half = max(K._polys_of(half), key=lambda g: g.area)
    r0, r1, r2 = [P(ax + a, cy + c) for a, c in rachis]
    rp = _pts(K.arc3(r0, r1, r2), 0.4)
    # extend the rachis up under the moustache (it springs from behind it)
    t0 = rp[1] - rp[0]
    t0 = t0 / np.hypot(*t0)
    rp = np.vstack([rp[0] - t0 * 14.0, rp])
    zone = half.difference(K.box(ax - axis_gap, 0, 2000, 2000))
    if mo is not None:
        zone = zone.difference(mo.shape.buffer(MEDIUM / 2 + GAP_MARK))
    rl = K.clip_in(K.line(rp, w_rachis, role="rachis"), zone.buffer(-(MEDIUM / 2 + GAP_MARK + w_rachis / 2)))
    lines = C.Frag() + rl
    tip_pt = rp[-1]
    if terminal:
        lines += K.dot(tip_pt, K.TD, role="terminal")
    cv = K.G.Curve(rp)
    L = cv.length
    sa = math.sin(math.radians(angle))
    step = max(pitch, (FINE + GAP + 0.3) / sa) if ends != "butt" else pitch / sa
    if ends == "butt":
        clear_zone = zone.buffer(-0.01)          # butt on the outline centreline (the contour covers the join)
    else:
        clear_zone = zone.buffer(-(MEDIUM / 2 + GAP + FINE / 2 + 0.2))
    rach_geom = LineString(rp).buffer(w_rachis / 2 + 0.01)
    ss = np.arange(14.0 + start, L - (K.TD / 2 + GAP_MARK + 2.0 if terminal else 4.0), step)
    for s in ss:
        p = cv.at_s(s)
        t = cv.tangent_s(s)
        a = math.atan2(t[1], t[0])
        for sd in ((1, -1) if inner else (1,)):
            ang = a - sd * math.radians(angle)
            u = np.array([math.cos(ang), math.sin(ang)])
            Lmax = max_len if max_len else 120.0
            ln = LineString([tuple(p), tuple(p + u * Lmax)]).intersection(clear_zone)
            segs = [g for g in K._lines_of(ln) if g.distance(Point(*p)) < 1.0]
            if not segs:
                continue
            g = segs[0]
            if g.length < 4.0:
                continue
            q = np.asarray(g.coords)
            style = "hatch" if ends == "butt" else "ornament"
            lines += K.line(q, FINE, style=style, role="tick")
    lines = lines + lines.mirror_x(ax)
    return K.Part(b.shape, K.fill(b.shape, GOLD), lines + K.outline(b.shape), dict(b.meta))
