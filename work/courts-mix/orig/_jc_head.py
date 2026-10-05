"""art/_jc_head.py — J♣ · The River Squire: hair and the heron plume.

Built from deck.courtkit primitives (G1 arc splines, current lines with
curled Ø6.3 terminals, legal strokes), at final size, card px (top half).
"""
from __future__ import annotations

import math
import re

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


# ---------------------------------------------------------------------------
# hair: the near-side bob (behind the ear, under the cap's turned-up back)
# ---------------------------------------------------------------------------
def hair_bob(outer, inner, *, n=4, stagger=9.0, side=+1, color=GOLD, first=None):
    """A bob of hair as one region between an ``outer`` edge (a G1 spline
    through points, root → rolled end) and an ``inner`` edge (points, end →
    root, hidden under the head / collar). Current lines (§G.24) are offsets
    of the outer edge toward ``side`` (+1 = screen-left of travel), each
    rolling into a Ø6.3 terminal; line k is ``stagger``·k shorter. → Part."""
    od = spl(outer)
    op = pts_of(od, 0.3)
    ip = pts_of(spl(inner), 0.3)
    reg = Polygon(np.vstack([op, ip])).buffer(0)
    reg = reg.buffer(1.0, join_style=1).buffer(-1.0, join_style=1)
    lines = K.current_lines(op, n, reg, side=side, edge=CONTOUR, stagger=stagger,
                            first=first)
    return K.Part(reg, K.fill(reg, color), lines + K.outline(reg), {"outer": op})


# ---------------------------------------------------------------------------
# the heron plume
# ---------------------------------------------------------------------------
def heron_plume(guide_pts, *, w_max=24.0, w_root=9.0, swell=0.35, h0=None, h1=None, quill=0.55,
                n_lines=1, stagger=10.0, tip_curl=None):
    """A great-blue-heron plume (§H.9: paper, current lines, gold quill) on
    an S guide from the root (tucked at the cap) to the tip: a slender paper
    vane swelling to ``w_max`` at ``swell`` of its length and drawn out to a
    long point (a heron's occipital plume is a ribbon, not a quill-feather);
    a GOLD quill along its centre from the root to ``quill`` of the length,
    ending in a gold Ø6.3 terminal; ``n_lines`` current lines either side of
    the quill streaming on toward the tip into Ø6.3 terminals. → Part."""
    gd = spl(guide_pts, h0=h0, h1=h1)
    g = pts_of(gd, 0.3)
    cv = K.G.Curve(g)
    L = cv.length
    s = np.linspace(0, L, 400)
    pts = cv.at_s(s)
    tang = np.array([cv.tangent_s(x) for x in s])
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
    t = s / L
    hw = np.where(t < swell, w_root / 2 + (w_max - w_root) / 2 * np.sin(t / swell * np.pi / 2),
                  w_max / 2 * np.cos((t - swell) / (1 - swell) * np.pi / 2) ** 0.9)
    hw[-1] = 0.0
    left = pts + nrm * hw[:, None]
    right = pts - nrm * hw[:, None]
    ring = np.vstack([left, right[::-1][1:]])
    vane = Polygon(ring).buffer(1.2, join_style=1).buffer(-1.2, join_style=1).buffer(0)
    lines = C.Frag()
    qi = int(np.searchsorted(s, quill * L))
    q = pts[:qi]
    lines += K.line(C.polyline_d(q), MEDIUM, color=GOLD, role="quill")
    lines += K.dot(q[-1], K.TD, color=GOLD, role="quill-end")
    placed = LineString(q).buffer(MEDIUM / 2).union(Point(*q[-1]).buffer(K.TD / 2))
    for sd in (+1, -1):
        off = MEDIUM / 2 + K.GAP + FINE / 2 + 0.2
        lines += K.current_lines(g, n_lines, vane, side=sd, first=off, edge=CONTOUR, stagger=stagger,
                                 placed=placed)
    return K.Part(vane, C.Frag(), lines + K.outline(vane), {"guide": g, "vane": vane})


