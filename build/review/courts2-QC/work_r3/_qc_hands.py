"""art/_qc_hands.py — Q♣ · court-local refinements of the kit hands (deck.courtkit
is shared and owned elsewhere; these patch only the Q♣ calls).

    tuck(hand, sc)         the kit's own wrist tuck (``Hand.tucked``), frozen:
                           → a Hand whose Part is final (stub 0), so a patch
                           to its lines survives ``add_to``
    palm_tips(part, ...)   the kit's palm-view fist draws three fingertip lobes
                           at the heel end of the finger lines; the lowest
                           (little finger) ends 3.2 px above the block's
                           underside, its round cap ~0.2 px from the heel's
                           contour — a hook touching the line (§I.12). The
                           little finger's tip is the one a closed fist hides
                           under the heel: the lobe is left out and finger
                           line 3 ends freely, like the back-view lines.
    notch_stubs(...)       a textile line that crosses the notch where a wrist
                           meets its wider cuff shows as a free 5–9 px stub
                           there: pieces of the pattern, once cut by the hand
                           and the cuff, that lie wholly near that corner and
                           are short are dropped (a whole leaf elsewhere stays)
    strip_to_paper(...)    ground left between a sleeve and a haloed shaft
                           narrower than a band turns to paper (the kit does
                           this for the heel pocket above the cuff; below it
                           a 3–6 px jade strip with a spur was left).
"""
from __future__ import annotations

import math

import numpy as np
import shapely

from deck import courtkit as K
from deck.motifs import core as C


def tuck(hand: K.Hand, sc: K.Scene, cuff=None) -> K.Hand:
    """The hand as ``add_to`` would stack it (wrist cut on the cuff), frozen."""
    hp = hand.tucked(sc, cuff)
    return K.Hand(hp, hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, 0.0)


def _pts(d):
    return np.asarray(C.sample_d(d, 0.5)[0][0], float)


def palm_tips(hand: K.Hand, *, drop_lowest=True) -> K.Hand:
    """Drop the lowest palm-view fingertip lobe (see the module docstring).
    'Lowest' = the lobe nearest the heel side of the block, i.e. the one
    farthest from the thumb crease. → Hand (frozen)."""
    hp = hand.hand
    inner = hp.meta.get("inner")
    if inner is None or not drop_lowest:
        return hand
    tips = [m for m in inner.marks if m.role == "fingertip"]
    if len(tips) < 2:
        return hand
    thumb = [m for m in inner.marks if m.role in ("thumb",)]
    ref = np.vstack([_pts(m.d) for m in thumb]).mean(axis=0) if thumb else None
    if ref is None:
        return hand
    far = max(tips, key=lambda m: float(np.hypot(*(_pts(m.d).mean(axis=0) - ref))))
    new_inner = C.Frag([m for m in inner.marks if m is not far], inner.meta)
    lines = C.Frag([m for m in hp.lines.marks if m is not far], hp.lines.meta)
    part = K.Part(hp.shape, hp.fills, lines, {**hp.meta, "inner": new_inner})
    return K.Hand(part, hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, 0.0)


def strip_to_paper(sc: K.Scene, name: str, shaft: str, arms, *, below, above=None, close=K.HEEL_CLOSE,
                   band=None):
    """Turn the ground between the arm regions ``arms`` (item names) and the
    haloed item ``shaft`` into paper where it is narrower than 2 × ``close``
    (the kit's heel-pocket rule, continued down the sleeve), between y
    ``above`` (default: none) and ``below``. Adds an empty channel item
    ``name`` in front of the ground (halo_zone = that strip)."""
    it = {i.name: i for i in sc.items}
    sh = it[shaft]
    A = sh.occ.buffer(sh.halo + K.MEDIUM / 2, quad_segs=12)
    arm_r = shapely.union_all([it[a].occ for a in arms if a in it])
    both = shapely.union_all([A, arm_r])
    gap = both.buffer(close, quad_segs=12).buffer(-close, quad_segs=12).difference(both)
    y0 = -K.BIG if above is None else above
    gap = gap.intersection(shapely.box(-K.BIG, y0, K.BIG, below))
    gap = shapely.union_all([g for g in K._polys_of(gap) if g.area > 2.0 and g.distance(A) < 0.6
                             and g.distance(arm_r) < 0.6]) if not gap.is_empty else gap
    if gap.is_empty:
        return None
    sc.add(name, C.Frag(), gap, sil=False, halo=sh.halo, halo_skip=tuple(sh.halo_skip) + tuple(arms),
           halo_only=sh.halo_only, halo_zone=gap)
    return gap


