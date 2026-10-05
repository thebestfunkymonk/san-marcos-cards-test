"""Kit demo: the face kit at frontal / 3/4 left / 3/4 right. Render: tools/preview.py work/ks-panel/trad/kit_demo_faces.py KS <out>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataclasses import replace
from deck import tokens as T
from trad_kit import face as FK
from trad_kit.scene import Scene, Item
def build():
    sc = Scene()
    for cx, turn in ((240, 0), (375, -1), (510, 1)):
        s = FK.FaceSpec(cx=cx, eye_y=300, top=250, chin=376, half_w=50, nose_len=28, mouth_y=355,
                        crease=False, brow_gap=11.5, bridge=5.5, eye_dx=25.0, nose_top=291, turn=turn)
        sc.add(Item(f"f{cx}", FK.face_outline(s), None, detail=FK.face_features(s)))
    sc.add(Item("dummy", __import__('shapely').box(150, 450, 600, 505), T.JADE))
    sc.add(Item("dummy2", __import__('shapely').box(150, 60, 160, 70), T.RED))
    sc.add(Item("dummy3", __import__('shapely').box(590, 60, 600, 70), T.FOIL))
    f, _ = sc.render()
    return f.layers()
