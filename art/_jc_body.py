"""art/_jc_body.py — J♣ · The River Squire: the body (jerkin, sleeves, arms,
collar, belt, placket), built from deck.courtkit / deck.motifs primitives at
final size in card px (top half). Every builder returns a courtkit Part.
"""
from __future__ import annotations

import math
import re

import numpy as np
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
        mp = pts_of(K.spline([e - K.unit(h) * 9.0, (e + q) / 2 + K.unit(h - 90) * 0.8, q]), 0.3)
        f += K.fill(_leaf_region(mp, leaflet[1] * 1.45), INK, role="leaflet")
    return f


def pecan_nut(c, heading_deg=-90.0, *, L=15.0, W=9.5):
    """A small gold pecan nut (a pointed ovoid): solid gold with an Aquifer
    FINE contour (§C.4: gold on red only as a contoured solid). → (Frag, region)."""
    c = P(c)
    u = K.unit(heading_deg)
    reg = K.R(K.vesica(c - u * L / 2, c + u * L / 2, W)).buffer(1.2, join_style=1).buffer(-1.2, join_style=1)
    return K.fill(reg, GOLD, role="nut") + K.outline(reg, FINE, role="nut"), reg








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
