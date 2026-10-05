"""art/_qs_parts.py — Q♠ · The Blind Oracle: the parts the court kit does not have.

Everything here is built the kit's way (deck.courtkit): compass arcs and arc
splines at final size, K.Part(shape, fills, lines, meta), legal widths only,
knockouts as geometry. Q♠-specific; candidates for upstreaming are noted in
each docstring.

    rot_part         rigid rotation of a Part (the inclined head group)
    veil             the paper veil: back drape + crown (split so the hair sits between)
    stalactite_diadem  a gold circlet hung with nine graduated stalactite points (§G.13)
    gill_plume_lobe  one ruff plume: a red frond, barbs on one side, spine + barbs knocked out (§G.15)
    mirror           the scrying mirror: gold frame, jade field, the blind-salamander vision, handle
    salamander       Eurycea rathbuni, dorsal view, paper silhouette on jade (vision), red gills
    laurel_sprig     Texas mountain laurel: pinnate glossy leaves (jade) + pendant raceme (paper)
    drip_cuff        a cuff band whose drip fringe (§G.14) is knocked out of the sleeve below it
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms as FM
from inkkit import geom as G

P = K.P
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD
KO = MEDIUM                      # knockout line width (§I.12: ≥ 2.5)


# -----------------------------------------------------------------------------
# rigid moves
# -----------------------------------------------------------------------------
def rot_frag(f: C.Frag, deg, pivot):
    return f.rotate(deg, pivot[0], pivot[1]) if deg else f


def rot_geom(g, deg, pivot):
    return shapely.affinity.rotate(g, deg, origin=tuple(pivot)) if deg else g


def rot_pt(p, deg, pivot):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    v = P(p) - P(pivot)
    return P(pivot) + np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def rot_part(part: K.Part, deg, pivot) -> K.Part:
    """A Part turned rigidly by ``deg`` (screen degrees, clockwise) about ``pivot``."""
    if not deg:
        return part
    meta = {}
    for k, v in part.meta.items():
        meta[k] = rot_pt(v, deg, pivot) if isinstance(v, np.ndarray) and v.shape == (2,) else v
    return K.Part(rot_geom(part.shape, deg, pivot), rot_frag(part.fills, deg, pivot),
                  rot_frag(part.lines, deg, pivot), meta)


def polys(g):
    return K._polys_of(g)


def biggest(g):
    ps = polys(g)
    return max(ps, key=lambda q: q.area) if ps else Polygon()


def ko_lines(solid_region, frag: C.Frag, color, role=""):
    """A solid ``color`` fill of ``solid_region`` with ``frag``'s marks knocked out (paper)."""
    d = C.knockout(K.D(solid_region), frag)
    return K.fill(d, color, role=role)


# -----------------------------------------------------------------------------
# veil
# -----------------------------------------------------------------------------
def veil(far_pts, apex, near_pts, opening, *, apex_in=-28.0, apex_out=28.0, n_contours=2,
         contour_side="near", contour_stagger=16.0, contour_region=None):
    """The paper veil (§H.2 'paper veil with sparse contour lines'), a
    Madonna veil over the head whose crown rises to a softly POINTED top (the
    Spring Lake lens, §G.26, in cloth) and falls to the shoulders.

    far_pts   far-side contour from its foot (hidden) up to below the apex;
    apex      the top point; ``apex_in`` / ``apex_out`` the headings (screen
              deg) arriving at and leaving it (a soft point, never a hood's beak);
    near_pts  near-side contour from below the apex down to its foot (hidden);
    opening   the face opening (shapely region): the hair and face show
              through it; its boundary inside the veil is the veil's front edge.

    Returns (back, crown): ``back`` is the whole veil, to stack BEHIND the hair
    and head; ``crown`` = veil − opening, to stack IN FRONT of the hair (its
    only interior line is the front edge). meta['contours']: the sparse FINE
    contour lines (§G.24 current lines following the near-side edge)."""
    fp = [P(p) for p in far_pts] + [P(apex)]
    npts = [P(apex)] + [P(p) for p in near_pts]
    _, pf, _ = FM.arc_spline(fp, headings={len(fp) - 1: apex_in})
    _, pn, _ = FM.arc_spline(npts, headings={0: apex_out})
    outline_pts = np.vstack([pf, pn[1:]])
    reg = biggest(Polygon(np.vstack([outline_pts, [outline_pts[0]]])).buffer(0))
    crown = biggest(reg.difference(opening))
    back_lines = K.outline(reg)
    edge = opening.boundary.intersection(reg.buffer(-0.5))
    crown_lines = C.Frag()
    for ln in K._lines_of(shapely.line_merge(edge) if edge.geom_type != "LineString" else edge):
        if ln.length > 4:
            crown_lines += K.line(C.polyline_d(np.asarray(ln.coords)), MEDIUM, role="veil-edge")
    guide = pn if contour_side == "near" else pf[::-1]
    creg = crown.buffer(-(MEDIUM / 2)) if contour_region is None else contour_region
    contours = K.current_lines(guide, n_contours, creg, side=+1 if contour_side == "near" else -1, edge=CONTOUR,
                               stagger=contour_stagger) if n_contours else C.Frag()
    return (K.Part(reg, C.Frag(), back_lines, {"pts": outline_pts}),
            K.Part(crown, C.Frag(), crown_lines + contours, {"edge": edge}))