def notch_stubs(frag: C.Frag, joins, *, roles=("leaf", "hatch", "midrib"), radius=12.0,
                max_len=14.0) -> C.Frag:
    """The COMPOSED frag minus every stroke piece of ``roles`` shorter than
    ``max_len`` that lies wholly within ``radius`` of ``joins`` (the points
    where a wrist meets its cuff): the textile's stubs in that notch."""
    from dataclasses import replace
    from inkkit import geom as G
    if joins is None or joins.is_empty:
        return frag
    near = joins.buffer(radius)
    out = []
    for m in frag.marks:
        if m.kind != "stroke" or not m.d or m.role not in roles:
            out.append(m)
            continue
        d = ""
        for pts, closed in G.as_polys(m.d, 0.05):
            pts = np.asarray(pts, float)
            if len(pts) > 1 and not closed:
                ln = shapely.LineString(pts)
                if ln.length < max_len and near.contains(ln):
                    continue
            d += C.polyline_d(pts, closed=closed)
        if d:
            out.append(replace(m, d=d))
    return C.Frag(out, frag.meta)


# ---------------------------------------------------------------------------------------------
# palm_fist: the kit's fist (deck.courtkit.fist, copied — the kit is shared and not edited from a
# court) with the THUMB as a thumb. In the kit the thumb's root centre sits 0.01 × hb above the
# block and its tip 0.1 × hb below it: an 11° near-horizontal capsule, 12 → 9.6 px thick, as long
# as the finger rolls and parallel to them, whose top edge runs on straight from the back of the
# hand. Seen at 750 and at 188 it read as an index finger pointing across the culm (verifier,
# courts2 round 2). Here the thumb
#   * rises from a fuller root (the ball of the thumb) standing ``rise`` px higher on the back of
#     the hand, so the silhouette steps UP from the palm into the thumb's knuckle;
#   * comes DOWN onto the index finger in one bowed sweep (≈ 30° here), its round tip resting on
#     that finger at the shaft's near half (``tip`` × the block length from the knuckles);
#   * tapers visibly (root ``rr`` × hb → tip ``rt`` × the band pitch);
#   * keeps its crease only where it lies on the fingers (the kit's crease ran on into the palm).
# Everything else — block, lobes, finger lines, wrist sweep, heel, tip/heel zones, rebuild on
# re-aim — is the kit's, line for line.
# ---------------------------------------------------------------------------------------------
THUMB = dict(tip=0.50, rise=6.0, rr=0.23, rt=0.56, bow=2.4, crease_x=0.16, root_x=0.06)


