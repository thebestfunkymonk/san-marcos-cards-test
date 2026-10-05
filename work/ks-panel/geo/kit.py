"""Compass-and-ruler construction kit for HEADWATERS courts.

Everything a court figure is built from lives here:

* exact circular arcs (SVG ``A``) defined the way a draughtsman would with a
  compass: by centre + radius + angles, by three points, or by a chord and its
  sagitta (``arc_sag``); tangent arc chains via ``deck.motifs.Turtle``;
* closed shapes assembled from those arcs and straight lines (``Path``);
* the Moss egg (the face kit head), vesicas, rounded rectangles;
* a painter's-order ``Scene`` that turns an ordered stack of objects into a
  flat, plate-separated drawing: every object hides whatever lies behind it
  GEOMETRICALLY (fills are differenced with a 1.6 px trap, lines are clipped
  0.5 px under the front contour), so paper-coloured paint is never used;
  objects may carry a HALO (a geometric paper channel, the Drifters treatment
  of hands and attributes); the figure's outer silhouette (the union of every
  object's opaque region) is stroked once at CONTOUR, so interior boundaries
  stay MEDIUM automatically (§B.2: 2 : 1 contour to detail);
* ``heal``: a final pass that measures pieces exactly as QA check 12 does and
  repairs, locally, the near-misses clipping leaves at corners (§I.12);
* ``current_lines``: concentric-arc current lines with staggered terminals.

Coordinates are card px (750 x 1050, y down). Angles are screen degrees
(0 = +x, 90 = down, positive = clockwise on screen), as in deck.motifs.
Nothing here scales a stroke; transforms are rigid only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import shapely
import shapely.prepared
from shapely.geometry import LineString, MultiLineString, Polygon

from deck import tokens as T
from deck.motifs import core as C
from inkkit import geom as G

AX = float(T.CX)          # the figure axis, x = 375
BIG = 5000.0

FINE, MEDIUM, RULE, CONTOUR, HAIR = T.FINE, T.MEDIUM, T.RULE, T.CONTOUR, T.HAIRLINE
INK, RED, JADE, GOLD, PAPER = T.INK, T.RED, T.JADE, T.FOIL, T.PAPER
PITCH = T.HATCH_PITCH
TD = T.TERMINAL_D


def _f(v):
    return f"{float(v):.3f}".rstrip("0").rstrip(".")


def P(x, y=None):
    if y is None:
        x, y = x
    return np.array([float(x), float(y)])


# =============================================================================
# circles and arcs (the compass)
# =============================================================================
def circ3(p0, p1, p2):
    """Centre and radius of the circle through three points."""
    (ax, ay), (bx, by), (cx, cy) = p0, p1, p2
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        raise ValueError("circ3: collinear points")
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    c = np.array([ux, uy])
    return c, float(np.hypot(*(np.asarray(p0, float) - c)))


def left_normal(p0, p1):
    d = np.asarray(p1, float) - np.asarray(p0, float)
    L = float(np.hypot(*d))
    return np.array([d[1], -d[0]]) / L          # screen-left of travel (y down)


def sag_centre(p0, p1, sag):
    """Centre/radius of the arc p0→p1 whose midpoint bulges ``sag`` px to the
    screen-left of the chord (negative = right)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    c = L / 2
    s = abs(sag)
    R = (c * c + s * s) / (2 * s)
    n = left_normal(p0, p1) * (1 if sag > 0 else -1)
    m = (p0 + p1) / 2
    return m + n * (s - R), R


