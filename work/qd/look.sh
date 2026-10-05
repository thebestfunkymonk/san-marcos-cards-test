#!/usr/bin/env bash
# QD look: fast preview + one contact sheet of crops.
# usage: work/qd/look.sh <tag> [qa]
set -e
cd /home/luke/Projects/design/san-marcos-deck
TAG=${1:-l}
OUT=work/qd/out/$TAG
mkdir -p "$OUT"
if [ "$2" = "qa" ]; then
  .venv/bin/python tools/preview.py art/QD.py QD "$OUT" --qa 2>&1 | grep -v "^$" | tail -22
else
  .venv/bin/python tools/preview.py art/QD.py QD "$OUT" --no-white 2>&1 | grep -v "^$" | tail -2
fi
rsvg-convert -w 2250 "$OUT/QD.svg" -o "$OUT/QD-3x.png"
magick "$OUT/QD-3x.png" -crop 540x600+870+300 +repage "$OUT/face3.png"
magick "$OUT/QD-3x.png" -crop 900x900+420+690 +repage "$OUT/body3.png"
magick "$OUT/QD-3x.png" -crop 600x660+1230+210 +repage "$OUT/scales3.png"
magick "$OUT/QD-3x.png" -crop 480x450+1380+1080 +repage "$OUT/handR3.png"
magick "$OUT/QD-3x.png" -crop 480x450+500+1150 +repage "$OUT/handL3.png"
magick "$OUT/QD.png" -crop 480x470+135+50 +repage "$OUT/top.png"
