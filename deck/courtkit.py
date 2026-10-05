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
    3  Part and Scene           Part, Scene (add / part / compose / layers; rank=None leaves
                                full-scene continuous art unclipped by the band), flatten_fills, silhouette_line,
    3a C2 court helpers         rot180, c2, s_curve, seam_half
                                heal (logs every change, with the neighbour it fled)
    4  current lines (§G.24)    current_lines (safe curled terminals), lock_fan
    5  faces (§H.0)             FaceSpec, Face, face(center, gaze=frontal | 3/4-left | 3/4-right |
                                profile-left | profile-right, sex, age, lids, **overrides)
    6  hair and beards          HairSpec, hair_fall, hair_cap, hair_back, neck, BeardSpec, beard,
                                MoustacheSpec, moustache
    7  hands                    Hand (add_to tucks the wrist into the cuff; silhouette / with_sleeve:
                                hand + arm as one outline), hand5(at, angle, pose, ...),
                                hand_size(face),
                                fist (any cylinder, any angle, back or palm view), pinch (stem, key,
                                ring), fist_geom / fist_wrist (where the wrist reads), cup (orb from
                                below), flat / open_hand (chest, gesture), clear_of_hand, HandWarning,
                                HAND_LOG
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


def rot180(value, cx=T.CX, cy=T.CY):
    """Rotate a point, path, region, Frag or Part 180° about ``(cx, cy)``."""
    if isinstance(value, Part):
        return Part(shapely.affinity.rotate(value.shape, 180.0, origin=(cx, cy)),
                    value.fills.rot180(cx, cy), value.lines.rot180(cx, cy), dict(value.meta))
    if isinstance(value, C.Frag):
        return value.rot180(cx, cy)
    if isinstance(value, np.ndarray) and value.shape == (2,):
        return P(2 * cx - value[0], 2 * cy - value[1])
    if isinstance(value, (tuple, list)) and len(value) == 2 and all(
            isinstance(v, (int, float, np.integer, np.floating)) for v in value):
        return P(2 * cx - value[0], 2 * cy - value[1])
    if isinstance(value, list) and value and all(
            isinstance(point, (tuple, list, np.ndarray)) and len(point) == 2 for point in value):
        return G.rotate180(np.asarray(value, dtype=float), cx, cy)
    return G.rotate180(value, cx, cy)


def c2(value, cx=T.CX, cy=T.CY):
    """C2-close geometry or drawable art: ``value ∪ rot180(value)``."""
    if isinstance(value, Part):
        rotated = rot180(value, cx, cy)
        return Part(U(value.shape, rotated.shape), value.fills + rotated.fills,
                    value.lines + rotated.lines, dict(value.meta))
    if isinstance(value, C.Frag):
        return value + rot180(value, cx, cy)
    return U(value, rot180(value, cx, cy))


def _catmull_rom(points, samples=24):
    """Sample a Catmull-Rom curve through points with end-chord tangents."""
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 2:
        raise ValueError("Catmull-Rom needs at least two (x, y) points")
    if not isinstance(samples, (int, np.integer)) or samples < 1:
        raise ValueError("samples must be a positive integer")
    padded = np.vstack([2 * points[0] - points[1], points, 2 * points[-1] - points[-2]])
    out = []
    for i in range(1, len(padded) - 2):
        p0, p1, p2, p3 = padded[i - 1], padded[i], padded[i + 1], padded[i + 2]
        for t in np.linspace(0.0, 1.0, samples, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t
                              + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(padded[-2])
    return np.asarray(out)


def s_curve(left_half, n=24):
    """Build a C2 Catmull-Rom S-curve from left-side control points.

    ``left_half`` runs left-to-centre but excludes the centre. Its rotated
    reflection is appended automatically, yielding a full symmetric seam.
    """
    left = [tuple(map(float, point)) for point in left_half]
    if len(left) < 2:
        raise ValueError("s_curve needs at least two left-half control points")
    centre = (float(T.CX), float(T.CY))
    right = [(2 * T.CX - x, 2 * T.CY - y) for x, y in reversed(left)]
    return _catmull_rom(left + [centre] + right, samples=n)


def seam_half(curve, centre=(T.CX, T.CY)):
    """Return the sampled curve's left half as a ``SEAM`` point list.

    The returned points run from the left edge/control point to the exact
    card centre, ready for ``frames.seam_points`` or ``SEAM = ...``.
    """
    points = np.asarray(curve, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 2:
        raise ValueError("seam curve must contain at least two (x, y) points")
    centre = P(centre)
    idx = int(np.argmin(np.hypot(points[:, 0] - centre[0], points[:, 1] - centre[1])))
    if np.hypot(*(points[idx] - centre)) > 0.5:
        raise ValueError(f"curve must pass through its centre {tuple(centre)}")
    half = points[:idx + 1].copy()
    half[-1] = centre
    if len(half) < 2 or np.any(np.diff(half[:, 0]) < -1e-7):
        raise ValueError("left seam half must run monotonically from left to centre")
    return [tuple(map(float, point)) for point in half]


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
    near-misses clipping leaves. ``heal_log`` lists every change.

    ``rank=None`` is full-scene mode: no court-band clip or special band-rule
    healing is applied. Continuous court art should be composed this way,
    then clipped and rotated by ``deck.build``.
    """
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
# 7  hands — existing court hands and the new shared five-finger primitive
# =============================================================================
#
# The older ``fist``, ``pinch``, ``cup``, ``flat`` and ``open_hand`` functions
# remain below for existing court modules, whose outputs must stay unchanged
# until their individual migrations. New/reworked courts use the shared
# ``hand5`` primitive below: one five-digit silhouette, face-scaled, with the
# thumb leaving the palm side on an open V (never across the finger band).
# Its strokes stay clear of the three fingertip notches, and ``with_sleeve``
# makes the hand and sleeve share one outer contour.

FIST_H_MIN = 32.0        # fist height floor: four fingers at ≥ 8 px pitch
FIST_H_K = 0.92          # fist height per unit of the caller's (old) h
FIST_LEN_K = 1.04        # fingertips → knuckle ridge, per unit fist height
FIST_TIP_OUT = 5.0       # fingertip lobes show at most this far past the shaft's far edge
HAND_K = 0.42            # knuckle breadth (= fist height) per unit hand length
HAND_STUB = 7.0          # px a hand runs on past its wrist point, under the cuff
PARALLEL_MIN = GAP + MEDIUM          # 7.3: centre distance of two parallel MEDIUM lines (§I.12)
HEEL_CLOSE = 8.0         # ground between a heel and a haloed shaft narrower than 2 × this turns to paper
ARM_WORDS = ("cuff", "sleeve", "forearm", "arm", "gauntlet", "bracelet", "wrist")
CUFF_WORDS = ("cuff", "gauntlet", "bracelet", "wrist")
_DEFAULT_HAND_HALO = object()
LINE_TUCK = 1e-3         # the 'halo' of an unhaloed hand: lines behind stop under its outline stroke
HAND_LOG: list = []      # construction warnings, newest last (also issued as HandWarning)

# grip proportions (index → little)
GRIP_FH = (0.265, 0.27, 0.25, 0.215)    # each finger's share of the fist height
GRIP_OUT = (0.85, 1.0, 0.85, 0.50)       # fingertip reach past the shaft (× tip_out): the middle longest
GRIP_TILT = (-1.0, 0.0, 3.0, 8.0)        # degrees: + lifts the fingertip toward the shaft's up end (a slight fan)
GRIP_TIP_R = 0.47                        # fingertip lobe radius × finger height
GRIP_LINE = (0.30, 0.24, 0.34)           # back view: finger lines stop this far (× fist length) short of the knuckles
GRIP_THUMB = dict(tip=0.06, root=0.165, rise=0.22, crease_back=1.0, crease_palm=1.0)
PINCH_REACH = 0.14       # pinch: the index fingertip curls this far (× fist height) past the stem
PINCH_STEP = 0.07        # pinch: each lower fingertip stands this much (× fist height) further back


def hand_size(fc) -> float:
    """The hand length that goes with a face (``Face`` or its anchors): its
    chin-to-hairline length (the classical 'a hand is a face')."""
    a = fc.anchors if hasattr(fc, "anchors") else fc
    cy, r = float(a["center"][1]), float(a["r"])
    return float(a["chin"][1]) - (cy - 0.62 * r)


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
    ``inside`` (and inside ``keep``, when given): a digit's edge where it
    lies on the rest of the hand. → list of point arrays."""
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


def _digit(cen, widths, quad=16):
    """A tapered digit (finger, thumb, wrist sweep): the union of the hulls
    of consecutive discs along the centreline ``cen`` (diameters ``widths``,
    one per point, or a (root, tip) pair). Round root and round tip."""
    cen = np.asarray(cen, float)
    if np.ndim(widths) == 0 or len(widths) != len(cen):
        w0, w1 = (float(widths), float(widths)) if np.ndim(widths) == 0 else (float(widths[0]), float(widths[-1]))
        widths = np.linspace(w0, w1, len(cen))
    ds = [Point(*q).buffer(max(float(w) / 2, 0.3), quad_segs=quad) for q, w in zip(cen, widths)]
    if len(ds) == 1:
        return ds[0]
    return shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(ds[:-1], ds[1:])])


def _bend(p0, d0, length, curl_deg, n=12):
    """A digit centreline from ``p0`` heading ``d0`` (unit), ``length`` long,
    bending ``curl_deg`` (screen degrees, + clockwise) evenly along it."""
    pts = [P(p0)]
    h = math.atan2(d0[1], d0[0])
    step = length / n
    dh = math.radians(curl_deg) / n
    for _ in range(n):
        h += dh
        pts.append(pts[-1] + step * P(math.cos(h - dh / 2), math.sin(h - dh / 2)))
    return np.array(pts)


def _biggest(g, solid=True):
    """The largest polygon of g, its holes filled (a hand is one solid silhouette)."""
    ps = _polys_of(g)
    if not ps:
        return Polygon()
    pg = max(ps, key=lambda gg: gg.area)
    return Polygon(pg.exterior) if solid and pg.interiors else pg


def _open_line(pts, shape, *, start_on=True, inset=0.0, min_len=4.0):
    """An open interior line through ``pts`` kept inside ``shape`` (so it
    starts exactly on the outline when ``pts`` begins outside it). ``inset``
    > 0 keeps its free end that far inside the outline. → list of point
    arrays (MEDIUM line centrelines)."""
    ln = LineString(np.asarray(pts, float))
    z = shape.buffer(-inset) if inset > 0 else shape
    res = ln.intersection(z.buffer(-0.02))
    out = [np.asarray(g.coords) for g in _lines_of(res) if g.length >= min_len]
    if start_on and out:
        # only the piece that starts at the first contact with the outline
        p0 = Point(*np.asarray(pts, float)[0])
        out = [min(out, key=lambda q: p0.distance(Point(*q[0])))]
    return out


def _behind(T, d):
    """The half plane behind point T for a digit pointing d (toward T)."""
    T, d = P(T), _unit(d)
    n = np.array([-d[1], d[0]])
    return Polygon([tuple(T + n * BIG), tuple(T - n * BIG), tuple(T - n * BIG - d * BIG), tuple(T + n * BIG - d * BIG)])


def _webs(digits, cens, order=None):
    """Fill the wedge between neighbouring tapered digits behind their tips
    (so the notch between two fingertips is one clean V of their round tips,
    never a slit running back between the fingers). ``cens``: centrelines
    (root → tip). → region to union with the digits."""
    order = list(range(len(digits))) if order is None else order
    out = []
    for i, j in zip(order[:-1], order[1:]):
        parts = []
        for k in (i, j):
            c = np.asarray(cens[k], float)
            parts.append(digits[k].intersection(_behind(c[-1], c[-1] - c[-2])))
        out.append(shapely.union_all(parts).convex_hull)
    return shapely.union_all(out) if out else Polygon()