def arc_sag(p0, p1, sag, move=True):
    """Exact circular arc from p0 to p1 bulging ``sag`` px to the screen-left
    of p0→p1 (a compass arc given by its chord and sagitta)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    head = f"M{_f(p0[0])} {_f(p0[1])}" if move else ""
    if abs(sag) < 1e-9:
        return head + f"L{_f(p1[0])} {_f(p1[1])}"
    L = float(np.hypot(*(p1 - p0)))
    R = ((L / 2) ** 2 + sag * sag) / (2 * abs(sag))
    large = 1 if abs(sag) > L / 2 else 0
    sweep = 1 if sag > 0 else 0
    return head + f"A{_f(R)} {_f(R)} 0 {large} {sweep} {_f(p1[0])} {_f(p1[1])}"


def arc3(p0, pm, p1, move=True):
    """Exact arc from p0 through pm to p1."""
    c, r = circ3(p0, pm, p1)
    # direction: is pm to the left of p0->p1 ?
    n = left_normal(p0, p1)
    side = float(np.dot(np.asarray(pm, float) - np.asarray(p0, float), n))
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    # sagitta of the pm-side arc: apex = m + n (dcm ± r)
    m = (p0 + p1) / 2
    dcm = float(np.dot(c - m, n))                     # centre offset along n
    s = dcm + r if side > 0 else dcm - r
    return arc_sag(p0, p1, s, move=move)


def arc_c(c, r, a0, a1, move=True):
    """Arc of the circle (c, r) from screen angle a0 to a1 (a1 > a0: clockwise)."""
    return C.arc_d(c[0], c[1], r, a0, a1, move=move)


def polar(c, r, deg):
    a = math.radians(deg)
    return np.array([c[0] + r * math.cos(a), c[1] + r * math.sin(a)])


def ang(c, p):
    return math.degrees(math.atan2(p[1] - c[1], p[0] - c[0]))


def circle(c, r):
    return G.circle_d(c[0], c[1], r)


def line_circle(p, u, c, r):
    """Intersections p + t u with circle (c, r): list of points (t ascending)."""
    p, u, c = np.asarray(p, float), np.asarray(u, float), np.asarray(c, float)
    u = u / np.hypot(*u)
    f = p - c
    b = float(np.dot(f, u))
    disc = b * b - (float(np.dot(f, f)) - r * r)
    if disc < 0:
        return []
    s = math.sqrt(disc)
    return [p + u * (-b - s), p + u * (-b + s)]


def circle_circle(c0, r0, c1, r1):
    c0, c1 = np.asarray(c0, float), np.asarray(c1, float)
    d = float(np.hypot(*(c1 - c0)))
    if d > r0 + r1 or d < abs(r0 - r1) or d == 0:
        return []
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h = math.sqrt(max(r0 * r0 - a * a, 0))
    m = c0 + (c1 - c0) * a / d
    n = np.array([-(c1 - c0)[1], (c1 - c0)[0]]) / d
    return [m + n * h, m - n * h]


# =============================================================================
# paths
# =============================================================================
class Path:
    """Tiny path builder: exact lines and arcs, closed or open.

        Path(p0).line(p1).sag(p2, 6).arc3(pm, p3).close().d
    """

    def __init__(self, p0):
        self.p = P(p0)
        self.start = self.p.copy()
        self.parts = [f"M{_f(self.p[0])} {_f(self.p[1])}"]

    def line(self, p):
        p = P(p)
        self.parts.append(f"L{_f(p[0])} {_f(p[1])}")
        self.p = p
        return self

    def sag(self, p, s):
        p = P(p)
        self.parts.append(arc_sag(self.p, p, s, move=False))
        self.p = p
        return self

    def arc3(self, pm, p):
        p = P(p)
        self.parts.append(arc3(self.p, pm, p, move=False))
        self.p = p
        return self

    def arc_to(self, c, r, p, cw=True):
        """Along circle (c, r) from the current point to p (both on it)."""
        p = P(p)
        self.parts.append(C.arc_between(c, r, self.p, p, cw=cw, move=False))
        self.p = p
        return self

    def close(self):
        self.parts.append("Z")
        self.p = self.start.copy()
        return self

    @property
    def d(self):
        return "".join(self.parts)


def chain(p0, heading, *steps):
    """Tangent arc chain (Turtle): steps are ('fd', L) | ('arc', r, sweep).
    Returns (d, end_point, end_heading)."""
    t = C.Turtle(p0[0], p0[1], heading)
    for s in steps:
        if s[0] == "fd":
            t.fd(s[1])
        else:
            t.arc(s[1], s[2])
    return t.d(), t.pos, t.heading


def rrect(x0, y0, x1, y1, r):
    return G.rect_d(x0, y0, x1 - x0, y1 - y0, r)


def moss_egg(c, r, up=True):
    """Moss egg (compass construction): circle of radius r about c; its lower
    half replaced by two arcs of radius 2r struck from the ends of the
    horizontal diameter, closed by a small arc of radius r(2 − √2) struck
    from the circle's bottom point. Width 2r, height r(4 − √2) ≈ 2.586 r.
    (Face kit head: r 44 → 88 × 113.8.)"""
    cx, cy = c
    A, B = P(cx - r, cy), P(cx + r, cy)
    D = P(cx, cy + r)                      # bottom point of the circle
    rs = r * (2 - math.sqrt(2))
    # tangent points on the small arc: along lines A→D and B→D, extended
    u_a = (D - A) / np.hypot(*(D - A))
    u_b = (D - B) / np.hypot(*(D - B))
    E = A + u_a * 2 * r                    # end of arc struck from A (radius 2r)
    F = B + u_b * 2 * r
    d = (f"M{_f(B[0])} {_f(B[1])}"
         f"A{_f(r)} {_f(r)} 0 0 0 {_f(A[0])} {_f(A[1])}"          # top half (anticlockwise on screen: over the top)
         f"A{_f(2 * r)} {_f(2 * r)} 0 0 0 {_f(F[0])} {_f(F[1])}"  # left side, struck from B
         f"A{_f(rs)} {_f(rs)} 0 0 0 {_f(E[0])} {_f(E[1])}"        # chin
         f"A{_f(2 * r)} {_f(2 * r)} 0 0 0 {_f(B[0])} {_f(B[1])}Z")
    return d, {"top": cy - r, "chin": cy + r + rs, "A": A, "B": B, "E": E, "F": F}


def vesica(p0, p1, width):
    return C.vesica_d(p0, p1, width)


# =============================================================================
# regions (shapely) and d
# =============================================================================
def R(x):
    """Any closed d / shapely → valid shapely region."""
    if x is None:
        return Polygon()
    if isinstance(x, shapely.Geometry):
        return x if x.is_valid else shapely.make_valid(x)
    return C.region(x)


def D(g):
    """shapely → path d."""
    if isinstance(g, str):
        return g
    return G.from_shape(g)


def U(*xs):
    gs = [R(x) for x in xs if x is not None]
    return shapely.union_all(gs) if gs else Polygon()


def mirror(x, axis=AX):
    """Mirror a d, a Frag, or a shapely region about x = axis."""
    if isinstance(x, C.Frag):
        return x.mirror_x(axis)
    if isinstance(x, shapely.Geometry):
        return shapely.affinity.scale(x, -1, 1, origin=(axis, 0))
    return G.mirror_x(x, axis)


def bi(x, axis=AX):
    """Bilateral: x plus its mirror (Frag concatenation, region union)."""
    if isinstance(x, C.Frag):
        return x + x.mirror_x(axis)
    return U(x, mirror(x, axis))


def halfplane(p0, p1, side=+1):
    """Big polygon on the screen-left (side +1) or right (−1) of p0→p1."""
    p0, p1 = P(p0), P(p1)
    u = (p1 - p0) / np.hypot(*(p1 - p0))
    n = np.array([u[1], -u[0]]) * side
    return Polygon([p0 - u * BIG, p1 + u * BIG, p1 + u * BIG + n * BIG, p0 - u * BIG + n * BIG])


def box(x0, y0, x1, y1):
    return shapely.box(x0, y0, x1, y1)


# =============================================================================
# marks (thin wrappers over deck.motifs so every width stays legal)
# =============================================================================
def line(d, w=MEDIUM, color=INK, style="ornament", terminals=None, role=""):
    return C.stroke(d, w, style=style, color=color, terminals=terminals, role=role)


def fill(d, color):
    if isinstance(d, shapely.Geometry):
        d = D(d)
    return C.fill(d, color=color) if d else C.Frag()


def dot(p, d=TD, color=INK):
    return C.dot(p[0], p[1], d, color=color)


def outline(d, w=MEDIUM, color=INK):
    """A closed shape's own contour line (interior weight by default)."""
    if isinstance(d, shapely.Geometry):
        d = D(d)
    return C.stroke(d, w, style="ornament", color=color, role="outline")


