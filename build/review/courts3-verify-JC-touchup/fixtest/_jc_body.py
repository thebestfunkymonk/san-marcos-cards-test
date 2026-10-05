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


def sleeve_part(reg, sprays=(), *, color=JADE, ink=False, avoid=None, **kw):
    """A jade sleeve region with comb sprays along ``sprays``: knocked out
    (paper, MEDIUM) or, with ``ink``, drawn in Aquifer FINE on the jade
    (§C.4 'patterns in Aquifer on jade'), clear of ``avoid``."""
    reg = K.R(reg)
    if ink and sprays:
        return K.Part(reg, K.fill(reg, color), K.outline(reg) + comb_ink(reg, sprays, avoid=avoid, **kw), {})
    fill = K.fill(comb_ko(reg, sprays, **kw), color) if sprays else K.fill(reg, color)
    return K.Part(reg, fill, K.outline(reg), {})


def comb_ink(field, paths, *, w=FINE, pitch=9.0, tick=11.0, angle=52.0, inset=None, cone=None, avoid=None,
             edge=CONTOUR):
    """§G.18 comb sprays along ``paths`` (d strings) drawn in Aquifer FINE on
    a jade field (§C.4), kept clear of the field's edge (``edge`` weight +
    3 px) and of ``avoid`` (the objects that will lie in front: hands,
    cuffs, the jerkin): a tick is kept whole or dropped (no stubs under a
    hand), the rachis is clipped. → ink Frag."""
    reg = K.R(field)
    ins = (edge / 2 + K.GAP + w / 2 + 0.3) if inset is None else inset
    zone = reg.buffer(-ins)
    if avoid is not None:
        zone = zone.difference(K.R(avoid).buffer(MEDIUM / 2 + K.GAP_MARK + w / 2 + 0.3))
    out = C.Frag()
    for p in paths:
        f = MG.comb_spray(p, pitch=pitch, tick=tick, angle=angle, w=w, cone=cone)
        for m in f.marks:
            one = C.Frag([m])
            if m.role == "tick":
                if zone.contains(one.shape()):
                    out += one
            else:
                out += K.clip_in(one, zone)
    return out


def cuff(p_top0, p_top1, depth, *, sag=2.5, color=RED, flare=(0.0, 0.0)):
    """A cuff band: its top edge the chord p_top0 → p_top1 (sagging ``sag``),
    ``depth`` px deep toward the hand (the left normal of the chord).
    ``flare`` = (px at p_top0's end, px at p_top1's end): the hand-side edge
    runs that much further out than the top chord (a turned-back cuff that
    opens wider than the forearm, so the wrist tapers into it)."""
    a, b = P(p_top0), P(p_top1)
    u = (b - a) / np.hypot(*(b - a))
    n = np.array([u[1], -u[0]])
    a2, b2 = a + n * depth - u * flare[0], b + n * depth + u * flare[1]
    d = K.Path(a).sag(b, sag).line(b2).sag(a2, -sag).close().d
    reg = K.R(d)
    return K.Part(reg, K.fill(reg, color), K.outline(reg), {"inner_edge": (a2, b2)})


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
                 extend=(0.0, 0.0), clip=None, color=None):
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
    fills = K.fill(reg, color) if color else C.Frag()
    return K.Part(reg, fills, lines, {"inner": off})


def falling_collar(cf=(371.0, 303.0), *, L0=(346, 290), Lo=(326, 314), Lt=(334, 338), R0=(410, 288),
                   Ro=(430, 311), Rt=(416, 339), ci_dy=12.0, hem=0.0, color=None):
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
    return K.Part(reg, K.fill(reg, color) if color else C.Frag(), lines, {"cf": cf})


