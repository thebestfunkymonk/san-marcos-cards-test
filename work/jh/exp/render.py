"""Render helper for JH experiments: render(frags, box, path, width)."""
import os, subprocess, sys
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
from deck import tokens as T

def render(frags, box, path, width, bg=None):
    x0, y0, x1, y1 = box
    parts = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{bg or T.PAPER}"/>']
    for L in T.LAYERS:
        for f in frags:
            v = f.layers().get(L)
            if v:
                parts.append(v)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" width="{width}" '
           f'height="{int(width * (y1 - y0) / (x1 - x0))}">' + "".join(parts) + "</svg>")
    with open(path.replace(".png", ".svg"), "w") as fh:
        fh.write(svg)
    subprocess.run(["rsvg-convert", "-w", str(width), path.replace(".png", ".svg"), "-o", path], check=True)
