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
    salamander       (superseded: the mirror now draws art/_qs_sal.salamander via mirror(sal_build=))
    laurel_sprig     Texas mountain laurel: pinnate glossy leaves (jade) + pendant raceme (paper)
    drip_cuff        a cuff band whose drip fringe (§G.14) is knocked out of the sleeve below it
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
import shapely.ops
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
    if clip is not None and stop is not None:
        # the far points go behind the veil's contour with the band
        stone = K.U(*[g for g in K._polys_of(stone.intersection(clip)) if g.area > 4.0])
        kites = [k_.intersection(clip) for k_ in kites]
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
SAL_HW = [(0.000, 0.0), (0.004, 5.4), (0.018, 7.2), (0.055, 8.0), (0.095, 8.2), (0.122, 7.5),
          (0.150, 4.8), (0.190, 4.4), (0.290, 5.0), (0.400, 4.9), (0.470, 4.3), (0.540, 3.5),
          (0.700, 2.5), (0.860, 1.3), (1.000, 0.0)]


def salamander(spine_pts, *, eye_s=0.058, eye_off=3.1, gill_s=0.172, fore_s=0.235, hind_s=0.455,
               limb=(10.0, 9.5), limb_a=(-20.0, 60.0), toe=4.6, fin=(0.50, 0.0), fin_w=4.2, gill_len=(10.0, 11.0, 9.5),
               gill_w=3.4, gill_angles=(18.0, 58.0, 98.0), gill_step=1.2, limb_w=None):
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
            ko += C.stroke(C.polyline_d([sh, el, wr]), limb_w or KO, role="limb")
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
        for j, (ang, ln) in enumerate(zip(gill_angles, gill_len)):
            a = math.radians(ang)
            u = out * math.cos(a) + tg * math.sin(a)                   # + leans toward the tail
            q0 = p + tg * (j - 1) * gill_step
            b0 = q0 + out * (h - 1.8)
            b1 = b0 + u * ln
            v = np.array([-u[1], u[0]])
            frond = K.R(K.vesica(b0 - u * 1.0, b1, gill_w))
            # fimbriae: two small side nubs (feathery)
            nubs = [Point(*(b0 + u * ln * f + v * s * 1.9)).buffer(1.35, quad_segs=6) for f, s in ((0.42, 1), (0.68, -1))]
            gill_regs.append(K.U(frond, *nubs))
    gills = K.U(*gill_regs).buffer(0.4, quad_segs=6).buffer(-0.4, quad_segs=6)
    eyes = C.Frag()
    # the vestigial eyes: two Ø3 dots under the skin, placed where both keep
    # 3.2 px of paper to the body's edge and to the gills (searched along the head)
    safe = body.buffer(-(1.5 + 3.1)).difference(gills.buffer(1.5 + 3.1))
    best = None
    for fr in np.linspace(eye_s - 0.02, eye_s + 0.04, 25):
        p, tg, nrm, h = frame(fr)
        qa, qb = p + nrm * eye_off, p - nrm * eye_off
        if safe.contains(Point(*qa)) and safe.contains(Point(*qb)):
            d_ = abs(fr - eye_s)
            if best is None or d_ < best[0]:
                best = (d_, qa, qb)
    if best is not None:
        eyes += K.dot(best[1], 3.0, role="eye") + K.dot(best[2], 3.0, role="eye")
    return {"body": body, "ko": ko, "gills": gills, "eyes": eyes, "L": L, "spine": sp}


