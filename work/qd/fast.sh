#!/usr/bin/env bash
# QD fast draft: preview (750/188/1500, no QA, no white) + 3x crops.
# usage: work/qd/fast.sh <tag> [qa]
set -e
cd /home/luke/Projects/design/san-marcos-deck
TAG=${1:-f}
OUT=work/qd/out/$TAG
mkdir -p "$OUT"
if [ "$2" = "qa" ]; then
  .venv/bin/python tools/preview.py art/QD.py QD "$OUT" --qa 2>&1 | grep -v "^$" | tail -22
else
  .venv/bin/python tools/preview.py art/QD.py QD "$OUT" --no-white 2>&1 | grep -v "^$" | tail -5
fi
rsvg-convert -w 2250 "$OUT/QD.svg" -o "$OUT/QD-3x.png"
magick "$OUT/QD-3x.png" -crop 600x660+840+300 +repage "$OUT/face3.png"
magick "$OUT/QD-3x.png" -crop 900x1050+510+765 +repage "$OUT/body3.png"
magick "$OUT/QD-3x.png" -crop 630x700+1230+210 +repage "$OUT/scales3.png"
magick "$OUT/QD-3x.png" -crop 600x900+450+600 +repage "$OUT/left3.png"
magick "$OUT/QD.png" -crop 480x470+135+50 +repage "$OUT/top.png"
