"""Quick crop renderer for J♣ experiments: render a Scene (or Frag) crop.

    from sketch import render; render(frag, (x0, y0, x1, y1), path, width)
"""
import os
import subprocess
import sys

ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "art"))

from deck import tokens as T  # noqa: E402


def render(frags, box, path, width):
    if not isinstance(frags, (list, tuple)):
        frags = [frags]
    x0, y0, x1, y1 = box
    parts = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{T.PAPER}"/>']
    for L in T.LAYERS:
        for f in frags:
            v = f.layers().get(L)
            if v:
                parts.append(v)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" width="{width}" '
           f'height="{int(width * (y1 - y0) / (x1 - x0))}">' + "".join(parts) + "</svg>")
    sp = path.replace(".png", ".svg")
    with open(sp, "w") as fh:
        fh.write(svg)
    subprocess.run(["rsvg-convert", "-w", str(width), sp, "-o", path], check=True)
    return path
