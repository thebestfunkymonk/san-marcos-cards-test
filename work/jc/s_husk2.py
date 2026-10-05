import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sketch import render, ROOT
from deck import courtkit as K
import _jc_parts as J
OUT = os.path.join(ROOT, "work/jc/out/sk")
sc = K.Scene()
sc.add("bg", K.fill(K.box(0, 0, 2000, 2000), K.RED), K.box(0, 0, 0, 0), sil=False)
sc.part("belt", K.Part(K.box(0, 441.5, 2000, 458.5), K.fill(K.box(0, 441.5, 2000, 458.5), K.JADE), K.outline(K.box(-10, 441.5, 2000, 458.5))), sil=False)
sc.part("h", J.pecan_husk((200, 450), style="D", s=1.28))
render([sc.compose(contour=None)], (150, 400, 250, 500), os.path.join(OUT, "husk2.png"), 600)