def pecan_sprig(base, heading_deg, *, leaf_kw=None, nut=(14.0, 9.0), nut_gap=4.2, nut_spread=26.0, nut_back=9.0):
    """One pecan sprig for the jerkin's weave: a pinnate leaf (``pecan_leaf``,
    to knock out of the red) springing from ``base`` toward ``heading_deg``,
    and a PAIR of gold nuts hanging from the petiole's foot, splayed
    ``nut_spread``° either side of straight back (contoured solids, §C.4).
    → (leaf Frag, nut Frag, nut region)."""
    kw = dict(leaf_kw or {})
    b = P(base)
    lf = pecan_leaf(b, heading_deg, **kw)
    u = K.unit(heading_deg)
    L, W = nut
    nf, regs = C.Frag(), []
    for sg in (-1, 1):
        h = heading_deg + 180.0 + sg * nut_spread
        c = b - u * nut_back * 0.3 + K.unit(h) * (L / 2 + nut_gap + 1.5)
        f, r = pecan_nut(c, h, L=L, W=W)
        nf += f
        regs.append(r)
    return lf, nf, K.U(*regs)


def sprig_field(region, *, pitch=(56.0, 60.0), origin=(300.0, 360.0), heading=-66.0, margin=4.0, leaf_kw=None,
                nut=(14.0, 9.0), nut_spread=26.0, shift=0.0):
    """A half-drop lattice of pecan sprigs (leaf + nut pair), each kept whole
    inside ``region`` (inset ``margin``). ``shift`` px offsets alternate rows
    along x (the drop). → (leaf Frag to knock out, nut Frag on top)."""
    reg = K.R(region)
    inner = reg.buffer(-margin)
    x0, y0, x1, y1 = reg.bounds
    ox, oy = origin
    px, py = pitch
    kw = dict(leaf_kw or {})
    L = kw.get("length", 80.0)
    leaves, nutf = C.Frag(), C.Frag()
    j0, j1 = int(math.floor((y0 - oy) / py)) - 2, int(math.ceil((y1 - oy) / py)) + 2
    for j in range(j0, j1 + 1):
        off = (px / 2 if j % 2 else 0.0) + shift * (j % 2)
        for i in range(int(math.floor((x0 - ox - off) / px)) - 2, int(math.ceil((x1 - ox - off) / px)) + 3):
            cx, cy = ox + off + i * px, oy + j * py
            base = P(cx, cy) - K.unit(heading) * L / 2
            lf, nf, nr = pecan_sprig(base, heading, leaf_kw=kw, nut=nut, nut_spread=nut_spread)
            sh = K.U(lf.shape(), nr.buffer(FINE / 2))
            if inner.contains(sh):
                leaves += lf
                nutf += K.atomic(nf, f"nuts{i}_{j}")
    return leaves, nutf


def leaf_field(region, *, pitch=(62.0, 72.0), origin=(300.0, 360.0), heading=-66.0, margin=7.0, leaf_kw=None,
               drop=0.5, whole=False, min_frac=0.55):
    """A half-drop lattice of pecan leaves (an ink Frag to KNOCK OUT of the
    red), clipped to ``region`` inset ``margin`` (a plain border) — a woven
    print that runs off the panel edges. Leaves with less than ``min_frac``
    of their area inside are dropped (no stray leaflet crumbs); ``whole``
    keeps only leaves wholly inside."""
    reg = K.R(region)
    inner = reg.buffer(-margin)
    x0, y0, x1, y1 = reg.bounds
    ox, oy = origin
    px, py = pitch
    kw = dict(leaf_kw or {})
    L = kw.get("length", 80.0)
    out = C.Frag()
    j0, j1 = int(math.floor((y0 - oy) / py)) - 2, int(math.ceil((y1 - oy) / py)) + 2
    for j in range(j0, j1 + 1):
        off = px * drop * (j % 2)
        for i in range(int(math.floor((x0 - ox - off) / px)) - 2, int(math.ceil((x1 - ox - off) / px)) + 3):
            cx, cy = ox + off + i * px, oy + j * py
            base = P(cx, cy) - K.unit(heading) * L / 2
            lf = pecan_leaf(base, heading, **kw)
            sh = lf.shape()
            if whole:
                if inner.contains(sh):
                    out += lf
                continue
            a_in = sh.intersection(inner).area
            if a_in < min_frac * sh.area:
                continue
            out += K.clip_in(lf, inner) if a_in < sh.area - 0.5 else lf
    return out


