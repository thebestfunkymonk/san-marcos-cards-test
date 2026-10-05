"""art/_qh_attr.py — the Q♥ attributes (§H.5): the arrowhead sceptre and the air hose.

ARROWHEAD (*Sagittaria*, held upright on the viewer's right — the tall
attribute) as REGALIA (§H.0 care rules: plants appear as regalia): a wrought
gold stem with sheathing collars at its nodes; from the upper node a gold
petiole carries ONE ARROW-SHAPED JADE LEAF standing up (a sagittate blade:
a pointed tip, two long basal lobes pointing down and out, the petiole in
the sinus; arching FINE veins converging on the tip; one half hatched
perpendicular to the midrib); the stem ends in a THREE-PETALLED PAPER
FLOWER (three broad rounded petals, each half-hatched, three small pointed
jade sepals between them, a gold centre with a Ø4.2 dot). Arrowhead is a
common native of the Spring Lake vents — not an endangered plant.

AIR-HOSE RIBBON (§H.5): a jade ribbon curling up from behind the far
shoulder toward the top-right, carrying a column of rising bubbles knocked
out to paper (Ø3 → 8, growing as they rise); at its open end the air
escapes as free bubbles (FINE rings, Ø ≥ 8.4; Ø4.2/6.3 dots) — all ≥ 12 px
inside the frame.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C

P = K.P
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR
JADE, GOLD, RED, INK = K.JADE, K.GOLD, K.RED, K.INK


def _rot(p, c, deg):
    a = math.radians(deg)
    v = P(p) - P(c)
    return P(c) + P(v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def arrow_leaf(sinus, *, tilt=0.0, blade=66.0, half_w=23.0, widest=0.30, lobe=(30.0, 36.0), notch=(7.0, 18.0),
               hatch_side=+1, veins=True):
    """A sagittate leaf, its petiole joining at ``sinus``, pointing up and
    turned ``tilt`` degrees (clockwise) about the sinus.

    blade    tip height above the sinus; ``half_w`` its half-width at
             ``widest`` × blade above the sinus;
    lobe     (dx, dy) of each basal lobe tip from the sinus (down and out);
    notch    (dx, dy): the inner lobe edges leave the sinus through
             (±dx, dy) toward the lobe tips.
    → Part (meta tip, sinus, lobes)."""
    S = P(sinus)

    def q(x, y):
        return _rot(S + P(x, y), S, tilt)
    T = q(0.0, -blade)
    Wl, Wr = q(-half_w, -blade * widest), q(half_w, -blade * widest)
    Ll, Lr = q(-lobe[0], lobe[1]), q(lobe[0], lobe[1])
    # outer edges: tip → widest → a shoulder → the lobe tip (one G1 arc spline each side)
    shr, shl = q(half_w * 0.98, 4.0), q(-half_w * 0.98, 4.0)
    _, pr, _ = K.FM.arc_spline([T, Wr, shr, Lr])
    _, pl, _ = K.FM.arc_spline([Ll, shl, Wl, T])
    # inner lobe edges: lobe tip → notch → sinus
    nr, nl = q(notch[0], notch[1]), q(-notch[0], notch[1])
    _, ir, _ = K.FM.arc_spline([Lr, nr, S + (q(0, 1.0) - S)])
    _, il, _ = K.FM.arc_spline([S + (q(0, 1.0) - S), nl, Ll])
    ring = np.vstack([np.asarray(pr), np.asarray(ir)[1:], np.asarray(il)[1:], np.asarray(pl)[1:]])
    reg = Polygon(ring).buffer(0)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    lines = C.Frag()
    fills = K.fill(reg, JADE)
    inner = reg.buffer(-(MEDIUM / 2 + K.GAP_MARK + FINE / 2 + 0.2))
    # midrib (MEDIUM) from the sinus toward the tip
    mid0, mid1 = q(0.0, -2.0), q(0.0, -blade + 11.0)
    lines += K.seg(mid0, mid1, MEDIUM, role="vein")
    if veins:
        # arching veins: from the sinus along each side, converging toward the tip
        for sg in (-1, 1):
            a0 = q(sg * 2.0, -4.0)
            aw = q(sg * half_w * 0.52, -blade * widest)
            a1 = q(sg * 3.5, -blade + 16.0)
            _, vp, _ = K.FM.arc_spline([a0, aw, a1])
            lines += K.clip_in(K.line(C.polyline_d(np.asarray(vp)), FINE, role="vein"), inner)
            # a vein into each lobe
            lp = Ll if sg < 0 else Lr
            lv0 = q(sg * 3.0, 1.5)
            lv1 = lp + (S - lp) * 0.30
            lines += K.clip_in(K.line(K.arc_sag(lv0, lv1, -sg * 2.0), FINE, role="vein"), inner)
    # one half of the blade hatched perpendicular to the midrib (not the lobes)
    half = reg.intersection(K.halfplane(q(0, 40), q(0, -blade), side=hatch_side))
    half = half.difference(K.halfplane(q(-80, -1.5), q(80, -1.5), side=-1))
    ang = -90.0 + tilt
    hatch = K.hatch_in(half, angle=ang + 90.0, origin=tuple(S))
    # the hatch stays off the arching vein on that side (it stops on the midrib and the outline)
    lines += hatch
    lines = K.outline(reg) + lines
    return K.Part(reg, fills, lines, {"tip": T, "sinus": S, "lobes": (Ll, Lr)})


def flower(c, *, r_petal=27.0, petal_w=30.0, rot=-90.0, centre_r=8.4, hatch_side=+1, sepal_len=0.95):
    """A three-petalled flower facing the viewer: broad rounded (obovate) paper
    petals at ``rot`` + 120°·k, each with a FINE midline and one half
    hatched; three small pointed jade sepals between them (behind); a gold
    centre disc with an Aquifer contour and a Ø4.2 dot. → list of (name,
    Part) in painter's order."""
    c = P(c)
    parts = []
    seps = []
    for k in range(3):
        a = rot + 60.0 + 120.0 * k
        tip = K.polar(c, r_petal * sepal_len, a)
        seps.append(K.R(K.vesica(K.polar(c, 3.0, a), tip, 12.0)))
    sreg = shapely.union_all(seps)
    parts.append(("sepals", K.Part(sreg, K.fill(sreg, JADE), K.outline(sreg), {})))
    pet = []
    for k in range(3):
        a = rot + 120.0 * k
        tip = K.polar(c, r_petal, a)
        mid = K.polar(c, r_petal * 0.60, a)
        hw = petal_w / 2
        pl = mid + K.unit(a - 90.0) * hw
        pr = mid + K.unit(a + 90.0) * hw
        base_l = K.polar(c, 2.5, a - 60.0)
        base_r = K.polar(c, 2.5, a + 60.0)
        d, _, _ = K.FM.arc_spline([base_l, pl, tip, pr, base_r])
        reg = K.R(d + "Z").buffer(0)
        pet.append((reg, a, tip))
    petals = shapely.union_all([g for g, _, _ in pet])
    lines = K.outline(petals)
    disc_zone = K.R(K.circle(c, centre_r + MEDIUM / 2 + K.GAP_MARK))
    for reg, a, tip in pet:
        lines += K.clip_out(K.outline(reg), petals.buffer(-0.01).difference(reg.buffer(0.01)), eps=0.0, trap=0.0)
        rib0 = K.polar(c, centre_r + 3.5, a)
        rib1 = K.polar(c, r_petal - 8.0, a)
        lines += K.seg(rib0, rib1, FINE, role="petal-rib")
        half = reg.intersection(K.halfplane(c, tip, side=hatch_side)).difference(disc_zone)
        lines += K.hatch_in(half, angle=a + 90.0, origin=tuple(c))
    parts.append(("petals", K.Part(petals, C.Frag(), lines, {})))
    disc = K.R(K.circle(c, centre_r))
    parts.append(("centre", K.Part(disc, K.fill(disc, GOLD), K.outline(disc, MEDIUM) + K.dot(c, 4.2), {})))
    return parts


