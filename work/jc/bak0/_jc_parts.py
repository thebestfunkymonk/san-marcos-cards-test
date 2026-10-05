"""art/_jc_parts.py — J♣ · The River Squire: the parts the kit does not have.

Built only from deck.courtkit / deck.motifs primitives (compass arcs, G1 arc
splines, vesicas, legal strokes), at final size, in card px (top half).
Every builder returns a courtkit Part (shape, fills, lines, meta).
"""
from __future__ import annotations

import math
import re

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM

P = K.P
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR


# ---------------------------------------------------------------------------
# construction helpers
# ---------------------------------------------------------------------------
def spl(points, h0=None, h1=None, headings=None):
    """Open G1 arc spline through points (d with its M)."""
    return K.spline(points, h_start=h0, h_end=h1, headings=headings)


def _tail(d):
    """Strip the leading M of a path so it can continue another."""
    return re.sub(r"^M\s*[-\d.]+[ ,]\s*[-\d.]+", "", d.strip(), count=1)


def chain_d(*ds, close=True):
    """Join open path segments end to start (each starts where the last
    ended) into one path; closed with Z."""
    out = ds[0] + "".join(_tail(d) for d in ds[1:])
    return out + ("Z" if close else "")


def pts_of(d, step=0.4):
    return C.sample_d(d, step)[0][0]


def heading(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))


# ---------------------------------------------------------------------------
# the brimmed cap (jade): pointed peak forward (the turn), turned-up brim at
# the back carrying the Lion Mark badge and the heron plume
# ---------------------------------------------------------------------------
def cap(fc, *, tip=(301.0, 173.0), top=(390.0, 117.0), flap_tip=(467.0, 138.0), hatband=8.5):
    """The squire's brimmed cap (§H.9 'a jade brimmed cap'), 3/4 left: a
    soft crown; a brim that runs forward into a pointed peak over the brow
    (the turn) and turns up at the back into a pointed flap, where the heron
    plume is tucked. A gold hatband (the jack's crown-band) runs round the
    crown above the brim, split from it by the brim's MEDIUM seam.
    → Part (meta 'flap_tip', 'fold', 'back', 'band_top', 'hatband')."""
    a = fc.anchors
    T = P(tip)
    # the lower edge: the peak's tip, its root on the far temple, across the
    # forehead, to behind the near temple (above the ear)
    far = P(a["side_x"](188.0, -1) - 1.0, 188.5)
    back = P(a["side_x"](194.0, +1) + 8.0, 195.0)
    lower = spl([T, P(324.0, 184.0), far, P(374.0, 183.5), P(407.0, 184.5), back], h0=12.0, h1=35.0)
    # the turned-up brim at the back: its outer edge sweeps up from the band
    # to its point, its top edge runs back down into the crown (the fold)
    Ft = P(flap_tip)
    Fi = P(445.0, 151.0)
    flap_out = spl([back, P(459.0, 172.0), Ft], h0=-60.0, h1=-78.0)
    flap_in = spl([Ft, P(455.0, 148.0), Fi], h0=150.0, h1=178.0)
    crown = spl([Fi, P(441.0, 128.0), P(420.0, 115.0), P(top), P(358.0, 128.0), P(337.0, 153.0)], h0=-100.0)
    peak_top = spl([P(337.0, 153.0), P(318.0, 164.0), T], h1=165.0)
    d = chain_d(lower, flap_out, flap_in, crown, peak_top)
    shape = K.R(d).buffer(0)
    seam_pts = [P(322.0, 168.0), P(350.0, 172.0), P(378.0, 169.5), P(410.0, 170.5), P(436.0, 177.0), P(449.0, 184.0)]
    band_top = spl(seam_pts, h0=8.0)
    fold_d = spl([P(449.0, 184.0), P(448.0, 166.0), Fi], h0=-88.0)
    brim = K.R(chain_d(lower, flap_out, flap_in, K.spline([Fi, P(448.0, 166.0), P(449.0, 184.0)], h_end=92.0),
                       K.spline(seam_pts[::-1], h_end=188.0), spl([seam_pts[0], T]))).buffer(0)
    seam = K.clip_in(K.line(band_top, MEDIUM, role="cap-seam"), shape.buffer(-0.5))
    fold = K.clip_in(K.line(fold_d, MEDIUM, role="cap-fold"), shape.buffer(-0.5))
    lines = K.outline(shape) + seam + fold
    fills = K.fill(shape, JADE)
    hb = None
    if hatband:
        # the hatband: the strip between the seam and its parallel ``hatband`` px above
        sp = pts_of(band_top, 0.4)
        off = K.G.Curve(sp).offset(hatband, spacing=0.5)
        ring = np.vstack([sp, off[::-1]])
        hb = Polygon(ring).buffer(0).intersection(shape.buffer(-0.2)).difference(brim.buffer(0.01))
        hb = hb.intersection(K.box(0, 0, 446.0, 2000))
        fills += K.fill(hb, GOLD)
        up = K.G.Curve(sp).offset(hatband, spacing=0.5)
        lines += K.clip_in(K.line(C.polyline_d(up), MEDIUM, role="hatband"), shape.buffer(-0.5).difference(K.box(446.0, 0, 2000, 2000).buffer(0)))
    return K.Part(shape, fills, lines,
                  {"flap_tip": Ft, "fold": Fi, "back": back, "band_top": band_top, "hatband": hb})


