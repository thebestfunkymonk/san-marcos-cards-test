#!/bin/bash
# rq.sh <iter> : preview QS into work/<iter>, render 3x and crops
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-QS/work/$1
.venv/bin/python tools/preview.py art/QS.py QS $W --no-white $2 2>&1 | grep -v "^\[preview\]" | tail -25
rsvg-convert -w 2250 $W/QS.svg -o $W/x3.png
magick $W/x3.png -crop 360x420+780+1050 +repage $W/handL_3x.png
magick $W/x3.png -crop 420x420+1380+1170 +repage $W/handR_3x.png
magick $W/x3.png -crop 1416x420+417+1110 +repage $W/lower_3x.png
magick $W/QS-1500.png -crop 944x912+278+110 +repage $W/top2x.png
magick $W/QS-188.png -scale 400% $W/s188x4.png