def mirror(c, r_field=40.0, r_frame=56.0, *, handle_to=512.0, handle_w=12.0, sal_pts=None,
           ripple=((-75.0, 5.0), (105.0, 185.0)), knop_y=None, sal_kw=None, beads=12, bead_d=4.2, bead_phase=0.0,
           collar_r=11.0, knops=(), sal_build=None):
    """The scrying mirror (§H.2: 'gold frame, Ø110'): a gold frame ring
    (``r_field`` → ``r_frame``) set with ``beads`` Aquifer bead dots (§G.9
    bubble beading, the spring's bubbles), a jade field, and in it the blind
    salamander as a VISION — paper (the jade is cut away), its gills red, its
    eyes Ø3 Aquifer dots under the skin — ringed by ripple arcs knocked out of
    the jade (§G.8). Below, a gold handle (``handle_w`` wide) on a collar,
    with ``knops`` (y, r) and a foot knop at ``handle_to``. ``sal_build(c)``
    (e.g. art._qs_sal.salamander) supplies the vision; else the legacy
    ``salamander(sal_pts)``. → Part (meta 'field', 'ring', 'sal')."""
    c = P(c)
    field = Point(*c).buffer(r_field, quad_segs=64)
    disc = Point(*c).buffer(r_frame, quad_segs=64)
    ring = disc.difference(field)
    top = c[1] + r_frame - 6.0
    grip = K.box(c[0] - handle_w / 2, top, c[0] + handle_w / 2, handle_to)
    collar = Point(c[0], c[1] + r_frame + 2.0).buffer(collar_r, quad_segs=24)
    ky = knop_y if knop_y is not None else handle_to - 8.0
    parts = [grip, collar, Point(c[0], ky).buffer(9.5, quad_segs=24)]
    for (yk, rk) in knops:
        parts.append(Point(c[0], yk).buffer(rk, quad_segs=24))
    handle = K.U(*parts)
    shape = K.U(field, ring, handle)
    lines = C.Frag()
    lines += K.outline(K.circle(c, r_field))
    # the handle's own joints: each knop's outline where it stands proud of the grip
    lines += K.clip_out(K.outline(handle), disc, eps=-0.5, trap=0.0)
    for g in parts[1:]:
        edge = g.boundary.intersection(grip.buffer(-0.4)).difference(disc.buffer(K.GAP_MARK + MEDIUM))
        for ln in K._lines_of(edge):
            if ln.length > 6.0:
                lines += K.line(C.polyline_d(np.asarray(ln.coords)), MEDIUM, role="knop")
    # the frame's inset rule (a FINE ring 4.2+ clear of both edges), broken
    # where the handle collar joins
    rr_ = r_field + MEDIUM / 2 + K.GAP + FINE / 2 + 0.2
    rule = K.line(K.circle(c, rr_), FINE, role="frame-rule")
    lines += K.clip_out(rule, collar.buffer(K.GAP_MARK + MEDIUM / 2), eps=0.0, trap=0.0) if beads else rule
    fills = K.fill(K.U(ring, handle), GOLD)
    if sal_build is not None:
        sal = sal_build(c)
    else:
        sal = salamander(sal_pts, **(sal_kw or {})) if sal_pts is not None else None
    red = C.Frag()
    eyes = C.Frag()
    if sal:
        ko_reg = K.U(sal["body"], sal["ko"].shape(), sal["gills"])
        for pc in K._polys_of(sal["gills"]):          # one mark per plume (no piece is a 'crumb')
            red += K.fill(pc, RED, role="gill")
        eyes += sal["eyes"]
    else:
        ko_reg = Polygon()
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
def drip_fringe_ko(sleeve_part, cuff_part, *, n=3, pitch=7.8, l_min=3.0, l_max=17.0):
    """§G.14 drip fringe hanging from a cuff's lower edge down the sleeve,
    KNOCKED OUT of the jade sleeve (MEDIUM paper strokes + Ø6.3 terminals):
    ``n`` strokes along the sleeve axis at ``pitch`` px (≥ 3 px of jade
    between a terminal and the next stroke, the outer terminals ≥ 3 px inside
    the sleeve's outline), their lengths on one slow sine (short–long–short).
    Each starts under the cuff, so it hangs from the cuff's edge. A drip that
    would not keep that paper is dropped whole. Returns the sleeve Part with
    its fill knocked out (meta 'drips': the knockout Frag).

    (It used to measure the cuff's lower edge from the wrist point, which
    lies on the cuff's top edge and so is not inside it: the drips started at
    the cuff's TOP, six of them 3 px apart, and all that showed below the cuff
    was one lumpy paper blob.)"""
    m = sleeve_part.meta
    W, u, nn = P(m["W"]), P(m["u"]), P(m["n"])
    cuff = cuff_part.shape
    sl = sleeve_part.shape
    inner = sl.buffer(-(MEDIUM / 2 + K.GAP_MARK), quad_segs=12)
    # centre the fringe on the sleeve's cross-section just below the cuff (a sagged
    # sleeve is not symmetric about the wrist point's axis)
    s = 0.0
    while not cuff.contains(Point(*(W - u * s))) and s < 30.0:
        s += 0.25
    while cuff.contains(Point(*(W - u * s))) and s < 60.0:
        s += 0.25
    xs = LineString([tuple(W - u * (s + 3.0) + nn * 80), tuple(W - u * (s + 3.0) - nn * 80)]).intersection(sl)
    if not xs.is_empty:
        xs = max(K._lines_of(xs), key=lambda g: g.length)
        mid = np.asarray(xs.interpolate(0.5, normalized=True).coords[0])
        W = W + nn * float(np.dot(mid - (W - u * (s + 3.0)), nn))
    ko = C.Frag()
    for i in range(n):
        off = (i - (n - 1) / 2) * pitch
        t = (i + 0.5) / n
        Lk = l_min + (l_max - l_min) * math.sin(math.pi * t)
        q = W + nn * off
        s = 0.0
        while not cuff.contains(Point(*(q - u * s))) and s < 30.0:     # into the cuff …
            s += 0.25
        while cuff.contains(Point(*(q - u * s))) and s < 60.0:         # … and out through its lower edge
            s += 0.25
        p0 = q - u * (s - 2.0)                                        # 2 px under the cuff
        p1 = p0 - u * (Lk + 2.0)
        drip = C.stroke(C.polyline_d([p0, p1]), KO, role="drip") + C.dot(p1[0], p1[1], K.TD, role="drip-t")
        body = LineString([tuple(q - u * (s + 0.5)), tuple(p1)]).buffer(KO / 2).union(
            Point(*p1).buffer(K.TD / 2, quad_segs=12))
        if inner.contains(body):
            ko += drip
    fills = sleeve_part.fills
    new = C.Frag()
    for mk in fills.marks:
        if mk.kind == "fill":
            new += K.fill(C.knockout(mk.d, ko), mk.color, role=mk.role)
        else:
            new += C.Frag([mk])
    return K.Part(sl, new, sleeve_part.lines, {**sleeve_part.meta, "drips": ko})


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