def stem(p0, p1, w=14.0, *, nodes=(), node_w=6.0, node_h=7.0, color=GOLD):
    """A straight gold stem from p0 (bottom) to p1 (top), ``w`` wide, with
    sheathing collars (``node_w`` px wider, ``node_h`` tall) at the given
    heights (fractions 0–1 of the length). → Part."""
    p0, p1 = P(p0), P(p1)
    u = (p1 - p0) / np.hypot(*(p1 - p0))
    L = float(np.hypot(*(p1 - p0)))
    reg = LineString([tuple(p0), tuple(p1)]).buffer(w / 2, cap_style=2)
    cols = []
    for t in nodes:
        c = p0 + u * L * t
        cols.append(LineString([tuple(c - u * node_h / 2), tuple(c + u * node_h / 2)]).buffer(
            (w + node_w) / 2, cap_style=2).buffer(1.5, quad_segs=6).buffer(-1.5, quad_segs=6))
    shape = shapely.union_all([reg] + cols)
    lines = K.outline(shape)
    for cg in cols:
        lines += K.clip_in(K.outline(cg), reg.buffer(-0.01))
    return K.Part(shape, K.fill(shape, color), lines, {"u": u})


def petiole(p0, p1, w=8.0, sag=0.0, color=GOLD):
    """A curved gold petiole (an arc of sagitta ``sag``) of width ``w``."""
    d = K.arc_sag(P(p0), P(p1), sag)
    pts = C.sample_d(d, 0.5)[0][0]
    reg = LineString(pts).buffer(w / 2, cap_style=2, quad_segs=8)
    return K.Part(reg, K.fill(reg, color), K.outline(reg), {"pts": pts})


