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


def _key(v, table):
    """``table``'s entry for bound ``v`` (keys match within 0.5 px), else None."""
    for q, val in (table or {}).items():
        if abs(float(v) - float(q)) < 0.5:
            return val
    return None


def _hatch_set(band, ang, origin=None):
    """Hatch lines (LineStrings) of ``band`` exactly as K.hatch_in draws them
    (each polygon piece hatched on its own; ``origin`` fixes the phase)."""
    out = []
    for pg in K._polys_of(band):
        if pg.area <= 1.0:
            continue
        out += [LineString(c) for c in C.hatch_lines(pg, ang, K.PITCH, origin=origin)]
    return out


def _alongside(h, region, need, max_deg=30.0):
    """Does hatch line ``h`` run ALONG ``region``'s edge (within ``need`` px of
    it and within ``max_deg`` of parallel)? Such a line is cut by the region
    into a sliver that runs beside its contour (a lone tick after heal)."""
    vis = h.difference(region)
    if vis.is_empty:
        return False
    if vis.distance(region) >= need:
        return False
    from shapely.ops import nearest_points
    bd = region.boundary
    q = nearest_points(bd, vis)[0]
    s = bd.project(q)
    p0, p1 = np.asarray(bd.interpolate(s - 2.0).coords[0]), np.asarray(bd.interpolate(s + 2.0).coords[0])
    t = p1 - p0
    c = np.asarray(h.coords)
    u = c[-1] - c[0]
    cosang = abs(float(np.dot(t, u))) / (float(np.hypot(*t)) * float(np.hypot(*u)) + 1e-9)
    return cosang > math.cos(math.radians(max_deg))


def _cut_at(pcs, E, keep="above"):
    """The pieces of one groove line (``pcs``) cut at point ``E``, keeping the
    part above (or below) it; pieces wholly on the other side go."""
    from shapely.ops import substring
    out = []
    for g in pcs:
        gc = np.asarray(g.coords)
        down = gc[0][1] < gc[-1][1]                          # the piece runs downward
        if g.distance(Point(*E)) > 0.5:
            if (keep == "above" and g.bounds[3] <= E[1] + 0.5) or (keep == "below" and g.bounds[1] >= E[1] - 0.5):
                out.append(g)
            continue
        s_ = g.project(Point(*E))
        if keep == "above":
            part = substring(g, 0.0, s_) if down else substring(g, s_, g.length)
        else:
            part = substring(g, s_, g.length) if down else substring(g, 0.0, s_)
        if part.length > 6:
            out.append(part)
    return out


def _end_on(h, pcs):
    """The end of hatch line ``h`` that lies on the groove line ``pcs`` (or None)."""
    if not pcs:
        return None
    c = np.asarray(h.coords)
    g = shapely.union_all(pcs)
    e = min((c[0], c[-1]), key=lambda q: g.distance(Point(*q)))
    return e if g.distance(Point(*e)) < 0.5 else None


def _first_hit(line_pts, obs):
    """Where the polyline from line_pts[0] first reaches ``obs``'s boundary."""
    ln = LineString(line_pts)
    hit = ln.intersection(obs.boundary)
    if hit.is_empty:
        return None
    pts = [np.asarray(g.coords[0]) for g in getattr(hit, "geoms", [hit])]
    return min(pts, key=lambda q: float(np.hypot(*(q - line_pts[0]))))


def corners_of(region, *, deg=35.0, step=1.0):
    """Points where ``region``'s outline turns by more than ``deg`` within
    ±2 px (a cuff's corners): hatch and groove lines should not land there."""
    out = []
    for pg in K._polys_of(K.R(region)):
        ring = pg.exterior
        n = max(int(ring.length / step), 8)
        pts = np.array([ring.interpolate(i * ring.length / n).coords[0] for i in range(n)])
        for i in range(n):
            a, b, c = pts[(i - 2) % n], pts[i], pts[(i + 2) % n]
            u, w_ = b - a, c - b
            cosang = float(np.dot(u, w_)) / (float(np.hypot(*u)) * float(np.hypot(*w_)) + 1e-9)
            if cosang < math.cos(math.radians(deg)):
                if not out or min(np.hypot(*(np.asarray(out) - b).T)) > 3.0:
                    out.append(b)
    return out


