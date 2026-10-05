#!/usr/bin/env bash
# QD draft render: preview (750/188/1500/white + QA) and 3x crops.
# usage: work/qd/render.sh <tag>
set -e
cd /home/luke/Projects/design/san-marcos-deck
TAG=${1:-p}
OUT=work/qd/out/$TAG
mkdir -p "$OUT"
.venv/bin/python tools/preview.py art/QD.py QD "$OUT" --qa 2>&1 | grep -v "^$" | tail -25
rsvg-convert -w 2250 "$OUT/QD.svg" -o "$OUT/QD-3x.png"
magick "$OUT/QD-3x.png" -crop 600x640+855+330 +repage "$OUT/face3.png"
magick "$OUT/QD-3x.png" -crop 900x1050+510+765 +repage "$OUT/body3.png"
magick "$OUT/QD-3x.png" -crop 600x660+1230+210 +repage "$OUT/scales3.png"
magick "$OUT/QD.png" -crop 480x470+135+50 +repage "$OUT/top.png"
.venv/bin/python - "$OUT" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1] + "/QD-qa.json"))
p = r["pieces"][0] if "pieces" in r else r
c5 = p.get("5", {})
print("balance", c5.get("balance"), "gold", c5.get("gold_pct"))
for k in ("1", "4", "4b", "4c", "5r", "10a", "10c", "12", "17", "24", "25"):
    v = p.get(k)
    if v is not None:
        det = v.get("detail", [])
        print(k, v.get("ok"), (det[:6] if det else ""))
EOF
