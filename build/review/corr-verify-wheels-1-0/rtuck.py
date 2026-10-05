import os, sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/build/review/corr-verify-wheels-1-0")
import rmeasure as R
os.chdir(R.ROOT)
BOARD, FOIL = "#0F2B29", "#B08D57"
res = {}
for name, svg, c, ox, oy in (("front", "tuck/TUCK-FRONT.svg", (56, 56), 0, 0),
                             ("tback", "tuck/TUCK-BACK.svg", (81, 81), 0, 0),
                             ("flatfront", "tuck/TUCK-FLAT.svg", (56, 56), 225, 405),
                             ("flatback", "tuck/TUCK-FLAT.svg", (81, 81), 1219, 405)):
    r = R.scan(svg, 769, 1069, c, BOARD, FOIL, ox=ox, oy=oy, label=name)
    res[name] = r
    print("==", name, "(crop starts 12 px outside the panel fold; subtract 12)")
    for k, v in r.items():
        s, t = v["side"], v["tb"]
        print(f"  {k} side foil edges {s['ink_edges']} alpha {s['alpha_edges']} | tb foil edges {t['ink_edges']} alpha {t['alpha_edges']}")
json.dump(res, open(os.path.join(R.OUT, "raster_tuck.json"), "w"), indent=1)