def _smooth_pts(pts, n=24):
    """Resample a polyline into a smooth curve (Chaikin twice) for drawing."""
    q = np.asarray(pts, float)
    for _ in range(2):
        if len(q) < 3:
            break
        a, b = q[:-1], q[1:]
        mid = np.empty((2 * len(a), 2))
        mid[0::2] = 0.75 * a + 0.25 * b
        mid[1::2] = 0.25 * a + 0.75 * b
        q = np.vstack([q[:1], mid, q[-1:]])
    return q


@dataclass
class Hand:
    """A built hand: ONE region (``hand``: palm, fingers and thumb merged)
    stacked in front of the scene by ``add_to``. ``thumb`` carries the thumb's
    own region for callers that use it as a blocker (``meta['merged']``: it
    is already part of ``hand`` and is never stacked). ``wrist``/``wrist_w``:
    where the arm meets the hand; ``wrist_dir``: the unit direction from the
    hand into the forearm there; ``stub``: px the hand runs on past ``wrist``,
    cut by the cuff in ``add_to``."""
    hand: Part
    thumb: Part
    wrist: np.ndarray
    wrist_w: float
    wrist_dir: np.ndarray | None = None
    stub: float = 0.0

    @property
    def shape(self):
        return self.hand.shape

    def silhouette(self, run=40.0, *, width=None):
        """The hand plus ``run`` px of forearm beyond the wrist (straight,
        ``width`` wide — default the wrist width), as ONE region: union it with
        a sleeve / arm region so the hand and arm share one outline."""
        if self.wrist_dir is None:
            return self.hand.shape
        W, u = P(self.wrist), _unit(self.wrist_dir)
        w = float(width) if width is not None else float(self.wrist_w)
        n = np.array([u[1], -u[0]])
        back = max(self.stub, 2.0)
        arm = Polygon([tuple(W - u * back + n * w / 2), tuple(W + u * run + n * w / 2),
                       tuple(W + u * run - n * w / 2), tuple(W - u * back - n * w / 2)])
        return _biggest(shapely.union(self.hand.shape, arm).buffer(0.6, quad_segs=8).buffer(-0.6, quad_segs=8))

    def with_sleeve(self, sleeve, *, color=None, cuff_line=False) -> Part:
        """Hand + sleeve as ONE Part with one continuous outline: ``sleeve`` is a
        Part (its fills keep its colour) or a region (filled ``color``). The
        hand's wrist runs into the sleeve; by default the cuff is a colour
        edge without an extra stroke, and the outer contour runs on from the
        sleeve into the hand without a corner or a T. Set ``cuff_line=True``
        only for an explicitly inked cuff."""
        if isinstance(sleeve, Part):
            sr, sf, sl = sleeve.shape, sleeve.fills, sleeve.lines
        else:
            sr, sf, sl = R(sleeve), (fill(R(sleeve), color) if color else C.Frag()), C.Frag()
        hs = self.silhouette(run=self.wrist_w * 0.6)
        body = _biggest(shapely.union(hs, sr).buffer(1.0, quad_segs=8).buffer(-1.0, quad_segs=8))
        hand_r = self.hand.shape.difference(sr.buffer(-0.01)) if not self.wrist_dir is None else self.hand.shape
        hand_r = _biggest(hand_r)
        arm_r = body.difference(hand_r)
        fills = clip_in(sf, arm_r) if sf else C.Frag()
        lines = outline(body)
        lines += clip_in(sl.select(lambda m: m.role != "outline"), arm_r.buffer(0.01)) if sl else C.Frag()
        if cuff_line:
            edge = hand_r.boundary.intersection(body.buffer(-0.8))
            for g in _lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
                if g.length > 2.0:
                    lines += line(C.polyline_d(np.asarray(g.coords)), MEDIUM, role="cuffline")
        inner = self.hand.meta.get("inner", C.Frag())
        return Part(body, fills, lines + clip_in(inner, hand_r.buffer(0.5)),
                    {**self.hand.meta, "kind": self.hand.meta.get("kind", "") + "+sleeve", "hand_region": hand_r})

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
        lip = 3.6 if (cuffr is not None and us is not None) else 0.0
        lipz = Polygon([tuple(W - 0.2 * u + n * r0), tuple(W - 0.2 * u - n * r0),
                        tuple(W + lip * u - n * r0), tuple(W + lip * u + n * r0)]) if lip else Polygon()
        if cuffr is not None:
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
        inner = clip_in(hp.meta["inner"], shape.buffer(-0.5))
        return Part(shape, hp.fills, outline(shape) + inner,
                    {**hp.meta, "inner": inner, "tucked": True, "cutline": (W, u, max(lip, self.stub - 1.0))})

    def add_to(self, sc: "Scene", name: str, *, halo=_DEFAULT_HAND_HALO, halo_skip=(), halo_only=None, cuff=None):
        """Stack the hand in front (wrist tucked into the arm, see ``tucked``)
        as ONE item. With ``halo=0`` (the v3 default for a held attribute: the
        shaft runs under the fingers, sharing their contour) a hand closed on a
        HALOED attribute still carries that attribute's paper channel round
        its fingertips and heel, so the lobes end in paper. New ``hand5`` grips
        default to no halo; the established court hands retain their old halo."""
        if halo is _DEFAULT_HAND_HALO:
            halo = 0.0 if str(self.hand.meta.get("kind", "")).startswith("hand5") else HALO
        elif halo is None:
            halo = 0.0
        hp = self.tucked(sc, cuff)
        if "inner" in hp.meta and not halo:
            tips = hp.meta.get("tipzone")
            heelz = hp.meta.get("heelzone")
            arms = tuple(it.name for it in sc.items if any(w in it.name.lower() for w in ARM_WORDS))
            for it in list(sc.items) if tips is not None else []:
                if it.halo > LINE_TUCK and it.occ is not None and not it.occ.is_empty and it.occ.intersects(hp.shape):
                    zone = hp.shape.intersection(it.occ.buffer(it.halo + MEDIUM / 2 + 3.5, quad_segs=12))
                    zone = zone.intersection(tips)
                    if zone.area > 1.0:
                        hz = zone.buffer(it.halo + MEDIUM / 2, quad_segs=12).intersection(
                            it.occ.buffer(it.halo + MEDIUM / 2 + 5.0, quad_segs=12))
                        sc.add(f"{name}~{it.name}", C.Frag(), zone, sil=False, halo=it.halo,
                               halo_skip=it.halo_skip, halo_only=it.halo_only, halo_zone=hz.union(zone))
                    if heelz is None:
                        continue
                    A = it.occ.buffer(it.halo + MEDIUM / 2, quad_segs=12)
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
        if halo:
            sc.add(name, hp.frag, hp.shape, halo=halo, halo_skip=halo_skip, halo_only=halo_only)
        else:
            # no paper channel, but the lines behind end UNDER the hand's outline stroke: a
            # line meeting the hand stops where its round cap reaches the stroke's inner edge,
            # so no cap shows as a bead inside the hand (fills behind are unchanged: their
            # trap stays under the outline)
            sc.add(name, hp.frag, hp.shape, halo=LINE_TUCK, halo_skip=halo_skip, halo_only=halo_only,
                   halo_zone=hp.shape.buffer(-MEDIUM / 2, quad_segs=8))
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


def _lines_frag(polys, role, w=MEDIUM):
    f = C.Frag()
    for pts in polys:
        if len(pts) >= 2:
            f += line(C.polyline_d(pts), w, role=role)
    return f


# -----------------------------------------------------------------------------
# grip: a fist closed round a cylinder (and the pinch)
# -----------------------------------------------------------------------------
def _trim_start(pts, shape, d=None, step=0.2):
    """Cut the start of polyline ``pts`` (which begins ON ``shape``'s
    outline, in a notch) until it is ``d`` px from the outline: the line then
    leaves the notch where the two outline strokes' inner edges meet, so it
    continues the outline's V and its round cap never sits in the notch as a
    dark bead. → point array or None."""
    d = 0.42 * MEDIUM if d is None else d
    ln = LineString(np.asarray(pts, float))
    L = ln.length
    b = shape.boundary
    s = 0.0
    while s < L and b.distance(ln.interpolate(s)) < d:
        s += step
    if s > L - 2.0:
        return None
    return np.asarray(shapely.ops.substring(ln, s, L).coords)


def _notch_lines(pts, shape, *, min_len=4.0):
    """An open interior line from a notch of ``shape``: ``pts`` start outside
    it (beyond the notch) and run inward; clipped to the shape and trimmed
    off the notch (``_trim_start``). → list of point arrays."""
    out = []
    for q in _open_line(pts, shape, min_len=min_len):
        q = _trim_start(q, shape)
        if q is not None and LineString(q).length >= min_len:
            out.append(q)
    return out


def _clean(g, r_open=1.0, r_close=0.7):
    """One smooth solid silhouette: an opening (drops spurs and hairline
    nicks' rims) then a small closing (fills nicks), holes filled."""
    g = _biggest(g)
    g = g.buffer(-r_open, quad_segs=8).buffer(r_open, quad_segs=8)
    g = g.buffer(r_close, quad_segs=8).buffer(-r_close, quad_segs=8)
    return _biggest(g)


def _grip_frame(at, axis_deg, shaft_w, back, h, size, reach, knuckle, thumb="over", pinch=False):
    """The local frame of a grip (shaft vertical through the origin, its UP
    end toward −y, knuckles toward +x; mirrored for ``back`` = −1)."""
    hb = max(HAND_K * float(size), FIST_H_MIN) if size is not None else max(FIST_H_K * float(h), FIST_H_MIN)
    a = shaft_w / 2.0
    t_up = GRIP_THUMB["rise"] * hb if thumb == "over" else 0.0
    if pinch:                                      # the index finger crosses the stem at ``at``
        y0 = -0.5 * GRIP_FH[0] * hb
        ytop = y0 - t_up
    else:
        ytop = -(hb + t_up) / 2.0
        y0 = ytop + t_up
    y1 = y0 + hb
    yc = (y0 + y1) / 2
    tip_out = min(max(float(reach), 2.5), FIST_TIP_OUT) if not pinch else PINCH_REACH * hb
    x_tip = -a - tip_out
    Lf = max(FIST_LEN_K * hb, 2 * a + tip_out + max(float(knuckle), 12.0))
    x_kn = x_tip + Lf
    rot = axis_deg + 90.0
    return dict(hb=hb, a=a, t_up=t_up, ytop=ytop, y0=y0, y1=y1, yc=yc, tip_out=tip_out, x_tip=x_tip,
                Lf=Lf, x_kn=x_kn, rot=rot, mir=back < 0)


