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


def spline_pts(points, h_start=None, h_end=None, headings=None, step=0.5):
    d = K.spline(points, h_start, h_end, headings=headings)
    return C.sample_d(d, step)[0][0]


# =============================================================================
# the portico diadem
# =============================================================================
def _arc_y(p0, pm, p1):
    """y(x) on the circle through three points (upper or lower branch picked
    to pass through pm)."""
    c, r = K.circ3(P(p0), P(pm), P(p1))
    sgn = 1.0 if pm[1] > c[1] else -1.0
    return lambda x: c[1] + sgn * math.sqrt(max(r * r - (x - c[0]) ** 2, 0.0))


def portico(ax, *, xl, xr, top_l, top_c, top_r, band_h=16.0, n_col=4, pitch=19.0, far_k=0.88, col_w=10.0,
            col_h=26.0, vy=420.0, cap_h=5.0, cap_over=2.5, ent_h=6.0, ped_over=5.0, ped_rise=26.0,
            oculus_r=6.8, acro=(15.0, 11.0), stones=(10.0, 6.0), stone_pitch=17.0, turn=+1, shade_color=RED,
            cornice=False, oculus_at=0.40) -> K.Part:
    """The portico diadem (§H.11: 'a gold pediment with an oculus over four
    column-teeth'), worn as a crown.

    The circlet runs from ``xl`` to ``xr`` (the sides of the hair mass),
    its top edge an arc through (xl, top_l), (ax, top_c), (xr, top_r) — the
    front dips toward the viewer — ``band_h`` deep, and carries the ♦
    stepping-stone chain (§G.23: Aquifer lozenges along its mid-line, 3 px
    clear of its edges). ``n_col`` gold column-teeth stand on it about the
    feature axis ``ax`` (the far side's pitch × ``far_k``: the head turns),
    their axes on rays from (ax, ``vy``) so the crown FLARES; each carries a
    capital block; between them JADE shade. A gold architrave spans the
    capitals and the pediment (``ped_rise`` tall, ``ped_over`` beyond the
    architrave) sits on it, a FINE raking cornice inside its slopes and the
    OCULUS in its tympanum: a round window knocked out to paper, four FINE
    lights. A gold lozenge (the ♦ house mark) crowns the apex."""
    yb = _arc_y((xl, top_l), (ax, top_c), (xr, top_r))
    # ---- circlet
    xs = np.linspace(xl, xr, 160)
    up = np.column_stack([xs, [yb(x) for x in xs]])
    lo = up + P(0.0, band_h)
    band = _poly(np.vstack([up, lo[::-1]]))
    # ---- column-teeth
    offs = [(k - (n_col - 1) / 2) for k in range(n_col)]
    xs_b = [ax + o * pitch * (far_k if o * turn > 0 else 1.0) for o in offs]
    cols, caps = [], []
    y_top = min(yb(x) for x in xs_b) - col_h
    for x in xs_b:
        y0 = yb(x) + 3.0                                   # foot runs into the band (hidden)
        kx = (vy - y_top) / (vy - y0)
        xt = ax + (x - ax) * kx
        u = P(xt - x, y_top - y0)
        u = u / np.hypot(*u)
        nrm = P(-u[1], u[0])
        a, b = P(x, y0), P(xt, y_top + cap_h * 0.5)
        cols.append(_poly([a + nrm * col_w / 2, b + nrm * col_w / 2, b - nrm * col_w / 2, a - nrm * col_w / 2]))
        if cap_h:
            caps.append(K.box(xt - col_w / 2 - cap_over, y_top - 0.5, xt + col_w / 2 + cap_over, y_top + cap_h))
    xt_l = ax + (xs_b[0] - ax) * (vy - y_top) / (vy - yb(xs_b[0]) - 3.0)
    xt_r = ax + (xs_b[-1] - ax) * (vy - y_top) / (vy - yb(xs_b[-1]) - 3.0)
    hw_ent = max(ax - xt_l, xt_r - ax) + col_w / 2 + cap_over + 1.5
    ent = K.box(ax - hw_ent, y_top - ent_h, ax + hw_ent, y_top + 0.5)
    ped_hw = hw_ent + ped_over
    ped_base = y_top - ent_h + 0.5
    apex = P(ax, ped_base - ped_rise)
    ped = _poly([(ax - ped_hw, ped_base), (ax + ped_hw, ped_base), tuple(apex)])
    # shade between the columns: under the architrave, above the circlet
    shade_zone = _poly([(xs_b[0], yb(xs_b[0]) + 2.0), (xt_l, y_top), (xt_r, y_top),
                        (xs_b[-1], yb(xs_b[-1]) + 2.0)])
    shade = shade_zone.difference(U(*cols)).difference(band)
    aw, ah = acro
    acro_c = P(ax, apex[1] - ah / 2 + 3.5)
    acro_r = R(C.lozenge_d(acro_c[0], acro_c[1], ah, aw, 90.0))
    stone = U(ent, ped, acro_r, *cols, *caps)
    oc = P(ax, ped_base - ped_rise * oculus_at)
    ocu = R(K.circle(oc, oculus_r))
    shape = U(stone, shade, band)
    fills = K.fill(U(stone, band).difference(ocu), GOLD) + K.fill(shade, shade_color)
    lines = C.Frag()
    # raking cornice: FINE, inset from the pediment's slopes
    inset = CONTOUR / 2 + GAP + FINE / 2 + 0.3
    pin = ped.buffer(-inset, join_style=2)
    if cornice and not pin.is_empty:
        cc = np.asarray(pin.exterior.coords)
        ymax = cc[:, 1].max()
        lft = cc[np.argmin(cc[:, 0])]
        rgt = cc[np.argmax(cc[:, 0])]
        apx = cc[np.argmin(cc[:, 1])]
        lines += K.line(C.polyline_d([lft, apx, rgt]), FINE, style="rule", role="cornice")
    lines += K.outline(K.circle(oc, oculus_r), MEDIUM, role="oculus")
    for a in (0, 90):
        lines += K.seg(K.polar(oc, oculus_r, a), K.polar(oc, oculus_r, a + 180), FINE, role="mullion")
    # contours: the stone pieces, each stopping under what is in front
    front = K.outline(U(ent, ped))
    for i_, c_ in enumerate(cols):
        k_ = caps[i_] if caps else Polygon()
        front += K.clip_out(K.outline(c_), U(k_, ent), eps=-0.6, trap=0.0)
    for k_ in caps:
        front += K.clip_out(K.outline(k_), ent, eps=-0.6, trap=0.0)
    front = K.clip_out(front, acro_r, eps=-0.5, trap=0.0) + C.stroke(D(acro_r), MEDIUM, style="point",
                                                                      role="acroterion")
    lines += K.clip_out(front, band, eps=-0.8, trap=0.0)
    lines += K.outline(band)
    # the ♦ stepping-stone chain along the circlet's mid-line
    mid = np.column_stack([xs, [yb(x) + band_h / 2 for x in xs]])
    mc = LineString(mid)
    L = mc.length
    sl, sw = stones
    n = int((L - 2 * sl) // stone_pitch)
    s0 = (L - (n - 1) * stone_pitch) / 2
    s_ax = mc.project(Point(ax, yb(ax) + band_h / 2))
    # centre one stone on the axis
    k0 = round((s_ax - s0) / stone_pitch)
    s0 = s_ax - k0 * stone_pitch
    s = s0
    while s < L - sl * 0.9:
        if s > sl * 0.9:
            p = mc.interpolate(s)
            q = mc.interpolate(min(s + 1.0, L))
            ang = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
            lines += C.fill(C.lozenge_d(p.x, p.y, sl, sw, ang), color=INK, role="stone")
        s += stone_pitch
    return K.Part(shape, fills, lines, {"band": band, "oculus": oc, "apex": apex, "top": acro_c[1] - ah / 2,
                                        "cols": xs_b, "band_y": yb})


# =============================================================================
# the balance scales
# =============================================================================
def balance(fx, *, beam_y=140.0, half=62.0, beam_h=(12.0, 8.0), boss_r=6.5, fin=(16.0, 24.0), staff_hw=7.0,
            staff_bottom=548.0, collars=(236.0, 300.0), knop_r=8.5, pan_hw=22.0, pan_y=196.0, surf_ry=12.0,
            pan_depth=11.0, foot=(7.0, 5.0), hook_dy=11.0, cord_in=1.5, drop=False):
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
    neck = K.box(fx - 3.5, fy + fh / 2 - 2.0, fx + 3.5, beam_y)
    lozenge = R(C.lozenge_d(fx, fy, fh, fw, 90.0))
    pivot = K.circle((fx, beam_y), 4.6)
    shape = U(beam, *bosses, neck, lozenge)
    fl = K.fill(shape, GOLD)
    bl = K.outline(beam) + K.outline(lozenge)
    for b in bosses:
        bl = K.clip_out(bl, b, eps=-0.5, trap=0.0) + K.outline(b)
    bl = K.clip_out(bl, neck, eps=-0.5, trap=0.0) + K.clip_out(K.outline(neck), U(beam, lozenge), eps=-0.5,
                                                                trap=0.0)
    half_l = lozenge.intersection(K.box(0, 0, fx, 1000))
    bl += K.hatch_in(half_l, angle=-45.0, origin=(fx, fy))
    bl += K.seg(P(fx, fy - fh / 2 + 4.0), P(fx, fy + fh / 2 - 4.0), FINE, style="rule", role="joint")
    bl += K.outline(pivot, MEDIUM, role="pivot")
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
# the stomacher: four fluted column shafts
# =============================================================================
def stomacher(ax, *, top=338.0, bottom=548.0, hw_top=38.0, hw_bot=29.0, cap_h=9.0, cap_over=4.0, n=4,
              necking=True, base_h=0.0) -> K.Part:
    """Four gold column shafts side by side (§H.11 'stomacher: four gold
    fluted column shafts'), tapering from ``hw_top`` to ``hw_bot`` (the
    waist), MEDIUM joints between them and one FINE flute down each shaft;
    a capital band across their tops (``cap_over`` wider each side) with an
    astragal (necking) line under it."""
    y_cap = top + cap_h

    def xat(t, y):                  # t in [-1, 1] across the panel
        k = (y - y_cap) / (bottom - y_cap)
        hw = hw_top + (hw_bot - hw_top) * k
        return ax + t * hw
    panel = _poly([(xat(-1, y_cap), y_cap), (xat(1, y_cap), y_cap), (xat(1, bottom), bottom),
                   (xat(-1, bottom), bottom)])
    cap = R(K.rrect(ax - hw_top - cap_over, top, ax + hw_top + cap_over, y_cap + 1.0, 2.0))
    shape = U(panel, cap)
    lines = K.clip_out(K.outline(panel), cap, eps=-0.5, trap=0.0) + K.outline(cap)
    y_end = bottom
    if base_h:
        # the base (a plinth under the shafts): wider than the shafts' feet
        hwb = hw_bot + cap_over
        base = R(K.rrect(ax - hwb, bottom - 1.0, ax + hwb, bottom + base_h, 2.0))
        shape = U(shape, base)
        lines = K.clip_out(lines, base, eps=-0.5, trap=0.0) + K.outline(base)
        yb2 = bottom - 6.0
        lines += K.seg(P(xat(-1, yb2), yb2), P(xat(1, yb2), yb2), FINE, style="rule", role="torus")
        y_end = yb2 - FINE - GAP_MARK - 0.5
    ts = np.linspace(-1, 1, n + 1)
    for t in ts[1:-1]:
        lines += K.seg(P(xat(t, y_cap), y_cap), P(xat(t, bottom), bottom), MEDIUM, role="joint")
    flute_end = y_end
    y_f0 = y_cap + MEDIUM / 2 + GAP_MARK + FINE / 2 + 1.0
    if necking:
        yn = y_cap + 7.0
        lines += K.seg(P(xat(-1, yn), yn), P(xat(1, yn), yn), FINE, style="rule", role="necking")
        y_f0 = yn + FINE + GAP_MARK + 0.5
    for a, b in zip(ts[:-1], ts[1:]):
        t = (a + b) / 2
        lines += K.seg(P(xat(t, y_f0), y_f0), P(xat(t, flute_end), flute_end), FINE, style="rule", role="flute")
    return K.Part(shape, K.fill(shape, GOLD), lines, {"top": top, "xat": xat})
