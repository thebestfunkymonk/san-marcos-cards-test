"""art/_qc_fan.py — Q♣ · the egret-plume fan (§H.8: "at the breast, holds an
egret-plume fan (paper, current lines)").

Each plume is a paper lock whose spine rises from the ferrule and droops
outward (an egret's breeding aigrette arches and falls); its width swells
from the root and tapers to a fine point. Its §G.24 current lines are
offsets of the plume's OUTER (convex) edge — like a lock of hair — so they
run nearly to the tip and, as the plume narrows, end one after another in
curled Ø6.3 terminals: the lacy, wispy fall of the filaments. The plumes
spray out of a gold ferrule (a reed node) on a short gold handle.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM
from inkkit import geom as G

P, R, U = K.P, K.R, K.U
FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR


def _biggest(g):
    ps = K._polys_of(g.buffer(0))
    return max(ps, key=lambda q: q.area) if ps else Polygon()


def plume(root, heading, length, *, bend=(-8.0, -50.0), split=0.45, w_root=7.0, w_max=26.0, peak=0.40,
          power=1.0, w_tip=0.0, n=3, first=None, stagger=5.0, curl_r=4.2, curl_deg=85.0, edge=CONTOUR,
          min_len=16.0, mode="outer", barb=38.0, barb_room=4.0):
    """One egret plume from ``root`` along ``heading``: the spine is two
    tangent arcs (``bend`` degrees over ``split`` of the length and the
    rest; − = counter-clockwise), the half-width swells from ``w_root``/2
    to ``w_max``/2 at ``peak`` and falls to a point at the tip. Current lines
    are offsets of the CONVEX edge (the side the plume droops away from),
    ``first`` px inside it, 7 px apart, each rolling inward into a terminal.
    → Part (paper: no fill; meta: mid, tip, outer)."""
    _, mid, _ = FM.arc_path(root[0], root[1], heading, [(length * split, bend[0]), (length * (1 - split), bend[1])])
    cv = G.Curve(np.asarray(mid, float))
    L = cv.length
    s = np.linspace(0, L, 500)
    pts = cv.at_s(s)
    nrm = cv.normal_s(s)
    t = s / L
    hw = np.where(t < peak,
                  w_root / 2 + (w_max - w_root) / 2 * np.sin(np.pi / 2 * t / peak),
                  w_tip / 2 + ((w_max - w_tip) / 2) * np.cos(np.pi / 2 * (t - peak) / (1 - peak)) ** power)
    left = pts + nrm * hw[:, None]
    right = pts - nrm * hw[:, None]
    reg = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    if w_tip > 0:                                   # a rounded tip
        reg = reg.union(K.R(K.circle(pts[-1], w_tip / 2)))
    reg = _biggest(reg)
    reg = reg.buffer(0.8, quad_segs=8).buffer(-0.8, quad_segs=8)
    # the convex edge: G.Curve normals point to the traveller's RIGHT, so
    # ``left`` above is really the right-hand edge. A counter-clockwise (−)
    # spine curves to its left: the convex edge is on its right, and the
    # lines are offset from it toward the traveller's left (current_lines
    # side +1), and vice versa.
    turn = bend[0] + bend[1]
    outer, side = (left, -1) if turn < 0 else (right, +1)
    first_ = (edge / 2 + K.GAP + FINE / 2 + 0.1) if first is None else first
    f = C.Frag()
    placed = Polygon()
    if mode == "vane":
        # the vane: n parallel offsets of the SPINE (7 px apart, centred),
        # from the root (hidden under the ferrule) toward the tip; where the
        # narrowing plume would squeeze a line against its edge, the line
        # sweeps OUT (``barb``°) and butts into the outline like a feather's
        # barb — no free ends, no hairline wedges
        offs = [(k - (n - 1) / 2) * K.PITCH for k in range(n)]
        hw_s = np.interp(np.linspace(0, L, 2000), s, hw)
        ss = np.linspace(0, L, 2000)
        edge_d = reg.boundary
        for o in offs:
            if abs(o) < 1e-6:
                continue
            g = np.asarray(cv.offset(o, spacing=0.5))
            gc = G.Curve(g)
            # arc length on the spine ≈ on the offset (gentle curvature)
            need = abs(o) + FINE / 2 + K.GAP_MARK + MEDIUM / 2 + barb_room
            past = np.where((ss > L * peak) & (hw_s < need))[0]
            s_c = ss[past[0]] if len(past) else L * 0.9
            s_c = min(s_c * gc.length / L, gc.length - 1.0)
            body = gc.sub(0, s_c / gc.length).pts
            tg = body[-1] - body[-2]
            tg = tg / np.hypot(*tg)
            nr = np.array([-tg[1], tg[0]])
            # outward = away from the spine
            sp = cv.at_s(min(s_c, L))
            if np.dot(body[-1] - sp, nr) < 0:
                nr = -nr
            a_ = math.radians(barb)
            v = tg * math.cos(a_) + nr * math.sin(a_)
            ext = np.vstack([body, body[-1] + v * 40.0])
            ln = LineString(ext).intersection(reg)
            parts = [q for q in getattr(ln, "geoms", [ln]) if q.geom_type == "LineString" and q.length > min_len]
            if not parts:
                continue
            q = max(parts, key=lambda g_: g_.length)
            f += C.stroke(np.asarray(q.coords), FINE, role="current")
        return K.Part(reg, C.Frag(), K.outline(reg) + f, {"mid": np.asarray(mid), "tip": np.asarray(mid)[-1],
                                                          "outer": outer})
    for kk in range(n):
        ln = K.current_lines(outer, 1, reg, side=side, first=first_ + kk * K.PITCH, edge=MEDIUM, stagger=0.0,
                             curl_r=curl_r, curl_deg=curl_deg, placed=placed, min_len=min_len)
        for q in ln.meta.get("lines", []):
            placed = placed.union(LineString(q).buffer(FINE / 2))
        for m in ln.marks:
            if m.role == "terminal":
                placed = placed.union(R(G.from_skia(m.skia())))
        f += ln
    return K.Part(reg, C.Frag(), K.outline(reg) + f, {"mid": np.asarray(mid), "tip": np.asarray(mid)[-1],
                                                      "outer": outer})


def fan(fist, axis, plumes, *, handle_len=30.0, handle_w=12.0, neck=36.0, root_dy=8.0, ferrule=(13.0, 7.5), **kw):
    """The fan: gold handle along ``axis``° through the ``fist`` point
    (``handle_len`` below it, ``neck`` above it to the ferrule), the
    ferrule (a gold reed-node ellipse ``ferrule`` = (rx, ry)) and the plumes
    ``plumes`` = [(heading, length, bend, w_max)] springing from just above
    it. → list of (name, Part) back to front."""
    u = np.array([math.cos(math.radians(axis)), math.sin(math.radians(axis))])
    f = np.asarray(fist, float)
    top = f + u * neck
    root = top + u * root_dy
    out = []
    for i, (hd, L, bend, wm) in enumerate(plumes):
        out.append((f"plume{i}", plume(tuple(root), hd, L, bend=bend, w_max=wm, **kw)))
    out.append(("handle", K.staff(tuple(f - u * handle_len), tuple(top), handle_w)))
    fer = R(C.ellipse_d(top[0], top[1], ferrule[0], ferrule[1], axis + 90.0))
    out.append(("ferrule", K.Part(fer, K.fill(fer, K.GOLD), K.outline(fer), {})))
    return out