# -----------------------------------------------------------------------------
# stalactite diadem (§G.13 points on a circlet)
# -----------------------------------------------------------------------------
def stalactite_diadem(far_end, mid, near_end, *, h=10.0, n=9, lengths=(20.0, 8.0), widths=(9.0, 4.6),
                      far_k=0.84, gap_extra=0.6, detail_min=8.0):
    """A gold circlet worn over the veil at the brow — a band ``h`` tall whose
    centre line is the arc far_end → mid (on the feature axis) → near_end —
    hung with ``n`` graduated STALACTITE points (§G.13: tall kites, largest at
    the centre) that fall plumb from its lower edge. The points are spaced by
    their own widths (3 px of paper + the MEDIUM outline between
    neighbours), so nine fit without crowding into a zigzag; the far half is
    foreshortened by ``far_k`` (3/4 head). Points ≥ ``detail_min`` wide carry
    a FINE split joint (the stalactite's growth axis). Upstream: kit
    ``diadem`` spaces points by a uniform pitch, which clamps nine to slivers
    on a queen's head."""
    far_end, mid, near_end = P(far_end), P(mid), P(near_end)
    c_arc, r_arc = K.circ3(far_end, mid, near_end)
    band_d = K.arc3(far_end, mid, near_end)
    cl = C.sample_d(band_d, 0.4)[0][0]
    cline = LineString(cl)
    band = cline.buffer(h / 2, cap_style=1, quad_segs=10)
    half = (n - 1) // 2
    ws, ls = [], []
    for i in range(-half, half + 1):
        k = 1.0 - abs(i) / half
        ws.append(widths[1] + (widths[0] - widths[1]) * k)
        ls.append(lengths[1] + (lengths[0] - lengths[1]) * k)
    xs = [0.0] * n
    for j in range(half + 1, n):
        xs[j] = xs[j - 1] + (ws[j - 1] + ws[j]) / 2 + K.GAP_MARK + MEDIUM + gap_extra
    for j in range(half - 1, -1, -1):
        xs[j] = xs[j + 1] - ((ws[j + 1] + ws[j]) / 2 + K.GAP_MARK + MEDIUM + gap_extra) * far_k
    xs = [mid[0] + x for x in xs]

    def low_y(x):
        # lower edge of the band at x (the band's centre arc + h/2)
        ln = LineString([(x, -1000), (x, 2000)]).intersection(band)
        return ln.bounds[3] if not ln.is_empty else mid[1] + h / 2

    kites, axes = [], C.Frag()
    for x, w, L in zip(xs, ws, ls):
        top = low_y(x) - 1.6
        kite = Polygon([(x - w / 2, top - 2.0), (x + w / 2, top - 2.0), (x + w * 0.20, top + L * 0.62),
                        (x, top + L), (x - w * 0.20, top + L * 0.62)])
        kites.append(kite)
        if w >= detail_min:
            axes += K.seg(P(x, top + 4.6), P(x, top + L - 5.5), FINE, role="axis")
    stone = K.U(*kites)
    shape = K.U(band, stone)
    lines = K.clip_out(K.outline(stone), band, eps=-0.8, trap=0.0) + K.outline(band)
    lines += K.clip_out(axes, band.buffer(3.2), eps=0.0, trap=0.0)
    return K.Part(shape, K.fill(shape, GOLD), lines, {"band": band, "xs": xs, "kites": kites})


