import sys, importlib, subprocess
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/kc")
from snap import render
from deck import courtkit as K
import art._kc_crown as CR, art._kc_parts as KP, art._kc_beard as KB
variants = eval(sys.argv[1])
outs = []
CROWN = dict(H=64.0, widths=(34.0,38.0,44.0,38.0,34.0), xs=(-60.0,-31.0,0.0,31.0,60.0), knob=0.24, side_k=1.8, order='front', flute_mode='side', side_gap=3.0, flutes=1, band_hw=78.0, wave_top=(26.0, 2.6), ripple=(2, 26.0, 2.2))
for i, v in enumerate(variants):
    fkw = v.get("face", {})
    fc = K.face((375.0, 207.0), "frontal", age="elder", **{**dict(lids="heavy"), **fkw})
    print(i, "strokes", fc.strokes)
    hs = K.HairSpec(**{**dict(top=(-52.0, -30.0), bulge=(-64.0, 40.0), bottom=(-53.0, 110.0), ribbons=4), **v.get("hair", {})})
    sc = K.Scene(rank="K")
    for s in (-1, 1): sc.part(f"hair{s}", K.hair_fall(fc, s, hs))
    sc.add("head", fc.lines + K.outline(fc.head), fc.skin)
    mo = K.moustache(fc, K.MoustacheSpec(**{**dict(root=(-1.5, 8.5), tip=(-32.0, 30.0), arch=7.0), **v.get("mo", {})}))
    bf = v.get("beard_fn", "spray_lines_beard")
    sc.part("beard", getattr(KB if hasattr(KB, bf) else KP, bf)(fc, mo, **{**dict(n=2, pitch=15.0, tick=6.0, tick_angle=40.0), **v.get("beard", {})}))
    sc.part("moustache", mo)
    sc.part("crown", CR.knee_crown(**{**CROWN, **v.get("crown", {})}))
    o = f"/home/luke/Projects/design/san-marcos-deck/work/kc/t/face{i}.png"
    render(sc.layers(), o, (290, 75, 170, 290), 3.0)
    outs.append(o)
subprocess.run(["magick", *outs, "+append", "/home/luke/Projects/design/san-marcos-deck/work/kc/t/faces.png"], check=True)