def stalactite_circlet(far_end, mid, near_end, *, h=9.0, xs, lengths, widths, head=0.18, axis_min=8.5,
                       jewel=None, clip=None, fringe=False, top_k=0.36, stop=None):
    """The stalactite diadem (§H.2): a gold circlet ``h`` tall on the arc
    far_end → mid → near_end, hung with graduated STALACTITE points (§G.13
    kites, widest at ``head`` of their length) that fall plumb from its
    lower edge at the given ``xs`` with the given ``lengths``/``widths``.
    Kites ≥ ``axis_min`` wide carry the FINE split axis (the growth line).
    ``stop`` (a line, e.g. the veil's inner contour): the circlet ends where
    its centreline meets it (the crossing nearest ``near_end``) in a round
    cap centred on that line; ``clip`` still trims the far end.
    → Part (meta 'band', 'kites', 'arc', 'end')."""
    far_end, mid, near_end = P(far_end), P(mid), P(near_end)
    band_d = K.arc3(far_end, mid, near_end)
    cl = C.sample_d(band_d, 0.4)[0][0]
    cline = LineString(cl)
    arc_full = cl                                   # meta 'arc': the whole circlet line (the veil's dome split)
    end = None
    if stop is not None:
        hit = cline.intersection(stop)
        xs_ = [g for g in getattr(hit, "geoms", [hit]) if g.geom_type == "Point"]
        if xs_:
            e = max(xs_, key=lambda q: cline.project(q))
            cline = shapely.ops.substring(cline, 0.0, cline.project(e))
            cl = np.asarray(cline.coords)
            end = np.array([e.x, e.y])
    band = cline.buffer(h / 2, cap_style=1, quad_segs=10)
    band_full = band
    if clip is not None:
        band = biggest(band.intersection(clip))

    def low_y(x):
        # the lower edge of the whole circlet (a point hung where the far
        # contour already hides the band still hangs from its true edge)
        ln = LineString([(x, -1000), (x, 2000)]).intersection(band_full)
        return ln.bounds[3] if not ln.is_empty else mid[1] + h / 2

    kites, axes = [], C.Frag()
    for x, L, w in zip(xs, lengths, widths):
        top = low_y(x) - 2.0
        yw = top + 2.0 + L * head
        if fringe:
            # an icicle fringe: each point hangs from the band's edge at its full width
            kite = Polygon([(x - w / 2, top - 1.0), (x + w / 2, top - 1.0), (x + w / 2, top + 2.0),
                            (x, top + 2.0 + L), (x - w / 2, top + 2.0)])
        else:
            kite = Polygon([(x - w * top_k, top), (x + w * top_k, top), (x + w / 2, yw), (x, top + 2.0 + L),
                            (x - w / 2, yw)])
        kites.append(kite)
        if w >= axis_min:
            axes += K.seg(P(x, top + 2.0 + K.GAP_MARK + 0.6), P(x, top + 2.0 + L - 5.0), FINE, role="axis")
    stone = K.U(*kites)
    if clip is not None and stop is not None:
        # the far points go behind the veil's contour with the band
        stone = K.U(*[g for g in K._polys_of(stone.intersection(clip)) if g.area > 4.0])
        kites = [k_.intersection(clip) for k_ in kites]
    shape = K.U(band, stone)
    if fringe:
        lines = K.outline(shape)
    else:
        lines = K.clip_out(K.outline(stone), band, eps=-0.8, trap=0.0) + K.outline(band)
    lines += K.clip_out(axes, band.buffer(K.GAP_MARK + MEDIUM / 2), eps=0.0, trap=0.0)
    fills = K.fill(shape, GOLD)
    if jewel is not None:
        jw = K.jewel(jewel[0], jewel[1])
        lines = K.clip_out(lines, jw.shape, eps=0.0, trap=0.0, extra=jw.shape.buffer(K.GAP + MEDIUM))
        return K.Part(shape.union(jw.shape), fills + jw.fills, lines + jw.lines, {"band": band, "kites": kites})
    meta = {"band": band, "kites": kites, "arc": arc_full}
    if end is not None:
        meta["end"] = end
    return K.Part(shape, fills, lines, meta)


def gill_frond(root, tip, *, sag=8.0, n=6, side=+1, spine_w=(10.0, 4.4), barb_len=(20.0, 7.0),
               barb_w=(8.0, 5.2), angle=48.0, curve=0.16, t0=0.22, t1=0.9, barb_round=True, spine_ko=0.0,
               tip_dot=True, color=RED, both=False, barb_ko=False):
    """§G.15 gill plume at ruff scale — a solid red frond: a tapering spine
    band ``root`` → ``tip`` (bulging ``sag``, + = left of travel) with ``n``
    rounded BARBS on one side (``side`` +1 = left of travel) swept ``angle``°
    toward the tip, shortening ``barb_len[0]`` → ``[1]`` (6–8 barbs,
    §G.15), gently bowed toward the tip like a feather's barbs; the tip a
    rounded end (the Ø4.2 tip dot of §G.15 at this scale). One MEDIUM
    outline round the union. ``spine_ko`` > 0: a paper knockout line along
    the spine where it is wide enough (§I.12). → Part (meta 'spine')."""
    root, tip = P(root), P(tip)
    sp = C.sample_d(K.arc_sag(root, tip, sag), 0.5)[0][0]
    cv = G.Curve(sp)
    L = cv.length
    ss = np.linspace(0, L, 200)
    t = ss / L
    hw = spine_w[0] / 2 + (spine_w[1] / 2 - spine_w[0] / 2) * t
    Pp = np.array([cv.at_s(s) for s in ss])
    Nn = np.array([cv.normal_s(s) for s in ss])
    left, right = Pp + Nn * hw[:, None], Pp - Nn * hw[:, None]
    body = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    body = K.U(body, Point(*Pp[-1]).buffer(hw[-1] + 0.6, quad_segs=12))
    regs = [body]
    sides = (side, -side) if both else (side,)
    for sd in sides:
        for k in range(n):
            tk = t0 + (t1 - t0) * k / max(n - 1, 1)
            s = tk * L
            p = cv.at_s(s)
            tg = cv.tangent_s(s)
            nr = cv.normal_s(s) * sd
            h = float(np.interp(s, ss, hw))
            ln = barb_len[0] + (barb_len[1] - barb_len[0]) * k / max(n - 1, 1)
            if both and sd != side:
                ln *= 0.7
            bw = barb_w[0] + (barb_w[1] - barb_w[0]) * k / max(n - 1, 1)
            a = math.radians(angle)
            u = nr * math.cos(a) + tg * math.sin(a)
            b0 = p + nr * (h - 1.0)
            b1 = b0 + u * ln
            # bow toward the tip: the barb's mid pushed along the spine tangent
            mid = (b0 + b1) / 2 + tg * curve * ln
            arc = C.sample_d(K.arc3(b0, mid, b1), 0.4)[0][0]
            acv = G.Curve(arc)
            AL = acv.length
            sb = np.linspace(0, AL, 40)
            bp = np.array([acv.at_s(x) for x in sb])
            bn = np.array([acv.normal_s(x) for x in sb])
            ww = (bw / 2) * (1.0 - 0.45 * (sb / AL))
            bl, br = bp + bn * ww[:, None], bp - bn * ww[:, None]
            bar = Polygon(np.vstack([bl, br[::-1]])).buffer(0)
            if barb_round:
                bar = K.U(bar, Point(*bp[-1]).buffer(ww[-1], quad_segs=10))
            regs.append(bar)
    shape = K.U(*regs).buffer(1.2, quad_segs=8).buffer(-1.2, quad_segs=8)
    shape = biggest(shape.buffer(0))
    ko = C.Frag()
    if spine_ko:
        safe = shape.buffer(-(KO / 2 + K.GAP_MARK + MEDIUM / 2 + 0.2))
        sp_pts = np.array([cv.at_s(s) for s in np.linspace(0.04 * L, spine_ko * L, 60)])
        ko = K.clip_in(C.stroke(C.polyline_d(sp_pts), KO, role="ko-spine"), safe)
    fills = K.fill(C.knockout(K.D(shape), ko) if ko else K.D(shape), color, role="plume")
    return K.Part(shape, fills, K.outline(shape), {"spine": sp})


