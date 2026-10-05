"""art/_kc_hands.py — the K♣'s cone hand, refined locally on top of deck.courtkit.

The kit (``deck/courtkit.py``) is shared by all twelve courts and is not edited
from a court. The K♣ holds his cypress cone from below exactly as the K♠ holds
his orb, so the cone hand is drawn in the same hand language as the K♠'s
``art/_ks_hands.orb_cup`` (a local copy here, so the two courts do not depend
on each other's files): §H.0 mitten — paper, CONTOUR silhouette, MEDIUM
interior, four fingers + three finger lines, a separate thumb merged at its
root, a tapered back running into the cuff.

``cone_cup``  the kit's ``cup`` with
              * a thumb that is a thumb: it leaves the back of the hand low on
                the wrist side and rises in one tapered sweep to a round tip on
                the cone's rim, opening a V to the index finger (the kit's
                thumb is a short knob on the rim that fuses with the index
                finger's edge: the hand read as a mitten with a bump);
              * the back's little-finger edge a cubic that leaves the finger on
                its tangent (the kit's quadratic falls back to the chord when
                the tangents do not meet ahead: a square corner at the
                little-finger knuckle);
              * no crease stubs: the only interior lines are the three finger
                lines (from the notches between the tips down to the
                knuckles).

``short_crease``  a kit fist (palm view) whose thumb crease is cut to the
              22 px at the thumb's tip: the tip's round end plus its underside
              as far as the shaft's near edge. The kit's crease runs back
              nearly to the heel, and the thumb over the top of the fist read
              as a long pointing index finger. (A candidate for the kit's palm
              view; other palm-view fists — K♠, Q♣ R, J♣ … — still draw the
              long crease.)

``tidy_fist``  a kit palm-view fist whose interior lines all end on something:
              the (short) thumb crease joined into the top fingertip curl (their
              ends lay 2 px apart: an ink knot), the lowest curl stretched onto
              the fist's bottom edge (it stopped 3 px short: a free end over a
              paper hairline).

``clear_caps``  an attribute's lines cut 1 px OUTSIDE the hand that closes on
              it: the scene cuts lines behind a front object 0.5 px inside it,
              so a MEDIUM line's round cap poked ~0.5–1 px past the front
              object's MEDIUM outline (nubs where the staff's contours enter the
              fist). A candidate for the kit (courtkit.clip_out's STROKE_EPS vs
              the cap radius); other courts' shafts show the same nubs at 30×.

The hand builders return the kit's own ``K.Hand``, so ``add_to`` tucks the wrist
into the cuff exactly as for a kit hand.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C

BIG = K.BIG


def _unit(v):
    v = np.asarray(v, float)
    n = float(np.hypot(*v))
    return v / n if n > 1e-9 else np.array([1.0, 0.0])


def _largest(g):
    ps = K._polys_of(g)
    return max(ps, key=lambda q: q.area) if ps else Polygon()


def _chain(cen, widths, quad=16):
    """A tapered capsule chain: union of the hulls of consecutive discs."""
    ds = [Point(*q).buffer(max(float(w), 0.3), quad_segs=quad) for q, w in zip(cen, widths)]
    return shapely.union_all([shapely.union(a, b).convex_hull for a, b in zip(ds[:-1], ds[1:])])


def _cubic_edge(p0, u0, p1, u1, k=0.40, bulge=0.0, n=28):
    """A smooth edge from p0 leaving along u0 to p1 arriving along u1: a cubic
    Bézier with handles ``k`` × the chord (it always leaves and arrives on its
    tangents), optionally swollen ``bulge`` px to the screen-left of travel
    with a sin² profile."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    c0, c1 = p0 + _unit(u0) * k * L, p1 - _unit(u1) * k * L
    t = np.linspace(0.0, 1.0, n)[:, None]
    pts = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c0 + 3 * (1 - t) * t ** 2 * c1 + t ** 3 * p1
    if bulge:
        ch = _unit(p1 - p0)
        pts = pts + np.array([ch[1], -ch[0]]) * bulge * np.sin(np.pi * t) ** 2
    return pts


