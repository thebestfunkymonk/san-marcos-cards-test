"""Endemic creatures — creative brief §G.15, §G.25, §H.2/§H.20 (seal).

* :func:`gill_plume`        §G.15 a curved spine with 6–8 barbs on one side,
                            shortening toward the tip, which ends in a Ø4.2 dot.
* :func:`fountain_darter`   §G.25 *Etheostoma fonticola*: slender 6 : 1 body, a
                            fanned first dorsal (9 spines, scalloped membrane arcs),
                            a stitch line of 7 px dashes / 4 px gaps along the flank,
                            8 short saddle bars across the back, a round eye with a dot.
                            Faces right (``facing=+1``) or left (−1).
* :func:`blind_salamander`  *Eurycea rathbuni* for the seal: curled in a single C
                            (dorsal view), flat spatulate snout, two vestigial dot eyes,
                            three feathery gills per side, long thin limbs, finned
                            tapering tail.

All creatures are built at FINAL size (``length`` sets the geometry; stroke
widths never scale) from tangent circular arcs (:func:`forms.biarc_chain`) and
straight lines, and return a Frag (line mode / knockout mode as usual).
Species references: research/refs/smtx/fountain_darter.jpg,
blind_salamander.jpg; san-marcos.md §2.2, §2.4.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from inkkit import geom as G

from deck import tokens as T
import shapely
import shapely.affinity

from .core import (MIN_CLEAR, Frag, cut, dashes, dot, hatch, occlude, polyline_d, sample_d, stroke, terminal)
from .forms import arc_path, arc_spline, biarc, biarc_chain, scallop_arc, unit

__all__ = ["gill_plume", "fountain_darter", "blind_salamander", "DARTER"]

FINE, HAIR = T.FINE, T.HAIRLINE


def _warn(f: Frag, msg: str) -> Frag:
    f.meta.setdefault("warnings", []).append(msg)
    return f


def _pts(path) -> np.ndarray:
    if isinstance(path, str):
        return sample_d(path, 0.25)[0][0]
    return np.asarray(path, float)


# =============================================================================
# §G.15 gill plume
# =============================================================================
def gill_plume(path, *, n: int = 7, barb: tuple[float, float] = (11.0, 4.5), angle: float = 52.0,
               side: int = 1, start: float = 0.12, end: float = 0.1, curve: float = 0.18,
               tip_dot: float = 4.2, w: float = FINE, color: str = T.RED,
               layer: str | None = None) -> Frag:
    """§G.15 a gill plume on the spine ``path`` (base → tip): ``n`` (6–8)
    barbs on ONE side (``side`` +1 = left of travel), swept ``angle``°
    forward toward the tip, their lengths shortening linearly from
    ``barb[0]`` to ``barb[1]``; the tip ends in a Ø4.2 dot. Barbs are gentle
    arcs (sagitta ``curve`` × length) bowing toward the tip, like a feather's
    barbs. Barb stations run from ``start`` to 1 − ``end`` of the spine.
    Printed in Gill Red on faces (default colour)."""
    P = _pts(path)
    cv = G.Curve(P)
    L = cv.length
    f = stroke(polyline_d(P), w, color=color, layer=layer, role="spine")
    s0, s1 = start * L, (1 - end) * L - tip_dot
    sa = math.sin(math.radians(angle))
    pitch = (s1 - s0) / max(n - 1, 1)
    if pitch * sa < w + MIN_CLEAR - 1e-6:
        _warn(f, f"gill_plume: barb spacing {pitch * sa:.1f} < 6.3 (spine too short for {n} barbs)")
    for k in range(n):
        s = s0 + k * pitch
        t = k / max(n - 1, 1)
        ln = barb[0] + (barb[1] - barb[0]) * t
        p = cv.at_s(s)
        td = cv.tangent_s(s)
        a = math.degrees(math.atan2(td[1], td[0])) - side * (180 - angle)
        # barb leaves the spine pointing back-and-out, i.e. its free end is
        # toward the base? No — plume barbs sweep FORWARD: direction = tangent
        # rotated away from the spine by `angle`.
        a = math.degrees(math.atan2(td[1], td[0])) - side * angle
        q = p + unit(a) * ln
        if curve:
            d = f"M{p[0]:.3f} {p[1]:.3f}" + scallop_arc(p, q, side * curve * ln, move=False)
        else:
            d = polyline_d([p, q])
        f += stroke(d, w, color=color, layer=layer, role="barb")
    tp = cv.at_s(L)
    f += dot(tp[0], tp[1], tip_dot, color=color, layer=layer, role="tip")
    return f


# =============================================================================
# §G.25 fountain darter
# =============================================================================
# Design table at L = 100 (tail end x = 0, snout x = 100, axis y = 0, facing +x,
# dorsal toward −y). Positions scale with length; stroke widths never do.
# Body depth 16.7 = L / 6 (§G.25 "length : depth 6 : 1").
DARTER = dict(
    ventral=[(19.0, 3.7), (30.0, 4.7), (48.0, 6.6), (68.0, 7.7), (84.0, 7.5), (94.0, 5.9), (99.0, 3.1)],
    nose=(100.0, 0.4),
    # a blunt, rounded head, deep enough to hold the eye ring clear of both contours
    dorsal=[(97.3, -5.4), (91.0, -8.7), (80.0, -9.2), (64.0, -8.7), (44.0, -6.8), (27.0, -4.4), (19.0, -3.7)],
    caudal=dict(top=(3.6, -8.4), bot=(3.6, 8.4), rear_bulge=-3.4, edge_bow=0.9),
    fin_base_bow=1.4,
    # first dorsal (§G.25 "fanned, 9 spines with scalloped membrane arcs"): the spines spring
    # from a BASE LINE on the back (x0 → x1, never one pivot), fanning from ``lean0`` (front,
    # leaning forward) to ``lean1`` (rear, raking back); ``lens`` = spine lengths front → rear
    # (a rounded fin); the membrane is a run of shallow CONVEX arcs between the tips
    # (``scallop`` px outward: a fin, not a crown).
    d1=dict(x0=76.5, x1=44.0, n=9, lean0=-74.0, lean1=-134.0, scallop=1.3,
            lens=(8.6, 10.6, 11.7, 12.3, 12.3, 11.9, 11.1, 10.0, 8.6)),
    # soft dorsal: long and low, highest at the front; anal fin small, set back
    d2=dict(pts=[(40.0, 0.0), (36.0, -5.4), (27.0, -4.6), (21.5, 0.0)]),
    anal=dict(pts=[(33.0, 0.0), (29.0, 4.2), (23.5, 0.0)]),
    gill=dict(top=81.8, bot=80.6, mid=(77.4, 0.8)),
    # the eye: a ring (centreline radius r) with the Ø``dot`` pupil set forward, overlapping the
    # ring's inner edge by 0.4 px (one clean shape, no hairline sliver), so a crescent of
    # ground shows behind it — the "round eye with a dot" (§G.25). Rings shrink never; at
    # L >= 150 the pupil is centred with >= 3 px of ground all round when the head allows.
    eye=dict(c=(88.4, -0.9), r=4.2, dot=4.2),
    mouth=((99.2, 2.6), (95.2, 3.4)),
    # the stitch line runs the whole flank, from behind the gill cover to the caudal peduncle
    # (refs/smtx/fountain_darter.jpg: most prominent toward the rear)
    stitch=dict(y=1.6, x0=74.5, x1=21.0, on=7.0, off=4.0),
    # saddle bars: short bars hanging from the back, raked back, each stopping 3.0 px (the
    # §I.12 knockout minimum) above the stitch dashes: at L = 100 the body (16.7 px) cannot
    # hold saddle + 4.2 + stitch + 4.2 + belly, and behind x 40 the peduncle has no room at all
    saddles=dict(n=8, x0=77.5, x1=40.5, len=4.6, stitch_clear=3.0, rake=14.0),
)


def _contour_y(pts: np.ndarray, x: float, top: bool = True) -> float:
    """y of a dense contour polyline at x (the crossing on the top or bottom half)."""
    xs = pts[:, 0]
    idx = np.where((xs[:-1] - x) * (xs[1:] - x) <= 0)[0]
    ys = []
    for j in idx:
        a, b = pts[j], pts[j + 1]
        t = 0.0 if b[0] == a[0] else (x - a[0]) / (b[0] - a[0])
        ys.append(float(a[1] + (b[1] - a[1]) * t))
    if not ys:
        return float("nan")
    return min(ys) if top else max(ys)


def fountain_darter(x: float = 0.0, y: float = 0.0, length: float = 100.0, *, facing: int = 1,
                    rot: float = 0.0, stitch: bool = True, saddles: bool = True, fins: bool = True,
                    tail_hatch: bool = True, w: float = FINE, color: str = T.INK,
                    layer: str | None = None) -> Frag:
    """§G.25 a fountain darter, ``length`` px snout to tail, centred at
    (x, y), swimming toward +x (``facing`` = +1) or −x (−1), then rotated
    ``rot`` degrees about (x, y) (e.g. to follow an orbit; a C2 pair is
    ``d`` + ``d.rot180()``).

    Anatomy (refs/smtx/fountain_darter.jpg): blunt rounded snout, a large
    high eye (a ring with its pupil set forward, a crescent of ground
    behind it), gill-cover arc, a FANNED first dorsal of 9 spines springing
    from a base line along the back (each spine its own root, >= 2 px of
    ground between neighbours even at the base — no converging pivot) with a
    membrane of shallow convex arcs between the tips; low rounded second
    dorsal and anal fins; rounded caudal fin on a narrow peduncle, split on
    its axis with the upper half hatched (the Jinkins half-hatch). The
    STITCH LINE of 7 px dashes and 4 px gaps (butt caps, so the gaps stay
    true) runs the whole flank from behind the gill cover to the caudal
    peduncle; 8 short saddle bars hang from the back, raked like the spines,
    each stopping 3.0 px (the §I.12 knockout minimum) above the stitch.

    Designed at L = 100 (the back's size, §H.19); every clearance grows
    with L. ``meta``: length, facing, eye (centre, ring radius)."""
    k = length / 100.0
    D = DARTER

    def P(p):
        return (p[0] * k, p[1] * k)

    f = Frag()
    # --- body outline: peduncle (below) → belly → rounded snout → back → peduncle (above)
    prof = [P(p) for p in D["ventral"]] + [P(D["nose"])] + [P(p) for p in D["dorsal"]]
    d_body, body_pts, _ = arc_spline(prof, headings={len(D["ventral"]): -90.0})
    pb, pt = prof[0], prof[-1]
    cd = D["caudal"]
    ct, cb = P(cd["top"]), P(cd["bot"])
    # caudal: gently concave top/bottom edges flaring from the peduncle, a
    # convex (rounded) rear edge
    tail_d = (scallop_arc(pt, ct, cd["edge_bow"] * k, move=False)
              + scallop_arc(ct, cb, cd["rear_bulge"] * k, move=False)
              + scallop_arc(cb, pb, cd["edge_bow"] * k, move=False))
    f += stroke(d_body + tail_d + "Z", w, color=color, layer=layer, role="outline")
    # fin base across the peduncle (bows toward the head)
    f += stroke(f"M{pt[0]:.3f} {pt[1]:.3f}" + scallop_arc(pt, pb, D["fin_base_bow"] * k, move=False),
                w, color=color, layer=layer, role="finbase")
    if tail_hatch:
        # split the caudal on its axis; hatch the upper half (§B.2 half-hatch)
        base_mid = (pt[0] - D["fin_base_bow"] * k, 0.0)
        rear_mid = (ct[0] + cd["rear_bulge"] * k, 0.0)
        f += stroke(polyline_d([base_mid, rear_mid]), w, color=color, layer=layer, role="ray")
        tail_poly = Polygon(sample_d(f"M{pt[0]:.3f} {pt[1]:.3f}" + tail_d
                                     + scallop_arc(pb, pt, -D["fin_base_bow"] * k, move=False), 0.25)[0][0])
        upper = tail_poly.intersection(Polygon([(-50, 0), (200, 0), (200, -200), (-50, -200)]))
        f += hatch(upper, 90.0, color=color, layer=layer)
    # --- head: gill-cover arc, mouth, eye
    gd = D["gill"]
    g0 = (gd["top"] * k, _contour_y(body_pts, gd["top"] * k, True))
    g2 = (gd["bot"] * k, _contour_y(body_pts, gd["bot"] * k, False))
    gm = P(gd["mid"])
    d_g, gp, _ = arc_spline([g0, gm, g2])
    f += stroke(d_g, w, color=color, layer=layer, role="gill")
    f += stroke(polyline_d([P(D["mouth"][0]), P(D["mouth"][1])]), w, color=color, layer=layer, role="mouth")
    ec = np.array(P(D["eye"]["c"]))
    er = D["eye"]["r"] * max(1.0, k)
    pd = D["eye"]["dot"]
    f += stroke(G.circle_d(ec[0], ec[1], er), w, color=color, layer=layer, role="eye")
    hole = er - w / 2
    if hole - pd / 2 >= 3.0:
        pc = ec                                   # big enough: pupil centred, >= 3 px of ground all round
    else:
        # the pupil sits forward, overlapping the ring's inner edge by 0.4 px (one clean
        # shape, no sliver): a crescent of ground (up to 2·hole − pd wide) shows behind it
        pc = ec + np.array([hole - pd / 2 + 0.4, 0.0])
    f += dot(pc[0], pc[1], pd, color=color, layer=layer, role="pupil")
    # --- fins
    if fins:
        d1 = D["d1"]
        n = d1["n"]
        xs = np.linspace(d1["x0"] * k, d1["x1"] * k, n)
        leans = np.linspace(d1["lean0"], d1["lean1"], n)
        lens = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(d1["lens"])), d1["lens"]) * k
        tips, rays = [], []
        for xx, a, ln in zip(xs, leans, lens):
            base = np.array([xx, _contour_y(body_pts, xx, True)])     # on the back's centreline (T-junction)
            tip = base + unit(a) * ln
            tips.append(tip)
            rays.append(polyline_d([base, tip]))
        f += stroke("".join(rays), w, style="point", color=color, layer=layer, role="spine")
        # membrane: convex arcs between the tips (front → rear, bulging away from the body)
        memb = f"M{tips[0][0]:.3f} {tips[0][1]:.3f}" + "".join(
            scallop_arc(tips[i], tips[i + 1], -d1["scallop"] * k, move=False) for i in range(len(tips) - 1))
        f += stroke(memb, w, style="point", color=color, layer=layer, role="membrane")
        # soft (second) dorsal and anal fins: arcs standing on the contours
        # (points give x and the height above/below the contour there)
        for key, top in (("d2", True), ("anal", False)):
            pts = []
            for px, dh in D[key]["pts"]:
                yy = _contour_y(body_pts, px * k, top)
                pts.append((px * k, yy + dh * k))
            d_fin, _, _ = arc_spline(pts)
            f += stroke(d_fin, w, color=color, layer=layer, role="fin")
    # --- stitch line (7 on / 4 off, butt caps) and saddle bars
    st = D["stitch"]
    sy = st["y"] * k
    pieces = []
    if stitch:
        line = np.array([[st["x0"] * k, sy], [st["x1"] * k, sy]])
        pieces = dashes(line, st["on"], st["off"], min_len=3.0)
        f += stroke(pieces, w, style="rule", color=color, layer=layer, role="stitch")
    if saddles:
        sd = D["saddles"]
        xs = np.linspace(sd["x0"] * k, sd["x1"] * k, sd["n"])
        bars = []
        rk = math.radians(sd.get("rake", 0.0))
        for xx in xs:
            yt = _contour_y(body_pts, xx, True)
            yb = _contour_y(body_pts, xx, False)
            over_stitch = stitch and st["x1"] * k - 2 <= xx <= st["x0"] * k + 2
            if over_stitch:
                room = (sy - yt) - w - sd["stitch_clear"]
            else:
                room = (yb - yt) / 2 - w / 2
            ln = min(sd["len"] * max(1.0, k), room)
            if ln < 2.2:
                continue
            # raked back (toward the tail) like the spines: never a ruler of plumb ticks
            q = (xx - ln * math.tan(rk), yt + ln)
            bars.append(polyline_d([(xx, yt), q]))
        if bars:
            f += stroke("".join(bars), w, style="rule", color=color, layer=layer, role="saddle")
        if len(bars) < sd["n"]:
            _warn(f, f"fountain_darter: only {len(bars)} saddle bars fit at length {length}")
    # centre on (x, y): the design box spans x 0..L
    f = f.translate(-length / 2, 0)
    eye_c = (ec[0] - length / 2, ec[1])
    if facing < 0:
        f = f.mirror_x(0.0)
    if rot:
        f = f.rotate(rot, 0.0, 0.0)
    f = f.translate(x, y)
    f.meta.update(length=length, facing=facing, eye=(eye_c, er))
    return f


def _lines(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    out = []
    for p in getattr(g, "geoms", []):
        out += _lines(p)
    return out


# =============================================================================
# Texas blind salamander (seal; Q♠ mirror)
# =============================================================================
# Design (dorsal view) along a spine of arc length L (snout s = 0 → tail tip s = L),
# as fractions of L. Half-widths in px at L = 300 (the seal); every length and
# width scales LINEARLY with L (k = L / 300), with floors that keep the smallest
# figure (≈ Ø100, the Q♠ mirror) legible — strokes never scale.
SALAMANDER = dict(
    # a broad, flat head with a long spatulate snout (rounded spoon tip), a slim neck,
    # a slender trunk, a long tapering tail (refs/smtx/blind_salamander.jpg)
    hw=[(0.000, 0.0), (0.004, 4.6), (0.016, 7.6), (0.045, 8.8), (0.080, 10.6), (0.110, 10.2),
        (0.140, 7.4), (0.185, 8.6), (0.300, 10.2), (0.460, 9.8), (0.520, 8.8), (0.620, 7.0),
        (0.800, 4.0), (0.930, 1.5), (1.000, 0.0)],
    eyes=(0.062, 4.4),                        # (s, lateral offset): two dots under the skin
    # gills: three short bushy tufts a side (about half the head's width), rooted at three
    # separate stations behind the eyes, swept back from the outward normal toward the tail
    gills=dict(s=(0.100, 0.120, 0.140), sweep=(22.0, 44.0, 66.0), length=14.0, width=8.4, bend=18.0,
               inner_sweep=0.45),
    # limbs (long, spindly jointed tubes splayed from the flanks; the inner pair on the
    # C's concave side lies along the curl): (s, up, down, a_up, a_dn, toes, toe) —
    # a_up / a_dn: angles from the outward normal toward the head (+) or tail (−)
    # ``inner`` = (a_up, a_dn) for the limb on the C's concave side: it lies back along the curl,
    # clear of the head and gills
    fore=(0.235, dict(up=19.0, down=16.0, a_up=26.0, a_dn=62.0, toes=4, toe=6.5, inner=(-22.0, 12.0))),
    hind=(0.505, dict(up=21.0, down=18.0, a_up=-14.0, a_dn=-58.0, toes=5, toe=7.0, inner=(-14.0, -58.0))),
    limb_hw=3.1,
    grooves=(0.262, 0.47, 11),                # costal grooves: span and (maximum) count
    fin=(0.56, 5.0),                          # the tail's fin fold: starts at s, max width px
)


def _sal_hw(L: float):
    """Half-width along the spine: the table × k (linear), but the HEAD never
    smaller than 84 % of the seal's (a Ø4.2 eye dot a side needs ~9 px of
    half-width to sit clear inside it) — small figures get a broad head, as
    the blind salamander has anyway."""
    pts = SALAMANDER["hw"]
    xs = np.array([p[0] for p in pts]) * L
    k = L / 300.0
    ys = np.array([p[1] for p in pts]) * k
    head = np.array([p[1] for p in pts]) * max(k, 0.84)
    fr = np.array([p[0] for p in pts])
    wgt = np.clip((0.15 - fr) / 0.04, 0.0, 1.0)                    # head (s <= 0.11) → trunk (s >= 0.15)
    ys = np.maximum(ys, head * wgt)
    return lambda s: np.interp(np.asarray(s, float), xs, ys)


def blind_salamander(cx: float = 0.0, cy: float = 0.0, radius: float = 74.0, *, arc: float = 255.0,
                     head_deg: float = -50.0, tighten: float = 0.06, rot: float = 0.0, centre: bool = True,
                     w: float = FINE, color: str = T.FOIL, layer: str | None = None,
                     gill_color: str | None = None) -> Frag:
    """The Texas blind salamander (*Eurycea rathbuni*) curled in a single C,
    seen from above — the seal (§H.20: gold foil on Gill Red) and the Q♠
    scrying-mirror vision (§H.2, ≈ Ø100: ``radius`` ≈ 32).

    Accurate to refs/smtx/blind_salamander.jpg and san-marcos.md §2.2: a
    broad flat head with a long, flattened SPATULATE snout; the eyes only two
    small dots under the skin; three short, bushy external gills a side
    (feathery tufts about half the head's width, each a gently curved stalk
    with alternate barbs leaning to the tip and a Ø4.2 tip dot), rooted at
    three stations behind the eyes and swept back; long, spindly jointed
    limbs splayed from the flanks (4 front toes, 5 hind); costal grooves
    along each flank; a long tapering tail with its fin fold along the outer
    side.

    Body, limbs and feet are ONE silhouette contour (their union), so there
    is never a crossing among them; gill tufts that overlap interlace with
    4.2 px gaps; nothing crosses plainly (§I.13, checked by
    ``core.crossings``). Every size and count follows the spine length
    (linear scaling, legal floors): the groove count drops to what keeps
    4.2 px between grooves. ``gill_color`` (e.g. Gill Red on the Q♠) paints
    the gills alone. ``meta``: length, spine, silhouette, warnings.

    The spine is a spiral arc of ``arc`` degrees round (cx, cy) starting at
    ``head_deg`` (the snout) at ``radius`` and tightening by ``tighten`` ×
    radius toward the tail tip. ``rot`` turns the whole figure."""
    D = SALAMANDER
    n = 900
    th = np.radians(head_deg - np.linspace(0, arc, n))              # counter-clockwise on screen
    rr = radius * (1 - tighten * np.linspace(0, 1, n) ** 1.6)
    spine = np.column_stack([cx + rr * np.cos(th), cy + rr * np.sin(th)])
    cv = G.Curve(spine)
    L = cv.length
    k = L / 300.0
    hw = _sal_hw(L)
    warns: list[str] = []
    s = np.linspace(0, L, 1400)
    P = cv.at_s(s)
    N = cv.normal_s(s)                                                # left of travel
    H = hw(s)[:, None]
    body = Polygon(np.vstack([P + N * H, (P - N * H)[::-1]])).buffer(0)
    # the spatulate snout ends in a round spoon tip, never a wedge
    r_n = float(hw(0.016 * L))
    body = body.union(shapely.Point(*cv.at_s(r_n)).buffer(r_n, quad_segs=24)).buffer(0)

    def frame(frac):
        ss = frac * L
        p = cv.at_s(ss)
        t = cv.tangent_s(ss)
        nrm = np.array([t[1], -t[0]])
        return p, t, nrm, float(hw(ss))

    centre_pt = np.array([cx, cy])
    # --- limbs: jointed tubes unioned with the body (one contour), toes as strokes
    lhw = max(D["limb_hw"] * k, w + 0.9)                             # tube half-width (>= a visible interior)
    limb_polys, toes = [], []
    for key in ("fore", "hind"):
        frac, Lm = D[key]
        p, t, nrm, h = frame(frac)
        head_dir = -t
        for sg in (1, -1):
            out = sg * nrm
            inner = float(out @ (centre_pt - p)) > 0                  # this side faces the inside of the C
            sc = k * (0.86 if inner else 1.0)
            a_up, a_dn = Lm["inner"] if inner else (Lm["a_up"], Lm["a_dn"])

            def rotv(v, deg):
                a_ = math.radians(deg)
                return v * math.cos(a_) + head_dir * math.sin(a_)
            shoulder = p + out * (h * 0.5)
            elbow = p + out * h + rotv(out, a_up) * Lm["up"] * sc
            wrist = elbow + rotv(out, a_dn) * Lm["down"] * sc
            _, cl, _ = arc_spline([shoulder, elbow, wrist])
            limb_polys.append(LineString(cl).buffer(lhw, quad_segs=12, cap_style="round"))
            fwd = rotv(out, a_dn)
            base_ang = math.degrees(math.atan2(fwd[1], fwd[0]))
            nt = Lm["toes"]
            spread = 26.0 if nt == 4 else 22.0
            tl = max(Lm["toe"] * k, 2 * w + 1.0)
            for i in range(nt):
                ta = base_ang + (i - (nt - 1) / 2) * spread
                a0 = wrist + unit(ta) * (lhw - 0.2)
                toes.append(polyline_d([a0, wrist + unit(ta) * (lhw + tl)]))
    sil = shapely.union_all([body] + limb_polys).buffer(0)
    if sil.geom_type != "Polygon":
        sil = max(sil.geoms, key=lambda g: g.area)
    ext = np.asarray(sil.exterior.coords)
    f = stroke(polyline_d(ext, closed=True), w, color=color, layer=layer, role="outline")
    f += stroke("".join(toes), w, color=color, layer=layer, role="toe")
    # --- eyes: two dots under the skin
    p, t, nrm, h = frame(D["eyes"][0])
    for sg in (1, -1):
        e = p + nrm * sg * max(D["eyes"][1] * max(k, 0.84), 4.2)
        f += dot(e[0], e[1], 4.2, color=color, layer=layer, role="eye")
    # --- costal grooves: ticks inward from each flank, thinned to keep 4.2 px apart
    g0, g1, ng = D["grooves"]
    span = (g1 - g0) * L
    ng_fit = min(ng, int(span // (w + MIN_CLEAR)) + 1)
    if ng_fit < ng:
        warns.append(f"blind_salamander: {ng_fit} of {ng} costal grooves fit at spine length {L:.0f}")
    glen = max(4.6 * k, 2 * w)
    grooves = []
    for frac in np.linspace(g0, g1, ng_fit):
        p, t, nrm, h = frame(frac)
        if h - glen < w + MIN_CLEAR / 2:
            continue
        for sg in (1, -1):
            grooves.append(polyline_d([p + sg * nrm * h, p + sg * nrm * (h - glen)]))
    if grooves:
        # the grooves never run into a limb root
        gf = stroke("".join(grooves), w, style="rule", color=color, layer=layer, role="groove")
        f += occlude(gf, shapely.union_all(limb_polys).buffer(w / 2 + MIN_CLEAR))
    # --- tail fin fold along the OUTER (convex) side, from the outline to the tail tip
    f0, fmax = D["fin"]
    ss = np.linspace(f0 * L, L, 240)
    pts_f = []
    for s_ in ss:
        p_ = cv.at_s(s_)
        t_ = cv.tangent_s(s_)
        nrm_ = np.array([t_[1], -t_[0]])
        side_out = -1.0 if float(nrm_ @ (centre_pt - p_)) > 0 else 1.0
        u_ = min(max((s_ - f0 * L) / ((1 - f0) * L), 0.0), 1.0)
        fw = max(fmax * k, w + MIN_CLEAR) * math.sin(math.pi * min(u_ / 0.35, 1.0) / 2) * (1 - u_) ** 0.6
        pts_f.append(p_ + nrm_ * side_out * (float(hw(s_)) + fw))
    f += stroke(polyline_d(np.asarray(pts_f)), w, color=color, layer=layer, role="fin")
    # --- gills: three short bushy tufts a side, rooted ON the outline (T-junction)
    gd = D["gills"]
    gcol = gill_color or color
    gill_units = []
    for sg in (1, -1):
        for j, (gs, sw) in enumerate(zip(gd["s"], gd["sweep"])):
            p, t, nrm, h = frame(gs)
            out = sg * nrm
            tail_dir = t
            if float(out @ (centre_pt - p)) > 0:
                sw = sw * gd.get("inner_sweep", 1.0)                  # the concave side: the body curls toward them
            ang_v = out * math.cos(math.radians(sw)) + tail_dir * math.sin(math.radians(sw))
            h0 = math.degrees(math.atan2(ang_v[1], ang_v[0]))
            base = p + out * h
            glen_ = max(gd["length"] * k, 9.5)
            cr_ = float(out[0] * tail_dir[1] - out[1] * tail_dir[0])
            turn = gd["bend"] * (1 if cr_ > 0 else -1)               # curving on back toward the tail
            _, gp, _ = arc_path(base[0], base[1], h0 - turn / 2, [(glen_, turn)])
            gill_units.append(_gill_tuft(gp, gd, k, w=w, color=gcol, layer=layer))
    gills = Frag()
    front = None
    for gu in gill_units:                            # later tufts lie behind earlier ones (T-junction)
        gills += occlude(gu, front) if front is not None else gu
        reg = gu.meta["region"]
        front = reg if front is None else front.union(reg)
    from .core import drop_specks
    f += drop_specks(occlude(gills, sil), 3.0, roles=None)
    if centre:
        x0, y0, x1, y1 = f.bbox()
        dx, dy = cx - (x0 + x1) / 2, cy - (y0 + y1) / 2
        f = f.translate(dx, dy)
        sil = shapely.affinity.translate(sil, dx, dy)
        spine = spine + np.array([dx, dy])
    if rot:
        f = f.rotate(rot, cx, cy)
        sil = shapely.affinity.rotate(sil, rot, origin=(cx, cy))
    f.meta.update(length=L, spine=spine, silhouette=sil)
    if warns:
        f.meta["warnings"] = warns
    return f


def _gill_tuft(stalk, gd, k, *, w=FINE, color=T.RED, layer=None) -> Frag:
    """One external gill as a feathery TUFT: a closed lobe on the curved
    ``stalk`` (base → tip), widest at 60 % of its length, whose two edges
    are rows of small outward scallops meeting in a soft point — the fringe
    of filaments seen at small size (bushy, never antlers or hooked briars).
    One closed stroke, so neighbouring tufts occlude cleanly (T-junction) and
    nothing inside it can crowd. ``meta['region']`` is its filled outline."""
    from .forms import scallop_row
    cv = G.Curve(np.asarray(stalk, float))
    Lg = cv.length
    W = max(gd.get("width", 8.4) * k, 5.6)
    ss = np.linspace(0, Lg, 120)
    prof = np.sin(np.pi * np.clip(ss / (0.6 * Lg), 0, 1) / 2) * np.clip((Lg - ss) / (0.4 * Lg), 0, 1) ** 0.8
    hwv = (W / 2) * np.maximum(prof, 0.0)
    hwv[0] = 0.9 * W / 2                                           # the root is open-ish (hidden in the body)
    P = cv.at_s(ss)
    Nn = cv.normal_s(ss)
    left = P + Nn * hwv[:, None]
    right = P - Nn * hwv[:, None]
    n_sc = max(2, int(round(G.Curve(left).length / max(3.9, 3.9 * k))))
    pitch_l = G.Curve(left).length / n_sc
    sag = max(0.9, 0.22 * pitch_l)
    d_l, _, _ = scallop_row(left, pitch_l, sag, side=1)
    rr = right[::-1]
    pitch_r = G.Curve(rr).length / n_sc
    d_r, _, _ = scallop_row(rr, pitch_r, sag, side=-1)
    d = d_l + d_r.replace("M", "L", 1) + "Z"
    f = stroke(d, w, color=color, layer=layer, role="gill")
    f.meta["region"] = Polygon(np.vstack([left, rr])).buffer(sag + 0.2)
    return f
