"""Quick part snapshots: python work/kc/snap.py <out.png> <x0> <y0> <w> <h> <scale> <expr...>
Each expr is python evaluated with K, CR, BD, RB, RG, KP, KC imported; it must return a Scene or a
list of (name, Part) or a layers dict."""
import os, sys, subprocess
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
import importlib
from deck import courtkit as K
from deck import tokens as T


def render(layers, out, box, scale=3.0):
    x0, y0, w, h = box
    body = "".join(f'<g id="{L}">{layers[L] if isinstance(layers[L], str) else "".join(layers[L])}</g>'
                   for L in T.LAYERS if L in layers)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*scale}" height="{h*scale}">'
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{T.PAPER}"/>{body}</svg>')
    p = out[:-4] + ".svg"
    open(p, "w").write(svg)
    subprocess.run(["rsvg-convert", p, "-o", out], check=True)


def scene_of(parts):
    sc = K.Scene(rank="K")
    for n, p in parts:
        sc.part(n, p)
    return sc
