"""art/_ks_hands.py — the K♠'s orb hand and orb, refined locally on top of deck.courtkit.

The kit (``deck/courtkit.py``) is shared by all twelve courts and is not edited
from a court. What the K♠ needed beyond the kit's parameters lives here, built
from the kit's own primitives and hand language (§H.0 mitten: paper, CONTOUR
silhouette, MEDIUM interior, four fingers + three finger lines, a separate
thumb merged at its root, a tapered back running into the cuff):

``orb_cup``  the kit's ``cup`` with
             * a thumb that is a thumb: it leaves the back of the hand low on
               the wrist side and rises in one tapered sweep to a round tip on
               the orb's rim, opening a V to the index finger (the kit's thumb
               hugs the rim from under the index and reads as a fifth finger
               stub at card size), its outer edge one smooth line from the
               wrist to the tip (no knuckle bump where the thumb meets the
               back);
             * the back's little-finger edge a cubic that leaves the finger on
               its tangent (the kit's quadratic falls back to the chord when
               the tangents do not meet ahead: a corner at the knuckle);
             * no crease stubs: the only interior lines are the three finger
               lines and the index finger's edge where the thumb passes
               behind it.
``orb``      the kit's spring-vent orb with the latitude gaps as a parameter,
             so the lowest ripple can sit behind the fingers instead of
             grazing the fingertips.
``clear_grazing``  drops an attribute's pattern strokes that would run along
             the edge of the hand closed on it (a sceptre course lying on the
             top of the fist merged with its outline into one heavy band).

Both return the kit's own types (``K.Hand`` / ``K.Part``), so ``add_to`` tucks
the wrist into the cuff exactly as for a kit hand.
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


def _polys(g):
    return K._polys_of(g)


def _largest(g):
    ps = _polys(g)
    return max(ps, key=lambda q: q.area) if ps else Polygon()


def _chain(cen, widths, quad=16):
    """A tapered capsule chain: union of the hulls of consecutive discs."""
    ds = [Point(*q).buffer(max(float(w), 0.3), quad_segs=quad) for q, w in zip(cen, widths)]
    return shapely.union_all([shapely.union(a, b).convex_hull for a, b in zip(ds[:-1], ds[1:])])


def _cubic_edge(p0, u0, p1, u1, k=0.40, bulge=0.0, n=28):
    """A smooth edge from p0 leaving along u0 to p1 arriving along u1: a cubic
    Bézier with handles ``k`` × the chord (so it always leaves and arrives on
    its tangents — the kit's quadratic falls back to the straight chord when
    the tangents do not meet ahead, which leaves a corner at p0), optionally
    swollen ``bulge`` px to the screen-left of travel with a sin² profile."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    c0, c1 = p0 + _unit(u0) * k * L, p1 - _unit(u1) * k * L
    t = np.linspace(0.0, 1.0, n)[:, None]
    pts = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c0 + 3 * (1 - t) * t ** 2 * c1 + t ** 3 * p1
    if bulge:
        ch = _unit(p1 - p0)
        pts = pts + np.array([ch[1], -ch[0]]) * bulge * np.sin(np.pi * t) ** 2
    return pts


def orb(c, r=33.0, *, gaps=(8.2, 10.6, 13.8), bubble_d=13.0, color=K.GOLD) -> K.Part:
    """``K.orb`` with the latitude gaps as a parameter (same marks, roles and
    meta). The ripples still widen downward from the vent."""
    c = K.P(c)
    body = K.R(K.circle(c, r))
    top = c[1] - r
    bc = K.P(c[0], top - K.MEDIUM - K.GAP - bubble_d / 2)
    bub = K.R(K.circle(bc, bubble_d / 2 + K.MEDIUM / 2))
    shape = K.U(body, bub)
    fills = K.fill(body, color)
    lines = K.outline(body) + K.line(K.circle(bc, bubble_d / 2), K.MEDIUM, role="bubble")
    y = top + 5.5
    for g in gaps:
        y += g
        dx = math.sqrt(max(r * r - (y - c[1]) ** 2, 0))
        lines += K.line(K.arc_sag((c[0] - dx, y), (c[0] + dx, y), -(2.6 + 0.10 * (y - top))), K.FINE,
                        role="latitude")
    return K.Part(shape, fills, lines, {"c": c, "r": r, "bubble": bc})


