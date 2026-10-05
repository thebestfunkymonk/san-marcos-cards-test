"""Kit demo: fist round a staff + hand grasping an orb (trad_kit.hands). Render with tools/preview.py (piece id KS)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shapely
from shapely.geometry import Point
from deck import tokens as T
from deck.motifs import core as MC
from trad_kit import shapes as SH, hands as HK, regalia as RG
from trad_kit.scene import Scene, Item
def build():
    sc = Scene()
    sc.add(Item("bg", shapely.box(160, 330, 590, 525), T.JADE))
    shaft, collars, det = RG.banded_shaft(540, 166, 525, 18, n=7)
    sc.add(Item("shaft", shaft, T.FOIL, detail=det), Item("collars", collars, T.FOIL, inner=T.MEDIUM))
    fh = HK.fist(540, 452, staff_w=18, side=1)
    cuff = SH.ribbon(SH.seg(fh["wrist"], (fh["wrist"][0]+12, fh["wrist"][1]+20)), 24, 26, cap1="flat")
    sc.add(Item("cuff", cuff, T.RED), Item("hand", fh["hand"], None, detail=fh["lines"]), Item("thumb", fh["thumb"], None))
    sphere, bub, col, odet = RG.spring_orb(300, 426, 30)
    sc.add(Item("col", col, T.FOIL, inner=T.MEDIUM), Item("orb", sphere, T.FOIL, detail=odet), Item("bub", bub, None, inner=T.MEDIUM))
    ch = HK.cup(300, 426, 30, side=-1)
    sc.add(Item("chand", ch["hand"], None, detail=ch["lines"]), Item("cthumb", ch["thumb"], None))
    f, _ = sc.render()
    return f.layers()