# ---------------------------------------------------------------------------
# the heron plume (paper vane, Aquifer current lines, gold quill)
# ---------------------------------------------------------------------------
def plume(guide_pts, *, w_max=32.0, w_root=10.0, h0=None, h1=None, quill_to=0.70, stagger=10.0):
    """A heron's occipital plume on an S guide (root → tip): a paper vane
    that swells to ``w_max`` and tapers to a point; a GOLD quill (MEDIUM gold
    line, §C.1 'gold is line') along its centre from the root to
    ``quill_to`` of its length, ending in a gold Ø6.3 terminal; one current
    line (§G.24) either side of it, streaming on to Ø6.3 terminals.
    → Part (meta 'guide')."""
    gd = spl(guide_pts, h0=h0, h1=h1)
    g = pts_of(gd, 0.3)
    cv = K.G.Curve(g)
    L = cv.length
    s = np.linspace(0, L, 300)
    pts = cv.at_s(s)
    tang = np.array([cv.tangent_s(x) for x in s])
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])      # screen-left of travel
    t = s / L
    # half-width: root w_root, swelling to w_max at ~45 %, a long taper to the tip
    hw = np.where(t < 0.45, w_root / 2 + (w_max - w_root) / 2 * np.sin(t / 0.45 * np.pi / 2),
                  w_max / 2 * np.cos((t - 0.45) / 0.55 * np.pi / 2) ** 0.8)
    hw[-1] = 0.0
    left = pts + nrm * hw[:, None]
    right = pts - nrm * hw[:, None]
    ring = np.vstack([left, right[::-1][1:]])
    vane = Polygon(ring).buffer(1.5, join_style=1).buffer(-1.5, join_style=1).buffer(0)
    lines = K.outline(vane)
    qi = int(np.searchsorted(s, quill_to * L))
    quill = pts[:qi]
    lines += K.line(C.polyline_d(quill), MEDIUM, color=GOLD, role="quill")
    lines += K.dot(quill[-1], K.TD, color=GOLD, role="quill-end")
    placed = LineString(quill).buffer(MEDIUM / 2).union(Point(*quill[-1]).buffer(K.TD / 2))
    for sd in (+1, -1):
        off = MEDIUM / 2 + K.GAP + FINE / 2 + 0.2
        lines += K.current_lines(g, 1, vane, side=sd, first=off, edge=CONTOUR, stagger=stagger, placed=placed)
    return K.Part(vane, C.Frag(), lines, {"guide": g})


