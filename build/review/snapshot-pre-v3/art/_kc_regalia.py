"""K♣ · the regalia (brief §H.7).

    cone_orb6   'the orb: a gold cypress cone, a sphere of wrinkled scale-plates'
                (the director's cone: graded, crinkled, wrinkled, half-hatched,
                with a stalk — see its docstring); cone_orb … cone_orb4 are the
                earlier drafts, kept for reference
    gold_staff  'a fluted cypress staff' in gold: two Aquifer flutes per run
                between raised bead collars (the red staff with paper flutes,
                ``staff``, read as a candy cane)
"""
from __future__ import annotations

from dataclasses import replace

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
# the cone orb
# =============================================================================
def cone_orb(c, r=35.0, *, n=5, inner=0.50, rot=-90.0, bow=0.10, seam_sag=1.8, twist=10.0, stalk=True,
             wrinkles=True, umbo_d=(6.3, 4.2), ridge=0.0, umbo_k=0.45, centre_ridge=False, half_hatch=False, hatch_side=1, wavy=True) -> K.Part:
    """A bald-cypress cone as the orb (§H.7 'a gold cypress cone, a sphere of
    wrinkled scale-plates'): the gold sphere cracked into PELTATE scale
    plates — a centre plate (an ``n``-gon, its edges bowed out: a domed
    scale facing the viewer) ringed by ``n`` rim plates whose seams run from
    its corners out to the rim, bowed and turned ``twist``° (the cone's
    spiral phyllotaxis) — MEDIUM seams, no X crossings. Every plate has its
    umbo (the scale's point: an Aquifer dot) with FINE wrinkles radiating
    from it: toward the corners on the centre plate, a fan toward the rim on
    each rim plate. A short stalk (the peduncle) stands on top where an
    orb's cross would."""
    c = P(c)
    body = K.R(K.circle(c, r))
    lines = K.outline(K.circle(c, r))
    ri = inner * r
    corners = [K.polar(c, ri, rot + 360.0 * k / n) for k in range(n)]
    cp = K.Path(corners[0])
    for k in range(1, n + 1):
        a, b = corners[k - 1], corners[k % n]
        cp.sag(b, -bow * float(np.hypot(*(b - a))))
    centre_plate = K.R(cp.close().d)
    lines += K.outline(centre_plate)
    for k in range(n):
        a = rot + 360.0 * k / n
        p0 = corners[k]
        p1 = K.polar(c, r + 4.0, a + twist)
        if wavy:
            # a crinkled seam: two opposed arcs (the wrinkled edge of a scale)
            pm = (p0 + p1) / 2
            d = K.arc_sag(p0, pm, seam_sag) + K.arc_sag(pm, p1, -seam_sag, move=False)
        else:
            d = K.arc_sag(p0, p1, seam_sag)
        lines += K.clip_in(K.line(d, MEDIUM, role="seam"), body.buffer(-0.2))
    f = C.Frag()
    f += K.dot(c, umbo_d[0], role="umbo")
    keep = body.buffer(-(CONTOUR / 2 + GAP + FINE / 2))
    seams_zone = lines.select(lambda m: m.role == "seam")
    if wrinkles:
        # the wrinkled faces: on each rim plate a FINE ridge following the rim
        # (butting on the seams: no free ends), on the centre plate a FINE
        # inner offset of its edge — the domed scale's ridge
        ring = K.R(K.circle(c, r - ridge)).boundary
        if ridge:
            rl = K.clip_in(K.line(K.circle(c, r - ridge), FINE, role="wrinkle"),
                           body.difference(centre_plate.buffer(MEDIUM / 2 + GAP + FINE / 2)))
            f += rl
        if centre_ridge:
            ci = centre_plate.buffer(-(MEDIUM / 2 + GAP + FINE / 2 + 0.1), join_style=2)
            if not ci.is_empty and ci.area > 40:
                f += K.outline(ci, FINE, role="wrinkle")
    seam_regions = None
    if half_hatch:
        # each rim plate split on its radius through the umbo; its clockwise
        # half hatched parallel to that radius (the wrinkles of the scale face)
        seams_u = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in lines.marks if m.role == "seam"])
        rim = body.difference(centre_plate).difference(seams_u)
    for k in range(n):
        am = rot + 360.0 * (k + 0.5) / n + twist * 0.5
        um = K.polar(c, ri + (r - ri - ridge) * umbo_k, am)
        f += K.dot(um, umbo_d[1], role="umbo")
        if half_hatch:
            plates = [g for g in K._polys_of(rim) if g.contains(Point(*um))]
            if plates:
                pl = plates[0]
                half = pl.intersection(K.halfplane(tuple(c), tuple(um), side=hatch_side))
                zone = half.buffer(-(MEDIUM / 2 + GAP + FINE / 2 - 0.9))
                zone = zone.difference(K.R(K.circle(um, umbo_d[1] / 2 + GAP_MARK + FINE / 2)))
                ang = am
                f += K.clip_in(K.hatch_in(half, angle=ang, origin=tuple(um)), zone)
    lines += f
    shape = body
    if stalk:
        top = c[1] - r
        st = K.R(K.rrect(c[0] - 4.2, top - 10.0, c[0] + 4.2, top + 3.0, 2.2))
        shape = K.U(body, st)
        lines += K.clip_out(K.outline(st), body, eps=-0.5, trap=0.0)
    fills = K.fill(shape, GOLD)
    return K.Part(shape, fills, lines, {"c": c, "r": r})