# -----------------------------------------------------------------------------
# gill-plume ruff (§G.15 at ruff scale)
# -----------------------------------------------------------------------------
def gill_plume_lobe(root, tip, *, sag=10.0, width=30.0, n=6, side=+1, scallop=3.2, spine_ko=True,
                    barb_ko=0.62, color=RED, tip_bead=0.0):
    """One ruff plume: a red frond on a curved spine ``root`` → ``tip``
    (bulging ``sag`` px to the left of travel). Its outline is a slim
    lanceolate web whose ONE feathered side (``side`` +1 = left of travel)
    is cut into ``n`` scallops (the barbs of §G.15, shortening toward the
    tip); the other side is plain. The spine and the barb shafts (spine →
    each scallop's cusp, swept toward the tip) are KNOCKED OUT to paper at
    MEDIUM (§C.4: patterns on red are knockouts), stopping 3 px inside the
    edge. → Part (meta 'spine')."""
    root, tip = P(root), P(tip)
    sp = C.sample_d(K.arc_sag(root, tip, sag), 0.5)[0][0]
    cv = G.Curve(sp)
    L = cv.length
    ss = np.linspace(0, L, 160)
    Pp = np.array([cv.at_s(s) for s in ss])
    Nn = np.array([cv.normal_s(s) for s in ss]) * side     # toward the feathered side
    t = ss / L
    prof = np.sin(np.pi * np.clip(t, 0, 1) ** 0.72)
    w_out = (width * 0.58) * prof + 2.5 * (1 - t)
    w_in = (width * 0.30) * prof + 2.5 * (1 - t)
    outer = Pp + Nn * w_out[:, None]
    inner = Pp - Nn * w_in[:, None]
    # scallops on the feathered side between t 0.14 and 0.96
    ta = np.linspace(0.14, 0.97, n + 1)
    cusp = [np.array([np.interp(tt, t, outer[:, 0]), np.interp(tt, t, outer[:, 1])]) for tt in ta]
    # deepen the cusps toward the spine (the notches between barbs)
    cusp_in = []
    for tt, cp in zip(ta, cusp):
        k = int(np.clip(round(tt * (len(ss) - 1)), 0, len(ss) - 1))
        cusp_in.append(cp - Nn[k] * min(scallop, 0.35 * w_out[k]))
    k0 = int(round(ta[0] * (len(ss) - 1)))
    path = K.Path(inner[-1])
    for q in inner[::-1][1:]:
        path.line(q)
    for q in outer[1:k0]:
        path.line(q)
    path.line(cusp_in[0])
    for j in range(n):
        a, b = cusp_in[j], cusp_in[j + 1]
        bulge = float(np.hypot(*(b - a))) * 0.34 + scallop * 0.5
        # the barb bulges outward (to the feathered side of travel along the edge)
        path.sag(b, bulge * side)
    k1 = int(round(ta[-1] * (len(ss) - 1)))
    for q in outer[k1:]:
        path.line(q)
    path.close()
    shape = biggest(K.R(path.d).buffer(0))
    shape = shape.buffer(0.8, quad_segs=8).buffer(-0.8, quad_segs=8)
    ko = C.Frag()
    if spine_ko:
        spine_pts = np.array([cv.at_s(s) for s in np.linspace(0.06 * L, 0.93 * L, 80)])
        ko += C.stroke(C.polyline_d(spine_pts), KO, role="ko-spine")
    if barb_ko:
        # a paper line from each notch in toward the spine: the barbs part
        for j in range(1, n):
            k = int(round(ta[j] * (len(ss) - 1)))
            c_in = cusp_in[j]
            p = Pp[min(k + 6, len(ss) - 1)]
            ko += C.stroke(C.polyline_d([c_in, c_in + (p - c_in) * barb_ko]), KO, role="ko-barb")
    safe = shape.buffer(-(K.GAP_MARK + KO / 2 + CONTOUR / 2 + 0.2))
    ko = K.clip_in(ko, safe)
    fills = K.fill(C.knockout(K.D(shape), ko) if ko else K.D(shape), color, role="plume")
    return K.Part(shape, fills, K.outline(shape), {"spine": sp})


# -----------------------------------------------------------------------------
# the blind salamander (vision in the mirror)
# -----------------------------------------------------------------------------
# half-width profile along the spine (fraction of length, px): a broad flat
# spatulate head (widest just behind the snout's rounded square tip), a neck
# where the gills sit, a slim trunk, a long tail tapering to a point
SAL_HW = [(0.000, 0.0), (0.004, 3.4), (0.014, 5.4), (0.040, 6.4), (0.095, 7.0), (0.125, 6.4),
          (0.150, 4.4), (0.190, 4.3), (0.290, 4.9), (0.400, 4.8), (0.470, 4.3), (0.540, 3.5),
          (0.700, 2.5), (0.860, 1.3), (1.000, 0.0)]