def cone_cup(c, r, *, wrist, wrist_w=26.0, grip=0.40, fw=None, converge=0.80, knuckle=3.0,
             thumb_tip=13.0, thumb_rim=0.5, thumb_root=(-0.50, 0.05), thumb_bow=2.0, thumb_w=None, vee=0.30,
             flank_r=10.0, hypo=0.0, hypo_k=0.35, vee_r=0.0, stub=K.HAND_STUB) -> K.Hand:
    """A sphere held from below by the figure's RIGHT hand (viewer's left),
    back of the hand to the viewer, wrist down and to the viewer's left.

    ``grip``: fingertip centres ≈ (grip − 0.05)·r below the centre (smaller =
    fingers further up the sphere). ``thumb_tip``: the tip's centre, degrees
    below the equator, ``thumb_rim`` px outside the radius ``r`` (the cone's
    limb domes out between its seams). ``thumb_root``: the thumb's root on
    the back of the hand, in finger widths from the index knuckle (x, toward
    the wrist side) and in r below the knuckle row (y). ``thumb_bow``: px the
    thumb's centreline bows outward. ``vee``: where the V between thumb and
    index closes, as a fraction of the way from the knuckle row up to the
    thumb tip. ``flank_r``: the fillet where the thumb's outer edge runs into
    the wrist. ``hypo_k`` / ``hypo``: the little-finger edge's handle length
    (× chord) and extra swell (in r). ``vee_r``: a fillet of that radius
    rounding the bottom of the V (0 = the kit's smoothing only)."""
    c = K.P(c)
    fw = fw if fw is not None else r * 0.34
    y_kn = r + max(float(knuckle), 0.14 * r)
    g = max(0.12, float(grip) - 0.05)
    xb = [(k - 1.5) * fw + 0.10 * r for k in range(4)]                 # knuckles (index … little)
    xt = [x * converge for x in xb]                                    # tips close in round the ball
    top_y = [g * r + 0.45 * x * x / r for x in xt]
    cols = [LineString([(x0 + (x0 - x1) * 0.3, y_kn + (y_kn - yt) * 0.3), (x1, yt)]).buffer(
        fw / 2, cap_style=1, quad_segs=16) for x0, x1, yt in zip(xb, xt, top_y)]
    fingers = shapely.union_all(cols).intersection(shapely.box(-BIG, -BIG, BIG, y_kn + 1.0))
    W = K.P(wrist) - c
    kc = K.P(np.mean(xb), y_kn)
    span = 4 * fw
    hw = min(float(wrist_w), 0.45 * span) / 2.0
    tw = float(thumb_w) if thumb_w is not None else fw
    w0, w1 = 0.62 * tw, 0.52 * tw                                      # thumb root / tip radius

    def build(u):
        u = _unit(u)
        n = np.array([u[1], -u[0]])
        Wl, Wr = (W + n * hw, W - n * hw) if n[0] < 0 else (W - n * hw, W + n * hw)
        dl = _unit(K.P(xb[0] - xt[0], y_kn - top_y[0]))
        dr = _unit(K.P(xb[3] - xt[3], y_kn - top_y[3]))
        kl = K.P(xb[0], y_kn) - K.P(dl[1], -dl[0]) * (fw / 2)
        kr = K.P(xb[3], y_kn) + K.P(dr[1], -dr[0]) * (fw / 2)
        # the back: the thumb side runs straight to the wrist; the little-finger side is
        # a cubic that leaves the finger's edge on its tangent and arrives along the forearm
        le = K._edge(kl, dl, Wl, u, 24)
        re_ = _cubic_edge(kr, dr, Wr, u, k=hypo_k, bulge=hypo * r)
        ring = ([K.P(xb[0], y_kn - 6.0)] + list(le) + [Wl + u * stub, Wr + u * stub] + list(re_[::-1])
                + [K.P(xb[3], y_kn - 6.0)])
        back = _largest(Polygon([tuple(q) for q in ring]).buffer(0))
        # the thumb: from low on the wrist side of the back, one tapered sweep to a
        # round tip centred on the rim (the limb passes behind it)
        a = math.radians(thumb_tip)
        rt = r + float(thumb_rim)
        tip = K.P(-rt * math.cos(a), rt * math.sin(a))
        root = K.P(xb[0] + thumb_root[0] * fw, y_kn + thumb_root[1] * r)
        ch = tip - root
        nrm = _unit(K.P(ch[1], -ch[0]))
        if nrm[0] > 0:
            nrm = -nrm                                                 # outward = toward the wrist side
        ctrl = (root + tip) / 2 + nrm * float(thumb_bow)
        cen = K._qbez(root, ctrl, tip, 20)
        ws = np.linspace(w0, w1, len(cen))
        thumb = _chain(cen, ws)
        # the web: below the V's root the ground between the thumb and the index is hand
        yv = y_kn - float(vee) * (y_kn - tip[1])
        low = shapely.box(-BIG, yv, BIG, BIG)
        web = shapely.union(thumb.intersection(low), cols[0].intersection(low)).convex_hull
        web = web.intersection(shapely.box(-BIG, -BIG, BIG, y_kn + 1.0))
        hand = shapely.union_all([fingers, back, thumb, web])
        # round the notches: a small radius in the V's root, the kit's 5 px elsewhere
        # (never across the fingertips)
        tips = shapely.box(-BIG, -BIG, BIG, max(top_y) + 0.45 * fw)
        vee_z = shapely.box(tip[0], -BIG, xb[0], yv + 1.0).difference(low.buffer(-3.0))
        hand = K._junction_smooth(hand, tips.difference(thumb.buffer(3.0)).union(vee_z), r=5.0)
        hand = K._junction_smooth(hand, tips.difference(vee_z), r=2.2)
        # the thumb's outer edge runs on into the wrist without a dent at its root
        flank = shapely.box(-BIG, root[1] - 0.45 * (root[1] - tip[1]), xb[0] - 0.5 * fw, BIG)
        hand = hand.union(hand.buffer(float(flank_r), quad_segs=12).buffer(-float(flank_r), quad_segs=12)
                          .intersection(flank))
        # the V's bottom one round arc (with the tip out past the rim the V pinches, and its
        # bottom printed as a flat run between two tiny concave corners: ink lumps)
        if vee_r:
            gaps = [g for g in K._polys_of(hand.convex_hull.difference(hand))
                    if tip[0] - 1.0 < g.centroid.x < xb[0] + fw / 2 and g.area > 4.0]
            if gaps:
                vg = max(gaps, key=lambda g: g.area)
                pts_ = np.asarray(vg.exterior.coords)
                vb = pts_[np.argmax(pts_[:, 1])]
                fillet = hand.buffer(vee_r, quad_segs=16).buffer(-vee_r, quad_segs=16)
                hand = hand.union(fillet.intersection(Point(*vb).buffer(2.5 * vee_r, quad_segs=16)))
        # every convex corner sharper than a 3.5 px radius goes (lobes and tips are rounder)
        hand = _largest(hand.buffer(-3.5, quad_segs=10).buffer(3.5, quad_segs=10))
        inner = C.Frag()
        for k in range(1, 4):
            ta, tb = K.P(xt[k - 1], top_y[k - 1]), K.P(xt[k], top_y[k])
            m = (ta + tb) / 2
            dd = float(np.hypot(*(tb - ta))) / 2
            rr_ = fw / 2
            up = math.sqrt(max(rr_ * rr_ - dd * dd, 0.0))
            nn = _unit(K.P(-(tb - ta)[1], (tb - ta)[0]))
            if nn[1] > 0:
                nn = -nn
            notch = m + nn * up
            base = K.P((xb[k - 1] + xb[k]) / 2, y_kn - 3.0 + (1.5 if k == 2 else 0.0))
            inner += K.seg(notch + _unit(base - notch) * 0.4, base, K.MEDIUM, role="finger")
        return hand, inner, thumb

    Mt = (1, 0, 0, 1, c[0], c[1])

    def place(u):
        hl, il, tl = build(u)
        hs, is_ = K._xf(hl, Mt), il.translate(c[0], c[1])
        return K.Part(hs, C.Frag(), K.outline(hs) + is_, {"kind": "cup", "inner": is_, "rebuild": rebuild}), tl

    def rebuild(u_screen):
        return place(K.P(u_screen))[0]

    u0 = _unit(W - kc)
    part, tl = place(u0)
    return K.Hand(part, K.Part(K._xf(tl, Mt), C.Frag(), C.Frag(), {"merged": True}), W + c, 2 * hw, u0,
                  float(stub))