# =============================================================================
# the fluted cypress staff
# =============================================================================
def staff(x=540.0, top=186.0, bottom=548.0, hw=13.0, ferrules=(198.0, 300.0), ferrule_hw=17.0,
          ferrule_h=10.0, flute_w=10.0, grip=None, color=RED, flute_kind="slot") -> K.Part:
    """Red cypress heartwood between gold ferrules. In each run of wood a
    carved flute is KNOCKED OUT: a long stadium slot (two MEDIUM paper lines
    ``flute_w`` apart, joined in semicircles), stopping 6 px short of the
    ferrules — the groove of a fluted column, never a stripe. ``grip`` (y0,
    y1): the hand's span, so a slot never runs out from under a fist."""
    shaft = K.box(x - hw, top, x + hw, bottom)
    fer = [K.R(K.rrect(x - ferrule_hw, y - ferrule_h / 2, x + ferrule_hw, y + ferrule_h / 2, 3.2)) for y in ferrules]
    shape = K.U(shaft, *fer)
    lines = K.clip_out(K.outline(shaft), K.U(*fer), eps=-0.5, trap=0.0)
    ko = C.Frag()
    stops = [top] + [y for y in ferrules] + [bottom + 40.0]
    # runs of wood between the stops (ferrules / grip)
    cuts = sorted([(y - ferrule_h / 2, y + ferrule_h / 2) for y in ferrules] + ([grip] if grip else []))
    runs, y_prev = [], top + 2.0
    for (a, b) in cuts:
        if a > y_prev:
            runs.append((y_prev, a))
        y_prev = max(y_prev, b)
    runs.append((y_prev, bottom + 40.0))
    rr = flute_w / 2
    for (a, b) in runs:
        y0, y1 = a + MEDIUM / 2 + GAP_MARK + rr + 3.0, b - (MEDIUM / 2 + GAP_MARK + rr + 3.0)
        if y1 - y0 < 16.0:
            continue
        if flute_kind == "lines":
            # two grooves: separate knocked-out lines, round-ended (a fluted shaft)
            for sx in (-rr, rr):
                ko += K.line(f"M{x + sx:.3f} {y0 - rr + 2.0:.3f}L{x + sx:.3f} {y1 + rr - 2.0:.3f}", MEDIUM,
                             role="flute")
            continue
        slot = (f"M{x - rr:.3f} {y1:.3f}L{x - rr:.3f} {y0:.3f}"
                + C.arc_between(P(x, y0), rr, P(x - rr, y0), P(x + rr, y0), cw=True)
                + f"L{x + rr:.3f} {y1:.3f}"
                + C.arc_between(P(x, y1), rr, P(x + rr, y1), P(x - rr, y1), cw=True))
        ko += K.line(slot, MEDIUM, role="flute")
    wood = shaft.difference(K.U(*fer).buffer(-0.5))
    fill_d = C.knockout(K.D(wood), ko)
    fills = K.fill(fill_d, color) + C.Frag().add(*[K.fill(g, GOLD) for g in fer])
    lines += C.Frag().add(*[K.outline(g) for g in fer])
    return K.Part(shape, fills, lines, {})


