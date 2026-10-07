"""art/_jc_head.py — J♣ · The River Squire: hair and the heron plume.

Built from deck.courtkit primitives (G1 arc splines, current lines with
curled Ø6.3 terminals, legal strokes), at final size, card px (top half).
"""
from __future__ import annotations


import numpy as np
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C

P = K.P
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR


def spl(points, h0=None, h1=None, headings=None, closed=False):
    return K.spline([P(p) for p in points], h_start=h0, h_end=h1, headings=headings, closed=closed)


def pts_of(d, step=0.4):
    return C.sample_d(d, step)[0][0]
















def plume_vane(guide_pts, *, w_max=30.0, w_root=12.0, swell=0.42, h0=None, h1=None, tip_pow=0.9, vane_from=0.0,
               tip_r=0.0, bulb=0.0):
    """The plume's paper vane on an S guide (root → tip): swelling to
    ``w_max`` at ``swell`` of its length, drawn out to a long point — or,
    with ``tip_r``, to a round end of that radius (+ ``bulb``: a round
    terminal a little wider than the neck before it).
    → (vane region, guide points, curve)."""
    gd = spl(guide_pts, h0=h0, h1=h1)
    g = pts_of(gd, 0.3)
    cv = K.G.Curve(g)
    L = cv.length
    s = np.linspace(0, L, 400)
    pts = cv.at_s(s)
    tang = np.array([cv.tangent_s(x) for x in s])
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
    t = np.clip((s - vane_from) / (L - vane_from), 0.0, 1.0)
    hw = np.where(t < swell, w_root / 2 + (w_max - w_root) / 2 * np.sin(t / swell * np.pi / 2),
                  w_max / 2 * np.cos((t - swell) / (1 - swell) * np.pi / 2) ** tip_pow)
    keep = s >= vane_from
    pts, nrm, hw = pts[keep], nrm[keep], hw[keep]
    if tip_r:
        hw = np.maximum(hw, np.where(np.arange(len(hw)) > len(hw) // 3, tip_r, 0.0))
    else:
        hw[-1] = 0.0
    ring = np.vstack([pts + nrm * hw[:, None], (pts - nrm * hw[:, None])[::-1][1:]])
    vane = Polygon(ring).buffer(0)
    if tip_r:
        vane = vane.union(Point(*pts[-1]).buffer(tip_r + bulb, quad_segs=24))
    if vane_from:
        vane = vane.union(Point(*pts[0]).buffer(w_root / 2, quad_segs=24))      # a rounded base
    vane = vane.buffer(1.2, join_style=1).buffer(-1.2, join_style=1).buffer(0)
    return vane, g, cv




def pageboy(outer, inner, *, n=4, first=9.0, pitch=K.PITCH, ends=None, starts=None, curl_side=-1, curl_r=4.2,
            curl_deg=110.0, color=GOLD, edge=CONTOUR):
    """The squire's page-boy hair (§G.24): ONE gold region between the
    ``outer`` edge (points, crown → rolled end, a G1 spline) and the hidden
    ``inner`` edge (points, from the rolled end back up under the head, cap
    and collar). ``n`` current lines are offsets of the outer edge at
    ``first`` + k·pitch inside it (7 px pitch), running down the fall; line k
    runs from ``starts[k]`` to ``ends[k]`` (px along the OUTER edge) and
    rolls ``curl_deg`` toward ``curl_side`` into a Ø6.3 terminal — the
    staggered lock ends. Explicit ends (no search): the caller places them,
    heal checks them. → Part."""
    od = spl(outer)
    op = pts_of(od, 0.3)
    ip = pts_of(spl(inner), 0.3)
    reg = Polygon(np.vstack([op, ip])).buffer(0)
    reg = reg.buffer(1.0, join_style=1).buffer(-1.0, join_style=1)
    inside = reg.buffer(-(edge / 2 + K.GAP_MARK + FINE / 2), quad_segs=12)
    cv = K.G.Curve(op)
    L = cv.length
    f = C.Frag()
    guides = []
    for k in range(n):
        a = 0.0 if starts is None else starts[k]
        b = L if ends is None else ends[k]
        sub = K.G.Curve(cv.sub(a / L, min(b, L) / L).pts)
        g = sub.offset(-(first + k * pitch), spacing=0.5)
        ln = LineString(g).intersection(inside)
        pcs = [np.asarray(q.coords) for q in K._lines_of(ln) if q.length > 10.0]
        if not pcs:
            continue
        q = max(pcs, key=lambda z: LineString(z).length)
        if np.hypot(*(q[0] - g[0])) > np.hypot(*(q[-1] - g[0])):
            q = q[::-1]
        tail = K._curl(q, curl_side, curl_r, curl_deg)
        f += C.stroke(tail, FINE, color=INK, role="current")
        f += C.dot(tail[-1][0], tail[-1][1], K.TD, color=INK, role="terminal")
        guides.append(tail)
    return K.Part(reg, K.fill(reg, color), f + K.outline(reg), {"outer": op, "guides": guides, "L": L})


def heron_plume3(guide_pts, *, w_max=26.0, w_root=11.0, swell=0.40, tip_pow=0.9, vane_from=20.0, h0=None, h1=None,
                 lines=((0.0, 30.0, -34.0, +1), (-7.0, 38.0, -62.0, -1), (7.0, 44.0, -80.0, +1)),
                 quill=34.0, quill_w=8.0, quill_back=16.0, curl_r=4.2, curl_deg=100.0, shaft=None, tip_r=0.0,
                 bulb=0.0):
    """§H.9 great-blue-heron plume: a PAPER vane on an S guide (root at the
    cap → tip), swelling to ``w_max`` and drawn out to a long point, carrying
    §G.24 current lines — each (offset from the guide, start s, end s,
    curl side), s in px along the guide (a negative end counts back from
    the tip) — that stream toward the tip and roll into Ø6.3 terminals;
    springing from a GOLD quill (a slim vesica, Aquifer contour) tucked
    under the cap. Explicit line ends (heal checks them).
    → (vane Part, quill Part)."""
    vane, g, cv = plume_vane(guide_pts, w_max=w_max, w_root=w_root, swell=swell, h0=h0, h1=h1, tip_pow=tip_pow,
                             vane_from=vane_from, tip_r=tip_r, bulb=bulb)
    L = cv.length
    qp = cv.sub(0, min(1.0, quill / L)).pts
    q0, q1 = qp[0], qp[-1]
    u = (q1 - q0) / np.hypot(*(q1 - q0))
    qreg = K.R(K.vesica(q0 - u * quill_back, q1, quill_w)).buffer(0)
    inside = vane.buffer(-(CONTOUR / 2 + K.GAP_MARK + FINE / 2), quad_segs=12).difference(
        qreg.buffer(MEDIUM / 2 + K.GAP_MARK))
    f = C.Frag()
    gold_line = C.Frag()
    if shaft:
        # the quill's shaft runs on up the vane's centre as a MEDIUM gold line
        # into a gold Ø6.3 terminal (gold is line, §C.1; on paper, never on red)
        sp = cv.sub(max(0.0, (quill - 4.0) / L), shaft / L).pts
        gold_line += C.stroke(sp, MEDIUM, color=GOLD, role="quill")
        gold_line += C.dot(sp[-1][0], sp[-1][1], K.TD, color=GOLD, role="quill-end")
        inside = inside.difference(LineString(sp).buffer(MEDIUM / 2 + K.GAP + FINE / 2 - 0.05))
        inside = inside.difference(Point(*sp[-1]).buffer(K.TD / 2 + K.GAP_MARK + FINE / 2))
    for off, s0, s1, side in lines:
        a = s0 if s0 >= 0 else L + s0
        b = s1 if s1 >= 0 else L + s1
        sub = K.G.Curve(cv.sub(a / L, b / L).pts)
        gg = sub.offset(off, spacing=0.5) if off else sub.resample(0.5)
        ln = LineString(gg).intersection(inside)
        pcs = [np.asarray(q.coords) for q in K._lines_of(ln) if q.length > 10.0]
        if not pcs:
            continue
        q = max(pcs, key=lambda z: LineString(z).length)
        if np.hypot(*(q[0] - gg[0])) > np.hypot(*(q[-1] - gg[0])):
            q = q[::-1]
        tail = K._curl(q, side, curl_r, curl_deg) if side else q
        f += C.stroke(tail, FINE, color=INK, role="current")
        f += C.dot(tail[-1][0], tail[-1][1], K.TD, color=INK, role="terminal")
    vp = K.Part(vane, C.Frag(), gold_line + f + K.outline(vane), {"guide": g, "L": L})
    qpart = K.Part(qreg, K.fill(qreg, GOLD), K.outline(qreg), {})
    return vp, qpart


def far_lock(outer, inner, *, axis=375.0, **kw):
    """The far-side lock of a 3/4-LEFT head (the viewer's left temple, under
    the cap's peak): ``pageboy`` drawn in the mirror (so its current lines
    fall on the inside of the lock and curl toward the face, as the near
    side's do) and mirrored back about ``axis``. Points are given in CARD
    coordinates (outer: under the brim → the rolled end; inner: back up,
    hidden under the face). → Part."""
    mo = [(2 * axis - x, y) for x, y in outer]
    mi = [(2 * axis - x, y) for x, y in inner]
    return pageboy(mo, mi, **kw).mirrored(axis)
