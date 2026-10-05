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
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import geometric as MG
from inkkit import geom as G

P, R, U, D = K.P, K.R, K.U, K.D
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD
GAP, GAP_MARK = K.GAP, K.GAP_MARK


def _poly(pts):
    return Polygon([tuple(map(float, p)) for p in pts]).buffer(0)


def spline_pts(points, h_start=None, h_end=None, headings=None, step=0.5):
    """Dense points of the kit's G1 arc spline through ``points``."""
    d = K.spline(points, h_start, h_end, headings=headings)
    return C.sample_d(d, step)[0][0]


# =============================================================================
# Texas paintbrush (§H.11: "a sprig of Texas paintbrush with red-dipped bracts
# and jade leaves")
# =============================================================================
def _capsule(p0, p1, w):
    return LineString([tuple(p0), tuple(p1)]).buffer(w / 2, cap_style=1, quad_segs=16)


# =============================================================================
# cape and gown
# =============================================================================
def cape(left_pts, right_pts, open_l, open_r, *, top_y=286.0, bottom=548.0, band_in=6.3 + MEDIUM / 2,
         band_w=14.0, stone_len=12.0, pitch=22.0, field=None, lining=0.0):
    """The Gill Red cape: the silhouette from ``left_pts`` (neck → shoulder →
    side, down to ``bottom``) and ``right_pts``; the front opening between the
    ``open_l`` / ``open_r`` edges (neck → band) is cut away (the gown shows
    there). Along each front edge a stepping-stone chain (§G.23) is knocked
    out to paper: two rails and a row of lozenges whose tips touch them."""
    Lp = spline_pts(left_pts)
    Rp = spline_pts(right_pts)
    outer = _poly(np.vstack([Lp, [[Lp[-1][0], bottom]], [[Rp[-1][0], bottom]], Rp[::-1]]))
    OL = spline_pts(open_l)
    OR = spline_pts(open_r)
    opening = _poly(np.vstack([OL, [[OL[-1][0], bottom + 5]], [[OR[-1][0], bottom + 5]], OR[::-1],
                               [[OR[0][0], top_y - 30]], [[OL[0][0], top_y - 30]]]))
    reg = outer.difference(opening)
    reg = U(*[g for g in K._polys_of(reg) if g.area > 50.0])
    # stepping-stone chains along the two front edges
    holes = C.Frag()
    for edge, sd in ((OL, -1), (OR, +1)):
        cv = G.Curve(edge)
        # offset toward the cape (away from the opening): left edge → −x side
        r_in = band_in
        r_out = band_in + band_w
        rails = []
        for off in (r_in, r_out):
            o = cv.offset(off * (-1 if sd < 0 else 1), spacing=0.5)
            rails.append(np.asarray(o))
        for o in rails:
            holes += C.stroke(o, MEDIUM, style="rule", role="rail")
        mid = np.asarray(cv.offset((band_in + band_w / 2) * (-1 if sd < 0 else 1), spacing=0.5))
        mc = G.Curve(mid)
        Lm = mc.length
        s = pitch * 0.6
        while s < Lm - 4:
            p = mc.at_s(s)
            q = mc.at_s(min(s + 1.0, Lm))
            ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
            holes += C.fill(C.lozenge_d(p[0], p[1], stone_len, band_w, ang), color=INK, role="stone")
            s += pitch
    if field:
        # a diaper of small stepping stones knocked out of the cape body, in a
        # half-drop grid, inside a plain border (the ♦ house's textile)
        px, py = field.get("pitch", (30.0, 26.0))
        sl, sw = field.get("stone", (10.0, 7.0))
        brd = field.get("border", 30.0)
        zone = reg.buffer(-brd)
        for edge, sd in ((OL, -1), (OR, +1)):
            chain = LineString(edge).buffer(band_in + band_w + 10.0)
            zone = zone.difference(chain)
        ox, oy = field.get("origin", (375.0, 300.0))
        for j in range(-2, 14):
            off = px / 2 if j % 2 else 0.0
            for i in range(-12, 13):
                x, y = ox + off + i * px, oy + j * py
                lz = R(C.lozenge_d(x, y, sw, sl, 90.0))
                if zone.contains(lz):
                    holes += C.fill(C.lozenge_d(x, y, sw, sl, 90.0), color=INK, role="stone")
    lines = K.outline(reg)
    lin = Polygon()
    if lining:
        # the jade lining turned back along each front edge (a narrow revers),
        # a MEDIUM fold line where it meets the red
        bands = []
        for edge in (OL, OR):
            bands.append(LineString(edge).buffer(lining, cap_style=2).intersection(reg))
        lin = U(*bands)
        fold = lin.boundary.intersection(reg.buffer(-0.6))
        for g in K._lines_of(shapely.line_merge(fold) if fold.geom_type != "LineString" else fold):
            if g.length > 4:
                lines += K.line(np.asarray(g.coords), MEDIUM, role="fold")
    solid = C.knockout(D(reg.difference(lin)), holes) if not lin.is_empty else C.knockout(D(reg), holes)
    fills = K.fill(R(solid).intersection(reg), RED)
    if not lin.is_empty:
        fills = fills + K.fill(lin, JADE)
    return K.Part(reg, fills, lines, {"outer": outer, "opening": opening, "OL": OL, "OR": OR, "lining": lin})