def salamander(spine_pts, *, eye_s=0.060, eye_off=2.9, gill_s=0.150, fore_s=0.235, hind_s=0.455,
               limb=(10.0, 9.5), limb_a=(-20.0, 60.0), toe=4.6, fin=(0.50, 0.0), fin_w=4.2, gill_len=(7.0, 8.0, 6.5),
               gill_w=3.6):
    """Eurycea rathbuni, dorsal view, as a VISION in the mirror (§H.2): the
    pale body is PAPER (a hole in the mirror's jade) — the white cave
    creature — its eyes two Ø3 Aquifer dots UNDER the skin, three feathery
    red gills per side behind the broad, flat, spatulate head, long spindly
    jointed legs (paper lines; 4 splayed toes forward, 5 behind, shown as 3 at
    this size), and a tapering tail whose fin is a paper line offset round it
    (the tail fin seen from above). ``spine_pts``: snout → tail tip.
    Returns dict(body, ko (paper strokes), gills (region), eyes (ink Frag))."""
    _, sp, _ = FM.arc_spline(spine_pts)
    cv = G.Curve(np.asarray(sp))
    L = cv.length
    xs = np.array([a for a, _ in SAL_HW]) * L
    ys = np.array([b for _, b in SAL_HW])
    ss = np.linspace(0, L, 500)
    Pp = np.array([cv.at_s(s) for s in ss])
    Nn = np.array([cv.normal_s(s) for s in ss])
    H = np.interp(ss, xs, ys)
    left, right = Pp + Nn * H[:, None], Pp - Nn * H[:, None]
    body = Polygon(np.vstack([left, right[::-1]])).buffer(0.8, quad_segs=6).buffer(-0.8, quad_segs=6)
    body = biggest(body)

    def frame(frac):
        s = frac * L
        return cv.at_s(s), cv.tangent_s(s), cv.normal_s(s), float(np.interp(s, xs, ys))

    ko = C.Frag()
    for frac, fwd, ntoe in ((fore_s, +1, 3), (hind_s, -1, 3)):
        p, tg, nrm, h = frame(frac)
        for sg in (1, -1):
            out = nrm * sg
            a1 = math.radians(limb_a[0] * fwd)       # upper limb: out and a little back (fore) / forward (hind)
            u1 = out * math.cos(a1) - tg * math.sin(a1)
            a2 = math.radians(limb_a[1] * fwd)       # lower limb: bent toward the head (fore) / tail (hind)
            u2 = out * math.cos(a2) - tg * math.sin(a2)
            sh = p + out * (h - 1.5)
            el = sh + u1 * limb[0]
            wr = el + u2 * limb[1]
            ko += C.stroke(C.polyline_d([sh, el, wr]), KO, role="limb")
            base = math.degrees(math.atan2(u2[1], u2[0]))
            for dt in np.linspace(-40.0, 40.0, ntoe):
                q = wr + K.unit(base + dt) * toe
                ko += C.stroke(C.polyline_d([wr, q]), KO, role="toe")
    # tail fin: the tail twists as it curves, so its fin shows as a thin blade
    # along the OUTER side of the curve (paper, merged with the tail),
    # rising from the tail base and running out at the tip
    f0 = fin[0] * L
    s_f = np.linspace(f0, L, 160)
    Pf = np.array([cv.at_s(s) for s in s_f])
    Nf = np.array([cv.normal_s(s) for s in s_f])
    Hf = np.interp(s_f, xs, ys)
    tt = (s_f - f0) / (L - f0)
    fw = fin_w * np.sin(np.pi * np.clip(tt, 0, 1) ** 0.8)
    # outer side of the curve: the side away from the tail's centre of curvature
    mid = cv.at_s((f0 + L) / 2)
    chord_mid = (cv.at_s(f0) + cv.at_s(L)) / 2
    nmid = cv.normal_s((f0 + L) / 2)
    fs = -1.0 if float(np.dot(mid - chord_mid, nmid)) < 0 else 1.0
    if fin[1]:
        fs = fin[1]
    edge_in = Pf + Nf * (fs * Hf)[:, None] * 0.5
    edge_out = Pf + Nf * (fs * (Hf + fw))[:, None]
    fin_reg = Polygon(np.vstack([edge_in, edge_out[::-1]])).buffer(0)
    body = biggest(K.U(body, fin_reg).buffer(0.6, quad_segs=6).buffer(-0.6, quad_segs=6))
    # gills: three feathery red fronds per side, from the back of the head
    gill_regs = []
    p, tg, nrm, h = frame(gill_s)
    for sg in (1, -1):
        out = nrm * sg
        for j, (ang, ln) in enumerate(zip((-35.0, 0.0, 35.0), gill_len)):
            a = math.radians(ang)
            u = out * math.cos(a) + tg * math.sin(a)                   # + leans toward the tail
            b0 = p + out * (h - 1.5) + tg * (j - 1) * 3.0
            b1 = b0 + u * ln
            v = np.array([-u[1], u[0]])
            frond = K.R(K.vesica(b0 - u * 1.0, b1, gill_w))
            # fimbriae: two small side nubs (feathery)
            nubs = [Point(*(b0 + u * ln * f + v * s * 1.9)).buffer(1.35, quad_segs=6) for f, s in ((0.42, 1), (0.68, -1))]
            gill_regs.append(K.U(frond, *nubs))
    gills = K.U(*gill_regs).buffer(0.4, quad_segs=6).buffer(-0.4, quad_segs=6)
    eyes = C.Frag()
    p, tg, nrm, h = frame(eye_s)
    for sg in (1, -1):
        eyes += K.dot(p + nrm * sg * eye_off, 3.0, role="eye")
    return {"body": body, "ko": ko, "gills": gills, "eyes": eyes, "L": L, "spine": sp}


