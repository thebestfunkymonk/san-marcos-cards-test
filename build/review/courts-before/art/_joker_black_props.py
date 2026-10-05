"""JOKER_BLACK props: the sagging festoon wire and its three gold bulbs, the
legs and the feet gripping the wire, the stolen gold coronet, the five call
rays and the caption block (brief §H.18, §F.4, §G.28; contract §3.3)."""
from __future__ import annotations

import math

import numpy as np
import shapely
import shapely.affinity as AF
from shapely.geometry import LineString, Point, Polygon

from inkkit import geom as G
from deck import tokens as T, frames as F
from deck import motifs as M

import _joker_black_pose as P

WIRE_W = T.MEDIUM


# ---------------------------------------------------------------------------
# placement (client correction 2026-09-24)
# ---------------------------------------------------------------------------
# Everything here and in _joker_black_pose is drafted in one frame; the whole
# figure (bird, coronet, rays, wire, bulbs) is moved onto the card by ONE
# rigid translation, FIG_SHIFT (JOKER_BLACK.build), so the drawing itself is
# unchanged. The wire's ends and the bulbs are drafted pre-offset by -dx so
# that on the card they keep their places, symmetric about x 375 (ends at
# 52 / 698); the kink travels with the feet.
FIG_SHIFT = (-8.4, 72.8)                   # (dx, dy) card px: bird + coronet centroid x 375.0; lowest ink 50.0 above the rule (= the Fool)
WIRE_END_X = (52.0, 698.0)                 # on the card (symmetric about 375)
BULB_CARD_X = (175.0, 560.0, 655.0)        # on the card


# ---------------------------------------------------------------------------
# the wire: two shallow circular arcs meeting in a kink under the feet
# ---------------------------------------------------------------------------
WIRE_L = np.array([WIRE_END_X[0] - FIG_SHIFT[0], 452.0])
WIRE_R = np.array([WIRE_END_X[1] - FIG_SHIFT[0], 452.0])
KINK = np.array([436.0, 502.0])            # the load point, between the feet
SAG_L, SAG_R = 10.0, 7.0                   # sagitta of each arm