def orb_cup(c, r, *, wrist, wrist_w=26.0, grip=0.40, fw=None, converge=0.80, knuckle=3.0,
            thumb_tip=12.0, thumb_root=(-0.50, 0.05), thumb_bow=2.0, thumb_w=None, vee=0.30,
            crease=0.0, flank_r=10.0, hypo=0.0, hypo_k=0.35, stub=K.HAND_STUB) -> K.Hand:
    """A sphere held from below by the figure's RIGHT hand (viewer's left),
    back of the hand to the viewer, wrist down and to the viewer's left
    (the kit's ``cup(side=+1)`` construction, thumb on the wrist side).

    ``grip``: fingertip centres ≈ (grip − 0.05)·r below the centre (smaller =
    fingers further up the sphere). ``thumb_tip``: the tip's centre on the
    rim, degrees below the equator. ``thumb_root``: the thumb's root on the
    back of the hand, in finger widths from the index knuckle (x, toward the
    wrist side) and in r below the knuckle row (y). ``thumb_bow``: px the
    thumb's centreline bows outward. ``vee``: where the V between thumb and
    index closes, as a fraction of the way from the knuckle row up to the
    thumb tip. ``crease``: px the index finger's edge runs on below the V
    (0: none). ``flank_r``: the fillet where the thumb's outer edge runs into
    the wrist. ``hypo_k`` / ``hypo``: the little-finger edge's handle length
    (× chord) and extra swell (in r)."""
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
        # a cubic that leaves the finger's edge on its tangent (no corner at the knuckle)
        # and arrives along the forearm
        le = K._edge(kl, dl, Wl, u, 24)
        re_ = _cubic_edge(kr, dr, Wr, u, k=hypo_k, bulge=hypo * r)
        ring = ([K.P(xb[0], y_kn - 6.0)] + list(le) + [Wl + u * stub, Wr + u * stub] + list(re_[::-1])
                + [K.P(xb[3], y_kn - 6.0)])
        back = _largest(Polygon([tuple(q) for q in ring]).buffer(0))
        # the thumb: from low on the wrist side of the back, one tapered sweep to a
        # round tip centred on the rim (the contour passes behind it)
        a = math.radians(thumb_tip)
        tip = K.P(-(r - 0.5) * math.cos(a), (r - 0.5) * math.sin(a))
        root = K.P(xb[0] + thumb_root[0] * fw, y_kn + thumb_root[1] * r)
        ch = tip - root
        nrm = _unit(K.P(ch[1], -ch[0]))                                 # screen-left of root → tip
        if nrm[0] > 0:
            nrm = -nrm                                                 # outward = toward the wrist side
        ctrl = (root + tip) / 2 + nrm * float(thumb_bow)
        cen = K._qbez(root, ctrl, tip, 20)
        ws = np.linspace(w0, w1, len(cen))
        thumb = _chain(cen, ws)
        # the web: below the V's root (``vee`` of the way from the knuckle row up to the
        # thumb tip) the ground between the thumb and the index finger is hand
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
        # the thumb's outer edge runs on into the wrist without a dent where its root
        # meets the back: a wide fillet on the wrist side only
        flank = shapely.box(-BIG, root[1] - 0.45 * (root[1] - tip[1]), xb[0] - 0.5 * fw, BIG)
        hand = hand.union(hand.buffer(float(flank_r), quad_segs=12).buffer(-float(flank_r), quad_segs=12)
                          .intersection(flank))
        # and every convex corner sharper than a 3.5 px radius (lobes and tips are rounder)
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
        # the index finger's outer edge where the thumb's root passes behind it: from the
        # V's root down into the back (joined to the outline at the V, never a stub)
        if crease:
            zone = hand.buffer(-0.3).intersection(shapely.box(-BIG, yv - 3.0, xb[0], y_kn + float(crease)))
            edge = cols[0].boundary.intersection(zone)
            for ln in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
                if ln.length >= 9.0:
                    inner += K.line(C.polyline_d(np.asarray(ln.coords)), K.MEDIUM, role="thumb")
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


def clear_grazing(part: K.Part, front, roles=("course", "hatch", "marl", "chert"), gap=None) -> K.Part:
    """``part`` without the pattern strokes that would GRAZE the edge of
    ``front`` (a hand closed on it): a stroke whose visible remainder runs
    mostly within ``gap`` of that edge — e.g. a sceptre segment's strata course
    lying along the top of the fist, which merges with the hand's outline into
    one heavy band — is dropped whole; strokes that simply pass under the
    front object (a steep crossing) are kept. Default ``gap``: the §I.12
    parallel clearance between a MEDIUM edge and a FINE line (centre to
    centre)."""
    gap = float(gap) if gap is not None else K.MEDIUM / 2 + K.GAP + K.FINE / 2
    front = K.R(front)
    zone = front.buffer(gap, quad_segs=12)
    keep = []
    for m in part.lines.marks:
        if m.kind == "fill" or m.role.split("@")[0] not in roles:
            keep.append(m)
            continue
        ls = K._stroke_lines(m.d)
        if not ls:
            keep.append(m)
            continue
        vis = shapely.union_all(ls).difference(front)
        if vis.is_empty or vis.length < 0.5:
            keep.append(m)
            continue
        near = vis.intersection(zone).length
        if near > gap and near > 0.6 * vis.length:
            continue
        keep.append(m)
    return K.Part(part.shape, part.fills, C.Frag(keep, part.lines.meta), part.meta)
