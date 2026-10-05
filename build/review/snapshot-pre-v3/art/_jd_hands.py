"""art/_jd_hands.py — the J♦ herald's hands, seated on the kit fists.

Local helpers for art/JD.py only (deck/courtkit.py is shared; nothing here
changes it). Both hands are kit fists (§H.0 mitten, 3 finger lines, thumb over
the top):

* ``fist`` — a local copy of ``courtkit.fist`` with two refinements exposed
  (defaults = the kit): the THUMB tip's radius and place (the kit's tip stood
  only 1.6 px above the index finger's edge, its round end and that edge
  knotting into one blob of ink at 8×; J♦ uses a fuller tip that stands
  clear, a distinct notch), and ``floor_eps`` (the kit leaves a 0.4 px ledge
  where the little finger's underside meets the heel's floor — a jog in the
  contour at 16×; J♦ runs the underside straight into the heel). A candidate
  for the kit; not changed there (shared by all twelve courts).

* ``smooth_back`` — the kit fist tucked into its cuff (``Hand.tucked``) with
  the concave dip where the knuckle round meets the wrist's sweep filled
  inside a zone (a closing: the back stays one curve into the cuff, only the
  kink goes). → a ``K.Hand`` with ``stub`` 0 (already tucked) for ``add_to``.
  Only the back side goes in the zone: a closing that reaches the heel
  fills the wrist's taper too (a convex hull did: the wrist read as wide as
  the knuckles).
* ``add_haloed`` — the trumpet fist stacked with its OWN paper channel on the
  tabard (the kit carries only the attribute's channel round the fingertips):
  the tabard's inner chain rail ran 2–3 px beside the fist's back, leaving red
  teeth and half stones along it. The channel is kept inside the panel's red
  rim (never opening the tabard's edge line onto the sleeve), and the ground
  between it and the trumpet's own channel is closed on a round arc under
  the heel, as the kit does for a heel beside a haloed shaft. (The red left
  between that channel and the edge line is knocked out by ``JD.rim_cut``.)
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import Point, Polygon

from deck import courtkit as K
from deck.courtkit import (BIG, C, FIST_H_K, FIST_H_MIN, FIST_LEN_K, FIST_TIP_OUT, HAND_STUB, MEDIUM,  # noqa: F401
                           PARALLEL_MIN, P, Hand, Part, Path, R, arc_sag, halfplane, line, outline, seg)
from deck.courtkit import (_crease, _edge, _hand_warn, _junction_smooth, _polys_of, _qbez, _rigid,  # noqa: F401
                           _to_local, _unit, _vec, _xf)


def _biggest(g):
    return max(K._polys_of(g.buffer(0)), key=lambda q: q.area)


def smooth_back(hand, sc, zone, r):
    """``hand`` (a kit Hand) tucked into the arm already in ``sc``; the dip
    between its knuckle round and its wrist sweep closed (radius ``r``)
    inside ``zone`` (the cuff is never touched: the tuck already cut the
    wrist on the cuff's edge, and the closing is clipped off the cuff)."""
    hp = hand.tucked(sc)
    cuffs = [it.occ for it in sc.items if it.occ is not None and not it.occ.is_empty
             and any(w in it.name.lower() for w in K.CUFF_WORDS)]
    cuff = K.U(*cuffs) if cuffs else None
    z = zone if cuff is None else zone.difference(cuff.buffer(0.6))
    cl = hp.shape.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)
    shape = _biggest(K.U(hp.shape, cl.intersection(z)))
    part = K.Part(shape, hp.fills, K.outline(shape) + hp.meta["inner"], dict(hp.meta))
    return K.Hand(part, hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, 0.0)


