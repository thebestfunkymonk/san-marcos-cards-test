"""A♠ · the Lion of the Source — the winged lion of St. Mark in moleca
(brief §G.2, §H.13). Owned by the A♠; started from deck/motifs/lion.py and
redrawn.

Frontal and secular: never a halo, a book or an inscription (§G.2, §J.1).
All gold FINE monoline. The right half is drawn and mirrored, so the emblem
is exactly bilateral.

Stacking, front to back: paws > face > mane tiers (inner over outer) >
vent > wings. Whatever passes behind something ends ON the front contour's
centreline (a T-junction), so the front line's own stroke closes the joint.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import frames as F
from deck import tokens as T
from deck.motifs import forms as FM
from deck.motifs.core import Frag, clip, dot, polar, polyline_d, region, sample_d, stroke, vesica_d
from inkkit import geom as G

GOLD = T.FOIL
FINE = T.FINE
GAP = 4.2
PITCH = FINE + GAP                    # 6.3: the closest legal centre-to-centre spacing of two FINE lines
CX = 375.0
HEAD = (375.0, 262.0)
FACE_R = 30.0
INSET = 12.0 + FINE / 2               # §H.13: every stroke EDGE keeps 12 px from the silhouette


# =============================================================================
# helpers
# =============================================================================
def S(d, role="", style="ornament") -> Frag:
    return stroke(d, FINE, style=style, color=GOLD, role=role)


def P(x, y, sg=1):
    """Head-local point (y down) -> card coordinates; sg=-1 mirrors."""
    return np.array((HEAD[0] + sg * x, HEAD[1] + y))


def spline(pts, **kw) -> str:
    return FM.arc_spline([np.asarray(p, float) for p in pts], **kw)[0]


def mirror(f: Frag) -> Frag:
    """``f`` plus its mirror image about the spade's axis."""
    return f + f.mirror_x(CX)


def mirror_shape(g):
    return shapely.union_all([g, shapely.affinity.scale(g, -1, 1, origin=(CX, 0))])


def poly(pts):
    g = Polygon(np.asarray(pts, float))
    return g if g.is_valid else g.buffer(0)


def shape_of(d: str):
    """Filled region of a closed centreline path (union of its subpaths)."""
    rings = [p for p, _ in sample_d(d, 0.25)]
    return shapely.union_all([poly(r) for r in rings if len(r) > 2])


def behind(f: Frag, front) -> Frag:
    """``f`` lies behind ``front`` (a region bounded by the front line's
    centreline): its lines end ON that centreline (T-junction)."""
    if front is None or front.is_empty:
        return f
    return clip(f, front, inside=False)


def spade():
    return region(F.ace_pip_d("S"))


def spade_inset(extra: float = 0.0):
    """Where stroke CENTRELINES may run: the silhouette inset by 12 px + half
    a FINE stroke (+ ``extra``)."""
    g = spade().buffer(-(INSET + extra), quad_segs=64)
    return max(getattr(g, "geoms", [g]), key=lambda x: x.area)


# =============================================================================
# face
# =============================================================================
FACE = dict(
    # right half, head-local (y down), face radius 30. A lion, not a man: a
    # long, broad nose bridge flowing from a strong level brow, eyes slanted
    # up and out, a wide nose pad, and the split upper lip (ω) of a big cat.
    brow=[(20.5, -12.6), (12.5, -12.0), (6.0, -8.6), (4.9, -1.5), (7.4, 6.8)],     # brow into the bridge
    eye=dict(c=(13.2, -3.4), half=6.2, h=4.0, tilt=10.0, pupil=(0.3, -0.3)),
    nose=[(-7.4, 6.8), (7.4, 6.8), (2.4, 12.4), (-2.4, 12.4)],                   # the trapezoid nose pad
    philtrum=[(0.0, 12.4), (0.0, 17.8)],
    lip=[(0.0, 17.8), (6.0, 20.8), (11.8, 18.2)], lip_h=(25.0, -40.0),           # a closed mouth, the ω
)


