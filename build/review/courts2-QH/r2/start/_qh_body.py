"""art/_qh_body.py — the Q♥ body (brief §H.5): gown, bodice, partlet, pearls, arms.

The gown is built as one compass silhouette and cut into panels, so every
panel edge is shared (no slivers, no near-misses):

* SLEEVES (Spring Jade): everything outside the shoulder seams and the bodice
  sides — rounded (feminine) shoulders sloping from the pearl collar, the
  upper arms falling to the band. Parallel WAVE-LINES (Aquifer FINE compass
  waves, §H.5 'sleeves: jade, with wave-lines') inside a plain jade border
  that runs along the silhouette only.
* BODICE (Gill Red): a SWEETHEART neckline — two lobes meeting in a V (the
  heart of the House of the Fount) — and fitted sides to the band; the §G.16
  scale lattice KNOCKED OUT to paper inside a plain red border. It runs to
  the divider; no tail is ever shown.
* PARTLET (paper): the modest high front between the pearl collar and the
  sweetheart edge, carrying a half-drop grid of small rising bubbles (the
  ♥ counterpart of the K♠'s paper tunic with karst voids).
* PEARL COLLAR (gold beads, Aquifer FINE contours): strands round the base
  of the neck; a pearl trim on the sweetheart edge (gold on red only as
  contoured solids, §C.4).
* FOREARM SLEEVES (jade, wave-lines along the arm) rising from the band to
  pearl bracelets.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG

P = K.P
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR
JADE, GOLD, RED, INK = K.JADE, K.GOLD, K.RED, K.INK
BOTTOM = 548.0


# -----------------------------------------------------------------------------
# helpers
# -----------------------------------------------------------------------------
def fast_knockout(solid, frag, quad=8):
    """``solid`` minus the exact outlines of ``frag``'s strokes (their true
    widths, round caps and joins) and fills — the geometric knockout of
    deck.motifs.knockout, computed with shapely (the skia union of a dense
    lattice polyline is slow). → region."""
    reg = K.R(solid)
    holes = []
    for m in frag.marks:
        if not m.d:
            continue
        if m.kind == "fill":
            holes.append(K.R(m.d))
            continue
        for pts, closed in K.G.flatten(m.d, 0.05):
            if len(pts) < 2:
                continue
            ln = LineString(np.vstack([pts, pts[:1]]) if closed else pts)
            holes.append(ln.buffer(m.w / 2, quad_segs=quad, cap_style=1, join_style=1))
    if not holes:
        return reg
    return reg.difference(shapely.union_all(holes)).buffer(0)


def spline_pts(points, **kw):
    d, pts, _ = K.FM.arc_spline([P(q) for q in points], **kw)
    return d, np.asarray(pts)


def biggest(g):
    ps = K._polys_of(g)
    return max(ps, key=lambda q: q.area) if ps else g


def wave_lines(region, *, pitch=11.0, wl=24.0, amp=3.2, angle=0.0, origin=(375.0, 300.0), min_len=10.0,
               skip=()):
    """Parallel compass waves (half-waves of sagitta ``amp``, wavelength
    ``wl``) every ``pitch`` px, rotated ``angle`` degrees, clipped to
    ``region`` (butt on its edge). FINE Aquifer. ``skip``: (v0, v1) ranges
    of the row offset (for ``angle`` 0: the row's centre y minus the
    origin's y) whose rows are left out whole — a plain band under a pearl
    armlet. → Frag."""
    reg = K.R(region)
    if reg.is_empty:
        return C.Frag()
    x0, y0, x1, y1 = reg.buffer(40).bounds
    ox, oy = origin
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    diag = math.hypot(x1 - x0, y1 - y0) + abs(ox - (x0 + x1) / 2) + abs(oy - (y0 + y1) / 2) + 80
    f = C.Frag()
    k0, k1 = int(-diag / pitch) - 2, int(diag / pitch) + 2
    for k in range(k0, k1 + 1):
        v = k * pitch
        if any(a <= v <= b for a, b in skip):
            continue
        xs = np.arange(-diag, diag + 0.01, wl / 2)
        d = ""
        for i, (u0, u1) in enumerate(zip(xs[:-1], xs[1:])):
            s = amp if i % 2 == 0 else -amp
            p0 = P(ox + u0 * ca - v * sa, oy + u0 * sa + v * ca)
            p1 = P(ox + u1 * ca - v * sa, oy + u1 * sa + v * ca)
            d += K.arc_sag(p0, p1, s, move=(i == 0))
        ls = LineString(C.sample_d(d, 0.6)[0][0])
        if not ls.intersects(reg):
            continue
        for g in K._lines_of(ls.intersection(reg)):
            if g.length > min_len:
                f += C.stroke(C.polyline_d(np.asarray(g.coords)), FINE, color=INK, role="wave")
    return f


def pearls_on(path_pts, d_max=8.4, d_min=6.3, gap=0.0, n=None, even=False):
    """Graduated pearls (§G.29) along a path, largest at the middle, gold with
    an Aquifer FINE contour; ``gap`` = clear gap (0: strung, touching).
    → Part (shape = union of the pearls; meta 'discs')."""
    pts = np.asarray(path_pts, float)
    cv = K.G.Curve(pts)
    L = cv.length

    def sizes(m):
        if even or m == 1:
            return [d_max] * m
        t = np.abs(np.linspace(-1, 1, m))
        return list(d_min + (d_max - d_min) * (1 - t) ** 1.2)
    if n is None:
        n = 1
        while sum(sizes(n + 2)) + (n + 1) * gap <= L:
            n += 2
    ds = sizes(n)
    total = sum(ds) + (n - 1) * gap
    s = (L - total) / 2
    discs = []
    for dd in ds:
        s += dd / 2
        discs.append(Point(*cv.at_s(s)).buffer(dd / 2, quad_segs=24))
        s += dd / 2 + gap
    shape = shapely.union_all(discs)
    lines = C.Frag()
    for g in discs:
        lines += K.outline(g, FINE, role="pearl")
    return K.Part(shape, K.fill(shape, GOLD), lines, {"discs": discs})


# -----------------------------------------------------------------------------
# the gown
# -----------------------------------------------------------------------------
class Gown:
    """Compass layout of the gown (card px).

    TORSO (red): from the collar at the neck (``neck_l``/``neck_r``, the
    shoulder line's inner ends) along the shoulder tops to the armhole
    points ``arm_l``/``arm_r``, down the armhole seams (``hole_l``/``hole_r``
    control points) and the bodice sides to the band. The SWEETHEART line
    (left end, left lobe, V, right lobe, right end) splits it into the plain
    YOKE above (rising bubbles knocked out) and the LATTICE bodice below
    (§G.16 scales knocked out).

    SLEEVES (jade): each a puff (circle ``puff_*`` = (centre, r)) on the
    shoulder plus the upper arm falling to the band (outer edge through
    ``arm_out_*`` points), minus the torso."""

    def __init__(self, *, neck_l, neck_r, shoulder_l, shoulder_r, hole_l, hole_r, sweet, puff_l, puff_r,
                 out_l, out_r):
        self.neck_l, self.neck_r = P(neck_l), P(neck_r)
        _, sh_l = spline_pts([neck_l] + list(shoulder_l))       # neck → armhole top, over the shoulder
        _, sh_r = spline_pts([neck_r] + list(shoulder_r))
        _, ho_l = spline_pts([shoulder_l[-1]] + list(hole_l))   # armhole top → band
        _, ho_r = spline_pts([shoulder_r[-1]] + list(hole_r))
        self.sh_l, self.sh_r, self.ho_l, self.ho_r = sh_l, sh_r, ho_l, ho_r
        left = np.vstack([sh_l, ho_l[1:]])
        right = np.vstack([sh_r, ho_r[1:]])
        ring = np.vstack([left[::-1], right, [[right[-1][0], BOTTOM], [left[-1][0], BOTTOM]]])
        self.torso_shape = Polygon(ring).buffer(0)
        ext = np.vstack([left[::-1], right, [[right[-1][0], BOTTOM + 300], [left[-1][0], BOTTOM + 300]]])
        self.torso_ext = Polygon(ext).buffer(0)
        # sweetheart
        cl, lobe_l, V, lobe_r, cr = [P(q) for q in sweet]
        self.V = V
        _, sw_l = spline_pts([cl, lobe_l, V])
        _, sw_r = spline_pts([V, lobe_r, cr])
        self.sweet_pts = np.vstack([sw_l, sw_r[1:]])
        below = np.vstack([[[cl[0] - 60, cl[1] + 4]], self.sweet_pts, [[cr[0] + 60, cr[1] + 4]],
                           [[cr[0] + 60, BOTTOM + 300]], [[cl[0] - 60, BOTTOM + 300]]])
        self.below = Polygon(below).buffer(0)
        self.lattice_shape = self.torso_shape.intersection(self.below)
        self.yoke_shape = self.torso_shape.difference(self.below)
        # sleeves: one arc-spline outline each, from the armhole top over the
        # puff and down the outer arm to the band; the inner side is the torso
        sl = []
        self.gathers = []
        for outs, sgn, top in ((out_l, -1, shoulder_l[-1]), (out_r, +1, shoulder_r[-1])):
            o = [P(top)] + [P(q) for q in outs]
            _, op = spline_pts(o)
            ring = np.vstack([op, [[op[-1][0], BOTTOM]], [[P(top)[0] - sgn * 200, BOTTOM]],
                              [[P(top)[0] - sgn * 200, P(top)[1] + 2]]])
            reg = Polygon(ring).buffer(0).difference(self.torso_shape.buffer(-0.05))
            reg = reg.intersection(K.box(0, 0, 750, BOTTOM))
            sl.append(max(K._polys_of(reg), key=lambda g: g.area))
        self.sleeve_l, self.sleeve_r = sl
        self.puff_l, self.puff_r = puff_l, puff_r
    # --- panels ------------------------------------------------------------
    def sleeve(self, side, *, border=13.0, pitch=11.0, wl=24.0, amp=3.2, origin=(375.0, 322.0), gather=None,
               skip_y=()):
        """The jade sleeve on ``side``: wave-lines inside a plain border along
        the silhouette. ``gather`` = (p0, p1, sag): the puff's gathered lower
        edge, an arc across the sleeve (returned in meta for the pearl band)."""
        reg = self.sleeve_l if side < 0 else self.sleeve_r
        lines = K.outline(reg)
        outer_edge = reg.boundary.difference(self.torso_shape.buffer(1.0)).difference(
            K.box(0, BOTTOM - 1, 750, BOTTOM + 50))
        inner = reg.difference(outer_edge.buffer(border, quad_segs=16))
        inner = max(K._polys_of(inner), key=lambda g: g.area)
        seam = inner.boundary.intersection(reg.buffer(-(MEDIUM / 2 + K.GAP + FINE / 2)))
        seam = seam.difference(self.torso_shape.buffer(MEDIUM / 2 + K.GAP + FINE / 2))
        for ln in K._lines_of(shapely.line_merge(seam) if seam.geom_type == "MultiLineString" else seam):
            if ln.length > 8:
                lines += C.stroke(C.polyline_d(np.asarray(ln.coords)), FINE, color=INK, role="seam")
        pat = inner.buffer(-(FINE / 2 + K.GAP + FINE / 2 + 0.2), quad_segs=16)
        pat = pat.intersection(reg.buffer(-(MEDIUM / 2 + K.GAP + FINE / 2 + 0.3)))
        lines += wave_lines(pat, pitch=pitch, wl=wl, amp=amp, origin=origin,
                            skip=[(a - origin[1], b - origin[1]) for a, b in skip_y])
        return K.Part(reg, K.fill(reg, JADE), lines, {"inner": pat, "region": reg})

    def armlet(self, side, p0, p1, *, sag=-6.0, d=8.4):
        """A strung pearl armlet (gold beads, §G.29) round the puff's gathered
        base: an arc p0 → p1 across the sleeve, kept inside it. → Part."""
        reg = self.sleeve_l if side < 0 else self.sleeve_r
        pts = np.asarray(C.sample_d(K.arc_sag(P(p0), P(p1), sag), 0.3)[0][0])
        ln = LineString(pts).intersection(reg.buffer(-(d / 2 + FINE / 2 + 0.6)))
        ln = max(K._lines_of(ln), key=lambda g: g.length)
        return pearls_on(np.asarray(ln.coords), d_max=d, d_min=d, even=True)

    def torso(self, *, scale_r=9.0, border=10.0, knock=MEDIUM, origin=None, bubbles=()):
        """The red torso: the lattice bodice (scales knocked out inside a plain
        border) and the yoke (plain, with ``bubbles`` — [(path points, d0,
        d_max)] columns of rising bubbles knocked out)."""
        reg = self.torso_shape
        inner = self.torso_ext.buffer(-border, quad_segs=12).intersection(self.below.buffer(-border, quad_segs=12))
        inner = inner.intersection(K.box(0, 0, 750, BOTTOM + 10))
        org = origin if origin is not None else (self.V[0], self.V[1] + 10.0)
        lat = MG.scale_lattice(inner, scale_r, w=knock, color=INK, origin=org)
        holes = C.Frag() + lat
        for path, d0, dmax in bubbles:
            holes += C.bubble_path(np.asarray(path, float), d0, ratio=1.18, gap=None, style="dot", d_max=dmax)
        solid = fast_knockout(reg, holes)
        lines = K.outline(reg)
        return K.Part(reg, K.fill(solid, RED), lines, {"inner": inner})


# -----------------------------------------------------------------------------
# arms
# -----------------------------------------------------------------------------
def forearm(base, wrist, *, width=44.0, wrist_w=30.0, sag=0.0, color=JADE, waves=True, pitch=10.0):
    """A jade forearm sleeve from the band up to the wrist: two arcs, wave
    lines running ACROSS the arm (so they read against the upper sleeve's
    horizontal waves). → Part (meta u, n)."""
    B, W = P(base), P(wrist)
    u = (W - B) / np.hypot(*(W - B))
    n = np.array([u[1], -u[0]])
    bl, br = B + n * width / 2, B - n * width / 2
    wl, wr = W + n * wrist_w / 2, W - n * wrist_w / 2
    d = K.Path(bl).sag(wl, sag).line(wr).sag(br, -sag).close().d
    reg = K.R(d)
    lines = K.outline(reg)
    if waves:
        inner = reg.buffer(-(MEDIUM / 2 + K.GAP + FINE / 2 + 0.3))
        ang = math.degrees(math.atan2(u[1], u[0]))
        lines += wave_lines(inner, pitch=pitch, wl=20.0, amp=2.6, angle=ang, origin=tuple(W))
    return K.Part(reg, K.fill(reg, color), lines, {"u": u, "n": n, "W": W})


def bracelet(wrist, u, width, *, d=6.3, rows=1, back=0.0):
    """A strung pearl bracelet across the wrist (perpendicular to the
    forearm axis ``u``). → Part."""
    W = P(wrist) - P(u) * back
    n = np.array([u[1], -u[0]])
    p0 = W + n * (width / 2 + 1.0)
    p1 = W - n * (width / 2 + 1.0)
    pts = np.array([p0 + (p1 - p0) * t for t in np.linspace(0, 1, 60)])
    return pearls_on(pts, d_max=d, d_min=d, even=True)