def gown(opening, neck_l, neck_r, neck_sag, *, bottom=548.0, rows=(), jamb=10.0, key=(5.0, 24.0), avoid=None):
    """The jade gown: the cape's opening below a neckline arc (``neck_l`` →
    ``neck_r``, sagging ``neck_sag``), patterned with ARCADES (§G.21, the
    courthouse's arched windows): each row (x0, x1, sill_y, span, pier) is a
    run of keystoned round arches on a FINE sill that butts into the gown's
    edges; every arch is an atomic motif (dropped whole where something in
    front covers it)."""
    nl, nr = P(neck_l), P(neck_r)
    top = R(K.Path(nl).sag(nr, neck_sag).line((nr[0] + 200, nr[1] - 200)).line((nl[0] - 200, nl[1] - 200)).close().d)
    reg = opening.difference(top).intersection(K.box(0, 0, 750, bottom))
    reg = max(K._polys_of(reg), key=lambda g: g.area) if reg.geom_type != "Polygon" else reg
    lines = K.outline(reg)
    inner = reg.buffer(-(MEDIUM / 2 + GAP + FINE / 2))
    if avoid is not None:
        inner = inner.difference(avoid)
    pat = C.Frag()
    for j, (x0, x1, y, span, pier) in enumerate(rows):
        a = MG.arcade(x0, x1, y, span=span, pier=pier, jamb=jamb, base=False, ring=None, key=key, w=FINE)
        # split into single arches (3 marks each: two arch halves + keystone)
        ms = list(a.marks)
        for k in range(0, len(ms), 3):
            one = C.Frag(ms[k:k + 3])
            if inner.contains(R(one.outline())):
                pat += K.atomic(one, f"arch{j}_{k}")
        sill = LineString([(x0 - 60, y), (x1 + 60, y)]).intersection(reg.buffer(-0.5))
        if avoid is not None:
            sill = sill.difference(avoid.buffer(GAP + FINE))
        for g in K._lines_of(sill):
            if g.length > 12:
                pat += K.line(np.asarray(g.coords), FINE, style="rule", role="sill")
    return K.Part(reg, K.fill(reg, JADE), lines + pat, {"inner": inner, "neck": (nl, nr, neck_sag)})


def paintbrush2(base, tip, *, spike=66.0, style="bracts", dip=0.44,
                leaves=((0.18, -1, 32.0), (0.42, +1, 28.0), (0.64, -1, 24.0)), leaf_w=8.5, leaf_deg=34.0,
                tiers=((0.00, 54.0, 25.0, 13.0, 0.42), (0.22, 36.0, 26.0, 13.5, 0.48), (0.44, 18.0, 25.0, 13.0, 0.60)),
                centres=((0.06, 24.0, 13.0, 0.40), (0.30, 24.0, 13.0, 0.50))):
    """Texas paintbrush, v2: ``tiers`` of bract pairs (t along the spike,
    spread°, length, width, red fraction) fanning out like bristles, with
    upright centre bracts (``centres``) in front, lower tiers in front of
    upper ones; each bract a round-tipped tongue, paper at its base and
    Gill Red at its tip (its own MEDIUM dip line) — the brush dipped in
    paint. The top bract is all red."""
    b, t = P(base), P(tip)
    u = (t - b) / np.hypot(*(t - b))
    nrm = np.array([u[1], -u[0]])
    L = float(np.hypot(*(t - b)))
    s0 = t - u * spike
    bracts = []            # (region, red region, dip line pts) back to front

    def tongue(p0, dvec, blen, bw, red_frac):
        p1 = p0 + dvec * (blen - bw / 2)
        reg = _capsule(p0, p1, bw)
        cut = p0 + dvec * (blen * (1 - red_frac))
        side = np.array([dvec[1], -dvec[0]])
        zone = K.halfplane(cut, cut + side, side=+1)
        red = reg.intersection(zone)
        if not red.contains(Point(*(p1 + dvec * 1.0))):
            red = reg.difference(zone)
        dl = LineString([tuple(cut - side * 30), tuple(cut + side * 30)]).intersection(reg.buffer(-0.3))
        return reg, red, dl

    # top bract (all red), then tiers top → bottom, centre bracts in front of their tier
    top_start = s0 + u * spike * 0.56
    top = _capsule(top_start, t - u * 7.0, 14.0)
    bracts.append((top, top, None))
    tiers_sorted = sorted(tiers, key=lambda x: -x[0])
    cents = {c[0]: c for c in centres}
    for (tt, spread, blen, bw, rf) in tiers_sorted:
        at = s0 + u * spike * tt
        for sg in (-1, 1):
            a = math.radians(sg * spread)
            dvec = u * math.cos(a) + nrm * math.sin(a)
            bracts.append(tongue(at, dvec, blen, bw, rf))
        for (ct, cl, cw, crf) in centres:
            if abs(ct - tt) < 0.12:
                bracts.append(tongue(s0 + u * spike * ct, u, cl, cw, crf))
    fills, lines = C.Frag(), C.Frag()
    acc = Polygon()
    for reg, red, dl in reversed(bracts):          # front to back
        f = K.fill(red, RED) + K.outline(reg, MEDIUM, role="bract")
        if dl is not None:
            for g in K._lines_of(dl):
                f += K.line(np.asarray(g.coords), MEDIUM, role="dip")
        if not acc.is_empty:
            f = K.clip_out(f, acc)
        fills += f.select(lambda m: m.kind == "fill")
        lines += f.select(lambda m: m.kind != "fill")
        acc = acc.union(reg.buffer(0.3))
    head = U(*[x[0] for x in bracts])
    spike_items = [(head, fills, lines)]
    stem_end = s0 + u * 8.0
    stem = LineString([tuple(b), tuple(stem_end)]).buffer(MEDIUM / 2)
    stem_items = [(stem, C.Frag(), K.line(C.polyline_d([b, stem_end]), MEDIUM, role="stem"))]
    for (tt, sg, ll) in leaves:
        at = b + u * (L - spike) * tt
        a = math.radians(sg * leaf_deg)
        dvec = u * math.cos(a) + nrm * math.sin(a)
        p0, p1 = at, at + dvec * ll
        vd = C.vesica_d(tuple(p0), tuple(p1), leaf_w)
        reg = R(vd)
        ln = C.stroke(vd, MEDIUM, style="point", role="leaf")
        ln += K.seg(p0 + dvec * 6.0, p1 - dvec * 8.0, FINE, role="midrib")
        stem_items.append((reg, K.fill(reg, JADE), ln))
    items = stem_items + spike_items
    out_items, acc = [], Polygon()
    for reg, fl, ln in reversed(items):
        f = fl + ln
        if not acc.is_empty:
            f = K.clip_out(f, acc)
        out_items.append(f)
        acc = acc.union(reg.buffer(0.3))
    fr = C.Frag()
    for f in reversed(out_items):
        fr += f
    shape = U(*[it[0] for it in items])
    return K.Part(shape, fr.select(lambda m: m.kind == "fill"), fr.select(lambda m: m.kind != "fill"),
                  {"spike_base": s0, "u": u})


