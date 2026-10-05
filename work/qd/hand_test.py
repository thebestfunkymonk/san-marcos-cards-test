"""Fist variants on a stem, in isolation, at 5x. arg: JSON list of fist kwargs (+ 'stem': [x0,y0,x1,y1,w])."""
import sys, json, subprocess, math
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
from deck import courtkit as K, tokens as T
VAR = json.loads(sys.argv[1])
outs = []
for i, v in enumerate(VAR):
    sc = K.Scene()
    x0, y0, x1, y1, w = v.pop("stem")
    st = K.staff((x0, y0), (x1, y1), w)
    sc.part("stem", st)
    sl = v.pop("sleeve", None)
    if sl:
        s_, c_ = K.sleeve(K.SleeveSpec(base=tuple(sl[0]), wrist=tuple(v["wrist"]), sag=sl[1], width=sl[2], wrist_w=sl[3], cuff=sl[4], color=K.JADE, cuff_color=K.GOLD))
        sc.part("sleeve", s_)
        sc.part("cuff", c_)
    at = tuple(v.pop("at"))
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    h = K.fist(at, ang, **{k: (tuple(val) if isinstance(val, list) else val) for k, val in v.items()})
    h.add_to(sc, "hand", halo=0.0)
    f = sc.compose()
    bx = (at[0] - 45, at[1] - 45, at[0] + 45, at[1] + 55)
    lay = f.layers()
    parts = [f'<rect x="{bx[0]}" y="{bx[1]}" width="90" height="100" fill="{T.PAPER}"/>'] + [lay[L] for L in T.LAYERS if lay.get(L)]
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bx[0]} {bx[1]} 90 100" width="450" height="500">' + "".join(parts) + "</svg>"
    p = f"{ROOT}/work/qd/out/parts/hv{i}.svg"
    open(p, "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", "450", p, "-o", p[:-4] + ".png"], check=True)
    outs.append(p[:-4] + ".png")
subprocess.run(["magick"] + outs + ["-bordercolor", "white", "-border", "3", "+append", f"{ROOT}/work/qd/out/parts/hvs.png"], check=True)
print("ok")