def strands(guides, region, *, edge=CONTOUR, curl_r=4.2, curl_deg=80.0, curl_side=+1, placed=None,
            ends=None, w=FINE, color=INK, min_len=12.0):
    """Hair strands (§G.24 current lines drawn one by one): each guide (a
    point list, root → free end) is clipped to ``region``; its free end rolls
    ``curl_deg`` toward ``curl_side`` (+1 = screen-left of travel) on radius
    ``curl_r`` into a Ø6.3 terminal. The end is pulled back until the curl and
    terminal sit ≥ 3 px + half the edge inside the region and ≥ 3 px from
    every strand already placed. ``ends`` optionally caps each strand's
    length (px from its root). → Frag (meta['lines'])."""
    reg = K.R(region)
    tr = K.TD / 2
    safe = reg.buffer(-(tr + K.GAP_MARK + edge / 2 + 0.1), quad_segs=12)
    body_zone = reg.buffer(-(w / 2 + K.GAP_MARK + edge / 2), quad_segs=12)
    acc = placed if placed is not None else Polygon()
    f = C.Frag()
    out = []
    sides = list(curl_side) if isinstance(curl_side, (list, tuple)) else [curl_side] * len(guides)
    for k, g in enumerate(guides):
        if isinstance(g, str):
            gp = pts_of(g, 0.25)
        elif len(g) <= 8:                         # control points: a G1 arc spline through them
            gp = pts_of(spl(g), 0.25)
        else:
            gp = np.asarray(g, float)
        ln = LineString(gp).intersection(reg)
        pieces = [p for p in K._lines_of(ln) if p.length >= min_len]
        if not pieces:
            continue
        base = LineString(gp)
        pieces.sort(key=lambda p: base.project(Point(p.coords[0])))
        q = np.asarray(pieces[0].coords)
        if base.project(Point(q[0])) > base.project(Point(q[-1])):
            q = q[::-1]
        pc = K.G.Curve(q)
        Lp = pc.length
        s = Lp if ends is None or ends[k] is None else min(Lp, ends[k])
        while s > min_len:
            body = pc.sub(0, s / Lp).pts
            tail = K._curl(body, sides[k], curl_r, curl_deg)
            tp = tail[-1]
            seg = LineString(tail[max(0, len(body) - 2):])
            ok = safe.contains(Point(*tp)) and body_zone.contains(seg)
            if ok and not acc.is_empty:
                tg = Point(*tp).buffer(tr, quad_segs=12)
                ok = (acc.distance(tg) >= K.GAP_MARK + 0.05
                      and acc.distance(LineString(tail).buffer(w / 2)) >= K.GAP_MARK + 0.05)
            if ok:
                f += C.stroke(tail, w, color=color, role="current")
                f += C.dot(tp[0], tp[1], K.TD, color=color, role="terminal")
                out.append(tail)
                acc = acc.union(LineString(tail).buffer(w / 2 + 1.1)).union(Point(*tp).buffer(tr))
                break
            s -= 1.0
    f.meta["lines"] = out
    return f


def offsets(guide_pts, dists):
    """Parallel offsets of one guide (points) at the given signed distances
    (+ = screen-left of travel)."""
    cv = K.G.Curve(np.asarray(guide_pts, float))
    return [cv.offset(d, spacing=0.5) if d else cv.resample(0.5) for d in dists]


def scallop_edge(pts, sag):
    """d (continuing, no M) of scallops through ``pts`` each bulging ``sag``
    to the screen-left of travel."""
    return "".join(K.arc_sag(P(a), P(b), sag, move=False) for a, b in zip(pts[:-1], pts[1:]))


def _tail(d):
    """Strip the leading M of a path so it can continue another."""
    return re.sub(r"^M\s*[-\d.]+[ ,]\s*[-\d.]+", "", d.strip(), count=1)


def hair_locks(back, scallops, front, strand_guides, *, sag=-7.0, curl_side=-1, curl_r=4.2, curl_deg=90.0,
               color=GOLD, ends=None):
    """Hair whose lower edge is a row of rolled lock ends: ``back`` (points,
    root → first scallop point) is the outer edge, ``scallops`` the points
    along the lower edge (each span bulges ``sag``, + = screen-left of
    travel), ``front`` (points, from the last scallop point) runs back up to
    the root under the head / cap. Each strand guide (points, root → end)
    runs down into one lock and rolls into a Ø6.3 terminal. → Part."""
    d = spl(back) + scallop_edge(scallops, sag) + _tail(spl([scallops[-1]] + list(front))) + "Z"
    reg = K.R(d).buffer(0)
    lines = strands(strand_guides, reg, curl_side=curl_side, curl_r=curl_r, curl_deg=curl_deg, ends=ends)
    return K.Part(reg, K.fill(reg, color), lines + K.outline(reg), {})


