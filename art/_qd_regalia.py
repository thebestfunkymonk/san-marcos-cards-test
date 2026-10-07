"""art/_qd_regalia.py — Q♦ · The Queen of Scales: her regalia (brief §H.11).

    portico     the portico diadem: a gold circlet wrapping the head, carrying
                the ♦ stepping-stone chain; four column-teeth rising from it on
                rays (a crown flares; a building does not), jade shade between
                them; a low pediment whose tympanum holds the OCULUS; a gold
                lozenge acroterion on the apex
    balance     the balance scales held aloft on a gold standard: level beam,
                lozenge pointer, cords, two pans of water with ripple rings
    stomacher   four gold fluted column shafts under a capital band, tapering
                to the waist

Every builder returns a deck.courtkit Part drawn at final size (card px)."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C

P, R, U, D = K.P, K.R, K.U, K.D
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD
GAP, GAP_MARK = K.GAP, K.GAP_MARK


def _poly(pts):
    return Polygon([tuple(map(float, p)) for p in pts]).buffer(0)


# =============================================================================
# the portico diadem
# =============================================================================
def _arc_y(p0, pm, p1):
    """y(x) on the circle through three points (upper or lower branch picked
    to pass through pm)."""
    c, r = K.circ3(P(p0), P(pm), P(p1))
    sgn = 1.0 if pm[1] > c[1] else -1.0
    return lambda x: c[1] + sgn * math.sqrt(max(r * r - (x - c[0]) ** 2, 0.0))


# =============================================================================
# the balance scales
# =============================================================================
def balance(fx, *, beam_y=140.0, half=62.0, beam_h=(12.0, 8.0), boss_r=6.5, fin=(16.0, 24.0), staff_hw=7.0,
            staff_bottom=548.0, collars=(236.0, 300.0), knop_r=8.5, pan_hw=22.0, pan_y=196.0, surf_ry=12.0,
            pan_depth=11.0, foot=(7.0, 5.0), hook_dy=11.0, cord_in=1.5, drop=False, pivot=True, neck_hw=3.5,
            fin_marks=True):
    """→ dict of Parts: 'staff' (behind the hand), 'beam' (beam, bosses,
    pivot, lozenge pointer), 'cords' (lines only), 'panL', 'panR'.

    The pans are shallow gold dishes seen a little from above: the WATER is
    a jade ellipse (``pan_hw`` × ``surf_ry``) with ripple rings on it (§G.8:
    one FINE ring and the drop at its centre — the most a 24 px surface
    holds at §I.12's gaps), the gold bowl below it. The beam is level and
    the pointer plumb: the kingdom's water, weighed even."""
    out = {}
    top = beam_y + beam_h[0] / 2 - 1.0
    shaft = K.box(fx - staff_hw, top, fx + staff_hw, staff_bottom)
    knop_c = P(fx, beam_y + beam_h[0] / 2 + knop_r + 1.0)
    knop = R(K.circle(knop_c, knop_r))
    cl = [R(K.rrect(fx - staff_hw - 3.5, y - 3.8, fx + staff_hw + 3.5, y + 3.8, 2.5)) for y in collars]
    body = U(shaft, knop, *cl)
    lines = K.clip_out(K.outline(shaft), U(knop, *cl), eps=-0.5, trap=0.0)
    for c_ in cl:
        lines += K.outline(c_)
    lines += K.outline(knop)
    out["staff"] = K.Part(body, K.fill(body, GOLD), lines, {"knop": knop_c})
    # ---- beam + pointer
    hc, he = beam_h[0] / 2, beam_h[1] / 2
    xl, xr = fx - half, fx + half
    beam = _poly([(xl, beam_y - he), (fx, beam_y - hc), (xr, beam_y - he), (xr, beam_y + he), (fx, beam_y + hc),
                  (xl, beam_y + he)])
    bosses = [R(K.circle((x, beam_y), boss_r)) for x in (xl, xr)]
    fw, fh = fin
    fy = beam_y - hc - 5.0 - fh / 2
    neck = K.box(fx - neck_hw, fy + fh / 2 - 2.0, fx + neck_hw, beam_y)
    lozenge = R(C.lozenge_d(fx, fy, fh, fw, 90.0))
    pivot_d = K.circle((fx, beam_y), 4.6)
    shape = U(beam, *bosses, neck, lozenge)
    fl = K.fill(shape, GOLD)
    bl = K.outline(beam) + K.outline(lozenge)
    for b in bosses:
        bl = K.clip_out(bl, b, eps=-0.5, trap=0.0) + K.outline(b)
    bl = K.clip_out(bl, neck, eps=-0.5, trap=0.0) + K.clip_out(K.outline(neck), U(beam, lozenge), eps=-0.5,
                                                                trap=0.0)
    if fin_marks:
        half_l = lozenge.intersection(K.box(0, 0, fx, 1000))
        bl += K.hatch_in(half_l, angle=-45.0, origin=(fx, fy))
        bl += K.seg(P(fx, fy - fh / 2 + 4.0), P(fx, fy + fh / 2 - 4.0), FINE, style="rule", role="joint")
    if pivot:
        bl += K.outline(pivot_d, MEDIUM, role="pivot")
    out["beam"] = K.Part(shape, fl, bl, {"ends": (P(xl, beam_y), P(xr, beam_y)), "top": fy - fh / 2})
    # ---- pans
    cords = C.Frag()
    for key, x in (("panL", xl), ("panR", xr)):
        surf = R(C.ellipse_d(x, pan_y, pan_hw, surf_ry))
        bowl = R(K.Path((x - pan_hw, pan_y)).sag((x + pan_hw, pan_y), -(surf_ry * 0 + pan_depth + surf_ry * 0.0)).close().d)
        # the bowl: the lower half-ellipse deepened by pan_depth
        th = np.radians(np.linspace(0, 180, 90))
        bowl_pts = np.column_stack([x + pan_hw * np.cos(th), pan_y + (surf_ry + pan_depth) * np.sin(th)])
        bowl = _poly(np.vstack([bowl_pts, [[x - pan_hw, pan_y], [x + pan_hw, pan_y]]]))
        if foot:
            fw_, fh_ = foot
            yf = pan_y + surf_ry + pan_depth - 3.0
            foot_r = R(K.rrect(x - fw_, yf, x + fw_, yf + fh_ + 3.0, 2.0))
        else:
            foot_r = Polygon()
        pan = U(surf, bowl, foot_r)
        gold_r = U(bowl, foot_r).difference(surf)
        gold_r = gold_r.buffer(-1.6, join_style=2).buffer(1.6, join_style=2)      # no sliver at the rim ends
        fills = K.fill(gold_r, GOLD) + K.fill(surf, JADE)
        pl = K.outline(surf) + K.clip_out(K.outline(U(bowl, foot_r)), surf, eps=-0.5, trap=0.0)
        # ripple ring + the drop (Aquifer on jade, §C.4)
        room = surf_ry - MEDIUM / 2 - GAP - FINE / 2
        rr_y = room
        rr_x = rr_y * pan_hw / surf_ry
        pl += K.line(C.ellipse_d(x, pan_y, rr_x, rr_y), FINE, role="ripple")
        inner = rr_y - FINE / 2
        if drop and inner - GAP_MARK >= 2.1:
            pl += K.dot((x, pan_y), 4.2, role="drop")
        out[key] = K.Part(pan, fills, pl, {"c": P(x, pan_y)})
        hook = P(x, beam_y + boss_r - 0.5)               # the cords hang from the boss
        for sg in (-1, 1):
            rim = P(x + sg * (pan_hw - cord_in), pan_y - 1.0)
            cords += K.seg(hook, rim, MEDIUM, role="cord")
    out["cords"] = K.Part(Polygon(), C.Frag(), cords, {})
    return out


# =============================================================================
# the portico diadem, v3: a pediment tiara
# =============================================================================
def portico3(ax, *, xl, xr, top_l, top_c, top_r, band_h=14.0, col_offs=(-1.5, -0.5, 0.5, 1.5), pitch=26.0,
             far_k=0.82, col_w=9.0, col_h=22.0, vy=600.0, cap=(3.2, 3.0), base=(2.6, 2.6), arch_h=7.5,
             ped_hw=(60.0, 49.0), ped_rise=27.0, oculus_r=7.4, oculus_at=0.40, acro=(14.0, 10.0),
             corner_acro=None, stone=(10.0, 6.3), stone_pitch=16.0, turn=+1, oculus_pane=None, cornice=True,
             stone_dy=0.0, oculus_ring=True, foot_dy=2.0, capitals=True):
    """The portico diadem (§H.11 'a gold pediment with an oculus over four
    column-teeth') as a PEDIMENT TIARA — a crown, not a building:

    * the CIRCLET wraps the head, top edge an arc through (xl, top_l),
      (ax, top_c), (xr, top_r), ``band_h`` deep, set with the ♦
      stepping-stone chain (§G.23: Aquifer lozenges on the gold);
    * four slender column-TEETH stand on it across its whole width (the far
      side foreshortened × ``far_k``), axes on rays from (ax, ``vy``) — the
      crown flares — each with a capital and a base; PAPER between them,
      the open-work of a crown;
    * a thin ARCHITRAVE spans them, and the PEDIMENT (half-widths
      ``ped_hw`` near/far of the axis, ``ped_rise`` tall) is the tiara's
      peak: a FINE raking cornice inside its slopes, the OCULUS (a round
      window knocked out to paper — MEDIUM frame, FINE mullions) as its
      centre stone, a gold ♦ lozenge finial on the apex.

    → (frame Part, columns Part): the frame joins the silhouette (CONTOUR);
    the columns are added with sil=False so their sides stay MEDIUM."""
    yb = _arc_y((xl, top_l), (ax, top_c), (xr, top_r))
    xs = np.linspace(xl, xr, 200)
    up = np.column_stack([xs, [yb(x) for x in xs]])
    lo = up + P(0.0, band_h)
    band = _poly(np.vstack([up, lo[::-1]]))
    xs_b = [ax + o * pitch * (far_k if o * turn > 0 else 1.0) for o in col_offs]
    y_top = min(yb(x) for x in xs_b) - col_h
    cols, caps, bases, axes = [], [], [], []
    ch, cov = cap
    bh, bov = base
    for x in xs_b:
        y0 = yb(x) + foot_dy
        kx = (vy - y_top) / (vy - y0)
        xt = ax + (x - ax) * kx
        u = P(xt - x, y_top - y0)
        u = u / np.hypot(*u)
        nrm = P(-u[1], u[0])
        a, b = P(x, y0), P(xt, y_top)
        cols.append(_poly([a + nrm * col_w / 2, b + nrm * col_w / 2, b - nrm * col_w / 2, a - nrm * col_w / 2]))
        axes.append((a, b))
        caps.append(K.box(xt - col_w / 2 - cov, y_top - 0.5, xt + col_w / 2 + cov, y_top + ch) if capitals
                    else Polygon())
        if bh:
            bases.append(K.box(x - col_w / 2 - bov, yb(x) - bh, x + col_w / 2 + bov, yb(x) + 1.5))
    hl_, hr_ = ped_hw
    x_l, x_r = ax - hl_ + 4.0, ax + hr_ - 4.0
    ent = K.box(x_l, y_top - arch_h, x_r, y_top + 0.5)
    ped_base = y_top - arch_h + 0.5
    pl, pr = P(ax - hl_, ped_base), P(ax + hr_, ped_base)
    apex = P(ax, ped_base - ped_rise)
    ped = _poly([tuple(pl), tuple(pr), tuple(apex)])
    aw, ah = acro
    acro_c = P(apex[0], apex[1] - ah / 2 + 3.0)
    acros = [R(C.lozenge_d(acro_c[0], acro_c[1], ah, aw, 90.0))]
    if corner_acro:
        cw_, chh = corner_acro
        for p in (pl, pr):
            acros.append(R(C.lozenge_d(p[0], p[1] - chh / 2 + 0.5, chh, cw_, 90.0)))
    oc = P(apex[0] - 1.0, ped_base - ped_rise * oculus_at)
    ocu = R(K.circle(oc, oculus_r))
    frame = U(band, ent, ped, *acros)
    col_shape = U(*cols, *caps, *bases)
    fills_f = K.fill(frame.difference(ocu), GOLD)
    lines_f = C.Frag()
    inset = CONTOUR / 2 + GAP + FINE / 2
    pin = ped.buffer(-inset, join_style=2)
    if cornice and not pin.is_empty:
        cc = np.asarray(pin.exterior.coords)
        lft = cc[np.argmin(cc[:, 0])]
        rgt = cc[np.argmax(cc[:, 0])]
        apx = cc[np.argmin(cc[:, 1])]
        lines_f += K.line(C.polyline_d([lft, apx, rgt]), FINE, style="rule", role="cornice")
    if oculus_ring:
        lines_f += K.outline(K.circle(oc, oculus_r), MEDIUM, role="oculus")
    if oculus_pane:
        fills_f += K.fill(K.circle(oc, oculus_r), oculus_pane)
    else:
        for a_ in (0, 90):
            lines_f += K.seg(K.polar(oc, oculus_r, a_), K.polar(oc, oculus_r, a_ + 180), FINE, role="mullion")
    lines_f += K.seg(P(x_l + 0.5, ped_base), P(x_r - 0.5, ped_base), MEDIUM, role="joint")
    for a_r in acros:
        lines_f += C.stroke(D(a_r), MEDIUM, style="point", role="acroterion")
    mid = np.column_stack([xs, [yb(x) + band_h / 2 + stone_dy for x in xs]])
    mc = LineString(mid)
    L = mc.length
    sl, sw = stone
    s_ax = mc.project(Point(ax, yb(ax) + band_h / 2 + stone_dy))
    k0 = math.floor(s_ax / stone_pitch)
    s = s_ax - k0 * stone_pitch
    while s < L - sl * 0.9:
        if s > sl * 0.9:
            p = mc.interpolate(s)
            q = mc.interpolate(min(s + 1.0, L))
            ang = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
            lines_f += C.fill(C.lozenge_d(p.x, p.y, sl, sw, ang), color=INK, role="stone")
        s += stone_pitch
    fr = K.Part(frame, fills_f, lines_f, {"band": band, "oculus": oc, "apex": apex, "top": acro_c[1] - ah / 2,
                                           "band_y": yb, "y_top": y_top, "cols": xs_b, "ped": ped})
    lines_c = C.Frag()
    for i_, (c_, k_) in enumerate(zip(cols, caps)):
        b_ = bases[i_] if bases else Polygon()
        lines_c += K.clip_out(K.outline(c_), U(k_, b_), eps=-0.5, trap=0.0) if not (k_.is_empty and b_.is_empty) \
            else K.outline(c_)
        if not k_.is_empty:
            lines_c += K.outline(k_)
        if bases:
            lines_c += K.outline(b_)
    cp = K.Part(col_shape, K.fill(col_shape, GOLD), lines_c, {})
    return fr, cp


# =============================================================================
# the stomacher, v2: four fluted shafts tapering to the waist
# =============================================================================


def stomacher3(ax, *, top=334.0, hw_top=36.0, hw_mid=30.0, y_mid=436.0, y_point=484.0, cap_h=9.0, cap_over=4.5,
               n=4, necking=True, point_r=3.0) -> K.Part:
    """§H.11 'stomacher: four gold fluted column shafts': a POINTED
    stomacher on the bodice — sides tapering from ``hw_top`` to ``hw_mid``
    at ``y_mid``, then a V down to the point at ``y_point`` (above the
    waist; its C2 twin points back at it across the band) — built as four
    column shafts side by side under a capital band (+ FINE astragal):
    MEDIUM joints between the shafts, a FINE flute down each; every line
    runs out onto the V edges (no free ends)."""
    y_cap = top + cap_h

    def hw(y):
        return hw_top + (hw_mid - hw_top) * (y - y_cap) / (y_mid - y_cap)
    body = _poly([(ax - hw_top, y_cap - 1.0), (ax + hw_top, y_cap - 1.0), (ax + hw_mid, y_mid), (ax, y_point),
                  (ax - hw_mid, y_mid)])
    if point_r:
        body = body.buffer(-point_r, join_style=1).buffer(point_r, join_style=1)
    cap = R(K.rrect(ax - hw_top - cap_over, top, ax + hw_top + cap_over, y_cap + 1.0, 2.0))
    shape = U(body, cap)
    lines = K.clip_out(K.outline(body), cap, eps=-0.5, trap=0.0) + K.outline(cap)
    inside = body.buffer(-0.3)
    ts = np.linspace(-1, 1, n + 1)
    y_f0 = y_cap + MEDIUM / 2 + GAP_MARK + FINE / 2 + 1.0
    if necking:
        yn = y_cap + 7.0
        lines += K.seg(P(ax - hw(yn), yn), P(ax + hw(yn), yn), FINE, style="rule", role="necking")
        y_f0 = yn + FINE + GAP + 0.5
    for t in ts[1:-1]:
        ln = LineString([(ax + t * hw_top, y_cap), (ax + t * hw_mid, y_mid), (ax + t * hw_mid * 1.0, y_point + 20)])
        for g in K._lines_of(ln.intersection(inside)):
            lines += K.line(np.asarray(g.coords), MEDIUM, role="joint")
    for a, b in zip(ts[:-1], ts[1:]):
        t = (a + b) / 2
        ln = LineString([(ax + t * hw(y_f0), y_f0), (ax + t * hw_mid, y_mid), (ax + t * hw_mid, y_point + 20)])
        for g in K._lines_of(ln.intersection(inside)):
            lines += K.line(np.asarray(g.coords), FINE, style="rule", role="flute")
    return K.Part(shape, K.fill(shape, GOLD), lines, {"top": top, "hull": shape})
