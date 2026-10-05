"""Wild-rice (*Zizania texana*) drawing for the A♣ · The Reed (brief §G.4–6, §H.15).

Two scales, one plant:

* the KNOCKOUT spray inside the club: paper lines (MEDIUM, §B.2 knockout
  lines) and SOLID paper grains and leaf halves, i.e. holes in the Aquifer
  pip, never paint;
* the GOLD wreath outside it (FINE line, §G.6): :func:`wreath`.

Botany (san-marcos.md §2.1, §G.5, refs/smtx/wild_rice.jpg): one culm; the
panicle carries stiffly ERECT, awned female spikelets at its top and, below
them, spreading branches from which the small, awnless male florets hang
PENDULOUS on short pedicels; long ribbon leaves arise from the base, their
sheaths clasping the culm.
"""
from __future__ import annotations

import math

import numpy as np

from deck import tokens as T
from deck import motifs as M
from deck.motifs import forms
from deck.motifs import rice as RI
from inkkit import geom as G

from art import _aces_common as A

W = A.KO
FINE = T.FINE
GOLD = T.FOIL
CX = A.CX


def u(a: float) -> np.ndarray:
    return A.unit(a)


def mirror(f: M.Frag) -> M.Frag:
    return f + f.mirror_x(CX)


def line(pts, role: str = "line") -> M.Frag:
    return M.stroke(M.polyline_d([np.asarray(p, float) for p in pts]), W, role=role)


# =============================================================================
# the knockout spray (inside the club)
# =============================================================================
def grain(base, ang: float, L: float, wd: float, role: str = "spikelet") -> M.Frag:
    """A solid paper spikelet / floret: a vesica from ``base`` along ``ang``."""
    base = np.asarray(base, float)
    return M.fill(M.vesica_d(base, base + u(ang) * L, wd), role=role)


def female_panicle(x: float, y_top: float, *, tiers: int = 2, pitch: float = 16.0, first: float = 14.0,
                   L: float = 16.0, wd: float = 5.0, ped: float = 8.0, spread: float = 50.0,
                   lean: float = 18.0, awn: float = 12.0, top_L: float = 16.0) -> M.Frag:
    """The erect female part of the panicle on the culm tip (§G.5): a
    terminal spikelet and ``2 × tiers`` below it, alternating sides, each on
    a short pedicel leaving the culm at ``spread``°, the spikelet itself
    standing only ``lean``° off vertical (stiffly erect), with one awn
    running on from its tip. A knockout awn must be >= 2.5 px (§I.12), so
    it is MEDIUM, not §G.5's line-mode HAIRLINE."""
    f = grain((x, y_top), -90.0, top_L, wd)
    tip = np.array([x, y_top - top_L])
    f += line([tip + (0.0, 2.0), tip - (0.0, awn)], "awn")
    for k in range(2 * tiers):
        side = 1 if k % 2 == 0 else -1
        p = np.array([x, y_top + first + k * pitch])
        q = p + u(-90.0 + side * spread) * ped
        f += line([p, q], "pedicel")
        a = -90.0 + side * lean
        f += grain(q - u(a) * 0.5, a, L, wd)
        t = q + u(a) * L
        f += line([t - u(a) * 2.0, t + u(a) * awn], "awn")
    return f


def male_branch(root, h0: float, turns, florets, *, L: float = 10.5, wd: float = 3.7) -> M.Frag:
    """A male panicle branch from ``root`` on the culm, heading ``h0`` along
    tangent arcs ``turns`` [(length, turn°)]. ``florets`` [(fraction of the
    branch, hang°, pedicel)] hang PENDULOUS (90 = straight down) on short
    pedicels; a pedicel of 0 hangs the floret from the branch's own end,
    continuing it. Male spikelets are smaller than the female and awnless."""
    d, P, _ = forms.arc_path(root[0], root[1], h0, turns)
    f = M.stroke(d, W, role="branch")
    cv = G.Curve(P)
    for s, hang, ped in florets:
        p = cv.at(s)
        if ped <= 0:
            t = cv.tangent_s(cv.length)
            hg = math.degrees(math.atan2(t[1], t[0]))
            f += grain(p - u(hg) * 1.0, hg, L, wd, "floret")
        else:
            q = p + u(hang) * ped
            f += line([p, q], "pedicel")
            f += grain(q - u(hang) * 0.5, hang, L, wd, "floret")
    return f


