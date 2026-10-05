import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
import _jc_parts as J
OUT = os.path.join(ROOT, "work/jc/out/sk"); os.makedirs(OUT, exist_ok=True)
fr = []
for i, st in enumerate("ADC"):
    sc = K.Scene()
    sc.add("bg", K.fill(K.box(0, 0, 2000, 2000), K.RED), K.box(0, 0, 0, 0), sil=False)
    sc.part("belt", K.Part(K.box(0, 450 - 8.5, 2000, 450 + 8.5), K.fill(K.box(0, 441.5, 2000, 458.5), K.JADE), K.outline(K.box(-10, 441.5, 2000, 458.5))), sil=False)
    sc.part("h", J.pecan_husk((100 + 90 * i, 450), style=st))
    fr.append(sc.compose(contour=None))
render(fr, (50, 400, 330, 500), os.path.join(OUT, "husk.png"), 840)
sp = K.Scene()
sp.add("bg", K.fill(K.box(0, 0, 2000, 2000), K.RED), K.box(0,0,0,0), sil=False)
from deck.motifs import core as C
f = J.pecan_sprig((80, 560), -62.0) + J.pecan_sprig((160, 560), -62.0)
ko = C.knockout(K.D(K.box(40, 480, 260, 580)), f)
render([K.fill(ko, K.RED)], (40, 480, 260, 580), os.path.join(OUT, "sprig.png"), 660)
