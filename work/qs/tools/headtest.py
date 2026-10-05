import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render
from deck import courtkit as K
import art.QS as QS
fc, drape, crown, hair, head, neck, diad = QS.head_group()
sc = K.Scene()
for nm, p in (("drape", drape), ("hair", hair), ("neck", neck), ("head", head), ("crown", crown), ("diad", diad)):
    sc.part(nm, p)
lay = sc.layers()
render(lay, sys.argv[1], (300, 120, 480, 330), 4)
print(len(drape.lines.marks), [m.role for m in crown.lines.marks], [m.role for m in hair.lines.marks])
for e in sc.heal_log:
    print(e)