def plume(root, tip, *, width=34.0, sag=8.0, n=5, side=+1, t_scallop=(0.22, 0.97), depth=4.5, widest=0.42,
          tip_r=5.0, spine=(0.06, 0.86), barb_reach=0.72, barb_lean=0.10, color=RED, root_w=None,
          hatch=None, hatch_lean=38.0, ko_w=None):
    """§G.15 gill plume at ruff scale: a red feathery frond — a lanceolate
    web on a curved spine ``root`` → ``tip`` (bulging ``sag``, + = left of
    travel), widest at ``widest`` of its length, the tip ROUNDED (r
    ``tip_r``: a gill's soft end, never a flame's point). Its feathered side
    (``side`` +1 = left of travel) is cut into ``n`` scallops (the barbs,
    shortening toward the tip); the other side is plain. The spine and the
    barb partings (from each notch in toward the spine, leaning toward the
    tip) are KNOCKED OUT to paper at MEDIUM (§C.4), 3 px clear of the edge.
    → Part (meta 'spine', 'notches')."""
    root, tip = P(root), P(tip)
    sp = C.sample_d(K.arc_sag(root, tip, sag), 0.5)[0][0]
    cv = G.Curve(sp)
    L = cv.length
    ss = np.linspace(0, L, 240)
    t = ss / L
    Pp = np.array([cv.at_s(s) for s in ss])
    Nn = np.array([cv.normal_s(s) for s in ss]) * side          # toward the feathered side
    # width profile: two arcs (vesica-like), widest at `widest`, rounded to tip_r at the end
    rw = (root_w if root_w is not None else width * 0.45) / 2
    prof = np.where(t < widest, rw + (width / 2 - rw) * np.sin(np.pi / 2 * t / widest),
                    tip_r + (width / 2 - tip_r) * np.cos(np.pi / 2 * (t - widest) / (1 - widest)))
    w_out = prof * 1.08
    w_in = prof * 0.92
    outer = Pp + Nn * w_out[:, None]
    inner = Pp - Nn * w_in[:, None]
    ta = np.linspace(t_scallop[0], t_scallop[1], n + 1)
    idx = [int(np.clip(round(tt * (len(ss) - 1)), 0, len(ss) - 1)) for tt in ta]
    notch = [outer[k] - Nn[k] * min(depth, 0.3 * w_out[k]) for k in idx]
    path = K.Path(inner[-1])
    for q in inner[::-1][1:]:
        path.line(q)
    for q in outer[1:idx[0]]:
        path.line(q)
    path.line(notch[0])
    for j in range(n):
        a, b = notch[j], notch[j + 1]
        chord = float(np.hypot(*(b - a)))
        path.sag(b, (chord * 0.30 + depth * 0.6) * side)
    for q in outer[idx[-1]:]:
        path.line(q)
    path.close()
    shape = biggest(K.R(path.d).buffer(0))
    shape = K.U(shape, Point(*Pp[-1]).buffer(tip_r, quad_segs=12))
    shape = biggest(shape.buffer(1.0, quad_segs=8).buffer(-1.0, quad_segs=8))
    kw = KO if ko_w is None else ko_w
    ko = C.Frag()
    k0, k1 = int(spine[0] * (len(ss) - 1)), int(spine[1] * (len(ss) - 1))
    ko += C.stroke(C.polyline_d(Pp[k0:k1 + 1]), kw, role="ko-spine")
    if hatch:
        # §B.2 half-hatching in knockout: the feathered half is cut by paper
        # barbs at a ``hatch`` pitch, each leaving the spine and leaning
        # ``hatch_lean``° toward the tip (a feather's vane)
        s_ = hatch * 0.6
        while s_ < L * 0.93:
            p0 = cv.at_s(s_)
            tg = cv.tangent_s(s_)
            nr = cv.normal_s(s_) * side
            a = math.radians(hatch_lean)
            u = nr * math.cos(a) + tg * math.sin(a)
            ko += C.stroke(C.polyline_d([p0, p0 + u * width]), kw, role="ko-barb")
            s_ += hatch / math.cos(a)
    else:
        for j in range(1, n):
            k = idx[j]
            c_in = notch[j]
            target = Pp[min(k + int(barb_lean * len(ss)), len(ss) - 1)]
            ko += C.stroke(C.polyline_d([c_in, c_in + (target - c_in) * barb_reach]), kw, role="ko-barb")
    safe = shape.buffer(-(K.GAP_MARK + kw / 2 + CONTOUR / 2 + 0.2))
    ko = K.clip_in(ko, safe)
    fills = K.fill(C.knockout(K.D(shape), ko) if ko else K.D(shape), color, role="plume")
    return K.Part(shape, fills, K.outline(shape), {"spine": sp, "notches": notch})