def cone_orb2(c, r=35.0, *, lats=(-0.52, -0.08, 0.36), lat_sag=3.0,
              rows=((-0.30, 0.30), (-0.62, 0.0, 0.62), (-0.34, 0.34), (0.0,)), wavy=1.2, umbo="dot",
              umbo_d=4.2, stalk=True, seam_w=MEDIUM, min_plate=15.0) -> K.Part:
    """The orb as a bald-cypress cone (§H.7 'a gold cypress cone, a sphere of
    wrinkled scale-plates'): the gold sphere cracked into shield-shaped scale
    plates laid in staggered courses (a cone's spiral rows seen from the
    side, never a ball's pentagons): latitude seams bowing down (seen a
    little from above, like the K♠ orb's latitudes) and meridian seams
    following the sphere, staggered course to course like brickwork. Every
    seam is crinkled (a slow wave: the wrinkled edge of a scale). Each
    plate wide enough carries its umbo (the scale's point: an Aquifer dot,
    or a short wrinkle dash). A short stalk stands on top where an orb's
    cross would. ``rows``: per course (top to bottom), the meridian seams as
    fractions of the sphere's half-width."""
    c = P(c)
    cx, cy = c
    body = K.R(K.circle(c, r))
    lines = C.Frag()
    inner = body.buffer(-0.3)
    lat_y = [cy + k * r for k in lats]

    def half_w(y):
        return math.sqrt(max(r * r - (y - cy) ** 2, 0.0))

    def lat_at(k, x):
        y = lat_y[k]
        dx = half_w(y) + 4.0
        t = (x - cx) / dx
        return y + lat_sag * (1 - t * t)

    for k, y in enumerate(lat_y):
        xs = np.linspace(cx - half_w(y) - 4.0, cx + half_w(y) + 4.0, 200)
        ys = np.array([lat_at(k, x) for x in xs]) + np.sin(np.linspace(0, math.pi * 5, len(xs))) * wavy * 0.7
        lines += K.clip_in(K.line(np.column_stack([xs, ys]), seam_w, role="seam"), inner)
    nrow = len(rows)
    for ri, xs in enumerate(rows):
        for xk in xs:
            def x_at(y, xk=xk):
                return cx + xk * half_w(y)
            xm = x_at(cy)
            ya = (cy - r - 2) if ri == 0 else lat_at(ri - 1, xm)
            yb = (cy + r + 2) if ri == nrow - 1 else lat_at(ri, xm)
            ys = np.linspace(ya, yb, 60)
            pts = np.column_stack([[x_at(y) for y in ys], ys])
            if wavy:
                n = len(pts)
                pts = pts + np.column_stack([np.sin(np.linspace(0, math.pi * 2, n)) * wavy, np.zeros(n)])
            lines += K.clip_in(K.line(pts, seam_w, role="seam"), inner)
    f = C.Frag()
    bnd = [cy - r] + lat_y + [cy + r]
    for ri, xs in enumerate(rows):
        y = (bnd[ri] + bnd[ri + 1]) / 2 + lat_sag * 0.5
        edges = [-1.0] + list(xs) + [1.0]
        for a_, b_ in zip(edges[:-1], edges[1:]):
            km = (a_ + b_) / 2
            hw = half_w(y)
            x = cx + km * hw
            wdt = (b_ - a_) * hw
            hgt = bnd[ri + 1] - bnd[ri]
            if wdt < min_plate or hgt < 12.0:
                continue
            if Point(x, y).distance(body.exterior) < 8.0:
                continue
            if umbo == "dot":
                f += K.dot((x, y), umbo_d, role="umbo")
            elif umbo == "dash":
                f += K.line(K.arc_sag((x - 3.5, y), (x + 3.5, y), 1.0), FINE, role="umbo")
    lines += f
    lines = K.outline(K.circle(c, r)) + lines
    shape = body
    if stalk:
        top = cy - r
        st = K.R(K.rrect(cx - 4.2, top - 11.0, cx + 4.2, top + 3.0, 2.2))
        shape = K.U(body, st)
        lines += K.clip_out(K.outline(st), body, eps=-0.5, trap=0.0)
    return K.Part(shape, K.fill(shape, GOLD), lines, {"c": c, "r": r})


def _pts(d, step=0.4):
    return C.sample_d(d, step)[0][0]