def mirror(c, r_field=48.0, r_frame=58.0, *, handle_to=512.0, handle_w=12.0, sal_pts=None,
           ripple=((-75.0, 5.0), (105.0, 185.0)), knop_y=None, sal_kw=None):
    """The scrying mirror (§H.2): a gold frame ring (``r_field`` → ``r_frame``)
    with a FINE Aquifer rule round its middle and Aquifer bead dots, a jade
    field, and in it the blind salamander as a vision — paper (the jade is cut
    away), its gills red, its eyes Ø3 Aquifer dots under the skin — ringed by
    ripple arcs knocked out of the jade. A gold handle (``handle_w`` wide)
    runs down from the frame to ``handle_to`` with a knop. → Part (the
    frame + handle), plus meta['field'] for halos."""
    c = P(c)
    field = Point(*c).buffer(r_field, quad_segs=64)
    ring = Point(*c).buffer(r_frame, quad_segs=64).difference(field)
    # handle: a collar under the frame, the grip, a knop at the foot
    top = c[1] + r_frame - 4.0
    grip = K.box(c[0] - handle_w / 2, top, c[0] + handle_w / 2, handle_to)
    collar = Point(c[0], c[1] + r_frame + 3.0).buffer(10.0, quad_segs=24)
    ky = knop_y if knop_y is not None else handle_to - 8.0
    knop = Point(c[0], ky).buffer(9.5, quad_segs=24)
    handle = K.U(grip, collar, knop)
    shape = K.U(field, ring, handle)
    lines = C.Frag()
    lines += K.outline(K.circle(c, r_field))
    lines += K.clip_out(K.outline(handle), Point(*c).buffer(r_frame), eps=-0.5, trap=0.0)
    # frame: FINE rule round the middle + beads
    rm = (r_field + r_frame) / 2
    lines += K.line(K.circle(c, rm + 2.0), FINE, role="frame-rule")
    # handle detail: knop and collar rings
    lines += K.clip_out(K.outline(collar), Point(*c).buffer(r_frame), eps=-0.5, trap=0.0)
    lines += K.outline(knop)
    fills = K.fill(K.U(ring, handle), GOLD)
    # the vision
    sal = salamander(sal_pts, **(sal_kw or {})) if sal_pts is not None else None
    ko = C.Frag()
    red = C.Frag()
    eyes = C.Frag()
    if sal:
        body = sal["body"]
        # knockout lines + body: the paper holes; gills sit in their own paper hole (3 px rim)
        holes = K.U(body, sal["ko"].shape(), sal["gills"])
        ko_reg = holes
        red += K.fill(sal["gills"], RED, role="gill")
        eyes += sal["eyes"]
    else:
        ko_reg = Polygon()
    # ripple arcs (§G.8): groups of three concentric arcs about the field
    # centre, gaps growing ×1.3 inward→outward, cut 3.5 px clear of the vision
    rip = C.Frag()
    r_out = r_field - MEDIUM / 2 - K.GAP_MARK - KO / 2 - 0.4
    g0 = KO + K.GAP_MARK + 0.2
    radii = [r_out, r_out - g0 * 1.3, r_out - g0 * 1.3 - g0]
    for (a0, a1) in ripple:
        for k, R_ in enumerate(radii):
            sh = 6.0 * k
            rip += C.stroke(K.arc_c(c, R_, a0 + sh, a1 - sh), KO, role="ripple")
    if not ko_reg.is_empty:
        rip = C.cut(rip, ko_reg, K.GAP_MARK + 0.6)
        keep = []
        for m in rip.marks:
            pcs = [p for p, _ in G.flatten(m.d, 0.1)]
            pcs = [p for p in pcs if len(p) > 1 and LineString(p).length >= 12.0]
            if pcs:
                keep.append(m.__class__(**{**m.__dict__, "d": "".join(C.polyline_d(p) for p in pcs)}))
        rip = C.Frag(keep)
    jade_field = field.difference(ko_reg).difference(rip.shape())
    fills += K.fill(jade_field, JADE, role="mirror-field") + red
    return K.Part(shape, fills, lines + eyes, {"field": field, "ring": ring, "c": c, "sal": sal})


# -----------------------------------------------------------------------------
# Texas mountain laurel (regalia sprig in a gold posy-holder)
# -----------------------------------------------------------------------------
def leaflet(p0, p1, width):
    """One glossy leaflet: a vesica-ish oval (rounded, not pointed: two arcs +
    rounded tip) → region."""
    p0, p1 = P(p0), P(p1)
    reg = K.R(K.vesica(p0, p1, width))
    return reg.buffer(-1.2).buffer(2.2, quad_segs=8).buffer(-1.0, quad_segs=8)


