"""art/_qc_parts.py — Q♣ · The Wild-Rice Queen: the parts the shared kit does not have.

Everything is built the courtkit way (compass geometry, Parts with an opaque
``shape``, legal widths only, nothing scaled, nothing paper painted):

    coronet(fc, ...)      §H.8 rice-spike coronet: a band round a 3/4 head with
                          upright gold spikelets on fine pedicels + HAIRLINE awns
    rice_sceptre(...)     §H.8/§G.5 the sceptre wrought as a flowering wild-rice
                          stalk: gold culm with node collars, drooping male florets
                          below, erect awned female spikelets at the tip
    plume(...)            one egret plume: a paper lock with current lines (§G.24)
    plume_fan(...)        the fan: plumes layered on a gold ferrule + handle
    lacing(...)           §H.8 bodice lacing: a gold reed ladder (§G.19)
    gown(...)             the jade gown (scoop neckline, sloped shoulders) with a
                          plain border + FINE seam, ribbon-leaf textile inside
    leaf_field(...)       §G.4 ribbon leaves streaming diagonally (the current)
    lining(...)           the Gill Red neckline lining
    puff(...)             a slashed puffed sleeve-cap (red, vesica slashes)
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from inkkit import geom as G
from deck.motifs import core as C
from deck.motifs import forms as FM
from deck.motifs import rice as MR

P, R, U = K.P, K.R, K.U
FINE, MEDIUM, RULE, CONTOUR, HAIR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR, K.HAIR_W
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD


def _u(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


# =============================================================================
# coronet
# =============================================================================
def coronet(fc, *, y=166.0, h=9.0, bow=5.0, spikes=((0.0, 0.0, 48.0, 16.0, 8.0, 18.0),), over=2.0, far=0.8,
            studs=(), ends=None, hair=None, clear=7.9):
    """The rice-spike coronet (§H.8): a gold band (``crown_band``) wrapping the
    head at height ``y`` and upright gold spikelets (3 : 1 vesicas) standing
    on MEDIUM pedicels on its top edge, each with a HAIRLINE awn. ``spikes``
    = (dx from the face axis, tilt° from upright, length, width, pedicel,
    awn); a spike on the far side of a 3/4 head has its dx compressed by
    ``far``. ``studs``: dx of Ø4.2 Aquifer studs on the band.
    → Part (meta: band, tips)."""
    a = fc.anchors
    yy = y + h / 2
    if ends is None:
        xl, xr = a["side_x"](yy, -1) - over, a["side_x"](yy, +1) + over
    else:
        xl, xr = ends
    cx, hw = (xl + xr) / 2, (xr - xl) / 2
    band, band_d = K.crown_band(cx, y, h, hw, bow)
    ax = float(a["axis"])
    turn = a.get("turn", 0)

    def top_y(x):
        t = (x - cx) / hw
        return y - bow * t * t                     # the band's top edge (ends ``bow`` higher)

    els, lines, fills, awns, tips = [], C.Frag(), C.Frag(), C.Frag(), []
    for (dx, tilt, L, W, pd, aw) in spikes:
        if turn and dx * turn > 0:
            dx *= far
        x = ax + dx
        u = _u(-90.0 + tilt)
        p0 = P(x, top_y(x) + 0.8)
        if hair is not None:
            # the stem rises from the band through the hair's edge: the spikelet starts
            # ``clear`` px beyond that CONTOUR edge (3 px + half CONTOUR + half MEDIUM)
            ray = LineString([tuple(p0), tuple(p0 + u * 80.0)]).intersection(hair)
            exit_ = max((np.hypot(*(np.asarray(g.coords)[-1] - p0)) for g in K._lines_of(ray)), default=0.0)
            pd = max(pd, exit_ + clear)
        p1 = p0 + u * pd
        p2 = p1 + u * L
        ves = C.vesica_d(p1, p2, W)
        els.append(R(ves))
        lines += C.stroke(ves, MEDIUM, style="point", role="spikelet")
        lines += K.seg(p0, p1 + u * 1.0, MEDIUM, role="pedicel")
        awns += C.stroke(C.polyline_d([p2, p2 + u * aw]), HAIR, role="awn")
        tips.append(p2 + u * aw)
    stone = U(*els)
    bl = K.outline(band_d)
    for dx in studs:
        x = ax + (dx * far if (turn and dx * turn > 0) else dx)
        bl += K.dot((x, top_y(x) + h / 2 + 0.3), 4.2)
    band_part = K.Part(band, K.fill(band, GOLD), bl, {})
    spikes = K.Part(stone, K.fill(stone, GOLD), lines + awns, {"tips": tips})
    return band_part, spikes


# =============================================================================
# the wild-rice sceptre
# =============================================================================
def rice_sceptre(x=545.0, *, tip_y=100.0, bottom=545.0, hw=7.0, culm_top=292.0, nodes=(338.0, 428.0),
                 node_hw=12.5, node_h=8.0, rachis_hw=3.6, t_len=34.0, t_w=11.0, t_awn=16.0,
                 female=((6.0, 45.0, 32.0, 10.6, 9.0, 17.0),) * 6, f_pitch=14.0,
                 male=((24.0, 18.0, 27.0, 9.0, 18.0),) * 6, m_pitch=14.0, gap=12.0):
    """§H.8 / §G.5 the sceptre wrought in gold as a flowering wild-rice
    stalk, botanically ordered along its own axis (x = ``x``):

    * the CULM (``hw`` half-wide) from below the band up to ``culm_top``,
      with raised node collars at ``nodes`` (a grass stalk, not a wand);
    * the RACHIS (``rachis_hw``) on up to the terminal spikelet;
    * ``female`` spikelets toward the tip, alternating sides, each
      (pedicel, pedicel°, length, width, axis° off vertical, awn): ERECT —
      the spikelet's axis stands a few degrees off the stalk — each with a
      HAIRLINE awn; the stalk ends in a terminal spikelet whose awn reaches
      ``tip_y``;
    * below them, after ``gap``, ``male`` florets, alternating, each
      (branch, branch° above horizontal, length, width, hang° off
      vertical): a MEDIUM branch spreading up and out, the floret (a 3 : 1
      vesica) HANGING from its end, pointing down and out — the pendulous
      male spikelets.

    → Part (meta: culm = the silhouette piece; head = the spikelets)."""
    t_base = tip_y + t_awn + t_len             # terminal spikelet base on the axis
    culm = K.box(x - hw, culm_top, x + hw, bottom)
    knop = R(K.circle(P(x, culm_top), hw + 2.5))
    collars = [R(K.rrect(x - node_hw, yy - node_h / 2, x + node_hw, yy + node_h / 2, 3.2)) for yy in nodes]
    els_f, els_m, lines = [], [], C.Frag()
    p1 = P(x, t_base)
    p2 = P(x, t_base - t_len)
    ves = C.vesica_d(p1, p2, t_w)
    els_f.append(R(ves))
    lines += C.stroke(ves, MEDIUM, style="point", role="spikelet")
    lines += C.stroke(C.polyline_d([p2, P(x, tip_y)]), HAIR, role="awn")
    side = -1
    y = t_base - 2.0
    f_bases = []
    for (ped, ped_deg, L, W, deg, awn) in female:
        y += f_pitch
        p0 = P(x + side * rachis_hw, y)
        q = p0 + _u(-90.0 + side * ped_deg) * ped
        ax_dir = _u(-90.0 + side * deg)
        tip = q + ax_dir * L
        ves = C.vesica_d(q, tip, W)
        els_f.append(R(ves))
        lines += C.stroke(ves, MEDIUM, style="point", role="spikelet")
        lines += K.seg(p0 - P(side * 1.2, 0), q + ax_dir * 1.2, MEDIUM, role="pedicel")
        lines += C.stroke(C.polyline_d([tip, tip + ax_dir * awn]), HAIR, role="awn")
        f_bases.append(q)
        side = -side
    y += gap
    m_pts = []
    for (br, br_deg, L, W, hang) in male:
        p0 = P(x + side * rachis_hw, y)
        q = p0 + _u(-br_deg if side > 0 else 180.0 + br_deg) * br
        hd = _u(90.0 - side * hang)
        tip = q + hd * L
        ves = C.vesica_d(q, tip, W)
        els_m.append(R(ves))
        lines += C.stroke(ves, MEDIUM, style="point", role="floret")
        lines += K.seg(p0 - P(side * 1.2, 0), q + hd * 1.2, MEDIUM, role="branch")
        m_pts.append(q)
        side = -side
        y += m_pitch
    rachis = K.box(x - rachis_hw, t_base - 1.0, x + rachis_hw, culm_top + 2.0)
    stone = U(*els_f, *els_m)
    body = U(culm, rachis, knop, *collars)
    fills = K.fill(body, GOLD) + K.fill(stone, GOLD)
    body_lines = K.clip_out(K.outline(U(culm, knop)), U(*collars), eps=-0.5, trap=0.0)
    body_lines += K.clip_out(K.outline(rachis), U(knop, *els_f), eps=-0.5, trap=0.0)
    for cd in collars:
        body_lines += K.outline(cd)
    shape = U(body, stone)
    return K.Part(shape, fills, body_lines + lines,
                  {"culm": U(culm, knop, *collars), "rachis": rachis, "head": stone, "female": f_bases,
                   "male": m_pts, "last_y": y})


def rice_finial_sceptre(x=545.0, *, bottom=545.0, hw=7.0, knop_y=250.0, knop_hw=13.0, knop_h=9.0, nodes=(330.0, 468.0),
                        node_hw=12.0, node_h=8.0, rachis_hw=4.5, rachis_top=150.0,
                        terminal=(36.0, 12.0, 18.0),
                        female=((182.0, 12.0, 60.0, 30.0, 10.0, 12.0, 15.0), (216.0, 14.0, 60.0, 30.0, 10.0, 20.0, 14.0)),
                        arm=(46.0, 14.0, 6.0), florets=((0.52, 25.0, 8.4, 3.0), (1.0, 27.0, 9.0, 7.0))):
    """§H.8 / §G.5 the sceptre WROUGHT in gold as a flowering wild-rice
    stalk: regalia, so its flowering head is set symmetrically about the
    staff, but botanically ordered along the stalk's own axis —

    * the CULM (``hw``) from below the band up to a reed-node KNOP at
      ``knop_y``, with raised node collars at ``nodes``;
    * below the knop's shoulder, pairs of DROOPING MALE florets:
      ``male`` = (rachis y, branch reach, branch rise, L, W, hang° off
      vertical): an arched MEDIUM branch out to each side and a 3 : 1 gold
      floret hanging from its end, pointing down (the pendulous male
      spikelets, below);
    * above, the RACHIS (``rachis_hw``) carries pairs of ERECT FEMALE
      spikelets: ``female`` = (rachis y, pedicel, pedicel°, L, W, axis° off
      upright, awn) with HAIRLINE awns, and ends in a terminal spikelet
      (L, W, awn) standing on ``rachis_top`` (the erect female spikelets,
      at the tip).

    → Part (meta: culm = the silhouette piece, head = spikelets + florets)."""
    culm = K.box(x - hw, knop_y, x + hw, bottom)
    knop = R(K.rrect(x - knop_hw, knop_y - knop_h / 2, x + knop_hw, knop_y + knop_h / 2, 4.0))
    collars = [R(K.rrect(x - node_hw, yy - node_h / 2, x + node_hw, yy + node_h / 2, 3.2)) for yy in nodes]
    rachis = K.box(x - rachis_hw, rachis_top - 1.0, x + rachis_hw, knop_y)
    els, lines = [], C.Frag()
    L, W, aw = terminal
    p1, p2 = P(x, rachis_top + 1.5), P(x, rachis_top + 1.5 - L)
    ves = C.vesica_d(p1, p2, W)
    els.append(R(ves))
    lines += C.stroke(ves, MEDIUM, style="point", role="spikelet")
    lines += C.stroke(C.polyline_d([p2, p2 + P(0, -aw)]), HAIR, role="awn")
    for (ry, ped, ped_deg, L, W, deg, aw) in female:
        for sd in (-1, 1):
            p0 = P(x + sd * rachis_hw, ry)
            q = p0 + _u(-90.0 + sd * ped_deg) * ped
            u = _u(-90.0 + sd * deg)
            tip = q + u * L
            ves = C.vesica_d(q, tip, W)
            els.append(R(ves))
            lines += C.stroke(ves, MEDIUM, style="point", role="spikelet")
            lines += K.seg(p0 - P(sd * 1.2, 0), q + u * 1.2, MEDIUM, role="pedicel")
            lines += C.stroke(C.polyline_d([tip, tip + u * aw]), HAIR, role="awn")
    # one arching arm each side from the knop, the male florets hanging from it (drops on a chandelier arm)
    reach, rise, sag = arm
    for sd in (-1, 1):
        p0 = P(x + sd * (knop_hw - 1.5), knop_y)
        q = P(x + sd * (knop_hw + reach), knop_y - rise)
        arm_d = K.arc_sag(p0, q, sag * sd)
        arm_pts = np.asarray(C.sample_d(arm_d, 0.25)[0][0])
        cv = G.Curve(arm_pts)
        lines += K.line(arm_d, MEDIUM, role="branch")
        for (t, L, W, hang) in florets:
            b = cv.at_s(cv.length * t)
            u = _u(90.0 - sd * hang)
            tip = b + u * (L + 1.5)
            ves = C.vesica_d(b + u * 1.5, tip, W)
            els.append(R(ves))
            lines += C.stroke(ves, MEDIUM, style="point", role="floret")
        lines += K.dot(q, 6.3, role="terminal") if False else C.Frag()
    stone = U(*els)
    body = U(culm, rachis, knop, *collars)
    fills = K.fill(body, GOLD) + K.fill(stone, GOLD)
    bl = K.clip_out(K.outline(culm), U(knop, *collars), eps=-0.5, trap=0.0)
    bl += K.clip_out(K.outline(rachis), U(knop, *els), eps=-0.5, trap=0.0)
    bl += K.outline(knop)
    for cd in collars:
        bl += K.outline(cd)
    return K.Part(U(body, stone), fills, bl + lines, {"culm": U(culm, knop, *collars), "head": stone})


# =============================================================================
# egret plumes
# =============================================================================
def plume(root, heading, length, *, w_max=24.0, bend=(10.0, -40.0), split=0.45, n=2, w_root=6.0, peak=0.42,
          tip_w=0.0, stagger=10.0, curl_deg=80.0, offsets=None):
    """One egret breeding plume (§H.8 'paper, current lines'): its spine is
    two tangent arcs from ``root`` (``heading``; turning ``bend`` degrees
    over the first ``split`` of the length and the rest — rising, then
    drooping outward), its width swells from ``w_root`` to ``w_max`` at
    ``peak`` and tapers to a point at the tip. ``n`` current lines (§G.24)
    run along it at ``offsets`` from the spine (default ±3.5: 7 px apart)
    and roll into Ø6.3 terminals toward the tip, staggered. Paper: no
    fill. → Part (meta 'mid' spine points)."""
    _, mid, _ = FM.arc_path(root[0], root[1], heading, [(length * split, bend[0]), (length * (1 - split), bend[1])])
    mid = np.asarray(mid, float)
    cv = G.Curve(mid)
    L = cv.length
    s = np.linspace(0, L, 300)
    pts = cv.at_s(s)
    nrm = cv.normal_s(s)
    t = s / L
    hw = np.where(t < peak,
                  w_root / 2 + (w_max - w_root) / 2 * np.sin(np.pi / 2 * t / peak),
                  tip_w / 2 + (w_max - tip_w) / 2 * np.cos(np.pi / 2 * (t - peak) / (1 - peak)) ** 0.8)
    left = pts + nrm * hw[:, None]
    right = pts - nrm * hw[:, None]
    reg = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    reg = max(K._polys_of(reg), key=lambda g: g.area).buffer(0.8, quad_segs=8).buffer(-0.8, quad_segs=8)
    offs = offsets if offsets is not None else [(k - (n - 1) / 2) * K.PITCH for k in range(n)]
    f = C.Frag()
    placed = Polygon()
    curl_side = -1 if bend[1] < 0 else +1          # roll the ends the way the plume droops
    for k, o in enumerate(sorted(offs, key=lambda v: -v * curl_side)):
        g = cv.offset(o, spacing=0.5) if o else cv.resample(0.5)
        g = np.asarray(g)
        Lg = np.cumsum(np.r_[0, np.hypot(*np.diff(g, axis=0).T)])
        g = g[Lg <= Lg[-1] - k * stagger]
        ln = K.current_lines(g, 1, reg, side=curl_side, first=0.0, edge=MEDIUM, stagger=0.0,
                             curl_r=4.2, curl_deg=curl_deg, placed=placed)
        for q in ln.meta.get("lines", []):
            placed = placed.union(LineString(q).buffer(FINE / 2))
        for m in ln.marks:
            if m.role == "terminal":
                placed = placed.union(R(G.from_skia(m.skia())))
        f += ln
    return K.Part(reg, C.Frag(), K.outline(reg) + f, {"mid": mid, "tip": mid[-1]})


def lacing(x=375.0, y0=340.0, y1=545.0, *, hw=(10.0, 6.0), rung=22.0, node_every=4, node_over=5.0, node_h=8.0,
           first=None, ref_y=511.0):
    """§H.8 bodice lacing, a gold reed ladder (§G.19): a gold strip whose
    MEDIUM edges are the ladder's rails, tapering from ``hw[0]`` at ``y0``
    to ``hw[1]`` at ``ref_y`` (it follows the V of the bodice), FINE rungs
    every ``rung`` px, and on every ``node_every``-th rung a raised node
    collar (the reed node) ``node_over`` px proud of the rails. → Part."""
    def hwy(y):
        return hw[0] + (hw[1] - hw[0]) * (y - y0) / (ref_y - y0)
    strip = Polygon([(x - hwy(y0), y0), (x + hwy(y0), y0), (x + hwy(y1), y1), (x - hwy(y1), y1)])
    ys = []
    yy = y0 + (rung if first is None else first)
    while yy < y1 - 4:
        ys.append(yy)
        yy += rung
    nodes = [R(K.rrect(x - hwy(y_) - node_over, y_ - node_h / 2, x + hwy(y_) + node_over, y_ + node_h / 2, 3.2))
             for i, y_ in enumerate(ys) if (i + 1) % node_every == 0]
    lines = C.Frag()
    for i, y_ in enumerate(ys):
        if (i + 1) % node_every == 0:
            continue
        w_ = hwy(y_)
        lines += C.stroke(f"M{x - w_:.2f} {y_:.2f}L{x + w_:.2f} {y_:.2f}", FINE, style="hatch", role="rung")
    body = U(strip, *nodes)
    ol = K.clip_out(K.outline(strip), U(*nodes), eps=-0.5, trap=0.0) if nodes else K.outline(strip)
    for nd in nodes:
        ol += K.outline(nd)
    return K.Part(body, K.fill(body, GOLD), ol + lines, {"rungs": ys})


# =============================================================================
# the gown
# =============================================================================
def gown_outline(*, cx=375.0, neck_y=312.0, neck_x=322.0, neck_top=296.0, neck_sag=-9.0, shoulder=(208.0, 334.0),
                 shoulder_sag=7.0, corner_r=30.0, bottom=560.0, hem_x=172.0):
    """The gown's outline, bilateral about ``cx``: a scoop neckline (an arc
    from the axis at ``neck_y`` up to the neck point (``neck_x``,
    ``neck_top``)), a sloping, rounded shoulder (an arc to ``shoulder``,
    corner rounded ``corner_r``) and the side falling to ``hem_x`` at the
    band. → (region, meta N / S0)."""
    N = P(cx, neck_y)
    S0 = P(neck_x, neck_top)
    Sh = P(*shoulder)
    Hm = P(hem_x, bottom)
    d_half = K.Path(N).sag(S0, neck_sag).sag(Sh, shoulder_sag).line(Hm).line((cx, bottom)).close().d
    half = R(d_half)
    shape = U(half, K.mirror(half, cx))
    rounded = shape.buffer(-corner_r, join_style=1).buffer(corner_r, join_style=1)
    keep = shape.intersection(K.box(neck_x - 24, 0, 2 * cx - neck_x + 24, neck_top + 40))
    shape = U(rounded, keep).buffer(0)
    return shape, {"N": N, "S0": S0}


def stomacher(gown_shape, N, S0, *, cx=375.0, neck_sag=-9.0, band=15.0, top_hw=34.0, bot_hw=18.0, top_y=None,
              bottom=560.0, edge_sag=-4.0):
    """The Gill Red lining (§H.8 'neckline lining'): a band ``band`` px deep
    under the neckline, and the laced V of the bodice opening below it (the
    red lining shows between the jade fronts): from ``top_hw`` half-wide at
    the neckline to ``bot_hw`` at the band, edges gently curved. → Part."""
    arc_l = C.sample_d(K.arc_sag(N, S0, neck_sag), 0.3)[0][0]
    pts = np.vstack([arc_l[::-1], np.column_stack([2 * cx - arc_l[1:, 0], arc_l[1:, 1]])])
    ln = LineString(pts)
    nb = gown_shape.intersection(ln.buffer(band, cap_style=2, quad_segs=16))
    nb = max(K._polys_of(nb.buffer(0)), key=lambda g: g.area)
    ty = N[1] + band * 0.5 if top_y is None else top_y
    tl, bl = P(cx - top_hw, ty), P(cx - bot_hw, bottom)
    vd = K.Path(tl).sag(bl, edge_sag).line(K.mirror_pt(bl, cx) if hasattr(K, "mirror_pt") else P(2 * cx - bl[0], bl[1]))
    vd = vd.sag(P(2 * cx - tl[0], tl[1]), edge_sag).close().d
    v = R(vd)
    reg = U(nb, v).intersection(gown_shape).buffer(0)
    return K.Part(reg, K.fill(reg, RED), K.outline(reg), {"neckband": nb, "v": v})


def leaf_field(region, *, heading=64.0, length=150.0, width=14.4, row=46.0, step=176.0, stagger=0.5,
               origin=(375.0, 330.0), bend=(13.0, -13.0), hatch=1, clip=True):
    """§H.8 ribbon leaves streaming diagonally with the current (§G.4): a
    lattice of S-curved, half-hatched vesicas, all heading ``heading``°
    (the current), rows ``row`` px apart across the stream, leaves
    ``step`` px apart along it, alternate rows shifted ``stagger``·step.
    Aquifer FINE on the jade; clipped to ``region``. → Frag."""
    reg = R(region)
    x0, y0, x1, y1 = reg.bounds
    u = _u(heading)
    v = np.array([-u[1], u[0]])
    o = P(origin)
    f = C.Frag()
    diag = math.hypot(x1 - x0, y1 - y0) + length
    kmax = int(diag / row) + 2
    jmax = int(diag / step) + 2
    for k in range(-kmax, kmax + 1):
        off = (k % 2) * stagger * step
        for j in range(-jmax, jmax + 1):
            base = o + v * (k * row) + u * (j * step + off)
            tip = base + u * length
            bb = shapely.box(min(base[0], tip[0]) - 20, min(base[1], tip[1]) - 20,
                             max(base[0], tip[0]) + 20, max(base[1], tip[1]) + 20)
            if not bb.intersects(reg):
                continue
            lf = MR.ribbon_leaf(base[0], base[1], heading, length, width, bend=bend, hatch=hatch)
            f += K.atomic(lf, f"leaf{k}_{j}") if not clip else lf
    return K.clip_in(f, reg) if clip else f


def lining(gown_shape, N, S0, *, width=17.0, cx=375.0, neck_sag=-10.0):
    """The Gill Red neckline lining (§H.8): the band between the neckline and
    its offset ``width`` px into the gown. → Part."""
    arc_l = C.sample_d(K.arc_sag(N, S0, neck_sag), 0.3)[0][0]          # axis → neck point (left half)
    pts = np.vstack([arc_l[::-1], np.column_stack([2 * cx - arc_l[1:, 0], arc_l[1:, 1]])])
    ln = LineString(pts)
    reg = gown_shape.intersection(ln.buffer(width, cap_style=2, quad_segs=16))
    reg = max(K._polys_of(reg.buffer(0)), key=lambda g: g.area)
    return K.Part(reg, K.fill(reg, RED), K.outline(reg), {"line": pts})


def puff(c, r=34.0, *, squash=0.86, rot=0.0, slashes=3, slash_len=0.62, slash_w=7.4, spread=34.0, color=RED):
    """A puffed sleeve-cap: a slightly squashed round ``r`` about ``c``,
    ``slashes`` vesica slashes radiating from its foot knocked out to paper
    (Tudor slashing). → Part."""
    c = P(c)
    circ = Point(0, 0).buffer(r, quad_segs=64)
    circ = shapely.affinity.scale(circ, 1.0, squash)
    circ = shapely.affinity.rotate(circ, rot, origin=(0, 0))
    reg = shapely.affinity.translate(circ, c[0], c[1])
    holes = C.Frag()
    for k in range(slashes):
        a = rot + 90.0 + (k - (slashes - 1) / 2) * spread
        u = _u(a - 180.0)          # from the foot up through the centre
        p0 = c - u * (r * 0.62)
        p1 = c + u * (r * (slash_len - 0.2))
        holes += C.stroke(C.vesica_d(p0, p1, slash_w), MEDIUM, style="point")
    fill_d = C.knockout(K.D(reg), holes.to_fill()) if slashes else K.D(reg)
    return K.Part(reg, K.fill(fill_d, color), K.outline(reg), {})


# =============================================================================
# locks: hair and plumes (§G.24)
# =============================================================================
def lock(outer, inner, *, n=4, color=GOLD, edge=CONTOUR, stagger=9.0, tip_sag=None, h_outer=None, h_inner=None,
         curl_r=4.2, curl_deg=80.0, lines=True):
    """A lock of hair (or a plume) between two arc splines drawn ROOT → TIP:
    ``outer`` (the edge the current lines follow, usually the silhouette:
    ``edge`` CONTOUR) and ``inner``; the tip is closed by a round cap (an arc
    of sagitta ``tip_sag``, default half the tip gap). ``n`` current lines
    (§G.24) are offsets of the outer edge, 7 px apart, rolling into Ø6.3
    terminals toward the tip, staggered. ``color`` None = paper (a plume).
    → Part (meta 'outer', 'inner' dense points)."""
    d_o, po, _ = FM.arc_spline(outer, h_outer)
    d_i, pi_, _ = FM.arc_spline(inner, h_inner)
    po, pi_ = np.asarray(po, float), np.asarray(pi_, float)
    a, b = po[-1], pi_[-1]
    gap = float(np.hypot(*(a - b)))
    if gap > 1.0:
        cap = np.asarray(C.sample_d(K.arc_sag(a, b, (tip_sag if tip_sag is not None else gap / 2) *
                                               (1 if _left_is_out(po, pi_) else -1)), 0.3)[0][0])
        ring = np.vstack([po, cap[1:-1], pi_[::-1]])
    else:
        ring = np.vstack([po, pi_[::-1][1:]])
    reg = Polygon(ring).buffer(0)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    reg = reg.buffer(0.6, quad_segs=8).buffer(-0.6, quad_segs=8)
    f = C.Frag()
    if lines:
        side = +1 if not _left_is_out(po, pi_) else -1
        f = K.current_lines(po, n, reg, side=side, edge=edge, stagger=stagger, curl_r=curl_r, curl_deg=curl_deg)
    fills = K.fill(reg, color) if color else C.Frag()
    return K.Part(reg, fills, K.outline(reg) + f, {"outer": po, "inner": pi_})


def _left_is_out(po, pi_):
    """True when the outer edge lies to the screen-left of the inner one
    (travelling root → tip)."""
    k = len(po) // 2
    t = po[min(k + 1, len(po) - 1)] - po[max(k - 1, 0)]
    nl = np.array([t[1], -t[0]])
    j = int(np.argmin(np.hypot(*(pi_ - po[k]).T)))
    return float(np.dot(po[k] - pi_[j], nl)) > 0


def neck_chest(left, right, bottom=345.0):
    """The paper neck and upper chest: two arc-spline sides (top → down) closed
    below ``bottom`` (hidden by the gown). → Part (paper, MEDIUM outline)."""
    _, pl, _ = FM.arc_spline(left)
    _, pr, _ = FM.arc_spline(right)
    pl, pr = np.asarray(pl), np.asarray(pr)
    ring = np.vstack([pl, [[pl[-1][0], bottom], [pr[-1][0], bottom]], pr[::-1]])
    reg = Polygon(ring).buffer(0)
    return K.Part(reg, C.Frag(), K.outline(reg), {})


def hair_lock(fc, outer, inner, *, n=4, stagger=8.0, face_clip=True, hairline=None, h_outer=None, h_inner=None,
              edge=CONTOUR, color=GOLD, curl_r=4.2, curl_deg=80.0, starts=None, ends=None):
    """A queen's side lock worn IN FRONT of the head: the region between the
    ``outer`` and ``inner`` arc splines (root at the crown → tip), minus the
    face below the ``hairline`` (a region: the skin the lock must leave
    bare) — so below the temple the lock's inner edge IS the cheek contour.

    Current lines (§G.24) are offsets of the outer edge, line k at
    8.4 + 7k px inside it; ``starts`` (one y per line, or None) lets the
    inner lines begin lower down — they emerge from behind the cheek where
    the fall widens — so every line runs to the tip and rolls into a Ø6.3
    terminal (``ends``: extra shortening per line, px). → Part."""
    d_o, po, _ = FM.arc_spline(outer, h_outer)
    d_i, pi_, _ = FM.arc_spline(inner, h_inner)
    po, pi_ = np.asarray(po, float), np.asarray(pi_, float)
    gap = float(np.hypot(*(po[-1] - pi_[-1])))
    if gap < 1.0:
        ring = np.vstack([po, pi_[::-1][1:]])
    else:                                  # a rounded tip: a semicircle-ish cap bulging past the ends
        sg = 1 if _left_is_out(po, pi_) else -1
        cap = np.asarray(C.sample_d(K.arc_sag(po[-1], pi_[-1], sg * gap * 0.5), 0.3)[0][0])
        ring = np.vstack([po, cap[1:-1], pi_[::-1]])
    reg = Polygon(ring).buffer(0)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    if face_clip and hairline is not None:
        reg = reg.difference(R(hairline))
        reg = max(K._polys_of(reg.buffer(0)), key=lambda g: g.area)
    reg = reg.buffer(0.6, quad_segs=8).buffer(-0.6, quad_segs=8)
    side = +1 if not _left_is_out(po, pi_) else -1
    first0 = edge / 2 + K.GAP + FINE / 2 + 0.05
    starts = starts or [None] * n
    ends = ends or [k * stagger for k in range(n)]
    f = C.Frag()
    placed = Polygon()
    for k in range(n):
        g = po
        if starts[k] is not None:
            i0 = int(np.argmax(po[:, 1] >= starts[k]))
            g = po[i0:]
        if ends[k]:
            L = np.cumsum(np.r_[0, np.hypot(*np.diff(g, axis=0).T)])
            g = g[L <= L[-1] - ends[k]]
        ln = K.current_lines(g, 1, reg, side=side, first=first0 + k * K.PITCH, edge=MEDIUM, stagger=0.0,
                             curl_r=curl_r, curl_deg=curl_deg, placed=placed)
        for q in ln.meta.get("lines", []):
            placed = placed.union(LineString(q).buffer(FINE / 2))
        for m in ln.marks:
            if m.role == "terminal":
                placed = placed.union(R(G.from_skia(m.skia())))
        f += ln
    return K.Part(reg, K.fill(reg, color) if color else C.Frag(), K.outline(reg) + f, {"outer": po, "inner": pi_})


def cloak(*, cx=375.0, top=(300.0, 318.0), shoulder=(196.0, 326.0), hem=(146.0, 560.0), corner_r=26.0, color=RED):
    """The queen's cloak, worn behind the gown and falling from the shoulders:
    bilateral about ``cx``; its top edge runs behind the hair from
    ``top`` (x, y) out to the rounded ``shoulder`` and the side falls to
    ``hem`` at the band. Only the strips outside the gown show. → Part."""
    tp, sh, hm = P(*top), P(*shoulder), P(*hem)
    d_half = K.Path(P(cx, top[1] - 6.0)).sag(tp, -2.0).sag(sh, 6.0).line(hm).line((cx, hem[1])).close().d
    half = R(d_half)
    shape = U(half, K.mirror(half, cx))
    shape = U(shape.buffer(-corner_r, join_style=1).buffer(corner_r, join_style=1),
              shape.intersection(K.box(tp[0] - 10, 0, 2 * cx - tp[0] + 10, 2000))).buffer(0)
    return K.Part(shape, K.fill(shape, color), K.outline(shape), {})


def laced_v(gown_shape, N, S0, *, cx=375.0, neck_sag=-9.0, band=15.0, top_y=318.0, top_hw=34.0, tip_y=488.0,
            edge_sag=-5.0, rail=8.5, bar=9.0, pitch=22.0, first=26.0, node_every=4, node_rise=3.0, min_window=9.0):
    """The laced bodice (§H.8): the Gill Red lining — a band ``band`` px deep
    under the neckline and the V opening of the bodice (from ``top_hw`` at
    ``top_y`` to a point at ``tip_y``) — laced with a GOLD REED LADDER
    (§G.19) whose rails run down both edges of the V (``rail`` wide) and
    whose rungs (``bar`` tall, every ``pitch``) cross the red; every
    ``node_every``-th rung is a reed node (it swells ``node_rise`` px at the
    centre). Gold on red only as solids with an Aquifer contour (§C.4):
    rails and rungs are ≥ 8.5 px wide, so ≥ 5 px of gold shows inside the
    MEDIUM contour. → (lining Part (red), ladder Part (gold))."""
    arc_l = C.sample_d(K.arc_sag(N, S0, neck_sag), 0.3)[0][0]
    pts = np.vstack([arc_l[::-1], np.column_stack([2 * cx - arc_l[1:, 0], arc_l[1:, 1]])])
    nb = gown_shape.intersection(LineString(pts).buffer(band, cap_style=2, quad_segs=16))
    nb = max(K._polys_of(nb.buffer(0)), key=lambda g: g.area)
    tl, tip, tr = P(cx - top_hw, top_y), P(cx, tip_y), P(cx + top_hw, top_y)
    vd = K.Path(tl).sag(tip, edge_sag).sag(tr, edge_sag).close().d
    v = R(vd).intersection(gown_shape)
    lining = U(nb, v).intersection(gown_shape).buffer(0)
    inner = v.buffer(-rail, join_style=2, mitre_limit=10.0)
    rails = v.difference(inner.buffer(0))
    rails = rails.intersection(K.box(0, top_y + 0.5, 2000, 2000))
    bars = []
    y = top_y + first
    k = 0
    while True:
        row = inner.intersection(K.box(0, y - bar / 2, 2000, y + bar / 2))
        if row.is_empty or row.bounds[2] - row.bounds[0] < 2 * min_window + 4:
            break
        k += 1
        if node_every and k % node_every == 0:
            x0_, _, x1_, _ = row.bounds
            nd = R(K.Path(P(x0_ - 1, y - bar / 2)).sag(P(x1_ + 1, y - bar / 2), node_rise)
                   .line(P(x1_ + 1, y + bar / 2)).sag(P(x0_ - 1, y + bar / 2), node_rise).close().d)
            row = row.union(nd.intersection(v))
        bars.append(row)
        y += pitch
    last = y - pitch
    # below the last rung the rails close up into the V's point (a solid gold tip)
    tipfill = v.intersection(K.box(0, last, 2000, 2000))
    ladder = U(rails, *bars, tipfill).buffer(0.01).buffer(-0.01)
    return (K.Part(lining, K.fill(lining, RED), K.outline(lining), {"v": v}),
            K.Part(ladder, K.fill(ladder, GOLD), K.outline(ladder), {"rungs": len(bars)}))
