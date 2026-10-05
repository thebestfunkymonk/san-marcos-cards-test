import sys, subprocess
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
from deck import courtkit as K, tokens as T
import _qd_parts as Q
B, TP = (240.0, 462.0), (212.0, 222.0)
vs = [
 ("v6a", lambda: Q.paintbrush6(B, TP)),
 ("v6b", lambda: Q.paintbrush6(B, TP, bract="vesica", tiers=((0.00, 40.0, 28.0, 15.0, 0.46), (0.2, 34.0, 26.0, 14.5, 0.55), (0.40, 28.0, 23.0, 14.0, 0.64), (0.58, 22.0, 20.0, 13.0, 0.75)), top=(22.0, 14.0))),
 ("v6c", lambda: Q.paintbrush6(B, TP, spike=96.0, tiers=((0.00, 50.0, 26.0, 14.0, 0.42), (0.17, 44.0, 25.0, 13.5, 0.5), (0.34, 38.0, 23.0, 13.0, 0.58), (0.50, 32.0, 21.0, 12.5, 0.68), (0.65, 26.0, 18.0, 12.0, 0.8)), top=(20.0, 13.0))),
 ("v6d", lambda: Q.paintbrush6(B, TP, spike=90.0, tiers=((0.00, 36.0, 26.0, 15.0, 0.45), (0.2, 30.0, 24.0, 14.5, 0.55), (0.39, 24.0, 22.0, 14.0, 0.66), (0.56, 18.0, 19.0, 13.0, 0.8)), top=(20.0, 14.0))),
]
outs = []
for name, fn in vs:
    sc = K.Scene()
    sc.part("pb", fn(), sil=False)
    f = sc.compose()
    lay = f.layers()
    x0, y0, w, h = 160, 200, 110, 280
    parts = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{T.PAPER}"/>'] + [lay[L] for L in T.LAYERS if lay.get(L)]
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w*3}" height="{h*3}">' + "".join(parts) + "</svg>"
    p = f"{ROOT}/work/qd/out/parts/pb_{name}.svg"
    open(p, "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(w * 3), p, "-o", p[:-4] + ".png"], check=True)
    outs.append(p[:-4] + ".png")
subprocess.run(["magick"] + outs + ["-bordercolor", "white", "-border", "3", "+append", f"{ROOT}/work/qd/out/parts/pbs.png"], check=True)
print("ok")
