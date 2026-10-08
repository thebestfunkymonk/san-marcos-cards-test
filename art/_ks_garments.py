"""KS whole-card textiles: the jade barrel mantle, red lapels and the karst lens.

Everything here is built so the 180° copy continues the top half without a
visible join: regions are C2 about (375, 525) by construction, and each pattern
is drawn once on the full-height left half (or, for the lens that straddles the
axis, on rows that are C2 partners of each other) and then rotated.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import shapely
import shapely.ops
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG
from inkkit import geom as G

AX, CY = K.AX, 525.0
BORDER = 38.0                       # patterned jade border inside the outline
LENS_HW, LENS_THROAT = 33.0, 312.0
LAP_X, LAP_R = 274.0, 1450.0        # lapel outer arc: x at the centre, radius (a near-plumb shawl edge)
SIDE_X = 146.0                      # mantle side at the card centre


def rot(g):
    return shapely.affinity.rotate(g, 180.0, origin=(AX, CY))


def c2_frag(f: C.Frag) -> C.Frag:
    """``f`` plus its 180° partner; atomic-motif keys of the partner get a suffix so
    covering one copy never deletes the other."""
    r = K.rot180(f)
    marks = [replace(m, role=m.role + "~") if "@" in m.role else m for m in r.marks]
    return f + C.Frag(marks, r.meta)


def barrel() -> object:
    """The whole-card jade mantle: shoulders from the neck, a smooth bowed side
    with a vertical tangent on the centre line (no kink at the join)."""
    ms = K.MantleSpec(neck_y=270.0, neck_heading=170.0, run=140.0, corner_r=30.0, side_heading=99.0)
    pts = K.mantle_outline(ms)
    k = next(i for i, p in enumerate(pts) if p[1] >= 369.0)
    head = pts[:k + 1]
    p0 = head[-1]
    d0 = (head[-1] - head[-2]) / np.hypot(*(head[-1] - head[-2]))
    p3 = np.array([SIDE_X, CY])
    c1, c2 = p0 + d0 * 52.0, p3 - np.array([0.0, 1.0]) * 62.0
    t = np.linspace(0.0, 1.0, 40)[1:, None]
    cub = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p3
    half = Polygon(np.vstack([head, cub, [[AX, CY]]])).buffer(0)
    top = K.U(half, K.mirror(half, AX))
    return K.U(top, rot(top))


def drop_short(f: C.Frag, min_len: float = 9.0) -> C.Frag:
    """Remove stroke pieces shorter than ``min_len`` (the stubs a hatch leaves in a pocket)."""
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d:
            out.append(m)
            continue
        d = "".join(C.polyline_d(pts, closed=cl) for pts, cl in G.flatten(m.d, 0.05)
                    if G.Curve(np.asarray(pts), closed=cl).length >= min_len)
        if d:
            out.append(replace(m, d=d))
    return C.Frag(out, f.meta)


def seam_guard(f: C.Frag, seam, margin: float = 4.8, at=None) -> C.Frag:
    """Drop stroke pieces with an end within ``margin`` of the seam: the half's clip would cut
    them a hair short of their junction, leaving a sub-3 px stub the other half has to finish.
    ``at``: only ends lying on this geometry count."""
    if seam is None:
        return f

    def near(p):
        q = Point(*p)
        return q.distance(seam) < margin and (at is None or q.distance(at) < 1.0)

    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d:
            out.append(m)
            continue
        keep = []
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts)
            if not cl and (near(pts[0]) or near(pts[-1])):
                continue
            keep.append(C.polyline_d(pts, closed=cl))
        if keep:
            out.append(replace(m, d="".join(keep)))
    return C.Frag(out, f.meta)


def lens():
    g = K.lens(K.LensSpec(half_w=LENS_HW, throat_y=LENS_THROAT))
    return K.R(K.circle(g["cL"], g["R"])).intersection(K.R(K.circle(g["cR"], g["R"])))


THROAT_R = 3.6


def lens_throat(lens_s, blockers):
    """The lens tip runs up into the beard fork alongside the fork's edges, 1–4 px off them: a
    red needle each side that heal clears by deleting the lens outline. Close the lens onto the
    fork instead, so the red ends in a tongue ≥ 2·THROAT_R wide (C2 at the foot)."""
    zone = K.box(AX - 22.0, LENS_THROAT - 16.0, AX + 22.0, LENS_THROAT + 24.0)
    zone = K.U(zone, rot(zone))
    closed = K.U(lens_s, blockers).buffer(THROAT_R, quad_segs=16).buffer(-THROAT_R, quad_segs=16)
    fill = closed.difference(blockers).intersection(zone).intersection(lens_s.buffer(2 * THROAT_R))
    return K.U(lens_s, fill)


def lapel_zone(shape):
    """The red shawl band: between the lens and a near-plumb outer arc, both sides."""
    left = K.R(K.circle((LAP_X + LAP_R, CY), LAP_R))
    right = K.R(K.circle((2 * AX - LAP_X - LAP_R, CY), LAP_R))
    return left.intersection(right).intersection(shape)


def karst(inner, *, pitch=(22.0, 16.5), sizes=(6.0, 10.0, 16.0), weights=(0.12, 0.33, 0.55), flood_min=9.5,
          seed=1983, seam=None):
    """§G.12 staggered voids on rows that are C2 partners of each other (row k above
    the centre pairs with row k below it), so the lens reads as one continuous field.
    Returns (jade fills, ink lines) of the TOP half only."""
    px, py = pitch
    cum = np.cumsum(weights) / np.sum(weights)
    placed = []
    fills, lines = C.Frag(), C.Frag()
    n = 0
    w = K.FINE
    for j in range(0, 24):
        cy = CY - py / 2 - j * py
        if cy < LENS_THROAT:
            break
        off = px / 4 + (px / 2 if j % 2 else 0.0)
        for i in range(-3, 4):
            cx = AX + off + i * px
            hsh = ((i * 73856093) ^ (j * 19349663) ^ (seed * 83492791)) & 0xFFFFFF
            k = min(int(np.searchsorted(cum, (hsh % 10007) / 10007.0, side="right")), len(sizes) - 1)
            for kk in range(k, -1, -1):
                d = sizes[kk]
                rx, ry = MG.KARST_ASPECT * d / 2 + w / 2, d / 2 + w / 2
                ell = shapely.affinity.scale(Point(cx, cy).buffer(1.0, quad_segs=32), rx, ry)
                if not inner.contains(ell):
                    continue
                if ell.distance(rot(ell)) < MG_MIN_CLEAR:
                    continue
                if seam is not None and ell.distance(seam) < 6.0:
                    continue
                if any(ell.distance(q) < MG_MIN_CLEAR for q in placed):
                    continue
                placed += [ell, rot(ell)]
                n += 1
                v = MG.karst_void(cx, cy, d, w=w)
                lines += K.atomic(v, f"ks{n}")
                if d >= flood_min:
                    closed = [p for p, cl in G.flatten(v.marks[0].d, 0.05) if cl][0]
                    fills += K.atomic(K.fill(Polygon(closed), K.JADE, role="cavern"), f"ks{n}")
                break
    return fills, lines


MG_MIN_CLEAR = C.MIN_CLEAR


def bubble_field(region_left, *, d_lo=4.2, d_hi=9.5, pitch=21.0, offsets=(13.0, 34.0, 55.0), lens_shape=None,
                 ramp=(30.0, 200.0), seam=None, blockers=None):
    """Rising bubbles (paper dots knocked out of the red): columns along offset curves of
    the lens edge, staggered, growing with the distance from the card centre so the
    top figure's bubbles rise toward ITS head and the 180° copy's toward its own."""
    edge = lens_shape.boundary
    left_edge = LineString(np.asarray(edge.coords)).intersection(K.box(0, 0, AX, 2000))
    arcs = [g for g in K._lines_of(left_edge)]
    arc = max(arcs, key=lambda g: g.length)
    # parametrise the lens' left arc from the bottom tip to the top tip
    pts = np.asarray(arc.coords)
    if pts[0][1] < pts[-1][1]:
        pts = pts[::-1]
    base = LineString(pts[::-1])                     # bottom -> top
    out = C.Frag()
    L = base.length
    zone = region_left.buffer(-4.2 - 1.55)
    for ci, o in enumerate(offsets):
        s = (pitch / 2) * (ci % 2)
        while s < L:
            p = np.array(base.interpolate(s).coords[0])
            q = np.array(base.interpolate(min(s + 0.5, L)).coords[0])
            tan = (q - p) / max(np.hypot(*(q - p)), 1e-9)
            nrm = np.array([-tan[1], tan[0]])        # to the screen-left of travel (outward at left lapel)
            if nrm[0] > 0:
                nrm = -nrm
            c = p + nrm * o
            dist = abs(c[1] - CY)
            t = min(max((dist - ramp[0]) / (ramp[1] - ramp[0]), 0.0), 1.0)
            d = d_lo + (d_hi - d_lo) * t
            if seam is not None and Point(*c).distance(seam) < d / 2 + 7.0:
                s += pitch
                continue
            if blockers is not None and blockers.distance(Point(*c)) < d / 2 + 6.5:
                s += pitch
                continue
            if zone.contains(Point(*c).buffer(d / 2 + 0.5)):
                out += K.atomic(C.dot(c[0], c[1], d, role="bubble"), f"b{ci}_{int(s)}")
            s += pitch
    return out


FAULT = ((282.0, 486.5), (208.0, 566.5))    # its ends and its seam crossing fall >= 5 px from every course line
STRATA_Y0 = 519.0                             # courses 12/19 are symmetric about y 525 from this phase
FAULT_JOG = 12.0                              # one thin-course height (brief §11)
STRATA_MIN = 7.0                              # a full hatched 12 px course gives 17 px pieces at 45°
COURSE_MIN = 16.0


def _side(p0, p1, sign):
    """Half-plane left (+1) or right (-1) of the directed line p0→p1."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    u = (p1 - p0) / np.hypot(*(p1 - p0))
    n = np.array([-u[1], u[0]]) * sign
    big = 4000.0
    return Polygon([p0 - u * big, p1 + u * big, p1 + u * big + n * big, p0 - u * big + n * big])