def ribbon(points, *, w=18.0, bub=(3.0, 8.0), ratio=1.16, gap=5.0, start=16.0, end_gap=12.0):
    """The air-hose ribbon: a jade band ``w`` wide along an arc spline through
    ``points`` (root behind the shoulder → open end), a column of bubbles on
    its centreline KNOCKED OUT to paper, Ø ``bub[0]`` → ``bub[1]`` growing
    ×``ratio`` as they rise, with ``gap`` px of jade between them.
    → Part (meta end, heading, pts)."""
    d, pts, _ = K.FM.arc_spline([P(q) for q in points])
    pts = np.asarray(pts)
    reg = LineString(pts).buffer(w / 2, cap_style=2, quad_segs=16)
    cv = K.G.Curve(pts)
    Lt = cv.length
    holes = []
    s_ = start
    dd = bub[0]
    while True:
        dc = min(dd, bub[1])
        if s_ + dc > Lt - end_gap:
            break
        c = cv.at_s(s_ + dc / 2)
        holes.append(Point(*c).buffer(dc / 2, quad_segs=24))
        s_ += dc + gap
        dd *= ratio
    solid = reg.difference(shapely.union_all(holes)) if holes else reg
    end = pts[-1]
    head = math.degrees(math.atan2(pts[-1][1] - pts[-4][1], pts[-1][0] - pts[-4][0]))
    return K.Part(reg, K.fill(solid, JADE), K.outline(reg), {"end": end, "heading": head, "pts": pts})


def free_bubbles(points_sizes):
    """Escaping bubbles: [(point, Ø)] — Ø ≤ 6.3 solid dots (legal Ø4.2 /
    6.3), larger FINE rings (centreline Ø). → Frag."""
    f = C.Frag()
    for p, d in points_sizes:
        if d <= 6.3:
            f += K.dot(p, d, role="bubble")
        else:
            f += C.stroke(K.circle(P(p), d / 2), FINE, color=INK, role="bubble")
    return f


