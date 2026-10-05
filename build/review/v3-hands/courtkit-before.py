"""deck.courtkit — the shared court kit for the twelve HEADWATERS courts.

One hand draws every court. This module is that hand: compass-and-ruler
primitives, a painter's-order Scene that turns a stack of parts into flat,
plate-separated, QA-clean line art, and parametric builders for every part a
court is made of (face, hair, beard, hands, garments, crowns, regalia,
pattern fills, the Lion Mark clasp). ``deck/COURT_GUIDE.md`` is the recipe;
``art/KS.py`` is the worked example.

    from deck import courtkit as K

    def build():
        sc = K.Scene(rank="K")                            # clip + heal against the band / medallion
        fc = K.face((K.AX, 207.0), "frontal", age="elder")
        sc.part("mantle", K.mantle(K.MantleSpec(), pattern_kind="strata"))   # back ...
        sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
        sc.part("crown", K.merlon_crown())
        K.fist((540.0, 419.0), back=-1).add_to(sc, "handR")                  # ... to front
        K.band_guard(sc, "K")
        return sc.layers()                                # {layer: [svg]}: build()'s return value

Conventions (the brief's and deck.motifs'):

* card px, 750 x 1050, y DOWN; the figure axis is x = 375; draw the TOP half.
* angles are SCREEN degrees: 0 = +x, 90 = down, positive = clockwise.
* every mark is a ``deck.motifs`` Frag mark, so widths are always legal
  (1.6 / 2.1 / 3.1 / 4.2 / 6.25) and colours select their print layer.
* nothing is ever scaled; parts are placed with rigid moves and ±1 mirrors.
* nothing paper-coloured is ever painted: hiding, halos, knockouts and
  interlace gaps are geometric (differences of regions).
* deterministic: no randomness, no clocks; same inputs, same SVG.

Sections
    1  compass geometry         P, polar, ang, circ3, arc_sag, arc3, arc_c, Path, chain, spline,
                                egg, moss_egg, vesica, rrect, line_circle, circle_circle, unwrap
    2  regions and marks        R, D, U, mirror, bi, box, halfplane, line, seg, fill, dot, outline,
                                hatch_in, clip_in, atomic, clip_out
    3  Part and Scene           Part, Scene (add / part / compose / layers; rank= clips + heals
                                against the band), flatten_fills, silhouette_line,
                                heal (logs every change, with the neighbour it fled)
    4  current lines (§G.24)    current_lines (safe curled terminals), lock_fan
    5  faces (§H.0)             FaceSpec, Face, face(center, gaze=frontal | 3/4-left | 3/4-right |
                                profile-left | profile-right, sex, age, lids, **overrides)
    6  hair and beards          HairSpec, hair_fall, hair_cap, hair_back, neck, BeardSpec, beard,
                                MoustacheSpec, moustache
    7  hands                    Hand (add_to tucks the wrist into the cuff), fist (any cylinder, any angle,
                                back or palm view), fist_geom / fist_wrist (where the wrist reads),
                                cup (sphere), flat (chest, belt), clear_of_hand (knockouts near a hand),
                                HandWarning, HAND_LOG
    8  garments                 MantleSpec, mantle, LensSpec, lens, tunic, lapel, SleeveSpec,
                                sleeve, standing_collar, torso, cap ('flat' | 'hood')
    9  crowns and regalia       crown_band, diadem, jewel, CrownSpec, merlon_hatch, merlon_crown,
                                orb, SceptreSpec, sceptre, staff
    10 pattern fills            pattern(region, kind) — strata, karst, karst_flooded, scales,
                                ashlar, fluting, hatch, rowels, rowels_solid, bubbles
    11 Lion Mark clasp (§G.2)   lion_clasp, band_guard
    12 output helpers           layers, BALANCE_TARGET, balance_hint
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

import numpy as np
import shapely
import shapely.affinity
import shapely.ops
import shapely.prepared
from shapely.geometry import LineString, MultiLineString, Point, Polygon

from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms as FM
from deck.motifs import geometric as MG
from inkkit import geom as G

AX = float(T.CX)                 # the figure axis, x = 375
BIG = 5000.0
HAIR_W, FINE, MEDIUM, RULE, CONTOUR = T.HAIRLINE, T.FINE, T.MEDIUM, T.RULE, T.CONTOUR
INK, RED, JADE, GOLD, PAPER = T.INK, T.RED, T.JADE, T.FOIL, T.PAPER
PITCH = T.HATCH_PITCH            # 7.0: hatch and current-line pitch
TD = T.TERMINAL_D                # 6.3: free-end terminal
GAP = 4.2                        # §I.12 parallel strokes / §B.2 interlace gap
GAP_MARK = 3.0                   # §I.12 separate marks
HALO = 4.3                       # paper channel round hands and attributes crossing a pattern
EDGE_MED = MEDIUM / 2 + GAP + FINE / 2 + 0.2      # 7.0: first FINE line inside a MEDIUM edge
EDGE_CON = CONTOUR / 2 + GAP + FINE / 2 + 0.05    # 8.4: first FINE line inside a CONTOUR edge


def _f(v):
    return f"{float(v):.3f}".rstrip("0").rstrip(".")


# =============================================================================
# 1  compass geometry
# =============================================================================
def P(x, y=None):
    """A point as a float array: P(x, y) or P((x, y))."""
    if y is None:
        x, y = x
    return np.array([float(x), float(y)])


def polar(c, r, deg):
    a = math.radians(deg)
    return np.array([c[0] + r * math.cos(a), c[1] + r * math.sin(a)])


def ang(c, p):
    """Screen angle (degrees) of p seen from c."""
    return math.degrees(math.atan2(p[1] - c[1], p[0] - c[0]))


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


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
    """Unit normal to the screen-left of travel p0 → p1 (y down)."""
    d = np.asarray(p1, float) - np.asarray(p0, float)
    return np.array([d[1], -d[0]]) / float(np.hypot(*d))


def sag_centre(p0, p1, sag):
    """Centre and radius of the arc p0 → p1 bulging ``sag`` px to the
    screen-left of the chord (negative = right)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    s = abs(sag)
    Rr = ((L / 2) ** 2 + s * s) / (2 * s)
    n = left_normal(p0, p1) * (1 if sag > 0 else -1)
    return (p0 + p1) / 2 + n * (s - Rr), Rr


def arc_sag(p0, p1, sag, move=True):
    """Exact circular arc p0 → p1 bulging ``sag`` px to the screen-left of the
    chord — a compass arc given by chord and sagitta (0 = straight)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    head = f"M{_f(p0[0])} {_f(p0[1])}" if move else ""
    if abs(sag) < 1e-9:
        return head + f"L{_f(p1[0])} {_f(p1[1])}"
    L = float(np.hypot(*(p1 - p0)))
    Rr = ((L / 2) ** 2 + sag * sag) / (2 * abs(sag))
    large = 1 if abs(sag) > L / 2 else 0
    sweep = 1 if sag > 0 else 0
    return head + f"A{_f(Rr)} {_f(Rr)} 0 {large} {sweep} {_f(p1[0])} {_f(p1[1])}"


def arc3(p0, pm, p1, move=True):
    """Exact arc from p0 through pm to p1."""
    c, r = circ3(p0, pm, p1)
    n = left_normal(p0, p1)
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    side = float(np.dot(np.asarray(pm, float) - p0, n))
    m = (p0 + p1) / 2
    dcm = float(np.dot(c - m, n))
    s = dcm + r if side > 0 else dcm - r
    return arc_sag(p0, p1, s, move=move)


def arc_c(c, r, a0, a1, move=True):
    """Arc of circle (c, r) from screen angle a0 to a1 (a1 > a0: clockwise)."""
    return C.arc_d(c[0], c[1], r, a0, a1, move=move)


def circle(c, r):
    return G.circle_d(c[0], c[1], r)


def line_circle(p, u, c, r):
    """Intersections of the line p + t·u with circle (c, r), t ascending."""
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


def unwrap(a0, a1, cw):
    """a1' ≡ a1 (mod 360) such that a0 → a1' runs clockwise (cw) or
    anticlockwise, by less than one turn."""
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


class Path:
    """Tiny exact path builder (lines and circular arcs):

        Path(p0).line(p1).sag(p2, 6).arc3(pm, p3).arc_to(c, r, p4).close().d
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
    """Tangent arc chain (Turtle). Steps: ('fd', L) | ('arc', r, sweep°).
    Returns (d, end point, end heading)."""
    t = C.Turtle(p0[0], p0[1], heading)
    for s in steps:
        if s[0] == "fd":
            t.fd(s[1])
        else:
            t.arc(s[1], s[2])
    return t.d(), t.pos, t.heading


def spline(points, h_start=None, h_end=None, headings=None, closed=False):
    """G1 chain of tangent circular arcs through ``points`` (deck.motifs.forms
    arc_spline): the kit's freehand-free way to draw an organic contour.
    Returns the path d (closed with Z when ``closed``)."""
    d, _, _ = FM.arc_spline(points, h_start, h_end, headings=headings)
    return d + ("Z" if closed else "")


def rrect(x0, y0, x1, y1, r):
    return G.rect_d(x0, y0, x1 - x0, y1 - y0, r)


def vesica(p0, p1, width):
    """The deck's leaf: two equal arcs from p0 to p1, ``width`` apart."""
    return C.vesica_d(p0, p1, width)


def egg(c, r, chin_dx=0.0, chin_r=None, chin_dy=None):
    """The face-kit head (§H.0) as a compass construction: a circle of radius
    r about c (its upper half is the skull), two side arcs tangent to it at
    the ends of the horizontal diameter, and a chin circle (radius
    ``chin_r``, default r(2 − √2)) tangent to both. With ``chin_dx`` = 0 this
    is exactly the Moss egg (side arcs radius 2r; 88 × 113.8 at r 44). A
    3/4 head swings the chin ``chin_dx`` toward the turn: the far side arc
    flattens and the near one rounds — the head turns, not just the
    features. Returns (d, info) with the key points."""
    cx, cy = c
    rs = r * (2 - math.sqrt(2)) if chin_r is None else chin_r
    yc = r if chin_dy is None else chin_dy
    Cc = P(cx + chin_dx, cy + yc)
    pts = {}
    for s in (-1, 1):
        A = s * r - chin_dx
        den = 2 * (A * s - rs)
        rho = (A * A + yc * yc - rs * rs) / den
        O = P(cx + s * (r - rho), cy)
        u = (Cc - O) / np.hypot(*(Cc - O))
        Tp = O + u * rho
        pts[s] = (P(cx + s * r, cy), O, rho, Tp)
    (Al, Ol, rl, Tl), (Ar, Or, rr, Tr) = pts[-1], pts[1]
    d = (f"M{_f(Ar[0])} {_f(Ar[1])}"
         f"A{_f(r)} {_f(r)} 0 0 0 {_f(Al[0])} {_f(Al[1])}"
         f"A{_f(rl)} {_f(rl)} 0 0 0 {_f(Tl[0])} {_f(Tl[1])}"
         f"A{_f(rs)} {_f(rs)} 0 0 0 {_f(Tr[0])} {_f(Tr[1])}"
         f"A{_f(rr)} {_f(rr)} 0 0 0 {_f(Ar[0])} {_f(Ar[1])}Z")
    info = {"top": cy - r, "chin": P(cx + chin_dx, cy + yc + rs), "A": Al, "B": Ar,
            "E": Tl, "F": Tr, "O_l": Ol, "O_r": Or, "rho_l": rl, "rho_r": rr, "chin_c": Cc, "chin_r": rs}
    return d, info


def moss_egg(c, r):
    """The Moss egg (88 × 113.8 at r 44)."""
    return egg(c, r)


# =============================================================================
# 2  regions and marks
# =============================================================================
def R(x):
    """Any closed d or shapely geometry → a valid shapely region."""
    if x is None:
        return Polygon()
    if isinstance(x, shapely.Geometry):
        return x if x.is_valid else shapely.make_valid(x)
    return C.region(x)


def D(g):
    """shapely → path d (d passes through)."""
    if isinstance(g, str):
        return g
    return G.from_shape(g)


def U(*xs):
    gs = [R(x) for x in xs if x is not None]
    return shapely.union_all(gs) if gs else Polygon()


def mirror(x, axis=AX):
    """Mirror a d, a Frag, a Part or a shapely region about x = axis."""
    if isinstance(x, Part):
        return x.mirrored(axis)
    if isinstance(x, C.Frag):
        return x.mirror_x(axis)
    if isinstance(x, shapely.Geometry):
        return shapely.affinity.scale(x, -1, 1, origin=(axis, 0))
    return G.mirror_x(x, axis)


def bi(x, axis=AX):
    """Bilateral: x plus its mirror image (Frag concatenation, region union)."""
    if isinstance(x, C.Frag):
        return x + x.mirror_x(axis)
    return U(x, mirror(x, axis))


def box(x0, y0, x1, y1):
    return shapely.box(x0, y0, x1, y1)


def halfplane(p0, p1, side=+1):
    """Big polygon on the screen-left (side +1) or right (−1) of p0 → p1."""
    p0, p1 = P(p0), P(p1)
    u = (p1 - p0) / np.hypot(*(p1 - p0))
    n = np.array([u[1], -u[0]]) * side
    return Polygon([p0 - u * BIG, p1 + u * BIG, p1 + u * BIG + n * BIG, p0 - u * BIG + n * BIG])


def line(d, w=MEDIUM, color=INK, style="ornament", terminals=None, role=""):
    """A stroke mark (legal widths only)."""
    return C.stroke(d, w, style=style, color=color, terminals=terminals, role=role)


def seg(p0, p1, w=MEDIUM, color=INK, style="ornament", role=""):
    return C.stroke(f"M{_f(p0[0])} {_f(p0[1])}L{_f(p1[0])} {_f(p1[1])}", w, style=style, color=color, role=role)


def fill(d, color, role=""):
    if isinstance(d, shapely.Geometry):
        d = D(d)
    return C.fill(d, color=color, role=role) if d else C.Frag()


def dot(p, d=TD, color=INK, role="dot"):
    return C.dot(p[0], p[1], d, color=color, role=role)


def outline(d, w=MEDIUM, color=INK, role="outline"):
    """A closed shape's own contour (interior weight by default)."""
    if isinstance(d, shapely.Geometry):
        d = D(d)
    return C.stroke(d, w, style="ornament", color=color, role=role) if d else C.Frag()


def hatch_in(region, angle=C.DIAG, pitch=PITCH, origin=None, color=INK):
    """FINE butt-capped hatch clipped to a region (§B.2). Robust to degenerate
    cells (a corner touching a course line)."""
    g = R(region)
    polys = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and p.area > 1.0]
    f = C.Frag()
    for pg in polys:
        try:
            f += C.hatch(pg, angle, pitch, origin=origin, color=color)
        except ValueError:
            continue
    return f