def add_haloed(sc, name, hand, *, only, within, attr=None, close=K.HEEL_CLOSE):
    """Stack a (tucked) kit ``hand`` with its own paper channel (HALO) on the
    items ``only`` behind it, the channel kept inside ``within`` (e.g. clear
    of a panel's edge line and rim, so the channel never opens the panel's
    outline onto the ground behind it). With ``attr`` (the held object's
    region, itself haloed on the same items), the ground left between the
    two channels narrower than 2 × ``close`` turns to paper too, closing on a
    round arc (the kit's heel treatment): no cusp, no 1–3 px island."""
    hp = hand.tucked(sc)
    h = K.HALO + K.MEDIUM / 2
    g = hp.shape.buffer(h, quad_segs=12)
    if attr is not None:
        A = attr.buffer(h, quad_segs=12)
        closed = K.U(g, A).buffer(close, quad_segs=12).buffer(-close, quad_segs=12)
        g = K.U(g, closed.difference(A).intersection(hp.shape.buffer(h + 2.0 * close, quad_segs=12)))
    zone = g.intersection(within)
    sc.add(name, hp.frag, hp.shape, halo=K.HALO, halo_only=tuple(only), halo_zone=zone)
    return hp


def fist(at, axis_deg=-90.0, *, shaft_w=22.0, back=+1, wrist=None, wrist_w=24.0, h=34.0,
         reach=7.0, knuckle=11.0, thumb_r=5.6, hand=None, view=None, arm=None, stub=HAND_STUB,
         hidden_wrist=False, thumb=None, floor_eps=0.4) -> Hand:
    """``courtkit.fist`` (same construction, same arguments, same Hand) with
    the THUMB's tip exposed as ``thumb`` = dict(rt=, tt=): the tip radius
    (× the finger pitch; kit 0.60) and where the tip sits along the block
    (× its length back from the knuckles; kit 0.56). The kit's tip stands
    only 0.2 pitch (≈ 1.6 px) above the index finger's edge: its round end
    and that edge run together into one knot of ink at 8×. A fuller tip
    (rt ≈ 0.74) stands clear above the finger — a distinct notch — while its
    underside still continues finger line 1. ``floor_eps``: the kit keeps the
    wrist's sweep 0.4 px below the little finger's underside where the heel's
    floor starts, a 0.4 px ledge that reads as a jog in the contour at 16×;
    0 runs the underside straight into the heel. Local copy for the J♦ only."""
    a = shaft_w / 2.0
    hb = max(FIST_H_K * float(h), FIST_H_MIN)
    p = hb / 4.0
    t_up = 0.20 * hb                               # the thumb's root stands this far above the block
    ytop = -(hb + t_up) / 2.0                      # the whole fist (thumb + block) centred on ``at``
    y0 = ytop + t_up
    y1 = y0 + hb
    yc = (y0 + y1) / 2
    tip_out = min(max(float(reach), 3.0), FIST_TIP_OUT)
    x_tip = -a - tip_out
    Lf = max(FIST_LEN_K * hb, 2 * a + tip_out + max(float(knuckle), 12.0))
    x_kn = x_tip + Lf
    rot = axis_deg + 90.0
    mir = back < 0
    M, Mf = _rigid(at, rot, mirror_x=mir)
    dorsal = "L" if back > 0 else "R"
    if view is None:
        view = "back" if (hand is None or str(hand).upper()[:1] == dorsal) else "palm"
    where = f"fist at ({float(at[0]):.0f}, {float(at[1]):.0f})"

    # ---- finger block: four bands, rounded fingertip lobes, notches -------------------
    sl = (0.36 if view == "back" else 0.28) * p
    x_c = x_tip + sl
    path = Path(P(x_kn, y0)).line(P(x_c, y0))
    cusps = [P(x_c, y0)]
    for k in range(4):
        q = P(x_c, y0 + (k + 1) * p)
        path.sag(q, -sl)
        cusps.append(q)
    block = R(path.line(P(x_kn, y1)).close().d)
    block = block.buffer(-2.2, quad_segs=10).buffer(2.2, quad_segs=10)

    # ---- thumb: over the top of the fist, tip resting on the index finger --------------
    rr = 0.19 * hb                                 # root radius
    tk = {"rt": 0.60, "tt": 0.56, **(thumb or {})}
    rt = tk["rt"] * p                              # tip radius
    x_tt = x_kn - tk["tt"] * Lf
    Tc = P(x_tt, y0 + p - rt)                      # its underside continues finger line 1
    Rc = P(x_kn - 0.06 * Lf, ytop + rr)
    cen = _qbez(Tc, (Tc + Rc) / 2 + P(0.0, -1.6), Rc, 16)
    discs = [Point(*q).buffer(rw, quad_segs=16) for q, rw in zip(cen, np.linspace(rt, rr, len(cen)))]
    thumb = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(discs[:-1], discs[1:])])

    # ---- the wrist ----------------------------------------------------------------
    W = P(x_kn, yc) + hb * P(0.55, 0.62) if wrist is None else _to_local(wrist, at, rot, mir)
    Bs = P(x_kn - 0.20 * hb, yc + 0.03 * hb)       # the back-of-hand mass the wrist grows from
    chord = W - Bs
    off = math.degrees(math.atan2(chord[1], chord[0]))
    dist = float(np.hypot(*(W - P(x_kn, yc))))
    if W[0] < x_kn - 4.0 and not hidden_wrist:
        _hand_warn(f"{where}: wrist {x_kn - W[0]:.0f} px inside the knuckle line (move it out along the hand axis)")
    if abs(off) > 65.0 and not hidden_wrist:
        _hand_warn(f"{where}: wrist bent {off:.0f}° off the hand axis (≤ 65° reads)")
    if dist > 1.3 * hb and not hidden_wrist:
        _hand_warn(f"{where}: wrist {dist:.0f} px from the knuckles (> 1.3 × {hb:.0f}): a long bare wrist; "
                   "move the cuff up the forearm")
    x_min = a + PARALLEL_MIN                       # the heel's floor below the fist
    hK = 0.47 * hb                                 # half-breadth of the back at the knuckles

    def build(u):
        """hand region and interior lines (local) for a forearm direction u."""
        u = _unit(u)
        n_th = np.array([u[1], -u[0]])             # the thumb side of the wrist
        hw = min(float(wrist_w), 0.70 * hb) / 2.0
        hw_in = hw
        Wb = W - n_th * hw
        x_floor = x_min + 0.16 * hb                # the heel angles away from the shaft
        if Wb[0] < x_floor and Wb[1] > y1 and n_th[0] > 1e-3:
            hw_in = min(hw, max((W[0] - x_floor) / n_th[0], 0.55 * hw))
            Wb = W - n_th * hw_in
            if Wb[0] < x_min + 0.5:
                # never onto the shaft: the inner wrist edge stops at the heel's floor
                hw_in = max((W[0] - x_min - 0.5) / n_th[0], 0.25 * hw)
                Wb = W - n_th * hw_in
        # the wrist: one tapered sweep from the knuckle mass, arriving along the forearm
        Lw = float(np.hypot(*(W - Bs)))
        C_ = W - u * 0.45 * Lw
        nseg = max(10, int(Lw / 2.5))
        tt = np.linspace(0.0, 1.0, nseg + 1)
        cen_ = list(_qbez(Bs, C_, W, nseg + 1)) + [W + u * stub * 0.5, W + u * stub]
        wid = [hK + (hw - hK) * (t * t * (3 - 2 * t)) for t in tt] + [hw, hw]
        # the inner side narrows toward the wrist when the shaft is close
        shift = [n_th * (hw - hw_in) / 2 * (t * t * (3 - 2 * t)) for t in tt] + [n_th * (hw - hw_in) / 2] * 2
        wid = [w_ - (hw - hw_in) / 2 * (t * t * (3 - 2 * t)) for w_, t in zip(wid, list(tt) + [1.0, 1.0])]
        ds = [Point(*(q + s_)).buffer(max(rw, 0.5), quad_segs=16) for q, s_, rw in zip(cen_, shift, wid)]
        neck = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(ds[:-1], ds[1:])])
        neck = neck.intersection(halfplane(W + u * stub, W + u * stub + n_th, side=+1))
        # the heel: a smooth concave curve from the block's underside into the wrist, off the shaft
        x_h = max(x_min, min(x_kn - 0.42 * hb, Wb[0] - 2.0))
        H = _edge(P(x_h, y1), (1.0, 0.0), Wb, u, 16)
        clear = Polygon()
        if u[1] > -0.3:
            heel = Polygon([tuple(q) for q in list(H) + [W, Bs, P(x_h, y1 - 2.0)]]).buffer(0)
            neck = neck.union(heel)
            clear = Polygon([(-BIG, y1 + floor_eps), (x_h, y1 + floor_eps)] + [tuple(q) for q in H[1:]]
                            + [tuple(Wb + u * 400.0), (-BIG, BIG)]).buffer(0)
            trimmed = neck.difference(clear)
            if trimmed.geom_type == "Polygon" or not trimmed.is_empty:
                neck = max(_polys_of(trimmed), key=lambda g: g.area) if trimmed.geom_type != "Polygon" else trimmed
        # the thumb's root flows into the back of the hand: no notch between them
        root_join = shapely.union(Point(*Rc).buffer(rr, quad_segs=16),
                                  Point(*Bs).buffer(hK, quad_segs=16)).convex_hull
        root_join = root_join.intersection(shapely.box(x_kn - 0.30 * Lf, -BIG, BIG, BIG))
        hand_ = shapely.union_all([block, neck, thumb, root_join])
        # the heel's floor: nothing of the hand below the fingers comes within 7.3 px of the shaft
        floor = shapely.box(-BIG, y1 + floor_eps, x_min, BIG) if u[1] > -0.3 else Polygon()
        if not floor.is_empty:
            hand_ = hand_.difference(floor)
            if hand_.geom_type != "Polygon":
                hand_ = max(_polys_of(hand_), key=lambda g: g.area)
        keep_out = shapely.box(-BIG, -BIG, x_kn - 0.30 * Lf, BIG).union(clear.buffer(0.3)).union(floor)
        hand_ = _junction_smooth(hand_, keep_out, r=0.20 * hb)
        hand_ = hand_.buffer(-1.2, quad_segs=8).buffer(1.2, quad_segs=8)
        if hand_.geom_type != "Polygon":
            hand_ = max(_polys_of(hand_), key=lambda g: g.area)
        inner = C.Frag()
        body = block.union(neck)
        for pts in _crease(thumb, body, keep=shapely.box(-BIG, -BIG, x_kn - 0.10 * Lf, BIG)):
            inner += line(C.polyline_d(pts), MEDIUM, role="thumb")
        inner += seg(cusps[1] + P(0.3, 0.0), P(x_tt + 0.4, y0 + p), MEDIUM, role="finger")
        ends = {2: 0.16, 3: 0.24} if view == "back" else {2: 0.30, 3: 0.34}
        for k in (2, 3):
            q0 = cusps[k] + P(0.3, 0.0)
            inner += line(arc_sag(q0, P(x_kn - ends[k] * Lf, q0[1]), -0.7), MEDIUM, role="finger")
        if view == "palm":
            # the fingertips curled back to the heel: tip lobes where the lines end
            xf = x_kn - max(ends.values()) * Lf - 0.8
            for k in (1, 2, 3):
                ya, yz = y0 + k * p + 0.4, y0 + (k + 1) * p - (0.4 if k < 3 else 3.2)
                inner += line(arc_sag(P(xf, ya), P(xf, yz), 0.26 * p), MEDIUM, role="fingertip")
        return hand_, inner, 2 * hw

    drawn = dorsal if view == "back" else ("R" if dorsal == "L" else "L")
    tipzone = _xf(shapely.box(-BIG, -BIG, -a + 1.0, BIG), M)       # the fingertip side of the shaft
    heelzone = _xf(shapely.box(a - 1.0, y1 - 1.0, BIG, BIG), M)     # below the fingers, knuckle side
    base_meta = {"kind": "fist", "hand": drawn, "view": view, "block_h": hb, "block_len": Lf, "wrist_off_deg": off}
    Ws = _xf(Point(*W), M)
    Ws = P(Ws.x, Ws.y)

    def place(u_local):
        hl, il, ww = build(u_local)
        hs, is_ = _xf(hl, M), il.transformed(Mf)
        meta = {**base_meta, "inner": is_, "rebuild": rebuild, "tipzone": tipzone, "heelzone": heelzone}
        return Part(hs, C.Frag(), outline(hs) + is_, meta), ww, _unit(_vec(M, _unit(u_local)))

    def _loc_vec(v):
        return _to_local(P(at) + P(v), at, rot, mir)

    def rebuild(u_screen):
        """the same hand with its wrist arriving along screen direction u_screen."""
        return place(_loc_vec(u_screen))[0]

    u0 = _loc_vec(arm) if arm is not None else chord
    part, ww, us = place(u0)
    return Hand(part, Part(_xf(thumb, M), C.Frag(), C.Frag(), {"merged": True}), Ws, ww, us, float(stub))