def hatch_in(region, angle=C.DIAG, pitch=PITCH, origin=None):
    return C.hatch(R(region), angle, pitch, origin=origin)


# =============================================================================
# the painter's-order scene
# =============================================================================
@dataclass
class Item:
    name: str
    frag: C.Frag
    occ: object = None            # shapely region this item hides (its opaque body)
    sil: bool = True              # part of the figure silhouette?
    halo: float = 0.0             # >0: everything behind stops this clear of the outline (paper channel)
    halo_skip: tuple = ()         # names of items behind that the halo leaves alone (a hand's own cuff)


@dataclass
class Scene:
    """Ordered stack, back to front. ``add(name, frag, occ)`` puts an object
    in front of everything added before. ``compose()`` returns one Frag in
    which each object's marks are clipped to what is visible, plus the
    silhouette CONTOUR (union of every ``sil`` item's ``occ``)."""
    items: list = field(default_factory=list)
    clip_tol: float = 0.05

    def add(self, name, frag, occ=None, sil=True, halo=0.0, halo_skip=()):
        """Put an object in front of everything added so far. ``occ`` is its
        opaque region. ``halo`` > 0 surrounds it with a geometric paper
        channel: every fill and line behind it stops ``halo`` px clear of its
        MEDIUM outline (the Drifters treatment of hands and attributes; also
        the §B.2 interlace break). Without a halo, lines behind run under its
        contour and fills are trapped under it."""
        occ = R(occ) if occ is not None else None
        frag = flatten_fills(frag if frag is not None else C.Frag())
        self.items.append(Item(name, frag, occ, sil, halo, tuple(halo_skip)))
        return self

    def region(self, names=None, sil_only=False):
        gs = [it.occ for it in self.items if it.occ is not None and (names is None or it.name in names)
              and (not sil_only or it.sil)]
        return shapely.union_all(gs) if gs else Polygon()

    def silhouette(self):
        return self.region(sil_only=True)

    def compose(self, contour=CONTOUR, extra_front=None, heal_gaps=True):
        out = []
        acc = Polygon()            # occluders: lines run under, fills are trapped
        halos = []                 # (name, skip, halo channel region) of items in front
        for it in reversed(self.items):
            f = it.frag
            hz = [h for (nm, skip, h) in halos if it.name not in skip]
            acc_halo = shapely.union_all(hz) if hz else Polygon()
            if f and not (acc.is_empty and acc_halo.is_empty):
                f = clip_out(f, acc, self.clip_tol, halo=acc_halo)
            out.append(f)
            if it.occ is not None and not it.occ.is_empty:
                # 0.3 px closes the hairline slits left where two front objects
                # share an edge (they are flattened differently), so the trap
                # erosion never opens a strip between them
                acc = acc.union(it.occ.buffer(0.3, quad_segs=6))
                if it.halo:
                    halos.append((it.name, it.halo_skip, it.occ.buffer(it.halo + MEDIUM / 2, quad_segs=12)))
        out.reverse()
        res = C.frag(*out)
        if contour:
            res += silhouette_line(self.silhouette(), contour)
        if extra_front:
            res += extra_front
        if heal_gaps:
            res = heal(res)
        return res


