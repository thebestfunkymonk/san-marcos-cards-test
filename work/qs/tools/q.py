"""quick render of art.QS figure: q.py OUT [scale] [x0 y0 x1 y1] [--log]"""
import sys, time, importlib
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qs/tools")
from r import render
out = sys.argv[1]
scale = float(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else 1.5
nums = [float(v) for v in sys.argv[3:7]] if len(sys.argv) > 6 else [139, 55, 611, 525]
t = time.time()
import art.QS as QS
sc = QS.figure()
lay = sc.layers()
un = [e for e in sc.heal_log if e.get("action") == "UNRESOLVED"]
print(f"compose {time.time()-t:.1f}s heal {len(sc.heal_log)} unresolved {len(un)}")
render(lay, out, tuple(nums), scale)
if "--log" in sys.argv:
    for e in sc.heal_log:
        print(e)