def cone_orb3(c, r=35.0, *, du=40.0, dv=30.0, tilt=-12.0, plate=0.40, round_k=0.45, v0=0.0, u0=0.0,
              w=MEDIUM, umbo_d=4.2, umbo_min=15.0, stalk=True, margin=0.6, min_area=40.0) -> K.Part:
    """The orb as a bald-cypress cone (§H.7 'a sphere of wrinkled
    scale-plates'): a gold sphere set with separate shield-shaped plates
    (rounded lozenges) on a staggered lattice — the cone's spiral rows —
    projected onto the sphere (orthographic, tilted ``tilt``° so we see a
    little of the top), so the plates foreshorten toward the rim. Each plate
    is an Aquifer outline (no seams cross: no X, §I.13); the larger ones
    carry their umbo, a Ø4.2 dot. Stalk on top. Plates the rim cuts are
    kept (they run under the contour) unless they are slivers."""
    c = P(c)
    cx, cy = c
    body = K.R(K.circle(c, r))
    ti = math.radians(tilt)

    def proj(u, v):
        # sphere point (lon u, lat v), rotated about x by tilt, orthographic
        ur, vr = math.radians(u), math.radians(v)
        X = math.cos(vr) * math.sin(ur)
        Y = math.sin(vr)
        Z = math.cos(vr) * math.cos(ur)
        Y2 = Y * math.cos(ti) - Z * math.sin(ti)
        Z2 = Y * math.sin(ti) + Z * math.cos(ti)
        return P(cx + r * X, cy + r * Y2), Z2

    lines = C.Frag()
    dots = C.Frag()
    inner = body.buffer(-(CONTOUR / 2 - 0.5))
    j = -4
    for j in range(-4, 5):
        v = v0 + j * dv
        if abs(v) > 89:
            continue
        off = (du / 2) if (j % 2) else 0.0
        for i in range(-6, 7):
            u = u0 + off + i * du
            if abs(u) > 100:
                continue
            # the plate: a rounded lozenge in (u, v), sampled and projected
            pts, vis = [], True
            nn = 64
            for k in range(nn):
                a = 2 * math.pi * k / nn
                ca, sa = math.cos(a), math.sin(a)
                # superellipse between a diamond and an ellipse
                e = 2.0 / (1.0 + round_k * 2.0)
                su = math.copysign(abs(ca) ** e, ca) * plate * du
                sv = math.copysign(abs(sa) ** e, sa) * plate * dv
                p, z = proj(u + su, v + sv)
                if z < -0.05:
                    vis = False
                pts.append(p)
            ctr, zc = proj(u, v)
            if zc < 0.15:
                continue
            poly = shapely.geometry.Polygon(pts).buffer(0)
            if poly.is_empty:
                continue
            vis_part = poly.intersection(inner)
            if vis_part.is_empty or vis_part.area < min_area:
                continue
            lines += K.clip_in(K.outline(poly, w, role="plate"), body.buffer(-0.2))
            if poly.area > umbo_min * umbo_min * 0.8 and inner.buffer(-4.0).contains(Point(*ctr)):
                dots += K.dot(ctr, umbo_d, role="umbo")
    lines += dots
    lines = K.outline(K.circle(c, r)) + lines
    shape = body
    if stalk:
        top = cy - r
        st = K.R(K.rrect(cx - 4.2, top - 11.0, cx + 4.2, top + 3.0, 2.2))
        shape = K.U(body, st)
        lines += K.clip_out(K.outline(st), body, eps=-0.5, trap=0.0)
    return K.Part(shape, K.fill(shape, GOLD), lines, {"c": c, "r": r})


def cone_orb4(c, r=35.0, *, n=34, tilt=-18.0, spin=0.0, w=MEDIUM, umbo_d=4.2, umbo_min_z=0.55,
              umbo_min_area=150.0, stalk=True, wrinkle=False, seam_min_z=0.0) -> K.Part:
    """The orb as a bald-cypress cone (§H.7 'a gold cypress cone, a sphere of
    wrinkled scale-plates'): the gold sphere cracked into peltate scale
    plates by a spherical Voronoi of ``n`` points on a Fibonacci spiral (the
    cone's own phyllotaxis) — plates meet in three-way seams (never an X,
    §I.13), irregular and organic, never a ball's regular pentagons. The
    sphere is seen tilted ``tilt``° (a little of the top), orthographic, so
    plates foreshorten toward the rim. Seams MEDIUM Aquifer; each plate
    facing us carries its umbo (the scale's point: an Ø4.2 dot). A short
    stalk stands on top where an orb's cross would."""
    from scipy.spatial import SphericalVoronoi
    c = P(c)
    cx, cy = c
    body = K.R(K.circle(c, r))
    ga = math.pi * (3.0 - math.sqrt(5.0))
    pts3 = []
    for i in range(n):
        y = 1.0 - 2.0 * (i + 0.5) / n
        rad = math.sqrt(max(1.0 - y * y, 0.0))
        th = ga * i + math.radians(spin)
        pts3.append((math.cos(th) * rad, y, math.sin(th) * rad))
    pts3 = np.array(pts3)
    sv = SphericalVoronoi(pts3, radius=1.0, center=np.zeros(3))
    sv.sort_vertices_of_regions()
    ti = math.radians(tilt)
    Rx = np.array([[1, 0, 0], [0, math.cos(ti), -math.sin(ti)], [0, math.sin(ti), math.cos(ti)]])

    def to2(p3):
        q = Rx @ p3
        # screen: x right, y down; sphere 'y' is up → screen y = -q[1]; z toward viewer = q[2]
        return P(cx + r * q[0], cy - r * q[1]), q[2]

    edges = set()
    for reg in sv.regions:
        for a, b in zip(reg, reg[1:] + reg[:1]):
            edges.add((min(a, b), max(a, b)))
    lines = C.Frag()
    inner = body.buffer(-0.2)
    for a, b in sorted(edges):
        pa, pb = sv.vertices[a], sv.vertices[b]
        # the great-circle arc between the two Voronoi vertices, sampled
        ts = np.linspace(0.0, 1.0, 24)
        seg3 = [(pa * (1 - t) + pb * t) for t in ts]
        seg3 = [s / np.linalg.norm(s) for s in seg3]
        seg2 = [to2(s) for s in seg3]
        run = [q for q, z in seg2 if z > seam_min_z]
        if len(run) < 2:
            continue
        lines += K.clip_in(K.line(np.array(run), w, role="seam"), inner)
    dots = C.Frag()
    for i, p3 in enumerate(pts3):
        q, z = to2(p3)
        if z < umbo_min_z:
            continue
        reg = sv.regions[i]
        poly = shapely.geometry.Polygon([tuple(to2(sv.vertices[k])[0]) for k in reg]).buffer(0)
        if poly.area < umbo_min_area:
            continue
        dots += K.dot(q, umbo_d, role="umbo")
    lines = K.outline(K.circle(c, r)) + lines + dots
    shape = body
    if stalk:
        top = cy - r
        st = K.R(K.rrect(cx - 4.2, top - 11.0, cx + 4.2, top + 3.0, 2.2))
        shape = K.U(body, st)
        lines += K.clip_out(K.outline(st), body, eps=-0.5, trap=0.0)
    return K.Part(shape, K.fill(shape, GOLD), lines, {"c": c, "r": r})


