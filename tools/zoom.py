#!/usr/bin/env python3
"""Render exact SVG crops or overlapping zoom tiles by vector re-rendering.

Crop mode:
    python tools/zoom.py <svg> <x> <y> <w> <h> <zoom> <out.png>

    Coordinates are in the SVG's user space (for cards, 750 × 1050 px). The
    crop keeps exactly ``(x, y, w, h)`` as its viewBox and renders to
    ``round(w*zoom) × round(h*zoom)`` pixels. This re-renders the original
    paths; it does not enlarge a raster image.

Tile mode:
    python tools/zoom.py <svg> --tiles OUTDIR --tile 150 --overlap 25 \\
        --zoom 10 [--region x y w h]

    The region defaults to the SVG viewBox. Tiles are emitted as PNG files
    with their card-space x/y/width/height and pixel dimensions recorded in
    ``OUTDIR/tiles.json``. Tile edges are anchored to the region's far edge,
    so the whole region is covered, including when its final overlap is
    larger than requested to avoid a narrow uncovered remainder.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path


def _root_tag(svg_text: str) -> str:
    match = re.search(r"<svg\b[^>]*>", svg_text)
    if not match:
        raise ValueError("input has no <svg> root element")
    return match.group(0)


def _attribute(tag: str, name: str) -> str | None:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(['\"])(.*?)\1", tag)
    return match.group(2) if match else None


def _view_box(svg_text: str) -> tuple[float, float, float, float]:
    tag = _root_tag(svg_text)
    view_box = _attribute(tag, "viewBox")
    if view_box:
        values = [float(value) for value in re.split(r"[\s,]+", view_box.strip())]
        if len(values) == 4 and values[2] > 0 and values[3] > 0:
            return tuple(values)
        raise ValueError(f"invalid SVG viewBox: {view_box!r}")

    def dimension(name):
        value = _attribute(tag, name)
        match = re.match(r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))", value or "")
        if not match or float(match.group(1)) <= 0:
            raise ValueError(f"SVG needs a positive {name} or viewBox")
        return float(match.group(1))

    return 0.0, 0.0, dimension("width"), dimension("height")


def _render(svg_path: str | os.PathLike, box: tuple[float, float, float, float],
            zoom: float, out_path: str | os.PathLike) -> tuple[int, int]:
    x, y, width, height = map(float, box)
    if not all(math.isfinite(value) for value in (x, y, width, height, zoom)):
        raise ValueError("crop coordinates and zoom must be finite numbers")
    if width <= 0 or height <= 0 or zoom <= 0:
        raise ValueError("crop width, height and zoom must be positive")
    pixel_width = max(1, round(width * zoom))
    pixel_height = max(1, round(height * zoom))

    source = Path(svg_path).read_text(encoding="utf-8")
    tag_match = re.search(r"<svg\b[^>]*>", source)
    if not tag_match:
        raise ValueError(f"no <svg> root in {svg_path}")
    tag = tag_match.group(0)
    tag = re.sub(r"\s(?:viewBox|width|height|preserveAspectRatio)\s*=\s*(['\"])[^'\"]*\1", "", tag)
    tag = tag[:-1].rstrip("/") + (
        f' viewBox="{x:g} {y:g} {width:g} {height:g}" width="{pixel_width}" '
        f'height="{pixel_height}" preserveAspectRatio="none">'
    )
    rendered_source = source[:tag_match.start()] + tag + source[tag_match.end():]
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["rsvg-convert", "-u", "-w", str(pixel_width), "-h", str(pixel_height),
         "-o", str(output), "-"],
        input=rendered_source.encode("utf-8"),
        check=True,
    )
    return pixel_width, pixel_height


def zoom(svg_path, x, y, width, height, zoom_factor, out_path):
    """Render one exact vector crop. Kept as the simple crop-mode API."""
    pixels = _render(svg_path, (x, y, width, height), zoom_factor, out_path)
    print(f"{out_path} {pixels[0]}x{pixels[1]}")
    return pixels


def _positions(start: float, extent: float, tile: float, overlap: float) -> list[float]:
    size = min(tile, extent)
    span = extent - size
    if span <= 1e-8:
        return [start]
    count = math.ceil(span / (tile - overlap)) + 1
    step = span / (count - 1)
    return [start + index * step for index in range(count)]


def render_tiles(svg_path, out_dir, tile_size=150.0, overlap=25.0, zoom_factor=10.0, region=None):
    """Render an overlapping tile grid and write its card-coordinate index."""
    if tile_size <= 0 or overlap < 0 or overlap >= tile_size or zoom_factor <= 0:
        raise ValueError("tile and zoom must be positive; overlap must be in [0, tile)")
    source = Path(svg_path).read_text(encoding="utf-8")
    vx, vy, vw, vh = _view_box(source)
    rx, ry, rw, rh = (vx, vy, vw, vh) if region is None else map(float, region)
    if not all(math.isfinite(value) for value in (rx, ry, rw, rh)):
        raise ValueError("region coordinates must be finite numbers")
    if rw <= 0 or rh <= 0:
        raise ValueError("region width and height must be positive")
    if rx < vx - 1e-8 or ry < vy - 1e-8 or rx + rw > vx + vw + 1e-8 or ry + rh > vy + vh + 1e-8:
        raise ValueError("tile region must be inside the SVG viewBox")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    xs = _positions(rx, rw, tile_size, overlap)
    ys = _positions(ry, rh, tile_size, overlap)
    tiles = []
    for row, y in enumerate(ys, 1):
        for col, x in enumerate(xs, 1):
            width = min(tile_size, rx + rw - x)
            height = min(tile_size, ry + rh - y)
            filename = f"tile-r{row:03d}-c{col:03d}.png"
            pixels = _render(svg_path, (x, y, width, height), zoom_factor, out_dir / filename)
            tiles.append({
                "row": row,
                "column": col,
                "file": filename,
                "x": round(x, 6),
                "y": round(y, 6),
                "width": round(width, 6),
                "height": round(height, 6),
                "pixels": {"width": pixels[0], "height": pixels[1]},
            })
    index = {
        "svg": str(Path(svg_path)),
        "viewBox": [vx, vy, vw, vh],
        "region": {"x": rx, "y": ry, "width": rw, "height": rh},
        "tile": tile_size,
        "overlap": overlap,
        "zoom": zoom_factor,
        "tiles": tiles,
    }
    index_path = out_dir / "tiles.json"
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"{len(tiles)} tiles -> {out_dir} (index: {index_path})")
    return index


def _tile_parser(svg_path):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tiles", required=True, metavar="OUTDIR")
    parser.add_argument("--tile", type=float, default=150.0, help="tile width and height in SVG units")
    parser.add_argument("--overlap", type=float, default=25.0, help="overlap between neighboring tiles")
    parser.add_argument("--zoom", type=float, default=10.0, help="output pixels per SVG unit")
    parser.add_argument("--region", nargs=4, type=float, metavar=("X", "Y", "W", "H"))
    return parser


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv in (["-h"], ["--help"]):
        print(__doc__)
        return 0
    svg_path, *arguments = argv
    if "--tiles" in arguments:
        parser = _tile_parser(svg_path)
        options = parser.parse_args(arguments)
        render_tiles(svg_path, options.tiles, options.tile, options.overlap, options.zoom, options.region)
        return 0
    if len(arguments) != 6:
        raise SystemExit(__doc__)
    x, y, width, height, zoom_factor = map(float, arguments[:5])
    zoom(svg_path, x, y, width, height, zoom_factor, arguments[5])
    return 0


if __name__ == "__main__":
    main()