def _trim_marks(frag, role, at, keep):
    """``frag`` with every ``role`` stroke cut to the ``keep`` px nearest ``at``
    (measured along the stroke from its end nearer ``at``)."""
    from shapely.ops import substring
    out = []
    for m in frag.marks:
        if m.kind == "fill" or m.role.split("@")[0] != role:
            out.append(m)
            continue
        for ln in K._stroke_lines(m.d):
            q = np.asarray(ln.coords)
            if np.hypot(*(q[-1] - at)) < np.hypot(*(q[0] - at)):
                ln = LineString(q[::-1])
            if ln.length > keep:
                ln = substring(ln, 0.0, keep)
            if ln.length >= 3.0:
                out += K.line(C.polyline_d(np.asarray(ln.coords)), K.MEDIUM, role=role).marks
    return C.Frag(out, frag.meta)


def short_crease(hand: K.Hand, keep=12.0) -> K.Hand:
    """A kit fist whose thumb crease (the line under the thumb, from its tip back
    toward the heel) is cut to the ``keep`` px nearest the thumb tip. In the palm
    view the kit's crease runs from the tip nearly to the back of the hand, and the
    thumb over the top of the fist read as a long pointing index finger; cut short,
    the thumb leaves the ball of the palm over the shaft and the palm stays one mass.
    The cut applies to rebuilt hands too (``add_to`` re-aims the wrist)."""
    # the thumb tip: the thumb's point farthest from the wrist
    pts = np.asarray(hand.thumb.shape.exterior.coords)
    tip = pts[np.argmax(np.hypot(*(pts - np.asarray(hand.wrist)).T))]

    def fix(part):
        inner = _trim_marks(part.meta["inner"], "thumb", tip, keep)
        rb = part.meta.get("rebuild")
        meta = {**part.meta, "inner": inner}
        if rb is not None:
            meta["rebuild"] = lambda u, rb=rb: fix(rb(u))
        return K.Part(part.shape, part.fills, K.outline(part.shape) + inner, meta)

    return K.Hand(fix(hand.hand), hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, hand.stub)