def palm_fist(at, axis_deg=-90.0, *, shaft_w=22.0, back=+1, wrist=None, wrist_w=24.0, h=34.0,
              reach=7.0, knuckle=11.0, hand=None, view=None, arm=None, stub=K.HAND_STUB,
              thumb=None) -> K.Hand:
    """``courtkit.fist`` with the thumb described above (``thumb``: overrides of ``THUMB``)."""
    from shapely.geometry import Point, Polygon
    P, R, BIG = K.P, K.R, K.BIG
    tk = {**THUMB, **(thumb or {})}
    a = shaft_w / 2.0
    hb = max(K.FIST_H_K * float(h), K.FIST_H_MIN)
    p = hb / 4.0
    t_up = 0.20 * hb
    ytop = -(hb + t_up) / 2.0
    y0 = ytop + t_up
    y1 = y0 + hb
    yc = (y0 + y1) / 2
    tip_out = min(max(float(reach), 3.0), K.FIST_TIP_OUT)
    x_tip = -a - tip_out
    Lf = max(K.FIST_LEN_K * hb, 2 * a + tip_out + max(float(knuckle), 12.0))
    x_kn = x_tip + Lf
    rot = axis_deg + 90.0
    mir = back < 0
    M, Mf = K._rigid(at, rot, mirror_x=mir)
    dorsal = "L" if back > 0 else "R"
    if view is None:
        view = "back" if (hand is None or str(hand).upper()[:1] == dorsal) else "palm"

    # ---- finger block (kit) ------------------------------------------------------------
    sl = (0.36 if view == "back" else 0.28) * p
    x_c = x_tip + sl
    path = K.Path(P(x_kn, y0)).line(P(x_c, y0))
    cusps = [P(x_c, y0)]
    for k in range(4):
        q = P(x_c, y0 + (k + 1) * p)
        path.sag(q, -sl)
        cusps.append(q)
    block = R(path.line(P(x_kn, y1)).close().d)
    block = block.buffer(-2.2, quad_segs=10).buffer(2.2, quad_segs=10)

    # ---- thumb: rises from the ball of the thumb, comes down onto the index finger -------
    rr = tk["rr"] * hb
    rt = tk["rt"] * p
    x_tt = x_kn - tk["tip"] * Lf
    Tc = P(x_tt, y0 + p - rt)                      # its underside continues finger line 1
    Rc = P(x_kn - tk["root_x"] * Lf, ytop + rr - tk["rise"])
    nrm = K._unit(P(-(Tc - Rc)[1], (Tc - Rc)[0]))
    if nrm[1] > 0:
        nrm = -nrm                                  # bow upward (convex top)
    cen = K._qbez(Tc, (Tc + Rc) / 2 + nrm * tk["bow"], Rc, 18)
    rads = [rt + (rr - rt) * (t ** 1.3) for t in np.linspace(0.0, 1.0, len(cen))]
    discs = [Point(*q).buffer(rw, quad_segs=16) for q, rw in zip(cen, rads)]
    thumb_r = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(discs[:-1], discs[1:])])

    # ---- the wrist (kit) ---------------------------------------------------------------
    W = P(x_kn, yc) + hb * P(0.55, 0.62) if wrist is None else K._to_local(wrist, at, rot, mir)
    Bs = P(x_kn - 0.20 * hb, yc + 0.03 * hb)
    chord = W - Bs
    off = math.degrees(math.atan2(chord[1], chord[0]))
    x_min = a + K.PARALLEL_MIN
    hK = 0.47 * hb

    def build(u):
        u = K._unit(u)
        n_th = np.array([u[1], -u[0]])
        hw = min(float(wrist_w), 0.70 * hb) / 2.0
        hw_in = hw
        Wb = W - n_th * hw
        x_floor = x_min + 0.16 * hb
        if Wb[0] < x_floor and Wb[1] > y1 and n_th[0] > 1e-3:
            hw_in = min(hw, max((W[0] - x_floor) / n_th[0], 0.55 * hw))
            Wb = W - n_th * hw_in
            if Wb[0] < x_min + 0.5:
                hw_in = max((W[0] - x_min - 0.5) / n_th[0], 0.25 * hw)
                Wb = W - n_th * hw_in
        Lw = float(np.hypot(*(W - Bs)))
        C_ = W - u * 0.45 * Lw
        nseg = max(10, int(Lw / 2.5))
        tt = np.linspace(0.0, 1.0, nseg + 1)
        cen_ = list(K._qbez(Bs, C_, W, nseg + 1)) + [W + u * stub * 0.5, W + u * stub]
        wid = [hK + (hw - hK) * (t * t * (3 - 2 * t)) for t in tt] + [hw, hw]
        shift = [n_th * (hw - hw_in) / 2 * (t * t * (3 - 2 * t)) for t in tt] + [n_th * (hw - hw_in) / 2] * 2
        wid = [w_ - (hw - hw_in) / 2 * (t * t * (3 - 2 * t)) for w_, t in zip(wid, list(tt) + [1.0, 1.0])]
        ds = [Point(*(q + s_)).buffer(max(rw, 0.5), quad_segs=16) for q, s_, rw in zip(cen_, shift, wid)]
        neck = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(ds[:-1], ds[1:])])
        neck = neck.intersection(K.halfplane(W + u * stub, W + u * stub + n_th, side=+1))
        x_h = max(x_min, min(x_kn - 0.42 * hb, Wb[0] - 2.0))
        H = K._edge(P(x_h, y1), (1.0, 0.0), Wb, u, 16)
        clear = Polygon()
        if u[1] > -0.3:
            heel = Polygon([tuple(q) for q in list(H) + [W, Bs, P(x_h, y1 - 2.0)]]).buffer(0)
            neck = neck.union(heel)
            clear = Polygon([(-BIG, y1 + 0.4), (x_h, y1 + 0.4)] + [tuple(q) for q in H[1:]]
                            + [tuple(Wb + u * 400.0), (-BIG, BIG)]).buffer(0)
            trimmed = neck.difference(clear)
            if trimmed.geom_type == "Polygon" or not trimmed.is_empty:
                neck = max(K._polys_of(trimmed), key=lambda g: g.area) if trimmed.geom_type != "Polygon" \
                    else trimmed
        root_join = shapely.union(Point(*Rc).buffer(rr, quad_segs=16),
                                  Point(*Bs).buffer(hK, quad_segs=16)).convex_hull
        root_join = root_join.intersection(shapely.box(x_kn - 0.30 * Lf, -BIG, BIG, BIG))
        hand_ = shapely.union_all([block, neck, thumb_r, root_join])
        floor = shapely.box(-BIG, y1 + 0.4, x_min, BIG) if u[1] > -0.3 else Polygon()
        if not floor.is_empty:
            hand_ = hand_.difference(floor)
            if hand_.geom_type != "Polygon":
                hand_ = max(K._polys_of(hand_), key=lambda g: g.area)
        keep_out = shapely.box(-BIG, -BIG, x_kn - 0.30 * Lf, BIG).union(clear.buffer(0.3)).union(floor)
        hand_ = K._junction_smooth(hand_, keep_out, r=0.20 * hb)
        hand_ = hand_.buffer(-1.2, quad_segs=8).buffer(1.2, quad_segs=8)
        if hand_.geom_type != "Polygon":
            hand_ = max(K._polys_of(hand_), key=lambda g: g.area)
        inner = C.Frag()
        body = block.union(neck)
        # the crease only where the thumb lies on the fingers (not on into the palm)
        for pts in K._crease(thumb_r, body, keep=shapely.box(-BIG, -BIG, x_kn - tk["crease_x"] * Lf, BIG)):
            inner += K.line(C.polyline_d(pts), K.MEDIUM, role="thumb")
        inner += K.seg(cusps[1] + P(0.3, 0.0), P(x_tt + 0.4, y0 + p), K.MEDIUM, role="finger")
        ends = {2: 0.16, 3: 0.24} if view == "back" else {2: 0.30, 3: 0.34}
        for k in (2, 3):
            q0 = cusps[k] + P(0.3, 0.0)
            inner += K.line(K.arc_sag(q0, P(x_kn - ends[k] * Lf, q0[1]), -0.7), K.MEDIUM, role="finger")
        if view == "palm":
            xf = x_kn - max(ends.values()) * Lf - 0.8
            for k in (1, 2, 3):
                ya, yz = y0 + k * p + 0.4, y0 + (k + 1) * p - (0.4 if k < 3 else 3.2)
                inner += K.line(K.arc_sag(P(xf, ya), P(xf, yz), 0.26 * p), K.MEDIUM, role="fingertip")
        return hand_, inner, 2 * hw

    drawn = dorsal if view == "back" else ("R" if dorsal == "L" else "L")
    tipzone = K._xf(shapely.box(-BIG, -BIG, -a + 1.0, BIG), M)
    heelzone = K._xf(shapely.box(a - 1.0, y1 - 1.0, BIG, BIG), M)
    base_meta = {"kind": "fist", "hand": drawn, "view": view, "block_h": hb, "block_len": Lf, "wrist_off_deg": off}
    Ws = K._xf(Point(*W), M)
    Ws = P(Ws.x, Ws.y)

    def place(u_local):
        hl, il, ww = build(u_local)
        hs, is_ = K._xf(hl, M), il.transformed(Mf)
        meta = {**base_meta, "inner": is_, "rebuild": rebuild, "tipzone": tipzone, "heelzone": heelzone}
        return K.Part(hs, C.Frag(), K.outline(hs) + is_, meta), ww, K._unit(K._vec(M, K._unit(u_local)))

    def _loc_vec(v):
        return K._to_local(P(at) + P(v), at, rot, mir)

    def rebuild(u_screen):
        return place(_loc_vec(u_screen))[0]

    u0 = _loc_vec(arm) if arm is not None else chord
    part, ww, us = place(u0)
    return K.Hand(part, K.Part(K._xf(thumb_r, M), C.Frag(), C.Frag(), {"merged": True}), Ws, ww, us, float(stub))


