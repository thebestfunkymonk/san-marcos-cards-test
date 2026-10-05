"""Review scratch: reed partition with leaf pairs phased onto the nodes (not project code)."""
import subprocess, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from deck import tokens as T, frames as F
from inkkit import geom as G
X0, X1, CX, CY = 139, 611, 375, 525
def st(d, w=T.MEDIUM, cap="butt", join="miter"):
    return f'<path d="{d}" fill="none" stroke="{T.INK}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="{join}"/>'
def rules():
    return st(G.poly_d([(135, 511), (615, 511)]) + G.poly_d([(135, 539), (615, 539)]), T.FINE)
def frame():
    return (f'<path d="M135 480V570M615 480V570" stroke="{T.FOIL}" stroke-width="{T.FINE}"/>'
            f'<path d="M128 480V570M622 480V570" stroke="{T.INK}" stroke-width="{T.RULE}"/>')
def current():
    stalk, ticks, nodes = F._reed_parts(0)
    nd = "".join(G.ellipse_d(x, y, 7, 3.5) for x, y in nodes)
    return st(stalk) + st(ticks, cap="round", join="round") + f'<path d="{nd}" fill="{T.INK}"/>'
def phased():
    stalk = G.poly_d([(X0, CY), (X1, CY)])
    ticks, nodes = [], []
    for k in range(-6, 7):
        x = CX + k * 48
        if x - 20 < X0 + 6 or x + 20 > X1 - 6: continue
        if k % 2 == 0:
            nodes.append(x)
            # blades spring from the node's ends (like the house mark): up-right from the right end, C2 partner
            ticks.append(F._blade_d(x + 7, CY, 1) + F._blade_d(x - 7, CY, -1))
        else:
            ticks.append(F._blade_d(x, CY, 1) + F._blade_d(x, CY, -1))
    nd = "".join(G.ellipse_d(x, CY, 7, 3.5) for x in nodes)
    return st(stalk) + st("".join(ticks), cap="round", join="round") + f'<path d="{nd}" fill="{T.INK}"/>'
def node_only():
    stalk = G.poly_d([(X0, CY), (X1, CY)])
    ticks, nodes = [], []
    for k in range(-4, 5):
        x = CX + k * 48
        nodes.append(x)
        ticks.append(F._blade_d(x + 7, CY, 1) + F._blade_d(x - 7, CY, -1))
    nd = "".join(G.ellipse_d(x, CY, 7, 3.5) for x in nodes)
    return st(stalk) + st("".join(ticks), cap="round", join="round") + f'<path d="{nd}" fill="{T.INK}"/>'
rows = [current(), phased(), node_only()]
H = 60; W = 520
out = [f'<g transform="translate(-120 {i*H - 525 + H/2})">{frame()}{rules()}{b}</g>' for i, b in enumerate(rows)]
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H*len(rows)}" viewBox="0 0 {W} {H*len(rows)}">'
       f'<rect width="{W}" height="{H*len(rows)}" fill="{T.PAPER}"/>' + "".join(out) + "</svg>")
p = "/home/luke/Projects/design/san-marcos-deck/build/review/reed_mock"
open(p + ".svg", "w").write(svg)
subprocess.run(["rsvg-convert", "-z", "2.5", p + ".svg", "-o", p + ".png"], check=True)
