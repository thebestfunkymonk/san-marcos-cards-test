"""art/_jd_parts.py — J♦ · The Herald of the Road: the herald's own parts (brief §H.12).

Everything is built from deck.courtkit primitives at final size (card px,
top half, y down): compass arcs and G1 arc splines, legal strokes only,
knockouts and hiding as geometry (nothing paper-coloured is painted).

* ``trumpet``      the long straight herald's trumpet (gold): a modest
                   trumpet flare with a dark mouth, a split line, a bead knop
                   under the bell, a ball boss, ferrules, a cupped mouthpiece.
* ``banner`` / ``rod``  the square jade banner (plain border, FINE seam,
                   §G.14 drip fringe) on its gold rod with ball finials.
* ``feather``      a scissor-tailed flycatcher tail feather (paper vane, one
                   current line, red tip behind a chevron).
* ``flat_cap``     the flat cap: band + crown lens (two parts); ``ear``.
* ``rowel*``       spur rowels as ONE gold solid with an Aquifer contour, and
                   the tabard's half-drop grid of them (kept whole or dropped).
* ``ford_chain`` / ``tabard``  the red tabard with a §G.23 stepping-stone
                   chain KNOCKED OUT round its edges (the Q♦ cape's edging).
* ``running_scroll`` / ``gauntlet`` / ``tooled_belt``  gold cuffs and belt
                   carrying §G.31 tooled scroll (♦ cuffs and belts only): one
                   row of large eye volutes on a running stem of tangent arcs,
                   one vesica leaf per turn.
* ``lozenge_buckle``  the ♦ lozenge buckle / brooch: red stone cut into gold.
* ``hair_bob``     page-boy hair with §G.24 current lines.
* ``map_open``     the map held open between two rollers: triple wavy river
                   crossed by the dotted route.
* ``sleeve_part`` / ``ford_brocade``  jade sleeves with the K♦ ford-stone
                   brocade.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck import motifs as M
from deck.motifs import core as C
from deck.motifs import geometric as MG

P = K.P
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD
HAIR, FINE, MEDIUM, RULE, CONTOUR = 1.6, K.FINE, K.MEDIUM, K.RULE, K.CONTOUR


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def spl(points, h0=None, h1=None, headings=None, closed=False):
    return K.spline([P(p) for p in points], h_start=h0, h_end=h1, headings=headings, closed=closed)


def spl_region(points, headings=None):
    """A closed G1 arc-spline region through ``points``."""
    return K.R(spl(points, headings=headings, closed=True)).buffer(0)


def pts_of(d, step=0.4):
    return C.sample_d(d, step)[0][0]


def biggest(g):
    ps = K._polys_of(g)
    return max(ps, key=lambda q: q.area) if ps else Polygon()


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


# ---------------------------------------------------------------------------
# the herald's trumpet
# ---------------------------------------------------------------------------
class Trumpet:
    """Axis frame: s runs from the bell MOUTH centre ``mouth`` (s = 0) down
    the tube toward the mouthpiece; ``u`` points up the axis (toward the
    bell), ``n`` is its left normal."""

    def __init__(self, mouth, axis_deg=-63.0):
        self.B = P(mouth)
        self.u = unit(axis_deg)
        self.n = np.array([self.u[1], -self.u[0]])
        self.deg = axis_deg

    def at(self, s, v=0.0):
        return self.B - self.u * s + self.n * v

    def poly(self, prof):
        """Region from a profile [(s, half-width)] symmetric about the axis."""
        left = [self.at(s, hw) for s, hw in prof]
        right = [self.at(s, -hw) for s, hw in prof[::-1]]
        return Polygon(np.vstack([left, right])).buffer(0)

    def point_at_y(self, y):
        s = (y - self.B[1]) / (-self.u[1])
        return self.at(s), s


def trumpet(T: Trumpet, *, bell_len=56.0, mouth_hw=23.0, lip=5.5, tube_w=14.0, length=340.0,
            knop=(62.0, 9.0), knops=(), ferrules=(118.0, 250.0), ferrule=(6.0, 3.6), boss=(186.0, 12.0),
            mp=(10.0, 6.5, 8.0), flare=2.4, throat=INK, throat_merge=False, hatch_bell=True) -> K.Part:
    """The long straight herald's trumpet (§H.12, gold). ``bell_len`` flare
    from the mouth to the tube (half-width falling as (1 − t)^``flare``, so a
    higher ``flare`` keeps the bell a modest trumpet flare, not a cone);
    ``mouth_hw`` half-width of the mouth; ``lip`` the mouth ellipse's
    half-depth (the bell seen from the side, its throat showing); ``knop`` =
    (s, r) the bead where the bell meets the tube, ``knops`` more beads down
    the tube (the banner's rod lashes at one); ``ferrules`` bands (s)
    ``ferrule`` = (height, overhang); ``boss`` = (s, r) a ball boss on the
    tube; ``mp`` = (length, cup r, stem half-width) the mouthpiece at the
    tube's end (s = ``length``)."""
    tw = tube_w / 2
    prof = []
    for k in range(0, 41):
        t = k / 40
        s = t * bell_len
        prof.append((s, tw + (mouth_hw - tw) * (1 - t) ** flare))
    bell = T.poly(prof + [(bell_len + 2.0, tw)])
    # the mouth: an ellipse across the axis (half-axes mouth_hw along n, lip along u): the dark opening
    th = np.linspace(0, 2 * math.pi, 97)
    mouth = Polygon([T.at(lip * math.cos(a), mouth_hw * math.sin(a)) for a in th]).buffer(0)
    tube = T.poly([(bell_len, tw), (length, tw)])
    beads = [Point(*T.at(ks)).buffer(kr, quad_segs=24) for ks, kr in (knop, *knops)]
    knop_g = beads[0]
    bs, br = boss
    boss_g = Point(*T.at(bs)).buffer(br, quad_segs=24)
    fh, fo = ferrule
    fer = [T.poly([(s - fh / 2, tw + fo), (s + fh / 2, tw + fo)]) for s in ferrules]
    ml, mr, mhw = mp
    stem = T.poly([(length - 1.0, mhw - 1.5), (length + ml, mhw - 2.5)])
    cup = Point(*T.at(length + ml + mr * 0.6)).buffer(mr, quad_segs=24)
    shape = K.U(bell, mouth, tube, *beads, boss_g, stem, cup, *fer).buffer(0.4, quad_segs=6).buffer(-0.4,
                                                                                                    quad_segs=6)
    # the dark throat: ≥ 3 px of gold rim all round it, or (``throat_merge``, a small bell whose rim cannot
    # hold 3 px inside its contour) the whole mouth dark, the throat running under the rim line
    if throat_merge:
        throat_g = mouth
    else:
        t_hw, t_lip = mouth_hw - 6.5, max(lip - 4.6, 2.2)
        throat_g = Polygon([T.at(t_lip * math.cos(a) - 0.4, t_hw * math.sin(a)) for a in th]).buffer(0)
    gold = shape.difference(throat_g) if throat else shape
    fills = K.fill(gold, GOLD)
    if throat:
        fills += K.fill(throat_g, throat)
    lines = C.Frag()
    lines += K.outline(mouth, MEDIUM, role="rim")
    s_split = lip - 1.0 if throat_merge else lip + 1.0     # merged: the split springs from the dark mouth (a T)
    for g in [*beads, boss_g, *fer, cup]:
        lines += K.outline(g, MEDIUM, role="trumpet")
    if hatch_bell:
        if hatch_bell != "split":            # "split": the axis line alone (a small bell's hatch is only ticks)
            half = bell.difference(mouth.buffer(MEDIUM / 2 + 0.2)).intersection(
                K.halfplane(T.at(-10.0), T.at(bell_len + 10.0), side=-1))
            half = half.difference(knop_g.buffer(0.5))
            lines += K.hatch_in(half, angle=T.deg + 90.0 + 45.0)
        lines += K.clip_in(K.seg(T.at(s_split), T.at(bell_len - 1.0), FINE, role="split"),
                           bell.difference(mouth).difference(knop_g))
    return K.Part(shape, fills, lines, {"bell": bell, "mouth": mouth, "tube": tube, "knop": T.at(knop[0]),
                                        "boss": T.at(bs), "cup": T.at(length + ml)})


# ---------------------------------------------------------------------------
# the banner
# ---------------------------------------------------------------------------
def banner(x0, y0, x1, y1, *, seam=10.5, fringe=(10.5, 9.0, 20.0), fringe_w=FINE,
           fringe_color=INK, corner=2.0, avoid=None, fringe_x0=None) -> K.Part:
    """The square jade banner (§H.12): its field x0..x1 × y0..y1 (the top
    edge tucks under the rod), a plain border closed by a FINE seam ``seam``
    px in (≥ 8.4 inside the CONTOUR edge), and a §G.14 drip
    fringe (strokes with Ø6.3 terminals, lengths on a slow sine) hanging from
    the lower edge (meta 'fringe': add it separately, sil=False) — from
    ``fringe_x0`` when something (the trumpet) crosses the edge's left end,
    so the sine is whole over the drips that hang."""
    cloth = K.box(x0, y0, x1, y1)
    if corner:
        cloth = cloth.buffer(-corner, join_style=2).buffer(corner, join_style=1)
    inner = K.box(x0 + seam, y0 + seam, x1 - seam, y1 - seam)
    fills = K.fill(cloth, JADE)
    lines = K.outline(cloth)
    lines += C.stroke(K.D(inner), FINE, style="rule", role="seam")
    pitch, lmin, lmax = fringe
    fr = C.Frag()
    av = K.R(avoid).buffer(K.CONTOUR / 2 + 3.2) if avoid is not None else None
    xa, xb = max(x0 + 7.0, fringe_x0 if fringe_x0 is not None else -1e9), x1 - 7.0
    n = int((xb - xa) // pitch) + 1
    for k in range(n):
        # §G.14: lengths on a slow sine (one period across the run); where the drip would reach something
        # below (the tabard, the trumpet) it is shortened, never below 4 px, else dropped whole (atomic)
        xv = (xa + xb) / 2 + (k - (n - 1) / 2) * pitch
        t = (xv - xa) / max(xb - xa, 1e-9)
        L = lmin + (lmax - lmin) * (0.5 - 0.5 * math.cos(2 * math.pi * t))
        while L >= 4.0:
            dr = C.stroke(C.polyline_d([(xv, y1), (xv, y1 + L)]), fringe_w, color=fringe_color, role="drip",
                          terminals="end")
            if av is None or not av.intersects(dr.shape()):
                fr += K.atomic(dr, f"drip{k}")
                break
            L -= 0.5
    hull = K.box(x0 + 2.0, y1, x1 - 2.0, y1 + lmax + K.TD)
    return K.Part(cloth, fills, lines, {"inner": inner, "fringe": fr, "fringe_hull": hull,
                                        "centre": P((x0 + x1) / 2, (y0 + y1) / 2)})


def rod(p0, p1, *, h=8.0, finial=5.2) -> K.Part:
    """The banner's gold rod with a ball finial at each end."""
    p0, p1 = P(p0), P(p1)
    body = LineString([tuple(p0), tuple(p1)]).buffer(h / 2, cap_style=2)
    balls = [Point(*p0).buffer(finial, quad_segs=24), Point(*p1).buffer(finial, quad_segs=24)]
    shape = K.U(body, *balls)
    lines = C.Frag()
    for b in balls:
        lines += K.outline(b)
    return K.Part(shape, K.fill(shape, GOLD), K.outline(shape) + lines, {})


# ---------------------------------------------------------------------------
# the flycatcher feathers
# ---------------------------------------------------------------------------
def feather(guide_pts, *, w_root=5.0, w_max=16.0, grow=0.22, taper=0.82, w_tip=11.0, tip=28.0, h0=None,
            h1=None, point=10.0, n_lines=0, side=+1, curl=(60.0, 4.2), quill=0.0) -> K.Part:
    """A scissor-tailed flycatcher's outer tail feather (§H.12: paper,
    current line, red tip) along the G1 guide (root → tip): a slim quill
    root widening to ``w_max`` by ``grow`` of the length, easing to ``w_tip``
    after ``taper``, closing in a POINTED oblique tip (``point`` px); the last
    ``tip`` px Gill Red behind a MEDIUM chevron; the MEDIUM shaft (rachis)
    runs from the root to the chevron's apex (no free end)."""
    gd = spl(guide_pts, h0=h0, h1=h1)
    g = pts_of(gd, 0.3)
    cv = K.G.Curve(g)
    Ln = cv.length
    s = np.linspace(0, Ln, 400)
    pts = cv.at_s(s)
    tang = np.array([cv.tangent_s(x) for x in s])
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
    t = s / Ln
    hw = np.where(t < grow, w_root / 2 + (w_max - w_root) / 2 * np.sin(np.clip(t / grow, 0, 1) * np.pi / 2),
                  w_max / 2 + (w_tip - w_max) / 2 * np.clip((t - taper) / max(1 - taper, 1e-6), 0, 1))
    # pointed tip over the last ``point`` px: the upper (left) edge runs on, the lower edge sweeps in
    tp = s > Ln - point
    f = np.clip((s - (Ln - point)) / point, 0, 1)
    hl = np.where(tp, hw * (1 - f ** 1.6), hw)
    hr = np.where(tp, hw * (1 - f ** 0.7), hw)
    left = pts + nrm * hl[:, None]
    right = pts - nrm * hr[:, None]
    vane = Polygon(np.vstack([left, right[::-1]])).buffer(0.8, join_style=1).buffer(-0.8, join_style=1).buffer(0)
    s_t = Ln - tip
    c0 = cv.at_s(s_t)
    tt = cv.tangent_s(s_t)
    nn = np.array([tt[1], -tt[0]])
    apex = c0 - tt * 7.0
    wing_l, wing_r = c0 + nn * (w_max / 2 + 5) + tt * 1.0, c0 - nn * (w_max / 2 + 5) + tt * 1.0
    beyond = Polygon([tuple(apex), tuple(wing_l), tuple(wing_l + tt * 300), tuple(wing_r + tt * 300),
                      tuple(wing_r)]).buffer(0)
    red = vane.intersection(beyond)
    chev = LineString([tuple(wing_l), tuple(apex), tuple(wing_r)]).intersection(vane.buffer(-0.3))
    fills = K.fill(red, RED)
    if quill:
        qz = vane.intersection(Point(*cv.at_s(0.0)).buffer(quill))
        fills += K.fill(qz, GOLD)
    lines = K.outline(vane)
    if quill:
        qe = Point(*cv.at_s(0.0)).buffer(quill).boundary.intersection(vane.buffer(-0.3))
        for ln in K._lines_of(qe):
            lines += K.line(np.asarray(ln.coords), MEDIUM, role="quill")
    for ln in K._lines_of(chev):
        lines += K.line(np.asarray(ln.coords), MEDIUM, role="chevron")
    if n_lines:
        # a §G.24 current line down the vane's middle: it springs from a Ø6.3 terminal where the vane is
        # wide enough to hold it clear of the CONTOUR, and runs into the red tip's chevron (no free end there)
        need = 2 * (K.TD / 2 + K.GAP_MARK + K.CONTOUR / 2) + 0.6
        i0 = int(np.argmax(2 * hw >= need)) + 3
        s0 = s[i0]
        s_ap = s_t - 7.0 + 0.8
        cl = cv.sub(s0 / Ln, s_ap / Ln).pts
        lines += C.stroke(cl, FINE, role="current")
        lines += K.dot(cl[0], K.TD, role="terminal")
    else:
        s_ap = s_t - 7.0
        sh = cv.sub(0.0, s_ap / Ln).pts
        lines += K.clip_in(C.stroke(sh, MEDIUM, role="shaft"), vane.buffer(1.0))
    return K.Part(vane, fills, lines, {"guide": g, "red": red, "len": Ln, "cv": cv})


# ---------------------------------------------------------------------------
# rowels
# ---------------------------------------------------------------------------
def rowel_solid(c, r_out, *, points=8, core=None, waist=None, rot=-90.0):
    """An ``points``-point spur rowel as ONE solid silhouette: a core disc and
    kite points (widest at ``waist`` = (radius, width), sharp tip at r_out)."""
    c = P(c)
    core = r_out * 0.47 if core is None else core
    wr, ww = waist if waist is not None else (r_out * 0.52, r_out * 0.54)
    parts = [Point(*c).buffer(core, quad_segs=24)]
    for k in range(points):
        a = math.radians(rot + 360.0 * k / points)
        u = np.array([math.cos(a), math.sin(a)])
        v = np.array([-u[1], u[0]])
        pm = c + u * wr
        parts.append(Polygon([tuple(c + u * core * 0.3), tuple(pm + v * ww / 2), tuple(c + u * r_out),
                              tuple(pm - v * ww / 2)]))
    g = shapely.union_all(parts).buffer(0)
    return Polygon(g.exterior) if g.geom_type == "Polygon" else Polygon(max(g.geoms, key=lambda q: q.area).exterior)


def rowel(c, r_out, *, hole=None, rot=-90.0, w=FINE):
    """A gold spur rowel (solid, Aquifer contour; legal on red, §C.4). With
    ``hole`` a paper axle hole (a hole in the gold, ringed FINE)."""
    sil = rowel_solid(c, r_out, rot=rot)
    gold = sil
    f = C.Frag()
    if hole:
        hg = Point(*P(c)).buffer(hole / 2, quad_segs=24)
        gold = sil.difference(hg)
    f += K.fill(gold, GOLD, role="rowel") + K.outline(sil, w, role="rowel")
    if hole:
        f += C.stroke(C.circle_d(c[0], c[1], hole / 2), FINE, color=INK, role="rowel")
    return sil, f


def rowel_grid(region, *, pitch=(40.0, 36.0), r=9.0, origin=(382.0, 330.0), clear=4.3, hole=None,
               visible=None, rot=-90.0):
    """Gold rowels in a HALF-DROP grid (§H.12) inside ``region``: each kept
    whole (atomic) ≥ ``clear`` px + FINE inside it; with ``visible`` only the
    rowels that stay wholly visible (not under something in front) are kept.
    → (list of silhouettes, Frag, list of core discs)."""
    reg = K.R(region)
    px, py = pitch
    ox, oy = origin
    x0, y0, x1, y1 = reg.bounds
    inner = reg.buffer(-(clear + FINE / 2), quad_segs=12)
    vis = K.R(visible).buffer(-(clear + FINE / 2), quad_segs=12) if visible is not None else None
    sils, f, cores = [], C.Frag(), []
    for i in range(int(math.floor((x0 - ox) / px)) - 1, int(math.ceil((x1 - ox) / px)) + 2):
        off = py / 2 if i % 2 else 0.0                  # half-drop: alternate COLUMNS drop half a pitch
        for j in range(int(math.floor((y0 - oy - off) / py)) - 1, int(math.ceil((y1 - oy - off) / py)) + 2):
            x, y = ox + i * px, oy + off + j * py
            sil = rowel_solid((x, y), r, rot=rot)
            if not inner.contains(sil):
                continue
            if vis is not None and not vis.contains(sil):
                continue
            s_, fr = rowel((x, y), r, hole=hole, rot=rot)
            sils.append(s_)
            cores.append(s_.buffer(-3.6, quad_segs=8).buffer(3.6, quad_segs=8))   # where the gold is a solid (4c)
            f += fr
    return sils, f, cores


# ---------------------------------------------------------------------------
# the tabard
# ---------------------------------------------------------------------------
def ford_chain(reg, *, d_in=8.0, band=12.0, stone=11.0, pitch=20.0, bottom=511.0, keep=None, turn=22.0):
    """A §G.23 stepping-stone chain run round the inside of region ``reg``
    (the ♦ house edging, as on the Q♦ cape): two MEDIUM rails ``d_in`` and
    ``d_in + band`` px in from the edge and lozenge stones between them, tips
    on the rails — returned as INK marks for knocking out of the fill
    (paper, never paint). Nothing runs along the band cut (below
    ``bottom`` − 6). ``keep``: stones must lie inside it (else dropped whole)."""
    reg = K.R(reg)
    x0, y0, x1, y1 = reg.bounds
    if y1 > bottom - 1:
        # the region runs on below the band cut: extrude its cross-section there (not its full
        # width — on a T-shaped tabard that put a corner at the panel's edge and the rails turned
        # out along it, two paper arcs beside the forearm)
        bx0, _, bx1, _ = reg.intersection(K.box(-2000, bottom - 40, 4000, 4000)).bounds
        ext = reg.union(K.box(bx0, bottom - 40, bx1, bottom + 80))
    else:
        ext = reg
    cutoff = K.box(-10, -10, 2000, bottom + 30)
    f = C.Frag()
    for d in (d_in, d_in + band):
        ring = ext.buffer(-d, quad_segs=16).boundary.intersection(cutoff)
        for ln in K._lines_of(shapely.line_merge(ring) if ring.geom_type != "LineString" else ring):
            if ln.length > 6:
                f += C.stroke(np.asarray(ln.coords), MEDIUM, style="rule", color=INK, role="rail")
    mid = ext.buffer(-(d_in + band / 2), quad_segs=16).boundary.intersection(cutoff)
    kp = K.R(keep) if keep is not None else None
    for ln in K._lines_of(shapely.line_merge(mid) if mid.geom_type != "LineString" else mid):
        Lm = ln.length
        n = max(1, int(Lm // pitch))
        st = (Lm - (n - 1) * pitch) / 2 if n > 1 else Lm / 2
        for k in range(n):
            sp = st + k * pitch
            p = ln.interpolate(sp)
            q = ln.interpolate(min(sp + 1.0, Lm))
            o = ln.interpolate(max(sp - 1.0, 0.0))
            ang = math.degrees(math.atan2(q.y - o.y, q.x - o.x))
            # no stone on a corner: the rails turn there, the stone would jam against them
            qa, qb = ln.interpolate(max(sp - stone, 0.0)), ln.interpolate(max(sp - stone + 1.0, 0.0))
            ra, rb = ln.interpolate(min(sp + stone - 1.0, Lm)), ln.interpolate(min(sp + stone, Lm))
            a0 = math.degrees(math.atan2(qb.y - qa.y, qb.x - qa.x))
            a1 = math.degrees(math.atan2(rb.y - ra.y, rb.x - ra.x))
            if abs(((a1 - a0) + 180.0) % 360.0 - 180.0) > turn:
                continue
            ld = C.lozenge_d(p.x, p.y, stone, band, ang)
            if kp is not None and not kp.contains(K.R(ld)):
                continue
            f += C.fill(ld, color=INK, role="stone")
    return f


def tabard(reg, *, seams=(), border=10.0, rowels=None, trap=1.6, bottom=511.0, color=RED, cores=(),
           chain=None) -> K.Part:
    """A red tabard piece over region ``reg``: its edging either a plain
    border closed by a FINE seam ``border`` px inside every edge but the band
    cut, or (``chain`` = ford_chain kwargs) a §G.23 stepping-stone chain
    KNOCKED OUT to paper; MEDIUM ``seams`` (polylines); gold ``rowels``
    (silhouettes, Frag, cores) sitting on it — the red is CUT under each
    rowel's core disc and under ``cores`` (solids in front: 1.6 px trap; the
    rowel points are thinner than a CONTOUR, so no plate hides under another)."""
    reg = K.R(reg)
    x0, y0, x1, y1 = reg.bounds
    ext = reg.union(K.box(x0 + 1, bottom - 40, x1 - 1, bottom + 60)) if y1 > bottom else reg
    red = reg
    fills = C.Frag()
    lines = K.outline(reg)
    if chain is None and border:
        inner_ext = ext.buffer(-border, quad_segs=12).intersection(reg)
        lines += K.clip_in(C.stroke(K.D(inner_ext), FINE, role="seam"), K.box(0, 0, 2000, bottom + 20))
    for sd in seams:
        lines += K.clip_in(K.line(C.polyline_d(sd), MEDIUM, role="seam"), reg.buffer(-0.3))
    for cg in cores:
        red = red.difference(cg.buffer(-trap))
    if rowels is not None:
        sils, rf, rcores = rowels
        for cg in rcores:
            red = red.difference(cg.buffer(-trap))
    red_d = K.D(red)
    if chain is not None:
        red_d = C.knockout(red_d, ford_chain(reg, bottom=bottom, **chain))
    fills += C.fill(red_d, color=color, role="fill")
    if rowels is not None:
        fills += rf.select(lambda m: m.layer != "ink")
        lines += rf.select(lambda m: m.layer == "ink")
    return K.Part(reg, fills, lines, {})


# ---------------------------------------------------------------------------
# cuffs
# ---------------------------------------------------------------------------
def gauntlet(W, u, *, width=36.0, flare=48.0, depth=36.0, height=26.0, n=2, mirror=False, top_sag=-2.5,
             bottom_sag=3.0, sprig=None, bottom=511.0) -> K.Part:
    """A flared gold cuff from the wrist W (top edge across the arm) back down
    the arm (−u) ``depth`` px, ``width`` → ``flare`` wide, carrying §G.31
    tooled scroll (♦ cuffs only) across its middle: the deck's running
    two-row motif, or with ``sprig`` = running_scroll kwargs (x_first, yc in
    the cuff's frame: x across it, y down the arm from its middle) ONE unit
    of the belt's scroll — the stem in from one side, a large eye volute, a
    sessile leaf — its leaves kept only where they stand clear inside (and
    clear above the band cut ``bottom``)."""
    W, u = P(W), np.asarray(u, float) / np.hypot(*u)
    nrm = np.array([u[1], -u[0]])
    a0, a1 = W + nrm * width / 2, W - nrm * width / 2
    Bp = W - u * depth
    b0, b1 = Bp + nrm * flare / 2, Bp - nrm * flare / 2
    d = K.Path(a0).sag(a1, top_sag).line(b1).sag(b0, bottom_sag).close().d
    reg = K.R(d)
    lines = K.outline(reg)
    L = (width + flare) / 2 + 1.0
    ang = math.degrees(math.atan2(-nrm[1], -nrm[0]))
    C0 = W - u * depth * 0.5
    if sprig is not None:
        # the cuff in its own frame (x across, y down the arm), so leaves are tested before placing
        ex, ey = -nrm, -u
        seen = reg.intersection(K.box(0.0, 0.0, 2000.0, bottom - K.GAP_MARK))
        loc = shapely.transform(seen, lambda xy: np.column_stack([(xy - C0) @ ex, (xy - C0) @ ey]))
        if mirror:
            loc = shapely.transform(loc, lambda xy: xy * np.array([-1.0, 1.0]))
        kw = dict(sprig)
        kw.setdefault("lead_x", -L / 2 - 8.0)
        kw.setdefault("tail", L)
        sc = running_scroll(n=1, keep=loc.buffer(-(MEDIUM / 2 + K.GAP_MARK + FINE / 2 + 0.3)), **kw)
    else:
        sc = M.tooled_scroll(-L / 2, L / 2, 0.0, height=height, n=n)
    if mirror:
        sc = sc.mirror_x(0.0)
    sc = sc.rotate(ang).translate(C0[0], C0[1])
    lines += K.clip_in(sc, reg.buffer(-0.2))
    return K.Part(reg, K.fill(reg, GOLD), lines, {})


# ---------------------------------------------------------------------------
# the flat cap
# ---------------------------------------------------------------------------
def flat_cap(band_lo, band_hi, crown, *, color=RED, band_color=RED, tip_r=3.5):
    """The herald's flat cap as TWO parts, band then crown (add in that
    order): ``band_lo`` / ``band_hi`` the band's lower and upper edges as
    (p0, p1, sag) arcs across the brow — the upper edge is hidden under the
    crown; ``crown`` the flat crown seen nearly edge-on, (left tip, right
    tip, top sag, under sag) — a lens overhanging the band. → (band, crown)."""
    (l0, l1, ls), (h0, h1, hs) = band_lo, band_hi
    band_d = K.Path(l0).sag(l1, ls).line(h1).sag(h0, -hs).close().d
    band = K.R(band_d)
    ct0, ct1, top_s, under_s = crown
    crown_d = K.Path(ct0).sag(ct1, top_s).sag(ct0, under_s).close().d
    cr = K.R(crown_d).buffer(-tip_r, join_style=1).buffer(tip_r, join_style=1)
    return (K.Part(band, K.fill(band, band_color), K.outline(band), {}),
            K.Part(cr, K.fill(cr, color), K.outline(cr), {}))


def ear(c, *, r=9.0, a0=100.0, a1=260.0, inner=True) -> K.Part:
    """A paper ear on the near side of a 3/4 head (in front of the hair): a
    half-disc C of radius r about c from a0 to a1 (screen degrees), closed
    along its chord (tucked under the head outline), with a small inner C."""
    c = P(c)
    d = K.arc_c(c, r, a0, a1) + "Z"
    reg = K.R(d).buffer(0)
    lines = K.outline(reg)
    if inner:
        lines += K.line(K.arc_c(c + P(1.5, 0.0), r * 0.45, a0 + 25.0, a1 - 25.0), MEDIUM, role="ear")
    return K.Part(reg, C.Frag(), lines, {})


# ---------------------------------------------------------------------------
# hair
# ---------------------------------------------------------------------------
def hair_bob(outline_pts, guide_pts, *, n=3, side=+1, stagger=8.0, curl_deg=90.0, visible=None, color=GOLD,
             edge=CONTOUR, first=None, cut=None) -> K.Part:
    """A bob at the back of a 3/4 head: the closed spline region through
    ``outline_pts``; current lines (§G.24) offset from ``guide_pts`` (the
    outer edge, root → free end) toward ``side``, clipped to ``visible`` (the
    part not behind the face), rolling into Ø6.3 terminals."""
    reg = spl_region(outline_pts)
    if cut is not None:                      # tucked under something in front (a feather, a cap band)
        reg = biggest(reg.difference(K.R(cut).buffer(-1.2)))
    g = pts_of(spl(guide_pts), 0.3)
    zone = reg if visible is None else reg.intersection(K.R(visible))
    if cut is not None:
        zone = zone.difference(K.R(cut))
    lines = K.current_lines(g, n, zone, side=side, edge=edge, stagger=stagger, curl_deg=curl_deg, first=first)
    return K.Part(reg, K.fill(reg, color), lines + K.outline(reg), {})


# ---------------------------------------------------------------------------
# the map scroll
# ---------------------------------------------------------------------------
def map_open(x_l, x_r, y0, y1, *, roll_l=14.0, roll_r=12.0, over=6.0, over_l=None, cap_l=None,
             river=(3, 8.0, 2.2, 7.0), route_d=4.2, route_pitch=8.4, route_slope=0.22, crossing=False,
             roller=GOLD) -> K.Part:
    """The map scroll held open (§H.12, paper): a roll at each end (the left
    one, ``roll_l`` thick, is the one the fist grips — ``over_l`` px proud
    of the sheet, default ``over``, its ends rounded ``cap_l``, default a
    full half-round; the right one ``over``), and between
    them the sheet: a TRIPLE WAVY RIVER running down it (FINE Aquifer,
    ``river`` = (n, pitch, amplitude, λ/2π)) crossed by the DOTTED ROUTE
    (Ø4.2 dots) — El Camino Real at the ford.

    ``crossing`` False: the dots stop 3 px short of the river on either
    side. True: ONE route at a steady pitch runs right across the sheet —
    through the river, a dot between each two river lines — and each river
    line is broken where the route crosses it (interlace: the line ends
    ≥ 3 px from the dots), so the crossing reads as the road fording the
    water. → Part (meta 'roll_l', 'sheet')."""
    ol = over if over_l is None else over_l
    rl = K.R(K.rrect(x_l - roll_l / 2, y0 - ol, x_l + roll_l / 2, y1 + ol, roll_l / 2 if cap_l is None else cap_l))
    rr = K.R(K.rrect(x_r - roll_r / 2, y0 - over + 2.0, x_r + roll_r / 2, y1 + over - 2.0, roll_r / 2))
    sheet = K.box(x_l, y0, x_r, y1)
    shape = K.U(rl, rr, sheet)
    fills = K.fill(K.U(rl, rr), roller) if roller else C.Frag()
    lines = K.outline(shape)
    lines += K.clip_in(K.outline(rl), shape.buffer(-0.3))
    lines += K.clip_in(K.outline(rr), shape.buffer(-0.3))
    field = sheet.buffer(-(MEDIUM / 2 + 3.2)).difference(rl.buffer(MEDIUM / 2 + 3.2)).difference(
        rr.buffer(MEDIUM / 2 + 3.2))
    n, pitch, amp, lam = river
    xa, xb = x_l + roll_l / 2, x_r - roll_r / 2            # the open sheet between the rolls
    xm = (xa + xb) / 2
    cxr = xm + 2.0 if crossing else (x_l + x_r) / 2 + 4.0
    yr = (y0 + y1) / 2 + 2.0
    # crossing: the wave passes through a node where the route fords it, so the reach above and
    # the reach below are the two opposite halves of one S (not two unrelated arcs)
    ph = -(yr - (cxr - xm) * route_slope - y0) / lam if crossing else 0.0
    ys = np.linspace(y0 - 10, y1 + 10, 400)
    guides = []
    for k in range(n):
        xo = cxr + (k - (n - 1) / 2) * pitch
        xs = xo + amp * np.sin((ys - y0) / lam + ph) - (ys - (y0 + y1) / 2) * 0.18
        guides.append(np.column_stack([xs, ys]))
    dots = []
    if not crossing:
        riv = C.Frag()
        for g in guides:
            riv += K.clip_in(K.line(g, FINE, role="river"), field)
        lines += riv
        rv = riv.shape() if riv.marks else Polygon()
        for k in range(-8, 9):
            q = P((x_l + x_r) / 2 + k * route_pitch, yr - k * route_pitch * route_slope)
            dg = Point(*q).buffer(route_d / 2)
            if field.contains(dg) and rv.distance(dg) >= 3.05:
                lines += K.atomic(K.dot(q, route_d, role="route"), f"route{k}")
        return K.Part(shape, fills, lines, {"roll_l": rl, "sheet": sheet})
    # one straight route; where it crosses each river line
    def route_y(x):
        return yr - (x - xm) * route_slope
    road = LineString([(x_l - 20, route_y(x_l - 20)), (x_r + 20, route_y(x_r + 20))])
    cross = []
    for g in guides:
        hit = road.intersection(LineString(g))
        pts = [hit] if hit.geom_type == "Point" else list(getattr(hit, "geoms", []))
        if pts:
            cross.append(min(pts, key=lambda q: abs(q.x - cxr)).x)
    cross.sort()
    step = (cross[-1] - cross[0]) / max(len(cross) - 1, 1) if len(cross) > 1 else route_pitch
    # a dot midway between each two river lines, and on outward at the same pitch
    xs_d = [(a + b) / 2 for a, b in zip(cross[:-1], cross[1:])]
    xd = cross[0] - step / 2
    while xd > x_l - 50:
        xs_d.append(xd)
        xd -= step
    xd = cross[-1] + step / 2
    while xd < x_r + 50:
        xs_d.append(xd)
        xd += step
    for k, xd in enumerate(sorted(xs_d)):
        q = P(xd, route_y(xd))
        dg = Point(*q).buffer(route_d / 2)
        if field.contains(dg):
            dots.append(dg)
            lines += K.atomic(K.dot(q, route_d, role="route"), f"route{k}")
    # the river lines broken where the route fords them (≥ 3 px from every dot)
    keep_off = K.U(*dots).buffer(K.GAP_MARK + FINE / 2 + 1.0, quad_segs=12) if dots else Polygon()
    # the river's ends keep §I.12's 3 px from the sheet's outline (their round caps included)
    rfield = sheet.buffer(-(MEDIUM / 2 + K.GAP_MARK + FINE / 2 + 0.4))
    for g in guides:
        ln = K.clip_in(K.line(g, FINE, role="river"), rfield)
        if not keep_off.is_empty:
            ln = K.clip_out(ln, keep_off, eps=0.0)
        lines += ln
    return K.Part(shape, fills, lines, {"roll_l": rl, "sheet": sheet})


def running_scroll(x_first, n, yc, *, r0=9.0, q=8.4, flat=2.5, leaf=(14.0, 6.0), pet=3.0, lead_x=None,
                   tail=24.0, keep=None, w=FINE) -> C.Frag:
    """§G.31 tooled scroll as ONE row of large, regular volutes (a belt is too
    narrow for the two-row motif): a running stem of tangent arcs along a
    base line ``q`` px below the volutes' centre line ``yc`` — before each
    volute a CCW quarter (radius ``q``) rises to its left foot, a CW half
    circle (radius ``r0``; centres ``x_first`` + k·p) rolls over it, and at
    its right foot the stem FORKS: the eye half turn (r0/2, the deck's 'eye'
    volute) curls back to the centre into a Ø6.3 terminal, while a CCW
    quarter carries the stem back down to the base line (a clean λ fork,
    the two branches curving apart). p = 2·r0 + 2·q + ``flat``. One vesica
    leaf (``leaf`` = (length, width)) stands upright midway between each two
    volutes (and before the first): on a ``pet`` px petiole from the base
    line, or with ``pet`` < FINE sessile, its lower tip sunk in the stem (a
    petiole shorter than the leaf's pointed overshoot leaves a paper wedge). The stem starts at ``lead_x`` and runs ``tail`` px on after the
    last volute: both ends must lie under something in front (the buckle, a
    cuff). Leaves are atomic, and kept only inside ``keep``."""
    p = 2 * r0 + 2 * q + flat
    yb = yc + q
    x0 = x_first - r0 - q - flat - 4.0 if lead_x is None else lead_x
    t = C.Turtle(x0, yb, 0.0)
    f = C.Frag()
    mids = [x_first - r0 - q - flat / 2]
    for k in range(n):
        xk = x_first + k * p
        t.line_to(xk - r0 - q, yb)
        t.arc(q, -90.0)                                    # up to the left foot
        t.arc(r0, 180.0)                                   # over the volute (CW)
        e = C.Turtle(*t.pos, 90.0)
        e.arc(r0 / 2, 180.0)                               # the eye half turn back to the centre
        f += C.stroke(e.d(), w, role="volute")
        f += K.dot(e.pos, K.TD, role="terminal")
        t.arc(q, -90.0)                                    # down to the base line (CCW)
        mids.append(xk + r0 + q + flat / 2)
    t.fd(tail)
    f = C.stroke(t.d(), w, role="stem") + f
    Lf, Wf = leaf
    kp = K.R(keep) if keep is not None else None
    for j, xm in enumerate(mids):
        b = P(xm, yb)
        p0 = b + P(0.0, -pet)
        p1 = p0 + P(0.0, -Lf)
        lf = C.stroke(C.polyline_d([b, p0]), w, role="petiole") if pet > w else C.Frag()
        lf += C.stroke(C.vesica_d(p0, p1, Wf), w, style="point", role="leaf")
        if kp is not None and not kp.contains(lf.shape()):
            continue
        f += K.atomic(lf, f"leaf{j}")
    f.meta.update(pitch=p, base=yb)
    return f


def tooled_belt(x0, x1, y0, y1, clip, *, height=26.0, n=None, color=JADE, scroll=None) -> K.Part:
    """A belt (♦: §G.31 tooled scroll on cuffs and belts) from x0 to x1
    between y0 and y1, clipped to ``clip``: the running scroll in Aquifer
    FINE on the ``color`` leather — the deck's two-row motif, or with
    ``scroll`` = running_scroll kwargs the single row of large volutes."""
    reg = K.box(x0, y0, x1, y1).intersection(K.R(clip))
    lines = K.outline(reg)
    if scroll is not None:
        sc = running_scroll(yc=(y0 + y1) / 2 + scroll.pop("dy", 0.0), **scroll)
        lines += K.clip_in(sc, reg.buffer(-(MEDIUM / 2 + 0.2)))
    else:
        sc = M.tooled_scroll(x0, x1, (y0 + y1) / 2, height=height, n=n)
        lines += K.clip_in(sc, reg.buffer(-(MEDIUM / 2 + 0.2)))
    return K.Part(reg, K.fill(reg, color), lines, {})


def lozenge_buckle(c, *, L=26.0, W=34.0, inner=(12.0, 16.0), color=GOLD, stone=RED) -> K.Part:
    """The belt buckle as the ♦ house mark: a gold lozenge (``L`` tall × ``W``
    wide) framing a Gill Red ford stone (``inner``), the red CUT into the gold
    (the layer trap), MEDIUM Aquifer contours. → Part."""
    c = P(c)
    outer = K.R(C.lozenge_d(c[0], c[1], W, L, 0.0)).buffer(1.2, join_style=1).buffer(-1.2, join_style=1)
    st = K.R(C.lozenge_d(c[0], c[1], inner[1], inner[0], 0.0))
    fills = K.fill(outer.difference(st), color) + K.fill(st, stone)
    lines = K.outline(outer) + K.outline(st)
    return K.Part(outer, fills, lines, {})


def sleeve_part(reg, folds=(), *, color=JADE, brocade=None) -> K.Part:
    """A doublet sleeve (jade) over region ``reg`` with MEDIUM fold lines
    (G1 splines through each point list) running edge to edge — both ends
    under something in front or on the band cut, so no free ends — and an
    optional ♦ brocade (``brocade`` = ford_brocade kwargs: small outlined
    ford stones in a half-drop grid, as on the K♦ mantle)."""
    reg = K.R(reg)
    lines = K.outline(reg)
    fl = C.Frag()
    for fp in folds:
        fl += K.clip_in(K.line(spl(fp), MEDIUM, role="fold"), reg.buffer(-0.3))
    lines += fl
    if brocade is not None:
        avoid = fl.shape() if fl.marks else None
        lines += ford_brocade(reg, avoid=avoid, **brocade)
    return K.Part(reg, K.fill(reg, color), lines, {})


def ford_brocade(region, *, pitch=(26.0, 22.0), size=(12.0, 7.5), origin=(375.0, 300.0), avoid=None,
                 color=INK, bottom=511.0) -> C.Frag:
    """A half-drop grid of small outlined lozenges (the ♦ divider's stepping
    stones strewn as a brocade; FINE Aquifer on jade, §C.4), each atomic
    (kept whole or dropped), ≥ 4.3 px + FINE inside the region's CONTOUR
    edge and ≥ 3 px clear of ``avoid`` (fold lines)."""
    reg = K.R(region)
    px, py = pitch
    L, W = size
    inner = reg.buffer(-(L / 2 + FINE / 2 + K.CONTOUR / 2 + 3.2))
    av = K.R(avoid).buffer(FINE / 2 + 3.1) if avoid is not None else None
    x0, y0, x1, y1 = reg.bounds
    ox, oy = origin
    f = C.Frag()
    for j in range(int(math.floor((y0 - oy) / py)) - 1, int(math.ceil((y1 - oy) / py)) + 2):
        off = px / 2 if j % 2 else 0.0
        for i in range(int(math.floor((x0 - ox - off) / px)) - 1, int(math.ceil((x1 - ox - off) / px)) + 2):
            x, y = ox + off + i * px, oy + j * py
            if not inner.contains(Point(x, y)) or y + W / 2 + FINE / 2 + 3.4 > bottom:
                continue
            ld = C.lozenge_d(x, y, W, L, 90.0)
            if av is not None and av.intersects(K.R(ld)):
                continue
            f += K.atomic(C.stroke(ld, FINE, style="point", color=color, role="stone"), f"brc{i}_{j}")
    return f
