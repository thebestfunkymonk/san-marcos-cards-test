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