def sleeve_to_shaft(s: K.SleeveSpec, *, reach_x, dip=0.0):
    """``courtkit.sleeve`` whose sleeve runs on, BELOW its cuff, to a shaft standing at x =
    ``reach_x`` (stack it behind the shaft): from the cuff's lower outer corner the sleeve's edge
    runs along the cuff's lower line (``dip`` px lower at the shaft) and then down under the shaft.
    The cuff gathers a sleeve that is fuller below it, and the kit's sleeve — diverging from the
    culm below the cuff at the forearm's 65° — no longer leaves a jade wedge that narrows to a
    sliver between the cuff, the node collar and the culm's halo (nor a paper strip down to the
    band). The fold lines are the kit's. → (sleeve, cuff) Parts."""
    P, R = K.P, K.R
    B, W = P(s.base), P(s.wrist)
    u = (W - B) / np.hypot(*(W - B))
    n = np.array([u[1], -u[0]])
    bl, br = B + n * s.width / 2, B - n * s.width / 2
    wl, wr = W + n * s.wrist_w / 2, W - n * s.wrist_w / 2
    cw_l, cw_r = wl - u * s.cuff, wr - u * s.cuff
    d = K._unit(cw_r - cw_l)                        # along the cuff's lower line, outward
    t = (reach_x - cw_r[0]) / d[0]
    cw_x = cw_r + d * t + P(0.0, dip)
    yb = max(B[1], br[1], bl[1]) + 40.0
    body = K.Path(bl).sag(wl, s.sag).line(wr).line(cw_r).line(cw_x).line((reach_x, yb)).line((bl[0], yb)).close()
    shape = R(body.d)
    cuff_d = K.Path(wl).sag(wr, -2.5).line(cw_r).sag(cw_l, 2.5).close().d
    cuff = R(cuff_d)
    lines = K.outline(body.d)
    for k in range(1, s.folds + 1):
        tk = k / (s.folds + 1)
        f0 = bl + (br - bl) * (0.30 + 0.25 * tk)
        f1 = cw_l + (cw_r - cw_l) * (0.30 + 0.25 * tk)
        fd = K.arc_sag(f0 - u * 20.0, f1 + u * 2.0, s.sag * 0.55)
        lines += K.clip_in(K.line(fd, K.MEDIUM, role="fold"), shape.difference(cuff.buffer(0.5)))
    sl = K.Part(shape, K.fill(shape, s.color), lines, {"W": W, "u": u, "n": n})
    cf = K.Part(cuff, K.fill(cuff, s.cuff_color), K.outline(cuff_d), {})
    return sl, cf