LAYER_RANK = {L: i for i, L in enumerate(T.LAYERS)}


def flatten_fills(f: C.Frag) -> C.Frag:
    """Painter's order among the FILLS of one object: the print layers stack
    paper < jade < red < gold < ink regardless of drawing order, so a fill
    meant to lie in front of a fill on a HIGHER layer (a red jewel on a gold
    band) must be cut out of it geometrically. Later fills win."""
    from dataclasses import replace
    marks = list(f.marks)
    fills = [i for i, m in enumerate(marks) if m.kind == "fill"]
    for j in fills:
        mj = marks[j]
        for i in fills:
            if i >= j:
                break
            mi = marks[i]
            if mi.layer != mj.layer and LAYER_RANK[mi.layer] > LAYER_RANK[mj.layer] and mi.d:
                gi = G.to_shape(mi.d, tol=0.05)
                gj = G.to_shape(mj.d, tol=0.05)
                if gi.intersects(gj):
                    marks[i] = replace(mi, d=G.from_shape(gi.difference(gj)))
    return C.Frag(marks, f.meta)


def _lines_of(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    out = []
    for p in getattr(g, "geoms", []):
        out += _lines_of(p)
    return out


STROKE_EPS = -0.5    # strokes behind run 0.5 px INTO the front object (under its contour)
TRAP = 1.6           # fills behind run this far under the front object's contour (a trap)


def clip_out(f: C.Frag, zone, tol=0.05, eps=STROKE_EPS, trap=TRAP, extra=None, halo=None) -> C.Frag:
    """Remove the parts of ``f`` lying inside ``zone`` (a shapely region).

    * Stroke centrelines are cut |eps| px INSIDE the zone boundary, so a line
      that meets the front object ends under its contour (≥ MEDIUM, 1.55 px
      each side) and overlaps its fill: the pieces join, no hairline gap. A
      back outline that coincides with the front boundary survives whole and
      lies hidden under the front outline (fragmenting it would leave slivers).
    * Fills are differenced with the zone shrunk by ``trap`` px, so the back
      fill runs under the front contour (a trap): abutting plates overlap and
      marks touching the front contour from inside overlap the back fill."""
    from dataclasses import replace
    out = []
    z_line = zone.buffer(eps, quad_segs=8) if eps else zone
    if z_line.is_empty:
        z_line = zone
    if extra is not None and not extra.is_empty:
        z_line = z_line.union(extra)
    z_fill = zone.buffer(-trap, quad_segs=8) if trap else zone
    has_halo = halo is not None and not halo.is_empty
    if has_halo:
        z_fill = z_fill.union(halo)
    z_any = z_line.union(halo.buffer(3.2)) if has_halo else z_line
    zp = shapely.prepared.prep(z_any)
    halo_by_w = {}
    for m in f.marks:
        if m.kind == "fill":
            s = G.to_shape(m.d, tol=tol)
            if not zp.intersects(s):
                out.append(m)
                continue
            s = s.difference(z_fill)
            # drop strips narrower than 3 px left between two front objects
            # (e.g. between a halo channel and a neighbour's trap): an opening
            # of radius 1.5, applied only next to what was cut away
            if not s.is_empty:
                opened = s.buffer(-1.5, quad_segs=6).buffer(1.5, quad_segs=6)
                thin = s.difference(opened)
                if not thin.is_empty:
                    s = s.difference(thin.intersection(z_fill.buffer(3.5, quad_segs=6)))
            d = G.from_shape(s)
            if d:
                out.append(replace(m, d=d))
            continue
        lines = [LineString(np.vstack([p, p[:1]]) if c else p) for p, c in G.flatten(m.d, tol) if len(p) >= 2]
        if not lines:
            continue
        ml = MultiLineString(lines)
        if not zp.intersects(ml):
            out.append(m)
            continue
        zl = z_line
        if has_halo:
            if m.w not in halo_by_w:
                halo_by_w[m.w] = z_line.union(halo.buffer(m.w / 2, quad_segs=8))
            zl = halo_by_w[m.w]
        res = shapely.difference(ml, zl)
        try:
            res = shapely.line_merge(res)
        except shapely.errors.GEOSException:
            pass
        pieces = [np.asarray(l.coords) for l in _lines_of(res) if l.length > 0.3]
        if pieces:
            out.append(replace(m, d="".join(C.polyline_d(p) for p in pieces)))
    return C.Frag(out, f.meta)


def clip_in(f: C.Frag, zone, tol=0.05) -> C.Frag:
    """Keep only the parts of ``f`` inside ``zone``."""
    from dataclasses import replace
    out = []
    zone = R(zone)
    for m in f.marks:
        if m.kind == "fill":
            s = G.to_shape(m.d, tol=tol).intersection(zone)
            d = G.from_shape(s)
            if d:
                out.append(replace(m, d=d))
            continue
        lines = [LineString(np.vstack([p, p[:1]]) if c else p) for p, c in G.flatten(m.d, tol) if len(p) >= 2]
        if not lines:
            continue
        res = shapely.intersection(MultiLineString(lines), zone)
        try:
            res = shapely.line_merge(res)
        except shapely.errors.GEOSException:
            pass
        pieces = [np.asarray(l.coords) for l in _lines_of(res) if l.length > 0.3]
        if pieces:
            out.append(replace(m, d="".join(C.polyline_d(p) for p in pieces)))
    return C.Frag(out, f.meta)


def silhouette_line(sil, w=CONTOUR):
    """Stroke every ring of the silhouette region at CONTOUR (round joins)."""
    if sil.is_empty:
        return C.Frag()
    d = G.from_shape(sil.simplify(0.02))
    return C.stroke(d, w, style="ornament", role="contour")


# =============================================================================
# current lines (§G.24): 3–5 parallel curves at a 7 px pitch from one guide
# =============================================================================
def concentric_arcs(c, radii, a0, a1):
    """Arcs of one centre (a compass set): the exact offsets of one guide."""
    return [arc_c(c, r, a0, a1) for r in radii]


def unwrap(a0, a1, cw):
    """Return a1' ≡ a1 (mod 360) so that a0→a1' runs clockwise (a1' > a0) if
    ``cw`` else anticlockwise (a1' < a0), by less than one turn."""
    if cw:
        while a1 <= a0:
            a1 += 360.0
        while a1 - a0 > 360.0:
            a1 -= 360.0
    else:
        while a1 >= a0:
            a1 -= 360.0
        while a0 - a1 > 360.0:
            a1 += 360.0
    return a1


def current_lines(c, radii, a0, a1, region, *, end="a1", term_inset=0.0, w=FINE, color=INK, stagger=0.0):
    """Concentric guide arcs (centre c, radii, a0→a1 in screen degrees, the
    sign of a1 − a0 gives the direction) clipped to ``region``; each piece
    ends at its ``end`` side in a Ø6.3 terminal. ``term_inset`` pulls the
    terminal end back that many px along the arc from the region edge."""
    reg = R(region)
    f = C.Frag()
    span = a1 - a0
    sgn = 1.0 if span > 0 else -1.0

    def prog(q):
        th = math.degrees(math.atan2(q[1] - c[1], q[0] - c[0]))
        return ((th - a0) * sgn) % 360.0

    for k_r, r in enumerate(radii):
        inset = term_inset + (stagger if k_r % 2 else 0.0)
        n = max(8, int(abs(math.radians(span)) * r / 0.5))
        th = np.radians(np.linspace(a0, a1, n + 1))
        pts = np.column_stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)])
        res = shapely.intersection(LineString(pts), reg)
        for ln in _lines_of(res):
            q = np.asarray(ln.coords)
            if len(q) < 2 or ln.length < 8:
                continue
            if prog(q[-1]) < prog(q[0]):
                q = q[::-1]
            cv = G.Curve(q)
            if inset and cv.length > inset + 6:
                if end == "a1":
                    q = cv.sub(0, 1 - inset / cv.length).pts
                else:
                    q = cv.sub(inset / cv.length, 1).pts
            f += C.stroke(q, w, color=color, role="current")
            if end:
                tp = q[-1] if end == "a1" else q[0]
                f += C.terminal(tp[0], tp[1], color=color)
    return f