def _polylines(frag):
    """[(mark, [N×2 arrays])] for the stroke marks of ``frag``."""
    return [(m, [np.asarray(ln.coords) for ln in K._stroke_lines(m.d)]) for m in frag.marks if m.kind != "fill"]


def tidy_fist(hand: K.Hand, *, join=6.5, reach=4.5) -> K.Hand:
    """A kit palm-view fist whose interior lines all end on something:

    * the thumb crease's end and the top fingertip curl's start lie ≈ 2 px
      apart (a near-miss that prints as an ink knot): the crease is cut back
      to where it leaves the curl ``join`` px clear and joined to the curl's
      start, so the thumb's underside runs on into the fingertip (it IS that
      finger's upper edge there, as the first finger line already merges
      into the crease);
    * the lowest fingertip curl stops ≈ 3 px above the fist's bottom edge (a
      free end with a paper hairline under it): it is stretched along its
      chord so its end lands on the outline (a cusp like the ones between
      the curls above).

    Applies to rebuilt hands too (``add_to`` re-aims the wrist)."""
    from shapely.geometry import Point as _Pt

    def fix(part):
        bnd = part.shape.boundary
        inner = part.meta["inner"]
        pls = _polylines(inner)
        curls = [(m, q) for m, qs in pls if m.role.split("@")[0] == "fingertip" for q in qs]
        creases = [(m, q) for m, qs in pls if m.role.split("@")[0] == "thumb" for q in qs]
        rest = [m for m in inner.marks if m.kind == "fill" or m.role.split("@")[0] not in ("fingertip", "thumb")]
        out = C.Frag(list(rest), inner.meta)
        used = set()
        for mc, q in creases:
            # the crease end farther from the thumb tip (the tip is its start: see short_crease)
            e = q[-1]
            best = None
            for i, (mf, f) in enumerate(curls):
                for k, s in ((0, f[0]), (-1, f[-1])):
                    d = float(np.hypot(*(s - e)))
                    if d < 2.0 * join and (best is None or d < best[0]):
                        best = (d, i, k)
            if best is None:
                out += K.line(C.polyline_d(q), mc.w, role="thumb")
                continue
            _, i, k = best
            f = curls[i][1] if k == 0 else curls[i][1][::-1]
            s = f[0]
            dist = np.hypot(*(q - s).T)
            cut = len(q)
            while cut > 2 and dist[cut - 1] < join:
                cut -= 1
            path = np.vstack([q[:cut], f])
            out += K.line(C.polyline_d(path), mc.w, role="fingertip")
            used.add(i)
        for i, (mf, f) in enumerate(curls):
            if i in used:
                continue
            for end in (-1, 0):
                p = f[end]
                d = bnd.distance(_Pt(*p))
                if not (0.4 < d < reach):
                    continue
                s = f[0] if end == -1 else f[-1]
                # the outline point the curl's chord points at (else the nearest one)
                ch = _unit(p - s)
                ray = LineString([tuple(p), tuple(p + ch * (reach + 3.0))]).intersection(bnd)
                tgt = None
                if not ray.is_empty:
                    cands = [np.asarray(g.coords)[0] for g in getattr(ray, "geoms", [ray])]
                    tgt = min(cands, key=lambda c_: float(np.hypot(*(c_ - p))))
                if tgt is None:
                    continue
                # stretch the curl along its chord (start fixed) so this end lands on tgt
                a0 = p - s
                a1 = tgt - s
                L0 = float(np.hypot(*a0))
                if L0 < 1.0:
                    continue
                e0 = a0 / L0
                n0 = np.array([-e0[1], e0[0]])
                L1 = float(np.hypot(*a1))
                e1 = a1 / L1
                n1 = np.array([-e1[1], e1[0]])
                loc = np.column_stack([(f - s) @ e0, (f - s) @ n0])
                f = s + np.outer(loc[:, 0] * (L1 / L0), e1) + np.outer(loc[:, 1], n1)
                break
            out += K.line(C.polyline_d(f), mf.w, role="fingertip")
        rb = part.meta.get("rebuild")
        meta = {**part.meta, "inner": out}
        if rb is not None:
            meta["rebuild"] = lambda u, rb=rb: fix(rb(u))
        return K.Part(part.shape, part.fills, K.outline(part.shape) + out, meta)

    return K.Hand(fix(hand.hand), hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, hand.stub)


