"""art/_qs_finish.py — Q♠ compose finish: the kit's Scene.compose() with two
repairs slotted in BEFORE the heal (the kit heals first, so a repair made
after it would be unchecked):

* ``close_rings`` — a closed ring that ``clip_out`` re-serialised as an open
  polyline (ends coincide) is closed again with ``Z``. Open, its seam renders
  with round caps (and heal's skia outline agrees) while QA 12 (GEOS) buffers
  it as a ring with a miter spike there: the two disagree by up to 10 × w/2.
* ``trap_cut`` — §2.1 of ART_CONTRACT (the layer trap): where two contours
  meet at an acute junction the ink is wider than a CONTOUR line, and the red
  / gold fills trapped under it are a lower plate hidden under a higher solid
  (QA 4c). The fills are cut back under such ink solids (by the solid minus
  ``keep`` px, so they still run under every line: no hairline, no change in
  the print).

``compose(sc)`` → Frag, exactly what ``build()`` prints; ``sc.heal_log`` is
refreshed. Upstream candidate: Scene.compose(close_rings=True, trap_cut=True).
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G

HIDE_OPEN = K.CONTOUR / 2 + 0.3          # deck.qa's 4c opening radius


def close_rings(f: C.Frag) -> C.Frag:
    out = []
    for m in f.marks:
        if m.kind != "stroke" or not m.d:
            out.append(m)
            continue
        polys = G.as_polys(m.d, 0.05)
        if not any((not c) and len(p) > 3 and np.allclose(p[0], p[-1], atol=0.02) for p, c in polys):
            out.append(m)
            continue
        d = ""
        for pts, closed in polys:
            pts = np.asarray(pts, float)
            shut = len(pts) > 3 and np.allclose(pts[0], pts[-1], atol=0.02)
            if closed or shut:
                d += C.polyline_d(pts[:-1] if shut else pts, closed=True)
            else:
                d += C.polyline_d(pts)
        out.append(replace(m, d=d))
    return C.Frag(out, f.meta)


def trap_cut(f: C.Frag, keep=1.4, uppers=("ink", "gold")) -> C.Frag:
    """Cut every fill of a lower layer back from the solids (wider than a
    CONTOUR line) of each layer in ``uppers`` above it."""
    order = ["jade", "red", "gold", "ink"]
    marks = list(f.marks)
    for U in uppers:
        ms = [m for m in marks if m.layer == U and m.d]
        if not ms:
            continue
        sol = C.Frag(ms).shape()
        sol = sol.buffer(-HIDE_OPEN, quad_segs=8).buffer(HIDE_OPEN - keep, quad_segs=8)
        if sol.is_empty:
            continue
        lower = order[:order.index(U)]
        new = []
        for m in marks:
            if m.kind == "fill" and m.layer in lower and m.d:
                s = G.to_shape(m.d, tol=0.05)
                if s.intersects(sol):
                    s = s.difference(sol)
                    d = G.from_shape(s)
                    if d:
                        new.append(replace(m, d=d))
                    continue
            new.append(m)
        marks = new
    return C.Frag(marks, f.meta)


def drop_crumbs(f: C.Frag, min_area=40.0, keep_roles=("dot", "pupil", "bubble", "bead", "terminal")) -> C.Frag:
    """Remove the crumbs clipping leaves of a big fill: pieces under
    ``min_area`` px² of a fill mark that also has a bigger piece (e.g. a
    lining corner left between two paper halos)."""
    out = []
    for m in f.marks:
        if m.kind != "fill" or not m.d or m.role in keep_roles:
            out.append(m)
            continue
        s = G.to_shape(m.d, tol=0.05)
        pcs = K._polys_of(s)
        if len(pcs) < 2 or not any(p.area < min_area for p in pcs):
            out.append(m)
            continue
        big = [p for p in pcs if p.area >= min_area]
        if big:
            d = G.from_shape(K.U(*big))
            if d:
                out.append(replace(m, d=d))
    return C.Frag(out, f.meta)


def compose(sc, cut_y=511.0, trap=True):
    res = sc.compose(heal_gaps=False)
    res = close_rings(res)
    if trap:
        res = trap_cut(res)
    band = C.stroke(f"M100 {cut_y:g}L650 {cut_y:g}", K.FINE, style="rule", role="_band")
    log = []
    res = K.heal(res + band, log=log, keep_roles=("contour", "_band"))
    sc.heal_log = log
    return drop_crumbs(res.select(lambda m: m.role != "_band"))
