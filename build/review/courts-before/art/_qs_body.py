"""art/_qs_body.py — Q♠ · The Blind Oracle: veil, hair and garments.

Built the kit's way (deck.courtkit): G1 arc splines through planned points,
regions + fills + MEDIUM outlines, FINE current lines and seams, knockouts as
geometry. Q♠-specific; see QS.py for the composition plan.

    cspline        a CLOSED G1 arc spline through points (the kit's spline is open)
    veil           the paper veil: the whole drape (behind hair and head) + the
                   crown over the head (in front of them), sparse contour lines
    hair           gold hair under the veil: the bands framing the face and
                   the long locks falling in front of the shoulders
    gown_front     the paper gown panel: sparse contour lines + dotted side seam
    lining         a red turned-back mantle front with a knocked-out pattern
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM
from inkkit import geom as G

P = K.P
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD


def biggest(g):
    ps = K._polys_of(g)
    return max(ps, key=lambda q: q.area) if ps else Polygon()


def cspline(pts, headings=None):
    """A closed G1 chain of tangent circular arcs through ``pts`` (the tangent
    at each point from the circle through it and its neighbours; ``headings``
    {i: deg} pins any). → d."""
    pts = [P(p) for p in pts]
    n = len(pts)
    hs = [FM.circle_heading(pts[i - 1], pts[i], pts[(i + 1) % n]) for i in range(n)]
    for i, h in (headings or {}).items():
        hs[i] = h
    d, _ = FM.biarc_chain(pts, hs, closed=True)
    return d


def ospline(pts, h0=None, h1=None, headings=None):
    """Open arc spline → (d, dense points)."""
    d, q, _ = FM.arc_spline([P(p) for p in pts], h0, h1, headings=headings)
    return d, np.asarray(q)


def sample(d, step=0.4):
    return C.sample_d(d, step)[0][0]


# -----------------------------------------------------------------------------
# veil
# -----------------------------------------------------------------------------
def veil(outline_pts, opening_pts, *, guides=(), headings=None, edge_w=MEDIUM):
    """The paper veil (§H.2 'a paper veil with sparse contour lines'): one
    closed spline silhouette over the head, falling to the shoulders, and a
    face OPENING (a closed spline; its boundary inside the veil is the
    veil's front edge, framing the face and hair; open to the bottom so the
    hair locks fall over the drape).

    Returns (back, front): ``back`` = the whole veil (stack it BEHIND the
    hair and head); ``front`` = veil − opening (stack it IN FRONT of hair and
    head; its only interior line is the MEDIUM front edge). The sparse
    contour lines are FINE current lines (§G.24): ``guides`` = [(points
    root → free end, n, side, stagger, first)] following the veil's edges
    (the fall of the cloth), each rolling into a Ø6.3 terminal."""
    d = cspline(outline_pts, headings)
    reg = biggest(K.R(d).buffer(0))
    opening = K.R(cspline(opening_pts)).buffer(0)
    front = biggest(reg.difference(opening))
    lines = C.Frag()
    placed = Polygon()
    for g in guides:
        pts, n, side, stag = g[:4]
        first = g[4] if len(g) > 4 else 8.6
        _, q = ospline(pts)
        f = K.current_lines(q, n, front, side=side, edge=CONTOUR, stagger=stag, first=first, placed=placed)
        lines += f
        for ln in f.meta.get("lines", []):
            placed = placed.union(LineString(ln).buffer(FINE / 2 + 0.1))
    edge = opening.boundary.intersection(reg.buffer(-0.3))
    elines = C.Frag()
    for ln in K._lines_of(shapely.line_merge(edge) if edge.geom_type != "LineString" else edge):
        if ln.length > 4:
            elines += K.line(C.polyline_d(np.asarray(ln.coords)), edge_w, role="veil-edge")
    return (K.Part(reg, C.Frag(), K.outline(reg), {"d": d}),
            K.Part(front, C.Frag(), elines + lines, {"opening": opening}))


# -----------------------------------------------------------------------------
# hair under the veil
# -----------------------------------------------------------------------------
def hair(outline_pts, *, guides, face=None, headings=None, color=GOLD):
    """Gold hair under the veil (§H.2 'gold hair in current lines under the
    veil'): one closed spline region — the bands framing the face and the
    long locks falling in front of the shoulders — stacked BEHIND the head
    (the face covers its middle). ``guides``: [(points root → free end, n,
    side, stagger, first)] current lines (§G.24) following the lock edges,
    each rolling into a Ø6.3 terminal (fitted against the visible hair:
    ``face`` is subtracted first). → Part."""
    d = cspline(outline_pts, headings)
    reg = biggest(K.R(d).buffer(0))
    vis = reg.difference(face.buffer(CONTOUR / 2 + 0.5)) if face is not None else reg
    lines = C.Frag()
    placed = Polygon()
    for g in guides:
        pts, n, side, stag = g[:4]
        first = g[4] if len(g) > 4 else None
        _, q = ospline(pts)
        f = K.current_lines(q, n, vis, side=side, edge=MEDIUM, stagger=stag, first=first, placed=placed)
        lines += f
        for ln in f.meta.get("lines", []):
            placed = placed.union(LineString(ln).buffer(FINE / 2 + 0.1))
    return K.Part(reg, K.fill(reg, color), lines + K.outline(reg), {"d": d})


# -----------------------------------------------------------------------------
# pointed veil (Q♠ pass 4+)
# -----------------------------------------------------------------------------
def pointed_region(left_pts, apex, right_pts, *, apex_in=-40.0, apex_out=40.0, bottom=None):
    """A closed region whose top is a SOFT POINT (a Gothic / Spring Lake lens
    arch, §G.26): the arc spline ``left_pts`` (foot → up) arrives at ``apex``
    heading ``apex_in`` (screen deg), the arc spline ``right_pts`` leaves it
    heading ``apex_out`` (apex → foot); closed straight across the feet (or
    through ``bottom`` points). → (region, left dense pts, right dense pts)."""
    fp = [P(p) for p in left_pts] + [P(apex)]
    npts = [P(apex)] + [P(p) for p in right_pts]
    _, pl, _ = FM.arc_spline(fp, headings={len(fp) - 1: apex_in})
    _, pr, _ = FM.arc_spline(npts, headings={0: apex_out})
    pl, pr = np.asarray(pl), np.asarray(pr)
    ring = np.vstack([pl, pr[1:]] + ([np.asarray(bottom, float)] if bottom is not None else []))
    reg = biggest(Polygon(ring).buffer(0))
    return reg, pl, pr


def open_spline(pts, h0=None, h1=None, headings=None):
    """Open G1 arc spline through ``pts`` → dense points."""
    _, q, _ = FM.arc_spline([P(p) for p in pts], h0, h1, headings=headings)
    return np.asarray(q)


def ribbon(out_pts, in_pts, *, end_round=True, h0=None, h1=None):
    """A lock / band region between two open arc splines drawn top → bottom
    (``out_pts`` the outer edge, ``in_pts`` the inner), its bottom end a
    semicircle through the two end points (a rolled lock end). → (region,
    outer dense pts, inner dense pts)."""
    po = open_spline(out_pts, h0, h1)
    pi = open_spline(in_pts, h0, h1)
    ring = [po, pi[::-1]]
    reg = Polygon(np.vstack(ring)).buffer(0)
    if end_round:
        a, b = po[-1], pi[-1]
        c = (a + b) / 2
        reg = reg.union(Point(*c).buffer(float(np.hypot(*(a - b))) / 2, quad_segs=24))
    reg = biggest(reg.buffer(0.6, quad_segs=6).buffer(-0.6, quad_segs=6))
    return reg, po, pi


def lock_part(out_pts, in_pts, *, n=3, side=+1, stagger=10.0, hide=None, color=GOLD, first=None):
    """A gold hair lock (§G.24): ``ribbon`` filled gold, MEDIUM outline, ``n``
    FINE current lines offset from the OUTER edge (``side`` +1 = screen-left
    of travel down it) rolling into Ø6.3 terminals, fitted against the lock's
    VISIBLE part (``hide``: the regions in front, e.g. face and neck)."""
    reg, po, pi = ribbon(out_pts, in_pts)
    vis = reg.difference(hide.buffer(MEDIUM / 2 + 0.3)) if hide is not None else reg
    vis = biggest(vis)
    lines = K.current_lines(po, n, vis, side=side, edge=MEDIUM, stagger=stagger, first=first)
    return K.Part(reg, K.fill(reg, color), lines + K.outline(reg), {"out": po, "in": pi, "vis": vis})