def clear_caps(part: K.Part, front, *, out=1.0) -> K.Part:
    """``part`` (an attribute a hand closes on) with its lines cut ``out`` px
    OUTSIDE the ``front`` region (the hand). The scene cuts lines behind a
    front object 0.5 px inside it, so a MEDIUM line's round cap reaches
    ≈ 2 px in — past the front object's own MEDIUM outline (1.55 px each
    side): a staff contour showed as a round nub on the fist's edge. Cut
    this way, the cap stays under the outline."""
    zone = K.R(front).buffer(out, quad_segs=16)
    return K.Part(part.shape, part.fills, K.clip_out(part.lines, zone, eps=0.0), part.meta)


def seat_fingers(hand: K.Hand, *, reach=3.5) -> K.Hand:
    """A kit palm-view fist whose finger lines END ON the cusp between two
    fingertip curls: the kit runs the lines between the 2nd/3rd and 3rd/4th
    curls ≈ 0.8–2.4 px past the cusp, so their round caps poked ≈ 1 px
    out of the curl stack's edge (a nub at 12×). Each finger-line end within
    ``reach`` of a cusp (the midpoint of two curl ends that nearly meet) is
    moved onto it. Applies to rebuilt hands too."""

    def fix(part):
        inner = part.meta["inner"]
        pls = _polylines(inner)
        ends = [q for m, qs in pls if m.role.split("@")[0] == "fingertip" for f in qs for q in (f[0], f[-1])]
        cusps = []
        for i, p in enumerate(ends):
            for q in ends[i + 1:]:
                if float(np.hypot(*(p - q))) < 1.5:
                    cusps.append((p + q) / 2)
        out = C.Frag([m for m in inner.marks if m.kind == "fill" or m.role.split("@")[0] != "finger"], inner.meta)
        for m, qs in pls:
            if m.role.split("@")[0] != "finger":
                continue
            for q in qs:
                q = np.array(q, float)
                for k in (0, -1):
                    if not cusps:
                        break
                    cp = min(cusps, key=lambda c_: float(np.hypot(*(c_ - q[k]))))
                    if float(np.hypot(*(cp - q[k]))) < reach:
                        q[k] = cp
                out += K.line(C.polyline_d(q), m.w, role="finger")
        rb = part.meta.get("rebuild")
        meta = {**part.meta, "inner": out}
        if rb is not None:
            meta["rebuild"] = lambda u, rb=rb: fix(rb(u))
        return K.Part(part.shape, part.fills, K.outline(part.shape) + out, meta)

    return K.Hand(fix(hand.hand), hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, hand.stub)