# -----------------------------------------------------------------------------
# v4: the flower, the leaf veins, the hose
# -----------------------------------------------------------------------------
def flower2(c, *, r_petal=34.0, petal_w=36.0, rot=-90.0, centre_r=11.0, hatch_side=+1, sepal=(0.92, 13.0),
            stamen_d=4.2, stamen_n=0, widest=0.66, claw=40.0):
    """The arrowhead flower (three broad obovate paper petals at ``rot`` +
    120°·k, each with ONE half hatched perpendicular to its axis — no midrib,
    so the hatch reads as the petal's shade, not a ladder), three pointed
    jade sepals between them (behind), and a gold centre of stamens: a gold
    disc with an Aquifer contour and a ring of Ø4.2 paper knockouts round a
    Ø4.2 Aquifer dot. → list of (name, Part), back to front."""
    c = P(c)
    parts = []
    seps = []
    for k in range(3):
        a = rot + 60.0 + 120.0 * k
        tip = K.polar(c, r_petal * sepal[0], a)
        seps.append(K.R(K.vesica(K.polar(c, 4.0, a), tip, sepal[1])))
    sreg = shapely.union_all(seps)
    parts.append(("sepals", K.Part(sreg, K.fill(sreg, JADE), K.outline(sreg), {})))
    pet = []
    for k in range(3):
        a = rot + 120.0 * k
        tip = K.polar(c, r_petal, a)
        mid = K.polar(c, r_petal * widest, a)
        hw = petal_w / 2
        pl = mid + K.unit(a - 90.0) * hw
        pr = mid + K.unit(a + 90.0) * hw
        base_l = K.polar(c, 4.0, a - claw)
        base_r = K.polar(c, 4.0, a + claw)
        d, _, _ = K.FM.arc_spline([base_l, pl, tip, pr, base_r])
        reg = K.R(d + "Z").buffer(0)
        pet.append((reg, a, tip))
    petals = shapely.union_all([g for g, _, _ in pet])
    lines = K.outline(petals)
    disc_zone = K.R(K.circle(c, centre_r + MEDIUM / 2 + K.GAP_MARK + 0.5))
    for i, (reg, a, tip) in enumerate(pet):
        # the seam between neighbouring petals
        others = shapely.union_all([g for j, (g, _, _) in enumerate(pet) if j != i])
        lines += K.clip_out(K.outline(reg), petals.buffer(-0.01).difference(reg.buffer(0.01)), eps=0.0, trap=0.0)
        half = reg.intersection(K.halfplane(c, tip, side=hatch_side)).difference(disc_zone)
        half = half.difference(others.buffer(0.01))
        lines += K.hatch_in(half, angle=a + 90.0, origin=tuple(c))
    parts.append(("petals", K.Part(petals, C.Frag(), lines, {})))
    disc = K.R(K.circle(c, centre_r))
    holes = []
    rr = centre_r - MEDIUM / 2 - 3.0 - stamen_d / 2
    for k in range(stamen_n):
        holes.append(K.R(K.circle(K.polar(c, rr, rot + 30.0 + 360.0 / stamen_n * k), stamen_d / 2)))
    gold = disc.difference(shapely.union_all(holes)) if holes else disc
    parts.append(("centre", K.Part(disc, K.fill(gold, GOLD), K.outline(disc, MEDIUM) + K.dot(c, 4.2), {})))
    return parts


