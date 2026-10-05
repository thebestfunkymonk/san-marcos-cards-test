"""art/_jc_body.py — J♣ · The River Squire: the body (jerkin, sleeves, arms,
collar, belt, placket), built from deck.courtkit / deck.motifs primitives at
final size in card px (top half). Every builder returns a courtkit Part.
"""
from __future__ import annotations

import math
import re

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG

P = K.P
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR


def spl(points, h0=None, h1=None, headings=None):
    return K.spline([P(p) for p in points], h_start=h0, h_end=h1, headings=headings)


def _tail(d):
    return re.sub(r"^M\s*[-\d.]+[ ,]\s*[-\d.]+", "", d.strip(), count=1)


def chain(*segs):
    """Closed path through consecutive segments; each segment is either a
    list of points (a G1 arc spline through them) or ('L', pts) for straight
    lines. Segment k starts where segment k−1 ended."""
    d = ""
    for i, sg in enumerate(segs):
        if isinstance(sg, tuple) and sg[0] == "L":
            pts = [P(p) for p in sg[1]]
            dd = "M" + "L".join(f"{p[0]:.2f} {p[1]:.2f}" for p in pts)
        elif isinstance(sg, tuple) and sg[0] == "S":         # spline with end headings
            _, pts, h0, h1 = sg
            dd = spl(pts, h0, h1)
        else:
            dd = spl(sg)
        d += dd if i == 0 else _tail(dd)
    return d + "Z"


def region(*segs):
    return K.R(chain(*segs)).buffer(0)


def pts_of(d, step=0.4):
    return C.sample_d(d, step)[0][0]


# ---------------------------------------------------------------------------
# knock-out comb sprays (§G.18, cypress foliage) for the jade sleeves
# ---------------------------------------------------------------------------
def comb_ko(field, paths, *, w=MEDIUM, pitch=9.0, tick=11.0, angle=52.0, inset=None):
    """Comb sprays along ``paths`` (d strings), clipped ``inset`` inside the
    field and knocked out of it (paper lines in the jade). → jade fill Frag."""
    f = C.Frag()
    for p in paths:
        f += MG.comb_spray(p, pitch=pitch, tick=tick, angle=angle, w=w)
    reg = K.R(field)
    ins = (MEDIUM / 2 + 3.2) if inset is None else inset
    f = K.clip_in(f, reg.buffer(-ins))
    return C.knockout(K.D(reg), f)


def sleeve_part(reg, sprays=(), *, color=JADE, **kw):
    """A jade sleeve region with comb sprays knocked out along ``sprays``."""
    reg = K.R(reg)
    fill = K.fill(comb_ko(reg, sprays, **kw), color) if sprays else K.fill(reg, color)
    return K.Part(reg, fill, K.outline(reg), {})


def cuff(p_top0, p_top1, depth, *, sag=2.5, color=RED):
    """A cuff band: its top edge the chord p_top0 → p_top1 (sagging ``sag``),
    ``depth`` px deep toward the hand (the left normal of the chord)."""
    a, b = P(p_top0), P(p_top1)
    u = (b - a) / np.hypot(*(b - a))
    n = np.array([u[1], -u[0]])
    d = K.Path(a).sag(b, sag).line(b + n * depth).sag(a + n * depth, -sag).close().d
    reg = K.R(d)
    return K.Part(reg, K.fill(reg, color), K.outline(reg), {})


# ---------------------------------------------------------------------------
# pecan (Carya illinoinensis) compound leaf, for knocking out of the red
# ---------------------------------------------------------------------------
def _leaf_region(mid_pts, width):
    from deck.motifs import forms as FM
    mid = np.asarray(mid_pts, float)
    _, _, ring = FM.leaf_edges(mid, FM.vesica_hw(K.G.Curve(mid).length, width))
    return Polygon(ring).buffer(0)


