"""art/_jh_parts.py — the J♥ Spring Minstrel's own parts, in the courtkit hand.

Everything is a courtkit Part (shape, fills, lines, meta) built from compass
geometry at final size; the Scene in art/JH.py stacks them back to front.

    beret          jade beret: a soft crown with three ripple rings round its
                   button (the spring seen from above), a jade band
    fluke_heart    the small red fluke-heart brooch (§H.6) on a gold bezel
    plume          one long curling plume of gold current lines (§G.24)
    hair_bob       the page's gold bob behind the ear, rolled under
    fiddle_neck    scroll (a true volute), pegbox with four pegs, nut and the
                   jade (ebony) fingerboard
    fiddle_body    upper bout, pointed corners, C-bouts, lower bout; purfling;
                   f-holes with their eyes; strings, bridge, tailpiece
    bow            red (pernambuco) stick, gold frog and head, the hair
    sash           the paper sash on the diagonal through the card centre,
                   with the festoon string-light catenary (gold bulbs)
    bead_chain     bubble-chain piping: gold beads with an Aquifer contour
    ripple_slashes ripple-arc slashes knocked out of a jade sleeve
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs import forms as FM
from deck.motifs import geometric as MG

P = K.P
MED, FINE, RULE, CON = K.MEDIUM, K.FINE, K.RULE, K.CONTOUR
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD


def spline_region(points, headings=None):
    """Closed G1 arc spline through ``points`` → (d, shapely region)."""
    pts = [P(p) for p in points]
    n = len(pts)
    hs = []
    for i in range(n):
        h = (headings or {}).get(i)
        if h is None:
            h = FM.circle_heading(pts[i - 1], pts[i], pts[(i + 1) % n])
        hs.append(h)
    d, _ = FM.biarc_chain(pts, hs, closed=True)
    return d, K.R(d)


def open_spline(points, headings=None):
    """Open G1 arc spline → (d, dense points)."""
    d, pts, _ = FM.arc_spline([P(p) for p in points], headings=headings or {})
    return d, pts


# ---------------------------------------------------------------------------
# beret, brooch, plume, hair
# ---------------------------------------------------------------------------
def beret(pts, rim, button, *, ripples=(11.0, 17.0), ripple_ry=0.34, underside=True):
    """The jade beret, a soft flat bonnet seen in profile. ``pts``: its closed
    outline, clockwise from the band's front-bottom corner. ``rim``: the
    crown's rim (the disc's edge, front → back, a 3-point arc) — the
    underside below it, where the disc overhangs the band, is half-hatched
    (§B.2: FINE, 7.0, one half of the split shape). The button on the crown
    sits in two flattened ripple arcs (§G.8) — the spring seen from above."""
    d, reg = spline_region(pts)
    lines = K.outline(reg)
    rim_d = K.arc3(*rim)
    lines += K.clip_in(K.line(rim_d, MED, role="rim"), reg.buffer(-0.5))
    below = K.R(rim_d + "L2000 2000L-2000 2000Z").buffer(0)
    if underside:
        under = reg.intersection(below).buffer(-(MED / 2 + 0.3))
        lines += K.hatch_in(under, angle=-45.0, origin=(rim[0][0], rim[0][1]))
    cx, cy = button
    rip = C.Frag()
    for r in ripples:
        rip += C.stroke(C.ellipse_arc_d(cx, cy, r, r * ripple_ry, 200, 340), FINE, role="ripple")
    rip = K.clip_in(rip, reg.buffer(-(CON / 2 + K.GAP + FINE / 2 + 0.2)))
    btn = K.dot((cx, cy), 8.4, INK, role="button")
    return K.Part(reg, K.fill(reg, JADE), lines + rip + btn, {"under": reg.intersection(below)})


def heart_d(cx, top, u):
    """The deck's heart pip construction (§E.1): lobes r 0.26u at (±0.24u,
    0.26u), straight tangents to the point at 0.92u. Point DOWN."""
    from deck import pips as PP
    return PP.pip_top_d("H", u, cx, top) if hasattr(PP, "pip_top_d") else None


def fluke_heart(c, u=24.0, bezel=4.0):
    """The red fluke-heart brooch: a Gill Red heart (the deck's pip
    construction, point down) on a gold bezel that follows it ``bezel`` px
    outside — solid gold with an Aquifer contour (legal against red)."""
    from deck import pips as PP
    hd = PP.pip_d("H", u, c[0], c[1])
    heart = K.R(hd)
    bz = heart.buffer(bezel, quad_segs=12)
    fills = K.fill(bz.difference(heart), GOLD) + K.fill(heart, RED)
    lines = K.outline(bz) + K.outline(heart, FINE)
    return K.Part(bz, fills, lines, {"heart": heart})


PITCH_ = K.PITCH


def plume(root, heading, turns, hw_max=16.0, hw_tip=2.0, root_hw=3.0, belly=0.45, n=3, stagger=9.0,
          side=-1, curl_deg=100.0, locks=0, lock_from=0.45, lock_depth=7.0, tip_round=0.0, lock_side=-1):
    """One long curling plume (§H.6) of gold current lines (§G.24). Its
    centre guide is a tangent-arc chain (a Turtle from ``root`` at
    ``heading`` through ``turns`` = [(r, sweep°), ...], all turning the same
    way, so the plume CURLS); its half-width swells from the quill
    (``root_hw``) to ``hw_max`` at ``belly`` of the length and tapers to
    ``hw_tip`` (a pointed, curling wisp). With ``locks`` the OUTER edge
    breaks, from ``lock_from`` of the length, into lopsided flame locks
    (forms.lock_row) flowing to the tip — the fronds of an ostrich plume.
    ``n`` current lines — offsets of the outer edge inward, 7 px apart —
    roll into Ø6.3 terminals, staggered."""
    t = C.Turtle(root[0], root[1], heading)
    for r, sw in turns:
        t.arc(r, sw)
    gp = t.pts(0.5)[0]
    cv = K.G.Curve(gp)
    L = cv.length
    ss = np.linspace(0, L, 480)
    tt = ss / L
    hw = np.where(tt < belly, root_hw + (hw_max - root_hw) * np.sin(np.pi / 2 * np.clip(tt / belly, 0, 1)) ** 0.8,
                  hw_tip + (hw_max - hw_tip) * np.cos(np.pi / 2 * np.clip((tt - belly) / (1 - belly), 0, 1)) ** 0.9)
    pts = np.array([cv.at_s(s) for s in ss])
    tang = np.gradient(pts, axis=0)
    tang /= np.hypot(*tang.T)[:, None]
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])
    left = pts + nrm * hw[:, None]
    right = pts - nrm * hw[:, None]
    outer, inner = (left, right) if side < 0 else (right, left)
    if locks:
        # the UNDERSIDE fringes into lopsided locks flowing to the tip
        k0 = int(len(ss) * lock_from)
        seg_len = float(np.sum(np.hypot(*np.diff(inner[k0:], axis=0).T)))
        d_l, cusps, peaks = FM.lock_row(inner[k0:], seg_len / locks, lock_depth,
                                        side=(1 if side < 0 else -1) * lock_side, skew=0.70)
        lk = C.sample_d(d_l, 0.4)[0][0]
        inner = np.vstack([inner[:k0], lk])
    poly = Polygon(np.vstack([outer, inner[::-1]])).buffer(0)
    quill = Point(*pts[0]).buffer(root_hw, quad_segs=12)
    parts = [poly, quill]
    if tip_round:
        parts.append(Point(*pts[-1]).buffer(tip_round, quad_segs=16))
    reg = shapely.union_all(parts).buffer(0.8, quad_segs=8).buffer(-0.8, quad_segs=8)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    edge_pts = left if side < 0 else right
    lines = K.current_lines(edge_pts, n, reg, side=side, edge=CON, stagger=stagger, curl_r=4.2, curl_deg=curl_deg)
    return K.Part(reg, K.fill(reg, GOLD), K.outline(reg) + lines,
                  {"guide": pts, "n_lines": len(lines.meta.get("lines", []))})


def hair_bob(outline_pts, guide_pts, n=4, side=-1):
    """The page's gold bob: region through ``outline_pts``; current lines are
    offsets of ``guide_pts`` (drawn from the crown down to the roll), rolling
    into terminals at the roll."""
    d, reg = spline_region(outline_pts)
    _, gp = open_spline(guide_pts)
    lines = K.current_lines(gp, n, reg, side=side, edge=CON, stagger=7.0, curl_r=4.2, curl_deg=80.0)
    return K.Part(reg, K.fill(reg, GOLD), K.outline(reg) + lines, {"n_lines": len(lines.meta.get("lines", []))})


# ---------------------------------------------------------------------------
# the fiddle
# ---------------------------------------------------------------------------
class Fiddle:
    """A frontal fiddle standing on the vertical axis x = ``x`` (card px, y
    down), built as two Parts so the player's fist can sit between them: the
    NECK (volute scroll, pegbox, four pegs, nut, the ebony fingerboard in
    jade) behind the fist and the BODY in front of the fist's wrist.

    The body outline is the right half through ``half`` (dx, dy below
    ``body_top``) — shoulder, widest upper bout, the pointed upper corner,
    the C-bout waist, the pointed lower corner, the lower bout — mirrored."""

    def __init__(self, x=528.0, scroll_c=(528.0, 132.0), scroll_r=19.0, nut=212.0, pegbox_w=(15.0, 21.0),
                 fb_w=(17.0, 25.0), fb_end=398.0, body_top=325.0, bridge=428.0, tail_top=446.0,
                 half=((34.0, 6.0), (50.0, 33.0), (47.0, 55.0), (46.5, 64.0), (32.0, 92.0), (45.0, 121.0),
                       (58.0, 140.0), (64.0, 178.0))):
        self.x = x
        self.scroll_c, self.scroll_r = P(scroll_c), scroll_r
        self.nut, self.pegbox_w, self.fb_w, self.fb_end = nut, pegbox_w, fb_w, fb_end
        self.body_top, self.bridge, self.tail_top = body_top, bridge, tail_top
        self.half = half

    def _hp(self, i, sg=1):
        dx, dy = self.half[i]
        return P(self.x + sg * dx, self.body_top + dy)

    def body_region(self):
        x, y0 = self.x, self.body_top
        T_ = P(x, y0)
        S1, U_, Ub, CU, W_, CL, Lb, L_ = (self._hp(i) for i in range(8))
        pth = K.Path(T_).arc3(S1, U_).arc3(Ub, CU).arc3(W_, CL).arc3(Lb, L_)
        pth.line(P(L_[0] + 2.0, 600.0)).line(P(x, 600.0)).close()
        half = K.R(pth.d)
        return K.U(half, K.mirror(half, x))

    def neck_part(self):
        x = self.x
        sc, sr = self.scroll_c, self.scroll_r
        w0, w1 = self.pegbox_w
        pb_top = sc[1] + sr * 0.62
        pegbox = Polygon([(x - w0 / 2, pb_top - 6), (x + w0 / 2, pb_top - 6), (x + w1 / 2, self.nut),
                          (x - w1 / 2, self.nut)])
        head = Point(*sc).buffer(sr, quad_segs=48)
        pegs = []
        ys = [pb_top + (self.nut - pb_top) * t for t in (0.26, 0.66)]
        for sg, y in [(-1, ys[0]), (1, ys[0] + 7.0), (-1, ys[1]), (1, ys[1] + 7.0)]:
            wy = w0 + (w1 - w0) * (y - pb_top) / (self.nut - pb_top)
            xe = x + sg * wy / 2
            shaft = LineString([(xe - sg * 3, y), (xe + sg * 8.0, y)]).buffer(3.2, cap_style=2)
            thumb = shapely.affinity.scale(Point(xe + sg * 15.5, y).buffer(8.0, quad_segs=24), 1.0, 0.70)
            pegs.append(shapely.union_all([shaft, thumb]))
        pegs_u = shapely.union_all(pegs)
        a, b = self.fb_w
        fb = Polygon([(x - a / 2, self.nut), (x + a / 2, self.nut), (x + b / 2, self.fb_end), (x - b / 2, self.fb_end)])
        gold = shapely.union_all([pegbox, head])
        shape = shapely.union_all([gold, pegs_u, fb])
        fills = K.fill(gold, GOLD) + K.fill(pegs_u.difference(gold.buffer(-0.3)), JADE) + K.fill(fb, JADE)
        lines = K.outline(shape)
        lines += K.clip_out(K.outline(pegs_u), gold.buffer(-0.3), eps=-0.6, trap=0.0)
        lines += K.outline(fb)
        # the volute (a true scroll): from the pegbox's back edge up round the
        # head in a spiral of tangent arcs rolling into the Ø6.3 eye
        r1 = sr - CON / 2 - K.GAP - MED / 2 + 0.6
        t = C.Turtle(sc[0] - r1, sc[1] + 3.0, -90.0)
        t.arc(r1, 180.0)
        t.arc(r1 * 0.66, 180.0)
        t.arc(r1 * 0.40, 120.0)
        # the spiral's tail runs down into the pegbox's left cheek
        t0 = C.Turtle(sc[0] - r1, sc[1] + 3.0, 90.0)
        t0.fd(pb_top - sc[1] - 3.0 + 2.0)
        vol = K.line(t.d(), MED, role="volute") + K.dot(t.pos, 6.3, role="volute-eye")
        lines += vol
        lines += K.seg(P(x - a / 2, self.nut), P(x + a / 2, self.nut), MED, role="nut")
        return K.Part(shape, fills, lines, {"fingerboard": fb, "gold": gold, "head": head})

    def body_part(self, *, hatch_side=0):
        x = self.x
        reg = self.body_region()
        lines = K.outline(reg)
        purf = reg.buffer(-(CON / 2 + K.GAP + FINE / 2 + 0.05), quad_segs=16)
        a, b = self.fb_w
        fb = Polygon([(x - b / 2 - 0.3, self.body_top - 40), (x + b / 2 + 0.3, self.body_top - 40),
                      (x + b / 2, self.fb_end), (x - b / 2, self.fb_end)]).intersection(reg)
        tail = Polygon([(x - 10.0, self.tail_top), (x + 10.0, self.tail_top), (x + 14.5, 600.0), (x - 14.5, 600.0)])
        tail = tail.buffer(2.0, join_style=1).buffer(-2.0, join_style=1).intersection(reg)
        bridge = K.R(K.rrect(x - 13.5, self.bridge - 3.4, x + 13.5, self.bridge + 3.4, 2.2))
        keep_clear = fb.union(tail).union(bridge)
        det = C.stroke(K.D(purf), FINE, role="purfling")
        # f-holes: an S between two eyes (Ø6.3 above, Ø8.4 below), with the
        # two notches at the waist, one each side of the strings
        cu, cl = self._hp(3), self._hp(5)
        for sg in (-1, 1):
            up = P(x + sg * 21.0, cu[1] + 6.0)
            lo = P(x + sg * 26.5, cl[1] - 5.0)
            mid = (up + lo) / 2
            d = K.arc_sag(up, mid, -sg * 3.4) + K.arc_sag(mid, lo, sg * 3.4, move=False)
            det += K.line(d, MED, role="f-hole")
            det += K.dot(up + P(-sg * 1.4, -2.2), 6.3, role="f-eye")
            det += K.dot(lo + P(sg * 1.2, 2.8), 8.4, role="f-eye")
        det = K.clip_out(det, keep_clear, eps=0.0, trap=0.0, extra=keep_clear.buffer(K.GAP_MARK + FINE))
        strings = C.Frag()
        for k in range(4):
            u = (k - 1.5)
            x0, x1, x2 = x + u * 5.4, x + u * 6.6, x + u * 5.4
            strings += K.seg(P(x0, self.fb_end), P(x1, self.bridge), FINE, role="string")
            strings += K.seg(P(x1, self.bridge), P(x2, self.tail_top), FINE, role="string")
        strings = K.clip_out(strings, bridge, eps=-0.6, trap=0.0)
        fills = K.fill(reg, GOLD) + K.fill(fb, JADE) + K.fill(tail, JADE) + K.fill(bridge, GOLD)
        if hatch_side:
            half = reg.intersection(K.halfplane((x, 0), (x, 1000), side=-hatch_side))
            hz = half.buffer(-(CON / 2)).difference(keep_clear.buffer(K.GAP + MED))
            det += K.hatch_in(hz, angle=-45.0 if hatch_side > 0 else -135.0)
        lines = lines + det + K.outline(fb) + K.outline(tail) + K.outline(bridge) + strings
        return K.Part(reg, fills, lines, {"fb": fb, "tail": tail})


# ---------------------------------------------------------------------------
# the bow
# ---------------------------------------------------------------------------
def bow(x, tip_y, frog_y, end_y, *, stick_w=10.0, camber=4.0, hair_dx=12.0, color=RED):
    """The bow, vertical, the stick on the left of the hair (§H.6: parallel
    to the fiddle neck, never crossing it). The stick (Gill Red: pernambuco)
    is cambered toward the hair; the head a small gold hatchet at the tip;
    the frog a gold block with a pearl eye; the hair a MEDIUM line from the
    frog to the head, ≥ 4.2 clear of the stick."""
    top = P(x, tip_y)
    bot = P(x, end_y)
    stick_guide = K.arc_sag(bot, top, -camber)            # bulges toward +x (the hair)
    gp = C.sample_d(stick_guide, 0.5)[0][0]
    stick = LineString(gp).buffer(stick_w / 2, cap_style=1, quad_segs=8)
    hx = x + hair_dx
    head = Polygon([(x - stick_w / 2, tip_y + 4), (x - 1.0, tip_y - 7), (hx + 4.0, tip_y + 9),
                    (hx + 4.0, tip_y + 18), (x + stick_w / 2, tip_y + 22)])
    head = head.buffer(2.2, join_style=1).buffer(-2.2, join_style=1)
    frog = K.R(K.rrect(x + stick_w / 2 - 2.0, frog_y, hx + 6.0, frog_y + 30.0, 3.5))
    button = K.R(K.rrect(x - stick_w / 2 - 1.0, end_y - 16, x + stick_w / 2 + 1.0, end_y, 2.5))
    shape = shapely.union_all([stick, head, frog, button])
    eye = Point(hx - 1.0, frog_y + 13.0).buffer(3.4, quad_segs=16)
    gold = shapely.union_all([head, frog, button])
    fills = K.fill(stick.difference(gold), color) + K.fill(gold.difference(eye), GOLD)
    lines = K.outline(shape)
    lines += K.clip_out(K.outline(frog) + K.outline(head) + K.outline(button), stick.buffer(-0.4).difference(
        gold.buffer(0.1)), eps=0.0, trap=0.0) if False else (K.outline(frog) + K.outline(head) + K.outline(button))
    lines += K.outline(eye, FINE)
    hair_ln = LineString([(hx, frog_y), (hx, tip_y + 14)])
    hair = K.line(K.D(hair_ln), MED, role="bow-hair")
    return K.Part(shape.union(hair_ln.buffer(MED / 2)), fills, lines + hair, {"stick": stick, "hair_x": hx})


# ---------------------------------------------------------------------------
# sash with the festoon, bead chain, slashes
# ---------------------------------------------------------------------------
def sash(p_top, p_bot, half_w, clip_region, *, swag=44.0, sag=8.5, phase=0.0):
    """The paper sash: a band ``half_w`` px either side of the line
    p_top → p_bot (through the card centre, so its 180° copy continues it),
    clipped to ``clip_region`` (the torso). Along it the festoon string-light
    catenary (§G.28): FINE Aquifer swags between supports near the sash's
    upper edge, sagging toward its lower edge, with gold bulbs (Ø6.3 solid,
    §G.28's 5–6 px) hung at the low points and at the joins. The festoon is
    clipped whole-bulb (atomic) to the sash, 4.2 px inside its edges."""
    a, b = P(p_top), P(p_bot)
    u = (b - a) / np.hypot(*(b - a))
    n = np.array([u[1], -u[0]])            # screen-left of travel: the sash's upper edge side
    band = Polygon([a - u * 300 + n * half_w, b + u * 300 + n * half_w, b + u * 300 - n * half_w,
                    a - u * 300 - n * half_w])
    reg = band.intersection(clip_region)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    lines = K.outline(reg)
    inner = reg.buffer(-(MED / 2 + K.GAP + FINE / 2 + 0.1))
    L = float(np.hypot(*(b - a)))
    wire = C.Frag()
    bulbs = C.Frag()
    ks = np.arange(-8, int(L / swag) + 4)
    supports = [a + u * (phase + k * swag) + n * (half_w * 0.34) for k in ks]
    for i, (p0, p1) in enumerate(zip(supports[:-1], supports[1:])):
        m = (p0 + p1) / 2 - n * sag
        wire += K.line(K.arc3(p0, m, p1), FINE, role="wire")
        bulbs += K.atomic(K.dot(m - n * 4.6, 6.3, GOLD, role="bulb") +
                          K.line(K.D(LineString([tuple(m), tuple(m - n * 1.6)])), FINE, role="socket"), f"bulb{i}")
    for i, p in enumerate(supports):
        bulbs += K.atomic(K.dot(p, 6.3, GOLD, role="bulb"), f"join{i}")
    wire = K.clip_in(wire, inner)
    keep = C.Frag()
    groups = {}
    for m in bulbs.marks:
        groups.setdefault(m.role.split("@")[1], []).append(m)
    zone = reg.buffer(-(MED / 2 + K.GAP_MARK + 0.2))
    for key, ms in groups.items():
        g = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in ms])
        if zone.contains(g):
            keep += C.Frag(ms)
    return K.Part(reg, C.Frag(), lines + wire + keep, {"u": u, "n": n, "band": band})


def bead_chain(path_pts, d=7.4, gap=3.6, grow=None, keep=None):
    """Bubble-chain piping: solid gold beads with a FINE Aquifer contour
    (the only legal gold on red, §C.4) strung along ``path_pts`` with equal
    clear gaps; ``grow`` (d0, d1) grades them (bubbles grow as they rise)."""
    cv = K.G.Curve(np.asarray(path_pts, float))
    L = cv.length
    f = C.Frag()
    s = 0.0
    k = 0
    beads = []
    while True:
        dd = d if grow is None else grow[0] + (grow[1] - grow[0]) * min(s / max(L, 1), 1.0)
        if s + dd / 2 > L:
            break
        c = cv.at_s(s + dd / 2)
        beads.append((c, dd))
        s += dd + gap + FINE
    for i, (c, dd) in enumerate(beads):
        if keep is not None and not keep.contains(Point(*c).buffer(dd / 2 + FINE)):
            continue
        g = Point(*c).buffer(dd / 2, quad_segs=16)
        f += K.atomic(K.fill(g, GOLD, role="bead") + K.outline(g, FINE, role="bead"), f"bead{id(path_pts)}_{i}")
    return f


def ripple_slashes(field_d, centre, radii, a0, a1, w=MED):
    """Ripple-arc slashes (§H.6 'sleeves slashed with ripple arcs'): groups of
    concentric arcs (§G.8, gaps ×1.3) KNOCKED OUT of the jade — the white
    shirt showing through. Returns the knockout Frag (strokes)."""
    f = C.Frag()
    for r in radii:
        f += C.stroke(C.arc_d(centre[0], centre[1], r, a0, a1), w, role="slash")
    return f
