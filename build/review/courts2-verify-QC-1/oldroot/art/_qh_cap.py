"""art/_qh_cap.py — the Q♥ 1950s PETAL SWIM-CAP DIADEM (brief §H.5), v4.

"Overlapping half-hatched petals in jade forming a close cap, with a gold rim
and a gold pearl at its crown."

Construction — a compass cap on a turned sphere, projected flat:

* The skull is a sphere (centre ``c``, radius ``R`` px) turned ``yaw``
  degrees toward the viewer's right (the 3/4-right head) and nodded
  ``pitch`` degrees (we look very slightly down on the crown).
* The cap has its own POLE, tilted ``tilt`` degrees back from the vertical
  (a swim cap sits back on the head: high over the forehead, low at the
  nape). Positions on the cap are (t, phi): t = polar angle from the cap
  pole, phi = azimuth about it (0 = the front, toward the face).
* The RIM is a gold band along the cap's lower edge, t_rim(phi) running
  high across the forehead, dipping over the ears and low at the nape.
* PETALS hang in rows like shingles, tips DOWN (away from the pole); rows
  nearer the pole lie IN FRONT and cover the roots of the row below, so each
  row shows its rounded ends. Each petal's tip lifts a little off the
  skull (``lift``), so at the limb the petals break the silhouette into a
  row of petal backs — a flower, not a helmet. Each petal: one FINE midrib
  and ONE half hatched perpendicular to it (§B.2, FINE, 7.0 pitch), the
  same half on every petal (the far side, away from the light).
* The PEARL: a gold sphere at the cap pole, Aquifer contour, a Ø4.2 paper
  highlight knocked out.

Everything is sampled from exact circles on the sphere and emitted as
polylines of ≤ 0.6 px chords (smooth approximations of the projected arcs).
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


def _rx(v, deg):
    a = math.radians(deg)
    x, y, z = v
    return np.array([x, y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)])


def _ry(v, deg):
    a = math.radians(deg)
    x, y, z = v
    return np.array([x * math.cos(a) + z * math.sin(a), y, -x * math.sin(a) + z * math.cos(a)])


class Cap:
    """The cap on a turned sphere. Head coordinates: a = the head's own left
    (the viewer's right when it faces us), b = up, c = front (the face)."""

    def __init__(self, c, R, *, yaw=24.0, pitch=10.0, tilt=24.0, t_front=66.0, t_back=104.0, t_side=92.0,
                 rim_h=10.0):
        self.c, self.R = P(c), float(R)
        self.yaw, self.pitch, self.tilt = yaw, pitch, tilt
        self.t_front, self.t_back, self.t_side = t_front, t_back, t_side
        self.rim_h = rim_h
        al = math.radians(tilt)
        self.n = np.array([0.0, math.cos(al), -math.sin(al)])          # cap pole: up and back
        self.e1 = np.array([0.0, math.sin(al), math.cos(al)])          # toward the face
        self.e2 = np.cross(self.n, self.e1)                              # sideways
        # which way e2 points on screen: pick so phi > 0 is the viewer's right
        if self.view(self.e2)[0] < 0:
            self.e2 = -self.e2

    # ---- frames ------------------------------------------------------------
    def dir(self, t, phi):
        t, phi = math.radians(t), math.radians(phi)
        return math.cos(t) * self.n + math.sin(t) * (math.cos(phi) * self.e1 + math.sin(phi) * self.e2)

    def view(self, v):
        """head → view (x right, y up, z toward the viewer)."""
        w = _ry(np.asarray(v, float), self.yaw)        # face turns toward +x
        return _rx(w, self.pitch)                      # crown tips toward the viewer

    def screen(self, v, r=1.0):
        w = self.view(v) * r
        return P(self.c[0] + self.R * w[0], self.c[1] - self.R * w[1]), w[2]

    def pt(self, t, phi, r=1.0):
        return self.screen(self.dir(t, phi), r)

    def t_rim(self, phi):
        """The rim's lower edge: t_front at the face, t_side over the ears,
        t_back at the nape (smooth in phi)."""
        c_ = math.cos(math.radians(phi))
        s2 = math.sin(math.radians(phi)) ** 2
        base = self.t_front + (self.t_back - self.t_front) * (1 - c_) / 2
        mid = (self.t_front + self.t_back) / 2
        return base + (self.t_side - mid) * s2

    # ---- regions -------------------------------------------------------------
    def _grid_region(self, fn, s_n=48, w_n=24, zmin=0.0):
        """Union of the projected cells of a (s, w) ∈ [0,1]×[-1,1] patch; ``fn``
        maps (s, w) → (screen point, z). Only cells wholly in front."""
        S = np.linspace(0.0, 1.0, s_n + 1)
        W = np.linspace(-1.0, 1.0, w_n + 1)
        pts = np.empty((len(S), len(W), 2))
        zs = np.empty((len(S), len(W)))
        for i, s in enumerate(S):
            for j, w in enumerate(W):
                p, z = fn(s, w)
                pts[i, j] = p
                zs[i, j] = z
        cells = []
        for i in range(s_n):
            for j in range(w_n):
                if min(zs[i, j], zs[i + 1, j], zs[i + 1, j + 1], zs[i, j + 1]) <= zmin:
                    continue
                q = Polygon([pts[i, j], pts[i + 1, j], pts[i + 1, j + 1], pts[i, j + 1]])
                if q.is_valid and q.area > 1e-6:
                    cells.append(q)
                else:
                    cells.append(q.buffer(0))
        if not cells:
            return Polygon()
        g = shapely.union_all(cells).buffer(0.25, quad_segs=4).buffer(-0.25, quad_segs=4)
        if self.open_r:
            # drop the limb slivers (cells of a lifted petal grazing the horizon)
            g = g.buffer(-self.open_r, quad_segs=8).buffer(self.open_r, quad_segs=8)
        return g

    open_r = 1.6

    def dome(self, t_hi=None, r=1.0):
        """The visible cap surface from the pole down to ``t_hi(phi)``
        (default: the rim's lower edge)."""
        t_hi = t_hi or self.t_rim

        def fn(s, w):
            phi = 180.0 * w
            t = s * t_hi(phi)
            return self.pt(t, phi, r)
        return self._grid_region(fn, s_n=40, w_n=90)

    def rim(self):
        """The gold rim band: rim_h px tall (measured on the sphere) above the
        rim edge. → Part."""
        dt = math.degrees(self.rim_h / self.R)

        def fn(s, w):
            phi = 180.0 * w
            t = self.t_rim(phi) - dt * (1 - s)
            return self.pt(t, phi)
        band = self._grid_region(fn, s_n=6, w_n=180)
        band = max(K._polys_of(band), key=lambda g: g.area)
        return K.Part(band, K.fill(band, GOLD), K.outline(band), {})

    def base(self):
        """The jade cap under the petals (it shows in the notches)."""
        dt = math.degrees(self.rim_h / self.R)
        reg = self.dome(lambda phi: self.t_rim(phi) - dt + 0.3)
        reg = max(K._polys_of(reg), key=lambda g: g.area)
        return K.Part(reg, K.fill(reg, JADE), K.outline(reg), {})

    # ---- petals ----------------------------------------------------------------
    def T(self, phi):
        """The petal latitude scale: the rim's middle line at azimuth phi."""
        return self.t_rim(phi) - math.degrees(self.rim_h / self.R) * self.rim_mid

    rim_mid = 0.5

    def petal_fn(self, phi_c, u0, u1, half_w, *, shoulder=0.45, lift=0.06, tip="round", root=0.3):
        """(s, w) → (screen, z) for one petal: root at u0, tip at u1 (fractions
        of T(phi): the rows follow the rim as it dips over the ears), px
        half-width ``half_w`` measured on the sphere; straight-sided to
        ``shoulder`` then a rounded (elliptic) or pointed (ogive) end; lifted
        off the sphere by ``lift``·s² (a free petal tip stands off the cap)."""
        R = self.R
        Tc = self.T(phi_c)

        def prof(s):
            if tip == "vesica":
                # a lens of two arcs, widest at ``shoulder``; the root keeps
                # ``root`` of the width (it hides under the pearl / the row above)
                if s <= shoulder:
                    u = (shoulder - s) / shoulder
                    return max(root, math.sqrt(max(1 - u * u, 0.0)) ** 0.9)
                u = (s - shoulder) / (1 - shoulder)
                return max(1 - u * u, 0.0) ** 0.62
            if s <= shoulder:
                return 1.0
            u = (s - shoulder) / (1 - shoulder)
            if tip == "round":
                return math.sqrt(max(1 - u * u, 0.0))
            return max(1 - u * u * (1.2 - 0.2 * u), 0.0) ** 0.75

        def fn(s, w):
            u = u0 + (u1 - u0) * s
            hw = half_w * prof(s)
            st = max(math.sin(math.radians(u * Tc)), 0.08)
            phi = phi_c + math.degrees(w * hw / (R * st))
            t = u * self.T(phi)
            return self.pt(t, phi, 1.0 + lift * s * s)
        return fn

    def petal(self, phi_c, u0, u1, half_w, **kw):
        fn = self.petal_fn(phi_c, u0, u1, half_w, **kw)
        return self._grid_region(fn, s_n=48, w_n=16), fn

    def petals(self, u0, u1, n, *, phase=0.0, half_w=None, widen=1.0, hatch_side=+1, rib=True, hatch=True,
               tip="vesica", lift=0.06, shoulder=0.5, root=0.3, rib_to=0.86, min_area=120.0, hatch_rel=90.0):
        """n separate petals (one Part each), sorted BACK TO FRONT by the
        depth of their middles — overlapping like a flower seen from above.
        → list of (phi, Part)."""
        R = self.R
        if half_w is None:
            um = u0 + (u1 - u0) * shoulder
            half_w = widen * 0.5 * 2 * math.pi * R * math.sin(math.radians(um * self.T(0.0))) / n
        out = []
        for k in range(n):
            phi = (360.0 / n) * (k + phase)
            phi = ((phi + 180.0) % 360.0) - 180.0
            reg, fn = self.petal(phi, u0, u1, half_w, tip=tip, lift=lift, shoulder=shoulder, root=root)
            if reg.is_empty or reg.area < min_area:
                continue
            reg = max(K._polys_of(reg), key=lambda g: g.area)
            _, zmid = fn(0.5, 0.0)
            lines = K.outline(reg)
            if rib:
                ss = np.linspace(0.08, rib_to, 48)
                pz = [fn(s_, 0.0) for s_ in ss]
                pts = np.array([p for p, z in pz if z > 0])
                if len(pts) > 2:
                    lines += K.clip_in(C.stroke(C.polyline_d(pts), FINE, color=INK, role="midrib"),
                                       reg.buffer(-(MEDIUM / 2 + 0.3)))
            if hatch:
                def half_fn(s_, w, fn=fn):
                    return fn(s_, (w + 1) / 2 * hatch_side)
                half = self._grid_region(half_fn, s_n=48, w_n=8).intersection(reg)
                a0, _ = fn(0.30, 0.0)
                a1, _ = fn(0.75, 0.0)
                ax = math.degrees(math.atan2(a1[1] - a0[1], a1[0] - a0[0]))
                lines += K.hatch_in(half, angle=ax + hatch_rel, origin=tuple(a1))
            out.append((zmid, phi, K.Part(reg, K.fill(reg, JADE), lines, {"phi": phi, "fn": fn})))
        out.sort(key=lambda q: q[0])
        return [(phi, pt) for _, phi, pt in out]

    def row(self, u0, u1, n, *, phase=0.0, half_w=None, widen=1.0, hatch_side=+1, rib=True, hatch=True,
            tip="round", lift=0.06, shoulder=0.45, skip=(), clip=None):
        """n petals round the cap (azimuths 360/n apart, offset ``phase``
        steps), root u0, tip u1. ``half_w`` default: touching at the
        shoulder latitude × ``widen``. Visible ones only. → Part (meta:
        petals)."""
        R = self.R
        if half_w is None:
            um = u0 + (u1 - u0) * shoulder
            half_w = widen * 0.5 * 2 * math.pi * R * math.sin(math.radians(um * self.T(0.0))) / n
        regs, info = [], []
        for k in range(n):
            if k in skip:
                continue
            phi = (360.0 / n) * (k + phase)
            phi = ((phi + 180.0) % 360.0) - 180.0
            reg, fn = self.petal(phi, u0, u1, half_w, tip=tip, lift=lift, shoulder=shoulder)
            if reg.is_empty or reg.area < 25.0:
                continue
            if clip is not None:
                reg = reg.intersection(clip)
                if reg.is_empty or reg.area < 25.0:
                    continue
            regs.append(reg)
            info.append(dict(phi=phi, fn=fn, reg=reg))
        if not regs:
            return K.Part(Polygon(), C.Frag(), C.Frag(), {"petals": []})
        shape = shapely.union_all(regs)
        lines = C.Frag()
        for q in info:
            reg = q["reg"]
            lines += K.outline(reg)
            fn = q["fn"]
            if rib:
                ss = np.linspace(0.0, 0.86, 40)
                pz = [fn(s_, 0.0) for s_ in ss]
                pts = np.array([p for p, z in pz if z > 0])
                if len(pts) > 2:
                    lines += K.clip_in(C.stroke(C.polyline_d(pts), FINE, color=INK, role="midrib"),
                                       reg.buffer(-(MEDIUM / 2 + 0.3)))
            if hatch:
                def half_fn(s_, w, fn=fn):
                    return fn(s_, (w + 1) / 2 * hatch_side)
                half = self._grid_region(half_fn, s_n=36, w_n=8).intersection(reg)
                a0, _ = fn(0.35, 0.0)
                a1, _ = fn(0.80, 0.0)
                ax = math.degrees(math.atan2(a1[1] - a0[1], a1[0] - a0[0]))
                lines += K.hatch_in(half, angle=ax + 90.0, origin=tuple(a1))
        return K.Part(shape, K.fill(shape, JADE), lines, {"petals": info})

    def pearl(self, d=16.0, *, t=0.0, phi=0.0, r=1.08, hl=4.2):
        c, _ = self.pt(t, phi, r)
        disc = K.R(K.circle(c, d / 2))
        hole = K.R(K.circle(c + P(-d * 0.18, -d * 0.18), hl / 2))
        return K.Part(disc, K.fill(disc.difference(hole), GOLD), K.outline(disc), {"c": c})


# ---------------------------------------------------------------------------
# v5: a ring of long petals drawn as the deck's leaf (screen-space vesicas)
# ---------------------------------------------------------------------------
def radial_petals(cap, *, n=8, phase=0.5, reach=0.97, width=0.46, root_r=6.0, hatch_side=+1, hatch_rel=90.0,
                  min_area=90.0, clip=None):
    """The petals of the §H.5 swim cap as a flower seen from above: ``n``
    long petals radiating from the pearl (the cap's pole) to the rim, each
    the deck's leaf (§G.4's vesica: two equal arcs) in screen space from a
    point ``root_r`` px out from the pole toward its tip on the rim's middle
    line (``reach`` of the latitude scale T, azimuth 360/n·(k + phase)),
    ``width`` × its length wide; a FINE midrib on the chord and ONE half
    hatched across it (§B.2's leaf rule, the same half on every petal, 7 px
    pitch). Straight midribs keep the hatch a clean ladder of 4–7 ticks
    (the projected-sphere petals' curved halves left 2–3, which read as
    letters). Sorted back to front by the depth of the tip; clipped to
    ``clip`` (the dome). → list of (phi, Part)."""
    pole, _ = cap.pt(0.0, 0.0)
    out = []
    for k in range(n):
        phi = (360.0 / n) * (k + phase)
        phi = ((phi + 180.0) % 360.0) - 180.0
        tip, z = cap.pt(reach * cap.T(phi), phi)
        if z <= 0.05:
            continue
        v = tip - pole
        L = float(np.hypot(*v))
        if L < 12.0:
            continue
        u = v / L
        p0 = pole + u * root_r
        reg = K.R(K.vesica(p0, tip, width * (L - root_r)))
        if clip is not None:
            reg = reg.intersection(clip)
        polys = [g for g in K._polys_of(reg) if g.area > 1.0]
        if not polys:
            continue
        reg = max(polys, key=lambda g: g.area)
        if reg.area < min_area:
            continue
        lines = K.outline(reg)
        inner = reg.buffer(-(MEDIUM / 2 + 0.3))
        lines += K.clip_in(K.seg(p0, tip, FINE, role="midrib"), inner)
        half = reg.intersection(K.halfplane(p0, tip, side=hatch_side)).buffer(-0.05)
        ang = math.degrees(math.atan2(v[1], v[0]))
        lines += K.hatch_in(half, angle=ang + hatch_rel, origin=tuple(tip))
        out.append((z, phi, K.Part(reg, K.fill(reg, JADE), lines, {"phi": phi, "tip": tip})))
    out.sort(key=lambda q: q[0])
    return [(phi, pt) for _, phi, pt in out]


def snap_to_limb(part, dome, snap=7.0):
    """A petal whose edge runs a few px inside the cap's silhouette leaves a
    jade sliver trapped between its MEDIUM outline and the CONTOUR (an ink
    solid over jade: QA 4c). Carry the petal out to the silhouette wherever
    it comes within ``snap`` px of it, and redraw its outline."""
    reg = part.shape
    band = dome.difference(dome.buffer(-snap))
    reg2 = reg.union(reg.buffer(snap, join_style=1).intersection(band)).intersection(dome)
    reg2 = max(K._polys_of(reg2.buffer(0)), key=lambda g: g.area)
    reg2 = Polygon(reg2.exterior)                 # no pinholes between the petal and the limb
    keep = part.lines.select(lambda m: m.role not in ("outline",))
    return K.Part(reg2, K.fill(reg2, JADE), K.outline(reg2) + keep, part.meta)


# ---------------------------------------------------------------------------
# v6: the cap as a ROSETTE of the deck's leaf, drawn flat (screen space)
# ---------------------------------------------------------------------------
def leaf_petal(root, tip, width, *, bend=0.0, shoulder=0.42, root_w=0.34, p=0.62, hatch_side=+1,
               rib=(0.10, 0.84), hatch=True, n=72, color=JADE, clip=None):
    """One petal: the deck's leaf (§G.4) bent ``bend`` px (sagitta; + bulges
    to the screen-left of root → tip) — widest at ``shoulder``, pointed at
    the tip, ``root_w`` of its width kept at the root (it hides under the
    petal or the pearl in front). A FINE midrib and ONE half hatched across
    it (§B.2's leaf rule, FINE at 7.0). → Part (meta: tip, root, mid)."""
    root, tip = P(root), P(tip)
    v = tip - root
    L = float(np.hypot(*v))
    u = v / L
    nl = np.array([u[1], -u[0]])                    # screen-left of travel (y down)
    ts = np.linspace(0.0, 1.0, n)
    cen = np.array([root + v * t + nl * bend * 4 * t * (1 - t) for t in ts])
    tan = np.array([v + nl * bend * 4 * (1 - 2 * t) for t in ts])
    tan = tan / np.hypot(tan[:, 0], tan[:, 1])[:, None]
    nrm = np.stack([tan[:, 1], -tan[:, 0]], axis=1)

    def f(t):
        if t <= shoulder:
            q = (shoulder - t) / shoulder
            return max(root_w, (1 - q * q) ** p)
        q = (t - shoulder) / (1 - shoulder)
        return max(1 - q * q, 0.0) ** p
    hw = np.array([width / 2 * f(t) for t in ts])
    left = cen + nrm * hw[:, None]
    right = cen - nrm * hw[:, None]
    reg = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    if clip is not None:
        reg = max(K._polys_of(reg.intersection(clip)), key=lambda g: g.area)
    lines = K.outline(reg)
    if rib:
        i0, i1 = int(rib[0] * (n - 1)), int(rib[1] * (n - 1))
        lines += K.clip_in(C.stroke(C.polyline_d(cen[i0:i1 + 1]), FINE, color=INK, role="midrib"),
                           reg.buffer(-(MEDIUM / 2 + 0.3)))
    if hatch:
        side = left if hatch_side > 0 else right
        half = Polygon(np.vstack([side, cen[::-1]])).buffer(0).intersection(reg).buffer(-0.05)
        ang = math.degrees(math.atan2(u[1], u[0]))
        lines += K.hatch_in(half, angle=ang + 90.0, origin=tuple(tip))
    return K.Part(reg, K.fill(reg, color), lines, {"tip": tip, "root": root, "mid": cen[n // 2]})


def ray_to(reg, origin, ang, overshoot=0.0, max_len=200.0):
    """Distance from ``origin`` along screen angle ``ang`` to the far edge of
    ``reg`` (+ overshoot)."""
    o = P(origin)
    d = P(math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    ln = LineString([tuple(o), tuple(o + d * max_len)])
    g = ln.intersection(reg)
    if g.is_empty:
        return None
    L = max(o_.length for o_ in (g.geoms if hasattr(g, "geoms") else [g]))
    # the segment inside reg that starts at the origin
    return float(L) + overshoot


def _ray_hit(reg, origin, ang, max_len=200.0):
    """Distance from ``origin`` along screen angle ``ang`` to the first point
    of ``reg`` (None if the ray misses it)."""
    o = P(origin)
    d = P(math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    g = LineString([tuple(o), tuple(o + d * max_len)]).intersection(reg)
    if g.is_empty:
        return None
    return float(min(Point(tuple(o)).distance(q) for q in (g.geoms if hasattr(g, "geoms") else [g])))


def rosette(pole, dome, tiers, *, front_x=395.0, hatch_side=+1, stop=None, stop_gap=7.0, clip=None):
    """Petals radiating from ``pole`` over the ``dome`` region, in tiers
    (back tier first). Each tier: dict(angles=[screen °], frac=, over=,
    width=, bend=, min_len=, lens={angle: len}). A petal's length is ``frac``
    of the pole→dome-edge distance along its angle plus ``over`` px (the tips
    of the back tier stand past the dome, scalloping the silhouette). Within
    a tier petals are stacked from the one farthest from ``front_x`` (the
    front of the cap: the face side) to the nearest. → [(name, Part)]."""
    pole = P(pole)
    out = []
    for k, tr in enumerate(tiers):
        parts = []
        for a in tr["angles"]:
            L = tr.get("lens", {}).get(a)
            if L is None:
                d = ray_to(dome, pole, a)
                if d is None:
                    continue
                L = d * tr.get("frac", 1.0) + tr.get("over", 0.0)
                if stop is not None:
                    # a tip pointing at the rim stops short of it on the
                    # jade base (a petal edge crossing the band's edge at a
                    # shallow angle leaves slivers under the ink: QA 4c)
                    h = _ray_hit(stop, pole, a)
                    if h is not None:
                        L = min(L, h - stop_gap)
            if L < tr.get("min_len", 14.0):
                continue
            r0 = tr.get("r0", 0.0)
            dvec = P(math.cos(math.radians(a)), math.sin(math.radians(a)))
            root, tip = pole + dvec * r0, pole + dvec * L
            # bulge away from the vertical through the pole, as a meridian of
            # a dome seen from the front does (+ = the screen-left of travel)
            bend = tr.get("bend", 0.0) * float(dvec[0])
            w = tr["width"]
            if isinstance(w, (list, tuple)):              # (fraction of length, min, max)
                w = min(max(w[0] * (L - r0), w[1]), w[2])
            pt = leaf_petal(root, tip, w, bend=bend, shoulder=tr.get("shoulder", 0.42),
                            root_w=tr.get("root_w", 0.34), hatch_side=hatch_side, clip=clip)
            seam = tr.get("seam")
            if seam is None:
                key = -abs(float(tip[0]) - front_x)
            else:
                # PINWHEEL: each petal laps over the one before it (clockwise),
                # so every petal shows the same (hatched) half; the one lap
                # that closes the ring sits at ``seam``
                key = (a - seam) % 360.0
            parts.append((key, f"petal{k}_{a:.0f}", pt))
        parts.sort(key=lambda q: q[0])
        out += [(nm, pt) for _, nm, pt in parts]
    return out