# =============================================================================
# heal: remove near-misses (§I.12 / QA 12) left by clipping at corners
# =============================================================================
GAP_MIN = 3.0          # different pieces either touch or keep this much paper
GAP_FILL = 2.5         # same-layer fill pieces (a knockout line)
GAP_PAR = 4.2          # two strokes running alongside each other
PAR_RUN = 12.0         # ... for longer than this (QA 12's measure)


def _run_len(a, b):
    """QA 12's 'alongside' measure: the longer side of the minimum rotated
    rectangle of the part of ``a`` within GAP_PAR + 0.1 of ``b``."""
    near = a.intersection(b.buffer(GAP_PAR + 0.1, quad_segs=4))
    if near.is_empty:
        return 0.0
    rr = near.minimum_rotated_rectangle
    if rr.geom_type != "Polygon":
        return 0.0
    xy = np.asarray(rr.exterior.coords)
    return float(max(np.linalg.norm(xy[1] - xy[0]), np.linalg.norm(xy[2] - xy[1])))


def _mark_polys(m):
    """Outline of one mark as shapely polygons (true width, caps, joins)."""
    g = R(G.from_skia(m.skia()))
    return [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and p.area > 0.05]


def _groups(marks):
    """Group mark indices the way Frag.svg emits SVG elements: consecutive
    strokes with one style share a <path>; each fill is its own element.
    (Per layer, in mark order.)"""
    groups = []
    for lay in T.LAYERS:
        key, cur = None, []
        for i, m in enumerate(marks):
            if m.layer != lay or not m.d:
                continue
            if m.kind == "fill":
                if cur:
                    groups.append(cur)
                groups.append([i])
                key, cur = None, []
                continue
            k = (m.color, m.w, m.cap, m.join, m.miter)
            if k != key and cur:
                groups.append(cur)
                cur = []
            key = k
            cur.append(i)
        if cur:
            groups.append(cur)
    return groups