def face(spec=None) -> Frag:
    """The frontal face (§G.2): face circle, almond eyes with pupils, the brow
    flowing into the nose bridge, the trapezoid nose and the closed ω mouth.
    Every mark keeps >= 3 px of ground from every other it does not join."""
    F_ = dict(FACE, **(spec or {}))
    f = S(G.circle_d(*HEAD, FACE_R), "face")
    f += S(polyline_d([P(*p) for p in F_["nose"]], closed=True), "nose", style="point")
    f += S(polyline_d([P(*p) for p in F_["philtrum"]]), "mouth")
    half = Frag()
    half += S(spline([P(*p) for p in F_["brow"]]), "brow")
    h0, h1 = F_["lip_h"]
    half += S(spline([P(*p) for p in F_["lip"]], h_start=h0, h_end=h1), "mouth")
    e = F_["eye"]
    c = P(*e["c"])
    u = FM.unit(-e["tilt"])
    half += S(vesica_d(c - u * e["half"], c + u * e["half"], e["h"]), "eye", style="point")
    half += dot(c[0] + e["pupil"][0], c[1] + e["pupil"][1], 4.2, color=GOLD, role="pupil")
    return f + mirror(half)


# =============================================================================
# mane: three tiers of pointed locks, each tier behind the one inside it
# =============================================================================
MANE = dict(
    # (cusp r — hidden behind the tier in front, tip r, phase offset in locks)
    tiers=((27.0, 37.0, 0.0), (32.0, 48.0, 0.5), (42.0, 60.0, 0.0)),
    n=12, skew=0.85, bow=0.22, hollow=0.10,
)


def _tuft(p, tip, q, bow, hollow=0.0):
    """A pointed lock from cusp p to cusp q through its tip: the leading flank
    a convex arc, the trailing flank convex (``hollow`` 0) or hollow (> 0) —
    a thorn / shark-fin lock that reads as hair flowing toward q."""
    c1 = float(np.hypot(*(tip - p)))
    c2 = float(np.hypot(*(q - tip)))
    return FM.scallop_arc(p, tip, bow * c1) + FM.scallop_arc(tip, q, (bow if hollow == 0 else -hollow) * c2, move=False)


def _ray_exit(region_, ang, r_max=200.0):
    """Distance from the head centre along screen angle ``ang`` to where the
    ray first leaves ``region_``."""
    c = np.asarray(HEAD)
    ln = LineString([c, c + FM.unit(ang) * r_max])
    it = ln.intersection(region_.exterior if region_.geom_type == "Polygon"
                         else shapely.MultiLineString([g.exterior for g in region_.geoms]))
    ds = [float(np.hypot(*(np.asarray(g_.coords)[0] - c))) for g_ in getattr(it, "geoms", [it]) if not g_.is_empty]
    return min(ds) if ds else 0.0


