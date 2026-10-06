#!/usr/bin/env python3
"""Measure court detail and flat ink cores, without rebuilding artwork.

    .venv/bin/python tools/density.py KH --ref b4e26982 --out /tmp/density/KH

Deck SVGs use only court-top/court-rot art, excluding indices, pips, frame,
band and medallion. Other SVGs use their full viewBox (useful for specimens).
All distances, areas and bounding boxes are in SVG/card units, not PNG units.
This is a measuring aid, not a substitute for visual review or house-rule QA.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from deck import tokens as T

SCALE = 1  # fixed render pixels per card px; never resize a cached preview
TILE = 24
LOW_DETAIL_FLOOR = 0.12
MIN_TILE_COVERAGE = 0.25
EROSION_RADIUS = 5
MIN_PATCH_AREA = 25
NS = "{http://www.w3.org/2000/svg}"
INKS = {"jade": T.JADE, "red": T.RED, "gold": T.FOIL, "ink": T.INK}
EMPTY_PATCH = {"area_px": 0.0, "bbox": None, "ink": None}


@dataclass
class Measurement:
    metrics: dict
    heatmap: Image.Image


def resolve_svg(value: str) -> Path:
    """An ID resolves to cards/<STEM>.svg; a path is used as supplied."""
    if re.fullmatch(r"[KQJ][SHCD]", value, re.I):
        return ROOT / "cards" / f"{value.upper()}.svg"
    return Path(value).expanduser().resolve()


def read_reference(path: Path, revision: str) -> str:
    """Read the committed court matching the input's basename, even for previews."""
    return subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{revision}:cards/{path.stem.upper()}.svg"],
        check=True, capture_output=True, text=True,
    ).stdout


def _viewbox(root: ET.Element) -> tuple[float, float, float, float]:
    if root.get("viewBox"):
        values = tuple(float(v) for v in re.split(r"[\s,]+", root.get("viewBox").strip()))
    else:
        values = (0.0, 0.0, float(root.get("width", "0")), float(root.get("height", "0")))
    if len(values) != 4 or not all(np.isfinite(values)) or min(values[2:]) <= 0:
        raise ValueError("SVG needs a finite, positive viewBox or width/height")
    return values


def _art_source(svg_text: str) -> tuple[bytes, tuple, bool]:
    root = ET.fromstring(svg_text)
    if root.tag not in (NS + "svg", "svg"):
        raise ValueError("input must have an SVG root")
    box = _viewbox(root)
    court_classes = {"court-top", "court-rot"}
    is_court = any(court_classes & set(el.get("class", "").split()) for el in root.iter())
    if is_court:
        # Keep ancestors (transforms/layer styling/clips), all definitions, and
        # the stock. Do not let system decoration inflate the figure's detail.
        def prune(parent):
            for child in list(parent):
                tag = child.tag.rsplit("}", 1)[-1]
                if (tag in {"defs", "style", "title"} or child.get("id") == "paper"
                        or court_classes & set(child.get("class", "").split())):
                    continue
                if tag == "g":
                    prune(child)
                    if len(child):
                        continue
                parent.remove(child)

        prune(root)
        x0, y0, x1, _ = T.ART_WINDOW
        box = (float(x0), float(y0), float(x1 - x0), float(T.H - 2 * y0))
    x, y, w, h = box
    root.set("viewBox", f"{x:g} {y:g} {w:g} {h:g}")
    root.set("width", str(max(1, round(w * SCALE))))
    root.set("height", str(max(1, round(h * SCALE))))
    root.set("preserveAspectRatio", "none")
    return ET.tostring(root), box, is_court


def _render(source: bytes) -> Image.Image:
    png = subprocess.run(
        ["rsvg-convert", "-"], input=source, capture_output=True, check=True, timeout=8,
    ).stdout
    with Image.open(io.BytesIO(png)) as rendered:
        rgba = rendered.convert("RGBA")
    ground = Image.new("RGBA", rgba.size, T.PAPER)
    return Image.alpha_composite(ground, rgba).convert("RGB")


