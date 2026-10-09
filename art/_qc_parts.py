"""art/_qc_parts.py — Q♣ · The Wild-Rice Queen: the head and collar parts the shared kit does not have.

Everything is built the courtkit way (compass geometry, Parts with an opaque
``shape``, legal widths only, nothing scaled, nothing paper painted):

    bertha(...)          §H.8 'neckline lining: Gill Red' — the gown's lining
                         turned out as a broad band round the neckline, with
                         paper knockouts
    rice_crown(...)      §H.8 rice-spike coronet as a goldsmith's crown of rice:
                         a solid moulded gold circlet with a set jewel and
                         three wild-rice sprays (3 : 1 spikelets on branching
                         pedicels, HAIRLINE awns) rising from behind its rim
    hair_lock(...)       a lock of gold hair between two arc splines
    neck_chest(...)      the neck and chest between two spines
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Polygon

from deck import courtkit as K
from inkkit import geom as G
from deck.motifs import core as C
from deck.motifs import forms as FM

P, R, U = K.P, K.R, K.U
FINE, MEDIUM, RULE, CONTOUR, HAIR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR, K.HAIR_W
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD


def ring_mid(d):
    """Re-seat every closed subpath of ``d`` so it starts MID-SIDE, not at a
    sharp tip. A vesica starts at its tip; once ``clip_out`` turns it into a
    polyline the ring's seam is an open end: the render (and heal's skia
    outline) caps it round while QA 12 closes it with a miter spike up to
    10 × w/2 long. Seated mid-side, the seam is smooth, both tips are true
    miter joins, and render, heal and QA agree. → d (closed polylines)."""
    out = ""
    for pts, closed in G.as_polys(d, K.FLAT_TOL):
        pts = np.asarray(pts, float)
        shut = len(pts) > 3 and np.allclose(pts[0], pts[-1])
        if closed or shut:
            ring = pts[:-1] if shut else pts
            k = int(np.argmax(np.hypot(*(ring - ring[0]).T)))
            ring = np.roll(ring, -(k // 2), axis=0)
            out += C.polyline_d(ring, closed=True)
        else:
            out += C.polyline_d(pts)
    return out


def reseat(f, roles=("leaf", "spikelet")):
    """``ring_mid`` on every stroke mark of ``f`` whose role is in ``roles``."""
    from dataclasses import replace as _rp
    return C.Frag([_rp(m, d=ring_mid(m.d)) if (m.kind == "stroke" and m.role in roles and m.d) else m
                   for m in f.marks], f.meta)


def _u(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def _pts(d, step=0.3):
    return np.asarray(C.sample_d(d, step)[0][0], float)


def _biggest(g):
    ps = K._polys_of(g.buffer(0))
    return max(ps, key=lambda q: q.area) if ps else Polygon()


# =============================================================================
# the gown
# =============================================================================


def bertha(shape, top, *, cx=375.0, depth=26.0, color=RED, pearl=None, avoid=None, avoid_gap=4.0):
    """§H.8 the neckline lining turned out: the band of the gown within
    ``depth`` px of its neckline + shoulder line (both halves), with a row
    of graduated paper pearls (§G.29, ``pearl`` = kw for ``pearls``)
    knocked out along its middle, none within ``avoid_gap`` of ``avoid``
    (the brooch). → Part (meta 'mid' = the band's centre line, right
    shoulder → left shoulder)."""
    full = np.vstack([np.column_stack([2 * cx - top[::-1, 0], top[::-1, 1]]), top[1:]])
    band = shape.intersection(LineString(full).buffer(depth, cap_style=2, quad_segs=16))
    band = _biggest(band)
    mid = np.asarray(G.Curve(full).offset(depth / 2, spacing=0.5))
    fill_d = K.D(band)
    if pearl is not None:
        pl = pearls(mid, **pearl)
        if avoid is not None:
            # a pearl half under the brooch reads as a stray 'C': keep it whole and clear, or drop it
            zone = R(avoid).buffer(avoid_gap)
            pl = C.Frag([m for m in pl.marks if not R(G.to_shape(m.d, tol=0.05)).intersects(zone)], pl.meta)
        fill_d = C.knockout(fill_d, pl)
    return K.Part(band, K.fill(fill_d, color), K.outline(band), {"line": full, "mid": mid})


# =============================================================================
# the laced bodice front
# =============================================================================


# =============================================================================
# sleeves
# =============================================================================


def pearls(line_pts, *, d_end=6.3, d_mid=10.5, gap=5.0, margin=10.0):
    """§G.29 pearl beading along a polyline (from one end to the other):
    circles graduated from ``d_end`` at the ends to ``d_mid`` at the middle,
    ``gap`` px of red between neighbours. → Frag of FILL discs (to knock out)."""
    cv = G.Curve(np.asarray(line_pts, float))
    L = cv.length
    f = C.Frag()

    def dia(s):
        return d_mid + (d_end - d_mid) * abs(s / L - 0.5) * 2

    # laid out from a gap at the middle and mirrored, so the run is centred exactly
    half = [L / 2 + (dia(L / 2) + gap) / 2]
    while True:
        s, d = half[-1], dia(half[-1])
        nxt = s + d / 2 + gap + dia(s + d) / 2
        if nxt + dia(nxt) / 2 > L - margin:
            break
        half.append(nxt)
    items = sorted([(L - s, dia(L - s)) for s in half] + [(s, dia(s)) for s in half])
    # where the line turns sharply (the neck point) two pearls can crowd into
    # one blob: working out from the middle, a pearl less than ``gap`` from
    # one already kept is dropped (symmetric for a symmetric line)
    placed = [(cv.at_s(s), d) for s, d in items]
    order = sorted(range(len(placed)), key=lambda i: abs(items[i][0] - L / 2))
    keep = []
    for i in order:
        p, d = placed[i]
        if all(np.hypot(*(p - q)) >= (d + e) / 2 + gap - 0.5 for q, e in (placed[j] for j in keep)):
            keep.append(i)
    for i in sorted(keep):
        p, d = placed[i]
        f += C.fill(C.circle_d(p[0], p[1], d / 2))
    return f


# =============================================================================
# the rice crown
# =============================================================================
def _circlet_d(cx, top, h, hw_top, hw_bot, bow):
    """A flared circlet: top arc (cx ± hw_top at top − bow, through (cx, top)),
    straight ends, bottom arc (cx ± hw_bot at top + h − bow, through
    (cx, top + h)). → d."""
    y0, y1 = top - bow, top + h - bow
    return K.Path((cx - hw_top, y0)).arc3((cx, top), (cx + hw_top, y0)).line((cx + hw_bot, y1)).arc3(
        (cx, top + h), (cx - hw_bot, y1)).close().d


def _circlet_arc(cx, top, hw, bow, dy, x0, x1, n=120):
    """The circlet's top arc (through (cx ± hw, top − bow) and (cx, top))
    shifted ``dy`` down, sampled from x0 to x1. → points."""
    xs = np.linspace(x0, x1, n)
    return np.column_stack([xs, [_arc_y(cx, top, hw, bow, x) + dy for x in xs]])


def rice_crown(fc, *, cx=386.5, top=142.0, h=26.0, bow=4.0, hw=(58.0, 54.0), rim=8.5, base=8.0,
               jewel=(9.5, 144.5, 6.3), sprays=(), far=0.85, sink=5.0):
    """§H.8 the rice-spike coronet as a goldsmith's crown of rice — a METAL
    crown, never a feather headband (director's note, §J):

    * the CIRCLET — a solid gold band ``h`` tall at the front, dipping
      ``bow``, flaring from ``hw[1]`` at its foot to ``hw[0]`` at its rim and
      as wide as the hair it sits on (a crown worn on the head, not a band
      across the brow); a MEDIUM line ``rim`` px under its top edge (the rim
      moulding) and one ``base`` px over its foot (the base moulding), each
      ≥ 4.2 px of gold clear of the edge strokes;
    * a set JEWEL (``jewel`` = (r, centre y, red core Ø)) on the face axis,
      standing proud of the rim, the mouldings stopping on it;
    * the SPRAYS — wrought wild-rice panicles rising from behind the rim
      (their wire rods start ``sink`` px under it, so the rim stays one
      unbroken CONTOUR): ``sprays`` = (dx from the face axis, tilt°, rod
      length, terminal (L, W, awn), side spikelets ((s up the rod, side ±1,
      pedicel, pedicel° off the rod, L, W, spikelet° off the rod, awn), …)).
      Each is a MEDIUM rod ending in a terminal spikelet, with small 3 : 1
      gold spikelets (MEDIUM, sharp miter tips) on MEDIUM pedicels branching
      from it below the terminal (so no two spikelets run side by side) and
      a HAIRLINE awn off every tip. Far-side dx are compressed by ``far``.
      Paint the sprays back to front: the side sprays first.

    → (band Part: circlet + jewel, in the silhouette; sprays Part: add
       BEFORE the band, outside the silhouette)."""
    a = fc.anchors
    ax = float(a["axis"])
    turn = a.get("turn", 0)
    hw_t, hw_b = hw
    band_d = _circlet_d(cx, top, h, hw_t, hw_b, bow)
    band = R(band_d)

    # ---- sprays ------------------------------------------------------------------
    els, ves_ds, wires, awns, tips = [], [], [], C.Frag(), []

    def spikelet(q, v, L, W, aw):
        ves = C.vesica_d(q - v * 1.0, q + v * L, W)
        els.append(R(ves))
        ves_ds.append(ves)
        tip = q + v * L
        if aw:
            awns.marks.extend(C.stroke(C.polyline_d([tip, tip + v * aw]), HAIR, role="awn").marks)
        tips.append(tip + v * aw)

    for (dx, tilt, rod, term, sides) in sprays:
        if turn and dx * turn > 0:
            dx *= far
        x = ax + dx
        u = _u(-90.0 + tilt)
        b = P(x, _arc_y(cx, top, hw_t, bow, x))
        r_top = b + u * rod
        spikelet(r_top, u, *term)
        wires.append((b - u * sink, r_top + u * 1.5))
        for (s_, sd, ped, ped_deg, L, W, deg, aw) in sides:
            p0 = b + u * s_
            q = p0 + _u(-90.0 + tilt + sd * ped_deg) * ped
            v = _u(-90.0 + tilt + sd * deg)
            spikelet(q, v, L, W, aw)
            wires.append((p0, q + v * 1.5))
    stone = U(*els) if els else Polygon()
    wire_l = C.Frag()
    for p_, q_ in wires:
        wire_l += K.seg(p_, q_, MEDIUM, role="pedicel")
    wire_l = K.clip_out(wire_l, stone, eps=-0.5, trap=0.0)
    sp_lines = C.Frag()
    for vd in ves_ds:
        sp_lines += C.stroke(ring_mid(vd), MEDIUM, style="point", role="spikelet")
    spr = K.Part(stone, K.fill(stone, GOLD), sp_lines + wire_l + awns, {"tips": tips})

    # ---- circlet, mouldings, jewel ----------------------------------------------------
    lines = K.outline(band_d)
    for dy in (rim, h - base):
        # each moulding runs parallel to the rim from one flared end to the other
        x0 = cx - (hw_t + (hw_b - hw_t) * dy / h)
        pts = _circlet_arc(cx, top, hw_t, bow, dy, x0 - 2.0, 2 * cx - x0 + 2.0)
        lines += K.clip_in(K.line(C.polyline_d(pts), MEDIUM, role="moulding"), band)
    whole, fills, meta = band, K.fill(band, GOLD), {"band": band}
    if jewel:
        jr, jy, jcore = (tuple(jewel) + (8.4,))[:3]
        jc = P(ax, jy)
        jw = cabochon(jc, jr, core=jcore)
        lines = K.clip_out(lines, jw.shape, eps=-0.5, trap=0.0) + jw.lines
        whole = U(band, jw.shape)
        fills = K.fill(whole, GOLD) + K.dot(jc, jcore, RED)
        meta["jewel"] = jc
    return K.Part(whole, fills, lines, meta), spr


def cabochon(c, r=9.0, core=8.4, color=RED):
    """A small set stone: a gold disc (MEDIUM outline) with a Gill Red core
    cut into the gold (the layer trap, §2.1). → Part."""
    c = P(c)
    disc = R(K.circle(c, r))
    return K.Part(disc, K.fill(disc, GOLD) + K.dot(c, core, color), K.outline(K.circle(c, r)), {})


def _arc_y(cx, y, hw, bow, x):
    """The crown band's top edge (an arc through (cx - hw, y - bow), (cx, y),
    (cx + hw, y - bow)) at x."""
    c, r = K.circ3(P(cx - hw, y - bow), P(cx, y), P(cx + hw, y - bow))
    return c[1] + math.sqrt(max(r * r - (x - c[0]) ** 2, 0.0))


# =============================================================================
# the wild-rice sceptre
# =============================================================================


# =============================================================================
# locks: hair and plumes (§G.24)
# =============================================================================
def _left_is_out(po, pi_):
    """True when the outer edge lies to the screen-left of the inner one
    (travelling root → tip)."""
    k = len(po) // 2
    t = po[min(k + 1, len(po) - 1)] - po[max(k - 1, 0)]
    nl = np.array([t[1], -t[0]])
    j = int(np.argmin(np.hypot(*(pi_ - po[k]).T)))
    return float(np.dot(po[k] - pi_[j], nl)) > 0


def hair_lock(fc, outer, inner, *, n=4, stagger=8.0, face_clip=True, hairline=None, h_outer=None, h_inner=None,
              edge=CONTOUR, color=GOLD, curl_r=4.2, curl_deg=80.0, starts=None, ends=None, tip_sag=0.5,
              guide="outer", first=None):
    """A lock (hair, or a plume when ``color`` is None) between the
    ``outer`` and ``inner`` arc splines (root → tip), minus ``hairline``
    (a region: the skin the lock must leave bare). The tip is closed by an
    arc of sagitta ``tip_sag`` × the tip gap.

    Current lines (§G.24) are offsets of the ``guide`` edge, line k at
    ``first`` + 7k px inside it; ``starts`` (one y per line, or None) lets
    inner lines begin lower down; every line rolls into a Ø6.3 terminal
    (``ends``: extra shortening per line, px). → Part."""
    d_o, po, _ = FM.arc_spline(outer, h_outer)
    d_i, pi_, _ = FM.arc_spline(inner, h_inner)
    po, pi_ = np.asarray(po, float), np.asarray(pi_, float)
    gap = float(np.hypot(*(po[-1] - pi_[-1])))
    if gap < 1.0:
        ring = np.vstack([po, pi_[::-1][1:]])
    else:
        sg = 1 if _left_is_out(po, pi_) else -1
        cap = _pts(K.arc_sag(po[-1], pi_[-1], sg * gap * tip_sag))
        ring = np.vstack([po, cap[1:-1], pi_[::-1]])
    reg = _biggest(Polygon(ring).buffer(0))
    if face_clip and hairline is not None:
        reg = _biggest(reg.difference(R(hairline)))
    reg = reg.buffer(0.6, quad_segs=8).buffer(-0.6, quad_segs=8)
    out_left = _left_is_out(po, pi_)
    if guide == "outer":
        g0, side = po, (+1 if not out_left else -1)
    else:
        g0, side = pi_, (-1 if not out_left else +1)
    first0 = (edge / 2 + K.GAP + FINE / 2 + 0.05) if first is None else first
    starts = starts or [None] * n
    ends = ends or [k * stagger for k in range(n)]
    f = C.Frag()
    placed = Polygon()
    for k in range(n):
        g = g0
        if starts[k] is not None:
            i0 = int(np.argmax(g0[:, 1] >= starts[k]))
            g = g0[i0:]
        if ends[k]:
            Lc = np.cumsum(np.r_[0, np.hypot(*np.diff(g, axis=0).T)])
            g = g[Lc <= Lc[-1] - ends[k]]
        if len(g) < 3:
            continue
        ln = K.current_lines(g, 1, reg, side=side, first=first0 + k * K.PITCH, edge=MEDIUM, stagger=0.0,
                             curl_r=curl_r, curl_deg=curl_deg, placed=placed)
        for q in ln.meta.get("lines", []):
            placed = placed.union(LineString(q).buffer(FINE / 2))
        for m in ln.marks:
            if m.role == "terminal":
                placed = placed.union(R(G.from_skia(m.skia())))
        f += ln
    return K.Part(reg, K.fill(reg, color) if color else C.Frag(), K.outline(reg) + f, {"outer": po, "inner": pi_})


def neck_chest(left, right, bottom=345.0):
    """The paper neck and upper chest: two arc-spline sides (top → down) closed
    below ``bottom`` (hidden by the gown). → Part (paper, MEDIUM outline)."""
    _, pl, _ = FM.arc_spline(left)
    _, pr, _ = FM.arc_spline(right)
    pl, pr = np.asarray(pl), np.asarray(pr)
    ring = np.vstack([pl, [[pl[-1][0], bottom], [pr[-1][0], bottom]], pr[::-1]])
    reg = Polygon(ring).buffer(0)
    return K.Part(reg, C.Frag(), K.outline(reg), {})