def ink_fillet(frag: C.Frag, zone, *, r=1.6, inside=None, min_area=0.2, role="contour") -> C.Frag:
    """``frag`` plus Aquifer fillets in the concave corners of the ink within ``zone``: the
    ink there closed by ``r`` (only inside ``inside``, e.g. an object's gold). Where a thick
    silhouette ring turns into an object's thinner outline (the knop straddling the cloak line)
    the ink steps from 3.1 to 1.55 px deep — a round bite in the gold. The fillet makes the step
    a smooth chamfer. → Frag."""
    from inkkit import geom as G
    near = zone.buffer(2 * r + 4.0)
    x0, y0, x1, y1 = near.bounds
    gs = []
    for m in frag.marks:
        if m.layer != "ink" or not m.d:
            continue
        g = K.R(G.from_skia(m.skia()))
        a0, b0, a1, b1 = g.bounds
        if a1 < x0 or a0 > x1 or b1 < y0 or b0 > y1:
            continue
        gs.append(g.intersection(near))
    if not gs:
        return frag
    ink = shapely.union_all(gs)
    closed = ink.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)
    fil = closed.difference(ink).intersection(zone)
    if inside is not None:
        fil = fil.intersection(inside)
    pcs = [g for g in K._polys_of(fil) if g.area > min_area]
    if not pcs:
        return frag
    # the fillet alone tapers to nothing (a fill thinner than HAIRLINE, §I.12): the fill takes in
    # the ink round it too (within 2 px), so it is a solid blob lying on the strokes
    blob = closed.intersection(shapely.union_all(pcs).buffer(2.0, quad_segs=12))
    blob = blob.buffer(-0.9, quad_segs=8).buffer(0.9, quad_segs=8)
    return frag + K.fill(blob, K.INK, role=role)