def fist(at, axis_deg=-90.0, *, shaft_w=22.0, back=+1, wrist=None, wrist_w=None, h=34.0, size=None,
         reach=7.0, knuckle=11.0, thumb_r=5.6, hand=None, view=None, arm=None, stub=HAND_STUB,
         hidden_wrist=False, thumb="over", grip="power") -> Hand:
    """A hand closed round a cylinder (sceptre, staff, rod, key, paddle, fiddle
    neck, trumpet, stem, rope) whose axis passes through ``at`` pointing
    ``axis_deg`` (screen degrees of the shaft's UP end; −90 = vertical; any
    angle, the hand turns with the shaft). ONE silhouette, five digits:

    * the FOUR FINGERS wrap across the front of the shaft (the shaft shows
      above and below, its contour running under the fingers' — no halo):
      tapered digits with round tips curling round the shaft's far edge (≤ 5
      px past it, the middle finger furthest, the little finger shortest,
      narrowest and lifted a little so the underside rounds up into its
      tip); three open finger lines from the notches between the tips,
      toward the knuckles at staggered lengths;
    * the THUMB is the fist's top edge: it lies along the index finger from
      the back of the hand, its top sloping down from the back-of-hand
      contour to a small round tip at the shaft's near edge (no step, no
      overhang); its only line is its underside, open, from the tip toward
      the knuckle line (short in the back view, to the knuckles in the palm
      view). ``thumb='behind'``: the top of the fist is the index finger and
      only the thumb's tip shows, a small lobe beside the index fingertip
      past the shaft's far edge;
    * the BACK OF THE HAND is the rounded knuckle end; the WRIST tapers out
      of it to ``wrist`` (``fist_wrist`` gives a good point) along the
      forearm (``arm``; ``Hand.add_to`` re-aims it along the sleeve it finds)
      and runs ``stub`` px on into the sleeve; the HEEL leaves the little
      finger in a smooth curve 7.3 px off the shaft.

    Size: ``size`` = the hand length (``hand_size(face)``; the fist is
    ``HAND_K × size`` tall), else the old ``h`` (fist ≈ max(0.92 h, 32)).
    ``grip='pinch'``: a light hold of a thin object (see ``pinch``).

    Chirality: the construction is a back-of-hand view — a LEFT hand when
    ``back`` = +1 (knuckles toward the wrist side), a RIGHT hand when −1.
    ``hand='L'|'R'`` (the figure's hand) that does not match is drawn as the
    PALM view (``view='palm'``): the finger lines stop at the shaft's near
    edge (the curled fingertips) and the thumb's underside runs to the
    knuckles. ``HandWarning``s (also in ``HAND_LOG``) flag wrists inside the
    knuckle line, bent > 65°, far from the knuckles (``hidden_wrist``
    silences them). Returns a Hand."""
    pinch_ = grip == "pinch"
    F = _grip_frame(at, axis_deg, shaft_w, back, h, size, reach, knuckle, thumb, pinch_)
    hb, a, y0, y1, yc, ytop = F["hb"], F["a"], F["y0"], F["y1"], F["yc"], F["ytop"]
    Lf, x_kn, tip_out, rot, mir, t_up = F["Lf"], F["x_kn"], F["tip_out"], F["rot"], F["mir"], F["t_up"]
    M, Mf = _rigid(at, rot, mirror_x=mir)
    dorsal = "L" if back > 0 else "R"
    if view is None:
        view = "back" if (hand is None or str(hand).upper()[:1] == dorsal) else "palm"
    where = f"fist at ({float(at[0]):.0f}, {float(at[1]):.0f})"

    # ---- the four fingers: tapered digits, round tips, a slight fan -----------------------
    fh = [k * hb for k in GRIP_FH]
    tops = [y0 + sum(fh[:k]) for k in range(4)]
    x_root = x_kn - 0.30 * hb
    fingers, tipc, tipr, cens, fronts = [], [], [], [], []
    for k in range(4):
        yck = tops[k] + fh[k] / 2
        r_t = GRIP_TIP_R * fh[k]
        if pinch_ and k > 0:                        # curled into the palm, stepped back off the stem
            front = a + PARALLEL_MIN + 0.8 + (k - 1) * PINCH_STEP * hb
            tilt = (0.0, 5.0, 9.0, 14.0)[k]
        elif pinch_:
            front = -a - PINCH_REACH * hb
            tilt = 0.0
        else:
            front = -a - tip_out * GRIP_OUT[k]
            tilt = GRIP_TILT[k]
        root = P(max(x_root, front + 2 * r_t + 4.0), yck)
        Lk = float(root[0] - (front + r_t))
        tr = math.radians(tilt)
        tip = root + Lk * P(-math.cos(tr), -math.sin(tr))
        cen = _qbez(tip, (tip + root) / 2 + P(0.0, -0.035 * Lk), root, 12)
        fingers.append(_digit(cen, np.linspace(2 * r_t, fh[k] + 1.0, len(cen))))
        cens.append(cen)
        tipc.append(tip)
        tipr.append(r_t)
        fronts.append(front)
    block = shapely.union_all(fingers + [_webs(fingers, [c[::-1] for c in cens])])
    # the knuckle end: the fingers' roots merge into one rounded ridge
    ridge = _digit(np.array([[x_kn - 0.32 * hb, y0 + 0.30 * fh[0]], [x_kn - 0.32 * hb, y1 - 0.30 * fh[3]]]),
                   0.62 * hb)
    x_ridge = (max(fronts[1:]) + 2 * max(tipr)) if pinch_ else -a + 2.0
    ridge = ridge.intersection(shapely.box(x_ridge, y0 - 0.5, BIG, y1 + 0.5))
    # ... and never below the little finger's lower edge (the underside rounds up into its tip)
    d3 = _unit(cens[3][-1] - cens[3][0])
    n3 = P(-d3[1], d3[0]) if d3[0] > 0 else P(d3[1], -d3[0])
    if n3[1] < 0:
        n3 = -n3
    lo3 = cens[3][-1] + n3 * (fh[3] + 1.0) / 2
    hp3 = halfplane(lo3, lo3 + d3, side=+1)
    if not hp3.contains(Point(*cens[3][-1])):
        hp3 = halfplane(lo3, lo3 + d3, side=-1)
    ridge = ridge.intersection(hp3) if not ridge.is_empty else ridge
    tipzone_l = shapely.union_all([Point(*q).buffer(r + 2.4, quad_segs=12) for q, r in zip(tipc, tipr)])
    block = _biggest(_junction_smooth(block.union(ridge), tipzone_l, r=2.2))
    # pinch: ground between the stem and the curled fingers' tips (nothing fills it)
    carve = Polygon()
    if pinch_:
        carve = shapely.union_all([shapely.box(-BIG, tops[k], fronts[k] + tipr[k],
                                               BIG if k == 3 else tops[k] + fh[k] + 0.6) for k in (1, 2, 3)])
        carve = carve.difference(shapely.union_all(fingers[1:])).difference(fingers[0].buffer(0.01))

    # ---- the thumb ---------------------------------------------------------------------
    th = GRIP_THUMB
    rt, rr = th["tip"] * hb, th["root"] * hb
    band = thumb == "over" and (pinch_ or view == "palm")
    if thumb == "over":
        if band:
            # palm view / pinch: the thumb wraps round the front of the shaft as the fist's top
            # band, its round tip in the column of fingertips beside the index tip (the notch
            # between them is where its one line starts)
            rt = 0.5 * t_up
            x_tf = (-a - 0.5) if pinch_ else (-a - 0.45 * tip_out * GRIP_OUT[0])
            Tc = P(x_tf + rt, y0 - rt + 0.8)
        else:
            # back view: a wedge along the top of the index finger, its top flush with the
            # index top at the shaft's near edge and rising to the back of the hand
            x_tf = a + 5.5                          # clear of the shaft's edge where it meets the top
            Tc = P(x_tf + rt, y0 + rt - 0.4)
        Rc = P(x_kn + (0.0 if band else 0.08) * hb, y0 - t_up + rr)
        cen_t = _qbez(Tc, (Tc + Rc) / 2 + P(0.0, -0.03 * hb), Rc, 16)
        w_t = np.linspace(2 * rt, 2 * rr, len(cen_t))
        thumb_r = _digit(cen_t, w_t)
        # its underside (for the crease)
        nt = np.array([_unit(cen_t[min(i + 1, len(cen_t) - 1)] - cen_t[max(i - 1, 0)]) for i in range(len(cen_t))])
        nt = np.column_stack([-nt[:, 1], nt[:, 0]])
        nt[nt[:, 1] < 0] *= -1
        under_t = cen_t + nt * (w_t[:, None] / 2)
    else:                                          # 'behind': only its tip, beside the index tip
        rtb = 0.12 * hb
        Tc = P(tipc[0][0] - tipr[0] - 0.15 * rtb, tipc[0][1] + 0.12 * fh[0])
        thumb_r = _digit(np.array([P(-a + 1.0, Tc[1]), Tc]), 2 * rtb)

    # ---- the wrist -------------------------------------------------------------------
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
    hK = 0.46 * hb                                 # half-breadth of the back at the knuckles

    def build(u):
        """hand region and interior lines (local) for a forearm direction u."""
        u = _unit(u)
        n_th = np.array([u[1], -u[0]])             # the thumb side of the wrist
        hw = min(float(wrist_w) if wrist_w is not None else BIG, 0.68 * hb) / 2.0
        hw_in = hw
        Wb = W - n_th * hw
        x_floor = x_min + 0.16 * hb
        if Wb[0] < x_floor and Wb[1] > y1 and n_th[0] > 1e-3:
            hw_in = min(hw, max((W[0] - x_floor) / n_th[0], 0.55 * hw))
            Wb = W - n_th * hw_in
            if Wb[0] < x_min + 0.5:
                hw_in = max((W[0] - x_min - 0.5) / n_th[0], 0.25 * hw)
                Wb = W - n_th * hw_in
        # the wrist: one tapered sweep from the knuckle mass, arriving along the forearm,
        # with a slight waist just before the cuff
        Lw = float(np.hypot(*(W - Bs)))
        C_ = W - u * 0.45 * Lw
        nseg = max(10, int(Lw / 2.5))
        tt = np.linspace(0.0, 1.0, nseg + 1)
        cen_ = list(_qbez(Bs, C_, W, nseg + 1)) + [W + u * stub * 0.5, W + u * stub]
        prof = [t * t * (3 - 2 * t) for t in tt]
        wid = [hK + (hw - hK) * p for p in prof] + [hw, hw]
        shift = [n_th * (hw - hw_in) / 2 * p for p in prof] + [n_th * (hw - hw_in) / 2] * 2
        wid = [w_ - (hw - hw_in) / 2 * p for w_, p in zip(wid, prof + [1.0, 1.0])]
        ds = [Point(*(q + s_)).buffer(max(rw, 0.5), quad_segs=16) for q, s_, rw in zip(cen_, shift, wid)]
        neck = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(ds[:-1], ds[1:])])
        neck = neck.intersection(halfplane(W + u * stub, W + u * stub + n_th, side=+1))
        if pinch_:
            neck = neck.difference(carve)
        # the heel: a smooth curve from the little finger into the wrist, off the shaft
        # the underside: ONE curve from the little fingertip's lowest point into the wrist
        P3 = tipc[3] + n3 * tipr[3]
        H = _edge(P3, d3, Wb, u, 24)
        clear = Polygon()
        if u[1] > -0.3:
            heel = Polygon([tuple(q) for q in list(H) + [W, Bs, tipc[3]]]).buffer(0)
            neck = neck.union(heel)
            far = P3 - d3 * 400.0
            clear = Polygon([tuple(far + n3 * 0.3), tuple(P3 + n3 * 0.3)] + [tuple(q) for q in H[1:]]
                            + [tuple(Wb + u * 400.0), tuple(Wb + u * 400.0 + n3 * 400.0),
                               tuple(far + n3 * 400.0)]).buffer(0)
            trimmed = neck.difference(clear)
            if not trimmed.is_empty:
                neck = _biggest(trimmed)
        # the thenar: the thumb's root flows into the back of the hand (no notch, no line)
        parts = [block, neck]
        if thumb == "over":
            # (on along the wrist's top so the thumb's knuckle rounds into it, no dip)
            Qw = _qbez(Bs, C_, W, 11)[2]
            rq = hK + (hw - hK) * 0.10
            root_join = shapely.union_all([Point(*Rc).buffer(rr, quad_segs=16),
                                           Point(*Bs).buffer(hK, quad_segs=16),
                                           Point(*Qw).buffer(rq, quad_segs=16)]).convex_hull
            root_join = root_join.intersection(shapely.box(x_kn - 0.36 * Lf, -BIG, BIG, BIG))
            parts += [thumb_r, root_join]
        else:
            parts += [thumb_r]
        hand_ = shapely.union_all(parts)
        floor = clear
        if not floor.is_empty:
            hand_ = _biggest(hand_.difference(floor))
        if pinch_:
            hand_ = _biggest(hand_.difference(carve))
        tz = tipzone_l.union(Point(*Tc).buffer((rt if thumb == "over" else 0.115 * hb) + 2.6, quad_segs=12))
        keep_out = tz.union(clear.buffer(0.3)).union(floor).union(carve.buffer(2.0))
        hand_ = _junction_smooth(hand_, keep_out, r=0.20 * hb)
        hand_ = _clean(hand_, r_open=2.0)

        # ---- interior lines: open, from the notches -------------------------------------
        inner = C.Frag()
        lines_ = []
        # finger separations k-1 | k: from the notch between the tips toward the knuckles
        for k in (1, 2, 3):
            ca, cb = cens[k - 1], cens[k]
            wa, wb = fh[k - 1], fh[k]
            mid = (ca * wb + cb * wa) / (wa + wb)          # the seam between the two fingers
            if pinch_:
                # from the notch where the curled tip meets the finger above, along its top edge
                dk = _unit(cb[-1] - cb[0])
                nk = P(dk[1], -dk[0]) if dk[0] > 0 else P(-dk[1], dk[0])
                if nk[1] > 0:
                    nk = -nk
                p0 = cb[0] + nk * tipr[k] - dk * 6.0
                xe = x_kn - (0.10 if k == 1 else 0.04) * Lf
                if view == "palm":
                    xe = fronts[k] + 2 * tipr[k] + 4.0
                p1 = cb[-1] + nk * (fh[k] + 1.0) / 2
                p1 = p0 + (p1 - p0) * max(0.2, (xe - p0[0]) / max(p1[0] - p0[0], 1e-6))
                pts = np.linspace(p0, p1, 16)
            else:
                ext = mid[0] + _unit(mid[0] - mid[2]) * 8.0
                mid = np.vstack([mid, mid[-1] + _unit(mid[-1] - mid[-3]) * Lf])
                xe = x_kn - GRIP_LINE[k - 1] * Lf if view == "back" else a + 1.5 + (k == 2) * 2.0
                if k == 1 and thumb == "over" and not band:
                    xe = min(xe, x_tf - 3.5)          # clear of the thumb's crease
                cut = LineString(np.vstack([ext, mid])).intersection(shapely.box(-BIG, -BIG, xe, BIG))
                gs = [g for g in _lines_of(cut) if g.length > 1.0]
                if not gs:
                    continue
                pts = np.asarray(max(gs, key=lambda g: g.length).coords)
            lines_ += _notch_lines(pts, hand_)
        inner += _lines_frag(lines_, "finger")
        # the thumb's underside: from its tip toward the knuckle line, open
        if thumb == "over":
            body = block.union(neck)
            span = x_kn - 0.02 * hb - Tc[0]            # never past the knuckle line
            stop = Tc[0] + (th["crease_back"] if view == "back" else th["crease_palm"]) * span
            if band:
                # from the notch between its tip and the index tip, along its underside
                for pts in _crease(thumb_r, body, keep=shapely.box(-BIG, -BIG, stop, BIG), min_len=4.0):
                    if np.hypot(*(pts[-1] - Tc)) < np.hypot(*(pts[0] - Tc)):
                        pts = pts[::-1]
                    q = _trim_start(pts, hand_)
                    if q is not None and LineString(q).length > 4.0:
                        inner += line(C.polyline_d(q), MEDIUM, role="thumb")
            else:
                # a branch off the top contour at the tip, down and back along its underside
                y_end = float(np.interp(stop, under_t[:, 0], under_t[:, 1]))
                p0, p1 = P(x_tf - 1.0, y0 - 1.6), P(stop, y_end)
                ctrl = P(x_tf + 3.0 * rt, y_end + 0.4)
                for q in _notch_lines(_qbez(p0, ctrl, p1, 24), hand_):
                    inner += line(C.polyline_d(q), MEDIUM, role="thumb")
        # ('behind': the notches above and below its tip lobe are the only separation)
        return hand_, inner, 2 * hw

    drawn = dorsal if view == "back" else ("R" if dorsal == "L" else "L")
    tipzone = _xf(shapely.box(-BIG, -BIG, -a + 1.0, BIG), M)       # the fingertip side of the shaft
    heelzone = _xf(shapely.box(a - 1.0, y1 - 1.0, BIG, BIG), M)     # below the fingers, knuckle side
    base_meta = {"kind": "pinch" if pinch_ else "fist", "hand": drawn, "view": view, "block_h": hb,
                 "block_len": Lf, "wrist_off_deg": off, "size": hb / HAND_K}
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
    return Hand(part, Part(_xf(thumb_r, M), C.Frag(), C.Frag(), {"merged": True}), Ws, ww, us, float(stub))