def mane(spec=None, insert=None) -> Frag:
    """Right half built lock by lock (screen angles -90 = crown .. 90 = chin),
    mirrored. A lock straddling the axis is symmetric (its tip on the axis);
    the others lean downstream (``skew``), so the mane flows from the crown
    down both sides. Each tier lies behind the ones inside it, and its cusps
    sit exactly ON the contour in front (so two neighbouring locks spring
    from one point of that line, never side by side)."""
    sp = dict(MANE, **(spec or {}))
    n = sp["n"]
    step = 360.0 / n
    front = Point(*HEAD).buffer(FACE_R, quad_segs=128)
    f = Frag()
    fronts = []
    for (rc, rt, ph) in sp["tiers"]:
        half = Frag()
        polys = []
        cusp = lambda ang: polar(*HEAD, _ray_exit(front, ang), ang)
        a = -90.0 + (ph - 1) * step if ph else -90.0
        while a < 90.0 - 1e-6:
            b = a + step
            if a < -90.0 + 1e-6 and b > -90.0 + 1e-6 and ph:          # straddles the crown: symmetric
                tip = polar(*HEAD, rt, -90.0)
                q = cusp(b)
                d = FM.scallop_arc(tip, q, sp["bow"] * float(np.hypot(*(q - tip))))
                pts = sample_d(d, 0.25)[0][0]
                polys.append(poly(np.vstack([[HEAD[0], HEAD[1]], pts])))
            elif b > 90.0 + 1e-6:                                       # straddles the chin: symmetric
                tip = polar(*HEAD, rt, 90.0)
                p = cusp(a)
                d = FM.scallop_arc(p, tip, sp["bow"] * float(np.hypot(*(tip - p))))
                pts = sample_d(d, 0.25)[0][0]
                polys.append(poly(np.vstack([pts, [HEAD[0], HEAD[1]]])))
            else:
                p, q = cusp(a), cusp(b)
                tip = polar(*HEAD, rt, a + sp["skew"] * step)
                d = _tuft(p, tip, q, sp["bow"], sp["hollow"])
                pts = sample_d(d, 0.25)[0][0]
                polys.append(poly(np.vstack([pts, [HEAD[0], HEAD[1]]])))
            half += S(d, "mane", style="point")
            a = b
        ring = mirror(half)
        f += behind(ring, front)
        front = front.union(mirror_shape(shapely.union_all(polys)))
        if insert is not None and len(fronts) == insert[0]:
            fr, shp = insert[1], insert[2]
            f += behind(fr, front)
            front = front.union(shp)
        fronts.append(front)
    f.meta["silhouette"] = front
    f.meta["fronts"] = fronts
    return f


EARS = dict(on=True, at=47.0, half=13.0, h=10.5, inner=0.5, point=0.35)


def ears(spec=None):
    """Two ears standing out of the mane at ±``at``° from the crown: each a
    rounded, slightly pointed lobe rising off the face circle, with an inner
    fold. Returns (frag, filled shape)."""
    sp = dict(EARS, **(spec or {}))
    cx, cy = HEAD
    a = -90.0 + sp["at"]
    p0 = polar(cx, cy, FACE_R, a - sp["half"])
    p1 = polar(cx, cy, FACE_R, a + sp["half"])
    tip = polar(cx, cy, FACE_R + sp["h"], a + 2.0)
    d = spline([p0, tip, p1], h_start=a - sp["half"] - 90.0 + 40.0)
    q0 = polar(cx, cy, FACE_R, a - sp["half"] * sp["inner"])
    q1 = polar(cx, cy, FACE_R, a + sp["half"] * sp["inner"])
    qt = polar(cx, cy, FACE_R + sp["h"] * 0.5, a + 1.0)
    di = spline([q0, qt, q1])
    f = S(d, "ear") + S(di, "ear")
    shp = poly(np.vstack([sample_d(d, 0.25)[0][0], [[cx, cy]]]))
    return mirror(f), mirror_shape(shp)


def head(face_spec=None, mane_spec=None, ear_spec=None):
    """Face, ears and mane. Returns (frag, silhouette)."""
    fc = face(face_spec)
    ins = None
    if dict(EARS, **(ear_spec or {}))["on"]:
        er, esh = ears(ear_spec)
        ins = (0, er, esh)                         # the ears stand behind the inner tier, in front of the rest
    mn = mane(mane_spec, ins)
    return mn + fc, mn.meta["silhouette"]


# =============================================================================
# forepaws
# =============================================================================
PAWS = dict(x=17.0, w=24.0, top=290.0, sole=341.0, toes=3, toe_sag=3.4, splay=3.0, heel=5.0)