def compound_leaf(base, heading, length, *, pairs=(0.34, 0.66), leaf=(17.0, 9.6), spread=52.0, bend=5.0,
                  shrink=0.08, terminal=1.05, gloss=True):
    """A Texas mountain-laurel leaf (pinnate, §H.2 'glossy pinnate leaves'):
    a MEDIUM rachis from ``base`` along ``heading`` bending ``bend``, opposite
    leaflet pairs at the ``pairs`` stations spread ``spread``° from it and a
    terminal leaflet; each leaflet a rounded oval (jade, own outline) with a
    small paper GLOSS crescent knocked out near its upper edge. →
    (list of leaflet regions, rachis points, gloss Frag)."""
    base = P(base)
    end = base + K.unit(heading) * length
    rp = C.sample_d(K.arc_sag(base, end, bend), 0.5)[0][0]
    cv = G.Curve(rp)
    L = cv.length
    regs = []
    for k, t in enumerate(pairs):
        s = L * t
        p = cv.at_s(s)
        tg = cv.tangent_s(s)
        nrm = cv.normal_s(s)
        ll = leaf[0] * (1.0 - shrink * (len(pairs) - 1 - k))
        ww = leaf[1] * (1.0 - shrink * (len(pairs) - 1 - k))
        for sg in (1, -1):
            u = tg * math.cos(math.radians(spread)) + nrm * sg * math.sin(math.radians(spread))
            regs.append(leaflet(p + u * 1.5, p + u * ll, ww))
    tg = cv.tangent_s(L)
    regs.append(leaflet(end - tg * 1.5, end + tg * leaf[0] * terminal, leaf[1]))
    gl = C.Frag()
    if gloss:
        for rg in regs:
            inner = rg.buffer(-(MEDIUM / 2 + K.GAP_MARK + KO / 2 + 0.2))
            if inner.is_empty or inner.area < 12:
                continue
            mrr = inner.minimum_rotated_rectangle
            xy = np.asarray(mrr.exterior.coords)[:4]
            e = sorted([(np.hypot(*(xy[(i + 1) % 4] - xy[i])), i) for i in range(4)])
            i = e[-1][1]
            a0, a1 = xy[i], xy[(i + 1) % 4]
            ln = LineString([tuple(a0 + (a1 - a0) * 0.22), tuple(a0 + (a1 - a0) * 0.70)]).intersection(inner)
            for g in K._lines_of(ln):
                if g.length > 4.5:
                    gl += C.stroke(C.polyline_d(np.asarray(g.coords)), KO, role="gloss")
    return regs, rp, gl