def _groove(band, zone, ra, rb, rules, ang, v, origin):
    """One groove (band between lines ``ra`` / ``rb`` = lists of pieces) with its
    fitting ``rules`` applied, at one hatch phase. → (score, ra, rb, hatch)."""
    rays = {"a": list(ra), "b": list(rb)}
    off = lambda h: float(np.asarray(h.centroid.coords[0]) @ v)
    hs = _hatch_set(band, ang, origin=origin)
    hard, soft = [], []            # hard: margins that must be ≥ 0; soft: the smaller the slack the better
    for r in rules:
        kind = r["mode"]
        need = float(r.get("need", GAP + FINE / 2 + MEDIUM / 2))
        obs = zone.boundary if r.get("obstacle") == "seam" else (K.R(r["obstacle"]) if r.get("obstacle") is not None else None)
        if kind == "fit":
            # drop lines running along the region's edge; the phase keeps the last one a pitch off
            reg = obs
            hs = [h for h in hs if not _alongside(h, reg, need)]
            near = [h.distance(reg) for h in hs if _alongside(h, reg, need + K.PITCH)]
            soft.append(-(min(near) - need) if near else -K.PITCH)
        elif kind == "drop":
            # line ``r['line']`` runs along the zone's edge (the border seam): it goes, and the
            # groove's hatch runs on to the seam
            L = r["line"]
            if rays[L]:
                o_ = "b" if L == "a" else "a"
                g_o = np.asarray(rays[o_][0].coords) if rays[o_] else None
                g_l = np.asarray(rays[L][0].coords)
                if g_o is not None:
                    away = g_l.mean(axis=0) - g_o.mean(axis=0)
                    away = away / (np.hypot(*away) + 1e-9)
                    pl = LineString(g_l)
                    ext = shapely.union_all([pl.buffer(0.01), LineString(g_l + away * 200.0).buffer(0.01)]).convex_hull
                    band = band.union(ext.intersection(zone))
                    hs = _hatch_set(band, ang, origin=origin)
            rays[L] = []
        elif kind == "land":
            # the groove's lines land on the obstacle (a sleeve): a hatch line landing within reach
            # of a line's landing or of a corner of the obstacle (a cuff's corner) is left out, none
            # is left as a short stub, and (``phase``) no hatch line ends on a groove line within
            # reach of that line's landing (a knot)
            Js = []
            for L in ("a", "b"):
                for g in rays[L]:
                    gc = np.asarray(g.coords)
                    gc = gc if gc[0][1] < gc[-1][1] else gc[::-1]
                    J = _first_hit(gc, obs)
                    if J is not None:
                        Js.append((L, J))
                        break
            spots = [J for _, J in Js] + [np.asarray(cq) for cq in r.get("corners", ())]
            reach = GAP_MARK + FINE / 2 + MEDIUM / 2 + 0.5
            keep, sc_ = [], []
            for h in hs:
                vis = h.difference(obs)
                if vis.is_empty:
                    continue
                if vis.length < 4.0 and not vis.equals(h):
                    continue
                hit = h.intersection(obs.boundary)
                hp = [np.asarray(g_.coords[0]) for g_ in getattr(hit, "geoms", [hit])] if not hit.is_empty else []
                if any(float(np.hypot(*(q - sp))) < reach for q in hp for sp in spots):
                    continue
                # an end short of the obstacle but within §I.12's 3 px (ink) of it: left out too
                ds_ = [obs.distance(Point(*e)) for e in np.asarray(h.coords)[[0, -1]]]
                if any(0.3 < d_ < GAP_MARK + FINE / 2 + MEDIUM / 2 for d_ in ds_):
                    continue
                keep.append(h)
                # (the phase: the fewer lines left out near the landings, the better)
                sc_.append(0.0)
            if r.get("phase"):
                soft.append(-0.5 * (len([h for h in hs if not h.difference(obs).is_empty]) - len(keep)))
            hs = keep
        elif kind == "merge":
            # the line ``r['line']`` ('a'|'b') runs up along the obstacle's edge: above its last
            # crossing still ``need`` clear, it goes and the hatch runs on to the obstacle
            L = r["line"]
            cr = [(h, _end_on(h, rays[L])) for h in hs]
            cr = sorted([(h, e) for h, e in cr if e is not None], key=lambda t: -t[1][1])
            keep = None
            for h, e in cr:
                if obs.distance(Point(*e)) < need:
                    break
                keep = (h, e)
            if keep is None or keep is cr[-1]:
                continue
            h, E = keep
            c = np.asarray(h.coords)
            other = c[0] if np.hypot(*(c[0] - E)) > np.hypot(*(c[-1] - E)) else c[-1]
            dh = (E - other) / (np.hypot(*(E - other)) + 1e-9)          # along the hatch, away from the band
            gc = np.asarray(rays[L][0].coords)
            ur = gc[0] - gc[-1] if gc[0][1] < gc[-1][1] else gc[-1] - gc[0]
            ur = ur / (np.hypot(*ur) + 1e-9)                              # up the line
            Lx = 400.0
            ext = Polygon([tuple(E), tuple(E + dh * Lx), tuple(E + dh * Lx + ur * Lx), tuple(E + ur * Lx)]).buffer(0)
            # (only just under the obstacle's edge: the scene hides the rest anyway)
            ext = ext.intersection(zone).difference(obs.buffer(-2.0)).intersection(
                LineString(gc).buffer(need + 4.0))
            band = band.union(ext)
            hs = [h_ for h_ in _hatch_set(band, ang, origin=origin)]
            rays[L] = _cut_at(rays[L], E, keep="below")
        elif kind == "top":
            # the groove starts on its first hatch line wholly clear of the obstacle above (and
            # whose ends on the groove's lines stand clear of ``ray_obstacle`` too)
            ro = K.R(r["ray_obstacle"]) if r.get("ray_obstacle") is not None else None
            hs = sorted(hs, key=off)
            # (below the LOWEST line that comes near the obstacle: nothing of the groove above it)
            near_i = [i for i, h in enumerate(hs) if h.distance(obs) < need]
            start = near_i[-1] + 1 if near_i else 0
            first = None
            for h in hs[start:]:
                ends = [e for e in (_end_on(h, rays["a"]), _end_on(h, rays["b"])) if e is not None]
                if ro is not None and any(ro.distance(Point(*e)) < float(r.get("ray_need", need)) for e in ends):
                    continue
                # a groove line still running on above this hatch line must end ON it (a corner, never
                # a free end)
                if any(_end_on(h, rays[L]) is None and any(g.bounds[1] < h.bounds[1] for g in rays[L])
                       for L in ("a", "b")):
                    continue
                first = h
                break
            if first is None:
                continue
            hs = [h for h in hs if off(h) >= off(first) - 0.1]
            for L in ("a", "b"):
                e = _end_on(first, rays[L])
                if e is not None:
                    rays[L] = _cut_at(rays[L], e, keep="below")
                else:
                    rays[L] = [g for g in rays[L] if g.bounds[1] >= first.bounds[1] - 0.5]
        elif kind in ("both", "cut"):
            # the groove ends on its last hatch line clear of the obstacle below: 'both' = the
            # whole line and both groove lines stop there; 'cut' = only line ``r['line']`` (the one
            # meeting the obstacle almost parallel) stops, the hatch line runs on to the obstacle
            hs = sorted(hs, key=off)
            last = None
            for h in hs:
                # (lines near the obstacle ABOVE the groove's clear run — the yoke seam at its
                # top, when the obstacle is the whole seam — are passed over)
                if kind == "both":
                    ok = h.distance(obs) >= need
                else:
                    e = _end_on(h, rays[r["line"]])
                    if e is None:
                        continue
                    ok = obs.distance(Point(*e)) >= need
                if ok:
                    last = h
                elif last is not None:
                    break
            if last is None:
                continue
            hs = [h for h in hs if off(h) <= off(last) + 0.1]
            for L in (("a", "b") if kind == "both" else (r["line"],)):
                e = _end_on(last, rays[L])
                if e is not None:
                    rays[L] = _cut_at(rays[L], e, keep="above")
            if kind == "cut" and not isinstance(obs, shapely.LineString) and r.get("phase"):
                # score: the closing line's landing on the obstacle and the other line's (and every
                # other hatch end on it) stay apart — no three-line knot on the contour
                Lo = "b" if r["line"] == "a" else "a"
                J = None
                for g in rays[Lo]:
                    gc = np.asarray(g.coords)
                    gc = gc if gc[0][1] < gc[-1][1] else gc[::-1]
                    J = _first_hit(gc, obs)
                    if J is not None:
                        break
                if J is not None:
                    c = np.asarray(last.coords)
                    E = _end_on(last, rays[r["line"]])
                    E = E if E is not None else c[0]
                    far = c[-1] if np.hypot(*(c[-1] - E)) > np.hypot(*(c[0] - E)) else c[0]
                    Hh = _first_hit(np.vstack([E, far]), obs)
                    sc_ = []
                    if Hh is not None:
                        sc_.append(float(np.hypot(*(Hh - J))) - (GAP_MARK + FINE + 0.5))
                    # every hatch end short of the obstacle stands §I.12's 3 px (ink) off it
                    for h in hs:
                        for e in np.asarray(h.coords)[[0, -1]]:
                            d_ = obs.distance(Point(*e))
                            if d_ > 0.3:
                                sc_.append(min(d_ - (GAP_MARK + FINE / 2 + MEDIUM / 2), 0.0))
                    hard.append(min(sc_) if sc_ else 0.0)
    score = 10.0 * sum(min(x, 0.0) for x in hard) + sum(soft) + 0.01 * (min(hard) if hard else 0.0)
    return score, rays["a"], rays["b"], hs