def soft_heel(hand: K.Hand, *, corner, r=6.0, find=3.0) -> K.Hand:
    """A kit palm-view fist whose heel leaves the fist's underside in a
    concave arc of radius ``r`` instead of a square step. With a short
    wrist (K♣: 0.85 × the block) the kit's heel curve degenerates to its
    chord — the wrist's inner edge runs straight into the block's underside
    at the heel's floor (7.3 px off the shaft) in a hard 118° corner. Here
    the edge leaves the underside at that same floor point (so the paper
    between heel and shaft never narrows) and turns down the wrist on a
    circle of radius ``r``: the ground inside the arc is taken off the
    hand (the wrist's inner edge moves in by ≈ 0.53 r below it, as the K♠'s
    longer wrist curves in). ``corner``: the screen point of the step
    (the heel's floor on the underside); the vertex nearest it within
    ``find`` px is used. Applies to rebuilt hands too (``add_to`` re-aims
    the wrist)."""
    corner = np.asarray(corner, float)

    def fix(part):
        shp = part.shape
        ring = LineString(shp.exterior.coords)
        s0 = ring.project(Point(*corner))
        A = np.asarray(ring.interpolate(s0).coords[0])
        if float(np.hypot(*(A - corner))) > find:
            return part
        L = ring.length
        pa = np.asarray(ring.interpolate((s0 - 6.0) % L).coords[0])
        pb = np.asarray(ring.interpolate((s0 + 6.0) % L).coords[0])
        # the underside runs level into the corner; the wrist's edge leaves it downward
        prev, nxt = (pa, pb) if pb[1] > pa[1] else (pb, pa)
        e1 = _unit(A - prev)                       # arriving along the underside
        e2 = _unit(nxt - A)                        # leaving down the wrist
        th = math.acos(max(-1.0, min(1.0, float(np.dot(e1, e2)))))
        if th < math.radians(20.0):
            return part
        n1 = _unit(e2 - float(np.dot(e2, e1)) * e1)
        c = A + n1 * r
        ts = np.linspace(0.0, th, 24)
        arc = [c - n1 * r * math.cos(t) + e1 * r * math.sin(t) for t in ts]
        P_ = arc[-1]
        cut = Polygon([tuple(A)] + [tuple(q) for q in arc] + [tuple(P_ + e2 * 80.0), tuple(A + e2 * 80.0)]).buffer(0)
        new = _largest(shp.difference(cut.buffer(0.02)))
        rb = part.meta.get("rebuild")
        meta = dict(part.meta)
        if rb is not None:
            meta["rebuild"] = lambda u, rb=rb: fix(rb(u))
        return K.Part(new, part.fills, K.outline(new) + part.meta["inner"], meta)

    return K.Hand(fix(hand.hand), hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, hand.stub)
