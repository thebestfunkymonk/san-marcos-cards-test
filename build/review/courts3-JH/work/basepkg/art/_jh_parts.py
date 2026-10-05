"""art/_jh_parts.py — the J♥ Spring Minstrel's own parts, in the courtkit hand.

Everything is a courtkit Part (shape, fills, lines, meta) built from compass
geometry at final size; art/JH.py stacks them back to front in a Scene.

    spline_region   closed G1 arc spline → (d, region)
    beret           the jade beret: a soft disc tilted over the brow on a band;
                    ripple rings round its button (the spring seen from above),
                    the overhang's underside half-hatched
    fluke_heart     the red fluke-heart brooch on a gold bezel (§H.6)
    plume           one long curling plume of gold current lines (§G.24)
    hair_bob        the page-boy bob behind the ear, rolled under
    collar          the jade standing collar, gold bubble piping on its edge
    Fiddle          scroll (a true volute), pegbox and pegs, neck + jade
                    fingerboard, the gold body with purfling, f-holes, bridge,
                    four Aquifer strings and the jade tailpiece
    bow             the bow: red stick, gold head and frog, the hair
    sash            the paper sash with the festoon string-light catenary
    bead_chain      bubble-chain piping: gold beads, Aquifer contour (legal on red)
    puff_sleeve     a puffed jade upper sleeve slashed with ripple arcs (paper)
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM

P = K.P
MED, FINE, RULE, CON = K.MEDIUM, K.FINE, K.RULE, K.CONTOUR
TD_EYE = 6.3 / 2 + MED / 2 + 3.0 + 0.2      # smallest volute radius that keeps the eye 3 px clear
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------
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


def open_spline(points, headings=None, h_start=None, h_end=None):
    """Open G1 arc spline → (d, dense points)."""
    d, pts, _ = FM.arc_spline([P(p) for p in points], h_start, h_end, headings=headings or {})
    return d, pts


def biggest(g):
    ps = K._polys_of(g)
    return max(ps, key=lambda q: q.area) if ps else Polygon()


# ---------------------------------------------------------------------------
# beret, brooch, plume, hair, collar
# ---------------------------------------------------------------------------
def disc_pts(c, rx, ry_top, ry_bot, tilt, n=16):
    """Points round a soft beret disc: an ellipse (``rx``; ``ry_top`` above
    its rim line, ``ry_bot`` below — the crown puffs up more than it
    overhangs) rotated ``tilt`` degrees (negative: the back rises)."""
    out = []
    ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    for k in range(n):
        th = 2 * math.pi * k / n
        x, y = rx * math.cos(th), (ry_bot if math.sin(th) > 0 else ry_top) * math.sin(th)
        out.append((c[0] + x * ca - y * sa, c[1] + x * sa + y * ca))
    return out


def beret(c, rx, ry_top, ry_bot, tilt, band_lo, band_h=13.0, *, skull=None, button=None,
          ripples=((15.0, 4.8), (29.0, 11.4)), button_d=0.0, hatch_band=True, n=16):
    """The jade beret: a soft DISC (``disc_pts``) tilted over the brow on a
    BAND that hugs the skull (the strip ``band_h`` px above the line
    ``band_lo`` = (front, back), clipped to the ``skull`` region grown
    2.5 px). The band — the disc's shadowed underside where it gathers onto
    the head — is half-hatched (§B.2: FINE 7.0, one half of the split
    shape, the other half the plain crown). On the crown a Ø8.4 button sits
    in flattened ripple rings (§G.8, gaps ×1.3) tilted with the disc: the
    spring seen from above."""
    d_disc, disc = spline_region(disc_pts(c, rx, ry_top, ry_bot, tilt, n))
    f0, f1 = P(band_lo[0]), P(band_lo[1])
    u = (f1 - f0) / np.hypot(*(f1 - f0))
    nn = np.array([u[1], -u[0]])                  # screen-left of front→back = up
    strip = Polygon([f0 - u * 40, f1 + u * 40, f1 + u * 40 + nn * (band_h + 40), f0 - u * 40 + nn * (band_h + 40)])
    head_zone = skull.buffer(2.5, quad_segs=24) if skull is not None else strip
    band = strip.intersection(head_zone)
    shape = biggest(K.U(disc, band).buffer(4.0, quad_segs=12).buffer(-4.0, quad_segs=12))
    band_vis = shape.difference(disc)
    fills = K.fill(shape, JADE)
    lines = K.outline(shape)
    lines += K.clip_in(K.outline(disc), band.buffer(-0.4))           # the disc's rim over the band
    if hatch_band:
        hz = band_vis.buffer(-0.2)
        lines += K.hatch_in(hz, angle=-50.0, origin=tuple(f0))
    rip = C.Frag()
    if button is not None:
        bx, by = button
        zone = disc.buffer(-(CON / 2 + K.GAP_MARK + FINE / 2 + 0.2))
        for i, (rx_, ry_) in enumerate(ripples):
            e = C.stroke(C.ellipse_arc_d(bx, by, rx_, ry_, 0, 360), FINE, role="ripple")
            e = e.rotate(tilt, bx, by) if tilt else e
            if zone.contains(K.R(K.G.from_skia(e.marks[0].skia()))):
                rip += e
        if button_d:
            rip += K.dot((bx, by), button_d, INK, role="button")
    return K.Part(shape, fills, lines + rip, {"disc": disc, "band": band, "band_vis": band_vis, "u": u, "n": nn})


def fluke_heart(c, u=22.0, bezel=3.5, ring=0.0):
    """The red fluke-heart brooch: a Gill Red heart (the deck's pip
    construction, point down) on a gold bezel ``bezel`` px outside it —
    solid gold with an Aquifer contour (legal against red)."""
    from deck import pips as PP
    hd = PP.pip_d("H", u, c[0], c[1])
    heart = K.R(hd)
    if ring > 0:
        # a pip in a setting: the Gill Red heart (a pip: no line of its own) in a paper channel
        # ``ring`` px wide knocked out of the gold bezel, whose outer edge carries the MEDIUM contour
        # (the look the brooch always had, built geometrically instead of by heal)
        bz = heart.buffer(bezel, quad_segs=12)
        gold = bz.difference(heart.buffer(ring, quad_segs=12))
        return K.Part(bz, K.fill(gold, GOLD) + K.fill(heart, RED), K.outline(bz, MED), {"heart": heart})
    if bezel <= 0:
        # the heart alone, MEDIUM Aquifer contour (a pin head on the quill)
        return K.Part(heart, K.fill(heart, RED), K.outline(heart, MED), {"heart": heart})
    # the two contours need 4.2 px of gold between them (heal): bezel ≥ MED/2 + FINE/2 + 4.2
    assert bezel >= MED / 2 + FINE / 2 + K.GAP - 1e-6, f"bezel {bezel} too narrow for two contours"
    bz = heart.buffer(bezel, quad_segs=12)
    fills = K.fill(bz.difference(heart), GOLD) + K.fill(heart, RED)
    lines = K.outline(bz, MED) + K.outline(heart, FINE)
    return K.Part(bz, fills, lines, {"heart": heart})


def ribbon(guide, hw_fn, *, tip_round=0.0, root_round=0.0):
    """A ribbon region of half-width hw_fn(t) (t 0..1) along a dense guide.
    → (region, left edge, right edge, guide pts)."""
    gp = np.asarray(guide, float)
    cv = K.G.Curve(gp)
    L = cv.length
    ss = np.linspace(0, L, max(60, int(L / 0.8)))
    tt = ss / L
    pts = np.array([cv.at_s(s) for s in ss])
    tang = np.gradient(pts, axis=0)
    tang /= np.hypot(*tang.T)[:, None]
    nrm = np.column_stack([tang[:, 1], -tang[:, 0]])             # screen-left of travel
    hw = np.array([hw_fn(t) for t in tt])
    left = pts + nrm * hw[:, None]
    right = pts - nrm * hw[:, None]
    poly = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    parts = [poly]
    if tip_round:
        parts.append(Point(*pts[-1]).buffer(tip_round, quad_segs=16))
    if root_round:
        parts.append(Point(*pts[0]).buffer(root_round, quad_segs=16))
    reg = biggest(shapely.union_all(parts).buffer(0.6, quad_segs=8).buffer(-0.6, quad_segs=8))
    return reg, left, right, pts


def plume(guide_pts, *, h_start=None, hw_root=4.5, hw_max=19.0, belly=0.40, hw_tip=6.0, n=3, stagger=14.0,
          side=+1, curl_r=4.2, curl_deg=110.0, fronds=0, frond_from=0.35, frond_depth=6.0, frond_skew=0.7,
          tip_round=7.0):
    """One long curling plume (§H.6) of gold current lines (§G.24). The
    guide is an open arc spline through ``guide_pts`` (root → curled tip);
    the half-width swells from the quill (``hw_root``) to ``hw_max`` at
    ``belly`` and eases to a round curled tip. ``n`` current lines run as
    offsets of the ``side`` edge (+1: the screen-left edge of travel)
    inward, 7 px apart, rolling into Ø6.3 terminals, staggered — the plume's
    barbs combed into locks. With ``fronds`` the other edge breaks into
    lopsided locks flowing to the tip (forms.lock_row)."""
    _, gp = open_spline(guide_pts, h_start=h_start)

    def hw(t):
        if t < belly:
            return hw_root + (hw_max - hw_root) * math.sin(math.pi / 2 * t / belly) ** 0.9
        return hw_tip + (hw_max - hw_tip) * math.cos(math.pi / 2 * (t - belly) / (1 - belly)) ** 1.1
    reg, left, right, pts = ribbon(gp, hw, tip_round=tip_round, root_round=hw_root)
    edge = left if side > 0 else right
    other = right if side > 0 else left
    if fronds:
        k0 = int(len(other) * frond_from)
        seg = other[k0:]
        L = float(np.sum(np.hypot(*np.diff(seg, axis=0).T)))
        d_l, _, _ = FM.lock_row(seg, L / fronds, frond_depth, side=(1 if side > 0 else -1) * -1 * -1,
                                skew=frond_skew)
        lk = C.sample_d(d_l, 0.4)[0][0]
        other2 = np.vstack([other[:k0], lk])
        poly = Polygon(np.vstack([edge, other2[::-1]]) if side > 0 else np.vstack([other2, edge[::-1]])).buffer(0)
        reg = biggest(K.U(poly, Point(*pts[-1]).buffer(tip_round, quad_segs=16),
                          Point(*pts[0]).buffer(hw_root, quad_segs=16)).buffer(0.6).buffer(-0.6))
    lines = K.current_lines(edge, n, reg, side=-side, edge=CON, stagger=stagger, curl_r=curl_r, curl_deg=curl_deg)
    return K.Part(reg, K.fill(reg, GOLD), K.outline(reg) + lines,
                  {"guide": pts, "n_lines": len(lines.meta.get("lines", [])), "edge": edge})


def hair_bob(outline_pts, guide_pts, n=4, side=-1, stagger=8.0, curl_deg=80.0, headings=None):
    """The page's gold bob: region through ``outline_pts``; current lines are
    offsets of ``guide_pts`` (drawn from the crown down to the roll),
    rolling into terminals at the roll."""
    _, reg = spline_region(outline_pts, headings)
    _, gp = open_spline(guide_pts)
    lines = K.current_lines(gp, n, reg, side=side, edge=CON, stagger=stagger, curl_r=4.2, curl_deg=curl_deg)
    return K.Part(reg, K.fill(reg, GOLD), K.outline(reg) + lines, {"n_lines": len(lines.meta.get("lines", []))})


def collar(front_top, back_top, front_bot, back_bot, *, top_sag=-5.0, bot_sag=-4.0, color=JADE,
           bead_d=6.3, bead_gap=3.6):
    """The standing collar round the neck, a short cylinder seen from the
    side: the top edge an arc from ``front_top`` to ``back_top`` (sagging
    ``top_sag``: the cylinder's near rim), the ends straight, the foot an arc
    from ``back_bot`` to ``front_bot``; filled ``color``, with a row of gold
    beads (Aquifer contour; bubble-chain piping, §H.6) round its middle."""
    ft, bt_, fb, bb = P(front_top), P(back_top), P(front_bot), P(back_bot)
    pth = K.Path(ft).sag(bt_, top_sag).line(bb).sag(fb, bot_sag).close()
    reg = K.R(pth.d).buffer(-2.5, quad_segs=12).buffer(2.5, quad_segs=12)
    lines = K.outline(reg)
    mid_d = K.arc_sag((ft + fb) / 2, (bt_ + bb) / 2, (top_sag - bot_sag) / 2)
    mp = C.sample_d(mid_d, 0.3)[0][0]
    extra = bead_chain(mp, d=bead_d, gap=bead_gap, keep=reg.buffer(-(MED / 2 + 3.0 - 0.05)))
    return K.Part(reg, K.fill(reg, color), lines + extra, {})


# ---------------------------------------------------------------------------
# the fiddle
# ---------------------------------------------------------------------------
class Fiddle:
    """A frontal fiddle standing upright on x = ``x`` (§H.6: gold, a volute
    scroll at the top, f-holes and four strings in Aquifer), built as two
    Parts so the player's fist can sit between them: the NECK (volute
    scroll, pegbox, the neck and the jade fingerboard; with ``pegs='oval'``
    four jade oval pegs) behind the fist, and the BODY in front of the fist's
    wrist. With ``pegs='T'`` the pegs are small gold T's, their own Part
    (``tpegs_part``) stacked behind the neck.

    Proportions follow a real violin at ≈ 0.575 px/mm: body 205 tall, upper
    bout 96, waist 64, lower bout 120; neck 74; pegbox + scroll ≈ 70."""

    def __init__(self, x=530.0, body_top=296.0, *, scale=1.0, scroll_r=19.0, neck_len=74.0, pegbox_len=47.0,
                 fb_len=142.0, bridge_dy=116.0, tail=(18.0, 62.0), peg_t=(0.22, 0.40, 0.62, 0.80), volute="eye",
                 tail_w=(26.0, 13.0), peg_len=17.0, peg_aspect=0.62, peg_shaft=3.0, waist=(31.0, 99.0),
                 fhole=(24.5, 84.0, 28.0, 134.0, 4.4), bridge_ext=7.5, pegs="oval", tpeg=(5.0, 6.0, 7.0, 13.0)):
        k = scale
        self.pegs, self.tpeg = pegs, tpeg
        self.peg_t, self.volute, self.tail_w = peg_t, volute, tail_w
        self.peg_len, self.peg_aspect, self.peg_shaft = peg_len, peg_aspect, peg_shaft
        self.waist, self.fhole, self.bridge_ext = waist, fhole, bridge_ext
        self.x, self.k = x, k
        self.bt = body_top
        self.nut = body_top - neck_len * k
        self.pb_top = self.nut - pegbox_len * k
        self.scroll_r = scroll_r * k
        self.scroll_c = P(x, self.pb_top - self.scroll_r * 0.35)
        self.fb_end = self.nut + fb_len * k
        self.bridge = body_top + bridge_dy * k
        self.tail_top = self.bridge + tail[0] * k
        self.tail_bot = self.tail_top + tail[1] * k
        self.bottom = body_top + 205.0 * k

    def _peg_rows(self):
        """(side, y, pegbox width at y) for the four pegs: left, right, left, right down the box."""
        k = self.k
        w_top, w_nut = 13.0 * k, 17.0 * k
        out = []
        for sg, t in ((-1, self.peg_t[0]), (1, self.peg_t[1]), (-1, self.peg_t[2]), (1, self.peg_t[3])):
            y = self.pb_top + (self.nut - self.pb_top) * t
            out.append((sg, y, w_top + (w_nut - w_top) * (y - self.pb_top) / (self.nut - self.pb_top)))
        return out

    def tpegs_part(self):
        """The four tuning pegs as small gold T's (a short shaft out of the cheek, the thumb-piece
        seen edge-on as a bar across its end), solid gold with an Aquifer contour, two a side.
        ``tpeg`` = (shaft showing between the cheek's CONTOUR and the head's outline, shaft width,
        head width, head height). The outer edge stays inside the scroll's silhouette
        (|dx| + MEDIUM/2 ≤ the scroll radius + CONTOUR/2). Add it BEHIND the neck, sil=False: the
        shafts run in under the cheek's contour and the pegs keep a MEDIUM outline (at CONTOUR a
        6 px shaft would be all ink)."""
        x = self.x
        shaft_vis, shaft_w, head_w, head_h = self.tpeg
        lim = self.scroll_r + CON / 2 - 0.4
        pegs = []
        for sg, y, wy in self._peg_rows():
            xc = x + sg * wy / 2                                         # the cheek
            x_head = xc + sg * (CON / 2 + shaft_vis + MED / 2)           # the thumb-piece's inner face
            x_out = x_head + sg * head_w
            assert abs(x_out - x) + MED / 2 <= lim + 1e-6, f"T-peg sticks out past the scroll: {abs(x_out - x):.2f}"
            x0, x1 = sorted((xc - sg * 3.0, x_head + sg * 1.0))
            shaft = K.box(x0, y - shaft_w / 2, x1, y + shaft_w / 2)
            h0, h1 = sorted((x_head, x_out))
            head = K.R(K.rrect(h0, y - head_h / 2, h1, y + head_h / 2, min(head_w / 2 - 0.2, 2.6)))
            pegs.append(shapely.union_all([shaft, head]))
        reg = shapely.union_all(pegs).buffer(0.6, quad_segs=8).buffer(-0.6, quad_segs=8)
        return K.Part(reg, K.fill(reg, GOLD), K.outline(reg, MED), {"pegs": pegs})

    # ---- the body -------------------------------------------------------
    def body_region(self):
        x, y0, k = self.x, self.bt, self.k

        def q(dx, dy):
            return P(x + dx * k, y0 + dy * k)
        pth = K.Path(q(0, 0)).arc3(q(33, 9), q(48, 40)).arc3(q(49, 57), q(44.5, 72))       # upper bout to its corner
        pth.arc3(q(self.waist[0], self.waist[1]), q(45.5, 127))                            # the C-bout
        pth.arc3(q(60, 160), q(47, 191)).arc3(q(26, 203.5), q(0, 205))                     # lower bout to the end
        pth.line(q(-2, 205)).line(q(-2, 0)).close()
        half = K.R(pth.d)
        return K.U(half, K.mirror(half, x)).buffer(0.3).buffer(-0.3)

    def neck_part(self):
        x, k = self.x, self.k
        sc, sr = self.scroll_c, self.scroll_r
        w_top, w_nut = 13.0 * k, 17.0 * k
        pegbox = Polygon([(x - w_top / 2, sc[1] + sr * 0.5), (x + w_top / 2, sc[1] + sr * 0.5),
                          (x + w_nut / 2, self.nut), (x - w_nut / 2, self.nut)])
        head = Point(*sc).buffer(sr, quad_segs=48)
        neck = Polygon([(x - 8.0 * k, self.nut), (x + 8.0 * k, self.nut), (x + 9.5 * k, self.bt + 12),
                        (x - 9.5 * k, self.bt + 12)])
        # four pegs, two each side, staggered (left, right, left, right down the box): a collar at the
        # cheek and an oval thumb-piece — or, with ``pegs='T'``, nothing here: the gold T-pegs are
        # their own Part behind the neck (``tpegs_part``)
        pegs = []
        for sg, y, wy in (self._peg_rows() if self.pegs == "oval" else ()):
            xe = x + sg * wy / 2
            # the oval thumb-piece springs straight from the cheek (a separate thin shaft would be
            # all contour: its jade lost under the ink)
            thumb = shapely.affinity.scale(Point(xe + sg * (self.peg_len / 2 - 2.0), y).buffer(self.peg_len / 2, quad_segs=24),
                                           1.0, self.peg_aspect)
            pegs.append(thumb)
        pegs_u = shapely.union_all(pegs) if pegs else Polygon()
        a, b = 15.5 * k, 24.0 * k
        fb = Polygon([(x - a / 2, self.nut), (x + a / 2, self.nut), (x + b / 2, self.fb_end),
                      (x - b / 2, self.fb_end)])
        gold = shapely.union_all([pegbox, head, neck]).buffer(0.8, quad_segs=12).buffer(-0.8, quad_segs=12)
        shape = shapely.union_all([gold, pegs_u, fb]).buffer(0.2).buffer(-0.2)
        fills = K.fill(gold.difference(fb), GOLD) + K.fill(fb, JADE)
        lines = K.outline(shape)
        if pegs:
            fills += K.fill(pegs_u.difference(gold), JADE)
            lines += K.clip_in(K.outline(gold), pegs_u.buffer(0.6))     # where the pegs enter the cheeks
        lines += K.outline(fb)
        # the volute (§H.6 'a true volute scroll'; the deck's §G.31 eye volute):
        # up the scroll's cheek 8.9 px inside its rim, a half turn round the
        # head's centre, a half turn at half the radius landing on that
        # centre, and the Ø6.3 eye there
        r0 = sr - (CON / 2 + K.GAP + MED / 2) - 0.8
        if self.volute == "spiral":
            # a true volute, 1½ turns: up the cheek, a half turn over the top at r0, a half turn under
            # at r0 − 3.65 (the coils 7.3 apart: MEDIUM + 4.2), and a last half turn at half that
            # radius which lands on its centre: the Ø6.3 eye
            dd = (MED + K.GAP) / 2
            t = C.Turtle(sc[0] - r0, sc[1] + sr * 0.75, -90.0)
            t.fd(sr * 0.75)
            t.arc(r0, 180.0)
            t.arc(r0 - dd, 180.0)
            t.arc((r0 - dd) / 2, 180.0)
        else:
            t = C.Turtle(sc[0] - r0, sc[1] + sr * 0.62, -90.0)
            t.fd(sr * 0.62)
            t.arc(r0, 180.0)
            t.arc(r0 / 2, 180.0)
        lines += K.line(t.d(), MED, role="volute") + K.dot(t.pos, 6.3, role="volute-eye")
        lines += K.seg(P(x - a / 2, self.nut), P(x + a / 2, self.nut), MED, role="nut")
        return K.Part(shape, fills, lines, {"fingerboard": fb, "gold": gold, "head": head})

    def body_part(self, *, strings=4, pitch=6.4):
        x, k = self.x, self.k
        reg = self.body_region()
        lines = K.outline(reg)
        # purfling: a FINE line 4.2 clear inside the CONTOUR edge
        purf = reg.buffer(-(CON / 2 + K.GAP + FINE / 2 + 0.05), quad_segs=16)
        a, b = 15.5 * k, 24.0 * k
        fb_top = self.bt - 30.0
        fbw = lambda y: a + (b - a) * (y - self.nut) / (self.fb_end - self.nut)
        fb = Polygon([(x - fbw(fb_top) / 2, fb_top), (x + fbw(fb_top) / 2, fb_top), (x + b / 2, self.fb_end),
                      (x - b / 2, self.fb_end)]).intersection(reg)
        tw0, tw1 = self.tail_w[0] * k, self.tail_w[1] * k
        tail = K.R(K.Path(P(x - tw0 / 2, self.tail_top + 3)).sag(P(x + tw0 / 2, self.tail_top + 3), 3.0)
                   .line(P(x + tw1 / 2, self.tail_bot - tw1 / 2)).sag(P(x - tw1 / 2, self.tail_bot - tw1 / 2), tw1 / 2)
                   .close().d)
        tail = tail.buffer(1.5, join_style=1).buffer(-1.5, join_style=1).intersection(reg)
        bw = (strings - 1) * pitch / 2 + self.bridge_ext
        bridge = K.R(K.Path(P(x - bw, self.bridge + 3.2)).line(P(x - bw + 3, self.bridge - 3.4))
                     .sag(P(x + bw - 3, self.bridge - 3.4), 2.4).line(P(x + bw, self.bridge + 3.2)).close().d)
        keep_clear = fb.union(tail).union(bridge)
        det = C.stroke(K.D(purf), FINE, role="purfling")
        # f-holes: an S between two eyes, beside the bridge
        for sg in (-1, 1):
            fx0, fy0, fx1, fy1, fs = self.fhole
            up = P(x + sg * fx0 * k, self.bt + fy0 * k)
            lo = P(x + sg * fx1 * k, self.bt + fy1 * k)
            mid = (up + lo) / 2
            d = K.arc_sag(up, mid, -sg * fs) + K.arc_sag(mid, lo, sg * fs, move=False)
            det += K.line(d, MED, role="f-hole")
            det += K.dot(up, 6.3, role="f-eye")          # the eyes sit ON the S's ends (its terminals)
            det += K.dot(lo, 8.4, role="f-eye")
            # the two notches at the waist of the f
            nt = mid + P(sg * 0.0, 0.0)
        det = K.clip_out(det, keep_clear, eps=0.0, trap=0.0, extra=keep_clear.buffer(K.GAP_MARK + MED / 2 + 1.0))
        # four strings, parallel at ``pitch`` (≥ 4.2 clear), from the fingerboard's end over the bridge to the tailpiece
        strs = C.Frag()
        for kk in range(strings):
            u = kk - (strings - 1) / 2
            xs = x + u * pitch
            strs += K.seg(P(xs, self.fb_end - 2.0), P(xs, self.tail_top + 2.0), FINE, role="string")
        strs = K.clip_out(strs, bridge, eps=-0.6, trap=0.0)
        dots = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in det.marks if m.role == "f-eye"] or [Polygon()])
        fills = K.fill(reg.difference(dots.buffer(-0.8)), GOLD) + K.fill(fb, JADE) + K.fill(tail, JADE) + K.fill(bridge, GOLD)
        lines = lines + det + K.outline(fb) + K.outline(tail) + K.outline(bridge) + strs
        # the tailpiece's fine-tuner / fret: a gold saddle eye
        return K.Part(reg, fills, lines, {"fb": fb, "tail": tail, "bridge": bridge})


# ---------------------------------------------------------------------------
# the bow
# ---------------------------------------------------------------------------
def bow(x, tip_y, frog_y, end_y, *, stick_w=8.4, camber=3.0, hair_dx=11.0, color=RED, frog_h=28.0):
    """The bow, upright (§H.6: parallel to the fiddle neck, never crossing
    it): the stick (Gill Red: pernambuco) cambered toward the hair, a small
    gold hatchet HEAD at the tip, the gold FROG (with a jade slide and a
    pearl eye) and the screw BUTTON at the heel; the hair a MEDIUM line from
    the frog up to the head, ≥ 4.2 clear of the stick."""
    top, bot = P(x, tip_y + 4.0), P(x, end_y - 5.0)          # the stick's round end stays inside the button
    guide = K.arc_sag(bot, top, -camber)                 # bulges toward +x (the hair)
    gp = C.sample_d(guide, 0.5)[0][0]
    hwf = lambda t: stick_w / 2 * (1.0 - 0.18 * t)
    stick, _, _, _ = ribbon(gp, hwf)
    stick = K.U(stick, Point(*gp[0]).buffer(stick_w / 2, quad_segs=12))
    hx = x + hair_dx
    head = Polygon([(x - stick_w / 2 - 0.6, tip_y + 10), (x - stick_w / 2 + 0.4, tip_y - 2), (x + 2.0, tip_y - 6.5),
                    (hx + 3.0, tip_y + 12), (hx + 3.0, tip_y + 20), (x + stick_w / 2 - 0.5, tip_y + 22)])
    head = head.buffer(2.0, join_style=1).buffer(-2.0, join_style=1)
    frog = K.R(K.rrect(x - stick_w / 2 + 0.5, frog_y, hx + 7.0, frog_y + frog_h, 3.2))
    # the button's left side runs on from the frog's (and the stick's): one straight edge, no 1.7 px jog
    button = K.R(K.rrect(x - stick_w / 2, frog_y + frog_h, x + stick_w / 2 + 1.2, end_y, 2.6))
    slide = K.R(K.rrect(x + stick_w / 2 + 2.6, frog_y + 5.0, hx + 3.0, frog_y + frog_h - 5.0, 1.6))
    eye = Point(x + stick_w / 2 + 1.2 + (hx + 7.0 - x - stick_w / 2) / 2, frog_y + frog_h / 2).buffer(0.1)
    gold = shapely.union_all([head, frog, button])
    shape = shapely.union_all([stick, gold]).buffer(0.2).buffer(-0.2)
    eye_c = P((x + stick_w / 2 + hx + 7.0) / 2 - 1.0, frog_y + frog_h / 2)    # its ring ≥ 4.2 clear of the frog's edge
    eye_g = Point(*eye_c).buffer(3.15, quad_segs=16)
    fills = K.fill(stick.difference(gold), color) + K.fill(gold, GOLD) + K.fill(eye_g, RED)
    lines = K.outline(shape) + K.outline(frog) + K.outline(button) + K.outline(eye_g, FINE)
    hair_ln = LineString([(hx, frog_y - 0.2), (hx, tip_y + 20.4)])        # butts on the frog and the head's underside
    hair = K.line(K.D(hair_ln), MED, role="bow-hair")
    return K.Part(K.U(shape, hair_ln.buffer(MED / 2)), fills, lines + hair,
                  {"stick": stick, "hair_x": hx, "frog": frog})


# ---------------------------------------------------------------------------
# sash with the festoon, bead chain, sleeves
# ---------------------------------------------------------------------------
def sash(p_top, p_bot, half_w, clip_region, *, swag=46.0, sag=9.0, phase=0.0, bulb_d=6.3, wire_at=0.30,
         drop=4.2, keep_above=None):
    """The paper sash: a band ``half_w`` px either side of the line
    p_top → p_bot (through the card centre, so its 180° copy continues it
    across the band as one baldric), clipped to ``clip_region``. Along it the
    festoon string-light catenary (§G.28): FINE Aquifer swags between
    supports near the sash's upper edge, gold bulbs (Ø6.3, §G.28's 5–6 px)
    hung at each low point on a short drop and at the joins. Each bulb is
    kept whole or dropped (atomic), 4.2 px inside the sash's edges, and —
    with ``keep_above`` (the court clip's y less 4.2) — whole above the clip:
    the band never halves a bulb."""
    a, b = P(p_top), P(p_bot)
    u = (b - a) / np.hypot(*(b - a))
    n = np.array([u[1], -u[0]])            # screen-left of travel
    band = Polygon([a - u * 300 + n * half_w, b + u * 300 + n * half_w, b + u * 300 - n * half_w,
                    a - u * 300 - n * half_w])
    reg = biggest(band.intersection(clip_region))
    lines = K.outline(reg)
    inner = reg.buffer(-(MED / 2 + K.GAP + FINE / 2 + 0.1))
    L = float(np.hypot(*(b - a)))
    wire = C.Frag()
    bulbs = C.Frag()
    ks = np.arange(-8, int(L / swag) + 4)
    supports = [a + u * (phase + k * swag) + n * (half_w * wire_at) for k in ks]
    for i, (p0, p1) in enumerate(zip(supports[:-1], supports[1:])):
        m = (p0 + p1) / 2 - n * sag
        wire += K.line(K.arc3(p0, m, p1), FINE, role="wire")
        bl = m - n * (drop + bulb_d / 2)
        bulbs += K.atomic(K.dot(bl, bulb_d, GOLD, role="bulb")
                          + K.line(K.D(LineString([tuple(m), tuple(m - n * (drop + 0.8))])), FINE, role="socket"),
                          f"bulb{i}")
    for i, p in enumerate(supports):
        bulbs += K.atomic(K.dot(p, bulb_d, GOLD, role="bulb"), f"join{i}")
    wire = K.clip_in(wire, inner)
    keep = C.Frag()
    groups = {}
    for m in bulbs.marks:
        groups.setdefault(m.role.split("@")[1], []).append(m)
    zone = reg.buffer(-(MED / 2 + K.GAP_MARK + 0.2))
    if keep_above is not None:
        zone = zone.intersection(K.box(-1e4, -1e4, 1e4, keep_above))
    for key, ms in groups.items():
        g = shapely.union_all([K.R(K.G.from_skia(m.skia())) for m in ms])
        if zone.contains(g):
            keep += C.Frag(ms)
    return K.Part(reg, C.Frag(), lines + wire + keep, {"u": u, "n": n, "band": band})


def bead_chain(path_pts, d=7.4, gap=3.6, grow=None, keep=None, w=FINE):
    """Bubble-chain piping: solid gold beads with a FINE Aquifer contour
    (the only legal gold on red, §C.4) strung along ``path_pts`` with equal
    clear gaps; ``grow`` (d0, d1) grades them (bubbles grow as they rise)."""
    cv = K.G.Curve(np.asarray(path_pts, float))
    L = cv.length
    f = C.Frag()
    s = 0.0
    beads = []
    while True:
        dd = d if grow is None else grow[0] + (grow[1] - grow[0]) * min(s / max(L, 1), 1.0)
        if s + dd / 2 > L:
            break
        c = cv.at_s(s + dd / 2)
        beads.append((c, dd))
        s += dd + gap + w
    for i, (c, dd) in enumerate(beads):
        if keep is not None and not keep.contains(Point(*c).buffer(dd / 2 + w)):
            continue
        g = Point(*c).buffer(dd / 2, quad_segs=16)
        f += K.atomic(K.fill(g, GOLD, role="bead") + K.outline(g, w, role="bead"), f"bead{id(path_pts)}_{i}")
    return f


def ripple_slashes(groups, w=MED):
    """Ripple-arc slashes (§H.6 'sleeves slashed with ripple arcs'): groups
    of concentric arcs (§G.8, gaps ×1.3) — [(centre, radii, a0, a1), ...] —
    returned as strokes to KNOCK OUT of the jade (the shirt showing through)."""
    f = C.Frag()
    for centre, radii, a0, a1 in groups:
        for r in radii:
            f += C.stroke(C.arc_d(centre[0], centre[1], r, a0, a1), w, role="slash")
    return f


def puff_sleeve(pts, slashes, *, color=JADE, inset=None):
    """A puffed upper sleeve: region through ``pts`` (closed spline), filled
    ``color``, with ripple-arc slashes knocked out to paper, kept ≥ 3 px +
    the contour clear of its edge."""
    _, reg = spline_region(pts)
    ins = inset if inset is not None else (CON / 2 + 3.2 + MED / 2)
    sl = K.clip_in(ripple_slashes(slashes), reg.buffer(-ins))
    fill_d = C.knockout(K.D(reg), sl)
    return K.Part(reg, K.fill(fill_d, color), K.outline(reg), {"slashes": sl})


def plume_locks(guide_pts, *, n=4, ends=(1.0, 0.84, 0.69, 0.55), h_start=None, pitch=K.PITCH, root_taper=14.0,
                taper0=0.0, curl_r=4.4, curl_deg=95.0, tip_curl=(9.0, 200.0), smooth=4.0, inner=-1):
    """One long curling plume (§H.6) built as a bundle of §G.24 current
    lines — ``n`` offsets of ONE guide at a 7 px pitch — whose gold body is
    the union of the lines' own clearance (8.4 px: 4.2 paper + the CONTOUR
    edge), so every line fits by construction. Line 0 runs along the guide
    (the plume's long outer edge) to the tip and rolls into a volute
    (``tip_curl`` = radius, degrees); the others lie on the ``inner`` side
    (−1: the screen-right of travel, the concave side of a clockwise sweep)
    and end one after another at ``ends`` (fractions of the length), each
    rolling on into the vacated space into a Ø6.3 terminal: the plume's
    fronds combed into locks, its lower edge stepping in lock by lock to the
    curled tip. The lines spring together from the quill and fan to the
    7 px pitch within ``root_taper`` px — under the brooch."""
    _, gp = open_spline(guide_pts, h_start=h_start)
    cv = K.G.Curve(gp)
    L = cv.length
    lines, terms = [], []
    for k in range(n):
        o = inner * k * pitch
        dist = lambda t, o=o: o * np.clip(taper0 + (1 - taper0) * (t * L) / root_taper, 0, 1)
        off = cv.offset(dist, spacing=0.5)
        c2 = K.G.Curve(off)
        seg = c2.sub(0.0, min(ends[k], 1.0)).pts
        if k == 0 and tip_curl:
            seg = K._curl(seg, inner, tip_curl[0], tip_curl[1])
        elif curl_deg:
            seg = K._curl(seg, inner, curl_r, curl_deg)
        lines.append(seg)
        terms.append(seg[-1])
    geo = [LineString(l).buffer(K.EDGE_CON, quad_segs=16) for l in lines]
    geo += [Point(*t).buffer(K.TD / 2 + K.GAP_MARK + CON / 2 + 0.1, quad_segs=16) for t in terms]
    reg = shapely.union_all(geo)
    reg = biggest(reg.buffer(smooth, quad_segs=16).buffer(-smooth, quad_segs=16))
    f = C.Frag()
    for l, t in zip(lines, terms):
        f += C.stroke(C.polyline_d(l), FINE, role="current") + K.dot(t, K.TD, role="terminal")
    return K.Part(reg, K.fill(reg, GOLD), K.outline(reg) + f, {"guide": gp, "lines": lines})


def lock_bundle(guide_pts, *, n=4, ends=(1.0, 0.9, 0.8, 0.7), starts=None, inner=-1, pitch=K.PITCH,
                curl_r=4.6, curl_deg=(100.0,), smooth=4.0, filler=None, h_start=None, h_end=None):
    """A lock of hair as a bundle of §G.24 current lines: ``n`` offsets of
    ONE guide (line 0) stepping 7 px to the ``inner`` side, line k running
    from ``starts[k]`` to ``ends[k]`` (fractions of the guide) and rolling
    on toward ``inner`` into a Ø6.3 terminal. The gold body is the union of
    the lines' clearance (8.4 px) plus an optional ``filler`` region (the
    skull it covers), smoothed — so every line fits by construction."""
    _, gp = open_spline(guide_pts, h_start=h_start, h_end=h_end)
    cv = K.G.Curve(gp)
    lines, terms = [], []
    starts = starts or (0.0,) * n
    cds = list(curl_deg) + [curl_deg[-1]] * (n - len(curl_deg))
    for k in range(n):
        off = cv.offset(inner * k * pitch, spacing=0.5) if k else cv.resample(0.5)
        c2 = K.G.Curve(off)
        seg = c2.sub(starts[k], min(ends[k], 1.0)).pts
        if cds[k]:
            seg = K._curl(seg, inner, curl_r, cds[k])
        lines.append(seg)
        terms.append(seg[-1])
    geo = [LineString(l).buffer(K.EDGE_CON, quad_segs=16) for l in lines]
    geo += [Point(*t).buffer(K.TD / 2 + K.GAP_MARK + CON / 2 + 0.1, quad_segs=16) for t in terms]
    if filler is not None:
        geo.append(filler)
    reg = shapely.union_all(geo)
    reg = biggest(reg.buffer(smooth, quad_segs=16).buffer(-smooth, quad_segs=16))
    f = C.Frag()
    for l, t in zip(lines, terms):
        f += C.stroke(C.polyline_d(l), FINE, role="current") + K.dot(t, K.TD, role="terminal")
    # any line the filler/smoothing pushed too close to the edge is healed by the Scene
    return K.Part(reg, K.fill(reg, GOLD), K.outline(reg) + f, {"lines": lines})


# ---------------------------------------------------------------------------
# powdered patterns (small motifs in a half-drop grid, knocked out of a fill)
# ---------------------------------------------------------------------------
def powder(region, motif, pitch=(30.0, 28.0), origin=(0.0, 0.0), clear=3.0 + MED / 2, visible=None):
    """A half-drop grid of small motifs (``motif(x, y, i, j) -> Frag``), each
    kept whole only if it lies ``clear`` px inside ``region`` (and inside
    ``visible``, the part of the region no later object covers)."""
    reg = K.R(region)
    zone = reg if visible is None else reg.intersection(visible)
    zone = zone.buffer(-clear, quad_segs=12)
    x0, y0, x1, y1 = reg.bounds
    px, py = pitch
    ox, oy = origin
    f = C.Frag()
    for j in range(int(math.floor((y0 - oy) / py)) - 1, int(math.ceil((y1 - oy) / py)) + 2):
        off = px / 2 if j % 2 else 0.0
        for i in range(int(math.floor((x0 - ox - off) / px)) - 1, int(math.ceil((x1 - ox - off) / px)) + 2):
            x, y = ox + off + i * px, oy + j * py
            m = motif(x, y, i, j)
            if not m.marks:
                continue
            g = m.shape()
            if zone.contains(g):
                f += K.atomic(m, f"pw{i}_{j}")
    return f


def rising(x, y, i=0, j=0, sizes=(4.2, 6.3, 8.4), gap=3.4):
    """Three bubbles rising (smallest at the bottom), centred on (x, y)."""
    hs = [s / 2 for s in sizes]
    total = sum(sizes) + gap * (len(sizes) - 1)
    yy = y + total / 2
    f = C.Frag()
    for s in sizes:
        f += C.dot(x, yy - s / 2, s, color=INK, role="bubble")
        yy -= s + gap
    return f


def triad(x, y, i=0, j=0, sizes=(4.2, 6.3, 4.2), angle=-45.0):
    return C.bubble_triad(x, y, angle, sizes, style="dot")