# =============================================================================
# the fluted cypress staff, wrought in gold (director's note: the red staff
# with paper flutes read as a candy cane; the kingfisher now sits on a
# matching gold shaft, like the K♠ sceptre and the K♦ staff)
# =============================================================================
def gold_staff(x=540.0, top=199.0, bottom=548.0, hw=11.5, collars=(199.0, 300.0, 474.0), collar_hw=15.5,
               collar_h=7.4, flute_dx=3.7, visible_to=511.0, color=GOLD) -> K.Part:
    """A gold cypress staff: the shaft between raised bead collars (the top
    collar seats the finial's knop), each run carved with two flutes — FINE
    Aquifer grooves ``flute_dx`` either side of the axis, running collar to
    collar (butting on the collars: no free ends), the fluted bark of the
    bald cypress. Aquifer on gold: legal, and never a stripe of a second
    colour (the candy-cane read). Detail stops 4.5 px above the band rule."""
    shaft = K.box(x - hw, top, x + hw, bottom)
    cols = [K.R(K.rrect(x - collar_hw, y - collar_h / 2, x + collar_hw, y + collar_h / 2, 3.2)) for y in collars]
    cu = K.U(*cols)
    shape = K.U(shaft, cu)
    lines = K.clip_out(K.outline(shaft), cu, eps=-0.5, trap=0.0)
    fl = C.Frag()
    stops = sorted(collars) + [bottom + 40.0]
    for a, b in zip(stops[:-1], stops[1:]):
        y0, y1 = a + collar_h / 2 - 0.5, b - collar_h / 2 + 0.5
        for sx in (-flute_dx, flute_dx):
            fl += K.line(f"M{x + sx:.3f} {y0:.3f}L{x + sx:.3f} {y1:.3f}", FINE, style="hatch", role="flute")
    lines += K.clip_in(fl, K.box(0, 0, 2000, visible_to - 4.5 - MEDIUM))
    for g in cols:
        lines += K.outline(g)
    fills = K.fill(shape, color)
    return K.Part(shape, fills, lines, {"collars": collars, "top": top})


# =============================================================================
# the cone orb, v6 (director's note: the v4 irregular plates with centre dots
# read as a soccer ball)
# =============================================================================
CONE_WHORLS = ((0, 1, 0), (40, 5, 0), (85, 6, 36), (130, 5, 0), (180, 1, 0))


def _slerp_run(pa, pb, n=24):
    ts = np.linspace(0.0, 1.0, n)
    out = [(pa * (1 - t) + pb * t) for t in ts]
    return [s / np.linalg.norm(s) for s in out]


