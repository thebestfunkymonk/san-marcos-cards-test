"""heallog.py [module] — compose the QD figure and print its heal log + HAND_LOG."""
import sys, os, importlib.util, warnings
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
warnings.simplefilter("ignore")
from deck import courtkit as K
path = sys.argv[1] if len(sys.argv) > 1 else ROOT + "/art/QD.py"
spec = importlib.util.spec_from_file_location("qdmod", path); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(path))); spec.loader.exec_module(m)
sc = m.figure()
m.compose_scene(sc)
box = None
if len(sys.argv) > 5:
    box = tuple(map(float, sys.argv[2:6]))
for e in sc.heal_log:
    at = e.get("at")
    if box and at is not None and not (box[0] <= at[0] <= box[2] and box[1] <= at[1] <= box[3]):
        continue
    print({k: (tuple(round(float(x), 1) for x in v) if k == "at" and v is not None else v) for k, v in e.items()})
print("HAND_LOG:", K.HAND_LOG)
print("n heal entries:", len(sc.heal_log))