def ribbon_leaf(P, width: float, hatch: int, *, w: float = W, pitch: float = T.HATCH_PITCH,
                win: float = 3.3) -> M.Frag:
    """§G.4 ribbon leaf for a KNOCKOUT, split on its midrib ``P`` (base → tip,
    vesica profile ``width`` wide):

    * the LIT half (``-hatch`` side) is solid paper — a hole in the pip;
    * the SHADED half (``hatch`` +1 left / −1 right of base → tip) is the
      half-hatch: a paper edge line (MEDIUM, its outer edge on the leaf's
      edge) and paper bars perpendicular to the midrib at the 7 px pitch,
      from the lit half to the edge line (both ends joined, never in
      mid-air, §B.2). Bars run only where the ink windows between them keep
      >= ``win`` px (≈ the middle 40 % of the blade); toward base and tip
      the shaded half closes to paper and the blade ends in clean points.

    Why: an OUTLINED knockout leaf (outline + midrib + hatch) needs >= 16 px
    and reads at MEDIUM as a ladder; a lit half + hatched half keeps the
    silhouette, reads at 188 px, and gives the deck's light / shade."""
    P = np.asarray(P, float)
    cv = G.Curve(P)
    L = cv.length
    hw = forms.vesica_hw(L, width)
    left, right, ol = forms.leaf_edges(P, hw)
    lit_edge = right if hatch > 0 else left
    f = M.fill(M.polyline_d(np.vstack([P, lit_edge[::-1]]), closed=True), role="leaf")
    s = np.linspace(0.0, L, max(200, int(L * 2)))
    N = cv.normal_s(s) * hatch
    h = np.maximum(hw(s) - w / 2, 0.0)
    f += M.stroke(M.polyline_d(cv.at_s(s) + N * h[:, None]), w, style="point", role="leaf-edge")
    ok = np.where(hw(s) >= w + win)[0]
    if len(ok):
        bars = forms.perp_hatch(P, lambda ss: np.maximum(hw(ss) - w / 2, 0.0), hatch, pitch=pitch,
                                s_range=(s[ok[0]], s[ok[-1]]), min_len=w / 2 + win)
        if bars:
            # each bar starts 1 px inside the lit half so it joins it cleanly
            bars = [np.array([a - (b - a) / np.linalg.norm(b - a), b]) for a, b in bars]
            f += M.stroke(bars, w, style="hatch", role="hatch")
    f.meta["outline"] = ol
    return f


def leaf_with_sheath(sheath_pts, h0: float, turns, width: float, hatch: int) -> M.Frag:
    """A sheath (a MEDIUM paper line clasping the culm, through
    ``sheath_pts``) and, from its collar, the blade along ``turns`` from
    heading ``h0`` (the S of tangent arcs, §G.4)."""
    d, _, _ = forms.arc_spline(sheath_pts, h_end=h0)
    f = M.stroke(d, W, role="sheath")
    base = sheath_pts[-1]
    _, P, _ = forms.arc_path(base[0], base[1], h0, turns)
    return f + ribbon_leaf(P, width, hatch)


# =============================================================================
# the gold wreath (outside the club)
# =============================================================================
# §G.4 ribbon blades for the wreath: (length of the knot-ward pair, length :
# width, angle off the stem, S bend (b0, b1) — + turns away from the stem,
# and whether the blade is half-hatched across its tip half). The OUTER blades
# (convex side) are long and stream tip-ward along the arc; the INNER ones
# (toward the club) are shorter, stand further off and stay plain.
BLADE_OUTER = dict(L=100.0, ratio=13.5, angle=10.0, bend=(-10.0, 14.0), hatch=True)
BLADE_INNER = dict(L=62.0, ratio=12.0, angle=26.0, bend=(-6.0, 14.0), hatch=False)


def wreath_blade(p, heading: float, side: int, L: float, W: float, angle: float, bend, hatch: bool):
    """One wild-rice ribbon blade springing TANGENTIALLY from the stem at
    ``p`` (stem heading ``heading``) on ``side`` (+1 = left of travel): a
    sheath (petiole) leaves on the stem's heading and turns ``angle``° away
    over 0.1 L, and the blade continues it on a §G.4 S midrib of two tangent
    arcs turning ``bend`` = (b0, b1)° (+ = away from the stem), with a vesica
    profile L × W. Blades are narrower than 12.6 px, so (the deck's narrow
    ribbon, deck.motifs.rice) no midrib is drawn and a ``hatch``-ed blade is
    hatched across its tip half — the ribbon turning over. → (Frag, filled
    region, blade base)."""
    pet = max(6.0, 0.1 * L)
    _, pp, _ = forms.arc_path(p[0], p[1], heading, [(pet, -side * angle)])
    q = pp[-1]
    lf = RI.ribbon_leaf(q[0], q[1], heading - side * angle, L, W, bend=(-side * bend[0], -side * bend[1]),
                        hatch=side if hatch else 0, narrow="tip", full=False, color=GOLD)
    f = M.stroke(M.polyline_d(pp), FINE, color=GOLD, role="petiole") + lf
    return f, M.region(M.polyline_d(lf.meta["outline"], closed=True)), q


