"""The winged lion of St. Mark — creative brief §G.2, §G.3, §H.13, §H.20.

* :func:`lion_moleca`   §G.2 FULL Lion in moleca for the A♠: a stern frontal head
                        (face Ø60, almond eyes under a heavy brow that runs into a long
                        nose bridge, trapezoid nose pad, muzzle pads, closed drooping
                        mouth), a mane of three rings of lopsided scalloped LOCKS
                        (peaks r 36 / 48 / 60, 12 a ring) flowing from the crown down
                        both sides, wings rising from behind the mane at the shoulders
                        (an arm with three shingled covert rows sweeping into the lobe,
                        five half-hatched vesica primaries sweeping up the spade's upper
                        edge, the leading primary curling inward over the head), and the
                        forepaws resting on a spring-vent rim. The wings are FITTED to a
                        silhouette (default: the A♠ spade from ``deck.frames``).
* :func:`lion_moleca_parts`  the same as separate, already-occluded Frags.
* :func:`lion_mark`     §G.2 SIMPLIFIED Lion Mark (≤ 60 px, ≤ 24 strokes) — the court
                        hallmark / clasp (§H.0).
* :func:`lion_andante`  §G.3 the tuck's lion in profile (§H.20).
* :func:`spring_vent`   the vent the A♠ lion rises from (§H.13).

Never a halo, a book or an inscription (§G.2, §J.1, san-marcos.md §6). The
lion is secular heraldry; it never appears on the back or on a joker.
All geometry is authored at final size; strokes are FINE unless noted.

Occlusion convention (README): a part that lies BEHIND another and does not
re-emerge ends on the front part's contour centreline (T-junction,
:func:`core.occlude`); interlace gaps (4.2 px, :func:`core.cut`) are only for
lines that pass under and continue.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from inkkit import geom as G

from deck import tokens as T
from .core import drop_specks as _core_drop_specks
from .core import (MIN_CLEAR, Frag, Turtle, clip, cut, dot, ellipse_arc_d, ellipse_d, fill, hatch, occlude,
                   polar, polyline_d, region, sample_d, stroke, terminal, vesica_d)
from .forms import (arc_path, arc_spline, leaf, lock_ring, scallop_arc, scallop_ring, scallop_row, unit)

__all__ = ["shingle_rows", "lion_moleca", "lion_moleca_parts", "lion_mark", "lion_andante", "spring_vent",
           "lion_face", "lion_ears", "mane_rings", "lion_paws", "moleca_wing", "drop_specks",
           "WingSpec", "MANE_RINGS", "WING_DEFAULT"]

FINE, MEDIUM, HAIR = T.FINE, T.MEDIUM, T.HAIRLINE
GOLD = T.FOIL
GAP = MIN_CLEAR                                   # §B.2 interlace gap / §I.12 clear

# §G.2 / §H.13: mane rings with their scallop PEAKS at r 36 / 48 / 60, 12 scallops each.
# (cusp radius, peak radius). All rings share one phase, so neighbouring rings run
# parallel like layered hair: >= 8.4 px clear everywhere (§I.12); the inner ring's
# cusps rest on the face circle (r 30).
MANE_RINGS = ((30.0, 36.0), (40.5, 48.0), (51.0, 60.0))


def _warn(f: Frag, msg: str) -> Frag:
    f.meta.setdefault("warnings", []).append(msg)
    return f


def _S(d, w=FINE, style="ornament", color=GOLD, layer=None, role=""):
    return stroke(d, w, style=style, color=color, layer=layer, role=role)


def drop_specks(f: Frag, min_len: float = 4.2, roles=("hatch",)) -> Frag:
    """Remove the stubs an occlusion cut leaves behind: open stroke sub-paths
    shorter than ``min_len`` px (hatch by default; ``roles=None`` = all),
    which would otherwise print as stray round-cap dots (§I.14). (Now
    :func:`core.drop_specks`; kept here for the old import path.)"""
    return _core_drop_specks(f, min_len, roles)


def _poly(pts) -> Polygon:
    g = Polygon(np.asarray(pts, float))
    return g if g.is_valid else g.buffer(0)


# =============================================================================
# frontal head: face, mane (ears optional)
# =============================================================================
# Face design at face radius 30 (positions scale with r; strokes never do).
# One half, mirrored (§H.0). A heavy brow runs down into a long, broad nose
# bridge that ends on the corners of an inverted-trapezoid nose pad; from the
# same corners two open muzzle arcs sweep out and down over the whisker pads;
# the closed mouth is the philtrum and two gently drooping upper-lip arcs
# (stern, never smiling). No chin arc (a chin under a
# drooping lip reads as a cat's ω), no ears (round ears on a face circle read
# as a teddy bear).
_FACE = dict(
    brow=[(22.4, -14.2), (13.2, -16.8), (6.8, -13.8), (5.6, -3.0), (8.6, 5.2)],
    eye=dict(c=(13.2, -6.8), half=6.6, h=5.0, tilt=17.0, pupil=(0.5, -0.6)),
    nose=[(-8.6, 5.2), (8.6, 5.2), (2.6, 11.6), (-2.6, 11.6)],
    philtrum=[(0.0, 11.6), (0.0, 14.6)],
    lip=[(0.0, 14.6), (6.0, 16.1), (10.8, 18.0)],
    lip_end=42.0,
    muzzle=[(8.6, 5.2), (13.4, 9.4), (15.2, 14.6)],
)


def lion_face(cx: float, cy: float, r: float = 30.0, *, pupils: bool = True, w: float = FINE,
              color: str = GOLD, layer: str | None = None) -> Frag:
    """The frontal lion face (§G.2): the face circle; almond eyes (pupils
    touching both lids) under a heavy brow that runs into a long nose
    bridge; an inverted-trapezoid nose pad; muzzle pads; a closed, drooping
    mouth (philtrum + upper-lip arcs). Stern, never smiling. Drawn as one
    half mirrored (§H.0). ``r`` 30 is the A♠ size (face Ø60)."""
    k = r / 30.0
    F = _FACE

    def P(x, y, sg=1):
        return (cx + sg * x * k, cy + y * k)

    f = _S(G.circle_d(cx, cy, r), w, color=color, layer=layer, role="face")
    f += _S(polyline_d([P(*p) for p in F["nose"]], closed=True), w, style="point", color=color, layer=layer,
            role="nose")
    f += _S(polyline_d([P(*p) for p in F["philtrum"]]), w, color=color, layer=layer, role="mouth")
    e = F["eye"]
    for sg in (-1, 1):
        f += _S(arc_spline([P(x, y, sg) for x, y in F["brow"]])[0], w, color=color, layer=layer, role="brow")
        f += _S(arc_spline([P(x, y, sg) for x, y in F["lip"]], h_end=90 - sg * F["lip_end"])[0], w,
                color=color, layer=layer, role="mouth")
        f += _S(arc_spline([P(x, y, sg) for x, y in F["muzzle"]])[0], w, color=color, layer=layer, role="muzzle")
        c = np.array(P(e["c"][0], e["c"][1], sg))
        u = unit(-e["tilt"] if sg > 0 else 180 + e["tilt"])
        f += stroke(vesica_d(c - u * e["half"] * k, c + u * e["half"] * k, e["h"] * k), w, style="point",
                    color=color, layer=layer, role="eye")
        if pupils:
            f += dot(c[0] + sg * e["pupil"][0] * k, c[1] + e["pupil"][1] * k, 4.2, color=color, layer=layer,
                     role="pupil")
    return f


def lion_ears(cx: float, cy: float, r: float = 30.0, *, at: float = 44.0, w: float = FINE,
              color: str = GOLD, layer: str | None = None) -> Frag:
    """Optional rounded ears on the face circle at ±``at``° from the top
    (outer arc + inner fold). NOT used by default: round ears on a face
    circle read as a teddy bear (review); kept for API compatibility."""
    f = Frag()
    k = r / 30.0
    for sg in (-1, 1):
        a = -90 + sg * at
        f += _S(arc_spline([polar(cx, cy, r, a - 19), polar(cx, cy, r + 11.0 * k, a), polar(cx, cy, r, a + 19)])[0],
                w, color=color, layer=layer, role="ear")
        f += _S(arc_spline([polar(cx, cy, r + 0.2, a - 7.5), polar(cx, cy, r + 4.0 * k, a),
                            polar(cx, cy, r + 0.2, a + 7.5)])[0], w, color=color, layer=layer, role="ear")
    return f


def mane_rings(cx: float, cy: float, rings=MANE_RINGS, n: int = 12, *, w: float = FINE,
               color: str = GOLD, layer: str | None = None) -> Frag:
    """§G.2 mane: three rings of scalloped arcs, ``n`` (12) scallops each,
    drawn as lopsided LOCKS (:func:`forms.lock_ring`): each scallop rises
    gently and dives steeply, flowing from the crown down both sides, so the
    rings read as layered hair rather than petals, a cloud or a sunflower.
    Each ring lies behind the one inside it (T-junctions on its contour).
    ``meta['silhouette']`` is the filled outline of the whole mane."""
    f = Frag()
    # (+0.25 px: cusps resting on the face circle end under its stroke, never a touch-crossing)
    front = Point(cx, cy).buffer(rings[0][0] + 0.25, quad_segs=64)
    for rc, rp in rings:
        d, poly = lock_ring(cx, cy, rc, rp, n)
        f += occlude(_S(d, w, color=color, layer=layer, role="mane"), front)
        front = front.union(poly)
    f.meta["silhouette"] = front.buffer(0)
    return f


# =============================================================================
# forepaws and the spring vent
# =============================================================================
def lion_paws(cx: float, rim, *, sep: float = 46.0, width: float = 25.0, height: float = 15.0,
              leg_top: float | None = None, toes: int = 4, leg_w: float = 19.0, w: float = FINE,
              color: str = GOLD, layer: str | None = None) -> Frag:
    """Two frontal forepaws resting on a rim, exactly mirror-symmetric about
    x = cx. ``rim(x) -> y`` gives the rim's top at x (or a constant y). Each
    forearm (``leg_w`` wide) comes straight down from ``leg_top`` and swells
    into a paw ``width`` wide whose ``toes`` knuckle scallops rest on the
    rim, with toes − 1 cleft lines between them. ``meta['shape']`` is the
    filled outline of both paws and forearms (for occluding what lies behind)."""
    rim_f = rim if callable(rim) else (lambda x, y0=float(rim): y0)
    px = cx + sep / 2                                     # the right paw; the left is its mirror
    x0, x1 = px - width / 2, px + width / 2
    lx0, lx1 = px - leg_w / 2, px + leg_w / 2
    base = [rim_f(x) - w / 2 for x in (x0, x1)]
    ytop = min(base) - height                             # where the leg swells into the paw
    lt = ytop - 10.0 if leg_top is None else leg_top
    xs = np.linspace(x0, x1, toes + 1)
    bump = 3.2
    cusp_y = [rim_f(x) - w / 2 - bump for x in xs]
    toe_d = ""
    for i in range(toes):
        a_, b_ = np.array((xs[i], cusp_y[i])), np.array((xs[i + 1], cusp_y[i + 1]))
        toe_d += scallop_arc(a_, b_, -bump, move=False)          # travelling right: right of travel = down
    left_d, _, _ = arc_spline([(lx0, lt), (lx0, ytop), (x0 + 0.6, (ytop + cusp_y[0]) / 2 + 2), (xs[0], cusp_y[0])],
                              h_start=90.0, headings={1: 90.0}, h_end=90.0)
    right_d, _, _ = arc_spline([(xs[-1], cusp_y[-1]), (x1 - 0.6, (ytop + cusp_y[-1]) / 2 + 2), (lx1, ytop), (lx1, lt)],
                               h_start=-90.0, headings={2: -90.0}, h_end=-90.0)
    d = left_d + toe_d + right_d.replace("M", "L", 1)
    right = _S(d, w, color=color, layer=layer, role="paw")
    for x, y in zip(xs[1:-1], cusp_y[1:-1]):
        right += _S(polyline_d([(x, y), (x, y - 6.5)]), w, color=color, layer=layer, role="toe")
    shape_r = _poly(sample_d(d + "Z", 0.3)[0][0])
    f = right + right.mirror_x(cx)
    f.meta["shape"] = shapely.union_all([shape_r, shapely.affinity.scale(shape_r, -1, 1, origin=(cx, 0))])
    f.meta["legs"] = (lx0, lx1)
    return f


def spring_vent(cx: float = T.CX, cy: float = 350.0, rx: float = 80.0, ry: float = 16.0, *,
                rings: int = 3, ribs: int = 12, ratio: float = 0.72, w: float = FINE, color: str = GOLD,
                layer: str | None = None) -> Frag:
    """§H.13 the spring vent: ``rings`` elliptical ripple rings (outer rx ×
    ry, each inner ring ``ratio`` × the next) and ``ribs`` radial ribs in the
    outer band, spaced evenly in angle (achiral). ``meta``: ``rim(x)`` → top
    of the outer ring at x, ``zone`` (the vent's filled outline). The lion's
    body rises out of the back of the vent: :func:`lion_moleca_parts` opens
    the inner rings there (occluded by the chest between the forelegs)."""
    f = Frag()
    radii = [(rx * ratio ** k, ry * ratio ** k) for k in range(rings)]
    for a, b in radii:
        f += _S(G.ellipse_d(cx, cy, a, b), w, color=color, layer=layer, role="vent")
    if ribs and rings >= 2:
        (a1, b1), (a2, b2) = radii[0], radii[1]
        segs = []
        for k in range(ribs):
            t = math.radians(360.0 * k / ribs + 180.0 / ribs)
            p = (cx + a2 * math.cos(t), cy + b2 * math.sin(t))
            q = (cx + a1 * math.cos(t), cy + b1 * math.sin(t))
            segs.append(polyline_d([p, q]))
        f += _S("".join(segs), w, color=color, layer=layer, role="rib")
    if rings >= 2:
        g = radii[0][1] - radii[1][1] - w
        if g < GAP:
            _warn(f, f"spring_vent: minor-axis ring clearance {g:.1f} < 4.2 (brief's rx 80 / ry 16 with 3 rings)")

    def rim(x):
        u = (x - cx) / rx
        return cy - ry * math.sqrt(max(0.0, 1 - u * u))
    f.meta.update(rim=rim, zone=shapely.affinity.scale(Point(cx, cy).buffer(1.0, quad_segs=64), rx, ry))
    return f


# =============================================================================
# wings fitted to a silhouette
# =============================================================================
@dataclass
class WingSpec:
    """Parameters of one (the viewer's right) moleca wing; the left is its
    mirror. Angles are screen degrees about the head centre.

    Construction (see :func:`moleca_wing`): an ARM from the shoulder (hidden
    behind the mane at ``root_deg``) sweeps out and down to the WRIST near
    the lobe's outer edge; three shingled covert ROWS line its upper side;
    five PRIMARIES rise from under the coverts and sweep up the spade's upper
    edge in parallel lanes ``lane`` px apart (outer feather on top, each
    shorter by ``stagger``), the leading primary curling inward over the head."""
    clear: float = 12.0                 # §H.13: gold >= 12 px inside the silhouette edge
    root_deg: float = 52.0              # the arm's root (behind the mane), about the head
    root_r: float = 55.0
    wrist_y: float | None = None        # the wrist's height (default: 60 % of the way from the lobe's widest point to its foot)
    wrist_in: float = 4.0               # wrist pulled in from the inset edge
    arm_sag: float = 0.05               # the arm's sagitta / chord (bows down, away from the feathers)
    rows: tuple[float, ...] = (0.0, 8.0, 16.0, 24.0)    # covert rows: cusp lines (px up from the arm)
    pitch: float = 13.5                 # covert scallop pitch along the arm
    n: int = 5                          # primaries (§G.2: 5 vesica primaries)
    lane: float = 0.0                   # minimum lane spacing (the lanes are always >= covering half-width + w + 4.2 apart)
    widths: tuple[float, ...] = (16.0, 14.0, 13.6, 13.0, 13.0)
    stagger: tuple[float, ...] = (0.0, 9.0, 9.0, 9.0, 9.0)   # tips stop this far short of the mane clearance
    curl_clear: float = 1.0             # extra clearance of the curling tip from the mane
    tip_axis: float = 18.0              # the curl stops this far from the axis (the tips never meet)
    tip_min_hw: float = 3.2             # the curl ends where the room left for the tip drops below this half-width
    hatch: int = 1                      # which half of each primary is hatched (+1 = inner, toward the head)
    rake: float = 50.0                  # feather barbs: hatch raking toward the tip at this angle to the shaft
    # (deprecated B2 knobs accepted and ignored so old calls keep working)
    root: float | None = None
    wrist: float | None = None
    fan: tuple | None = None


WING_DEFAULT = WingSpec()


def _largest(g):
    return max(getattr(g, "geoms", [g]), key=lambda x: x.area)


def _edge_up(ins, head, y0: float, y1: float) -> np.ndarray:
    """The RIGHT outer contour of ``ins`` travelling UP from height y0 (its
    outermost point there) to height y1."""
    hx, hy = head
    R = G.Curve(np.asarray(ins.exterior.coords)[:-1], closed=True).resample(0.5)
    right = R[:, 0] > hx + 5
    cand = np.where(right & (np.abs(R[:, 1] - y0) < 0.6))[0]
    if not len(cand):
        cand = np.where(right)[0][[int(np.argmin(np.abs(R[right, 1] - y0)))]]
    i0 = cand[np.argmax(R[cand, 0])]
    Rr = np.roll(R, -int(i0), axis=0)
    if Rr[4][1] > Rr[0][1]:
        Rr = np.vstack([Rr[:1], Rr[1:][::-1]])
    j = int(np.argmax(Rr[:, 1] <= y1))
    return Rr[:j + 1] if j > 2 else Rr


def _upper_side(g: G.Curve) -> Polygon:
    """The half-plane on the LEFT of a curve's travel, bounded by the curve
    extended tangentially at both ends."""
    t0, t1 = g.tangent_s(0.0), g.tangent_s(g.length)
    A = np.vstack([g.at_s(0.0) - t0 * 600, g.pts, g.at_s(g.length) + t1 * 600])
    n0, n1 = np.array([t0[1], -t0[0]]), np.array([t1[1], -t1[0]])
    return Polygon(np.vstack([A, A[-1] + n1 * 1200, A[0] + n0 * 1200])).buffer(0)


def _nrm(g: G.Curve, p) -> np.ndarray:
    """The left normal of curve ``g`` at its point nearest ``p``."""
    i = int(np.argmin(np.hypot(*(g.pts - np.asarray(p)).T)))
    t = g.pts[min(i + 1, len(g.pts) - 1)] - g.pts[max(i - 1, 0)]
    t = t / max(np.hypot(*t), 1e-9)
    return np.array([t[1], -t[0]])


def _runs(mask: np.ndarray) -> list[np.ndarray]:
    idx = np.where(mask)[0]
    if not len(idx):
        return []
    return np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)


def moleca_wing(sil, head, mane_sil, obstacles, spec: WingSpec = WING_DEFAULT, *, w: float = FINE,
                color: str = GOLD, layer: str | None = None) -> Frag:
    """The viewer's-RIGHT moleca wing fitted inside ``sil`` (shapely).

    §G.2 "two sickle arcs rising from behind the mane … 3 rows of scalloped
    coverts and 5 vesica primaries, one half of each hatched"; §H.13 "wings
    spread from behind the mane into both lobes, then sweep up along the
    spade's upper edges, tips curling inward toward the apex":

    * ARM — from the shoulder, hidden behind the mane (T-junction on its
      contour), out and down to the wrist near the lobe's outer edge;
    * COVERTS — three shingled scallop rows on the arm's upper side;
    * PRIMARIES — five vesicas in parallel lanes up the spade's upper edge
      (the inset silhouette), rising from under the coverts; the outer
      feather lies on top and each one inward is shorter, so every feather
      shows its pointed tip, its midrib and its hatched (inner) half, with
      >= 4.2 px clear to the feather over it; tips stop 4.2 px short of the
      mane. The leading primary runs the whole edge and its tip curls inward
      over the head, hugging the mane, stopping ``tip_axis`` px from the axis.

    All centrelines stay ``clear`` + w/2 inside the silhouette (§H.13 12 px);
    occluded parts end on the occluder's contour (T-junctions); barbs rake
    toward the tip and butt on the midrib and the outline (§B.2)."""
    hx, hy = head
    ins = _largest(sil.buffer(-(spec.clear + w / 2), quad_segs=32))
    # --- wrist: default 42 % of the way down from the lobe's widest point to its foot (right side)
    if spec.wrist_y is not None:
        wy = spec.wrist_y
    else:
        # the lobe only (outside the stem): the inset right of x = hx + 45
        right = ins.intersection(shapely.box(hx + 45.0, -1e4, 1e4, 1e4))
        right = _largest(right) if not right.is_empty else ins
        ys = np.arange(hy, right.bounds[3], 0.5)
        xr = [right.intersection(LineString([(hx, y), (hx + 800, y)])).bounds[2] if not
              right.intersection(LineString([(hx, y), (hx + 800, y)])).is_empty else hx for y in ys]
        y_wide = float(ys[int(np.argmax(xr))])
        wy = y_wide + 0.6 * (right.bounds[3] - y_wide)
    ln = ins.intersection(LineString([(hx, wy), (hx + 800, wy)]))
    wrist = np.array([ln.bounds[2] - spec.wrist_in, wy])
    root = np.array(polar(hx, hy, spec.root_r, spec.root_deg))
    ch = wrist - root
    Lc = float(np.hypot(*ch))
    nl = np.array([ch[1], -ch[0]]) / Lc
    arm_d, arm_p, _ = arc_spline([root, (root + wrist) / 2 - nl * spec.arm_sag * Lc, wrist])
    g = G.Curve(arm_p)
    Mp = _strip_map(g)
    rows, pitch = spec.rows, spec.pitch
    cov = shingle_rows(Mp, -pitch * 0.5, [g.length + pitch * 0.3] * (len(rows) - 1), rows, pitch,
                       w=w, color=color, layer=layer)
    # coverts lie on the arm's upper side: anything that dips below the arm ends on it
    lower = _upper_side(G.Curve(g.pts[::-1]))
    cov = occlude(cov, lower.buffer(0.25))
    # the covert band = everything under the OUTER row's scallop centrelines (so feathers
    # and their barbs butt exactly onto those scallops: T-junctions, §B.2)
    top_row = [pp for pp, _ in sample_d(cov.marks[-1].d, 0.25)] if cov.marks else []
    uu = np.linspace(-60, g.length + 60, 400)
    under = Mp(np.column_stack([uu, np.full_like(uu, -3.0)]))
    band = _poly(Mp(np.column_stack([uu, np.full_like(uu, rows[-2])])).tolist() + under[::-1].tolist())
    for pp in top_row:
        # each scallop closed down to the band's base line
        a_, b_ = pp[0], pp[-1]
        band = band.union(_poly(np.vstack([pp, [b_ - _nrm(g, b_) * 30, a_ - _nrm(g, a_) * 30]])))
    band = band.buffer(0)
    stop = mane_sil.buffer(w + GAP)                  # tips keep 4.2 clear of the mane's stroke
    zone = ins.intersection(_upper_side(g)).difference(stop).difference(band.buffer(-8.0))
    guide = G.Curve(_edge_up(ins, head, wy + 20.0, hy - 200.0))
    feathers = []
    hw1 = spec.widths[0] / 2
    v = hw1 + 1.2
    widths = [spec.widths[min(k, len(spec.widths) - 1)] for k in range(spec.n)]
    for k in range(spec.n):
        wd = widths[k]
        if k:
            # the covering (outer) feather's inner edge stays >= w + 4.2 from this midrib (§I.12)
            v += max(spec.lane, widths[k - 1] / 2 + w + GAP + 0.3)
        lc = G.Curve(guide.offset(v, spacing=0.5))
        ss = np.arange(0.0, lc.length, 0.5)
        pts = lc.at_s(ss)
        runs = _runs(shapely.contains_xy(zone, pts[:, 0], pts[:, 1]))
        if not runs:
            continue
        run = max(runs, key=len)
        a, b = int(run[0]), int(run[-1])
        a = max(0, a - 16)                             # the base dips 8 px under the coverts (hidden)
        hwf = None
        if k == 0:
            P, s_curl = _leading_primary(pts[a:], mane_sil, ins, head, wd / 2, spec, w)
            ext = ins.exterior

            def room(p, _e=ext):
                q = Point(*p)
                return min(_e.distance(q) - 0.3, mane_sil.distance(q) - w - GAP)
            hwf = _p1_hw(P, hw1, s_curl, room)
        else:
            b = max(a + 20, b - int(spec.stagger[min(k, len(spec.stagger) - 1)] / 0.5))
            P = pts[a:b + 1]
        if G.Curve(P).length < 24:
            continue
        feathers.append(leaf(P, wd, hw=hwf, hatch=spec.hatch, color=color, layer=layer, rake=spec.rake,
                             rake_mode="local", midrib_trim=(0.0, 0.10 if k else 0.07), w=w,
                             midrib_min_hw=w + GAP))
    wf = Frag()
    for lf in feathers[::-1]:                          # the outer (leading) feather lies on top
        wf = occlude(wf, _poly(lf.meta["outline"])) + lf
    wf = occlude(wf, band)
    arm = _S(arm_d, w, color=color, layer=layer, role="arm")
    # the arm ends on the leading primary's outline (T-junction), never in mid-air
    if feathers:
        arm = occlude(arm, _poly(feathers[0].meta["outline"]))
    wf = wf + cov + arm
    wf = occlude(wf, mane_sil)
    if obstacles is not None and not getattr(obstacles, "is_empty", True):
        wf = occlude(wf, obstacles)
    wf = clip(wf, ins.buffer(0.2))
    wf = drop_specks(wf, 4.2, roles=None)
    wf.meta.update(wrist=tuple(wrist), root=tuple(root), guide=guide.pts, n_primaries=len(feathers))
    if len(feathers) < spec.n:
        _warn(wf, f"moleca_wing: only {len(feathers)} of {spec.n} primaries fit this silhouette "
                  f"(the band between the mane and the edge is too narrow)")
    return wf


def _p1_hw(P, hw1, s_c, room=None):
    """Half-width of the leading primary: rises over the first 30 px (hidden
    under the coverts), holds, then tapers from ``s_c`` over the curl to a
    point — and never exceeds ``room(s)`` (the clearance left to the
    silhouette inset and the mane), so the outline always fits."""
    cv = G.Curve(P)
    L = cv.length
    s_c = min(max(s_c, 0.55 * L), L - 20.0)
    if room is not None:
        ss = np.linspace(0, L, max(16, int(L / 1.0)))
        rr = np.array([room(p) for p in cv.at_s(ss)])
        # keep the cap smooth (running minimum over ±6 px) so the outline never wobbles
        k = 6
        rr = np.array([rr[max(0, i - k):i + k + 1].min() for i in range(len(rr))])
    else:
        ss = rr = None

    def hw(s):
        s = np.asarray(s, float)
        up = np.clip(s / 30.0, 0, 1) ** 0.6
        down = np.clip((L - s) / max(L - s_c, 1.0), 0, 1) ** 0.85
        h = hw1 * np.minimum(up, down)
        if rr is not None:
            h = np.minimum(h, np.maximum(np.interp(s, ss, rr), 0.0))
        return h
    return hw


def _leading_primary(lane_pts, mane_sil, ins, head, hw1, spec, w):
    """The leading primary's midrib: up the edge lane until it would come
    within its own half-width + w + 4.2 of the mane, then curling inward over
    the head along the mane's contour at the clearance the tapering tip
    needs, until the room runs out or it nears the axis. Returns (midrib
    points, arc length where the tip's taper begins)."""
    hx, hy = head
    need = hw1 + w + GAP + spec.curl_clear
    dm = np.array([mane_sil.distance(Point(*p)) for p in lane_pts[::4]])
    dm = np.repeat(dm, 4)[:len(lane_pts)]
    hit = np.where(dm < need)[0]
    i_t = int(hit[0]) if len(hit) else len(lane_pts) - 1
    i_t = max(40, i_t)
    body = lane_pts[:i_t + 1]
    # the curl: follow the mane's offset contour from the transition toward the top of the axis
    tail_hw = 0.55 * hw1
    ring = mane_sil.buffer(tail_hw + w + GAP + spec.curl_clear, quad_segs=32).exterior
    ring_pts = np.asarray(ring.coords)
    p_t = body[-1]
    j0 = int(np.argmin(np.hypot(*(ring_pts - p_t).T)))
    # walk the ring toward decreasing screen angle about the head (up and over, toward the axis)
    n = len(ring_pts)
    ang = np.degrees(np.arctan2(ring_pts[:, 1] - hy, ring_pts[:, 0] - hx))
    step = 1 if ang[(j0 + 3) % n] < ang[j0] or (ang[(j0 + 3) % n] - ang[j0]) > 180 else -1
    curl = []
    j = j0
    for _ in range(n):
        j = (j + step) % n
        q = ring_pts[j]
        if q[0] < hx + spec.tip_axis + 2.0:
            break
        # room for the tapering tip inside the silhouette inset
        if ins.exterior.distance(Point(*q)) < spec.tip_min_hw + w / 2 or not ins.contains(Point(*q)):
            break
        curl.append(q)
    if len(curl) < 4:
        return body, G.Curve(body).length - 40.0
    curl = np.asarray(curl)
    # smooth the join: arc spline through a few body points, the transition and curl points
    cb = G.Curve(body)
    ctrl = [cb.at_s(s) for s in np.linspace(0, cb.length - 18.0, 5)]
    cc = G.Curve(curl)
    ctrl += [cc.at_s(s) for s in np.linspace(min(14.0, cc.length / 2), cc.length, max(2, int(cc.length / 16) + 1))]
    d_, P, _ = arc_spline(ctrl)
    return P, cb.length - 22.0


def _strip_map(g: G.Curve):
    """Strip map (u along the curve, v along its left normal) that extends the
    curve tangentially beyond both ends (Curve.map would clamp)."""
    L = g.length
    p0, p1 = g.at_s(0.0), g.at_s(L)
    t0, t1 = g.tangent_s(0.0), g.tangent_s(L)

    def f(uv):
        uv = np.atleast_2d(np.asarray(uv, float))
        u, v = uv[:, 0], uv[:, 1]
        uc = np.clip(u, 0, L)
        P = g.at_s(uc)
        Nn = g.normal_s(uc)
        lo, hi = u < 0, u > L
        P = np.where(lo[:, None], p0 + np.outer(u, t0), P)
        P = np.where(hi[:, None], p1 + np.outer(u - L, t1), P)
        n0 = np.array([t0[1], -t0[0]])
        n1 = np.array([t1[1], -t1[0]])
        Nn = np.where(lo[:, None], n0, Nn)
        Nn = np.where(hi[:, None], n1, Nn)
        return P + Nn * v[:, None]
    return f


def shingle_rows(mapf, u0: float, u_ends, rows, pitch: float, *, side: int = 1, w: float = FINE,
                 color: str = GOLD, layer: str | None = None) -> Frag:
    """Scalloped covert rows in a strip frame: ``mapf(uv) -> xy`` maps strip
    points (u along, v across). Row i has cusps at v = rows[i], every
    ``pitch`` along u starting at ``u0`` (+ half a pitch on odd rows) and
    ending before ``u_ends[i]``; each scallop is an exact arc through its two
    mapped cusps and bulges to rows[i + 1] (its peak is the next row's cusp),
    so the rows shingle like real coverts. ``side`` +1 bulges toward +v."""
    f = Frag()
    for i in range(len(rows) - 1):
        v0, v1 = rows[i], rows[i + 1]
        us = np.arange(u0 + (pitch / 2 if i % 2 else 0.0), u_ends[i] - pitch * 0.5 + 1e-6, pitch)
        d = []
        for j, u in enumerate(us):
            a, b = mapf(np.array([[u, v0], [u + pitch, v0]]))
            pk = mapf(np.array([[u + pitch / 2, v1]]))[0]
            c, R = _circle3(a, pk, b)
            chord = float(np.hypot(*(b - a)))
            sag = float(np.hypot(*(pk - (a + b) / 2)))
            cr = (b[0] - a[0]) * (pk[1] - a[1]) - (b[1] - a[1]) * (pk[0] - a[0])
            sweep = 1 if cr < 0 else 0
            large = 1 if sag > chord / 2 else 0
            d.append((f"M{a[0]:.3f} {a[1]:.3f}" if j == 0 else "") + f"A{R:.3f} {R:.3f} 0 {large} {sweep} {b[0]:.3f} {b[1]:.3f}")
        if d:
            f += _S("".join(d), w, color=color, layer=layer, role="covert")
    return f


def _circle3(p, q, r):
    ax, ay = p
    bx, by = q
    cx_, cy_ = r
    dd = 2 * (ax * (by - cy_) + bx * (cy_ - ay) + cx_ * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy_) + (bx * bx + by * by) * (cy_ - ay) + (cx_ * cx_ + cy_ * cy_) * (ay - by)) / dd
    uy = ((ax * ax + ay * ay) * (cx_ - bx) + (bx * bx + by * by) * (ax - cx_) + (cx_ * cx_ + cy_ * cy_) * (bx - ax)) / dd
    return np.array([ux, uy]), math.hypot(ax - ux, ay - uy)


# =============================================================================
# the full Lion in moleca
# =============================================================================
def _default_silhouette():
    try:
        from deck import frames as _F   # Track A's A♠ pip (read-only use)
        return _F.ace_pip_d("S")
    except Exception:                    # pragma: no cover - standalone fallback
        return None


def lion_moleca_parts(cx: float = T.CX, cy: float = 262.0, *, face_r: float = 30.0,
                      silhouette=None, wing: WingSpec | None = None, vent: dict | None = None,
                      paws: bool = True, ears: bool = False, pupils: bool = True, w: float = FINE,
                      color: str = GOLD, layer: str | None = None) -> dict:
    """The Lion in moleca as separate, already-occluded Frags:
    {'face', 'ears', 'mane', 'paws', 'wings', 'vent'} (+ 'meta').

    ``silhouette`` (FILL d or shapely) is what the wings are fitted inside;
    default ``deck.frames.ace_pip_d('S')`` (the A♠ spade, top y 140).
    ``vent`` = dict(cx, cy, rx, ry, rings, ribs) (default §H.13: (375, 350),
    80 × 16, 3 rings, 12 ribs) or False for none (paws then rest on y = cy + 72).
    ``ears`` (default False) adds the optional rounded ears.

    Layering, front to back: face, paws + forelegs, mane, vent, wings. The
    chest between the forelegs is clear (no mane fragments, the vent's inner
    rings open there: the lion rises out of the water)."""
    wing = wing or WING_DEFAULT
    sil_d = silhouette if silhouette is not None else _default_silhouette()
    sil = region(sil_d) if sil_d is not None else None
    parts: dict = {}
    face = lion_face(cx, cy, face_r, pupils=pupils, w=w, color=color, layer=layer)
    earf = lion_ears(cx, cy, face_r, w=w, color=color, layer=layer) if ears else Frag()
    k = face_r / 30.0
    mane = mane_rings(cx, cy, tuple((a * k, b * k) for a, b in MANE_RINGS), w=w, color=color, layer=layer)
    mane_sil = mane.meta["silhouette"]
    # vent
    vf, rim = Frag(), None
    if vent is not False:
        vk = dict(cx=cx, cy=cy + 88.0, rx=80.0, ry=16.0, rings=3, ribs=12)
        vk.update(vent or {})
        vf = spring_vent(vk["cx"], vk["cy"], vk["rx"], vk["ry"], rings=vk["rings"], ribs=vk["ribs"],
                         w=w, color=color, layer=layer)
        rim = vf.meta["rim"]
        vent_zone = vf.meta["zone"]
    else:
        vent_zone = Polygon()
    # paws on the rim, forelegs rising behind the face circle
    pf = Frag()
    paw_shape = Polygon()
    face_disc = Point(cx, cy).buffer(face_r, quad_segs=64)
    if paws:
        pf = lion_paws(cx, rim if rim is not None else (cy + 72.0), leg_top=cy + face_r * 0.55,
                       w=w, color=color, layer=layer)
        paw_shape = pf.meta["shape"]
        pf = occlude(pf, face_disc)                               # legs pass behind the face
        lx0, lx1 = pf.meta.get("legs", (cx + 13, cx + 33))
        # the chest between the forelegs: below the face, down to the vent's back rim
        chest = shapely.box(2 * cx - lx0, cy + face_r * 0.5, lx0, (cy + 88.0) if vent is not False else cy + 72)
        # inner rings stop at the legs; only the outer ring's lowest lock shows between them
        mane = Frag(occlude(Frag(mane.marks[:-1]), chest).marks + mane.marks[-1:], mane.meta)
        vf = occlude(vf, chest.difference(Point(cx, cy + 88.0).buffer(0.1)) if vent is not False else chest)
    if earf:
        ear_fill = shapely.union_all([_poly(sample_d(m.d + "Z", 0.3)[0][0]) for m in earf.marks[::2]])
        mane = occlude(mane, ear_fill)
    if paws:
        mane = occlude(mane, paw_shape)
        vf = occlude(vf, paw_shape)
    mane = drop_specks(mane, 4.2, roles=None)
    vf = drop_specks(vf, 4.2, roles=None)
    wings = Frag()
    if sil is not None:
        obst = vent_zone if not vent_zone.is_empty else Polygon()
        if paws:
            obst = obst.union(paw_shape)
        right = moleca_wing(sil, (cx, cy), mane_sil, obst, wing, w=w, color=color, layer=layer)
        wings = right + right.mirror_x(cx)
        parts["meta"] = dict(wrist=right.meta["wrist"], root=right.meta["root"], silhouette=sil,
                             n_primaries=right.meta["n_primaries"])
    else:
        parts["meta"] = {}
    parts.update(face=face, ears=earf, mane=mane, paws=pf, wings=wings, vent=vf)
    return parts


def lion_moleca(cx: float = T.CX, cy: float = 262.0, **kw) -> Frag:
    """§G.2 / §H.13 the full Lion in moleca, fitted to ``silhouette``
    (default: the A♠ spade). See :func:`lion_moleca_parts` for keywords.
    Returns one Frag (gold by default; pass ``color=`` to recolour)."""
    p = lion_moleca_parts(cx, cy, **kw)
    f = Frag()
    for k in ("wings", "vent", "mane", "ears", "paws", "face"):
        if p.get(k):
            f += p[k]
    f.meta.update(p.get("meta", {}))
    return f


# =============================================================================
# §G.2 simplified Lion Mark (court hallmark / clasp)
# =============================================================================
# Design table in units of a 60 px mark (head centre (0, 0), y down); smaller
# marks move the points closer together, never the strokes (they stay FINE).
#
# A frontal lion head — a 12-lock mane ring flowing from the crown down both
# sides round the face circle — carried on two UPSWEPT wings, each three
# pointed primaries fanned from behind the mane (the top primary's upper edge
# is the wing arc), tips stepped; a ripple line beneath. Tested at 24–60 px
# (build/motifs/sheet-figurative.png): upswept fanned primaries read as wings
# at every size; level wings with rounded lobes read as a bat, V/U wings
# above the head as horns, round even scallops as a sunflower, two eye dots as
# a skull or a cartoon. The stern face is two slanted almond strokes (inner
# corners low, as a lion's), a solid nose pad and, from 44 px, the Y of the
# philtrum and the drooping upper lip.
_MARK = dict(
    design=60.0,                            # the table's overall width (incl. the stroke)
    rc=12.6, rp=15.0, face=9.2,             # mane cusp / peak radius, face radius
    pivot=(6.0, 1.0),                       # where each wing's primaries fan from (hidden behind the mane)
    feathers=[(-38.0, 26.5, 3.4), (-16.0, 25.0, 3.3), (6.0, 20.5, 3.1)],   # (screen angle, length, half-width)
    bow=0.10,                               # each primary bows upward by this × its length
    eye=((2.1, -1.7), (5.8, -2.6)),         # inner, outer end of the right eye stroke
    nose=[(-2.7, 1.0), (2.7, 1.0), (0.0, 3.8)],
    mouth=((0.0, 5.0), (2.4, 5.7), (4.5, 6.1)),     # philtrum foot; the upper lip runs out, barely drooping
    ripple=(22.5, 13.0, 1.6, 8.6),          # y, half-length, amplitude, wavelength
)


def _mark_scallops(size: float) -> int:
    """§G.2 asks for 12 mane scallops; below 40 px they would clog (each
    lock narrower than two strokes), so 10 at 32–39 px and 8 below."""
    return 12 if size >= 40 else (10 if size >= 32 else 8)


def _mark_primary(p0, ang, L, hw, bow, side, w):
    u = unit(ang)
    tip = p0 + u * L
    n = np.array([u[1], -u[0]])
    mid = (p0 + tip) / 2 - n * bow * L * side             # bow upward (a raised wing)
    _, P, _ = arc_spline([p0, mid, tip])
    Lc = G.Curve(P).length

    def h(s):
        s = np.asarray(s, float)
        return hw * np.clip(s / (0.18 * Lc), 0, 1) ** 0.5 * np.clip((Lc - s) / (0.42 * Lc), 0, 1) ** 0.8
    return leaf(P, hw=h, hatch=0, midrib=None, w=w, style="point")


_TIP_REACH = 2.02        # measured: the needle primary tips (miter 10) reach ≈ this × w beyond the outline


_HALF = []


def _mark_half_extent() -> float:
    """Half-width of the design table's wing OUTLINE centrelines at scale 1 (cached)."""
    if not _HALF:
        D = _MARK
        xs = []
        for ang, L, hw in D["feathers"]:
            lf = _mark_primary(np.array(D["pivot"], float), ang, L, hw, D["bow"], 1, FINE)
            xs.append(float(np.max(lf.meta["outline"][:, 0])))
        _HALF.append(max(xs))
    return _HALF[0]


def _mark_geometry(cx, cy, size, w):
    D = _MARK
    k = (size - _TIP_REACH * w) / (2 * _mark_half_extent())   # size = overall width incl. the stroke

    def P(x, y, s=1):
        return np.array((cx + s * x * k, cy + y * k))
    n = _mark_scallops(size)
    ring_d, head = lock_ring(cx, cy, D["rc"] * k, D["rp"] * k, n, top="mound")
    wings = []
    for s in (1, -1):
        wing = []
        for ang, L, hw in D["feathers"]:
            a = ang if s > 0 else 180.0 - ang
            wing.append(_mark_primary(P(D["pivot"][0], D["pivot"][1], s), a, L * k, hw * k, D["bow"], s, w))
        wings.append(wing)
    gy, gh, amp, wl = D["ripple"]
    xs = np.linspace(-gh, gh, 90)
    ripple = size >= 32
    ground_d = polyline_d([P(x, gy + (amp * math.sin(x / wl * 2 * math.pi) if ripple else 0.0)) for x in xs])
    face = Point(cx, cy).buffer(D["face"] * k, quad_segs=48)
    return dict(k=k, P=P, n=n, ring_d=ring_d, head=head, wings=wings, ground_d=ground_d, ripple=ripple,
                face=face, face_r=D["face"] * k)


def lion_mark(cx: float, cy: float, size: float = 40.0, *, detail: str | None = None, style: str = "line",
              w: float = FINE, color: str = GOLD, layer: str | None = None, ink: str = T.INK) -> Frag:
    """§G.2 SIMPLIFIED Lion Mark, ``size`` px wide overall (≤ 60 per the
    brief; ≤ 40 as the court clasp, §H.0), centred on the head at (cx, cy).

    The face circle inside a 12-lock scalloped mane ring (10 / 8 locks below
    40 / 32 px, where 12 cannot be drawn clear), two upswept wings of three
    pointed primaries each, and a ripple line beneath (straight below 32 px).
    ≤ 24 strokes (``meta['strokes']``: 15 at full detail). Frontal and
    exactly bilateral; never a halo, book or inscription.

    ``style``:
      * 'line'  — gold monoline (on paper, jade or gold grounds), ≥ 44 px
        recommended;
      * 'solid' — the CLASP: the silhouette in flat gold with a FINE Aquifer
        contour; the face circle is a HOLE in the gold (the ground shows
        through — ``meta['face']`` is the disc, so an artist can knock it
        out of a coloured field underneath to paper); the features, the
        feather partings (≥ 36 px) and the ripple are Aquifer. The only
        legal form on red (§C rule 4) and the right form at ≤ 40 px.

    ``detail``: 'full' (eyes, nose, mouth — default ≥ 44 px), 'badge' (eyes
    and nose, 34–44 px) or 'tiny' (nose only, < 34 px)."""
    if detail is None:
        detail = "full" if size >= 44 else ("badge" if size >= 34 else "tiny")
    g = _mark_geometry(cx, cy, size, w)
    P, head, wings = g["P"], g["head"], g["wings"]
    D = _MARK
    solid = style == "solid"
    col = ink if solid else color
    lay = None if solid else layer
    f = Frag()
    n_strokes = 0
    sil = shapely.union_all([head] + [_poly(lf.meta["outline"]) for wing in wings for lf in wing]).buffer(0)
    if solid:
        f += fill(G.from_shape(sil.difference(g["face"])), color=color, role="clasp")
        f += stroke(G.from_shape(sil), w, color=ink, role="contour")
        n_strokes += 1
        if size >= 36:
            # the partings between the primaries, Aquifer on the gold; the mane ring's
            # own edge is the contour, the face circle the hole's edge
            inner = sil.buffer(-0.3)
            for wing in wings:
                for lf in wing[:-1]:
                    seg = _S(polyline_d(lf.meta["outline"], closed=True), w, color=ink, role="parting")
                    f += occlude(clip(seg, inner), head)
                    n_strokes += 1
    else:
        for wing in wings:
            wf = Frag()
            for lf in wing[::-1]:                  # the top primary lies over the ones below it
                wf = occlude(wf, _poly(lf.meta["outline"])) + lf
            f += occlude(wf.recolor(color, layer), head)
            n_strokes += 3
        f += _S(g["ring_d"], w, color=color, layer=layer, role="mane")
        f += _S(G.circle_d(cx, cy, g["face_r"]), w, color=color, layer=layer, role="face")
        n_strokes += 2
    if detail in ("full", "badge"):
        (ix, iy), (ox, oy) = D["eye"]
        for s in (1, -1):
            f += _S(polyline_d([P(ix, iy, s), P(ox, oy, s)]), w, color=col, layer=lay, role="eye")
        n_strokes += 2
    f += fill(polyline_d([P(*p) for p in D["nose"]], closed=True), color=col, layer=lay, role="nose")
    n_strokes += 1
    if detail == "full":
        (mx, my), (ax_, ay_), (bx, by) = D["mouth"]
        f += _S(polyline_d([P(0.0, D["nose"][2][1]), P(mx, my)]), w, color=col, layer=lay, role="mouth")
        for s in (1, -1):
            f += _S(arc_spline([P(mx, my), P(ax_, ay_, s), P(bx, by, s)])[0], w, color=col, layer=lay, role="mouth")
        n_strokes += 3
    f += _S(g["ground_d"], w, color=col, layer=lay, role="ripple")
    n_strokes += 1
    f = drop_specks(f, 2.5, roles=("leaf", "parting", "mane"))
    f.meta.update(strokes=n_strokes, detail=detail, size=size, style=style, scallops=g["n"],
                  silhouette=sil, face=g["face"])
    if g["n"] != 12:
        _warn(f, f"lion_mark: {g['n']} mane scallops at {size:g} px (12 cannot keep 4.2 px clear below 40 px)")
    if n_strokes > 24:
        _warn(f, f"lion_mark: {n_strokes} strokes > 24")
    return f


# =============================================================================
# §G.3 Lion andante (tuck front)
# =============================================================================
# Design table, in lens coordinates (the 330 × 440 lens centred on (0, 0), tips
# at y ±220), before ``offset``. The lion walks to the viewer's LEFT.
#
# Construction (heraldic, from circles and straight lines):
# * body — the near torso and legs are chains of joint circles joined by their
#   common tangents (torso: chest, withers, barrel, loin, haunch; legs: shoulder
#   / thigh, elbow / stifle, wrist / hock, paw), unioned and filleted (a
#   morphological closing, i.e. circular fillets); the near legs' own outlines
#   show inside the torso as the shoulder and thigh lines;
# * head — a profile of joined arc splines: level crown, brow, a straight nose
#   bridge, the squared nose, the deep upper lip, the mouth, the chin and jaw;
#   almond eye with a Ø4.2 pupil under the brow; nostril and muzzle line;
# * mane — two tiers of pointed flame LOCKS (§G.3 "scalloped arcs": each lock
#   is two circular arcs to a point) springing from behind the face and
#   flowing back and down over the neck and chest; each lock lies over the
#   next, the inner tier over the outer;
# * wing — upswept: the arm (leading edge) rises from the withers and hooks
#   back at the wrist; three shingled rows of scalloped coverts line it; five
#   raked, half-hatched vesica primaries sweep back from under the coverts,
#   tips stepped along the lens; the far wing shows as three primaries behind;
# * tail — an S behind the rump ending in a §G.7 curl whose eye is the Ø6.3
#   circle terminal, a tuft of three flame locks springing from it;
# * ground — forepaws on a 3-course limestone ledge (12 / 19 / 12, the thin
#   courses hatched 45°, §G.11), the scarp dropping to the water; hind paws
#   wading in 3 ripple lines (the legs end on the water line).
# Occlusion is by T-junction throughout (core.occlude): nothing passes under
# and re-emerges, so there are no interlace gaps.
def _env(lo, hi, pk=0.55, tail=0.35):
    """Lock-length envelope over a tier (t 0..1): rises to ``hi`` at ``pk``, then eases off."""
    def f(t):
        if t < pk:
            return lo + (hi - lo) * math.sin(math.pi * t / pk / 2)
        return hi - (hi - lo) * tail * (t - pk) / (1 - pk)
    return f


_ANDANTE = dict(
    offset=(8.0, 16.0),
    torso=[(-74, -2, 33), (-48, -14, 32), (0, -6, 27), (44, -9, 24), (78, -8, 30)],
    fore=[(-72, 8, 22), (-78, 34, 16.5), (-81, 58, 12.5), (-80, 66, 10)],
    fore_paw=((-78, 67, 8.0), (-101, 69, 6.0)),
    hind=[(80, -4, 30), (66, 32, 15), (95, 58, 9.5), (92, 110, 8.5)],
    far_fore=[(-40, 12, 17), (-44, 36, 13.5), (-47, 58, 10.5), (-47, 66, 9.5)],
    far_fore_paw=((-45, 67, 8.0), (-66, 69, 6.0)),
    far_hind=[(44, 4, 20), (48, 32, 12.5), (72, 60, 9), (62, 110, 8)],
    head=[  # outline segments (arc splines, joined; the corners stay crisp)
        dict(pts=[(-104, -96), (-120, -95), (-133, -90)]),                       # crown, flat forehead
        dict(pts=[(-133, -90), (-157, -72)]),                                    # long straight nose bridge
        dict(pts=[(-157, -72), (-159.5, -66.5), (-157.5, -61)]),                 # nose front
        dict(pts=[(-157.5, -61), (-157.5, -53), (-153.5, -48), (-148, -47)], h_start=92.0),  # deep upper lip
    ],
    chin=[(-149, -47), (-148, -41), (-142, -36), (-128, -34), (-106, -40)],
    head_back=[(-104, -62), (-106, -96)],
    eye=((-131, -78.5), 11.0, 4.6, 10.0),
    nostril=[(-158, -68.5), (-153, -67.5), (-151.5, -63.5)],
    mouth=[(-148, -47), (-139, -46.5), (-133.5, -45), (-130.5, -42)],
    muzzle=[(-147, -70), (-143.5, -62), (-140, -55.5)],
    mane_c=(-113, -63),
    # the crest: locks rooted on the crown behind the brow, IN FRONT of the head,
    # sweeping up and back over it: (root x on the crown, heading, length, width, bend)
    crest=[(-123, -44.0, 24, 12.0, 34), (-115, -32.0, 30, 13.5, 32), (-107, -22.0, 34, 14.5, 30),
           (-99, -12.0, 34, 15.0, 30)],
    # tiers: (root radius, first / last angle, locks, length envelope, width, flow vector, bend)
    mane=[(16, -104, 112, 11, _env(26, 46), 16.0, (0.8, 0.55), 26),
          (28, -100, 104, 10, _env(34, 62), 19.0, (0.8, 0.75), 30)],
    arm=[(-36, -48), (-52, -96), (-46, -142), (-22, -176), (8, -192)],
    covert_rows=(0.0, 9.0, 18.0, 27.0), covert_pitch=20.0, covert_u0=-8.0, covert_ends=(1.02, 0.96, 0.9),
    prim_v=12.0,
    # primaries: (base as a fraction along the covert band, tip, width, bend)
    primaries=[(0.90, (42, -198), 20.0, 14.0), (0.76, (74, -178), 21.0, 12.0), (0.60, (98, -152), 21.0, 12.0),
               (0.44, (112, -122), 20.0, 12.0), (0.28, (112, -90), 19.0, 12.0)],
    rake=50.0,
    far_wing_shift=(-18.0, -10.0),
    tail=[(106, -24), (126, -20), (138, -34), (136, -56), (124, -70)],
    tail_curl=(8.0, 250.0),                          # curl radius, sweep (counter-clockwise, to the left)
    # tuft: flame locks flaring on the curl's OUTSIDE from just before it:
    # (length, turn from the tail's end heading (+ = clockwise), width, bend)
    tuft_back=5.0,
    tuft=[(24, 26.0, 10, -30), (28, 58.0, 11, -34), (23, 92.0, 10, -34)],
    ledge=dict(x1=-18.0, top=75.0, heights=(12.0, 19.0, 12.0)),
    ripples=dict(x0=-8.0, ys=(95.0, 106.0, 120.0), amp=1.8, wave=24.0),
)


def _disc(c):
    x, y, r = c
    return Point(x, y).buffer(r, quad_segs=64)


def _chain(cs):
    """Union of the common-tangent hulls of consecutive joint circles (x, y, r)."""
    parts = [shapely.union_all([_disc(a), _disc(b)]).convex_hull for a, b in zip(cs[:-1], cs[1:])]
    return shapely.union_all(parts) if parts else _disc(cs[0])


def _hull(cs):
    return shapely.union_all([_disc(c) for c in cs]).convex_hull


def _fillet(g, r):
    """Circular fillets of radius ``r`` in the concave corners (morphological closing)."""
    return g.buffer(r, quad_segs=32).buffer(-r, quad_segs=32)


def _spl(pts, **kw):
    return arc_spline([np.asarray(p, float) for p in pts], **kw)


def _flame(base, direction, L, W, bend, *, fullness=0.35, w=FINE, color=GOLD, layer=None):
    """A flame LOCK (mane, tuft): a pointed leaf on a circular-arc midline of
    length ``L`` turning ``bend``° (+ = clockwise), widest (``W``) at
    ``fullness`` of its length. → (Frag, filled Polygon)."""
    base = np.asarray(base, float)
    h0 = math.degrees(math.atan2(direction[1], direction[0])) - bend / 2
    _, P, _ = arc_path(base[0], base[1], h0, [(L, bend)])
    Lc = G.Curve(P).length

    def hw(s):
        s = np.asarray(s, float)
        a = np.clip(s / (fullness * Lc), 0, 1)
        b = np.clip((Lc - s) / ((1 - fullness) * Lc), 0, 1)
        return (W / 2) * np.sqrt(1 - (1 - a) ** 2) * b ** 1.15
    # round joins: a needle tip at miter 10 renders differently in rsvg-convert and resvg (§I.25)
    lf = leaf(P, hw=hw, hatch=0, midrib=None, w=w, color=color, layer=layer, style="ornament")
    return lf, _poly(lf.meta["outline"])


def _stack(items):
    """Frags in front-to-back order, each (frag, region): every one occluded by all before it."""
    out, polys = Frag(), []
    for fr, pg in items:
        out += occlude(fr, shapely.union_all(polys)) if polys else fr
        polys.append(pg)
    return out, (shapely.union_all(polys) if polys else Polygon())


def _andante_head(D, w, color, layer):
    ds, allp = [], []
    for sg in D["head"]:
        d, P, _ = _spl(sg["pts"], h_start=sg.get("h_start"), h_end=sg.get("h_end"))
        ds.append(d if not ds else d.replace("M", "L", 1))
        allp.append(P)
    f = _S("".join(ds), w, color=color, layer=layer, role="head")
    d2, P2, _ = _spl(D["chin"], h_start=98.0)
    f += _S(d2, w, color=color, layer=layer, role="head")
    for key in ("nostril", "mouth", "muzzle"):
        f += _S(_spl(D[key])[0], w, color=color, layer=layer, role="head")
    (c, ln, h, tilt) = D["eye"]
    u = unit(180 + tilt)
    f += stroke(vesica_d(np.array(c) - u * ln / 2, np.array(c) + u * ln / 2, h), w, style="point", color=color,
                layer=layer, role="eye")
    f += dot(c[0] - 1.8, c[1] + 0.3, 4.2, color=color, layer=layer, role="pupil")
    region = _poly(np.vstack(allp + [P2, D["head_back"]]))
    return f, region, allp[0]


def _andante_crest(D, head_top, w, color, layer):
    """The crest locks rooted on the crown line (a polyline of the head's top)."""
    top = LineString(head_top)
    locks = []
    for x, hd, L, W, bend in D["crest"]:
        hit = top.intersection(LineString([(x, -300), (x, 300)]))
        if hit.is_empty:
            continue
        p = np.array(hit.coords[0] if hit.geom_type == "Point" else hit.geoms[0].coords[0])
        locks.append(_flame(p + np.array([0.0, 3.0]), unit(hd), L, W, bend, w=w, color=color, layer=layer))
    return _stack(locks)


def _andante_mane(D, front, w, color, layer):
    cx, cy = D["mane_c"]
    mane = Frag()
    for (r0, a0, a1, n, Lf, W, flow, bend) in D["mane"]:
        locks = []
        for i in range(n):
            t = i / (n - 1)
            a = a0 + (a1 - a0) * t
            dv = unit(a) + np.array(flow)
            locks.append(_flame(polar(cx, cy, r0, a), dv / np.hypot(*dv), Lf(t), W, bend, w=w, color=color,
                                layer=layer))
        tier, reg = _stack(locks)
        mane += occlude(tier, front)
        front = front.union(reg)
    return mane, front


def _andante_wing(D, w, color, layer):
    """The near wing (arm, three covert rows, five raked half-hatched primaries) and
    the far wing's three leading primaries → (near, silhouette, far)."""
    arm_d, arm_p, _ = _spl(D["arm"])
    cv = G.Curve(arm_p)
    L_ = cv.length
    sm = _strip_map(cv)
    rows = D["covert_rows"]

    def mp(uv):                                        # v toward the wing's rear (right of travel)
        uv = np.atleast_2d(uv)
        return sm(np.column_stack([uv[:, 0], -uv[:, 1]]))
    cov = shingle_rows(mp, D["covert_u0"], [L_ * e for e in D["covert_ends"]], rows, D["covert_pitch"],
                       w=w, color=color, layer=layer)
    # the covert band, exactly: from the arm to the last row's scallop centrelines
    lastrow = np.vstack([pp for pp, _ in sample_d(cov.marks[-1].d, 0.3)])
    uu = np.linspace(D["covert_u0"] - 20, L_ + 20, 300)
    band = _poly(np.vstack([mp(np.column_stack([uu, np.full_like(uu, -1.0)])), lastrow[::-1]]))
    inner = G.Curve(mp(np.column_stack([np.linspace(0, L_, 200), np.full(200, D["prim_v"])])))
    feathers = []
    for u_, tip, wd, bend in D["primaries"]:
        base, tip = inner.at_s(u_ * inner.length), np.asarray(tip, float)
        ch = tip - base
        h = math.degrees(math.atan2(ch[1], ch[0]))
        _, P, _ = arc_path(base[0], base[1], h - bend / 2, [(float(np.hypot(*ch)), bend)])
        Lc = G.Curve(P).length

        def hw(s_, Lc=Lc, W=wd):
            s_ = np.asarray(s_, float)
            return (W / 2) * np.clip(s_ / (0.15 * Lc), 0, 1) ** 0.5 * np.clip((Lc - s_) / (0.42 * Lc), 0, 1) ** 0.85
        fe = leaf(P, hw=hw, hatch=1, w=w, color=color, layer=layer, rake=D["rake"], rake_mode="local",
                  midrib_trim=(0.0, 0.1), midrib_min_hw=w + GAP)
        feathers.append((fe, _poly(fe.meta["outline"])))
    prim, prim_reg = _stack(feathers)                  # the top (leading) primary lies over the next
    near = occlude(prim, band) + cov + _S(arm_d, w, color=color, layer=layer, role="arm")
    sil = shapely.union_all([prim_reg, band]).buffer(1.0)
    far = Frag()
    for fe, _ in feathers[:3]:
        far += fe.translate(*D["far_wing_shift"])
    return near, sil, occlude(far, sil)


def _andante_tail(D, w, color, layer):
    tail_d, tail_p, _ = _spl(D["tail"])
    r_c, sweep = D["tail_curl"]
    t_end = tail_p[-1]
    tt = tail_p[-1] - tail_p[-4]
    h_end = math.degrees(math.atan2(tt[1], tt[0]))
    tu = Turtle(t_end[0], t_end[1], h_end)
    tu.arc(r_c, -sweep)                                 # curls counter-clockwise (up and over)
    ctr = t_end + unit(h_end - 90.0) * r_c              # the curl's eye
    root = t_end - unit(h_end) * D["tuft_back"]
    locks = [_flame(root, unit(h_end + da), L, W, bend, fullness=0.4, w=w, color=color, layer=layer)
             for L, da, W, bend in D["tuft"]]
    tuft, tuft_reg = _stack(locks)
    eye = Point(*ctr).buffer(r_c + w / 2 + 0.5)
    tail = _S(tail_d + tu.d().replace("M", "L", 1), w, color=color, layer=layer, role="tail")
    tail = occlude(tail, tuft_reg.difference(eye)) + terminal(*ctr, color=color, layer=layer)
    return tail + occlude(tuft, eye), shapely.union_all([tuft_reg, eye])


def _andante_ground(D, lens, w, color, layer):
    """The ledge (3 courses, thin ones hatched 45°) and the 3 ripple lines, inside
    the lens; → (frag, water region, lens polygon, lens geometry)."""
    from .geometric import lens_geometry
    geo = lens_geometry(0.0, -lens[1] / 2, lens[1] / 2, lens[0])
    lens_poly = _poly(sample_d(geo["d"], 0.5)[0][0])
    inside = lens_poly.buffer(-(w / 2 + GAP))
    dx, dy = D["offset"]
    g = Frag()
    L_ = D["ledge"]
    x1 = L_["x1"] + dx
    ys = [L_["top"] + dy]
    for hh in L_["heights"]:
        ys.append(ys[-1] + hh)
    x_left = -lens[0]
    ledge_poly = shapely.box(x_left, ys[0], x1, ys[-1]).intersection(inside)
    lx0 = ledge_poly.bounds[0]
    g += _S(polyline_d([(lx0, ys[0]), (x1, ys[0]), (x1, ys[-1])]), w, style="rule", color=color, layer=layer,
            role="ledge")
    for yv in ys[1:]:
        ln_ = LineString([(x_left, yv), (x1, yv)]).intersection(inside)
        if not ln_.is_empty:
            g += _S(polyline_d(np.asarray(ln_.coords)), w, style="rule", color=color, layer=layer, role="course")
    # a limestone face never ends in mid-air: the courses meet the lens clearance line
    # there, where the (clipped) lens rule closes them
    for (ya, yb_) in ((ys[0], ys[1]), (ys[2], ys[3])):
        g += hatch(ledge_poly.intersection(shapely.box(x_left, ya, x1, yb_)), -45.0, w=w, color=color, layer=layer)
    R_ = D["ripples"]
    for i, yv in enumerate(R_["ys"]):
        yv += dy
        xs = np.linspace(R_["x0"] + dx + 6 * i, lens[0] / 2, 400)
        pts = np.column_stack([xs, yv + R_["amp"] * np.sin((xs - R_["x0"] - dx) / R_["wave"] * 2 * math.pi)])
        ln_ = LineString(pts).intersection(inside)
        for gg in ([ln_] if ln_.geom_type == "LineString" else list(getattr(ln_, "geoms", []))):
            if gg.length > 4:
                g += _S(polyline_d(np.asarray(gg.coords)), w, color=color, layer=layer, role="ripple")
    water = shapely.box(R_["x0"] + dx - 8, R_["ys"][0] + dy, lens[0], lens[1])
    return g, water, lens_poly, geo


def lion_andante(cx: float = 0.0, cy: float = 0.0, *, lens: tuple[float, float] = (330.0, 440.0),
                 far_wing: bool = True, ledge: bool = True, ripples: bool = True, clip_lens: bool = True,
                 w: float = FINE, color: str = GOLD, layer: str | None = None) -> Frag:
    """§G.3 the lion andante for the tuck lens (§H.20 item 4), centred on the
    lens centre (cx, cy): a winged lion in profile walking to the viewer's
    LEFT, head in profile (one eye), forepaws on a 3-course half-hatched
    limestone ledge (the Balcones scarp), hind paws wading in 3 ripple lines,
    an upswept wing (arm, three rows of scalloped coverts, five raked
    half-hatched vesica primaries; the far wing's primaries show behind), the
    tail rising in an S to a curl whose eye is the Ø6.3 circle terminal, with
    a tuft of flame locks, and a mane of pointed flame locks in two tiers.
    Drawn for the 330 × 440 lens (the design table ``_ANDANTE``); clipped to
    the lens (4.2 px inside its rule) when ``clip_lens``.
    Gold foil on the Deep Hole board: line mode; knockout mode as usual.
    ``meta``: lens, faces='left', silhouette (filled outline of the lion)."""
    D = _ANDANTE
    # body (near): torso + near legs, filleted; the near legs' outlines show inside the torso
    torso = _chain(D["torso"])
    fore = _fillet(shapely.union_all([_chain(D["fore"]), _hull(D["fore_paw"])]), 4)
    hind = _chain(D["hind"])
    sil = _fillet(shapely.union_all([torso, fore, hind]), 8)
    body = _S(G.from_shape(sil), w, color=color, layer=layer, role="body")
    for part in (fore, hind):
        body += clip(_S(G.from_shape(part), w, color=color, layer=layer, role="body"), torso.buffer(-1.0))
    ff = _fillet(shapely.union_all([_chain(D["far_fore"]), _hull(D["far_fore_paw"])]), 4)
    fh = _chain(D["far_hind"])
    far = occlude(_S(G.from_shape(ff), w, color=color, layer=layer, role="far")
                  + _S(G.from_shape(fh), w, color=color, layer=layer, role="far"), sil)
    head, head_reg, head_top = _andante_head(D, w, color, layer)
    crest, crest_reg = _andante_crest(D, head_top, w, color, layer)
    head = occlude(head, crest_reg)
    mane, front = _andante_mane(D, head_reg.union(crest_reg), w, color, layer)
    mane = crest + mane
    wing, wing_sil, far_w = _andante_wing(D, w, color, layer)
    tail, tail_reg = _andante_tail(D, w, color, layer)
    # back to front: far wing, far legs, tail, body, near wing, mane, head
    f = Frag()
    if far_wing:
        f += occlude(far_w, shapely.union_all([sil, front]))
    f += occlude(far, front)
    f += occlude(tail, sil)
    f += occlude(occlude(body, front), wing_sil)
    f += occlude(wing, front)
    f += mane + head
    f = f.translate(*D["offset"])
    silhouette = shapely.affinity.translate(shapely.union_all([sil, ff, fh, front, wing_sil, tail_reg]),
                                            *D["offset"])
    g, water, lens_poly, _ = _andante_ground(D, lens, w, color, layer)
    if ripples:
        f = occlude(f, water)                          # the hind legs wade: they end on the water line
    if ledge or ripples:
        f += g.select(lambda m: (ledge and m.role in ("ledge", "course", "hatch"))
                      or (ripples and m.role == "ripple"))
    if clip_lens:
        f = clip(f, lens_poly.buffer(-(w / 2 + GAP)))
    f = drop_specks(f, 3.0, roles=None)
    f = f.translate(cx, cy)
    f.meta.update(lens=lens, faces="left", silhouette=shapely.affinity.translate(silhouette, cx, cy))
    return f