def arrow_leaf2(sinus, *, tilt=0.0, blade=74.0, half_w=24.0, widest=0.30, lobe=(24.0, 38.0), notch=(7.0, 18.0),
                hatch_side=+1, fill_open=2.6):
    """The sagittate leaf with the vein pattern of the real thing kept to the
    PLAIN half (an arching vein into the blade, one into the lobe), the
    MEDIUM midrib, and the other half of the blade hatched perpendicular to
    the midrib (§B.2 leaves) with nothing crossing the hatch. → Part."""
    S = P(sinus)

    def q(x, y):
        return _rot(S + P(x, y), S, tilt)
    T = q(0.0, -blade)
    Wl, Wr = q(-half_w, -blade * widest), q(half_w, -blade * widest)
    Ll, Lr = q(-lobe[0], lobe[1]), q(lobe[0], lobe[1])
    shr, shl = q(half_w * 0.98, 4.0), q(-half_w * 0.98, 4.0)
    _, pr, _ = K.FM.arc_spline([T, Wr, shr, Lr])
    _, pl, _ = K.FM.arc_spline([Ll, shl, Wl, T])
    nr, nl = q(notch[0], notch[1]), q(-notch[0], notch[1])
    _, ir, _ = K.FM.arc_spline([Lr, nr, S + (q(0, 1.0) - S)])
    _, il, _ = K.FM.arc_spline([S + (q(0, 1.0) - S), nl, Ll])
    ring = np.vstack([np.asarray(pr), np.asarray(ir)[1:], np.asarray(il)[1:], np.asarray(pl)[1:]])
    reg = Polygon(ring).buffer(0)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    # the jade stops short of the sharp lobe tips: a fill wholly under the
    # outline there is a hidden plate (QA 4c)
    fills = K.fill(reg.buffer(-fill_open, join_style=1).buffer(fill_open, join_style=1).intersection(reg), JADE)
    lines = K.outline(reg)
    inner = reg.buffer(-(MEDIUM / 2 + K.GAP_MARK + FINE / 2 + 0.4))
    mid0, mid1 = q(0.0, -2.0), q(0.0, -blade + 12.0)
    lines += K.seg(mid0, mid1, MEDIUM, role="vein")
    sg = hatch_side                              # the plain side (halfplane side +1 is the other half)
    a0 = q(sg * 2.5, -8.0)
    aw = q(sg * half_w * 0.55, -blade * widest)
    a1 = q(sg * 3.5, -blade + 20.0)
    _, vp, _ = K.FM.arc_spline([a0, aw, a1])
    lines += K.clip_in(K.line(C.polyline_d(np.asarray(vp)), FINE, role="vein"), inner)
    lp = Ll if sg < 0 else Lr
    lv0 = q(sg * 3.5, 2.0)
    lv1 = lp + (S - lp) * 0.30
    lines += K.clip_in(K.line(K.arc_sag(lv0, lv1, -sg * 2.0), FINE, role="vein"), inner)
    # the hatched half: the blade on hatch_side, above the sinus line
    half = reg.intersection(K.halfplane(q(0, 40), q(0, -blade), side=hatch_side))
    half = half.difference(K.halfplane(q(-80, -1.5), q(80, -1.5), side=-1))
    lines += K.hatch_in(half, angle=tilt, origin=tuple(S))
    return K.Part(reg, fills, lines, {"tip": T, "sinus": S, "lobes": (Ll, Lr)})


