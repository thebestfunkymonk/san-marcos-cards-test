"""Heraldic helpers: tincture hatching (Petra Sancta), shields, crowns.

    from inkkit import heraldry as HR
    sh = HR.shield(375, 520, 190, 230, "heater")
    d = HR.tincture(sh, "azure")                 # horizontal lines
    crown = HR.crown(375, 300, 150, style="royal")

All return FILL d (clockwise outlines) unless noted.
"""
from __future__ import annotations

import math

import numpy as np
import shapely

from . import geom as G
from . import hatch as H
from . import tokens as T

__all__ = ["TINCTURES", "tincture", "shield", "crown"]

# Petra Sancta hatching: line directions in screen degrees (0 = horizontal,
# 90 = vertical, 45 = dexter chief -> sinister base, i.e. top-left to
# bottom-right as seen), or 'dots' / None (plain).
TINCTURES = {
    "or": "dots", "argent": None,
    "gules": (90,), "azure": (0,), "vert": (45,), "purpure": (-45,),
    "sable": (0, 90), "tenne": (-45, 0), "sanguine": (45, -45), "murrey": (45, -45),
}


def tincture(shape, name: str, *, spacing: float = 4.2, lw: float | None = None,
             dot_r: float | None = None, inset: float = 0.0) -> str:
    """Hatch ``shape`` in the Petra Sancta convention for tincture ``name``:
    or = dots, argent = plain, gules = vertical, azure = horizontal,
    vert = bend (top-left to bottom-right), purpure = bend sinister,
    sable = horizontal + vertical, tenné = bend sinister + horizontal,
    sanguine / murrey = both bends. Lines are ``lw`` (default the print
    minimum) with butt ends at the edge. -> FILL d ('' for argent)."""
    key = str(name).lower().replace("é", "e")
    if key not in TINCTURES:
        raise ValueError(f"unknown tincture {name!r}; use one of {sorted(TINCTURES)}")
    w = lw if lw is not None else T.MIN_LINE
    spec = TINCTURES[key]
    if spec is None:
        return ""
    if spec == "dots":
        r = dot_r if dot_r is not None else max(0.6 * w, spacing * 0.16)
        return H.dot_screen(shape, spacing * 1.25, r, grid="hex", inset=inset)
    return "".join(H.parallel(shape, a, spacing, width=w, cap="butt", inset=inset) for a in spec)


_SHIELDS = ("heater", "french", "spanish", "swiss", "lozenge", "roundel", "oval")


def shield(cx: float, cy: float, w: float, h: float, style: str = "heater") -> str:
    """Escutcheon outline centred on (cx, cy): 'heater' (pointed), 'french'
    (square with a small base point), 'spanish' (round base), 'swiss'
    (engrailed chief, pointed base), 'lozenge', 'roundel', 'oval'. -> FILL d."""
    if style not in _SHIELDS:
        raise ValueError(f"shield style must be one of {_SHIELDS}, not {style!r}")
    if not (w > 0 and h > 0):
        raise ValueError("shield: w and h must be > 0")
    x0, y0 = cx - w / 2, cy - h / 2
    x1, y1 = cx + w / 2, cy + h / 2
    if style == "heater":
        cmds = [("M", x0, y0), ("L", x1, y0), ("L", x1, y0 + h * 0.42),
                ("C", x1, y0 + h * 0.74, cx + w * 0.22, y0 + h * 0.9, cx, y1),
                ("C", cx - w * 0.22, y0 + h * 0.9, x0, y0 + h * 0.74, x0, y0 + h * 0.42), ("Z",)]
    elif style == "french":
        k = h * 0.1
        cmds = [("M", x0, y0), ("L", x1, y0), ("L", x1, y1 - k * 2.4),
                ("C", x1, y1 - k * 0.9, cx + w * 0.16, y1 - k * 1.0, cx, y1),
                ("C", cx - w * 0.16, y1 - k * 1.0, x0, y1 - k * 0.9, x0, y1 - k * 2.4), ("Z",)]
    elif style == "spanish":
        r = w / 2
        cmds = [("M", x0, y0), ("L", x1, y0), ("L", x1, y1 - r),
                ("C", x1, y1 - r + r * 0.5523, cx + r * 0.5523, y1, cx, y1),
                ("C", cx - r * 0.5523, y1, x0, y1 - r + r * 0.5523, x0, y1 - r), ("Z",)]
    elif style == "swiss":
        dip = h * 0.06
        cmds = [("M", x0, y0), ("Q", cx - w * 0.25, y0 + dip * 1.6, cx, y0 + dip * 0.2),
                ("Q", cx + w * 0.25, y0 + dip * 1.6, x1, y0), ("L", x1, y0 + h * 0.45),
                ("C", x1, y0 + h * 0.76, cx + w * 0.2, y0 + h * 0.9, cx, y1),
                ("C", cx - w * 0.2, y0 + h * 0.9, x0, y0 + h * 0.76, x0, y0 + h * 0.45), ("Z",)]
    elif style == "lozenge":
        return G.poly_d([(cx, y0), (x1, cy), (cx, y1), (x0, cy)], True, orient="cw")
    elif style == "roundel":
        return G.circle_d(cx, cy, min(w, h) / 2)
    else:
        return G.ellipse_d(cx, cy, w / 2, h / 2)
    return G.orient(G.cmds_to_d(cmds), "cw")


_CROWNS = ("royal", "ducal", "mural", "eastern")