def pinch(at, axis_deg=-90.0, *, stem_w=5.0, back=+1, wrist=None, size=None, h=34.0, **kw) -> Hand:
    """A small object held between the thumb and the index finger — a flower
    stem, a key, a chalice stem — ``at`` is where it passes between their
    tips, ``axis_deg`` its up direction (tested from −45 to −135: an object
    held up and away; a lantern ring or bail is a GRIP, ``fist`` with axis
    180, the fingers hooked over the bar).
    The index finger crosses the object and curls round it; the thumb lies
    along the index finger, its tip pressing the object; the other three
    fingers are curled into the palm, each stepped further back, their round
    tips clear of the object, so the object runs on below the index finger
    over open ground. Same options as ``fist`` (``wrist``, ``hand``,
    ``view``, ``arm`` …)."""
    return fist(at, axis_deg, shaft_w=stem_w, back=back, wrist=wrist, size=size, h=h, grip="pinch",
                **{"reach": 4.0, **kw})


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


def fist_geom(at, axis_deg=-90.0, *, shaft_w=22.0, back=+1, h=34.0, size=None, reach=7.0, knuckle=11.0,
              thumb="over", grip="power"):
    """The frame facts of ``fist(...)`` with these arguments (no drawing):
    fist height ``hb``, length ``Lf``, the knuckle point ``kn`` and the
    back-of-hand mass ``Bs`` (screen points), the hand-axis unit ``axis``
    (from the fingertips toward the knuckles) and ``down`` (along the shaft
    toward its lower end). For placing wrists and cuffs."""
    F = _grip_frame(at, axis_deg, shaft_w, back, h, size, reach, knuckle, thumb, grip == "pinch")
    M, _ = _rigid(at, F["rot"], mirror_x=F["mir"])
    hb, x_kn, yc = F["hb"], F["x_kn"], F["yc"]

    def S(q):
        g = _xf(Point(*q), M)
        return P(g.x, g.y)
    o = S(P(0.0, 0.0))
    return {"hb": hb, "Lf": F["Lf"], "kn": S(P(x_kn, yc)), "Bs": S(P(x_kn - 0.20 * hb, yc + 0.03 * hb)),
            "axis": _unit(S(P(1.0, 0.0)) - o), "down": _unit(S(P(0.0, 1.0)) - o), "y1": F["y1"], "a": F["a"]}


def fist_wrist(at, axis_deg=-90.0, *, bend=40.0, dist=0.85, shaft_w=22.0, back=+1, h=34.0, size=None, reach=7.0,
               knuckle=11.0, grip="power"):
    """Where a fist's wrist reads best: ``dist`` × the fist height from the
    back-of-hand mass, ``bend``° off the hand axis toward the shaft's lower
    end (0 = straight out along the knuckles; ``fist`` warns past 65°).
    → screen point."""
    g = fist_geom(at, axis_deg, shaft_w=shaft_w, back=back, h=h, size=size, reach=reach, knuckle=knuckle, grip=grip)
    b = math.radians(bend)
    return g["Bs"] + g["hb"] * dist * (math.cos(b) * g["axis"] + math.sin(b) * g["down"])


# -----------------------------------------------------------------------------
# cup: an orb held from below
# -----------------------------------------------------------------------------
CUP_OVER = (0.20, 0.27, 0.23, 0.12)      # each fingertip's reach up over the sphere's lower rim (× r)
CUP_FW = (1.02, 1.04, 1.0, 0.88)         # finger width relative to a quarter of the knuckle breadth
CUP_KN = 0.30                            # knuckle row: this × finger width below the sphere's bottom


def _orb_low_latitude(r):
    """The kit ``orb``'s lowest ripple latitude as y(x) (sphere-local), or None."""
    y_end = -r + 5.5 + 8.2 + 10.6 + 13.8
    if y_end >= r - 2.0:
        return None
    sag = 2.6 + 0.10 * (y_end + r)
    dx = math.sqrt(max(r * r - y_end * y_end, 1.0))
    return lambda x: y_end + sag * max(0.0, 1.0 - (x / dx) ** 2)


