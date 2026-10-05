"""Playing-card structure: suit pips, corner indices, standard pip layouts,
court and ace frames.

Geometry 'headwaters' follows the HEADWATERS creative brief §E.1 (pips built
only from circles and straight lines; u = the spade's width):

* heart 1.00u × 0.92u — lobes r 0.26u at (±0.24u, 0.26u), straight tangents
  to the point, a sharp 0.16u cleft (drawn at 1.04× for optical balance)
* spade 1.00u × 1.10u — the heart construction point-up (0.80u tall body),
  a stem tapering 0.07u → 0.20u, and the two-step 'fault-step' plinth
* club 1.04u × 1.04u — three circles r 0.245u, a filled triangular core, the
  same stem and plinth
* diamond 0.80u × 1.12u — a rhombus whose sides bow inward by a 3 % sagitta

Geometry 'classic' gives traditional Bézier pips. All shapes are clockwise
FILL outlines centred on their bounding-box centre (pips are placed by the
centre of their bounding box).

    from inkkit import suits
    d = suits.pip("spade", 375, 525, 116)                  # field pip
    d = suits.pip("heart", 375, 470, 280, style="half")    # ace, half-hatched
    idx = suits.index("Q", "heart")                        # both corners
    for x, y, rot in suits.pip_layout(7): ...
"""
from __future__ import annotations

import math

import numpy as np
import shapely

from . import geom as G
from . import tokens as T

__all__ = ["SUITS", "RANKS", "suit_name", "pip_shape", "pip_size", "pip", "pip_layout",
           "index", "court_frame", "ace_keyline"]

SUITS = ("spade", "heart", "diamond", "club")
RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
_ALIAS = {"s": "spade", "spades": "spade", "♠": "spade", "h": "heart", "hearts": "heart", "♥": "heart",
          "d": "diamond", "diamonds": "diamond", "♦": "diamond", "c": "club", "clubs": "club", "♣": "club"}
_STYLES = ("solid", "outline", "half", "inline", "engraved")


def suit_name(s: str) -> str:
    """'S' / 'spades' / '♠' / 'spade' -> 'spade' (ValueError otherwise)."""
    k = str(s).strip().lower()
    k = _ALIAS.get(k, k)
    if k not in SUITS:
        raise ValueError(f"unknown suit {s!r}; use one of {SUITS} (or S/H/D/C)")
    return k


# =============================================================================
# silhouettes (unit u = 1, top-left origin, y down), as shapely
# =============================================================================
def _disc(cx, cy, r):
    return shapely.Point(cx, cy).buffer(r, quad_segs=64)


def _tangent_point(P, C, r, side):
    """Tangent point on circle (C, r) seen from P, on ``side`` (+1 / -1)."""
    P = np.asarray(P, float); C = np.asarray(C, float)
    d = C - P
    L = float(np.hypot(*d))
    a = math.atan2(d[1], d[0])
    b = math.asin(min(1.0, r / L))
    t = a + side * b
    k = math.sqrt(max(L * L - r * r, 0.0))
    return P + k * np.array([math.cos(t), math.sin(t)])


def _heart_body(apex_up: bool, r=0.26, cx=0.24, depth=0.66):
    """Two lobes and straight tangents to the point. Point at y = 0.26+depth
    (point down) — flipped when ``apex_up``."""
    CL, CR = (-cx, r), (cx, r)
    P = (0.0, r + depth)
    # outer tangent points (farthest from the axis)
    tl = min((_tangent_point(P, CL, r, sg) for sg in (1, -1)), key=lambda q: q[0])
    tr = max((_tangent_point(P, CR, r, sg) for sg in (1, -1)), key=lambda q: q[0])
    core = shapely.MultiPoint([P, tr, CR, CL, tl]).convex_hull
    body = shapely.union_all([_disc(*CL, r), _disc(*CR, r), core])
    if apex_up:
        body = shapely.affinity.scale(body, 1, -1, origin=(0, 0))
        body = shapely.affinity.translate(body, 0, r + depth)
    return body


def _plinth(y_top, step=0.05):
    upper = shapely.box(-0.13, y_top, 0.13, y_top + step)
    lower = shapely.box(-0.18, y_top + step, 0.18, y_top + 2 * step)
    return shapely.union_all([upper, lower])


def _stem(y0, y1, w0=0.07, w1=0.20):
    return shapely.Polygon([(-w0 / 2, y0), (w0 / 2, y0), (w1 / 2, y1), (-w1 / 2, y1)])