def _labels(image: Image.Image) -> np.ndarray:
    # Nearest palette colour removes anti-aliasing fringes. White and limestone
    # both map to paper so white-stock and limestone specimens use one metric.
    colours = [T.PAPER, *INKS.values(), T.WHITE]
    palette = np.array([tuple(bytes.fromhex(c[1:])) for c in colours], dtype=np.int32)
    rgb = np.asarray(image).astype(np.int32)
    distances = ((rgb[:, :, None, :] - palette) ** 2).sum(axis=3)
    labels = distances.argmin(axis=2).astype(np.uint8)
    labels[labels == len(colours) - 1] = 0
    return labels


def _edges(labels: np.ndarray) -> np.ndarray:
    edges = np.zeros(labels.shape, dtype=bool)
    horizontal = labels[:, 1:] != labels[:, :-1]
    vertical = labels[1:, :] != labels[:-1, :]
    edges[:, 1:] |= horizontal
    edges[:, :-1] |= horizontal
    edges[1:, :] |= vertical
    edges[:-1, :] |= vertical
    return edges


def _bbox(xs: slice, ys: slice, box: tuple) -> list[float]:
    x, y, _, _ = box
    return [round(x + xs.start / SCALE, 3), round(y + ys.start / SCALE, 3),
            round(x + xs.stop / SCALE, 3), round(y + ys.stop / SCALE, 3)]


def _patches(mask: np.ndarray, ink: str, box: tuple) -> tuple[list, np.ndarray]:
    # Zero padding is important: patches touching the window edge must erode,
    # too. Report the surviving flat core, not its un-eroded garment footprint.
    distance = ndimage.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    core = distance > EROSION_RADIUS * SCALE
    regions, _ = ndimage.label(core)  # four-connected: do not join at one corner
    sizes = np.bincount(regions.ravel())
    patches = []
    visible = np.zeros(mask.shape, dtype=bool)
    for label, slices in enumerate(ndimage.find_objects(regions), 1):
        if slices is None or sizes[label] / SCALE**2 < MIN_PATCH_AREA:
            continue
        ys, xs = slices
        patches.append({"area_px": round(float(sizes[label]) / SCALE**2, 3),
                        "bbox": _bbox(xs, ys, box), "ink": ink})
        visible[ys, xs] |= regions[ys, xs] == label
    return patches, visible


def _sorted_patches(patches: list) -> list:
    return sorted(patches, key=lambda p: (-p["area_px"], p["ink"], p["bbox"]))