def belt_hand(at, angle=40.0, *, side=-1, wrist_w=24.0, knuckle_w=30.0, back_len=24.0, finger_len=(19.0, 22.0, 21.0, 17.0),
              thumb=(4.0, 30.0), thumb_w=10.5, thumb_off=1.5, curl=0.0):
    """A hand resting on the belt (§H.0 mitten, 3 finger lines, separate
    thumb), seen from the back: the back of the hand widens from the wrist
    (``at``, width ``wrist_w``) to the knuckles (``back_len`` further along
    ``angle``); four rounded finger columns (their lengths ``finger_len``
    from the thumb side, the middle finger longest) lie side by side and
    close into one mitten with round tips; three MEDIUM finger lines run
    from the valleys between the tips back toward the knuckles; the THUMB is
    a separate capsule along the thumb-side edge (``side`` −1: the thumb is
    on the screen-left of the pointing direction), from ``thumb[0]`` to
    ``thumb[1]`` px along the hand. Built in a local frame and placed
    rigidly. → courtkit Hand."""
    fw = knuckle_w / 4.0
    cols = []
    tips = []
    ys = [(-1.5 + k) * fw for k in range(4)]            # local y of each finger (thumb side = −y)
    for y, L in zip(ys, finger_len):
        x1 = back_len + L - fw / 2
        cols.append(LineString([(back_len - 4.0, y), (x1, y)]).buffer(fw / 2 + 0.35, cap_style=1, quad_segs=16))
        tips.append((x1 + fw / 2, y))
    fingers = shapely.union_all(cols)
    back = Polygon([(0.0, -wrist_w / 2), (back_len, -knuckle_w / 2), (back_len, knuckle_w / 2), (0.0, wrist_w / 2)])
    hand = shapely.union_all([fingers, back]).buffer(1.2, quad_segs=8).buffer(-1.2, quad_segs=8)
    lines = C.Frag()
    for k in range(3):
        y = (ys[k] + ys[k + 1]) / 2
        xt = min(tips[k][0], tips[k + 1][0]) - fw * 0.55
        lines += K.seg(P(xt, y), P(back_len - 2.0, y), MEDIUM, role="finger")
    ty = -(knuckle_w / 2 + thumb_off) if side < 0 else (knuckle_w / 2 + thumb_off)
    th = LineString([(thumb[0], ty * 0.82), (thumb[1], ty)]).buffer(thumb_w / 2, quad_segs=16)
    M, Mf = K._rigid(at, angle, mirror_x=False)
    hand_s, thumb_s = K._xf(hand, M), K._xf(th, M)
    hl = (K.outline(hand) + lines).transformed(Mf)
    tl = K.outline(th).transformed(Mf)
    return K.Hand(K.Part(hand_s, C.Frag(), hl, {"kind": "belt"}), K.Part(thumb_s, C.Frag(), tl, {}), P(at), wrist_w)


def _drop_short_runs(stalk, cover, min_len, holes=None):
    """The stalk with every run that shows between covering objects shorter
    than ``min_len`` removed (a 6 px reed stub poking out between a hand and
    the buckle reads as a stray white hook). ``cover``: the region in front.
    A run that ends on a node (``holes``: the node regions) is kept whatever
    its length: it reads as the stalk leaving that node and passing under
    the cover, not as a stray piece."""
    if cover is None or min_len <= 0:
        return stalk
    cover = K.R(cover)
    node_r = K.U(*holes) if holes else None
    nodes = node_r.buffer(MEDIUM) if holes else None
    kill = []
    for m in stalk.marks:
        for pts, _closed in C.sample_d(m.d, 0.4):
            vis = LineString(pts).difference(cover)
            for g in K._lines_of(vis):
                if g.length >= min_len:
                    continue
                if nodes is not None and g.intersects(nodes):
                    # a node's run is kept when its other end passes under a cover
                    # or into the next node — not when it stops in the open (a stub
                    # left by the pattern's clip)
                    ends = [Point(*g.coords[0]), Point(*g.coords[-1])]
                    if all(e.distance(node_r) < 1.0 or e.distance(cover) < 1.0 for e in ends):
                        continue
                kill.append(g.buffer(MEDIUM, cap_style=2))
    if not kill:
        return stalk
    return K.clip_out(stalk, K.U(*kill), eps=0.0, trap=0.0)