# ---------------------------------------------------------------------------
# the near ear (a paper C joined to the cheek, its inner curl)
# ---------------------------------------------------------------------------
def ear(fc, *, c=(431.0, 226.0), rx=8.5, ry=13.0):
    """The near ear of a 3/4 head: a paper ellipse overlapping the cheek
    contour; only its OUTER edge is drawn (it joins the cheek, no closed
    ring on the face), plus one MEDIUM inner fold (the helix) springing from
    the cheek — a C inside a C."""
    c = P(c)
    reg = shapely.affinity.scale(Point(*c).buffer(1.0, quad_segs=32), rx, ry)
    head = fc.skin
    outer = K.clip_out(K.outline(reg), head.buffer(-0.5), eps=0.0, trap=0.0)
    curl = K.line(K.arc_c(c + P(-0.5, 0.5), 5.2, -75.0, 70.0), MEDIUM, role="ear")
    return K.Part(reg, C.Frag(), outer + curl, {"c": c})


# ---------------------------------------------------------------------------
# the body: jade doublet (sleeve heads, upper arms), red jerkin over it
# ---------------------------------------------------------------------------
def rounded(poly, r):
    return poly.buffer(-r, join_style=1).buffer(r, join_style=1)


def doublet(*, neck=(381.0, 292.0), neck_hw=30.0, sh_l=(204.0, 332.0), sh_r=(558.0, 326.0),
            bot_l=180.0, bot_r=588.0, bottom=545.0):
    """The jade doublet: the whole bust silhouette — shoulders sloping from
    the collar to rounded shoulder points, the upper arms falling (slightly
    flared) to the band. Its jade shows at the shoulders and down the upper
    arms either side of the red jerkin."""
    nx, ny = neck
    L = spl([P(nx - neck_hw, ny), P(300.0, 303.0), P(242.0, 314.0), P(sh_l), P(188.0, 380.0), P(bot_l, bottom)],
            h0=170.0, h1=96.0)
    R = spl([P(bot_r, bottom), P(580.0, 380.0), P(sh_r), P(518.0, 308.0), P(462.0, 299.0), P(nx + neck_hw, ny)],
            h0=-84.0, h1=190.0)
    d = chain_d(L, f"M{bot_l} {bottom}L{bot_r} {bottom}", R)
    body = K.R(d).buffer(0)
    return K.Part(body, K.fill(body, JADE), K.outline(body), {})


def _side(curve_pts, side, far=2000.0):
    """Region on one side (−1 left / +1 right) of a roughly vertical curve."""
    c = np.asarray(curve_pts, float)
    top, bot = c[0], c[-1]
    xf = far if side > 0 else -far
    ring = np.vstack([c, [[bot[0], bot[1] + far]], [[xf, bot[1] + far]], [[xf, top[1] - far]], [[top[0], top[1] - far]]])
    return Polygon(ring).buffer(0)


def jerkin(doub_shape, *, arm_l=((270.0, 300.0), (258.0, 360.0), (253.0, 440.0), (252.0, 560.0)),
           arm_r=((492.0, 296.0), (505.0, 360.0), (511.0, 440.0), (513.0, 560.0)),
           neck=((316.0, 296.0), (344.0, 311.0), (372.0, 316.0), (402.0, 311.0), (432.0, 296.0))):
    """The red jerkin over the doublet: armholes curving down either side
    (the jade upper arms show), a round neckline under the collar. → Part
    (meta 'neck_pts', 'front')."""
    aL = pts_of(spl([P(p) for p in arm_l]))
    aR = pts_of(spl([P(p) for p in arm_r]))
    nk = pts_of(spl([P(p) for p in neck]))
    below = Polygon(np.vstack([[[nk[0][0] - 400, nk[0][1]]], nk, [[nk[-1][0] + 400, nk[-1][1]]],
                               [[nk[-1][0] + 400, 2000]], [[nk[0][0] - 400, 2000]]])).buffer(0)
    reg = doub_shape.intersection(_side(aL, +1)).intersection(_side(aR, -1)).intersection(below)
    reg = reg.buffer(0)
    return K.Part(reg, K.fill(reg, RED), K.outline(reg), {"neck_pts": nk})


