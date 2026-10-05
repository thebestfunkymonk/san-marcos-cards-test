import sys, os, importlib.util, warnings, math
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
warnings.simplefilter("ignore")
import numpy as np
from deck import courtkit as K
from inkkit import geom as G
path = sys.argv[1] if len(sys.argv) > 1 else ROOT + "/art/QD.py"
spec = importlib.util.spec_from_file_location("qdmod", path); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(path))); spec.loader.exec_module(m)
sc = m.figure()
for it in sc.items:
    if it.name in ("handL", "handR"):
        print("==", it.name)
        for mk in it.frag.marks:
            if mk.role in ("finger", "thumb", "fingertip"):
                for pts, closed in G.as_polys(mk.d, 0.1):
                    pts = np.asarray(pts)
                    print(f"  {mk.role:9s} w{mk.w} from {pts[0].round(1)} to {pts[-1].round(1)} len {np.sum(np.hypot(*np.diff(pts,axis=0).T)):.1f}")
