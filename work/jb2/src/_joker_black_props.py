"""JOKER_BLACK props: the sagging festoon wire and its three gold bulbs, the
legs and the feet clasping the wire, the stolen gold coronet, the five call
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
from deck.motifs import forms

import _joker_black_pose as P

WIRE_W = T.MEDIUM


# ---------------------------------------------------------------------------
# the wire: two shallow circular arcs meeting in a kink under the feet
# ---------------------------------------------------------------------------
WIRE_L = np.array([52.0, 428.0])
WIRE_R = np.array([698.0, 428.0])
KINK = np.array([391.0, 470.0])            # the load point, under the feet
SAG_L, SAG_R = 9.0, 8.0                    # sagitta of each arm


def _arc_geom(p0, p1, sag):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    m = (p0 + p1) / 2
    ch = p1 - p0
    L = float(np.hypot(*ch))
    nrm = np.array([-ch[1], ch[0]]) / L
    if nrm[1] < 0:
        nrm = -nrm
    R = (L * L / 4 + sag * sag) / (2 * sag)
    c = m + nrm * (sag - R)
    return c, R


def _arc_pts(p0, p1, sag, n=300):
    c, R = _arc_geom(p0, p1, sag)
    a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
    a1 = math.atan2(p1[1] - c[1], p1[0] - c[0])
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    t = np.linspace(0, 1, n)
    a = a0 + da * t
    return np.column_stack([c[0] + R * np.cos(a), c[1] + R * np.sin(a)])


def wire_pts():
    left = _arc_pts(WIRE_L, KINK, SAG_L)
    right = _arc_pts(KINK, WIRE_R, SAG_R)
    return np.vstack([left, right[1:]])


def wire_y(x):
    pts = wire_pts()
    return float(np.interp(x, pts[:, 0], pts[:, 1]))


def wire_heading(x, dx=2.0):
    return math.degrees(math.atan2(wire_y(x + dx) - wire_y(x - dx), 2 * dx))


def wire_d():
    _, lr = _arc_geom(WIRE_L, KINK, SAG_L)
    _, rr = _arc_geom(KINK, WIRE_R, SAG_R)
    return (f"M{WIRE_L[0]:.3f} {WIRE_L[1]:.3f}A{lr:.3f} {lr:.3f} 0 0 0 {KINK[0]:.3f} {KINK[1]:.3f}"
            f"A{rr:.3f} {rr:.3f} 0 0 0 {WIRE_R[0]:.3f} {WIRE_R[1]:.3f}")


def wire_frag():
    return M.stroke(wire_d(), WIRE_W, role="wire")


def wire_terminals():
    return M.terminal(*WIRE_L) + M.terminal(*WIRE_R)


# ---------------------------------------------------------------------------
# bulbs: a drop, an Aquifer socket, a gold globe with a knocked-out glint
# ---------------------------------------------------------------------------
BULB_X = (150.0, 520.0, 630.0)
DROP = 7.0
SOCK_W, SOCK_H = 9.0, 9.0
GLOBE_R = 9.5
NECK_W = 6.4


def bulb(x):
    """-> (ink Frag, gold Frag)."""
    y0 = wire_y(x)
    ink = M.stroke(M.polyline_d([(x, y0), (x, y0 + DROP)]), T.MEDIUM, role="drop")
    sy = y0 + DROP - 1.0
    ink += M.fill(G.rect_d(x - SOCK_W / 2, sy, SOCK_W, SOCK_H, 1.6), color=T.INK, role="socket")
    cy = sy + SOCK_H + 3.0 + GLOBE_R - 1.0
    globe = Point(x, cy).buffer(GLOBE_R, quad_segs=48)
    neck = Polygon([(x - NECK_W / 2, sy + SOCK_H - 1.2), (x + NECK_W / 2, sy + SOCK_H - 1.2),
                    (x + NECK_W / 2 + 1.5, cy - GLOBE_R + 3.0), (x - NECK_W / 2 - 1.5, cy - GLOBE_R + 3.0)])
    glass = globe.union(neck).buffer(0.8, quad_segs=16).buffer(-0.8, quad_segs=16)
    glint = LineString([(x + 5.4 * math.cos(math.radians(a)), cy + 5.4 * math.sin(math.radians(a)))
                        for a in np.linspace(198, 258, 24)]).buffer(T.MEDIUM / 2, quad_segs=12)
    gold = M.fill(G.from_shape(glass.difference(glint)), color=T.FOIL, role="bulb")
    return ink, gold


# ---------------------------------------------------------------------------
# legs and feet
# ---------------------------------------------------------------------------
LEG_W = T.CONTOUR                 # tarsus: a band of the CONTOUR token's width (part of the ink solid)
TOE_W = T.RULE                    # toes: bands of the RULE token's width, the claws tapering to a point

# (hip inside the belly, ankle x on the wire, forward toe length, hind toe length)
LEGS = [((389.0, 432.0), 397.0, 13.0, 9.0),     # near leg
        ((374.0, 440.0), 379.0, 11.0, 8.0)]     # far leg


def _toe(x0, y0, direction, length, claw_r=4.2, sweep=150.0):
    """A toe lying on the wire from (x0, y0) forward (+1) or back (-1),
    ending in a claw curling down over the near face of the wire."""
    h = wire_heading(x0) + (0.0 if direction > 0 else 180.0)
    t = M.Turtle(x0, y0, h).fd(length).arc(claw_r, sweep * direction)
    pts = t.pts(0.25)[0]
    cv = G.Curve(pts)
    s = np.linspace(0, cv.length, 120)
    Pp = cv.at_s(s)
    tv = np.array([cv.tangent_s(v) for v in s])
    nv = np.column_stack([-tv[:, 1], tv[:, 0]])
    k = np.clip((s - length * 0.75) / (cv.length - length * 0.75), 0, 1)
    hw = TOE_W / 2 * (1.0 - 0.82 * k)
    ring = np.vstack([Pp + nv * hw[:, None], (Pp - nv * hw[:, None])[::-1]])
    g = Polygon(ring).buffer(0)
    return shapely.union_all([g, Point(*Pp[0]).buffer(TOE_W / 2, quad_segs=16)])


def legs():
    """-> list of FILL shapes (tarsi, ankles, toes) joining the ink solid."""
    shapes = []
    for hip, x, fwd, back in LEGS:
        y_top = wire_y(x) - WIRE_W / 2 - TOE_W / 2 + 0.6
        ank = np.array([x, y_top])
        shapes.append(LineString([hip, ank]).buffer(LEG_W / 2, quad_segs=16))
        shapes.append(_toe(x, y_top, +1, fwd))
        shapes.append(_toe(x, y_top, -1, back))
    return shapes


def claw_zones():
    """Where the claws cross the wire (for the interlace break)."""
    return shapely.union_all(legs())


# ---------------------------------------------------------------------------
# the stolen coronet
# ---------------------------------------------------------------------------
COR_W, COR_BAND, COR_SAG = 44.0, 10.5, 4.0     # band width, band height, band curvature (seen from a little above)
COR_POINTS = [(-0.5, 11.0), (-0.25, 15.0), (0.0, 20.0), (0.25, 15.0), (0.5, 11.0)]   # (x/W, height)
COR_PEARL = 6.3
COR_TILT = 18.0                                 # hanging: rotated clockwise about the grip
COR_GRIP = np.array([-0.5, -0.5])               # grip on the band (x/W, y/BAND) -- its left end
COR_JEWELS = (-0.25, 0.0, 0.25)


def _band_y(x, y0):
    W, S = COR_W / 2, COR_SAG
    R = (W * W + S * S) / (2 * S)
    return y0 + S - R + math.sqrt(max(R * R - x * x, 0.0))


def coronet_local():
    """Coronet in its own frame: band bottom-centre at (0, 0), y down.
    -> (gold body with the jewels knocked out, pearl centres)."""
    W, H = COR_W / 2, COR_BAND
    xs = np.linspace(-W, W, 80)
    bot = [(x, _band_y(x, 0.0)) for x in xs]
    top = [(x, _band_y(x, -H)) for x in xs[::-1]]
    band = Polygon(bot + top)
    pts, pearls = [], []
    for fx, h in COR_POINTS:
        px = fx * COR_W
        half = 5.2 if abs(fx) < 0.49 else 3.6
        px_in = px if abs(fx) < 0.49 else px - np.sign(fx) * 3.0
        yb = _band_y(px_in, -H) + 0.8
        apex = (px_in, yb - h)
        pts.append(Polygon([(px_in - half, yb), apex, (px_in + half, yb)]))
        pearls.append((apex[0], apex[1] - COR_PEARL / 2 + 1.2))
    body = shapely.union_all([band] + pts + [Point(*q).buffer(COR_PEARL / 2, quad_segs=24) for q in pearls])
    holes = []
    for fx in COR_JEWELS:
        jx = fx * COR_W
        jy = _band_y(jx, -H / 2)
        holes.append(Point(jx, jy).buffer(2.1, quad_segs=16))
    return body.difference(shapely.union_all(holes)), pearls


def coronet():
    body, _ = coronet_local()
    gx, gy = COR_GRIP[0] * COR_W, _band_y(COR_GRIP[0] * COR_W, COR_GRIP[1] * COR_BAND)
    g = AF.translate(body, -gx, -gy)
    g = AF.rotate(g, COR_TILT, origin=(0, 0))
    return AF.translate(g, P.BILL_TIP[0] + COR_OFF[0], P.BILL_TIP[1] + COR_OFF[1])


COR_OFF = (1.5, 6.0)                # the grip point relative to the bill tip


# ---------------------------------------------------------------------------
# the call: five short FINE dash-rays fanned behind the head
# ---------------------------------------------------------------------------
RAY_C = None                        # centre (defaults to the head centre)
RAY_R0, RAY_LEN = 30.0, 13.0
RAY_ANGLES = (150.0, 172.0, 194.0, 216.0, 238.0)


def call_rays():
    c = np.asarray(RAY_C if RAY_C is not None else P.HEAD(-20.0, 1.0), float)
    f = M.Frag()
    for a in RAY_ANGLES:
        u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        f += M.stroke(M.polyline_d([c + u * RAY_R0, c + u * (RAY_R0 + RAY_LEN)]), T.FINE, role="ray")
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


COUNTER_MIN = 2.65
COUNTER_CLOSE = 2.0


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