def _bowed_rhombus(w=0.80, h=1.12, sag=0.03, n=48):
    V = [np.array([0.0, 0.0]), np.array([w / 2, h / 2]), np.array([0.0, h]), np.array([-w / 2, h / 2])]
    pts = []
    for a, b in zip(V, V[1:] + V[:1]):
        L = float(np.hypot(*(b - a)))
        s = sag * L
        R = (L * L / 4 + s * s) / (2 * s)
        mid = (a + b) / 2
        dvec = (b - a) / L
        inward = np.array([dvec[1], -dvec[0]])
        if np.dot(np.array([0.0, h / 2]) - mid, inward) < 0:
            inward = -inward                            # unit normal toward the centre
        # the side bows toward the centre, so the circle's centre lies outside
        C = mid - inward * (R - s)
        a0 = math.atan2(a[1] - C[1], a[0] - C[0])
        a1 = math.atan2(b[1] - C[1], b[0] - C[0])
        da = math.atan2(math.sin(a1 - a0), math.cos(a1 - a0))
        t = np.linspace(0, 1, n, endpoint=False)
        pts.append(np.column_stack([C[0] + R * np.cos(a0 + da * t), C[1] + R * np.sin(a0 + da * t)]))
    return shapely.Polygon(np.vstack(pts)).buffer(0)


def _headwaters(suit):
    if suit == "heart":
        return _heart_body(False)
    if suit == "spade":
        body = _heart_body(True, depth=0.80 - 2 * 0.26 + 0.26)   # 0.80 tall body, apex at y=0
        stem = _stem(0.62, 1.00)
        return shapely.union_all([body, stem, _plinth(1.00)])
    if suit == "club":
        r = 0.245
        C = [(0.0, r), (-0.275, 0.53), (0.275, 0.53)]
        lobes = [_disc(x, y, r) for x, y in C]
        core = shapely.Polygon(C)
        # the stem starts hidden inside the core (brief: 0.07u at y 0.55u)
        stem = shapely.union_all([_stem(0.55, 0.94), shapely.box(-0.035, 0.45, 0.035, 0.56)])
        return shapely.union_all(lobes + [core, stem, _plinth(0.94)])
    return _bowed_rhombus()


def _classic(suit):
    def bez(cmds):
        # build at 1000x so flattening stays smooth, then scale back to unit
        big = [(c[0], *[v * 1000 for v in c[1:]]) for c in cmds]
        return shapely.affinity.scale(G.to_shape(G.cmds_to_d(big), tol=0.05), 1e-3, 1e-3, origin=(0, 0))
    if suit == "heart":
        return bez([("M", 0, 0.24), ("C", 0.05, 0.02, 0.5, -0.04, 0.5, 0.3),
                    ("C", 0.5, 0.55, 0.12, 0.72, 0, 0.92), ("C", -0.12, 0.72, -0.5, 0.55, -0.5, 0.3),
                    ("C", -0.5, -0.04, -0.05, 0.02, 0, 0.24), ("Z",)])
    if suit == "spade":
        body = bez([("M", 0, 0.0), ("C", 0.14, 0.2, 0.5, 0.32, 0.5, 0.58),
                    ("C", 0.5, 0.8, 0.2, 0.86, 0.04, 0.7), ("L", -0.04, 0.7),
                    ("C", -0.2, 0.86, -0.5, 0.8, -0.5, 0.58), ("C", -0.5, 0.32, -0.14, 0.2, 0, 0.0), ("Z",)])
        stem = bez([("M", -0.03, 0.66), ("L", 0.03, 0.66), ("C", 0.04, 0.85, 0.1, 0.98, 0.2, 1.1),
                    ("L", -0.2, 1.1), ("C", -0.1, 0.98, -0.04, 0.85, -0.03, 0.66), ("Z",)])
        return shapely.union_all([body, stem])
    if suit == "club":
        r = 0.25
        lobes = [_disc(0, r, r), _disc(-0.27, 0.54, r), _disc(0.27, 0.54, r)]
        core = shapely.Polygon([(0, r), (-0.27, 0.54), (0.27, 0.54)])
        stem = bez([("M", -0.04, 0.45), ("L", 0.04, 0.45), ("C", 0.05, 0.8, 0.1, 0.94, 0.2, 1.04),
                    ("L", -0.2, 1.04), ("C", -0.1, 0.94, -0.05, 0.8, -0.04, 0.45), ("Z",)])
        return shapely.union_all(lobes + [core, stem])
    return shapely.Polygon([(0, 0), (0.4, 0.56), (0, 1.12), (-0.4, 0.56)])