def paws(spec=None):
    """The two forepaws, frontal, side by side under the beard, resting on
    the vent's far rim: each a forearm coming down from behind the mane that
    swells into a broad paw; the toes bulge along the sole, parted by short
    grooves. Returns (frag, filled shape of both paws)."""
    sp = dict(PAWS, **(spec or {}))
    cx = CX + sp["x"]
    hw = sp["w"] / 2
    top, sole = sp["top"], sp["sole"]
    n = sp["toes"]
    yb = sole - sp["toe_sag"]                       # the toes' cusp line
    xa, xb = cx - hw - sp["splay"] * 0.4, cx + hw + sp["splay"]
    ya = yb - sp["heel"] - 8.0                      # where the sides start to swell into the paw
    xs = np.linspace(xa, xb, n + 1)
    # inner side: straight down, then swelling out; toes; outer side back up
    d = spline([(cx - hw + 2.0, top), (cx - hw + 1.0, ya), (xa, yb)], h_start=92.0, h_end=100.0)
    for i in range(n):
        d += FM.scallop_arc((xs[i], yb), (xs[i + 1], yb), -sp["toe_sag"], move=False)
    d += spline([(xb, yb), (cx + hw + 1.0, ya), (cx + hw - 1.0, top)], h_start=-80.0, h_end=-94.0).replace("M", "L", 1)
    f = S(d, "paw")
    for x in xs[1:-1]:
        f += S(polyline_d([(x, yb), (x, yb - 5.5)]), "toe")
    shp = shape_of(d + "Z")
    return mirror(f), mirror_shape(shp)


# =============================================================================
# wings
# =============================================================================
LOBE = np.array((448.6, 342.3))        # the right lobe's circle centre (D1 spade)
RIM_R = 66.6                           # the lobe's inset radius (stroke centrelines)


def rim_pt(a, r=RIM_R):
    return LOBE + r * FM.unit(a)


def right_contour(a_from: float = 130.0, y_to: float = 150.0) -> np.ndarray:
    """The inset contour on the right, from the lobe's underside (screen
    angle ``a_from`` about the lobe centre) round the lobe and up the upper
    edge toward the apex (stopping at ``y_to``). Dense, base -> apex; inward
    is to the LEFT of travel."""
    r = np.asarray(shapely.segmentize(spade_inset().exterior, 0.25).coords)[:-1]
    q = rim_pt(a_from)
    i0 = int(np.argmin(np.hypot(*(r - q).T)))
    ang = lambda q_: math.atan2(q_[1] - LOBE[1], q_[0] - LOBE[0])
    step = 1 if ang(r[(i0 + 8) % len(r)]) < ang(r[i0]) else -1
    out = [r[i0]]
    i = i0
    for _ in range(len(r)):
        i = (i + step) % len(r)
        if r[i][1] < y_to or r[i][0] < CX + 0.5:
            break
        out.append(r[i])
    return np.asarray(out)


def feather_hw(L, W, tip_len, base_len=0.0):
    """Half-width along a feather: parallel sides W wide, an ogive tip
    ``tip_len`` long (a rounded point), optionally a rounded base."""
    s_ = W / 2.0
    c = tip_len
    Rr = (c * c + s_ * s_) / (2 * s_)

    def hw(s):
        s = np.asarray(s, float)
        out = np.full_like(s, s_)
        u = s - (L - tip_len)
        m = u > 0
        out[m] = np.sqrt(np.maximum(Rr * Rr - u[m] ** 2, 0.0)) - (Rr - s_)
        if base_len > 0:
            mb = s < base_len
            v = (base_len - s[mb]) / base_len
            out[mb] = s_ * np.sqrt(np.maximum(1 - v ** 2, 0))
        return np.maximum(out, 0.0)
    return hw


