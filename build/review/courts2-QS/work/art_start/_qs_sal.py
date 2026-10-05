"""art/_qs_sal.py — Q♠ · the vision in the scrying mirror: one Texas blind
salamander (*Eurycea rathbuni*), dorsal view, paper on the mirror's jade.

The mirror's salamander is the seal's animal (tuck/_seal_salamander.py) drawn
small and reversed out: the same anatomy, simplified to what survives the
§I.12 knockout minimums (paper ≥ 2.5 wide, jade bridges ≥ 3.0):

* HEAD: broad and flat, a SHOVEL — a blunt rounded-square snout, sides
  flaring back to the cheeks (the widest part of the animal, ≈ 1.45 × the
  trunk), then a short neck. No point, no pentagon.
* EYES: vestigial, two Ø3 Aquifer dots under the skin in the front third of
  the head, set wide (they sit near the head's flanks, ≥ 3.0 of paper to the
  jade), so they read as specks, never as a face.
* GILLS: three raked red plumes a side from the back of the head, fanned and
  curling toward the tail; each a small solid frond with its filament lobes
  raked toward the tip (the seal's plume, in Gill Red on the jade). The three
  of a side root 4.2 px apart along the neck: three separate plumes with
  ≥ 2.5 of jade between them (§I.12), never one red blob.
* LIMBS: long and spindly (≈ 2.6 px paper), jointed, in a walking stride;
  three fine splayed digits each.
* TAIL: long and tapering, its FIN KEEL shown on the outer side of the curve
  as a paper blade split from the tail by a jade line (the seal's split line):
  it rises from the tail base, runs to the tip and closes there.

All geometry at final size, card px. ``salamander(c)`` → dict(body, ko, gills,
eyes, L, spine) for art._qs_parts.mirror.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.interpolate import PchipInterpolator
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G

P = K.P
KO_MIN = 2.5                                    # §I.12 knockout (paper) line

SPEC = dict(
    # the spine: snout at ``snout`` (relative to the mirror centre; re-centred
    # by ``fit``), heading ``h0`` (screen deg), curvature table (s, deg / px;
    # + turns clockwise): head carried straight, the trunk bowed a little, the
    # tail swept round in one even hook
    snout=(-22.5, -27.5), h0=50.0, L=86.0, fit=(0.0, 0.0),
    kappa=[(0.0, 0.0), (21.0, 0.0), (28.0, -0.6), (42.0, -0.5), (48.0, 2.4), (60.0, 4.0), (76.0, 3.8),
           (86.0, 3.2)],
    # half-width about the spine (s, px): the broad flat shovel head (a blunt
    # rounded-square snout flaring to the cheeks at s 16.5), the neck, trunk
    # and a long tapering tail
    hw=[(0.0, 5.2), (1.8, 5.8), (5.0, 6.8), (9.0, 7.75), (13.0, 8.05), (16.5, 8.2), (19.0, 7.6), (21.0, 6.3),
        (23.0, 5.3), (26.0, 5.1), (30.0, 5.2), (38.0, 5.4), (43.0, 5.2), (47.0, 4.8), (52.0, 4.1), (60.0, 3.3),
        (69.0, 2.4), (78.0, 1.5), (86.0, 0.0)],
    snout_cap=1.8, snout_p=2.2,
    eyes=(9.0, 3.1),                          # (s, lateral offset) of the two Ø3 dots: 3.0+ of paper round each
    eye_d=3.0,
    # gills: three plumes a side rooted on the neck contour at s, fanned at ang
    # (deg from the outward normal, + toward the tail), curling toward the
    # tail; filament lobes staggered on both edges, raked toward the tip
    gills=dict(s=(14.8, 19.0, 23.2), ang=(-24.0, 16.0, 54.0), length=(7.8, 8.6, 7.6), curl=(28.0, 24.0, 18.0),
               hw=1.45, stalk=1.0, tooth=0.9, pitch=2.4, rake=0.8, lean=0.9, root=0.32, tip=0.3, grow=0.3,
               sides=(1, -1), soft=0.25),
    # limbs: (s, side, l1, a1, l2, a2): side +1 = left of travel; a1 / a2 deg
    # from the outward normal, + toward the head (upper arm, forearm): a stride
    limbs=[(29.5, +1, 8.2, -18.0, 7.4, 48.0), (29.5, -1, 8.2, -28.0, 7.4, 18.0),
           (46.0, +1, 8.2, -32.0, 7.4, -70.0), (46.0, -1, 8.2, 2.0, 7.4, 42.0)],
    limb_w=(2.8, 2.5), joint_r=2.6,
    digits=3, digit_len=6.4, digit_spread=40.0, digit_w=2.5, digit_fillet=0.5,
    # the fin keel: extra width on the outer side of the tail (s, px), and the
    # jade split line (s0, s1) that rises on the dorsal midline at the hips and
    # eases out (split_shift) to the fin base
    fin_mode="split",
    fin=[(46.0, 0.0), (54.0, 2.4), (62.0, 3.3), (70.0, 3.0), (76.0, 1.9), (80.0, 0.6), (83.0, 0.0)],
    split=(44.0, 76.0), split_shift=(46.0, 62.0), split_w=3.0,
)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


class Spine:
    def __init__(self, c, spec):
        self.spec = spec
        L = spec["L"]
        s = np.linspace(0.0, L, int(L * 20) + 1)
        kx, ky = zip(*spec["kappa"])
        kap = np.interp(s, kx, ky)
        hd = spec["h0"] + np.concatenate([[0.0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(s))])
        hr = np.radians(hd)
        x = np.concatenate([[0.0], np.cumsum((np.cos(hr[1:]) + np.cos(hr[:-1])) / 2 * np.diff(s))])
        y = np.concatenate([[0.0], np.cumsum((np.sin(hr[1:]) + np.sin(hr[:-1])) / 2 * np.diff(s))])
        o = P(c) + P(spec["snout"])
        self.s, self.hd, self.L = s, hd, L
        self.P = np.column_stack([x + o[0], y + o[1]])
        hx, hy = zip(*spec["hw"])
        self._hw = PchipInterpolator(hx, hy, extrapolate=False)
        fx, fy = zip(*spec["fin"])
        self._fin = PchipInterpolator(fx, fy, extrapolate=False)

    def at(self, s):
        return np.array([np.interp(s, self.s, self.P[:, 0]), np.interp(s, self.s, self.P[:, 1])])

    def tan(self, s):
        return unit(float(np.interp(s, self.s, self.hd)))

    def left(self, s):
        """Normal to the left of travel on screen (y down)."""
        t = self.tan(s)
        return np.array([t[1], -t[0]])

    def hw(self, s):
        s = np.asarray(s, float)
        v = np.nan_to_num(self._hw(np.clip(s, 0, self.L)))
        c, p = self.spec["snout_cap"], self.spec["snout_p"]
        wc = float(self._hw(c))
        cap = wc * np.power(np.clip(1 - np.power(np.clip((c - s) / c, 0, 1), p), 0, 1), 1 / p)
        return np.clip(np.where(s < c, cap, v), 0, None)

    def fin(self, s):
        s = np.asarray(s, float)
        f0 = self.spec["fin"][0][0]
        v = np.nan_to_num(self._fin(np.clip(s, f0, self.L)))
        return np.where(s < f0, 0.0, np.clip(v, 0, None))

    def outer(self, s):
        """+1 if the tail's outer (convex) side at s is the left of travel."""
        k = float(np.interp(s, [a for a, _ in self.spec["kappa"]], [b for _, b in self.spec["kappa"]]))
        return +1.0 if k > 0 else -1.0      # turning clockwise (screen): the convex side is the left