def pip_shape(suit, u: float = 100.0, *, geometry: str = "headwaters", optical: bool = True) -> str:
    """Pip silhouette of unit ``u`` centred on its bounding-box centre at the
    origin, upright. Hearts are drawn at 1.04× when ``optical``. -> FILL d."""
    suit = suit_name(suit)
    if geometry not in ("headwaters", "classic"):
        raise ValueError("geometry must be 'headwaters' or 'classic'")
    if not u > 0:
        raise ValueError("pip: u must be > 0")
    gm = _headwaters(suit) if geometry == "headwaters" else _classic(suit)
    k = u * (1.04 if (suit == "heart" and optical) else 1.0)
    x0, y0, x1, y1 = gm.bounds
    gm = shapely.affinity.affine_transform(gm, [k, 0, 0, k, -k * (x0 + x1) / 2, -k * (y0 + y1) / 2])
    return G.from_shape(gm)


def pip_size(suit, u: float = 100.0, *, geometry: str = "headwaters", optical: bool = True):
    """(width, height) of a pip of unit ``u``."""
    x0, y0, x1, y1 = G.bbox(pip_shape(suit, u, geometry=geometry, optical=optical))
    return x1 - x0, y1 - y0


def pip(suit, cx: float, cy: float, u: float = 62.0, *, rot: float = 0.0, style: str = "solid",
        lw: float | None = None, geometry: str = "headwaters", optical: bool = True,
        hatch_spacing: float = T.HATCH_PITCH, hatch_angle: float | None = None,
        inline: float | None = None) -> str:
    """A pip centred (bounding box) on (cx, cy), rotated ``rot`` degrees.

    style 'solid'     the silhouette
          'outline'   silhouette outlined at ``lw`` (default FINE 2.1)
          'half'      outline + FINE hatch in exactly one half (split on the
                      pip's vertical axis) — the Monarchs/Drifters treatment
          'inline'    solid with an inset knockout line (``inline`` px from the
                      edge, drawn MEDIUM 3.1 wide) — the brief's ace treatment
          'engraved'  outline + bevel-shaded tonal hatching
    -> FILL d."""
    if style not in _STYLES:
        raise ValueError(f"pip style must be one of {_STYLES}, not {style!r}")
    suit = suit_name(suit)
    if hatch_angle is None:   # keep hatch well away from the edge directions
        hatch_angle = 0.0 if suit == "diamond" else 45.0
    d = pip_shape(suit, u, geometry=geometry, optical=optical)
    w = lw if lw is not None else (T.MEDIUM if style == "inline" else T.FINE)
    if style == "solid":
        out = d
    elif style == "outline":
        out = G.outline(d, w, join="miter")
    elif style == "half":
        from . import hatch as H
        body = G.outline(d, w, join="miter")
        x0, y0, x1, y1 = G.bbox(d)
        axis = np.array([[0.0, y0 - 5], [0.0, y1 + 5]])
        hh = H.half(d, axis, side=-1, angle=hatch_angle, spacing=hatch_spacing, width=w, cap="butt",
                    min_len=hatch_spacing)
        out = G.union(body, hh) if hh else body
    elif style == "inline":
        ins = inline if inline is not None else max(0.035 * u, w * 1.4)
        ring = G.offset(d, -ins, join="miter")
        out = G.difference(d, G.outline(ring, w, join="miter")) if ring else d
    else:
        from . import hatch as H
        body = G.outline(d, w, join="miter")
        tone = H.bevel_tone(d, -135, width=0.18 * u, base=0.12, strength=0.9)
        inner = G.offset(d, -w * 0.5)
        eng = H.tonal(inner, tone, angle=hatch_angle, spacing=max(3.0, 0.045 * u), wmax=max(2.0, 0.03 * u),
                      edge_gap=w * 0.6) if inner else ""
        out = body + eng
    if rot:
        out = G.rotate(out, rot)
    return G.translate(out, cx, cy)


def pip_layout(rank, *, cols=(222.0, 375.0, 528.0), rows=(198.0, 852.0), center=(375.0, 525.0)):
    """Standard pip centres for ranks A–10 as [(x, y, rotated), ...]; pips
    centred below the card centre are rotated 180° (brief §E.2 defaults:
    columns 222/375/528, rows 198–852)."""
    r = str(rank).upper()
    L, C, R = cols
    T_, B = rows
    mid = center[1]
    q = [T_ + (B - T_) * k / 3 for k in range(4)]          # four-row columns
    lay = {
        "A": [(C, mid)], "1": [(C, mid)],
        "2": [(C, T_), (C, B)],
        "3": [(C, T_), (C, mid), (C, B)],
        "4": [(L, T_), (R, T_), (L, B), (R, B)],
        "5": [(L, T_), (R, T_), (L, B), (R, B), (C, mid)],
        "6": [(x, y) for y in (T_, mid, B) for x in (L, R)],
        "7": [(x, y) for y in (T_, mid, B) for x in (L, R)] + [(C, (T_ + mid) / 2)],
        "8": [(x, y) for y in (T_, mid, B) for x in (L, R)] + [(C, (T_ + mid) / 2), (C, (mid + B) / 2)],
        "9": [(x, y) for y in q for x in (L, R)] + [(C, mid)],
        "10": [(x, y) for y in q for x in (L, R)] + [(C, (q[0] + q[1]) / 2), (C, (q[2] + q[3]) / 2)],
    }
    if r not in lay:
        raise ValueError(f"pip_layout: rank must be A or 2–10, not {rank!r}")
    return [(float(x), float(y), bool(y > mid + 1e-9)) for x, y in lay[r]]