def pinnate_leaf(base, heading, length, *, n_pairs=3, leaf_len=22.0, leaf_w=11.0, bend=6.0, terminal=True):
    """A pinnate compound leaf: a rachis from ``base`` along ``heading``
    (screen deg) curving ``bend``; ``n_pairs`` opposite leaflets + a terminal
    one, all jade with an Aquifer outline, a MEDIUM midrib stub and a paper
    gloss crescent knocked out on the upper half. → Part."""
    base = P(base)
    end = base + K.unit(heading) * length
    d = K.arc_sag(base, end, bend)
    rp = C.sample_d(d, 0.5)[0][0]
    cv = G.Curve(rp)
    L = cv.length
    regs = []
    for k in range(n_pairs):
        s = L * (0.32 + 0.60 * k / max(n_pairs, 1))
        p = cv.at_s(s)
        tg = cv.tangent_s(s)
        nrm = cv.normal_s(s)
        ll = leaf_len * (1.0 - 0.06 * k)
        for sg in (1, -1):
            u = tg * math.cos(math.radians(55)) + nrm * sg * math.sin(math.radians(55))
            q0 = p + u * 2.0
            q1 = p + u * ll
            regs.append(leaflet(q0, q1, leaf_w * (1.0 - 0.05 * k)))
    if terminal:
        tg = cv.tangent_s(L)
        regs.append(leaflet(end - tg * 1.0, end + tg * leaf_len * 0.95, leaf_w))
    leaves = regs
    return leaves, rp


def laurel_sprig(stem_base, stem_top, *, leaves_spec, raceme_top, raceme_len=64.0, raceme_bend=6.0,
                 raceme_heading=100.0, n_florets=7, floret_r=6.5):
    """Texas mountain laurel (§H.2): glossy pinnate leaves (jade, Aquifer
    outline, MEDIUM midribs) on a short stem, and a pendant raceme of pea
    flowers in PAPER outline (each floret a small rounded standard petal on a
    short FINE pedicel from a MEDIUM axis). Returns dict of Parts:
    stem, leaves (one Part), raceme."""
    stem_base, stem_top = P(stem_base), P(stem_top)
    stem = LineString([tuple(stem_base), tuple(stem_top)]).buffer(3.4, cap_style=1)
    leaf_regs = []
    rachises = []
    for spec in leaves_spec:
        regs, rp = pinnate_leaf(**spec)
        leaf_regs += regs
        rachises.append(rp)
    leaves = K.U(*leaf_regs)
    llines = C.Frag()
    for rg in leaf_regs:
        llines += K.outline(rg)
    # gloss: a paper crescent knocked out near each leaflet's edge
    gloss = C.Frag()
    for rg in leaf_regs:
        inner = rg.buffer(-(MEDIUM / 2 + K.GAP_MARK + 1.6))
        if inner.is_empty or inner.area < 30:
            continue
        mrr = inner.minimum_rotated_rectangle
        xy = np.asarray(mrr.exterior.coords)[:4]
        e = [(np.hypot(*(xy[(i + 1) % 4] - xy[i])), i) for i in range(4)]
        e.sort()
        i = e[-1][1]
        a0, a1 = xy[i], xy[(i + 1) % 4]
        ln = LineString([tuple(a0 + (a1 - a0) * 0.25), tuple(a0 + (a1 - a0) * 0.75)])
        gl = ln.intersection(inner)
        for g in K._lines_of(gl):
            if g.length > 5:
                gloss += C.stroke(C.polyline_d(np.asarray(g.coords)), KO, role="gloss")
    leaf_fill = K.fill(C.knockout(K.D(leaves), gloss) if gloss else K.D(leaves), JADE, role="laurel")
    rach = C.Frag()
    for rp in rachises:
        rach += K.clip_out(K.line(C.polyline_d(rp), MEDIUM, role="rachis"), K.Polygon(), eps=0)
    # raceme: a drooping axis from raceme_top; pea florets (teardrops: round
    # banner, pointed keel) on short pedicels, alternating sides, shrinking to
    # a tip of closed buds — a hanging cluster, not a bunch of grapes
    rt = P(raceme_top)
    ax_d = K.arc_sag(rt, rt + K.unit(raceme_heading) * raceme_len, raceme_bend)
    ax_pts = C.sample_d(ax_d, 0.5)[0][0]
    acv = G.Curve(ax_pts)
    AL = acv.length
    florets, fl_lines = [], C.Frag()
    rows = n_florets
    for k in range(rows):
        t = 0.10 + 0.78 * k / (rows - 1)
        p = acv.at_s(AL * t)
        tg = acv.tangent_s(AL * t)
        nrm = acv.normal_s(AL * t)
        sg = 1 if k % 2 == 0 else -1
        r = floret_r * (1.0 - 0.42 * t)
        v = nrm * sg * 0.80 + tg * 0.60                         # outward and down the axis
        v = v / np.hypot(*v)
        q = p + v * (r + 3.5)                                    # banner centre, clear of the axis
        banner = Point(*q).buffer(r, quad_segs=16)
        keel = K.R(K.vesica(q, q + v * r * 1.9, r * 1.25))
        fl = K.U(banner, keel).buffer(0.5, quad_segs=6).buffer(-0.5, quad_segs=6)
        florets.append(fl)
        fl_lines += K.outline(fl)
        fl_lines += K.seg(p, q - v * (r - 0.5), MEDIUM, role="pedicel")
    tip = acv.at_s(AL)
    bud = Point(*tip).buffer(floret_r * 0.42, quad_segs=12)
    florets.append(bud)
    fl_lines += K.outline(bud)
    axis_line = K.line(C.polyline_d(np.array([acv.at_s(s) for s in np.linspace(0, AL - floret_r * 0.42, 60)])),
                       MEDIUM, role="raceme-axis")
    rac = K.U(*florets, LineString([tuple(q_) for q_ in ax_pts]).buffer(MEDIUM / 2 + 0.2))
    flines = fl_lines + axis_line
    return {"stem": K.Part(stem, K.fill(stem, GOLD), K.outline(stem), {}),
            "leaves": K.Part(leaves, leaf_fill, llines + rach, {"regs": leaf_regs}),
            "raceme": K.Part(rac, C.Frag(), flines, {"florets": florets})}


