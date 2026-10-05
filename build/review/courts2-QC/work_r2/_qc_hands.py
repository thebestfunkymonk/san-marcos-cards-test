"""art/_qc_hands.py — Q♣ · court-local refinements of the kit hands (deck.courtkit
is shared and owned elsewhere; these patch only the Q♣ calls).

    tuck(hand, sc)         the kit's own wrist tuck (``Hand.tucked``), frozen:
                           → a Hand whose Part is final (stub 0), so a patch
                           to its lines survives ``add_to``
    palm_tips(part, ...)   the kit's palm-view fist draws three fingertip lobes
                           at the heel end of the finger lines; the lowest
                           (little finger) ends 3.2 px above the block's
                           underside, its round cap ~0.2 px from the heel's
                           contour — a hook touching the line (§I.12). The
                           little finger's tip is the one a closed fist hides
                           under the heel: the lobe is left out and finger
                           line 3 ends freely, like the back-view lines.
    notch_stubs(...)       a textile line that crosses the notch where a wrist
                           meets its wider cuff shows as a free 5–9 px stub
                           there: pieces of the pattern, once cut by the hand
                           and the cuff, that lie wholly near that corner and
                           are short are dropped (a whole leaf elsewhere stays)
    strip_to_paper(...)    ground left between a sleeve and a haloed shaft
                           narrower than a band turns to paper (the kit does
                           this for the heel pocket above the cuff; below it
                           a 3–6 px jade strip with a spur was left).
"""
from __future__ import annotations

import numpy as np
import shapely

from deck import courtkit as K
from deck.motifs import core as C


def tuck(hand: K.Hand, sc: K.Scene, cuff=None) -> K.Hand:
    """The hand as ``add_to`` would stack it (wrist cut on the cuff), frozen."""
    hp = hand.tucked(sc, cuff)
    return K.Hand(hp, hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, 0.0)


def _pts(d):
    return np.asarray(C.sample_d(d, 0.5)[0][0], float)


def palm_tips(hand: K.Hand, *, drop_lowest=True) -> K.Hand:
    """Drop the lowest palm-view fingertip lobe (see the module docstring).
    'Lowest' = the lobe nearest the heel side of the block, i.e. the one
    farthest from the thumb crease. → Hand (frozen)."""
    hp = hand.hand
    inner = hp.meta.get("inner")
    if inner is None or not drop_lowest:
        return hand
    tips = [m for m in inner.marks if m.role == "fingertip"]
    if len(tips) < 2:
        return hand
    thumb = [m for m in inner.marks if m.role in ("thumb",)]
    ref = np.vstack([_pts(m.d) for m in thumb]).mean(axis=0) if thumb else None
    if ref is None:
        return hand
    far = max(tips, key=lambda m: float(np.hypot(*(_pts(m.d).mean(axis=0) - ref))))
    new_inner = C.Frag([m for m in inner.marks if m is not far], inner.meta)
    lines = C.Frag([m for m in hp.lines.marks if m is not far], hp.lines.meta)
    part = K.Part(hp.shape, hp.fills, lines, {**hp.meta, "inner": new_inner})
    return K.Hand(part, hand.thumb, hand.wrist, hand.wrist_w, hand.wrist_dir, 0.0)


def strip_to_paper(sc: K.Scene, name: str, shaft: str, arms, *, below, above=None, close=K.HEEL_CLOSE,
                   band=None):
    """Turn the ground between the arm regions ``arms`` (item names) and the
    haloed item ``shaft`` into paper where it is narrower than 2 × ``close``
    (the kit's heel-pocket rule, continued down the sleeve), between y
    ``above`` (default: none) and ``below``. Adds an empty channel item
    ``name`` in front of the ground (halo_zone = that strip)."""
    it = {i.name: i for i in sc.items}
    sh = it[shaft]
    A = sh.occ.buffer(sh.halo + K.MEDIUM / 2, quad_segs=12)
    arm_r = shapely.union_all([it[a].occ for a in arms if a in it])
    both = shapely.union_all([A, arm_r])
    gap = both.buffer(close, quad_segs=12).buffer(-close, quad_segs=12).difference(both)
    y0 = -K.BIG if above is None else above
    gap = gap.intersection(shapely.box(-K.BIG, y0, K.BIG, below))
    gap = shapely.union_all([g for g in K._polys_of(gap) if g.area > 2.0 and g.distance(A) < 0.6
                             and g.distance(arm_r) < 0.6]) if not gap.is_empty else gap
    if gap.is_empty:
        return None
    sc.add(name, C.Frag(), gap, sil=False, halo=sh.halo, halo_skip=tuple(sh.halo_skip) + tuple(arms),
           halo_only=sh.halo_only, halo_zone=gap)
    return gap


def notch_stubs(frag: C.Frag, joins, *, roles=("leaf", "hatch", "midrib"), radius=12.0,
                max_len=14.0) -> C.Frag:
    """The COMPOSED frag minus every stroke piece of ``roles`` shorter than
    ``max_len`` that lies wholly within ``radius`` of ``joins`` (the points
    where a wrist meets its cuff): the textile's stubs in that notch."""
    from dataclasses import replace
    from inkkit import geom as G
    if joins is None or joins.is_empty:
        return frag
    near = joins.buffer(radius)
    out = []
    for m in frag.marks:
        if m.kind != "stroke" or not m.d or m.role not in roles:
            out.append(m)
            continue
        d = ""
        for pts, closed in G.as_polys(m.d, 0.05):
            pts = np.asarray(pts, float)
            if len(pts) > 1 and not closed:
                ln = shapely.LineString(pts)
                if ln.length < max_len and near.contains(ln):
                    continue
            d += C.polyline_d(pts, closed=closed)
        if d:
            out.append(replace(m, d=d))
    return C.Frag(out, frag.meta)