def _lines_of(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "LinearRing":
        return [LineString(g.coords)]
    out = []
    for p in getattr(g, "geoms", []):
        out += _lines_of(p)
    return out


def _polys_of(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    out = []
    for p in getattr(g, "geoms", []):
        out += _polys_of(p)
    return out


def _stroke_lines(d, tol=0.05):
    return [LineString(np.vstack([p, p[:1]]) if c else p) for p, c in G.flatten(d, tol) if len(p) >= 2]


def clip_in(f: C.Frag, zone, tol=0.05) -> C.Frag:
    """Keep only the parts of ``f`` inside ``zone`` (stroke centrelines are
    clipped; fills are intersected)."""
    out = []
    zone = R(zone)
    zp = shapely.prepared.prep(zone)
    for m in f.marks:
        if not m.d:
            continue
        x0, y0, x1, y1 = G.bbox(m.d) if hasattr(G, "bbox") else R(G.from_skia(m.skia())).bounds
        if zp.contains(shapely.box(x0 - m.w, y0 - m.w, x1 + m.w, y1 + m.w)):
            out.append(m)                   # wholly inside: keep its exact arcs
            continue
        if m.kind == "fill":
            d = G.from_shape(G.to_shape(m.d, tol=tol).intersection(zone))
            if d:
                out.append(replace(m, d=d))
            continue
        lines = _stroke_lines(m.d, tol)
        if not lines:
            continue
        res = shapely.intersection(MultiLineString(lines), zone)
        try:
            res = shapely.line_merge(res)
        except shapely.errors.GEOSException:
            pass
        pieces = [np.asarray(ln.coords) for ln in _lines_of(res) if ln.length > 0.3]
        if pieces:
            out.append(replace(m, d="".join(C.polyline_d(p) for p in pieces)))
    return C.Frag(out, f.meta)


def atomic(f: C.Frag, key) -> C.Frag:
    """Tag every mark of ``f`` as one indivisible motif (a void with its
    crescent and cavern, a bubble, a rowel): when something in front covers
    any of it, ``clip_out`` drops the whole motif instead of leaving a
    clipped arc or a sliver (a stray '⌣' under a clasp is a defect)."""
    return C.Frag([replace(m, role=f"{m.role.split('@')[0]}@{key}") for m in f.marks], f.meta)


STROKE_EPS = -0.5    # strokes behind stop 0.5 px INSIDE the front object (under its contour)
TRAP = 1.6           # fills behind run this far under the front object's contour


def clip_out(f: C.Frag, zone, tol=0.05, eps=STROKE_EPS, trap=TRAP, extra=None, halo=None) -> C.Frag:
    """Remove the parts of ``f`` inside ``zone`` (a shapely region): what an
    object in front hides.

    * stroke centrelines are cut |eps| px inside the zone boundary, so a line
      that meets the front object ends under its contour — the pieces join,
      no hairline gap;
    * fills are differenced with the zone shrunk by ``trap`` px, so the back
      plate runs under the front contour (a trap), and strips thinner than
      3 px left beside the cut are dropped;
    * ``halo`` (a region): everything, lines and fills, also stops clear of
      it — a geometric paper channel."""
    out = []
    # atomic motifs (role 'x@key'): all or nothing
    groups = {}
    for m in f.marks:
        if "@" in m.role and m.d:
            groups.setdefault(m.role.split("@", 1)[1], []).append(m)
    if groups:
        touch = zone.buffer(GAP_MARK + 0.3, quad_segs=6)
        if halo is not None and not halo.is_empty:
            touch = touch.union(halo.buffer(GAP_MARK, quad_segs=6))
        tp = shapely.prepared.prep(touch)
        drop = set()
        for key, ms in groups.items():
            g = shapely.union_all([R(G.from_skia(m.skia())) for m in ms])
            if tp.intersects(g):
                drop.add(key)
        if drop:
            f = C.Frag([m for m in f.marks if not ("@" in m.role and m.role.split("@", 1)[1] in drop)], f.meta)
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
            if not s.is_empty:
                opened = s.buffer(-1.5, quad_segs=6).buffer(1.5, quad_segs=6)
                thin = s.difference(opened)
                if not thin.is_empty:
                    s = s.difference(thin.intersection(z_fill.buffer(3.5, quad_segs=6)))
            d = G.from_shape(s)
            if d:
                out.append(replace(m, d=d))
            continue
        lines = _stroke_lines(m.d, tol)
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
        pieces = [np.asarray(ln.coords) for ln in _lines_of(res) if ln.length > 0.3]
        if pieces:
            out.append(replace(m, d="".join(C.polyline_d(p) for p in pieces)))
    return C.Frag(out, f.meta)


# =============================================================================
# 3  Part and Scene
# =============================================================================
@dataclass
class Part:
    """One drawable object: its opaque ``shape`` (shapely), its colour
    ``fills`` and its ``lines`` (Frags), and construction facts in ``meta``
    (anchor points for the next builder)."""
    shape: object
    fills: C.Frag = field(default_factory=C.Frag)
    lines: C.Frag = field(default_factory=C.Frag)
    meta: dict = field(default_factory=dict)

    @property
    def frag(self):
        return self.fills + self.lines

    def mirrored(self, axis=AX):
        meta = {}
        for k, v in self.meta.items():
            if isinstance(v, np.ndarray) and v.shape == (2,):
                meta[k] = P(2 * axis - v[0], v[1])
            else:
                meta[k] = v
        return Part(mirror(self.shape, axis), self.fills.mirror_x(axis), self.lines.mirror_x(axis), meta)

    def __add__(self, other):
        return Part(U(self.shape, other.shape), self.fills + other.fills, self.lines + other.lines,
                    {**self.meta, **other.meta})


@dataclass
class Item:
    name: str
    frag: C.Frag
    occ: object = None            # opaque region this item hides
    sil: bool = True              # part of the figure silhouette (stroked once at CONTOUR)?
    halo: float = 0.0             # >0: things behind stop this clear of the item's outline
    halo_skip: tuple = ()         # items behind the halo leaves alone (a hand's own cuff)
    halo_only: tuple | None = None   # if set, the halo applies ONLY to these items behind
    halo_zone: object = None      # hand hook: an explicit paper-channel region (instead of occ + halo)


@dataclass
class Scene:
    """Painter's-order stack, back to front.

    ``add(name, frag, occ)`` puts an object in front of everything added so
    far; ``compose()`` returns one Frag in which every object's marks are
    clipped to what is visible, plus the figure silhouette (the union of the
    ``sil`` items' regions) stroked once at CONTOUR — so every interior edge
    stays MEDIUM automatically (§B.2: 2 : 1) — and then ``heal``s the §I.12
    near-misses clipping leaves. ``heal_log`` lists every change."""
    items: list = field(default_factory=list)
    clip_tol: float = 0.05
    heal_log: list = field(default_factory=list)
    rank: str | None = None       # 'K' | 'Q' | 'J': clip to the system's court clip before healing
    cut_y: float = 511.0          # the module's CUT_Y

    def add(self, name, frag, occ=None, sil=True, halo=0.0, halo_skip=(), halo_only=None, halo_zone=None):
        """Add an object in front. ``occ``: its opaque region (shapely or d).
        ``halo`` > 0 surrounds it with a geometric paper channel: fills and
        lines behind stop ``halo`` px clear of its MEDIUM outline (the
        Drifters treatment of hands and attributes crossing a pattern).
        ``halo_skip`` exempts named items behind (a hand's own cuff);
        ``halo_only`` restricts the halo to the named items behind (e.g. only
        the patterned mantle). Without a halo, lines behind run under its
        contour and fills are trapped under it. ``halo_zone`` (a region; kit
        hands use it for the paper between a heel and a haloed shaft) is
        the channel itself, used instead of ``occ`` grown by ``halo``."""
        if isinstance(frag, Part):
            occ = frag.shape if occ is None else occ
            frag = frag.frag
        occ = R(occ) if occ is not None else None
        frag = flatten_fills(frag if frag is not None else C.Frag())
        self.items.append(Item(name, frag, occ, sil, halo, tuple(halo_skip),
                               None if halo_only is None else tuple(halo_only),
                               None if halo_zone is None else R(halo_zone)))
        return self

    def part(self, name, part: "Part", **kw):
        """``add`` for a Part (its frag and shape)."""
        return self.add(name, part.frag, part.shape, **kw)

    def region(self, names=None, sil_only=False):
        gs = [it.occ for it in self.items if it.occ is not None and (names is None or it.name in names)
              and (not sil_only or it.sil)]
        return shapely.union_all(gs) if gs else Polygon()

    def silhouette(self):
        return self.region(sil_only=True)

    def compose(self, contour=CONTOUR, extra_front=None, heal_gaps=True):
        out = []
        acc = Polygon()
        halos = []                 # (name, skip, only, channel region) of items in front
        for it in reversed(self.items):
            f = it.frag
            hz = [h for (nm, skip, only, h) in halos
                  if it.name not in skip and (only is None or it.name in only)]
            acc_halo = shapely.union_all(hz) if hz else Polygon()
            if f and not (acc.is_empty and acc_halo.is_empty):
                f = clip_out(f, acc, self.clip_tol, halo=acc_halo)
            out.append(f)
            if it.occ is not None and not it.occ.is_empty:
                # 0.3 px closes hairline slits between two front objects that
                # share an edge, so the trap never opens a strip between them
                acc = acc.union(it.occ.buffer(0.3, quad_segs=6))
                if it.halo:
                    halos.append((it.name, it.halo_skip, it.halo_only,
                                  it.halo_zone if it.halo_zone is not None
                                  else it.occ.buffer(it.halo + MEDIUM / 2, quad_segs=12)))
        out.reverse()
        res = C.frag(*out)
        if contour:
            res += silhouette_line(self.silhouette(), contour)
        if extra_front:
            res += extra_front
        if self.rank is not None:
            # the system clips every layer to the art window above CUT_Y minus
            # the medallion disc; clip first so heal sees the printed pieces
            # (a fill that is thin only after that clip is otherwise missed)
            from deck import frames as _F
            res = clip_in(res, R(_F.court_clip_d(self.rank, self.cut_y)), self.clip_tol)
        if heal_gaps:
            self.heal_log = []
            if self.rank is not None:
                # the band's top rule is drawn by the system: heal against it
                # too (a line ending 1–2 px above y 511 is a §I.12 failure)
                band = C.stroke(f"M100 {_f(self.cut_y)}L650 {_f(self.cut_y)}", FINE, style="rule", role="_band")
                res = heal(res + band, log=self.heal_log, keep_roles=("contour", "_band"))
                res = res.select(lambda m: m.role != "_band")
            else:
                res = heal(res, log=self.heal_log)
        return res

    def layers(self, **kw):
        """compose() → {layer: [svg fragment]}: an art module's build() value."""
        return layers(self.compose(**kw))


LAYER_RANK = {L: i for i, L in enumerate(T.LAYERS)}


def flatten_fills(f: C.Frag) -> C.Frag:
    """Painter's order among ONE object's fills. The plates print paper <
    jade < red < gold < ink whatever the drawing order, so a fill meant to lie
    in front of a fill on a HIGHER plate (a red jewel on a gold band) is cut
    out of it geometrically. Later fills win."""
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


def silhouette_line(sil, w=CONTOUR):
    """Stroke every ring of the silhouette region at CONTOUR (round joins)."""
    if sil.is_empty:
        return C.Frag()
    return C.stroke(G.from_shape(sil.simplify(0.02)), w, style="ornament", role="contour")


# ---- heal ------------------------------------------------------------------
GAP_FILL = 2.5
PAR_RUN = 12.0


def _run_len(a, b):
    """QA 12's 'alongside' measure: longer side of the minimum rotated
    rectangle of the part of ``a`` within GAP + 0.1 of ``b``."""
    near = a.intersection(b.buffer(GAP + 0.1, quad_segs=4))
    if near.is_empty:
        return 0.0
    rr = near.minimum_rotated_rectangle
    if rr.geom_type != "Polygon":
        return 0.0
    xy = np.asarray(rr.exterior.coords)
    return float(max(np.linalg.norm(xy[1] - xy[0]), np.linalg.norm(xy[2] - xy[1])))


def _groups(marks):
    """Mark indices grouped the way Frag.svg emits SVG elements: consecutive
    strokes of one style share a <path>; each fill is its own element."""
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


def heal(f: C.Frag, *, max_iter: int = 6, stub: float = 7.0, sliver: float = 12.0, keep_roles=("contour",),
         log=None) -> C.Frag:
    """Make every pair of drawn pieces either touch or keep the §I.12 paper
    between them, measured exactly as QA check 12 does (SVG elements outlined
    with their true widths, split into connected pieces): ≥ 3.0 between
    separate pieces, ≥ 4.2 between strokes running alongside for ≥ 12 px,
    ≥ 2.5 between same-layer fills. Only the collateral damage of clipping is
    repaired, locally:

    * fill pieces thinner than HAIRLINE are dropped;
    * knockout holes closer than 3 px to their solid's edge are filled;
    * a stroke piece shorter than ``stub`` (a fill smaller than ``sliver``
      px²) that nearly touches another piece is deleted;
    * a longer stroke is cut back only where it nears the other piece.

    Marks whose role is in ``keep_roles`` (the silhouette CONTOUR) are never
    changed. Every change is appended to ``log`` (a list of dicts: what,
    where, why) — read it: surgery the drawing needs is a design problem."""
    marks = list(f.marks)
    lg = log if log is not None else []

    def note(kind, m, where, why, near=None):
        e = {"action": kind, "role": (m.role or m.kind).split("@")[0], "layer": m.layer,
             "at": [round(float(where[0]), 1), round(float(where[1]), 1)], "why": why}
        if near:
            e["near"] = near
        lg.append(e)

    for i, m in enumerate(marks):
        if m.kind != "fill" or m.role in keep_roles or not m.d:
            continue
        s = G.to_shape(m.d, tol=0.05)
        parts = [p for p in getattr(s, "geoms", [s]) if p.geom_type == "Polygon"]
        bad = [p for p in parts if p.buffer(-0.8).is_empty]
        if bad:
            for p in bad:
                c = p.representative_point()
                note("drop", m, (c.x, c.y), "fill piece thinner than HAIRLINE")
            keep = [p for p in parts if not p.buffer(-0.8).is_empty]
            marks[i] = replace(m, d=G.from_shape(shapely.union_all(keep)) if keep else "")
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
                if min(h.distance(o) for o in others) < GAP_MARK + 0.1:
                    changed = True
                    c = h.centroid
                    note("fill-hole", m, (c.x, c.y), "knockout hole < 3 px from an edge")
                    continue
                keep.append(h)
            polys.append(shapely.Polygon(pg.exterior.coords, [x.coords for x in keep]))
        if changed:
            marks[i] = replace(m, d=G.from_shape(shapely.union_all(polys)))
    for it_ in range(max_iter + 1):
        outl = {i: R(G.from_skia(m.skia())) for i, m in enumerate(marks) if m.d}
        pieces = []
        for grp in _groups(marks):
            u = shapely.union_all([outl[i] for i in grp if i in outl])
            for pg in _polys_of(u):
                if pg.area <= 0.05:
                    continue
                mem = [i for i in grp if outl[i].intersects(pg)]
                m0 = marks[grp[0]]
                prot = any(marks[i].role in keep_roles for i in mem)
                pieces.append((pg, mem, m0.kind, m0.layer, prot))
        if not pieces:
            break
        geoms = [p[0] for p in pieces]
        tree = shapely.STRtree(geoms)
        pairs = tree.query(geoms, predicate="dwithin", distance=GAP)
        todo = []
        for a, b in zip(*pairs):
            if a >= b:
                continue
            pa, pb = pieces[a], pieces[b]
            d = pa[0].distance(pb[0])
            if d < 0.08:
                continue
            both_fill = pa[2] == "fill" and pb[2] == "fill" and pa[3] == pb[3]
            need = GAP_FILL if both_fill else GAP_MARK
            if pa[2] == "stroke" and pb[2] == "stroke" and d >= GAP_MARK - 0.08:
                if _run_len(pa[0], pb[0]) >= PAR_RUN - 0.5:
                    need = GAP
                else:
                    continue
            if d >= need - 0.08:
                continue
            cand = [(p[0].area, p, q) for p, q in ((pa, pb), (pb, pa)) if not p[4]]
            if not cand:
                continue
            cand.sort(key=lambda t: t[0])
            _, victim, other = cand[0]
            todo.append((victim, other[0], need, d, sorted({(marks[i].role or marks[i].kind).split("@")[0]
                                                            for i in other[1]})))
        if not todo:
            break
        if it_ == max_iter:                 # still failing: say so (QA 12 will too)
            for (pg, mem, kind, layer, _), other, need, dd, near in todo:
                w_ = pg.representative_point()
                note("UNRESOLVED", marks[mem[0]], (w_.x, w_.y), f"{dd:.2f} px from a neighbour (needs {need})", near)
            break
        for (pg, mem, kind, layer, _), other, need, dd, near in todo:
            where = pg.representative_point()
            for i in mem:
                m = marks[i]
                if not m.d:
                    continue
                if m.kind == "fill":
                    s = G.to_shape(m.d, tol=0.05)
                    if pg.area < sliver:
                        s = s.difference(pg.buffer(0.2))
                        note("delete", m, (where.x, where.y), f"sliver {pg.area:.1f} px² {dd:.2f} px from a neighbour", near)
                    else:
                        s = s.difference(other.buffer(need + 0.1).intersection(pg.buffer(0.5)))
                        note("trim", m, (where.x, where.y), f"fill {dd:.2f} px from a neighbour (needs {need})", near)
                    marks[i] = replace(m, d=G.from_shape(s))
                    continue
                ml = MultiLineString(_stroke_lines(m.d, 0.05))
                local = shapely.intersection(ml, pg.buffer(0.01))
                if local.length < stub:
                    ml = shapely.difference(ml, pg.buffer(0.3))
                    note("delete", m, (where.x, where.y), f"stub {local.length:.1f} px, {dd:.2f} px from a neighbour", near)
                else:
                    ml = shapely.difference(ml, other.buffer(need + m.w / 2 + 0.1).intersection(pg.buffer(0.5)))
                    note("trim", m, (where.x, where.y), f"stroke {dd:.2f} px from a neighbour (needs {need})", near)
                try:
                    ml = shapely.line_merge(ml)
                except Exception:
                    pass
                # a trimmed stroke never leaves a crumb that reads as a stray dot
                pcs = [np.asarray(ln.coords) for ln in _lines_of(ml) if ln.length > max(2.5, 1.5 * m.w)]
                marks[i] = replace(m, d="".join(C.polyline_d(p) for p in pcs))
    return C.Frag([m for m in marks if m.d], f.meta)


# =============================================================================
# 4  current lines (§G.24)
# =============================================================================
def _curl(pts, side, r, deg):
    """Continue the polyline's free end with a tangent arc of radius r turning
    ``deg`` toward ``side`` (+1 = screen-left of travel). → points."""
    p = pts[-1]
    t = pts[-1] - pts[-2]
    t = t / np.hypot(*t)
    h = math.degrees(math.atan2(t[1], t[0]))
    tu = C.Turtle(p[0], p[1], h)
    tu.arc(r, -deg * side)
    arc = np.asarray(tu.pts(0.5)[0])
    return np.vstack([pts, arc[1:]])


def current_lines(guide, n, region=None, *, side=+1, pitch=PITCH, first=None, edge=MEDIUM,
                  stagger=8.0, end="curl", curl_r=4.2, curl_deg=75.0, root="edge",
                  min_len=10.0, placed=None, w=FINE, color=INK, terminal=TD):
    """§G.24 current lines: ``n`` (3–5) parallel offsets of ONE guide at a
    7 px pitch, clipped to ``region``, each ending in a Ø6.3 terminal.

    guide   d-string or points, drawn from the ROOT (hairline, chin) to the
            free end; offsets go to ``side`` (+1 = screen-left of travel).
    first   offset of line 0 from the guide (default: the guide is the
            region's edge, so first = 7.0 inside a MEDIUM edge, 8.4 inside a
            CONTOUR edge — pass ``edge``).
    stagger line k is shortened k·stagger px at its free end (layered lock
            ends). Terminals on neighbouring lines stay ≥ 3 px clear.
    end     'curl' — the free end turns ``curl_deg`` toward ``side`` on radius
            ``curl_r`` before its terminal (the rolled lock end; it also keeps
            the terminal 3 px clear of the neighbour that runs on, which a
            straight end at a 7.0 pitch cannot: 7 − 3.15 − 1.05 = 2.8);
            'dot' — straight end + terminal; 'edge' — run to the region edge
            and butt into its outline (no terminal).
    Every end is checked against the region edge and everything already
    placed (``placed``: shapely geometry of other marks, and each line as it
    is drawn) and stepped back until §I.12 holds; a line that cannot fit is
    dropped. Returns a Frag (meta['lines'] = the centrelines)."""
    if isinstance(guide, str):
        gp = C.sample_d(guide, 0.25)[0][0]
    else:
        gp = np.asarray(guide, float)
    cv = G.Curve(gp)
    reg = R(region) if region is not None else None
    if first is None:
        first = (edge / 2 + GAP + w / 2 + 0.2) if reg is not None else 0.0
    tr = terminal / 2
    safe = reg.buffer(-(tr + GAP_MARK + edge / 2 + 0.1), quad_segs=12) if reg is not None else None
    body_zone = reg.buffer(-(w / 2 + GAP_MARK + edge / 2), quad_segs=12) if reg is not None else None
    acc = placed if placed is not None else Polygon()
    f = C.Frag()
    out_lines = []
    for k in range(n):
        off = cv.offset(side * (first + k * pitch), spacing=0.5) if (first + k * pitch) else cv.resample(0.5)
        ln = LineString(off)
        if not ln.is_simple:
            uu = shapely.ops.unary_union(ln)
            parts = list(uu.geoms) if hasattr(uu, "geoms") else [ln]
            ln = max(parts, key=lambda g: g.length)
        pieces = [ln] if reg is None else [g for g in _lines_of(ln.intersection(reg)) if g.length >= min_len]
        if not pieces:
            continue
        # the piece nearest the root
        s0 = [ln.project(Point(g.coords[0])) for g in pieces]
        piece = pieces[int(np.argmin(s0))]
        q = np.asarray(piece.coords)
        if ln.project(Point(q[0])) > ln.project(Point(q[-1])):
            q = q[::-1]
        pc = G.Curve(q)
        Lp = pc.length
        if end == "edge":
            f += C.stroke(q, w, color=color, role="current")
            out_lines.append(q)
            acc = acc.union(LineString(q).buffer(w / 2))
            continue
        # free end: the last point before the line leaves the terminal-safe zone
        s_end = Lp - k * stagger
        if safe is not None:
            ss = np.arange(0.0, Lp, 0.5)
            ins = np.array([safe.contains(Point(*pc.at_s(s))) for s in ss])
            if ins.any():
                i0 = int(np.argmax(ins))                       # first safe point
                after = np.where(~ins[i0:])[0]
                s_exit = ss[i0 + after[0] - 1] if len(after) else Lp
                s_end = min(s_end, s_exit)
            else:
                continue
        done = False
        s = s_end
        while s > min_len:
            body = pc.sub(0, s / Lp).pts
            tail = _curl(body, side, curl_r, curl_deg) if end == "curl" else body
            tp = tail[-1]
            tail_start = max(0, len(body) - 2)
            geom_body = LineString(tail).buffer(w / 2, quad_segs=6)
            tgeom = Point(*tp).buffer(tr, quad_segs=12)
            ok = True
            if safe is not None and not safe.contains(Point(*tp)):
                ok = False
            if ok and body_zone is not None and end == "curl":
                if not body_zone.contains(LineString(tail[tail_start:])):
                    ok = False
            if ok and not acc.is_empty:
                if acc.distance(tgeom) < GAP_MARK + 0.05 or acc.distance(
                        LineString(tail[tail_start:]).buffer(w / 2, quad_segs=6)) < GAP_MARK + 0.05:
                    ok = False
            if ok:
                f += C.stroke(tail, w, color=color, role="current")
                f += C.dot(tp[0], tp[1], terminal, color=color, role="terminal")
                out_lines.append(tail)
                acc = acc.union(geom_body).union(tgeom)
                done = True
                break
            s -= 1.0
        if not done:
            continue
    f.meta["lines"] = out_lines
    return f


def lock_fan(c, r_out, r_in, a0, a1, cap=True):
    """Annulus sector a0 → a1 (screen degrees) between r_in and r_out; with
    ``cap`` the a1 end is a semicircle across the ribbons (a rolled lock
    end). The compass shape of a hair fall. → shapely region."""
    c = P(c)
    cw = a1 > a0
    p_o0, p_o1 = polar(c, r_out, a0), polar(c, r_out, a1)
    p_i0, p_i1 = polar(c, r_in, a0), polar(c, r_in, a1)
    p = Path(p_o0).arc_to(c, r_out, p_o1, cw=cw)
    if cap:
        h = (r_out - r_in) / 2
        p.sag(p_i1, h if cw else -h)
    else:
        p.line(p_i1)
    p.arc_to(c, r_in, p_i0, cw=not cw).close()
    return R(p.d)


# =============================================================================
# 5  faces (§H.0)
# =============================================================================
@dataclass
class FaceSpec:
    """Face-kit proportions (card px), relative to the egg centre (cx, cy)
    and the eye line. Defaults are the K♠ king: head 88 × 113.8, eyes 24 × 10
    at y cy + 6, level heavy lids. ``face()`` applies the sex / age / lids
    presets on top of a copy of this."""
    r: float = 44.0                 # egg circle radius (88 × 113.8)
    eye_dy: float = 6.0             # eye line below the egg centre (its widest line)
    eye_dx: float = 22.0            # eye centre from the feature axis
    eye_w: float = 24.0
    lid_sag: float = 4.3            # upper lid (RULE) sagitta — flatter than the lower: a heavy lid
    low_sag: float = 5.8            # lower lid (FINE) sagitta; lid_sag + low_sag = 10.1 (the 24 × 10 vesica)
    pupil_d: float = 6.0
    pupil_tuck: float = 0.0         # pupil top below the lid centreline (0: it hangs from the lid)
    pupil_dx: float = 0.0           # gaze: pupils shifted toward +x (px)
    flick: float = 0.0              # RULE lid runs this far past the outer corner (0 = none)
    brow_dy: float = -13.0          # brow inner end, relative to the eye line
    brow_in: float = 7.0
    brow_out: float = 35.0
    brow_drop: float = 1.5          # outer end lower than the inner
    brow_sag: float = 3.2
    nose: str = "wing"              # frontal nose: 'wing' (ridge + alar loop) | 'hook'
    nose_top_dy: float = 3.0         # ridges start below the eye line: ≥ 3 px from the inner eye corners
    nose_bot_dy: float = 20.0       # nose base below the eye line
    nose_dx_top: float = 3.7        # ridge offset from the axis at the bridge (≥ 4.2 px between the ridges)
    nose_dx: float = 6.0            # ... and above the wing
    wing_r: float = 3.6
    mouth: bool = True
    mouth_dy: float = 42.5          # mouth corners below the eye line (≥ 4.2 px under a moustache)
    mouth_hw: float = 9.0
    bow_rise: float = 1.6           # centre cusp higher than the corners
    bow_sag: float = -1.2
    lip_dy: float = 50.0            # lower-lip tick (≥ 4.2 px below the bow)
    lip_hw: float = 5.5
    lip_sag: float = -1.8
    ears: bool = False
    turn_shift: float = 0.12        # 3/4: feature axis shift, fraction of the head width
    far_eye: float = 0.70           # 3/4: far eye width fraction
    chin_swing: float = 0.55        # 3/4: chin shift as a fraction of the feature shift


SEX_PRESETS = {
    "m": {},
    "f": dict(r=42.0, eye_dx=20.5, brow_dy=-14.5, brow_sag=4.0, brow_out=33.0, brow_drop=2.5, nose="hook",
              nose_bot_dy=17.0, nose_dx=5.0, nose_dx_top=3.0, mouth_dy=36.0, mouth_hw=8.5, bow_rise=2.0,
              lip_dy=44.0, lip_hw=5.0, lip_sag=-2.2),
}
AGE_PRESETS = {
    "young": dict(nose_bot_dy=-2.5, brow_dy=-1.0, mouth_dy=-2.0, lip_dy=-2.0),     # deltas
    "adult": {},
    "elder": dict(brow_sag=-0.8, brow_dy=1.0, nose_bot_dy=1.0),
}
LID_PRESETS = {
    "heavy": dict(lid_sag=4.3, low_sag=5.8, pupil_tuck=0.0),
    "level": dict(lid_sag=5.0, low_sag=5.0, pupil_tuck=-1.0),
    "half": dict(lid_sag=2.6, low_sag=6.0, pupil_tuck=1.2),
    "lowered": dict(lid_sag=3.2, low_sag=6.8, pupil_tuck=2.2),
    "raised": dict(lid_sag=5.6, low_sag=4.4, pupil_tuck=-1.8),
    "closed": dict(lid_sag=-3.0, low_sag=0.0),
}


@dataclass
class Face:
    head: str            # head silhouette d
    skin: object         # its region (paper)
    lines: C.Frag        # feature lines (ink)
    anchors: dict        # named points for hair, beard, crown and hands
    strokes: int         # feature stroke count (§H.0: ≤ 14)

    @property
    def part(self):
        return Part(self.skin, C.Frag(), self.lines, self.anchors)


def _eye(ex, ey, s, w, side, lids="heavy", vestigial=False, pupil=True, pdx=None):
    """One eye centred (ex, ey), width w (side −1: outer corner on the left):
    the RULE upper lid and FINE lower lid are the two arcs of the 24 × 10
    vesica; the Ø6 pupil hangs from the lid (``_pupil``)."""
    f = C.Frag()
    k = w / s.eye_w
    outer = P(ex + side * w / 2, ey)
    inner = P(ex - side * w / 2, ey)
    a, b = (outer, inner) if side < 0 else (inner, outer)       # left → right: screen-left = up
    if lids == "closed":
        f += line(arc_sag(a, b, s.lid_sag * k), RULE, role="lid")
    else:
        up = arc_sag(a, b, s.lid_sag * k)
        if s.flick:
            o2 = outer + P(side * s.flick, 1.0)
            up = up + f"M{_f(outer[0])} {_f(outer[1])}L{_f(o2[0])} {_f(o2[1])}"
        f += line(up, RULE, role="lid")
        f += line(arc_sag(a, b, -s.low_sag * k), FINE, role="lid-lo")
    if pupil:
        f += _pupil(ex, ey, s, w, lids, vestigial, pdx)
    return f


def _pupil(ex, ey, s, w, lids="heavy", vestigial=False, pdx=None):
    """The Ø6 pupil: its top on the RULE lid's centreline (+ ``pupil_tuck``),
    so it hangs from the lid — the level, heavy-lidded gaze. Its bottom
    either touches the lower lid or keeps 3 px from it (§I.12). Closed lids:
    the Ø3 vestigial dot below the lid (Q♠)."""
    k = w / s.eye_w
    if lids == "closed":
        if not vestigial:
            return C.Frag()
        return dot((ex, ey + abs(s.lid_sag) * k + RULE / 2 + GAP_MARK + 1.5 + 0.8), 3.0, role="pupil")
    px = ex + (s.pupil_dx * k if pdx is None else pdx)
    t = ((px - ex) / (w / 2)) ** 2
    lid_y = ey - s.lid_sag * k * (1 - t)
    low_in = ey + s.low_sag * k * (1 - t) - FINE / 2
    rp = s.pupil_d / 2
    py = lid_y + rp + s.pupil_tuck
    gap = low_in - (py + rp)
    if 0.0 < gap < GAP_MARK:
        py = low_in - rp - GAP_MARK if gap > GAP_MARK / 2 else low_in - rp + 0.4
    return dot((px, py), s.pupil_d, role="pupil")


def _brow(ax, s, side, eye_y, scale=1.0):
    bi_ = P(ax + side * s.brow_in * scale, eye_y + s.brow_dy)
    bo = P(ax + side * (s.brow_in + (s.brow_out - s.brow_in) * scale) * (1 if scale == 1 else 1),
           eye_y + s.brow_dy + s.brow_drop)
    if scale != 1:
        bo = P(ax + side * (s.brow_in * scale + (s.brow_out - s.brow_in) * scale), eye_y + s.brow_dy + s.brow_drop)
    a, b = (bo, bi_) if side < 0 else (bi_, bo)
    return line(arc_sag(a, b, s.brow_sag), MEDIUM, role="brow")


def _nose_frontal(ax, s, side, eye_y):
    """Frontal nose, one side: a straight MEDIUM ridge converging toward the
    brow, then the alar wing — a tangent arc out and round under the nostril
    back toward the axis ('wing'), or a small inward hook ('hook')."""
    p0 = P(ax + side * s.nose_dx_top, eye_y + s.nose_top_dy)
    base = eye_y + s.nose_bot_dy
    if s.nose == "wing":
        p1 = P(ax + side * s.nose_dx, base - 2 * s.wing_r - 1.5)
        h = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        t = C.Turtle(p0[0], p0[1], h)
        t.line_to(p1[0], p1[1])
        # out (away from the axis) ...
        t.arc(s.wing_r * 1.2, 55.0 * (1 if side < 0 else -1))
        # ... round the bottom of the wing and back in, level
        cur = t.heading
        target = 0.0 if side < 0 else 180.0
        turn = ((target - cur + 540) % 360) - 180
        t.arc(s.wing_r, turn)
        t.fd(1.2)
        return line(t.d(), MEDIUM, role="nose")
    p1 = P(ax + side * s.nose_dx, base - s.wing_r)
    h = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    t = C.Turtle(p0[0], p0[1], h)
    t.line_to(p1[0], p1[1])
    t.arc(s.wing_r, -100.0 * (1 if side < 0 else -1))
    return line(t.d(), MEDIUM, role="nose")


def _mouth(fx, s, eye_y, hw_l, hw_r):
    f = C.Frag()
    y = eye_y + s.mouth_dy
    if s.mouth:
        cusp = P(fx, y - s.bow_rise)
        lc, rc = P(fx - hw_l, y), P(fx + hw_r, y)
        d = arc_sag(lc, cusp, s.bow_sag) + arc_sag(cusp, rc, s.bow_sag, move=False)
        f += line(d, MEDIUM, role="mouth")
    ly = eye_y + s.lip_dy
    hl = s.lip_hw * (hw_l / s.mouth_hw)
    hr = s.lip_hw * (hw_r / s.mouth_hw)
    f += line(arc_sag(P(fx - hl, ly), P(fx + hr, ly), s.lip_sag), FINE, role="lip")
    return f


def face(center=(AX, 207.0), gaze="frontal", *, sex="m", age="adult", lids="heavy", spec=None,
         vestigial=False, **over) -> Face:
    """Draw a §H.0 face. ``center`` = the centre of the head egg's circle (its
    widest line); the eye line is ``eye_dy`` below it.

    gaze   'frontal' (one half drawn and mirrored — perfectly symmetric),
           '3/4-left' | '3/4-right' (turned toward the viewer's left/right:
           the chin swings, the far cheek flattens, features shift 12 % of
           the head width toward the turn, the far eye is 70 % wide with
           its outer corner JOINING the head contour and its pupil centred,
           the far brow ends on the contour, one nose ridge on the far side
           hooks back toward the near cheek),
           'profile-left' | 'profile-right' (one eye; a biarc silhouette
           with the neck; facing right is the exact mirror of facing left).
    sex    'm' | 'f' (finer, higher-arched brows, shorter nose, smaller mouth,
           a 84-wide head).
    age    'young' | 'adult' | 'elder'.
    lids   'heavy' (default: the pupil hangs from the RULE lid) | 'level' |
           'half' | 'lowered' | 'raised' | 'closed' (+ ``vestigial`` Ø3 dots,
           the Q♠ blind oracle).
    spec   a FaceSpec to start from; keyword overrides (``pupil_dx=2``,
           ``ears=True`` …) are applied last.

    Returns a Face: the head silhouette (paper skin), feature lines (≤ 14
    strokes, counted in ``strokes``) and anchors — axis, eye_y, brow_y,
    nose_y, mouth_y, lip_y, chin, top, temple_l/r, jaw_l/r, crown_y (where a
    band sits), ear_l/r, turn, facing."""
    s = replace(spec) if spec is not None else FaceSpec()
    for k, v in SEX_PRESETS.get(sex, {}).items():
        setattr(s, k, v)
    for k, v in AGE_PRESETS.get(age, {}).items():
        if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in ("nose",):
            setattr(s, k, getattr(s, k) + v)
    for k, v in LID_PRESETS.get(lids, {}).items():
        setattr(s, k, v)
    for k, v in over.items():
        if not hasattr(s, k):
            raise TypeError(f"face(): unknown FaceSpec field {k!r}")
        setattr(s, k, v)
    cx, cy = float(center[0]), float(center[1])
    if gaze.startswith("profile"):
        return _profile_face(cx, cy, s, -1 if gaze.endswith("left") else +1, lids, vestigial)
    turn = 0 if gaze == "frontal" else (-1 if gaze.endswith("left") else +1)
    ey = cy + s.eye_dy
    lines = C.Frag()
    if turn == 0:
        head, info = egg((cx, cy), s.r)
        ax = cx
        # one half drawn and mirrored (§H.0); pupils placed after, so a gaze
        # shift moves both the same way
        half = _eye(ax - s.eye_dx, ey, s, s.eye_w, -1, lids, vestigial, pupil=False)
        half += _brow(ax, s, -1, ey)
        half += _nose_frontal(ax, s, -1, ey)
        lines += half + half.mirror_x(ax)
        if lids != "closed" or vestigial:
            for sd in (-1, 1):
                lines += _pupil(ax + sd * s.eye_dx, ey, s, s.eye_w, lids, vestigial)
        lines += _mouth(ax, s, ey, s.mouth_hw, s.mouth_hw)
        if s.ears:
            e = _ear(cx, cy, s, -1)
            lines += e + e.mirror_x(ax)
    else:
        shift = turn * s.turn_shift * 2 * s.r
        ax = cx + shift
        if "pupil_dx" not in over:
            s.pupil_dx = turn * 2.5
        head, info = egg((cx, cy), s.r, chin_dx=shift * s.chin_swing)
        near, far = -turn, turn
        lines += _eye(ax + near * s.eye_dx, ey, s, s.eye_w, near, lids, vestigial)
        # the far eye (70 % wide) is foreshortened against the far cheek: its
        # outer corner runs 0.8 px INTO the head contour (the lids join the
        # outline — no near-miss, the classic 3/4 eye); the far brow ends on
        # the contour too (the brow ridge)
        fe_w = s.eye_w * s.far_eye
        cx_far = _side_x(info, cx, cy, s.r, ey, far)
        fe_x = cx_far - far * (0.8 + fe_w / 2)
        # its pupil keeps 3 px from the contour: centred, never pushed outward
        lines += _eye(fe_x, ey, s, fe_w, far, lids, vestigial, pdx=-far * 0.6)
        lines += _brow(ax, s, near, ey)
        by = ey + s.brow_dy + s.brow_drop * 0.6
        b_out = P(_side_x(info, cx, cy, s.r, by, far) - far * 0.8, by)
        b_in = P(ax + far * s.brow_in * 0.8, ey + s.brow_dy)
        a_, b_ = (b_out, b_in) if far < 0 else (b_in, b_out)
        lines += line(arc_sag(a_, b_, s.brow_sag * 0.8), MEDIUM, role="brow")
        lines += _nose_3q(ax, s, turn, ey)
        hw_far = s.mouth_hw * 0.78
        lines += _mouth(ax + turn * 1.5, s, ey, hw_far if turn < 0 else s.mouth_hw,
                        hw_far if turn > 0 else s.mouth_hw)
        if s.ears:
            lines += _ear(cx, cy, s, near)
    skin = R(head)
    anchors = _anchors(cx, cy, s, info, ax, ey, turn, 0)
    return Face(head, skin, lines, anchors, _count(lines))


def _side_x(info, cx, cy, r, y, sgn):
    """x of the egg outline at height y on side sgn (circle above cy, the
    side arc below)."""
    if y <= cy:
        return cx + sgn * math.sqrt(max(r * r - (y - cy) ** 2, 0.0))
    O = info["O_l"] if sgn < 0 else info["O_r"]
    rho = info["rho_l"] if sgn < 0 else info["rho_r"]
    return O[0] + sgn * math.sqrt(max(rho * rho - (y - O[1]) ** 2, 0.0))


def _count(lines):
    return sum(1 for m in lines.marks if m.kind == "stroke" or m.role == "pupil")


def _ear(cx, cy, s, side):
    c = P(cx + side * (s.r - 2.0), cy + s.eye_dy + 12)
    a0, a1 = (110, 250) if side < 0 else (-70, 70)
    return line(arc_c(c, 8.5, a0, a1), MEDIUM, role="ear")


def _nose_3q(ax, s, turn, ey):
    """3/4 nose: one MEDIUM ridge from the far brow's inner end down past
    the axis toward the turn, hooking back round the tip toward the near
    cheek (the nostril)."""
    p0 = P(ax + turn * 2.5, ey - 3.0)
    p1 = P(ax + turn * 8.0, ey + s.nose_bot_dy - 5.5)
    h = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    t = C.Turtle(p0[0], p0[1], h)
    t.line_to(p1[0], p1[1])
    # round the tip, then back toward the near side, level
    cur = t.heading
    target = 180.0 if turn > 0 else 0.0
    sweep = ((target - cur + 540) % 360) - 180
    t.arc(3.8, sweep)
    t.fd(5.5)
    return line(t.d(), MEDIUM, role="nose")


def _anchors(cx, cy, s, info, ax, ey, turn, facing):
    r = s.r

    def side_x(y, sgn):
        # x of the head outline at height y on side sgn (circle above cy, side arc below)
        if y <= cy:
            return cx + sgn * math.sqrt(max(r * r - (y - cy) ** 2, 0.0))
        O = info["O_l"] if sgn < 0 else info["O_r"]
        rho = info["rho_l"] if sgn < 0 else info["rho_r"]
        return O[0] + sgn * math.sqrt(max(rho * rho - (y - O[1]) ** 2, 0.0))

    a = dict(center=P(cx, cy), axis=ax, eye_y=ey, brow_y=ey + s.brow_dy, nose_y=ey + s.nose_bot_dy,
             mouth_y=ey + s.mouth_dy, lip_y=ey + s.lip_dy, chin=info["chin"], top=cy - r, r=r,
             temple_l=P(side_x(ey, -1), ey), temple_r=P(side_x(ey, 1), ey),
             jaw_l=P(side_x(ey + s.mouth_dy, -1), ey + s.mouth_dy),
             jaw_r=P(side_x(ey + s.mouth_dy, 1), ey + s.mouth_dy),
             crown_y=cy - r * 0.55, ear_l=P(cx - r + 2, ey + 12), ear_r=P(cx + r - 2, ey + 12),
             turn=turn, facing=facing, side_x=side_x, spec=s)
    return a


def _hd(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))


def _profile_face(cx, cy, s, facing, lids, vestigial):
    """Strict profile (§H.0: one eye), built facing LEFT and mirrored for
    'profile-right' (the exact mirror). The silhouette is ONE G1 chain of
    biarcs through pinned points with pinned tangents — crown, forehead,
    brow ridge, the nose-root notch, a straight nose ridge, the rounded tip,
    subnasale, lips, chin, throat and the neck down to the collar line, then
    up the nape and round the skull — so it reads cleanly at CONTOUR weight
    (no fussy lip notches). Interior marks: the eye (RULE lid,
    FINE lower lid, Ø6 pupil at its front, hanging from the lid), one brow
    arc, the nostril hook and the mouth line (both springing from the
    contour, so they join it), the ear C, and the jaw line from the chin
    back toward the ear (8 strokes). Every free mark keeps
    ≥ 3 px from the CONTOUR's inner edge. The head region includes the neck
    to ``my + 62``: put the collar in front of it."""
    if facing > 0:
        fl = _profile_face(cx, cy, s, -1, lids, vestigial)
        a = dict(fl.anchors)
        for k, v in list(a.items()):
            if isinstance(v, np.ndarray) and v.shape == (2,):
                a[k] = P(2 * cx - v[0], v[1])
            elif isinstance(v, Polygon):
                a[k] = mirror(v, cx)
        a["front"] = 2 * cx - fl.anchors["front"]
        a["axis"] = 2 * cx - fl.anchors["axis"]
        a["facing"] = +1
        hd = G.mirror_x(fl.head, cx)
        return Face(hd, R(hd), fl.lines.mirror_x(cx), a, fl.strokes)
    r = s.r
    ey = cy + s.eye_dy
    fr = cx - r * 0.84                    # the face's front line (brow / lips)
    top = cy - r
    nb = ey + s.nose_bot_dy
    my = ey + min(s.mouth_dy, 41.0)
    ridge = _hd((fr + 3.5, ey + 1.5), (fr - 10.5, nb - 5.0))
    nk = 4.0 if s.r < 43 else 0.0          # a slenderer neck on the smaller (queen / page) head
    chain_pts = [
        ((cx + 4.0, top), 180.0),                    # crown of the skull
        ((fr + 9.0, cy - 30.0), 122.0),              # forehead
        ((fr + 1.0, ey - 8.0), 98.0),                # brow ridge
        ((fr + 3.5, ey + 1.5), ridge),               # nose root (the notch)
        ((fr - 10.5, nb - 5.0), ridge),              # straight ridge to the tip
        ((fr - 8.5, nb + 0.4), 12.0),                # round the tip, under the nose
        ((fr - 1.0, nb + 2.2), 78.0),                # subnasale
        ((fr - 2.6, my - 3.2), 100.0),               # upper lip
        ((fr - 0.4, my + 0.6), 62.0),                # mouth corner (a soft notch)
        ((fr - 1.6, my + 5.0), 108.0),               # lower lip
        ((fr + 2.0, my + 10.5), 88.0),               # chin crease
        ((fr - 0.2, my + 17.5), 102.0),              # chin
        ((fr + 7.0, my + 24.0), 18.0),               # under the chin
        ((fr + 18.0, my + 28.5), 62.0),              # throat
        ((fr + 21.0, my + 62.0), 88.0),              # neck front (to the collar line)
        ((cx + 24.0 - nk, my + 62.0), -95.0),        # neck back
        ((cx + 27.0 - nk, ey + 32.0), -118.0),       # nape (curving in under the occiput)
        ((cx + r + 5.0, cy + 2.0), -88.0),           # occiput: the profile skull is deeper than the frontal egg
    ]
    pts = [P(q) for q, _ in chain_pts]
    hs = [h for _, h in chain_pts]
    d, _ = FM.biarc_chain(pts, hs, closed=True)
    head = d
    lines = C.Frag()
    # eye: front ≥ 3 px + RULE/2 from the contour's inner edge at the nose root
    ex0 = fr + 3.5 + CONTOUR / 2 + GAP_MARK + RULE / 2 + 1.5
    ew = s.eye_w * 0.62
    front, back = P(ex0, ey - 0.3), P(ex0 + ew, ey + 0.9)
    lid_s = max(s.lid_sag, 2.0) * 0.9
    if lids == "closed":
        lines += line(arc_sag(front, back, -abs(s.lid_sag) * 0.8), RULE, role="lid")
        if vestigial:
            lines += dot((ex0 + ew / 2, ey + 7.5), 3.0, role="pupil")
    else:
        lines += line(arc_sag(front, back, lid_s), RULE, role="lid")
        lower_end = P(front[0] + 1.8, ey + 3.6)
        lines += line(arc_sag(lower_end, back, -2.0), FINE, role="lid-lo")
        pu = P(front[0] + 3.6 + max(min(s.pupil_dx, 2.0), -2.0), ey - lid_s * 0.55 + 3.2 + s.pupil_tuck)
        lines += dot(pu, s.pupil_d, role="pupil")
    # brow: from over the eye's front back over the eye
    bx0 = fr + 1.0 + CONTOUR / 2 + GAP_MARK + MEDIUM / 2 + 1.0
    lines += line(arc_sag(P(bx0, ey + s.brow_dy + 1.5), P(ex0 + ew + 3.0, ey + s.brow_dy + 2.5), 2.2),
                  MEDIUM, role="brow")
    # nostril: a hook springing from the contour under the nose, curling up and back
    tn = C.Turtle(fr - 4.0, nb + 1.2, -60.0)
    tn.arc(3.4, 150.0)
    lines += line(tn.d(), MEDIUM, role="nose")
    # mouth: from the corner notch on the contour, back into the cheek
    lines += line(arc_sag(P(fr - 0.4, my + 0.6), P(fr + 10.0, my + 1.6), -1.0), MEDIUM, role="mouth")
    # ear: a C (opening forward) + its inner FINE arc
    ear_c = P(cx + r * 0.20, ey + 9.0)
    lines += line(arc_c(ear_c, 8.5, -75, 95), MEDIUM, role="ear")
    # jaw: from under the chin back toward the ear lobe (stops 3 px short of the ear)
    lines += line(arc_sag(P(fr + 9.0, my + 24.6), P(cx + 1.0, ey + 24.0), 4.0), MEDIUM, role="jaw")
    info = {"chin": P(fr - 0.2, my + 17.5)}
    anchors = dict(center=P(cx, cy), axis=ex0 + ew / 2, front=fr, eye=P(ex0 + ew / 2, ey), eye_y=ey,
                   brow_y=ey + s.brow_dy, nose_y=nb, mouth_y=my, lip_y=my + 5.0, chin=info["chin"], top=top, r=r,
                   nape=P(cx + 27.0 - nk, ey + 32.0), jaw=P(cx + 1.0, ey + 24.0), ear=ear_c,
                   neck_y=my + 62.0, throat=P(fr + 18.0, my + 28.5),
                   crown_y=cy - r * 0.55, turn=0, facing=-1, spec=s)
    return Face(head, R(head), lines, anchors, _count(lines))


# =============================================================================
# 6  hair and beards (§G.24 current lines; gold locks, §C.1)
# =============================================================================
@dataclass
class HairSpec:
    """A hair fall beside the face, as a lock FAN: an annulus sector whose
    outer arc passes through three points (dx from the face axis, dy from the
    egg centre) and whose end is rolled (a semicircular cap)."""
    top: tuple = (-52.0, -30.0)      # outer edge under the crown band end
    bulge: tuple = (-72.0, 42.0)     # outermost point
    bottom: tuple = (-60.0, 118.0)   # outer edge at the rolled end
    ribbons: int = 5                  # lock width in 7 px ribbons; lines = ribbons − 1
    over: float = 14.0               # degrees the fan starts above ``top`` (hidden under the band)
    color: str = GOLD
    edge: float = CONTOUR            # the fan's outer edge weight where it meets paper (sets line 0's inset)


def hair_fall(fc: "Face", side=-1, h: HairSpec = HairSpec()) -> Part:
    """Hair falling beside the face (side −1 = viewer's left; +1 is the exact
    mirror about the face's centre line). The current lines are the fan's
    concentric offsets, 7 px apart, the first 8.4 px inside the outer edge,
    each rolling inward into a Ø6.3 terminal at the curl."""
    cx = float(fc.anchors["center"][0])
    cy = float(fc.anchors["center"][1])
    T0 = P(cx + h.top[0], cy + h.top[1])
    Bg = P(cx + h.bulge[0], cy + h.bulge[1])
    B0 = P(cx + h.bottom[0], cy + h.bottom[1])
    c, Rr = circ3(T0, Bg, B0)
    a_top, a_bot = ang(c, T0), ang(c, B0)
    a0 = a_top + h.over
    a1 = unwrap(a0, a_bot, cw=False)
    first = h.edge / 2 + GAP + FINE / 2 + 0.05
    r_in = Rr - (first + PITCH * (h.ribbons - 2) + EDGE_MED)
    reg = lock_fan(c, Rr, r_in, a0, a1)
    th = np.radians(np.linspace(a0, a1, 400))
    guide = np.column_stack([c[0] + Rr * np.cos(th), c[1] + Rr * np.sin(th)])
    lines = current_lines(guide, h.ribbons - 1, reg, side=+1, first=first, edge=MEDIUM, stagger=9.0)
    part = Part(reg, fill(reg, h.color), lines + outline(reg), {"c": c, "R": Rr, "a": (a0, a1), "r_in": r_in})
    return part.mirrored(cx) if side > 0 else part


def hair_back(fc: "Face", *, volume=9.0, hairline=None, n=4, nape_drop=18.0, color=GOLD, curl=True) -> Part:
    """Hair on the back of a PROFILE (or 3/4) head: the skull plus ``volume``
    px, behind a hairline from the forehead top to behind the ear, down to
    ``nape_drop`` below the ear. Current lines follow the skull (concentric
    offsets of the outer edge) from the forehead back to the nape, rolling
    into terminals. Put it in front of the head in the Scene."""
    a = fc.anchors
    cx, cy = a["center"]
    r = a["r"]
    facing = a.get("facing", 0) or a.get("turn", 0) or -1        # a 3/4 head's back is away from its turn
    outer = Point(cx, cy).buffer(r + volume, quad_segs=64)
    ear = a.get("ear", P(cx, cy + 12))
    fore = P(cx + facing * r * 0.55, cy - r * 0.78) if hairline is None else P(hairline[0])
    back_low = P(cx - facing * (r + volume + 4), ear[1] + nape_drop)
    ear_front = P(ear[0] + facing * 10.0, ear[1] - 6.0)
    cut = Polygon([tuple(fore), tuple(ear_front), (ear[0] + facing * 4.0, ear[1] + nape_drop),
                   tuple(back_low), (cx - facing * (r + 40), cy - r - 40), (cx + facing * (r * 0.3), cy - r - 40)])
    reg = outer.intersection(cut.convex_hull if False else cut).buffer(0)
    reg = max(_polys_of(reg), key=lambda g: g.area) if not reg.is_empty else reg
    # guide: the outer circle from the forehead end back and down
    a0 = ang((cx, cy), fore) - facing * 4.0
    a1 = ang((cx, cy), back_low)
    cw = facing < 0
    a1 = unwrap(a0, a1, cw=cw)
    th = np.radians(np.linspace(a0, a1, 400))
    guide = np.column_stack([cx + (r + volume) * np.cos(th), cy + (r + volume) * np.sin(th)])
    side = +1 if not cw else -1
    lines = current_lines(guide, n, reg, side=-side if facing < 0 else side, edge=CONTOUR, stagger=9.0,
                          end="curl" if curl else "edge")
    if not lines.meta.get("lines"):
        lines = current_lines(guide, n, reg, side=side if facing < 0 else -side, edge=CONTOUR, stagger=9.0)
    return Part(reg, fill(reg, color), lines + outline(reg), {})


def hair_cap(fc: "Face", *, volume=10.0, hairline=0.62, temple_dy=-2.0, drop=14.0, n=4, parting=0.0,
             color=GOLD) -> Part:
    """Hair covering the skull of a FRONTAL or 3/4 head (queens, jacks, a
    bare-headed king): the skull circle plus ``volume`` px, above a hairline
    arc from temple to temple through the forehead top (``hairline`` × r
    above the egg centre), down to ``drop`` px below the eye line at the
    sides. A 3/4 head's cap swells away from the turn (we see the back of
    the skull). Current lines (§G.24) run from the ``parting`` (px from the
    face axis; 0 = centre) down each side, offsets of the outer edge, rolling
    into terminals at the temples. Put it in front of the head; long hair
    (``hair_fall``) goes behind the head. → Part (meta 'hairline')."""
    a = fc.anchors
    cx, cy = a["center"]
    r = a["r"]
    turn = a.get("turn", 0)
    ey = a["eye_y"]
    ax = float(a["axis"]) if not isinstance(a["axis"], np.ndarray) else float(a["axis"][0])
    oc = P(cx - turn * 4.0, cy - 2.0)
    outer = Point(*oc).buffer(r + volume, quad_segs=64)
    L = P(_side_x_face(a, ey + temple_dy, -1) + 1.0, ey + temple_dy)
    Rt = P(_side_x_face(a, ey + temple_dy, +1) - 1.0, ey + temple_dy)
    Tp = P(ax + parting * 0.3, cy - r * hairline)
    hl = C.sample_d(arc3(L, Tp, Rt), 0.3)[0][0]
    face_zone = Polygon(np.vstack([hl, [[Rt[0] + 60, Rt[1]], [Rt[0] + 60, cy + 3 * r], [L[0] - 60, cy + 3 * r],
                                        [L[0] - 60, L[1]]]])).buffer(0)
    reg = outer.intersection(box(0, 0, 2000, ey + drop)).difference(face_zone)
    # keep the side locks outside the head (they frame the temples)
    reg = reg.difference(fc.skin.buffer(-0.5).intersection(box(0, ey + temple_dy, 2000, 2000)))
    reg = max(_polys_of(reg.buffer(0)), key=lambda g: g.area)
    lines = C.Frag()
    top = P(ax + parting, oc[1] - (r + volume))
    for sg in (-1, 1):
        a0 = ang(oc, top)
        a1 = ang(oc, (oc[0] + sg * (r + volume), ey + drop))
        cw = sg > 0
        a1 = unwrap(a0, a1, cw=cw)
        th = np.radians(np.linspace(a0, a1, 300))
        guide = np.column_stack([oc[0] + (r + volume) * np.cos(th), oc[1] + (r + volume) * np.sin(th)])
        half = reg.intersection(box(top[0], -1e4, 1e4, 1e4) if sg > 0 else box(-1e4, -1e4, top[0], 1e4))
        lines += current_lines(guide, n, half, side=(-1 if sg > 0 else +1), edge=CONTOUR, stagger=8.0,
                               placed=None)
    return Part(reg, fill(reg, color), lines + outline(reg), {"hairline": hl})


def _side_x_face(a, y, sgn):
    """x of a frontal / 3/4 face's head outline at height y (anchors ``a``)."""
    return a["side_x"](y, sgn)


def neck(fc: "Face", *, bottom=None, width=None, color=None) -> Part:
    """The neck under a frontal / 3/4 head: a paper (skin) column from inside
    the jaw down to ``bottom`` (default: 70 px below the chin), slightly
    widening, shifted toward a 3/4 turn. Put it BEHIND the head (the jaw
    overlaps it) and behind the collar. Paper parts are never painted: its
    region only hides what is behind it. → Part."""
    a = fc.anchors
    cx, cy = a["center"]
    r = a["r"]
    turn = a.get("turn", 0)
    ch = a["chin"]
    w = width if width is not None else r * 0.78
    yb = ch[1] + 70.0 if bottom is None else bottom
    x0 = cx + turn * r * 0.10
    top_y = cy + r * 0.55
    poly = Polygon([(x0 - w / 2, top_y), (x0 + w / 2, top_y), (x0 + w / 2 + 4, yb), (x0 - w / 2 - 4, yb)])
    fills = fill(poly, color) if color else C.Frag()
    return Part(poly, fills, outline(poly), {})


@dataclass
class BeardSpec:
    """A beard as current lines (points: dx from the face axis, dy from the
    egg centre). 'forked' = two lobes to tips either side of a notch on the
    axis; 'full' = one rounded lobe; 'square' = a flat-bottomed block."""
    style: str = "forked"
    side: tuple = (-42.0, 20.0)      # sideburn, on the head outline
    bulge: tuple = (-48.0, 78.0)     # outermost point of the outer edge
    tip: tuple = (-17.0, 138.0)      # fork tip
    notch_dy: float = 104.0          # fork notch on the axis
    cheek_sag: float = -3.0          # cheek line (sideburn → moustache) bulge; − = toward the chin
    lip_clear: float = 8.2           # beard top this far below the lower-lip tick (≥ 3 px clear)
    lines: int = 4
    stagger: float = 9.0
    color: str = GOLD


def beard(fc: "Face", b: BeardSpec = BeardSpec(), mo: "Part | None" = None) -> Part:
    """Frontal beard (drawn as the left half and mirrored). The outer edge is
    one arc (sideburn → bulge → tip); a forked beard's inner edge runs from
    the tip up to the notch on the axis. Its current lines are offsets of the
    OUTER edge, 7 px apart, flowing from the cheek to the tip, so they
    converge on the tip as the lobe narrows; each ends in a rolled Ø6.3
    terminal where the lobe runs out, staggered — no cluster at the fork.
    Pass the moustache Part as ``mo`` so the beard's upper edge tucks under
    it (the beard's upper edge then tucks under the moustache)."""
    a = fc.anchors
    ax = float(a["axis"])
    cx, cy = a["center"]
    S = P(ax + b.side[0], cy + b.side[1])
    Bg = P(ax + b.bulge[0], cy + b.bulge[1])
    Ft = P(ax + b.tip[0], cy + b.tip[1])
    top_ax = a["lip_y"] + b.lip_clear
    if b.style == "forked":
        N = P(ax, cy + b.notch_dy)
        out = Path(S).arc3(Bg, Ft).sag(N, -3.0).line((ax, top_ax))
    elif b.style == "square":
        Bt = P(ax + b.bulge[0] + 2, cy + b.tip[1])
        out = Path(S).arc3(Bg, Bt).line((ax, cy + b.tip[1])).line((ax, top_ax))
    else:
        out = Path(S).arc3(Bg, (ax, cy + b.tip[1])).line((ax, top_ax))
    # upper edge: from under the lip, round the mouth, up INTO the moustache
    # (hidden behind it: the junction is the moustache's own outline, no
    # sliver of skin, no ink knot), then out along the cheek to the sideburn
    sp = a["spec"]
    Q = P(ax - sp.mouth_hw - 8.0, a["lip_y"] + 2.0)          # ≥ 3 px clear of the mouth corners
    if mo is not None:
        tip, root = mo.meta["tip"], mo.meta["root"]
        Mi = tip + (root - tip) * 0.42 - P(0.0, 3.2)
    else:
        Mi = P(ax - sp.mouth_hw - 4.0, a["mouth_y"] - 4.0)
    out.arc3(Q, Mi).sag(S, b.cheek_sag).close()
    half = R(out.d).intersection(box(0, 0, ax, 2000))
    half = max(_polys_of(half), key=lambda g: g.area)
    shape = U(half, mirror(half, ax))
    # current lines: offsets of the outer edge from the sideburn down to the tip
    gpts = C.sample_d(arc3(S, Bg, Ft if b.style == "forked" else P(ax, cy + b.tip[1])), 0.4)[0][0]
    # extend the guide up past the sideburn so the first lines start on the cheek edge
    t0 = gpts[1] - gpts[0]
    t0 = t0 / np.hypot(*t0)
    gpts = np.vstack([gpts[0] - t0 * 30.0, gpts])
    lines = current_lines(gpts, b.lines, half, side=+1, first=EDGE_MED, edge=MEDIUM, stagger=b.stagger)
    lines = lines + lines.mirror_x(ax)
    return Part(shape, fill(shape, b.color), lines + outline(shape),
                {"S": S, "tip": Ft, "top_ax": top_ax})


@dataclass
class MoustacheSpec:
    """Two drooping leaves (the deck's leaf form) from under the nose out and
    down past the mouth corners; dx from the axis, dy below the nose base."""
    root: tuple = (-1.5, 8.5)   # 8.5 below the nose base: the alar wings keep 3 px (K♠)
    tip: tuple = (-30.0, 25.0)
    arch: float = 6.2           # upper edge sagitta (bulges up)
    under: float = 0.8          # lower edge sagitta (bulges down: a leaf); keep the mouth ≥ 3 px clear
    color: str = GOLD


def moustache(fc: "Face", m: MoustacheSpec = MoustacheSpec()) -> Part:
    """Frontal moustache: each half is a drooping leaf between two arcs from
    the root under the nose to a tip beside the mouth, the upper arc higher
    than the lower; the halves meet under the nose. The mouth's lip bow and
    lower-lip tick show below it."""
    a = fc.anchors
    ax = float(a["axis"])
    ny = a["nose_y"]
    p0 = P(ax + m.root[0], ny + m.root[1])
    p1 = P(ax + m.tip[0], ny + m.tip[1])
    # travel tip → root (left to right): screen-left = up
    leaf = R(Path(p1).sag(p0, m.arch).sag(p1, m.under).close().d)
    shape = U(leaf, mirror(leaf, ax))
    return Part(shape, fill(shape, m.color), outline(shape), {"tip": p1, "root": p0})


# =============================================================================
# 7  hands (§H.0: mitten, 3 finger lines, separate thumb, closed round a cylinder)
# =============================================================================
#
# One hand language for every kit hand (COURT_GUIDE §4 "Hands"):
#
# * a paper mitten: CONTOUR silhouette, MEDIUM interior lines, no fill;
# * four fingers: rounded fingertip LOBES separated by notches, and three
#   MEDIUM finger lines that start in the notches and stop short of the
#   knuckles at staggered lengths (the middle one longest), ≥ 7.3 px apart
#   centre to centre (4.2 px of paper between MEDIUM lines, §I.12);
# * the THUMB: tapered, its root merged into the back of the hand (no line
#   across it); its crease is the only line where it lies on the hand;
# * the back of the hand tapers from the knuckle ridge to a wrist ≈ 0.7 × the
#   knuckle breadth, then runs ``HAND_STUB`` px on past the wrist point.
#   ``Hand.add_to`` cuts that run with the arm already in the scene (cuff,
#   sleeve, forearm, gauntlet, bracelet), so the cuff's edge is the only line
#   at the junction: the wrist goes INTO the cuff instead of sitting on it;
# * sizes are tied to the face, not to the object held: a fist's finger block
#   is ≥ 32 px tall (four 8 px fingers) and 1.15 × as long, whatever the shaft;
# * the wrist goes out along the hand's axis (``fist_wrist``); below a fist the
#   heel keeps 7.3 px off the shaft, and on a haloed shaft the ground left
#   between heel, cuff and paper channel turns to paper (``HEEL_CLOSE``).

FIST_H_MIN = 32.0        # finger-block height floor: four bands at ≥ 8 px pitch
FIST_H_K = 0.92          # block height per unit of the caller's h (the thumb now stands on top of the block)
FIST_LEN_K = 1.15        # finger-block length (fingertip lobes → knuckle ridge) per unit block height
FIST_TIP_OUT = 5.0       # fingertip lobes show at most this far past the shaft's far edge
HAND_STUB = 7.0          # px a hand runs on past its wrist point, under the cuff
PARALLEL_MIN = GAP + MEDIUM          # 7.3: centre distance of two parallel MEDIUM lines (§I.12)
HEEL_CLOSE = 8.0         # ground between a heel and a haloed shaft narrower than 2 × this turns to paper
ARM_WORDS = ("cuff", "sleeve", "forearm", "arm", "gauntlet", "bracelet", "wrist")
CUFF_WORDS = ("cuff", "gauntlet", "bracelet", "wrist")
HAND_LOG: list = []      # construction warnings, newest last (also issued as HandWarning)


class HandWarning(UserWarning):
    """A hand the kit can draw but a court should re-seat (wrist position)."""


def _hand_warn(msg):
    import warnings
    HAND_LOG.append(msg)
    warnings.warn(msg, HandWarning, stacklevel=3)


def _unit(v, default=(1.0, 0.0)):
    v = np.asarray(v, float)
    n = float(np.hypot(*v))
    return v / n if n > 1e-9 else np.asarray(default, float)


def _qbez(p0, c, p1, n=18):
    t = np.linspace(0.0, 1.0, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t ** 2 * p1


def _edge(p0, u0, p1, u1, n=18):
    """Points of a smooth edge leaving p0 along u0 and arriving at p1 along
    u1: a quadratic Bézier whose control point is where the two tangents
    meet (straight when they do not meet ahead of p0 and behind p1)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    u0, u1 = _unit(u0), _unit(u1)
    L = float(np.hypot(*(p1 - p0)))
    A = np.array([[u0[0], u1[0]], [u0[1], u1[1]]])
    ctrl = (p0 + p1) / 2
    if abs(np.linalg.det(A)) > 1e-6:
        s, t = np.linalg.solve(A, p1 - p0)          # p0 + s u0 = p1 - t u1
        if 0.5 < s < 1.6 * L and 0.5 < t < 1.6 * L:
            ctrl = p0 + s * u0
    return _qbez(p0, ctrl, p1, n)


def _to_local(pt, at, rot, mirror):
    """Screen point → a hand's local frame (inverse of _rigid)."""
    ww = P(pt) - P(at)
    rr = math.radians(-rot)
    q = P(ww[0] * math.cos(rr) - ww[1] * math.sin(rr), ww[0] * math.sin(rr) + ww[1] * math.cos(rr))
    if mirror:
        q[0] = -q[0]
    return q


def _vec(M, v):
    """Apply the linear part of shapely matrix M to vector v."""
    a, b, d, e = M[0], M[1], M[2], M[3]
    return P(a * v[0] + b * v[1], d * v[0] + e * v[1])


def _crease(boundary, inside, keep=None, min_len=3.0):
    """The part of ``boundary`` (a region's outline) that lies inside
    ``inside`` (and inside ``keep``, when given): a thumb's crease where it
    lies on the hand. → list of point arrays."""
    rings = [LineString(np.asarray(pg.exterior.coords)) for pg in _polys_of(boundary)]
    if not rings:
        return []
    ln = shapely.union_all(rings)
    z = inside.buffer(-0.05)
    if keep is not None:
        z = z.intersection(keep)
    res = ln.intersection(z)
    try:
        res = shapely.line_merge(res)
    except Exception:
        pass
    return [np.asarray(g.coords) for g in _lines_of(res) if g.length >= min_len]


def _arm_dir(armr, W, u_guess, reach=8.0):
    """The forearm direction (unit, from the wrist into the arm) implied by
    the arm region's edge through the wrist point ``W`` (a kit sleeve's
    cuff line), or None when W is not on that edge or the edge is not a
    clear line within 55° of square to ``u_guess``."""
    b = armr.boundary
    pw = Point(*W)
    if b.distance(pw) > 2.5:
        return None
    near = b.intersection(pw.buffer(reach, quad_segs=16))
    try:
        near = shapely.line_merge(near)
    except Exception:
        pass
    ls = [g for g in _lines_of(near) if g.length > 0.5 * reach]
    if not ls:
        return None
    g = min(ls, key=lambda gg: gg.distance(pw))
    xy = np.asarray(g.coords)
    e = _unit(xy[-1] - xy[0])
    # a straight run: every vertex within 1.2 px of the chord
    nrm = np.array([-e[1], e[0]])
    if np.max(np.abs((xy - xy[0]) @ nrm)) > 1.2:
        return None
    us = np.array([e[1], -e[0]])
    if armr.contains(Point(*(W + us * 3.0))) == armr.contains(Point(*(W - us * 3.0))):
        if float(np.dot(us, u_guess)) < 0:
            us = -us
    elif not armr.contains(Point(*(W + us * 3.0))):
        us = -us
    if float(np.dot(us, _unit(u_guess))) < math.cos(math.radians(55.0)):
        return None
    return us


@dataclass
class Hand:
    """A built hand. ``hand`` (the mitten, thumb merged in for kit hands) is
    stacked in front of the scene by ``add_to``; ``thumb`` is a separate
    front piece only for hands that keep one (``thumb.meta['merged']`` marks
    a kit thumb that is already part of ``hand`` — its shape is still given,
    for callers that use it as a blocker). ``wrist``/``wrist_w``: where the
    arm meets the hand; ``wrist_dir``: the unit direction from the hand into
    the forearm there; ``stub``: px the hand runs on past ``wrist``, cut by
    the cuff in ``add_to``."""
    hand: Part
    thumb: Part
    wrist: np.ndarray
    wrist_w: float
    wrist_dir: np.ndarray | None = None
    stub: float = 0.0

    def tucked(self, sc: "Scene | None" = None, cuff=None) -> Part:
        """The hand Part with its wrist run cut by the arm: ``cuff`` = item
        name(s) in ``sc`` or a region; default every item already in ``sc``
        whose name contains cuff / sleeve / forearm / arm / gauntlet /
        bracelet / wrist and that overlaps the run. When the wrist point lies
        on the arm's edge (a kit sleeve's cuff line), the wrist is first
        re-aimed along the forearm that edge implies and cut on that line, so
        the cuff edge is the one line at the junction."""
        hp = self.hand
        if self.stub <= 0 or self.wrist_dir is None or "inner" not in hp.meta:
            return hp
        W, u = P(self.wrist), _unit(self.wrist_dir)
        r0 = self.stub + self.wrist_w + 8.0
        disc = Point(*W).buffer(r0, quad_segs=16)
        regs, cuffs = [], []
        if cuff is None:
            if sc is not None:
                pw = Point(*W)
                for it in sc.items:
                    if (it.occ is not None and not it.occ.is_empty and it.occ.intersects(disc)
                            and any(w in it.name.lower() for w in ARM_WORDS)):
                        if it.occ.contains(pw) and it.occ.boundary.distance(pw) > 3.0:
                            continue                # a region the whole wrist sits on (an upper sleeve)
                        regs.append(it.occ)
                        if any(w in it.name.lower() for w in CUFF_WORDS):
                            cuffs.append(it.occ)
        elif isinstance(cuff, str) or (isinstance(cuff, (tuple, list)) and cuff and isinstance(cuff[0], str)):
            names = (cuff,) if isinstance(cuff, str) else tuple(cuff)
            regs = [it.occ for it in (sc.items if sc is not None else []) if it.name in names and it.occ is not None]
        else:
            regs = [R(cuff)]
        if not regs:
            return hp
        armr = shapely.union_all(regs)
        cuffr = shapely.union_all(cuffs) if cuffs else None
        us = _arm_dir(armr, W, u)
        if us is not None:
            if "rebuild" in hp.meta and float(np.dot(us, u)) < math.cos(math.radians(3.0)):
                hp = hp.meta["rebuild"](us)
            u = us
        n = np.array([u[1], -u[0]])
        zone = Polygon([tuple(W - 4.0 * u + n * r0), tuple(W - 4.0 * u - n * r0),
                        tuple(W + u * r0 - n * r0), tuple(W + u * r0 + n * r0)])
        run = hp.shape.intersection(zone)
        if run.is_empty:
            return hp
        # the hand runs over the sleeve's lip above a cuff (the kit cuff's top edge sags
        # 2.5 px below the sleeve's end) and stops at the cuff: one line at the junction
        lip = 0.0
        if cuffr is not None and us is not None:
            lip = 3.6
        lipz = Polygon([tuple(W - 0.2 * u + n * r0), tuple(W - 0.2 * u - n * r0),
                        tuple(W + lip * u - n * r0), tuple(W + lip * u + n * r0)]) if lip else Polygon()
        if cuffr is not None:
            # the cuff alone decides where the hand ends: the hand covers any sleeve lip
            # above it and is cut exactly on the cuff's edge (one line, no corner knobs);
            # a straight cut only well inside the cuff
            cut = run.intersection(cuffr)
            deep = max(lip, self.stub - 1.0)
            cut = cut.union(run.intersection(armr.difference(cuffr)).intersection(
                halfplane(W + u * deep, W + u * deep + n, side=-1)))
            cut = cut.union(run.intersection(halfplane(W + u * deep, W + u * deep + n, side=-1)))
        else:
            cut = run.intersection(armr.difference(lipz))
            if us is not None:                      # everything past the cuff line goes, covered or not
                cut = cut.union(run.intersection(halfplane(W + u * lip, W + u * lip + n, side=-1)))
        if cut.area < 0.5:
            return hp
        shape = hp.shape.difference(cut)
        # drop the hairline spikes a cut along a nearly coincident cuff edge can leave
        shape = shape.buffer(-0.4, join_style=2, mitre_limit=4.0).buffer(0.4, join_style=2, mitre_limit=4.0)
        polys = _polys_of(shape)
        if not polys:
            return hp
        shape = max(polys, key=lambda g: g.area)
        beyond = Polygon([tuple(W + u * (lip + 1.5) + n * r0), tuple(W + u * (lip + 1.5) - n * r0),
                          tuple(W + u * r0 - n * r0), tuple(W + u * r0 + n * r0)])
        left = shape.intersection(beyond).difference(armr).area
        if left > 6.0:
            _hand_warn(f"hand at ({W[0]:.0f}, {W[1]:.0f}): {left:.0f} px² of the wrist shows past the cuff "
                       "(hand wider than the cuff opening, or the cuff not at the wrist)")
        return Part(shape, hp.fills, outline(shape) + hp.meta["inner"],
                    {**hp.meta, "tucked": True, "cutline": (W, u, max(lip, self.stub - 1.0))})

    def add_to(self, sc: "Scene", name: str, *, halo=HALO, halo_skip=(), halo_only=None, cuff=None):
        """Stack the hand in front (wrist tucked into the arm, see ``tucked``),
        then its thumb if it is a separate piece (the thumb's halo leaves its
        own hand alone)."""
        hp = self.tucked(sc, cuff)
        if "inner" in hp.meta and not halo:
            # a kit hand closed on a haloed attribute carries the attribute's paper
            # channel round its own fingertips and heel there (the Drifters treatment):
            # the lobes end in paper instead of 1–3 px short of a pattern. The
            # channel is an empty item just behind the hand.
            tips = hp.meta.get("tipzone")
            heelz = hp.meta.get("heelzone")
            arms = tuple(it.name for it in sc.items if any(w in it.name.lower() for w in ARM_WORDS))
            for it in list(sc.items) if tips is not None else []:
                if it.halo > 0 and it.occ is not None and not it.occ.is_empty and it.occ.intersects(hp.shape):
                    zone = hp.shape.intersection(it.occ.buffer(it.halo + MEDIUM / 2 + 3.5, quad_segs=12))
                    zone = zone.intersection(tips)
                    if zone.area > 1.0:
                        # the channel round the lobes stays beside the attribute (not past its end)
                        hz = zone.buffer(it.halo + MEDIUM / 2, quad_segs=12).intersection(
                            it.occ.buffer(it.halo + MEDIUM / 2 + 5.0, quad_segs=12))
                        sc.add(f"{name}~{it.name}", C.Frag(), zone, sil=False, halo=it.halo,
                               halo_skip=it.halo_skip, halo_only=it.halo_only, halo_zone=hz.union(zone))
                    if heelz is None:
                        continue
                    # below the fingers the shaft's channel reaches the heel: the ground left
                    # between them (narrower than 2 × HEEL_CLOSE) turns to paper, closing on
                    # a round concave arc — never a 1–3 px sliver or an acute wedge
                    A = it.occ.buffer(it.halo + MEDIUM / 2, quad_segs=12)
                    # the cuff/sleeve at the wrist closes the pocket too (no jade sliver left
                    # between the paper and the cuff's side)
                    armz = [a.occ for a in sc.items if a.name in arms and a.occ is not None]
                    arm_r = shapely.union_all(armz) if armz else Polygon()
                    near_arm = arm_r.intersection(hp.shape.buffer(3.0 * HEEL_CLOSE, quad_segs=8))
                    both = shapely.union_all([A, hp.shape, near_arm])
                    gap = both.buffer(HEEL_CLOSE, quad_segs=12).buffer(-HEEL_CLOSE, quad_segs=12).difference(both)
                    gap = gap.intersection(heelz)
                    if not arm_r.is_empty:
                        gap = gap.difference(arm_r)
                    cl = hp.meta.get("cutline")
                    if cl is not None:
                        Wc, uc, dp = cl
                        nc = np.array([uc[1], -uc[0]])
                        d2 = dp + 1.5 * HEEL_CLOSE
                        gap = gap.intersection(halfplane(Wc + uc * d2, Wc + uc * d2 + nc, side=+1))
                    # only the ground BETWEEN the shaft's channel and the heel
                    gap = shapely.union_all([g for g in _polys_of(gap) if g.area > 2.0
                                             and g.distance(A) < 0.6 and g.distance(hp.shape) < 0.6]) \
                        if not gap.is_empty else gap
                    if gap.is_empty or gap.area < 2.0:
                        continue
                    occ = hp.shape.intersection(gap.buffer(2.0, quad_segs=8))
                    if occ.is_empty:
                        continue
                    sc.add(f"{name}~heel~{it.name}", C.Frag(), occ, sil=False, halo=it.halo,
                           halo_skip=tuple(it.halo_skip) + arms, halo_only=it.halo_only,
                           halo_zone=gap.union(occ))
        sc.add(name, hp.frag, hp.shape, halo=halo, halo_skip=halo_skip, halo_only=halo_only)
        th = self.thumb
        if th.shape is not None and not th.shape.is_empty and not th.meta.get("merged"):
            sc.add(name + "-thumb", th.frag, th.shape, halo=halo,
                   halo_skip=tuple(halo_skip) + (name,), halo_only=halo_only)
        return sc


def _xf(g, M):
    """Apply the rigid 2×3 matrix M (a, b, c, d, e, f) to shapely g."""
    return shapely.affinity.affine_transform(g, M)


def _rigid(origin, deg, mirror_x=False):
    """Local → screen: optional mirror about local x = 0, rotate by ``deg``
    (screen, clockwise), translate to ``origin``. Returns (M for shapely,
    M for Frag.transformed)."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    mx = -1.0 if mirror_x else 1.0
    # [x'] = [c -s][mx*x] + o
    A, Bm, Cm, Dm = c * mx, -s, s * mx, c
    ox, oy = origin
    return (A, Bm, Cm, Dm, ox, oy), (A, Cm, Bm, Dm, ox, oy)


def _scallops(p_from, p_to, n, sag):
    """n scallops from p_from to p_to bulging ``sag`` to the screen-left. → d
    (continuing a path; no M)."""
    pts = [p_from + (p_to - p_from) * k / n for k in range(n + 1)]
    return "".join(arc_sag(pa, pb, sag, move=False) for pa, pb in zip(pts[:-1], pts[1:])), pts


def _junction_smooth(shape, keep_out, r=2.6):
    """Fill the concave notches of ``shape`` (closing, radius r) except inside
    ``keep_out`` (fingertip notches stay crisp)."""
    closed = shape.buffer(r, quad_segs=10).buffer(-r, quad_segs=10)
    return shape.union(closed.difference(keep_out))


def fist(at, axis_deg=-90.0, *, shaft_w=22.0, back=+1, wrist=None, wrist_w=24.0, h=34.0,
         reach=7.0, knuckle=11.0, thumb_r=5.6, hand=None, view=None, arm=None, stub=HAND_STUB,
         hidden_wrist=False) -> Hand:
    """A fist closed round a cylinder (sceptre, staff, key, paddle, fiddle
    neck, trumpet, stem, rope) whose axis passes through ``at`` pointing
    ``axis_deg`` (screen degrees of the shaft's UP end; −90 = vertical).

    Built in a local frame (shaft vertical, knuckles toward +x when ``back``
    = +1, i.e. the back of the hand faces the wrist side), then placed
    rigidly:

    * the FINGER BLOCK: four bands wrapping across the front of the shaft,
      ``max(0.92 h, 32)`` tall and 1.15 × as long whatever the shaft width
      (a thin stem no longer makes a small square fist); its fingertip edge
      is four rounded lobes curling round the far side of the shaft, ≤ 5 px
      past it (``reach`` caps this), the notches just past the edge;
    * finger line 1 runs from its notch into the thumb's underside (one
      stroke: the index finger's edge becomes the thumb's), lines 2 and 3
      stop short of the knuckles (the middle one longest); every band is
      ≥ 8 px (≥ 4.9 px of paper between MEDIUM lines);
    * the THUMB lies over the top of the fist: its root stands 0.2 × the
      block height above it at the knuckle end (merged into the back of the
      hand, no line across it), it tapers to a rounded tip resting on the
      index finger near the shaft's centre line;
    * the BACK OF THE HAND is the rounded knuckle end of the fist; the WRIST
      tapers out of it (to ≈ 0.7 × the block height, never wider than
      ``wrist_w``), bending smoothly to arrive at ``wrist`` (screen point;
      default down and out) along the forearm (``arm``: a screen direction
      from the wrist toward the elbow; default: estimated, and
      ``Hand.add_to`` re-aims it along the sleeve it finds), and runs
      ``stub`` px on into the sleeve;
    * the HEEL leaves the block's underside in a smooth concave curve that
      keeps 7.3 px off the shaft (the shaft shows full width below the fist).

    ``hand`` ('L'|'R', the figure's hand): the construction is a back-of-hand
    view, which is a LEFT hand when ``back`` = +1 and a RIGHT hand when −1;
    a mismatch is drawn as the PALM view (``view='palm'``: the same
    silhouette read from the palm side, the fingertips curled back to the
    heel shown as tip lobes where the finger lines end). ``HandWarning``s
    (also in ``HAND_LOG``) flag wrists inside the knuckle line, bent > 65°
    off the hand axis, far from the knuckles, or over the shaft
    (``hidden_wrist``: the wrist runs on behind something in front — a
    fiddle's body — so only its direction matters and these are not
    raised). ``fist_wrist`` gives a good wrist point. Returns a Hand whose
    thumb is merged into the mitten."""
    a = shaft_w / 2.0
    hb = max(FIST_H_K * float(h), FIST_H_MIN)
    p = hb / 4.0
    t_up = 0.20 * hb                               # the thumb's root stands this far above the block
    ytop = -(hb + t_up) / 2.0                      # the whole fist (thumb + block) centred on ``at``
    y0 = ytop + t_up
    y1 = y0 + hb
    yc = (y0 + y1) / 2
    tip_out = min(max(float(reach), 3.0), FIST_TIP_OUT)
    x_tip = -a - tip_out
    Lf = max(FIST_LEN_K * hb, 2 * a + tip_out + max(float(knuckle), 12.0))
    x_kn = x_tip + Lf
    rot = axis_deg + 90.0
    mir = back < 0
    M, Mf = _rigid(at, rot, mirror_x=mir)
    dorsal = "L" if back > 0 else "R"
    if view is None:
        view = "back" if (hand is None or str(hand).upper()[:1] == dorsal) else "palm"
    where = f"fist at ({float(at[0]):.0f}, {float(at[1]):.0f})"

    # ---- finger block: four bands, rounded fingertip lobes, notches -------------------
    sl = (0.36 if view == "back" else 0.28) * p
    x_c = x_tip + sl
    path = Path(P(x_kn, y0)).line(P(x_c, y0))
    cusps = [P(x_c, y0)]
    for k in range(4):
        q = P(x_c, y0 + (k + 1) * p)
        path.sag(q, -sl)
        cusps.append(q)
    block = R(path.line(P(x_kn, y1)).close().d)
    block = block.buffer(-2.2, quad_segs=10).buffer(2.2, quad_segs=10)

    # ---- thumb: over the top of the fist, tip resting on the index finger --------------
    rr = 0.19 * hb                                 # root radius
    rt = 0.60 * p                                  # tip radius
    x_tt = x_kn - 0.56 * Lf
    Tc = P(x_tt, y0 + p - rt)                      # its underside continues finger line 1
    Rc = P(x_kn - 0.06 * Lf, ytop + rr)
    cen = _qbez(Tc, (Tc + Rc) / 2 + P(0.0, -1.6), Rc, 16)
    discs = [Point(*q).buffer(rw, quad_segs=16) for q, rw in zip(cen, np.linspace(rt, rr, len(cen)))]
    thumb = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(discs[:-1], discs[1:])])

    # ---- the wrist ----------------------------------------------------------------
    W = P(x_kn, yc) + hb * P(0.55, 0.62) if wrist is None else _to_local(wrist, at, rot, mir)
    Bs = P(x_kn - 0.20 * hb, yc + 0.03 * hb)       # the back-of-hand mass the wrist grows from
    chord = W - Bs
    off = math.degrees(math.atan2(chord[1], chord[0]))
    dist = float(np.hypot(*(W - P(x_kn, yc))))
    if W[0] < x_kn - 4.0 and not hidden_wrist:
        _hand_warn(f"{where}: wrist {x_kn - W[0]:.0f} px inside the knuckle line (move it out along the hand axis)")
    if abs(off) > 65.0 and not hidden_wrist:
        _hand_warn(f"{where}: wrist bent {off:.0f}° off the hand axis (≤ 65° reads)")
    if dist > 1.3 * hb and not hidden_wrist:
        _hand_warn(f"{where}: wrist {dist:.0f} px from the knuckles (> 1.3 × {hb:.0f}): a long bare wrist; "
                   "move the cuff up the forearm")
    x_min = a + PARALLEL_MIN                       # the heel's floor below the fist
    hK = 0.47 * hb                                 # half-breadth of the back at the knuckles

    def build(u):
        """hand region and interior lines (local) for a forearm direction u."""
        u = _unit(u)
        n_th = np.array([u[1], -u[0]])             # the thumb side of the wrist
        hw = min(float(wrist_w), 0.70 * hb) / 2.0
        hw_in = hw
        Wb = W - n_th * hw
        x_floor = x_min + 0.16 * hb                # the heel angles away from the shaft
        if Wb[0] < x_floor and Wb[1] > y1 and n_th[0] > 1e-3:
            hw_in = min(hw, max((W[0] - x_floor) / n_th[0], 0.55 * hw))
            Wb = W - n_th * hw_in
            if Wb[0] < x_min + 0.5:
                # never onto the shaft: the inner wrist edge stops at the heel's floor
                hw_in = max((W[0] - x_min - 0.5) / n_th[0], 0.25 * hw)
                Wb = W - n_th * hw_in
        # the wrist: one tapered sweep from the knuckle mass, arriving along the forearm
        Lw = float(np.hypot(*(W - Bs)))
        C_ = W - u * 0.45 * Lw
        nseg = max(10, int(Lw / 2.5))
        tt = np.linspace(0.0, 1.0, nseg + 1)
        cen_ = list(_qbez(Bs, C_, W, nseg + 1)) + [W + u * stub * 0.5, W + u * stub]
        wid = [hK + (hw - hK) * (t * t * (3 - 2 * t)) for t in tt] + [hw, hw]
        # the inner side narrows toward the wrist when the shaft is close
        shift = [n_th * (hw - hw_in) / 2 * (t * t * (3 - 2 * t)) for t in tt] + [n_th * (hw - hw_in) / 2] * 2
        wid = [w_ - (hw - hw_in) / 2 * (t * t * (3 - 2 * t)) for w_, t in zip(wid, list(tt) + [1.0, 1.0])]
        ds = [Point(*(q + s_)).buffer(max(rw, 0.5), quad_segs=16) for q, s_, rw in zip(cen_, shift, wid)]
        neck = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(ds[:-1], ds[1:])])
        neck = neck.intersection(halfplane(W + u * stub, W + u * stub + n_th, side=+1))
        # the heel: a smooth concave curve from the block's underside into the wrist, off the shaft
        x_h = max(x_min, min(x_kn - 0.42 * hb, Wb[0] - 2.0))
        H = _edge(P(x_h, y1), (1.0, 0.0), Wb, u, 16)
        clear = Polygon()
        if u[1] > -0.3:
            heel = Polygon([tuple(q) for q in list(H) + [W, Bs, P(x_h, y1 - 2.0)]]).buffer(0)
            neck = neck.union(heel)
            clear = Polygon([(-BIG, y1 + 0.4), (x_h, y1 + 0.4)] + [tuple(q) for q in H[1:]]
                            + [tuple(Wb + u * 400.0), (-BIG, BIG)]).buffer(0)
            trimmed = neck.difference(clear)
            if trimmed.geom_type == "Polygon" or not trimmed.is_empty:
                neck = max(_polys_of(trimmed), key=lambda g: g.area) if trimmed.geom_type != "Polygon" else trimmed
        # the thumb's root flows into the back of the hand: no notch between them
        root_join = shapely.union(Point(*Rc).buffer(rr, quad_segs=16),
                                  Point(*Bs).buffer(hK, quad_segs=16)).convex_hull
        root_join = root_join.intersection(shapely.box(x_kn - 0.30 * Lf, -BIG, BIG, BIG))
        hand_ = shapely.union_all([block, neck, thumb, root_join])
        # the heel's floor: nothing of the hand below the fingers comes within 7.3 px of the shaft
        floor = shapely.box(-BIG, y1 + 0.4, x_min, BIG) if u[1] > -0.3 else Polygon()
        if not floor.is_empty:
            hand_ = hand_.difference(floor)
            if hand_.geom_type != "Polygon":
                hand_ = max(_polys_of(hand_), key=lambda g: g.area)
        keep_out = shapely.box(-BIG, -BIG, x_kn - 0.30 * Lf, BIG).union(clear.buffer(0.3)).union(floor)
        hand_ = _junction_smooth(hand_, keep_out, r=0.20 * hb)
        hand_ = hand_.buffer(-1.2, quad_segs=8).buffer(1.2, quad_segs=8)
        if hand_.geom_type != "Polygon":
            hand_ = max(_polys_of(hand_), key=lambda g: g.area)
        inner = C.Frag()
        body = block.union(neck)
        for pts in _crease(thumb, body, keep=shapely.box(-BIG, -BIG, x_kn - 0.10 * Lf, BIG)):
            inner += line(C.polyline_d(pts), MEDIUM, role="thumb")
        inner += seg(cusps[1] + P(0.3, 0.0), P(x_tt + 0.4, y0 + p), MEDIUM, role="finger")
        ends = {2: 0.16, 3: 0.24} if view == "back" else {2: 0.30, 3: 0.34}
        for k in (2, 3):
            q0 = cusps[k] + P(0.3, 0.0)
            inner += line(arc_sag(q0, P(x_kn - ends[k] * Lf, q0[1]), -0.7), MEDIUM, role="finger")
        if view == "palm":
            # the fingertips curled back to the heel: tip lobes where the lines end
            xf = x_kn - max(ends.values()) * Lf - 0.8
            for k in (1, 2, 3):
                ya, yz = y0 + k * p + 0.4, y0 + (k + 1) * p - (0.4 if k < 3 else 3.2)
                inner += line(arc_sag(P(xf, ya), P(xf, yz), 0.26 * p), MEDIUM, role="fingertip")
        return hand_, inner, 2 * hw

    drawn = dorsal if view == "back" else ("R" if dorsal == "L" else "L")
    tipzone = _xf(shapely.box(-BIG, -BIG, -a + 1.0, BIG), M)       # the fingertip side of the shaft
    heelzone = _xf(shapely.box(a - 1.0, y1 - 1.0, BIG, BIG), M)     # below the fingers, knuckle side
    base_meta = {"kind": "fist", "hand": drawn, "view": view, "block_h": hb, "block_len": Lf, "wrist_off_deg": off}
    Ws = _xf(Point(*W), M)
    Ws = P(Ws.x, Ws.y)

    def place(u_local):
        hl, il, ww = build(u_local)
        hs, is_ = _xf(hl, M), il.transformed(Mf)
        meta = {**base_meta, "inner": is_, "rebuild": rebuild, "tipzone": tipzone, "heelzone": heelzone}
        return Part(hs, C.Frag(), outline(hs) + is_, meta), ww, _unit(_vec(M, _unit(u_local)))

    def _loc_vec(v):
        return _to_local(P(at) + P(v), at, rot, mir)

    def rebuild(u_screen):
        """the same hand with its wrist arriving along screen direction u_screen."""
        return place(_loc_vec(u_screen))[0]

    u0 = _loc_vec(arm) if arm is not None else chord
    part, ww, us = place(u0)
    return Hand(part, Part(_xf(thumb, M), C.Frag(), C.Frag(), {"merged": True}), Ws, ww, us, float(stub))


def clear_of_hand(holes, hand, *, gap=GAP_MARK):
    """Knockouts (paper bubbles, drops …) near a hand: each hole is kept only
    when it lies hidden under the hand (within its outline's half-width) or
    stands ≥ ``gap`` clear of the outline — a hole ON the contour reads as a
    stray paper crescent. ``holes``: a region (one polygon per hole) or a
    fill region with interior rings; ``hand``: a region (``Hand.hand.shape``).
    → the same kind of region with the offending holes filled back."""
    holes, hand = R(holes), R(hand)
    under = hand.buffer(MEDIUM / 2 - 0.3, quad_segs=8)

    def ok(g):
        return under.contains(g) or g.distance(hand) >= MEDIUM / 2 + gap

    if any(len(pg.interiors) for pg in _polys_of(holes)):
        return shapely.union_all([Polygon(pg.exterior, [r for r in pg.interiors if ok(Polygon(r))])
                                  for pg in _polys_of(holes)])
    kept = [g for g in _polys_of(holes) if ok(g)]
    return shapely.union_all(kept) if kept else Polygon()


def fist_geom(at, axis_deg=-90.0, *, shaft_w=22.0, back=+1, h=34.0, reach=7.0, knuckle=11.0):
    """The frame facts of ``fist(...)`` with these arguments (no drawing):
    block height ``hb``, length ``Lf``, the knuckle point ``kn`` and the
    back-of-hand mass ``Bs`` (screen points), the hand-axis unit ``axis``
    (from the fingertips toward the knuckles) and ``down`` (along the shaft
    toward its lower end). For placing wrists and cuffs."""
    a = shaft_w / 2.0
    hb = max(FIST_H_K * float(h), FIST_H_MIN)
    t_up = 0.20 * hb
    ytop = -(hb + t_up) / 2.0
    y0 = ytop + t_up
    y1 = y0 + hb
    yc = (y0 + y1) / 2
    tip_out = min(max(float(reach), 3.0), FIST_TIP_OUT)
    x_tip = -a - tip_out
    Lf = max(FIST_LEN_K * hb, 2 * a + tip_out + max(float(knuckle), 12.0))
    x_kn = x_tip + Lf
    rot = axis_deg + 90.0
    M, _ = _rigid(at, rot, mirror_x=back < 0)

    def S(q):
        g = _xf(Point(*q), M)
        return P(g.x, g.y)
    o = S(P(0.0, 0.0))
    return {"hb": hb, "Lf": Lf, "kn": S(P(x_kn, yc)), "Bs": S(P(x_kn - 0.20 * hb, yc + 0.03 * hb)),
            "axis": _unit(S(P(1.0, 0.0)) - o), "down": _unit(S(P(0.0, 1.0)) - o), "y1": y1, "a": a}


def fist_wrist(at, axis_deg=-90.0, *, bend=40.0, dist=1.0, shaft_w=22.0, back=+1, h=34.0, reach=7.0,
               knuckle=11.0):
    """Where a fist's wrist reads best: ``dist`` × the block height from the
    back-of-hand mass, ``bend``° off the hand axis toward the shaft's lower
    end (0 = straight out along the knuckles; ``fist`` warns past 65°).
    → screen point."""
    g = fist_geom(at, axis_deg, shaft_w=shaft_w, back=back, h=h, reach=reach, knuckle=knuckle)
    b = math.radians(bend)
    return g["Bs"] + g["hb"] * dist * (math.cos(b) * g["axis"] + math.sin(b) * g["down"])


CUP_K = {"kn": 0.14, "tip": 0.05, "curve": 0.45, "fw": 0.34, "w": (0.62, 0.52), "join": 5.0, "rc": -0.5,
         "root": (0.62, 0.12), "off": 0.10, "full": (0.16, 0.04)}


def cup(c, r, *, side=-1, wrist=None, wrist_w=24.0, grip=0.50, fw=None, thumb_w=None,
        thumb_from=72.0, thumb_to=30.0, knuckle=3.0, converge=0.80, stub=HAND_STUB) -> Hand:
    """A hand holding a sphere (orb, cone, bowl, lantern) from below, the back
    of the hand to the viewer (§H.0 mitten, 3 finger lines, separate thumb):

    * four fingers curl up over the sphere's lower front from a knuckle row
      just below it, each a rounded column whose tip sits on a curve that
      follows the sphere ≈ (grip − 0.05)·r below its centre, the columns
      converging (``converge``) as a hand closes round a ball;
    * three MEDIUM finger lines from the notches between the fingertips down
      the finger boundaries to the knuckles;
    * the back of the hand: tapered from the knuckle row to the wrist
      (≈ 0.7 × the knuckle breadth, never wider than ``wrist_w``), rounded,
      running ``stub`` px on into the sleeve (``Hand.add_to`` tucks it);
    * the THUMB rises from the back of the hand beside the index finger
      (its root merged, no line across it), crosses the sphere's wrist-side
      rim steeply near ``thumb_from``° below the equator (the contour passes
      behind it) and lies ON the sphere, tapering (``thumb_w`` ≈ its root
      width, default a finger's) to a rounded tip at ``thumb_to``° below the
      equator, its edge ≥ 4.2 px inside the rim — never along the rim.

    ``side`` −1: wrist toward the viewer's right; +1: toward the left (the
    thumb is on the wrist side). The best wrist is ≈ 1.3–1.5 r below the
    sphere's centre (further down makes a long bare back: move the cuff up
    the forearm). Returns a Hand."""
    c = P(c)
    fw = fw if fw is not None else r * CUP_K["fw"]
    sd = -1.0 if side < 0 else 1.0
    y_kn = r + max(float(knuckle), CUP_K["kn"] * r)
    g = max(0.12, float(grip) - CUP_K["tip"])
    xb = [(k - 1.5) * fw + sd * CUP_K["off"] * r for k in range(4)]    # finger bases (knuckles)
    xt = [x * converge for x in xb]                                    # tips close in round the ball
    top_y = [g * r + CUP_K["curve"] * x * x / r for x in xt]
    cols = [LineString([(x0 + (x0 - x1) * 0.3, y_kn + (y_kn - yt) * 0.3), (x1, yt)]).buffer(fw / 2, cap_style=1,
                                                                                          quad_segs=16)
            for x0, x1, yt in zip(xb, xt, top_y)]
    fingers = shapely.union_all(cols).intersection(shapely.box(-BIG, -BIG, BIG, y_kn + 1.0))
    # the wrist
    kc = P(np.mean(xb), y_kn)
    W = P(sd * r * 0.9, y_kn + 0.30 * r) if wrist is None else P(wrist) - c
    if W[1] > 1.62 * r + 22.0:
        _hand_warn(f"cup at ({c[0]:.0f}, {c[1]:.0f}): wrist {W[1]:.0f} px below the sphere centre "
                   f"(best ≈ {1.3 * r:.0f}–{1.5 * r:.0f}): a long back; move the cuff up")
    span = 4 * fw
    hw = min(float(wrist_w), 0.45 * span) / 2.0
    ts = -sd
    kk = 0 if ts < 0 else 3

    def build(u):
        u = _unit(u, (0.0, 1.0))
        n = np.array([u[1], -u[0]])
        Wl, Wr = (W + n * hw, W - n * hw) if (n[0] < 0) else (W - n * hw, W + n * hw)
        dl = _unit(P(xb[0] - xt[0], y_kn - top_y[0]))
        dr = _unit(P(xb[3] - xt[3], y_kn - top_y[3]))
        kl = P(xb[0], y_kn) - P(dl[1], -dl[0]) * (fw / 2)          # the columns' outer edges at the knuckles
        kr = P(xb[3], y_kn) + P(dr[1], -dr[0]) * (fw / 2)
        le = _edge(kl, dl, Wl, u)
        re_ = _edge(kr, dr, Wr, u)
        # a full, rounded back: the little-finger side swells (the hypothenar), the thumb side a little
        ctr_ = (kl + kr + Wl + Wr) / 4.0
        for pts_, full in ((le, CUP_K["full"][0 if ts > 0 else 1]), (re_, CUP_K["full"][1 if ts > 0 else 0])):
            ch = _unit(pts_[-1] - pts_[0])
            nn_ = np.array([-ch[1], ch[0]])
            if float(np.dot(nn_, (pts_[0] + pts_[-1]) / 2 - ctr_)) < 0:
                nn_ = -nn_
            tt_ = np.linspace(0.0, 1.0, len(pts_))[:, None]
            pts_ += nn_ * full * r * np.sin(np.pi * tt_)
        ring = ([P(xb[0], y_kn - 6.0)] + list(le) + [Wl + u * stub, Wr + u * stub] + list(re_[::-1])
                + [P(xb[3], y_kn - 6.0)])
        back_ = Polygon([tuple(q) for q in ring]).buffer(0)
        if back_.geom_type != "Polygon":
            back_ = max(_polys_of(back_), key=lambda gg: gg.area)
        # thumb: from the back of the hand beside the index finger up the sphere's
        # wrist-side rim, centred ON the rim (both its edges clear of the contour,
        # which passes behind it and leaves square from under the round tip)
        tw = float(thumb_w) if thumb_w is not None else fw
        w0, w1 = CUP_K["w"][0] * tw, CUP_K["w"][1] * tw                  # root / tip radius
        root = P(xb[kk] + ts * CUP_K["root"][0] * fw, y_kn + CUP_K["root"][1] * r)
        a_lo = 90 - ts * (90 - thumb_from)
        a_hi = 90 - ts * (90 - thumb_to)
        th = np.radians(np.linspace(a_lo, a_hi, 16))
        r_c = r + CUP_K["rc"]
        arc_pts = np.column_stack([r_c * np.cos(th), r_c * np.sin(th)])
        mid = (root + arc_pts[0]) / 2 + P(ts * 1.2, 0.0)
        cen = np.vstack([_qbez(root, mid, arc_pts[0], 8)[:-1], arc_pts])
        ws = np.linspace(w0, w1, len(cen))
        ds = [Point(*q).buffer(rw, quad_segs=12) for q, rw in zip(cen, ws)]
        thumb = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(ds[:-1], ds[1:])])
        # the web: the thumb's base flows into the back of the hand
        low = shapely.box(-BIG, arc_pts[0][1], BIG, BIG)
        web = shapely.union(thumb.intersection(low), back_.intersection(
            shapely.box(-BIG, -BIG, BIG, root[1] + 0.45 * r))).convex_hull
        back_ = back_.union(web.difference(fingers.buffer(-0.5).difference(back_)))
        hand_ = shapely.union_all([fingers, back_, thumb])
        tips = shapely.box(-BIG, -BIG, BIG, max(top_y) + 0.45 * fw)
        keep_out = tips.difference(thumb.buffer(3.0)).union(fingers.buffer(0.2).difference(back_.buffer(4.0)))
        hand_ = _junction_smooth(hand_, keep_out, r=CUP_K["join"])
        hand_ = hand_.buffer(-1.0, quad_segs=8).buffer(1.0, quad_segs=8)
        if hand_.geom_type != "Polygon":
            hand_ = max(_polys_of(hand_), key=lambda gg: gg.area)
        inner = C.Frag()
        for k in range(1, 4):
            ta, tb = P(xt[k - 1], top_y[k - 1]), P(xt[k], top_y[k])
            m = (ta + tb) / 2
            dd = float(np.hypot(*(tb - ta))) / 2
            rr_ = fw / 2
            up = math.sqrt(max(rr_ * rr_ - dd * dd, 0.0))
            nn = _unit(P(-(tb - ta)[1], (tb - ta)[0]))
            if nn[1] > 0:
                nn = -nn
            notch = m + nn * up
            base = P((xb[k - 1] + xb[k]) / 2, y_kn - 3.0 + (1.5 if k == 2 else 0.0))
            inner += seg(notch + _unit(base - notch) * 0.4, base, MEDIUM, role="finger")
        # where the thumb's base passes behind the index finger, the finger's edge is the line
        rz = Point(*root).buffer(0.30 * r)
        for pts in _crease(fingers, thumb.difference(rz).difference(back_.buffer(-3.0)), min_len=6.0):
            inner += line(C.polyline_d(pts), MEDIUM, role="thumb")
        body = fingers.union(back_)
        for pts in _crease(thumb.difference(fingers.buffer(0.3)).buffer(0), body.difference(fingers.buffer(0.3)),
                           keep=shapely.box(-BIG, -BIG, BIG, BIG).difference(rz), min_len=6.0):
            inner += line(C.polyline_d(pts), MEDIUM, role="thumb")
        return hand_, inner, thumb

    Mt = (1, 0, 0, 1, c[0], c[1])
    meta0 = {"kind": "cup"}

    def place(u):
        hl, il, tl = build(u)
        hs, is_ = _xf(hl, Mt), il.translate(c[0], c[1])
        return Part(hs, C.Frag(), outline(hs) + is_, {**meta0, "inner": is_, "rebuild": rebuild}), tl

    def rebuild(u_screen):
        return place(P(u_screen))[0]

    u0 = _unit(W - kc, (0.0, 1.0))
    part, tl = place(u0)
    return Hand(part, Part(_xf(tl, Mt), C.Frag(), C.Frag(), {"merged": True}), W + c, 2 * hw, u0, float(stub))


def flat(at, angle=0.0, *, side=-1, length=56.0, width=30.0, wrist_w=24.0, tips=(3.0, 0.0, 2.0, 7.0),
         knuckle=0.50, thumb_deg=24.0, thumb_len=0.44, taper=0.78, curl=0.0, stub=0.0) -> Hand:
    """A hand laid flat (on the chest, a bodice, a belt, a hilt), back to the
    viewer, from ``at`` (the wrist) pointing ``angle`` (screen degrees):

    * the back of the hand tapers from the knuckles (``knuckle`` × length
      along) to a wrist ``taper`` × ``width`` wide (never wider than
      ``wrist_w``), running ``stub`` px on behind ``at`` (tucked into a cuff
      by ``Hand.add_to``);
    * four finger columns side by side with rounded tips — ``tips``: how far
      each stops short of ``length`` (index, middle, ring, little, from the
      thumb side: the middle finger longest) — ``curl`` degrees bends them
      toward the little-finger side (a softly closing hand);
    * three MEDIUM finger lines from the notches between the tips back to
      the knuckles (staggered);
    * the THUMB rooted in the back of the hand by the wrist (no line across
      its root), diverging ``thumb_deg``° from the index edge with a web
      notch between them, tapering to a rounded tip, ``thumb_len`` × length
      long; ``side`` −1 puts it on the screen-left of the pointing direction.
    Returns a Hand."""
    L = float(length)
    hw = width / 2.0
    fw = width / 4.0
    ts = -1.0 if side < 0 else 1.0                 # local y of the thumb side
    xk = L * knuckle
    ww = min(float(wrist_w), taper * width) / 2.0
    back_ = Polygon([(-stub, -ww), (0.0, -ww), (xk, -hw + 0.6), (xk, hw - 0.6), (0.0, ww), (-stub, ww)])
    back_ = back_.buffer(3.0, quad_segs=10).buffer(-3.0, quad_segs=10)
    caps, tip_c = [], []
    for k in range(4):
        yk = ts * (hw - fw / 2) - ts * k * fw
        x_end = L - tips[k] - fw / 2
        bend = math.radians(curl * (k / 3.0))
        p1 = P(x_end, yk - ts * (x_end - xk) * math.sin(bend) * 0.5)
        caps.append(LineString([(xk - 3.0, yk), tuple(p1)]).buffer(fw / 2 + 0.3, quad_segs=16))
        tip_c.append(p1)
    fingers = shapely.union_all(caps)
    # thumb
    root = P(L * 0.14, ts * (ww - 2.5))
    a = math.radians(thumb_deg)
    d = P(math.cos(a), ts * math.sin(a))
    Lt = L * thumb_len
    cen = np.array([root + d * Lt * t for t in np.linspace(0.0, 1.0, 12)])
    cen[:, 1] += ts * 1.2 * np.sin(np.linspace(0.0, math.pi, 12))          # a slight outward arc
    ws = np.linspace(0.22 * width, 0.16 * width, len(cen))
    ds = [Point(*q).buffer(rw, quad_segs=12) for q, rw in zip(cen, ws)]
    thumb = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(ds[:-1], ds[1:])])
    body = fingers.union(back_)
    hand_ = shapely.union_all([body, thumb])
    tipz = shapely.box(xk + 2.0, -BIG, BIG, BIG)
    hand_ = _junction_smooth(hand_, tipz.union(thumb.difference(Point(*root).buffer(0.30 * width))), r=2.4)
    hand_ = hand_.buffer(-0.8, quad_segs=8).buffer(0.8, quad_segs=8)
    if hand_.geom_type != "Polygon":
        hand_ = max(_polys_of(hand_), key=lambda gg: gg.area)
    inner = C.Frag()
    for k in range(1, 4):
        ta, tb = tip_c[k - 1], tip_c[k]
        m = (ta + tb) / 2
        dd = float(np.hypot(*(tb - ta))) / 2
        rr_ = fw / 2 + 0.3
        ahead = math.sqrt(max(rr_ * rr_ - dd * dd, 0.0))
        notch = m + P(ahead, 0.0)
        # the notch is where the two tip circles meet; start the line just inside it
        q0 = notch - P(0.6, 0.0)
        q1 = P(xk + 1.5 + (2.0 if k == 2 else 0.0), m[1])
        if q0[0] - q1[0] > 6.0:
            inner += seg(q0, q1, MEDIUM, role="finger")
    for pts in _crease(thumb, body, keep=body.difference(Point(*root).buffer(0.34 * width))):
        inner += line(C.polyline_d(pts), MEDIUM, role="thumb")
    M, Mf = _rigid(at, angle, mirror_x=False)
    hand_s = _xf(hand_, M)
    inner_s = inner.transformed(Mf)
    u = _unit(_vec(M, P(-1.0, 0.0)))
    meta = {"kind": "flat", "inner": inner_s}
    return Hand(Part(hand_s, C.Frag(), outline(hand_s) + inner_s, meta),
                Part(_xf(thumb, M), C.Frag(), C.Frag(), {"merged": True}), P(at), 2 * ww, u, float(stub))


# =============================================================================
# 8  garments
# =============================================================================
@dataclass
class MantleSpec:
    """The mantle's outline, a tangent arc chain from the neck: a shoulder
    arc sloping down, a straight run, the shoulder corner, the side falling
    to the band. §H.0: shoulders ≈ 330 at x ≈ 180/570."""
    cx: float = AX
    neck_y: float = 282.0          # top of the mantle on the axis
    neck_heading: float = 173.0    # leaving the axis (180 = level; <180 slopes down)
    yoke_r: float = 380.0
    yoke_sweep: float = 8.0
    run: float = 125.0
    corner_r: float = 34.0
    side_heading: float = 96.0     # after the corner (90 = plumb; >90 flares out)
    bottom: float = 545.0


def mantle_outline(s: MantleSpec = MantleSpec()):
    """Left half of the mantle outline (points, from the axis at the neck to
    the band)."""
    t = C.Turtle(s.cx, s.neck_y, s.neck_heading)
    t.arc(s.yoke_r, -s.yoke_sweep)
    t.fd(s.run)
    t.arc(s.corner_r, -(s.neck_heading - s.yoke_sweep - s.side_heading))
    y0 = t.pos[1]
    L = (s.bottom - y0) / math.sin(math.radians(t.heading))
    t.fd(L)
    return np.asarray(t.pts(0.5)[0])


def mantle(s: MantleSpec = MantleSpec(), *, color=JADE, border=16.0, seam=True, pattern_kind=None,
           **pattern_kw) -> Part:
    """The mantle: a bilateral region (left half mirrored) filled ``color``.
    With ``border`` a plain band of that width runs inside the whole outer
    edge, closed by a FINE seam (the exact parallel of the silhouette, ≥ 4.2
    clear of its CONTOUR), and the house pattern (``pattern_kind``: see
    ``pattern``) fills the inside — so no pattern line ever grazes a sloping
    silhouette. meta: 'inner' (the patterned region), 'half' (left points)."""
    pts = mantle_outline(s)
    left = np.vstack([pts, [[s.cx, s.bottom]]])
    half = Polygon(left).buffer(0)
    shape = U(half, mirror(half, s.cx))
    lines = outline(shape)
    # the border runs along the silhouette only, never along the (clipped)
    # bottom edge: inset a copy of the outline extended far below the band
    ext = np.vstack([pts, [[pts[-1][0] + (pts[-1][0] - pts[-2][0]) / max(pts[-1][1] - pts[-2][1], 1e-6) * 300.0,
                            s.bottom + 300.0], [s.cx, s.bottom + 300.0]]])
    ext_half = Polygon(ext).buffer(0)
    ext_shape = U(ext_half, mirror(ext_half, s.cx))
    inner = ext_shape.buffer(-border, quad_segs=16).intersection(box(0, 0, 2000, s.bottom + 20)) if border else shape
    if border and seam:
        lines += C.stroke(D(inner), FINE, role="seam")
    if pattern_kind:
        lines += pattern(inner, pattern_kind, **pattern_kw)
    return Part(shape, fill(shape, color), lines, {"inner": inner, "half": pts})


@dataclass
class LensSpec:
    """The Spring Lake lens tunic: a vesica whose tips are the throat and its
    180° image, so it is two-headed by construction."""
    cx: float = AX
    throat_y: float = 312.0
    half_w: float = 31.0        # half-width at the card centre (y 525)
    lapel_w: float = 58.0       # lapel band width at the waist


def lens(s: LensSpec = LensSpec()):
    h = T.CY - s.throat_y
    Rr = (h * h + s.half_w ** 2) / (2 * s.half_w)
    cL = P(s.cx - s.half_w + Rr, T.CY)
    cR = P(s.cx + s.half_w - Rr, T.CY)
    return {"R": Rr, "cL": cL, "cR": cR, "top": P(s.cx, s.throat_y)}


def tunic(s: LensSpec = LensSpec(), *, pattern_kind="karst_flooded", clear_below=None, **kw) -> Part:
    """The lens tunic (paper), patterned (default: §G.12 karst voids whose
    largest cavities are flooded jade — the aquifer). ``clear_below``: keep
    the pattern above this y (the band / medallion)."""
    g = lens(s)
    reg = R(circle(g["cL"], g["R"])).intersection(R(circle(g["cR"], g["R"])))
    reg = reg.intersection(box(0, 0, 750, 545))
    lines = outline(reg)
    fills = C.Frag()
    if pattern_kind:
        prg = reg.buffer(-(MEDIUM / 2 + 3.2))
        yb = (T.BAND_Y0 - 0.55 - 3.2) if clear_below is None else clear_below
        prg = prg.intersection(box(0, 0, 750, yb))
        pf = pattern(prg, pattern_kind, origin=(s.cx, s.throat_y + 22.0), **kw)
        fills += pf.select(lambda m: m.kind == "fill" and m.layer != "ink")
        lines += pf.select(lambda m: not (m.kind == "fill" and m.layer != "ink"))
    return Part(reg, fills, lines, g)


def lapel(s: LensSpec = LensSpec(), side=-1, mantle_shape=None, *, shoulder_x=276.0, collar_sag=-6.0,
          bubbles=True, bub_top=370.0, bub_bottom=530.0, bub_max=12.6, color=RED) -> Part:
    """A lapel (the collar lining turned back, §H.1 'Collar lining: Gill
    Red'): the band between the lens arc and an outer arc from the shoulder
    (x ``shoulder_x`` on the mantle's top) to the lens offset ``lapel_w`` at
    the band — a shawl collar, broad at the shoulder. With ``bubbles`` a
    column of rising bubbles (§G.9, Ø4.2 → 12.6, ×1.16) is knocked out of the
    red on its mid-line."""
    g = lens(s)
    c, Rr = g["cL"], g["R"]
    yb = 545.0
    xb = c[0] - math.sqrt((Rr + s.lapel_w) ** 2 - (yb - T.CY) ** 2)
    B_o = P(xb, yb)
    ms = mantle_shape if mantle_shape is not None else mantle().shape
    col = ms.intersection(LineString([(shoulder_x, 0), (shoulder_x, 700)]))
    S_o = P(shoulder_x, col.bounds[1])
    oc, orad = sag_centre(S_o, B_o, collar_sag)
    reg = (ms.intersection(R(circle(oc, orad))).difference(R(circle(c, Rr)))
           .intersection(box(0, 0, s.cx, 545)))
    fill_d = D(reg)
    if bubbles:
        rm = Rr + s.lapel_w / 2
        a_bot = ang(c, (c[0] - math.sqrt(rm ** 2 - (bub_bottom - T.CY) ** 2), bub_bottom))
        a_top = unwrap(a_bot, ang(c, (c[0] - math.sqrt(rm ** 2 - (bub_top - T.CY) ** 2), bub_top)), cw=True)
        th = np.radians(np.linspace(a_bot, a_top, 200))
        path = np.column_stack([c[0] + rm * np.cos(th), c[1] + rm * np.sin(th)])
        bf = C.bubble_path(path, 4.2, ratio=1.16, gap=None, style="dot", d_max=bub_max)
        fill_d = C.knockout(fill_d, bf)
    part = Part(reg, fill(fill_d, color), outline(reg),
                {"c": c, "R": Rr, "outer_c": oc, "outer_r": orad, "S_o": S_o, "B_o": B_o})
    return part.mirrored(s.cx) if side > 0 else part


@dataclass
class SleeveSpec:
    base: tuple = (232.0, 545.0)   # sleeve centre where it leaves the band
    wrist: tuple = (276.0, 462.0)  # wrist centre (cuff top)
    sag: float = -10.0             # guide-arc bulge (negative: right of travel)
    width: float = 52.0            # at the base
    wrist_w: float = 34.0          # at the wrist
    cuff: float = 12.0             # cuff band depth
    folds: int = 1                 # MEDIUM fold lines along the sleeve (edge to edge, no free ends)
    color: str = JADE
    cuff_color: str = RED


def sleeve(s: SleeveSpec = SleeveSpec()):
    """A forearm sleeve from the band up to the wrist, plus its cuff. The two
    long edges are arcs of the guide's sagitta; the cuff is a band between
    two short arcs; ``folds`` MEDIUM lines run along the sleeve from the
    band to the cuff (both ends butt, so no free ends). → (sleeve, cuff)."""
    B, W = P(s.base), P(s.wrist)
    u = (W - B) / np.hypot(*(W - B))
    n = np.array([u[1], -u[0]])
    bl, br = B + n * s.width / 2, B - n * s.width / 2
    wl, wr = W + n * s.wrist_w / 2, W - n * s.wrist_w / 2
    body = Path(bl).sag(wl, s.sag).line(wr).sag(br, -s.sag).close()
    shape = R(body.d)
    cw_l, cw_r = wl - u * s.cuff, wr - u * s.cuff
    cuff_d = Path(wl).sag(wr, -2.5).line(cw_r).sag(cw_l, 2.5).close().d
    cuff = R(cuff_d)
    lines = outline(body.d)
    for k in range(1, s.folds + 1):
        t = k / (s.folds + 1)
        f0 = bl + (br - bl) * (0.30 + 0.25 * t)
        f1 = cw_l + (cw_r - cw_l) * (0.30 + 0.25 * t)
        fd = arc_sag(f0 - u * 20.0, f1 + u * 2.0, s.sag * 0.55)
        lines += clip_in(line(fd, MEDIUM, role="fold"), shape.difference(cuff.buffer(0.5)))
    sl = Part(shape, fill(shape, s.color), lines, {"W": W, "u": u, "n": n})
    cf = Part(cuff, fill(cuff, s.cuff_color), outline(cuff_d), {})
    return sl, cf


def standing_collar(cx=AX, *, top_y=240.0, half_w=106.0, neck_y=268.0, shoulder=(-150.0, 318.0), top_sag=7.0,
                    side_sag=-6.0, rim=8.0, depth=120.0, color=RED, rim_color=JADE) -> Part:
    """A standing fan collar rising behind the head: its inner face is the
    Gill Red LINING (§H.1 'Collar lining: Gill Red'), its top edge turned
    over as a jade rim (the mantle cloth). Compass-built, left half mirrored:
    the top edge is an arc from the neck (``neck_y`` on the axis, hidden by
    the head) rising to a POINTED corner (cx − ``half_w``, ``top_y``) — never
    round, so it cannot read as a nimbus — and the outer edge an arc down to
    the ``shoulder`` point (dx, y). Keep ``top_y`` below the eye line and the
    corners well inside the crown's width; put it BEHIND the mantle (its foot
    hides under the mantle's neckline) and behind the hair. → Part (meta 'rim')."""
    A = P(cx, neck_y)
    Cn = P(cx - half_w, top_y)
    Sh = P(cx + shoulder[0], shoulder[1])
    top = Path(A).sag(Cn, top_sag)
    half_d = top.sag(Sh, side_sag).line((Sh[0], Sh[1] + depth)).line((cx, Sh[1] + depth)).close().d
    half = R(half_d)
    shape = U(half, mirror(half, cx))
    edge = C.sample_d(arc_sag(A, Cn, top_sag), 0.3)[0][0]
    edge = np.vstack([edge, [Cn + (Cn - edge[-2]) / np.hypot(*(Cn - edge[-2])) * 30.0]])
    band = LineString(edge).buffer(rim, cap_style=2, quad_segs=12).intersection(half)
    band = U(band, mirror(band, cx)).intersection(shape)
    body = shape.difference(band)
    fills = fill(body, color) + fill(band, rim_color)
    lines = outline(shape)
    fold = R(band).buffer(0).boundary.intersection(shape.buffer(-0.6))
    for ln in _lines_of(shapely.line_merge(fold) if fold.geom_type != "LineString" else fold):
        if ln.length > 4:
            lines += line(np.asarray(ln.coords), MEDIUM, role="fold")
    return Part(shape, fills, lines, {"rim": band, "corner": Cn})


def torso(cx=AX, *, neck_y=300.0, neck_hw=26.0, shoulder=(170.0, 330.0), corner_r=26.0, side_x=None,
          bottom=545.0, turn=0, neck_depth=18.0, color=JADE, pattern_kind=None, border=0.0, **pattern_kw) -> Part:
    """A generic bust garment — doublet, bodice, gown, tabard — as a closed
    compass-built region: a neckline (a shallow U, ``neck_hw`` half-wide,
    ``neck_depth`` deep, sitting at ``neck_y``), shoulders sloping to the
    ``shoulder`` corner (half-width, y), rounded (``corner_r``), sides falling
    to ``side_x`` half-width at ``bottom`` (default: plumb). ``turn`` ±1 (a 3/4
    figure) moves the neckline 12 % of the shoulder span toward the turn and
    narrows the far shoulder by 14 % — the body turns with the head. Filled
    ``color``; ``pattern_kind`` (see ``pattern``) fills it inside an optional
    plain ``border``. → Part (meta 'inner', 'neck')."""
    hw, sy = shoulder
    sx = hw if side_x is None else side_x
    shift = turn * 0.12 * hw
    halves = []
    for sg in (-1, 1):
        k = 0.86 if (turn and sg == turn) else 1.0
        n0 = P(cx + shift + sg * neck_hw, neck_y)
        sh = P(cx + shift * 0.5 + sg * hw * k, sy)
        b = P(cx + shift * 0.3 + sg * sx * k, bottom)
        poly = Polygon([(cx + shift, neck_y + neck_depth), tuple(n0), tuple(sh), tuple(b),
                        (cx + shift * 0.3, bottom)]).buffer(0)
        halves.append(poly)
    body = U(*halves)
    # round the shoulder corners only (open-close by the corner radius)
    rounded = body.buffer(-corner_r, join_style=1).buffer(corner_r, join_style=1)
    top_band = box(0, 0, 2000, neck_y + neck_depth + 2)
    shape = U(rounded, body.intersection(top_band)).buffer(0)
    neck = LineString([(cx + shift - neck_hw - 2, neck_y), (cx + shift, neck_y + neck_depth),
                       (cx + shift + neck_hw + 2, neck_y)])
    lines = outline(shape)
    inner = shape.buffer(-border, quad_segs=12) if border else shape
    fills = fill(shape, color)
    if pattern_kind:
        pf = pattern(inner, pattern_kind, **pattern_kw)
        fills += pf.select(lambda m: m.kind == "fill" and m.layer != "ink")
        lines += pf.select(lambda m: not (m.kind == "fill" and m.layer != "ink"))
        if border:
            lines += C.stroke(D(inner), FINE, role="seam")
    return Part(shape, fills, lines, {"inner": inner, "neck": neck, "shift": shift})


def cap(fc: "Face", *, kind="flat", color=RED, band=7.0, rise=20.0, over=12.0, drop=0.42, cape=70.0) -> Part:
    """Headwear resting on a face (``fc`` from ``face``). Put it IN FRONT of
    the head and hair.

    'flat'  a flat cap: a band ``band`` px deep across the forehead (its lower
            edge ``drop`` × r above the egg centre) under a flat lens-shaped
            crown ``rise`` px tall that overhangs ``over`` px toward the face
            (a 3/4 or profile head's turn) — J♦'s flat red cap;
    'hood'  (profiles, 3/4) the skull plus 10 px, the face opening an arc
            from the forehead behind the eye to under the chin (the ear is
            covered), falling as a short cape to ``cape`` px below the chin
            over the shoulders; a MEDIUM crown seam — J♠'s red hood.
    → Part (meta 'band_y' / 'seam')."""
    a = fc.anchors
    cx, cy = a["center"]
    r = a["r"]
    facing = a.get("facing", 0) or a.get("turn", 0)
    if kind == "flat":
        yb = cy - r * drop
        xl = cx - r - 2.0 - (over if facing < 0 else 3.0)
        xr = cx + r + 2.0 + (over if facing > 0 else 3.0)
        if facing == 0:
            xl, xr = cx - r - over * 0.5, cx + r + over * 0.5
        b0, b1 = P(xl + 6.0, yb), P(xr - 6.0, yb)
        band_d = Path(b0).line(b1).line(b1 + P(1.0, -band)).line(b0 + P(-1.0, -band)).close().d
        crown_d = Path(P(xl, yb - band)).sag(P(xr, yb - band), rise).line(P(xl, yb - band)).close().d
        shape = U(R(band_d), R(crown_d)).buffer(2.0, join_style=1).buffer(-2.0, join_style=1)
        lines = outline(shape)
        edge = LineString([(xl - 20, yb - band), (xr + 20, yb - band)]).intersection(shape.buffer(-0.6))
        for ln in _lines_of(edge):
            lines += line(np.asarray(ln.coords), MEDIUM, role="cap-band")
        return Part(shape, fill(shape, color), lines, {"band_y": yb})
    # hood, built facing LEFT (sd = +1 mirrors to facing right)
    sd = 1.0 if facing > 0 else -1.0

    def X(dx):                      # dx measured toward the BACK of the head
        return cx - sd * dx
    fr = -r * 0.84
    ey, my = a["eye_y"], a["mouth_y"]
    oc = P(X(-4.0), cy - 2.0)
    Ro = r + 10.0
    Fp = P(X(fr + 20.0), cy - r * 0.62)                      # forehead: the opening's top
    pts = []
    th = np.radians(np.linspace(222.0, 355.0, 80) if sd < 0 else np.linspace(-42.0, -175.0, 80))   # no beak
    for t in th:
        pts.append((oc[0] + Ro * math.cos(t), oc[1] + Ro * math.sin(t)))
    back = P(X(r + 14.0), cy + r * 0.5)
    cape_b = P(X(r + 34.0), a["chin"][1] + cape)
    cape_f = P(X(fr + 2.0), a["chin"][1] + cape)
    chin_p = P(X(fr + 24.0), a["chin"][1] + 12.0)
    cheek = P(X(fr + 40.0), ey + 10.0)                       # behind the eye, over the ear
    poly = Polygon(pts + [tuple(back), tuple(cape_b), tuple(cape_f), tuple(chin_p), tuple(cheek), tuple(Fp)])
    shape = poly.buffer(5.0, join_style=1).buffer(-5.0, join_style=1).buffer(0)
    seam = C.sample_d(arc_c(oc, Ro - 13.0, 215 if sd < 0 else -35, 300 if sd < 0 else -120)
                      if sd < 0 else arc_c(oc, Ro - 13.0, -120, -35), 0.4)[0][0]
    lines = outline(shape) + clip_in(line(C.polyline_d(seam), MEDIUM, role="seam"), shape.buffer(-6.0))
    return Part(shape, fill(shape, color), lines, {"seam": seam})


# =============================================================================
# 9  crowns and regalia
# =============================================================================
def _ray_x(v, deg, y):
    """x where the ray from vanishing point v at ``deg`` from the vertical
    (negative = left) meets the line y."""
    return v[0] + math.tan(math.radians(deg)) * (v[1] - y)


def crown_band(cx, top, h, hw, bow=4.0, v=None, edge_deg=None):
    """The crown base for every court: a gold band between two parallel arcs
    (seen slightly from above it dips ``bow`` at the centre). With a
    vanishing point ``v`` and ``edge_deg`` its ends are rays from v, so they
    continue a flared crown's outer edges. → (region, d)."""
    y0, y1 = top - bow, top + h - bow
    if v is not None:
        xl0, xl1 = _ray_x(v, -edge_deg, y0), _ray_x(v, -edge_deg, y1)
    else:
        xl0 = xl1 = cx - hw
    a0, a1 = P(xl0, y0), P(2 * cx - xl0, y0)
    b0, b1 = P(xl1, y1), P(2 * cx - xl1, y1)
    d = Path(a0).arc3((cx, top), a1).line(b1).arc3((cx, top + h), b0).close().d
    return R(d), d


def diadem(cx=AX, y=165.0, hw=46.0, *, h=11.0, kind="stalactite", n=9, lengths=(26.0, 14.0), widths=(11.0, 8.0),
           bow=5.0, color=GOLD, jewel_r=0.0, turn=0, axis=None, fc: "Face | None" = None) -> Part:
    """A queen's / page's circlet: a gold band (``crown_band``, ``h`` tall,
    dipping ``bow`` at the centre) with ``n`` graduated elements, largest at
    the centre:

      'stalactite'  kites HANGING below the band (§G.13: Q♠'s stalactite
                    diadem), each an outline with its axis joint;
      'point'       kites standing ON the band (a coronet);
      'knee'        §G.17 cypress knees on the band (K♣'s knee crown);
      'bead'        Ø 8.4 → 6.3 gold beads on the band (pearl beading, §G.29).

    ``lengths``/``widths`` = (centre, ends). ``turn`` ±1 compresses the far
    half by 20 % (a 3/4 head). Mirror-symmetric when turn = 0.
    ``fc`` (a Face): the band runs from one side of that head to the other
    at height ``y`` (``cx``/``hw`` are then derived) and the elements centre
    on its feature axis (``axis``), so a 3/4 circlet wraps the head. → Part."""
    if fc is not None:
        a_ = fc.anchors
        yy = y + h / 2
        xl, xr = a_["side_x"](yy, -1) - 2.0, a_["side_x"](yy, +1) + 2.0
        cx, hw = (xl + xr) / 2, (xr - xl) / 2
        turn = a_.get("turn", 0)
        axis = float(a_["axis"]) if axis is None else axis
    ax_ = cx if axis is None else axis
    band, band_d = crown_band(cx, y, h, hw, bow)
    els = []
    lines = C.Frag()
    xs = np.linspace(-1.0, 1.0, n)
    # each side of the feature axis spans to its own end of the band (a 3/4
    # circlet is foreshortened on the far side by construction); elements
    # never crowd: each keeps 3 px + its outline from the next
    x_lo, x_hi = cx - hw, cx + hw
    half_n = max((n - 1) / 2, 1)
    pitch = min(ax_ - x_lo, x_hi - ax_) / half_n * 0.86
    wmax = pitch - GAP_MARK - MEDIUM
    widths = (min(widths[0], wmax), min(widths[1], wmax))
    for t in xs:
        k = 1.0 - abs(t)
        L = lengths[1] + (lengths[0] - lengths[1]) * k
        W = widths[1] + (widths[0] - widths[1]) * k
        span = ((x_hi - ax_) if t > 0 else (ax_ - x_lo)) - W / 2 - 4.0
        x = ax_ + t * span
        yb = y - bow * t * t                 # the band dips ``bow`` at the centre (seen from above)
        if kind == "stalactite":
            top = yb + h - 1.0
            kite = Polygon([(x, top - 1.0), (x + W / 2, top + 0.2 * L), (x, top + L), (x - W / 2, top + 0.2 * L)])
            els.append(kite)
            lines += seg(P(x, top + 0.2 * L + 3.0), P(x, top + L - 5.0), FINE, style="point", role="axis")
        elif kind == "point":
            # a pointed arch standing on the band: full width at the band's
            # top edge, two convex arcs to the tip (a stalactite reversed)
            base = yb + 2.0
            pa = Path((x - W / 2, base)).sag((x, base - L), -W * 0.12).sag((x + W / 2, base), -W * 0.12).close()
            els.append(R(pa.d))
        elif kind == "knee":
            els.append(R(MG.cypress_knee(x, yb + 1.0, L, base_w=W * 1.6).outline()))
        else:
            els.append(Point(x, yb - 3.0).buffer(W / 2 * 0.6 + 1.0, quad_segs=16))
    stone = U(*els)
    shape = U(band, stone)
    lines = clip_out(outline(stone), band, eps=-0.8, trap=0.0) + outline(band_d) + clip_out(
        lines.select(lambda m: m.role == "axis"), band.buffer(3.2), eps=0.0, trap=0.0)
    fills = fill(shape, color)
    if jewel_r:
        jw = jewel((cx, y + h / 2 - bow), jewel_r)
        lines = clip_out(lines, jw.shape, eps=0.0, trap=0.0, extra=jw.shape.buffer(4.3 + MEDIUM))
        return Part(shape.union(jw.shape), fills + jw.fills, lines + jw.lines, {"band": band})
    return Part(shape, fills, lines, {"band": band})


def jewel(c, r=13.0, ribs=8, centre=RED, centre_d=8.4) -> Part:
    """A small Source Rosette jewel (§G.1 reduced, straight ribs so it is
    mirror-symmetric): a gold disc, ``ribs`` FINE Aquifer ribs from the rim
    toward a Gill Red Ø8.4 centre CUT INTO the gold (the layer trap, §2.1)."""
    c = P(c)
    disc = R(circle(c, r))
    lines = outline(circle(c, r))
    r_in = centre_d / 2 + 3.0 + FINE / 2
    for k in range(ribs):
        a = -90 + 360 * k / ribs + 180 / ribs
        lines += seg(polar(c, r, a), polar(c, r_in, a), FINE, role="rib")
    fills = fill(disc, GOLD) + (dot(c, centre_d, centre) if centre else C.Frag())
    return Part(disc, fills, lines, {})


@dataclass
class CrownSpec:
    """Merlon crown (the K♠ Escarpment Crown by default). Merlon edges are
    rays from one vanishing point, so the crown flares; tops step up in
    fault-steps to the centre. Re-parameterise for fewer merlons, a flat
    parapet, a different flare."""
    cx: float = AX
    band_top: float = 158.0
    band_h: float = 22.0
    band_hw: float = 68.0
    band_bow: float = 4.0
    vanish: tuple = (AX, 700.0)
    edges: tuple = (7.315, 5.36, 4.243, 2.27, 1.146)   # left half: outer merlon, crenel, middle, crenel, centre (deg)
    tops: tuple = (128.0, 105.0, 82.0)                 # outer, middle, centre merlon tops
    crenel_depth: float = 12.0
    jewel_r: float = 13.0
    studs: tuple = (26.0, 44.0)
    hatch: bool = True


def merlon_hatch(k, a, b, t, v, band_top, band, nmerl):
    """Half-hatch of merlon k (edges at ray angles a < b, top t). Side
    merlons: the outer half hatched 45° (split on the merlon's mid-ray by a
    FINE joint). The CENTRE merlon: split into two courses by a FINE bedding
    line; the LOWER course is split on the axis by a FINE joint and hatched
    mirror-wise at ±45° — half-hatched at 45° AND mirror-symmetric (a single
    45° hatch cannot be both)."""
    f = C.Frag()

    def wedge(a_, b_, top_, bottom_):
        return Polygon([(_ray_x(v, a_, top_), top_), (_ray_x(v, b_, top_), top_),
                        (_ray_x(v, b_, bottom_), bottom_), (_ray_x(v, a_, bottom_), bottom_)])
    mid = (a + b) / 2
    centre = nmerl // 2
    if k != centre:
        left = k < centre
        half = wedge(a, mid, t, band_top + 2) if left else wedge(mid, b, t, band_top + 2)
        half = half.difference(band)
        org = (_ray_x(v, a if left else b, t), t)
        f += hatch_in(half, angle=-45.0 if left else -135.0, origin=org)
        seg_ = LineString([(_ray_x(v, mid, t), t), (_ray_x(v, mid, band_top + 8), band_top + 8)]).difference(band)
        for ln in _lines_of(seg_):
            f += line(np.asarray(ln.coords), FINE, role="joint")
        return f
    ym = t + (band_top - t) * 0.46
    xa, xb = _ray_x(v, a, ym), _ray_x(v, b, ym)
    f += seg(P(xa, ym), P(xb, ym), FINE, style="rule", role="bed")
    cx = v[0]
    lo = wedge(a, b, ym, band_top + 2).difference(band)
    lh = lo.intersection(box(0, 0, cx, 1000))
    rh = lo.intersection(box(cx, 0, 2000, 1000))
    f += hatch_in(lh, angle=-45.0, origin=(cx, ym))
    f += hatch_in(rh, angle=-135.0, origin=(cx, ym))
    seg_ = LineString([(cx, ym), (cx, band_top + 8)]).difference(band)
    for ln in _lines_of(seg_):
        f += line(np.asarray(ln.coords), FINE, role="joint")
    return f


def merlon_crown(s: CrownSpec = CrownSpec()) -> Part:
    """The merlon crown: a gold band (``crown_band``) carrying five gold
    merlons on rays from one vanishing point, tops rising in three
    fault-steps to the centre (§H.1 Escarpment Crown); MEDIUM joints under
    the crenels; each merlon half-hatched (``merlon_hatch``); a Source
    Rosette ``jewel`` on the band with the crown's lines breaking 3 px clear
    of it; stud dots either side. Exactly mirror-symmetric."""
    cx = s.cx
    v = P(s.vanish)
    band, band_d = crown_band(cx, s.band_top, s.band_h, s.band_hw, s.band_bow, v=v, edge_deg=s.edges[0])
    e = s.edges
    Lm = [(-e[0], -e[1], s.tops[0]), (-e[2], -e[3], s.tops[1])]
    Cm = (-e[4], e[4], s.tops[2])
    merl = Lm + [Cm] + [(-bb, -aa, t) for (aa, bb, t) in reversed(Lm)]
    base = s.band_top + 8.0

    def wedge(a, b, t, bottom=base):
        return Polygon([(_ray_x(v, a, t), t), (_ray_x(v, b, t), t),
                        (_ray_x(v, b, bottom), bottom), (_ray_x(v, a, bottom), bottom)])
    blocks = [wedge(a, b, t) for (a, b, t) in merl]
    walls = []
    for k in range(len(merl) - 1):
        a = merl[k][1]
        b = merl[k + 1][0]
        t = max(merl[k][2], merl[k + 1][2]) + s.crenel_depth
        walls.append(wedge(a - 0.3, b + 0.3, t))
    stone = U(*blocks, *walls)
    above_band = box(0, 0, 750, 400).difference(band.union(box(0, s.band_top + s.band_h - s.band_bow, 750, 400)))
    stone = stone.intersection(above_band.buffer(1.6))
    shape = U(stone, band)
    fills = fill(band, GOLD) + fill(stone, GOLD)
    lines = C.Frag()
    for k in range(len(merl) - 1):
        a = merl[k][1]
        b = merl[k + 1][0]
        t = max(merl[k][2], merl[k + 1][2]) + s.crenel_depth
        mid = (a + b) / 2
        sg = LineString([(_ray_x(v, mid, t), t), (_ray_x(v, mid, base), base)]).difference(band)
        for ln in _lines_of(sg):
            lines += line(np.asarray(ln.coords), MEDIUM, role="joint")
    if s.hatch:
        for k, (a, b, t) in enumerate(merl):
            lines += merlon_hatch(k, a, b, t, v, s.band_top, band, len(merl))
    lines += clip_out(outline(stone), band, eps=-0.8, trap=0.0)
    lines += outline(band_d)
    jy = s.band_top + s.band_h / 2
    jw = jewel((cx, jy), s.jewel_r)
    lines = clip_out(lines, jw.shape, eps=0.0, trap=0.0, extra=jw.shape.buffer(4.3 + MEDIUM))
    studs = C.Frag()
    for dx in s.studs:
        for sg in (-1, 1):
            yy = s.band_top + s.band_h / 2 - s.band_bow * (1 - (dx / s.band_hw) ** 2)
            studs += dot((cx + sg * dx, yy), 6.3)
    return Part(shape.union(jw.shape), fills + jw.fills, lines + studs + jw.lines,
                {"band": band, "stone": stone, "blocks": blocks, "top": min(s.tops)})


def orb(c, r=33.0, *, latitudes=3, bubble_d=13.0, color=GOLD) -> Part:
    """The spring-vent orb (§H.1): a gold sphere with ``latitudes`` ripple
    latitudes (§G.8: arcs bowing down, gaps growing ×1.3 from the pole, the
    ripples spreading from the vent) and ONE bubble floating free above the
    pole in place of a cross — a MEDIUM ring 4.2 px clear of the sphere, no
    stem, no collar (never a bauble or a pot lid). No mark at the pole: a
    small vent ellipse there reads as a smile."""
    c = P(c)
    body = R(circle(c, r))
    top = c[1] - r
    bc = P(c[0], top - MEDIUM - GAP - bubble_d / 2)
    bub = R(circle(bc, bubble_d / 2 + MEDIUM / 2))
    shape = U(body, bub)
    fills = fill(body, color)
    lines = outline(body) + line(circle(bc, bubble_d / 2), MEDIUM, role="bubble")
    gaps = [8.2, 10.6, 13.8][:latitudes]
    y = top + 5.5
    for k in range(latitudes):
        y += gaps[k]
        dx = math.sqrt(max(r * r - (y - c[1]) ** 2, 0))
        lines += line(arc_sag((c[0] - dx, y), (c[0] + dx, y), -(2.6 + 0.10 * (y - top))), FINE, role="latitude")
    return Part(shape, fills, lines, {"c": c, "r": r, "bubble": bc})


@dataclass
class SceptreSpec:
    x: float = 540.0
    hw: float = 11.0
    top: float = 162.0
    bottom: float = 545.0
    finial_c: tuple = (540.0, 114.0)
    finial_r: float = 29.0
    segments: int = 7
    collar_hw: float = 15.0        # raised bead collars between segments
    collar_h: float = 7.4
    kinds: tuple = ("marl", "strata", "chert")
    color: str = GOLD
    visible_to: float = 511.0      # the band's top rule: segment detail stops 4.5 px above it


def _segment(kind, x, y0, y1, hw, edge=CONTOUR):
    """One drill-core segment's pattern. ``edge``: the shaft's outline weight
    where it meets paper (the figure CONTOUR), which sets the free room:
    marks keep 3 px clear of its inner edge (§I.12)."""
    room = hw - edge / 2 - GAP_MARK - MEDIUM / 2 - 0.2
    f = C.Frag()
    ym = (y0 + y1) / 2
    if kind == "strata":
        ya, yb = ym - 5.5, ym + 5.5
        f += seg(P(x - hw, ya), P(x + hw, ya), FINE, style="rule", role="course")
        f += seg(P(x - hw, yb), P(x + hw, yb), FINE, style="rule", role="course")
        f += hatch_in(box(x - hw, ya, x + hw, yb), angle=-45.0)
    elif kind == "chert":
        h = (y1 - y0) / 2 - 9.0          # the sharp (miter 10) tips keep 3 px from the collars
        vw = min(10.0, 2 * (room - (GAP - GAP_MARK)))             # runs alongside the outline: 4.2 px
        f += C.stroke(vesica((x, ym - h), (x, ym + h), vw), MEDIUM, style="point", role="chert")
    else:
        dl = min(3.5, room)
        for yy in (ym - 8.0, ym, ym + 8.0):
            f += seg(P(x - dl, yy), P(x + dl, yy), MEDIUM, role="marl")
    return f


def sceptre(s: SceptreSpec = SceptreSpec()) -> Part:
    """The core sceptre (§H.1): a drill core of ``segments`` banded segments
    (strata, chert vesica, marl dashes, repeated) between RAISED bead collars
    that read at 188 px, on a knop under a Source Rosette finial with a red
    centre cut into the gold. The collars and finial make it a sceptre, not
    a wand."""
    x = s.x
    shaft = box(x - s.hw, s.top, x + s.hw, s.bottom)
    fc = P(s.finial_c)
    fin = R(circle(fc, s.finial_r))
    knop_c = P(x, fc[1] + s.finial_r + 10.0)
    knop = R(circle(knop_c, 11.5))
    seg_len = (s.bottom - s.top) / s.segments
    ys = [s.top + k * seg_len for k in range(s.segments + 1)]
    collars = [rrect(x - s.collar_hw, y - s.collar_h / 2, x + s.collar_hw, y + s.collar_h / 2, 3.2)
               for y in ys[1:-1]]
    body = U(shaft, knop, *[R(cd) for cd in collars])
    shape = U(body, fin)
    lines = C.Frag()
    lines += clip_out(outline(shaft), U(*[R(cd) for cd in collars], knop), eps=-0.5, trap=0.0)
    seg_f = C.Frag()
    for k in range(s.segments):
        y0 = ys[k] + s.collar_h / 2
        y1 = ys[k + 1] - s.collar_h / 2
        seg_f += _segment(s.kinds[k % len(s.kinds)], x, y0 + 3.0, y1 - 3.0, s.hw)
    # detail never ends a hair above the band rule (§I.12): drop what the band cuts
    lines += clip_in(seg_f, box(0, 0, 2000, s.visible_to - 4.5 - MEDIUM))
    for cd in collars:
        lines += outline(cd)
    lines += clip_out(outline(knop), fin, eps=-0.5, trap=0.0)
    lines += outline(circle(fc, s.finial_r))
    ros_r = s.finial_r - CONTOUR / 2 - GAP - FINE / 2 - 0.1
    ros = MG.source_rosette(fc[0], fc[1], ros_r)
    ros = ros.select(lambda m: not (m.kind == "fill" and m.role in ("dot", "hub")))
    lines += clip_out(ros, R(circle(fc, 7.2)), eps=0.0, trap=0.0)
    fills = fill(shape, s.color) + dot(fc, 8.4, RED)
    return Part(shape, fills, lines, {"seg_len": seg_len, "ys": ys, "collars": collars})


def staff(p0, p1, w=18.0, *, color=GOLD) -> Part:
    """A plain straight shaft (paddle loom, key stem, trumpet, pole) from p0
    to p1, ``w`` wide, square ends; for the other courts' tall attributes."""
    p0, p1 = P(p0), P(p1)
    reg = LineString([tuple(p0), tuple(p1)]).buffer(w / 2, cap_style=2)
    return Part(reg, fill(reg, color), outline(reg), {})


# =============================================================================
# 10  pattern fills
# =============================================================================
def pattern(region, kind, *, origin=None, color=INK, **kw) -> C.Frag:
    """A house pattern clipped to ``region`` (shapely/d), drawn in Aquifer
    FINE by deck.motifs. Kinds:

      'strata'         §G.11 courses 12/19, thin ones hatched; kw: fault=((x,y),(x,y)), jog, y0
      'karst'          §G.12 staggered Ø6/10/16 voids; kw: pitch, sizes, seed
      'karst_flooded'  the same with every Ø16 cavern FILLED JADE (+ its FINE
                       crescent) — the aquifer; returns jade fills + ink lines
      'scales'         §G.16 scale lattice; kw: r
      'ashlar'         §G.20 running-bond blocks; kw: block
      'fluting'        vertical buttress lines widening downward; kw: pitch
      'hatch'          plain 45° hatch; kw: angle
      'rowels'         §G.22 small rowel stars in a half-drop grid; kw: pitch, r
      'rowels_solid'   the same as SOLID gold stars with an Aquifer contour (legal on red)
      'bubbles'        a half-drop grid of rising bubbles; kw: pitch, d

    Pattern lines end on the region's edge (butt); free motifs keep 4.2 px +
    their width inside it. For a pattern KNOCKED OUT of a red/jade field use
    ``C.knockout(field_d, pattern(...))``."""
    reg = R(region)
    if reg.is_empty:
        return C.Frag()
    if kind == "strata":
        fault = kw.pop("fault", None)
        return MG.strata(reg, fault=fault, color=color, **kw)
    if kind in ("karst", "karst_flooded"):
        flood_min = kw.pop("flood_min", 15.0)        # flood voids at least this tall (16: caverns only; 9.5: Ø10 too)
        f = MG.karst_voids(reg, origin=origin, color=color, pitch=kw.pop("pitch", (28.0, 21.0)), **kw)
        # one atomic motif per void: its ellipse, its crescent, its cavern fill
        out, cur, n = C.Frag(), C.Frag(), 0
        fills_, lines_ = C.Frag(), C.Frag()
        for m in f.marks:
            closed = [p for p, cl in G.flatten(m.d, 0.05) if cl]
            if closed:                                  # an ellipse starts a new void
                if cur:
                    lines_ += atomic(cur, f"karst{n}")
                n += 1
                cur = C.Frag([m])
                g_ = Polygon(closed[0])
                x0, y0, x1, y1 = g_.bounds
                if kind == "karst_flooded" and y1 - y0 >= flood_min:
                    fills_ += atomic(fill(g_, JADE, role="cavern"), f"karst{n}")
            else:
                cur += C.Frag([m])
        if cur:
            lines_ += atomic(cur, f"karst{n}")
        return fills_ + lines_
    if kind == "scales":
        return MG.scale_lattice(reg, kw.pop("r", 10.0), color=color, **kw)
    if kind == "ashlar":
        return MG.ashlar(reg, color=color, **kw)
    if kind == "hatch":
        return hatch_in(reg, angle=kw.get("angle", C.DIAG), origin=origin, color=color)
    if kind == "fluting":
        pitch = kw.get("pitch", 14.0)
        x0, y0, x1, y1 = reg.bounds
        f = C.Frag()
        cx = (x0 + x1) / 2 if origin is None else origin[0]
        k = 0
        while cx + k * pitch < x1 + 40 or cx - k * pitch > x0 - 40:
            for sg in ((1,) if k == 0 else (-1, 1)):
                xt = cx + sg * k * pitch
                xb = cx + sg * k * pitch * 1.25
                ln = LineString([(xt, y0 - 5), (xb, y1 + 5)]).intersection(reg)
                for l_ in _lines_of(ln):
                    f += line(np.asarray(l_.coords), FINE, color=color, style="rule", role="flute")
            k += 1
        return f
    if kind == "rowels_solid":
        # §C.4: gold on red only as SOLID shapes with an Aquifer contour
        px, py = kw.get("pitch", (38.0, 34.0))
        rr = kw.get("r", 8.5)
        x0, y0, x1, y1 = reg.bounds
        ox, oy = (x0, y0) if origin is None else origin
        inner = reg.buffer(-(rr + GAP + FINE))
        f = C.Frag()
        for j in range(int(math.floor((y0 - oy) / py)) - 1, int(math.ceil((y1 - oy) / py)) + 2):
            off = px / 2 if j % 2 else 0.0
            for i in range(int(math.floor((x0 - ox - off) / px)) - 1, int(math.ceil((x1 - ox - off) / px)) + 2):
                x, y = ox + off + i * px, oy + j * py
                if not inner.contains(Point(x, y)):
                    continue
                st = MG.rowel_star(x, y, rr, hub=rr * 0.36, solid=True, color=GOLD)
                sil = R(st.outline())
                f += atomic(fill(sil, GOLD, role="rowel") + outline(sil, FINE, role="rowel"), f"rowel{i}_{j}")
        return f
    if kind in ("rowels", "bubbles"):
        px, py = kw.get("pitch", (34.0, 30.0))
        x0, y0, x1, y1 = reg.bounds
        ox, oy = (x0, y0) if origin is None else origin
        rr = kw.get("r", 8.0) if kind == "rowels" else kw.get("d", 8.4) / 2
        inner = reg.buffer(-(rr + GAP + FINE))
        f = C.Frag()
        j0 = int(math.floor((y0 - oy) / py)) - 1
        j1 = int(math.ceil((y1 - oy) / py)) + 1
        for j in range(j0, j1 + 1):
            off = px / 2 if j % 2 else 0.0
            i0 = int(math.floor((x0 - ox - off) / px)) - 1
            i1 = int(math.ceil((x1 - ox - off) / px)) + 1
            for i in range(i0, i1 + 1):
                x, y = ox + off + i * px, oy + j * py
                if not inner.contains(Point(x, y)):
                    continue
                if kind == "rowels":
                    f += atomic(MG.rowel_star(x, y, rr, hub=rr * 0.34, color=color), f"rowel{i}_{j}")
                else:
                    f += atomic(C.bubble(x, y, 2 * rr, color=color), f"bub{i}_{j}")
        return f
    raise ValueError(f"pattern: unknown kind {kind!r}")


# =============================================================================
# 11  the simplified Lion Mark clasp (§G.2, ≤ 40 px, gold on any ground)
# =============================================================================
# The Lion Mark clasp, in 40 px units (k = size / 40); see lion_clasp. At
# 40 px every face mark keeps ≥ 3 px (QA 12 'separate marks') from the paper
# disc's rim and from the other marks; the gold the ground can touch is 3.6 px
# (brow) to 4.25 px (chin) wide between face and contour (QA 5r clean on red);
# and the outline stays inside the old mark's envelope (mane 14.3 below c, 15.65
# above), which every court was composed around.
_CLASP = dict(
    rf=9.0, lift=1.0,                         # face: paper disc radius; its centre this far above c
    rc=12.4,                                  # mane cusps: radius at the sides (behind the wings),
    rc_low=14.3, low=(0.25, 0.6),             # ... under the chin, eased in over sin(angle) 0.25 → 0.6,
    rc_top=13.65, top=(0.6, 0.85),            # ... over the brow, eased in over −sin(angle) 0.6 → 0.85
    tip=1.0, n=12, sag=0.5,                   # lock depth; 12 pointed locks; their arcs' bulge
    pivot=(4.0, -3.6),                        # right wing (x outward, y down from c): the primaries' root,
    fan=((-1.0, -10.6), (0.0, -4.2), (-1.6, 1.9)),  # each primary's tip (x back from the outer edge)
    fan_w=(6.6, 5.6, 5.0),                    # ... and vesica width
    focus=(-6.0, -3.0),                       # the partings aim here (near-parallel, not a fish tail)
    eye=(3.05, -3.4), eye_len=0.9,            # face (from its centre): right almond eye, dash length
    nose_top=(2.0, 1.75), nose_bot=(0.35, 3.0),     # (half-width, y) of the solid trapezoid nose
    mouth_y=4.05, mouth_w=2.7, mouth_sag=0.45,      # level mouth: y of its ends, half-length, muzzle dip
)


def _clasp_mane(hc, k):
    """The mane about the face centre: 12 pointed locks (the A♠'s mane is
    pointed locks; round fleece scallops read as a sheep), two shallow arcs
    from each cusp to its tip, fuller under the chin and over the brow."""
    s = _CLASP

    def ease(v, lo, hi):
        t = min(1.0, max(0.0, (v - lo) / (hi - lo)))
        return t * t * (3 - 2 * t)

    def rc(a):                                # cusp radius at angle a (deg, y down)
        sn = math.sin(math.radians(a))
        return (s["rc"] + (s["rc_low"] - s["rc"]) * ease(sn, *s["low"])
                + (s["rc_top"] - s["rc"]) * ease(-sn, *s["top"])) * k

    step = 360.0 / s["n"]
    pth = None
    for i in range(s["n"]):
        a0 = -90.0 + step / 2 + i * step
        am = a0 + step / 2
        c0, tip, c1 = polar(hc, rc(a0), a0), polar(hc, rc(am) + s["tip"] * k, am), polar(hc, rc(a0 + step), a0 + step)
        pth = pth or Path(c0)
        pth.sag(tip, -s["sag"] * k).sag(c1, -s["sag"] * k)
    return R(pth.close().d)


def _clasp_wing(c, k, sg, xo):
    """One wing (sg −1 left, +1 right): the union of three vesica primaries
    fanned LEVEL from a pivot hidden behind the mane, tips at x ``xo`` (40 px
    units), and its two partings (notch → focus; the caller clips them)."""
    s = _CLASP

    def q(x, y):
        return c + P(sg * x, y) * k

    pv, fo = q(*s["pivot"]), q(*s["focus"])
    tips = [q(xo + dx, y) for dx, y in s["fan"]]
    shape = U(*[R(vesica(pv, t, w * k)) for t, w in zip(tips, s["fan_w"])])
    part = C.Frag()
    for t0, t1 in zip(tips[:-1], tips[1:]):
        part += seg((t0 + t1) / 2, fo, FINE, role="shaft")
    return shape, part


def lion_clasp(c, size=40.0) -> Part:
    """The court hallmark (§H.0; §G.2 'simplified Lion Mark: face circle,
    12-scallop mane ring, two wing arcs with 3 primaries each, and a ripple
    line'): ``size`` px wide overall (40 on the courts; ≤ 60 on the J♦ banner),
    a SOLID GOLD clasp with one FINE Aquifer contour (legal on red, §C.4).
    11 strokes. It is the A♠ lion's face at a quarter of its size — calm,
    frontal, noble — never an emoji: nothing slants, nothing droops, and no
    face mark touches the gold (the old mark's rim-touching V brow over a
    drooping mouth read as an angry face; director's note).

    * **Face** — a PAPER disc (r 9, centred 1 px above ``c``) knocked out of
      the gold, holding TWO SEPARATE level almond eyes (FINE dashes 3.0 ×
      2.1), a SOLID trapezoid nose (wide top, as the A♠'s pad) and, one mark
      with it, the philtrum and a LEVEL closed mouth (ends level; a 0.45 px
      muzzle dip each side — the A♠'s mouth, flattened). Every face mark keeps
      ≥ 3 px from the rim and from every other mark, so at 40 px the nose sits
      low under wide-set eyes: a long lion's muzzle.
    * **Mane** — 12 pointed locks; narrow at the sides, where the wings cover
      it, and fuller under the chin and over the brow, where the ground
      touches it (3.6–4.25 px of gold between face and contour: no thin gold
      on red). Its outline keeps to the old mark's envelope (14.3 px below
      ``c``, 15.65 above) so no court's neighbouring line crowds it.
    * **Wings** — each a fan of three long vesica primaries splayed LEVEL
      from behind the mane to the ``size`` edge (the top one's upper edge is
      the wing arc; it stops 1 px short so the tips never butt a neighbouring
      collar link), split by two FINE partings that start on the contour and
      stop on the mane — drawn in the contour's own stroke, so heal never
      strips them as stubs. Raised wings at this size read as horns, ears or
      a bat (COURT_GUIDE §9).
    * **Ripple** — one FINE ripple line beneath, 20.9 px below ``c``.

    Designed at 40 px; every length scales with ``size`` but the strokes do
    not (§B.2), so below 40 px the face marks crowd past §I.12's 3 px (a
    warning is issued). Never a halo (§G.2): add it to the Scene with
    ``halo=0``. meta: ``silhouette`` (gold, face included), ``head`` (face
    centre), ``face`` (the paper disc)."""
    s = _CLASP
    c = P(c)
    k = size / 40.0
    if k < 0.999:
        import warnings
        warnings.warn(f"lion_clasp: {size:g} px < 40 — the face marks cannot keep 3 px apart (§I.12)",
                      stacklevel=2)
    hc = c + P(0.0, -s["lift"]) * k
    mane = _clasp_mane(hc, k)
    xo = (size - FINE) / 2 / k                # primary tips: the contour's outer edge lands on `size`
    wings, parts = zip(*(_clasp_wing(c, k, sg, xo) for sg in (-1, 1)))
    face = Point(*hc).buffer(s["rf"] * k, quad_segs=48)
    sil = U(mane, *wings).buffer(0.3, quad_segs=8).buffer(-0.3, quad_segs=8)
    fills = fill(sil.difference(face), GOLD, role="clasp")
    # the contour and the partings (notch → mane edge) are ONE stroke mark: where a court's line comes
    # near, heal then trims the contour locally instead of deleting the short partings as stubs
    part_d = "".join(m.d for m in clip_in(parts[0] + parts[1], sil.difference(mane)).marks if m.d)
    lines = line(D(sil) + part_d, FINE, role="clasp-contour")
    # the face: two level almond eyes; ONE mark for the solid nose, philtrum and level mouth
    ex, ey = s["eye"]
    ea = s["eye_len"] / 2
    for sg in (-1, 1):
        lines += seg(hc + P(sg * (ex - ea), ey) * k, hc + P(sg * (ex + ea), ey) * k, FINE, role="lion-eye")
    (tw, ty), (bw, by) = s["nose_top"], s["nose_bot"]
    nose = C.polyline_d([hc + P(x, y) * k for x, y in ((-tw, ty), (tw, ty), (bw, by), (-bw, by))], closed=True)
    lines += fill(nose, INK, role="lion-nose") + line(nose, FINE, role="lion-nose")
    mc = hc + P(0.0, s["mouth_y"]) * k
    feat = C.polyline_d([hc + P(0.0, by) * k, mc])
    for sg in (-1, 1):
        feat += arc_sag(mc, mc + P(sg * s["mouth_w"], 0.0) * k, -sg * s["mouth_sag"] * k)
    lines += line(feat, FINE, role="lion-face")
    # the ripple line beneath the chin
    xs = np.linspace(-9.0 * k, 9.0 * k, 61)
    ry = hc[1] + (s["rc_low"] + s["tip"]) * k + FINE + 4.5 * k
    rip = np.column_stack([hc[0] + xs, ry + 1.3 * k * np.sin(xs / (4.5 * k) * math.pi)])
    lines += line(C.polyline_d(rip), FINE, role="ripple")
    shape = U(sil, LineString(rip).buffer(FINE / 2))
    return Part(shape, fills, lines, {"strokes": 11, "silhouette": sil, "head": hc, "face": face})


def band_guard(sc: "Scene", rank="K", cx=AX):
    """Add the rank medallion's invisible occluder to a Scene (add it LAST).
    The system clips court art at y 511 and masks a disc round the medallion;
    a line cut by that disc just above y 511 would end < 3 px from the band
    rule (a QA 12 failure). The guard (the mask disc plus a strip down from
    y 504.5 as wide as the disc) makes everything behind it stop ≥ 3 px
    above the rule there, and fills stop 3 px short. Jacks have no
    medallion: nothing to guard."""
    from deck import frames as _F
    rm = _F.medallion_radius(rank)
    if not rm:
        return sc
    rmask = rm + 4.2
    g = U(circle((cx, T.CY), rmask + 0.6), box(cx - rmask - 3.0, 504.0, cx + rmask + 3.0, T.CY + 40))
    sc.add("band-guard", C.Frag(), g, sil=False)
    return sc


# =============================================================================
# 12  output helpers
# =============================================================================
def layers(frag: C.Frag) -> dict:
    """{layer: [svg fragment]} in print order — an art module's build() value."""
    return {k: [v] for k, v in frag.layers().items()}


BALANCE_TARGET = {"paper": (45, 50), "jade": (15, 20), "red": (12, 16), "gold": (10, 15), "ink": (8, 16)}


def balance_hint(bal: dict) -> list[str]:
    """Given QA check 5's balance dict, list the §C.2 levers to pull (see
    COURT_GUIDE.md §7)."""
    tips = []
    for k, (lo, hi) in BALANCE_TARGET.items():
        v = bal.get(k, 0.0)
        if v < lo:
            tips.append(f"{k} {v}% < {lo}: " + {
                "paper": "trim a flood (narrower mantle, smaller collar), open the tunic",
                "jade": "jade sleeves, flooded karst caverns, a wider mantle or plain jade border",
                "red": "wider lapels / collar lining, red cuffs, a red lining band",
                "gold": "larger regalia (crown, orb, sceptre collars), gold locks",
                "ink": "(fine)"}[k])
        elif v > hi:
            tips.append(f"{k} {v}% > {hi}: " + {
                "paper": "more colour: wider lapels, jade sleeves, a standing collar",
                "jade": "strata or knockouts on the jade",
                "red": "knock bubbles out of the red",
                "gold": "smaller crown or hair; fewer gold fills",
                "ink": "fewer hatched courses, fewer halo pairs, shorter silhouette; "
                       "≈2.2 of every court's ink is the system's corner pip"}[k])
    return tips
