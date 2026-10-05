import sys, os, time, importlib.util, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
os.chdir("/home/luke/Projects/design/san-marcos-deck")
import numpy as np, shapely
from tuck import build_tuck as BT
from tuck import _tuck_common as K
# the ORIGINAL build_tuck (the fixer's backup) for its foil_gaps
spec = importlib.util.spec_from_file_location("bt_orig", "/tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/wheels/orig/build_tuck.py")
BO = importlib.util.module_from_spec(spec); spec.loader.exec_module(BO)
t = time.time()
b = BT.build_all()
print("built in", round(time.time() - t, 1))
p = b["panels"]
pieces = [("FRONT", b["front"]["foil"]), ("BACK", b["back"]["foil"]), ("SIDE-A", p["side_a"]), ("SIDE-B", p["side_b"]),
          ("TOP", p["top"]), ("BOTTOM", p["bottom"])]
res = {}
for name, frag in pieces:
    sh = frag.shape()
    th = K.type_hull(frag)
    par = name != "BACK"
    new = [g for g in BT.foil_gaps(sh, parallel=par, type_shape=th) if "warn" not in g["rule"]]
    old = [g for g in BO.foil_gaps(sh, parallel=par, type_shape=th) if "warn" not in g["rule"]]
    # the original with the piece order REVERSED (the other ordering of each pair)
    geoms = list(getattr(sh, "geoms", [sh]))[::-1]
    oldrev = [g for g in BO.foil_gaps(shapely.MultiPolygon(geoms), parallel=par, type_shape=th) if "warn" not in g["rule"]]
    print(f"{name:7} new {len(new)}  orig {len(old)}  orig-reversed {len(oldrev)}")
    for tag, L in (("new", new), ("orig", old), ("orig-rev", oldrev)):
        for g in L[:6]:
            print("     ", tag, g)
    if name == "FRONT":
        tb = BT.tight_board(frag)
        cor = [r for r in tb if (r["at"][0] < 140 or r["at"][0] > 629) and (r["at"][1] < 140 or r["at"][1] > 929)]
        print("   front tight-board clusters total", len(tb), " in corners:", cor)
    if name == "BACK":
        tb = BT.tight_board(frag)
        cor = [r for r in tb if (r["at"][0] < 140 or r["at"][0] > 629) and (r["at"][1] < 140 or r["at"][1] > 929)]
        print("   back tight-board clusters total", len(tb), " in corners:", cor)
