"""Sceptre test: python work/qc/t/sc_test.py out.png"""
import sys, subprocess, importlib
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
from deck import courtkit as K, tokens as T
import _qc_sceptre as S
import _qc_parts as Q
import json
cfg = json.loads(open(sys.argv[2]).read()) if len(sys.argv) > 2 else {}
import os
X = float(os.environ.get("SX", 545.0))
FEMALE = cfg.get("female")
ARMS = cfg.get("arms")
sc = K.Scene(rank="Q")
sc.part("cloak", Q.cloak(top=(322.0, 270.0), shoulder=(168.0, 286.0), hem=(144.0, 560.0), corner_r=50.0, side_sag=-4.0))
sp = S.rice_sceptre(X, **cfg.get("kw", {}), female=[tuple(f) for f in FEMALE],
                    arms=[(a[0], a[1], [tuple(p) for p in a[2]], a[3], [tuple(f) for f in a[4]], tuple(a[5]) if a[5] else None) for a in ARMS])
from deck.motifs import core as C
sc.add("culm", C.Frag(), sp.meta["culm"])
sc.add("sceptre", sp.frag, sp.shape, sil=False)
K.fist((X, 428.0), -90.0, shaft_w=17.0, back=-1, wrist=(524.0, 470.0), wrist_w=26.0, h=34.0).add_to(sc, "handR", halo=0.0)
f = sc.compose()
print("heal", len(sc.heal_log), "top", sp.meta["top"])
for e in sc.heal_log:
    print("  ", {k: e[k] for k in e if k != 'geom'})
x0, y0, x1, y1, s = 460, 80, 620, 330, 6
lay = f.layers()
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{(x1-x0)*s}" height="{(y1-y0)*s}">'
       f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>'
       + "".join(lay.get(L, "") for L in T.LAYERS)
       + f'<line x1="611" y1="{y0}" x2="611" y2="{y1}" stroke="#f0f" stroke-width="0.5"/></svg>')
out = sys.argv[1]
open(out.replace(".png", ".svg"), "w").write(svg)
subprocess.run(["rsvg-convert", "-w", str((x1-x0)*s//2), out.replace(".png", ".svg"), "-o", out], check=True)