def _arc_pts(p0, p1, sag, n=240):
    """Points of the circular arc p0 -> p1 hanging ``sag`` px below its chord."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    m = (p0 + p1) / 2
    ch = p1 - p0
    L = float(np.hypot(*ch))
    nrm = np.array([-ch[1], ch[0]]) / L
    if nrm[1] < 0:
        nrm = -nrm                              # downward normal
    R = (L * L / 4 + sag * sag) / (2 * sag)
    c = m + nrm * (sag - R)
    a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
    a1 = math.atan2(p1[1] - c[1], p1[0] - c[0])
    # go the short way (through the low side)
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    t = np.linspace(0, 1, n)
    a = a0 + da * t
    return np.column_stack([c[0] + R * np.cos(a), c[1] + R * np.sin(a)]), c, R


def wire_arms():
    left, _, _ = _arc_pts(WIRE_L, KINK, SAG_L)
    right, _, _ = _arc_pts(KINK, WIRE_R, SAG_R)
    return left, right


def wire_pts():
    left, right = wire_arms()
    return np.vstack([left, right[1:]])


def wire_y(x):
    pts = wire_pts()
    return float(np.interp(x, pts[:, 0], pts[:, 1]))


def wire_d():
    """The wire as exact SVG arcs."""
    _, _, lr = _arc_pts(WIRE_L, KINK, SAG_L)
    _, _, rr = _arc_pts(KINK, WIRE_R, SAG_R)
    return (f"M{WIRE_L[0]:.3f} {WIRE_L[1]:.3f}A{lr:.3f} {lr:.3f} 0 0 0 {KINK[0]:.3f} {KINK[1]:.3f}"
            f"A{rr:.3f} {rr:.3f} 0 0 0 {WIRE_R[0]:.3f} {WIRE_R[1]:.3f}")


def wire_frag():
    return M.stroke(wire_d(), WIRE_W, role="wire")


def wire_terminals():
    return M.terminal(*WIRE_L) + M.terminal(*WIRE_R)


# ---------------------------------------------------------------------------
# bulbs: drop, Aquifer socket, gold globe with a knocked-out glint
# ---------------------------------------------------------------------------
BULB_X = tuple(x - FIG_SHIFT[0] for x in BULB_CARD_X)      # drafting frame
DROP = 7.0
SOCK_W, SOCK_H = 9.0, 9.0
GLOBE_R = 9.5
NECK, NECK_W = 3.0, 6.4


def bulb(x):
    """-> (ink Frag, gold Frag). Hangs plumb from the wire at x: a MEDIUM
    drop, an Aquifer socket, and a gold globe whose neck tucks up under the
    socket (ink over gold: a trap, not a gap), with a knocked-out glint."""
    y0 = wire_y(x)
    ink = M.stroke(M.polyline_d([(x, y0), (x, y0 + DROP)]), T.MEDIUM, role="drop")
    sy = y0 + DROP - 1.0
    ink += M.fill(G.rect_d(x - SOCK_W / 2, sy, SOCK_W, SOCK_H, 1.6), color=T.INK, role="socket")
    cy = sy + SOCK_H + NECK + GLOBE_R - 1.0
    globe = Point(x, cy).buffer(GLOBE_R, quad_segs=48)
    neck = Polygon([(x - NECK_W / 2, sy + SOCK_H - 1.2), (x + NECK_W / 2, sy + SOCK_H - 1.2),
                    (x + NECK_W / 2 + 1.5, cy - GLOBE_R + 3.0), (x - NECK_W / 2 - 1.5, cy - GLOBE_R + 3.0)])
    glass = globe.union(neck).buffer(0.8, quad_segs=16).buffer(-0.8, quad_segs=16)
    glint = LineString([(x + 5.4 * math.cos(math.radians(a)), cy + 5.4 * math.sin(math.radians(a)))
                        for a in np.linspace(198, 258, 24)]).buffer(T.MEDIUM / 2, quad_segs=12)
    gold = M.fill(G.from_shape(glass.difference(glint)), color=T.FOIL, role="bulb")
    return ink, gold


# ---------------------------------------------------------------------------
# legs and feet (strutting along the wire: the near foot forward)
# ---------------------------------------------------------------------------
LEG_W = 7.2                # tarsus: constant width, part of the ink solid (a fill, not a stroke)
TOE_HW = 2.7               # toe half-width at its base (a filled part of the silhouette)


def _wire_heading(x):
    dx = 2.0
    return math.degrees(math.atan2(wire_y(x + dx) - wire_y(x - dx), 2 * dx))


def _toe(x0, direction, length, claw_r=4.6, claw_sweep=158.0):
    """One toe lying along the top of the wire from ``x0`` (+1 forward, -1
    back), its claw hooking down over the near face of the wire: a filled
    band tapering from TOE_HW to a sharp point along the claw."""
    h = _wire_heading(x0) + (0.0 if direction > 0 else 180.0)
    y0 = wire_y(x0) - WIRE_W / 2 - TOE_HW + 0.8      # the toe rests on the wire (overlapping it 0.8)
    t = M.Turtle(x0, y0, h).fd(length).arc(claw_r, claw_sweep * direction)
    pts = t.pts(0.3)
    cv = G.Curve(pts)
    L = cv.length
    s = np.linspace(0, L, 90)
    Pp = cv.at_s(s)
    tv = np.array([cv.tangent_s(v) for v in s])
    nv = np.column_stack([-tv[:, 1], tv[:, 0]])
    k = np.clip((s - length * 0.8) / (L - length * 0.8), 0, 1)
    hw = np.maximum(TOE_HW * (1.0 - 0.9 * k ** 1.1), 0.95)
    left = Pp + nv * hw[:, None]
    right = Pp - nv * hw[:, None]
    g = Polygon(np.vstack([left, right[::-1]])).buffer(0)
    return shapely.union_all([g, Point(*Pp[0]).buffer(TOE_HW, quad_segs=16), Point(*Pp[-1]).buffer(0.95, quad_segs=8)])


def legs():
    """-> (leg + foot FILL shapes, empty Frag -- kept for the old signature). The tarsi rise from inside
    the belly; each foot is a front toe and a hind toe lying along the top of
    the wire, the claws hooked over it; all of it joins the ink solid."""
    knee_n = P.BODY(-30.0, 40.0)
    knee_f = P.BODY(-48.0, 34.0)
    shapes = []
    for knee, x, fwd, back in ((knee_n, P.FOOT_N[0], 19.0, 12.0), (knee_f, P.FOOT_F[0], 17.0, 11.0)):
        ank = np.array([x, wire_y(x) - WIRE_W / 2 - TOE_HW + 0.8])
        shapes.append(LineString([knee, ank]).buffer(LEG_W / 2, quad_segs=16))
        shapes.append(Point(*ank).buffer(LEG_W / 2 + 0.6, quad_segs=16))     # the ankle joint
        shapes.append(_toe(x, +1, fwd))
        shapes.append(_toe(x, -1, back))
    return shapes, M.Frag()


# ---------------------------------------------------------------------------
# the stolen coronet, hanging from the bill tip, swinging
# ---------------------------------------------------------------------------
# Client correction 2026-09-24: the coronet hangs from the TIP of the bill by
# its band. The tip's point just catches the band's bottom rim beside its left
# end and lies over it -- ink over gold, a trap (the same join as the bulb
# necks tucked under their sockets), not a crossing -- so neither the bill nor
# the coronet is cut: band, all five points, the three ball finials and the
# three jewels read whole, and the bill keeps its sharp tip and its gape.
# (A 4.2-gapped over/under crossing has no room on this coronet: the jewels
# (each with >= 3 px of gold round it) and the plain end points leave no span
# of band wider than ~4.6 px, and a crossing needs the tip plus 2 x 4.2.)
# The swing is opened from 52 to 64 deg so the coronet hangs more below the
# tip than beside it (its centroid 48 deg off plumb, was 59) while its band
# still clears the bill.
COR_SWING = 64.0                     # caught mid-swing, hanging off the bill tip (clockwise, deg)
COR_HOOK = (-24.0, -1.0)             # coronet-frame point on the bill tip: ~1.5 px inside the band's
                                     # bottom rim, 3 px in from its left end
BAND_W, BAND_H, BAND_SAG = 27.0, 14.0, 3.0
POINTS = [(-23.0, 8.0, False), (-11.5, 15.0, True), (0.0, 20.0, True),
          (11.5, 15.0, True), (23.0, 8.0, False)]


def _band_y(x, y0):
    """y of a band edge (a circular arc through (-W, y0), (0, y0 + S), (W, y0))."""
    W, S = BAND_W, BAND_SAG
    R = (W * W + S * S) / (2 * S)
    return y0 + S - R + math.sqrt(R * R - x * x)


def _cor_local():
    """Coronet in its own frame: band bottom centre at (0, 0), y down.
    A circlet seen a little from above: both band edges are circular arcs
    bowing down by S at the middle; five points (the three tall ones with
    ball finials) and three lozenge jewels knocked out of the band."""
    W, H, S = BAND_W, BAND_H, BAND_SAG
    from deck.motifs.forms import scallop_arc
    bot = M.sample_d(scallop_arc((W, 0.0), (-W, 0.0), S), 0.3)[0][0]
    top = M.sample_d(scallop_arc((-W, -H), (W, -H), -S), 0.3)[0][0]
    band = Polygon(np.vstack([bot, top]))
    pts = []
    half = 4.6
    for (px, h, _ball) in POINTS:
        yb = _band_y(px, -H) + 0.8
        pts.append(Polygon([(px - half, yb), (px, yb - h - 2.0), (px + half, yb)]))
    body = shapely.union_all([band] + pts)
    # knockouts: three lozenge jewels on the band (>= 3 px of gold round each)
    jewels = []
    for jx in (-15.0, 0.0, 15.0):
        jy = _band_y(jx, -H / 2)
        jewels.append(Polygon([(jx - 4.4, jy), (jx, jy - 3.2), (jx + 4.4, jy), (jx, jy + 3.2)]))
    holes = shapely.union_all(jewels)
    balls = []
    for (px, h, ball) in POINTS:
        if ball:
            yb = _band_y(px, -H) + 0.8
            balls.append((px, yb - h - 2.0 - 1.8))       # the ball overlaps the point's apex
    return body, holes, balls


def coronet():
    """-> gold shape of the coronet (band, points, finials; jewels knocked
    out), hung by its band from the bill tip: COR_HOOK sits on the tip and
    the coronet is swung COR_SWING about it. Drawn whole; the caller gives it
    its finish (plumage.clean: the 1.3 px closing) and lays the bill over it."""
    body, holes, balls = _cor_local()
    g = body.difference(holes)
    g = shapely.union_all([g] + [Point(*b).buffer(T.TERMINAL_D / 2, quad_segs=24) for b in balls])
    hx, hy = COR_HOOK
    g = AF.translate(g, -hx, -hy)
    g = AF.rotate(g, COR_SWING, origin=(0, 0))
    return AF.translate(g, P.BILL_TIP[0], P.BILL_TIP[1])


# ---------------------------------------------------------------------------
# the call: five short FINE dash-rays behind the head
# ---------------------------------------------------------------------------
RAY_FAN = (-52.0, -26.0, 0.0, 26.0, 52.0)      # about the head's dorsal normal
RAY_GAP, RAY_LEN = 17.0, 16.0                  # clear of the head outline / dash length


def call_rays(head_sil=None):
    """Five short FINE dashes fanned about the back of the head, each starting
    RAY_GAP px clear of the head's outline along its own direction."""
    if head_sil is None:
        head_sil = G.to_shape(P.body_d()).union(G.to_shape(P.bill_d()))
    c = np.asarray(P.CALL_C, float)
    base = P.HEAD.head(-90.0)                       # the dorsal normal (screen deg)
    f = M.Frag()
    for da in RAY_FAN:
        a = math.radians(base + da)
        u = np.array([math.cos(a), math.sin(a)])
        ray = LineString([c, c + u * 300.0])
        hit = ray.intersection(head_sil.boundary)
        pts = [np.array(q.coords[0]) for q in getattr(hit, "geoms", [hit]) if not q.is_empty]
        r0 = max(float(np.hypot(*(q - c))) for q in pts) if pts else 60.0
        p0 = c + u * (r0 + RAY_GAP)
        p1 = c + u * (r0 + RAY_GAP + RAY_LEN)
        f += M.stroke(M.polyline_d([p0, p1]), T.FINE, role="ray")
    return f