def cup(c, r, *, side=-1, wrist=None, wrist_w=None, grip=None, fw=None, thumb_w=None,
        thumb_from=72.0, thumb_to=24.0, knuckle=3.0, converge=0.80, stub=HAND_STUB, size=None,
        spread=1.10, clear_y="orb") -> Hand:
    """A hand holding a sphere (orb, cone, bowl, lantern) from below: ONE
    silhouette, the palm UNDER the sphere and only the fingertips over it.

    * the palm sits below the sphere, its knuckle row just under the
      sphere's bottom; it tapers into the wrist (the little-finger side
      swelling a little) and runs ``stub`` px on into the sleeve;
    * four short fingers curl up the sphere's near lower rim: tapered, round
      tips on an arc following the rim (only the tips overlap the sphere,
      well below its equator), the middle finger highest, the little finger
      short and narrow, fanning a little (``spread``: tip spacing / knuckle
      spacing); three open lines from the notches between the tips stop at
      the knuckle row;
    * the THUMB is a short lobe from the thumb-side edge of the palm, its
      round tip resting on the sphere's rim ``thumb_to`` + 8° below the
      equator (a short lobe, never a hook along the rim); the web between it and the index
      finger is a wide, smooth V of the outline.

    ``side`` −1: thumb toward +x (screen right), +1: toward −x. The hand's
    scale follows ``size`` (``hand_size(face)``) when given, else ``fw`` or
    0.34 r per finger. ``grip`` (default 0.36) scales how far the tips reach
    over the rim. ``clear_y``: a sphere-local y (or a function of x) the
    fingertips stay ≥ 6.3 px below — by default the kit ``orb``'s lowest
    ripple latitude, so the ripples run whole above the fingers and are
    never chopped into dashes between the tips (None: no limit). The best
    wrist is ≈ 1.6–1.9 r below the sphere's centre, a little toward the
    little-finger side. Returns a Hand."""
    c = P(c)
    if size is not None:
        fw = HAND_K * float(size) / 4.0
    fw = fw if fw is not None else r * 0.34
    sd = -1.0 if side < 0 else 1.0                   # the little finger's x side
    ts = -sd                                         # the thumb's x side
    reach_k = min(max((0.36 if grip is None else float(grip)) / 0.36, 0.6), 1.6)
    fws = [fw * k for k in CUP_FW]
    span = sum(fws)
    # knuckle row (index on the thumb side), centred a little toward the little finger
    order = list(range(4)) if ts < 0 else list(range(3, -1, -1))     # left → right finger ids
    xs, x = {}, -span / 2 + sd * 0.06 * span
    for fid in order:
        xs[fid] = x + fws[fid] / 2
        x += fws[fid]
    y_kn = r + CUP_KN * fw + 0.02 * float(knuckle)
    lat = _orb_low_latitude(r) if clear_y == "orb" else (
        None if clear_y is None else (clear_y if callable(clear_y) else (lambda x, _y=float(clear_y): _y)))
    CLR = GAP + MEDIUM / 2 + FINE / 2 + 0.6          # a fingertip's top below a latitude
    tips0 = []
    for k in range(4):
        xt = xs[k] * spread
        rho = r * (1.0 - CUP_OVER[k] * reach_k)
        yt = math.sqrt(max(rho * rho - xt * xt, 0.25 * rho * rho))
        tips0.append(P(xt, yt + 0.44 * fws[k] * 0.2))
    lat_mode = None
    if lat is not None:
        # the ripple latitude either runs whole ABOVE the fingertips, or (when that would push
        # them off the sphere) passes BEHIND the fingers below the notches, hidden from the
        # index to the little finger: never chopped into dashes between the tips
        below = [max(t[1], lat(t[0]) + CLR + 0.44 * fws[k]) for k, t in enumerate(tips0)]
        if max(b - t[1] for b, t in zip(below, tips0)) <= 0.12 * r:
            lat_mode = "above"
            for k, t in enumerate(tips0):
                t[1] = below[k]
        else:
            lat_mode = "behind"
            for k, t in enumerate(tips0):
                t[1] = min(t[1], lat(t[0]) - (MEDIUM / 2 + FINE / 2 + 1.5))
    fing, tipc, cens, tipr, kns = [], [], [], [], []
    for k in range(4):
        xk = xs[k]
        kn = P(xk, y_kn + 0.06 * abs(xk) ** 1.5 / max(r, 1.0) ** 0.5)
        rt_ = 0.44 * fws[k]
        tip = tips0[k]
        xt = tip[0]
        mid = (kn + tip) / 2 + P(0.08 * (xt - xk) + 0.04 * xt, 0.0)
        cen = _qbez(kn + P(0.0, 0.45 * fws[k]), mid, tip, 12)
        fing.append(_digit(cen, np.linspace(fws[k] + 0.8, 2 * rt_, len(cen))))
        cens.append(cen)
        tipc.append(tip)
        tipr.append(rt_)
        kns.append(kn)
    fingers = shapely.union_all(fing + [_webs(fing, cens, order)])
    tipz = shapely.union_all([Point(*q).buffer(rr_ + 2.6, quad_segs=12) for q, rr_ in zip(tipc, tipr)])
    fingers = _biggest(_junction_smooth(fingers, tipz, r=2.0))
    W = P(sd * 0.45 * r, 1.8 * r) if wrist is None else P(wrist) - c
    if W[1] > 2.1 * r + 22.0:
        _hand_warn(f"cup at ({c[0]:.0f}, {c[1]:.0f}): wrist {W[1]:.0f} px below the sphere centre "
                   f"(best ≈ {1.6 * r:.0f}–{1.9 * r:.0f}): a long palm; move the cuff up")
    hw = min(float(wrist_w) if wrist_w is not None else BIG, 0.68 * span) / 2.0
    kc = P(np.mean([q[0] for q in kns]), y_kn)
    # the thumb: a short lobe from the palm's thumb-side edge up to the rim
    tw = float(thumb_w) if thumb_w is not None else 1.0 * fw
    a_t = math.radians(min(max(float(thumb_to) + 8.0, 22.0), 60.0))
    t_tip = P(ts * (r - 0.15 * tw) * math.cos(a_t), (r - 0.15 * tw) * math.sin(a_t))
    while lat_mode == "above" and t_tip[1] - 0.43 * tw < lat(t_tip[0]) + CLR and a_t < math.radians(75.0):
        a_t += math.radians(2.0)                   # the thumb's tip below the ripple latitude too
        t_tip = P(ts * (r - 0.15 * tw) * math.cos(a_t), (r - 0.15 * tw) * math.sin(a_t))
    i_idx = 0
    t_root = P(xs[i_idx] + ts * 0.05 * fws[i_idx], y_kn + 0.55 * fw)

    def build(u):
        u = _unit(u, (0.0, 1.0))
        n = np.array([u[1], -u[0]])
        Wl, Wr = (W + n * hw, W - n * hw) if (n[0] < 0) else (W - n * hw, W + n * hw)
        lft, rgt = order[0], order[-1]
        kl = P(xs[lft] - fws[lft] / 2 - 0.2, kns[lft][1] + 0.9 * fw)
        kr = P(xs[rgt] + fws[rgt] / 2 + 0.2, kns[rgt][1] + 0.9 * fw)
        # the palm's sides: down from the knuckles, curving into the wrist; the little-finger
        # side swells (hypothenar), the thumb side is straighter (the thumb grows from it)
        dn = _unit(P(0.0, 1.0) + 0.8 * u)
        le = _edge(kl, _unit(dn + P(0.25, 0.0)) if Wl[0] > kl[0] else dn, Wl, u, 20)
        re_ = _edge(kr, _unit(dn + P(-0.25, 0.0)) if Wr[0] < kr[0] else dn, Wr, u, 20)
        for pts_, is_little in ((le, sd < 0), (re_, sd > 0)):
            ch = _unit(pts_[-1] - pts_[0])
            nn_ = np.array([-ch[1], ch[0]])
            if float(np.dot(nn_, pts_[0] - kc)) < 0:
                nn_ = -nn_
            tt_ = np.linspace(0.0, 1.0, len(pts_))[:, None]
            bulge = (0.035 if is_little else 0.0) * span
            pts_ += nn_ * bulge * np.sin(np.pi * tt_) ** 1.3
        ring = ([P(kl[0], y_kn - 0.6 * fw)] + list(le) + [Wl + u * stub, Wr + u * stub] + list(re_[::-1])
                + [P(kr[0], y_kn - 0.6 * fw)])
        palm = _biggest(Polygon([tuple(q) for q in ring]).buffer(0))
        # the thumb, rooted in the thenar on the palm's edge
        root = t_root + P(0.0, 0.10 * fw)
        d_t = _unit(t_tip - root)
        mid_t = (root + t_tip) / 2 + np.array([d_t[1], -d_t[0]]) * (0.10 * tw) * (1 if ts * d_t[1] < 0 else -1)
        cen_t = _qbez(root, mid_t, t_tip, 12)
        thumb = _digit(cen_t, np.linspace(1.15 * tw, 0.86 * tw, len(cen_t)))
        # the thenar: the thumb's lower half flows into the palm and on into the wrist
        Wt = Wl if ts < 0 else Wr
        low_t = thumb.intersection(shapely.box(-BIG, y_kn - 0.1 * fw, BIG, BIG))
        thenar = shapely.union_all([low_t, Point(*Wt).buffer(0.5), Point(*W).buffer(0.5),
                                    Point(*kns[i_idx]).buffer(0.5)]).convex_hull if not low_t.is_empty else Polygon()
        hand_ = shapely.union_all([fingers, palm, thumb, thenar])
        keep = tipz.union(Point(*t_tip).buffer(0.43 * tw + 2.6, quad_segs=12))
        # the web between thumb and index finger: a wide smooth V (closing only there)
        webc = (t_tip + tipc[i_idx]) / 2
        webz = Point(*((webc + kns[i_idx]) / 2)).buffer(0.9 * fw)
        hand_ = _junction_smooth(hand_, keep.union(shapely.box(-BIG, -BIG, BIG, BIG).difference(webz)), r=0.55 * fw)
        hand_ = _junction_smooth(hand_, keep.union(webz), r=0.30 * fw)
        hand_ = _clean(hand_, r_open=1.4, r_close=0.9)
        inner = C.Frag()
        lines_ = []
        stops = {frozenset((0, 1)): 0.15, frozenset((1, 2)): 0.0, frozenset((2, 3)): 0.25}
        for i in range(3):
            ka, kb_ = order[i], order[i + 1]
            ca, cb = cens[ka], cens[kb_]
            wa, wb = fws[ka], fws[kb_]
            seam = (ca * wb + cb * wa) / (wa + wb)                      # knuckle → tips
            ext = seam[-1] + _unit(seam[-1] - seam[-3]) * 8.0
            # stop at (or a little above) the knuckle row, staggered
            s_ = stops[frozenset((ka, kb_))]
            end = seam[0] + (seam[-1] - seam[0]) * (0.18 + s_)
            q = np.vstack([ext, seam[::-1]])
            q = q[q[:, 1] <= end[1] + 1e-6]
            if len(q) >= 2:
                lines_ += _notch_lines(np.vstack([q, end]), hand_)
        inner += _lines_frag(lines_, "finger")
        return hand_, inner, thumb

    Mt = (1, 0, 0, 1, c[0], c[1])
    meta0 = {"kind": "cup", "size": 4 * fw / HAND_K}

    def place(u):
        hl, il, tl = build(u)
        hs, is_ = _xf(hl, Mt), il.translate(c[0], c[1])
        return Part(hs, C.Frag(), outline(hs) + is_, {**meta0, "inner": is_, "rebuild": rebuild}), tl

    def rebuild(u_screen):
        return place(P(u_screen))[0]

    u0 = _unit(W - kc, (0.0, 1.0))
    part, tl = place(u0)
    return Hand(part, Part(_xf(tl, Mt), C.Frag(), C.Frag(), {"merged": True}), W + c, 2 * hw, u0, float(stub))


# -----------------------------------------------------------------------------
# open hand: flat on the chest, a gesture, a blessing
# -----------------------------------------------------------------------------
OPEN_LEN = (0.89, 1.0, 0.94, 0.74)       # finger length (index → little) relative to the middle
OPEN_KN = (0.025, 0.0, 0.025, 0.075)     # knuckle set-back (× hand length) from the middle finger's
OPEN_FW = (1.02, 1.04, 1.0, 0.86)        # finger width relative to a quarter of the knuckle breadth
OPEN_STOP = (0.20, 0.10, 0.24)           # finger lines stop this far (× finger length) short of the knuckles