# -----------------------------------------------------------------------------
# drip-fringe cuff
# -----------------------------------------------------------------------------
def drip_fringe_ko(sleeve_part, cuff_part, *, n=6, l_min=8.0, l_max=20.0):
    """§G.14 drip fringe hanging from a cuff's lower edge down the sleeve,
    KNOCKED OUT of the jade sleeve (paper strokes + Ø6.3 terminals): vertical
    (along the sleeve axis) strokes whose lengths follow one slow sine period.
    Returns the sleeve Part with its fill knocked out."""
    m = sleeve_part.meta
    W, u, nn = m["W"], m["u"], m["n"]
    cuff = cuff_part.shape
    # the cuff's lower edge centre: move down the sleeve from the wrist until outside the cuff
    s = 0.0
    while cuff.contains(Point(*(W - u * s))) and s < 60:
        s += 0.5
    base = W - u * (s + K.GAP_MARK * 0.0)
    sl = sleeve_part.shape
    # width across at the base
    xline = LineString([tuple(base + nn * 80), tuple(base - nn * 80)]).intersection(sl)
    hw = xline.length / 2 if not xline.is_empty else 15.0
    ko = C.Frag()
    usable = hw - (MEDIUM / 2 + K.GAP_MARK + K.TD / 2 + 0.5)
    for i in range(n):
        t = (i + 0.5) / n
        off = (t - 0.5) * 2 * usable
        Lk = l_min + (l_max - l_min) * (0.5 + 0.5 * math.sin(math.pi * t))
        p0 = base + nn * off + u * 2.0
        p1 = p0 - u * Lk
        ko += C.stroke(C.polyline_d([p0, p1]), KO, role="drip")
        ko += C.dot(p1[0], p1[1], K.TD, role="drip-t")
    fills = sleeve_part.fills
    new = C.Frag()
    for mk in fills.marks:
        if mk.kind == "fill":
            new += K.fill(C.knockout(mk.d, ko), mk.color, role=mk.role)
        else:
            new += C.Frag([mk])
    return K.Part(sl, new, sleeve_part.lines, sleeve_part.meta)


# -----------------------------------------------------------------------------
# hair under the veil
# -----------------------------------------------------------------------------
def hair_under_veil(edge_pts, bottom_y, *, n=2, stagger=10.0, round_r=9.0, face=None):
    """Gold hair (§H.2 'gold hair in current lines under the veil'): two
    locks inside the veil's face-opening edge (``edge_pts``, far → over the
    brow → near), cut level at ``bottom_y`` and rounded into lock ends
    (``round_r``), to stack BEHIND the head and neck and in front of the ruff:
    only the strips between the veil edge and the face show. Current lines
    (§G.24) run down each side as offsets of the veil edge, 7 px apart, each
    rolling into a Ø6.3 terminal where the lock ends (placed against the
    visible strip: ``face`` (region) is subtracted before fitting them)."""
    _, pe, _ = FM.arc_spline(edge_pts)
    pe = np.asarray(pe)
    reg = Polygon(np.vstack([pe, [[pe[-1][0], bottom_y + 40], [pe[0][0], bottom_y + 40]]])).buffer(0)
    reg = biggest(reg).intersection(K.box(-1e4, -1e4, 1e4, bottom_y))
    reg = reg.buffer(-round_r, quad_segs=12).buffer(round_r, quad_segs=12)
    reg = biggest(reg)
    i_top = int(np.argmin(pe[:, 1]))
    vis = reg.difference(face.buffer(K.CONTOUR / 2)) if face is not None else reg
    lines = C.Frag()
    far = pe[:i_top + 1][::-1]
    near = pe[i_top:]
    far_reg = vis.intersection(K.box(-1e4, -1e4, pe[i_top][0], 1e4))
    near_reg = vis.intersection(K.box(pe[i_top][0], -1e4, 1e4, 1e4))
    lines += K.current_lines(far, n, far_reg, side=+1, edge=MEDIUM, stagger=stagger)
    lines += K.current_lines(near, n, near_reg, side=-1, edge=MEDIUM, stagger=stagger)
    return K.Part(reg, K.fill(reg, GOLD), lines + K.outline(reg), {"edge": pe})