def reed_belt(clip, *, y=440.0, h=24.0, sag=4.0, x0=200.0, x1=570.0, front=358.0, node_every=58.0, node=(7.0, 4.0),
              skip=None, avoid=None, color=JADE, cover=None, min_run=0.0, rise=(2.0, 4.0), node_phase=0.0):
    """The squire's belt: a jade band across the jerkin, sagging ``sag`` at
    ``front``, with the House of the Reed's stalk KNOCKED OUT along its
    centre (§G.19 / the ♣ partition line): a MEDIUM paper stalk with outlined
    node ellipses (``node`` = (rx, ry)) every ``node_every`` px from the
    front (+ ``node_phase``). ``rise``: how far the belt's two ends ride
    above ``y``. ``skip`` (a region, e.g. the buckle) keeps the pattern
    clear. ``avoid`` (a region: the hands, cuffs and forearms in front) drops any node that
    would sit partly under it — the stalk runs on under, a node is whole or
    hidden, never a paper 'C' against a hand. ``cover`` (the region in
    front: hands, cuffs, sleeves, the paddle's channel) with ``min_run``:
    stalk runs showing between them shorter than ``min_run`` are dropped.
    → Part (meta 'mid' = the centre line points)."""
    mid_pts = [P(x0, y - rise[0]), P(front, y + sag), P(x1, y - rise[1])]
    top = spl([p + P(0, -h / 2) for p in mid_pts])
    bot = spl([p + P(0, h / 2) for p in mid_pts][::-1])
    d = top + f"L{x1:.2f} {y - rise[1] + h / 2:.2f}" + _tail(bot) + "Z"
    reg = K.R(d).buffer(0).intersection(K.R(clip))
    mid = pts_of(spl(mid_pts), 0.4)
    cv = K.G.Curve(mid)
    s_front = None
    dd = np.hypot(mid[:, 0] - front, mid[:, 1] - (y + sag))
    s_front = float(K.G.Curve(mid[: int(np.argmin(dd)) + 1]).length) if np.argmin(dd) > 0 else 0.0
    L = cv.length
    ko = C.Frag()
    holes = []
    for k in range(-12, 13):
        s = s_front + node_phase + k * node_every
        if s < 12.0 or s > L - 12.0:
            continue
        p = cv.at_s(s)
        t = cv.tangent_s(s)
        a = math.degrees(math.atan2(t[1], t[0]))
        e = K.G.ellipse_d(p[0], p[1], node[0], node[1], a)
        if avoid is not None and K.R(e).buffer(MEDIUM / 2 + K.GAP_MARK).intersects(K.R(avoid)) \
                and not K.R(avoid).buffer(-MEDIUM).contains(K.R(e)):
            continue
        ko += C.stroke(e, MEDIUM, role="node")
        holes.append(K.R(e))
    stalk = C.stroke(mid, MEDIUM, role="stalk")
    if holes:
        stalk = K.clip_out(stalk, K.U(*holes), eps=0.0, trap=0.0)
    zone = reg.buffer(-(MEDIUM / 2 + 3.0 + MEDIUM / 2))
    if skip is not None:
        zone = zone.difference(K.R(skip).buffer(6.0))
    stalk = _drop_short_runs(K.clip_in(stalk, zone), cover, min_run, holes)
    ko += stalk
    ko = K.clip_in(ko, zone)
    fill = K.fill(C.knockout(K.D(reg), ko), color)
    return K.Part(reg, fill, K.outline(reg), {"mid": mid})