# ---------------------------------------------------------------------------
# the canoe paddle, held upright like a halberd (blade up, §H.9)
# ---------------------------------------------------------------------------
def paddle(x=550.0, *, tip=90.0, blade_hw=28.0, widest=192.0, throat=252.0, shaft_hw=13.0, bottom=545.0,
           band=(194.0, 226.0), collar_h=15.0, collar_hw=18.5, hatch_side=+1):
    """A canoe paddle held upright like a halberd (§H.9): an ottertail blade
    (narrow rounded tip, widest low, a quick shoulder into the throat) on a
    gold loom. The blade is paper, split on its spine (MEDIUM) with ONE half
    hatched at 45° (§B.2) above a broad gold band across its widest part;
    below the band the throat is plain; a raised gold collar joins it to the
    loom. The spine stops at the band, so band and spine never make a cross.
    → Part (meta 'blade', 'shaft', 'band')."""
    right = [P(x, tip), P(x + blade_hw * 0.62, tip + 14.0), P(x + blade_hw * 0.93, tip + 52.0),
             P(x + blade_hw, widest), P(x + blade_hw * 0.70, throat - 22.0), P(x + shaft_hw, throat + 4.0)]
    dR = spl(right, h0=0.0, h1=100.0)
    left = [P(2 * x - p[0], p[1]) for p in right]
    dL = spl(left[::-1], h0=-100.0, h1=0.0)
    d = chain_d(dR, f"M{x + shaft_hw} {throat + 4.0}L{x - shaft_hw} {throat + 4.0}", dL)
    blade = K.R(d).buffer(0)
    by0 = throat - collar_h * 0.55
    collar = K.R(K.rrect(x - collar_hw, by0, x + collar_hw, by0 + collar_h, 3.2))
    shaft = K.box(x - shaft_hw, by0 + 2.0, x + shaft_hw, bottom)
    bandr = blade.intersection(K.box(0, band[0], 2000, band[1]))
    shape = K.U(blade, shaft, collar)
    spine_top = tip + 16.0
    spine = K.seg(P(x, spine_top), P(x, band[0] + 1.0), MEDIUM, role="spine")
    half = blade.intersection(K.box(x, 0, 2000, band[0]) if hatch_side > 0 else K.box(0, 0, x, band[0]))
    hatch = K.hatch_in(half.intersection(K.box(0, spine_top - 4.0, 2000, 2000)), angle=-45.0)
    fills = K.fill(K.U(shaft.difference(blade), collar, bandr), GOLD)
    band_lines = K.clip_in(K.outline(bandr), blade.buffer(-0.5))
    lines = (K.outline(shape) + K.clip_out(K.outline(blade), collar, eps=-0.5, trap=0.0) + K.outline(collar)
             + band_lines + spine + hatch)
    return K.Part(shape, fills, lines, {"blade": blade, "shaft": shaft, "band": bandr})


# ---------------------------------------------------------------------------
# pecan (Carya illinoinensis): the pinnate leaf sprig and the husk buckle
# ---------------------------------------------------------------------------
def pecan_sprig(base, heading_deg, *, length=70.0, pairs=4, leaf=(21.0, 5.4), spread=60.0, step=10.5,
                bend=8.0, w=MEDIUM):
    """A pecan pinnate leaf for knocking out of red (§H.9 'pecan pinnate
    leaves'): a gently curved rachis carrying ``pairs`` sub-opposite pairs of
    long, slightly sickle-shaped (falcate) leaflets swept toward the tip, the
    pairs shortening toward the tip, and one terminal leaflet — a compound
    leaf, never a laurel sprig. Returns an ink Frag (the caller knocks its
    union out of the red)."""
    b = P(base)
    # the rachis: one arc bending ``bend`` px to the screen-left of travel
    tip = b + K.unit(heading_deg) * (length - leaf[0])
    rd = K.arc_sag(b, tip, bend * 0.25)
    rp = pts_of(rd, 0.25)
    cv = K.G.Curve(rp)
    Lr = cv.length
    f = C.Frag()
    f += K.line(rd, w, role="rachis")
    for k in range(pairs):
        s = Lr - 3.0 - (pairs - k) * step
        if s < 4.0:
            continue
        p = cv.at_s(s)
        tg = cv.tangent_s(s)
        h = math.degrees(math.atan2(tg[1], tg[0]))
        ll = leaf[0] * (0.82 + 0.18 * (k + 1) / pairs) if False else leaf[0] * (1.0 - 0.06 * (pairs - 1 - k) * 0.0)
        ll = leaf[0] * (1.0 - 0.05 * k)
        for sg in (-1, 1):
            a = h + sg * spread
            q = p + K.unit(a) * ll
            mid = (p + q) / 2 + K.unit(a - sg * 90.0) * 1.6          # falcate: bowed toward the tip
            d = K.spline([p - K.unit(a) * 0.5, mid, q])
            f += K.fill(_leaf_region(d, leaf[1]), INK, role="leaflet")
    q = tip + K.unit(heading_deg) * leaf[0] * 1.05
    f += K.fill(K.vesica(tip - K.unit(heading_deg) * 3.0, q, leaf[1]), INK, role="leaflet")
    return f


