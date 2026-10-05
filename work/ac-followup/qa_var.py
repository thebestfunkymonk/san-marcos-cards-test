"""QA a variant SVG: python work/ac-followup/qa_var.py NAME"""
import sys, os, json
sys.path.insert(0, os.getcwd())
from deck import build as B, qa as Q
name = sys.argv[1]
info = B.parse("AC")
svg = os.path.abspath(f"work/ac-followup/out/{name}/AC.svg")
info.update(status="art", stock="limestone", svg=svg, png=svg[:-4] + ".png", small=svg[:-4] + "_s.png",
            order=["paper", "jade", "red", "ink", "gold"])
r = Q.check_piece((info, None))
if "error" in r:
    print(r["error"]); sys.exit(1)
for k, v in r.items():
    if isinstance(v, dict) and "ok" in v:
        if v["ok"] is not True:
            print(k, v["ok"], v.get("detail", [])[:8])
print("12 raster:", {L: (len(v['thin']), len(v['gaps']), [g.get('at', g) for g in v['gaps']][:8], [g.get('at', g) for g in v['thin']][:8]) for L, v in r["12"]["raster"].items()})
print("12 vector:", len(r["12"]["vector"]))
