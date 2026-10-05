"""Suit pips — the constructions of creative-brief §E.1 (circles and straight
lines only), with the two deviations recorded in deck/ART_CONTRACT.md
"Deviations from brief" (D1 spade body, D2 plinth treads).

Every silhouette is built ONCE in unit space from circles, circular arcs
and straight lines only, unioned with skia-pathops, and then reused by exact
affine placement (never redrawn):

* **Heart** (1.00 u x 0.92 u): lobes r 0.26 u at (±0.24 u, 0.26 u); straight
  tangents to the point (0, 0.92 u); the lobes cross at a sharp cleft 0.16 u
  deep. Drawn at ``HEART_OPTICAL`` (1.04) x the unit.
* **Spade** (1.00 u x 1.22 u): the heart construction flipped point-up at
  full size — circle lobes, 83° apex (D1: the brief's extra "scaled to
  0.80 u tall" squashes the lobes into 0.87 ellipses and blunts the apex to
  91°, a squat arrowhead next to the references); a straight trapezoid stem
  0.07 u -> 0.20 u (0.07 u at 0.18 u above the lobe bottoms, hidden in the
  body; 0.20 u at the plinth, 0.20 u below the lobes, as in §E.1); and the
  fault-step plinth to 1.22 u.
* **Club** (1.04 u x 1.04 u): three circles r 0.245 u at (0, 0.245 u) and
  (±0.275 u, 0.53 u), a triangular core through their centres, the same
  0.07 u -> 0.20 u stem from y 0.55 u to 0.94 u (continued up inside the
  core, which closes a pinhole the construction leaves between the side
  lobes at y 0.53-0.55 u), and the plinth to 1.04 u.
* **Fault-step plinth** (spade and club): two treads 0.05 u tall, the upper
  0.30 u and the lower 0.40 u wide, so each step overhangs by an equal
  0.05 u (D2: the brief's 0.26 / 0.36 leaves a 0.03 u upper tread, 1.9 px at
  index size, which reads as one slab).
* **Diamond** (0.80 u x 1.12 u): a rhombus whose sides bow inward by a
  circular sagitta of 3 % of the side length; the tips stay sharp.

Stems meet the lobes in sharp V crotches, like the reference pips; there
are no fillets, so every edge is an exact circle arc or a straight line.

API
---
``pip_d(suit, u, cx, cy, rotate=False)`` -> closed FILL path whose bounding
box is centred on (cx, cy); ``rotate`` turns it 180° about that centre.
``pip_top_d(suit, u, cx, top)`` places by top edge (index / corner pips).
``pip_bbox(suit, u, cx, cy)`` -> (x0, y0, x1, y1); ``pip_size(suit, u)`` -> (w, h).
``unit_d(suit)`` gives the canonical path at u = 1000 (x centred on 0, top
at y = 0). ``SPADE_H`` is the spade's height in u (1.22).
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from inkkit import geom as G
from deck import tokens as T

__all__ = ["pip_d", "pip_top_d", "pip_bbox", "pip_size", "unit_d", "optical_u",
           "SUIT_SIZE", "SPADE_H", "PLINTH", "ACE_SPADE_U"]

# Construction scale: unit geometry is built at u = 1000 so that path data
# written on inkkit's 0.01 grid keeps 1e-5 u precision.
_U0 = 1000.0

# §E.1 heart construction (u)
HEART_R, HEART_DX, HEART_POINT = 0.26, 0.24, 0.92
# Spade (§E.1 + D1): heart flipped at full size; stem 0.20 u visible below the
# lobes (as in §E.1: lobes end 0.80, plinth starts 1.00); plinth 2 x 0.05 u.
SPADE_BODY_H = HEART_POINT
SPADE_STEM_BOTTOM = SPADE_BODY_H + 0.20                 # 1.12: plinth top
PLINTH = {"upper_w": 0.30, "lower_w": 0.40, "tread_h": 0.05}   # D2 (brief: 0.26 / 0.36)
SPADE_H = SPADE_STEM_BOTTOM + 2 * PLINTH["tread_h"]      # 1.22
STEM_W_TOP, STEM_W_FOOT = 0.07, 0.20                    # §E.1 taper

# A♠ unit (§E.1 table "A♠ u 340 (340 x 374)", §H.13 "top y 140 … plinth
# y 480-514"): with the D1 spade the A♠ keeps its 374 px height and vertical
# extents (top 140, plinth bottom 514, clear of the legend at 560), so
# u = 374 / 1.22 = 306.56 (41 % of the card width instead of 45 %).
ACE_SPADE_U = T.PIP_U_ACE_SPADE * 1.10 / SPADE_H

# §E.1 dimensions in u (heart before the 1.04 optical factor).
SUIT_SIZE = {"S": (1.00, SPADE_H), "H": (1.00, 0.92), "C": (1.04, 1.04), "D": (0.80, 1.12)}


# -----------------------------------------------------------------------------
# primitive builders (unit coordinates, y down)
# -----------------------------------------------------------------------------
def _arc_cubics(cx, cy, rx, ry, a0, a1):
    """Cubic Béziers for the elliptical arc from angle a0 to a1 (radians,
    screen convention: x = cx + rx cos a, y = cy + ry sin a). Returns a list
    of (p1, p2, p3) control-point triples; the start point is implied."""
    n = max(1, int(math.ceil(abs(a1 - a0) / (math.pi / 4))))
    out = []
    da = (a1 - a0) / n
    k = 4.0 / 3.0 * math.tan(da / 4.0)
    for i in range(n):
        t0 = a0 + i * da
        t1 = t0 + da
        p0 = np.array([cx + rx * math.cos(t0), cy + ry * math.sin(t0)])
        p3 = np.array([cx + rx * math.cos(t1), cy + ry * math.sin(t1)])
        d0 = np.array([-rx * math.sin(t0), ry * math.cos(t0)])
        d1 = np.array([-rx * math.sin(t1), ry * math.cos(t1)])
        out.append((p0 + k * d0, p3 - k * d1, p3))
    return out


class _Pen:
    """Tiny absolute-coordinate path writer (full float precision)."""

    def __init__(self):
        self.parts = []

    @staticmethod
    def _f(v):
        return f"{v:.6f}".rstrip("0").rstrip(".")

    def M(self, p):
        self.parts.append(f"M{self._f(p[0])} {self._f(p[1])}")
        return self

    def L(self, p):
        self.parts.append(f"L{self._f(p[0])} {self._f(p[1])}")
        return self

    def arc(self, cx, cy, rx, ry, a0, a1):
        for p1, p2, p3 in _arc_cubics(cx, cy, rx, ry, a0, a1):
            self.parts.append("C" + " ".join(self._f(v) for v in (*p1, *p2, *p3)))
        return self

    def Z(self):
        self.parts.append("Z")
        return self

    def d(self):
        return "".join(self.parts)


def _poly(pts):
    p = _Pen().M(pts[0])
    for q in pts[1:]:
        p.L(q)
    return p.Z().d()


def _circle(cx, cy, r):
    return _Pen().M((cx + r, cy)).arc(cx, cy, r, r, 0.0, 2 * math.pi).Z().d()


def _scaled(d, s):
    return G.transform(d, (s, 0, 0, s, 0, 0))


# -----------------------------------------------------------------------------
# silhouettes (unit space; later scaled by _U0)
# -----------------------------------------------------------------------------
def _heart_outline(point_y: float = HEART_POINT, flip: bool = False) -> str:
    """The §E.1 heart as one closed outline: point -> straight tangent ->
    left lobe over the top -> sharp cleft -> right lobe -> tangent -> point.
    ``flip`` turns it point-up (apex at y = 0) for the spade body."""
    r, cxl, cxr, cy = HEART_R, -HEART_DX, HEART_DX, HEART_R
    px, py = 0.0, point_y
    dl = math.hypot(px - cxl, py - cy)
    al = math.atan2(py - cy, px - cxl) + math.acos(r / dl)      # left lobe, outer tangent
    ar = math.atan2(py - cy, px - cxr) - math.acos(r / dl)      # right lobe, outer tangent
    ky = cy - math.sqrt(r * r - cxl * cxl)                      # cleft (x = 0)
    akl = math.atan2(ky - cy, -cxl) + 2 * math.pi
    akr = math.atan2(ky - cy, -cxr)

    def P(x, y):
        return (x, py - y) if flip else (x, y)

    pen = _Pen()
    tl = (cxl + r * math.cos(al), cy + r * math.sin(al))
    pen.M(P(px, py)).L(P(*tl))
    for p1, p2, p3 in _arc_cubics(cxl, cy, r, r, al, akl) + _arc_cubics(cxr, cy, r, r, akr, ar + 2 * math.pi):
        a, b, c = P(*p1), P(*p2), P(*p3)
        pen.parts.append("C" + " ".join(pen._f(v) for v in (*a, *b, *c)))
    pen.L(P(px, py)).Z()
    return pen.d()


def _plinth(y0: float) -> list[str]:
    """Fault-step plinth (§E.1, D2): upper tread over lower tread from y0."""
    wu, wl, h = PLINTH["upper_w"] / 2, PLINTH["lower_w"] / 2, PLINTH["tread_h"]
    return [_poly([(-wu, y0), (wu, y0), (wu, y0 + h), (-wu, y0 + h)]),
            _poly([(-wl, y0 + h), (wl, y0 + h), (wl, y0 + 2 * h), (-wl, y0 + 2 * h)])]


def _stem(y_top: float, y_bot: float, y_from: float) -> str:
    """Straight trapezoid 0.07 wide at y_top -> 0.20 wide at y_bot, extended
    (same side lines) up to y_from where it is hidden inside the body."""
    h0, h1 = STEM_W_TOP / 2, STEM_W_FOOT / 2

    def hw(y):
        return h0 + (h1 - h0) * (y - y_top) / (y_bot - y_top)
    return _poly([(-hw(y_from), y_from), (hw(y_from), y_from), (h1, y_bot), (-h1, y_bot)])


def _U(*ds):
    """Scale unit-space pieces to the u = 1000 construction scale."""
    return [_scaled(d, _U0) for d in ds]


@lru_cache(maxsize=None)
def unit_d(suit: str) -> str:
    """Canonical pip outline at u = 1000 (x centred on 0, top at y = 0).
    All booleans run at this scale (inkkit writes path data on a 0.01 grid)."""
    suit = suit.upper()
    if suit == "H":
        return G.union(*_U(_heart_outline()))
    if suit == "S":
        body = _heart_outline(SPADE_BODY_H, flip=True)
        y_top = SPADE_BODY_H - 0.18                      # 0.07 u, hidden between the lobes
        return G.union(*_U(body, _stem(y_top, SPADE_STEM_BOTTOM, y_top - 0.12),
                           *_plinth(SPADE_STEM_BOTTOM)))
    if suit == "C":
        r = 0.245
        lobes = [_circle(0.0, r, r), _circle(-0.275, 0.53, r), _circle(0.275, 0.53, r)]
        core = _poly([(0.0, r), (0.275, 0.53), (-0.275, 0.53)])
        return G.union(*_U(*lobes, core, _stem(0.55, 0.94, 0.45), *_plinth(0.94)))
    if suit == "D":
        w, h = 0.80, 1.12
        V = [(0.0, 0.0), (w / 2, h / 2), (0.0, h), (-w / 2, h / 2)]
        pen = _Pen().M(V[0])
        cxy = np.array([0.0, h / 2])
        for i in range(4):
            a, b = np.array(V[i]), np.array(V[(i + 1) % 4])
            L = float(np.linalg.norm(b - a))
            s = 0.03 * L                                   # sagitta, 3 % of the side
            R = (L * L / 4 + s * s) / (2 * s)
            m = (a + b) / 2
            nrm = np.array([-(b - a)[1], (b - a)[0]]) / L
            if np.dot(cxy - m, nrm) < 0:                  # nrm -> towards the centre
                nrm = -nrm
            # inward bow: the arc's centre lies OUTSIDE the rhombus
            c = m - nrm * (R - s)
            a0 = math.atan2(a[1] - c[1], a[0] - c[0])
            a1 = math.atan2(b[1] - c[1], b[0] - c[0])
            da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
            pen.arc(c[0], c[1], R, R, a0, a0 + da)
        pen.Z()
        return G.union(*_U(pen.d()))
    raise ValueError(f"unknown suit {suit!r}")


@lru_cache(maxsize=None)
def _unit_bbox(suit: str):
    return G.bbox(unit_d(suit))


def optical_u(suit: str, u: float) -> float:
    """The drawing scale for a nominal unit u (hearts are drawn 1.04 x)."""
    return u * T.HEART_OPTICAL if suit.upper() == "H" else u


def pip_size(suit: str, u: float) -> tuple[float, float]:
    x0, y0, x1, y1 = _unit_bbox(suit.upper())
    s = optical_u(suit, u) / _U0
    return ((x1 - x0) * s, (y1 - y0) * s)


def _matrix(suit: str, u: float, cx: float, cy: float, rotate: bool):
    suit = suit.upper()
    x0, y0, x1, y1 = _unit_bbox(suit)
    ux, uy = (x0 + x1) / 2, (y0 + y1) / 2
    s = optical_u(suit, u) / _U0
    if rotate:
        return (-s, 0.0, 0.0, -s, cx + s * ux, cy + s * uy)
    return (s, 0.0, 0.0, s, cx - s * ux, cy - s * uy)


def pip_d(suit: str, u: float, cx: float, cy: float, rotate: bool = False) -> str:
    """Closed FILL outline of the pip, bbox centred on (cx, cy).
    ``rotate`` turns it 180° about (cx, cy) (pips below y = 525 on pip cards)."""
    return G.transform(unit_d(suit.upper()), _matrix(suit, u, cx, cy, rotate))


def pip_top_d(suit: str, u: float, cx: float, top: float, rotate: bool = False) -> str:
    """Pip centred on x = cx with its top edge at y = top (index/corner pips)."""
    w, h = pip_size(suit, u)
    return pip_d(suit, u, cx, top + h / 2, rotate)


def pip_bbox(suit: str, u: float, cx: float, cy: float, rotate: bool = False):
    w, h = pip_size(suit, u)
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


# -----------------------------------------------------------------------------
# specimen sheet:  .venv/bin/python -m deck.pips  -> build/specimen/pips.png
# -----------------------------------------------------------------------------
def specimen(out_dir=None) -> str:
    """Render every pip at index / court / field / ace sizes (and upside down
    at field size) on Limestone, with construction guides at ace size."""
    import os
    import subprocess
    out_dir = out_dir or os.path.join(T.ROOT, "build", "specimen")
    os.makedirs(out_dir, exist_ok=True)
    W, H = 1900, 1180
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{T.PAPER}"/>']
    col = {"S": T.INK, "H": T.RED, "C": T.INK, "D": T.RED}
    # row 1: ace sizes with bbox guides
    x = 200
    for s in "SHCD":
        u = ACE_SPADE_U if s == "S" else T.PIP_U_ACE
        w, h = pip_size(s, u)
        cy = 60 + h / 2 if s == "S" else 60 + 374 / 2
        parts.append(f'<path d="{pip_d(s, u, x, cy)}" fill="{col[s]}"/>')
        bx = pip_bbox(s, u, x, cy)
        parts.append(f'<rect x="{bx[0]:.2f}" y="{bx[1]:.2f}" width="{w:.2f}" height="{h:.2f}" '
                     f'fill="none" stroke="#e0a" stroke-width="0.8" stroke-dasharray="4 3"/>')
        x += 470
    # row 2: field size upright + rotated, court, index
    y2 = 560
    x = 90
    for s in "SHCD":
        parts.append(f'<path d="{pip_d(s, T.PIP_U_FIELD, x + 60, y2 + 70)}" fill="{col[s]}"/>')
        parts.append(f'<path d="{pip_d(s, T.PIP_U_FIELD, x + 200, y2 + 70, rotate=True)}" fill="{col[s]}"/>')
        parts.append(f'<path d="{pip_top_d(s, T.PIP_U_COURT, x + 320, y2 + 22)}" fill="{col[s]}"/>')
        parts.append(f'<path d="{pip_top_d(s, T.PIP_U_INDEX, x + 410, y2 + 30)}" fill="{col[s]}"/>')
        x += 470
    # row 3: index size at 1:1 and 25 % (188-px card) proxies, in a row
    y3 = 800
    x = 60
    for s in "SHCD":
        for k in range(3):
            parts.append(f'<path d="{pip_top_d(s, T.PIP_U_INDEX, x, y3)}" fill="{col[s]}"/>')
            x += 80
        x += 30
    # row 4: a 10-spot-like strip of field pips
    x = 110
    for s in "SHCD":
        parts.append(f'<path d="{pip_d(s, T.PIP_U_FIELD, x, 1030)}" fill="{col[s]}"/>')
        parts.append(f'<path d="{pip_d(s, T.PIP_U_FIELD, x + 153, 1030, rotate=True)}" fill="{col[s]}"/>')
        x += 470
    parts.append("</svg>")
    svg_path = os.path.join(out_dir, "pips.svg")
    png_path = os.path.join(out_dir, "pips.png")
    with open(svg_path, "w") as fh:
        fh.write("\n".join(parts))
    subprocess.run(["rsvg-convert", "-w", str(W), svg_path, "-o", png_path], check=True)
    return png_path




# Reference pips for side-by-side study (internal review only; never shipped,
# never traced). Crop boxes are (file, x0, y0, x1, y1) in research/refs/.
_REF_CROPS = [
    ("Monarchs spade", "monarchs_rpc_monarchs-10.jpg", 900, 320, 1070, 510),
    ("Drifters spade", "drifters_rpc_drifters-2.jpg", 880, 45, 1065, 255),
    ("Monarchs club", "monarchs_rpc_monarchs-10.jpg", 765, 1000, 935, 1170),
    ("Monarchs diamond", "monarchs_rpc_monarchs-10.jpg", 1405, 955, 1545, 1140),
]


def compare_refs(out_dir=None, h: int = 240) -> str:
    """build/specimen/pips-vs-refs.png: reference pips (top) above ours at
    the same height (bottom), for eyeballing proportion and stem weight."""
    import os
    import subprocess
    from PIL import Image, ImageDraw, ImageFont
    out_dir = out_dir or os.path.join(T.ROOT, "build", "specimen")
    os.makedirs(out_dir, exist_ok=True)
    refs = []
    for label, f, x0, y0, x1, y1 in _REF_CROPS:
        im = Image.open(os.path.join(T.ROOT, "research", "refs", f)).convert("RGB").crop((x0, y0, x1, y1))
        refs.append((label, im.resize((int(im.width * h / im.height), h), Image.LANCZOS)))
    ours = []
    for s in "SHCD":
        w, hh = pip_size(s, 1000)
        sc = (h - 30) / hh
        W, H = int(w * sc) + 30, h
        d = G.transform(unit_d(s), (sc, 0, 0, sc, W / 2, 15))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
               f'<rect width="{W}" height="{H}" fill="{T.PAPER}"/>'
               f'<path d="{d}" transform="translate({-sc * 0:.1f} 0)" fill="{T.SUIT_COLOR[s]}"/></svg>')
        r = subprocess.run(["rsvg-convert"], input=svg.encode(), capture_output=True, check=True)
        import io
        ours.append(("HEADWATERS " + {"S": "spade", "H": "heart", "C": "club", "D": "diamond"}[s],
                     Image.open(io.BytesIO(r.stdout)).convert("RGB")))
    pad = 20
    cols = max(len(refs), len(ours))
    cw = max(im.width for _, im in refs + ours) + pad
    sheet = Image.new("RGB", (pad + cols * cw, 2 * (h + 36) + pad), (60, 60, 60))
    dr = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(T.FONT_INDEX), 18)
    except Exception:
        font = ImageFont.load_default()
    for row, items in enumerate((refs, ours)):
        for i, (label, im) in enumerate(items):
            x, y = pad + i * cw, pad + row * (h + 36)
            sheet.paste(im, (x, y))
            dr.text((x, y + h + 4), label, fill=(225, 220, 210), font=font)
    p = os.path.join(out_dir, "pips-vs-refs.png")
    sheet.save(p)
    return p


if __name__ == "__main__":
    print(specimen())
    print(compare_refs())