def hose(points, *, w0=10.0, w1=15.0, bub=(3.0, 8.0), ratio=1.2, gap0=5.0, gap_grow=1.12, start=22.0,
         end_gap=9.0, ferrule=None):
    """The air hose (§H.5): a jade ribbon along an arc spline through
    ``points`` (root behind the far shoulder → open end), SWELLING from
    ``w0`` to ``w1`` as it rises; a column of bubbles knocked out to paper on
    its centreline, Ø ``bub[0]`` growing ×``ratio`` to ``bub[1]`` with
    growing gaps (§G.9 bubble beading, rising). ``ferrule`` (length px):
    a gold band round the open end. → (hose Part, ferrule Part | None,
    meta end/heading)."""
    d, pts, _ = K.FM.arc_spline([P(q) for q in points])
    pts = np.asarray(pts)
    cv = K.G.Curve(pts)
    Lt = cv.length
    ss = np.linspace(0.0, Lt, max(int(Lt / 1.0), 8))
    cps = np.array([cv.at_s(s) for s in ss])
    tang = np.gradient(cps, axis=0)
    tang = tang / np.hypot(tang[:, 0], tang[:, 1])[:, None]
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
    ws = w0 + (w1 - w0) * (ss / Lt) ** 1.2
    left = cps + nrm * (ws / 2)[:, None]
    right = cps - nrm * (ws / 2)[:, None]
    reg = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    holes = []
    s_ = start
    dd = bub[0] if bub else 0.0
    gap = gap0
    while bub:
        dc = min(dd, bub[1])
        if s_ + dc > Lt - end_gap - (ferrule or 0.0):
            break
        cc = cv.at_s(s_ + dc / 2)
        holes.append(Point(*cc).buffer(dc / 2, quad_segs=24))
        s_ += dc + gap
        dd *= ratio
        gap *= gap_grow
    solid = reg.difference(shapely.union_all(holes)) if holes else reg
    end = pts[-1]
    head = math.degrees(math.atan2(pts[-1][1] - pts[-4][1], pts[-1][0] - pts[-4][0]))
    fer = None
    if ferrule:
        s0 = Lt - ferrule
        band = reg.intersection(LineString([cv.at_s(s) for s in np.linspace(s0, Lt, 20)]).buffer(
            w1, cap_style=2)).buffer(0)
        band = band.buffer(0.8, quad_segs=6).buffer(1.2, quad_segs=6).intersection(
            LineString([cv.at_s(s) for s in np.linspace(s0, Lt, 20)]).buffer(w1 / 2 + 2.0, cap_style=2))
        fer = K.Part(band, K.fill(band, GOLD), K.outline(band), {})
    return K.Part(reg, K.fill(solid, JADE), K.outline(reg), {"end": end, "heading": head, "pts": pts}), fer


def bubble_rise(points, *, d0=4.2, ratio=1.2, d_max=10.5, gap0=5.0, gap_grow=1.1, start=0.0, ring_min=7.0):
    """Free bubbles rising along an arc spline through ``points`` (§G.9
    bubble beading, growing ×``ratio`` in the direction of rise): up to
    Ø6.3 solid Aquifer dots (legal Ø4.2 / 6.3), larger FINE rings. →
    Frag (meta 'discs': [(c, d)])."""
    d, pts, _ = K.FM.arc_spline([P(q) for q in points])
    cv = K.G.Curve(np.asarray(pts))
    Lt = cv.length
    f = C.Frag()
    s_ = start
    dd = d0
    gap = gap0
    discs = []
    while True:
        if s_ + dd > Lt + 0.5:
            break
        cc = cv.at_s(s_ + dd / 2)
        if dd < ring_min:
            dq = 4.2 if dd < 5.25 else 6.3
            f += K.dot(cc, dq, role="bubble")
            discs.append((cc, dq))
        else:
            f += C.stroke(K.circle(P(cc), dd / 2), FINE, color=INK, role="bubble")
            discs.append((cc, dd + FINE))
        s_ += dd + gap
        dd = min(dd * ratio, d_max)
        gap *= gap_grow
    f.meta["discs"] = discs
    return f