def strata_fluting(zone, *, vy=-400.0, y_ref=511.0, widths=(19.0, 12.0), centre=19.0, hatched="thin",
                   angle=45.0, x_span=300.0, forks=None, w=FINE, skip=(), shift=None, side_skip=None,
                   rules=()) -> C.Frag:
    """Buttress fluting as VERTICAL strata (the K♠ mantle's §G.11 courses
    stood on end): bands alternating ``widths`` px at ``y_ref`` on rays from
    (AX, vy), so every flute widens downward; the thin bands (the grooves)
    hatched at 45° (mirrored on the right half), the broad ones (the ridges)
    plain. Mirror-symmetric about the axis. ``skip``: groove bounds (their
    distance from the axis at ``y_ref``) left out on both sides, with the
    hatch of any groove they bound; ``side_skip`` {side: (bounds …)} the
    same on one side only (side −1 = viewer's left); ``shift`` {bound: dX}
    moves a bound on both sides.

    ``rules`` fit a groove to what stands in front of the robe, so the
    scene's clip and heal have nothing to repair — each a dict with
    ``side``, ``groove`` (its inner bound), ``mode``, ``obstacle`` (a region,
    or 'seam' = the zone's edge) and ``need`` (px, centre line to the
    obstacle; default 6.8 = §I.12's 4.2 between a FINE and a MEDIUM line),
    applied in order:

    * 'fit': the groove's 45° hatch lies parallel to the obstacle's edge
      (the left sleeve): a line closer than ``need`` is left out whole (no
      cut tick), and with ``phase`` the phase puts the last line one
      pitch off the edge — the groove hatched right down to it;
    * 'merge' (``line`` 'a' inner | 'b' outer): that groove line runs up
      along the obstacle's edge (the stole): above its last hatch crossing
      still ``need`` clear it goes, and the hatch there runs on under the
      obstacle — the groove opens onto the stole instead of pinching a
      sliver of jade against it;
    * 'top': the groove starts on its first hatch line wholly ``need``
      clear of the obstacle (the collar's end link, whose comb ticks reach
      its edge: a groove line or hatch ending there leaves a stub or eats a
      tick) and whose ends stand clear of ``ray_obstacle``;
    * 'both': the groove ends on its last hatch line wholly clear of the
      obstacle below, both lines stopping there;
    * 'cut' (``line``): the groove ends on its last hatch line whose end on
      ``line`` stands ``need`` clear of the obstacle; that line stops there
      and the hatch line runs on to the obstacle — a groove line meeting a
      contour almost parallel (the border seam, the back of a hand) closes
      on a 45° line instead of a sliver of jade. With ``phase`` the hatch
      phase keeps that closing line's landing and every hatch end on the
      other line clear of the other line's own landing (no knot).
    → Frag of FINE Aquifer lines."""
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
    skip_ = [float(v) for v in skip]
    gone = lambda v, extra=(): any(abs(v - q) < 0.5 for q in list(skip_) + list(extra))
    bounds = [X for X in bounds if not gone(X)]
    grooves = [(a, b) for (a, b) in grooves if not (gone(a) or gone(b))]
    mv = lambda v: v + (_key(v, shift) or 0.0)
    bounds = [mv(X) for X in bounds]
    grooves = [(mv(a), mv(b)) for (a, b) in grooves]
    hatch_all = []
    for sg in (-1, 1):
        extra = [float(q) for q in (side_skip or {}).get(sg, ())]
        rays = {}
        for X in bounds:
            if gone(X, extra):
                continue
            pts = np.column_stack([[ray_x(AX + sg * X, y) for y in ys], ys])
            rays[X] = [g for g in K._lines_of(LineString(pts).intersection(zone)) if g.length > 6]
        ang = -angle if sg < 0 else -(180.0 - angle)
        a_ = math.radians(ang)
        v = np.array([-math.sin(a_), math.cos(a_)])        # the hatch's step direction
        v = v if v[1] > 0 else -v                          # … pointing down the robe
        hatch = []
        for (a, b) in grooves:
            if gone(a, extra) or gone(b, extra) or not hatched:
                continue
            band = Polygon([(ray_x(AX + sg * a, 150.0), 150.0), (ray_x(AX + sg * b, 150.0), 150.0),
                            (ray_x(AX + sg * b, 600.0), 600.0), (ray_x(AX + sg * a, 600.0), 600.0)]).buffer(0)
            band = band.intersection(zone)
            if band.is_empty:
                continue
            rs = [r for r in rules if r["side"] == sg and abs(float(r["groove"]) - a) < 0.5]
            if not rs:
                hatch += _hatch_set(band, ang)
                continue
            o0 = np.asarray(band.representative_point().coords[0])
            phases = np.arange(0.0, K.PITCH, 0.25) if any(r.get("phase") for r in rs) else [0.0]
            best = None
            for ph in phases:
                res = _groove(band, zone, rays[a], rays[b], rs, ang, v, tuple(o0 + v * ph))
                if best is None or res[0] > best[0] + 1e-6:
                    best = res
            rays[a], rays[b] = best[1], best[2]
            hatch += best[3]
        for X, gs in rays.items():
            for g in gs:
                f += K.line(np.asarray(g.coords), w, role="flute")
        hatch_all += hatch
    # all the flutes first, then all the hatch: the flutes of both sides print in one path with
    # the seam before them, so a flute that ends on the seam is one piece with it (§I.12 pieces)
    if hatch_all:
        f += C.stroke([np.asarray(h.coords) for h in hatch_all], FINE, style="hatch", role="hatch")
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
          spray_len=48.0, spray_angle=35.0, spray_sag=3.0, tick=10.0, cones=True, cone_d=8.4, hide=None,
          keep_frac=0.8) -> K.Part:
    """One side of the stole (left; ``side`` +1 mirrors): a broad red band
    coming over the shoulder from behind the neck and hanging straight between
    ``x_out`` and ``x_in``. Knocked out of the red (paper, MEDIUM ≥ 2.5 px,
    gaps ≥ 3): a piping line ``piping`` px inside the long edge(s)
    (``piping_sides`` 'both' | 'outer' | 'inner'), and down the middle a
    column of cypress sprigs — §G.18 comb sprays tilted with the tip up and
    out, each carrying its round cone (a knocked-out bead) at the tip.

    ``hide``: the region of things that will stand in front of this side
    (before any mirroring: the viewer's-left stole behind the cone and the
    cone hand). A sprig is kept whole or not at all: one that would show
    less than ``keep_frac`` of itself past ``hide`` is dropped, so no lone
    tick or cone bead peeps out beside the orb or a finger."""
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
        sp = spray_ko(base, tip, tick=tick, sag=spray_sag)
        if cones:
            u = (tip - base) / np.hypot(*(tip - base))
            sp += K.dot(tip + u * (cone_d / 2 + 1.0), cone_d, role="cone")
        if hide is not None:
            ink = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in K.clip_in(sp, body).marks])
            vis = ink.difference(K.R(hide).buffer(MEDIUM / 2 + GAP_MARK))
            if ink.area > 0 and vis.area < keep_frac * ink.area:
                continue
        ko_t += sp
    ko += K.clip_in(ko_t, body)
    fill_d = C.knockout(K.D(reg), ko)
    part = K.Part(reg, K.fill(fill_d, RED), K.outline(reg), {"x": (x_out, x_in), "body": body})
    return part.mirrored(AX) if side > 0 else part