def cone_orb6(c, r=40.0, *, rings=CONE_WHORLS, jitter=5.0, jitter_seed=7, spin=0.0, tilt=-38.0, roll=30.0,
              w=MEDIUM, crinkle=1.2, bulge=3.0, seam_min_z=0.2, umbo_d=3.4, min_plate=60.0, wrinkles=3,
              whorl_len=0.8, whorl_sag=0.8, whorl_min=5.6, whorl_max=10.0, hatch_side=1, term_lon=25.0,
              hatch_frac=0.5, stem=(-1.5, 9.0), stem_lean=-12.0, stem_w=(7.0, 8.2), avoid=None,
              drop_at=(), hatch_limb=0.0) -> K.Part:
    """A bald-cypress cone as the orb (§H.7 'a gold cypress cone, a sphere of
    wrinkled scale-plates'). What makes it a cone and not a (soccer) ball:

    * GRADED scales: a spherical Voronoi of generators laid in whorls round
      the stalk (``rings`` = (colatitude°, count, phase°), jittered
      ``jitter``°), few near the poles and more round the equator, so the
      scales shrink toward the stalk and the apex; seen from above the stalk
      (``tilt``) and turned (``roll``) so the stalk rises at the upper left.
    * CRINKLED seams (MEDIUM): each seam bent into a slow S of ``crinkle`` px —
      the wrinkled edge of a scale; they still meet three-way (no X, §I.13).
    * A LUMPY limb: between the points where the seams reach it, the outline
      bulges ``bulge`` px — every rim scale domes out.
    * Each lit scale: a small umbo (the mucro, Ø``umbo_d``) where the visible
      scale has most room, and up to ``wrinkles`` FINE wrinkle arcs springing
      from it, turned away from the stalk, each as long as the scale allows
      (≥ ``whorl_min`` beyond the umbo, so heal never takes it for a stub).
    * One hemisphere HALF-HATCHED (``hatch_side`` +1 = the viewer's right):
      the scales lying mostly beyond the meridian ``term_lon``° are hatched
      WHOLE, FINE 45° at 7.0, seam to seam — no wrinkles or umbos there.
    * The stalk: a short gold peduncle leaning out from behind the limb
      (``stem`` = sag, length beyond the limb; its root at the pole), ``stem_w``
      = (root, end) px wide, flat-ended (the scar where it broke from the
      twig) with an Aquifer MEDIUM outline, returned in ``meta['stem']`` for
      art/KC.py to add BEHIND the cone (a bare CONTOUR ink stub read as the
      fuse of a bomb). ``stem_w=None`` gives the old ink stub.
    * No HUGGING seams beside the hand: the seams through ``drop_at`` (points
      within 2.5 px of their course) are left out with their limb notches —
      art/KC.py names the ones that ran along the hand (down the V beside the
      thumb; down the little finger's outer edge and along the limb beside
      it, where they doubled the edge into an ink knot with gold hairlines);
      the scales they parted read as one (one umbo per visible scale, and a
      merged scale is hatched by what shows of it past ``avoid``, the hand).
      A seam left with a visible free end by that goes too. ``hatch_limb``
      (px): a hatch line lying mostly within that of the limb (where the limb
      runs parallel to the 45° hatch) is left out."""
    from scipy.spatial import SphericalVoronoi
    from shapely.ops import polylabel
    c = P(c)
    cx, cy = c
    rng = np.random.default_rng(jitter_seed)
    pts3 = []
    for (colat, cnt, ph0) in rings:
        for k in range(cnt):
            jc, jl = (rng.uniform(-1, 1, 2) * jitter) if colat not in (0, 180) else (0.0, 0.0)
            th_, lo_ = math.radians(colat + jc), math.radians(ph0 + 360.0 * k / cnt + spin + jl)
            pts3.append((math.sin(th_) * math.cos(lo_), math.cos(th_), math.sin(th_) * math.sin(lo_)))
    pts3 = np.array(pts3)
    pts3 = pts3 / np.linalg.norm(pts3, axis=1)[:, None]
    sv = SphericalVoronoi(pts3, radius=1.0, center=np.zeros(3))
    sv.sort_vertices_of_regions()
    ti, ro = math.radians(tilt), math.radians(roll)
    Rx = np.array([[1, 0, 0], [0, math.cos(ti), -math.sin(ti)], [0, math.sin(ti), math.cos(ti)]])
    Rz = np.array([[math.cos(ro), -math.sin(ro), 0], [math.sin(ro), math.cos(ro), 0], [0, 0, 1]])
    Rv = Rz @ Rx

    def to2(p3):
        q = Rv @ p3
        return P(cx + r * q[0], cy - r * q[1]), q[2]

    # ---- seams, and where they reach the limb ---------------------------------------------
    edges = set()
    for reg in sv.regions:
        for a, b in zip(reg, reg[1:] + reg[:1]):
            edges.add((min(a, b), max(a, b)))
    runs, rim_angles = [], []
    av = K.R(avoid) if avoid is not None else None
    marks_ = [P(q) for q in (drop_at or ())]
    dropped = []
    cand = {}
    for a, b in sorted(edges):
        s3 = _slerp_run(sv.vertices[a], sv.vertices[b], 48)
        pv = [(to2(s), s) for s in s3]
        run = [q for (q, z), _ in pv if z > seam_min_z]
        crossings = []
        for ((_, z0), s0), ((_, z1), s1) in zip(pv[:-1], pv[1:]):
            if (z0 > 0) != (z1 > 0):
                t = z0 / (z0 - z1)
                m3 = s0 * (1 - t) + s1 * t
                qv = Rv @ (m3 / np.linalg.norm(m3))
                crossings.append(math.atan2(-qv[1], qv[0]))
        cand[(a, b)] = (run, crossings)
    keep = {e for e, (run, _) in cand.items()
            if not (run and marks_ and min(float(np.min(np.hypot(*(np.array(run) - m).T))) for m in marks_) < 2.5)}
    # a seam left with a visible free end by that goes too (it would stop short in the open)
    while True:
        deg = {}
        for (a, b) in keep:
            deg[a] = deg.get(a, 0) + 1
            deg[b] = deg.get(b, 0) + 1
        loose = set()
        for (a, b) in keep:
            for v in (a, b):
                q, z = to2(sv.vertices[v])
                if deg[v] == 1 and z > seam_min_z and (av is None or not av.buffer(1.0).contains(Point(*q))):
                    loose.add((a, b))
        if not loose:
            break
        keep -= loose
    for e in sorted(cand):
        run, crossings = cand[e]
        if e not in keep:
            if len(run) >= 2:
                dropped.append((np.round(run[0], 1).tolist(), np.round(run[-1], 1).tolist()))
            continue
        rim_angles += crossings
        if len(run) < 2:
            continue
        run = np.array(run)
        slen = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(run, axis=0).T))])
        if crinkle and slen[-1] > 4.0:
            # the wrinkled edge of a scale: a slow S along the seam's normal,
            # zero at both ends (the three-way junctions stay put)
            tang = np.gradient(run, axis=0)
            tang /= (np.hypot(tang[:, 0], tang[:, 1])[:, None] + 1e-9)
            nrm = np.column_stack([-tang[:, 1], tang[:, 0]])
            amp = crinkle * min(1.0, slen[-1] / 14.0)
            run = run + nrm * (amp * np.sin(2 * math.pi * slen / slen[-1]))[:, None]
        runs.append(run)
    # ---- the lumpy limb: an arc bulging out between consecutive seam ends -----------------
    rim_angles = sorted(rim_angles)
    if bulge and len(rim_angles) >= 3:
        pts_ = [P(cx + r * math.cos(a), cy + r * math.sin(a)) for a in rim_angles]
        d = f"M{pts_[0][0]:.3f} {pts_[0][1]:.3f}"
        for pa, pb, aa, ab in zip(pts_, pts_[1:] + pts_[:1], rim_angles,
                                  rim_angles[1:] + [rim_angles[0] + 2 * math.pi]):
            span = ab - aa
            chord = 2 * r * math.sin(span / 2)
            sag_c = r * (1 - math.cos(span / 2))          # the circle's own sagitta
            d += K.arc_sag(pa, pb, -(sag_c + bulge * min(1.0, chord / 22.0)), move=False)
        body = K.R(d + "Z").union(K.R(K.circle(c, r - 0.5)))
    else:
        body = K.R(K.circle(c, r))
    seam_f = C.Frag()
    inner = body.buffer(-0.2)
    for run in runs:
        seam_f += K.clip_in(K.line(run, w, role="seam"), inner)
    seam_ink = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in seam_f.marks]) if seam_f.marks else Polygon()
    free = body.difference(seam_ink).difference(body.boundary.buffer(CONTOUR / 2))
    lines = K.outline(body) + seam_f
    # ---- the half-hatched hemisphere: whole scales beyond the terminator -------------------
    lon = math.radians(term_lon)
    term = [(cx + r * math.cos(la) * math.sin(lon), cy - r * math.sin(la))
            for la in np.linspace(-math.pi / 2, math.pi / 2, 90)]       # a meridian fixed to the viewer
    far = -1.0 if hatch_side < 0 else 1.0
    beyond = Polygon(term + [(cx + far * 3 * r, cy - 3 * r), (cx + far * 3 * r, cy + 3 * r)]).buffer(0)
    def _seen(g):
        return g.difference(av) if av is not None else g
    hz = [g.buffer(MEDIUM / 2 + 0.2, join_style=2).intersection(body) for g in K._polys_of(free)
          if g.area >= 8.0 and _seen(g).intersection(beyond).area > hatch_frac * _seen(g).area]
    shade = K.U(*hz) if hz else Polygon()
    if not shade.is_empty:
        h = K.hatch_in(shade, angle=-45.0 if hatch_side > 0 else -135.0, origin=tuple(c))
        if hatch_limb:
            # a hatch line running ALONG the limb (where the limb turns parallel to the
            # 45° hatch) prints as a hairline band of gold beside it: it goes
            band = body.boundary.buffer(hatch_limb)
            hm = []
            for m in h.marks:
                ls = [ln for ln in K._stroke_lines(m.d)
                      if not (ln.length > 0 and ln.intersection(band).length > 0.6 * ln.length
                              and ln.intersection(band).length > 8.0)]
                if ls:
                    hm.append(replace(m, d="".join(C.polyline_d(np.asarray(ln.coords)) for ln in ls)))
            h = C.Frag(hm, h.meta)
        lines += K.clip_out(h, seam_ink, eps=-0.5, trap=0.0)
    # ---- the lit scales: umbo and wrinkles --------------------------------------------------
    pole2, _ = to2(np.array([0.0, 1.0, 0.0]))
    lit = free.difference(shade.buffer(GAP_MARK + FINE / 2))
    n_pl = 0
    done = []
    for g3 in pts3:
        q, z = to2(g3)
        if z < 0.0:
            continue
        cells = [g for g in K._polys_of(lit) if g.contains(Point(*q))]
        if not cells or cells[0].area < min_plate:
            continue
        cell = cells[0]
        if any(cell.equals(d_) for d_ in done):
            continue                    # two scales merged where a hugging seam was left out
        done.append(cell)
        # the mucro where the visible scale has most room (its pole of inaccessibility)
        q = P(*polylabel(cell, tolerance=0.3).coords[0])
        if av is not None and av.buffer(umbo_d).contains(Point(*q)):
            continue                    # behind the hand: its wrinkles would show as a lone tick
        n_pl += 1
        lines += K.dot(q, umbo_d, role="umbo")
        clear_u = K.R(K.circle(q, umbo_d / 2 + GAP_MARK + FINE / 2)).buffer(-0.5)
        zone = cell.buffer(-(GAP_MARK + FINE / 2)).union(clear_u)
        away = math.atan2(q[1] - pole2[1], q[0] - pole2[0]) if np.hypot(*(q - pole2)) > 1.0 else math.pi / 2
        for jj in range(wrinkles):
            an = away + math.radians((jj - (wrinkles - 1) / 2) * 360.0 / max(wrinkles, 1))
            u = np.array([math.cos(an), math.sin(an)])
            hit = LineString([tuple(q), tuple(q + u * 40.0)]).intersection(zone)
            segs = [g for g in K._lines_of(hit) if g.distance(Point(*q)) < 0.5]
            if not segs:
                continue
            L = min(segs[0].length * whorl_len, whorl_max)
            if L < umbo_d / 2 + whorl_min:
                continue
            d = K.arc_sag(q, q + u * L, whorl_sag * (-1) ** jj)
            lines += K.clip_in(K.line(d, FINE, role="wrinkle"), zone)
    # ---- the stalk ------------------------------------------------------------------------------
    stem_part = None
    if stem:
        sw, sh = stem
        pole, _ = to2(np.array([0.0, 1.0, 0.0]))
        rho = float(np.hypot(*(pole - c)))
        a0 = math.atan2(*(((pole - c) / max(rho, 1e-6))[::-1])) + math.radians(stem_lean)
        tip = pole + np.array([math.cos(a0), math.sin(a0)]) * (r - rho + sh)
        if stem_w is None:
            st = K.line(K.arc_sag(pole, tip, sw), CONTOUR, role="stem")
            stem_part = K.Part(K.R(K.G.from_skia(st.marks[0].skia())), C.Frag(), st, {})
        else:
            # a gold peduncle: flat-ended (the scar where it broke from the twig, corners
            # rounded), widening a little toward that end; meant to stand BEHIND the cone
            # so only the part beyond the limb shows
            ch = tip - pole
            L = max(float(np.hypot(*ch)), 1e-6)
            e = ch / L
            nrm = np.array([-e[1], e[0]])
            tt = np.linspace(0.0, 1.0, 24)
            cen = np.array([pole + ch * t + nrm * (-sw) * 4 * t * (1 - t) for t in tt])
            tan = np.gradient(cen, axis=0)
            tan /= np.hypot(tan[:, 0], tan[:, 1])[:, None]
            nn = np.column_stack([-tan[:, 1], tan[:, 0]])
            ws = np.linspace(stem_w[0] / 2, stem_w[1] / 2, len(cen))[:, None]
            ring = list(cen + nn * ws) + list((cen - nn * ws)[::-1])
            reg = Polygon([tuple(q) for q in ring]).buffer(0)
            reg = reg.buffer(-1.6, quad_segs=8).buffer(1.6, quad_segs=8)
            stem_part = K.Part(reg, K.fill(reg, GOLD), K.outline(reg), {"pole": pole, "tip": tip})
    return K.Part(body, K.fill(body, GOLD), lines, {"c": c, "r": r, "plates": n_pl, "stem": stem_part,
                                                     "dropped": dropped})
