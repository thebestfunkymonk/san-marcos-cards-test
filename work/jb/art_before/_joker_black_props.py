"""JOKER_BLACK props: the sagging festoon wire and its three gold bulbs, the
legs and feet gripping the wire, the stolen gold coronet, the five call rays
and the caption block (brief §H.18, §F.4, §G.28; contract §3.3)."""
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
# the wire: two shallow circular arcs meeting in a kink under the feet
# ---------------------------------------------------------------------------
WIRE_L = np.array([52.0, 476.0])
WIRE_R = np.array([698.0, 476.0])
KINK = np.array([472.0, 514.0])            # the load point, between the feet
SAG_L, SAG_R = 9.0, 6.0                    # sagitta of each arm


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
BULB_X = (105.0, 375.0, 645.0)
DROP = 7.0
SOCK_W, SOCK_H = 9.0, 9.0
GLOBE_R = 9.5


def bulb(x):
    """-> (ink Frag, gold Frag). Hangs plumb from the wire at x."""
    y0 = wire_y(x)
    ink = M.stroke(M.polyline_d([(x, y0), (x, y0 + DROP)]), T.MEDIUM, role="drop")
    sy = y0 + DROP - 1.0
    ink += M.fill(G.rect_d(x - SOCK_W / 2, sy, SOCK_W, SOCK_H, 1.6), color=T.INK, role="socket")
    cy = sy + SOCK_H + 3.0 + GLOBE_R                  # 3 px registration gap socket -> glass
    globe = Point(x, cy).buffer(GLOBE_R, quad_segs=48)
    glint = LineString([(x + 5.2 * math.cos(math.radians(a)), cy + 5.2 * math.sin(math.radians(a)))
                        for a in np.linspace(196, 262, 24)]).buffer(T.MEDIUM / 2, quad_segs=12)
    gold = M.fill(G.from_shape(globe.difference(glint)), color=T.FOIL, role="bulb")
    return ink, gold


# ---------------------------------------------------------------------------
# legs and feet (strutting: the near foot forward)
# ---------------------------------------------------------------------------
LEG_W = 7.4                # tarsus: constant width, part of the ink solid (a fill, not a stroke)
TOE_W = T.MEDIUM


def _ankle(x):
    """The foot sits ON the wire: the toe centreline 1.2 px above the wire's."""
    return np.array([x, wire_y(x) - 1.2])


def _wire_heading(x):
    dx = 2.0
    return math.degrees(math.atan2(wire_y(x + dx) - wire_y(x - dx), 2 * dx))


def legs():
    """-> (leg FILL shapes, toe Frag). The tarsi (and the feathered tibiae)
    are unioned into the ink solid; the toes are MEDIUM strokes lying on the
    wire, claws hooked round it."""
    knee_n = np.array([474.0, 418.0])
    knee_f = np.array([458.0, 422.0])
    ank_n = _ankle(P.FOOT_N[0])
    ank_f = _ankle(P.FOOT_F[0])
    shapes = []
    for a, b in ((knee_n, ank_n), (knee_f, ank_f)):
        shapes.append(LineString([a, b]).buffer(LEG_W / 2, quad_segs=16))
        # feathered tibia ('trousers'): a short capsule where the leg leaves the belly
        u = (b - a) / np.hypot(*(b - a))
        shapes.append(LineString([a - u * 14.0, a + u * 6.0]).buffer(5.6, quad_segs=16))
    return shapes, foot(ank_n) + foot(ank_f)


def foot(ank):
    """The toes lie along the top of the wire (merging with it) and their
    claws hook down round it: the front toe reaching forward, the hind toe
    back. MEDIUM tangent-arc strokes."""
    x, y = ank
    h = _wire_heading(x)
    f = M.Frag()
    t = M.Turtle(x, y, h).fd(16.0).arc(3.8, 120.0)
    f += M.stroke(t.d(), TOE_W, role="toe")
    t = M.Turtle(x, y, h + 180.0).fd(11.0).arc(3.6, -120.0)
    f += M.stroke(t.d(), TOE_W, role="toe")
    return f


# ---------------------------------------------------------------------------
# the stolen coronet, hooked on the bill tip, swinging
# ---------------------------------------------------------------------------
COR_SWING = 34.0                     # caught mid-swing, hanging off the bill tip (clockwise, deg)
COR_PIVOT = (-22.0, -6.0)            # the bill tip passes through the band's left end (coronet frame)
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


def _cor_place(g):
    px, py = COR_PIVOT
    g = AF.translate(g, -px, -py)
    g = AF.rotate(g, COR_SWING, origin=(0, 0))
    return AF.translate(g, P.BILL_TIP[0], P.BILL_TIP[1])


def coronet():
    """-> gold shape of the coronet (band, points, finials; jewels knocked
    out), hung on the bill tip. It hangs BEHIND the bill: the caller cuts it
    where the bill passes in front (interlace gap)."""
    body, holes, balls = _cor_local()
    g = body.difference(holes)
    g = shapely.union_all([g] + [Point(*b).buffer(T.TERMINAL_D / 2, quad_segs=24) for b in balls])
    return _cor_place(g)


# ---------------------------------------------------------------------------
# the call: five short FINE dash-rays behind the head
# ---------------------------------------------------------------------------
RAY_ANGLES = (150.0, 175.0, 200.0, 225.0, 250.0)
RAY_R = (62.0, 78.0)


def call_rays():
    cx, cy = P.CALL_C
    f = M.Frag()
    for a in RAY_ANGLES:
        u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        p0 = np.array([cx, cy]) + u * RAY_R[0]
        p1 = np.array([cx, cy]) + u * RAY_R[1]
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
    f = M.fill(d_t, color=T.INK, role="title") + M.fill(d_s, color=T.INK, role="subline")
    f += M.stroke(em, T.FINE, style="rule", role="em-rule")
    return f