# =============================================================================
# plain pockets
# =============================================================================
def sleeve_pocket(spec, meta, far_x, *, y_bot=530.0, into=10.0, up=4.0) -> Polygon:
    """The robe ground on the OUTER side of a kit forearm sleeve (the side
    toward the axis for the viewer's-left arm, toward the staff for the
    viewer's-right one: the sleeve's −n side), from the cuff down past the band
    and across to ``far_x`` (a line hidden under the stole or the staff). The
    left boundary is the sleeve's outer chord pushed ``into`` px into the
    sleeve, so the sagged edge is always inside; the sleeve itself covers the
    rest. → Polygon (subtract nothing: everything but the pocket is in front)."""
    W, u, n = P(meta["W"]), P(meta["u"]), P(meta["n"])
    B = P(spec["base"])
    wr = W - n * (spec["wrist_w"] / 2 - into) + u * up
    br = B - n * (spec["width"] / 2 - into)
    d = br - wr
    t = (y_bot - wr[1]) / d[1] if abs(d[1]) > 1e-6 else 1.0
    bot = wr + d * t
    return Polygon([tuple(wr), (far_x, wr[1]), (far_x, y_bot), tuple(bot)]).buffer(0)


def plain_pocket(part: K.Part, zone, roles=("flute", "hatch")) -> K.Part:
    """``part`` (the robe) with its pattern lines (``roles``) removed from
    ``zone``: a narrow wedge of ground left between a forearm and the thing
    beside it (the staff's halo, the stole) stays plain jade. Flutes and hatch
    that ran down such a wedge forked off the sleeve's contour at a shallow
    angle and ran within 4.2 px of it (a tangency), and a hatch groove left a
    lone tick. The outline and the seam are kept."""
    keep = C.Frag([m for m in part.lines.marks if m.role.split("@")[0] not in roles], part.lines.meta)
    pat = C.Frag([m for m in part.lines.marks if m.role.split("@")[0] in roles], part.lines.meta)
    pat = K.clip_out(pat, K.R(zone), eps=0.0)
    return K.Part(part.shape, part.fills, keep + pat, part.meta)