def fault_blocks():
    """The half-planes screen-left of the fault (x smaller) and its 180° partner."""
    left = _side(*FAULT, 1)
    return left, rot(left)


def _pieces(f, role):
    return [np.asarray(p) for m in f.marks if m.role == role and m.kind != "fill" and m.d
            for p, _ in G.flatten(m.d, 0.05)]


def prune_cells(f, blockers, lapel, min_course=COURSE_MIN, near=4.6):
    """Empty the small strata cells the orb/lapel gap and the fault's corners leave: a course
    piece shorter than ``min_course`` goes if it ends on the lapel or if no front item ends it,
    and the hatch of the course it bounds goes with it (same fault block, within one thin
    course of it). A hatch piece with an end that meets no course or fault line but stops
    within ``near`` of one goes too (a hatch end on a front item just short of a course
    corner). Heal would otherwise trim these into hooks and floating dashes."""
    left, right = fault_blocks()

    def block(pt):
        p = Point(*pt)
        return 1 if left.contains(p) else 2 if right.contains(p) else 0

    def on(pt, g):
        return Point(*pt).distance(g) < 1.2

    dropped = []
    for pts in _pieces(f, "course"):
        if G.Curve(pts).length >= min_course:
            continue
        a, b = pts[0], pts[-1]
        if on(a, lapel) or on(b, lapel) or not (on(a, blockers) or on(b, blockers)):
            xa, xb = sorted((a[0], b[0]))
            dropped.append((LineString(pts), a[1], xa, xb, block((pts[0] + pts[-1]) / 2)))

    def is_dropped(pts):
        return any(ln.distance(Point(*pts[0])) < 0.05 and ln.distance(Point(*pts[-1])) < 0.05
                   for ln, *_ in dropped)

    rails = shapely.MultiLineString([p for p in _pieces(f, "course") if not is_dropped(p)] + _pieces(f, "fault"))

    def gone(role, pts):
        if role == "course":
            return is_dropped(pts)
        if any(0.6 < rails.distance(Point(*e)) < near for e in (pts[0], pts[-1])):
            return True
        mid = (pts[0] + pts[-1]) / 2
        for ln, y, xa, xb, blk in dropped:
            if ln.distance(Point(*pts[0])) < 0.6 or ln.distance(Point(*pts[-1])) < 0.6:
                return True
            if (blk == block(mid) and abs(mid[1] - y) < 12.0 and xa - 1.0 <= pts[:, 0].max()
                    and pts[:, 0].min() <= xb + 1.0):
                return True
        return False

    out = []
    for m in f.marks:
        if m.role not in ("course", "hatch") or m.kind == "fill" or not m.d:
            out.append(m)
            continue
        keep = [C.polyline_d(p, closed=cl) for p, cl in G.flatten(m.d, 0.05) if not gone(m.role, np.asarray(p))]
        if keep:
            out.append(replace(m, d="".join(keep)))
    return C.Frag(out, f.meta)