def _round_corner(a, b, c, r):
    """Polyline a → b → c with the corner at b rounded on radius r."""
    a, b, c = P(a), P(b), P(c)
    u1 = (b - a) / np.linalg.norm(b - a)
    u2 = (c - b) / np.linalg.norm(c - b)
    ang = math.acos(max(-1.0, min(1.0, float(np.dot(-u1, u2)))))
    if ang > math.radians(175) or ang < 1e-3:
        return np.array([a, b, c])
    t = r / math.tan(ang / 2)
    t = min(t, 0.45 * np.linalg.norm(b - a), 0.45 * np.linalg.norm(c - b))
    p1, p2 = b - u1 * t, b + u2 * t
    q = [a]
    for k in np.linspace(0, 1, 9):
        q.append((1 - k) ** 2 * p1 + 2 * (1 - k) * k * b + k ** 2 * p2)
    q.append(c)
    return np.array(q)


def _tapered(pts, w0, w1):
    """A solid limb along ``pts``: width w0 at the root easing to w1, round ends."""
    cv = G.Curve(np.asarray(pts, float))
    L = cv.length
    ss = np.linspace(0, L, 60)
    Pp = np.array([cv.at_s(x) for x in ss])
    Nn = np.array([cv.normal_s(x) for x in ss])
    ww = (w0 + (w1 - w0) * ss / L) / 2
    left, right = Pp + Nn * ww[:, None], Pp - Nn * ww[:, None]
    reg = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    return K.U(reg, Point(*Pp[-1]).buffer(ww[-1], quad_segs=10), Point(*Pp[0]).buffer(ww[0], quad_segs=10))


