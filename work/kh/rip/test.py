import sys, math, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import numpy as np
from deck import courtkit as K
from deck.motifs import core as C

M = K.MEDIUM

def group_full(c, ry=(4.2, 10.4, 18.4), aspect=0.62):
    f = C.Frag()
    for r in ry:
        f += K.line(C.ellipse_d(c[0], c[1], r / aspect, r), M)
    return f

def ell_arc(c, rx, ry, a0, a1, n=80):
    t = np.radians(np.linspace(a0, a1, n))
    return np.column_stack([c[0] + rx * np.cos(t), c[1] + ry * np.sin(t)])

def group_arcs(c, ry=(4.6, 10.8, 18.8), aspect=0.55, span=(200, 340), dot=True):
    f = C.Frag()
    if dot:
        f += K.dot(c, 6.3)
    for r in ry[1:] if dot else ry:
        f += K.line(C.polyline_d(ell_arc(c, r / aspect, r, span[0], span[1])), M)
    return f

def group_dot_rings(c, ry=(10.4, 17.6), aspect=0.58):
    f = K.dot(c, 6.3)
    for r in ry:
        f += K.line(C.ellipse_d(c[0], c[1], r / aspect, r), M)
    return f

def field(gfun, x0, y0, w, h, px, py):
    out = C.Frag()
    for j in range(-1, int(h / py) + 2):
        off = px / 2 if j % 2 else 0
        for i in range(-1, int(w / px) + 2):
            out += gfun((x0 + off + i * px, y0 + j * py))
    return out

tiles = [(group_full, (66, 46)), (lambda c: group_arcs(c), (60, 40)), (lambda c: group_arcs(c, span=(180, 360), dot=False), (62, 40)),
         (group_dot_rings, (62, 42)), (lambda c: group_arcs(c, ry=(4.6, 10.8, 18.8), aspect=0.5, span=(195, 345), dot=False), (70, 38))]
frags = C.Frag()
for k, (g, (px, py)) in enumerate(tiles):
    x0 = 20 + k * 150
    box = K.box(x0, 20, x0 + 140, 220)
    pat = K.clip_in(field(g, x0 + 20, 40, 140, 200, px, py), box.buffer(-8))
    red = C.knockout(K.D(box), pat)
    frags += K.fill(red, K.RED)
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 240" width="2340"><rect width="780" height="240" fill="#F4EFE3"/>' + "".join(v for v in frags.layers().values()) + "</svg>"
open("/home/luke/Projects/design/san-marcos-deck/work/kh/rip/t.svg", "w").write(svg)
subprocess.run(["rsvg-convert", "/home/luke/Projects/design/san-marcos-deck/work/kh/rip/t.svg", "-o", "/home/luke/Projects/design/san-marcos-deck/work/kh/rip/t.png"], check=True)