def drop_seam_wedges(f, seam_geom, depth=12.0):
    """A course piece that runs wholly within ``depth`` (one thin course) of the border seam
    closes a wedge of colour against it; where no hatch hangs from its far side the course and
    the hatch between it and the seam go, and the cell below runs up to the seam."""
    courses = [p for p in _pieces(f, "course")]
    hatch = [p for p in _pieces(f, "hatch")]
    gone = []
    for pts in courses:
        ln = LineString(pts)
        if max(seam_geom.distance(Point(*p)) for p in pts) >= depth:
            continue
        mid_d = seam_geom.distance(ln.interpolate(0.5, normalized=True))
        hung = touch = False
        for h in hatch:
            for a, b in ((h[0], h[-1]), (h[-1], h[0])):
                if ln.distance(Point(*a)) < 1.2:
                    if seam_geom.distance(Point(*b)) > mid_d:
                        hung = True
                    else:
                        touch = True
        if not hung:
            gone.append(ln)

    def drop(role, pts):
        if role == "course":
            return any(g.distance(Point(*pts[0])) < 0.05 and g.distance(Point(*pts[-1])) < 0.05 for g in gone)
        return any(g.distance(Point(*pts[0])) < 1.2 or g.distance(Point(*pts[-1])) < 1.2 for g in gone)

    if not gone:
        return f
    out = []
    for m in f.marks:
        if m.role not in ("course", "hatch") or m.kind == "fill" or not m.d:
            out.append(m)
            continue
        keep = [C.polyline_d(p, closed=cl) for p, cl in G.flatten(m.d, 0.05) if not drop(m.role, np.asarray(p))]
        if keep:
            out.append(replace(m, d="".join(keep)))
    return C.Frag(out, f.meta)