def pecan_leaf(base, heading_deg, *, length=78.0, pairs=4, leaflet=(24.0, 5.6), angle=42.0, step=12.5,
               bend=6.0, falcate=2.6, shrink=0.07, rachis_w=MEDIUM, terminal=True, first=10.0, alt=0.0):
    """A pecan leaf (pinnately compound): a gently arched rachis carrying
    ``pairs`` (sub-)opposite pairs of long lanceolate, FALCATE leaflets swept
    ``angle`` degrees toward the tip, shrinking ``shrink`` per pair toward the
    tip, and one terminal leaflet. Neighbouring leaflets on one side keep ≥ 3 px
    (step·sin(angle) − width). ``alt`` staggers the two sides (px along the
    rachis): pecan leaflets are often sub-opposite. Returns an ink Frag of
    fills + the rachis (to knock out of red)."""
    b = P(base)
    u = K.unit(heading_deg)
    tip = b + u * length
    rd = K.arc_sag(b, tip - u * leaflet[0] * 0.9, bend)
    rp = pts_of(rd, 0.25)
    cv = K.G.Curve(rp)
    Lr = cv.length
    f = C.Frag()
    f += K.line(rd, rachis_w, role="rachis")
    for k in range(pairs):
        for sg in (-1, 1):
            s = first + k * step + (alt if sg > 0 else 0.0)
            if s > Lr - 2.0:
                continue
            p = cv.at_s(s)
            tg = cv.tangent_s(s)
            h = math.degrees(math.atan2(tg[1], tg[0]))
            ll = leaflet[0] * (1.0 - shrink * k)
            a = h + sg * angle
            q = p + K.unit(a) * ll
            mid = (p + q) / 2 + K.unit(a + sg * 90.0) * falcate           # bowed away: the tip hooks forward (falcate)
            mp = pts_of(K.spline([p - K.unit(a) * 0.6, mid, q]), 0.3)
            f += K.fill(_leaf_region(mp, leaflet[1] * (1.0 - shrink * k * 0.5)), INK, role="leaflet")
    if terminal:
        e = cv.at_s(Lr)
        tg = cv.tangent_s(Lr)
        h = math.degrees(math.atan2(tg[1], tg[0]))
        q = e + K.unit(h) * leaflet[0] * 0.95
        mp = pts_of(K.spline([e - K.unit(h) * 1.5, (e + q) / 2 + K.unit(h - 90) * 0.8, q]), 0.3)
        f += K.fill(_leaf_region(mp, leaflet[1]), INK, role="leaflet")
    return f


def pecan_nut(c, heading_deg=-90.0, *, L=15.0, W=9.5):
    """A small gold pecan nut (a pointed ovoid): solid gold with an Aquifer
    FINE contour (§C.4: gold on red only as a contoured solid). → (Frag, region)."""
    c = P(c)
    u = K.unit(heading_deg)
    reg = K.R(K.vesica(c - u * L / 2, c + u * L / 2, W)).buffer(1.2, join_style=1).buffer(-1.2, join_style=1)
    return K.fill(reg, GOLD, role="nut") + K.outline(reg, FINE, role="nut"), reg


def pecan_field(region, *, pitch=(58.0, 50.0), origin=(300.0, 330.0), heading=-58.0, margin=4.0, nut_at=(0.5, 0.5),
                nuts=True, leaf_kw=None, nut_heading=-100.0):
    """The jerkin's pattern: a half-drop grid of pecan leaves (an ink Frag
    to KNOCK OUT of the red) and, at ``nut_at`` of each cell, a gold pecan
    nut (contoured solid, drawn on top). Every motif is kept whole inside
    ``region`` (inset ``margin``), and nuts keep ≥ 3 px + FINE from leaves.
    → (leaf Frag, nut Frag)."""
    reg = K.R(region)
    inner = reg.buffer(-margin)
    x0, y0, x1, y1 = reg.bounds
    ox, oy = origin
    px, py = pitch
    kw = dict(length=80.0, pairs=3, leaflet=(22.0, 5.2), angle=55.0, step=14.0, falcate=0.8, first=10.0,
              shrink=0.03, bend=3.0)
    kw.update(leaf_kw or {})
    L = kw["length"]
    leaves, nutf, placed = C.Frag(), C.Frag(), []
    j0, j1 = int(math.floor((y0 - oy) / py)) - 2, int(math.ceil((y1 - oy) / py)) + 2
    cells = []
    for j in range(j0, j1 + 1):
        off = px / 2 if j % 2 else 0.0
        for i in range(int(math.floor((x0 - ox - off) / px)) - 2, int(math.ceil((x1 - ox - off) / px)) + 3):
            cells.append((i, j, ox + off + i * px, oy + j * py))
    for i, j, cx, cy in cells:
        base = P(cx, cy) - K.unit(heading) * L / 2
        lf = pecan_leaf(base, heading, **kw)
        sh = lf.shape()
        if inner.contains(sh):
            leaves += lf
            placed.append(sh)
    if nuts:
        allp = shapely.union_all(placed) if placed else Polygon()
        for i, j, cx, cy in cells:
            c = (cx + px * nut_at[0], cy + py * nut_at[1] * 0.0 + (py * nut_at[1] if nut_at[1] else 0.0))
            f, nreg = pecan_nut(c, nut_heading)
            if inner.contains(nreg.buffer(1.0)) and allp.distance(nreg) > 3.0 + FINE:
                nutf += K.atomic(f, f"nut{i}_{j}")
    return leaves, nutf