def _rig(origin, u):
    """Local (x lateral, y along −u … i.e. local −y points along u) → screen."""
    u = np.asarray(u, float)
    v = np.array([-u[1], u[0]])            # local +x
    o = np.asarray(origin, float)

    def f(pts):
        pts = np.atleast_2d(np.asarray(pts, float))
        return o + pts[:, :1] * v + (-pts[:, 1:2]) * u
    return f


def paintbrush3(base, tip, *, spike=66.0, rows=((13.0, 3), (15.5, 3), (15.5, 3), (13.0, 2), (9.5, 2)),
                row_h=10.5, row0=9.0, sag=4.6, dip_row=2, stem_w=7.0, top_r=7.5,
                leaves=((0.16, -1, 34.0, 10.0), (0.40, +1, 32.0, 10.0), (0.63, -1, 28.0, 9.0)), leaf_deg=30.0):
    """Texas paintbrush (Castilleja: the colour is in the BRACTS), v3.

    The spike is a stack of bract rows seen from the side, lower rows in
    front: each row's upper edge is a run of convex scallops (the rounded
    bract tips) across the spike, ``rows`` = (half-width, tips) from the
    base up, ``row_h`` apart, capped by a rounded top bract. The whole spike
    above row ``dip_row``'s scallop edge is Gill Red — the brush dipped in
    paint — and the bases below it are paper. Stem: a jade band ``stem_w``
    wide; leaves: alternate sessile jade vesicas, FINE midribs. → Part."""
    b, t = P(base), P(tip)
    u = (t - b) / np.hypot(*(t - b))
    L = float(np.hypot(*(t - b)))
    s0 = t - u * spike
    to = _rig(s0, u)

    def scallop_pts(hw, y, m):
        xs = np.linspace(-hw, hw, m + 1)
        out = []
        for x0, x1 in zip(xs[:-1], xs[1:]):
            d = K.arc_sag(P(x0, y), P(x1, y), -sag)      # bulge toward the tip (−y)
            pts = C.sample_d(d, 0.3)[0][0]
            out.append(pts if not out else pts[1:])
        return np.vstack(out)
    # rows: local y grows DOWN on screen when u points up, so the spike rises toward −y
    edges = []
    polys = []
    for k, (hw, m) in enumerate(rows):
        y = -(row0 + k * row_h)
        e = scallop_pts(hw, y, m)
        edges.append(e)
        yb = y + row_h + 4.0 if k else 2.0
        hb = rows[k - 1][0] * 0.92 if k else hw * 0.35
        poly = Polygon(np.vstack([[[-hb, yb]], e, [[hb, yb]]])).buffer(0)
        polys.append(poly)
    ytop = -(row0 + (len(rows) - 1) * row_h) - sag
    cap_c = P(0.0, ytop - top_r * 0.55)
    top = Point(*cap_c).buffer(top_r, quad_segs=24).union(
        Polygon([(-rows[-1][0] * 0.8, ytop + 4), (-top_r, cap_c[1]), (top_r, cap_c[1]), (rows[-1][0] * 0.8, ytop + 4)]))
    sil_l = U(top, *polys).buffer(0.6, quad_segs=6).buffer(-0.6, quad_segs=6)
    # the red: above the dip row's scallop edge
    de = edges[dip_row]
    above = Polygon(np.vstack([de, [[de[-1][0] + 40, de[-1][1]], [de[-1][0] + 40, -400], [de[0][0] - 40, -400],
                                    [de[0][0] - 40, de[0][1]]]])).buffer(0)
    red_l = sil_l.intersection(above)
    # to screen
    def xf(g):
        import shapely
        return shapely.transform(g, lambda a: to(a))
    sil = xf(sil_l)
    red = xf(red_l)
    lines = K.outline(sil, MEDIUM, role="spike")
    for k, e in enumerate(edges):
        # each row's tip edge, inside the spike (it butts into the outline)
        ln = LineString(to(e)).intersection(sil.buffer(-0.2))
        for g in K._lines_of(ln):
            if g.length > 4:
                lines += K.line(np.asarray(g.coords), MEDIUM, role="bract")
    spike_fr = K.fill(red, RED) + lines
    # stem + leaves (behind the spike)
    stem_end = s0 + u * 8.0
    stem = LineString([tuple(b), tuple(stem_end)]).buffer(stem_w / 2, cap_style=1)
    items = [(stem, K.fill(stem, JADE) + K.outline(stem, MEDIUM, role="stem"))]
    for (tt, sg, ll, lw) in leaves:
        at = b + u * (L - spike) * tt
        a = math.radians(sg * leaf_deg)
        nrm = np.array([u[1], -u[0]])
        dvec = u * math.cos(a) + nrm * math.sin(a)
        p0, p1 = at, at + dvec * ll
        vd = C.vesica_d(tuple(p0), tuple(p1), lw)
        reg = R(vd)
        ln = C.stroke(vd, MEDIUM, style="point", role="leaf")
        ln += K.seg(p0 + dvec * 7.0, p1 - dvec * 9.0, FINE, role="midrib")
        items.append((reg, K.fill(reg, JADE) + ln))
    items.append((sil, spike_fr))
    out, acc = [], Polygon()
    for reg, f in reversed(items):
        if not acc.is_empty:
            f = K.clip_out(f, acc)
        out.append(f)
        acc = acc.union(reg.buffer(0.3))
    fr = C.Frag()
    for f in reversed(out):
        fr += f
    shape = U(*[it[0] for it in items])
    return K.Part(shape, fr.select(lambda m: m.kind == "fill"), fr.select(lambda m: m.kind != "fill"),
                  {"spike_base": s0, "u": u, "stem": stem})


