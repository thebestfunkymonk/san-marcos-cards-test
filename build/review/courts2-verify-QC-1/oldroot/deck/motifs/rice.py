"""Texas wild-rice (*Zizania texana*) — creative brief §G.4, §G.5, §G.6.

* :func:`ribbon_leaf`  §G.4 ribbon leaf: S midrib of two tangent arcs, vesica
                       width profile (length : width 10–14 : 1), split on the
                       midrib, one half hatched PERPENDICULAR to the midrib.
* :func:`rice_stalk`   §G.5 flowering stalk: erect female spikelets toward the
                       tip (3 : 1 vesicas on 6 px pedicels, ±15°, one HAIRLINE
                       awn each), drooping male florets below them (±150°).
* :func:`rice_wreath`  §G.6 wreath: stems with paired ribbon leaves every 14°
                       (or every ``pitch`` px on any path), shrinking 6 % per
                       pair toward the tips, the stems tied with a reed-node knot.
* :func:`rice_wreath_arc`  the same on a circular arc (A♣: 4 → 8 o'clock).

All return a :class:`~deck.motifs.core.Frag` drawn at final size (line mode via
``.layers()``, knockout mode via ``core.knockout``). Species notes
(san-marcos.md §2.1): leaves stream parallel to the current; on the flowering
stalk the female spikelets are erect ABOVE and the male florets droop BELOW.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point
from shapely import union_all as shapely_union

from inkkit import geom as G

from deck import tokens as T
from .core import (MIN_CLEAR, Frag, cut, dot, occlude, polyline_d, region, stroke, terminal, vesica_d)
from .forms import arc_path, leaf, unit, vesica_hw

__all__ = ["ribbon_leaf", "rice_stalk", "rice_wreath", "rice_wreath_arc", "spikelet",
           "LEAF_FULL_MIN_W", "RIBBON_RATIO"]

FINE, HAIR = T.FINE, T.HAIRLINE

# §G.4 length : width 10–14 : 1 — the default is the widest legal leaf, so the perpendicular half-hatch
# lines are long enough to read as tone rather than as a ladder.
RIBBON_RATIO = 10.0
# §I.12: the un-hatched half keeps >= 4.2 px clear between midrib and edge, so the
# full G.4 construction (midrib + half-hatch) needs half-width >= w + 4.2 = 6.3,
# i.e. a leaf at least 12.6 px wide. Narrower leaves are drawn as plain vesicas.
LEAF_FULL_MIN_W = 2 * (FINE + MIN_CLEAR)
# §B.2 dots / §G.5 pedicels
PEDICEL = 6.0


def _warn(f: Frag, msg: str) -> Frag:
    f.meta.setdefault("warnings", []).append(msg)
    return f


# =============================================================================
# §G.4 ribbon leaf
# =============================================================================
def ribbon_leaf(x: float, y: float, heading: float, length: float = 140.0, width: float | None = None, *,
                ratio: float = RIBBON_RATIO, bend: tuple[float, float] = (14.0, -14.0), hatch: int = 1,
                narrow: str = "plain", full: bool | None = None, w: float = FINE, color: str = T.INK,
                layer: str | None = None) -> Frag:
    """§G.4 a wild-rice ribbon leaf from its base (x, y) heading ``heading``
    (screen degrees). The midrib is an S of two tangent circular arcs, each
    half the length, turning ``bend`` = (β1, β2) degrees (+ clockwise;
    (β, −β) is the S, (β, β) a C, (0, 0) straight). The outline has a vesica
    width profile (``width`` default length / ``ratio``). The leaf is split
    on the midrib and ONE half (``hatch`` +1 left / −1 right of base→tip,
    0 none) is hatched perpendicular to the midrib at 7 px pitch.

    Leaves narrower than 12.6 px cannot keep 4.2 px clear between midrib and
    edge (§I.12), so they drop the midrib (recorded in ``meta['warnings']``)
    and, with ``narrow``:

    * 'plain' — a plain S-ribbon vesica outline (the B2 behaviour);
    * 'tip'   — the leaf is split ACROSS at the S's inflection and its
      tip-ward half (the ribbon turning over in the current) is hatched
      perpendicular to the (undrawn) midrib, every line running edge to edge
      and butting on the outline centreline — still "one half hatched", no
      hatch end in mid-air, and never a plain laurel leaf.

    ``full`` forces the choice (True only where W >= 12.6 anyway; False
    draws the narrow form at any width — a wreath keeps one form throughout).
    ``meta``: width, full, mid (midrib points), outline, base, tip."""
    W = length / ratio if width is None else width
    _, mid, _t = arc_path(x, y, heading, [(length / 2, bend[0]), (length / 2, bend[1])])
    can = W >= LEAF_FULL_MIN_W - 1e-9
    full = can if full is None else (bool(full) and can)
    f = leaf(mid, W, hatch=hatch if full else 0, midrib="full" if full else None,
             w=w, color=color, layer=layer)
    if not full:
        if narrow == "tip" and hatch:
            f += _tip_half_hatch(f.meta["mid"], f.meta["hw"], w=w, color=color, layer=layer)
            if not can:
                _warn(f, f"ribbon_leaf: width {W:.1f} < {LEAF_FULL_MIN_W:.1f} — no midrib; tip half hatched across")
        elif not can:
            _warn(f, f"ribbon_leaf: width {W:.1f} < {LEAF_FULL_MIN_W:.1f} — plain vesica (no midrib/hatch)")
    f.meta.update(width=W, full=full)
    return f


def _tip_half_hatch(mid, hw, *, split: float = 0.5, pitch: float = T.HATCH_PITCH, w: float = FINE,
                    color: str = T.INK, layer: str | None = None) -> Frag:
    """Hatch lines ACROSS a leaf (edge to edge, perpendicular to its midrib)
    over the tip-ward part from ``split`` × length, 7 px apart; lines shorter
    than 2·w (the needle tip) are dropped. Both ends of every line lie on the
    outline centreline (the outline is built from the same half-widths)."""
    from .core import MIN_HATCH_LEN
    cv = G.Curve(np.asarray(mid, float))
    L = cv.length
    ss = np.arange(split * L + pitch / 2, L, pitch)
    lines = []
    for s_ in ss:
        h = float(hw(np.array([s_]))[0])
        if 2 * h < MIN_HATCH_LEN + 0.5:
            continue
        p = cv.at_s(s_)
        n = cv.normal_s(np.array([s_]))[0]
        lines.append(np.array([p - n * h, p + n * h]))
    return stroke(lines, w, style="hatch", color=color, layer=layer, role="hatch") if lines else Frag()


# =============================================================================
# §G.5 flowering stalk
# =============================================================================
def spikelet(base, axis_deg: float, length: float = 14.0, width: float | None = None, *,
             awn: float = 0.0, w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """One 3 : 1 spikelet / floret: a vesica from ``base`` along ``axis_deg``
    (sharp miter-10 tips, §B.2) with an optional HAIRLINE awn continuing
    from its tip (§G.5)."""
    base = np.asarray(base, float)
    width = length / 3.0 if width is None else width
    tip = base + unit(axis_deg) * length
    f = stroke(vesica_d(base, tip, width), w, style="point", color=color, layer=layer, role="spikelet")
    if awn > 0:
        # the awn starts at the vesica's tip point, clear of the miter
        a0 = tip + unit(axis_deg) * 0.0
        f += stroke(polyline_d([a0, tip + unit(axis_deg) * awn]), HAIR, color=color, layer=layer, role="awn")
    f.meta.update(tip=tuple(tip))
    return f


def rice_stalk(x: float, y: float, heading: float = -90.0, length: float = 170.0, *,
               n_female: int = 6, n_male: int = 4, spikelet_len: float = 14.0, pedicel: float = PEDICEL,
               female_angle: float = 15.0, male_angle: float = 150.0, female_spread: float = 70.0,
               male_spread: float = 95.0, awn: float = 13.0, f_pitch: float | None = None,
               m_pitch: float | None = None, gap: float = 10.0, bend: float = 0.0, terminal_spikelet: bool = True,
               w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.5 a flowering stalk from its base (x, y) along ``heading`` for
    ``length`` px (``bend`` degrees of gentle arc over the whole length).

    Toward the tip: ``n_female`` erect female spikelets, alternating sides,
    each a 3 : 1 vesica whose axis stands ``female_angle`` (±15°) off the
    stalk, on a 6 px pedicel, with one HAIRLINE awn; the stalk ends in a
    terminal spikelet. Below them, after ``gap`` px of bare stalk:
    ``n_male`` drooping male florets, the same vesicas hung at
    ``male_angle`` (±150°) from the stalk's upward direction.

    Interpretation (documented in README): a 6 px pedicel at 15° cannot carry
    a 3 : 1 spikelet clear of the stalk, so the PEDICEL leaves the stalk at
    ``female_spread`` / ``male_spread`` degrees and the spikelet's own axis
    stands at ±15° / ±150°. Pitches default to the smallest that keep every
    awn and floret >= 4.2 px clear of its same-side neighbour.
    ``meta``: tip, base, female (list of spikelet bases), male."""
    turns = [(length, bend)]
    _, P, _t = arc_path(x, y, heading, turns)
    cv = G.Curve(P)
    L = cv.length
    f = stroke(polyline_d(P), w, color=color, layer=layer, role="stalk")
    sw = spikelet_len / 3.0
    sa = math.radians(female_angle)
    # same-side neighbours are 2·pitch apart along the stalk; their parallel
    # axes are 2·pitch·sin(angle) apart — keep the awn (HAIRLINE) >= 4.2 clear
    # of the next spikelet's outer edge, or stop short of it.
    if f_pitch is None:
        need = (sw / 2 + w / 2 + HAIR / 2 + MIN_CLEAR) / math.sin(sa) / 2
        reach = (spikelet_len + awn) * math.cos(sa) / 2 + 1.0
        f_pitch = max(9.0, min(need, reach))
    if m_pitch is None:
        m_pitch = max(9.5, (spikelet_len * math.cos(math.radians(180 - male_angle)) + w + MIN_CLEAR) / 2 + 1.0)
    females, males = [], []
    tip_s = L
    # terminal spikelet on the axis
    if terminal_spikelet:
        tp = cv.at_s(L)
        td = cv.tangent_s(L)
        ta = math.degrees(math.atan2(td[1], td[0]))
        f += spikelet(tp, ta, spikelet_len, awn=awn, w=w, color=color, layer=layer)
        females.append(tuple(tp))
    side = 1
    s = L - f_pitch * 0.9
    for k in range(n_female):
        if s < 0:
            break
        p = cv.at_s(s)
        td = cv.tangent_s(s)
        a = math.degrees(math.atan2(td[1], td[0]))
        # side +1 = screen-left of travel (a − θ), −1 = right
        ped_a = a - side * female_spread
        q = p + unit(ped_a) * pedicel
        f += stroke(polyline_d([p, q]), w, color=color, layer=layer, role="pedicel")
        f += spikelet(q, a - side * female_angle, spikelet_len, awn=awn, w=w, color=color, layer=layer)
        females.append(tuple(q))
        side = -side
        s -= f_pitch
    s -= gap
    for k in range(n_male):
        if s < 0:
            _warn(f, "rice_stalk: stalk too short for all male florets")
            break
        p = cv.at_s(s)
        td = cv.tangent_s(s)
        a = math.degrees(math.atan2(td[1], td[0]))
        ped_a = a - side * male_spread
        q = p + unit(ped_a) * pedicel
        f += stroke(polyline_d([p, q]), w, color=color, layer=layer, role="pedicel")
        f += spikelet(q, a - side * male_angle, spikelet_len, w=w, color=color, layer=layer)
        males.append(tuple(q))
        side = -side
        s -= m_pitch
    f.meta.update(tip=tuple(cv.at_s(L)), base=(x, y), female=females, male=males,
                  f_pitch=f_pitch, m_pitch=m_pitch, bare=s)
    return f


