"""Tiny render helpers for Q♠ iteration (work only)."""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from deck import tokens as T  # noqa: E402


def svg_of(frag_or_layers, box, scale=3.0, bg=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    lay = frag_or_layers if isinstance(frag_or_layers, dict) else frag_or_layers.layers()
    body = ""
    for k in T.LAYERS:
        v = lay.get(k, "")
        body += "".join(v) if isinstance(v, list) else v
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*scale:.0f}" '
            f'height="{h*scale:.0f}"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{bg or T.PAPER}"/>'
            f'{body}</svg>')


def render(frag_or_layers, out, box=(139, 55, 611, 525), scale=3.0, bg=None):
    s = svg_of(frag_or_layers, box, scale, bg)
    tmp = out.rsplit(".", 1)[0] + ".svg"
    with open(tmp, "w") as fh:
        fh.write(s)
    subprocess.run(["rsvg-convert", tmp, "-o", out], check=True)
    return out


def montage(files, out, tile=None, geometry="+4+4"):
    cmd = ["magick", "montage", *files, "-geometry", geometry]
    if tile:
        cmd += ["-tile", tile]
    cmd += [out]
    subprocess.run(cmd, check=True)
    return out