def wreath(cx: float, cy: float, r: float, *, pairs: int = 3, outer: dict | None = None,
           inner: dict | None = None, spike: dict | None = None, knot_deg: float = 90.0,
           tip_deg: float = 30.0, step_deg: float = 14.0, first: float = 0.55, shrink: float = 0.06) -> M.Frag:
    """§G.6 / §H.15 the wild-rice half-wreath cupping the club from 4 to 8
    o'clock: ONE continuous arc stem per side (radius ``r`` round the pip
    centre) from the reed-node knot at 6 o'clock (``knot_deg``) to 4 o'clock
    (``tip_deg``), where it runs on into a flowering spike (§G.5).

    * Every ``step_deg`` (14°) of stem from ``first`` × pitch, ``pairs`` PAIRS
      of ribbon blades (§G.4) spring tangentially from it, each pair 6 %
      (``shrink``) smaller than the last toward the tip. Blades keep §G.4's
      10–14 : 1 (``outer`` / ``inner`` specs, :data:`BLADE_OUTER` /
      :data:`BLADE_INNER`) on S midribs, so the wreath reads as wild-rice
      GRASS: short 4 : 1 vesicas on a stem read as olive / laurel, which
      §G.6 bans (art-director review). Three pairs: a fourth, at 50°, would
      reach its blades into the spike.
    * Tip-ward blades lie over knot-ward ones (T-junctions on the front
      outline, hatch included); the blades break 4.2 px clear of the spike's
      lines (interlace); the stem is never broken by its own blades.
    * The spike: three erect awned spikelets on 8 px pedicels, so every
      spikelet stands >= 3 px clear of the stalk; the stem runs on 10 px up
      its stalk (drawn over it), so the first pedicel springs from ONE line.
    * The two stems run into the knot's node ellipse and end on its rim; the
      cut ends splay below it (deck.motifs.rice's reed-node knot)."""
    outer = dict(BLADE_OUTER, **(outer or {}))
    inner = dict(BLADE_INNER, **(inner or {}))
    pts = G.arc_pts(cx, cy, r, knot_deg, tip_deg, n=400)
    cv = G.Curve(pts)
    pitch = math.radians(step_deg) * r
    units, bases = [], []
    for k in range(pairs):
        s = (first + k) * pitch
        p, t = cv.at_s(s), cv.tangent_s(s)
        a = math.degrees(math.atan2(t[1], t[0]))
        sc = (1 - shrink) ** k
        # +1 = left of travel: on the right-hand branch (knot -> 4 o'clock) that is the inside
        for side, spec in ((1, inner), (-1, outer)):
            L = spec["L"] * sc
            f, reg, q = wreath_blade(p, a, side, L, L / spec["ratio"], spec["angle"], spec["bend"], spec["hatch"])
            units.append((f, reg))
            bases.append(q)
    # the flowering spike on the stem's end
    p, t = cv.at_s(cv.length), cv.tangent_s(cv.length)
    sk = dict(n_female=3, n_male=0, spikelet_len=12.0, awn=15.0, female_spread=64.0, pedicel=8.0, f_pitch=14.0)
    sk.update(spike or {})
    length = sk.pop("length", 44.0)
    sp = M.rice_stalk(p[0], p[1], math.degrees(math.atan2(t[1], t[0])), length, color=GOLD, **sk)
    # stacking, back to front: knot-ward blades lie under tip-ward ones
    lv, front = M.Frag(), None
    for f, reg in units[::-1]:
        lv += M.occlude(f, front) if front is not None else f
        front = reg if front is None else front.union(reg)
    lv = M.cut(lv, sp.shape(), A.CLEAR)
    lv = M.prune_hatch(M.drop_specks(lv, 4.2, roles=None), 1.3)
    # ONE continuous stem, running on 10 px up the spike's stalk
    stem = M.stroke(M.polyline_d(pts) + M.polyline_d([p - t * 1.0, p + t * 10.0]), FINE, color=GOLD, role="stem")
    branch = stem + lv + sp
    out = branch + branch.mirror_x(cx)
    knot = RI._reed_knot((cx, pts[0][1]), 90.0, color=GOLD)
    out = M.drop_specks(M.occlude(out, knot.meta["zone"]), 4.2, roles=None) + knot
    out.meta.update(stem=pts, bases=bases, pairs=pairs)
    return out