def feather(mid, W, tip_len, *, hatch=1, rake=55.0, base_len=0.0, hw=None) -> Frag:
    """A vesica flight feather on a (curved) shaft: the outline, the shaft,
    and ONE vane half-hatched with barbs raked toward the tip (§G.2)."""
    mid = np.asarray(mid, float)
    L = G.Curve(mid).length
    f = FM.leaf(mid, hw=hw or feather_hw(L, W, tip_len, base_len), hatch=hatch, color=GOLD, rake=rake,
                rake_mode="local", midrib="full", midrib_trim=(0.0, 0.16), midrib_min_hw=FINE + GAP)
    f.meta["shape"] = poly(f.meta["outline"])
    return f


def arc_pts(p, q, sag):
    return sample_d(FM.scallop_arc(np.asarray(p, float), np.asarray(q, float), sag), 0.25)[0][0]


def curl(mid: np.ndarray, y_curl: float, R: float, turn: float) -> np.ndarray:
    """Cut a rising shaft where it climbs past ``y_curl`` and continue it on a
    circle of radius ``R`` turning LEFT (toward the axis) by ``turn``°."""
    k = int(np.argmax(mid[:, 1] < y_curl)) if (mid[:, 1] < y_curl).any() else len(mid) - 1
    base = mid[:k + 1]
    t = base[-1] - base[-3]
    h = math.atan2(t[1], t[0])
    nl = np.array([math.cos(h - math.pi / 2), math.sin(h - math.pi / 2)])
    c = base[-1] + nl * R
    a0 = math.atan2(base[-1][1] - c[1], base[-1][0] - c[0])
    angs = a0 - np.radians(np.linspace(0, turn, 60))[1:]
    arc = np.column_stack([c[0] + R * np.cos(angs), c[1] + R * np.sin(angs)])
    return np.vstack([base, arc])


WING = dict(
    # the leading edge, a SICKLE (§G.2): from the shoulder behind the mane it
    # runs out ``run`` px, turns up through a radius-``R`` elbow onto the
    # spade's upper edge (heading ``up[0]``, the inset contour's direction),
    # rises ``up[1]`` px along it and curls in over the head (``curl`` =
    # radius, turn) until its tip tucks behind the mane's crown — so it has
    # no free end (``terminal`` adds the §B.2 Ø6.3 dot if it ever does)
    shoulder=(412.0, 303.0), h0=-12.0, run=38.0, R=22.0, up=(-131.7, 72.0), curl=(19.0, 96.0), terminal=False,
    # three covert rows inside the sickle: (offset, pitch, depth)
    rows=((6.3, 10.0, 4.2), (16.9, 11.0, 4.8), (28.1, 12.0, 5.4)),
    fillet=14.0,
    # five flight feathers from under the arm: (arc length of the base along
    # the sickle, tip angle on the lobe rim about LOBE, width)
    feathers=((6.0, 100.0, 15.0), (15.0, 77.0, 16.0), (24.0, 54.0, 17.0), (33.0, 31.0, 17.0), (42.0, 8.0, 16.0)),
    tuck=5.0, f_tip=1.25, f_hatch=1, f_bow=-3.0, rake=48.0,
)


def sickle(sp=None) -> np.ndarray:
    """The wing's leading edge (dense points, shoulder -> curl)."""
    sp = dict(WING, **(sp or {}))
    h0 = sp["h0"]
    h_up, L_up = sp["up"]
    Rc, tc = sp["curl"]
    turns = [(sp["run"], 0.0), (math.radians(abs(h_up - h0)) * sp["R"], h_up - h0), (L_up, 0.0),
             (math.radians(tc) * Rc, -tc)]
    _, pts, _ = FM.arc_path(sp["shoulder"][0], sp["shoulder"][1], h0, turns)
    return pts