def paintbrush4(base, tip, *, spike=58.0, fingers=((-26.0, 36.0, 12.5), (-13.0, 46.0, 13.0), (0.0, 52.0, 13.5),
                (13.0, 46.0, 13.0), (26.0, 36.0, 12.5)), dip=0.50, dip_sag=6.0, lower=((-58.0, 22.0, 11.0), (58.0, 22.0, 11.0)),
                order=(0, 4, 1, 3, 2), stem_w=7.0,
                leaves=((0.16, -1, 34.0, 10.0), (0.40, +1, 32.0, 10.0), (0.63, -1, 28.0, 9.0)), leaf_deg=30.0,
                fan_c=10.0, below=None, inner_lines="all"):
    """Texas paintbrush, v4 — 'a brush dipped in paint' (Castilleja: the
    colour is in the BRACTS). The spike is a bundle of broad round-tipped
    bracts (``fingers`` = (angle from the axis, length, width)) fanning a
    little from a point ``fan_c`` px below the spike base, the centre bract
    in front (``order``: back → front); every bract is Gill Red above ONE
    common dip line (an arc across the bundle at ``dip`` of the spike
    length, bowing ``dip_sag`` toward the tip) and paper below it — the
    paint line. Two short lower bracts spread wide under the bundle. Stem:
    a jade band; leaves: alternate sessile jade vesicas, FINE midribs."""
    b, t = P(base), P(tip)
    u = (t - b) / np.hypot(*(t - b))
    nrm = np.array([u[1], -u[0]])
    L = float(np.hypot(*(t - b)))
    s0 = t - u * spike
    root = s0 - u * fan_c

    def dirv(a):
        a = math.radians(a)
        return u * math.cos(a) + nrm * math.sin(a)
    tongues = []
    for i in order:
        a, ln, w = fingers[i]
        d = dirv(a)
        p0 = root + d * (fan_c + 2.0)
        p1 = root + d * (fan_c + ln - w / 2)
        tongues.append(_capsule(p0, p1, w))
    lows = []
    for a, ln, w in lower:
        d = dirv(a)
        lows.append((d, R(C.vesica_d(tuple(s0 - u * 6.0 + d * 1.0), tuple(s0 - u * 6.0 + d * ln), w))))
    # the paint line: an arc across the bundle, ``dip`` of the centre bract's
    # visible length below its tip, bowing ``dip_sag`` toward the tip
    a_c, l_c, w_c = max(fingers, key=lambda f: f[1])
    tip_c = root + dirv(a_c) * (fan_c + l_c)
    dp = tip_c - u * (l_c - 2.0) * dip
    q0, q1 = dp - nrm * 44.0, dp + nrm * 44.0
    dip_d = K.arc_sag(q0, q1, dip_sag)
    dpts = C.sample_d(dip_d, 0.4)[0][0]
    above = Polygon(np.vstack([dpts, [q1 + u * 200], [q0 + u * 200]])).buffer(0)
    if not above.contains(Point(*(t - u * 2))):
        above = Polygon(np.vstack([dpts, [q1 - u * 200], [q0 - u * 200]])).buffer(0)
        above = K.box(-1e4, -1e4, 1e4, 1e4).difference(above)
    items_sp = [(lw_, K.fill(lw_, JADE)) for _, lw_ in lows]
    for tg in tongues:
        fr_ = K.fill(tg.intersection(above), RED)
        if below:
            fr_ += K.fill(tg.difference(above), below)
        items_sp.append((tg, fr_))
    fr_sp, acc = [], Polygon()
    n_low = len(lows)
    for i_, (reg, f) in enumerate(reversed(items_sp)):
        is_low = i_ >= len(items_sp) - n_low
        f = f + (C.stroke(D(reg), MEDIUM, style="point", role="bract") if is_low else K.outline(reg, MEDIUM, role="bract"))
        dl = LineString(dpts).intersection(reg.buffer(-0.3))
        if dl.length > 2 and not f.marks[0].kind == "stroke" if f.marks else False:
            pass
        for g in K._lines_of(LineString(dpts).intersection(reg.buffer(-0.2))):
            if g.length > 2 and reg.intersection(above).area > 1 and not is_low:
                f += K.line(np.asarray(g.coords), MEDIUM, role="dip")
        if not acc.is_empty:
            f = K.clip_out(f, acc)
            if inner_lines == "red" and not is_low:
                # below the paint line only the bundle's own outline shows
                f = C.Frag([m for m in f.marks if m.kind == "fill"]) + K.clip_in(
                    f.select(lambda m: m.kind != "fill"), above.buffer(1.0))
        fr_sp.append(f)
        acc = acc.union(reg.buffer(0.3))
    spike_fr = C.Frag()
    for f in reversed(fr_sp):
        spike_fr += f
    sil = U(*[it[0] for it in items_sp])
    if inner_lines == "red":
        bundle = U(*tongues)
        spike_fr += K.clip_out(K.outline(bundle, MEDIUM, role="bract"), U(*[lw_ for _, lw_ in lows]).difference(bundle), eps=-0.5, trap=0.0) if False else C.Frag()
        spike_fr += K.clip_in(K.outline(bundle, MEDIUM, role="bract"), K.box(-1e4, -1e4, 1e4, 1e4).difference(above.buffer(-0.5)))
    stem_end = s0 + u * 4.0
    stem = LineString([tuple(b), tuple(stem_end)]).buffer(stem_w / 2, cap_style=1)
    items = [(stem, K.fill(stem, JADE) + K.outline(stem, MEDIUM, role="stem"))]
    for (tt, sg, ll, lw) in leaves:
        at = b + u * (L - spike) * tt
        d = dirv(sg * leaf_deg)
        p0, p1 = at, at + d * ll
        vd = C.vesica_d(tuple(p0), tuple(p1), lw)
        reg = R(vd)
        ln = C.stroke(vd, MEDIUM, style="point", role="leaf")
        ln += K.seg(p0 + d * 7.0, p1 - d * 9.0, FINE, role="midrib")
        items.append((reg, K.fill(reg, JADE) + ln))
    items.append((sil, spike_fr))
    out, acc = [], Polygon()
    for reg, f in reversed(items):
        if not acc.is_empty:
            f = K.clip_out(f, acc)
        out.append(f)
        acc = acc.union(reg.buffer(0.3))
    fr = C.Frag()
    for f in reversed(out):
        fr += f
    shape = U(*[it[0] for it in items])
    return K.Part(shape, fr.select(lambda m: m.kind == "fill"), fr.select(lambda m: m.kind != "fill"),
                  {"spike_base": s0, "u": u, "stem": stem})