def crown(cx: float, base_y: float, width: float, *, style: str = "royal",
          lw: float | None = None, line_style: str = "solid", jewels: bool = True) -> str:
    """Heraldic crown sitting on ``base_y`` (the band's lower edge), centred
    on ``cx``, ``width`` wide, built from a band, fleurons, pearls and (royal)
    pearled arches with an orb and cross:

    'royal'   band + alternating crosses/fleurs + two pearled arches, orb, cross
    'ducal'   band + three strawberry-leaf fleurons with pearls between
    'mural'   castellated masonry band (civic crown)
    'eastern' band + pointed rays tipped with pearls
    line_style 'solid' (silhouette with knocked-out jewels / details) or
    'outline' (line art at ``lw``). -> FILL d."""
    from .ornament.radiance import fleuron
    from .ornament.borders import beaded
    if style not in _CROWNS:
        raise ValueError(f"crown style must be one of {_CROWNS}, not {style!r}")
    if line_style not in ("solid", "outline"):
        raise ValueError("crown line_style must be 'solid' or 'outline'")
    W = float(width)
    if not W > 0:
        raise ValueError("crown: width must be > 0")
    w = lw if lw is not None else max(T.FINE, W / 70)
    bh = W * 0.16
    x0, x1 = cx - W / 2, cx + W / 2
    band = G.rect_d(x0, base_y - bh, W, bh, bh * 0.18)
    solids, cuts, lines = [band], [], []
    top = base_y - bh
    if jewels and style != "mural":
        for k, xk in enumerate(np.linspace(x0 + W * 0.12, x1 - W * 0.12, 5)):
            rx, ry = (bh * 0.22, bh * 0.3) if k % 2 == 0 else (bh * 0.14, bh * 0.14)
            cuts.append(G.ellipse_d(xk, base_y - bh / 2, rx, ry))
    if style == "royal":
        # pearled arches from the band ends to the centre top
        apex = (cx, top - W * 0.52)
        for sg in (-1, 1):
            p0 = np.array([cx + sg * W * 0.44, top])
            ctrl = np.array([cx + sg * W * 0.46, top - W * 0.55])
            t = np.linspace(0, 1, 60)[:, None]
            arch = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * ctrl + t ** 2 * np.array([cx + sg * W * 0.03, apex[1] + W * 0.08])
            lines.append(arch)
            solids.append(beaded(arch[6:-4], max(W * 0.018, T.MIN_LINE), W * 0.012))
        # centre arch
        lines.append(np.array([[cx, top], [cx, apex[1] + W * 0.06]]))
        orb_r = W * 0.065
        oy = apex[1] - orb_r * 0.2
        solids.append(G.circle_d(cx, oy, orb_r))
        cuts.append(G.outline(np.array([[cx - orb_r, oy], [cx + orb_r, oy]]), max(T.MIN_REVERSED, orb_r * 0.2)))
        ch = orb_r * 2.2
        solids.append(G.rect_d(cx - orb_r * 0.18, oy - orb_r - ch, orb_r * 0.36, ch + 1, 0))
        solids.append(G.rect_d(cx - orb_r * 0.6, oy - orb_r - ch * 0.7, orb_r * 1.2, orb_r * 0.36, 0))
        # crosses and fleurs on the band rim
        for k, xk in enumerate(np.linspace(x0 + W * 0.06, x1 - W * 0.06, 5)):
            if k % 2 == 0:
                solids.append(fleuron(xk, top - W * 0.075, W * 0.17, style="lily"))
            else:
                a = W * 0.045
                solids.append(G.rect_d(xk - a * 0.3, top - a * 2.4, a * 0.6, a * 2.4, 0))
                solids.append(G.rect_d(xk - a * 0.9, top - a * 1.9, a * 1.8, a * 0.6, 0))
    elif style == "ducal":
        for k, xk in enumerate(np.linspace(x0 + W * 0.12, x1 - W * 0.12, 3)):
            solids.append(fleuron(xk, top - W * 0.11, W * 0.26, style="palmette"))
        for xk in np.linspace(x0 + W * 0.29, x1 - W * 0.29, 2):
            solids.append(G.rect_d(xk - W * 0.008, top - W * 0.09, W * 0.016, W * 0.09, 0))
            solids.append(G.circle_d(xk, top - W * 0.1, W * 0.035))
    elif style == "mural":
        n = 5
        mw_ = W / (2 * n - 1)
        for k in range(n):
            xk = x0 + k * 2 * mw_
            solids.append(G.rect_d(xk, top - bh * 0.9, mw_, bh * 0.9 + 1, 0))
        # masonry joints knocked out of band + merlons
        jw = max(T.MIN_REVERSED, bh * 0.07)
        for yy in (base_y - bh / 2,):
            cuts.append(G.outline(np.array([[x0 + jw, yy], [x1 - jw, yy]]), jw, cap="flat"))
        for k in range(2 * n):
            xx = x0 + (k + 0.5) * mw_
            y_a, y_b = (base_y - bh / 2, base_y) if k % 2 else (top, base_y - bh / 2)
            cuts.append(G.outline(np.array([[xx, y_a + jw], [xx, y_b - jw]]), jw, cap="flat"))
    else:  # eastern
        n = 7
        for k in range(n):
            xk = x0 + W * (k + 0.5) / n
            hk = W * (0.26 if k % 2 == 0 else 0.2)
            solids.append(G.poly_d([(xk - W * 0.05, top + 1), (xk, top - hk), (xk + W * 0.05, top + 1)], True,
                                   orient="cw"))
            solids.append(G.circle_d(xk, top - hk - W * 0.025, W * 0.028))
    body = G.union(*solids, *([G.outline(lines, w * 1.3)] if lines else []))
    if cuts:
        body = G.difference(body, *cuts)
    if line_style == "outline":
        return G.outline(body, w)
    return body