def wing(spec=None) -> Frag:
    """The RIGHT wing (the left is its mirror), §G.2 / §H.13: the leading edge
    is a sickle that rises from the shoulder behind the mane, turns up onto
    the spade's upper edge and curls in over the head toward the apex; three
    rows of scalloped coverts line its inside; five vesica flight feathers,
    each half-hatched, fan from under the arm down into the lobe, tips on the
    lobe's rim, each tucked behind its outer neighbour.
    meta: shape (filled region), cover (the covert zone)."""
    sp = dict(WING, **(spec or {}))
    ins = spade_inset()
    E = sickle(sp)
    ec = G.Curve(E)
    ss = np.linspace(0.0, ec.length, len(E))
    nrm = ec.normal_s(ss)                     # left of travel = inside the sickle (toward the head)
    arm = S(polyline_d(E), "arm")
    if sp["terminal"]:                        # §B.2: a free end takes a Ø6.3 terminal
        arm += dot(*E[-1], T.TERMINAL_D, color=GOLD, role="terminal")
    zone = None
    rows = Frag()
    for i, (off, pitch, depth) in enumerate(sp["rows"]):
        # a true inner offset, filleted: where the elbow / curl is tighter than
        # the row's offset the row turns the corner on a radius-``fillet`` arc
        # instead of folding back on itself (scallops would cross there)
        rr = sp["fillet"]
        o1 = LineString(E).offset_curve(-(off + rr), quad_segs=32, join_style="round")
        o1 = max(getattr(o1, "geoms", [o1]), key=lambda g: g.length)
        base = np.asarray(o1.offset_curve(rr, quad_segs=32, join_style="round").coords)
        d, _, _ = FM.scallop_row(base, pitch, depth, side=1, start=(pitch / 2 if i % 2 else 0.0))
        row = S(d, "covert")
        rows += behind(row, zone) if zone is not None else row
        low = sample_d(d, 0.25)[0][0]
        rz = poly(np.vstack([E, low[::-1]]))
        zone = rz if zone is None else zone.union(rz)
    cov_zone = zone
    # everything on the inner side of the arm: the feathers come out from under it
    arm_side = poly(np.vstack([E, (ec.at_s(ss) + nrm * 40.0)[::-1]]))
    out = Frag()
    cover = None
    for (s0, a_tip, w) in reversed(sp["feathers"]):       # outer first = in front
        b = ec.at_s(s0) + ec.normal_s(np.array([s0]))[0] * sp["tuck"]
        tip = rim_pt(a_tip, RIM_R - 0.5)
        mid = arc_pts(b, tip, sp["f_bow"])
        fe = feather(mid, w, sp["f_tip"] * w, hatch=sp["f_hatch"], rake=sp["rake"])
        out += behind(fe, cover) if cover is not None else fe
        cover = fe.meta["shape"] if cover is None else cover.union(fe.meta["shape"])
    out = behind(out, arm_side.union(cov_zone))
    res = clip(arm + rows + out, ins.buffer(0.3))
    shape = cov_zone.union(cover)
    res.meta.update(shape=shape.intersection(ins.buffer(0.3)), cover=cov_zone)
    return res


# =============================================================================
# print-clearance pass (§I.12)
# =============================================================================
_SHAPELY_CAP = {"round": "round", "butt": "flat", "square": "square"}
_SHAPELY_JOIN = {"round": "round", "miter": "mitre", "bevel": "bevel"}


def _pieces(f: Frag):
    """Every sub-path of every mark as its own inked piece (true width, caps
    and joins): (mark index, sub-path index, role, shapely geometry)."""
    out = []
    for i, m in enumerate(f.marks):
        for j, (pts, closed) in enumerate(G.flatten(m.d, 0.05)):
            pts = np.asarray(pts, float)
            if len(pts) < 2:
                continue
            if m.kind == "fill":
                g = Polygon(pts).buffer(0)
            else:
                ln = shapely.LinearRing(pts) if closed and len(pts) >= 3 else LineString(pts)
                g = ln.buffer(m.w / 2, quad_segs=8, cap_style=_SHAPELY_CAP.get(m.cap, "round"),
                              join_style=_SHAPELY_JOIN.get(m.join, "round"), mitre_limit=max(m.miter, 1.0))
            if not g.is_empty:
                out.append((i, j, m.role, g))
    return out