def index(rank, suit, *, font: str = "BarlowCondensed-SemiBold", size: float = 137.14,
          axis_x: float = 84.0, baseline: float = 142.0, pip_u: float = 62.0,
          pip_top: float = 164.0, tracking: float | None = None, variations=None,
          both: bool = True, geometry: str = "headwaters", center=(375.0, 525.0)) -> dict:
    """Corner index: rank glyph centred on ``axis_x`` sitting on ``baseline``,
    with the suit pip (unit ``pip_u``, top at ``pip_top``) below it; ``both``
    adds the rotate(180) copy for the opposite corner (brief §D.1 defaults).
    Returns {'rank': d, 'pip': d, 'd': everything}."""
    from .typeset import text_to_path
    suit = suit_name(suit)
    r = str(rank).upper()
    if r not in RANKS and r != "JOKER":
        raise ValueError(f"index: rank must be one of {RANKS}, not {rank!r}")
    tr = tracking if tracking is not None else (-20.0 if r == "10" else 0.0)
    rd, _, _ = text_to_path(font, r, size, axis_x, baseline, anchor="middle", tracking=tr,
                            variations=variations)
    x0, y0, x1, y1 = G.bbox(rd)
    rd = G.translate(rd, axis_x - (x0 + x1) / 2, 0)       # optical centring on the glyph box
    w, h = pip_size(suit, pip_u, geometry=geometry)
    pd = pip(suit, axis_x, pip_top + h / 2, pip_u, geometry=geometry)
    d = rd + pd
    if both:
        d += G.rotate180(rd + pd, *center)
    return {"rank": rd, "pip": pd, "d": d}


def court_frame(x0: float = 128.0, y0: float = 44.0, x1: float = 622.0, y1: float = 1006.0, *,
                chamfer: float = 18.0, inner: float = 7.0, rule: float = T.RULE,
                fine: float = T.FINE, band=(511.0, 539.0)) -> dict:
    """Court frame (brief §F.1): an outer ``rule`` on the rectangle with 45°
    chamfered corners (miter joins) and an inner ``fine`` rule ``inner`` px
    inside it following the chamfers; the divider band rules at ``band``.
    Returns {'outer', 'inner', 'band', 'window'} (FILL d's; window =
    (x0, y0, x1, y1) of the drawable top half)."""
    c = chamfer
    ring = np.array([(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1),
                     (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)])
    pg = shapely.Polygon(ring)
    outer = G.outline([(ring, True)], rule, join="miter", miter_limit=4)
    in_pg = pg.buffer(-inner, join_style="mitre", mitre_limit=4)
    in_ring = np.asarray(in_pg.exterior.coords)[:-1]
    inner_d = G.outline([(in_ring, True)], fine, join="miter", miter_limit=4)
    ix0, iy0, ix1, iy1 = in_pg.bounds
    band_d = ""
    if band:
        band_d = G.outline([(np.array([(ix0, band[0]), (ix1, band[0])]), False),
                            (np.array([(ix0, band[1]), (ix1, band[1])]), False)], fine, cap="flat")
    win = (x0 + inner + (rule + fine) / 2 + 1.35, y0 + inner + (rule + fine) / 2 + 1.35,
           x1 - inner - (rule + fine) / 2 - 1.35, band[0] if band else (y0 + y1) / 2)
    return {"outer": outer, "inner": inner_d, "band": band_d, "window": tuple(round(v, 2) for v in win)}


def ace_keyline(suit, cx: float, cy: float, u: float, *, offset: float = 10.0,
                lw: float = T.FINE, geometry: str = "headwaters") -> str:
    """Offset keyline ``offset`` px outside a pip silhouette (brief §F.3 ace
    'frame'), drawn at ``lw``. -> FILL d."""
    d = pip_shape(suit, u, geometry=geometry)
    return G.translate(G.outline(G.offset(d, offset, join="round"), lw), cx, cy)