def laurel_posy(mouth, axis_deg, *, holder_len=40.0, holder_w=(13.0, 6.0), leaves=(), raceme=None, layered=False):
    """The Texas mountain laurel sprig held as REGALIA (§H.0 care rule:
    plants appear as regalia): set in a slim gold posy-holder (a cone whose
    ``mouth`` is at the top, pointing ``axis_deg``; ``holder_len`` long, widths
    (mouth, foot)) — the fist closes round the holder, never the plant. From
    the mouth: ``leaves`` [(heading, length, bend, spec…)] glossy pinnate
    leaves in jade, and a pendant ``raceme`` (heading, length, bend, n,
    floret_r) of pea flowers in PAPER outline. ``layered``: a later leaf lies
    in front of an earlier one where their leaflets cross. → dict of Parts:
    holder, leaves, raceme."""
    mouth = P(mouth)
    u = K.unit(axis_deg)
    foot = mouth - u * holder_len
    nrm = np.array([-u[1], u[0]])
    w0, w1 = holder_w
    cone = Polygon([tuple(mouth + nrm * w0 / 2), tuple(mouth - nrm * w0 / 2), tuple(foot - nrm * w1 / 2),
                    tuple(foot + nrm * w1 / 2)])
    lip = LineString([tuple(mouth + nrm * (w0 / 2 + 2.0)), tuple(mouth - nrm * (w0 / 2 + 2.0))]).buffer(3.4, cap_style=1)
    knob = Point(*(foot - u * 2.0)).buffer(w1 / 2 + 2.2, quad_segs=16)
    holder = K.U(cone, lip, knob).buffer(0.6, quad_segs=6).buffer(-0.6, quad_segs=6)
    hl = K.outline(holder)
    # the lip's lower edge: a MEDIUM line across the cone
    ring_ln = LineString([tuple(mouth - u * 3.6 + nrm * 20), tuple(mouth - u * 3.6 - nrm * 20)]).intersection(
        holder.buffer(-0.5))
    for g in K._lines_of(ring_ln):
        hl += K.line(C.polyline_d(np.asarray(g.coords)), MEDIUM, role="holder-lip")
    all_regs, rachises, gloss = [], [], C.Frag()
    per_leaf = []
    for spec in leaves:
        hd, ln, bd = spec[:3]
        kw = spec[3] if len(spec) > 3 else {}
        regs, rp, gl = compound_leaf(mouth + K.unit(hd) * 2.0, hd, ln, bend=bd, **kw)
        all_regs += regs
        rachises.append(rp)
        per_leaf.append((regs, rp, gl))
    leaf_shape = K.U(*all_regs)
    llines = C.Frag()
    for i, (regs, rp, gl) in enumerate(per_leaf):
        f_i = C.Frag()
        for rg in regs:
            f_i += K.outline(rg)
        f_i += K.line(C.polyline_d(rp), MEDIUM, role="rachis")
        front = K.U(*[g for (rr, _, _) in per_leaf[i + 1:] for g in rr]) if layered and i + 1 < len(per_leaf) \
            else Polygon()
        if not front.is_empty:
            # the leaves overlap in LAYERS (a later leaf in front): where a front leaflet
            # crosses one behind, the one behind stops under its outline (no crossed outlines)
            f_i = K.clip_out(f_i, front)
            gl = K.clip_out(gl, front.buffer(MEDIUM / 2 + K.GAP_MARK + KO / 2, quad_segs=8), eps=0.0, trap=0.0)
            gl = C.Frag([m for m in gl.marks if m.d and LineString(
                np.asarray(G.as_polys(m.d, 0.1)[0][0])).length > 4.5]) if gl.marks else gl
        llines += f_i
        gloss += gl
    leaf_fill = K.fill(C.knockout(K.D(leaf_shape), gloss) if gloss else K.D(leaf_shape), JADE, role="laurel")
    out = {"holder": K.Part(holder, K.fill(holder, GOLD), hl, {}),
           "leaves": K.Part(leaf_shape.union(K.U(*[LineString(r).buffer(MEDIUM / 2) for r in rachises])),
                            leaf_fill, llines, {"regs": all_regs})}
    if raceme is not None:
        hd, ln, bd, n, fr = raceme
        rt = mouth + K.unit(hd) * 3.0
        ax_d = K.arc_sag(rt, rt + K.unit(hd) * ln, bd)
        ax_pts = C.sample_d(ax_d, 0.5)[0][0]
        acv = G.Curve(ax_pts)
        AL = acv.length
        florets, fl_lines = [], C.Frag()
        for k in range(n):
            t = 0.16 + 0.74 * k / (n - 1)
            p = acv.at_s(AL * t)
            tg = acv.tangent_s(AL * t)
            nr = acv.normal_s(AL * t)
            sg = 1 if k % 2 == 0 else -1
            r = fr * (1.0 - 0.40 * t)
            v = nr * sg * 0.78 + tg * 0.62
            v = v / np.hypot(*v)
            q = p + v * (r + 3.4)
            banner = Point(*q).buffer(r, quad_segs=16)
            keel = K.R(K.vesica(q, q + v * r * 1.8, r * 1.2))
            fl = K.U(banner, keel).buffer(0.5, quad_segs=6).buffer(-0.5, quad_segs=6)
            florets.append(fl)
            fl_lines += K.outline(fl)
            fl_lines += K.seg(p, q - v * (r - 0.5), MEDIUM, role="pedicel")
        tip = acv.at_s(AL)
        bud = Point(*tip).buffer(fr * 0.45, quad_segs=12)
        florets.append(bud)
        fl_lines += K.outline(bud)
        axis_line = K.line(C.polyline_d(np.array([acv.at_s(s) for s in np.linspace(0, AL - fr * 0.45, 60)])),
                           MEDIUM, role="raceme-axis")
        rac = K.U(*florets, LineString([tuple(q_) for q_ in ax_pts]).buffer(MEDIUM / 2 + 0.2))
        out["raceme"] = K.Part(rac, C.Frag(), fl_lines + axis_line, {"florets": florets})
    return out


# -----------------------------------------------------------------------------
# stalactite fringe circlet (pass 4+)
# -----------------------------------------------------------------------------
def fringe_circlet(far_end, mid, near_end, *, h=10.0, xs, lengths, widths, clip=None, shoulder=0.30,
                   axis_min=11.0, tip_r=1.2, bead=None):
    """The stalactite diadem (§H.2): a gold circlet ``h`` tall whose centre
    line is the arc far_end → mid → near_end, hung with graduated STALACTITE
    points (§G.13) that fall plumb from its lower edge at ``xs`` (card x),
    ``lengths`` and ``widths``. Neighbouring points meet at the band, so the
    fringe is ONE gold shape (no crowding slivers between separate kites):
    each point keeps its full width for ``shoulder`` of its length, then
    tapers along two straight sides to a sharp tip (a stalactite, never a
    tooth: long and slender). The largest points (≥ ``axis_min`` wide) carry
    the FINE growth axis. → Part (meta 'band', 'arc', 'tips')."""
    far_end, mid, near_end = P(far_end), P(mid), P(near_end)
    cl = C.sample_d(K.arc3(far_end, mid, near_end), 0.4)[0][0]
    band = LineString(cl).buffer(h / 2, cap_style=2, quad_segs=10)
    if clip is not None:
        band = biggest(band.intersection(clip))

    def low_y(x):
        ln = LineString([(x, -1000), (x, 2000)]).intersection(band)
        return ln.bounds[3] if not ln.is_empty else mid[1] + h / 2

    pts, tips, axes = [], [], C.Frag()
    for x, L, w in zip(xs, lengths, widths):
        y0 = low_y(x) - 1.5
        ys = y0 + 1.5 + L * shoulder
        tip = P(x, y0 + 1.5 + L)
        kite = Polygon([(x - w / 2, y0), (x + w / 2, y0), (x + w / 2, ys), tuple(tip), (x - w / 2, ys)])
        pts.append(kite)
        tips.append(tip)
        if w >= axis_min:
            axes += K.seg(P(x, y0 + 1.5 + K.GAP_MARK + MEDIUM / 2 + 1.0), P(x, tip[1] - 6.0), FINE, role="axis")
    stone = K.U(*pts)
    shape = K.U(band, stone).buffer(0.4, join_style=2).buffer(-0.4, join_style=2)
    lines = K.outline(shape)
    # the band's lower edge across each point's root (the joint of point and band)
    edge = LineString(cl).offset_curve(-h / 2) if False else None
    lines += axes
    fills = K.fill(shape, GOLD)
    return K.Part(shape, fills, lines, {"band": band, "arc": cl, "tips": tips})