def strata_field(region, jog=FAULT_JOG):
    """Whole-card strata with the Balcones fault: the fault and its 180° partner split the card
    into three blocks. The centre block keeps the phase symmetric about y 525; the block left of
    the fault drops ``jog`` px and its 180° partner rises by the same amount, so the hatched
    courses step across both faults."""
    p0, p1 = FAULT
    d = np.array(p1) - np.array(p0)
    fault_l = LineString([np.array(p0) - d * 6, np.array(p1) + d * 6])
    left_zone, right_zone = fault_blocks()
    mid = region.difference(left_zone).difference(right_zone)
    out = C.Frag()
    # the fault runs ~47° the same way as C.DIAG; hatching the other diagonal keeps the hatch
    # from running alongside the fault line in thin wedges
    for zone, shift in ((mid, 0.0), (region.intersection(left_zone), jog),
                        (region.intersection(right_zone), -jog)):
        if not zone.is_empty:
            out += MG.strata(zone, y0=STRATA_Y0 + shift, heights=(12.0, 19.0), hatched="thin", angle=-C.DIAG,
                             origin=(AX, CY + shift))
    for ln in (fault_l, rot(fault_l)):
        for g in K._lines_of(ln.intersection(region)):
            if g.length > 1.0:
                out += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="fault")
    return out