def heal(f: C.Frag, *, max_iter: int = 5, stub: float = 7.0, sliver: float = 12.0, keep_roles=("contour",),
         log=None) -> C.Frag:
    """Make every pair of drawn pieces either touch or keep the §I.12 paper
    between them, measured the way QA check 12 does: SVG elements (Frag.svg
    grouping) outlined with true widths, split into connected pieces; ≥ 3.0
    between separate pieces, ≥ 4.2 between strokes running alongside for
    ≥ 12 px, ≥ 2.5 between same-layer fills.

    Only the collateral damage of clipping is repaired, locally:
      * fill pieces thinner than HAIRLINE are dropped;
      * a stroke piece shorter than ``stub`` px (or a fill piece smaller than
        ``sliver`` px²) that nearly touches another piece is deleted;
      * a longer stroke piece is cut back, only where it nears the other
        piece, so it keeps the required clearance (an interlace-style break).
    Marks whose role is in ``keep_roles`` (the silhouette CONTOUR) are never
    modified."""
    from dataclasses import replace
    marks = list(f.marks)
    for i, m in enumerate(marks):
        if m.kind != "fill" or m.role in keep_roles:
            continue
        s = G.to_shape(m.d, tol=0.05)
        parts = [p for p in getattr(s, "geoms", [s]) if p.geom_type == "Polygon"]
        if any(p.buffer(-0.8).is_empty for p in parts):
            keep = [p for p in parts if not p.buffer(-0.8).is_empty]
            marks[i] = replace(m, d=G.from_shape(shapely.union_all(keep)) if keep else "")
    # knockout holes too close to their solid's edge (or to each other) are
    # filled: the bridge would be < 3 px (a halo may have cut the solid later)
    for i, m in enumerate(marks):
        if m.kind != "fill" or not m.d:
            continue
        s = G.to_shape(m.d, tol=0.05)
        changed = False
        polys = []
        for pg in getattr(s, "geoms", [s]):
            if pg.geom_type != "Polygon":
                continue
            ext = shapely.LinearRing(pg.exterior.coords)
            holes = [shapely.LinearRing(r.coords) for r in pg.interiors]
            keep = []
            for k, h in enumerate(holes):
                others = [ext] + [x for j, x in enumerate(holes) if j != k and x not in keep]
                if min(h.distance(o) for o in others) < GAP_MIN + 0.1:
                    changed = True
                    continue
                keep.append(h)
            polys.append(shapely.Polygon(pg.exterior.coords, [x.coords for x in keep]))
        if changed:
            marks[i] = replace(m, d=G.from_shape(shapely.union_all(polys)))
    for _ in range(max_iter):
        outl = {}
        for i, m in enumerate(marks):
            if m.d:
                outl[i] = R(G.from_skia(m.skia()))
        pieces = []                      # (polygon, [mark indices], kind, layer, protected)
        for grp in _groups(marks):
            u = shapely.union_all([outl[i] for i in grp if i in outl])
            for pg in getattr(u, "geoms", [u]):
                if pg.geom_type != "Polygon" or pg.area <= 0.05:
                    continue
                mem = [i for i in grp if outl[i].intersects(pg)]
                m0 = marks[grp[0]]
                prot = any(marks[i].role in keep_roles for i in mem)
                pieces.append((pg, mem, m0.kind, m0.layer, prot))
        if not pieces:
            break
        geoms = [p[0] for p in pieces]
        tree = shapely.STRtree(geoms)
        pairs = tree.query(geoms, predicate="dwithin", distance=GAP_PAR)
        todo = []
        for a, b in zip(*pairs):
            if a >= b:
                continue
            pa, pb = pieces[a], pieces[b]
            d = pa[0].distance(pb[0])
            if d < 0.08:
                continue
            both_fill = pa[2] == "fill" and pb[2] == "fill" and pa[3] == pb[3]
            need = GAP_FILL if both_fill else GAP_MIN
            if pa[2] == "stroke" and pb[2] == "stroke" and d >= GAP_MIN - 0.08:
                if _run_len(pa[0], pb[0]) >= PAR_RUN - 0.5:
                    need = GAP_PAR
                else:
                    continue
            if d >= need - 0.08:
                continue
            cand = [(p[0].area, p, q) for p, q in ((pa, pb), (pb, pa)) if not p[4]]
            if not cand:
                continue
            cand.sort(key=lambda t: t[0])
            _, victim, other = cand[0]
            todo.append((victim, other[0], need))
        if not todo:
            break
        for (pg, mem, kind, layer, _), other, need in todo:
            for i in mem:
                m = marks[i]
                if not m.d:
                    continue
                if m.kind == "fill":
                    s = G.to_shape(m.d, tol=0.05)
                    if pg.area < sliver:
                        s = s.difference(pg.buffer(0.2))
                    else:
                        s = s.difference(other.buffer(need + 0.1).intersection(pg.buffer(0.5)))
                    marks[i] = replace(m, d=G.from_shape(s))
                    continue
                lines = [LineString(np.vstack([p, p[:1]]) if c else p) for p, c in G.flatten(m.d, 0.05) if len(p) >= 2]
                ml = MultiLineString(lines)
                local = shapely.intersection(ml, pg.buffer(0.01))
                if local.length < stub:
                    ml = shapely.difference(ml, pg.buffer(0.3))
                else:
                    ml = shapely.difference(ml, other.buffer(need + m.w / 2 + 0.1).intersection(pg.buffer(0.5)))
                try:
                    ml = shapely.line_merge(ml)
                except Exception:
                    pass
                pcs = [np.asarray(l.coords) for l in _lines_of(ml) if l.length > 0.6]
                marks[i] = replace(m, d="".join(C.polyline_d(p) for p in pcs))
    return C.Frag([m for m in marks if m.d], f.meta)