def hair_lock(guide_pts, widths, *, n_lines=2, stagger=9.0, line_from=0.25, bias=0.0, profile=(0.35, 1.0)):
    """A lock of gold hair (§G.24): a ribbon along the arc spline
    ``guide_pts`` (root under the veil → free end) whose width runs through
    ``widths`` (a list of (t, w) pairs, t = fraction of length), the free end
    rounded (a rolled lock end). ``n_lines`` FINE current lines run along it,
    7 px apart about the guide (+ ``bias``), from ``line_from`` of the way
    down, each rolling into a Ø6.3 terminal near the end (staggered). → Part."""
    _, gp, _ = FM.arc_spline(guide_pts)
    cv = G.Curve(np.asarray(gp))
    L = cv.length
    ss = np.linspace(0, L, 260)
    Pp = np.array([cv.at_s(s) for s in ss])
    Nn = np.array([cv.normal_s(s) for s in ss])
    t = ss / L
    w = np.interp(t, [a for a, _ in widths], [b for _, b in widths])
    left = Pp + Nn * (w / 2)[:, None]
    right = Pp - Nn * (w / 2)[:, None]
    reg = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    reg = K.U(reg, Point(*Pp[-1]).buffer(w[-1] / 2, quad_segs=16))
    reg = biggest(reg.buffer(0.5, quad_segs=6).buffer(-0.5, quad_segs=6))
    k0 = int(line_from * (len(ss) - 1))
    guide = Pp[k0:]
    first = bias - (n_lines - 1) * K.PITCH / 2
    lines = K.current_lines(guide, n_lines, reg, side=+1, first=first, edge=CONTOUR, stagger=stagger)
    return K.Part(reg, K.fill(reg, GOLD), lines + K.outline(reg), {"guide": gp})


def hair_frame(head_region, *, far=13.0, near=18.0, bottom_y=268.0, axis_x=None, n_lines=1, round_r=6.0):
    """Gold hair parted and smoothed back under the veil (§H.2 'gold hair in
    current lines under the veil'), Renaissance-Madonna fashion: a band
    framing the face, ``far`` px wide on the far cheek and ``near`` px on the
    near side (a 3/4 head shows more of its back), cut at ``bottom_y`` with
    rounded lock ends. Current lines (§G.24) follow its outer edge. Stack it
    behind the head; the veil crown in front covers its top. → Part (meta
    'outer' = its outer edge region, the veil's opening)."""
    hx0, hy0, hx1, hy1 = head_region.bounds
    ax = (hx0 + hx1) / 2 if axis_x is None else axis_x
    grown_far = head_region.buffer(far, quad_segs=24)
    grown_near = head_region.buffer(near, quad_segs=24)
    outer = K.U(grown_far.intersection(K.box(-1e4, -1e4, ax, 1e4)),
                grown_near.intersection(K.box(ax, -1e4, 1e4, 1e4))).buffer(3.0, quad_segs=12).buffer(-3.0, quad_segs=12)
    reg = outer.intersection(K.box(-1e4, -1e4, 1e4, bottom_y))
    reg = biggest(reg.buffer(-round_r, quad_segs=12).buffer(round_r, quad_segs=12))
    vis = reg.difference(head_region.buffer(MEDIUM / 2))
    ring = [np.asarray(reg.exterior.coords)]
    lines = C.Frag()
    # guide: the outer edge from the far lock end, over the top, to the near lock end
    ext = np.asarray(reg.exterior.coords)
    top_i = int(np.argmin(ext[:, 1]))
    ext = np.vstack([ext[top_i:], ext[1:top_i + 1]])            # start at the top
    # split into the two sides at the lowest points
    lows = np.argsort(ext[:, 1])[::-1]
    xs = ext[:, 0]
    # far side: points left of the axis, walking from the top counter-clockwise
    for sgn in (-1, 1):
        side_pts = []
        seq = ext if sgn > 0 else ext[::-1]
        for q in seq:
            if (q[0] - ax) * sgn < -2 and len(side_pts) > 2:
                break
            side_pts.append(q)
            if q[1] >= bottom_y - round_r - 1:
                break
        side_pts = np.asarray(side_pts)
        if len(side_pts) > 5:
            sreg = vis.intersection(K.box(ax if sgn > 0 else -1e4, -1e4, 1e4 if sgn > 0 else ax, 1e4))
            lines += K.current_lines(side_pts, n_lines, sreg, side=(-1 if sgn > 0 else +1), edge=MEDIUM, stagger=8.0)
    return K.Part(reg, K.fill(reg, GOLD), lines + K.outline(reg), {"outer": outer})
