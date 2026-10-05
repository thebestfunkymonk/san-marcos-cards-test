"""Render one attribute in isolation: python work/qc/parttest.py <which> out.png"""
import subprocess, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")
from deck import tokens as T, courtkit as K
from deck.motifs import core as C
import _qc_parts as Q, QC
which, out = sys.argv[1], sys.argv[2]
sc = K.Scene()
if which == "sceptre":
    sp = Q.rice_finial_sceptre(QC.SCEPTRE_X, **QC.SCEPTRE)
    sc.add("culm", C.Frag(), sp.meta["culm"])
    sc.add("sceptre", sp.frag, sp.shape, sil=False)
    box = (470, 80, 620, 330)
elif which == "fan":
    QC.fan_group(sc)
    box = (140, 180, 340, 470)
f = sc.compose()
for e in sc.heal_log:
    print("   ", e)
x0, y0, x1, y1 = box
lay = f.layers()
parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>'] + [lay[L] for L in T.LAYERS if lay.get(L)]
W = int((x1 - x0) * 3)
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{W}" height="{int(W*(y1-y0)/(x1-x0))}">' + "".join(parts) + "</svg>"
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str(W), out.replace(".png", ".svg"), "-o", out], check=True)
