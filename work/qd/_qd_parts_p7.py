"""art/_qd_parts.py — Q♦ · The Queen of Scales: the builders that are hers
alone (brief §H.11). Every builder returns a deck.courtkit Part (shape,
fills, lines, meta) drawn at final size in card px, compass-built from the
kit's primitives; art/QD.py stacks them.

    portico      the portico diadem: gold pediment with an oculus over four
                 column-teeth standing on a band (jade intercolumns)
    balance      the balance scales held aloft on a gold staff: beam, lozenge
                 pointer-finial, cords, two pans of water with ripple rings
    paintbrush   a sprig of Texas paintbrush: red-dipped paper bracts on a
                 spike, jade lanceolate leaves (regalia, not a picked rarity:
                 Castilleja indivisa is common)
    stomacher    four gold fluted column shafts with capitals
    cape         the Gill Red cape, its front edges carrying a stepping-stone
                 chain knocked out to paper (§G.23)
    gown         the jade gown with an arcade of keystoned arches (§G.21)
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
# the portico diadem (§H.11: "a gold pediment with an oculus over four
# column-teeth")
# =============================================================================
def portico(axis=386.0, *, band_cx=None, band_top=170.0, band_h=10.0, band_hw=45.0, bow=3.0, col_top=138.0,
            col_w=12.0, col_pitch=25.0, ent_h=8.0, ent_hw=47.0, ped_hw=51.0, apex=104.0, oculus_r=7.5,
            mullions=True, studs=(), acroterion=(0.0, 0.0)) -> K.Part:
    """The courthouse portico worn as a diadem. A gold band round the head
    (``crown_band``); four gold column-teeth rising from it with JADE
    intercolumns (the portico's shade); a gold entablature; a low gold
    pediment whose tympanum carries the OCULUS — a round window knocked out to
    paper with four FINE mullions. Frontal, centred on the face axis."""
    bcx = axis if band_cx is None else band_cx
    band, band_d = K.crown_band(bcx, band_top, band_h, band_hw, bow)
    ent_bot = col_top
    ent_top = col_top - ent_h
    ent = K.box(axis - ent_hw, ent_top, axis + ent_hw, ent_bot)
    # pediment: a low triangle on the entablature (a classical 1:4 pitch)
    ped = _poly([(axis - ped_hw, ent_top + 0.5), (axis + ped_hw, ent_top + 0.5), (axis, apex)])
    xs = [axis + (k - 1.5) * col_pitch for k in range(4)]
    cols = [K.box(x - col_w / 2, ent_bot - 1.0, x + col_w / 2, band_top + 4.0) for x in xs]
    inter = K.box(xs[0], ent_bot - 1.0, xs[-1], band_top + 4.0).difference(U(*cols))
    stone = U(ent, ped, *cols)
    acro = None
    if acroterion[0]:
        aw, ah = acroterion                 # a small gold lozenge (the house mark) on the apex
        acro = R(C.lozenge_d(axis, apex - ah / 2 + 3.0, ah, aw, 90.0))
        stone = U(stone, acro)
    shape = U(stone, inter, band)
    # oculus: a round window, the paper showing through the gold
    tri_h = ent_top - apex
    oc = P(axis, ent_top - tri_h * 0.40)
    ocu = R(K.circle(oc, oculus_r))
    fills = K.fill(stone.difference(band).difference(ocu).union(band), GOLD) + K.fill(inter, JADE)
    lines = C.Frag()
    # raking cornice: a FINE line inside the pediment's sloping edges
    inset = CONTOUR / 2 + GAP + FINE / 2 + 0.1
    ped_in = ped.buffer(-inset, join_style=2)
    if not ped_in.is_empty:
        pl = ped_in.exterior
        # keep only the two raking sides (drop the bottom edge: it runs along the entablature)
        coords = np.asarray(pl.coords)
        ymax = coords[:, 1].max()
        top_pts = [c for c in coords if c[1] < ymax - 0.5]
        if len(top_pts) >= 1:
            lft = P(coords[:, 0].min(), ymax)
            rgt = P(coords[:, 0].max(), ymax)
            apx = coords[np.argmin(coords[:, 1])]
            lines += K.line(C.polyline_d([lft, apx, rgt]), FINE, style="rule", role="cornice")
    lines += K.outline(K.circle(oc, oculus_r), MEDIUM, role="oculus")
    if mullions:
        for a in (0, 90):
            p0 = K.polar(oc, oculus_r, a)
            p1 = K.polar(oc, oculus_r, a + 180)
            lines += K.seg(p0, p1, FINE, role="mullion")
    # the stone's own contour (interior edges MEDIUM); the band in front
    front = K.outline(U(ent, ped)) + sum((K.outline(c) for c in cols), C.Frag())
    if acro is not None:
        front = K.clip_out(front, acro, eps=-0.5, trap=0.0) + C.stroke(D(acro), MEDIUM, style="point")
    lines += K.clip_out(front, band, eps=-0.8, trap=0.0)
    lines += K.outline(band_d)
    for sx in studs:                      # Aquifer studs on the band where it wraps the head
        t = (sx - bcx) / band_hw
        lines += K.dot((sx, band_top + band_h / 2 - bow * (1 - t * t)), 4.2, role="stud")
    return K.Part(shape, fills, lines, {"band": band, "oculus": oc, "top": apex, "cols": xs})


# =============================================================================
# the balance scales (§H.11: "a gold beam at y ≈ 140 spanning x ≈ 430–600,
# with pans holding ripple rings"; must-have: level scales with water)
# =============================================================================
def balance(fx=521.0, *, beam_y=140.0, half=69.0, beam_h=(12.0, 8.0), boss_r=6.5, fin=(18.0, 26.0),
            staff_hw=7.0, staff_bottom=548.0, collars=(250.0, 330.0), pan_hw=17.0, pan_y=182.0,
            pan_depth=11.0, surf_ry=6.5, hook_dy=12.0):
    """→ dict of Parts: 'staff' (behind the hand), 'beam' (beam, bosses,
    pivot and the lozenge pointer-finial), 'cords' (lines only, sil False),
    'panL', 'panR'. The beam is level: the pointer stands plumb."""
    out = {}
    # ---- staff -----------------------------------------------------------------
    top = beam_y + beam_h[0] / 2 - 1.0
    shaft = K.box(fx - staff_hw, top, fx + staff_hw, staff_bottom)
    knop_c = P(fx, beam_y + beam_h[0] / 2 + 9.0)
    knop = R(K.circle(knop_c, 8.5))
    cl = [R(K.rrect(fx - staff_hw - 3.5, y - 3.5, fx + staff_hw + 3.5, y + 3.5, 2.5)) for y in collars]
    body = U(shaft, knop, *cl)
    lines = K.clip_out(K.outline(shaft), U(knop, *cl), eps=-0.5, trap=0.0)
    for c_ in cl:
        lines += K.outline(c_)
    lines += K.outline(knop)
    out["staff"] = K.Part(body, K.fill(body, GOLD), lines, {})
    # ---- beam + pointer-finial ---------------------------------------------------
    hc, he = beam_h[0] / 2, beam_h[1] / 2
    xl, xr = fx - half, fx + half
    beam = _poly([(xl, beam_y - he), (fx, beam_y - hc), (xr, beam_y - he), (xr, beam_y + he), (fx, beam_y + hc),
                  (xl, beam_y + he)])
    bosses = [R(K.circle((x, beam_y), boss_r)) for x in (xl, xr)]
    fw, fh = fin
    fy = beam_y - hc - 5.0 - fh / 2
    neck = K.box(fx - 3.5, fy + fh / 2 - 2.0, fx + 3.5, beam_y)
    lozenge = R(C.lozenge_d(fx, fy, fh, fw, 90.0))
    pivot = R(K.circle((fx, beam_y), 5.0))
    shape = U(beam, *bosses, neck, lozenge)
    fl = K.fill(shape, GOLD)
    bl = K.outline(beam) + K.outline(lozenge)
    for b in bosses:
        bl = K.clip_out(bl, b, eps=-0.5, trap=0.0) + K.outline(b)
    bl = K.clip_out(bl, neck, eps=-0.5, trap=0.0) + K.clip_out(K.outline(neck), U(beam, lozenge), eps=-0.5, trap=0.0)
    # the lozenge half-hatched (a split lozenge, §G.22's point): its axis a FINE joint
    top_pt, bot_pt = P(fx, fy - fh / 2), P(fx, fy + fh / 2)
    half_l = lozenge.intersection(K.box(0, 0, fx, 1000))
    bl += K.hatch_in(half_l, angle=-45.0, origin=(fx, fy))
    bl += K.seg(top_pt + P(0, 4.0), bot_pt - P(0, 4.0), FINE, style="rule", role="joint")
    bl += K.outline(pivot, MEDIUM, role="pivot")
    out["beam"] = K.Part(shape, fl, bl, {"ends": (P(xl, beam_y), P(xr, beam_y)), "finial_top": fy - fh / 2})
    # ---- pans: a gold bowl under a jade water surface with ripple rings ----------
    cords = C.Frag()
    for key, x in (("panL", xl), ("panR", xr)):
        sc = P(x, pan_y)
        surf = R(C.ellipse_d(x, pan_y, pan_hw, surf_ry))
        bowl_d = (f"M{x - pan_hw:.3f} {pan_y:.3f}A{pan_hw:.3f} {pan_depth + surf_ry * 0:.3f} 0 0 0 "
                  f"{x + pan_hw:.3f} {pan_y:.3f}Z")
        bowl = R(bowl_d).union(K.box(x - pan_hw, pan_y - 0.01, x + pan_hw, pan_y + 0.01))
        # foot: a small ring under the bowl
        foot = R(K.rrect(x - 6.0, pan_y + pan_depth - 2.0, x + 6.0, pan_y + pan_depth + 4.0, 2.0))
        pan = U(surf, bowl, foot)
        fills = K.fill(U(bowl, foot).difference(surf), GOLD) + K.fill(surf, JADE)
        pl = K.outline(surf) + K.clip_out(K.outline(U(bowl, foot)), surf, eps=-0.5, trap=0.0)
        # ripple rings on the water: one FINE ellipse + a centre dot (§G.8, gaps ≥ 3)
        rr = surf_ry - MEDIUM / 2 - GAP - FINE / 2
        if rr > 2.5:
            pl += K.line(C.ellipse_d(x, pan_y, rr * pan_hw / surf_ry * 0.8, rr), FINE, role="ripple")
        out[key] = K.Part(pan, fills, pl, {"c": sc})
        # cords: from the hook under the boss to the pan's rim ends (MEDIUM)
        hook = P(x, beam_y + hook_dy)
        for sg in (-1, 1):
            rim = P(x + sg * (pan_hw - 1.0), pan_y - 1.0)
            cords += K.seg(hook, rim, MEDIUM, role="cord")
        cords += K.dot(hook, 6.3, role="hook")
    out["cords"] = K.Part(Polygon(), C.Frag(), cords, {})
    return out


# =============================================================================
# Texas paintbrush (§H.11: "a sprig of Texas paintbrush with red-dipped bracts
# and jade leaves")
# =============================================================================
def _capsule(p0, p1, w):
    return LineString([tuple(p0), tuple(p1)]).buffer(w / 2, cap_style=1, quad_segs=16)


def paintbrush(base, tip, *, spike=60.0, tiers=((0.00, 38.0, 24.0, 13.0), (0.26, 30.0, 23.0, 12.5),
               (0.50, 20.0, 20.0, 12.0)), top_len=0.36, dip=0.50, dip_sag=-5.0,
               leaves=((0.20, -1, 32.0), (0.44, +1, 28.0), (0.66, -1, 24.0)), leaf_w=8.5, leaf_deg=34.0):
    """A sprig of Texas paintbrush from ``base`` (below the hand) to ``tip``.

    The spike (Castilleja: the colour is in the BRACTS) is a brush of broad
    round-tipped bracts — ``tiers`` of pairs (t along the spike, spread° from
    the axis, length, width), lower tiers in front, and one upright top
    bract — whose scalloped silhouette is dipped in Gill Red above one
    MEDIUM dip line (``dip`` of the way up, bowing ``dip_sag``): the brush
    dipped in paint. Below the spike the stem (MEDIUM Aquifer) carries
    alternate lanceolate jade leaves (MEDIUM outline, FINE midrib).
    → Part (add with sil=False: a light object with a MEDIUM contour)."""
    b, t = P(base), P(tip)
    u = (t - b) / np.hypot(*(t - b))
    nrm = np.array([u[1], -u[0]])                  # screen-left of travel (up the stem)
    L = float(np.hypot(*(t - b)))
    s0 = t - u * spike                             # spike base on the axis
    bracts = []                                    # back to front

    def bract(p0, dvec, blen, bw):
        p1 = p0 + dvec * (blen - bw / 2)
        return _capsule(p0, p1, bw)

    bracts.append(bract(s0 + u * spike * 0.60, u, spike * top_len + 6.0, 12.0))
    for (tt, spread, blen, bw) in reversed(tiers):
        at = s0 + u * spike * tt
        for sg in (-1, 1):
            a = math.radians(sg * spread)
            dvec = u * math.cos(a) + nrm * math.sin(a)
            bracts.append(bract(at, dvec, blen, bw))
    head = U(*bracts)
    # the dip line: an arc across the brush; above it the bracts are red
    dp = s0 + u * spike * dip
    q0, q1 = dp - nrm * 40.0, dp + nrm * 40.0
    dip_d = K.arc_sag(q1, q0, dip_sag)
    dip_poly = R(K.Path(q1).sag(q0, dip_sag).line(q0 + u * 200).line(q1 + u * 200).close().d)
    red = head.intersection(dip_poly)
    lines = C.Frag()
    acc = Polygon()
    for reg in reversed(bracts):                   # front to back: each outline stops under the ones in front
        f = K.outline(reg, MEDIUM, role="bract")
        if not acc.is_empty:
            f = K.clip_out(f, acc)
        lines += f
        acc = acc.union(reg.buffer(0.3))
    dl = C.sample_d(dip_d, 0.4)[0][0]
    for g in K._lines_of(LineString(dl).intersection(head.buffer(-0.3))):
        lines += K.line(np.asarray(g.coords), MEDIUM, role="dip")
    spike_items = [(head, K.fill(red, RED), lines)]
    # stem and leaves (behind the spike)
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


# =============================================================================
# stomacher (§H.11: "four gold fluted column shafts")
# =============================================================================
def stomacher(axis=384.0, *, top=364.0, bottom=548.0, shaft_w=14.0, pitch=22.0, cap_w=20.0, cap_h=8.0):
    """Four gold column shafts side by side, each under a capital block, a
    FINE flute down its middle; the gown's jade shows between them."""
    xs = [axis + (k - 1.5) * pitch for k in range(4)]
    regs, lines = [], C.Frag()
    for x in xs:
        cap = K.box(x - cap_w / 2, top, x + cap_w / 2, top + cap_h)
        sh = K.box(x - shaft_w / 2, top + cap_h - 0.5, x + shaft_w / 2, bottom)
        col = U(cap, sh)
        regs.append(col)
        lines += K.outline(col)
        lines += K.seg(P(x, top + cap_h + GAP_MARK + MEDIUM / 2 + 1.0), P(x, bottom), FINE, style="rule", role="flute")
    shape = U(*regs)
    return K.Part(shape, K.fill(shape, GOLD), lines, {"xs": xs})


# =============================================================================
# cape and gown
# =============================================================================
def cape(left_pts, right_pts, open_l, open_r, *, top_y=286.0, bottom=548.0, band_in=6.3 + MEDIUM / 2,
         band_w=14.0, stone_len=12.0, pitch=22.0):
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
    solid = C.knockout(D(reg), holes)
    fills = K.fill(R(solid).intersection(reg), RED)
    lines = K.outline(reg)
    return K.Part(reg, fills, lines, {"outer": outer, "opening": opening, "OL": OL, "OR": OR})


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