def plume_vane(guide_pts, *, w_max=30.0, w_root=12.0, swell=0.42, h0=None, h1=None, tip_pow=0.9, vane_from=0.0):
    """The plume's paper vane on an S guide (root → tip): swelling to
    ``w_max`` at ``swell`` of its length, drawn out to a long point.
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
    hw[-1] = 0.0
    ring = np.vstack([pts + nrm * hw[:, None], (pts - nrm * hw[:, None])[::-1][1:]])
    vane = Polygon(ring).buffer(0)
    if vane_from:
        vane = vane.union(Point(*pts[0]).buffer(w_root / 2, quad_segs=24))      # a rounded base
    vane = vane.buffer(1.2, join_style=1).buffer(-1.2, join_style=1).buffer(0)
    return vane, g, cv


def heron_plume2(guide_pts, *, w_max=31.0, w_root=12.0, swell=0.42, n=3, stagger=14.0, quill=26.0,
                 quill_w=7.0, quill_back=14.0, h0=None, h1=None, tip_pow=0.9, curl_side=-1, curl_deg=70.0,
                 vane_from=0.0):
    """§H.9 heron plume, §G.24 style: a paper vane on an S guide carrying
    ``n`` current lines (FINE, 7 px pitch, centred on the guide, their free
    ends staggered by ``stagger`` and rolled into Ø6.3 terminals toward the
    tip), springing from a GOLD quill: a slim gold vesica (``quill`` px along
    the guide, ``quill_w`` wide, starting ``quill_back`` px before the root,
    under the cap) with an Aquifer contour; the lines butt into it.
    → (vane Part, quill Part): add the vane, then the quill in front."""
    vane, g, cv = plume_vane(guide_pts, w_max=w_max, w_root=w_root, swell=swell, h0=h0, h1=h1, tip_pow=tip_pow,
                             vane_from=vane_from)
    L = cv.length
    off0 = -(n - 1) / 2 * K.PITCH
    guides = []
    for k in range(n):
        o = off0 + k * K.PITCH
        guides.append(cv.offset(o, spacing=0.5) if abs(o) > 1e-6 else cv.resample(0.5))
    qp = cv.sub(0, min(1.0, quill / L)).pts
    q0, q1 = qp[0], qp[-1]
    u = (q1 - q0) / np.hypot(*(q1 - q0))
    qreg = K.R(K.vesica(q0 - u * quill_back, q1, quill_w)).buffer(0)
    order = sorted(range(n), key=lambda k: abs(k - (n - 1) / 2))            # the centre line is the longest
    ends = [None] * n
    for rank, k in enumerate(order):
        ends[k] = L - rank * stagger
    # outer lines first, each curling AWAY from the centre (its terminal then
    # clears the line that runs on); the centre line last
    sides = [(-1 if (off0 + k * K.PITCH) < 0 else +1) if abs(off0 + k * K.PITCH) > 1e-6 else curl_side
             for k in range(n)]
    seq = order[::-1]
    lines = strands([guides[k] for k in seq], vane.difference(qreg), curl_side=[sides[k] for k in seq], curl_r=4.2,
                    curl_deg=curl_deg, ends=[ends[k] for k in seq])
    vp = K.Part(vane, C.Frag(), lines + K.outline(vane), {"guide": g})
    qpart = K.Part(qreg, K.fill(qreg, GOLD), K.outline(qreg), {})
    return vp, qpart


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
                 quill=34.0, quill_w=8.0, quill_back=16.0, curl_r=4.2, curl_deg=100.0, shaft=None):
    """§H.9 great-blue-heron plume: a PAPER vane on an S guide (root at the
    cap → tip), swelling to ``w_max`` and drawn out to a long point, carrying
    §G.24 current lines — each (offset from the guide, start s, end s,
    curl side), s in px along the guide (a negative end counts back from
    the tip) — that stream toward the tip and roll into Ø6.3 terminals;
    springing from a GOLD quill (a slim vesica, Aquifer contour) tucked
    under the cap. Explicit line ends (heal checks them).
    → (vane Part, quill Part)."""
    vane, g, cv = plume_vane(guide_pts, w_max=w_max, w_root=w_root, swell=swell, h0=h0, h1=h1, tip_pow=tip_pow,
                             vane_from=vane_from)
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