def trim_acute(f: C.Frag, *, roles=("course", "hatch"), within=None, angles=(6.0, 30.0), min_w=K.MEDIUM,
               targets=None, min_len=8.0, log=None) -> C.Frag:
    """A hatch or course line that runs into an outline at an angle within ``angles`` (°) leaves
    a long thin wedge between the two; end it short instead, where the clear gap reaches GAP
    (under the lower bound the line just runs on into it). Pieces left shorter than ``min_len``
    go. Only ends inside ``within``; only outlines ≥ ``min_w`` (or of the ``targets`` roles)."""
    strokes = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d or m.layer != "ink":
            continue
        for k, (pts, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL)):
            pts = np.asarray(pts, float)
            if len(pts) >= 2:
                strokes.append((i, k, m.w, LineString(np.vstack([pts, pts[:1]]) if cl else pts)))
    tree = shapely.STRtree([s[3] for s in strokes])
    changed = {}
    for j, (i, k, w, ln) in enumerate(strokes):
        if f.marks[i].role not in roles or ln.is_ring:
            continue
        cut = [0.0, ln.length]
        for end in (0, 1):
            e = Point(ln.coords[0] if end == 0 else ln.coords[-1])
            if within is not None and not within.contains(e):
                continue
            for q in tree.query(e.buffer(w / 2 + 6.0)):
                iq, kq, wq, lq = strokes[q]
                if q == j or (wq < min_w if targets is None else f.marks[iq].role not in targets) \
                        or lq.distance(e) > (w + wq) / 2 + 0.3:
                    continue
                s = ln.length if end else 0.0
                a = np.asarray(ln.interpolate(s).coords[0])
                b = np.asarray(ln.interpolate(max(s - 2.0, 0.0) if end else min(2.0, ln.length)).coords[0])
                u = (a - b) / max(np.hypot(*(a - b)), 1e-9)
                t = lq.project(e)
                c0 = np.asarray(lq.interpolate(max(t - 1.5, 0.0)).coords[0])
                c1 = np.asarray(lq.interpolate(min(t + 1.5, lq.length)).coords[0])
                v = (c1 - c0) / max(np.hypot(*(c1 - c0)), 1e-9)
                ang = math.degrees(math.acos(min(1.0, abs(float(np.dot(u, v))))))
                if not angles[0] <= ang < angles[1]:
                    continue
                need = K.GAP + (w + wq) / 2
                ss = np.arange(0.0, ln.length, 0.25)
                ok = [x for x in ss if lq.distance(ln.interpolate(x)) >= need]
                if end:
                    cut[1] = min(cut[1], max(ok) if ok else 0.0)
                else:
                    cut[0] = max(cut[0], min(ok) if ok else ln.length)
                if log is not None:
                    log.append((np.round(e.coords[0], 1).tolist(), round(ang, 1), f.marks[iq].role))
        if cut != [0.0, ln.length]:
            changed[(i, k)] = None if cut[1] - cut[0] < min_len else \
                np.asarray(shapely.ops.substring(ln, cut[0], cut[1]).coords)
    if not changed:
        return f
    out = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d or not any(key[0] == i for key in changed):
            out.append(m)
            continue
        runs = []
        for k, (p, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL)):
            if len(p) < 2:
                continue
            q = changed.get((i, k), np.asarray(p))
            if q is not None:
                runs.append(C.polyline_d(q, closed=cl))
        if runs:
            out.append(replace(m, d="".join(runs)))
    return C.Frag(out, f.meta)


def drop_crowding(f: C.Frag, *, roles=("hatch",), within=None, clear=2.8, min_w=K.MEDIUM, log=None) -> C.Frag:
    """Drop a hatch piece whose side passes an outline it does not touch with under ``clear`` px
    of jade between them (a hatch line slanting past a contour leaves a needle of colour)."""
    strokes = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d or m.layer != "ink":
            continue
        for k, (pts, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL)):
            pts = np.asarray(pts, float)
            if len(pts) >= 2:
                ln = LineString(np.vstack([pts, pts[:1]]) if cl else pts)
                strokes.append((i, k, m.w, ln, ln.buffer(m.w / 2, quad_segs=6)))
    tree = shapely.STRtree([s[4] for s in strokes])
    gone = set()
    for j, (i, k, w, ln, g) in enumerate(strokes):
        if f.marks[i].role not in roles or (within is not None and not within.contains(ln.centroid)):
            continue
        for q in tree.query(g.buffer(clear)):
            iq, kq, wq, lq, gq = strokes[q]
            if q == j or wq < min_w or gq.intersects(g):
                continue
            if gq.distance(g) < clear:
                s = ln.project(shapely.ops.nearest_points(ln, lq)[0])
                if not 1.0 < s < ln.length - 1.0:
                    continue                  # an end stopping short is close_ends' business
                gone.add((i, k))
                if log is not None:
                    log.append((np.round(ln.coords[0], 1).tolist(), round(gq.distance(g), 2), f.marks[iq].role))
                break
    if not gone:
        return f
    out = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d or not any(key[0] == i for key in gone):
            out.append(m)
            continue
        runs = [C.polyline_d(np.asarray(p), closed=cl) for k, (p, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL))
                if len(p) >= 2 and (i, k) not in gone]
        if runs:
            out.append(replace(m, d="".join(runs)))
    return C.Frag(out, f.meta)


