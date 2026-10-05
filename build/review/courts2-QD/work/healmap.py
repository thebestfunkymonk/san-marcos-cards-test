"""healmap.py SVG MODULE OUT — mark heal trims on a 2x render of the top half."""
import sys, os, subprocess, importlib.util, warnings
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art"); warnings.simplefilter("ignore")
from deck import courtkit as K
svg, path, out = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("qdmod", path); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(path))); spec.loader.exec_module(m)
sc = m.figure(); m.compose_scene(sc)
tmp = out + ".base.png"
subprocess.run(["rsvg-convert", "-w", "1500", svg, "-o", tmp], check=True)
draw = []
for i, e in enumerate(sc.heal_log):
    at = e.get("at")
    if at is None: continue
    x, y = at[0] * 2, at[1] * 2
    col = "blue" if e["action"] == "drop" else "magenta"
    draw += ["-stroke", col, "-strokewidth", "2", "-fill", "none", "-draw", f"circle {x},{y} {x+9},{y}",
             "-stroke", "none", "-fill", col, "-pointsize", "13", "-draw", f"text {x+10},{y-6} '{i}'"]
subprocess.run(["magick", tmp] + draw + ["-crop", "944x912+278+110", "+repage", out], check=True)
for i, e in enumerate(sc.heal_log):
    print(i, e["action"], e["role"], tuple(round(v, 1) for v in e["at"]) if e.get("at") is not None else None, e.get("near"))