def drop_specks(f: Frag, min_len: float = 4.0, roles=None) -> Frag:
    """Drop the open sub-paths shorter than ``min_len`` that clipping leaves
    behind (a 2 px stub of a ripple between two feathers is a flaw, not a
    line); ``roles`` limits it to marks of those roles."""
    from dataclasses import replace as _rep
    marks = []
    for m in f.marks:
        if m.kind != "stroke" or (roles is not None and m.role not in roles):
            marks.append(m)
            continue
        subs = [(np.asarray(p, float), c) for p, c in G.flatten(m.d, 0.05)]
        # also drop the tiny degenerate loops clipping can leave at a cusp
        # (an OPEN sub-path that returns to its start: a 10 px "tadpole")
        keep = [(p, c) for p, c in subs
                if c or (G.Curve(p).length >= min_len
                         and not (np.hypot(*(p[0] - p[-1])) < 0.5 and G.Curve(p).length < 3 * min_len))]
        if len(keep) == len(subs):
            marks.append(m)
        elif keep:
            marks.append(_rep(m, d="".join(polyline_d(p, closed=c) for p, c in keep)))
    return Frag(marks, f.meta)


def prune_hatch(f: Frag, *, gap: float = 3.05, axis: float = CX, roles=("hatch",)) -> Frag:
    """Where a hatch line comes within ``gap`` of another piece it does not
    touch (typically: two lines ending on the SAME contour from its two sides
    — a vent ripple passing behind a feather, a feather tucked behind its
    neighbour — or a hatch end grazing a line beside the contour), drop the
    hatch line: the hatching stops short of the busy joint, as an engraver's
    would, and every mark keeps §I.12's 3 px of ground from every mark it does
    not join. Removals are mirrored about ``axis`` so the emblem stays exactly
    bilateral. Repeats until no hatch line is in conflict."""
    for _ in range(12):
        pcs = _pieces(f)
        geoms = [p[3] for p in pcs]
        tree = shapely.STRtree(geoms)
        a_idx, b_idx = tree.query(geoms, predicate="dwithin", distance=gap)
        drop = set()
        for a, b in zip(a_idx, b_idx):
            if a >= b:
                continue
            pa, pb = pcs[a], pcs[b]
            if (pa[0], pa[1]) == (pb[0], pb[1]):
                continue
            d = pa[3].distance(pb[3])
            if d < 1e-6 or d >= gap:
                continue
            ha, hb = pa[2] in roles, pb[2] in roles
            if not (ha or hb):
                continue
            victim = pa if (ha and (not hb or pa[3].area <= pb[3].area)) else pb
            drop.add((victim[0], victim[1]))
        if not drop:
            break
        # mirror the removals: the partner of a dropped hatch line is the one
        # whose mirror image lies on it
        hatch_pcs = [p for p in pcs if p[2] in roles]
        for (i, j) in list(drop):
            g = next(p[3] for p in pcs if (p[0], p[1]) == (i, j))
            gm = shapely.affinity.scale(g, -1, 1, origin=(axis, 0))
            for p in hatch_pcs:
                if (p[0], p[1]) not in drop and p[3].intersection(gm).area > 0.8 * gm.area:
                    drop.add((p[0], p[1]))
        marks = []
        for i, m in enumerate(f.marks):
            subs = [(pts, c) for j, (pts, c) in enumerate(G.flatten(m.d, 0.05)) if (i, j) not in drop]
            if not subs:
                continue
            if len(subs) == len(G.flatten(m.d, 0.05)):
                marks.append(m)
                continue
            d = "".join(polyline_d(np.asarray(p, float), closed=c) for p, c in subs)
            from dataclasses import replace as _rep
            marks.append(_rep(m, d=d))
        f = Frag(marks, f.meta)
    return f