# ---------------------------------------------------------------------------
# caption (§F.4, §J.2 verbatim)
# ---------------------------------------------------------------------------
TITLE = "THE TRICKSTER"
SUBLINE = "A NATIVE OF ELSEWHERE"


def caption():
    t = F.JOKER_TITLE
    d_t, _ = F.slab_line(TITLE, t["cap"], t["baseline"], t["tracking"])
    s = F.JOKER_SUBLINE
    d_s, bb_s = F.type_line(SUBLINE, s["cap"], s["baseline"], s["tracking"])
    em = F.em_rules_d(bb_s, s["cap"])
    f = M.fill(d_t, color=T.INK, role="title") + M.fill(open_counters(d_s), color=T.INK, role="subline")
    f += M.stroke(em, T.FINE, style="rule", role="em-rule")
    return f


COUNTER_MIN = 2.65               # micro-type counters >= 2.5 px (+ AA margin)
COUNTER_CLOSE = 2.0              # ...narrower ones (the cap-12 A) are closed instead


def open_counters(d: str, min_w: float = COUNTER_MIN, close_below: float = COUNTER_CLOSE) -> str:
    """Micro-type print correction for the cap-12 subline (as on the aces,
    art/_aces_common.py): Barlow Condensed SemiBold's counters at cap 12 are
    2.40-2.51 px (D, O, R) and 1.73 px (A); §I.12 wants >= 2.5 px of paper
    inside a solid. Counters between ``close_below`` and ``min_w`` are opened
    outward (mitred) to ``min_w`` -- 0.1 px a side, invisible; the A's
    counter cannot open to 2.5 px without thinning its legs below HAIRLINE,
    so it is closed, as the press would close it."""
    s = G.to_shape(d, tol=0.01)
    polys = list(getattr(s, "geoms", [s]))
    out = []
    for pg in polys:
        holes = []
        for ring in pg.interiors:
            hole = shapely.Polygon(ring)
            w = 2 * shapely.maximum_inscribed_circle(hole, 0.01).length
            if w < close_below:
                continue
            if w < min_w:
                hole = hole.buffer((min_w - w) / 2 + 0.02, join_style="mitre", mitre_limit=4)
            holes.append(hole)
        pg = shapely.Polygon(pg.exterior)
        for h in holes:
            pg = pg.difference(h)
        out.append(pg)
    return G.from_shape(shapely.union_all(out))