def tuck_ends(part: K.Part, halo, *, roles=("seam",), w=FINE) -> C.Frag:
    """Short stubs that carry ``part``'s ``roles`` lines (the robe's seam) on
    into a paper ``halo`` by half their width: the scene stops a line behind
    a haloed object a cap's width short of the halo, so the cap only touches
    the paper; where the line meets the halo's edge at a slant the cap then
    stands clear of it on one side (a free round end in the jade). Each end
    that stops there gets a stub centring its cap ON the edge (the end
    'tucked under the halo'). Add the Frag in front of the haloed object."""
    halo = K.R(halo)
    f = C.Frag()
    lines = [ln for m in part.lines.marks if m.kind != "fill" and m.role.split("@")[0] in roles
             for ln in K._stroke_lines(m.d)]
    if not lines:
        return f
    cut = shapely.union_all(lines).difference(halo.buffer(w / 2, quad_segs=12))
    for g in K._lines_of(cut):
        c = np.asarray(g.coords)
        for p, q in ((c[0], c[min(3, len(c) - 1)]), (c[-1], c[max(-4, -len(c))])):
            d = halo.distance(Point(*p))
            if abs(d - w / 2) > 0.15:
                continue
            u = p - q
            n = float(np.hypot(*u))
            if n < 1e-6:
                continue
            u = u / n
            f += K.line(np.vstack([p - u * 0.6, p + u * (w / 2)]), w, role="seam")
    return f