# =============================================================================
# §G.6 wreath
# =============================================================================
def _reed_knot(p, heading: float, *, rx: float = 8.4, ry: float = 4.6, tail: float = 13.0,
               spread: float = 28.0, w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """The reed-node knot that ties the two stems: a node ellipse across the
    stems at ``p`` (major axis perpendicular to ``heading`` = the direction
    the stems arrive from), the stems running into it and ending on its rim;
    below it the two cut stem ends hang on as tails, each leaving the rim
    at its own point (0.5 rx either side of the axis — never one V, which
    reads as a cherry pair), splaying ±``spread``° and bowing gently
    outward, ending in Ø6.3 terminals. ``meta['zone']`` is the ellipse's
    filled region."""
    p = np.asarray(p, float)
    ell = G.ellipse_d(p[0], p[1], rx, ry, heading + 90)
    f = stroke(ell, w, color=color, layer=layer, role="knot")
    zone = G.to_shape(ell, tol=0.02)
    u, v = unit(heading), unit(heading + 90)
    for sgn in (1, -1):
        # the rim point below the axis, 0.5 rx to this side
        t = math.asin(0.5) * sgn
        a0 = p + v * (rx * math.sin(t)) + u * (ry * math.cos(t))
        a = heading + sgn * spread
        d_, pts, _ = arc_path(a0[0], a0[1], a, [(tail, sgn * 14.0)])
        f += stroke(d_, w, color=color, layer=layer, role="knot-tail")
        f += terminal(*pts[-1], color=color, layer=layer)
    f.meta["zone"] = zone
    return f


WREATH_FULL_LEN = 10.0 * LEAF_FULL_MIN_W        # 126: the shortest §G.4 leaf (ratio 10) that keeps midrib + hatch


def _petiole(p, heading: float, turn: float, length: float) -> np.ndarray:
    """A petiole springing TANGENTIALLY from the stem at ``p`` (starting on
    the stem's heading) and turning ``turn``° (+ clockwise) over ``length``."""
    _, P, _t = arc_path(p[0], p[1], heading, [(length, turn)])
    return P


def rice_wreath(path, *, axis: float | None = T.CX, pitch: float = 40.0, first: float = 20.0,
                leaf_len: float | None = None, ratio: float | None = None, width: float | None = None,
                shrink: float = 0.06, angle: float = 24.0, bend: tuple[float, float] = (12.0, -5.0),
                hatch_out: int = 1, tip: str | None = "spike", tip_leaf: bool | None = None,
                spike_len: float = 44.0, knot: bool = True, stem_end: float = 0.0,
                petiole: float | None = None, awn: float = 20.0, inner_scale: float = 0.66,
                inner_angle: float | None = None, narrow: str = "tip", narrow_bend: float | None = 18.0,
                w: float = FINE, color: str = T.INK, layer: str | None = None) -> Frag:
    """§G.6 wild-rice wreath. ``path`` is ONE branch's stem, drawn from the
    knot to the branch tip (d-string or points).

    * The STEM is one continuous arc line from the knot to the tip; nothing
      erases it: the leaves spring from it, and it breaks (4.2 px interlace
      gap) only where another station's blade truly crosses it.
    * Every ``pitch`` px from ``first`` a PAIR of ribbon leaves (§G.4) springs
      TANGENTIALLY from the stem: each leaf's petiole leaves the stem on its
      heading and curves out ``angle``° over ``petiole`` px (default 0.1 ×
      the leaf), and the leaf's midrib continues the petiole (an S of two
      tangent arcs turning ``bend`` = (β1, β2), back toward the tip then a
      flick out). Each pair is ``shrink`` (6 %) smaller than the last; the
      leaves on the concave side are ``inner_scale`` × as long and stand off
      at ``inner_angle`` (default ``angle`` + 16°) so they never bundle
      along the stem.
    * Leaf form, one for the whole wreath: when every pair is >= 12.6 px wide
      the full §G.4 leaf (midrib + perpendicular half-hatch on the
      ``hatch_out`` half); otherwise the narrow ribbon (``narrow`` 'tip': the
      tip-ward half hatched across, edge to edge; 'plain': outline only) with
      at least ``narrow_bend``° of S so it streams like a ribbon, never a
      laurel leaf. With ``leaf_len`` None the first pair is 2.5 × ``pitch``
      long (the last pair is stretched to the full 126 × 12.6 leaf when that
      is within 10 %); ``ratio`` defaults to 10 (§G.4's widest leaf).
    * The branch ends in ``tip``: 'spike' (default — a flowering spike of
      erect female spikelets with long HAIRLINE awns, §G.5, springing from
      the stem's end on its heading, so it is attached), 'leaf' or None.
    * With ``axis`` the branch is mirrored about x = axis and, with
      ``knot``, the two stems are tied by a reed-node knot at the path's
      start: the stems run into the node ellipse and end on its rim, the
      cut ends splay below it with Ø6.3 terminals.

    Tip-ward pairs lie over earlier ones: what lies behind ends ON the front
    leaf's outline (T-junction), hatch included, so no line stops in mid-air;
    cut stubs are dropped. ``meta``: n_pairs, stem (points), bases,
    leaf_len, ratio, full, warnings."""
    from .core import drop_specks, prune_hatch
    if isinstance(path, str):
        from .core import sample_d
        P = sample_d(path, 0.25)[0][0]
    else:
        P = np.asarray(path, float)
    cv = G.Curve(P)
    L = cv.length
    stem_len = L - stem_end
    stations = []
    s = first
    while s < stem_len - 6:
        stations.append(s)
        s += pitch
    n = len(stations)
    rat = RIBBON_RATIO if ratio is None else ratio
    last_k = (1 - shrink) ** max(n - 1, 0)
    if leaf_len is None:
        leaf_len = 2.5 * pitch
        full_first = WREATH_FULL_LEN * max(rat / RIBBON_RATIO, 1.0) / last_k
        if leaf_len >= full_first / 1.1 and width is None:
            leaf_len = full_first
    # one leaf form for the whole wreath: full only if the LAST (smallest) pair can be
    w_last = (leaf_len * last_k / rat) if width is None else width * last_k
    full = w_last >= LEAF_FULL_MIN_W - 1e-9
    if not full and narrow_bend:
        # a narrow leaf reads as a ribbon only with a real S (review: plain narrow vesicas read as laurel)
        b0 = math.copysign(max(abs(bend[0]), narrow_bend), bend[0] or 1.0)
        b1 = math.copysign(max(abs(bend[1]), narrow_bend), bend[1] or -1.0)
        bend = (b0, b1)
    units: list[tuple[Frag, object]] = []                 # (leaf + petiole, filled region), base → tip
    bases = []
    warns: list[str] = []
    lp_max = 0.0
    for k, s in enumerate(stations):
        ll = leaf_len * (1 - shrink) ** k
        lw = ll / rat if width is None else width * (1 - shrink) ** k
        p = cv.at_s(s)
        td = cv.tangent_s(s)
        a = math.degrees(math.atan2(td[1], td[0]))
        lp = max(6.0, 0.1 * ll) if petiole is None else petiole
        lp_max = max(lp_max, lp)
        # the concave (inner) side of a curved stem: its leaves are shorter
        # (``inner_scale``) so they never run into the next pair
        t2 = cv.tangent_s(min(s + 5.0, L))
        cr = float(td[0] * t2[1] - td[1] * t2[0])
        inner_side = 0 if abs(cr) < 1e-4 else (-1 if cr > 0 else 1)   # cr > 0: turning clockwise → right is inner
        for side in (1, -1):                                    # +1 = left of travel
            inner = side == inner_side
            ang = (inner_angle if inner_angle is not None else angle + 16.0) if inner else angle
            sc = inner_scale if inner else 1.0
            pet = _petiole(p, a, -side * ang, lp)
            q = pet[-1]
            h = a - side * ang
            lf = ribbon_leaf(q[0], q[1], h, ll * sc, lw * sc if width is not None else lw,
                             bend=(side * bend[0], side * bend[1]), hatch=side * hatch_out, narrow=narrow,
                             full=full, w=w, color=color, layer=layer)
            unit_f = stroke(polyline_d(pet), w, color=color, layer=layer, role="petiole") + lf
            reg = region(polyline_d(lf.meta["outline"], closed=True))
            units.append((unit_f, reg))
            bases.append(tuple(q))
            for m in lf.meta.get("warnings", []):
                if m not in warns:
                    warns.append(m)
    if not full:
        warns = [f"rice_wreath: leaves {w_last:.1f}–{leaf_len / rat if width is None else width:.1f} px wide "
                 f"(< 12.6): narrow ribbons ({narrow}), S {bend[0]:g}/{bend[1]:g}°"]
    stem_pts = cv.sub(0, stem_len / L).pts if stem_end else cv.pts
    stem = stroke(polyline_d(stem_pts), w, color=color, layer=layer, role="stem")
    if tip_leaf is not None:                       # backwards-compatible flag
        tip = "leaf" if tip_leaf else None
    p = cv.at_s(stem_len)
    td = cv.tangent_s(stem_len)
    a = math.degrees(math.atan2(td[1], td[0]))
    tip_f = Frag()
    if tip == "leaf":
        ll = leaf_len * (1 - shrink) ** n
        lw = ll / rat if width is None else width * (1 - shrink) ** n
        tip_f = ribbon_leaf(p[0], p[1], a, ll, lw, bend=(0.0, -bend[1]), hatch=hatch_out, narrow=narrow, full=full,
                            w=w, color=color, layer=layer)
    elif tip == "spike":
        # the spike springs from the stem's end on its heading: attached (§G.5, airy awns 1.7× the spikelet)
        tip_f = rice_stalk(p[0], p[1], a, spike_len, n_female=3, n_male=0, spikelet_len=12.0,
                           awn=awn, female_spread=64.0, w=w, color=color, layer=layer)
    # stacking, back to front: earlier (knot-ward) pairs lie under later ones;
    # whatever lies behind ends ON the front outline (T-junction), hatch included
    lv = Frag()
    front = None
    for unit_f, reg in units[::-1]:                  # front (tip-ward) first
        lv += occlude(unit_f, front) if front is not None else unit_f
        front = reg if front is None else front.union(reg)
    if tip_f:
        # the spike's thin lines lie over the last leaves: interlace gaps
        lv = cut(lv, tip_f.shape(), MIN_CLEAR)
    lv = prune_hatch(drop_specks(lv, 4.2, roles=None), 1.3)
    # the stem breaks only where a leaf BLADE truly crosses it away from that
    # leaf's own base (a leaf springs from the stem; it never erases it)
    stem_line = LineString(stem_pts)
    near_bases = shapely_union([Point(q).buffer(lp_max + 0.35 * leaf_len) for q in bases])
    cross = [reg for _, reg in units if reg.intersects(stem_line)
             and not reg.intersection(stem_line).within(near_bases)]
    if cross:
        stem = cut(stem, shapely_union(cross).difference(near_bases), MIN_CLEAR)
    branch = stem + lv + tip_f
    out = Frag(branch.marks)
    if axis is not None:
        out += branch.mirror_x(axis)
        if knot:
            td = cv.tangent_s(0)
            back = math.degrees(math.atan2(-td[1], -td[0]))
            p0 = cv.at_s(0)
            head = 90.0 if abs(p0[0] - axis) < 1 else back
            k_f = _reed_knot((axis, p0[1]), head, w=w, color=color, layer=layer)
            # the stems run INTO the node ellipse and end on its rim (the knot ties them)
            out = drop_specks(occlude(out, k_f.meta["zone"]), 4.2, roles=None) + k_f
    for m in tip_f.meta.get("warnings", []):
        if m not in warns:
            warns.append(m)
    out.meta["warnings"] = warns
    out.meta.update(n_pairs=n, stem=stem_pts, bases=bases, leaf_len=leaf_len, ratio=rat, full=full)
    return out


def rice_wreath_arc(cx: float, cy: float, r: float, *, knot_deg: float = 90.0, tip_deg: float = 30.0,
                    step_deg: float = 14.0, **kw) -> Frag:
    """§G.6 on a circle: the right-hand branch runs from ``knot_deg`` (90 =
    6 o'clock) to ``tip_deg`` (30 = 4 o'clock), mirrored about x = cx (so
    the pair spans 4 → 8 o'clock through 6). Leaf pairs every ``step_deg``
    (14°) of arc."""
    pts = G.arc_pts(cx, cy, r, knot_deg, tip_deg, n=max(32, int(abs(knot_deg - tip_deg) * r / 2)))
    kw.setdefault("pitch", math.radians(step_deg) * r)
    kw.setdefault("first", math.radians(step_deg) * r * 0.55)
    return rice_wreath(pts, axis=cx, **kw)