def flat(at, angle=0.0, *, side=-1, length=56.0, width=30.0, wrist_w=None, tips=None,
         knuckle=0.55, thumb_deg=32.0, thumb_len=0.44, taper=0.78, curl=0.0, stub=0.0, size=None,
         hand=None, view="back", spread=0.0, palm_crease=None) -> Hand:
    """An open hand (on the chest, a bodice, a belt, a hilt; a gesture) from
    ``at`` (the wrist) pointing ``angle`` (screen degrees): ONE silhouette.

    * the palm tapers from the knuckle row (``knuckle`` × length along, the
      index and little knuckles set back on an arc) to a wrist ``taper`` ×
      ``width`` wide (never wider than ``wrist_w``), the little-finger edge
      swelling a little (hypothenar), running ``stub`` px on behind ``at``
      (tucked into a cuff by ``Hand.add_to``);
    * four tapered fingers ≈ 45 % of the hand's length with round tips, the
      middle longest, the little finger short and narrow; ``spread``° opens
      them (0: together, their separations three open lines from the tip
      notches almost to the knuckles; ≥ 4: apart, the gaps drawn by the
      contour); ``curl``° bends them softly toward the little-finger side;
      ``tips`` (old API) sets how far each stops short of ``length``;
    * the THUMB opens from about mid-palm on a wide, smooth V web,
      ``thumb_deg``° off the index edge, ``thumb_len`` × length long from
      its root low in the thenar (its free part ≈ half the middle finger),
      its last joint bending a little back toward the fingers;
    * ``view='palm'`` adds the thenar crease ('life line'): from the web
      between thumb and index round the thumb's mound toward the wrist,
      its hollow toward the thumb, ≈ 0.35 × the palm long (``palm_crease``
      forces it on or off).

    Size: ``size`` = the hand length (``hand_size(face)``; overrides
    ``length``/``width``). Chirality: ``side`` −1 puts the thumb on the
    screen-left of the pointing direction; ``hand='L'|'R'`` with ``view``
    sets it instead (a right hand seen from the back has its thumb on the
    left of the pointing direction). Returns a Hand."""
    if size is not None:
        length, width = float(size), HAND_K * float(size)
    if hand is not None:
        right = str(hand).upper()[:1] == "R"
        side = -1 if right == (view == "back") else +1
    L = float(length)
    kb = float(width)
    ts = -1.0 if side < 0 else 1.0                 # local y of the thumb side
    fw0 = kb / 4.0
    fws = [fw0 * k for k in OPEN_FW]
    xk = L * float(knuckle)
    ww = min(float(wrist_w) if wrist_w is not None else BIG, taper * kb) / 2.0
    Lmid = L - xk
    # finger centres across the knuckle line (index on the thumb side)
    ys, y = [], ts * kb / 2
    for k in range(4):
        ys.append(y - ts * fws[k] / 2)
        y -= ts * fws[k]
    if tips is not None:
        lens = [max(L - xk - float(tips[k]), 0.3 * Lmid) for k in range(4)]
    else:
        lens = [Lmid * OPEN_LEN[k] for k in range(4)]
    sp = float(spread)
    fing, tipc, cens, kns = [], [], [], []
    for k in range(4):
        kx = xk - OPEN_KN[k] * L
        base = P(kx - 0.12 * Lmid, ys[k])
        ang_k = ts * (1.5 - k) * (sp if sp else 1.0)       # a hint of fan even together
        d0 = P(math.cos(math.radians(ang_k)), math.sin(math.radians(ang_k)))
        # curling: the fingers bend toward the palm (foreshortened: shorter), with only a
        # little sideways sweep toward the little finger; their tips stay in one smooth row
        cl = -ts * 0.45 * float(curl) * (0.7 + 0.3 * k / 3.0)
        lk = (lens[k] + 0.12 * Lmid) * (1.0 - 0.45 * math.sin(math.radians(min(float(curl), 80.0))))
        cen = _bend(base, d0, lk - 0.45 * fws[k], cl, n=12)
        fing.append(_digit(cen, np.linspace(fws[k] + 0.9, (0.84 if sp else 0.90) * fws[k], len(cen))))
        tipc.append(cen[-1])
        cens.append(cen)
        kns.append(P(kx, ys[k]))
    tipr = [0.45 * fws[k] * (0.84 if sp else 0.90) / 0.9 for k in range(4)]
    if sp:
        # apart: only the webs at their roots join them (a quarter of the way up)
        webs = shapely.union_all([shapely.union(fing[k], fing[k + 1]).convex_hull.intersection(
            _behind(cens[k][3], cens[k][-1] - cens[k][0])) for k in range(3)])
    else:
        webs = _webs(fing, cens)
    fingers = shapely.union_all(fing + [webs])
    tipz = shapely.union_all([Point(*q).buffer(tipr[k] + 2.6, quad_segs=12) for k, q in enumerate(tipc)])
    fingers = _junction_smooth(fingers, tipz, r=1.6 if sp else 2.0)

    # the palm: one convex mass from the wrist to the knuckle row, the hypothenar swelling
    kx0, kx3 = xk - OPEN_KN[0] * L, xk - OPEN_KN[3] * L
    hyp_r = 0.20 * kb
    hyp_c = P(0.42 * xk, -ts * (0.5 * (ww + kb / 2) - hyp_r + 0.02 * kb))
    edge_i = P(kx0 - 0.10 * Lmid, ys[0] + ts * (fws[0] / 2 - 2.0))
    edge_l = P(kx3 - 0.16 * Lmid, ys[3] - ts * (fws[3] / 2 - 2.0))
    palm = shapely.union_all([
        Point(-stub, -ww + 2.0).buffer(2.0), Point(-stub, ww - 2.0).buffer(2.0),
        Point(*edge_i).buffer(2.0, quad_segs=8), Point(*edge_l).buffer(2.0, quad_segs=8),
        Point(*hyp_c).buffer(hyp_r, quad_segs=16)]).convex_hull
    # the thumb: CMC low on the thumb side; a straight metacarpal in the thenar mound,
    # then the free part opening thumb_deg° off the index edge, its last joint bending back
    root = P(0.10 * L, ts * (ww - 0.11 * kb))
    web_x = 0.36 * L + 0.10 * xk                   # the V's bottom: about mid-palm
    Lt = L * float(thumb_len)
    a0 = math.radians(float(thumb_deg))
    d_free = P(math.cos(a0), ts * math.sin(a0))
    # the metacarpal runs along the thumb-side edge to the web, the free part turns out
    mcp = P(web_x - 0.02 * L, ts * (kb / 2 + 0.02 * kb))
    L1 = float(np.hypot(*(mcp - root)))
    L2 = max(Lt - L1, 0.62 * lens[1])
    L2 = min(L2, 0.70 * lens[1])                   # its free part ≈ half the middle finger (+ the joint)
    L2 *= 1.0 - 0.25 * math.sin(math.radians(min(float(curl), 80.0)))
    bend_t = -ts * 8.0                             # the last joint bends back a little toward the fingers
    cen2 = _bend(mcp, d_free, L2, bend_t, n=10)
    cen1 = np.linspace(root, mcp, 6)
    cen_t = np.vstack([cen1[:-1], cen2])
    wt = np.concatenate([np.linspace(0.38 * kb, 0.30 * kb, 5),
                         0.29 * kb - 0.06 * kb * np.linspace(0.0, 1.0, len(cen2)) ** 0.8])
    thumb = _digit(cen_t, wt)
    tip_t = cen_t[-1]
    # the thenar mound: from the thumb's root into the palm and the wrist (no notch)
    mound = 0.45 * root + 0.55 * mcp + P(0.0, ts * 0.02 * kb)    # the thenar swells a little past the metacarpal
    thenar = shapely.union_all([Point(*root).buffer(0.20 * kb, quad_segs=12),
                                Point(*mound).buffer(0.165 * kb, quad_segs=12),
                                Point(*(mcp - d_free * 0.04 * L)).buffer(0.14 * kb, quad_segs=12),
                                Point(*P(-stub, ts * (ww - 2.0))).buffer(2.0)]).convex_hull
    body = shapely.union_all([fingers, palm, thenar])
    hand_ = shapely.union_all([body, thumb])
    keep = tipz.union(Point(*tip_t).buffer(0.12 * kb + 2.6, quad_segs=12))
    if sp:
        keep = keep.union(shapely.union_all([shapely.union(fing[k], fing[k + 1]).convex_hull.difference(
            _behind(cens[k][3], cens[k][-1] - cens[k][0])) for k in range(3)]))
    # the palm's edges run smoothly into the outer fingers (no knob at a finger's root)
    between = shapely.union_all([shapely.union(fing[k], fing[k + 1]).convex_hull.difference(
        _behind(cens[k][len(cens[k]) // 3], cens[k][-1] - cens[k][0])) for k in range(3)])
    # the V between the thumb's free part and the index finger (kept open: only its bottom rounds)
    webz = Polygon([tuple(mcp - d_free * 0.06 * L), tuple(tip_t + d_free * 0.1 * kb),
                    tuple(tipc[0])]).buffer(0.06 * kb)
    hand_ = _junction_smooth(hand_, keep.union(between).union(webz), r=0.16 * kb)
    # the web between thumb and index: a wide V with a round bottom
    hand_ = _junction_smooth(hand_, keep.union(shapely.box(-BIG, -BIG, BIG, BIG).difference(webz)), r=0.07 * kb)
    hand_ = _clean(hand_, r_open=1.2, r_close=1.0)
    inner = C.Frag()
    lines_ = []
    if not sp:
        for k in (1, 2, 3):
            ca, cb = cens[k - 1], cens[k]
            n_ = min(len(ca), len(cb))
            wa, wb = fws[k - 1], fws[k]
            mid = (ca[:n_] * wb + cb[:n_] * wa) / (wa + wb)
            ext = mid[-1] + _unit(mid[-1] - mid[-2]) * 9.0
            m2 = np.vstack([ext, mid[::-1]])
            # from the notch back toward the knuckles, stopping a little short (staggered)
            fl = 0.5 * (lens[k - 1] + lens[k])
            keep_len = float(np.hypot(*(ext - mid[-1]))) + (1.0 - OPEN_STOP[k - 1]) * fl \
                - float(np.hypot(*(mid[0] - mid[-1]))) * 0.0
            acc, out = 0.0, [m2[0]]
            for p0, p1 in zip(m2[:-1], m2[1:]):
                s = float(np.hypot(*(p1 - p0)))
                if acc + s >= keep_len:
                    out.append(p0 + (p1 - p0) * (keep_len - acc) / max(s, 1e-9))
                    break
                out.append(p1)
                acc += s
            lines_ += _notch_lines(np.array(out), hand_)
    inner += _lines_frag(lines_, "finger")
    if (view == "palm") if palm_crease is None else palm_crease:
        # the thenar crease ('life line'): from just inside the web between thumb and index,
        # round the thumb's mound toward the wrist, its hollow facing the thumb
        clear_ = MEDIUM + GAP_MARK + 0.4
        zone = hand_.buffer(-clear_)
        others = [LineString(q) for q in lines_ if len(q) >= 2]
        if others:
            zone = zone.difference(shapely.union_all(others).buffer(clear_))
        web_v = P(web_x + 0.02 * L, ts * (kb / 2 - 0.02 * kb))
        Lc = 0.35 * xk
        start = web_v + P(0.02 * L, -ts * 0.17 * kb)        # inside the palm, below the web
        end = start + P(-0.90 * Lc, -ts * 0.05 * Lc)        # toward the wrist
        ctrl = (start + end) / 2 + P(0.0, -ts * 0.30 * Lc)  # bowing away from the thumb: hollow toward it
        pts = _qbez(start, ctrl, end, 20)
        lines_c = [q for q in _open_line(pts, zone, start_on=False) if len(q) >= 2]
        lines_c = [max(lines_c, key=lambda q: LineString(q).length)] if lines_c else []
        inner += _lines_frag(lines_c, "crease")
    M, Mf = _rigid(at, angle, mirror_x=False)
    hand_s = _xf(hand_, M)
    inner_s = inner.transformed(Mf)
    u = _unit(_vec(M, P(-1.0, 0.0)))
    drawn = None if hand is None else str(hand).upper()[:1]
    meta = {"kind": "flat", "inner": inner_s, "view": view, "hand": drawn, "size": L}
    return Hand(Part(hand_s, C.Frag(), outline(hand_s) + inner_s, meta),
                Part(_xf(thumb, M), C.Frag(), C.Frag(), {"merged": True}), P(at), 2 * ww, u, float(stub))


def open_hand(at, angle=-90.0, *, size, hand="R", view="back", spread=0.0, curl=0.0, thumb_deg=40.0,
              thumb_len=0.46, stub=HAND_STUB, wrist_w=None, **kw) -> Hand:
    """An open hand of the figure's ``hand`` ('L'|'R') seen from ``view``
    ('back'|'palm'), wrist at ``at``, fingers pointing ``angle``; ``size`` =
    ``hand_size(face)``. ``spread``° apart (0: together), ``curl``° softly
    closing. A thin front door to ``flat``."""
    return flat(at, angle, size=size, hand=hand, view=view, spread=spread, curl=curl, thumb_deg=thumb_deg,
                thumb_len=thumb_len, stub=stub, wrist_w=wrist_w, **kw)


def hand5(at, angle=-90.0, pose="wrap", *, size, hand="R", view="back", curl=0.0, spread=0.0,
          grip_w=22.0, sleeve=None, wrist_w=None, stub=HAND_STUB) -> Hand:
    """The shared five-digit court hand: one smoothed silhouette, either hand
    and either view, sized from the face (pass ``hand_size(face)``).

    ``pose`` is ``wrap`` (a cylindrical shaft centred on ``at``), ``cup``
    (fingers scallop around the lower rim of an orb whose diameter is
    ``grip_w``; the rim has a small proportional minimum for an open thumb
    web), ``rest`` (flat against the body), ``hold_flat`` (thumb
    lightly opposed to a flat object of width ``grip_w``), or ``open``.
    ``angle`` is the shaft axis for ``wrap`` and the wrist-to-fingertip
    direction for the other poses. For non-wrap poses ``at`` is the wrist;
    for wrap it is the centre of the shaft at the grip.

    ``curl`` adjusts finger bend/wrap (0–60°); ``spread`` fans them and opens
    the cup scallop (0–18°), outward for either hand and view. ``grip_w`` is
    shaft width for wrap and the held-object diameter/width for cup/hold_flat;
    cup uses a minimum rim
    diameter of 0.72 × ``size`` to keep the thumb web open. ``view`` is ``back`` or
    ``palm``; ``hand`` is the figure's anatomical ``L`` or ``R``. The thumb
    leaves from the palm edge on an open V and ends beside the index tip,
    never across the four-finger band. At most three short MEDIUM lines are
    drawn, with the finger lines starting clear of the tip notches and at
    least 4.2 px of paper between them. Crowded lines are shortened or omitted.

    When ``sleeve`` is a Part or region, the returned Hand carries the merged
    hand+sleeve Part and one continuous outer outline; its cuff is a colour
    edge. Otherwise call ``result.with_sleeve(sleeve)`` to create that Part.
    The hand stores its inner lines, fingertip/notch zones, and a rebuild
    callback in the established Hand contract. Grips default to ``halo=0``
    in ``Hand.add_to`` so held shafts run under the fingers without paper
    rings.
    """
    pose = str(pose).lower()
    if pose not in {"wrap", "cup", "rest", "hold_flat", "open"}:
        raise ValueError("hand5 pose must be wrap, cup, rest, hold_flat, or open")
    view = str(view).lower()
    if view not in {"back", "palm"}:
        raise ValueError("hand5 view must be back or palm")
    hand = str(hand).upper()[:1]
    if hand not in {"L", "R"}:
        raise ValueError("hand5 hand must be L or R")
    size = float(size)
    if size <= 0:
        raise ValueError("hand5 size must be positive")
    curl = min(max(float(curl), 0.0), 60.0)
    spread = min(max(float(spread), 0.0), 18.0)
    grip_w = max(float(grip_w), 0.0)
    if pose in {"wrap", "cup", "hold_flat"} and grip_w <= 0.0:
        raise ValueError(f"hand5 {pose} needs positive grip_w")
    hb = HAND_K * size
    object_radius = grip_w / 2.0
    object_width = min(grip_w, 0.50 * size) if pose == "hold_flat" else grip_w
    object_height = min(22.0, 0.28 * size) if pose == "hold_flat" else 0.0
    thumb_side = -1.0 if (hand == "R") == (view == "back") else 1.0
    is_wrap = pose == "wrap"
    rot = float(angle) + (90.0 if is_wrap else 0.0)
    M, Mf = _rigid(at, rot, mirror_x=False)
    ys = np.linspace(-0.3375 * hb, 0.3375 * hb, 4)
    ys = list(ys[::-1] if thumb_side > 0 else ys)
    if is_wrap:
        # Enough pitch for open webs even after the silhouette is stroked.
        ys = [y * (0.525 / 0.3375) for y in ys]
    fan_side = -thumb_side  # digit order reverses with the visible thumb side
    widths = (0.19, 0.205, 0.20, 0.18)
    lengths = (0.94, 0.99, 1.0, 0.87)
    centerlines = []
    digits = []
    tips = []
    tip_radii = []

    if is_wrap:
        a = grip_w / 2.0
        # The palm quad is behind the staff; four separate tapered centrelines
        # cross the shaft and turn only a little around its far edge.
        for i, y in enumerate(ys):
            fw = widths[i] * hb
            y_shift = fan_side * (i - 1.5) * (spread / 18.0) * 0.035 * hb
            root = P(0.43 * hb + (i in (0, 3)) * 0.025 * hb, y + y_shift)
            tip_y = y + y_shift + fan_side * (i - 1.5) * (0.012 + 0.03 * spread / 18.0) * hb
            tip = P(-a - (0.055 + 0.025 * math.sin(math.radians(curl))) * hb
                    - 0.012 * hb * lengths[i], tip_y)
            ctrl = P(-a - (0.19 + 0.10 * math.sin(math.radians(curl))) * hb,
                     y + y_shift + fan_side * (i - 1.5) * 0.018 * hb)
            cen = _qbez(root, ctrl, tip, 18)
            digit = _digit(cen, np.linspace(fw * 0.88, fw * 0.80, len(cen)))
            digits.append(digit)
            centerlines.append(cen)
            tips.append(cen[-1])
            tip_radii.append(fw * 0.40)

        # A tapered palm quad joins the four bases. Its heel grows into a real
        # wrist on the forearm side, not a boxed-off finger block.
        palm = Polygon([
            (0.26 * hb, -0.60 * hb), (0.72 * hb, -0.62 * hb),
            (1.10 * hb, -0.42 * hb), (1.18 * hb, 0.12 * hb),
            (0.89 * hb, 0.62 * hb), (0.29 * hb, 0.60 * hb),
        ]).buffer(1.3, quad_segs=10).buffer(-1.3, quad_segs=10)
        thumb_fan = 1.5 * (spread / 18.0) * 0.065 * hb
        thumb_root = P(0.39 * hb, thumb_side * 0.68 * hb)
        thumb_mcp = P(0.02 * hb, thumb_side * (0.90 * hb + thumb_fan))
        thumb_tip = P(-a - 0.075 * hb, thumb_side * (0.76 * hb + thumb_fan))
        thumb_cen = np.vstack([
            _qbez(thumb_root, P(0.22 * hb, thumb_side * (0.83 * hb + thumb_fan)), thumb_mcp, 12)[:-1],
            _qbez(thumb_mcp, P(-0.20 * hb, thumb_side * (0.84 * hb + thumb_fan)), thumb_tip, 14),
        ])
        thumb = _digit(thumb_cen, np.linspace(0.18 * hb, 0.12 * hb, len(thumb_cen)))
        wrist = P(0.96 * hb, 0.16 * hb)
        wrist_dir = P(1.0, 0.45)
        width_default = 0.95 * hb
        # The thumb lobe is kept on the palm side, outside the four-finger band.
        thumb_distal = thumb.difference(palm.buffer(-0.1))
        finger_band = shapely.union_all(digits)
        # Three shallow V webs at the roots, never a separate digit drawn on top.
        web_lines = []
        for i in range(3):
            gap_y = (ys[i] + ys[i + 1]) / 2.0
            start_x = 0.40 * hb
            end_x = 0.80 * hb
            if end_x > start_x + 4.0:
                web_lines.append(LineString([(start_x, gap_y), (end_x, gap_y)]))
        object_center = P(0.0, 0.0)
    else:
        # Open-family poses share one palm quad and the same four anatomical
        # finger centrelines. Cup tips use a true circular lower-rim profile.
        x_kn = 0.48 * size
        wrist = P(0.0, 0.0)
        wrist_dir = P(-1.0, 0.0)
        width_default = 0.95 * hb
        object_center = (P(0.88 * size, thumb_side * (0.80 * hb - object_height / 2.0))
                         if pose == "hold_flat" else P(1.08 * size, 0.0))
        base_spread = math.radians(spread)
        curl_rad = math.radians(curl)
        for i, y in enumerate(ys):
            side_from_mid = (i - 1.5) / 1.5
            fw = widths[i] * hb
            root = P(x_kn - (0.014 * hb if i in (0, 3) else 0.0), y * 0.94)
            # A slight anatomical fan remains at spread=0; explicit spread
            # adds to it while leaving room between the fingertip lobes.
            fan = fan_side * side_from_mid * (base_spread / 2.0 + math.radians(2.0))
            direction = P(math.cos(fan), math.sin(fan))
            if pose == "cup":
                radius = max(object_radius, 0.36 * size)
                object_radius = radius
                object_center = P(1.08 * size, 0.0)
                tip_y = min(max(y * (1.08 + 0.12 * spread / 18.0), -0.82 * radius), 0.82 * radius)
                # Let each tapered tip overlap the orb just enough that its
                # outline meets the rim without a paper sliver at the contact.
                tip_x = (object_center[0] - math.sqrt(max(radius * radius - tip_y * tip_y, 0.0)) + 1.5
                         - 0.10 * hb * math.sin(math.radians(curl)))
                tip = P(tip_x, tip_y)
                ctrl = P(root[0] + 0.68 * (tip_x - root[0]), (root[1] + tip_y) / 2)
                cen = _qbez(root, ctrl, tip, 18)
            else:
                palm_to_tip = size * max(lengths[i] - 0.48, 0.36)
                palm_to_tip *= 1.0 - 0.16 * math.sin(curl_rad)
                end = root + direction * palm_to_tip
                bend = -thumb_side * curl * (0.22 + 0.12 * i / 3.0)
                cen = _bend(root, direction, float(np.hypot(*(end - root))), bend, n=18)
            # Light knuckle rhythm: middle/index extend farther than the little
            # finger; every digit tapers into a rounded fingertip.
            taper = np.linspace(fw * 0.92, fw * 0.78, len(cen))
            digit = _digit(cen, taper)
            digits.append(digit)
            centerlines.append(cen)
            tips.append(cen[-1])
            tip_radii.append(fw * 0.39)
        if pose == "cup":
            palm_half = 0.455 * hb
            # The hand contacts only the orb's lower edge: scallops follow its
            # circle instead of standing up like a picket fence over its face.
            palm = Polygon([
                (-stub, -0.22 * hb), (0.12 * size, -palm_half),
                (x_kn - 0.04 * size, -palm_half), (x_kn + 0.04 * size, 0.0),
                (x_kn - 0.04 * size, palm_half), (0.12 * size, palm_half),
                (-stub, 0.22 * hb),
            ]).buffer(2.0, quad_segs=10).buffer(-2.0, quad_segs=10)
            root = P(0.24 * size, thumb_side * 0.42 * hb)
            mcp = P(0.42 * size, thumb_side * 0.57 * hb)
            thumb_tip_y = thumb_side * 0.66 * radius
            thumb_tip = P(object_center[0] - math.sqrt(max(radius * radius - thumb_tip_y * thumb_tip_y, 0.0)) - 1.2,
                          thumb_tip_y)
            thumb_controls = (P(0.32 * size, thumb_side * 0.50 * hb),
                              P(object_center[0] - 0.10 * radius, thumb_side * 0.64 * radius))
        else:
            palm_half = 0.45 * hb
            palm = Polygon([
                (-stub, -0.23 * hb), (0.22 * size, -0.43 * hb),
                (x_kn - 0.02 * size, -palm_half), (x_kn + 0.035 * size, -0.31 * hb),
                (x_kn + 0.05 * size, 0.31 * hb), (x_kn - 0.02 * size, palm_half),
                (0.22 * size, 0.43 * hb), (-stub, 0.23 * hb),
            ]).buffer(2.0, quad_segs=10).buffer(-2.0, quad_segs=10)
            if pose == "hold_flat":
                root = P(0.28 * size, thumb_side * 0.28 * hb)
                thumb_tip_x = object_center[0] - object_width / 2.0 + 1.2
                thumb_tip_y = object_center[1] + thumb_side * object_height / 2.0
                mcp = P(0.49 * size, thumb_side * 0.80 * hb)
                thumb_tip = P(thumb_tip_x, thumb_tip_y)
                thumb_controls = (P(0.37 * size, thumb_side * 0.67 * hb),
                                  (mcp + thumb_tip) / 2.0)
            else:
                root = P(0.16 * size, thumb_side * 0.16 * hb)
                mcp = P(0.27 * size, thumb_side * 0.25 * size)
                thumb_tip = P(0.37 * size, thumb_side * 0.31 * size)
                thumb_controls = (P(0.23 * size, thumb_side * 0.21 * size),
                                  P(0.36 * size, thumb_side * 0.30 * size))
        thumb_cen = np.vstack([
            _qbez(root, thumb_controls[0], mcp, 12)[:-1],
            _qbez(mcp, thumb_controls[1], thumb_tip, 14),
        ])
        thumb = _digit(thumb_cen, np.linspace(0.24 * hb, 0.135 * hb, len(thumb_cen)))
        thumb_distal = thumb.difference(palm.buffer(-0.1))
        finger_band = shapely.union_all(digits)
        if pose not in {"cup", "hold_flat"}:
            object_center = P(0.0, 0.0)
        web_lines = []
        for i in range(0 if pose == "cup" else 3):
            pa, pb = tips[i], tips[i + 1]
            # Interior lines approach each notch from the palm and stop at least
            # 7.3 px clear, so no rounded line cap sits in the web.
            mid = (ys[i] + ys[i + 1]) / 2.0
            start_x = 0.56 * size
            end_x = 0.72 * size
            if end_x - start_x >= 5.0:
                web_lines.append(LineString([(start_x, mid), (end_x, mid)]))
            elif pose != "cup":
                # The ordinary poses have room for short palm-side creases.
                start = P(0.54 * size, mid)
                end = P(0.69 * size, mid)
                web_lines.append(LineString([start, end]))
        if view == "palm" and pose != "cup":
            # The thenar crease replaces the outermost finger separation so
            # palm views stay within the three-line maximum.
            web_lines = web_lines[:2]
            if is_wrap:
                web_lines.append(LineString([
                    (0.34 * hb, thumb_side * 0.39 * hb),
                    (0.15 * hb, thumb_side * 0.19 * hb),
                ]))
            else:
                web_lines.append(LineString([
                    (0.20 * size, thumb_side * 0.13 * hb),
                    (0.39 * size, thumb_side * 0.22 * hb),
                ]))

    # The palm joins the four digit roots; the thumb is a distinct centreline
    # from the palm edge, then all five digit masses become one closed region.
    raw = shapely.union_all([palm, *digits, thumb])
    tip_keepout = shapely.union_all([
        Point(*tip).buffer(radius * 1.5 + 1.0, quad_segs=12)
        for tip, radius in zip(tips, tip_radii)
    ] + [Point(*thumb_cen[-1]).buffer(0.075 * hb + 2.0, quad_segs=12)])
    softened = raw.buffer(1.25, quad_segs=10).buffer(-1.25, quad_segs=10)
    if pose == "cup":
        # Fill narrow proximal webs under the rim without erasing the tips.
        softened = raw.buffer(CONTOUR / 2 + 0.4, quad_segs=12).buffer(
            -CONTOUR / 2 - 0.4, quad_segs=12)
    local_shape = _clean(raw.union(softened.difference(tip_keepout)), r_open=0.35, r_close=0.35)
    if local_shape.geom_type != "Polygon":
        local_shape = _biggest(local_shape)

    # Keep interior marks wholly inside the silhouette with generous paper
    # clearance; lines are short MEDIUM strokes and never enter a fingertip web.
    inner_lines = []
    inner_zone = local_shape.buffer(-MEDIUM / 2 - GAP_MARK - 0.4)
    for candidate in web_lines:
        clipped = candidate.intersection(inner_zone)
        for accepted in inner_lines:
            # Preserve the minimum after path coordinates round to 0.001 px.
            clipped = clipped.difference(accepted.buffer(MEDIUM + GAP + 0.002))
        pieces = [g for g in _lines_of(clipped) if g.length >= 5.0]
        pieces = [g for g in pieces
                  if all(g.distance(accepted) >= MEDIUM + GAP for accepted in inner_lines)]
        if pieces:
            piece = max(pieces, key=lambda g: g.length)
            # On wrap the start is the palmward endpoint. On the other poses
            # the line enters from the finger web and is trimmed away from it.
            if is_wrap:
                coords = np.asarray(piece.coords)
                if coords[0, 0] < coords[-1, 0]:
                    coords = coords[::-1]
                line_g = LineString(coords)
            else:
                line_g = piece
            inner_lines.append(line_g)
    inner = C.Frag()
    if view == "palm" and pose != "cup" and len(inner_lines) > 3:
        inner_lines = inner_lines[:3]
    for ln in inner_lines[:3]:
        inner += line(C.polyline_d(np.asarray(ln.coords)), MEDIUM, role="finger")

    shape = _xf(local_shape, M)
    inner_s = inner.transformed(Mf)
    thumb_s = _xf(thumb, M)
    distal_s = _xf(thumb_distal, M)
    band_s = _xf(finger_band, M)
    tips_s = [_xf(Point(*tip), M).coords[0] for tip in tips] + [_xf(Point(*thumb_cen[-1]), M).coords[0]]
    notches_local = []
    for i in range(3):
        # The open valleys between the four fingertip lobes.
        notches_local.append((tips[i] + tips[i + 1]) / 2)
    notches_s = [_xf(Point(*p), M) for p in notches_local]
    transformed_lines = [_xf(ln, M) for ln in inner_lines[:3]]
    W = P(at) if not is_wrap else _xf(Point(*wrist), M).coords[0]
    u = _unit(_vec(M, wrist_dir))
    ww = float(wrist_w) if wrist_w is not None else width_default
    meta = {
        "kind": "hand5", "pose": pose, "hand": hand, "view": view, "size": size,
        "curl": curl, "spread": spread, "grip_w": grip_w, "thumb_side": thumb_side,
        "inner": inner_s, "digit_centerlines": [_xf(LineString(cen), M) for cen in centerlines]
        + [_xf(LineString(thumb_cen), M)],
        "digit_tips": tips_s, "digit_tip_radii": tip_radii + [0.075 * hb],
        "notch_points": notches_s, "inner_lines": transformed_lines,
        "thumb_centerline": _xf(LineString(thumb_cen), M), "thumb_distal": distal_s,
        "finger_band": band_s, "tipzone": shapely.union_all([
            Point(*point).buffer(1.5 * radius, quad_segs=12)
            for point, radius in zip(tips_s[:4], tip_radii)
        ]), "heelzone": shape.buffer(0.01),
        "object_center": _xf(Point(*object_center), M).coords[0],
        "object_radius": object_radius,
        "object_width": object_width,
        "object_height": object_height,
    }
    # Use a common wrist direction and a rebuild closure so Hand.tucked can
    # preserve the pose if it needs to follow a sleeve's cuff edge.
    def build_part(direction):
        nonlocal wrist_dir
        wrist_dir = _unit(_to_local(P(at) + P(direction), at, rot, False))
        current_u = _unit(_vec(M, wrist_dir))
        part_meta = {**meta, "rebuild": rebuild, "wrist_dir": current_u}
        base = Part(shape, C.Frag(), outline(shape) + inner_s, part_meta)
        return base, current_u

    def rebuild(direction):
        base, _u = build_part(direction)
        if sleeve is not None:
            base = Hand(base, Part(thumb_s, C.Frag(), C.Frag(), {"merged": True}),
                        W, ww, _u, float(stub)).with_sleeve(sleeve)
        return base

    part, u = build_part(_vec(M, wrist_dir))
    hand_obj = Hand(part, Part(thumb_s, C.Frag(), C.Frag(), {"merged": True}),
                    W, ww, u, float(stub))
    if sleeve is not None:
        hand_obj = Hand(hand_obj.with_sleeve(sleeve), hand_obj.thumb,
                        W, ww, u, float(stub))
    return hand_obj


def hand(pose, *args, **kw) -> Hand:
    """One door to every hand: ``pose`` 'grip' (``fist``), 'pinch'
    (``pinch``), 'cup' (``cup``), 'open' (``open_hand``) or 'flat'
    (``flat``); the rest is passed on."""
    fn = {"grip": fist, "fist": fist, "pinch": pinch, "hold": pinch, "cup": cup, "orb": cup,
          "open": open_hand, "flat": flat, "gesture": open_hand}[pose]
    return fn(*args, **kw)


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


_DEFAULT_TUNIC_CLEAR_BELOW = object()


def tunic(s: LensSpec = LensSpec(), *, pattern_kind="karst_flooded",
          clear_below=_DEFAULT_TUNIC_CLEAR_BELOW, **kw) -> Part:
    """The lens tunic (paper), patterned (default: §G.12 karst voids whose
    largest cavities are flooded jade — the aquifer). By default pattern
    stops above the band; set ``clear_below`` to a chosen y to move the
    cutoff, or ``None`` to omit the band cutoff for a continuous court."""
    g = lens(s)
    reg = R(circle(g["cL"], g["R"])).intersection(R(circle(g["cR"], g["R"])))
    reg = reg.intersection(box(0, 0, 750, 545))
    lines = outline(reg)
    fills = C.Frag()
    if pattern_kind:
        prg = reg.buffer(-(MEDIUM / 2 + 3.2))
        yb = (T.BAND_Y0 - 0.55 - 3.2) if clear_below is _DEFAULT_TUNIC_CLEAR_BELOW else clear_below
        if yb is not None:
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
    visible_to: float | None = 511.0  # segment detail stops above this y; None disables the band cutoff


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
    if s.visible_to is not None:
        lines += clip_in(seg_f, box(0, 0, 2000, s.visible_to - 4.5 - MEDIUM))
    else:
        lines += seg_f
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


def band_guard(sc: "Scene", rank="K", cx=AX, *, band_y0=T.BAND_Y0, center_y=T.CY):
    """Add the rank medallion's invisible occluder to a Scene (add it LAST).
    The system clips band-mode court art at ``band_y0`` and masks a disc round the medallion;
    a line cut by that disc just above y 511 would end < 3 px from the band
    rule (a QA 12 failure). The guard (the mask disc plus a strip down from
    ``band_y0 - 7`` as wide as the disc) makes everything behind it stop ≥ 3 px
    above the rule there, and fills stop 3 px short. Jacks have no
    medallion: nothing to guard. A full/continuous ``Scene(rank=None)`` has
    no band and is left untouched."""
    if sc.rank is None:
        return sc
    from deck import frames as _F
    rm = _F.medallion_radius(rank)
    if not rm:
        return sc
    rmask = rm + 4.2
    g = U(circle((cx, center_y), rmask + 0.6),
          box(cx - rmask - 3.0, band_y0 - 7.0, cx + rmask + 3.0, center_y + 40))
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
