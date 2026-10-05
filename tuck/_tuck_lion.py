"""The tuck front's hero: the winged lion of St. Mark ANDANTE (brief §G.3, §H.20).

Redrawn (third pass) for heraldic clarity at every size — the silhouette
must say "winged lion" at 192 px before any detail is read:

* HEAD in true profile, walking to the viewer's LEFT: a heavy brow, the long
  and nearly straight bridge of a lion's nose ending in a broad, blunt nose
  leather, a deep square muzzle with the whisker pad marked off, the lip
  line running back to a corner under the eye, a firm chin; an almond eye
  set high with the lion's tear-line running down beside the nose; a small
  round ear half sunk in the mane.  One eye (profile).
* MANE the largest single mass, in SCALLOPED ARCS (§G.3): four rows of
  lopsided flame-locks (``forms.lock_row``) wrapping the face from the
  forehead back over the crown, down the nape to the withers and round under
  the chest; each inner row lies in front of the next, so the locks shingle.
* WING upswept from the withers BEHIND the mane — never from the head: a
  double-lined leading edge rising and raking back, three rows of scalloped
  coverts, five raked, half-hatched vesica PRIMARIES and two secondaries
  laid back over the body.  All tips point up and back (to the tail).
* BODY (fourth pass, AD note: "he stands rather than walks"): deep chest
  (hidden in the mane), level back under the wing, tucked flank, round croup.
  Two MEDIUM form lines model it (§B.2 interiors): the SHOULDER (the triceps
  arc from under the wing root to the chest line) and the HAUNCH (loin → flank
  fold, the front of the thigh).  Between them the underside — belly and far
  flank — is HALF-HATCHED (FINE, 7.0) below a FINE terminator, so the body
  carries the density of the mane and wing; the lit near side stays open.
* LEGS in STRIDE (a walk, not a stance): the NEAR FORE advanced and flexed at
  the carpus, stepping onto the 3-course half-hatched limestone LEDGE (the
  Balcones scarp) — it passes in front of the outer (chest) row of the mane,
  from under the inner rows, so the forearm shows; the FAR FORE raked back
  under the chest, supporting; the FAR HIND swinging forward under the belly;
  the NEAR HIND pushing off in the spring's 3 ripple lines (the cat's Z:
  stifle forward, gaskin raked back to a sharp hock, cannon raked back into
  the water).  Far legs half-hatched, all body hatch mirrored (the figure
  walks left; it crosses the MEDIUM form lines square) so four legs read,
  never two.
* TAIL hanging from the croup in a long curve behind the thigh and curling
  UP into a flame tuft whose eye is the Ø6.3 circle terminal.

No halo, book or inscription (§G.2, §J.1).  FINE gold foil line throughout
(ledge rules and hatch included), the two MEDIUM form lines excepted.
Coordinates: local, the LENS centre is the origin (the lens is 330 × 440).
Layering is cut-paper, back to front: a part's lines end ON the contour of
the part in front (T-junction: the occluding region is shrunk 0.5 px so the
ends overlap the front contour's stroke — never a hair-gap).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, Point, Polygon

from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms as FM
from inkkit import geom as G

FINE = T.FINE
HAIR = T.HAIRLINE
GOLD = T.FOIL
GAP = C.MIN_CLEAR
LENS = (330.0, 440.0)
LENS_INNER = 6.6        # the lens cartouche inner rule (centre to centre), as on the front
T_JOIN = 0.5            # T-junction overlap into the front contour


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def V(p):
    return np.asarray(p, float)


def spl(pts, h0=None, h1=None, headings=None):
    """Smooth G1 chain of circular arcs through ``pts`` → (d, dense pts)."""
    d, P, _ = FM.arc_spline([V(p) for p in pts], h0, h1, headings=headings)
    return d, P


def S(d, w=FINE, style="ornament", role="line"):
    return C.stroke(d, w, style=style, color=GOLD, role=role)


def poly(*arrs):
    P = np.vstack([np.atleast_2d(np.asarray(a, float)) for a in arrs])
    g = Polygon(P).buffer(0)
    if g.geom_type != "Polygon":
        g = max(getattr(g, "geoms", [g]), key=lambda x: x.area)
    return g


def behind(f: C.Frag, front) -> C.Frag:
    """Occlude ``f`` by ``front`` (T-junction, ends overlapping the front's contour)."""
    if front is None or front.is_empty:
        return f
    return C.occlude(f, front.buffer(-T_JOIN))


def stack(items, prune=False):
    """[(Frag, region), ...] FRONT to back → (Frag, union region).  With
    ``prune`` the lines of each back item that emerge alongside the lines
    already drawn in front are pruned where they hug them (< 4.2 px)."""
    from tuck import _tuck_common as K
    out, regs = C.Frag(), []
    for fr, rg in items:
        if regs:
            fr = behind(fr, shapely.union_all(regs))
            if prune and len(out):
                fr = K.prune_parallel(fr, out.shape(), min_run=11.0)
        out += fr
        if rg is not None and not rg.is_empty:
            regs.append(rg)
    return out, (shapely.union_all(regs) if regs else Polygon())


def stack_gapped(items, gap=GAP):
    """[(Frag, region), ...] FRONT to back → (Frag, union region): each back
    item is BROKEN ``gap`` px clear of everything in front of it (§B.2
    interlace gap), so shingled feathers never run alongside each other
    closer than 4.2 px."""
    out, regs = C.Frag(), []
    for fr, rg in items:
        if regs:
            fr = C.cut(fr, shapely.union_all(regs).buffer(FINE / 2), gap)
        out += fr
        if rg is not None and not rg.is_empty:
            regs.append(rg)
    return out, (shapely.union_all(regs) if regs else Polygon())


def drop_specks(f, min_len):
    from dataclasses import replace
    out = []
    for m in f.marks:
        if m.kind != "stroke":
            out.append(m)
            continue
        keep = [(p, cl) for p, cl in G.flatten(m.d, 0.05) if cl or (len(p) > 1 and G.Curve(p).length >= min_len)]
        if keep:
            out.append(replace(m, d="".join(C.polyline_d(p, closed=cl) for p, cl in keep)))
    return C.Frag(out, f.meta)


def _circle3(p, q, r):
    ax, ay = p
    bx, by = q
    cx, cy = r
    dd = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / dd
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / dd
    return np.array([ux, uy]), math.hypot(ax - ux, ay - uy)


def arc3(p, q, r, move=True):
    """Exact circular arc through three points p → q → r."""
    p, q, r = V(p), V(q), V(r)
    c, R = _circle3(p, q, r)
    cr = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    a0 = math.atan2(p[1] - c[1], p[0] - c[0])
    a2 = math.atan2(r[1] - c[1], r[0] - c[0])
    sweep = 1 if cr > 0 else 0
    span = (a2 - a0) % (2 * math.pi) if sweep else (a0 - a2) % (2 * math.pi)
    large = 1 if span > math.pi else 0
    head = f"M{p[0]:.3f} {p[1]:.3f}" if move else ""
    return head + f"A{R:.3f} {R:.3f} 0 {large} {sweep} {r[0]:.3f} {r[1]:.3f}"


def _strip_map(cv: G.Curve):
    L = cv.length
    p0, p1 = cv.at_s(0.0), cv.at_s(L)
    t0, t1 = cv.tangent_s(0.0), cv.tangent_s(L)

    def f(uv):
        uv = np.atleast_2d(np.asarray(uv, float))
        u, v = uv[:, 0], uv[:, 1]
        uc = np.clip(u, 0, L)
        P = cv.at_s(uc)
        Nn = cv.normal_s(uc)
        lo, hi = u < 0, u > L
        P = np.where(lo[:, None], p0 + np.outer(u, t0), P)
        P = np.where(hi[:, None], p1 + np.outer(u - L, t1), P)
        n0 = np.array([t0[1], -t0[0]])
        n1 = np.array([t1[1], -t1[0]])
        Nn = np.where(lo[:, None], n0, Nn)
        Nn = np.where(hi[:, None], n1, Nn)
        return P + Nn * v[:, None]
    return f


# ---------------------------------------------------------------------------
# the design table (lens-local px; lens centre = origin, y down)
# ---------------------------------------------------------------------------
FIG_DY = 12.0           # the whole figure + ground sit this much below the design table (wider lens above)
LEDGE_TOP = 112.0 + FIG_DY
COURSES = (12.0, 19.0, 12.0)
SCARP_X = 18.0
WATER = tuple(y + FIG_DY for y in (121.0, 132.5, 146.0))
RIPPLE = dict(amp=1.8, wl=22.0)

# the head is designed in HEAD-LOCAL px with the eye at the origin, then scaled as a unit
# (path data only; strokes stay FINE) and placed with the eye at EYE
EYE = (-97.0, -64.0)
HEAD_K = 1.14
HEAD_LOCAL = dict(
    brow=[(9.0, -24.0), (-2.0, -22.5), (-12.0, -16.0)],
    bridge=[(-12.0, -16.0), (-24.5, -9.8), (-35.5, -2.6)],
    nose=[(-35.5, -2.6), (-39.8, 0.6), (-41.2, 6.2), (-38.8, 11.2)],
    lip=[(-38.8, 11.2), (-39.2, 18.2), (-35.6, 24.2), (-26.0, 26.8), (-15.0, 27.6), (-7.0, 28.2)],
    chin=[(-31.0, 26.2), (-29.4, 32.4), (-22.0, 36.4), (-8.0, 38.6), (7.0, 37.0)],
    eye=((-8.5, 0.8), (7.0, -2.6), 7.2),
    pupil=(0.6, -3.0),
    tear=[(-9.4, 3.0), (-13.4, 8.6), (-15.0, 13.6)],
    brow_line=[(-13.0, -7.8), (-1.5, -11.5), (10.5, -9.0)],
    pad=[(-23.5, -3.8), (-19.5, 7.5), (-22.5, 19.5)],
    whisker=[],
    nostril=[(-39.6, 5.0), (-35.4, 3.8), (-32.8, 7.2)],
    ear=[(12.0, -22.0), (11.0, -32.0), (18.5, -37.5), (26.0, -32.5), (25.0, -22.5)],
    ear_in=[(15.5, -28.5), (19.0, -32.8), (22.5, -29.0)],
    face_back=[(7.0, 37.0), (18.0, 18.0), (21.0, -2.0), (17.0, -16.0), (9.0, -24.0)],
)


def _hl(p):
    return (EYE[0] + p[0] * HEAD_K, EYE[1] + p[1] * HEAD_K)


def _hmap(v):
    if isinstance(v, list):
        return [_hl(p) for p in v]
    if isinstance(v, tuple) and len(v) == 3 and isinstance(v[2], (int, float)):
        return (_hl(v[0]), _hl(v[1]), v[2] * HEAD_K)
    if isinstance(v, tuple) and len(v) == 2:
        return _hl(v)
    return v


HEAD = {k: _hmap(v) for k, v in HEAD_LOCAL.items()}

# mane: four rows of lopsided locks, INNER first; each guide runs clockwise (forehead → crown →
# nape → withers → chest → under the chin); locks bulge outward (left of travel) and flow along it
MANE = dict(
    rows=[
        dict(guide=[(-106, -96), (-92, -106), (-72, -100), (-64, -80), (-63, -54), (-67, -30), (-77, -10),
                    (-92, 4), (-112, 12)], pitch=17.0, depth=13.5),
        dict(guide=[(-107, -113), (-90, -124), (-62, -120), (-45, -98), (-41, -68), (-43, -38), (-51, -8),
                    (-65, 18), (-86, 34), (-112, 38)], pitch=19.0, depth=17.0),
        dict(guide=[(-98, -131), (-84, -142), (-50, -142), (-26, -118), (-18, -84), (-18, -48), (-24, -12),
                    (-36, 22), (-56, 48), (-84, 62), (-114, 62), (-128, 52)], pitch=21.0, depth=18.0),
    ],
    skew=0.8, bow=0.1,
)

BODY = dict(
    # the topline behind the wing: level back, the croup falling to the tail root
    back=[(92, -41), (104, -38), (113, -32), (119, -22)],
    # the chest line from behind the elbow, rising into the tuck-up at the flank fold
    belly=[(66, 27), (48, 38), (22, 50), (-6, 56.5), (-40, 59.5), (-50, 60)],
    # MEDIUM form lines (brief §B.2 interiors): the back of the shoulder mass (triceps) sweeping down
    # from under the wing root to the elbow, and the front of the haunch from the loin to the flank fold
    shoulder=[(10, -16), (18, 6), (14, 28), (0, 46), (-18, 57.5)],
    haunch=[(88, -30), (76, -10), (69, 10), (66, 27)],
    # the terminator of the half-hatched underside: shoulder line → haunch line (belly + far flank)
    terminator=[(17.5, 16), (40, 12), (70.5, 4)],
    # NEAR FORE — advanced, flexed at the knee (carpus), stepping onto the ledge
    near_fore=dict(
        front=[(-72, 18), (-79, 38), (-86, 54), (-94, 67), (-100.5, 77), (-103, 84)],
        paw=[(-103, 84), (-102, 90), (-100, 95), (-104, 98.5), (-107, 102.5), (-108.3, 107.5), (-108.3, 112.0)],
        heel=[(-78.5, 112.0), (-78.5, 106), (-80, 98.5), (-82.5, 93)],
        back=[(-82.5, 93), (-84.5, 88.5), (-76, 84.5), (-65, 78), (-56.5, 73), (-50.5, 66), (-46.5, 57),
              (-44.5, 46), (-48, 30), (-54, 12)],
        toes=[[(-87.5, 112), (-88, 106)], [(-95, 112), (-95.5, 105.5)], [(-102, 112), (-102.5, 107)]]),
    # FAR FORE — the supporting leg, raked back under the chest (hatched)
    far_fore=dict(
        front=[(-42, 54), (-33, 78), (-26.5, 94), (-25, 101)],
        paw=[(-25, 101), (-30, 104), (-33, 108), (-33.5, 112.0)],
        heel=[(6.1, 112.0), (5.5, 106.5), (1.5, 101), (-3, 97)],
        back=[(-3, 97), (-8, 80), (-15, 52)],
        hatch_origin=(2.65, -2.65)),       # hatch phase: no slivers at the paw or the belly
    # NEAR HIND — pushing off in the ripples: stifle forward, gaskin raked back to a sharp hock, the
    # cannon raked back into the water (the cat's Z: femur forward, tibia back, cannon back)
    near_hind=dict(
        front=[(66, 27), (61, 42), (64, 55), (71, 67), (78, 78), (81, 86), (86, 102), (91.5, 121.5)],
        back=[(101.5, 121.5), (97, 104), (93.5, 88), (93, 79), (100, 64), (111, 48), (119, 30),
              (123, 8), (122, -8), (119, -22)],
        stifle=None),
    # FAR HIND — swinging forward under the belly (hatched)
    far_hind=dict(
        front=[(40, 38), (35, 56), (33, 76), (33, 96), (31, 121.5)],
        back=[(51, 121.5), (54, 102), (59, 87), (64, 75), (72, 64)],
        hatch_origin=(1.06, -1.06)),       # hatch phase: no slivers at the belly or the water
    tail=[(116, -22), (127, -38), (131, -56), (128, -73)],
    tail_w=7.6,
    tuft_spec=dict(len=24.0, hw=7.5, curl_r=4.8, curl_sweep=200.0),
    hatch_angle=-135.0,         # §B.2 45° (FINE, 7.0 pitch), mirrored for the figure walking left
    far_angle=-135.0,           # the far legs mirrored ("\\"): they read apart from the belly, and cross the
                                # paws' "/" fronts square (no slivers)
)

WING = dict(
    arm=[(-4, -48), (-8, -88), (-2, -128), (14, -162), (40, -190)],
    arm_band=8.5,
    covert_rows=(8.5, 17.0, 25.5, 34.0),
    covert_pitch=14.0,
    covert_sag=None,
    covert_u0=4.0,
    covert_ends=(0.97, 0.86, 0.72),
    # five SEPARATE primaries fanned from a centre behind the mane (so they never hug: >= 4.2 clear
    # between neighbours outside the coverts), tips up and raked back toward the tail
    fan=None,
    # shingled (front first): each back feather emerges beyond the one in front
    primaries=[((34, -150), (70, -190), 20.0, 6.0), ((36, -134), (92, -172), 22.0, 7.0),
               ((36, -118), (108, -150), 23.0, 8.0), ((34, -102), (116, -124), 23.0, 8.0),
               ((32, -86), (106, -100), 22.0, 8.0)],
    secondaries=[((28, -72), (100, -71), 20.0, 7.0), ((22, -58), (104, -52), 19.0, 6.0),
                 ((14, -46), (96, -34), 17.0, 5.0)],
    rake=52.0,
)


def _fan(spec):
    out = []
    O = V(spec["centre"])
    for a, Lk, w in zip(spec["angles"], spec["lengths"], spec["widths"]):
        u = FM.unit(a)
        b = O + u * spec["r0"]
        out.append((tuple(b), tuple(b + u * Lk), w, spec["bend"]))
    return out


# ---------------------------------------------------------------------------
# parts → (Frag, shapely region)
# ---------------------------------------------------------------------------
def head():
    d = HEAD
    prof_d, prof_P = spl(d["brow"] + d["bridge"][1:], None, None)
    nose_d, nose_P = spl(d["nose"])
    lip_d, lip_P = spl(d["lip"])
    f = S(prof_d, role="head") + S(nose_d, role="head") + S(lip_d, role="head")
    ch_d, ch_P = spl(d["chin"])
    f += S(ch_d, role="head")
    for key in ("tear", "brow_line", "pad", "nostril"):
        f += S(spl(d[key])[0], role="head")
    p0, p1, hgt = d["eye"]
    f += C.stroke(C.vesica_d(V(p0), V(p1), hgt), FINE, style="point", color=GOLD, role="eye")
    if d.get("pupil"):
        f += C.dot(*d["pupil"], 4.2, color=GOLD, role="pupil")       # hangs from the upper lid (touching)
    for p in d.get("whisker") or []:
        f += C.dot(*p, 4.2, color=GOLD, role="whisker")
    back_P = spl(d["face_back"])[1]
    region = poly(prof_P, nose_P, lip_P, ch_P[::1], back_P)
    ear_d, ear_P = spl(d["ear"])
    ear = S(ear_d, role="ear")
    # the ear stands in a small clearing of the mane: whatever lies behind it breaks 4.2 px clear
    return (f, region), (ear, poly(ear_P, V(EYE) + V((12.0, -14.0))).buffer(GAP + FINE + 0.6))


def mane_rows(front):
    """Rows of lopsided flame-locks, inner rows in front (T-junctions, lines
    of a back row pruned where they would hug the rows in front), the face in
    front of all.  → [(Frag, region)] INNER row first; each region is the
    whole area inside that row's locked line."""
    cfg = MANE
    out, regs = [], [front]
    drawn = C.Frag()
    for row in cfg["rows"]:
        _, gP = spl(row["guide"])
        d, cusps, peaks = FM.tuft_row(gP, row["pitch"], row["depth"], side=1, skew=cfg["skew"],
                                      bow=cfg["bow"])
        fr = S(d, style="point", role="mane")
        P = C.sample_d(d, 0.3)[0][0]
        reg = poly(P, V(EYE) + np.array([10.0, 5.0]))       # the row's locked line closed back through the head
        fr = behind(fr, shapely.union_all(regs))
        if len(drawn):
            from tuck import _tuck_common as K
            fr = K.prune_parallel(fr, drawn.shape(), min_run=11.0)
        drawn += fr
        out.append((fr, reg))
        regs.append(reg)
    return out


def mane(front):
    """The whole mane → (Frag, region)."""
    rows = mane_rows(front)
    f = C.Frag()
    for fr, _ in rows:
        f += fr
    return f, rows[-1][1].difference(front)


def _leg(spec, role, hatch=False, region_extra=None, angle=None):
    """A leg: contours ``front`` / ``paw`` / ``heel`` / ``back`` (FINE), toe
    grooves, small model lines; far legs half-hatched (FINE, 7.0).  The
    region closes across the top (hidden under the body) — through
    ``region_extra`` (points, e.g. the haunch form line) when given."""
    ds, Ps = [], []
    for k in ("front", "paw", "heel", "back"):
        if k in spec:
            d_, P_ = spl(spec[k])
            ds.append(d_)
            Ps.append(P_)
    f = C.Frag()
    for d_ in ds:
        f += S(d_, role=role)
    for t in spec.get("toes", []):
        f += S(spl(t)[0], role="toe")
    for k in ("dew", "hock", "stifle"):
        if spec.get(k):
            f += S(spl(spec[k])[0], role="model")
    reg = poly(*(([region_extra] if region_extra is not None else []) + Ps))
    if hatch:
        # ``hatch_origin``: a corner a hatch line runs through, so no line cuts a sliver off it
        f += C.hatch(reg, BODY["far_angle"] if angle is None else angle, T.HATCH_PITCH, color=GOLD, min_len=6.0,
                     origin=spec.get("hatch_origin"))
    return f, reg


def torso():
    """The barrel: topline, chest-and-belly line, the MEDIUM shoulder and
    haunch form lines, and the underside (belly + far flank) HALF-HATCHED
    below a FINE terminator, between the two form lines."""
    d = BODY
    back_d, back_P = spl(d["back"])
    bel_d, bel_P = spl(d["belly"])
    sh_d, sh_P = spl(d["shoulder"])
    hn_d, hn_P = spl(d["haunch"])
    f = S(back_d, role="body") + S(bel_d, role="body")
    f += S(sh_d, w=T.MEDIUM, role="form") + S(hn_d, w=T.MEDIUM, role="form")
    reg = poly(back_P, V((112.0, 20.0)), bel_P, V((-46.0, 50.0)), V((-40.0, -40.0)))
    # the barrel between the form lines (shoulder top → elbow, along the belly → flank fold, haunch up)
    x_sh = sh_P[-1][0]
    bel_seg = bel_P[::-1]
    bel_seg = bel_seg[bel_seg[:, 0] >= x_sh - 0.01]
    between = poly(sh_P, bel_seg, hn_P[::-1])
    _, ter_P = spl(d["terminator"])
    lower = C.split_region(between, ter_P, side=-1)
    ter = LineString(_extend(ter_P, 12.0)).intersection(between.buffer(0.01))
    for gg in ([ter] if ter.geom_type == "LineString" else list(getattr(ter, "geoms", []))):
        if gg.length > 4:
            f += S(C.polyline_d(np.asarray(gg.coords)), role="model")
    f += C.hatch(lower, d["hatch_angle"], T.HATCH_PITCH, color=GOLD, min_len=6.0, origin=d.get("hatch_origin"))
    return f, reg


def _extend(P, L):
    P = np.asarray(P, float)
    t0 = P[0] - P[1]
    t0 = t0 / np.hypot(*t0)
    t1 = P[-1] - P[-2]
    t1 = t1 / np.hypot(*t1)
    return np.vstack([P[0] + t0 * L, P, P[-1] + t1 * L])


def feather(base, tip, W, bend, *, hatch=-1, tip_frac=0.42):
    base, tip = V(base), V(tip)
    ch = tip - base
    h = math.degrees(math.atan2(ch[1], ch[0]))
    _, P, _ = FM.arc_path(base[0], base[1], h - bend / 2, [(float(np.hypot(*ch)), bend)])
    Lc = G.Curve(P).length

    def hw(s_, Lc=Lc, W=W):
        s_ = np.asarray(s_, float)
        return (W / 2) * np.clip(s_ / (0.14 * Lc), 0, 1) ** 0.5 * np.clip((Lc - s_) / (tip_frac * Lc), 0, 1) ** 0.8
    fe = FM.leaf(P, hw=hw, hatch=hatch, w=FINE, color=GOLD, rake=WING["rake"], rake_mode="local",
                 midrib_trim=(0.0, 0.12), midrib_min_hw=FINE + GAP)
    return fe, poly(fe.meta["outline"])


def _covert_rows(mp, u0, u_ends, rows, pitch, sag=None):
    f = C.Frag()
    last = None
    for i in range(len(rows) - 1):
        v0 = rows[i]
        v1 = v0 + sag if sag else rows[i + 1]
        us = np.arange(u0 + (pitch / 2 if i % 2 else 0.0), u_ends[i] - pitch * 0.5 + 1e-6, pitch)
        dd = []
        for j, u in enumerate(us):
            a, b = mp(np.array([[u, v0], [u + pitch, v0]]))
            pk = mp(np.array([[u + pitch / 2, v1]]))[0]
            dd.append(arc3(a, pk, b, move=(j == 0)))
        if dd:
            f += S("".join(dd), role="covert")
            last = "".join(dd)
    return f, last


def wing():
    """Near wing → (Frag, region)."""
    d = WING
    arm_d, arm_P = spl(d["arm"])
    cv = G.Curve(arm_P)
    L = cv.length
    sm = _strip_map(cv)

    def mp(uv):   # v toward the wing's inside (right of travel up the arm)
        uv = np.atleast_2d(uv)
        return sm(np.column_stack([uv[:, 0], -uv[:, 1]]))
    band = d["arm_band"]
    uu = np.linspace(0, L, 300)
    inner_P = mp(np.column_stack([uu, np.full_like(uu, band)]))
    rows = d["covert_rows"]
    cov, last = _covert_rows(mp, d["covert_u0"], [L * e for e in d["covert_ends"]], rows, d["covert_pitch"],
                             d.get("covert_sag"))
    lastrow = np.vstack([pp for pp, _ in C.sample_d(last, 0.3)])
    uu2 = np.linspace(-40, L + 40, 300)
    cov_reg = poly(mp(np.column_stack([uu2, np.full_like(uu2, -2.0)])), lastrow[::-1])
    spec = _fan(d["fan"]) if d.get("fan") else d["primaries"] + d.get("secondaries", [])
    feathers = [feather(b_, t_, w_, bd_) for (b_, t_, w_, bd_) in spec]
    prim, prim_reg = stack(feathers, prune=True)
    prim = drop_specks(prim, 4.0)
    # the wing's leading edge is its front: nothing of a feather shows in front of (left of) the arm
    top = arm_P[-1] + (arm_P[-1] - arm_P[-8]) / np.hypot(*(arm_P[-1] - arm_P[-8])) * 80
    front_of_arm = poly(arm_P, top, V((-200, -300)), V((-200, 40)), arm_P[0] + V((0, 40)))
    prim = behind(prim, front_of_arm)
    arm = S(arm_d, role="arm") + S(C.polyline_d(inner_P), role="arm")
    near = behind(prim, cov_reg) + cov + arm
    sil = shapely.union_all([prim_reg, cov_reg]).buffer(0.3)
    return near, sil


def tail():
    """A tube from the croup rising in an S and ending in a FLAME TUFT: the
    tube's two sides swell into a pointed brush (a vesica, one hair line
    inside it), and the brush's point curls over into a hook that ends in the
    Ø6.3 circle terminal.  → (Frag, region)."""
    d = BODY
    tail_d, tail_P = spl(d["tail"])
    cv = G.Curve(tail_P)
    hw_ = d["tail_w"] / 2
    L = cv.length
    ss = np.linspace(0, L, 200)
    taper = hw_ * (1 - 0.18 * ss / L)
    Nn = cv.normal_s(ss)
    A = cv.at_s(ss) + Nn * taper[:, None]
    B = cv.at_s(ss) - Nn * taper[:, None]
    E = tail_P[-1]
    t = cv.tangent_s(L)
    h_end = math.degrees(math.atan2(t[1], t[0]))
    tu = d["tuft_spec"]
    u = FM.unit(h_end)
    T_ = E + u * tu["len"]
    nA = (A[-1] - E) / np.hypot(*(A[-1] - E))
    nB = (B[-1] - E) / np.hypot(*(B[-1] - E))
    sideA_d, sideA_P = spl([A[-1], E + u * tu["len"] * 0.42 + nA * tu["hw"], T_], h_end + 8.0, None)
    sideB_d, sideB_P = spl([B[-1], E + u * tu["len"] * 0.42 + nB * tu["hw"], T_], h_end - 8.0, None)
    tb = sideB_P[-1] - sideB_P[-6]
    hB = math.degrees(math.atan2(tb[1], tb[0]))
    turn = C.Turtle(T_[0], T_[1], hB)
    turn.arc(tu["curl_r"], tu["curl_sweep"])
    hook = S(turn.d(), role="tail")
    dot = C.terminal(*turn.pos, color=GOLD)
    hair_d = spl([E - u * 2.0, E + u * tu["len"] * 0.45 + nB * 1.5, E + u * tu["len"] * 0.72])[0]
    brush = S(sideA_d, style="point", role="tail") + S(sideB_d, style="point", role="tail") + S(hair_d, role="tail")
    tube = S(C.polyline_d(A), role="tail") + S(C.polyline_d(B), role="tail")
    reg = shapely.union_all([poly(A, B[::-1]), poly(sideA_P, sideB_P[::-1])])
    return tube + brush + hook + dot, reg


def _ripple_pts(i, x0, x1):
    xs = np.linspace(x0, x1, 600)
    return np.column_stack([xs, WATER[i] + RIPPLE["amp"] * np.sin((xs - SCARP_X) / RIPPLE["wl"] * 2 * math.pi
                                                                  + i * 1.3)])


def ground(lens=LENS):
    """Ledge (3 courses: the thin ones hatched 45°, limestone joints in the
    thick one) and 3 ripple lines, lens-local.  → (Frag, water region (the
    ground under the first ripple line), lens polygon, inside)."""
    from deck.motifs.geometric import lens_geometry
    geo = lens_geometry(0.0, -lens[1] / 2, lens[1] / 2, lens[0])
    lens_poly = poly(C.sample_d(geo["d"], 0.5)[0][0])
    inside = lens_poly.buffer(-(LENS_INNER + FINE + GAP + 2.0))     # + 2: vesica tips' miters
    g = C.Frag()
    ys = [LEDGE_TOP]
    for h in COURSES:
        ys.append(ys[-1] + h)
    x_left = -lens[0]
    ledge_poly = shapely.box(x_left, ys[0], SCARP_X, ys[-1]).intersection(inside)
    lx0 = ledge_poly.bounds[0]
    g += C.stroke(C.polyline_d([(lx0, ys[0]), (SCARP_X, ys[0]), (SCARP_X, ys[-1])]), FINE, style="rule",
                  color=GOLD, role="ledge")
    for yv in ys[1:]:
        ln_ = LineString([(x_left, yv), (SCARP_X, yv)]).intersection(inside)
        if not ln_.is_empty:
            g += C.stroke(C.polyline_d(np.asarray(ln_.coords)), FINE, style="rule", color=GOLD, role="course")
    for (ya, yb) in ((ys[0], ys[1]), (ys[2], ys[3])):
        g += C.hatch(ledge_poly.intersection(shapely.box(x_left, ya, SCARP_X, yb)), -45.0, color=GOLD, min_len=10.0)
    for xj in (-34.0, -86.0):
        g += C.stroke(C.polyline_d([(xj, ys[1]), (xj, ys[2])]), FINE, style="rule", color=GOLD, role="joint")
    for i in range(3):
        pts = _ripple_pts(i, SCARP_X + 8 + 4 * i, lens[0] / 2)
        ln_ = LineString(pts).intersection(inside)
        for gg in ([ln_] if ln_.geom_type == "LineString" else list(getattr(ln_, "geoms", []))):
            if gg.length > 4:
                g += C.stroke(C.polyline_d(np.asarray(gg.coords)), FINE, color=GOLD, role="ripple")
    top = _ripple_pts(0, SCARP_X - 20, lens[0])
    water = Polygon(np.vstack([top, [(lens[0], lens[1]), (SCARP_X - 20, lens[1])]])).buffer(0)
    return g, water, lens_poly, inside


def parts():
    (hd, head_reg), (ear, ear_reg) = head()
    rows = mane_rows(head_reg)
    inner = C.Frag()
    for fr, _ in rows[:-1]:
        inner += fr
    mane_in = (inner, rows[-2][1].difference(head_reg))
    mane_out = (rows[-1][0], rows[-1][1].difference(head_reg))
    mn = inner + rows[-1][0]
    return dict(head=(hd, head_reg), ear=(ear, ear_reg), mane=(mn, mane_out[1]), mane_in=mane_in,
                mane_out=mane_out, torso=torso(),
                near_fore=_leg(BODY["near_fore"], "leg"), far_fore=_leg(BODY["far_fore"], "far", hatch=True),
                near_hind=_leg(BODY["near_hind"], "leg", region_extra=spl(BODY["haunch"])[1]),
                far_hind=_leg(BODY["far_hind"], "far", hatch=True),
                wing=wing(), tail=tail())


def lion_andante(cx: float = 0.0, cy: float = 0.0, *, lens=LENS, ground_=True) -> C.Frag:
    """The lion andante centred on the lens centre (cx, cy).  meta: silhouette
    (shapely, whole figure incl. wing / tail)."""
    p = parts()
    # the near foreleg steps out in FRONT of the outer (chest) row of the mane, from under the inner rows
    order = [p["ear"], p["head"], p["mane_in"], p["near_fore"], p["mane_out"], p["wing"], p["near_hind"],
             p["torso"], p["tail"], p["far_fore"], p["far_hind"]]
    fig, sil = stack(order)
    fig = fig.translate(0.0, FIG_DY)
    sil = shapely.affinity.translate(sil, 0.0, FIG_DY)
    g, water, lens_poly, inside = ground(lens)
    fig = behind(fig, water)
    fig = behind(fig, shapely.box(-lens[0], LEDGE_TOP, SCARP_X, lens[1]))       # paws stand ON the ledge
    if ground_:
        fig += g
    fig = C.clip(fig, inside)
    fig = drop_specks(fig, 3.0)
    from tuck import _tuck_common as K
    fig = K.plug(K.enforce_gaps(K.heal(fig)))
    sil = sil.difference(water).intersection(inside)
    fig = fig.translate(cx, cy)
    fig.meta.update(lens=lens, faces="left", silhouette=shapely.affinity.translate(sil, cx, cy))
    return fig


# ---------------------------------------------------------------------------
# dev preview:  .venv/bin/python -m tuck._tuck_lion [sil]
# ---------------------------------------------------------------------------
def _preview(sil=False, tag=""):
    from tuck import _tuck_common as K
    from deck.motifs.geometric import lens_geometry, lens_cartouche
    geo = lens_geometry(0.0, -220, 220, 330)
    lens = lens_cartouche(geo).recolor(GOLD)
    f = lion_andante(0, 0)
    art = f + lens
    extra = ""
    if sil:
        p = parts()
        for key, col in (("far_hind", "#9aa"), ("far_fore", "#9aa"), ("tail", "#c96"), ("torso", "#e8c080"),
                         ("near_hind", "#d8b070"), ("near_fore", "#d8b070"), ("mane", "#d9a441"),
                         ("head", "#f3d9a0"), ("wing", "#cfa")):
            extra += f'<path d="{G.from_shape(p[key][1])}" fill="{col}" fill-opacity="0.6"/>'
    for name, bg, recol in (("board", T.BOARD, None), ("white", "#FFFFFF", T.INK)):
        a = art if recol is None else art.recolor(recol)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="480" viewBox="-200 -240 400 480">'
               f'<rect x="-200" y="-240" width="400" height="480" fill="{bg}"/>' + (extra if name == "white" else "")
               + a.svg() + "</svg>")
        pth = K.write(K.DEV / f"lion{tag}-{name}.svg", svg)
        K.render(pth, K.DEV / f"lion{tag}-{name}-1x.png", 400)
        K.render(pth, K.DEV / f"lion{tag}-{name}-3x.png", 1200)
        K.render(pth, K.DEV / f"lion{tag}-{name}-small.png", 100)
    print("check", C.check(f))


if __name__ == "__main__":
    import sys
    _preview("sil" in sys.argv[1:])