def analyze_svg(svg_text: str) -> Measurement:
    """Render and measure one SVG. Metrics and heatmap are deterministic."""
    source, box, is_court = _art_source(svg_text)
    image = _render(source)
    labels = _labels(image)
    # An explicit closed outer silhouette isn't present in every SVG. Fill
    # enclosed paper holes in the printed art to include faces/hands/knockouts;
    # boundary-connected paper is background and never a flat ink patch.
    figure = ndimage.binary_fill_holes(labels != 0)
    edges = _edges(labels) & figure
    tiles = []
    low_tiles = np.zeros(labels.shape, dtype=bool)
    step = TILE * SCALE
    height, width = labels.shape
    for y in range(0, height, step):
        for x in range(0, width, step):
            ys, xs = slice(y, min(y + step, height)), slice(x, min(x + step, width))
            tile_figure = figure[ys, xs]
            pixels = int(tile_figure.sum())
            if pixels == 0 or pixels < MIN_TILE_COVERAGE * tile_figure.size:
                continue
            score = float(edges[ys, xs].sum()) / pixels
            low = score < LOW_DETAIL_FLOOR
            tiles.append({"bbox": _bbox(xs, ys, box), "score": round(score, 6),
                          "figure_area_px": pixels / SCALE**2, "low_detail": low})
            if low:
                low_tiles[ys, xs] = tile_figure
    patches = []
    flat_mask = np.zeros(labels.shape, dtype=bool)
    for label, ink in enumerate(INKS, 1):
        ink_patches, mask = _patches((labels == label) & figure, ink, box)
        patches.extend(ink_patches)
        flat_mask |= mask
    patches = _sorted_patches(patches)
    paper, _ = _patches((labels == 0) & figure, "paper", box)
    paper = _sorted_patches(paper)
    metrics = {
        "score": round(float(np.mean([t["score"] for t in tiles])), 6) if tiles else 0.0,
        "low_detail_fraction": round(sum(t["low_detail"] for t in tiles) / len(tiles), 6)
        if tiles else 0.0,
        "largest_flat_patch": patches[0] if patches else dict(EMPTY_PATCH),
        "flat_patches": patches[:5],
        "flat_patch_count": len(patches),
        "paper_inside_figure_patches": paper[:5],
        "paper_inside_figure_patch_count": len(paper),
        "figure_area_px": float(figure.sum()) / SCALE**2,
        "figure_tile_count": len(tiles),
        "art_window": [box[0], box[1], box[0] + box[2], box[1] + box[3]],
        "scope": "court art only" if is_court else "full SVG",
        "parameters": {"render_scale": SCALE, "tile_px": TILE,
                       "low_detail_floor": LOW_DETAIL_FLOOR,
                       "min_tile_coverage": MIN_TILE_COVERAGE,
                       "erosion_radius_px": EROSION_RADIUS,
                       "min_patch_area_px": MIN_PATCH_AREA,
                       "patch_area": "eroded core", "connectivity": 4},
        "tiles": tiles,
    }
    rgb = np.asarray(image).copy()
    for mask, colour, alpha in [(low_tiles, (255, 210, 0), 0.38),
                                (flat_mask, (255, 0, 180), 0.60)]:
        rgb[mask] = np.round((1 - alpha) * rgb[mask] + alpha * np.array(colour)).astype(np.uint8)
    heatmap = Image.fromarray(rgb)
    draw = ImageDraw.Draw(heatmap)
    for patch, colour in [(p, "#FF00B4") for p in patches[:5]] + [
            (p, "#00BBDD") for p in paper[:5]]:
        x0, y0, x1, y1 = patch["bbox"]
        bounds = [(x0 - box[0]) * SCALE, (y0 - box[1]) * SCALE,
                  (x1 - box[0]) * SCALE - 1, (y1 - box[1]) * SCALE - 1]
        draw.rectangle(bounds, outline=colour, width=1)
        draw.text((bounds[0] + 2, bounds[1] + 2),
                  f'{patch["ink"]} {patch["area_px"]:g}', fill=colour, stroke_width=1,
                  stroke_fill=T.PAPER)
    draw.text((3, 3), "Yellow: low detail | Magenta: flat ink | Cyan: paper (info)",
              fill=T.INK, stroke_width=1, stroke_fill=T.PAPER)
    return Measurement(metrics, heatmap)


def _write(result: Measurement, path: Path, out: Path, label: str, revision=None) -> Path:
    basename = f"{path.stem}-{label}"
    report = {**result.metrics, "svg": str(path), "revision": revision}
    report_path = out / f"{basename}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    result.heatmap.save(out / f"{basename}-heatmap.png")
    return report_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("svg", help="SVG path or court ID (e.g. KH)")
    parser.add_argument("--ref", help="git revision for cards/<STEM>.svg")
    parser.add_argument("--out", type=Path, help="output directory (default: /tmp/density/<STEM>)")
    args = parser.parse_args(argv)
    path = resolve_svg(args.svg)
    out = args.out or Path("/tmp/density") / path.stem
    try:
        current = analyze_svg(path.read_text(encoding="utf-8"))
        reference = analyze_svg(read_reference(path, args.ref)) if args.ref else None
        out.mkdir(parents=True, exist_ok=True)
        report_path = _write(current, path, out, "current")
        if reference:
            _write(reference, path, out, "ref", args.ref)
        print(f"{path.stem}: {current.metrics['scope']}")
        print(f"{'Metric':<24}" + (f"{'ref (' + args.ref + ')':>20}" if reference else "")
              + f"{'current':>20}")
        for key in ("score", "low_detail_fraction", "largest_flat_patch"):
            def value(result):
                metric = result.metrics[key]
                return f"{metric['area_px']:g} ({metric['ink'] or 'none'})" if isinstance(metric, dict) \
                    else f"{metric:.6f}"
            print(f"{key:<24}" + (f"{value(reference):>20}" if reference else "")
                  + f"{value(current):>20}")
        print(f"JSON + heatmap: {report_path.parent}")
    except (OSError, ValueError, ET.ParseError, subprocess.SubprocessError) as error:
        parser.exit(1, f"density: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