def drop_stubs(f: C.Frag, *, roles=("current",), max_len=9.0, within=None, orphans=False) -> C.Frag:
    """Drop line pieces shorter than ``max_len`` left between two front objects (a beard current
    showing for a few px between the cheek line and the moustache). ``orphans``: only pieces that
    touch no other ink at either end (a seam dash left floating once its hatch has gone)."""
    keys, geoms = [], []
    for i, m in enumerate(f.marks):
        if not m.d or m.layer != "ink":
            continue
        if m.kind == "fill":
            keys.append((i, -1))
            geoms.append(K.R(m.d))
            continue
        for k, (pts, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL)):
            if len(pts) >= 2:
                keys.append((i, k))
                geoms.append(LineString(np.vstack([pts, pts[:1]]) if cl else pts).buffer(m.w / 2))
    tree = shapely.STRtree(geoms)

    def free(key, ln, w):
        for p in (ln.coords[0], ln.coords[-1]):
            cap = Point(*p).buffer(w / 2 + 0.3)
            if any(keys[q] != key and geoms[q].intersects(cap) for q in tree.query(cap)):
                return False
        return True

    out = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d or m.role not in roles:
            out.append(m)
            continue
        keep = []
        for k, (pts, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL)):
            pts = np.asarray(pts)
            if len(pts) < 2:
                continue
            ln = LineString(pts)
            if not cl and ln.length < max_len and (within is None or within.contains(ln)) and \
                    (not orphans or free((i, k), ln, m.w)):
                continue
            keep.append(C.polyline_d(pts, closed=cl))
        if keep:
            out.append(replace(m, d="".join(keep)))
    return C.Frag(out, f.meta)


def drop_corner_slivers(f: C.Frag, *, roles=("hatch",), within=None, reach=8.0, narrow=1.3, area=8.0) -> C.Frag:
    """Drop a hatch piece that closes off a corner between two outlines into a pocket of colour
    of ``area`` px² or more that is nowhere wider than 2·``narrow`` (QA 12's raster narrow gap)."""
    strokes = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d or m.layer != "ink":
            continue
        for k, (pts, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL)):
            pts = np.asarray(pts, float)
            if len(pts) >= 2:
                ln = LineString(np.vstack([pts, pts[:1]]) if cl else pts)
                strokes.append((i, k, ln.buffer(m.w / 2, quad_segs=6, cap_style=1 if m.cap == "round" else 2), ln))
    tree = shapely.STRtree([s[2] for s in strokes])
    gone = set()
    for j, (i, k, g, ln) in enumerate(strokes):
        if f.marks[i].role not in roles or (within is not None and not within.contains(ln.centroid)):
            continue
        hood = ln.buffer(reach)
        ink = shapely.union_all([strokes[q][2] for q in tree.query(hood)])
        colour = hood.difference(ink)
        for c in getattr(colour, "geoms", [colour]):
            if c.is_empty or c.distance(hood.exterior) < 0.05 or c.distance(g) > 0.05:
                continue
            if c.area >= area and c.buffer(-narrow).is_empty:
                gone.add((i, k))
                break
    if not gone:
        return f
    out = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d or not any(key[0] == i for key in gone):
            out.append(m)
            continue
        runs = [C.polyline_d(np.asarray(p), closed=cl) for k, (p, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL))
                if len(p) >= 2 and (i, k) not in gone]
        if runs:
            out.append(replace(m, d="".join(runs)))
    return C.Frag(out, f.meta)


CLOSE_ROLES = ("course", "hatch", "seam", "fault", "cuffline")


