"""Print preflight: find features too thin to print and gaps that will plug.

Every printed plate (see :meth:`inkkit.svg.Doc.separations`) is rendered with
rsvg-convert at ``scale``× (default 4× = 1200 ppi), then measured with
morphology:

* thin     ink that disappears under an opening with a disc of the profile's
           ``min_line`` diameter (hairlines, needle tips, slivers)
* plug     paper that fills in under a closing with a disc of ``min_gap``
           (reversed lines, crowded hatch, gaps between strokes)

    from inkkit import preflight
    rep = preflight.preflight(doc, "ink_offset", overlay="out/pf")
    print(preflight.summary(rep))

The report is a dict per plate: ink area, thin/plug areas (px² at card
scale), their share of the ink, component counts, path node counts and an
optional overlay PNG (grey ink, red = too thin, blue = will plug).
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile

import numpy as np

from . import tokens as T

__all__ = ["preflight", "preflight_svg", "summary", "node_count"]

_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def node_count(svg_text: str) -> int:
    """Approximate number of path nodes (coordinate pairs) in an SVG string."""
    n = 0
    for m in re.finditer(r'\sd="([^"]*)"', svg_text):
        n += len(_NUM.findall(m.group(1))) // 2
    return n


def _disk(r: float) -> np.ndarray:
    R = max(1, int(np.ceil(r)))
    y, x = np.mgrid[-R:R + 1, -R:R + 1]
    return (x * x + y * y) <= r * r + 1e-9


def _raster(svg_text: str, width_px: int) -> np.ndarray:
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        sp = os.path.join(td, "p.svg")
        pp = os.path.join(td, "p.png")
        with open(sp, "w", encoding="utf-8") as fh:
            fh.write(svg_text)
        r = subprocess.run(["rsvg-convert", "-w", str(width_px), "-b", "#FFFFFF", sp, "-o", pp],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"rsvg-convert failed: {r.stderr.strip()}")
        im = Image.open(pp).convert("L")
        return np.asarray(im) < 128


def _measure(mask: np.ndarray, scale: float, prof: dict):
    from scipy import ndimage
    thin_d = prof["min_line"] * scale * 0.95
    gap_d = prof["min_gap"] * scale * 0.95
    opened = ndimage.binary_opening(mask, structure=_disk(thin_d / 2))
    thin = mask & ~opened
    # ignore 1-px antialias fringes: a thin feature must survive an erosion by 1
    thin = ndimage.binary_opening(thin, structure=np.ones((2, 2), bool))
    closed = ndimage.binary_closing(mask, structure=_disk(gap_d / 2))
    plug = closed & ~mask
    plug = ndimage.binary_opening(plug, structure=np.ones((2, 2), bool))
    k2 = scale * scale
    ink = float(mask.sum()) / k2
    t_lab, t_n = ndimage.label(thin)
    p_lab, p_n = ndimage.label(plug)
    return {
        "ink_area": ink,
        "thin_area": float(thin.sum()) / k2,
        "plug_area": float(plug.sum()) / k2,
        "thin_frac": float(thin.sum()) / max(mask.sum(), 1),
        "plug_frac": float(plug.sum()) / max(mask.sum(), 1),
        "thin_count": int(t_n),
        "plug_count": int(p_n),
    }, thin, plug


def _overlay(mask, thin, plug, path):
    from PIL import Image
    img = np.full(mask.shape + (3,), 255, np.uint8)
    img[mask] = (150, 150, 150)
    img[thin] = (220, 30, 30)
    img[plug] = (30, 80, 230)
    Image.fromarray(img).save(path)
    return path


def preflight_svg(svg_text: str, profile="ink_offset", *, scale: float = 4.0, width: float = 750.0,
                  overlay: str | None = None) -> dict:
    """Preflight one single-ink SVG (a plate): anything not white is ink."""
    prof = T.PRINT_PROFILES[profile] if isinstance(profile, str) else dict(profile)
    if os.path.isfile(svg_text):
        with open(svg_text, encoding="utf-8") as fh:
            svg_text = fh.read()
    mask = _raster(svg_text, int(round(width * scale)))
    rep, thin, plug = _measure(mask, scale, prof)
    rep["nodes"] = node_count(svg_text)
    rep["bytes"] = len(svg_text.encode())
    if overlay:
        os.makedirs(os.path.dirname(os.path.abspath(overlay)) or ".", exist_ok=True)
        rep["overlay"] = _overlay(mask, thin, plug, overlay if overlay.endswith(".png") else overlay + ".png")
    return rep


def preflight(doc, profile="ink_offset", *, scale: float = 4.0, layers=None,
              overlay: str | None = None, profiles: dict | None = None, **sep_kw) -> dict:
    """Preflight every printed plate of a :class:`inkkit.svg.Doc`.

    profile   a key of ``tokens.PRINT_PROFILES`` ('ink_offset', 'foil',
              'foil_strict') or a dict {min_line, min_gap}; ``profiles`` maps
              layer name -> profile to mix (e.g. {'foil': 'foil'})
    overlay   path prefix: writes ``{overlay}-{layer}.png``
    Returns {layer: report}. Extra keywords go to ``doc.separations``."""
    plates = doc.separations(**sep_kw)
    out = {}
    for name, svg_text in plates.items():
        if layers is not None and name not in layers:
            continue
        prof = (profiles or {}).get(name, profile)
        ov = f"{overlay}-{name}.png" if overlay else None
        out[name] = preflight_svg(svg_text, prof, scale=scale, width=doc.viewBox[2], overlay=ov)
        out[name]["profile"] = prof if isinstance(prof, str) else "custom"
    return out


def summary(report: dict) -> str:
    """One line per plate: ink, % too thin, % plugging, nodes."""
    rows = []
    for name, r in report.items():
        rows.append(f"{name:8s} ink {r['ink_area']:9.0f} px²  thin {100 * r['thin_frac']:5.2f}% "
                    f"({r['thin_count']} spots)  plug {100 * r['plug_frac']:5.2f}% "
                    f"({r['plug_count']} spots)  nodes {r['nodes']}")
    return "\n".join(rows)