def _leaf_region(mid_d, width):
    """A vesica-profile leaf round a (curved) midrib d."""
    from deck.motifs import forms as FM
    mid = pts_of(mid_d, 0.3)
    _, _, ring = FM.leaf_edges(mid, FM.vesica_hw(K.G.Curve(mid).length, width))
    return Polygon(ring).buffer(0)


def pecan_field(region, *, pitch=(50.0, 40.0), origin=(366.0, 330.0), heading=-62.0, margin=5.0, **kw):
    """Half-drop grid of pecan sprigs, each kept whole inside ``region``
    (inset ``margin``): the jerkin's woven pattern."""
    reg = K.R(region)
    inner = reg.buffer(-margin)
    x0, y0, x1, y1 = reg.bounds
    ox, oy = origin
    px, py = pitch
    f = C.Frag()
    j0 = int(math.floor((y0 - oy) / py)) - 1
    j1 = int(math.ceil((y1 - oy) / py)) + 1
    for j in range(j0, j1 + 1):
        off = px / 2 if j % 2 else 0.0
        for i in range(int(math.floor((x0 - ox - off) / px)) - 1, int(math.ceil((x1 - ox - off) / px)) + 2):
            cx, cy = ox + off + i * px, oy + j * py
            L = kw.get("length", 56.0)
            base = P(cx, cy) - K.unit(heading) * L / 2
            sp = pecan_sprig(base, heading, **kw)
            if inner.contains(sp.shape()):
                f += sp
    return f


def _valve(root, tip, width, bow):
    """One husk valve: a leaf from ``root`` to ``tip`` whose midrib bows
    ``bow`` px to the screen-left of travel (recurved), ``width`` wide."""
    root, tip = P(root), P(tip)
    mid = (root + tip) / 2 + K.left_normal(root, tip) * bow
    d = K.spline([root, mid, tip])
    return _leaf_region(d, width), pts_of(d, 0.3)


