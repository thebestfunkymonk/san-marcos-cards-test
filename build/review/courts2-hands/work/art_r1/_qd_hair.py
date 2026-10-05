"""art/_qd_hair.py — Q♦'s hair and bare skin: the swept gold hair (cap and
long tresses, §G.24 current lines), the neck with the spring of the
shoulders, and the pearl choker. Built on deck.courtkit; art/QD.py stacks
them."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from inkkit import geom as G
from deck.motifs import core as C
from deck.motifs import geometric as MG

P, R, U, D = K.P, K.R, K.U, K.D
FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR
GOLD, INK = K.GOLD, K.INK
GAP, GAP_MARK = K.GAP, K.GAP_MARK


def sp(points, h_start=None, h_end=None, step=0.5):
    """Dense points of the kit's G1 arc spline."""
    return C.sample_d(K.spline(list(points), h_start, h_end), step)[0][0]


def smooth(p, step=1.0, win=9):
    """Resample a polyline evenly and smooth it (moving average): a clean
    guide for current lines — G.Curve.offset leaves micro-loops on some
    arc-spline guides at offsets > 20 px, which fragment the lines."""
    q = G.Curve(np.asarray(p, float)).resample(step)
    k = np.ones(win) / win
    x = np.convolve(np.pad(q[:, 0], win // 2, mode="edge"), k, mode="valid")
    y = np.convolve(np.pad(q[:, 1], win // 2, mode="edge"), k, mode="valid")
    return np.column_stack([x, y])


def neck_chest(axis=380.0, *, top=236.0, hw=14.5, base_y=286.0, shoulder=(346.0, 420.0), spring_y=300.0,
               bottom=380.0, lean=0.0) -> K.Part:
    """Bare skin: the neck column (a slender taper under the jaw) springing
    at its base into the shoulders — each side a tangent arc out to the
    cape's inner edge — and the chest down under the gown's neckline. Paper
    is never painted: the Part only hides what is behind it and draws the
    neck's two MEDIUM side lines."""
    xl, xr = axis - hw, axis + hw
    sl, sr = shoulder
    left = K.Path((xl + 1.0 + lean, top)).line((xl, base_y)).arc3((xl - 5.0, base_y + 9.5), (sl, spring_y))
    right = K.Path((xr - 1.0 + lean, top)).line((xr, base_y)).arc3((xr + 5.0, base_y + 9.5), (sr, spring_y))
    lp = C.sample_d(left.d, 0.5)[0][0]
    rp = C.sample_d(right.d, 0.5)[0][0]
    reg = Polygon(np.vstack([lp, [[sl - 4.0, spring_y + 2.0], [sl - 4.0, bottom], [sr + 4.0, bottom],
                                  [sr + 4.0, spring_y + 2.0]], rp[::-1]])).buffer(0)
    lines = K.line(left.d, MEDIUM, role="neck") + K.line(right.d, MEDIUM, role="neck")
    return K.Part(reg, C.Frag(), lines, {"left": lp, "right": rp})


def pearls(p0, pm, p1, *, d_min=4.2, d_max=6.3, gap=3.2, color=GOLD) -> C.Frag:
    """A graduated pearl strand (§G.29) along the arc p0 → pm → p1: gold beads,
    the largest at the centre, 3 px apart."""
    return MG.pearl_beading(K.arc3(p0, pm, p1), d_min=d_min, d_max=d_max, gap=gap, style="dot", color=color)


def ribbon(spine, w0, w1, *, cap=True, w_mid=None):
    """A lock of hair along ``spine`` (points, root → end), its width
    tapering w0 → (w_mid →) w1, the end rolled (a semicircle). → (region,
    left edge pts, right edge pts, centre pts) — left/right = screen-left /
    screen-right of travel."""
    cv = G.Curve(np.asarray(spine, float))
    pts = cv.resample(0.5)
    n = len(pts)
    t = np.linspace(0, 1, n)
    tang = np.gradient(pts, axis=0)
    tang /= np.hypot(tang[:, 0], tang[:, 1])[:, None]
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
    if w_mid is None:
        w = w0 + (w1 - w0) * t
    else:
        w = np.where(t < 0.5, w0 + (w_mid - w0) * t * 2, w_mid + (w1 - w_mid) * (t - 0.5) * 2)
    hw = (w / 2)[:, None]
    left, right = pts + nrm * hw, pts - nrm * hw
    ring = [left]
    if cap:
        c, r = pts[-1], float(hw[-1, 0])
        a0 = math.degrees(math.atan2(nrm[-1][1], nrm[-1][0]))
        for sgn in (-1, 1):
            th = np.radians(np.linspace(a0, a0 + sgn * 180.0, 40))
            arc = np.column_stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)])
            if np.dot(arc[20] - c, tang[-1]) > 0:
                break
        ring.append(arc)
    ring.append(right[::-1])
    reg = Polygon(np.vstack(ring)).buffer(0)
    return reg, left, right, pts


def lock(spine, w0, w1, *, n=2, side=+1, stagger=9.0, w_mid=None, color=GOLD, edge=CONTOUR,
         curl_deg=80.0) -> K.Part:
    """One long lock (§G.24): a gold ribbon with ``n`` current lines
    following its ``side`` edge (+1: the screen-right edge of travel is the
    guide, lines offset to its left), each rolling into a Ø6.3 terminal."""
    reg, le, ri, _ = ribbon(spine, w0, w1, w_mid=w_mid)
    guide = ri if side > 0 else le
    fl = K.current_lines(guide, n, reg, side=side, edge=edge, stagger=stagger, curl_deg=curl_deg)
    return K.Part(reg, K.fill(reg, color), fl + K.outline(reg), {"left": le, "right": ri})


def cap(fc, *, crown, r_back, back_low, hairline, far_outer, hairline_far, n=3, n_far=1, stagger=9.0,
        color=GOLD, back_pts=None) -> K.Part:
    """The hair over the skull of a 3/4-right head, swept back from the face.

    near (back) side: the outer contour an arc about ``crown`` (radius
    ``r_back``) from the top round the back of the skull to ``back_low``
    (or through ``back_pts``), the hairline a spline (``hairline``: from
    under the diadem at the front, over the temple and the ear, to the jaw).
    Current lines run PARALLEL TO THE HAIRLINE — the hair swept back — each
    rolling into a terminal toward the nape.
    far side: a narrow band beyond the far cheek (``far_outer`` / its
    ``hairline_far``), plain or with ``n_far`` lines."""
    cx, cy = crown
    top = P(cx, cy - r_back)
    if back_pts is None:
        a1 = K.ang(P(crown), P(back_low))
        a1 = K.unwrap(-90.0, a1, cw=False)
        th = np.radians(np.linspace(-90.0, a1, 200))
        outer = np.column_stack([cx + r_back * np.cos(th), cy + r_back * np.sin(th)])
    else:
        outer = sp([tuple(top)] + list(back_pts), h_start=180.0)
    hl = sp(hairline)
    near = Polygon(np.vstack([outer, hl[::-1]])).buffer(0)
    fo = sp([tuple(top)] + list(far_outer), h_start=0.0)
    hf = sp(hairline_far)
    far = Polygon(np.vstack([fo, hf[::-1]])).buffer(0)
    reg = U(near, far).buffer(0.4).buffer(-0.4)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    lines = K.current_lines(hl, n, near, side=-1 if hl[-1][1] > hl[0][1] else +1, edge=MEDIUM, stagger=stagger)
    if not lines.meta.get("lines"):
        lines = K.current_lines(hl, n, near, side=+1, edge=MEDIUM, stagger=stagger)
    if n_far:
        lines += K.current_lines(hf, n_far, far, side=+1, edge=MEDIUM, stagger=stagger)
    return K.Part(reg, K.fill(reg, color), lines + K.outline(reg), {"near": near, "far": far, "hairline": hl})


def tress(inner, outer, *, n=4, stagger=10.0, curl_deg=80.0, color=GOLD, end_r=None, side=+1, first=None,
          guide="inner", h_in=None, h_out=None, guide_from=None, guide_pts=None) -> K.Part:
    """One continuous mass of hair from the face to a rolled end: the region
    between the ``inner`` edge (points from the root at the brow, over the
    temple and down the tress — the side against the face and neck) and the
    ``outer`` edge (the same direction, round the back of the skull and down
    the tress), closed at the root by a straight cut (hidden under the
    diadem) and at the end by a round cap. Current lines (§G.24) run the
    whole length parallel to the ``guide`` edge, staggered and curled at
    their ends. ``side``: +1 when the outer edge is to the screen-left of
    travel along the inner edge."""
    pi = sp(inner, h_start=h_in)
    po = sp(outer, h_start=h_out)
    a, b = pi[-1], po[-1]
    c = (a + b) / 2
    r = float(np.hypot(*(b - a))) / 2 if end_r is None else end_r
    # round end: a semicircle from the outer end to the inner end, bulging forward
    tang = pi[-1] - pi[-6]
    tang = tang / np.hypot(*tang)
    mid = c + tang * r
    cap = C.sample_d(K.arc3(tuple(b), tuple(mid), tuple(a)), 0.5)[0][0]
    ring = np.vstack([pi, cap[::-1][1:-1][::-1] if False else cap[::-1], po[::-1]])
    ring = np.vstack([pi, cap[::-1], po[::-1]]) if np.hypot(*(cap[0] - pi[-1])) > np.hypot(*(cap[-1] - pi[-1])) \
        else np.vstack([pi, cap, po[::-1]])
    reg = Polygon(ring).buffer(0)
    if reg.geom_type != "Polygon":
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    g = pi if guide == "inner" else po
    if guide_pts is not None:
        g = sp(guide_pts)
    if guide_from is not None:                    # start the lines below the root (where the mass is wide)
        g = g[np.argmin(np.hypot(g[:, 0] - guide_from[0], g[:, 1] - guide_from[1])):]
    sd = side if guide == "inner" else -side
    fl = K.current_lines(g, n, reg, side=sd, edge=MEDIUM if guide == "inner" else CONTOUR, stagger=stagger,
                         curl_deg=curl_deg, first=first)
    return K.Part(reg, K.fill(reg, color), fl + K.outline(reg), {"inner": pi, "outer": po})


# =============================================================================
# the coiffure: hair waved back from the brow into a chignon at the nape
# =============================================================================
def coil(c, r, *, a0=-90.0, turns=1.5, w=FINE, pitch=7.0, first=None, edge=CONTOUR, cw=True):
    """A compass spiral inside a round chignon of radius ``r`` about ``c``:
    tangent half-circles whose radii shrink by pitch/2 each half turn (so
    the windings lie ``pitch`` apart), starting ``first`` inside the edge
    at angle ``a0`` and ending in a Ø6.3 terminal. → Frag."""
    first = (edge / 2 + GAP + w / 2 + 0.05) if first is None else first
    r1 = r - first
    c = P(c)
    p0 = K.polar(c, r1, a0)
    sg = 1 if cw else -1
    t = C.Turtle(p0[0], p0[1], a0 + sg * 90.0)
    rr = r1
    n_half = int(round(turns * 2))
    for _ in range(n_half):
        if rr < 2.5:
            break
        t.arc(rr, sg * 180.0)
        rr -= pitch / 2
    f = C.stroke(t.d(), w, role="coil")
    f += C.dot(t.pos[0], t.pos[1], K.TD, role="terminal")
    return f


def coiffure(skin, *, hairline, outer, bun_c, bun_r, n=4, stagger=8.0, curl_deg=80.0, skin_cut=236.0,
             coil_turns=1.5, coil_a0=-150.0, color=GOLD, band=None):
    """The near side of a 3/4 head's hair, dressed back: one mass from the
    ``hairline`` (points: root under the diadem at the brow → over the
    temple and the ear → behind the jaw) to the ``outer`` contour (root
    under the diadem at the back → round the back of the skull → toward
    the nape), and a round CHIGNON (``bun_c``, ``bun_r``) at the nape in
    front of it. Current lines (§G.24) run parallel to the hairline — the
    hair waved back from the face — and are gathered into the chignon (they
    run under its rim); the chignon carries a compass coil. The mass never
    covers the skin below ``skin_cut`` (the cheek and jaw stay paper).
    → (mass Part, chignon Part)."""
    hl = sp(hairline)
    ol = sp(outer)
    ring = np.vstack([hl, ol[::-1]])
    mass = Polygon(ring).buffer(0)
    if mass.geom_type != "Polygon":
        mass = max(K._polys_of(mass), key=lambda g: g.area)
    mass = mass.difference(skin.buffer(0.3).intersection(K.box(0, skin_cut, 750, 1000)))
    mass = max(K._polys_of(mass), key=lambda g: g.area)
    if band is not None:
        mass = mass.difference(band)
        mass = max(K._polys_of(mass), key=lambda g: g.area)
    bun = Point(*bun_c).buffer(bun_r, quad_segs=48)
    lines = K.current_lines(hl, n, mass, side=-1, edge=MEDIUM, stagger=stagger, curl_deg=curl_deg,
                            placed=bun.buffer(GAP_MARK))
    mp = K.Part(mass, K.fill(mass, color), lines + K.outline(mass), {"hairline": hl, "outer": ol})
    cl = coil(bun_c, bun_r, a0=coil_a0, turns=coil_turns)
    bp = K.Part(bun, K.fill(bun, color), cl + K.outline(bun), {})
    return mp, bp


def sliver(inner, outer, *, color=GOLD, end_r=None) -> K.Part:
    """A plain narrow band of hair (the far side of a 3/4 head): the region
    between two point lists (root → end), the end rounded."""
    pi = sp(inner)
    po = sp(outer)
    a, b = pi[-1], po[-1]
    c = (a + b) / 2
    r = float(np.hypot(*(b - a))) / 2
    tang = pi[-1] - pi[-6]
    tang = tang / np.hypot(*tang)
    capp = C.sample_d(K.arc3(tuple(b), tuple(c + tang * r), tuple(a)), 0.5)[0][0]
    ring = np.vstack([pi, capp[::-1], po[::-1]])
    reg = Polygon(ring).buffer(0)
    if reg.geom_type != "Polygon":
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    return K.Part(reg, K.fill(reg, color), K.outline(reg), {})


def fall(skin, *, inner, outer, n=4, stagger=9.0, curl_deg=80.0, skin_cut=236.0, band=None, cap=None,
         end_r=None, color=GOLD, first=None, guide="inner") -> K.Part:
    """The near side of a 3/4 head's hair as ONE mass: from the ``inner``
    edge (root under the diadem at the brow → over the temple and the ear →
    behind the jaw → down the long tress, the side toward the face and the
    body) to the ``outer`` edge (root under the diadem at the back → round
    the back of the skull → down the tress), the end rolled round. Current
    lines (§G.24) run the whole length parallel to the inner edge — the hair
    waved back from the face and falling — staggered and curled where the
    tress narrows. ``cap``: a region (the skull above the diadem band) added
    to the mass; the mass never covers the skin below ``skin_cut`` (cheek
    and jaw stay paper) and stops under ``band``."""
    pi = sp(inner)
    po = sp(outer)
    a, b = pi[-1], po[-1]
    c = (a + b) / 2
    r = float(np.hypot(*(b - a))) / 2 if end_r is None else end_r
    tang = (pi[-1] - pi[-6]) + (po[-1] - po[-6])
    tang = tang / np.hypot(*tang)
    capp = C.sample_d(K.arc3(tuple(a), tuple(c + tang * r), tuple(b)), 0.5)[0][0]
    ring = np.vstack([pi, capp, po[::-1]])
    reg = Polygon(ring).buffer(0)
    if reg.geom_type != "Polygon":
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    if cap is not None:
        reg = U(reg, cap).buffer(0.3).buffer(-0.3)
    reg = reg.difference(skin.buffer(0.3).intersection(K.box(0, skin_cut, 750, 1000)))
    if band is not None:
        reg = reg.difference(band)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    if guide == "inner":
        fl = K.current_lines(smooth(pi), n, reg, side=-1, edge=MEDIUM, stagger=stagger, curl_deg=curl_deg,
                             first=first)
    else:
        fl = K.current_lines(smooth(po), n, reg, side=+1, edge=CONTOUR, stagger=stagger, curl_deg=curl_deg,
                             first=first)
    return K.Part(reg, K.fill(reg, color), fl + K.outline(reg), {"inner": pi, "outer": po})


# =============================================================================
# hair dressed up: the ear, the swept mass with its knot, the earring
# =============================================================================
def ear(c, rx=7.5, ry=12.5, tilt=-12.0, *, face=None, inner=True, c_pts=None) -> K.Part:
    """The near ear of a 3/4 head: a paper oval (rx × ry about ``c``, tilted
    ``tilt``°) joined to the face (§H.0 'Ear: a C'): its outline MEDIUM, one
    MEDIUM C inside parallel to its back rim."""
    c = P(c)
    th = np.radians(np.linspace(0, 360, 181))
    a = math.radians(tilt)
    ca, sa = math.cos(a), math.sin(a)
    x = rx * np.cos(th)
    y = ry * np.sin(th)
    pts = np.column_stack([c[0] + x * ca - y * sa, c[1] + x * sa + y * ca])
    reg = Polygon(pts).buffer(0)
    if face is not None:
        reg = reg.difference(face)
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    lines = K.outline(reg)
    if inner:
        # the C: an arc inside the back rim, from the top of the bowl round to the lobe
        if c_pts is None:
            pa = c + P(rx * 0.30, -ry * 0.50)
            pm = c + P(-rx * 0.30, -ry * 0.05)
            pb = c + P(rx * 0.25, ry * 0.40)
        else:
            pa, pm, pb = (c + P(*q) for q in c_pts)
        lines += K.line(K.arc3(pa, pm, pb), MEDIUM, role="ear")
    return K.Part(reg, C.Frag(), lines, {"lobe": c + P(rx * 0.2, ry * 0.85)})


def earring(top, *, bead=6.3, drop=(12.0, 8.4), gap=0.0, color=GOLD) -> K.Part:
    """A gold earring: a bead at the lobe and a ♦ lozenge drop hanging from
    it (the house mark), both solid gold with Aquifer contours."""
    top = P(top)
    b = Point(*top).buffer(bead / 2, quad_segs=16)
    L, W = drop
    dc = top + P(0.0, bead / 2 + L / 2 - 1.0 + gap)
    lz = R(C.lozenge_d(dc[0], dc[1], L, W, 90.0))
    shape = U(b, lz)
    lines = K.outline(b) + C.stroke(D(lz), MEDIUM, style="point", role="drop")
    lines = K.clip_out(K.outline(lz, MEDIUM), b, eps=-0.5, trap=0.0) if False else lines
    return K.Part(shape, K.fill(shape, color), K.outline(shape), {})


def swept(skin, *, hairline, outer, n=4, stagger=8.0, curl_deg=80.0, band=None, avoid=None, color=GOLD,
          guide="hairline", side=-1, first=None, skin_cut=214.0) -> K.Part:
    """Hair dressed up and back: one mass between the ``hairline`` (root
    under the diadem at the brow → back over the ear → the nape) and the
    ``outer`` contour (root under the diadem at the back → round the skull
    → the knot at the nape → back under it to the nape), closed by a
    straight join (hidden by the neck / collar). Current lines (§G.24) run
    parallel to the hairline — swept back — and curl into the knot."""
    hl = sp(hairline)
    ol = sp(outer)
    reg = Polygon(np.vstack([hl, ol[::-1]])).buffer(0)
    if reg.geom_type != "Polygon":
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    reg = reg.difference(skin.buffer(0.3).intersection(K.box(0, skin_cut, 750, 1000)))
    if band is not None:
        reg = reg.difference(band)
    if avoid is not None:
        reg = reg.difference(avoid)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    g = smooth(hl if guide == "hairline" else ol)
    edge = MEDIUM if guide == "hairline" else CONTOUR
    fl = K.current_lines(g, n, reg, side=side, edge=edge, stagger=stagger, curl_deg=curl_deg, first=first)
    return K.Part(reg, K.fill(reg, color), fl + K.outline(reg), {"hairline": hl, "outer": ol})


def knot(c, r, *, n=2, a0=200.0, sweep=250.0, color=GOLD, pitch=7.0) -> K.Part:
    """The chignon: a round knot of hair at the nape, its current lines
    (§G.24) concentric arcs inside the rim — ``n`` of them, 7 px apart,
    each running ``sweep``° from ``a0`` and rolling inward into a Ø6.3
    terminal (a coiled braid, never a spiral: a spiral reads as an ear)."""
    c = P(c)
    reg = Point(*c).buffer(r, quad_segs=48)
    first = CONTOUR / 2 + GAP + FINE / 2 + 0.05
    lines = C.Frag()
    placed = Polygon()
    for k in range(n):
        rr = r - first - k * pitch
        if rr < 5.0:
            break
        a1 = a0 + sweep - k * 40.0
        th = np.radians(np.linspace(a0 + k * 20.0, a1, 160))
        g = np.column_stack([c[0] + rr * np.cos(th), c[1] + rr * np.sin(th)])
        fl = K.current_lines(g, 1, reg, side=+1, first=0.0, edge=CONTOUR, stagger=0.0, curl_deg=70.0,
                             placed=placed)
        lines += fl
        for ln in fl.meta.get("lines", []):
            placed = placed.union(LineString(ln).buffer(FINE / 2 + 0.01))
    return K.Part(reg, K.fill(reg, color), lines + K.outline(reg), {})


def knot2(c, r, *, n=6, twist=40.0, r0=None, a0=-90.0, color=GOLD, eye=True) -> K.Part:
    """The chignon as a TWISTED knot: ``n`` ribs, each a circular arc
    twisted ``twist``° from a Ø6.3 eye at the centre out to the rim (the
    rosette's pinwheel ribs, §G.1, here strands of hair wound round a
    pin). FINE Aquifer on gold, the ribs butting into the rim."""
    c = P(c)
    reg = Point(*c).buffer(r, quad_segs=48)
    r0 = (K.TD / 2 + GAP_MARK + FINE / 2 + 0.2) if r0 is None else r0
    r1 = r - 0.5
    lines = C.Frag()
    for k in range(n):
        a = a0 + k * 360.0 / n
        p0 = K.polar(c, r0, a)
        p1 = K.polar(c, r1, a + twist)
        # an arc from p0 to p1 bulging to one side (the twist)
        ch = np.hypot(*(p1 - p0))
        lines += K.line(K.arc_sag(p0, p1, ch * 0.16), FINE, role="strand")
    if eye:
        lines += K.dot(c, K.TD, role="eye")
    return K.Part(reg, K.fill(reg, color), lines + K.outline(reg), {})


def tie(p0, p1, w=8.4, *, color=None) -> K.Part:
    """A narrow band wrapped round a lock (the tie at the root of a
    ponytail): a round-ended bar from p0 to p1, ``w`` wide."""
    color = K.JADE if color is None else color
    reg = LineString([tuple(p0), tuple(p1)]).buffer(w / 2, cap_style=1, quad_segs=12)
    return K.Part(reg, K.fill(reg, color), K.outline(reg), {})


def mane(*, outer, inner, n=4, stagger=0.0, color=GOLD, band=None, first=None, curl_deg=80.0) -> K.Part:
    """Long hair falling BEHIND the head, the neck and the cape (the kit's
    convention: the face egg is in front of its hair): the region between
    the visible ``outer`` contour (root under the diadem → round the back
    of the skull → down the back, into the cape) and a hidden ``inner``
    edge (behind the face and neck). Current lines (§G.24) run parallel to
    the outer contour and pass under the cape (the long hair continues)."""
    po = sp(outer)
    pi = sp(inner)
    reg = Polygon(np.vstack([po, pi[::-1]])).buffer(0)
    if reg.geom_type != "Polygon":
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    if band is not None:
        reg = reg.difference(band)
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    fl = K.current_lines(smooth(po), n, reg, side=+1, edge=CONTOUR, stagger=stagger, curl_deg=curl_deg,
                         first=first)
    return K.Part(reg, K.fill(reg, color), fl + K.outline(reg), {"outer": po})


def ear2(top, mid, bot, *, face, inner=None) -> K.Part:
    """The near ear of a 3/4 head, §H.0 'a C': the lune between the face
    contour and one C arc from ``top`` (on the temple) out through ``mid``
    (the back of the helix) to ``bot`` (the lobe, on the jaw). Paper; the C
    is its outline. ``inner``: three points of a short MEDIUM inner fold."""
    arc = C.sample_d(K.arc3(P(top), P(mid), P(bot)), 0.4)[0][0]
    reg = Polygon(np.vstack([arc, [P(bot) + P(12.0, 0.0), P(top) + P(12.0, 0.0)]])).buffer(0)
    reg = reg.difference(face)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    lines = K.outline(reg)
    if inner is not None:
        lines += K.line(K.arc3(*[P(q) for q in inner]), MEDIUM, role="ear")
    return K.Part(reg, C.Frag(), lines, {"lobe": P(bot)})
