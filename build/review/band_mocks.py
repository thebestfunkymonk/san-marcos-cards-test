"""Review scratch: alternative ♠ fault-step and ♣ reed partition lines (not project code)."""
import math, subprocess, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import numpy as np
from deck import tokens as T, frames as F
from inkkit import geom as G
from shapely.geometry import LineString

X0, X1, CX, CY = 139, 611, 375, 525
def st(d, w=T.MEDIUM, cap="butt", join="miter"):
    return f'<path d="{d}" fill="none" stroke="{T.INK}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="{join}" stroke-miterlimit="4"/>'
def rules(cut=None):
    d = G.poly_d([(135, 511), (615, 511)]) + G.poly_d([(135, 539), (615, 539)])
    if cut: d = G.clip_out(d, cut)
    return st(d, T.FINE)
def frame():
    return (f'<path d="M135 480V570M615 480V570" stroke="{T.FOIL}" stroke-width="{T.FINE}"/>'
            f'<path d="M128 480V570M622 480V570" stroke="{T.INK}" stroke-width="{T.RULE}"/>')
h = F.FAULT_SPACING / 2

def fault_offset(s):
    # parallel offsets of ONE stepped centreline (riser of each line offset by ±h in x)
    a, b = CY - s / 2, CY + s / 2
    up = G.poly_d([(X0, a - h), (CX + h, a - h), (CX + h, b - h), (X1, b - h)])
    lo = G.poly_d([(X0, a + h), (CX - h, a + h), (CX - h, b + h), (X1, b + h)])
    return up + lo

def fault_outboard(s, xs=120):
    # K/Q: level centre under the medallion, one visible step each side at CX ± xs (C2)
    up = G.poly_d([(X0, CY - s - h), (CX - xs + h, CY - s - h), (CX - xs + h, CY - h), (CX + xs + h, CY - h),
                   (CX + xs + h, CY + s - h), (X1, CY + s - h)])
    lo = G.poly_d([(X0, CY - s + h), (CX - xs - h, CY - s + h), (CX - xs - h, CY + h), (CX + xs - h, CY + h),
                   (CX + xs - h, CY + s + h), (X1, CY + s + h)])
    return up + lo

def gap(d):
    parts = [p for p in d.split("M") if p]
    ls = [LineString(np.array([[float(v) for v in q.split(",")] if "," in q else [0, 0] for q in []])) for p in parts] if False else None
    return None

rows = []
rows.append(("current J♠ (risers collinear, 0.2 px gap)", st(F._fault_step_d()), None))
rows.append(("J♠ parallel-offset risers, step 4 (gap 4.2)", st(fault_offset(4.0)), None))
rows.append(("J♠ parallel-offset risers, step 7.3 = one course", st(fault_offset(7.3)), None))
mk = F.medallion_mask_d("K")
med = "".join(F.medallion_fragments("K", "S")["ink"] + F.medallion_fragments("K", "S")["gold"])
rows.append(("current K♠ (step hidden under medallion)", st(G.clip_out(F._fault_step_d(), mk)) + med, mk))
rows.append(("K♠ outboard steps at x 255 / 495, level centre", st(G.clip_out(fault_outboard(4.0), mk)) + med, mk))

# reed: current vs staggered straight ticks springing from the node
def reed_current():
    stalk, ticks, nodes = F._reed_parts(0)
    nd = "".join(G.ellipse_d(x, y, 7, 3.5) for x, y in nodes)
    return st(stalk) + st(ticks, cap="round", join="round") + f'<path d="{nd}" fill="{T.INK}"/>'
def reed_alt():
    stalk = G.poly_d([(X0, CY), (X1, CY)])
    ticks = []
    nodes = []
    for k in range(-5, 6):
        x = CX + k * 48
        if x - 20 < X0 + 8 or x + 20 > X1 - 8: continue
        nodes.append(x)
        # alternate leaves from each node: up-right from the node's right, its C2 partner down-left
        L, ang = 13.0, math.radians(32)
        ticks.append(G.poly_d([(x + 3, CY), (x + 3 + L * math.cos(ang), CY - L * math.sin(ang))]))
        ticks.append(G.poly_d([(x - 3, CY), (x - 3 - L * math.cos(ang), CY + L * math.sin(ang))]))
    nd = "".join(G.poly_d([(x - 1.2, CY - 6), (x - 1.2, CY + 6)]) + G.poly_d([(x + 1.2 + 0.0, CY - 6), (x + 1.2, CY + 6)]) for x in nodes)
    return st(stalk) + st("".join(ticks), cap="round") + st(nd, w=T.FINE)
rows.append(("current J♣ reed", reed_current(), None))
rows.append(("alt J♣: leaves spring from each node, alternate sides", reed_alt(), None))

H = 60
out = []
for i, (lab, body, cut) in enumerate(rows):
    y = i * H
    out.append(f'<g transform="translate(-120 {y - 525 + H/2})">{frame()}{rules(cut)}{body}</g>')
W = 520
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H*len(rows)}" viewBox="0 0 {W} {H*len(rows)}">'
       f'<rect width="{W}" height="{H*len(rows)}" fill="{T.PAPER}"/>' + "".join(out) + "</svg>")
p = "/home/luke/Projects/design/san-marcos-deck/build/review/band_mocks"
open(p + ".svg", "w").write(svg)
subprocess.run(["rsvg-convert", "-z", "2.5", p + ".svg", "-o", p + ".png"], check=True)
for lab, _, _ in rows: print(lab)
# gaps
def lines(d):
    import re
    out = []
    for sub in re.findall(r"M[^M]+", d):
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", sub)]
        out.append(LineString(np.array(nums).reshape(-1, 2)))
    return out
for lab, d in (("current", F._fault_step_d()), ("offset s4", fault_offset(4.0)), ("offset s7.3", fault_offset(7.3)), ("outboard", fault_outboard(4.0))):
    a, b = [l.buffer(T.MEDIUM / 2, cap_style="flat", join_style="mitre", mitre_limit=4) for l in lines(d)[:2]]
    print(lab, "min paper gap", round(a.distance(b), 2))
