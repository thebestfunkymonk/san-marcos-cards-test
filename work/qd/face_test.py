"""Face variants for QD at 3x: renders the head (+hair+diadem) with FaceSpec overrides."""
import os, subprocess, sys, json
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
from deck import courtkit as K
from deck import tokens as T
import QD

VARIANTS = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [{}]
out = []
for i, ov in enumerate(VARIANTS):
    QD.FACE_OVERRIDES = ov
    sc = QD.figure()
    f = sc.compose()
    x0, y0, x1, y1 = 290, 140, 470, 300
    parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>']
    lay = f.layers()
    for L in T.LAYERS:
        if lay.get(L):
            parts.append(lay[L])
    w = int((x1 - x0) * 3)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{w}" height="{int(w*(y1-y0)/(x1-x0))}">' + "".join(parts) + "</svg>")
    p = f"{ROOT}/work/qd/out/parts/face{i}.svg"
    open(p, "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(w), p, "-o", p.replace(".svg", ".png")], check=True)
    out.append(p.replace(".svg", ".png"))
subprocess.run(["magick"] + out + ["+append", f"{ROOT}/work/qd/out/parts/faces.png"], check=True)
print("ok", len(out))
