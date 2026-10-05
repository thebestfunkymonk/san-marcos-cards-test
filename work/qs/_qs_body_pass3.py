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