def flower3(c, *, r_petal=36.0, petal_w=31.0, squash=0.64, tilt=-14.0, face_rot=-90.0, centre_r=10.5,
            hatch_side=+1, sepal=(0.86, 17.0), widest=0.64, claw=36.0, centre="dot", notch=0.0, hatch_rel=90.0):
    """The arrowhead flower seen at an angle (it faces up and toward the
    queen): the flat three-petal flower of ``flower2`` laid in a plane and
    foreshortened — its local y squashed by ``squash`` and the whole turned
    ``tilt`` degrees — so it reads as a bloom on its stem, not a trefoil
    emblem (a frontal trefoil reads as a club pip). Geometry is transformed
    BEFORE stroking; hatch and outlines are drawn on the placed shapes at
    final size. Petals are painted far to near (by depth). → list of
    (name, Part), back to front."""
    c = P(c)
    a_t = math.radians(tilt)
    ca, sa = math.cos(a_t), math.sin(a_t)

    def X(p):
        x, y = p[0] - c[0], (p[1] - c[1]) * squash
        return P(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)

    def Xg(g):
        return shapely.affinity.affine_transform(
            g, (ca, -sa * squash, sa, ca * squash, c[0] - c[0] * ca + c[1] * sa * squash,
                c[1] - c[0] * sa - c[1] * ca * squash))
    import shapely.affinity
    parts = []
    seps = []
    for k in range(3):
        a = face_rot + 60.0 + 120.0 * k
        tip = K.polar(c, r_petal * sepal[0], a)
        seps.append(Xg(K.R(K.vesica(K.polar(c, 4.0, a), tip, sepal[1]))))
    sreg = shapely.union_all(seps)
    parts.append(("sepals", K.Part(sreg, K.fill(sreg, JADE), K.outline(sreg), {})))
    pet = []
    for k in range(3):
        a = face_rot + 120.0 * k
        tip = K.polar(c, r_petal, a)
        mid = K.polar(c, r_petal * widest, a)
        hw = petal_w / 2
        pl = mid + K.unit(a - 90.0) * hw
        pr = mid + K.unit(a + 90.0) * hw
        base_l = K.polar(c, 4.0, a - claw)
        base_r = K.polar(c, 4.0, a + claw)
        if notch:
            # a crinkled petal end: two lobes either side of a shallow notch
            t_in = K.polar(c, r_petal - notch, a)
            lo_l = K.polar(c, r_petal * 0.97, a - 11.0)
            lo_r = K.polar(c, r_petal * 0.97, a + 11.0)
            d, _, _ = K.FM.arc_spline([base_l, pl, lo_l, t_in], h_start=None)
            d2, _, _ = K.FM.arc_spline([t_in, lo_r, pr, base_r])
            reg = Xg(K.R(d + d2.replace("M", "L", 1) + "Z").buffer(0))
        else:
            d, _, _ = K.FM.arc_spline([base_l, pl, tip, pr, base_r])
            reg = Xg(K.R(d + "Z").buffer(0))
        # depth: the petal whose tip is lowest on screen is nearest
        pet.append((reg, X(tip), X(c)))
    pet.sort(key=lambda q: q[1][1])
    lines = C.Frag()
    placed = []
    disc = Xg(K.R(K.circle(c, centre_r)))
    disc_zone = disc.buffer(MEDIUM / 2 + K.GAP_MARK + 0.5)
    for i, (reg, tp, cc) in enumerate(pet):
        ax = math.degrees(math.atan2(tp[1] - cc[1], tp[0] - cc[0]))
        half = reg.intersection(K.halfplane(cc, tp, side=hatch_side)).difference(disc_zone)
        f = K.outline(reg) + K.hatch_in(half, angle=ax + hatch_rel, origin=tuple(cc))
        parts.append((f"petal{i}", K.Part(reg, C.Frag(), f, {})))
    if centre == "scallop":
        # a boss of stamens: a gold disc with a scalloped edge, a FINE pistil ring
        dsc, _, _ = K.FM.scallop_ring(c[0], c[1], centre_r - 2.2, centre_r, 9, phase=-90.0)
        disc = Xg(K.R(dsc + "Z").buffer(0))
        mark = K.outline(Xg(K.R(K.circle(c, 3.6))), FINE, role="pistil")
    else:
        mark = K.dot(X(c), 4.2)
    parts.append(("centre", K.Part(disc, K.fill(disc, GOLD), K.outline(disc, MEDIUM) + mark, {})))
    return parts