def paintbrush5(base, tip, *, spike=64.0, bracts=((0.00, -1, 24.0, 12.0, 0.50), (0.10, +1, 24.0, 12.0, 0.50),
                (0.24, -1, 22.0, 11.5, 0.55), (0.34, +1, 21.0, 11.5, 0.55), (0.48, -1, 18.0, 11.0, 0.62),
                (0.57, +1, 17.0, 11.0, 0.62)), spread=38.0, top=(18.0, 11.0), stem_w=7.8,
                leaves=((0.14, -1, 36.0, 9.5), (0.38, +1, 34.0, 9.5), (0.62, -1, 30.0, 9.0)), leaf_deg=26.0):
    """Texas paintbrush, v5, in the deck's own leaf (§G.4/§G.5 vesicas):
    the spike is the stem's top ``spike`` px set with alternate BRACTS —
    broad vesicas (t along the spike, side, length, width, red fraction)
    spreading ``spread``° from the axis, shrinking toward the tip — each
    DIPPED: Gill Red from its tip down ``red fraction`` of its length, paper
    below (a MEDIUM dip line across it); an upright red bract crowns it.
    Lower bracts are in front of upper ones (they overlap as they climb).
    Below the spike, alternate sessile jade leaves with FINE midribs.
    Castilleja indivisa is common: the sprig is regalia, not a rarity."""
    b, t = P(base), P(tip)
    u = (t - b) / np.hypot(*(t - b))
    nrm = np.array([u[1], -u[0]])
    L = float(np.hypot(*(t - b)))
    s0 = t - u * spike

    def dirv(a):
        a = math.radians(a)
        return u * math.cos(a) + nrm * math.sin(a)
    sp_items = []                                   # back to front: top first, then upper → lower bracts
    tl, tw = top
    tp0 = t - u * tl
    tv = C.vesica_d(tuple(tp0), tuple(t), tw)
    treg = R(tv)
    sp_items.append((treg, K.fill(treg, RED) + C.stroke(tv, MEDIUM, style="point", role="bract")))
    for (tt, sg, ln, w, rf) in sorted(bracts, key=lambda x: -x[0]):
        at = s0 + u * spike * tt
        d = dirv(sg * spread)
        p0, p1 = at, at + d * ln
        vd = C.vesica_d(tuple(p0), tuple(p1), w)
        reg = R(vd)
        cut = p1 - d * ln * rf
        side = np.array([d[1], -d[0]])
        zone = K.halfplane(cut, cut + side, side=+1)
        red = reg.intersection(zone)
        if not red.contains(Point(*(p1 - d * 2.0))):
            red = reg.difference(zone)
        f = K.fill(red, RED) + C.stroke(vd, MEDIUM, style="point", role="bract")
        for g in K._lines_of(LineString([tuple(cut - side * 20), tuple(cut + side * 20)]).intersection(reg.buffer(-0.2))):
            if g.length > 2:
                f += K.line(np.asarray(g.coords), MEDIUM, role="dip")
        sp_items.append((reg, f))
    stem = LineString([tuple(b), tuple(t - u * (tl * 0.6))]).buffer(stem_w / 2, cap_style=1)
    items = [(stem, K.fill(stem, JADE) + K.outline(stem, MEDIUM, role="stem"))]
    for (tt, sg, ll, lw) in leaves:
        at = b + u * (L - spike) * tt
        d = dirv(sg * leaf_deg)
        p0, p1 = at, at + d * ll
        vd = C.vesica_d(tuple(p0), tuple(p1), lw)
        reg = R(vd)
        ln = C.stroke(vd, MEDIUM, style="point", role="leaf")
        ln += K.seg(p0 + d * 7.0, p1 - d * 9.0, FINE, role="midrib")
        items.append((reg, K.fill(reg, JADE) + ln))
    items += sp_items
    out, acc = [], Polygon()
    for reg, f in reversed(items):
        if not acc.is_empty:
            f = K.clip_out(f, acc)
        out.append(f)
        acc = acc.union(reg.buffer(0.3))
    fr = C.Frag()
    for f in reversed(out):
        fr += f
    shape = U(*[it[0] for it in items])
    return K.Part(shape, fr.select(lambda m: m.kind == "fill"), fr.select(lambda m: m.kind != "fill"),
                  {"spike_base": s0, "u": u, "stem": stem})