# ---------------------------------------------------------------------------
# reed-ladder guards (§G.19) along the jerkin's front edges
# ---------------------------------------------------------------------------
def ladder_guard(edge, width=15.0, *, side=+1, rung=19.0, node_every=4, node_ry=4.6, start=10.0, end=10.0,
                 extend=(0.0, 0.0), clip=None):
    """A PAPER guard (trim band) along ``edge`` (points, a G1 spline through
    them), ``width`` px to ``side`` (+1 = screen-left of travel): its two
    rails are the band's outline; FINE Aquifer rungs cross it every ``rung``
    px, and every ``node_every``-th rung is a reed-node ellipse tangent to
    both rails — the House of the Reed's ladder (§G.19) as a Tudor guard.
    The region is paper (never painted: it only hides the red behind it).
    ``extend`` lengthens the band past the edge's ends; ``clip`` limits it.
    → Part (meta 'inner' = the offset rail points)."""
    d = spl(edge)
    ep = pts_of(d, 0.3)
    cv = K.G.Curve(ep)
    if any(extend):
        t0 = cv.tangent_s(0.0)
        t1 = cv.tangent_s(cv.length)
        ep = np.vstack([[ep[0] - t0 * extend[0]], ep, [ep[-1] + t1 * extend[1]]])
        cv = K.G.Curve(ep)
    off = cv.offset(side * width, spacing=0.4)
    reg = Polygon(np.vstack([ep, off[::-1]])).buffer(0)
    if clip is not None:
        reg = reg.intersection(K.R(clip)).buffer(0)
    lines = K.outline(reg)
    L = cv.length
    n = int((L - start - end) // rung)
    s0 = start + ((L - start - end) - n * rung) / 2
    inner = reg.buffer(-0.4)
    for k in range(n + 1):
        s = s0 + k * rung
        p = cv.at_s(s)
        t = cv.tangent_s(s)
        nrm = np.array([t[1], -t[0]]) * side         # toward the band (screen-left × side)
        a, b = p, p + nrm * width
        if node_every and k % node_every == node_every // 2:
            c = (a + b) / 2
            ang = math.degrees(math.atan2(nrm[1], nrm[0]))
            e = C.stroke(K.G.ellipse_d(c[0], c[1], width / 2, node_ry, ang), FINE, role="node")
            lines += K.clip_in(e, reg.buffer(0.3)) if False else e
        else:
            lines += K.clip_in(K.seg(a - nrm * 2.0, b + nrm * 2.0, FINE, role="rung"), inner)
    return K.Part(reg, C.Frag(), lines, {"inner": off})


def falling_collar(cf=(371.0, 303.0), *, L0=(346, 290), Lo=(326, 314), Lt=(334, 338), R0=(410, 288),
                   Ro=(430, 311), Rt=(416, 339), ci_dy=12.0, hem=0.0):
    """The squire's falling band (paper): two pointed collar wings lying on
    the chest, joined at the throat. The top edge runs from each neck side
    (L0 / R0) down to the centre front ``cf``; each wing's outer edge runs
    out and down through Lo / Ro to its point (Lt / Rt), and its inner edge
    back up to the centre front ``ci_dy`` px below ``cf``. A FINE hem runs
    ``hem`` px inside each wing's outer edge. Paper is never painted: the
    region only hides what is behind. → Part."""
    cf, L0, Lo, Lt, R0, Ro, Rt = (P(p) for p in (cf, L0, Lo, Lt, R0, Ro, Rt))
    ci = cf + P(0.0, ci_dy)
    pth = (K.Path(L0).sag(cf, 1.5).sag(R0, 1.5)
           .sag(Ro, 3.0).sag(Rt, 2.0).line(ci)
           .line(Lt).sag(Lo, 2.0).sag(L0, 3.0).close())
    reg = K.R(pth.d).buffer(0.6, join_style=1).buffer(-0.6, join_style=1)
    lines = K.outline(reg)
    if hem:
        for side in (-1, 1):
            a, b, c = (Ro, Rt, ci) if side > 0 else (Lo, Lt, ci)
            top = R0 if side > 0 else L0
            hd = K.Path(top).sag(a, 3.0).sag(b, 2.0).line(c).d if side > 0 else K.Path(c).line(b).sag(a, 2.0).sag(top, 3.0).d
            hp = C.sample_d(hd, 0.3)[0][0]
            off = K.G.Curve(hp).offset(-hem if side > 0 else -hem, spacing=0.4)
            lines += K.clip_in(C.stroke(C.polyline_d(off), FINE, role="hem"),
                               reg.buffer(-(hem - 1.2)).difference(K.box(cf[0] - 6, 0, cf[0] + 6, 2000)))
    return K.Part(reg, C.Frag(), lines, {"cf": cf})