def close_ends(f: C.Frag, *, roles=CLOSE_ROLES, reach=6.0, min_angle=35.0, within=None, skip=None, log=None) -> C.Frag:
    """Run each textile line end that heal or a clip left stopping 0.3–``reach`` px short of the
    stroke ahead of it on until it meets that stroke's centre line, when the run-on keeps the
    §I.12 3 px from every other mark and meets the stroke at ``min_angle``° or more (so no new
    acute wedge). Only ends inside ``within`` and outside ``skip`` (the red hatch's deliberate
    gap) are touched. Runs on the composed and healed frag; nothing is trimmed."""
    pieces = []                    # [mark index, sub-path index, pts, closed, w, cap, geometry]
    for i, m in enumerate(f.marks):
        if not m.d or m.layer != "ink":
            continue
        if m.kind == "fill":
            pieces.append([i, 0, None, True, 0.0, None, K.R(m.d)])
            continue
        for k, (pts, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL)):
            pts = np.asarray(pts, float)
            if len(pts) < 2:
                continue
            ln = LineString(np.vstack([pts, pts[:1]]) if cl else pts)
            pieces.append([i, k, pts, cl, m.w, m.cap, ln])
    geoms = [p[6] if p[2] is None else p[6].buffer(p[4] / 2, quad_segs=6) for p in pieces]
    tree = shapely.STRtree(geoms)
    added = []
    changed = {}
    for j, (i, k, pts, cl, w, cap, ln) in enumerate(pieces):
        if pts is None or cl or f.marks[i].role not in roles:
            continue
        for end in (0, -1):
            e = pts[end]
            if (skip is not None and skip.contains(Point(*e))) or (within is not None
                                                                     and not within.contains(Point(*e))):
                continue
            L = ln.length
            back = np.asarray(ln.interpolate(min(1.5, L / 2) if end == 0 else max(L - 1.5, L / 2)).coords[0])
            d = e - back
            if np.hypot(*d) < 1e-6:
                continue
            d = d / np.hypot(*d)
            start = e + d * (w / 2 if cap == "round" else 0.0)
            ray = LineString([start, start + d * reach])
            hit = None
            for q in tree.query(ray):
                if q == j:
                    continue
                x = ray.intersection(geoms[q])
                if not x.is_empty:
                    t = Point(*start).distance(x)
                    if hit is None or t < hit[0]:
                        hit = (t, q)
            if hit is None or hit[0] < 0.3 or pieces[hit[1]][2] is None:
                continue
            t, q = hit
            tgt = pieces[q]
            run = t + tgt[4] / 2
            p_new = e + d * run
            s = tgt[6].project(Point(*p_new))
            a = np.asarray(tgt[6].interpolate(max(s - 1.0, 0.0)).coords[0])
            b = np.asarray(tgt[6].interpolate(min(s + 1.0, tgt[6].length)).coords[0])
            tan = (b - a) / max(np.hypot(*(b - a)), 1e-9)
            ang = math.degrees(math.acos(min(1.0, abs(float(np.dot(tan, d))))))
            if ang < min_angle:
                if log is not None:
                    log.append(("angle", e.round(1).tolist(), round(ang, 1), f.marks[tgt[0]].role))
                continue
            ext = LineString([e, p_new]).buffer(w / 2, cap_style=2)
            body = ln.buffer(w / 2 + 0.05, quad_segs=6)
            ok = True
            for r in list(tree.query(ext.buffer(K.GAP_MARK))):
                if r in (j, q) or geoms[r].intersects(body):
                    continue
                gap = geoms[r].distance(ext)
                if gap < K.GAP_MARK:
                    ok = False
                    if log is not None:
                        log.append(("clear", e.round(1).tolist(), round(gap, 2), f.marks[pieces[r][0]].role))
                    break
            if ok and any(g.distance(ext) < K.GAP_MARK for g in added):
                ok = False
            if not ok:
                continue
            if log is not None:
                log.append(("run", e.round(1).tolist(), round(run, 2), f.marks[tgt[0]].role))
            pts = np.vstack([pts, [p_new]]) if end == -1 else np.vstack([[p_new], pts])
            ln = LineString(pts)
            added.append(ext)
        if len(pts) != len(pieces[j][2]):
            changed[(i, k)] = pts
    if not changed:
        return f
    out = []
    for i, m in enumerate(f.marks):
        if m.kind == "fill" or not m.d or not any(key[0] == i for key in changed):
            out.append(m)
            continue
        d = "".join(C.polyline_d(changed.get((i, k), np.asarray(p)), closed=cl)
                    for k, (p, cl) in enumerate(G.flatten(m.d, K.FLAT_TOL)) if len(p) >= 2)
        out.append(replace(m, d=d))
    return C.Frag(out, f.meta)