# -----------------------------------------------------------------------------
# Texas mountain laurel, pass 5: a sprig (stem + pinnate leaves + pendant raceme)
# -----------------------------------------------------------------------------
def oval(p0, p1, width):
    """A rounded leaflet: an ellipse-like oval from p0 to p1 (two arcs, both
    ends rounded). → region."""
    p0, p1 = P(p0), P(p1)
    L = float(np.hypot(*(p1 - p0)))
    c = (p0 + p1) / 2
    ang = math.degrees(math.atan2(*(p1 - p0)[::-1]))
    e = shapely.affinity.scale(Point(0, 0).buffer(1.0, quad_segs=32), L / 2, width / 2)
    return shapely.affinity.translate(shapely.affinity.rotate(e, ang, origin=(0, 0)), c[0], c[1])


def pinnate(base, heading, length, *, pairs=2, leaflet=(15.0, 8.6), spread=58.0, bend=4.0, shrink=0.10,
            t0=0.30, terminal=1.1):
    """One pinnate compound leaf (§H.2 'glossy pinnate leaves'): a rachis from
    ``base`` along ``heading`` bending ``bend``, ``pairs`` opposite leaflet
    pairs from ``t0`` to the tip, and a terminal leaflet; leaflets are
    rounded ovals. → (leaflet regions, rachis points)."""
    base = P(base)
    end = base + K.unit(heading) * length
    rp = C.sample_d(K.arc_sag(base, end, bend), 0.5)[0][0]
    cv = G.Curve(rp)
    L = cv.length
    regs = []
    for k in range(pairs):
        t = t0 + (0.86 - t0) * (k / max(pairs - 1, 1)) if pairs > 1 else 0.6
        s = L * t
        p, tg, nrm = cv.at_s(s), cv.tangent_s(s), cv.normal_s(s)
        f = 1.0 - shrink * (pairs - 1 - k) * -1 if False else 1.0 - shrink * k
        ll, ww = leaflet[0] * f, leaflet[1] * f
        for sg in (1, -1):
            u = tg * math.cos(math.radians(spread)) + nrm * sg * math.sin(math.radians(spread))
            regs.append(oval(p + u * 1.0, p + u * (ll + 1.0), ww))
    tg = cv.tangent_s(L)
    f = 1.0 - shrink * pairs
    regs.append(oval(end - tg * 1.0, end + tg * leaflet[0] * terminal * max(f, 0.7), leaflet[1] * max(f, 0.7)))
    return regs, rp


def raceme(top, heading, length, *, n=8, r=(6.2, 3.0), bend=4.0, style="drops", spread=62.0):
    """The pendant flower cluster (§H.2 'a pendant flower cluster in paper
    outline'): florets down a drooping axis from ``top`` (heading ``heading``,
    bending ``bend``), alternating sides, shrinking r[0] → r[1] toward a
    closed bud at the tip. ``style``:
      'drops'  each pea floret a paper teardrop hung outward on a short pedicel
               (the deck's hung-vesica floret, §G.5, rounded for a pea flower);
      'pairs'  florets in opposite pairs of small rounded bells.
    → (floret regions, axis points, pedicel segments)."""
    top = P(top)
    end = top + K.unit(heading) * length
    ax = C.sample_d(K.arc_sag(top, end, bend), 0.5)[0][0]
    cv = G.Curve(ax)
    L = cv.length
    fl, peds = [], []
    for k in range(n):
        t = 0.12 + 0.80 * k / max(n - 1, 1)
        s = L * t
        p, tg, nrm = cv.at_s(s), cv.tangent_s(s), cv.normal_s(s)
        rr = r[0] + (r[1] - r[0]) * t
        sides = (1, -1) if style == "pairs" else ((1,) if k % 2 == 0 else (-1,))
        for sg in sides:
            a = math.radians(spread)
            u = tg * math.cos(a) + nrm * sg * math.sin(a)          # outward and down the axis
            q = p + u * (rr + 3.6)
            if style == "pairs":
                shape = Point(*q).buffer(rr, quad_segs=16)
            elif style == "fans":
                # a pea flower from the side: the banner a round fan opening
                # outward-down from its base at the axis
                q = p + u * (rr * 0.35)
                a0 = math.degrees(math.atan2(u[1], u[0]))
                shape = Polygon([tuple(q)] + [tuple(K.polar(q, rr * 1.35, a0 + d)) for d in np.linspace(-62, 62, 25)])
                shape = shape.buffer(1.2, quad_segs=6).buffer(-1.2, quad_segs=6)
            else:
                shape = K.R(K.vesica(q - u * rr * 0.2, q + u * rr * 2.2, rr * 1.9)).union(
                    Point(*(q + u * rr * 0.6)).buffer(rr * 0.95, quad_segs=16))
            fl.append(shape)
            peds.append((p, q))
    tip = cv.at_s(L)
    fl.append(Point(*tip).buffer(r[1] * 0.9, quad_segs=12))
    return fl, ax, peds