def pecan_husk(c, *, style="A", s=1.0):
    """The buckle (§H.9): a gold pecan husk splitting open. The NUT (a
    pointed ovoid, one half hatched — the dark-streaked shell) stands in
    the middle; the husk's VALVES (four, split along their sutures) peel
    back round it, each half-hatched on its inner half. Solid gold with an
    Aquifer contour (legal on red, §C.4).

    style A: nut upright, the side valves and the front valve recurved down
             and out round its foot (the husk after it opens);
    style B: nut in the husk's cup, the side valves spreading up and out,
             their tips curling back;
    style C: seen from the apex: four valves as an X round the nut."""
    c = P(c)
    k = s
    parts, hatch_regs = [], []
    if style == "D":
        # the four valves spread in an X behind a nut lying along the belt
        nut = K.R(K.vesica(c + P(-24 * k, 0), c + P(22 * k, 0), 21 * k)).buffer(2.5 * k).buffer(-2.5 * k)
        for ang_, bow in ((-126.0, -4.0), (-54.0, 4.0), (54.0, -4.0), (126.0, 4.0)):
            reg, mp = _valve(c + K.unit(ang_) * 2 * k, c + K.unit(ang_) * 31 * k, 17 * k, bow * k)
            parts.append((reg, mp))
    elif style == "C":
        nut = K.R(K.vesica(c + P(0, -16 * k), c + P(0, 16 * k), 17 * k))
        for ang_ in (-135.0, -45.0, 45.0, 135.0):
            reg, mp = _valve(c + K.unit(ang_) * 6 * k, c + K.unit(ang_) * 27 * k, 13 * k, 3.0 * k)
            parts.append((reg, mp))
    else:
        nut = K.R(K.vesica(c + P(0, -28 * k), c + P(0, 14 * k), 23 * k))
        if style == "A":
            for sg in (-1, 1):
                reg, mp = _valve(c + P(sg * 7 * k, -1 * k), c + P(sg * 28 * k, 17 * k), 16 * k, -sg * 8.0 * k)
                parts.append((reg, mp))
            reg, mp = _valve(c + P(0, 3 * k), c + P(0, 29 * k), 18 * k, 0.0)
            parts.append((reg, mp))
        else:
            cup = K.R(K.Path(c + P(-14 * k, 4 * k)).sag(c + P(14 * k, 4 * k), 11 * k).close().d) if False else None
            for sg in (-1, 1):
                reg, mp = _valve(c + P(sg * 4 * k, 18 * k), c + P(sg * 25 * k, -16 * k), 12.5 * k, sg * 7.0 * k)
                parts.append((reg, mp))
            reg, mp = _valve(c + P(0, 22 * k), c + P(0, 4 * k), 22 * k, 0.0)
            parts.append((reg, mp))
    valves = [r for r, _ in parts]
    shape = K.U(nut, *valves).buffer(1.0, join_style=1).buffer(-1.0, join_style=1)
    vu = K.U(*valves)
    if style == "D":
        lines = K.outline(nut)
        husk = K.U(*[r for r, _ in parts]).buffer(1.0, join_style=1).buffer(-1.0, join_style=1)
        lines += K.clip_out(K.outline(husk), nut, eps=-0.5, trap=0.0)
        for r, mp in parts:
            rib = LineString(mp)
            # one half of each valve hatched, butting onto its rib (the wing ridge)
            side = K.halfplane(mp[0], mp[-1], side=+1)
            wedge = K.halfplane(mp[0], mp[-1], side=+1).intersection(Point(*c).buffer(40.0 * k))
            others = K.U(*[r2 for r2, m2 in parts if m2 is not mp])
            half = r.intersection(wedge).difference(nut).difference(others.difference(r.buffer(-0.01)))
            lines += K.clip_out(K.line(C.polyline_d(mp), MEDIUM, role="valve-rib"), nut, eps=-0.5, trap=0.0)
        # the nut: its suture along the length
        lines += K.seg(c + P(-12 * k, 0.6 * k), c + P(11 * k, 0.6 * k), FINE, role="suture")
        return K.Part(shape, K.fill(shape, GOLD), lines, {"c": c})
    lines = K.clip_out(K.outline(nut), vu, eps=-0.5, trap=0.0)
    for r, _ in parts:
        lines += K.outline(r)
    # the nut: split on its axis, the left half hatched (the streaked shell)
    nut_vis = nut.difference(vu.buffer(0.1))
    ax = K.seg(c + P(0, -27 * k if style != "C" else -16 * k), c + P(0, 13 * k), FINE, role="suture")
    lines += K.clip_in(ax, nut_vis.buffer(-1.0))
    lines += K.hatch_in(nut_vis.intersection(K.box(0, 0, c[0], 2000)), angle=-45.0)
    for r, mp in parts:
        lines += K.clip_in(K.line(C.polyline_d(mp), FINE, role="valve-rib"), r.buffer(-3.5))
    return K.Part(shape, K.fill(shape, GOLD), lines, {"c": c})


# ---------------------------------------------------------------------------
# collar, belt
# ---------------------------------------------------------------------------
def collar(fc, *, top_y=284.0, dip=8.0, hw=30.0, x=379.0, depth=40.0, flare=9.0):
    """The doublet's standing collar (jade) round the neck: its top edge an
    arc dipping ``dip`` at the front (seen from a little above), rounded
    corners, sides flaring to its foot, which hides under the jerkin's
    neckline."""
    a0, a1 = P(x - hw, top_y), P(x + hw, top_y)
    top = K.arc_sag(a0, a1, -dip)
    d = top + f"L{x + hw + flare} {top_y + depth}L{x - hw - flare} {top_y + depth}Z"
    reg = K.R(d).buffer(-5.0, join_style=1).buffer(5.0, join_style=1)
    return K.Part(reg, K.fill(reg, JADE), K.outline(reg), {})