def plume_polygon(pts, *, hw=1.6, stalk=1.2, tooth=1.3, pitch=2.8, rake=0.8, lean=0.9, sides=(1, -1),
                  root=0.25, tip=0.25, grow=0.3):
    """One raked gill plume on the rachis ``pts`` (root → tip): the seal's
    ``plume_polygon`` at mirror scale — a solid frond ``hw`` half-wide whose
    edges carry filament lobes ``tooth`` deep at ``pitch``, staggered side to
    side, each rising slowly toward the tip and dropping back sharply."""
    cv = G.Curve(np.asarray(pts, float))
    Lg = cv.length
    m = 400
    t = np.linspace(0, 1, m)
    s = t * Lg
    Pp = np.array([cv.at_s(x) for x in s])
    Tt = np.array([cv.tangent_s(x) for x in s])
    N = np.column_stack([Tt[:, 1], -Tt[:, 0]])
    g = np.clip(t / max(grow, 1e-6), 0, 1)
    g = 0.5 - 0.5 * np.cos(np.pi * g)
    tz = np.clip((t - (1 - tip)) / tip, 0, 1)
    rnd = np.sqrt(np.clip(1 - tz ** 2, 0, 1))
    core = (stalk + (hw - stalk) * g) * np.maximum(rnd, 0.0)
    edges = []
    for sd, phase in ((1, 0.0), (-1, 0.5)):
        u = (s - root * Lg) / pitch + phase
        fr = u - np.floor(u)
        saw = np.where(fr < rake, fr / rake, 1 - (fr - rake) / (1 - rake))
        on = 1.0 if sd in sides else 0.0
        amp = on * np.where(s < root * Lg, 0.0, 1.0) * np.clip(g * 1.4, 0, 1) * rnd
        edges.append(Pp + N * sd * (core + tooth * saw * amp)[:, None] + Tt * (lean * saw * amp)[:, None])
    poly = Polygon(np.vstack([edges[0], edges[1][::-1]])).buffer(0)
    return poly.buffer(0.3, quad_segs=6).buffer(-0.3, quad_segs=6)


def _rachis(p, h0, curl, length, n=40):
    hs = h0 + curl * np.linspace(0, 1, n) ** 1.15
    step = length / (n - 1)
    pts = [np.asarray(p, float)]
    for h in hs[:-1]:
        pts.append(pts[-1] + unit(h) * step)
    return np.array(pts)


def _biggest(g):
    ps = K._polys_of(g)
    return max(ps, key=lambda q: q.area) if ps else Polygon()