def garments(front, *, sleeves, cuff_bands, sleeve_grain, sleeve_edges, seam=None):
    """The whole-card robe: jade barrel mantle (strata + fault inside a hatched border), red lapels
    (rising bubbles + hatch), the karst lens, and the two jade sleeves, all as one C2 region set.
    ``front``: shapes of the items drawn over it (head, hands, attributes) — atomic motifs and
    pattern ends keep clear of them."""
    sleeve_zone = K.c2(sleeves)
    shape = K.U(barrel(), sleeve_zone)
    shape = K.U(shape, shape.buffer(12).buffer(-12).intersection(sleeve_zone.buffer(30)))
    blockers = K.c2(front)
    lens_s = lens_throat(lens().intersection(shape), blockers)
    zone = lapel_zone(shape)
    red = zone.difference(lens_s).difference(sleeve_zone)
    jade = shape.difference(lens_s).difference(red)

    # ---- jade: hatched border, FINE seam, strata + fault inside --------------------------
    inner_shape = barrel().buffer(-BORDER, quad_segs=16)
    border = jade.difference(inner_shape).difference(sleeve_zone)
    seam_line = K.outline(inner_shape, K.FINE, role="seam")
    seam_line = K.clip_in(seam_line, jade.buffer(-0.2).difference(sleeve_zone.buffer(0.4)))
    border_hatch = drop_short(K.hatch_in(border.buffer(0.25), angle=45.0, origin=(AX, CY)), 26.0)
    # grown 0.8 px under the lapel/lens/sleeve outlines so course lines overlap them instead of
    # stopping a hair short of the stroke
    strata_zone = jade.intersection(inner_shape).buffer(0.8).intersection(inner_shape).difference(sleeve_zone.buffer(-0.8))
    # cut under the front items first so the length test sees the visible piece (the orb and its
    # stem leave short course and hatch ends against the lapel)
    strata = K.clip_out(strata_field(strata_zone), blockers)
    strata = (drop_short(strata.select(lambda m: m.role in ("hatch", "course")), STRATA_MIN)
              + strata.select(lambda m: m.role not in ("hatch", "course")))
    strata = prune_cells(strata, blockers, K.U(red, lens_s))
    strata = drop_seam_wedges(strata, inner_shape.boundary)

    # ---- red lapels: rising bubbles knocked out, hatch between ---------------------------
    left_red = red.intersection(K.box(0, 0, AX, 2000))
    bubbles = bubble_field(left_red, lens_shape=lens_s, offsets=(20.0, 47.0), pitch=24.0, d_hi=8.4, seam=seam,
                           blockers=blockers)
    bubbles = c2_frag(bubbles)
    bub_shape = K.U(*[K.R(m.d) for m in bubbles.marks if m.kind == "fill"]) if bubbles.marks else Polygon()
    red_hatch = K.hatch_in(red, angle=-45.0, origin=(AX, CY))
    red_hatch = drop_short(K.clip_out(red_hatch, K.U(bub_shape, blockers), eps=6.2, trap=0.0), 12.0)
    red_fill = K.R(C.knockout(K.D(red), bubbles))

    # ---- the lens: karst voids, flooded caverns ------------------------------------------
    inner = lens_s.buffer(-(K.MEDIUM / 2 + 3.2))
    cav, voids = karst(inner, seam=seam)
    cav, voids = c2_frag(cav), c2_frag(voids)

    # ---- sleeves --------------------------------------------------------------------------
    fills = K.fill(jade, K.JADE) + K.fill(red_fill, K.RED) + cav.select(lambda m: m.kind == "fill")
    lines = K.outline(shape) + K.outline(lens_s) + K.outline(red)
    # the strata are exactly C2, so the other half continues every course and hatch piece the
    # seam cuts; guarding them all would drop each hatched course the shallow seam runs along.
    # Only the junctions on the fault where the seam crosses it need the guard.
    faults = shapely.MultiLineString(_pieces(strata, "fault"))
    textile = seam_guard(border_hatch + red_hatch, seam) + seam_guard(strata, seam, 4.0, at=faults)
    lines += seam_line + textile + voids + bubbles.select(lambda m: m.kind != "fill")
    lines += K.c2(cuff_bands) + K.c2(sleeve_grain) + K.c2(sleeve_edges)
    return K.Part(shape, fills, lines, {"jade": jade, "red": red, "lens": lens_s})