def belt(jerk_shape, *, y=458.0, h=20.0, sag=5.0, x0=200.0, x1=560.0, front=364.0):
    """A jade belt across the jerkin (between the armholes), sagging ``sag``
    at the front, a stitch line knocked out along it."""
    top = spl([P(x0, y - h / 2 - 2.0), P(front, y - h / 2 + sag), P(x1, y - h / 2 - 4.0)])
    bot = spl([P(x1, y + h / 2 - 4.0), P(front, y + h / 2 + sag), P(x0, y + h / 2 - 2.0)])
    d = chain_d(top, f"M{x1} {y - h / 2 - 4.0}L{x1} {y + h / 2 - 4.0}", bot)
    reg = K.R(d).buffer(0).intersection(jerk_shape)
    mid = spl([P(x0, y - 2.0), P(front, y + sag), P(x1, y - 4.0)])
    return K.Part(reg, K.fill(reg, JADE), K.outline(reg), {"mid": mid})


def pecan_nut(c, heading_deg=-90.0, *, L=16.0, W=10.0):
    """A small gold pecan nut (a pointed ovoid) for the jerkin's weave:
    solid gold with an Aquifer FINE contour (§C.4: gold on red only as a
    contoured solid)."""
    c = P(c)
    u = K.unit(heading_deg)
    reg = K.R(K.vesica(c - u * L / 2, c + u * L / 2, W)).buffer(1.2, join_style=1).buffer(-1.2, join_style=1)
    return K.fill(reg, GOLD, role="nut") + K.outline(reg, FINE, role="nut"), reg


def pecan_weave(region, *, pitch=(50.0, 40.0), origin=(366.0, 330.0), heading=-62.0, margin=5.0,
                nuts=True, **kw):
    """The jerkin's woven pattern: a half-drop grid of pecan leaves
    (knocked out of the red), and — in the gaps between them — gold pecan
    nuts (contoured solids). Each motif is kept whole inside ``region``.
    → (leaf Frag to knock out, nut Frag drawn on top)."""
    reg = K.R(region)
    inner = reg.buffer(-margin)
    x0, y0, x1, y1 = reg.bounds
    ox, oy = origin
    px, py = pitch
    leaves, nutf = C.Frag(), C.Frag()
    L = kw.get("length", 56.0)
    j0 = int(math.floor((y0 - oy) / py)) - 1
    j1 = int(math.ceil((y1 - oy) / py)) + 1
    placed = []
    for j in range(j0, j1 + 1):
        off = px / 2 if j % 2 else 0.0
        for i in range(int(math.floor((x0 - ox - off) / px)) - 1, int(math.ceil((x1 - ox - off) / px)) + 2):
            cx, cy = ox + off + i * px, oy + j * py
            base = P(cx, cy) - K.unit(heading) * L / 2
            sp = pecan_sprig(base, heading, **kw)
            sh = sp.shape()
            if inner.contains(sh):
                leaves += sp
                placed.append(sh)
    if nuts:
        allp = shapely.union_all(placed) if placed else Polygon()
        for j in range(j0, j1 + 1):
            off = px / 2 if j % 2 else 0.0
            for i in range(int(math.floor((x0 - ox - off) / px)) - 1, int(math.ceil((x1 - ox - off) / px)) + 2):
                cx, cy = ox + off + i * px + px / 2, oy + j * py + py * 0.05
                f, nreg = pecan_nut((cx, cy), heading)
                if inner.contains(nreg.buffer(1.0)) and allp.distance(nreg) > 3.0 + FINE:
                    nutf += K.atomic(f, f"nut{i}_{j}")
    return leaves, nutf


def placket(jerk_shape, *, top=(366.0, 314.0), bottom=(361.0, 560.0), hw=15.0):
    """The jade placket down the jerkin's front (the doublet showing where
    the jerkin closes): a straight band ``2·hw`` wide."""
    reg = LineString([top, bottom]).buffer(hw, cap_style=2).intersection(jerk_shape)
    return K.Part(reg, K.fill(reg, JADE), K.outline(reg), {})
