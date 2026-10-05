"""art/_kd_head.py — the K♦ head: a strict profile LEFT (§H.0: the one-eyed
K♦), with the squared gold beard of current lines (§H.10) and gold hair
falling to the shoulder behind the ear — the archaic squared-beard king.

* ``profile_face``   the kit's profile construction (courtkit._profile_face:
                     one G1 biarc chain + one eye, brow, nostril hook) with
                     the ELDER WARDEN's proportions: a longer, gently aquiline
                     nose, a heavier brow set lower over the eye, the eye a
                     little longer (0.70 of the frontal 24). The mouth and
                     jaw marks are dropped (the moustache and beard cover
                     them); the ear is drawn by ``ear_marks`` in the hair's
                     notch.
* ``gold_mass``      ONE outline for hair + beard (an L: the hair falls
                     behind to a flat foot on the shoulder, the beard to a
                     lower flat foot on the chest), split by a parting from
                     the ear lobe down to the hair's foot.
* ``hair`` / ``beard`` / ``profile_moustache``  the three gold parts.

All current lines are §G.24 (offsets of one guide at a 7 px pitch, rolled
into Ø6.3 terminals); ``falls`` is the kit's current_lines variant for a
lock that FALLS along an edge (upstream candidate, see KD.py).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM
from inkkit import geom as G

FINE, MEDIUM, RULE, CONTOUR, PITCH = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR, K.PITCH
GOLD, INK = K.GOLD, K.INK
TD = K.TD


# ---------------------------------------------------------------------------
# the profile face
# ---------------------------------------------------------------------------
@dataclass
class ProfileSpec:
    r: float = 44.0
    eye_dy: float = 6.0
    nose_bot_dy: float = 22.0       # nose base below the eye line (kit elder: 21)
    nose_out: float = 10.0          # tip ahead of the face front (kit: 10.5)
    root_h: float = 142.0           # ridge heading at the root (aquiline: flatter at the root ...)
    tip_h: float = 123.0            # ... steeper at the tip
    mouth_dy: float = 41.0
    eye_w: float = 16.8             # 0.70 × 24
    lid_sag: float = 3.9
    brow_dy: float = -11.5          # lower and straighter than the kit's: the stern elder
    brow_sag: float = 1.6
    brow_back: float = 5.0          # brow runs this far past the eye's back corner
    pupil_d: float = 6.0
    lip_out: float = 3.2            # the lower lip stands this far proud of the face front
    nostril: tuple = ()             # (dx from the tip, r, sweep) of the nostril hook; () none


def profile_face(center, ps: ProfileSpec = ProfileSpec()) -> K.Face:
    """Strict profile facing LEFT (see the module doc). Returns a courtkit
    Face whose anchors match ``courtkit.face(..., 'profile-left')``."""
    cx, cy = float(center[0]), float(center[1])
    r = ps.r
    ey = cy + ps.eye_dy
    fr = cx - r * 0.84
    top = cy - r
    nb = ey + ps.nose_bot_dy
    my = ey + ps.mouth_dy
    tip = (fr - ps.nose_out, nb - 5.0)
    chain_pts = [
        ((cx + 4.0, top), 180.0),                    # crown of the skull
        ((fr + 8.0, cy - 30.0), 118.0),              # forehead
        ((fr + 0.2, ey - 8.0), 97.0),                # brow ridge
        ((fr + 3.4, ey + 1.8), ps.root_h),           # nose root (the notch)
        (tip, ps.tip_h),                             # the ridge, gently aquiline, to the tip
        ((fr - ps.nose_out + 2.6, nb + 0.8), 4.0),   # round the tip, under the nose
        ((fr - 1.4, nb + 2.2), 68.0),                # subnasale (under the moustache from here down)
        ((fr - 2.6, my - 11.0), 96.0),               # upper lip (under the moustache)
        ((fr + 0.8, my - 4.5), 72.0),                # mouth corner (a soft notch, under the moustache)
        ((fr - ps.lip_out, my + 1.2), 98.0),         # lower lip: the one lip that shows
        ((fr + 2.0, my + 9.0), 72.0),                # chin crease (the beard springs here)
        ((fr - 0.2, my + 17.5), 102.0),              # chin
        ((fr + 7.0, my + 24.0), 18.0),               # under the chin
        ((fr + 18.0, my + 28.5), 62.0),              # throat
        ((fr + 21.0, my + 62.0), 88.0),              # neck front
        ((cx + 24.0, my + 62.0), -95.0),             # neck back
        ((cx + 27.0, ey + 32.0), -118.0),            # nape
        ((cx + r + 5.0, cy + 2.0), -88.0),           # occiput
    ]
    pts = [K.P(q) for q, _ in chain_pts]
    hs = [h for _, h in chain_pts]
    head, _ = FM.biarc_chain(pts, hs, closed=True)
    lines = C.Frag()
    # eye: its open front ≥ 3 px + RULE/2 inside the contour at the nose root
    ex0 = fr + 3.4 + CONTOUR / 2 + K.GAP_MARK + RULE / 2 + 1.2
    ew = ps.eye_w
    front, back = K.P(ex0, ey - 0.3), K.P(ex0 + ew, ey + 1.0)
    lines += K.line(K.arc_sag(front, back, ps.lid_sag), RULE, role="lid")
    lower_end = K.P(front[0] + 2.0, ey + 3.9)
    lines += K.line(K.arc_sag(lower_end, back, -2.2), FINE, role="lid-lo")
    pu = K.P(front[0] + 3.7, ey - ps.lid_sag * 0.55 + 3.2)
    lines += K.dot(pu, ps.pupil_d, role="pupil")
    # brow: from over the eye's open front back past its corner, low and level
    bx0 = fr + 0.2 + CONTOUR / 2 + K.GAP_MARK + MEDIUM / 2 + 1.2
    lines += K.line(K.arc_sag(K.P(bx0, ey + ps.brow_dy + 0.6), K.P(ex0 + ew + ps.brow_back, ey + ps.brow_dy + 2.4),
                              ps.brow_sag), MEDIUM, role="brow")
    # nostril: a hook springing from the contour under the nose, curling up and back
    if ps.nostril:
        tn = C.Turtle(fr - ps.nose_out + ps.nostril[0], nb + 1.1, -60.0)
        tn.arc(ps.nostril[1], ps.nostril[2])
        lines += K.line(tn.d(), MEDIUM, role="nose")
    ear_c = K.P(cx + 9.0, ey + 10.0)
    anchors = dict(center=K.P(cx, cy), axis=ex0 + ew / 2, front=fr, eye=K.P(ex0 + ew / 2, ey), eye_y=ey,
                   eye_back=back, brow_y=ey + ps.brow_dy, nose_y=nb, mouth_y=my, lip_y=my + 5.0,
                   chin=K.P(fr - 0.2, my + 17.5), top=top, r=r, nape=K.P(cx + 27.0, ey + 32.0),
                   ear=ear_c, neck_y=my + 62.0, throat=K.P(fr + 18.0, my + 28.5), tip=K.P(tip),
                   crown_y=cy - r * 0.55, turn=0, facing=-1, spec=ps)
    return K.Face(head, K.R(head), lines, anchors, K._count(lines))


# ---------------------------------------------------------------------------
# a gentle wave laid along a guide (the flow of a current)
# ---------------------------------------------------------------------------
def wave_along(pts, base, amp, lam, phase=0.0):
    """Displace polyline ``pts`` along the normals of the smooth ``base``
    curve by amp·sin(2π s/lam + phase), s = arclength on ``base`` of each
    point's projection. Every line displaced by the same wave keeps its
    spacing: parallel currents, never loops (unlike offsets of a wavy
    curve)."""
    if not amp:
        return np.asarray(pts, float)
    base = np.asarray(base, float)
    bl = LineString(base)
    out = []
    for q in np.asarray(pts, float):
        sq = bl.project(Point(*q))
        p0 = bl.interpolate(max(sq - 0.5, 0.0))
        p1 = bl.interpolate(min(sq + 0.5, bl.length))
        t = np.array([p1.x - p0.x, p1.y - p0.y])
        t = t / (np.hypot(*t) or 1.0)
        nrm = np.array([-t[1], t[0]])
        out.append(q + nrm * amp * math.sin(2 * math.pi * sq / lam + phase))
    return np.array(out)


def wave_x(pts, amp, lam, phase=0.0):
    """Shift every point sideways by amp·sin(2π y/lam + phase): all
    near-vertical lines warped by the same wave stay parallel (the beard)."""
    q = np.array(pts, float)
    if amp:
        q[:, 0] += amp * np.sin(2 * math.pi * q[:, 1] / lam + phase)
    return q


# ---------------------------------------------------------------------------
# current lines that FALL along an edge
# ---------------------------------------------------------------------------
def falls(guide, n, region, *, side, first=None, pitch=PITCH, edge=CONTOUR, curl_r=4.2, curl_deg=85.0,
          lengths=None, min_len=14.0, placed=None, w=FINE, keep="longest", wave=None, warp=None):
    """§G.24 current lines for a lock that FALLS along an edge: ``n`` offsets
    of ``guide`` at ``first`` + k·``pitch`` toward ``side``, each clipped to
    ``region`` (keep the longest piece, or 'first' — nearest the root),
    rooted on the region's edge, ending in a curl that turns toward ``side``
    into a Ø6.3 terminal. ``lengths``: per-line shortening at the free end.
    Each end steps back until curl and terminal keep §I.12's 3 px from the
    edge and from every line already placed. → Frag (meta['lines'])."""
    gp = C.sample_d(guide, 0.3)[0][0] if isinstance(guide, str) else np.asarray(guide, float)
    cv = G.Curve(gp)
    reg = K.R(region)
    first = (edge / 2 + K.GAP + w / 2 + 0.2) if first is None else first
    tr = TD / 2
    safe = reg.buffer(-(tr + K.GAP_MARK + edge / 2 + 0.05), quad_segs=12)
    body_zone = reg.buffer(-(w / 2 + K.GAP_MARK + edge / 2 - 0.2), quad_segs=12)
    acc = placed if placed is not None else shapely.Polygon()
    f = C.Frag()
    out = []
    for k in range(n):
        off = cv.offset(side * (first + k * pitch), spacing=0.5)
        off = np.asarray(shapely.segmentize(LineString(off).simplify(0.1), 0.5).coords)   # drop sub-px back-steps
        if wave:
            off = wave_along(off, gp, *wave)
        if warp is not None:
            off = warp(off)
        ln = shapely.LineString(off)
        ix = ln.intersection(reg)
        if ix.geom_type in ("MultiLineString", "GeometryCollection"):
            ix = shapely.line_merge(shapely.MultiLineString(K._lines_of(ix)))
        pieces = [g for g in K._lines_of(ix) if g.length >= min_len]
        if not pieces:
            continue
        if keep == "first":
            piece = min(pieces, key=lambda g: ln.project(Point(g.coords[0])))
        else:
            piece = max(pieces, key=lambda g: g.length)
        q = np.asarray(piece.coords)
        if ln.project(shapely.Point(q[0])) > ln.project(shapely.Point(q[-1])):
            q = q[::-1]
        pc = G.Curve(q)
        Lp = pc.length
        s = Lp - (lengths[k] if lengths is not None and k < len(lengths) else 0.0)
        while s > min_len:
            body = pc.sub(0, s / Lp).pts
            tail = K._curl(body, side, curl_r, curl_deg)
            tp = tail[-1]
            nb = len(body)
            tail_geom = shapely.LineString(tail[max(0, nb - 3):])
            ok = safe.contains(shapely.Point(*tp)) and body_zone.contains(tail_geom)
            if ok and not acc.is_empty:
                tg = shapely.Point(*tp).buffer(tr, quad_segs=12)
                if (acc.distance(tg) < K.GAP_MARK + 0.05
                        or acc.distance(tail_geom.buffer(w / 2)) < K.GAP_MARK + 0.05):
                    ok = False
            if ok:
                f += C.stroke(tail, w, color=INK, role="current")
                f += C.dot(tp[0], tp[1], TD, color=INK, role="terminal")
                out.append(tail)
                acc = acc.union(shapely.LineString(tail).buffer(w / 2)).union(
                    shapely.Point(*tp).buffer(tr, quad_segs=12))
                break
            s -= 1.0
    f.meta["lines"] = out
    f.meta["acc"] = acc
    return f


# ---------------------------------------------------------------------------
# hair + beard: one gold mass
# ---------------------------------------------------------------------------
@dataclass
class MassSpec:
    top_y: float = 172.0                 # hidden under the crown circlet
    temple_dx: float = 1.0               # hair's front edge at the circlet: dx from the ear centre
    ear_r: float = 12.5                  # the notch the ear sits in (radius about the ear centre)
    back: tuple = ((52.0, -22.0), (59.0, 14.0), (58.0, 52.0))
    wave: tuple = (2.2, 50.0, 0.6)       # the hair's flow: amplitude, wavelength, phase (0: none)
    beard_wave: tuple = (1.8, 38.0, 0.0)  # the beard's flow (a sideways wave in y: all its lines stay parallel)
    front_sag: float = -5.0              # the beard's front edge bows forward
    hair_foot: float = 296.0             # the hair's flat foot (on the shoulder)
    hair_foot_back: float = 56.0         # its back corner dx from the head centre
    corner_r: float = 6.5
    beard_foot: float = 320.0            # the beard's flat foot (on the chest)
    beard_front: float = -8.0            # beard front at the foot, dx from the face front
    beard_back: float = 17.0             # beard back edge (below the hair) dx from the head centre
    crease: tuple = (2.0, 9.4)          # the beard starts at the chin crease (dx from the front, dy below the mouth)
    cheek: tuple = (22.0, -3.0)          # cheek line passes (dx from the front, dy below the mouth line)
    lobe: tuple = (1.0, 15.5)            # cheek line reaches the ear lobe (dx, dy from the ear centre)


def gold_mass(fc, m: MassSpec = MassSpec()):
    """The hair + beard outline and its two pieces. Returns dict(hair, beard,
    parting (points), ear_c, ear_r)."""
    a = fc.anchors
    cx, cy = a["center"]
    fr, my = a["front"], a["mouth_y"]
    ear = a["ear"]
    # hair: back edge (the skull + volume, then falling to the shoulder)
    bpts = [K.P(cx + dx, cy + dy) for dx, dy in m.back]
    top_back = K.P(bpts[0][0] - 10.0, m.top_y)
    r = m.corner_r
    HB = K.P(cx + m.hair_foot_back, m.hair_foot - r)
    back_d = K.spline([top_back] + bpts + [HB])
    back_base = C.sample_d(back_d, 0.4)[0][0]
    # extend the smooth base past both ends (the guide the current lines share)
    e0 = back_base[1] - back_base[0]
    e0 = e0 / np.hypot(*e0)
    e1 = back_base[-1] - back_base[-6]
    e1 = e1 / np.hypot(*e1)
    guide_base = np.vstack([back_base[0] - e0 * 30.0, back_base, back_base[-1] + e1 * 60.0])
    back_pts = wave_along(back_base, guide_base, *m.wave) if m.wave else back_base
    # beard front: chin crease to the foot corner, standing a little proud
    Q0 = K.P(fr + m.crease[0], my + m.crease[1])
    Q1 = K.P(fr + m.beard_front, m.beard_foot - r)
    front_s = C.sample_d(K.arc_sag(Q0, Q1, m.front_sag), 0.4)[0][0]
    ft0 = (front_s[1] - front_s[0]) / np.hypot(*(front_s[1] - front_s[0]))
    ft1 = (front_s[-1] - front_s[-2]) / np.hypot(*(front_s[-1] - front_s[-2]))
    front_guide = np.vstack([front_s[0] - ft0 * 70.0, front_s, front_s[-1] + ft1 * 40.0])
    bw = m.beard_wave
    # the wave fades in below the chin crease so the beard still springs from the lip
    front_pts = front_s.copy()
    if bw and bw[0]:
        fade = np.clip((front_s[:, 1] - Q0[1]) / 14.0, 0.0, 1.0)
        front_pts[:, 0] += fade * bw[0] * np.sin(2 * math.pi * front_s[:, 1] / bw[1] + bw[2])
    xb = cx + m.beard_back
    # the outline, clockwise from the top-back: back edge down, hair foot,
    # step down the beard's back edge, beard foot, front edge up, cheek line
    # up to the ear lobe, round the ear notch, up to the circlet (sharp
    # corners here; the feet are rounded below by an open + close)
    HBs = K.P(HB[0], m.hair_foot)
    p = [back_pts, np.array([HBs, (xb, m.hair_foot), (xb, m.beard_foot), (Q1[0], m.beard_foot)])]
    p.append(front_pts[::-1])
    lobe = K.P(ear[0] + m.lobe[0], ear[1] + m.lobe[1])
    ch = K.P(fr + m.cheek[0], my + m.cheek[1])
    cheek = C.sample_d(K.Path(Q0).sag(ch, 2.0).sag(lobe, 3.0).d, 0.4)[0][0]
    p.append(cheek[1:])
    # round the ear: the notch is an arc about the ear centre from the lobe
    # back and up to the ear top, then the hair's front edge rises to the circlet
    a_lobe = K.ang(ear, lobe)                  # ≈ +85 (below): sweep back through 0 (behind) to the top
    th = np.radians(np.linspace(a_lobe, -100.0, 80))
    notch = np.column_stack([ear[0] + m.ear_r * np.cos(th), ear[1] + m.ear_r * np.sin(th)])
    p.append(notch)
    temple = K.P(ear[0] + m.temple_dx, m.top_y)
    up = C.sample_d(K.arc_sag(notch[-1], temple, -2.5), 0.4)[0][0]
    p.append(up[1:])
    outline_pts = np.vstack(p)
    mass = Polygon(outline_pts).buffer(0)
    mass = max(K._polys_of(mass), key=lambda q: q.area)
    low = K.box(0, m.hair_foot - 40.0, 2000, 2000)
    rounded = (mass.intersection(low.buffer(r * 3))
               .buffer(-r, join_style=1, quad_segs=16).buffer(r, join_style=1, quad_segs=16)
               .buffer(r, join_style=1, quad_segs=16).buffer(-r, join_style=1, quad_segs=16))
    mass = K.U(mass.difference(low), rounded.intersection(low)).buffer(0)
    mass = max(K._polys_of(mass), key=lambda q: q.area)
    # parting: from the ear lobe down to the hair foot's front (the step)
    Pp0 = K.P(lobe[0] + 2.0, lobe[1] - 1.0)
    Pp1 = K.P(xb, m.hair_foot + r)
    part_d = K.arc_sag(Pp0, Pp1, 2.5)
    part_pts = C.sample_d(part_d, 0.3)[0][0]
    ext = np.vstack([part_pts[0] + (part_pts[0] - part_pts[3]) * 8, part_pts,
                     part_pts[-1] + (part_pts[-1] - part_pts[-4]) * 12])
    cut = LineString(ext).buffer(0.02)
    pieces = sorted(K._polys_of(mass.difference(cut)), key=lambda g: -g.area)
    # hair = the piece containing the back edge
    hair = [g for g in pieces if g.distance(Point(*bpts[1])) < 1.0][0]
    beard = min(pieces, key=lambda g: g.distance(Point(*front_pts[-1])))
    return dict(mass=mass, hair=hair, beard=beard, parting=part_pts, back=back_pts, front=front_pts,
                guide_base=guide_base, front_guide=front_guide,
                ear_c=ear, ear_r=m.ear_r, Q0=Q0, Q1=Q1, xb=xb, lobe=lobe, spec=m)


def ear_marks(g):
    """The ear in the hair's notch: a C (MEDIUM) inside the rim, opening
    forward, ending in a small inward turn (the antihelix)."""
    ear, er = g["ear_c"], g["ear_r"]
    c = K.P(ear[0] - 1.0, ear[1] + 0.5)
    rr = er - (MEDIUM + K.GAP_MARK + 0.6)
    return K.line(K.arc_c(c, rr, -70.0, 75.0), MEDIUM, role="ear")


def hair(fc, g, n=3, stagger=9.0) -> K.Part:
    """The hair behind the ear, falling in gentle waves to a flat foot on
    the shoulder: ``n`` current lines (§G.24) run parallel to the wavy back
    edge (offsets of its smooth base, all displaced by the same wave), rolling
    FORWARD into staggered terminals at the foot; the lock by the ear stays
    flat gold."""
    reg = g["hair"]
    A, lam = g["spec"].wave[:2]
    slope = math.atan(2 * math.pi * A / lam)            # the wave tilts the spacing: widen the first step
    first = (CONTOUR / 2 + K.GAP + FINE / 2 + 0.2) / math.cos(slope)
    lines = falls(g["guide_base"], n, reg, side=-1, first=first, pitch=PITCH / math.cos(slope),
                  lengths=[k * stagger for k in range(n)], wave=g["spec"].wave)
    return K.Part(reg, K.fill(reg, GOLD), lines + K.outline(reg), {})


def beard(fc, g, n=(3, 2), stagger=(7.0, 7.0), split=(31.0, 38.0)) -> K.Part:
    """The squared beard in two locks (front: chin; back: jaw) divided by a
    MEDIUM parting from the cheek line to the flat foot. Each lock's current
    lines (§G.24) are offsets of its front boundary, falling to the foot and
    rolling BACK into terminals; the front lines run longest (the beard's
    foot juts forward), the ends stepping up ``stagger`` px per line."""
    reg = g["beard"]
    a = fc.anchors
    fr, my = a["front"], a["mouth_y"]
    m = g["spec"]
    bw = m.beard_wave
    warp = (lambda q: wave_x(q, *bw)) if bw and bw[0] else (lambda q: q)
    slope = math.atan(2 * math.pi * bw[0] / bw[1]) if bw and bw[0] else 0.0
    S0 = K.P(fr + split[0], my - 12.0)
    S1 = K.P(fr + split[1], m.beard_foot + 20.0)
    part_s = C.sample_d(K.arc_sag(S0, S1, -2.0), 0.3)[0][0]
    part_w = warp(part_s)
    part_d = C.polyline_d(part_w)
    part_ln = K.clip_in(K.line(part_d, MEDIUM, role="parting"), reg.buffer(-0.3))
    cut = LineString(part_w).buffer(0.01)
    halves = sorted(K._polys_of(reg.difference(cut)), key=lambda q: q.centroid.x)
    front_lock, back_lock = halves[0], halves[-1]
    first = (CONTOUR / 2 + K.GAP + FINE / 2 + 0.2) / math.cos(slope)
    lines = falls(g["front_guide"], n[0], front_lock, side=+1, first=first, pitch=PITCH / math.cos(slope),
                  lengths=[k * stagger[0] for k in range(n[0])], warp=warp)
    t2 = part_s[-1] - part_s[-2]
    t2 = t2 / np.hypot(*t2)
    g2 = np.vstack([part_s, part_s[-1] + t2 * 30.0])
    lines += falls(g2, n[1], back_lock, side=+1, first=(MEDIUM / 2 + K.GAP + FINE / 2 + 0.2) / math.cos(slope),
                   pitch=PITCH / math.cos(slope), edge=MEDIUM,
                   lengths=[2.0 + k * stagger[1] for k in range(n[1])], warp=warp)
    return K.Part(reg, K.fill(reg, GOLD), lines + part_ln + K.outline(reg), {"parting": part_d})


def profile_moustache(fc, top=(-1.4, 2.4), bot=(-4.0, 12.5), tip=(26.0, 18.5), arch=5.5, under=2.2,
                      nose=0.9) -> K.Part:
    """A drooping moustache: its root on the contour just under the nose
    (``top``: dx from the face front, dy below the nose base), a blunt front
    standing a little proud of the upper lip down to ``bot`` (the mouth line:
    the lower lip shows below it), a gently convex lower edge sweeping back
    and down to the ``tip`` over the beard, and an arched upper edge back to
    the root."""
    a = fc.anchors
    fr, nb = a["front"], a["nose_y"]
    P0 = K.P(fr + top[0], nb + top[1])
    P1 = K.P(fr + bot[0], nb + bot[1])
    T = K.P(fr + tip[0], nb + tip[1])
    d = K.Path(P0).sag(T, arch).sag(P1, under).sag(P0, nose).close().d
    reg = K.R(d)
    return K.Part(reg, K.fill(reg, GOLD), K.outline(reg), {"root": P0, "tip": T, "bot": P1})