def gown2(opening, neck_l, neck_r, neck_sag, *, bottom=548.0, rows=(), avoid=None, span=20.0, jamb=9.0,
          key=(5.0, 24.0), pier_min=11.0, edge_clear=3.0):
    """The jade gown with ARCADE FRIEZES (§G.21, the courthouse's arched
    ground-floor windows): each row (sill_y, cornice_y) is a band between two
    FINE rules that butt into the gown's edges (and the stomacher), with as
    many keystoned round arches standing on the sill as fit each run of the
    band, centred in it. Every arch is an atomic motif."""
    nl, nr = P(neck_l), P(neck_r)
    top = R(K.Path(nl).sag(nr, neck_sag).line((nr[0] + 200, nr[1] - 200)).line((nl[0] - 200, nl[1] - 200)).close().d)
    reg = opening.difference(top).intersection(K.box(0, 0, 750, bottom))
    reg = max(K._polys_of(reg), key=lambda g: g.area) if reg.geom_type != "Polygon" else reg
    lines = K.outline(reg)
    inner = reg.buffer(-(MEDIUM / 2 + GAP_MARK + FINE / 2 + edge_clear))
    body = reg if avoid is None else reg.difference(avoid)
    if avoid is not None:
        inner = inner.difference(avoid.buffer(GAP_MARK + FINE / 2 + MEDIUM / 2 + edge_clear))
    pat = C.Frag()
    r = span / 2
    kh = key[0]
    for j, (ys, yc) in enumerate(rows):
        top_y = ys - jamb - r - kh
        if top_y - (yc + FINE) < GAP_MARK:
            yc = top_y - FINE - GAP_MARK
        band = K.box(0, yc, 750, ys)
        runs = K._polys_of(inner.intersection(band))
        for rr, run in enumerate(runs):
            # the run's usable x-range: where the whole band height is inside
            xs = np.arange(run.bounds[0], run.bounds[2], 0.5)
            ok = [x for x in xs if inner.contains(LineString([(x, yc + 0.5), (x, ys - 0.5)]))]
            if not ok:
                continue
            xa, xb = min(ok), max(ok)
            n = int((xb - xa + pier_min) // (span + pier_min))
            if n < 1:
                continue
            pitch = span + pier_min
            used = n * pitch - pier_min
            s = xa + (xb - xa - used) / 2 + r
            for k in range(n):
                a = MG.arch(s + k * pitch, ys, span, jamb, key=key, ring=None, w=FINE)
                pat += K.atomic(a, f"arch{j}_{rr}_{k}")
        for y in (ys, yc):
            ln = LineString([(0, y), (750, y)]).intersection(body.buffer(-0.4))
            for g in K._lines_of(ln):
                if g.length > 12:
                    pat += K.line(np.asarray(g.coords), FINE, style="rule", role="frieze")
    return K.Part(reg, K.fill(reg, JADE), lines + pat, {"inner": inner, "neck": (nl, nr, neck_sag)})


def gown3(opening, neck_l, neck_r, neck_sag, *, bottom=548.0, avoid=None, span=14.0, jamb=14.0, key=(3.0, 24.0),
          ring=6.3, pitch=34.0, row_h=38.0, sill0=503.0, top_limit=330.0, ox=375.0, edge_clear=2.0, rows_max=6):
    """The jade gown woven with an ARCADE (§G.21, the courthouse's arched
    ground-floor windows) as a textile: rows of keystoned round arches
    standing on FINE sills ``row_h`` apart, each row offset half a pitch
    (a half-drop: cloth, never a façade). Sills butt into the gown's edges
    and the stomacher; every arch is atomic (whole or absent)."""
    nl, nr = P(neck_l), P(neck_r)
    top = R(K.Path(nl).sag(nr, neck_sag).line((nr[0] + 200, nr[1] - 200)).line((nl[0] - 200, nl[1] - 200)).close().d)
    reg = opening.difference(top).intersection(K.box(0, 0, 750, bottom))
    reg = max(K._polys_of(reg), key=lambda g: g.area) if reg.geom_type != "Polygon" else reg
    lines = K.outline(reg)
    body = reg if avoid is None else reg.difference(avoid)
    inner = reg.buffer(-(MEDIUM / 2 + GAP_MARK + FINE / 2 + edge_clear))
    if avoid is not None:
        inner = inner.difference(avoid.buffer(GAP_MARK + FINE / 2 + MEDIUM / 2 + edge_clear))
    pat = C.Frag()
    r = span / 2
    for j in range(rows_max):
        ys = sill0 - j * row_h
        if ys - jamb - r - (ring or 0.0) - key[0] < top_limit:
            break
        # fit each run of the row: as many arches as the run holds, centred
        top_y = ys - jamb - r - (ring or 0.0) - key[0] - 1.0
        aw = span + 2 * (ring or 0.0) + FINE
        xs = np.arange(0.0, 750.0, 0.5)
        ok = np.array([inner.contains(LineString([(x, top_y), (x, ys - 1.0)])) for x in xs])
        runs, st = [], None
        for x, o in zip(xs, ok):
            if o and st is None:
                st = x
            if not o and st is not None:
                runs.append((st, x - 0.5)); st = None
        if st is not None:
            runs.append((st, xs[-1]))
        for rr, (xa, xb) in enumerate(runs):
            n = int((xb - xa - aw) // pitch) + 1 if xb - xa >= aw else 0
            if n < 1:
                continue
            used = (n - 1) * pitch
            x0 = (xa + xb) / 2 - used / 2
            for k in range(n):
                a = MG.arch(x0 + k * pitch, ys, span, jamb, key=key, ring=ring, w=FINE)
                if inner.contains(R(a.outline())):
                    pat += K.atomic(a, f"arch{j}_{rr}_{k}")
        ln = LineString([(0, ys), (750, ys)]).intersection(body.buffer(-0.4))
        for g in K._lines_of(ln):
            if g.length > 12:
                pat += K.line(np.asarray(g.coords), FINE, style="rule", role="sill")
    return K.Part(reg, K.fill(reg, JADE), lines + pat, {"inner": inner, "neck": (nl, nr, neck_sag)})


def gown4(opening, neck_l, neck_r, neck_sag, *, bottom=548.0, avoid=None, span=14.0, jamb=10.0, key=(4.0, 26.0),
          pier=9.0, row_h=31.0, sill0=505.0, top_limit=330.0, ox=375.0, edge_clear=1.0, rows_max=7,
          half_drop=True, border=0.0):
    """The jade gown woven with an ARCADE (§G.21, the courthouse's arched
    ground-floor windows): rows of single-line round arches with their
    keystones, standing on FINE sills ``row_h`` apart, on one grid
    (``span`` + ``pier`` pitch, alternate rows offset half a pitch when
    ``half_drop``). Sills butt into the gown's edges and the stomacher; each
    arch is atomic (whole or absent)."""
    nl, nr = P(neck_l), P(neck_r)
    top = R(K.Path(nl).sag(nr, neck_sag).line((nr[0] + 200, nr[1] - 200)).line((nl[0] - 200, nl[1] - 200)).close().d)
    reg = opening.difference(top).intersection(K.box(0, 0, 750, bottom))
    reg = max(K._polys_of(reg), key=lambda g: g.area) if reg.geom_type != "Polygon" else reg
    lines = K.outline(reg)
    body = reg if avoid is None else reg.difference(avoid)
    inner = reg.buffer(-(MEDIUM / 2 + GAP_MARK + FINE / 2 + edge_clear + border))
    if avoid is not None:
        inner = inner.difference(avoid.buffer(GAP_MARK + FINE / 2 + MEDIUM / 2 + edge_clear))
    pat = C.Frag()
    r = span / 2
    pitch = span + pier
    for j in range(rows_max):
        ys = sill0 - j * row_h
        top_y = ys - jamb - r - key[0]
        if top_y < top_limit:
            break
        off = (pitch / 2 if (half_drop and j % 2) else 0.0)
        kmin = int(math.floor((0 - ox) / pitch)) - 1
        for k in range(kmin, kmin + int(750 / pitch) + 3):
            x = ox + off + k * pitch
            a = MG.arch(x, ys, span, jamb, key=key, ring=None, w=FINE)
            if inner.contains(R(a.outline())):
                pat += K.atomic(a, f"arch{j}_{k}")
        ln = LineString([(0, ys), (750, ys)]).intersection(body.buffer(-0.4))
        for g in K._lines_of(ln):
            if g.length > 12:
                pat += K.line(np.asarray(g.coords), FINE, style="rule", role="sill")
    return K.Part(reg, K.fill(reg, JADE), lines + pat, {"inner": inner, "neck": (nl, nr, neck_sag)})


def paintbrush6(base, tip, *, spike=84.0, tiers=((0.00, 44.0, 26.0, 14.0, 0.46), (0.22, 38.0, 24.0, 13.5, 0.55),
                (0.42, 32.0, 21.0, 13.0, 0.64), (0.60, 26.0, 18.0, 12.0, 0.75)), top=(20.0, 13.0), stem_w=8.4,
                leaves=((0.22, -1, 34.0, 10.5), (0.52, +1, 32.0, 10.0)), leaf_deg=32.0, bract="tongue",
                midribs=True):
    """Texas paintbrush, v6 (§H.11 'a sprig of Texas paintbrush with red-dipped
    bracts and jade leaves'; Castilleja: the colour is in the BRACTS): the
    spike is a stack of CHEVRON tiers — each tier (t along the spike,
    spread°, length, width, red fraction) a pair of broad round-tipped
    bracts leaning out either side of the axis, lower tiers in front of
    the upper ones like the scales of a cone — crowned by one upright
    bract. Every bract is DIPPED: Gill Red from its tip down its red
    fraction (more red toward the top), paper at its base, a MEDIUM dip
    line between. Stem a jade band; leaves alternate sessile jade vesicas
    with FINE midribs. Castilleja indivisa is common: the sprig is regalia,
    not a picked rarity."""
    b, t = P(base), P(tip)
    u = (t - b) / np.hypot(*(t - b))
    nrm = np.array([u[1], -u[0]])
    L = float(np.hypot(*(t - b)))
    s0 = t - u * spike

    def dirv(a):
        a = math.radians(a)
        return u * math.cos(a) + nrm * math.sin(a)

    def tongue(p0, d, ln, w, rf):
        if bract == "tongue":
            p1 = p0 + d * (ln - w / 2)
            reg = _capsule(p0, p1, w)
            outline = K.outline(reg, MEDIUM, role="bract")
        else:
            vd = C.vesica_d(tuple(p0), tuple(p0 + d * ln), w)
            reg = R(vd)
            outline = C.stroke(vd, MEDIUM, style="point", role="bract")
        cut = p0 + d * ln * (1 - rf)
        side = np.array([d[1], -d[0]])
        zone = K.halfplane(cut, cut + side, side=+1)
        red = reg.intersection(zone)
        if not red.contains(Point(*(p0 + d * (ln - 2.0)))):
            red = reg.difference(zone)
        f = K.fill(red, RED) + outline
        if rf < 0.98:
            for g in K._lines_of(LineString([tuple(cut - side * 30), tuple(cut + side * 30)]).intersection(reg.buffer(-0.2))):
                if g.length > 2:
                    f += K.line(np.asarray(g.coords), MEDIUM, role="dip")
        return reg, f
    items = []                                     # back → front
    tl, tw = top
    items.append(tongue(t - u * tl, u, tl, tw, 1.0))
    for (tt, spread, ln, w, rf) in sorted(tiers, key=lambda x: -x[0]):
        at = s0 + u * spike * tt
        for sg in (-1, +1):
            items.append(tongue(at, dirv(sg * spread), ln, w, rf))
    stem = LineString([tuple(b), tuple(s0 + u * spike * 0.5)]).buffer(stem_w / 2, cap_style=1)
    back = [(stem, K.fill(stem, JADE) + K.outline(stem, MEDIUM, role="stem"))]
    for (tt, sg, ll, lw) in leaves:
        at = b + u * (L - spike) * tt
        d = dirv(sg * leaf_deg)
        p0, p1 = at, at + d * ll
        vd = C.vesica_d(tuple(p0), tuple(p1), lw)
        reg = R(vd)
        ln = C.stroke(vd, MEDIUM, style="point", role="leaf")
        if midribs:
            ln += K.seg(p0 + d * 8.0, p1 - d * 10.0, FINE, role="midrib")
        back.append((reg, K.fill(reg, JADE) + ln))
    items = back + items
    out, acc = [], Polygon()
    for reg, f in reversed(items):
        if not acc.is_empty:
            f = K.clip_out(f, acc)
        out.append(f)
        acc = acc.union(reg.buffer(0.3))
    fr = C.Frag()
    for f in reversed(out):
        fr += f
    shape = U(*[it[0] for it in items])
    return K.Part(shape, fr.select(lambda m: m.kind == "fill"), fr.select(lambda m: m.kind != "fill"),
                  {"spike_base": s0, "u": u, "stem": stem})


def cuff_stones(cuff: K.Part, wrist, u, half_w, depth, *, stone=(8.4, 5.6), pitch=12.0, color=INK) -> K.Part:
    """Set the ♦ stepping-stone chain (§G.23: Aquifer lozenges) along a
    cuff's mid-line: the cuff from the kit's sleeve(), whose top edge is
    the wrist line (``wrist`` ± ``half_w`` across) and which runs ``depth``
    back down the sleeve (``u`` = the sleeve's direction, up the arm)."""
    W, u = P(wrist), P(u)
    n = np.array([u[1], -u[0]])
    mid = W - u * depth / 2
    sl, sw = stone
    ang = math.degrees(math.atan2(n[1], n[0]))
    m = int((2 * half_w - 2 * (MEDIUM + 3.0 + sl / 2)) // pitch)
    f = C.Frag()
    for k in range(m + 1):
        o = (k - m / 2) * pitch
        p = mid + n * o
        f += C.fill(C.lozenge_d(p[0], p[1], sl, sw, ang), color=color, role="stone")
    f = K.clip_in(f, cuff.shape.buffer(-(MEDIUM / 2 + GAP_MARK)))
    return K.Part(cuff.shape, cuff.fills, cuff.lines + f, cuff.meta)


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


def gown5(opening, neck_l, neck_r, neck_sag, *, bottom=548.0, avoid=None, ox=375.0, pitch=28.0, a=3.5, jamb=15.0,
          key=(6.0, 26.0), sills=(500.0, 456.0, 412.0), cornice=None, on_axis="arch", edge_clear=1.0,
          min_run=1, keep_out=None):
    """The jade gown with a stacked ARCADE (§G.21, the courthouse's arched
    windows): three tiers of CONTINUOUS arcades on FINE sills — round arches
    springing from impost bars on shared jambs, a keystone at every crown —
    all on one grid about ``ox`` (the stomacher's axis), so the keystones
    stand in vertical files tier over tier and the stomacher interrupts
    every tier symmetrically (``on_axis``: 'arch' puts a bay on the axis,
    'pier' a jamb). Each tier keeps the bays that fit whole inside the gown
    (clear of its edge and of ``avoid``), in contiguous runs; sills (and the
    optional ``cornice`` rule over the top tier) butt into the gown's edges
    and the stomacher."""
    nl, nr = P(neck_l), P(neck_r)
    top = R(K.Path(nl).sag(nr, neck_sag).line((nr[0] + 200, nr[1] - 200)).line((nl[0] - 200, nl[1] - 200)).close().d)
    reg = opening.difference(top).intersection(K.box(0, 0, 750, bottom))
    reg = max(K._polys_of(reg), key=lambda g: g.area) if reg.geom_type != "Polygon" else reg
    lines = K.outline(reg)
    body = reg if avoid is None else reg.difference(avoid)
    inner = reg.buffer(-(MEDIUM / 2 + GAP_MARK + FINE / 2 + edge_clear))
    if avoid is not None:
        # a whole arcade runs ALONGSIDE the stomacher's edge: §I.12's 4.2, not 3.0
        inner = inner.difference(avoid.buffer(GAP + FINE / 2 + MEDIUM / 2 + edge_clear))
    if keep_out is not None:
        inner = inner.difference(keep_out.buffer(GAP_MARK + FINE / 2))
    # rules run 0.8 px past the gown's edge (under its MEDIUM outline, onto the
    # lining behind it) and on under the stomacher, which clips them in the
    # Scene: they butt into both, never stopping a hair short
    ends = reg.buffer(0.8)
    r = pitch / 2 - a
    pat = C.Frag()
    off = 0.0 if on_axis == "arch" else pitch / 2
    ks = range(-int(400 / pitch), int(400 / pitch) + 1)
    bays_all = []
    for j, sill in enumerate(sills):
        ok = [k for k in ks if inner.contains(_bay_footprint(ox + off + k * pitch, sill, r=r, a=a, jamb=jamb, key=key,
                                                             pitch=pitch))]
        runs, cur = [], []
        for k in ok:
            if cur and k != cur[-1] + 1:
                runs.append(cur); cur = []
            cur.append(k)
        if cur:
            runs.append(cur)
        for run in runs:
            if len(run) < min_run:
                continue
            xb = [ox + off + k * pitch for k in run]
            ys = sill - jamb
            sl = a if inner.contains(LineString([(xb[0] - pitch / 2 - a, ys), (xb[0] - pitch / 2, ys)])) else 0.0
            sr = a if inner.contains(LineString([(xb[-1] + pitch / 2, ys), (xb[-1] + pitch / 2 + a, ys)])) else 0.0
            pat += K.atomic(_arcade_run(xb, sill, r=r, a=a, jamb=jamb, key=key, stub_l=sl, stub_r=sr),
                            f"arcade{j}_{run[0]}")
            bays_all.append((j, run))
        ln = LineString([(0, sill), (750, sill)]).intersection(ends)
        for g in K._lines_of(ln):
            if g.length > 12:
                pat += _own_path(K.line(np.asarray(g.coords), FINE, style="rule", role="sill"))
    if cornice is not None:
        ln = LineString([(0, cornice), (750, cornice)]).intersection(ends)
        for g in K._lines_of(ln):
            if g.length > 12:
                pat += _own_path(K.line(np.asarray(g.coords), FINE, style="rule", role="cornice"))
    return K.Part(reg, K.fill(reg, JADE), lines + pat, {"inner": inner, "neck": (nl, nr, neck_sag), "bays": bays_all})


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
                midribs=True, min_base=6.0, root=6.0):
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