def laurel_sprig2(mouth, axis_deg, stem_pts, *, holder_len=34.0, holder_w=(12.0, 6.0), leaves=(), rac=None,
                  rac_kw=None):
    """Texas mountain laurel as REGALIA (§H.0 care rule): a sprig set in a slim
    gold posy-holder whose mouth is at ``mouth`` (the fist closes round the
    holder, never the plant). From the mouth a woody stem (MEDIUM) runs
    through ``stem_pts``; ``leaves`` [(t, heading, length, kw)] are pinnate
    leaves in jade springing from the stem at fraction t; ``rac`` (t, heading,
    length) the pendant raceme in paper outline hanging from the stem.
    → dict of Parts: holder, stem, leaves, raceme."""
    mouth = P(mouth)
    u = K.unit(axis_deg)
    foot = mouth - u * holder_len
    nrm = np.array([-u[1], u[0]])
    w0, w1 = holder_w
    cone = Polygon([tuple(mouth + nrm * w0 / 2), tuple(mouth - nrm * w0 / 2), tuple(foot - nrm * w1 / 2),
                    tuple(foot + nrm * w1 / 2)])
    lip = LineString([tuple(mouth + nrm * (w0 / 2 + 2.2)), tuple(mouth - nrm * (w0 / 2 + 2.2))]).buffer(3.6,
                                                                                                   cap_style=1)
    knob = Point(*(foot - u * 2.0)).buffer(w1 / 2 + 2.4, quad_segs=16)
    holder = K.U(cone, lip, knob).buffer(0.6, quad_segs=6).buffer(-0.6, quad_segs=6)
    hl = K.outline(holder)
    ring_ln = LineString([tuple(mouth - u * 3.8 + nrm * 20), tuple(mouth - u * 3.8 - nrm * 20)]).intersection(
        holder.buffer(-0.5))
    for g in K._lines_of(ring_ln):
        hl += K.line(C.polyline_d(np.asarray(g.coords)), MEDIUM, role="holder-lip")
    sp = np.asarray(FM.arc_spline([mouth] + [P(q) for q in stem_pts], h_start=axis_deg)[1])
    scv = G.Curve(sp)
    SL = scv.length
    stem_reg = LineString(sp).buffer(MEDIUM / 2 + 0.6, cap_style=1)
    regs, rachises = [], []
    for (t, hd, ln, kw) in leaves:
        b = scv.at_s(SL * t)
        rg, rp = pinnate(b, hd, ln, **kw)
        regs += rg
        rachises.append(rp)
    leaf_shape = K.U(*regs)
    llines = C.Frag()
    for rg in regs:
        llines += K.outline(rg)
    rach_reg = K.U(*[LineString(r_).buffer(MEDIUM / 2 + 0.3) for r_ in rachises])
    for r_ in rachises:
        llines += K.line(C.polyline_d(r_), MEDIUM, role="rachis")
    out = {"holder": K.Part(holder, K.fill(holder, GOLD), hl, {}),
           "stem": K.Part(stem_reg, C.Frag(), K.line(C.polyline_d(sp), MEDIUM, role="stem"), {}),
           "leaves": K.Part(K.U(leaf_shape, rach_reg), K.fill(leaf_shape, JADE), llines, {"regs": regs})}
    if rac is not None:
        t, hd, ln = rac
        top = scv.at_s(SL * t)
        fl, ax, peds = raceme(top, hd, ln, **(rac_kw or {}))
        axis_reg = LineString(ax).buffer(MEDIUM / 2 + 0.3)
        # painter's order: the axis, then florets top → bottom (each hides the one above)
        flo = [K.Part(axis_reg, C.Frag(), K.line(C.polyline_d(ax), MEDIUM, role="raceme-axis"), {})]
        for f_ in fl:
            flo.append(K.Part(f_, C.Frag(), K.outline(f_), {}))
        rreg = K.U(*fl, axis_reg)
        out["florets"] = flo
        out["raceme"] = K.Part(rreg, C.Frag(), C.Frag(), {"florets": fl})
    return out


# -----------------------------------------------------------------------------
# paper pockets between a fist and the attribute it holds
# -----------------------------------------------------------------------------
def paper_pocket(sc, name, members, window, *, host, r=8.0, halo_only=None, min_area=2.0):
    """The ground left between the named scene items (each grown by its paper
    channel, ``halo`` + MEDIUM/2) and ``host`` (the region of the hand that
    is stacked NEXT, in front) that is narrower than 2·``r`` inside
    ``window`` turns to paper, closing on round arcs — the kit's heel
    treatment (courtkit.Hand.add_to, HEEL_CLOSE) for the pocket between a
    thumb, the attribute's stem and what hangs from it: no coloured wedge or
    sliver pinched between three outlines. Adds an empty item whose paper
    channel is the pocket (``halo_only``: the grounds it clears); its own
    region is a sliver of ``host``, so it hides nothing that shows.
    → the pocket region (empty when there is none)."""
    regs = [K.R(host)]
    for it in sc.items:
        if it.name in members and it.occ is not None and not it.occ.is_empty:
            regs.append(it.occ.buffer(it.halo + MEDIUM / 2, quad_segs=12) if it.halo else it.occ)
    both = K.U(*regs)
    gap = both.buffer(r, quad_segs=12).buffer(-r, quad_segs=12).difference(both)
    gap = gap.intersection(K.R(window))
    pcs = [g for g in K._polys_of(gap) if g.area > min_area]
    if not pcs:
        return Polygon()
    gap = K.U(*pcs)
    occ = K.R(host).intersection(gap.buffer(2.0, quad_segs=8))
    if occ.is_empty:
        return Polygon()
    sc.add(name, C.Frag(), occ, sil=False, halo=K.HALO, halo_only=halo_only, halo_zone=gap.union(occ))
    return gap

