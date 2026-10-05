"""Face variants for QD at 4x (head parts only). arg: JSON list of {"face":{...}, "jaw":[r,dy]}"""
import os, subprocess, sys, json
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
from deck import courtkit as K, tokens as T
import QD
VARIANTS = json.loads(sys.argv[1])
box = tuple(json.loads(sys.argv[2])) if len(sys.argv) > 2 else (300, 150, 450, 300)
names = ("collar", "hair", "cape", "neck", "head", "ear", "earring", "diadem", "columns", "gown", "clasp")
out = []
x0, y0, x1, y1 = box
for i, v in enumerate(VARIANTS):
    QD.FACE_OVERRIDES = v.get("face", {})
    if "jaw" in v:
        QD.JAW = tuple(v["jaw"])
    sc = QD.figure()
    sc.items = [it for it in sc.items if it.name in names or it.name.startswith("hair")]
    f = sc.compose()
    lay = f.layers()
    parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>']
    for L in T.LAYERS:
        if lay.get(L):
            parts.append(lay[L])
    w = int((x1 - x0) * 4)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{w}" height="{int(w*(y1-y0)/(x1-x0))}">' + "".join(parts) + "</svg>")
    p = f"{ROOT}/work/qd/out/parts/fv{i}.svg"
    open(p, "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(w), p, "-o", p.replace(".svg", ".png")], check=True)
    out.append(p.replace(".svg", ".png"))
subprocess.run(["magick"] + out + ["-bordercolor", "white", "-border", "4", "+append", f"{ROOT}/work/qd/out/parts/fvs.png"], check=True)
print("ok", len(out))