def salamander(c, **over):
    """Fit wrapper: the animal (body + gills) is centred on its smallest
    enclosing circle about ``c`` + ``spec['fit']`` (an offset), then built."""
    spec = {**SPEC, **over}
    if spec.get("fit") is not None:
        import shapely
        r0 = _salamander(c, spec)
        g = K.U(r0["body"], r0["gills"])
        m = shapely.minimum_bounding_circle(g).centroid
        want = P(c) + P(spec["fit"])
        d = want - np.array([m.x, m.y])
        spec = {**spec, "snout": tuple(P(spec["snout"]) + d)}
    out = _salamander(c, spec)
    import shapely
    out["radius"] = shapely.minimum_bounding_radius(K.U(out["body"], out["gills"]))
    return out


def _salamander(c, spec):
    """The mirror's blind salamander about the mirror centre ``c`` → dict(body
    (paper region, the fin split a jade hole in it), ko (empty Frag: limbs
    and digits are part of ``body``), gills (red region), eyes (ink Frag), L,
    spine)."""
    sp = Spine(c, spec)
    L = sp.L
    ss = np.linspace(0, L, 1400)
    Pp = np.array([sp.at(x) for x in ss])
    Nl = np.array([sp.left(x) for x in ss])
    H = sp.hw(ss)
    Fn = sp.fin(ss)
    osd = np.array([sp.outer(x) for x in ss])
    # the fin adds width on the outer side only
    hl = H + np.where(osd > 0, Fn, 0.0)
    hr = H + np.where(osd < 0, Fn, 0.0)
    left, right = Pp + Nl * hl[:, None], Pp - Nl * hr[:, None]
    body = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    body = _biggest(body)

    # limbs: tapered solids, filleted into the flank; digits fanned at the wrist
    parts = [body]
    digits = []
    for (s0, sd, l1, a1, l2, a2) in spec["limbs"]:
        p = sp.at(s0)
        out = sp.left(s0) * sd
        head_dir = -sp.tan(s0)

        def rot(deg):
            a = math.radians(deg)
            v = out * math.cos(a) + head_dir * math.sin(a)
            return v / np.linalg.norm(v)
        h = float(sp.hw(s0))
        root = p + out * (h - 2.5)
        sh = p + out * h
        el = sh + rot(a1) * l1
        wr = el + rot(a2) * l2
        pts = _round_corner(root, el, wr, spec["joint_r"])
        parts.append(_tapered(pts, *spec["limb_w"]))
        fwd = rot(a2)
        base = math.degrees(math.atan2(fwd[1], fwd[0]))
        n = spec["digits"]
        for dt in np.linspace(-spec["digit_spread"], spec["digit_spread"], n):
            q = wr + unit(base + dt) * spec["digit_len"]
            digits.append(LineString([tuple(wr - fwd * 0.8), tuple(q)]).buffer(spec["digit_w"] / 2, quad_segs=8))
    body = K.U(*parts)
    # armpit fillets (a closing): no jade sliver thinner than a hairline in a crotch
    body = body.buffer(1.1, quad_segs=10).buffer(-1.1, quad_segs=10)
    # the digits join after the fillet: each springs clean from the wrist
    body = K.U(body, *digits).buffer(spec.get("digit_fillet", 0.5), quad_segs=8).buffer(
        -spec.get("digit_fillet", 0.5), quad_segs=8)
    body = _biggest(body)

    # the fin keel
    split = Polygon()
    if spec.get("fin_mode", "split") == "split":
        # a jade split line on the tail's outer side, closed at both ends
        # inside the paper (a jade island), 2.5+ of paper each side of it
        s0, s1 = spec["split"]
        sw = spec["split_w"]
        s_ = np.linspace(s0, s1, 200)
        pts = []
        for x in s_:
            o = sp.outer(x)
            h, f = float(sp.hw(x)), float(sp.fin(x))
            lo = -h + KO_MIN + 0.25 + sw / 2
            hi = h + f - KO_MIN - 0.25 - sw / 2
            want = h - sw / 2 + spec.get("split_in", 0.3)
            sa, sb = spec.get("split_shift", (s0, s0))
            if sb > sa:                      # ease from the dorsal midline out to the fin base
                t_ = min(1.0, max(0.0, (x - sa) / (sb - sa)))
                want *= 0.5 - 0.5 * math.cos(math.pi * t_)
            if hi < lo:
                continue
            off = min(max(want, lo), hi)
            pts.append(sp.at(x) + sp.left(x) * o * off)
        if len(pts) > 4:
            split = LineString(pts).buffer(sw / 2, quad_segs=10)
            body = body.difference(split)
    else:
        # a paper fin line along the tail's outer side, ``fin_gap`` of jade
        # from it, rising free at the tail base and closing into the tip
        s0, sm = spec["fin_line"]
        fw, gap = spec["fin_w"], spec["fin_gap"]
        pts = []
        for x in np.linspace(s0, L, 240):
            o = sp.outer(x)
            h = float(sp.hw(x))
            k = min(1.0, max(0.0, (L - x) / (L - sm)))
            k = 0.5 - 0.5 * math.cos(math.pi * k)
            off = h + (gap + fw / 2) * k
            pts.append(sp.at(x) + sp.left(x) * o * off)
        fin_line = LineString(pts).buffer(fw / 2, quad_segs=10)
        body = _biggest(K.U(body, fin_line).buffer(0.4, quad_segs=8).buffer(-0.4, quad_segs=8))

    # gills: three raked plumes a side from one root on the neck contour
    g = spec["gills"]
    gill_regs = []
    for sd in (+1, -1):
        for k, sv in enumerate(g["s"]):
            out = sp.left(sv) * sd
            tail = sp.tan(sv)
            a = math.radians(g["ang"][k])
            d0 = out * math.cos(a) + tail * math.sin(a)
            p0 = sp.at(sv) + out * (float(sp.hw(sv)) - 1.2)
            cross = d0[0] * tail[1] - d0[1] * tail[0]
            sgn = 1.0 if cross > 0 else -1.0                 # curl toward the tail
            pts_r = _rachis(p0, math.degrees(math.atan2(d0[1], d0[0])), g["curl"][k] * sgn, g["length"][k])
            pg = plume_polygon(pts_r, hw=g["hw"], stalk=g["stalk"], tooth=g["tooth"], pitch=g["pitch"],
                               rake=g["rake"], lean=g["lean"], root=g["root"], tip=g["tip"], grow=g["grow"],
                               sides=tuple(g.get("sides", (1, -1))) if sd > 0 else tuple(-q for q in g.get("sides", (1, -1))))
            if g.get("soft"):
                r_ = g["soft"]
                pg = pg.buffer(r_, quad_segs=8).buffer(-2 * r_, quad_segs=8).buffer(r_, quad_segs=8)
            gill_regs.append(_biggest(pg))
    gills = K.U(*gill_regs).difference(body)
    gills = K.U(*[q for q in K._polys_of(gills) if q.area > 2.0])
    # a crumb of jade shut in between a plume's root and the neck goes paper
    pockets = [Polygon(r_) for pg in K._polys_of(K.U(body, gills)) for r_ in pg.interiors
               if Polygon(r_).area < 6.0]
    if pockets:
        body = K.U(body, *[q.buffer(0.15, quad_segs=4) for q in pockets])

    # the vestigial eyes: two Ø3 dots under the skin, in the front third
    se, lat = spec["eyes"]
    pe = sp.at(se)
    nl = sp.left(se)
    eyes = C.Frag()
    for sd in (+1, -1):
        eyes += K.dot(pe + nl * sd * lat, spec["eye_d"], color=spec.get("eye_color", K.INK), role="eye")
    return {"body": body, "ko": C.Frag(), "gills": gills, "eyes": eyes, "L": L, "spine": sp.P,
            "split": split}
