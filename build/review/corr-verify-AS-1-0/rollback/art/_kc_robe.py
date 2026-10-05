"""K♣ · the robe and the stole (brief §H.7).

    robe_outline  the jade robe's left half: yoke, shoulder corner and the side
                  flaring out in a concave arc like a bald cypress's buttressed base
    robe          'Robe: jade, with vertical buttress fluting in Aquifer, widening
                  downward' — FINE Aquifer flute lines on rays from a point high
                  above the head, so they fan out downward; as the field widens new
                  flutes FORK off their neighbours (a buttress's fibres splitting),
                  so no flute has a free end
    stole         'Stole: Gill Red, with comb sprays knocked out' — a red band over
                  each shoulder, a knocked-out piping line inside each long edge and
                  a hanging cypress twig down its middle: alternate comb-spray
                  branchlets (§G.18) drooping from a knocked-out twig, all paper
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C

P, AX = K.P, K.AX
FINE, MEDIUM, CONTOUR = T.FINE, T.MEDIUM, T.CONTOUR
INK, RED, JADE, GOLD = T.INK, T.RED, T.JADE, T.FOIL
GAP, GAP_MARK = K.GAP, K.GAP_MARK


# =============================================================================
# robe
# =============================================================================
def robe_outline(neck_y=272.0, neck_heading=169.0, yoke_r=380.0, yoke_sweep=7.0, run=140.0, corner_r=30.0,
                 side_heading=92.0, flare_r=420.0, flare=16.0, bottom=548.0):
    """Left half of the robe outline, from the axis at the neck."""
    t = C.Turtle(AX, neck_y, neck_heading)
    t.arc(yoke_r, -yoke_sweep)
    t.fd(run)
    t.arc(corner_r, -(neck_heading - yoke_sweep - side_heading))
    t.arc(flare_r, flare)
    y0 = t.pos[1]
    Lr = (bottom - y0) / math.sin(math.radians(t.heading))
    t.fd(max(Lr, 0.0))
    return np.asarray(t.pts(0.5)[0])


def _smooth(t):
    return t * t * (3 - 2 * t)


def fork_fluting(zone, *, vy=-300.0, pitch=13.0, y_ref=511.0, forks=None, fork_len=46.0, x_span=260.0,
                 w=FINE) -> C.Frag:
    """Buttress fluting: rays from (AX, vy), ``pitch`` apart at ``y_ref``.
    Even rays (primaries) run the full height of ``zone`` (they butt on its
    edge); odd rays (secondaries) FORK off a neighbouring primary at a height
    from ``forks`` and ease out to their own ray over ``fork_len`` px, so the
    fluting multiplies as the robe widens downward and no flute has a free
    end. → Frag of FINE Aquifer lines clipped to ``zone``."""
    zone = K.R(zone)
    f = C.Frag()
    n = int(x_span // pitch)
    ys = np.arange(150.0, 560.0, 1.0)

    def ray_x(k, y):
        return AX + k * pitch * (y - vy) / (y_ref - vy)

    forks = forks or (412.0, 446.0, 388.0, 430.0, 470.0, 400.0, 456.0, 420.0)
    for k in range(-n, n + 1):
        if k % 2 == 0:
            pts = np.column_stack([[ray_x(k, y) for y in ys], ys])
        else:
            # it splits off its OUTER neighbour (mirror-symmetric; the axis
            # flute runs on unbranched)
            parent = k + (1 if k > 0 else -1)
            ys_ = ys[ys >= forks[abs(k) % len(forks)]]
            y0 = ys_[0]
            t = np.clip((ys_ - y0) / fork_len, 0.0, 1.0)
            # leave the parent at an angle (a Y fork), ease onto the own ray
            e = 1.0 - (1.0 - t) ** 2
            xs = np.array([ray_x(parent, y) + (ray_x(k, y) - ray_x(parent, y)) * ee for y, ee in zip(ys_, e)])
            pts = np.column_stack([xs, ys_])
        ln = LineString(pts).intersection(zone)
        for g in K._lines_of(ln):
            if g.length > 6:
                f += K.line(np.asarray(g.coords), w, role="flute")
    return f


def strata_fluting(zone, *, vy=-400.0, y_ref=511.0, widths=(19.0, 12.0), centre=19.0, hatched="thin",
                   angle=45.0, x_span=300.0, forks=None, w=FINE) -> C.Frag:
    """Buttress fluting as VERTICAL strata (the K♠ mantle's §G.11 courses
    stood on end): bands alternating ``widths`` px at ``y_ref`` on rays from
    (AX, vy), so every flute widens downward; the thin bands (the grooves)
    hatched at 45° (mirrored on the right half), the broad ones (the ridges)
    plain. Mirror-symmetric about the axis. → Frag of FINE Aquifer lines."""
    zone = K.R(zone)
    f = C.Frag()
    def ray_x(X, y):
        return AX + (X - AX) * (y - vy) / (y_ref - vy)
    bounds, grooves = [], []
    x = centre / 2
    k = 0
    while x < x_span:
        wdt = widths[(k + 1) % 2]
        bounds.append(x)
        if (k + 1) % 2 == 1:
            grooves.append((x, x + wdt))
        x += wdt
        k += 1
    ys = np.array([150.0, 600.0])
    for sg in (-1, 1):
        for X in bounds:
            pts = np.column_stack([[ray_x(AX + sg * X, y) for y in ys], ys])
            ln = LineString(pts).intersection(zone)
            for g in K._lines_of(ln):
                if g.length > 6:
                    f += K.line(np.asarray(g.coords), w, role="flute")
        if hatched:
            for (a, b) in grooves:
                band = Polygon([(ray_x(AX + sg * a, 150.0), 150.0), (ray_x(AX + sg * b, 150.0), 150.0),
                                (ray_x(AX + sg * b, 600.0), 600.0), (ray_x(AX + sg * a, 600.0), 600.0)]).buffer(0)
                band = band.intersection(zone)
                if band.is_empty:
                    continue
                ang = -angle if sg < 0 else -(180.0 - angle)
                f += K.hatch_in(band, angle=ang)
    return f


def robe(*, border=30.0, seam=True, fluting=True, flute_kw=None, flute_kind="fork", **kw) -> K.Part:
    """The jade robe: bilateral silhouette, a plain border band + FINE seam
    along the whole outer edge (never along the band), buttress fluting
    inside."""
    pts = robe_outline(**kw)
    bottom = pts[-1][1]
    half = Polygon(np.vstack([pts, [[AX, bottom]]])).buffer(0)
    shape = K.U(half, K.mirror(half))
    ext = np.vstack([pts, [[pts[-1][0] - 60.0, bottom + 300.0], [AX, bottom + 300.0]]])
    ext_half = Polygon(ext).buffer(0)
    ext_shape = K.U(ext_half, K.mirror(ext_half))
    inner = ext_shape.buffer(-border, quad_segs=16).intersection(K.box(0, 0, 2000, bottom + 20))
    lines = K.outline(shape)
    if seam:
        lines += C.stroke(K.D(inner), FINE, role="seam")
    if fluting:
        zone = inner.buffer(-0.05)
        if flute_kind == "strata":
            lines += strata_fluting(zone, **(flute_kw or {}))
        else:
            lines += fork_fluting(zone, **(flute_kw or {}))
    return K.Part(shape, K.fill(shape, JADE), lines, {"inner": inner, "half": pts})


# =============================================================================
# stole
# =============================================================================
def spray_ko(p0, p1, *, tick=9.0, angle=50.0, pitch=None, w=MEDIUM, end_gap=3.0, both=True, sag=0.0,
             start=4.0):
    """One cypress branchlet for knocking out of red (§G.18 comb spray at
    MEDIUM, so each knockout line is ≥ 2.5 px): a rachis from p0 (base) to
    p1 (tip), straight or bowed by ``sag`` (an arc), and ticks both sides
    swept ``angle``° toward the tip, their lengths on a vesica envelope; the
    pitch keeps ≥ 3 px of red between neighbouring ticks. → Frag."""
    p0, p1 = P(p0), P(p1)
    d = K.arc_sag(p0, p1, sag) if abs(sag) > 1e-6 else f"M{p0[0]:.3f} {p0[1]:.3f}L{p1[0]:.3f} {p1[1]:.3f}"
    pts = C.sample_d(d, 0.25)[0][0]
    cv = K.G.Curve(pts)
    L = cv.length
    sa = math.sin(math.radians(angle))
    pitch = pitch or (w + GAP_MARK + 0.3) / sa
    f = K.line(d, w, role="rachis")
    s0, s1 = start, L - end_gap
    chord = s1 - s0
    reach = tick * sa
    Rv = ((chord / 2) ** 2 + reach ** 2) / (2 * reach)
    n = int(chord // pitch)
    ss = s0 + (chord - n * pitch) / 2 + np.arange(n + 1) * pitch
    for s in ss:
        xm = s - (s0 + s1) / 2
        hw = math.sqrt(max(Rv * Rv - xm * xm, 0.0)) - (Rv - reach)
        Lt = hw / sa
        if Lt < 3.0:
            continue
        p = cv.at_s(s)
        t = cv.tangent_s(s)
        a = math.atan2(t[1], t[0])
        for sd in ((1, -1) if both else (1,)):
            ang = a - sd * math.radians(angle)
            q = p + Lt * np.array([math.cos(ang), math.sin(ang)])
            f += K.seg(p, q, w, role="tick")
    return f


def stole(side=-1, *, within=None, x_in=360.0, x_out=298.0, shoulder=(266.0, 292.0), knee_y=372.0,
          bottom=548.0, piping=5.6, piping_sides="both", piping_top=312.0, sprays=(400.0, 448.0, 496.0),
          spray_len=48.0, spray_angle=35.0, spray_sag=3.0, tick=10.0, cones=True, cone_d=8.4) -> K.Part:
    """One side of the stole (left; ``side`` +1 mirrors): a broad red band
    coming over the shoulder from behind the neck and hanging straight between
    ``x_out`` and ``x_in``. Knocked out of the red (paper, MEDIUM ≥ 2.5 px,
    gaps ≥ 3): a piping line ``piping`` px inside the long edge(s)
    (``piping_sides`` 'both' | 'outer' | 'inner'), and down the middle a
    column of cypress sprigs — §G.18 comb sprays tilted with the tip up and
    out, each carrying its round cone (a knocked-out bead) at the tip."""
    sh = P(shoulder)
    outer = K.Path(P(sh[0] - 30.0, sh[1] - 40.0)).line(sh).arc3(
        P((sh[0] + x_out) / 2 + 3.0, (sh[1] + knee_y) / 2), P(x_out, knee_y)).line((x_out, bottom))
    reg = K.R(outer.line((x_in, bottom)).line((x_in, sh[1] - 60.0)).close().d)
    if within is not None:
        reg = reg.intersection(K.R(within))
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    xc = (x_in + x_out) / 2
    ko = C.Frag()
    edge_clear = MEDIUM / 2 + GAP_MARK + MEDIUM / 2 + 0.2          # a knockout line 3 px inside the outline
    if piping:
        # piping: the stole's own outline offset inward (so it follows the
        # shoulder curve), kept only along the hanging part
        pz = reg.buffer(-piping, quad_segs=12)
        keep = K.box(0, piping_top, 2000, bottom + 40.0)
        if piping_sides == "outer":
            keep = keep.intersection(K.box(0, 0, x_in - piping - 4.0, 2000))
        elif piping_sides == "inner":
            keep = keep.intersection(K.box(x_out + piping + 14.0, 0, 2000, 2000))
        for g in K._lines_of(pz.boundary):
            ko += K.clip_in(K.line(np.asarray(g.coords), MEDIUM, role="piping"), keep)
    body = reg.buffer(-(piping + MEDIUM / 2 + GAP_MARK + MEDIUM / 2 + 0.2)) if piping else reg.buffer(-edge_clear)
    ko_t = C.Frag()
    a = math.radians(spray_angle)
    for y in sprays:
        base = P(xc + spray_len * 0.5 * math.sin(a) * 0.9, y)
        tip = base + spray_len * np.array([-math.sin(a), -math.cos(a)])
        ko_t += spray_ko(base, tip, tick=tick, sag=spray_sag)
        if cones:
            u = (tip - base) / np.hypot(*(tip - base))
            ko_t += K.dot(tip + u * (cone_d / 2 + 1.0), cone_d, role="cone")
    ko += K.clip_in(ko_t, body)
    fill_d = C.knockout(K.D(reg), ko)
    part = K.Part(reg, K.fill(fill_d, RED), K.outline(reg), {"x": (x_out, x_in), "body": body})
    return part.mirrored(AX) if side > 0 else part
